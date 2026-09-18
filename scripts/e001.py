#!/usr/bin/env python3
"""E001 Gate 0 checks and bounded Gate 1 preparation; no research training runner."""

import argparse
import json
from pathlib import Path
import sys

from e001lib.acquire import archive_inventory, download_inventory
from e001lib.metrics import score
from e001lib.native import verify_source
from e001lib.records import ContractError, digest, partition, prepare_hmp, require, validate_attempt, write_cami, write_json
from e001lib.smoke import amber_smoke, feature_smoke, make_fixture, mapping_smoke, metabat_smoke


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    acquire = sub.add_parser("acquire", help="Inventory downloads only; dry run unless --execute")
    acquire.add_argument("--root", required=True, type=Path)
    acquire.add_argument("--execute", action="store_true")
    archive = sub.add_parser("archive-inventory")
    archive.add_argument("archive", type=Path)
    archive.add_argument("--out", required=True, type=Path)
    prepare = sub.add_parser("prepare-hmp")
    prepare.add_argument("--fasta", required=True, type=Path)
    prepare.add_argument("--mapping", required=True, type=Path)
    prepare.add_argument("--nodes", type=Path)
    prepare.add_argument("--out", required=True, type=Path)
    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--population", required=True, type=Path)
    evaluate.add_argument("--assignments", required=True, type=Path)
    evaluate.add_argument("--attempt", required=True, type=Path, help="Completed scientific attempt with input/output hashes")
    evaluate.add_argument("--layout", choices=["cami", "vamb", "comebin", "metabat"], default="cami")
    evaluate.add_argument("--out", required=True, type=Path)
    fixture = sub.add_parser("fixture")
    fixture.add_argument("--out", required=True, type=Path)
    source = sub.add_parser("verify-source")
    source.add_argument("tool", choices=["metabat", "vamb", "COMEBin", "AMBER_evaluation"])
    source.add_argument("source", type=Path)
    smoke = sub.add_parser("native-smoke")
    smoke.add_argument("tool", choices=["mapping", "metabat", "vamb", "comebin", "amber"])
    smoke.add_argument("--source", type=Path)
    smoke.add_argument("--fixture", type=Path)
    smoke.add_argument("--mapping", type=Path)
    smoke.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = None
    if args.command == "acquire":
        result = download_inventory(args.root, args.execute)
    elif args.command == "archive-inventory":
        result = archive_inventory(args.archive)
        write_json(args.out, result)
    elif args.command == "prepare-hmp":
        result = prepare_hmp(args.fasta, args.mapping, args.out, args.nodes)
    elif args.command == "evaluate":
        population = json.loads(args.population.read_text())
        require(population.get("gates") and all(population["gates"].values()), "Population is not validated/frozen")
        inventory = json.loads((args.population.parent / "inventory.json").read_text())
        require(inventory.get("status") == "validated" and inventory["outputs"][args.population.name] == digest(args.population), "Population integrity/validation mismatch")
        attempt = validate_attempt(args.attempt, args.assignments, args.population)
        assignments = partition(args.assignments, population["lengths"], args.layout)
        result = score(population, assignments)
        result["attempt"] = attempt
        args.out.mkdir(parents=True, exist_ok=False)
        write_cami(args.out / "predictions.tsv", population["lengths"], assignments=assignments)
        write_json(args.out / "metrics.json", result)
    elif args.command == "fixture":
        make_fixture(args.out)
    elif args.command == "verify-source":
        result = verify_source(args.tool, args.source)
    else:
        require(args.tool == "mapping" or args.source is not None, "--source required")
        require(args.tool == "amber" or args.fixture is not None, "--fixture required")
        if args.tool == "mapping":
            mapping_smoke(args.fixture, args.out)
        elif args.tool == "amber":
            amber_smoke(args.source, args.out)
        elif args.tool == "metabat":
            metabat_smoke(args.source, args.fixture, args.out)
        else:
            require(args.mapping is not None, "--mapping required")
            feature_smoke(args.tool, args.source, args.fixture, args.mapping, args.out)
    if result is not None:
        print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ContractError, OSError, ValueError) as error:
        print(f"E001 check failed: {error}", file=sys.stderr)
        raise SystemExit(1)
