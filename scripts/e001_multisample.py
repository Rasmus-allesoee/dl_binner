"""Owner-run GI acquisition and Snakemake preprocessing, without model fitting.

Inputs: the existing E001 work root, an explicit persistent data root and actual
vCPU/RAM allocation. Reuse accepted sample 0 and separate tool environments.
Outputs: a unique data attempt containing nine publisher archives, validated
FASTQs, C0/CT replicate-0 BAMs, rule benchmarks and an ordered ten-sample manifest.
Small return artifacts stay under the work root. Never delete or overwrite prior
attempts. Downloads require --allow-remaining-archives; no software installation.
"""

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import traceback
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e001_vamb_cpu import invoke, require, sha
from e001_preprocess import extract, worker as preprocess_worker

CODE = Path(__file__).resolve().parents[1]
EXPERIMENT = CODE / "experiments/E001-coverage-thinning"


def write_json(path, value):
    """Write new JSON provenance exclusively, refusing an existing record."""
    with Path(path).open("x") as handle:
        json.dump(value, handle, indent=2)


def retained_bytes(stage):
    """Count existing attempt files, tolerating sort temporaries removed mid-scan."""
    total = 0
    for path in stage.rglob("*"):
        try:
            if path.is_file():
                total += path.stat().st_size
        except FileNotFoundError:
            continue
    return total


def download(item, destination):
    """Stream one size/ETag-bound archive; verify publisher MD5 and record SHA256.

    Inputs are a resolved manifest entry and new path. Preserve partial data on
    HTTP, time, size or digest failure; only rename after complete verification.
    """
    require(not destination.exists(), "Archive destination exists; preserve it")
    partial = destination.with_suffix(".gz.partial")
    started, count = time.monotonic(), 0
    md5, strong = hashlib.md5(), hashlib.sha256()
    request = urllib.request.Request(item["url"], headers={"If-Match": item["etag"]})
    with urllib.request.urlopen(request, timeout=90) as response:
        require(response.status == 200, "Expected full HTTP 200 archive")
        require(response.headers.get("ETag") == item["etag"], "Archive ETag changed")
        require(int(response.headers.get("Content-Length", -1)) == item["bytes"], "Archive size changed")
        with partial.open("xb") as handle:
            while True:
                require(time.monotonic() - started < 3600, "Download exceeded one hour; partial preserved")
                block = response.read(min(1024 * 1024, item["bytes"] - count + 1))
                if not block:
                    break
                count += len(block)
                require(count <= item["bytes"], "Archive exceeded pinned byte count")
                handle.write(block)
                md5.update(block)
                strong.update(block)
                if count // 10**9 != (count - len(block)) // 10**9:
                    print(f"Sample {item['sample']}: downloaded {count / 10**9:.1f}/{item['bytes'] / 10**9:.1f} GB", flush=True)
    require(count == item["bytes"], "Truncated archive")
    require(md5.hexdigest() == item["md5"], "Publisher MD5 mismatch; partial preserved")
    partial.rename(destination)
    return {**item, "sha256": strong.hexdigest(), "publisher_md5_verified": True,
            "elapsed_seconds": time.monotonic() - started}


@contextmanager
def progress(stage, interval=1, heartbeat=60):
    """Mirror new rule/native log text and periodic size heartbeats to terminal.

    The original files remain authoritative; progress.log is a human-readable
    derivative. A background reader never modifies native logs or process pipes.
    """
    stop = threading.Event()
    positions = {}
    started = time.monotonic()
    with (stage / "progress.log").open("x") as output:
        def emit(message):
            line = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + " " + message
            print(line, flush=True)
            output.write(line + "\n")
            output.flush()

        def tail():
            paths = [stage / "workflow.stdout", stage / "workflow.stderr"]
            paths += list(stage.glob("sample_*/logs/*.log"))
            paths += list(stage.glob("sample_*/C0/pipeline/stage-*.stderr"))
            for path in paths:
                if not path.is_file():
                    continue
                with path.open(errors="replace") as stream:
                    stream.seek(positions.get(path, 0))
                    text = stream.read()
                    positions[path] = stream.tell()
                for line in text.splitlines():
                    emit(f"[{path.relative_to(stage)}] {line}")

        def watch():
            last = 0
            while not stop.wait(interval):
                tail()
                elapsed = time.monotonic() - started
                if elapsed - last >= heartbeat:
                    done = len(list(stage.glob("sample_*/preprocessing-summary.json")))
                    size = retained_bytes(stage)
                    emit(f"RUNNING: {done}/9 new samples complete; {elapsed / 60:.1f} min; {size / 10**9:.2f} GB retained")
                    last = elapsed
            tail()

        thread = threading.Thread(target=watch, daemon=True)
        thread.start()
        try:
            yield
        finally:
            stop.set()
            thread.join()


