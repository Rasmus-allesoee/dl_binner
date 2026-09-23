"""Stage the reviewed Linux workflow snapshot on job-local storage, without installs.

The input is the owner's SHA256-bound archive, not an arbitrary Conda prefix.
Extract only regular files/directories into a fresh /tmp directory; preserve the
original environment and archive. Write provenance to the persistent attempt.
The caller must validate the relocated interpreter and CLI before running rules.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import tempfile

SHA256 = "0fb6955cdc6263079d2f8f1a32c14037c29d5c90d16c3b3be233ea257c6ab103"
BYTES = 267595287


def stage_snapshot(archive, record_path, scratch=Path("/tmp"), expected_sha=SHA256,
                   expected_bytes=BYTES):
    """Verify an archive and return a fresh prefix; retain it even on failure.

    Only the newly created scratch directory is written. The persistent JSON
    records the input digest, runtime path and extracted size. No package files
    or entry-point shebangs are rewritten; execution must use prefix/bin/python.
    """
    archive, scratch = Path(archive), Path(scratch)
    if archive.stat().st_size != expected_bytes:
        raise ValueError("Workflow snapshot byte count differs from reviewed archive")
    if shutil.disk_usage(scratch).free < 2_000_000_000:
        raise ValueError("Need 2 GB free on job-local scratch")
    digest = hashlib.sha256()
    with archive.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != expected_sha:
        raise ValueError("Workflow snapshot SHA256 mismatch")
    destination = Path(tempfile.mkdtemp(prefix="e001-workflow-", dir=scratch))
    record = {"archive": str(archive), "sha256": expected_sha,
              "prefix": str(destination / "workflow"), "status": "extracting"}
    Path(record_path).write_text(json.dumps(record, indent=2) + "\n")
    seen, size = set(), 0
    print("Staging verified workflow snapshot on local scratch: " + str(destination), flush=True)
    with tarfile.open(archive, "r|gz") as source:
        for member in source:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or ".." in path.parts or not path.parts
                    or path.parts[0] != "workflow" or member.name in seen
                    or not (member.isdir() or member.isfile())):
                raise ValueError("Unsafe/duplicate workflow snapshot member: " + member.name)
            seen.add(member.name)
            target = destination.joinpath(*path.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                size += member.size
                if size > 1_000_000_000:
                    raise ValueError("Workflow snapshot exceeds extracted-size bound")
                target.parent.mkdir(parents=True, exist_ok=True)
                with source.extractfile(member) as src, target.open("xb") as dst:
                    shutil.copyfileobj(src, dst)
                target.chmod(member.mode & 0o777)
    prefix = destination / "workflow"
    if not os.access(prefix / "bin/python", os.X_OK):
        raise ValueError("Snapshot lacks executable Python")
    record.update(status="extracted", members=len(seen), extracted_bytes=size)
    Path(record_path).write_text(json.dumps(record, indent=2) + "\n")
    print("Snapshot ready; native prefix/package checks are still required", flush=True)
    return prefix


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    stage_snapshot(args.archive, args.record)
