"""Thin adapters to pinned native tools. No copied model or normalization logic."""

import importlib.metadata
import csv
import json
import logging
from pathlib import Path
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace

import numpy as np

from .records import ROOT, config, digest, require, sequences, write_json


def verify_source(tool, source):
    source = Path(source).resolve()
    snapshots = json.loads((ROOT / "docs/evidence/2026-09-17-tool-snapshots.json").read_text())
    expected = next(t["commit"] for t in snapshots["tools"] if t["name"] == tool)
    def git(*args):
        result = subprocess.run(["git", "-C", str(source), *args], text=True, capture_output=True)
        require(result.returncode == 0, f"Cannot verify {tool} Git source: {result.stderr.strip()}")
        return result.stdout.strip()
    require(Path(git("rev-parse", "--show-toplevel")).resolve() == source, "Tool has no independent Git root")
    require(git("rev-parse", "HEAD") == expected, f"Wrong {tool} commit")
    require(not git("diff", "HEAD", "--"), f"Tracked {tool} source modifications")
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    require(all(Path(p).name == ".DS_Store" for p in untracked), f"Unexpected untracked {tool} files")
    return {"tool": tool, "commit": expected, "source": str(source)}


def require_packages(versions):
    actual = {name: importlib.metadata.version(name) for name in versions}
    require(all(actual[name] == version for name, version in versions.items()), f"Native dependency mismatch: expected {versions}; got {actual}")
    return actual


def run_checked(argv, log_dir, label):
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    record = log_dir / (label + ".json")
    require(not record.exists(), f"Attempt already recorded: {record}")
    start = time.monotonic()
    with (log_dir / (label + ".stdout")).open("x") as stdout, (log_dir / (label + ".stderr")).open("x") as stderr:
        try:
            result = subprocess.run([str(v) for v in argv], stdout=stdout, stderr=stderr)
        except OSError as error:
            write_json(record, {"argv": [str(v) for v in argv], "elapsed_seconds": time.monotonic() - start,
                                "returncode": None, "status": "failed", "error": str(error)})
            raise
    write_json(record, {"argv": [str(v) for v in argv], "elapsed_seconds": time.monotonic() - start, "returncode": result.returncode,
                        "status": "completed" if result.returncode == 0 else "failed"})
    require(result.returncode == 0, f"Native command failed; inspect {record}")


def thinning_command(source, dest, replicate, sample_index):
    cfg = config()
    require(0 <= replicate < len(cfg["seeds"]) and 0 <= sample_index < len(cfg["samples"]), "Invalid replicate/sample index")
    require(Path(source).resolve() != Path(dest).resolve() and not Path(dest).exists(), "Thinning must create a new file")
    seed = 1000 * (replicate + 1) + sample_index
    return ["samtools", "view", "-b", "--subsample", str(cfg["thinning_fraction"]), "--subsample-seed", str(seed), "-o", str(dest), str(source)]


def mapping_commands(reference, read1, sample, output, read2=None, mapper_threads=4, sort_extra_threads=1):
    """Return argv arrays for a pipefail pipeline, never invoke a shell on user paths."""
    require(mapper_threads >= 1 and sort_extra_threads >= 0, "Invalid mapping thread allocation")
    cfg = config()
    cmd = ["strobealign", "-t", str(mapper_threads), "-r", str(cfg["mapper"]["read_length"]),
           "--rg-id", str(sample), "--rg", f"SM:{sample}", str(reference)]
    if read2 is None:
        cmd += ["--interleaved", str(read1)]
    else:
        cmd += [str(read1), str(read2)]
    return [cmd, ["samtools", "view", "-u", "-F", str(cfg["exclude_sam_flags"]), "-"],
            ["samtools", "sort", "-@", str(sort_extra_threads), "-m", "512M", "-o", str(output), "-"]]


