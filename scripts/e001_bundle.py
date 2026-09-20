"""Package committed E001 execution files, never local caches or research data."""

import argparse
import hashlib
import io
from pathlib import Path
import subprocess
import tarfile


PATHS = (
    "scripts/e001.py", "scripts/e001lib", "scripts/e001_bundle.py",
    "scripts/e001_linux_setup.sh", "scripts/e001_linux_smoke.sh",
    "scripts/e001_ucloud_preflight.sh",
    "scripts/e001_environment_review.py",
    "scripts/e001_gi_inventory.sh",
    "scripts/e001_hmp_audit.sh",
    "scripts/e001_inventory_resume.py",
    "scripts/e001_vamb_cpu.py",
    "scripts/e001_retry_conversion.sh",
    "tests", "experiments/E001-coverage-thinning",
    "docs/evidence/2026-09-17-tool-snapshots.json",
)


def build(repo, destination):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(repo), *args])

    if git("status", "--porcelain", "--untracked-files=normal"):
        raise ValueError("Commit or review outstanding changes before packaging")
    commit = git("rev-parse", "HEAD").decode().strip()
    name = "e001-code-" + commit[:12]
    payload = git("archive", "--format=tar", "HEAD", "--", *PATHS)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / (name + ".tar.gz")
    checksum = destination / (archive.name + ".sha256")
    if archive.exists() or checksum.exists():
        raise ValueError("Transfer files already exist; preserve them")
    with tarfile.open(fileobj=io.BytesIO(payload)) as source:
        members = source.getmembers()
        if any(not (m.isfile() or m.isdir()) for m in members):
            raise ValueError("Only regular committed files and directories may be transferred")
        with archive.open("xb") as output, tarfile.open(fileobj=output, mode="w:gz") as target:
            for member in members:
                member.name = name + "/" + member.name
                target.addfile(member, source.extractfile(member) if member.isfile() else None)
            provenance = (commit + "\n").encode()
            info = tarfile.TarInfo(name + "/SOURCE_COMMIT")
            info.size = len(provenance)
            info.mode = 0o644
            target.addfile(info, io.BytesIO(provenance))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    with checksum.open("x") as stream:
        stream.write(f"{digest}  {archive.name}\n")
    return archive, checksum


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    for path in build(Path(__file__).resolve().parents[1], args.out):
        print(path)
