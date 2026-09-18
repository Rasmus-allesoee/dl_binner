# E001: Validation and UCloud Preflight

Updated: 2026-09-18. This is the execution guide, not a scientific result. Read the [protocol](README.md) and [choice revision](../../docs/decisions/D004-human-cpu-preflight.md) first.

## What is ready

- [Configuration](config.json) owns numerical protocol/resource settings. [Acquisition manifest](acquisition.json) owns the selected URLs, GI sample IDs and publisher MD5s. Locally calculated SHA-256s are added only after download.
- [Harness](../../scripts/e001.py) and [tests](../../tests/test_e001.py) validate FASTA/truth/prediction joins, the conservative endpoint, exact neighborhood probes, source identities, safe archive inventory, and native input/output contracts.
- [Linux setup](../../scripts/e001_linux_setup.sh) prepares separate environments/checkouts. [Linux smoke](../../scripts/e001_linux_smoke.sh) runs synthetic checks only, with logs, exit codes and GNU time output. Neither script launches research training or downloads research data.
- Runtime recipes are **not solved Linux locks**. They follow the audited tool requirements, including different NumPy/PyTorch versions for VAMB and COMEBin. Generated `conda-explicit.txt`, `pip-freeze.txt`, binary hashes and smoke reports must be returned and inspected. There are no verified container digests, and none are fabricated. A failed solver/import is a compatibility blocker, not permission to downgrade silently.

The portable environment uses Python 3.12 or 3.13 and:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r experiments/E001-coverage-thinning/requirements-portable.txt
.venv/bin/python -m unittest discover -s tests -v
python3 scripts/check_docs.py --check-context
```

The first two commands are needed only for a new local environment. Native tests intentionally are not part of this portable pass. Pandoc is needed only for documentation checking.

## Gate 0: Owner-run Linux smoke

Start with **8 vCPU, 24 GB RAM, no GPU**, on an x86-64 Linux UCloud application with micromamba, Git, GNU `time` and `timeout`. Confirm the application and persistent work-directory path with Codex before running. Do not leave the allocated machine idle: charged core-hours are allocated vCPUs multiplied by elapsed hours, including setup, downloads and idle time. The initial preflight allowance is 32 core-hours, not an instruction to consume it.

Transfer the committed project code, tests, E001 files and `docs/evidence/2026-09-17-tool-snapshots.json`; keep its source commit and transfer checksum. No paper/thesis/tool-cache upload or public GitHub repository is needed. Codex will prepare the transfer command once the destination is known. Use new external directories, not `agent_context/tools_repo`. The examples below assume `CODE` is that code directory and `WORK` a new persistent directory; neither is a literal UCloud path.

```sh
cd "$CODE"
bash scripts/e001_linux_setup.sh mapping "$WORK"
bash scripts/e001_linux_smoke.sh mapping "$WORK"
bash scripts/e001_linux_setup.sh amber "$WORK"
bash scripts/e001_linux_smoke.sh amber "$WORK"
```

**Return these first.** Inspect failures before proceeding. This checks alignment output, BAM headers/flags/NM tags, template-preserving samtools thinning, and pinned AMBER unique/multi-origin semantics and strict thresholds. It does not estimate research-scale model training cost.

After those outputs have been inspected, prepare/run each remaining native smoke separately:

```sh
bash scripts/e001_linux_setup.sh vamb "$WORK"
bash scripts/e001_linux_smoke.sh vamb "$WORK"
bash scripts/e001_linux_setup.sh comebin "$WORK"
bash scripts/e001_linux_smoke.sh comebin "$WORK"
bash scripts/e001_linux_setup.sh metabat "$WORK"
bash scripts/e001_linux_smoke.sh metabat "$WORK"
```

COMEBin's setup uses the pinned source environment and CPU PyTorch 2.13.0; VAMB uses CPU PyTorch 2.6.0. Do not combine environments. MetaBAT2 is built from the audited source, not substituted with an unrelated conda release. Build dependencies are prospective pins; inspect the CMake log and resolved HTSlib/compiler identity. Native smoke has a 30-minute timeout per tool, preserves failure logs and refuses reused output directories. On failure, stop and return the logs; do not delete/retry repeatedly or install alternative versions.

The learned-method smoke extracts native features, tests scaling and zero handling, and evaluates a tiny CPU forward pass. It does **not** train, establish convergence, validate clustering/marker databases, or predict full-batch CPU runtime. COMEBin keeps one fixed augmentation bundle and recomputes all six views from new BAMs. Reports expose changes per view; unchanged zero-depth values are not automatically errors.

## Gate 1: Fresh GI inventory, not reads

After agreeing the work location and reviewing the first smoke outputs, acquire about **3 GB** of assembly/truth/setup plus small metadata. Allow **10 GB free** for this stage. These are archive-listing estimates, not observed filesystem usage. The following command defaults to a plan; only the second command actually downloads:

```sh
micromamba run -p "$WORK/envs/mapping" python scripts/e001.py acquire --root "$WORK/inventory"
micromamba run -p "$WORK/envs/mapping" python scripts/e001.py acquire --root "$WORK/inventory" --execute
micromamba run -p "$WORK/envs/mapping" python scripts/e001.py prepare-hmp \
  --fasta "$WORK/inventory/per_bodysite/gastro_bam/gsa.fa" \
  --mapping "$WORK/inventory/per_bodysite/gastro_bam/gsa_pooled_mapping_fixed.tsv" \
  --out "$WORK/input-preflight"
