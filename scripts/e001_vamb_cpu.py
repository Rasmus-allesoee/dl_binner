"""Owner-run VAMB installation, native smoke and synthetic CPU feasibility only."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback

SCHEDULE = [(256, 25), (512, 50), (1024, 75), (2048, 75), (4096, 75)]


def projected_core_hours(rows, allocation):
    return allocation * sum(max(r["measured_epoch_seconds"]) * r["schedule_epochs"] for r in rows) / 3600


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def invoke(args, env, stage, label, limit):
    """Run one labelled command and preserve its streams and outcome.

    Inputs: argv, an isolated child environment, an existing attempt directory,
    a unique stage label and a wall-time limit in seconds. Outputs: a zero exit
    status or an exception, plus exclusive stdout/stderr/command JSON records.
    Timed-out process groups are killed and their final return code is recorded.
    """
    print("START: " + label, flush=True)
    started = time.monotonic()
    record = {"argv": [str(a) for a in args], "timeout_seconds": limit}
    failure = None
    try:
        with (stage / (label + ".stdout")).open("x") as out, (stage / (label + ".stderr")).open("x") as err:
            try:
                process = subprocess.Popen(record["argv"], env=env, stdout=out, stderr=err, start_new_session=True)
            except OSError as exc:
                record["launch_error"] = repr(exc)
                raise
            try:
                record["returncode"] = process.wait(timeout=limit)
            except subprocess.TimeoutExpired as exc:
                record["timed_out"] = True
                record["timeout_error"] = f"exceeded {limit} seconds"
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                record["returncode"] = process.wait()
                raise subprocess.TimeoutExpired(f"{label}: {record['argv']!r}", limit) from exc
            except BaseException:
                # Child workers must not survive an interrupted parent command.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                record["returncode"] = process.wait()
                record["interrupted"] = True
                raise
        if record["returncode"] != 0:
            record["failure"] = "nonzero exit status"
            raise RuntimeError(f"{label} failed with return code {record['returncode']}; see captured stderr")
    except BaseException as exc:
        failure = exc
        record.setdefault("failure", f"{type(exc).__name__}: {exc}")
        raise
    finally:
        record["elapsed_seconds"] = time.monotonic() - started
        (stage / (label + ".command.json")).write_text(json.dumps(record, indent=2) + "\n")
        if failure is not None:
            print(f"FAIL: {label}: {failure}; logs and command record retained in {stage}", file=sys.stderr, flush=True)
    print("PASS: " + label, flush=True)


def measure(source, out, allocation):
    import numpy as np
    import torch
    import dadaptation
    from e001lib.native import verify_source, require_packages
    from e001lib.records import config, write_json
    code = Path(__file__).resolve().parents[1]
    provenance = verify_source("vamb", source)
    require_packages({"torch": "2.6.0+cpu", "numpy": "1.26.4", "dadaptation": "3.2"})
    sys.path.insert(0, str(source))
    import vamb
    require(Path(vamb.__file__).resolve().is_relative_to(source.resolve()), "Wrong VAMB import")
    frozen = json.loads((code / "experiments/E001-coverage-thinning/frozen-inputs.json").read_text())
    require(sha(code / "experiments/E001-coverage-thinning/config.json") == frozen["config_sha256"], "Changed frozen configuration")
    n, nsamples = frozen["retained_contigs"], len(frozen["samples"])
    torch.set_num_threads(max(1, allocation - 1))
    torch.set_num_interop_threads(1)
    rng = np.random.default_rng(11)
    coverage = rng.lognormal(size=(n, nsamples)).astype(np.float32)
    composition = rng.normal(size=(n, 103)).astype(np.float32)
    lengths = rng.integers(2500, 100000, size=n)
    rows = []
    # The CLI uses 300 epochs, unlike encode.trainmodel's 500-epoch API default.
    for batch, epochs in SCHEDULE:
        loader = vamb.encode.make_dataloader(coverage, composition, lengths, batchsize=batch, cuda=False)
        model = vamb.encode.VAE(nsamples=nsamples, cuda=False, seed=11)
        optimizer = dadaptation.DAdaptAdam(model.parameters(), decouple=True)
        seconds = []
        before = next(model.parameters()).detach().clone()
        for iteration in range(3):
            started = time.monotonic()
            loader = model.trainepoch(loader, iteration, optimizer, [])
            seconds.append(time.monotonic() - started)
            require(all(torch.isfinite(p).all().item() for p in model.parameters()), "Nonfinite CPU parameters")
        require(not torch.equal(before, next(model.parameters()).detach()), "Native optimizer did not update parameters")
        rows.append({"batch_size": batch, "schedule_epochs": epochs, "warmup_seconds": seconds[0],
                     "measured_epoch_seconds": seconds[1:], "batches_per_epoch": len(loader)})
    fit_hours = projected_core_hours(rows, allocation)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    report = {**provenance, "scope": "Synthetic CPU timing only; no research features, labels or saved model",
              "status": "measured", "contigs": n, "samples": nsamples, "seed": 11,
              "allocated_vcpus": allocation, "torch_threads": torch.get_num_threads(),
              "epochs": rows, "projected_fit_core_hours": fit_hours,
              "twofold_margin_fit_core_hours": 2 * fit_hours,
              "maxrss": usage.ru_maxrss, "maxrss_units": "bytes" if sys.platform == "darwin" else "KiB",
              "limits": config()["resources"],
              "limitations": "Projection excludes extraction, clustering, other tools and real-data effects; not scientific launch approval."}
    write_json(out, report)


def run(root, code, allocation=4):
    require(root.is_absolute() and root.is_dir(), "Existing absolute work root required")
    require(allocation == 4, "This bounded preflight is prepared for 4 allocated vCPUs")
    stage = Path(tempfile.mkdtemp(prefix="native-vamb-", dir=root))
    started, status = time.monotonic(), 1
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE", "PIP_NO_INDEX")}
    env.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="11",
               OMP_NUM_THREADS="3", MKL_NUM_THREADS="3", OPENBLAS_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    prefix = root / "envs/vamb"
    env["PATH"] = os.pathsep.join([str(prefix / "bin"), str(root / "bin"), env.get("PATH", "")])
    try:
        require(platform.system() == "Linux" and platform.machine() == "x86_64", "Linux x86_64 required")
        source_commit = (code / "SOURCE_COMMIT").read_text().strip()
        require(len(source_commit) == 40 and all(c in "0123456789abcdef" for c in source_commit), "Invalid source commit")
        (stage / "provenance.json").write_text(json.dumps({"source_commit": source_commit,
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "allocated_vcpus": allocation, "platform": platform.platform(), "hostname": platform.node(),
            "driver_sha256": sha(code / "scripts/e001_vamb_cpu.py"),
            "frozen_inputs_sha256": sha(code / "experiments/E001-coverage-thinning/frozen-inputs.json")}, indent=2))
        for binary in ("bash", "git", "sha256sum"):
            require(shutil.which(binary, path=env["PATH"]), "Missing prerequisite: " + binary)
        fixture = root / "fixture"
        mapping = root / "environment-review/mapping-smoke"
        if not mapping.is_dir():
            mapping = root / "smoke/mapping"
        require((fixture / "fixture.fna").is_file() and len(list((mapping / "CT").glob("*.bam"))) == 2,
                "Existing accepted synthetic fixture/CT BAMs missing")
        if not prefix.exists():
            mamba = root / "bin/micromamba"
            require(mamba.is_file() and sha(mamba) == "366cd9cd8be14df1ab8ed50352a82111082a36686b2d389fdb79a92c3fafb3e3", "Missing or changed persistent micromamba")
            invoke(["bash", code / "scripts/e001_linux_setup.sh", "vamb", root], env, stage, "setup", 2700)
        else:
            lock = root / "locks/vamb/setup.exit-code.txt"
            require(lock.is_file() and lock.read_text().strip() == "0", "Existing VAMB setup is incomplete; preserve and inspect")
        python = prefix / "bin/python"
        probe = ("import sys,site,json,torch,numpy,Bio,pysam,pycoverm,vamb; from pathlib import Path; "
                 "p=Path(sys.argv[1]).resolve(); assert Path(sys.prefix).resolve()==p; "
                 "assert not site.ENABLE_USER_SITE; assert torch.version.cuda is None; "
                 "assert all(Path(m.__file__).resolve().is_relative_to(p) for m in (torch,numpy,Bio,pysam,pycoverm,vamb)); "
                 "print(json.dumps({'python':sys.version,'torch':torch.__version__,'numpy':numpy.__version__,'prefix':str(p)}))")
        invoke([python, "-I", "-c", probe, prefix], env, stage, "environment", 120)
        invoke([python, "-I", "-m", "pip", "check"], env, stage, "pip-check", 120)
        invoke([python, "-s", code / "scripts/e001.py", "native-smoke", "vamb", "--source", root / "sources/vamb",
                "--fixture", fixture, "--mapping", mapping, "--out", stage / "smoke"], env, stage, "smoke", 600)
        invoke([python, "-s", code / "scripts/e001_vamb_cpu.py", "--measure", root / "sources/vamb",
                stage / "cpu.json"], env, stage, "cpu", 600)
        status = 0
    except Exception:
        (stage / "failure.txt").write_text(traceback.format_exc())
        print(traceback.format_exc(), file=sys.stderr)
    finally:
        (stage / "status.json").write_text(json.dumps({"exit_code": status, "elapsed_seconds": time.monotonic() - started,
            "allocated_vcpus": allocation, "driver_allocated_core_hours": allocation * (time.monotonic() - started) / 3600,
            "note": "Excludes owner job time outside this driver."}, indent=2))
        try:
            returned = root / (stage.name + "-return.tar.gz")
            with tarfile.open(returned, "x:gz") as archive:
                archive.add(stage, arcname=stage.name)
                if (root / "locks/vamb").is_dir():
                    archive.add(root / "locks/vamb", arcname=stage.name + "/locks")
            Path(str(returned) + ".sha256").write_text(sha(returned) + "  " + returned.name + "\n")
            print("RETURN: " + str(returned) + " and .sha256", flush=True)
        except Exception:
            status = 1
            (stage / "packaging-failed.txt").write_text(traceback.format_exc())
            (stage / "status.json").write_text(json.dumps({"exit_code": 1, "packaging_failed": True}))
            print("Packaging failed; preserve " + str(stage), file=sys.stderr)
    print("VAMB PREFLIGHT EXIT CODE: " + str(status), flush=True)
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?")
    parser.add_argument("--measure", type=Path, nargs=2, metavar=("SOURCE", "OUT"))
    args = parser.parse_args()
    if args.measure:
        measure(*args.measure, allocation=4)
    else:
        parser.error("root is required") if args.root is None else None
        raise SystemExit(run(args.root, Path(__file__).resolve().parents[1]))
