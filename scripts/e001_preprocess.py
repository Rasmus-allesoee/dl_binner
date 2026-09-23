"""Run the E001 sample-0 Snakemake preprocessing slice, without training.

Inputs: persistent root and actual allocation (at least three vCPUs for the
mapper/filter/sort pipeline). Outputs: a unique attempt with full validated
sample FASTQ, C0 BAM, seeded 10% CT BAM, QC and compact return artifacts. Only
an isolated workflow-engine environment may be installed. No research data
downloads, deletion of existing outputs, model fitting or biological scoring.
"""

import argparse
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e001_vamb_cpu import invoke, require, sha
from e001_mapper_feasibility import MEMBER, _MemberReader

ARCHIVE_SHA = "6f349a6f3299b4595f8c5acfb9ad7d8e2fc56fe657c1a451cde90e92c364f113"
EXPECTED_PAIRS = 16666043


def extract(archive, output, expected_pairs=EXPECTED_PAIRS, member_name=MEMBER, sample=None, max_pairs=20000000):
    """Stream a named plain FASTQ and validate every mate pair and read length.

    Write one interleaved file and return its count/hash. Preserve partial output
    on failure; never select another archive member or truncate to fit the count.
    An exact truth-derived count is required for sample 0. Other samples use
    expected_pairs=None, complete member EOF and a resource-only upper bound;
    optional sample checks their anonymous-ID prefix, not genome-origin truth.
    """
    from Bio.SeqIO.QualityIO import FastqGeneralIterator
    with tarfile.open(archive, "r|gz") as tar:
        for member in tar:
            if member.name != member_name:
                continue
            require(member.isfile(), "Anonymous reads must be a regular member")
            count = 0
            with io.TextIOWrapper(io.BufferedReader(_MemberReader(tar.extractfile(member))), encoding="ascii") as text, output.open("x") as out:
                records = iter(FastqGeneralIterator(text))
                for a in records:
                    b = next(records, None)
                    require(b is not None, "Odd number of reads")
                    x, y = a[0].split()[0], b[0].split()[0]
                    require(x.removesuffix("/1") == y.removesuffix("/2") and
                            not x.endswith("/2") and not y.endswith("/1"), "Invalid mate IDs")
                    if sample is not None:
                        require(x.startswith(f"S{sample}R"), "Read belongs to a different sample")
                    for record in (a, b):
                        require(len(record[1]) == 150, "Unexpected read length")
                        out.write(f"@{record[0]}\n{record[1]}\n+\n{record[2]}\n")
                    count += 1
                    require(count <= max_pairs, "Read count exceeds resource bound")
                    if expected_pairs is not None:
                        require(count <= expected_pairs, "More pairs than verified read truth")
                    if count % 1000000 == 0:
                        print(f"Validated {count:,} pairs", flush=True)
            require(count > 0, "Empty FASTQ")
            if expected_pairs is not None:
                require(count == expected_pairs, "Pair count differs from complete sample-0 truth")
            return {"pairs": count, "member": member_name, "bytes": output.stat().st_size, "sha256": sha(output)}
    raise ValueError("Inventoried anonymous FASTQ member missing")


def worker(mode, config_path):
    """Execute one rule with isolated mapping tools; write QC only on success."""
    from e001lib.native import mapping_commands, pipeline, thinning_command
    from e001lib.smoke import bam_inventory
    cfg = json.loads(config_path.read_text())
    stage, root = Path(cfg["stage"]), Path(cfg["root"])
    env = dict(os.environ, PATH=str(root / "envs/mapping/bin") + os.pathsep + os.environ.get("PATH", ""))
    os.environ.update(env)
    start = time.monotonic()
    reference = Path(cfg["reference"])
    sample, sample_index = cfg.get("sample", 0), cfg.get("sample_index", 0)
    print(f"START sample {sample}: {mode}", flush=True)
    if mode == "extract":
        require(sha(Path(cfg["archive"])) == ARCHIVE_SHA, "Existing sample archive changed")
        result = extract(Path(cfg["archive"]), stage / "reads.fq")
        result["elapsed_seconds"] = time.monotonic() - start
        (stage / "reads.json").write_text(json.dumps(result, indent=2))
        return
    require(sha(reference) == cfg["reference_sha256"], "Frozen reference changed")
    for tool, version in (("strobealign", "0.17.0"), ("samtools", "1.24")):
        first = subprocess.check_output([tool, "--version"], text=True).splitlines()[0]
        require(first.split()[-1].lstrip("v") == version, "Tool version changed: " + tool)
    label = "C0" if mode == "map" else "CT"
    out = stage / label
    out.mkdir(exist_ok=True)
    bam = out / "mapped.bam"
    require(not bam.exists(), "Refusing to overwrite previous BAM")
    if mode == "map":
        # Reserve one CPU each for samtools view and single-threaded sort.
        commands = mapping_commands(reference, stage / "reads.fq", f"E001-sample{sample}", bam,
                                    mapper_threads=cfg["vcpus"] - 2, sort_extra_threads=0)
        pipeline(commands, out / "pipeline")
    else:
        invoke(thinning_command(stage / "C0/mapped.bam", bam, replicate=0, sample_index=sample_index), env, out, "thin", 1800)
    invoke(["samtools", "index", bam], env, out, "index", 300)
    result = bam_inventory(bam, reference)
    require(result["records"] > 0, "No mapped records")
    result.update(bytes=bam.stat().st_size, elapsed_seconds=time.monotonic() - start)
    (out / "qc.json").write_text(json.dumps(result, indent=2))
    if mode == "thin":
        full = json.loads((stage / "C0/qc.json").read_text())
        require(result["records"] < full["records"], "Thinning did not reduce records")
        summary = {"sample": sample, "C0": full, "CT": result, "thinning_seed": 1000 + sample_index,
                   "thinning_fraction": 0.1, "observed_record_fraction": result["records"] / full["records"],
                   "scope": "Full-sample preprocessing, replicate 0 only; no features, training or biological scores"}
        (stage / "preprocessing-summary.json").write_text(json.dumps(summary, indent=2))
    print(f"PASS sample {sample}: {mode} ({time.monotonic() - start:.1f} seconds)", flush=True)