def pipeline(commands, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=False)
    processes, logs = [], []
    try:
        for i, argv in enumerate(commands):
            log = (outdir / f"stage-{i}.stderr").open("x")
            logs.append(log)
            previous = processes[-1].stdout if processes else None
            p = subprocess.Popen(argv, stdin=previous, stdout=subprocess.PIPE if i < len(commands) - 1 else subprocess.DEVNULL, stderr=log)
            if previous is not None:
                previous.close()
            processes.append(p)
        statuses = [p.wait() for p in processes]
        write_json(outdir / "pipeline.json", {"commands": commands, "returncodes": statuses})
        require(all(s == 0 for s in statuses), "Mapping pipeline failed; do not use partial output")
    finally:
        for p in processes:
            if p.poll() is None:
                p.terminate()
                p.wait()
        for log in logs:
            log.close()


def metabat_commands(reference, bams, outdir, seed=11, threads=2):
    require(seed != 0 and threads >= 1 and bams, "Invalid MetaBAT2 configuration")
    outdir = Path(outdir)
    return [["jgi_summarize_bam_contig_depths", "--outputDepth", str(outdir / "depth.tsv"), *map(str, bams)],
            ["metabat2", "-i", str(reference), "-a", str(outdir / "depth.tsv"), "-o", str(outdir / "bins"),
             "-t", str(threads), "--seed", str(seed), "--saveCls", "--unbinned"]]


def scale_metabat_depth(source, out, lengths):
    factor = config()["scale_factor"]
    seen = set()
    with Path(source).open() as handle, Path(out).open("x") as destination:
        reader = csv.reader(handle, delimiter="\t")
        writer = csv.writer(destination, delimiter="\t", lineterminator="\n")
        header = next(reader)
        require(header[:3] == ["contigName", "contigLen", "totalAvgDepth"] and len(header) >= 5 and (len(header) - 3) % 2 == 0, "Not a native mean/variance MetaBAT depth table")
        require(all(header[i + 1] == header[i] + "-var" for i in range(3, len(header), 2)), "Missing native variance channels")
        writer.writerow(header)
        for row in reader:
            require(len(row) == len(header) and row[0] in lengths and row[0] not in seen, "Invalid/duplicate depth row")
            seen.add(row[0])
            require(int(row[1]) == lengths[row[0]], "Depth length mismatch")
            values = np.asarray([float(v) for v in row[2:]])
            require(np.isfinite(values).all() and (values >= 0).all(), "Invalid depth values")
            values[0] *= factor
            values[1::2] *= factor
            values[2::2] *= factor ** 2
            writer.writerow(row[:2] + [format(v, ".17g") for v in values])
    require(seen == set(lengths), "Missing depth rows")


def vamb_features(source, fasta, bams, out, threads=2):
    provenance = verify_source("vamb", source)
    require_packages({"numpy": "1.26.4", "torch": "2.6.0+cpu", "pycoverm": "0.6.2"})
    sys.path.insert(0, str(Path(source).resolve()))
    import vamb
    require(Path(vamb.__file__).resolve().is_relative_to(Path(source).resolve()), "Imported VAMB from wrong location")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    with vamb.vambtools.Reader(Path(fasta)) as handle:
        composition = vamb.parsecontigs.Composition.from_file(handle, str(fasta), minlength=config()["min_contig_bp"])
    composition.save(out / "composition.npz")
    abundance = vamb.parsebam.Abundance.from_files([Path(p) for p in bams], out / "tmp", composition.metadata, True, 0.0, threads)
    abundance.save(out / "abundance.npz")
    for condition, factor in (("C0", 1.0), ("CS", config()["scale_factor"])):
        loader = vamb.encode.make_dataloader(abundance.matrix.copy() * factor, composition.matrix.copy(), composition.metadata.lengths.copy(), cuda=False)
        tensors = [t.numpy() for t in loader.dataset.tensors]
        np.savez_compressed(out / f"normalized-{condition}.npz", coverage=tensors[0], composition=tensors[1], total_abundance=tensors[2], weights=tensors[3])
    (out / "ids.txt").write_text("".join(str(s) + "\n" for s in composition.metadata.identifiers))
    np.save(out / "input-mask.npy", composition.metadata.mask, allow_pickle=False)
    with np.load(out / "normalized-C0.npz") as a, np.load(out / "normalized-CS.npz") as b:
        differences = {name: float(np.max(np.abs(a[name] - b[name]))) for name in a.files}
        require(all(np.allclose(a[name], b[name], atol=1e-5, rtol=1e-5) for name in a.files), "VAMB uniform scale invariance failed")
    write_json(out / "native-features.json", {**provenance, "scale_max_abs_difference": differences,
               "bam_sha256": {str(p): digest(p) for p in bams}, "fasta_sha256": digest(fasta)})