def sample_worker(mode, config_path, sample):
    """Execute one sample rule from its resolved config; emit QC and progress.

    Acquisition validates the whole publisher payload. Extraction scans the
    selected member to EOF and checks mates/length/sample identity, without
    imposing sample 0's count on other libraries. Mapping/thinning reuse the
    accepted implementation with sample-specific read groups and index seeds.
    """
    config = json.loads(config_path.read_text())
    cfg_path = Path(config["sample_configs"][str(sample)])
    cfg = json.loads(cfg_path.read_text())
    stage = Path(cfg["stage"])
    started = time.monotonic()
    print(f"START sample {sample}: {mode}", flush=True)
    if mode == "download":
        require(shutil.disk_usage(stage).free >= config["per_sample_minimum_free_bytes"], "Insufficient remaining disk space")
        result = download(cfg["acquisition"], Path(cfg["archive"]))
        write_json(stage / "acquisition.json", result)
    elif mode == "extract":
        record = json.loads((stage / "acquisition.json").read_text())
        require(record["publisher_md5_verified"] and Path(cfg["archive"]).stat().st_size == record["bytes"], "Unverified archive")
        result = extract(Path(cfg["archive"]), stage / "reads.fq", expected_pairs=None,
                         member_name=cfg["member"], sample=sample, max_pairs=config["max_pairs_per_sample"])
        result.update(archive_sha256=record["sha256"], elapsed_seconds=time.monotonic() - started)
        write_json(stage / "reads.json", result)
    else:
        preprocess_worker(mode, cfg_path)
    print(f"PASS sample {sample}: {mode} ({time.monotonic() - started:.1f} seconds)", flush=True)


def accepted_sample0(root, observed):
    """Check accepted small records and output presence, not repeat BAM scanning.

    Return the original locator and recorded hashes. Existing BAM bytes are not
    rehashed here; scientific feature input verification can use these hashes.
    """
    records = observed["records"]
    original = Path(records["runtime.json"]["stage"])
    require(original.parent == root, "Accepted sample-0 root differs")
    for name in ("runtime.json", "status.json", "reads.json", "preprocessing-summary.json", "C0/qc.json", "CT/qc.json"):
        require(json.loads((original / name).read_text()) == records[name], "Accepted sample-0 record changed: " + name)
    for condition in ("C0", "CT"):
        bam = original / condition / "mapped.bam"
        require(bam.stat().st_size == records[f"{condition}/qc.json"]["bytes"] and
                Path(str(bam) + ".bai").is_file(), "Accepted sample-0 BAM/index missing or size changed")
    return {"sample": 0, "directory": str(original), "summary": records["preprocessing-summary.json"],
            "reuse": "Accepted prior result; record and size checks only, no remapping or rethinning"}


def aggregate(config):
    """Build ordered ten-sample BAM manifest only after all new rules succeed."""
    entries = [config["sample0"]]
    for sample in config["samples"]:
        cfg = json.loads(Path(config["sample_configs"][str(sample)]).read_text())
        folder = Path(cfg["stage"])
        summary = json.loads((folder / "preprocessing-summary.json").read_text())
        require(summary["sample"] == sample and summary["thinning_seed"] == 1000 + cfg["sample_index"], "Sample/seed mismatch")
        reads = json.loads((folder / "reads.json").read_text())
        require(0 < summary["CT"]["records"] < summary["C0"]["records"] <= 2 * reads["pairs"], "Inconsistent BAM/read counts")
        entries.append({"sample": sample, "directory": str(folder), "summary": summary, "reads": reads})
    write_json(Path(config["stage"]) / "bam-manifest.json", {
        "scope": "C0 and CT replicate 0 only; no scientific training or scoring",
        "source_commit": config["source_commit"], "reference": config["reference"],
        "reference_sha256": config["reference_sha256"], "samples": entries})


