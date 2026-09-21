"""Bounded native clustering/marker/evaluator integration; no model fitting or downloads."""

import argparse
import hashlib
import json
import logging
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import time
import traceback
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e001_vamb_cpu import invoke, require, sha


def prepare(input_dir, out, frozen):
    from e001lib.records import sequences, write_cami
    for name in ("canonical.fna", "contigs.jsonl"):
        require(sha(input_dir / name) == frozen["outputs"][name], "Changed frozen input: " + name)
    candidates = [(hashlib.sha256(("E001-integration:" + name).encode()).hexdigest(), name)
                  for name, seq in sequences(input_dir / "canonical.fna") if 10000 <= len(seq) <= 100000]
    require(len(candidates) >= 128, "Insufficient bounded marker fixture")
    selected = {name for _, name in sorted(candidates)[:128]}
    out.mkdir()
    lengths = {}
    with (out / "fixture.fna").open("x") as handle:
        for name, seq in sequences(input_dir / "canonical.fna"):
            if name in selected:
                lengths[name] = len(seq)
                handle.write(f">{name}\n{seq}\n")
    origins = {}
    with (input_dir / "contigs.jsonl").open() as handle:
        for line in handle:
            row = json.loads(line)
            if row["id"] in selected:
                origins[row["id"]] = row["origins"]
    require(set(origins) == selected, "Missing fixture truth")
    write_cami(out / "truth.tsv", lengths, origins=origins)
    (out / "fixture.json").write_text(json.dumps({"lengths": lengths, "fasta_sha256": sha(out / "fixture.fna"),
        "scope": "Integration fixture only; hash-selected lengths 10-100 kb; not the frozen evaluation population"}, indent=2))


def cluster_worker(tool, source, fixture, out):
    import numpy as np
    from e001lib.native import verify_source
    from e001lib.records import write_cami
    provenance = verify_source("COMEBin" if tool == "comebin" else "vamb", source)
    info = json.loads((fixture / "fixture.json").read_text())
    lengths = info["lengths"]
    ids = list(lengths)
    lens = np.array(list(lengths.values()), dtype=np.int64)
    rng = np.random.default_rng(11)
    out.mkdir()
    if tool == "vamb":
        sys.path.insert(0, str(source))
        import vamb
        import torch
        torch.set_num_threads(4)
        predictions = {}
        matrix = rng.normal(size=(len(ids), 32)).astype(np.float32)
        for i, cluster in enumerate(vamb.cluster.ClusterGenerator(matrix, lens, cuda=False, rng_seed=11)):
            for index in cluster.members:
                require(ids[index] not in predictions, "Repeated VAMB assignment")
                predictions[ids[index]] = str(i)
        require(set(predictions) == set(ids), "Incomplete VAMB partition")
        report = {"clusters": len(set(predictions.values()))}
    else:
        sys.path.insert(0, str(source / "COMEBin"))
        from utils import gen_seed, configure_reproducibility
        from embedding_bundle import publish_embedding_bundle
        from cluster import cluster
        from leiden_grid import validate_leiden_output_set
        from get_final_result import run_get_final_result, _profile_marker_tables, Markers, select_best_result
        from checkm.defaultValues import DefaultValues
        data = Path(DefaultValues.CHECKM_DATA_DIR)
        require(data.resolve() == (Path(sys.prefix) / "checkm_data").resolve(), "Unexpected CheckM data root")
        payloads = {str(p.relative_to(data)): sha(p) for p in
                    (data / "hmms/checkm.hmm", data / "pfam/Pfam-A.hmm.dat", data / "pfam/tigrfam2pfam.tsv")}
        (out / "checkm-payloads.json").write_text(json.dumps(payloads, indent=2))
        configure_reproducibility(11)
        logger = logging.getLogger("E001-integration")
        logging.basicConfig(level=logging.INFO)
        # Marker tools create sidecars, so give them an attempt-local sequence copy.
        fasta = out / "fixture.fna"
        import shutil
        shutil.copyfile(fixture / "fixture.fna", fasta)
        seed_count = gen_seed(logger, str(fasta), 8, 1001, marker_name="bacar_marker", quarter="2quarter")
        for name in ("random.npy", "coverage.npy"):
            np.save(out / name, rng.normal(size=(len(ids), 128)).astype(np.float32))
        publish_embedding_bundle(out, out / "random.npy", out / "coverage.npy", ids, lens, 128, 128)
        args = SimpleNamespace(contig_file=str(fasta), output_path=str(out),
            emb_file=str(out / "embeddings.npy"), seed_file=str(fasta) + ".bacar_marker.2quarter_lencutoff_1001.seed",
            contig_len=1001, cluster_num=0, not_l2normaize=False, num_threads=8,
            leiden_workers=2, max_edges=100, seed=11, bac_mg_table=None, ar_mg_table=None)
        cluster(logger, args)
        names, rows = validate_leiden_output_set(out / "cluster_res", 100, expected_rows=len(ids))
        bac, ar = _profile_marker_tables(logger, args, seed_count, 8, "binary-labels", None)
        require(bac.is_file() and ar.is_file(), "Native CheckM tables missing; inspect stage logs")
        args.bac_mg_table, args.ar_mg_table = str(bac), str(ar)
        run_get_final_result(logger, args, seed_count, num_threads=8)
        markers = Markers()
        markers.marker_gene_tables(str(bac), str(ar))
        require(markers.bac_markers_on_contigs or markers.ar_markers_on_contigs, "No profiled markers in integration fixture")
        _, best, _ = select_best_result(out / "cluster_res", names, "binary-labels", ids, markers)
        labels = np.load(out / "cluster_res" / best, allow_pickle=False)
        predictions = {name: str(int(label)) for name, label in zip(ids, labels)}
        report = {"seed_count": seed_count, "candidate_count": len(names), "rows_per_candidate": rows,
                  "winning_candidate": best, "full_labels_sha256": sha(out / "cluster_res" / best),
                  "candidate_sha256": {name: sha(out / "cluster_res" / name) for name in names}}
    write_cami(out / "predictions.tsv", lengths, assignments=predictions)
    report.update(provenance=provenance, status="pass", assigned_contigs=len(predictions),
                  scope="Random embeddings, native clustering; no learned representation or biological performance claim")
    (out / "integration.json").write_text(json.dumps(report, indent=2))


