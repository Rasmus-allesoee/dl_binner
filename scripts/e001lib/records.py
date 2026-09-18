"""Strict input contracts and immutable E001 provenance records."""

import csv
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from Bio import SeqIO
from Bio.Seq import Seq


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/E001-coverage-thinning"
# The source scan rendered the orphan with asterisks, while Biopython's
# converter error exposed the same malformed record with underscores.  Keep
# both exact observed spellings narrow; do not generalize this exception.
KNOWN_EMPTY_ORPHAN_IDS = frozenset({"*from__to*-42_total_0", "_from__to_-42_total_0"})
HMP_HEADER = re.compile(r"(.+)_from_([0-9]+)_to_([0-9]+)_total_([0-9]+)")
DNA_ALPHABET = set("ACGTRYSWKMBDHVN")


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def digest(path, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")


def validate_attempt(attempt, assignments, population):
    record = json.loads(Path(attempt).read_text())
    require(record.get("status") == "completed", "Failed/incomplete attempt is not an empty biological result")
    require(record.get("assignment_sha256") == digest(assignments), "Assignment does not match completed attempt")
    require(record.get("population_sha256") == digest(population), "Attempt uses a different population")
    require(record.get("config_sha256") == digest(EXPERIMENT / "config.json"), "Attempt uses a different configuration")
    require(re.fullmatch(r"[0-9a-f]{40}", record.get("source_commit", "")), "Missing executable source commit")
    return record


def config():
    return json.loads((EXPERIMENT / "config.json").read_text())


def open_text(path):
    path = Path(path)
    return gzip.open(path, "rt") if path.suffix == ".gz" else path.open()


def sequences(path, skip_known_empty=False, excluded=None):
    seen = set()
    with open_text(path) as handle:
        require(handle.read(1) == ">", f"Not a FASTA file: {path}")
        handle.seek(0)
        for record in SeqIO.parse(handle, "fasta"):
            seq = str(record.seq)
            if skip_known_empty and record.id in KNOWN_EMPTY_ORPHAN_IDS and not seq:
                if excluded is not None:
                    excluded.append({"id": record.id, "length": 0,
                                     "sha256": hashlib.sha256(b"").hexdigest(),
                                     "reason": "known_empty_orphan"})
                continue
            require(record.id and record.id not in seen, f"Duplicate/empty FASTA ID: {record.id}")
            seen.add(record.id)
            require(seq and set(seq.upper()) <= DNA_ALPHABET, f"Invalid DNA: {record.id}")
            yield record.id, seq
    require(seen, "Empty FASTA")


def _coordinate_examples(counts, limit=20):
    return [{"contig_id": key[0], "start": key[1], "end": key[2], "count": counts[key]}
            for key in sorted(counts)[:limit]]


def audit_hmp(fasta, mapping, example_limit=20):
    """Report every FASTA/mapping coordinate mismatch without changing inputs."""
    columns = ("anonymous_contig_id", "genome_id", "tax_id", "contig_id",
               "number_reads", "start_position", "end_position")
    mapping_counts, mapping_signatures, mapping_invalid = Counter(), defaultdict(set), []
    for row in table(mapping, columns):
        try:
            key = (row["contig_id"], int(row["start_position"]), int(row["end_position"]))
        except ValueError:
            mapping_invalid.append({"contig_id": row["contig_id"],
                                    "start": row["start_position"], "end": row["end_position"]})
            continue
        mapping_counts[key] += 1
        mapping_signatures[key].add(tuple(row[name] for name in ("genome_id", "tax_id", "number_reads")))

    fasta_counts, fasta_ids = Counter(), Counter()
    malformed, invalid, length_mismatch, excluded = [], [], [], []
    with open_text(fasta) as handle:
        require(handle.read(1) == ">", f"Not a FASTA file: {fasta}")
        handle.seek(0)
        for record in SeqIO.parse(handle, "fasta"):
            fasta_ids[record.id] += 1
            sequence = str(record.seq)
            if record.id in KNOWN_EMPTY_ORPHAN_IDS and not sequence:
                excluded.append({"id": record.id, "length": 0,
                                 "sha256": hashlib.sha256(b"").hexdigest(),
                                 "reason": "known_empty_orphan"})
                continue
            match = HMP_HEADER.fullmatch(record.id)
            if match is None:
                malformed.append(record.id)
                continue
            accession, start, end, declared = match.groups()
            key = (accession, int(start), int(end))
            fasta_counts[key] += 1
            if not sequence or not set(sequence.upper()) <= DNA_ALPHABET:
                invalid.append(record.id)
            expected = int(declared)
            coordinate_length = key[2] - key[1] + 1
            if len(sequence) != expected or expected != coordinate_length:
                length_mismatch.append({"id": record.id, "actual": len(sequence),
                                        "declared": expected, "coordinate": coordinate_length})

    fasta_duplicate = Counter({key: count for key, count in fasta_counts.items() if count > 1})
    mapping_duplicate = Counter({key: count for key, count in mapping_counts.items() if count > 1})
    mapping_conflicting = {key: signatures for key, signatures in mapping_signatures.items() if len(signatures) > 1}
    fasta_missing_mapping = Counter({key: count for key, count in fasta_counts.items() if key not in mapping_counts})
    mapping_missing_fasta = Counter({key: count for key, count in mapping_counts.items() if key not in fasta_counts})
    duplicate_ids = {identifier: count for identifier, count in fasta_ids.items()
                     if count > 1 and identifier not in KNOWN_EMPTY_ORPHAN_IDS}
    join_contract_passes = not any((mapping_invalid, malformed, invalid, length_mismatch,
                                    duplicate_ids, fasta_duplicate, mapping_conflicting,
                                    fasta_missing_mapping, mapping_missing_fasta))
    return {
        "status": "join_audit",
        "join_contract_passes": join_contract_passes,
        "fasta_records": sum(fasta_ids.values()),
        "fasta_coordinate_keys": len(fasta_counts),
        "fasta_duplicate_id_count": len(duplicate_ids),
        "fasta_duplicate_id_examples": [{"id": identifier, "count": count}
                                         for identifier, count in sorted(duplicate_ids.items())[:example_limit]],
        "fasta_duplicate_coordinate_count": len(fasta_duplicate),
        "fasta_duplicate_coordinate_examples": _coordinate_examples(fasta_duplicate, example_limit),
        "fasta_keys_missing_mapping_count": len(fasta_missing_mapping),
        "fasta_keys_missing_mapping_examples": _coordinate_examples(fasta_missing_mapping, example_limit),
        "fasta_malformed_header_count": len(malformed),
        "fasta_malformed_header_examples": malformed[:example_limit],
        "fasta_invalid_dna_count": len(invalid),
        "fasta_invalid_dna_examples": invalid[:example_limit],
        "fasta_length_mismatch_count": len(length_mismatch),
        "fasta_length_mismatch_examples": length_mismatch[:example_limit],
        "excluded_known_empty_count": len(excluded),
        "excluded_known_empty_examples": excluded[:example_limit],
        "mapping_rows": sum(mapping_counts.values()),
        "mapping_coordinate_keys": len(mapping_counts),
        "mapping_duplicate_coordinate_count": len(mapping_duplicate),
        "mapping_duplicate_coordinate_examples": _coordinate_examples(mapping_duplicate, example_limit),
        "mapping_conflicting_coordinate_count": len(mapping_conflicting),
        "mapping_conflicting_coordinate_examples": _coordinate_examples(
            Counter({key: len(signatures) for key, signatures in mapping_conflicting.items()}), example_limit),
        "mapping_keys_missing_fasta_count": len(mapping_missing_fasta),
        "mapping_keys_missing_fasta_examples": _coordinate_examples(mapping_missing_fasta, example_limit),
        "mapping_invalid_coordinate_count": len(mapping_invalid),
        "mapping_invalid_coordinate_examples": mapping_invalid[:example_limit],
        "source_sha256": {"fasta": digest(fasta), "mapping": digest(mapping)},
    }


def table(path, columns, cami=False):
    """Parse one TSV sample; do not silently merge multiple CAMI sample blocks."""
    with open_text(path) as handle:
        header = None
        sample_count = 0
        for line in handle:
            if not line.strip():
                continue
            if cami and line.startswith("@") and not line.startswith("@@"):
                require(header is None, "Metadata after table data; multiple samples are not supported")
                sample_count += line.startswith("@SampleID:")
                require(sample_count <= 1, "Multiple CAMI samples")
                continue
            if header is None:
                prefix = "@@" if cami else "#"
                line = line.removeprefix(prefix)
                header = next(csv.reader([line], delimiter="\t"))
                require(len(set(header)) == len(header), "Duplicate table columns")
                require(set(columns) <= set(header), f"Required columns {columns}; got {header}")
                continue
            row = next(csv.reader([line], delimiter="\t"))
            require(len(row) == len(header), f"Wrong number of columns in {path}")
            yield dict(zip(header, row))
        require(header is not None, f"Missing header in {path}")


def truth_table(path, lengths):
    origins = defaultdict(list)
    pairs = set()
    for row in table(path, ("SEQUENCEID", "BINID", "LENGTH"), cami=True):
        seq, genome = row["SEQUENCEID"], row["BINID"]
        require(seq in lengths and genome, f"Unknown sequence or empty genome: {seq}")
        require(int(row["LENGTH"]) == lengths[seq], f"Truth length mismatch: {seq}")
        require((seq, genome) not in pairs, f"Duplicate truth association: {seq}, {genome}")
        pairs.add((seq, genome))
        origins[seq].append(genome)
    require(set(origins) == set(lengths), "Truth does not cover the complete input FASTA")
    return dict(origins)


def partition(path, lengths, layout="cami"):
    require(layout in {"cami", "vamb", "comebin", "metabat"}, "Unknown assignment layout")
    if layout == "cami":
        rows = ((r["SEQUENCEID"], r["BINID"]) for r in table(path, ("SEQUENCEID", "BINID"), cami=True))
    else:
        def native_rows():
            with open_text(path) as handle:
                for number, row in enumerate(csv.reader(handle, delimiter="\t")):
                    if layout == "vamb" and number == 0 and row == ["clustername", "contigname"]:
                        continue
                    if layout == "metabat" and number == 0 and row == ["ContigName", "ClusterId"]:
                        continue
                    require(len(row) == 2, f"Expected two columns at row {number + 1}")
                    yield (row[1], row[0]) if layout == "vamb" else tuple(row)
        rows = native_rows()
    result, seen = {}, set()
    for seq, bin_id in rows:
        require(seq in lengths, f"Unknown predicted ID: {seq}")
        require(seq not in seen, f"Duplicate/multiple predicted assignment: {seq}")
        require(bin_id and bin_id.strip() == bin_id, f"Invalid bin ID for {seq}")
        seen.add(seq)
        if layout == "metabat" and bin_id == "0":
            continue
        result[seq] = bin_id
    return result


def write_cami(path, lengths, origins=None, assignments=None):
    require((origins is None) != (assignments is None), "Supply truth or predictions, not both")
    with Path(path).open("x") as handle:
        handle.write("@Version:0.9.0\n@SampleID:E001\n@@SEQUENCEID\tBINID")
        handle.write("\tLENGTH\n" if origins is not None else "\n")
        for seq in lengths:
            if origins is not None:
                for genome in origins[seq]:
                    handle.write(f"{seq}\t{genome}\t{lengths[seq]}\n")
            elif seq in assignments:
                handle.write(f"{seq}\t{assignments[seq]}\n")


def domains_from_nodes(taxids, nodes_path):
    parents = {}
    with open_text(nodes_path) as handle:
        for row in csv.reader(handle, delimiter="|"):
            require(len(row) >= 3, "Invalid NCBI nodes.dmp")
            parents[row[0].strip()] = row[1].strip()
    roots = {"2": "bacteria", "2157": "archaea", "2759": "eukaryota", "10239": "viruses"}
    resolved = {}
    for taxid in set(taxids):
        current, visited = taxid, set()
        while current not in roots and current not in visited and current in parents:
            visited.add(current)
            current = parents[current]
        resolved[taxid] = roots.get(current, "unknown")
    return resolved


def prepare_hmp(fasta, mapping, out, nodes=None):
    """Join published coordinate headers to corrected anonymous IDs, never by row order."""
    cfg = config()
    out = Path(out)
    require(not out.exists(), f"Output exists: {out}")
    mapping_rows, id_keys = defaultdict(list), {}
    for row in table(mapping, ("anonymous_contig_id", "genome_id", "tax_id", "contig_id", "start_position", "end_position")):
        key = (row["contig_id"], int(row["start_position"]), int(row["end_position"]))
        seq_id = row["anonymous_contig_id"]
        require(re.fullmatch(r"PC[0-9]+", seq_id), f"Non-anonymous HMP ID: {seq_id}")
        require(seq_id not in id_keys or id_keys[seq_id] == key, f"Conflicting mapping for {seq_id}; is this the unfixed table?")
        require(key[1] >= 1 and key[2] >= key[1], "Invalid one-based inclusive coordinates")
        mapping_rows[key].append(row)
        id_keys[seq_id] = key
    aliases = {}
    for key, rows in mapping_rows.items():
        ids = sorted({r["anonymous_contig_id"] for r in rows}, key=lambda value: (int(value[2:]), value))
        if len(ids) > 1:
            # Publisher aliases are accepted only when every other source field agrees.
            metadata = [{k: v for k, v in r.items() if k != "anonymous_contig_id"} for r in rows]
            require(len(ids) == len(rows) and all(m == metadata[0] for m in metadata),
                    f"Conflicting coordinate aliases: {key}")
            aliases[key] = ids
            mapping_rows[key] = [next(r for r in rows if r["anonymous_contig_id"] == ids[0])]
        else:
            require(len({r["genome_id"] for r in rows}) == len(rows), "Duplicate truth row")
    taxids = [r["tax_id"] for rows in mapping_rows.values() for r in rows]
    domains = domains_from_nodes(taxids, nodes) if nodes else {}
    out.mkdir(parents=True)
    records, lengths, origins, seq_groups, seen, excluded_fasta = [], {}, {}, defaultdict(list), set(), []
    # A failed conversion leaves no complete inventory marker; retain it for diagnosis.
    with (out / "canonical.fna").open("x") as handle:
        for original, sequence in sequences(fasta, skip_known_empty=True, excluded=excluded_fasta):
            match = HMP_HEADER.fullmatch(original)
            require(match is not None, f"Unexpected HMP FASTA header: {original}")
            accession, start, end, declared = match.groups()
            key = (accession, int(start), int(end))
            require(key in mapping_rows and key not in seen, f"Missing/duplicate coordinate join: {original}")
            require(len(sequence) == int(declared) == key[2] - key[1] + 1, f"Sequence/coordinate length mismatch: {original}")
            seen.add(key)
            rows = mapping_rows[key]
            seq_id = rows[0]["anonymous_contig_id"]
            genomes = sorted(r["genome_id"] for r in rows)
            domain_values = sorted({domains.get(r["tax_id"], "unknown") for r in rows})
            seqhash = hashlib.sha256(sequence.encode("ascii")).hexdigest()
            upper = sequence.upper()
            canonical_hash = hashlib.sha256(min(upper, str(Seq(upper).reverse_complement())).encode("ascii")).hexdigest()
            retained = len(sequence) >= cfg["min_contig_bp"]
            record = {"id": seq_id, "original_id": original, "length": len(sequence), "sha256": seqhash,
                      "source_anonymous_ids": aliases.get(key, [seq_id]),
                      "strand_invariant_sha256": canonical_hash, "origins": genomes, "domains": domain_values,
                      "taxids": sorted({r["tax_id"] for r in rows}), "retained": retained, "reasons": []}
            if retained:
                lengths[seq_id] = len(sequence)
                origins[seq_id] = genomes
                seq_groups[canonical_hash].append(record)
                handle.write(f">{seq_id}\n")
                for i in range(0, len(sequence), 80):
                    handle.write(sequence[i:i + 80] + "\n")
            else:
                record["reasons"].append("below_length_threshold")
            records.append(record)
    require(seen == set(mapping_rows), "Truth rows without matching FASTA coordinates")
    require(lengths, "No retained contigs")
    for group in seq_groups.values():
        cross_origin = len({g for r in group for g in r["origins"]}) > 1
        for record in group:
            if len(record["origins"]) != 1:
                record["reasons"].append("multiple_origins")
            if not set(record["domains"]) <= {"bacteria", "archaea"}:
                record["reasons"].append("unknown_or_nonprokaryotic_domain")
            if cross_origin:
                record["reasons"].append("cross_origin_identical_sequence")
    unique = {r["id"]: r["origins"][0] for r in records if r["retained"] and not r["reasons"]}
    genome_bp, genome_counts = defaultdict(int), defaultdict(int)
    for seq_id, genome in unique.items():
        genome_bp[genome] += lengths[seq_id]
        genome_counts[genome] += 1
    genomes = sorted(g for g, bp in genome_bp.items() if bp >= cfg["min_genome_bp"])
    eligible = [s for s, g in unique.items() if g in genomes and genome_counts[g] >= cfg["probe_k"] + 1]
    queries = sorted(eligible, key=lambda s: (hashlib.sha256(("E001-probe:" + s).encode()).hexdigest(), s))[:cfg["probe_max_queries"]]
    short = [s for s in queries if lengths[s] < cfg["probe_short_max_bp"]]
    gates = {
        "domains_resolved": all("unknown" not in r["domains"] for r in records if r["retained"]),
        "enough_genomes": len(genomes) >= cfg["min_genomes"],
        "enough_short_queries": len(short) >= cfg["min_short_queries"],
        "enough_short_genomes": len({unique[s] for s in short}) >= cfg["min_short_query_genomes"],
        "within_size_limit": len(lengths) <= cfg["resources"]["max_contigs"] and sum(lengths.values()) <= cfg["resources"]["max_input_bp"],
    }
    with (out / "contigs.jsonl").open("x") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    if excluded_fasta:
        write_json(out / "excluded-fasta.json", excluded_fasta)
    write_cami(out / "truth.tsv", lengths, origins=origins)
    population = {"lengths": lengths, "unique_origins": unique, "genomes": genomes,
                  "probe_pool": sorted(eligible), "probe_queries": queries, "gates": gates}
    write_json(out / "population.json", population)
    report = {"status": "validated" if all(gates.values()) else "blocked", "gates": gates,
              "excluded_fasta_records": excluded_fasta,
              "coordinate_aliases": [{"canonical_id": r["id"], "source_ids": r["source_anonymous_ids"],
                                      "original_id": r["original_id"], "length": r["length"],
                                      "retained": r["retained"], "sha256": r["sha256"]}
                                     for r in records if len(r["source_anonymous_ids"]) > 1],
              "input_contigs": len(records), "retained_contigs": len(lengths), "retained_bp": sum(lengths.values()),
              "eligible_genomes": len(genomes), "short_queries": len(short),
              "excluded_retained_bp": sum(lengths[s] for s in lengths if s not in unique),
              "source_sha256": {"fasta": digest(fasta), "mapping": digest(mapping), "nodes": digest(nodes) if nodes else None},
              "config_sha256": digest(EXPERIMENT / "config.json"),
              "outputs": {p.name: digest(p) for p in out.iterdir() if p.is_file()}}
    write_json(out / "inventory.json", report)
    return report