def run(root, data_root, cpus, ram_gb, allow_downloads):
    """Probe existing runtimes, run one serial multi-sample DAG, package evidence.

    Explicit data-root prevents silent migration to shared storage. The 80
    allocated-core-hour group ceiling includes acquisition and waiting inside
    this driver, and leaves headroom under E001's 200-hour preprocessing ceiling.
    A failure preserves completed samples and partial files for targeted recovery.
    """
    require(allow_downloads, "Explicit --allow-remaining-archives required")
    require(root.is_absolute() and root.is_dir() and data_root.is_absolute() and data_root.is_dir(), "Existing absolute work/data roots required")
    require(cpus >= 3 and ram_gb >= 6, "Need at least 3 vCPU and 6 GB RAM")
    stage = Path(tempfile.mkdtemp(prefix="multisample-preprocess-", dir=data_root))
    started, status = time.monotonic(), 1
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE", "SNAKEMAKE_PROFILE", "SNAKEMAKE_WORKFLOW_PROFILE")}
    env.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1",
               OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               XDG_CACHE_HOME=str(root / "cache"))
    try:
        plan = json.loads((EXPERIMENT / "multisample-plan.json").read_text())
        require(shutil.disk_usage(stage).free >= plan["new_data_free_space_bytes"], "Need 275 GB free for retained new data; preserve existing files")
        acquisition = json.loads((EXPERIMENT / "acquisition.json").read_text())
        sources = {i["sample"]: i for i in acquisition["read_archives_not_authorized_by_inventory"]}
        frozen = json.loads((EXPERIMENT / "frozen-inputs.json").read_text())
        require(sha(EXPERIMENT / "config.json") == frozen["config_sha256"], "Frozen scientific configuration changed")
        samples = [i["sample"] for i in plan["samples"]]
        require([0] + samples == frozen["samples"], "Plan does not match frozen sample order")
        previous = accepted_sample0(root, json.loads((EXPERIMENT / "sample0-preprocess-observed.json").read_text()))
        mapping = root / "envs/mapping/bin/python"
        workflow = root / "envs/workflow/bin/snakemake"
        env["PATH"] = str(workflow.parent) + os.pathsep + env.get("PATH", "")
        env["TMPDIR"] = str(stage / "tmp")
        Path(env["TMPDIR"]).mkdir()
        probe = ("import sys,site,Bio,pysam; from pathlib import Path; p=Path(sys.argv[1]).resolve(); "
                 "assert Path(sys.prefix).resolve()==p and not site.ENABLE_USER_SITE; "
                 "assert all(Path(m.__file__).resolve().is_relative_to(p) for m in (Bio,pysam)); print(sys.version)")
        invoke([mapping, "-I", "-c", probe, mapping.parent.parent], env, stage, "mapping-environment", 60)
        for tool, expected in (("strobealign", "0.17.0"), ("samtools", "1.24")):
            version = subprocess.check_output([mapping.parent / tool, "--version"], env=env, text=True).splitlines()[0]
            require(version.split()[-1].lstrip("v") == expected, "Changed mapping executable: " + tool)
        version = subprocess.check_output([workflow, "--version"], env=env, text=True).strip()
        require(version == "9.13.7", "Missing/changed workflow environment; no reinstall")
        invoke([workflow.parent / "python", "-I", "-m", "pip", "freeze"], env, stage, "workflow-lock", 60)
        config = {**plan, "stage": str(stage), "root": str(root), "samples": samples,
                  "vcpus": cpus, "ram_gb": ram_gb, "sample_configs": {}, "sample0": previous,
                  "source_commit": (CODE / "SOURCE_COMMIT").read_text().strip(),
                  "reference": str(Path(frozen["owner_input_directory"]) / "canonical.fna"),
                  "reference_sha256": frozen["outputs"]["canonical.fna"],
                  "helper": str(CODE / "scripts/e001_multisample.py"), "mapping_python": str(mapping),
                  "runtime_config": str(stage / "runtime.json")}
        require(sha(Path(config["reference"])) == config["reference_sha256"], "Frozen reference changed")
        for item in plan["samples"]:
            sample = item["sample"]
            folder = stage / f"sample_{sample}"
            (folder / "logs").mkdir(parents=True)
            source = {**sources[sample], **item, "url": acquisition["base_url"] + sources[sample]["path"]}
            cfg = {"stage": str(folder), "root": str(root), "sample": sample,
                   "sample_index": frozen["samples"].index(sample), "vcpus": cpus,
                   "archive": str(folder / "source.tar.gz"), "member": item["directory"] + "/reads/anonymous_reads.fq",
                   "reference": config["reference"], "reference_sha256": config["reference_sha256"], "acquisition": source}
            path = folder / "runtime.json"
            write_json(path, cfg)
            config["sample_configs"][str(sample)] = str(path)
        write_json(stage / "runtime.json", config)
        cmd = [workflow, "--snakefile", CODE / "workflows/e001-preprocess/multisample.smk",
               "--directory", stage, "--configfile", stage / "runtime.json", "--cores", cpus,
               "--executor", "local", "--printshellcmds", "--keep-incomplete", "--benchmark-extended"]
        invoke(cmd + ["--dry-run"], env, stage, "dag", 120)
        with progress(stage):
            remaining = plan["group_core_hour_limit"] * 3600 / cpus - (time.monotonic() - started)
            require(remaining > 0, "Group compute ceiling exhausted")
            invoke(cmd, env, stage, "workflow", remaining)
        aggregate(config)
        status = 0
    except Exception:
        write_json(stage / "failure.json", {"traceback": traceback.format_exc()})
        print(traceback.format_exc(), file=sys.stderr)
    finally:
        elapsed = time.monotonic() - started
        write_json(stage / "status.json", {"exit_code": status, "actual_vcpus": cpus, "actual_ram_gb": ram_gb,
            "elapsed_seconds": elapsed, "allocated_core_hours": elapsed * cpus / 3600,
            "attempt_bytes": retained_bytes(stage),
            "note": "Excludes prior sample 0, environments and owner idle time outside this driver"})
        archive = root / (stage.name + "-return.tar.gz")
        try:
            with tarfile.open(archive, "x:gz") as tar:
                for path in stage.rglob("*"):
                    if path.is_file() and path.suffix in (".json", ".log", ".stdout", ".stderr", ".tsv", ".txt"):
                        tar.add(path, arcname=stage.name + "/" + str(path.relative_to(stage)))
            Path(str(archive) + ".sha256").write_text(sha(archive) + "  " + archive.name + "\n")
            print("RETURN:", archive, "and .sha256", flush=True)
        except Exception:
            status = 1
            record = json.loads((stage / "status.json").read_text())
            record.update(exit_code=1, packaging_failed=True)
            (stage / "status.json").write_text(json.dumps(record, indent=2))
            (stage / "packaging-failed.txt").write_text(traceback.format_exc())
            print("Packaging failed; preserve attempt and return terminal log:", stage, file=sys.stderr)
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?")
    parser.add_argument("--data-root", type=Path)
    parser.add_argument("--vcpus", type=int)
    parser.add_argument("--ram-gb", type=float)
    parser.add_argument("--allow-remaining-archives", action="store_true")
    parser.add_argument("--worker", choices=("download", "extract", "map", "thin"))
    parser.add_argument("--config", type=Path)
    parser.add_argument("--sample", type=int)
    args = parser.parse_args()
    if args.worker:
        if args.config is None or args.sample is None:
            parser.error("Worker requires --config and --sample")
        sample_worker(args.worker, args.config, args.sample)
    else:
        if any(v is None for v in (args.root, args.data_root, args.vcpus, args.ram_gb)):
            parser.error("root, --data-root, --vcpus and --ram-gb required")
        raise SystemExit(run(args.root, args.data_root, args.vcpus, args.ram_gb, args.allow_remaining_archives))
