"""Synthetic native checks. These are software tests, never research outcomes."""

from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import random
import re
import subprocess
import sys

import numpy as np
import pysam
from Bio.Seq import Seq
from Bio.SeqIO.QualityIO import FastqGeneralIterator

from .metrics import score
from .native import (comebin_features, mapping_commands, metabat_commands, pipeline, require_packages,
                     run_checked, scale_comebin, thinning_command, validate_comebin_pair, verify_source, vamb_features)
from .records import config, digest, partition, require, sequences, write_cami, write_json


def make_fixture(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    rng = random.Random(101)
    seqs = {f"contig_{i:02d}": "".join(rng.choices("ACGT", k=4000)) for i in range(12)}
    with (out / "fixture.fna").open("x") as handle:
        for name, sequence in seqs.items():
            handle.write(f">{name}\n{sequence}\n")
    header = {"HD": {"VN": "1.6", "SO": "coordinate"}, "SQ": [{"SN": s, "LN": len(v)} for s, v in seqs.items()]}
    (out / "C0").mkdir()
    for sample in range(2):
        records = []
        with (out / f"sample_{sample:02d}.fq").open("x") as fastq:
            for rid, (name, sequence) in enumerate(seqs.items()):
                if rid == 11:
                    continue
                for i in range(80 + 10 * sample + rid):
                    start = rng.randrange(0, len(sequence) - 350)
                    qname = f"s{sample}_c{rid}_p{i}"
                    first, second = sequence[start:start + 150], str(Seq(sequence[start + 120:start + 270]).reverse_complement())
                    fastq.write(f"@{qname}/1\n{first}\n+\n{'I' * 150}\n@{qname}/2\n{second}\n+\n{'I' * 150}\n")
                    for mate, pos, other, flag, query in ((0, start, start + 120, 99, first), (1, start + 120, start, 147, str(Seq(second).reverse_complement()))):
                        rec = pysam.AlignedSegment()
                        rec.query_name, rec.query_sequence, rec.flag = qname, query, flag
                        rec.reference_id, rec.reference_start, rec.mapping_quality = rid, pos, 60
                        rec.cigarstring = "150M"
                        rec.next_reference_id, rec.next_reference_start = rid, other
                        rec.template_length = 270 if mate == 0 else -270
                        rec.query_qualities = pysam.qualitystring_to_array("I" * 150)
                        rec.set_tag("NM", 0)
                        records.append(rec)
        with pysam.AlignmentFile(out / "C0" / f"sample_{sample:02d}.bam", "wb", header=header) as bam:
            for rec in sorted(records, key=lambda r: (r.reference_id, r.reference_start, r.query_name, r.flag)):
                bam.write(rec)
        pysam.index(str(out / "C0" / f"sample_{sample:02d}.bam"))
    write_json(out / "fixture.json", {"purpose": "software_smoke_only", "seed": 101, "contigs": len(seqs), "empty_coverage_contig": "contig_11"})


def check_interleaved(path, max_pairs=10000):
    from .records import open_text
    pairs, lengths = 0, Counter()
    with open_text(path) as handle:
        iterator = iter(FastqGeneralIterator(handle))
        for first in iterator:
            second = next(iterator, None)
            require(second is not None, "Odd number of interleaved reads")
            names = [r[0].split()[0] for r in (first, second)]
            require(names[0].removesuffix("/1") == names[1].removesuffix("/2"), "FASTQ mates have different template IDs")
            require(not names[0].endswith("/2") and not names[1].endswith("/1"), "Reversed FASTQ mates")
            for record in (first, second):
                lengths[len(record[1])] += 1
            pairs += 1
            if pairs == max_pairs:
                break
    require(pairs > 0, "Empty FASTQ")
    return {"pairs_checked": pairs, "scope": "prefix_only", "read_length_counts": dict(lengths)}


def bam_inventory(path, fasta):
    expected = [(s, len(seq)) for s, seq in sequences(fasta)]
    excluded_flags = config()["exclude_sam_flags"]
    count, low_mapq = 0, 0
    previous = (-1, -1)
    with pysam.AlignmentFile(path, "rb") as bam:
        require(list(zip(bam.references, bam.lengths)) == expected, "BAM reference names/order/lengths mismatch")
        require(bam.header.to_dict().get("HD", {}).get("SO") == "coordinate", "BAM is not declared coordinate sorted")
        for rec in bam.fetch(until_eof=True):
            require(not (rec.flag & excluded_flags), "Non-primary/unmapped BAM record")
            require(rec.has_tag("NM"), "Missing NM tag needed by native coverage estimators")
            position = (rec.reference_id, rec.reference_start)
            require(position >= previous, "BAM records not coordinate sorted")
            previous = position
            count += 1
            low_mapq += rec.mapping_quality == 0
    return {"records": count, "mapq_zero_records": low_mapq, "sha256": digest(path)}


def check_thinned_fixture(full, thin):
    def signatures(path):
        result = defaultdict(Counter)
        with pysam.AlignmentFile(path, "rb") as bam:
            for r in bam.fetch(until_eof=True):
                result[r.query_name][(r.flag, r.reference_id, r.reference_start, r.cigarstring)] += 1
        return result
    a, b = signatures(full), signatures(thin)
    require(0 < len(b) < len(a), "Fixture thinning did not remove a nonempty subset")
    require(all(name in a and records == a[name] for name, records in b.items()), "Thinning changed/dropped mates within a retained template")
    return {"original_templates": len(a), "retained_templates": len(b), "pair_consistency": "pass"}


def mapping_smoke(fixture, out):
    fixture, out = Path(fixture), Path(out)
    out.mkdir(parents=True, exist_ok=False)
    versions = {name: subprocess.check_output([name, "--version"], text=True).splitlines()[0] for name in ("samtools", "strobealign")}
    require(versions["samtools"].split()[1] == config()["samtools_version"], "Wrong samtools version")
    require(versions["strobealign"].split()[-1].lstrip("v") == config()["mapper"]["version"], "Wrong strobealign version")
    fasta = fixture / "fixture.fna"
    pipeline(mapping_commands(fasta, fixture / "sample_00.fq", "fixture", out / "mapped.bam"), out / "mapping")
    mapped = bam_inventory(out / "mapped.bam", fasta)
    require(mapped["records"] > 0, "No mapped fixture reads")
    correct, mates = 0, defaultdict(set)
    with pysam.AlignmentFile(out / "mapped.bam", "rb") as bam:
        for rec in bam:
            match = re.fullmatch(r"s0_c([0-9]+)_p[0-9]+", rec.query_name)
            require(match is not None and rec.is_paired and rec.is_read1 != rec.is_read2, "Unexpected fixture read or mate flags")
            correct += rec.reference_name == f"contig_{int(match.group(1)):02d}"
            mates[rec.query_name].add(1 if rec.is_read1 else 2)
    require(correct / mapped["records"] >= 0.99, "Synthetic unique-read mapping identity failed")
    require(all(m == {1, 2} for m in mates.values()), "Synthetic mapped pairs lost a mate")
    mapped["correct_reference_fraction"] = correct / mapped["records"]
    (out / "CT").mkdir()
    results = {}
    for sample in range(2):
        name = f"sample_{sample:02d}.bam"
        run_checked(thinning_command(fixture / "C0" / name, out / "CT" / name, 0, sample), out / "logs", f"thin-{sample}")
        run_checked(["samtools", "index", str(out / "CT" / name)], out / "logs", f"index-{sample}")
        results[name] = check_thinned_fixture(fixture / "C0" / name, out / "CT" / name)
    write_json(out / "smoke.json", {"status": "pass", "versions": versions, "mapping": mapped, "thinning": results})


def amber_smoke(source, out):
    provenance = verify_source("AMBER_evaluation", source)
    require_packages({"numpy": "2.0.1", "pandas": "2.2.2", "biopython": "1.87"})
    sys.path.insert(0, str(Path(source).resolve()))
    import pandas as pd
    from cami_amber.binning_classes import GenomeQuery, Options
    from cami_amber.utils.load_data import read_metadata
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    lengths = {"a1": 200000, "a2": 200000, "b1": 200000, "b2": 200000}
    origins = {s: [s[0]] for s in lengths}
    population = {"lengths": lengths, "unique_origins": {s: s[0] for s in lengths}, "genomes": ["a", "b"]}
    cases = {"perfect": {s: s[0] for s in lengths}, "merge": {s: "x" for s in lengths},
             "split": {s: s for s in lengths}, "missing": {s: "a" for s in lengths if s.startswith("a")},
             "unassigned": {"a1": "a", "a2": "a", "b1": "b"}}
    expected_recall = {"perfect": 1.0, "merge": 1.0, "split": 0.5, "missing": 0.5, "unassigned": 0.75}
    write_cami(out / "truth.tsv", lengths, origins=origins)
    options = Options(filter_tail_percentage=0, skip_heatmap=True)
    def evaluate(truth_path, query_path):
        gs = GenomeQuery("gold", "E001", options, read_metadata((str(truth_path), "gold"))[0], is_gs=True)
        query = GenomeQuery("fixture", "E001", options, read_metadata((str(query_path), "fixture"))[0])
        query.gold_standard = gs
        query.compute_metrics()
        return query
    results = {}
    for name, assignments in cases.items():
        path = out / (name + ".tsv")
        write_cami(path, lengths, assignments=assignments)
        query = evaluate(out / "truth.tsv", path)
        require(np.isclose(query.metrics.recall_avg_bp, expected_recall[name]), f"AMBER recall disagreement: {name}")
        recovery = {g: 0.0 for g in population["genomes"]}
        for _, row in query.precision_df.iterrows():
            if row["total_length"] >= config()["min_bin_bp"] and row["precision_bp"] >= config()["min_purity"]:
                recovery[row["genome_id"]] = max(recovery[row["genome_id"]], row["recall_bp"])
        measured = score(population, assignments)["r95"]
        require(np.isclose(measured, sum(recovery.values()) / len(recovery)), f"AMBER-derived R95 mismatch: {name}")
        results[name] = {"e001_r95": measured, "amber_unconstrained_recall": query.metrics.recall_avg_bp}
    # AMBER's strict threshold count is deliberately not E001's inclusive count.
    boundary = pd.DataFrame({"sample_id": ["E001"], "Tool": ["fixture"], "recall_bp": [0.5], "precision_bp": [0.95]})
    counts = GenomeQuery.calc_num_recovered_genomes(boundary, [0.5], [0.05])
    require(int(counts.iloc[0]["> 50% completeness"]) == 0, "AMBER threshold semantics changed")
    lengths2 = {"a": 200000, "shared": 100000, "b": 200000}
    write_cami(out / "multi-truth.tsv", lengths2, origins={"a": ["a"], "shared": ["a", "b"], "b": ["b"]})
    assignments = {"a": "A", "shared": "A", "b": "B"}
    write_cami(out / "multi-query.tsv", lengths2, assignments=assignments)
    query = evaluate(out / "multi-truth.tsv", out / "multi-query.tsv")
    require(np.isclose(query.metrics.recall_avg_bp, 1.0) and np.isclose(query.metrics.precision_avg_bp, 1.0), "AMBER multi-origin behavior changed")
    conservative = score({"lengths": lengths2, "unique_origins": {"a": "a", "b": "b"}, "genomes": ["a", "b"]}, assignments)
    require(conservative["r95"] == 0.5, "Conservative ambiguity contract failed")
    results["multi_origin"] = {"amber_recall": 1.0, "e001_r95": conservative["r95"], "parity_expected": False}
    write_json(out / "smoke.json", {**provenance, "status": "pass", "checks": results})


def feature_smoke(tool, source, fixture, mapping, out):
    fixture, mapping, out = Path(fixture), Path(mapping), Path(out)
    out.mkdir(parents=True, exist_ok=False)
    fasta = fixture / "fixture.fna"
    if tool == "vamb":
        for label, bamdir in (("C0", fixture / "C0"), ("CT", mapping / "CT")):
            vamb_features(source, fasta, sorted(bamdir.glob("*.bam")), out / label)
        import torch
        import vamb
        torch.set_num_threads(2)
        arrays = np.load(out / "C0/normalized-C0.npz")
        require(np.allclose(arrays["coverage"][-1], [0.5, 0.5]), "Native VAMB zero-row convention changed")
        try:
            vamb.encode.make_dataloader(np.zeros((12, 2), dtype=np.float32), arrays["composition"].copy(), np.full(12, 4000))
        except ValueError:
            pass
        else:
            raise ValueError("Native VAMB no longer rejects all-zero sample columns")
        model = vamb.encode.VAE(nsamples=2, cuda=False, seed=11)
        tensors = [torch.from_numpy(arrays[n][:8]) for n in ("coverage", "composition", "total_abundance")]
        output = model(*tensors)
        require(all(torch.isfinite(t).all().item() for t in output), "Nonfinite native VAMB CPU forward")
        report = {"status": "pass", "cpu_forward": "pass", "training": "not run"}
        arrays.close()
    else:
        comebin_features(source, fasta, fixture / "C0", out / "C0")
        comebin_features(source, fasta, mapping / "CT", out / "CT", fixed=out / "C0")
        report = validate_comebin_pair(out / "C0", out / "CT")
        require(all(n > 0 for n in report["changed_entries_per_view"]["coverage_mean.npy"]), "Synthetic CT did not change every view")
        scale_comebin(out / "C0", out / "CS")
        from get_augfeature import get_kmer_coverage
        a = np.load(out / "C0/normalized-views.npy")
        views, _, _, _ = get_kmer_coverage(out / "CS", n_views=6, addvars=True, vars_sqrt=True)
        b = np.stack([v.numpy() for v in views])
        np.save(out / "CS/normalized-views.npy", b, allow_pickle=False)
        require(np.array_equal(a[:, :, -136:], b[:, :, -136:]), "CS changed composition")
        require(np.max(np.abs(a[:, :, :4] - b[:, :, :4])) < 0.001, "Unexpected large COMEBin fixture scale discrepancy")
        import torch
        from models.mlp import EmbeddingNet
        from models.mlp2 import CombinedEmbeddingNet
        torch.set_num_threads(2)
        torch.manual_seed(11)
        cov = EmbeddingNet(4, 128, [2048] * 3, [0.2] * 2, actn=torch.nn.LeakyReLU())
        model = CombinedEmbeddingNet(264, 128, [2048] * 3, [0.2] * 2, actn=torch.nn.LeakyReLU(), cov_model=cov)
        output = model(torch.from_numpy(a[0, :8, -136:]), torch.from_numpy(a[0, :8, :4]))
        require(all(torch.isfinite(t).all().item() for t in output), "Nonfinite COMEBin CPU forward")
        report.update({"status": "pass", "cpu_forward": "pass", "training": "not run", "CS_max_abs_difference": float(np.max(np.abs(a - b)))})
    write_json(out / "smoke.json", report)


def metabat_smoke(source, fixture, out):
    provenance = verify_source("metabat", source)
    fixture, out = Path(fixture), Path(out)
    out.mkdir(parents=True, exist_ok=False)
    import shutil
    prefix = Path(os.environ["E001_METABAT_PREFIX"])
    for binary in ("metabat2", "jgi_summarize_bam_contig_depths"):
        require(shutil.which(binary) is not None and Path(shutil.which(binary)).resolve() == (prefix / "bin" / binary).resolve(), "MetaBAT executable is not from the prepared source build")
    for i, cmd in enumerate(metabat_commands(fixture / "fixture.fna", sorted((fixture / "C0").glob("*.bam")), out)):
        run_checked(cmd, out / "logs", f"metabat-{i}")
    lengths = {s: len(seq) for s, seq in sequences(fixture / "fixture.fna")}
    membership = out / "bins.MemberMatrix.txt"
    require(membership.exists(), "Native MetaBAT2 membership missing; inspect logs, do not assume an empty partition")
    assignments = partition(membership, lengths, "metabat")
    from .native import scale_metabat_depth
    scaled = out / "CS"
    scaled.mkdir()
    scale_metabat_depth(out / "depth.tsv", scaled / "depth.tsv", lengths)
    cmd = metabat_commands(fixture / "fixture.fna", sorted((fixture / "C0").glob("*.bam")), scaled)[1]
    run_checked(cmd, out / "logs", "metabat-CS")
    cs_assignments = partition(scaled / "bins.MemberMatrix.txt", lengths, "metabat")
    write_json(out / "smoke.json", {**provenance, "status": "pass", "assigned_contigs": len(assignments),
               "CS_assigned_contigs": len(cs_assignments), "biological_interpretation": "none"})
