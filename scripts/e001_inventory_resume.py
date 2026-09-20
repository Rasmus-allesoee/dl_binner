"""Owner-run GI inventory on a fresh job, using persistent files and environments.

No installation or network access. Each invocation creates a separate attempt;
old attempts are never renamed, deleted or reused. Conversion requires --convert.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback


def digest(path, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(root, code, convert=False, taxonomy=None):
    require(root.is_absolute() and root.is_dir(), "Existing absolute work root required")
    stage = Path(tempfile.mkdtemp(prefix="inventory-resume-", dir=root))
    started, status = time.monotonic(), 1
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE")}
    env.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1",
               OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    prefix = root / "envs/mapping"
    env["PATH"] = str(prefix / "bin") + os.pathsep + env.get("PATH", "")
    python = prefix / "bin/python"

    def command(label, args):
        print("START: " + label, flush=True)
        (stage / (label + ".command.json")).write_text(json.dumps([str(a) for a in args]) + "\n")
        with (stage / (label + ".stdout")).open("x") as out, (stage / (label + ".stderr")).open("x") as err:
            result = subprocess.run([str(a) for a in args], env=env, stdout=out, stderr=err, timeout=600)
        require(result.returncode == 0, label + " failed:\n" + (stage / (label + ".stderr")).read_text()[-6000:])
        print("PASS: " + label, flush=True)

    try:
        source = (code / "SOURCE_COMMIT").read_text().strip()
        require(len(source) == 40 and all(c in "0123456789abcdef" for c in source), "Invalid SOURCE_COMMIT")
        (stage / "provenance.json").write_text(json.dumps({
            "source_commit": source, "platform": platform.platform(), "hostname": platform.node(),
            "convert_requested": convert, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "code_sha256": {str(p.relative_to(code)): digest(p) for p in
                            (code / "scripts/e001_inventory_resume.py", code / "scripts/e001.py",
                             code / "scripts/e001lib/records.py", code / "scripts/e001lib/taxonomy.py")}}, indent=2) + "\n")
        require(python.is_file() and os.access(python, os.X_OK), "Persistent mapping Python is missing; preserve files and return logs")
        command("environment", [python, "-I", "-c",
                "import sys,site,json; from pathlib import Path; import Bio,numpy,pysam; "
                "p=Path(sys.argv[1]).resolve(); assert Path(sys.prefix).resolve()==p; "
                "assert not site.ENABLE_USER_SITE; "
                "assert all(Path(m.__file__).resolve().is_relative_to(p) for m in (Bio,numpy,pysam)); "
                "print(json.dumps({'python':sys.version,'prefix':str(p),'Bio':Bio.__version__}))", prefix])
        policy_path = code / "experiments/E001-coverage-thinning/gi-input-policy.json"
        policy = json.loads(policy_path.read_text())
        (stage / "policy.json").write_text(policy_path.read_text())
        taxonomy_args = []
        taxonomy_policy = None
        inventory = root / "inventory"
        gi = inventory / "per_bodysite/gastro_bam"
        setup = inventory / "gastrooral/setup.tar.gz"
        require(digest(gi / "gsa_pooled_mapping.tsv", "md5") == policy["original_mapping_md5"], "Original mapping checksum mismatch")
        require(digest(setup, "md5") == policy["setup_md5"], "Setup archive checksum mismatch")
        found = {}
        # Stream the checked archive; materialize only the three small metadata members.
        with tarfile.open(setup, "r|gz") as archive:
            for member in archive:
                if member.name not in policy["setup_member_sha256"]:
                    continue
                require(member.isfile() and 0 <= member.size <= 1_000_000, "Unexpected metadata member")
                data = archive.extractfile(member).read()
                require(hashlib.sha256(data).hexdigest() == policy["setup_member_sha256"][member.name], "Setup member checksum mismatch: " + member.name)
                found[member.name] = hashlib.sha256(data).hexdigest()
                if len(found) == len(policy["setup_member_sha256"]):
                    break
        require(set(found) == set(policy["setup_member_sha256"]), "Required setup metadata missing")
        (stage / "setup-verified.json").write_text(json.dumps(found, indent=2) + "\n")
        inputs = ["--fasta", gi / "gsa.fa", "--mapping", gi / "gsa_pooled_mapping_fixed.tsv"]
        command("audit", [python, "-s", code / "scripts/e001.py", "audit-hmp", *inputs, "--out", stage / "audit.json"])
        audit = json.loads((stage / "audit.json").read_text())
        require(audit["source_sha256"] == policy["source_sha256"], "GI source hashes differ from reviewed audit")
        require(audit["fasta_keys_missing_mapping_count"] == len(policy["quarantine"]), "Unexpected unmatched-key count")
        for field in ("mapping_keys_missing_fasta_count", "fasta_duplicate_coordinate_count", "fasta_duplicate_id_count",
                      "fasta_malformed_header_count", "fasta_invalid_dna_count", "fasta_length_mismatch_count",
                      "mapping_invalid_coordinate_count", "mapping_conflicting_coordinate_count"):
            require(audit[field] == 0, "Unreviewed input anomaly: " + field)
        require(audit["mapping_contract_error"] is None, "Invalid truth mapping")
        require(audit["excluded_known_empty_count"] == policy["expected_empty_records"], "Unexpected empty records")
        if taxonomy is not None:
            require(convert, "Taxonomy requires --convert")
            taxonomy_path = code / "experiments/E001-coverage-thinning/taxonomy-policy.json"
            taxonomy_policy = json.loads(taxonomy_path.read_text())
            (stage / "taxonomy-policy.json").write_text(taxonomy_path.read_text())
            command("taxonomy", [python, "-s", "-c",
                    "import sys; sys.path.insert(0,sys.argv[1]); from e001lib.taxonomy import prepare; "
                    "prepare(*sys.argv[2:])", code / "scripts", taxonomy, taxonomy_path,
                    gi / "gsa_pooled_mapping_fixed.tsv", stage / "taxonomy"])
            taxonomy_args = ["--nodes", stage / "taxonomy/nodes.dmp"]
        if convert:
            command("conversion", [python, "-s", code / "scripts/e001.py", "prepare-hmp", *inputs,
                                   "--policy", policy_path, *taxonomy_args, "--out", stage / "input"])
            report = json.loads((stage / "input/inventory.json").read_text())
            if taxonomy_policy is not None:
                for name, expected in taxonomy_policy["invariant_outputs"].items():
                    require(report["outputs"][name] == expected, "Taxonomy changed input: " + name)
                for name, expected in taxonomy_policy["expected_population"].items():
                    require(report[name] == expected, "Population differs from local validation: " + name)
                require(report["status"] == "validated", "Scientific population gates remain blocked")
            print("Conversion complete; scientific population status: " + report["status"], flush=True)
        status = 0
    except Exception:
        message = traceback.format_exc()
        (stage / "failure.txt").write_text(message)
        print(message, file=sys.stderr)
    finally:
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        (stage / "status.json").write_text(json.dumps({
            "exit_code": status, "elapsed_seconds": time.monotonic() - started,
            "children_user_seconds": usage.ru_utime, "children_system_seconds": usage.ru_stime,
            "children_maxrss": usage.ru_maxrss, "maxrss_units": "bytes" if sys.platform == "darwin" else "KiB",
            "note": "Process statistics, not allocated core-hours; includes completed child processes only."}, indent=2) + "\n")
        returned = root / (stage.name + "-return.tar.gz")
        try:
            with returned.open("xb") as handle, tarfile.open(fileobj=handle, mode="w:gz") as archive:
                for path in sorted(stage.iterdir()):
                    if path.is_file():
                        archive.add(path, arcname=stage.name + "/" + path.name)
                for name in ("inventory.json", "excluded-fasta.json"):
                    path = stage / "input" / name
                    if path.is_file():
                        archive.add(path, arcname=stage.name + "/input/" + name)
                coverage = stage / "taxonomy/coverage.json"
                if coverage.is_file():
                    archive.add(coverage, arcname=stage.name + "/taxonomy/coverage.json")
            with Path(str(returned) + ".sha256").open("x") as handle:
                handle.write(digest(returned) + "  " + returned.name + "\n")
            print("RETURN: " + str(returned) + " and .sha256", flush=True)
        except Exception:
            status = 1
            (stage / "packaging-failed.txt").write_text(traceback.format_exc())
            summary = json.loads((stage / "status.json").read_text())
            summary.update(exit_code=1, packaging_failed=True)
            (stage / "status.json").write_text(json.dumps(summary, indent=2) + "\n")
            print("Packaging failed; preserve " + str(stage), file=sys.stderr)
            traceback.print_exc()
    print("RESUME EXIT CODE: " + str(status), flush=True)
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--convert", action="store_true")
    parser.add_argument("--taxonomy", type=Path, help="Local pinned CAMI taxonomy archive; no download")
    args = parser.parse_args()
    raise SystemExit(run(args.root, Path(__file__).resolve().parents[1], args.convert, args.taxonomy))