```

This initial conversion deliberately has **no assumed taxonomy file**. It reports unresolved domains and blocks scientific population approval while checking the sequence/coordinate joins and size. Inspect `setup-members.json` for usable taxonomy/metadata. If necessary, verify and acquire the publisher-linked historical taxonomy separately. Supply its verified `nodes.dmp` through `--nodes` and use a **new** output directory for the final conversion. No current-taxonomy substitution or domain assignment from species names. Never confuse a blocked interpretability/domain gate with a failed download or negative biological result.

The public GI FASTA has coordinate-bearing source names. The converter joins accession, inclusive coordinates and exact length to the corrected mapping, and writes anonymous `PC...` IDs, a full ID/sequence-hash map, CAMI truth, fixed evaluation/probe populations and an inventory. It does not filter the input by truth or domain. Taxonomy determines only the scored subset. Known multi-owner and cross-origin identical/reverse-complement sequences remain in input and purity denominators. Unexpected coordinate/ID relationships stop conversion; no row-order matching.

Only archive **listing** is automated. Unsafe paths, duplicate members, links/devices or excessive unpacked sizes fail. We will prepare selective metadata/read extraction after inspecting actual members; never extract the entire setup/read archive blindly. Downloads verify publisher MD5s and calculate SHA-256s. Failed `.part` files remain for inspection; existing completed files are rechecked, not trusted by filename.

## Read acquisition and resource gate

The ten selected GI archives total roughly **94 GB compressed** according to the publisher listing and include more than just reads. Sample numbers are `0,1,2,3,4,5,9,10,11,12`, not `0..9`. No read-download command is enabled by `acquire`.

Before reads, inspect one archive's inventory to establish its actual interleaved FASTQ/member layout, needed metadata and checksum contract. Prepare a sequential download/extract/map plan: at most one sample archive, one extracted library and one sort workspace at a time; preserve checksums and record any regenerable deletion with owner agreement. Do not download simulator source-genome BAMs as coverage input. C0 BAMs and retained feature/model outputs still accumulate.

250 GB is enough for the inventory but **not yet established sufficient for E001**. Plan at most 200 GB working occupancy, retaining headroom for environments and filesystem overhead. A 0.5-1 TB quota would simplify later retention, but no increase is required now. Estimate peak storage from one sample and all retained outputs before bulk work; pause if it exceeds the configured limit.

The experiment ceiling is **800 of the available 2,100 allocated core-hours**, including the 32-core-hour preflight and 200-core-hour preprocessing ceilings; these are nested limits, not additive allowances. Preserve at least 1,300 core-hours for later work. Initially plan 16 vCPU/48 GB for scientific jobs, only after measurement. A learned fit must be projected below 80 core-hours and the complete schedule below the total ceiling. Twelve fits at that per-fit ceiling would already exceed the experiment budget: passing each individual ceiling is not sufficient. Use actual throughput and retained population size to decide whether COMEBin fits; do not shorten native training, drop replicates or silently replace it. If it does not fit, amend the question and decision rules before scientific scores.

The next compute assessment should measure CPU throughput on synthetic tensors with the real native batch/network sizes at two thread counts, plus a fixed read-prefix mapping/feature preflight. This needs an explicit bounded job after the current checks; a tiny forward pass is insufficient. Inspect strobealign/Bowtie2 alignment disagreement and low-MAPQ behavior on that prefix without tuning against binning scores. Strobealign is provisional, not proved faster or more accurate on this dataset.

## Return artifacts and stopping point

Return these small records, not the FASTA, BAMs, features or model files:

- `locks/`, setup stdout/stderr, `smoke/*.stdout`, `smoke/*.stderr`, `smoke/*.resources.txt`, `smoke/*.exit-code.txt`, and each tool's `smoke.json` (include failed stages).
- `inventory/acquisition-report.json`, `inventory/setup-members.json`, publisher `README.md`, and `input-preflight/inventory.json`.
- The executed project commit, actual UCloud vCPU/RAM allocation, elapsed allocation time, `df -h` output, and storage quota.

For the first mapping/AMBER smoke return, this command packages their entire tiny synthetic output, including any failure details, without research data:

```sh
tar -czf "$WORK/e001-smoke-return.tar.gz" -C "$WORK" locks smoke
sha256sum "$WORK/e001-smoke-return.tar.gz"
```

After Gate 1, this separate archive returns just the inventory summaries:

```sh
tar -czf "$WORK/e001-inventory-return.tar.gz" -C "$WORK" \
  inventory/acquisition-report.json inventory/setup-members.json inventory/README.md \
  input-preflight/inventory.json
sha256sum "$WORK/e001-inventory-return.tar.gz"
```

Inspect existing return filenames before rerunning packaging. No scientific `run-NNN` is allocated yet. The research launcher, CPU throughput authorization, full-stage artifact capture/AMBER reports and budget enforcement must be completed against the returned data/environment contract before Gate 2. The prepared native feature/output adapters are not an unattended experiment launcher.
