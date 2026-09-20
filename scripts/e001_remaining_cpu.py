"""Grouped, isolated COMEBin/MetaBAT2 synthetic native preflight. No research runs."""

import argparse
import json
import logging
import os
from pathlib import Path
import platform
import resource
import shutil
import sys
import tarfile
import tempfile
import time
import traceback
from types import SimpleNamespace

from e001_vamb_cpu import invoke, require, sha

TOOLS = ("metabat", "comebin")


def frozen(code):
    path = code / "experiments/E001-coverage-thinning/frozen-inputs.json"
    record = json.loads(path.read_text())
    require(sha(code / "experiments/E001-coverage-thinning/config.json") == record["config_sha256"], "Changed frozen config")
    return record


def comebin_measure(source, out, record):
    import torch
    from e001lib.native import verify_source, require_packages
    provenance = verify_source("COMEBin", source)
    require_packages({"torch": "2.13.0+cpu", "numpy": "2.4.6", "biopython": "1.87"})
    sys.path.insert(0, str(source / "COMEBin"))
    from models.mlp import EmbeddingNet
    from models.mlp2 import CombinedEmbeddingNet
    from simclr import SimCLR
    from utils import configure_reproducibility
    configure_reproducibility(11)
    torch.set_num_threads(8)
    torch.set_num_interop_threads(1)
    batch, views, dims = 1024, 6, 2 * len(record["samples"])
    cov = EmbeddingNet(dims, 128, [2048] * 3, [0.2] * 2, actn=torch.nn.LeakyReLU())
    model = CombinedEmbeddingNet(264, 128, [2048] * 3, [0.2] * 2, actn=torch.nn.LeakyReLU(), cov_model=cov)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
    args = SimpleNamespace(device=torch.device("cpu"), fp16_precision=False, output_path=str(out),
                           batch_size=batch, n_views=views, temperature=0.07)
    trainer = SimCLR(model=model, optimizer=optimizer, scheduler=None, args=args, logger=logging.getLogger("E001"))
    durations, losses = [], []
    before = next(model.parameters()).detach().clone()
    model.train()
    try:
        for _ in range(3):
            # Full native batch/view shape; source model and InfoNCE, not a surrogate loss.
            features = torch.rand(batch * views, 136 + dims)
            started = time.monotonic()
            embeddings, _ = model(features[:, -136:], features[:, :-136])
            logits, labels = trainer.info_nce_loss(embeddings)
            logits_shape = list(logits.shape)
            loss = trainer.criterion(logits, labels)
            require(torch.isfinite(loss).item(), "Nonfinite native contrastive loss")
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            durations.append(time.monotonic() - started)
            losses.append(loss.item())
            require(all(torch.isfinite(p).all().item() for p in model.parameters()), "Nonfinite COMEBin parameters")
            del features, embeddings, logits, labels, loss
        require(not torch.equal(before, next(model.parameters()).detach()), "COMEBin optimizer did not update")
    finally:
        trainer.writer.close()
    batches = record["retained_contigs"] // batch
    hours = 8 * max(durations[1:]) * batches * 200 / 3600
    return {**provenance, "status": "measured", "batch_size": batch, "views": views, "coverage_dimensions": dims,
            "seed": 11, "temperature": 0.07, "torch_threads": 8, "allocated_vcpus": 8,
            "logits_shape": logits_shape, "parameters": sum(p.numel() for p in model.parameters()),
            "warmup_seconds": durations[0], "measured_batch_seconds": durations[1:], "losses": losses,
            "batches_per_epoch": batches, "epoch_ceiling": 200, "projected_fit_core_hours": hours,
            "twofold_margin_fit_core_hours": 2 * hours,
            "scope": "Random synthetic full-batch optimizer timing; no learned research model or saved checkpoint",
            "limitations": "Excludes DataLoader, feature extraction, marker search, clustering/grid and real-data effects; no early-stop savings assumed."}


