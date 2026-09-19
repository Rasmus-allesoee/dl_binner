"""Bounded publisher-header audit; no BAM alignments or full archives fetched.

Inputs are local copies of the two checksum-verified truth tables, directory
listing and first 1 MiB of setup.tar.gz. Output is a generated evidence record.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import shlex
import struct
import tarfile
from urllib.request import Request, urlopen
import zlib

BASE = "https://frl.publisso.de/data/frl%3A6425518/"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.names = []

    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get("href", "")
        if tag == "a" and href.startswith("OTU_") and href.endswith(".bam") and "/" not in href:
            self.names.append(href)


def header(name):
    url = BASE + "per_bodysite/gastro_bam/" + name
    with urlopen(Request(url, headers={"Range": "bytes=0-4095"}), timeout=30) as response:
        if response.status != 206 or not response.headers.get("Content-Range", "").startswith("bytes 0-4095/"):
            raise ValueError("Server did not honor bounded range: " + url)
        data = response.read(4097)
    if len(data) != 4096:
        raise ValueError("Unexpected header range size: " + url)
    # Decode complete BGZF members only; never attempt to parse alignments.
    raw, offset = b"", 0
    while offset + 18 <= len(data):
        size = struct.unpack_from("<H", data, offset + 16)[0] + 1
        if size < 18 or offset + size > len(data):
            break
        raw += zlib.decompress(data[offset:offset + size], wbits=31)
        offset += size
        if len(raw) >= 8 and raw[:4] == b"BAM\x01" and len(raw) >= 8 + struct.unpack_from("<i", raw, 4)[0]:
            break
    if raw[:4] != b"BAM\x01" or len(raw) < 8:
        raise ValueError("No BAM header in range: " + url)
    size = struct.unpack_from("<i", raw, 4)[0]
    if not 0 <= size <= len(raw) - 8:
        raise ValueError("Incomplete BAM header: " + url)
    sam = raw[8:8 + size].decode()
    lines = [dict(field.split(":", 1) for field in line.split("\t")[1:]) for line in sam.splitlines()]
    sequences = [row for row in lines if "SN" in row]
    commands = [row["CL"] for row in lines if "CL" in row]
    sources = [shlex.split(cmd)[shlex.split(cmd).index("-i") + 1] for cmd in commands]
    return {"url": url, "filename_genome_id": name[:-4], "range_sha256": hashlib.sha256(data).hexdigest(),
            "sam_header": sam, "references": sequences, "source_paths": sources}


def audit(fixed, original, prefix, listing):
    hashes, tables = {}, {}
    for name, path, md5 in (("fixed", fixed, "954106872f9af342c0b7fd4422d8db9f"),
                             ("original", original, "6bed38a056082b3358c8796c97f136cf")):
        data = path.read_bytes()
        if hashlib.md5(data).hexdigest() != md5:
            raise ValueError("Publisher MD5 mismatch: " + name)
        hashes[name] = {"md5": md5, "sha256": hashlib.sha256(data).hexdigest()}
        tables[name] = list(csv.DictReader(io.StringIO(data.decode()), delimiter="\t"))
    metadata = {}
    with tarfile.open(prefix, "r|gz") as archive:
        for member in archive:
            if member.name.startswith("source_genomes"):
                break
            if member.name in {"metadata.tsv", "genome_to_id.tsv", "config.ini"}:
                data = archive.extractfile(member).read()
                metadata[member.name] = {"sha256": hashlib.sha256(data).hexdigest(), "text": data.decode()}
    expected = {row[0]: Path(row[1]).name for row in csv.reader(io.StringIO(metadata["genome_to_id.tsv"]["text"]), delimiter="\t")}
    links = Links()
    links.feed(listing.read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:
        headers = list(pool.map(header, sorted(set(links.names))))
    mapping_refs = {}
    for row in tables["fixed"]:
        mapping_refs.setdefault(row["genome_id"], set()).add(row["contig_id"])
    for row in headers:
        genome = row["filename_genome_id"]
        row["setup_source_basename"] = expected.get(genome)
        row["source_matches_setup"] = bool(row["source_paths"]) and all(Path(p).name == expected.get(genome) for p in row["source_paths"])
        refs = {sq["SN"] for sq in row["references"]}
        row["truth_references_missing_from_bam"] = sorted(mapping_refs.get(genome, set()) - refs)
        row["bam_references_absent_from_truth"] = sorted(refs - mapping_refs.get(genome, set()))
    return {"date": "2026-09-19", "base_url": BASE, "table_hashes": hashes,
            "setup_prefix_sha256": hashlib.sha256(prefix.read_bytes()).hexdigest(),
            "setup_prefix_note": "Bounded HTTP prefix, not full archive checksum validation; owner full archive must match recorded member hashes.",
            "metadata": metadata, "bam_headers": headers,
            "summary": {"bam_headers": len(headers),
                        "source_mismatches": sum(not h["source_matches_setup"] for h in headers),
                        "truth_reference_mismatches": sum(bool(h["truth_references_missing_from_bam"]) for h in headers)}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("fixed", "original", "prefix", "listing", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.fixed, args.original, args.prefix, args.listing)
    with args.out.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result["summary"], indent=2))
