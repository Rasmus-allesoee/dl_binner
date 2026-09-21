"""Explain the accepted E001 mapper discrepancy using existing BAMs only.

Inputs: the two hash-verified mapped BAMs from mapper-feasibility-89gpt00u and
the frozen contigs.jsonl. Outputs: an exclusive output directory containing
MAPQ/score-tag distributions, placement/genome-origin agreement, per-contig
read-count differences and provenance. Does not remap, download, fit or change
inputs. Assembly origins describe destination compatibility, not read truth;
neither agreement nor higher MAPQ establishes mapper accuracy.
"""

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e001_vamb_cpu import require, sha


def read_alignments(path, contigs):
    """Read primary mapped BAM records into mate-keyed summaries and histograms.

    Validate reference lengths and one record per mate. Keep per-mapper score
    gaps descriptive: scoring and MAPQ scales are not assumed comparable.
    """
    import pysam
    records, counts = {}, Counter()
    hist = {key: Counter() for key in ("mapq", "AS_minus_XS", "NM", "aligned_query_bp")}
    with pysam.AlignmentFile(path, "rb") as bam:
        require(dict(zip(bam.references, bam.lengths)) == {k: v["length"] for k, v in contigs.items()},
                "BAM reference dictionary differs from frozen retained contigs")
        for rec in bam.fetch(until_eof=True):
            require(not (rec.flag & 2308), "Expected primary mapped records only")
            require(rec.is_paired and rec.is_read1 != rec.is_read2, "Invalid mate flags")
            key = (rec.query_name, 2 if rec.is_read2 else 1)
            require(key not in records, "Duplicate primary mate")
            position = (rec.reference_name, rec.reference_start, rec.is_reverse)
            records[key] = {"position": position, "mapq": rec.mapping_quality,
                            "cigar": rec.cigarstring, "sequence": rec.get_forward_sequence()}
            counts[rec.reference_name] += 1
            hist["mapq"][str(rec.mapping_quality)] += 1
            hist["NM"][str(rec.get_tag("NM")) if rec.has_tag("NM") else "missing"] += 1
            hist["aligned_query_bp"][str(rec.query_alignment_length)] += 1
            gap = rec.get_tag("AS") - rec.get_tag("XS") if rec.has_tag("AS") and rec.has_tag("XS") else "missing"
            hist["AS_minus_XS"][str(gap)] += 1
    return records, counts, hist


def compare(a, b, contigs, total_reads):
    """Classify mate placements and mapped-destination origin compatibility.

    Inputs are mate-keyed records from read_alignments. Both-unmapped reads are
    counted from the accepted input size, since filtered BAMs omit them. Output
    includes category-specific MAPQ histograms and bounded examples, never an
    accuracy claim or a truth-selected mapper recommendation.
    """
    union = a.keys() | b.keys()
    require(len(union) <= total_reads, "More mapped mates than input reads")
    categories = Counter(both_unmapped=total_reads - len(union))
    cross = defaultdict(lambda: {"strobealign": Counter(), "bowtie2": Counter()})
    examples = defaultdict(list)
    same_position_different_cigar = 0
    for key in sorted(union):
        x, y = a.get(key), b.get(key)
        if x is None:
            category = "bowtie2_only"
        elif y is None:
            category = "strobealign_only"
        else:
            require(x["sequence"] == y["sequence"], "Mate sequence differs between BAMs")
            px, py = x["position"], y["position"]
            if px == py:
                category = "same_position"
                same_position_different_cigar += x["cigar"] != y["cigar"]
            elif px[0] == py[0]:
                category = "same_contig_other_position"
            elif set(contigs[px[0]]["origins"]) & set(contigs[py[0]]["origins"]):
                category = "different_contig_shared_origin"
            else:
                category = "different_contig_disjoint_origins"
        categories[category] += 1
        for tool, record in (("strobealign", x), ("bowtie2", y)):
            if record is not None:
                cross[category][tool][str(record["mapq"])] += 1
        if category != "same_position" and len(examples[category]) < 10:
            examples[category].append({"read": key, "strobealign": x and x["position"], "bowtie2": y and y["position"]})
    require(sum(categories.values()) == total_reads, "Agreement categories do not partition input reads")
    return {"categories": categories, "mapq_by_category": dict(cross), "examples": dict(examples),
            "same_position_different_cigar": same_position_different_cigar}


