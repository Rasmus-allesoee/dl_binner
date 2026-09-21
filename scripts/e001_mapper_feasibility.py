"""Compare native mappers on 100,000 GI read pairs without training.

Owner driver inputs: persistent E001 root, actual vCPU/RAM allocation and either
an existing publisher sample-0 archive or explicit permission to download that
single archive. Outputs: a unique attempt with prefix FASTQs, mapper indexes/BAMs,
timings, storage measurements and a small return archive. Original inputs and
accepted environments are never changed. Bowtie2 gets its own persistent prefix.
This is an input-order prefix, not a representative scientific sample.
"""

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e001_vamb_cpu import invoke, require, sha

URL = "https://frl.publisso.de/data/frl%3A6425518/gastrooral/sample_0.tar.gz"
ARCHIVE_BYTES = 9738621091
ETAG = '"2447790a3-5d68d6c44295d"'
# The publisher's outer sample archive places the FASTQ below ``short_read/``.
# Keep the complete member path pinned: choosing an arbitrary FASTQ from this
# archive could silently select a different read product or metadata payload.
MEMBER = "short_read/2017.12.04_18.45.54_sample_0/reads/anonymous_reads.fq.gz"
PAIRS = 100000


def acquire(destination):
    """Download one explicitly authorized publisher archive; return provenance.

    Enforce pinned size/ETag before reading, bound response bytes, hash the full
    payload and preserve partial files on failure. No automatic fallback/retry.
    """
    partial = destination.with_suffix(destination.suffix + ".partial")
    started = time.monotonic()
    print("Downloading one sample archive (9.74 GB); preserving it for reuse", flush=True)
    request = urllib.request.Request(URL, headers={"If-Match": ETAG})
    with urllib.request.urlopen(request, timeout=60) as response:
        require(response.status == 200, "Unexpected archive response")
        require(response.headers.get("ETag") == ETAG, "Publisher archive changed")
        require(int(response.headers.get("Content-Length", -1)) == ARCHIVE_BYTES, "Archive size changed")
        count = 0
        with partial.open("xb") as out:
            while True:
                require(time.monotonic() - started < 3600, "Download exceeded one-hour timeout; partial preserved")
                block = response.read(min(1024 * 1024, ARCHIVE_BYTES - count + 1))
                if not block:
                    break
                count += len(block)
                require(count <= ARCHIVE_BYTES, "Archive exceeded byte limit")
                out.write(block)
                if count // 10**9 != (count - len(block)) // 10**9:
                    print(f"Downloaded {count / 10**9:.1f} GB", flush=True)
        require(count == ARCHIVE_BYTES, "Truncated archive")
    partial.rename(destination)
    return {"url": URL, "etag": ETAG, "bytes": count, "sha256": sha(destination)}


def extract_prefix(archive, out, pairs=PAIRS):
    """Stream the exact nested FASTQ member into paired files; return hashes.

    Use Biopython's FASTQ parser, validate mate identity/orientation and 150 bp
    lengths, and stop after complete pairs. Do not extract BAMs or other members.
    The full outer archive is checked separately; the inner gzip is prefix-only.
    """
    from Bio.SeqIO.QualityIO import FastqGeneralIterator
    out.mkdir()
    with tarfile.open(archive, "r|gz") as tar:
        for member in tar:
            if member.name.lstrip("./") != MEMBER:
                continue
            require(member.isfile(), "Read member is not a regular file")
            with gzip.GzipFile(fileobj=tar.extractfile(member)) as compressed, \
                 io.TextIOWrapper(compressed, encoding="ascii") as text, \
                 (out / "R1.fq").open("x") as r1, (out / "R2.fq").open("x") as r2:
                records = iter(FastqGeneralIterator(text))
                for _ in range(pairs):
                    a, b = next(records, None), next(records, None)
                    require(a is not None and b is not None, "Insufficient complete pairs")
                    x, y = a[0].split()[0], b[0].split()[0]
                    require(x.removesuffix("/1") == y.removesuffix("/2"), "Mismatched mate IDs")
                    require(not x.endswith("/2") and not y.endswith("/1"), "Reversed mates")
                    for record, handle in ((a, r1), (b, r2)):
                        require(len(record[1]) == 150, "Unexpected read length")
                        handle.write(f"@{record[0]}\n{record[1]}\n+\n{record[2]}\n")
            return {"pairs": pairs, "member": MEMBER,
                    "sha256": {name: sha(out / name) for name in ("R1.fq", "R2.fq")}}
    raise ValueError("Expected sample-0 read member absent")


