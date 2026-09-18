"""Bounded acquisition and safe archive inventory. No read downloads or extraction."""

import json
import shutil
import tarfile
from pathlib import Path, PurePosixPath
from urllib.request import urlopen

from .records import EXPERIMENT, digest, require, write_json


def archive_inventory(path, max_unpacked=16_000_000_000, max_members=100000):
    members, seen, total = [], set(), 0
    with tarfile.open(path, "r|*") as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            require(not name.is_absolute() and ".." not in name.parts and "\\" not in member.name,
                    f"Unsafe archive path: {member.name}")
            require(member.isdir() or member.isfile(), f"Archive link/device rejected: {member.name}")
            require(str(name) not in seen, f"Duplicate archive member: {name}")
            seen.add(str(name))
            total += member.size
            require(total <= max_unpacked and len(seen) <= max_members, "Archive inventory exceeds limits")
            members.append({"name": member.name, "size": member.size, "kind": "file" if member.isfile() else "directory"})
    return {"sha256": digest(path), "unpacked_bytes": total, "members": members}


def download_inventory(root, execute=False):
    spec = json.loads((EXPERIMENT / "acquisition.json").read_text())
    plan = [{**item, "url": spec["base_url"] + item["path"]} for item in spec["inventory_files"]]
    if not execute:
        return {"status": "plan_only", "files": plan, "reads": "not downloaded"}
    root = Path(root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    require(shutil.disk_usage(root).free >= 10_000_000_000, "Need at least 10 GB free for inventory stage")
    require(not (root / "acquisition-report.json").exists(), "Completed acquisition already exists; use a new directory")
    report = []
    for item in plan:
        relative = PurePosixPath(item["path"])
        require(not relative.is_absolute() and ".." not in relative.parts, "Unsafe acquisition path")
        path = root / relative
        require(path.resolve().is_relative_to(root) and not path.is_symlink(), "Acquisition path escapes root")
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            partial = path.with_name(path.name + ".part")
            require(not partial.exists(), f"Partial download retained for inspection: {partial}")
            count = 0
            with urlopen(item["url"], timeout=90) as response, partial.open("xb") as handle:
                require(response.status == 200, "Expected complete HTTP 200 response")
                for block in iter(lambda: response.read(1024 * 1024), b""):
                    count += len(block)
                    require(count <= item["max_bytes"], f"Download exceeds declared limit: {path}")
                    handle.write(block)
            require(count > 0, f"Empty download: {path}")
            if item["md5"]:
                require(digest(partial, "md5") == item["md5"], f"Publisher checksum mismatch: {partial}")
            partial.rename(path)
        require(0 < path.stat().st_size <= item["max_bytes"], f"Invalid file size: {path}")
        if item["md5"]:
            require(digest(path, "md5") == item["md5"], f"Publisher checksum mismatch: {path}")
        report.append({**item, "bytes": path.stat().st_size, "sha256": digest(path), "publisher_checksum_verified": item["md5"] is not None})
    inventory = archive_inventory(root / "gastrooral/setup.tar.gz")
    write_json(root / "setup-members.json", inventory)
    result = {"status": "downloaded_and_checksummed_not_scientifically_validated", "files": report,
              "source_manifest_sha256": digest(EXPERIMENT / "acquisition.json"), "reads": "not downloaded"}
    write_json(root / "acquisition-report.json", result)
    return result