def evaluate(source, fixture, predictions, out):
    from e001lib.native import verify_source
    from e001lib.records import partition
    verify_source("AMBER_evaluation", source)
    sys.path.insert(0, str(source))
    from cami_amber.binning_classes import GenomeQuery, Options
    from cami_amber.utils.load_data import read_metadata
    lengths = json.loads((fixture / "fixture.json").read_text())["lengths"]
    require(set(partition(predictions, lengths)) == set(lengths), "Evaluator handoff lost assignments")
    options = Options(filter_tail_percentage=0, skip_heatmap=True)
    gold = GenomeQuery("gold", "E001", options, read_metadata((str(fixture / "truth.tsv"), "gold"))[0], is_gs=True)
    query = GenomeQuery("integration", "E001", options, read_metadata((str(predictions), "integration"))[0])
    query.gold_standard = gold
    query.compute_metrics()
    require(int(query.precision_df["total_length"].sum()) == sum(lengths.values()), "AMBER handoff changed assigned bases")
    out.mkdir()
    query.precision_df.to_csv(out / "per-bin.tsv", sep="\t", index=False)
    query.recall_df.to_csv(out / "per-genome.tsv", sep="\t", index=False)
    (out / "evaluation.json").write_text(json.dumps({"status": "pass", "assigned_bp": sum(lengths.values()),
        "scope": "Native clustering-to-AMBER contract only; random embeddings, not an E001 biological result"}, indent=2))


