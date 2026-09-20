"""Verify the pinned historical taxonomy; extract only its nodes table."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import tarfile

from .records import digest, domains_from_nodes, require, table, write_json


def prepare(archive_path, policy_path, mapping, out):
    policy = json.loads(Path(policy_path).read_text())
    require(digest(archive_path) == policy["archive_sha256"], "Taxonomy archive checksum mismatch")
    require(digest(mapping) == policy["mapping_sha256"], "Taxonomy mapping checksum mismatch")
    out = Path(out)
    require(not out.exists(), "Taxonomy output already exists")
    out.mkdir()
    found = {}
    # Never extract archive paths. Only nodes.dmp is written to a fixed local path.
    with tarfile.open(archive_path, "r|gz") as archive:
        for member in archive:
            require(member.name in policy["members"] and member.name not in found,
                    "Unexpected or duplicate taxonomy member")
            expected = policy["members"][member.name]
            require(member.isfile() and member.size == expected["size"], "Invalid taxonomy member")
            h = hashlib.sha256()
            output = (out / "nodes.dmp").open("xb") if member.name == "nodes.dmp" else None
            try:
                with archive.extractfile(member) as handle:
                    for block in iter(lambda: handle.read(1024 * 1024), b""):
                        h.update(block)
                        if output is not None:
                            output.write(block)
            finally:
                if output is not None:
                    output.close()
            require(h.hexdigest() == expected["sha256"], "Taxonomy member checksum mismatch")
            found[member.name] = h.hexdigest()
    require(set(found) == set(policy["members"]), "Missing taxonomy member")
    genomes = defaultdict(set)
    for row in table(mapping, ("genome_id", "tax_id")):
        genomes[row["genome_id"]].add(row["tax_id"])
    require(all(len(ids) == 1 for ids in genomes.values()), "Conflicting genome tax IDs")
    domains = domains_from_nodes({t for ids in genomes.values() for t in ids}, out / "nodes.dmp")
    require("unknown" not in domains.values(), "Unresolved historical tax IDs")
    counts = dict(Counter(domains[next(iter(ids))] for ids in genomes.values()))
    require(len(domains) == policy["taxid_count"] and counts == policy["genome_domains"],
            "Taxonomy coverage differs from reviewed population")
    report = {"archive_sha256": digest(archive_path), "policy_sha256": digest(policy_path),
              "members": found, "taxid_domains": domains, "genome_domains": counts,
              "genome_taxids": {g: next(iter(ids)) for g, ids in sorted(genomes.items())}}
    write_json(out / "coverage.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("archive", "policy", "mapping", "out"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    prepare(args.archive, args.policy, args.mapping, args.out)