def metabat_measure(source, out, record):
    import numpy as np
    from e001lib.native import verify_source, run_checked
    from e001lib.records import partition
    provenance = verify_source("metabat", source)
    rng = np.random.default_rng(11)
    n, samples = record["retained_contigs"], len(record["samples"])
    base, remainder = divmod(record["retained_bp"], n)
    fasta, depth = out / "synthetic.fna", out / "depth.tsv"
    lengths = {}
    alphabet = np.frombuffer(b"ACGT", dtype=np.uint8)
    profiles = rng.lognormal(3, 1, size=(32, samples))
    with fasta.open("x") as sequences, depth.open("x") as table:
        header = ["contigName", "contigLen", "totalAvgDepth"]
        for sample in range(samples):
            header += [f"sample{sample}.bam", f"sample{sample}.bam-var"]
        table.write("\t".join(header) + "\n")
        for i in range(n):
            name, length = f"synthetic{i:06d}", base + (i < remainder)
            lengths[name] = length
            gc = 0.25 + (i % 32) * 0.5 / 31
            seq = rng.choice(alphabet, size=length, p=[(1-gc)/2, gc/2, gc/2, (1-gc)/2]).tobytes().decode("ascii")
            sequences.write(f">{name}\n{seq}\n")
            means = profiles[i % 32] * rng.uniform(0.8, 1.2, size=samples)
            values = [name, str(length), str(float(means.sum()))]
            for mean in means:
                values += [str(float(mean)), str(float(mean))]
            table.write("\t".join(values) + "\n")
    started = time.monotonic()
    run_checked(["metabat2", "-i", fasta, "-a", depth, "-o", out / "bins", "-t", "8",
                 "--seed", "11", "--saveCls", "--unbinned"], out / "logs", "metabat-cpu")
    elapsed = time.monotonic() - started
    assignments = partition(out / "bins.MemberMatrix.txt", lengths, "metabat")
    return {**provenance, "status": "measured", "synthetic_contigs": n, "synthetic_bp": sum(lengths.values()),
            "samples": samples, "seed": 11, "allocated_vcpus": 8, "elapsed_seconds": elapsed,
            "binning_core_hours": 8 * elapsed / 3600, "assigned_contigs": len(assignments),
            "scope": "Synthetic FASTA/depth CPU smoke at frozen contig/base counts; no biological score",
            "limitations": "Uniform lengths and 32 synthetic composition/coverage groups; excludes BAM depth extraction and is not a real-data runtime guarantee."}


def measure(tool, source, out):
    out.mkdir(parents=True, exist_ok=False)
    record = frozen(Path(__file__).resolve().parents[1])
    report = (comebin_measure if tool == "comebin" else metabat_measure)(source, out, record)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    report.update(parent_maxrss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  children_maxrss=children.ru_maxrss, children_user_seconds=children.ru_utime,
                  children_system_seconds=children.ru_stime,
                  maxrss_units="bytes" if sys.platform == "darwin" else "KiB",
                  memory_note="Separate parent and completed-child peaks, not aggregate concurrent RAM.")
    (out.parent / "cpu.json").write_text(json.dumps(report, indent=2) + "\n")