def comebin_features(source, fasta, bamdir, out, fixed=None, threads=2):
    provenance = verify_source("COMEBin", source)
    require_packages({"numpy": "2.4.6", "torch": "2.13.0+cpu", "biopython": "1.87"})
    code = Path(source).resolve() / "COMEBin"
    sys.path.insert(0, str(code))
    from data_aug.generate_augfasta_and_saveindex import run_gen_augfasta
    from data_aug.gen_cov import run_gen_coverage
    from get_augfeature import get_kmer_coverage
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    args = SimpleNamespace(contig_file=str(Path(fasta).resolve()), out_augdata_path=str(out.resolve()),
                           bam_file_path=str(Path(bamdir).resolve()), n_views=config()["comebin_views"],
                           contig_len=1000, num_threads=threads, seed=config()["augmentation_seed"])
    logger = logging.getLogger("E001")
    if fixed:
        for name in ("feature_manifest.json", "contig_ids.txt", "contig_lengths.npy", "augmentation_intervals.npy", "kmer_counts.npy"):
            shutil.copyfile(Path(fixed) / name, out / name)
        previous = json.loads((Path(fixed) / "native-features.json").read_text())
        require(previous["fasta_sha256"] == digest(fasta), "Changed FASTA for fixed COMEBin views")
    else:
        run_gen_augfasta(logger, args)
    run_gen_coverage(logger, args)
    views, ids, lengths, _ = get_kmer_coverage(out, n_views=args.n_views, addvars=True, vars_sqrt=True, logger=logger)
    np.save(out / "normalized-views.npy", np.stack([v.numpy() for v in views]), allow_pickle=False)
    require(list(ids) == [s for s, _ in sequences(fasta)], "COMEBin unexpectedly dropped/reordered canonical IDs")
    write_json(out / "native-features.json", {**provenance, "fasta_sha256": digest(fasta),
               "interval_sha256": digest(out / "augmentation_intervals.npy"),
               "bam_sha256": {p.name: digest(p) for p in sorted(Path(bamdir).glob("*.bam"))},
               "coverage_sha256": {name: digest(out / name) for name in ("coverage_mean.npy", "coverage_var.npy")}})


def scale_comebin(source_bundle, out):
    source_bundle, out = Path(source_bundle), Path(out)
    require(not out.exists(), "Scale-control destination already exists")
    out.mkdir(parents=True)
    names = ["feature_manifest.json", "contig_ids.txt", "contig_lengths.npy", "augmentation_intervals.npy",
             "kmer_counts.npy", "coverage_manifest.json", "bam_ids.txt"]
    for name in names:
        shutil.copyfile(source_bundle / name, out / name)
    factor = config()["scale_factor"]
    for name, multiplier in (("coverage_mean.npy", factor), ("coverage_var.npy", factor ** 2)):
        values = np.load(source_bundle / name, allow_pickle=False)
        require(values.ndim == 3 and values.shape[1] == config()["comebin_views"] and np.isfinite(values).all() and (values >= 0).all(), "Invalid COMEBin coverage tensor")
        np.save(out / name, values * multiplier, allow_pickle=False)
    write_json(out / "scale-control.json", {"condition": "CS", "factor": factor, "source": str(source_bundle.resolve()),
               "source_mean_sha256": digest(source_bundle / "coverage_mean.npy"), "source_variance_sha256": digest(source_bundle / "coverage_var.npy")})