def truth_comparison(path, data, contigs):
    """Join mapped mate IDs to CAMI read-origin metadata, retaining ambiguity.

    Scan the complete gzip table (including CRC validation), select only mates
    present in either accepted BAM, and require complete unique joins. Report
    true-genome destination compatibility, not unique alignability or a generic
    mapping-accuracy benchmark. Both-unmapped mates need no origin for this count.
    """
    wanted = set().union(*(records.keys() for records, _, _ in data.values()))
    truth, rows = {}, 0
    with gzip.open(path, "rt") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        require(header == ["#anonymous_read_id", "genome_id", "tax_id", "read_id"], "Unexpected read-truth schema")
        for row in reader:
            require(len(row) == 4, "Malformed read-truth row")
            rows += 1
            name, sep, mate = row[0].rpartition("/")
            require(sep and mate in ("1", "2"), "Unexpected read-truth mate ID")
            key = (name, int(mate))
            if key in wanted:
                require(key not in truth, "Duplicate selected read truth")
                truth[key] = row[1]
    require(truth.keys() == wanted, "Missing mapped-read truth")
    results, joint = {}, Counter()
    correct = {}
    represented = set().union(*(set(row["origins"]) for row in contigs.values()))
    for tool, (records, _, _) in data.items():
        counts, by_mapq = Counter(), defaultdict(Counter)
        correct[tool] = {}
        for key, record in records.items():
            origins = contigs[record["position"][0]]["origins"]
            compatible = truth[key] in origins
            label = "origin_compatible" if compatible else "origin_incompatible"
            counts[label] += 1
            counts["source_genome_absent_from_retained_reference"] += truth[key] not in represented
            by_mapq[str(record["mapq"])][label] += 1
            correct[tool][key] = compatible
        results[tool] = {"counts": counts, "by_mapq": dict(by_mapq)}
    for key in wanted:
        a, b = correct["strobealign"].get(key, False), correct["bowtie2"].get(key, False)
        joint[f"strobe_{int(a)}_bowtie_{int(b)}"] += 1
    return {"source_sha256": sha(path), "source_rows": rows, "selected_rows": len(truth),
            "tools": results, "joint_on_mapped_union": joint,
            "top_source_genomes_on_mapped_union": Counter(truth.values()).most_common(10),
            "scope": "True source genome in destination origin set; wrong-source ties may be non-identifiable; prefix only"}


def analyze(paths, contig_path, out, read_truth=None):
    """Validate accepted input hashes and write a new local diagnostic report.

    Expected BAM identities come from mapper-observed.json; no execution snapshot
    or scientific configuration is changed. Refuse an existing output directory.
    """
    base = Path(__file__).resolve().parents[1] / "experiments/E001-coverage-thinning"
    frozen = json.loads((base / "frozen-inputs.json").read_text())
    observed = json.loads((base / "mapper-observed.json").read_text())
    accepted = [r for r in observed["attempts"] if r["records"]["status.json"]["exit_code"] == 0]
    require(len(accepted) == 1, "Expected one accepted mapper attempt")
    summary = accepted[0]["records"]["mapping-summary.json"]
    hashes = {tool: sha(path) for tool, path in paths.items()}
    for tool in paths:
        require(hashes[tool] == summary["tools"][tool]["sha256"], "Wrong accepted BAM: " + tool)
    require(sha(contig_path) == frozen["outputs"]["contigs.jsonl"], "Changed contig metadata")
    with contig_path.open() as handle:
        contigs = {row["id"]: row for row in map(json.loads, handle) if row["retained"]}
    require(not out.exists(), "Output already exists; preserve previous analysis")
    data = {tool: read_alignments(path, contigs) for tool, path in paths.items()}
    pairs = accepted[0]["records"]["reads/prefix.json"]["pairs"]
    report = compare(data["strobealign"][0], data["bowtie2"][0], contigs, pairs * 2)
    require(report["categories"]["same_position"] == summary["same_mapped_position_reads"], "Agreement differs from accepted summary")
    require(report["categories"]["both_unmapped"] == summary["both_unmapped_reads"], "Unmapped count differs")
    report["tools"] = {}
    for tool, (records, counts, hist) in data.items():
        require(len(records) == summary["tools"][tool]["records"], "Mapped count differs")
        require(hist["mapq"]["0"] == summary["tools"][tool]["mapq_zero_records"], "MAPQ-zero count differs")
        report["tools"][tool] = {"histograms": hist, "top_contigs": counts.most_common(10),
                                 "contigs_with_reads": len(counts)}
    counts_a, counts_b = data["strobealign"][1], data["bowtie2"][1]
    report["absolute_contig_read_count_difference_sum"] = sum(abs(counts_a[k] - counts_b[k]) for k in contigs)
    report["provenance"] = {"accepted_archive": accepted[0]["archive"], "bam_sha256": hashes,
                             "contigs_sha256": frozen["outputs"]["contigs.jsonl"], "script_sha256": sha(Path(__file__))}
    report["scope"] = "Existing prefix analysis only. Destination origin overlap is not true read origin; no accuracy or biological result."
    if read_truth is not None:
        report["read_truth"] = truth_comparison(read_truth, data, contigs)
    out.mkdir(parents=True)
    (out / "diagnostics.json").write_text(json.dumps(report, indent=2) + "\n")
    with (out / "contig-read-counts.tsv").open("x") as handle:
        handle.write("contig\tlength\tstrobealign_reads\tbowtie2_reads\torigins\n")
        for name, row in contigs.items():
            handle.write(f"{name}\t{row['length']}\t{counts_a[name]}\t{counts_b[name]}\t{','.join(row['origins'])}\n")
    print(json.dumps(report["categories"], indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strobe-bam", type=Path, required=True)
    parser.add_argument("--bowtie-bam", type=Path, required=True)
    parser.add_argument("--contigs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--read-truth", type=Path)
    args = parser.parse_args()
    analyze({"strobealign": args.strobe_bam, "bowtie2": args.bowtie_bam}, args.contigs, args.out, args.read_truth)