def run(root, code, tools=TOOLS):
    require(root.is_absolute() and root.is_dir(), "Existing absolute work root required")
    require(tools and len(tools) == len(set(tools)) and all(t in TOOLS for t in tools), "Invalid requested tools")
    stage = Path(tempfile.mkdtemp(prefix="native-remaining-", dir=root))
    started, statuses, status = time.monotonic(), {}, 1
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE", "PIP_NO_INDEX")}
    env.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="11",
               OMP_NUM_THREADS="8", MKL_NUM_THREADS="8", OPENBLAS_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    env["PATH"] = str(root / "bin") + os.pathsep + env.get("PATH", "")
    try:
        require(platform.system() == "Linux" and platform.machine() == "x86_64", "Linux x86_64 required")
        commit = (code / "SOURCE_COMMIT").read_text().strip()
        require(len(commit) == 40 and all(c in "0123456789abcdef" for c in commit), "Invalid source commit")
        frozen(code)
        (stage / "provenance.json").write_text(json.dumps({"source_commit": commit,
            "driver_sha256": sha(Path(__file__)), "allocated_vcpus": 8, "requested_ram_gb": 24,
            "platform": platform.platform(), "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "frozen_inputs_sha256": sha(code / "experiments/E001-coverage-thinning/frozen-inputs.json")}, indent=2))
        for binary in ("bash", "git", "sha256sum"):
            require(shutil.which(binary, path=env["PATH"]), "Missing prerequisite: " + binary)
        fixture, mapping = root / "fixture", root / "environment-review/mapping-smoke"
        if not mapping.is_dir():
            mapping = root / "smoke/mapping"
        require((fixture / "fixture.fna").is_file() and len(list((mapping / "CT").glob("*.bam"))) == 2, "Missing accepted synthetic fixtures")
        for tool in tools:
            attempt = stage / tool
            attempt.mkdir()
            try:
                prefix = root / "envs" / tool
                variables = dict(env, PATH=str(prefix / "bin") + os.pathsep + env["PATH"],
                                 E001_METABAT_PREFIX=str(root / "envs/metabat"))
                if not prefix.exists():
                    require(sha(root / "bin/micromamba") == "366cd9cd8be14df1ab8ed50352a82111082a36686b2d389fdb79a92c3fafb3e3", "Changed persistent micromamba")
                    invoke(["bash", code / "scripts/e001_linux_setup.sh", tool, root], variables, attempt, "setup", 1800)
                else:
                    lock = root / "locks" / tool / "setup.exit-code.txt"
                    require(lock.is_file() and lock.read_text().strip() == "0", "Partial existing setup; preserve for review")
                python = prefix / "bin/python"
                modules = "numpy,Bio,pysam" + (",torch,pandas" if tool == "comebin" else "")
                probe = (f"import sys,site,json,{modules}; from pathlib import Path; "
                         "p=Path(sys.argv[1]).resolve(); assert Path(sys.prefix).resolve()==p; assert not site.ENABLE_USER_SITE; "
                         f"assert all(Path(m.__file__).resolve().is_relative_to(p) for m in ({modules})); " +
                         ("assert torch.version.cuda is None; " if tool == "comebin" else "") +
                         "print(json.dumps({'python':sys.version,'prefix':str(p)}))")
                invoke([python, "-I", "-c", probe, prefix], variables, attempt, "environment", 120)
                invoke([python, "-I", "-m", "pip", "check"], variables, attempt, "pip-check", 120)
                if tool == "metabat":
                    invoke(["sha256sum", "--check", root / "locks/metabat/binaries.sha256"], variables, attempt, "binaries", 120)
                source = root / "sources" / ("COMEBin" if tool == "comebin" else tool)
                if tool == "comebin":
                    payloads = {name: sha(source / "auxiliary" / name) for name in ("marker.hmm", "bacar_marker.hmm")}
                    (attempt / "marker-payloads.json").write_text(json.dumps(payloads, indent=2))
                args = [python, "-s", code / "scripts/e001.py", "native-smoke", tool,
                        "--source", source, "--fixture", fixture, "--out", attempt / "smoke"]
                if tool == "comebin":
                    args += ["--mapping", mapping]
                invoke(args, variables, attempt, "smoke", 300)
                invoke([python, "-s", code / "scripts/e001_remaining_cpu.py", "--measure", tool, source, attempt / "cpu-work"],
                       variables, attempt, "cpu", 600)
                statuses[tool] = "pass"
            except Exception:
                statuses[tool] = "failed"
                (attempt / "failure.txt").write_text(traceback.format_exc())
                print(traceback.format_exc(), file=sys.stderr)
                print("Continuing to the other independent tool, if any.", flush=True)
        status = 0 if all(statuses.get(t) == "pass" for t in tools) else 1
    except Exception:
        (stage / "failure.txt").write_text(traceback.format_exc())
        print(traceback.format_exc(), file=sys.stderr)
    finally:
        elapsed = time.monotonic() - started
        (stage / "status.json").write_text(json.dumps({"exit_code": status, "tools": statuses, "requested_tools": list(tools),
            "elapsed_seconds": elapsed, "driver_allocated_core_hours": 8 * elapsed / 3600,
            "note": "Excludes owner job time outside driver."}, indent=2))
        try:
            returned = root / (stage.name + "-return.tar.gz")
            with tarfile.open(returned, "x:gz") as archive:
                # Never return the full-size synthetic FASTA, depth table or bin FASTAs.
                for path in sorted(stage.rglob("*")):
                    if path.is_file() and path.suffix in {".json", ".stdout", ".stderr", ".log", ".txt"}:
                        archive.add(path, arcname=stage.name + "/" + str(path.relative_to(stage)))
                for tool in tools:
                    lock = root / "locks" / tool
                    if lock.is_dir():
                        archive.add(lock, arcname=stage.name + "/" + tool + "/locks")
            Path(str(returned) + ".sha256").write_text(sha(returned) + "  " + returned.name + "\n")
            print("RETURN: " + str(returned) + " and .sha256", flush=True)
        except Exception:
            status = 1
            (stage / "packaging-failed.txt").write_text(traceback.format_exc())
            (stage / "status.json").write_text(json.dumps({"exit_code": 1, "packaging_failed": True, "tools": statuses}))
            print("Packaging failed; preserve " + str(stage), file=sys.stderr)
    print("GROUPED PREFLIGHT EXIT CODE: " + str(status), flush=True)
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?")
    parser.add_argument("--tools", nargs="+", choices=TOOLS, default=list(TOOLS), help="Default both; narrow only for reviewed recovery")
    parser.add_argument("--measure", nargs=3, metavar=("TOOL", "SOURCE", "OUT"))
    args = parser.parse_args()
    if args.measure:
        tool, source, out = args.measure
        require(tool in TOOLS, "Unknown tool")
        measure(tool, Path(source), Path(out))
    else:
        if args.root is None:
            parser.error("root is required")
        raise SystemExit(run(args.root, Path(__file__).resolve().parents[1], args.tools))