def validate_comebin_pair(full, thin):
    full, thin = Path(full), Path(thin)
    for name in ("contig_ids.txt", "contig_lengths.npy", "augmentation_intervals.npy", "kmer_counts.npy", "bam_ids.txt"):
        require(digest(full / name) == digest(thin / name), f"COMEBin paired identity changed: {name}")
    a, b = [json.loads((p / "native-features.json").read_text()) for p in (full, thin)]
    require(a["fasta_sha256"] == b["fasta_sha256"], "COMEBin references differ")
    require(a["bam_sha256"].keys() == b["bam_sha256"].keys(), "COMEBin sample columns differ")
    require(all(a["bam_sha256"][s] != b["bam_sha256"][s] for s in a["bam_sha256"]), "CT reused a C0 BAM")
    differences = {}
    for name in ("coverage_mean.npy", "coverage_var.npy"):
        arrays = [np.load(p / name, mmap_mode="r", allow_pickle=False) for p in (full, thin)]
        require(arrays[0].shape == arrays[1].shape and arrays[0].ndim == 3 and arrays[0].shape[1] == config()["comebin_views"], "COMEBin coverage shape mismatch")
        require(all(np.isfinite(x).all() and (x >= 0).all() for x in arrays), "Invalid COMEBin coverage")
        for p, record in ((full, a), (thin, b)):
            require(digest(p / name) == record["coverage_sha256"][name], "Coverage differs from completed native extraction")
        differences[name] = [int(np.count_nonzero(arrays[0][:, v, :] != arrays[1][:, v, :])) for v in range(config()["comebin_views"])]
    # Equal values can be legitimate in zero-depth views; report rather than invent changes.
    return {"status": "paired_provenance_valid", "changed_entries_per_view": differences}


def export_embeddings(tool, source, native_out, population, out):
    """Validate row axes before exporting native embeddings; never infer ID order."""
    native_out, out = Path(native_out), Path(out)
    out.mkdir(parents=True, exist_ok=False)
    verify_source("COMEBin" if tool == "comebin" else "vamb", source)
    if tool == "comebin":
        sys.path.insert(0, str(Path(source).resolve() / "COMEBin"))
        from embedding_bundle import load_embedding_bundle
        bundle = load_embedding_bundle(native_out / "embeddings.npy")
        ids, lengths, values = bundle.contig_ids, bundle.contig_lengths, bundle.embeddings
    else:
        sys.path.insert(0, str(Path(source).resolve()))
        import vamb
        composition = vamb.parsecontigs.Composition.load(native_out / "composition.npz")
        ids, lengths = composition.metadata.identifiers, composition.metadata.lengths
        with np.load(native_out / "latent.npz", allow_pickle=False) as archive:
            values = archive["arr_0"].copy()
    ids = [str(s) for s in ids]
    require(len(ids) == len(set(ids)) == len(values) == len(lengths) and np.asarray(values).ndim == 2 and np.isfinite(values).all(), "Invalid embedding axis/values")
    require(all(s in population["lengths"] and int(length) == population["lengths"][s] for s, length in zip(ids, lengths)), "Embedding ID/length mismatch")
    np.save(out / "embedding.npy", values, allow_pickle=False)
    (out / "ids.txt").write_text("".join(s + "\n" for s in ids))
    write_json(out / "axis.json", {"retained_ids": ids, "filtered_ids": sorted(set(population["lengths"]) - set(ids)),
               "lengths": [int(v) for v in lengths], "source": str(native_out.resolve())})
