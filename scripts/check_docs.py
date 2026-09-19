#!/usr/bin/env python3
"""Check maintained Markdown links and optional local source fingerprints."""

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
OPTIONAL = (ROOT / "agent_context",)


def optional(path):
    return any(path.is_relative_to(directory) for directory in OPTIONAL)


def nodes(value):
    if isinstance(value, dict):
        if "t" in value:
            yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


@lru_cache(maxsize=None)
def parse(path):
    result = subprocess.run(
        ["pandoc", "--from=gfm", "--to=json", str(path)],
        check=True, capture_output=True, text=True,
    )
    return list(nodes(json.loads(result.stdout)))


def maintained_files():
    paths = {ROOT / name for name in ("README.md", "AGENTS.md", "PROJECT_INTENT.md")}
    paths.update(path for path in (ROOT / "docs").rglob("*.md")
                 if not path.is_relative_to(ROOT / "docs/history"))
    paths.update((ROOT / "experiments").rglob("*.md"))
    paths.add(ROOT / "docs/history/README.md")
    return sorted(paths)


def check_links(paths):
    errors, missing_cache = [], set()
    count = 0
    for source in paths:
        label = source.relative_to(ROOT)
        for node in parse(source):
            if node["t"] not in ("Link", "Image"):
                continue
            target = node["c"][-1][0]
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            count += 1
            destination = (source.parent / unquote(url.path)).resolve() if url.path else source
            if not destination.is_relative_to(ROOT):
                errors.append(f"{label}: link leaves repository: {target}")
                continue
            if not destination.exists():
                if optional(destination):
                    missing_cache.add(str(destination.relative_to(ROOT)))
                else:
                    errors.append(f"{label}: missing target: {target}")
                continue
            if url.fragment and destination.suffix == ".md":
                identifiers = {item["c"][1][0] for item in parse(destination)
                               if item["t"] == "Header"}
                if unquote(url.fragment) not in identifiers:
                    errors.append(f"{label}: missing heading: {target}")
    return errors, missing_cache, count


def check_context():
    errors, missing_cache = [], set()
    count = 0
    manifest = ROOT / "docs/evidence/context-sources.sha256"
    seen = set()
    for line_number, line in enumerate(manifest.read_text().splitlines(), 1):
        digest, separator, filename = line.partition("  ")
        if not separator or not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"{manifest.name}:{line_number}: invalid checksum entry")
            continue
        path = (ROOT / filename).resolve()
        if path in seen or not path.is_relative_to(ROOT):
            errors.append(f"{manifest.name}:{line_number}: duplicate or invalid path")
            continue
        seen.add(path)
        if not path.is_file():
            if optional(path):
                missing_cache.add(filename)
            else:
                errors.append(f"Missing recorded source: {filename}")
            continue
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
        if hasher.hexdigest() != digest:
            errors.append(f"Recorded source has changed: {filename}")
        count += 1
    return errors, missing_cache, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-context", action="store_true",
                        help="Also verify present files against recorded source hashes")
    args = parser.parse_args()
    if not shutil.which("pandoc"):
        print("Pandoc is required to parse Markdown links; no checks performed.", file=sys.stderr)
        return 2
    paths = maintained_files()
    errors, missing_cache, link_count = check_links(paths)
    source_count = 0
    if args.check_context:
        source_errors, source_missing, source_count = check_context()
        errors.extend(source_errors)
        missing_cache.update(source_missing)
    print(f"Checked {len(paths)} maintained documents and {link_count} local links.")
    if args.check_context:
        print(f"Checked {source_count} present source fingerprints.")
    if missing_cache:
        print(f"Optional local cache files unavailable: {len(missing_cache)} (not verified).")
        for filename in sorted(missing_cache):
            print(f"  {filename}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print("FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Documentation check could not complete: {error}", file=sys.stderr)
        raise SystemExit(2)