def map_worker(root, stage, cpus):
    """Map identical paired prefixes to the frozen reference with both tools.

    Reuse mapping environment plus isolated Bowtie2 binaries. Write full SAMs,
    primary mapped sorted BAMs, native logs, elapsed times and descriptive
    alignment agreement. Truth is not used; mapper agreement is not accuracy.
    """
    import pysam
    from e001lib.smoke import bam_inventory
    code = Path(__file__).resolve().parents[1]
    frozen = json.loads((code / "experiments/E001-coverage-thinning/frozen-inputs.json").read_text())
    reference = Path(frozen["owner_input_directory"]) / "canonical.fna"
    require(sha(reference) == frozen["outputs"]["canonical.fna"], "Frozen reference changed")
    env = dict(os.environ)
    mapping = root / "envs/mapping/bin"
    bowtie = root / "envs/bowtie2/bin"
    versions = {name: subprocess.check_output([str(path), "--version"], text=True).splitlines()[0]
                for name, path in (("strobealign", mapping / "strobealign"),
                                   ("samtools", mapping / "samtools"), ("bowtie2", bowtie / "bowtie2"))}
    require(versions["strobealign"].split()[-1].lstrip("v") == "0.17.0", "Wrong strobealign")
    require("2.5.4" in versions["bowtie2"], "Wrong Bowtie2")
    require(versions["samtools"].split()[1] == "1.24", "Wrong samtools")
    index = stage / "bowtie-index"
    index.mkdir()
    invoke([bowtie / "bowtie2-build", "--threads", cpus, reference, index / "gi"], env, stage, "bowtie-index", 1800)
    summaries, placements = {}, {}
    for tool in ("strobealign", "bowtie2"):
        out = stage / tool
        out.mkdir()
        sam, bam = out / "full.sam", out / "mapped.bam"
        reads = [stage / "reads/R1.fq", stage / "reads/R2.fq"]
        if tool == "strobealign":
            cmd = [mapping / tool, "-t", cpus, "-r", 150, reference, *reads]
        else:
            cmd = [bowtie / tool, "-p", cpus, "-x", index / "gi", "-1", reads[0], "-2", reads[1]]
        # Native stdout is SAM; invoke captures it without a shell pipeline.
        invoke(cmd, env, stage, tool + "-map", 1800)
        (stage / (tool + "-map.stdout")).rename(sam)
        invoke([mapping / "samtools", "view", "-b", "-F", 2308, "-o", out / "unsorted.bam", sam], env, stage, tool + "-filter", 300)
        invoke([mapping / "samtools", "sort", "-@", max(0, cpus - 1), "-m", "256M", "-o", bam, out / "unsorted.bam"], env, stage, tool + "-sort", 300)
        invoke([mapping / "samtools", "index", bam], env, stage, tool + "-index", 300)
        summary = bam_inventory(bam, reference)
        require(summary["records"] > 0, "No mapped prefix reads")
        seen, total = {}, 0
        with pysam.AlignmentFile(sam, "r") as alignments:
            for rec in alignments:
                if rec.is_secondary or rec.is_supplementary:
                    continue
                total += 1
                require(rec.is_paired and rec.is_read1 != rec.is_read2, "Invalid primary mate flags")
                key = (rec.query_name, rec.is_read2)
                require(key not in seen, "Duplicate primary mate")
                seen[key] = None if rec.is_unmapped else (rec.reference_name, rec.reference_start, rec.is_reverse)
        require(total == 2 * PAIRS, "Primary read count changed")
        placements[tool] = seen
        summary.update(primary_records=total, bam_bytes=bam.stat().st_size,
                       bam_bytes_per_input_pair=bam.stat().st_size / PAIRS)
        summaries[tool] = summary
    a, b = placements.values()
    require(a.keys() == b.keys(), "Mappers saw different reads")
    report = {"versions": versions, "tools": summaries,
              "same_mapped_position_reads": sum(a[k] is not None and a[k] == b[k] for k in a),
              "both_unmapped_reads": sum(a[k] is None and b[k] is None for k in a),
              "child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              "scope": "Input-order prefix only; agreement is not accuracy; index/build cost separated from mapping; no whole-dataset throughput guarantee"}
    (stage / "mapping-summary.json").write_text(json.dumps(report, indent=2))


def run(args):
    """Run setup, authorized acquisition, prefix validation and mapping as one task.

    Preserve a unique attempt and package small diagnostics even on failure.
    Allocation is owner-supplied, not inferred from the host or recommendation.
    """
    root = args.root.resolve()
    require(root.is_dir() and args.vcpus >= 1 and args.ram_gb > 0, "Invalid root/allocation")
    require(args.archive is not None or args.allow_sample_archive, "Supply --archive or explicitly authorize --allow-sample-archive")
    stage = Path(tempfile.mkdtemp(prefix="mapper-feasibility-", dir=root))
    start, status = time.monotonic(), 1
    code = Path(__file__).resolve().parents[1]
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE")}
    env.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
    env["MAMBA_ROOT_PREFIX"] = str(root / "micromamba")
    try:
        (stage / "provenance.json").write_text(json.dumps({"source_commit": (code / "SOURCE_COMMIT").read_text().strip(),
            "driver_sha256": sha(Path(__file__)), "owner_vcpus": args.vcpus, "owner_ram_gb": args.ram_gb}, indent=2))
        free = shutil.disk_usage(stage).free
        require(free >= (8 if args.archive else 20) * 10**9, "Insufficient free space; choose reviewed storage, do not delete prior work")
        prefix = root / "envs/bowtie2"
        if not prefix.exists():
            invoke([root / "bin/micromamba", "create", "-y", "-p", prefix, "-c", "conda-forge", "-c", "bioconda",
                    "--strict-channel-priority", "bowtie2=2.5.4"], env, stage, "bowtie-setup", 1800)
        require((prefix / "bin/bowtie2").is_file(), "Incomplete Bowtie2 environment; preserved for inspection")
        invoke([root / "bin/micromamba", "list", "-p", prefix, "--explicit"], env, stage, "bowtie-lock", 60)
        archive = args.archive.resolve() if args.archive else stage / "sample_0.tar.gz"
        provenance = acquire(archive) if args.archive is None else {"local_path": str(archive), "sha256": sha(archive), "bytes": archive.stat().st_size}
        require(archive.stat().st_size == ARCHIVE_BYTES, "Unexpected supplied archive size")
        (stage / "acquisition.json").write_text(json.dumps(provenance, indent=2))
        python = root / "envs/mapping/bin/python"
        invoke([python, "-I", Path(__file__), "--extract", archive, stage / "reads"], env, stage, "prefix", 1800)
        invoke([python, "-I", Path(__file__), "--map", root, stage, args.vcpus], env, stage, "mapping", 5400)
        status = 0
    except Exception:
        (stage / "failure.txt").write_text(traceback.format_exc())
        print(traceback.format_exc(), file=sys.stderr)
    finally:
        elapsed = time.monotonic() - start
        (stage / "status.json").write_text(json.dumps({"exit_code": status, "elapsed_seconds": elapsed,
            "allocated_core_hours": args.vcpus * elapsed / 3600, "vcpus": args.vcpus,
            "attempt_bytes": sum(p.stat().st_size for p in stage.rglob("*") if p.is_file())}, indent=2))
        archive = root / (stage.name + "-return.tar.gz")
        with tarfile.open(archive, "x:gz") as tar:
            for p in stage.rglob("*"):
                if p.is_file() and p.suffix in (".json", ".stderr", ".stdout", ".txt"):
                    if p.name in ("strobealign-map.stdout", "bowtie2-map.stdout"):
                        continue
                    tar.add(p, arcname=stage.name + "/" + str(p.relative_to(stage)))
        Path(str(archive) + ".sha256").write_text(sha(archive) + "  " + archive.name + "\n")
        print("RETURN:", archive, "and .sha256")
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?")
    parser.add_argument("--vcpus", type=int)
    parser.add_argument("--ram-gb", type=float)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--archive", type=Path)
    group.add_argument("--allow-sample-archive", action="store_true")
    group.add_argument("--extract", nargs=2)
    group.add_argument("--map", nargs=3)
    args = parser.parse_args()
    if args.extract:
        archive, out = map(Path, args.extract)
        result = extract_prefix(archive, out)
        (out / "prefix.json").write_text(json.dumps(result, indent=2))
    elif args.map:
        root, stage, cpus = args.map
        map_worker(Path(root), Path(stage), int(cpus))
    else:
        if args.root is None or args.vcpus is None or args.ram_gb is None:
            parser.error("root, --vcpus and --ram-gb are required")
        raise SystemExit(run(args))