def run(root, cpus, ram_gb):
    """Install/reuse isolated workflow engine, execute a bounded DAG, package QC.

    Record actual allocation and locks. Keep incomplete outputs; another call
    creates a separate attempt. Neither existing attempts nor source inputs move.
    """
    require(root.is_absolute() and root.is_dir(), "Existing absolute root required")
    require(cpus >= 3 and ram_gb > 0, "At least three vCPUs required for the concurrent pipeline")
    stage = Path(tempfile.mkdtemp(prefix="sample0-preprocess-", dir=root))
    code = Path(__file__).resolve().parents[1]
    start, status = time.monotonic(), 1
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE", "SNAKEMAKE_PROFILE")}
    env.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MAMBA_ROOT_PREFIX=str(root / "micromamba"), XDG_CACHE_HOME=str(root / "cache"))
    try:
        require(shutil.disk_usage(stage).free >= 25 * 10**9, "Need 25 GB free for new reads/BAMs; preserve existing data")
        frozen = json.loads((code / "experiments/E001-coverage-thinning/frozen-inputs.json").read_text())
        cfg = {"root": str(root), "stage": str(stage), "vcpus": cpus, "ram_gb": ram_gb,
               "archive": str(root / "mapper-feasibility-13l53afq/sample_0.tar.gz"),
               "reference": str(Path(frozen["owner_input_directory"]) / "canonical.fna"),
               "reference_sha256": frozen["outputs"]["canonical.fna"],
               "mapping_python": str(root / "envs/mapping/bin/python"), "helper": str(Path(__file__).resolve()),
               "runtime_config": str(stage / "runtime.json"), "source_commit": (code / "SOURCE_COMMIT").read_text().strip()}
        (stage / "runtime.json").write_text(json.dumps(cfg, indent=2))
        require(Path(cfg["archive"]).is_file(), "Accepted archive missing; no automatic download")
        prefix = root / "envs/workflow"
        if not prefix.exists():
            invoke([root / "bin/micromamba", "create", "-y", "-p", prefix, "-c", "conda-forge",
                    "python=3.12.10", "pip=25.1.1"], env, stage, "workflow-env", 900)
            invoke([prefix / "bin/python", "-I", "-m", "pip", "install", "snakemake==9.13.7"], env, stage, "workflow-install", 900)
        env["PATH"] = str(prefix / "bin") + os.pathsep + env.get("PATH", "")
        version = subprocess.check_output([prefix / "bin/snakemake", "--version"], env=env, text=True).strip()
        require(version == "9.13.7", "Incomplete or different workflow environment; preserved")
        invoke([prefix / "bin/python", "-I", "-m", "pip", "freeze"], env, stage, "workflow-lock", 60)
        cmd = [prefix / "bin/snakemake", "--snakefile", code / "workflows/e001-preprocess/Snakefile",
               "--directory", stage, "--configfile", stage / "runtime.json", "--cores", cpus,
               "--printshellcmds", "--keep-incomplete"]
        invoke(cmd + ["--dry-run"], env, stage, "dag", 120)
        invoke(cmd, env, stage, "workflow", 3600)
        status = 0
    except Exception:
        (stage / "failure.txt").write_text(traceback.format_exc())
        print(traceback.format_exc(), file=sys.stderr)
    finally:
        elapsed = time.monotonic() - start
        (stage / "status.json").write_text(json.dumps({"exit_code": status, "elapsed_seconds": elapsed,
            "actual_vcpus": cpus, "actual_ram_gb": ram_gb, "allocated_core_hours": cpus * elapsed / 3600,
            "attempt_bytes": sum(p.stat().st_size for p in stage.rglob("*") if p.is_file())}, indent=2))
        archive = root / (stage.name + "-return.tar.gz")
        with tarfile.open(archive, "x:gz") as tar:
            for path in stage.rglob("*"):
                if path.is_file() and path.suffix in (".json", ".log", ".stdout", ".stderr", ".txt"):
                    tar.add(path, arcname=stage.name + "/" + str(path.relative_to(stage)))
        Path(str(archive) + ".sha256").write_text(sha(archive) + "  " + archive.name + "\n")
        print("RETURN:", archive, "and .sha256", flush=True)
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?")
    parser.add_argument("--vcpus", type=int)
    parser.add_argument("--ram-gb", type=float)
    parser.add_argument("--worker", choices=("extract", "map", "thin"))
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    if args.worker:
        require(args.config is not None, "Worker config required")
        worker(args.worker, args.config)
    else:
        if args.root is None or args.vcpus is None or args.ram_gb is None:
            parser.error("root, --vcpus and --ram-gb required")
        raise SystemExit(run(args.root, args.vcpus, args.ram_gb))
