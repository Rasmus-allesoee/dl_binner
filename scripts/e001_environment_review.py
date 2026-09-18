"""No-download origin audit and clean-environment rerun of existing native smoke."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tarfile
import time


PROBE = r'''
import importlib, importlib.metadata as md, json, os, pathlib, site, sys
prefix = pathlib.Path(sys.prefix).resolve()
distributions = []
for dist in md.distributions():
    origin = pathlib.Path(dist.locate_file("")).resolve()
    distributions.append({"name": dist.metadata.get("Name"), "version": dist.version,
                          "origin": str(origin), "inside_prefix": origin.is_relative_to(prefix)})
modules = {}
for name in (["numpy", "Bio", "pysam", "pandas"] if sys.argv[1] == "amber" else ["numpy", "Bio", "pysam"]):
    try:
        module = importlib.import_module(name)
        origin = pathlib.Path(module.__file__).resolve()
        modules[name] = {"origin": str(origin), "inside_prefix": origin.is_relative_to(prefix)}
    except Exception as error:
        modules[name] = {"error": str(error), "inside_prefix": False}
result = {"prefix": str(prefix), "executable": sys.executable, "sys_path": sys.path,
          "pythonpath": os.environ.get("PYTHONPATH"), "pythonhome": os.environ.get("PYTHONHOME"),
          "user_site_enabled": site.ENABLE_USER_SITE, "distributions": distributions, "modules": modules}
print(json.dumps(result, indent=2))
if sys.argv[2] == "clean":
    assert prefix == pathlib.Path(sys.argv[3]).resolve(), "Wrong environment prefix"
    assert not site.ENABLE_USER_SITE, "User-site is still enabled"
    assert all(d["inside_prefix"] for d in distributions), "External distribution remains visible"
    assert all(m["inside_prefix"] for m in modules.values()), "Required import outside prefix or missing"
'''


def clean_environment(environ):
    result = dict(environ)
    for key in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE"):
        result.pop(key, None)
    result.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="11",
                  OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1",
                  PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_NO_INDEX="1")
    return result


def run(argv, out, name, env):
    print("START:", name, flush=True)
    started = time.monotonic()
    status = None
    try:
        with (out / (name + ".stdout")).open("x") as stdout, (out / (name + ".stderr")).open("x") as stderr:
            process = subprocess.run(argv, stdout=stdout, stderr=stderr, env=env, timeout=1800)
        status = process.returncode
        if status:
            raise RuntimeError(f"{name} failed ({status}); return the review archive")
    finally:
        (out / (name + ".command.json")).write_text(json.dumps(
            {"argv": argv, "returncode": status, "elapsed_seconds": time.monotonic() - started}, indent=2))
    print("PASS:", name, flush=True)


def review(root):
    root = root.resolve()
    code = root / "e001-code-9c2b0ec6feb3"
    if (code / "SOURCE_COMMIT").read_text().strip() != "9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea":
        raise ValueError("Unexpected source snapshot")
    out = root / "environment-review"
    archive = root / "environment-review-return.tar.gz"
    checksum = root / (archive.name + ".sha256")
    if any(p.exists() or p.is_symlink() for p in (out, archive, checksum)):
        raise ValueError("Review outputs exist; preserve and inspect before retrying")
    out.mkdir()
    status = "failed"
    try:
        (out / "executed-review.py").write_bytes(Path(__file__).read_bytes())
        env = dict(os.environ, MAMBA_ROOT_PREFIX=str(root / "micromamba"), PYTHONDONTWRITEBYTECODE="1")
        clean = clean_environment(env)
        mamba = str(root / "bin/micromamba")
        for tool in ("mapping", "amber"):
            prefix = root / "envs" / tool
            base = [mamba, "run", "-p", str(prefix), "python"]
            for mode, variables in (("observed", env), ("clean", clean)):
                run(base + ["-c", PROBE, tool, mode, str(prefix)], out, tool + "-" + mode, variables)
            records = [json.loads(p.read_text()) for p in sorted((prefix / "conda-meta").glob("*.json"))]
            if not records:
                raise ValueError("Missing conda package records")
            fields = ("name", "version", "build", "url", "md5", "sha256", "channel", "subdir")
            (out / (tool + "-conda-records.json")).write_text(json.dumps(
                [{k: r.get(k) for k in fields} for r in records], indent=2))
            run(base + ["-m", "pip", "list", "--format=json"], out, tool + "-clean-packages", clean)
            run(base + ["-m", "pip", "check"], out, tool + "-clean-pip-check", clean)
            args = (["--fixture", str(root / "fixture")] if tool == "mapping" else
                    ["--source", str(root / "sources/AMBER_evaluation")])
            run(base + [str(code / "scripts/e001.py"), "native-smoke", tool, *args,
                        "--out", str(out / (tool + "-smoke"))], out, tool + "-clean-smoke", clean)
        status = "pass"
    finally:
        (out / "status.json").write_text(json.dumps({"status": status}))
        with tarfile.open(archive, "x:gz") as handle:
            handle.add(out, arcname=out.name)
        checksum.write_text(hashlib.sha256(archive.read_bytes()).hexdigest() + "  " + archive.name + "\n")
        print("Return:", archive, "and", checksum, flush=True)
    print("ENVIRONMENT REVIEW PASS; stop for inspection before GI acquisition.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise SystemExit("Linux x86_64 required")
    review(args.root)