def run(root, code):
    require(root.is_absolute() and root.is_dir(), "Existing absolute work root required")
    stage = Path(tempfile.mkdtemp(prefix="native-integration-", dir=root))
    start, status, outcomes = time.monotonic(), 1, {}
    base = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE")}
    base.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1",
                OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    def command(tool, label, args, limit):
        prefix = root / "envs" / tool
        env = dict(base, PATH=str(prefix / "bin") + os.pathsep + base.get("PATH", ""))
        if tool == "comebin":
            env["CHECKM_DATA_PATH"] = str(prefix / "checkm_data")
        invoke([prefix / "bin/python", "-I", code / "scripts/e001_integration.py", *args], env, stage, label, limit)
    try:
        commit = (code / "SOURCE_COMMIT").read_text().strip()
        require(len(commit) == 40 and all(c in "0123456789abcdef" for c in commit), "Invalid source commit")
        frozen_path = code / "experiments/E001-coverage-thinning/frozen-inputs.json"
        frozen_record = json.loads(frozen_path.read_text())
        (stage / "provenance.json").write_text(json.dumps({"source_commit": commit, "frozen_inputs_sha256": sha(frozen_path),
            "driver_sha256": sha(code / "scripts/e001_integration.py"), "allocated_vcpus": 8}, indent=2))
        fixture = stage / "fixture"
        command("mapping", "fixture", ["--prepare", frozen_record["owner_input_directory"], str(fixture), str(frozen_path)], 300)
        for tool in ("vamb", "comebin"):
            try:
                source = root / "sources" / ("COMEBin" if tool == "comebin" else "vamb")
                command(tool, tool, ["--cluster", tool, str(source), str(fixture), str(stage / tool)], 1800 if tool == "comebin" else 300)
                command("amber", tool + "-evaluate", ["--evaluate", str(root / "sources/AMBER_evaluation"), str(fixture),
                        str(stage / tool / "predictions.tsv"), str(stage / (tool + "-evaluation"))], 300)
                outcomes[tool] = "pass"
            except Exception:
                outcomes[tool] = "failed"
                (stage / (tool + "-failure.txt")).write_text(traceback.format_exc())
                print(traceback.format_exc(), file=sys.stderr)
        status = 0 if all(outcomes.get(t) == "pass" for t in ("vamb", "comebin")) else 1
    except Exception:
        (stage / "failure.txt").write_text(traceback.format_exc())
        print(traceback.format_exc(), file=sys.stderr)
    finally:
        elapsed = time.monotonic() - start
        (stage / "status.json").write_text(json.dumps({"exit_code": status, "tools": outcomes,
            "elapsed_seconds": elapsed, "driver_allocated_core_hours": 8 * elapsed / 3600}, indent=2))
        try:
            archive = root / (stage.name + "-return.tar.gz")
            with tarfile.open(archive, "x:gz") as handle:
                for path in stage.rglob("*"):
                    if path.is_file() and path.suffix in {".json", ".tsv", ".txt", ".log", ".stdout", ".stderr", ".out", ".err", ".seed"}:
                        handle.add(path, arcname=stage.name + "/" + str(path.relative_to(stage)))
            Path(str(archive) + ".sha256").write_text(sha(archive) + "  " + archive.name + "\n")
            print("RETURN:", archive, "and .sha256", flush=True)
        except Exception:
            status = 1
            (stage / "status.json").write_text(json.dumps({"exit_code": 1, "packaging_failed": True}))
            (stage / "packaging-failed.txt").write_text(traceback.format_exc())
            print("Packaging failed; preserve", stage, file=sys.stderr)
    print("INTEGRATION EXIT CODE:", status, flush=True)
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--prepare", nargs=3)
    modes.add_argument("--cluster", nargs=4)
    modes.add_argument("--evaluate", nargs=4)
    args = parser.parse_args()
    if args.prepare:
        inp, out, frozen_path = map(Path, args.prepare)
        prepare(inp, out, json.loads(frozen_path.read_text()))
    elif args.cluster:
        tool, source, fixture, out = args.cluster
        require(tool in ("vamb", "comebin"), "Unknown clustering tool")
        cluster_worker(tool, Path(source), Path(fixture), Path(out))
    elif args.evaluate:
        evaluate(*map(Path, args.evaluate))
    else:
        if args.root is None:
            parser.error("root is required")
        raise SystemExit(run(args.root, Path(__file__).resolve().parents[1]))
