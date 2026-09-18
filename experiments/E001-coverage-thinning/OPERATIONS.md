# E001: Validation and UCloud Preflight

Updated: 2026-09-18. This is the execution guide, not a scientific result. Read the [protocol](README.md) and [choice revision](../../docs/decisions/D004-human-cpu-preflight.md) first.

## What is ready

**Current action: conversion-only orphan/recovery correction.** Owner evidence establishes one FASTA record per alias group and two empty malformed orphan records. Upload/extract a new committed code bundle alongside the old one and run the new bundle's `scripts/e001_retry_conversion.sh WORK_ROOT --retry-known-failure`. It reuses the downloaded GI files and mapping environment, disables user-site exposure, writes `input-preflight-v2` and `conversion-alias-stage`, and packages `conversion-alias-return.tar.gz` plus `.sha256`. It downloads/installs nothing and does not require GNU time. The parser excludes only the two exact observed empty IDs (`*from__to*-42_total_0` and `_from__to_-42_total_0`); all other malformed input remains fatal. Recovery preserves the current failed attempt without overwriting earlier ones, choosing `failed-conversion-malformed-fasta-2`, `-3`, and so on when the base directory already exists. Earlier outputs remain untouched. Return both files and terminal output; taxonomy-free `blocked` remains expected, command errors do not. Existing active output files still cause a stop, not overwrite. Expect seconds to minutes on the current 4-vCPU/12-GB job. Prior recovery/acquisition instructions below are historical and must not be rerun now.

**Completed diagnostic checkpoint:** the alias retry exposed a second input-contract edge: empty malformed FASTA IDs `_from__to_-42_total_0`. The owner already ran the targeted read-only count against the existing GSA; it read no network data and returned the JSON evidence below. Do not rerun that scan, conversion or acquisition as part of this checkpoint.

The owner completed that scan: exactly two empty `*from__to*-42_total_0` records, no other malformed records. The next conversion bundle contains the narrow documented orphan exception and writes its exclusion report. The latest retry confirmed that the runtime error can expose the same artifact as `_from__to_-42_total_0`, and that a prior `failed-conversion-malformed-fasta/` directory must not block a new guarded recovery. The corrected retry verifies the known exit-1/Invalid-DNA signature, confirms the partial directory has no `inventory.json`, and moves all active artifacts under the next numbered preservation directory before creating fresh outputs. It refuses a completed or ambiguous inventory. It reuses existing files only.

**Current checkpoint:** acquisition succeeded after timer recovery; the owner's targeted FASTA scan completed and confirmed one physical sequence per truth alias group plus two empty orphan records. Do not rerun recovery/acquisition. The current action is the corrected, guarded conversion-only retry described above; a successful taxonomy-free conversion still requires inspection before any further acquisition or scientific work. The earlier recovery instructions below are historical, not the current command.

**Recovery checkpoint:** the first GI attempt failed before any acquisition because `/usr/bin/time` was absent. Replace only the uploaded supplemental inventory driver with the corrected version, verify its new checksum, and invoke `bash "$WORK/transfer/e001_gi_inventory.sh" "$WORK" --retry-missing-time`. It validates the specific exit-127 failure and absence of data, verifies and preserves the old return/stage under `failed-inventory-missing-time/`, then installs GNU time if missing and resumes the ordinary sequence. This updates the earlier statement that no software installation occurs: recovery may refresh Ubuntu package indexes and install only `time` and dependencies in the disposable container, not upgrade the system or reinstall tool environments. Installation output is saved in the new `inventory-stage/time-install.log`; no password is requested (`sudo -n`). Return the new same-named `gi-inventory-return.tar.gz` and `.sha256` plus final output. If recovery guards or installation fail, stop and return the error; do not delete prior files. Expect a small package install followed by the previously described approximately 3-GB inventory download.

**Current owner action (2026-09-18): GI inventory.** The environment-review return has been inspected and accepted; the EasyBuild concern is resolved by disabling user-site access. Upload [e001_gi_inventory.sh](../../scripts/e001_gi_inventory.sh) into the existing `transfer/` directory, verify its chat-supplied hash, then run `bash "$WORK/transfer/e001_gi_inventory.sh" "$WORK"`. Keep the current 4-vCPU/12-GB allocation. The earlier bootstrap/review commands below are completed history, not instructions to rerun them.

This grouped driver uses the unchanged transferred source snapshot, clears inherited Python paths and disables user-site, checks the clean mapping environment and completed review status, prints the acquisition plan, then downloads approximately 3 GB of manifest-listed assembly/truth/setup and small metadata. It verifies publisher MD5s and records local SHA-256s, safely lists the setup archive without extracting it, and runs the initial GI coordinate-to-anonymous-ID conversion without taxonomy. It never downloads sample/read archives or starts training. No new software is installed.

New paths under the experiment root: `inventory/` for downloaded inputs/reports, `input-preflight/` for canonical retained FASTA, ID/provenance records and initially blocked population, and `inventory-stage/` for commands, logs, timing and executed driver. Allow at least 10 GB free including generated output; expect minutes to tens of minutes depending on the publisher/network and shared filesystem, not a measured promise. Acquisition streams data and conversion streams FASTA while retaining truth/contig metadata; the 12-GB job is a reasonable initial allocation, with actual peak RAM recorded rather than assumed proven. Stop on any failed command; partial files are retained, and retries require inspection.

Return `gi-inventory-return.tar.gz` and `.sha256` plus final console lines. The archive contains only stage logs, publisher metadata, acquisition report, setup member listing and the conversion inventory, never the GSA/setup archive or large generated sequence/contig files. It is also packaged after ordinary failures; a hard-killed job may require separate log collection. A successful command can produce `status: blocked` in `input-preflight/inventory.json`: taxonomy is deliberately unresolved and scientific population approval must remain blocked until review. Inspect these returned records before selecting metadata extraction or historical taxonomy acquisition. No bulk reads are authorized.

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

### Current grouped execution

**Current checkpoint after first return:** bootstrap and mapping/AMBER synthetic checks passed; do not rerun the original driver. Unexpected EasyBuild entries in pip inventories require the no-download [environment review](../../scripts/e001_environment_review.py) before GI acquisition. Upload it into `$WORK/transfer`, verify its chat-supplied SHA-256, and run `python3 -I "$WORK/transfer/e001_environment_review.py" "$WORK"`. This reads existing installs, records observed/clean import origins and conda records, and reruns both synthetic checks into `$WORK/environment-review`; it creates `environment-review-return.tar.gz` and `.sha256` on ordinary success/failure. It does not install, remove or download anything. Existing environments/outputs are preserved; external Python paths are disabled only in child processes. Expect seconds to a few minutes on 4 vCPU/12 GB and a small return archive. Return both files and final console lines. Stop on errors; preserve partial outputs rather than retrying. Scientific data acquisition remains unauthorized until review. The earlier initial-driver instructions below are retained as execution history/reference, not the next action.

Owner update after extraction, 2026-09-18: archive checksum and full source commit are confirmed. The owner manages job extensions and authorizes grouping steps whose success is machine-checkable. This supersedes the earlier per-command chat pauses and requests for remaining time below. Do not repeatedly ask for job duration. Retain timestamps and allocation for eventual cost accounting.

Upload [e001_ucloud_preflight.sh](../../scripts/e001_ucloud_preflight.sh) separately into `$WORK/transfer`; the already verified execution snapshot does not need replacement. Verify the driver's SHA-256 supplied in chat, then invoke `bash "$WORK/transfer/e001_ucloud_preflight.sh" "$WORK"`. It uses the existing code at `$WORK/e001-code-9c2b0ec6feb3` and refuses previous bootstrap/tool outputs. Do not rerun after failure without reviewing preserved outputs.

The driver installs micromamba 2.9.0 from the official [2.9.0-0 release](https://github.com/mamba-org/micromamba-releases/releases/tag/2.9.0-0), whose Linux x86_64 binary is 18,292,808 bytes. The official GitHub release API was inspected 2026-09-18: asset SHA-256 `366cd9cd8be14df1ab8ed50352a82111082a36686b2d389fdb79a92c3fafb3e3`. This is pinned in the script and checked before execution; no remote installer is executed. Binary: `$WORK/bin/micromamba`; cache: `$WORK/micromamba`. No shell startup files are edited.

If missing, GNU time is installed with `sudo -n apt-get update` and `sudo -n ... apt-get install -y --no-install-recommends time` in the disposable Ubuntu container. This updates package indexes and installs the time package/dependencies, not a full system upgrade. The actual package version and executable hash are recorded. It may need reinstalling in a later job. No password/credential should be supplied if noninteractive sudo fails.

The driver then calls the unchanged mapping setup/smoke and AMBER setup/smoke scripts sequentially. Nonzero exits stop subsequent stages. A successful software check is sufficient to proceed within this synthetic-only batch; all locks/results still require human review before GI inventory. Downloads are software only; environments remain `$WORK/envs/mapping` and `$WORK/envs/amber`. Writes also include `sources/AMBER_evaluation`, `locks`, caches, synthetic `fixture`/`smoke`, and `bootstrap` logs. It launches no training or research-data acquisition. The 4-vCPU/12-GB job is retained for this small check, not established as sufficient for later native neural-method checks. The tiny mapping pipeline has multiple concurrent workers and may briefly contend for the allocation; its runtime is not a scaling benchmark.

Plan tens of minutes, with network/solver-dependent duration and several GB of disk headroom, not a measured guarantee. Existing per-stage timeouts remain; owner controls the job lifetime. Progress labels print immediately, each stage's detailed output goes to `bootstrap/<stage>.log`, and its last 15 lines print at completion. On ordinary success/failure the exit trap creates `$WORK/preflight-return.tar.gz` plus `.sha256`, containing bootstrap logs/executed driver, locks and synthetic smoke output when present. Return both files plus the final console lines. Hard termination can prevent packaging: preserve directories and return the last console output in that case. Do not continue to GI inventory until returned artifacts are inspected.

The sections below retain the individual commands and initial machine recommendation for reference; grouped execution above is the current route.

Owner-confirmed setup: **Terminal / Ubuntu / Aug2026**, DeIC Interactive HPC (SDU/K8s), CPU only, persistent root **`/work/Home/dl_binner/e001/e001-gate0`**, access expiry unknown. The [initial owner probe](validation.md#owner-returned-initial-probe-2026-09-18) confirms the upload checksum, mount and Ubuntu 24.04.4 x86_64; micromamba and GNU time are missing. Actual job allocation is **4 vCPU/12 GB**, started 2026-09-18 at 15:29, with submitted duration not yet confirmed. Keep it for extraction/bootstrap; the 8/24 recommendation below is not a minimum for those steps. At 4 vCPU, each allocated hour costs 4 core-hours, including idle time. Confirm remaining job time before installation. Keep environments at `$WORK/envs/mapping`, `$WORK/envs/amber`, etc. Package caches live at `$WORK/micromamba` and `$WORK/cache/pip`; they are not shared environments.

Start with **8 vCPU, at least 24 GB RAM, one node, no GPU, a two-hour job limit**, named `e001-gate0-preflight`. Select the CPU product available to the owner's allocation; the public [product catalog](https://docs.cloud.sdu.dk/guide/resources-products.html) currently calls the Zen5 family `cpu-amd-zen5`, but the actual selectable label/RAM must be confirmed in the UI. If 8 vCPU provides more than 24 GB, keep that allocation; do not increase CPU merely to match an old label. If no suitable option is available, return a screenshot before submitting. The owner-reported CPU model differs from the current public catalog; record the actual allocation rather than silently overwriting either source.

Two hours reserves at most **16 allocated core-hours** at 8 vCPU, within the 32-core-hour total preflight allowance. This is an initial timebox, not a measured installation estimate. Setup can be network/solver-bound; return failures instead of extending or retrying automatically. Stop the job when finished or stepping away: setup, downloads and idle allocation all consume budget. Select Bash, attach **Home** in Storage so it mounts at `/work/Home`, and leave initialization scripts, public links, SSH and multi-node options unused. Official [job submission documentation](https://docs.cloud.sdu.dk/guide/submitting.html) describes the controls and persistent `/work` volumes; consulted 2026-09-18. App version availability and bundled prerequisites have not been verified inside the owner's job.

### First checkpoint: transfer and prerequisites

Locally, Codex commits reviewed changes, then runs:

```sh
python3 scripts/e001_bundle.py --out artifacts/e001-transfer
```

This reads an allowlist from the clean Git HEAD and creates `e001-code-<12-character-commit>.tar.gz` plus `.tar.gz.sha256`. It includes runtime scripts, tests, the E001 protocol/configuration and tool-source snapshot, with the full commit in `SOURCE_COMMIT`. It excludes Git history, thesis/papers/tool caches, local environments, raw data and results. It is an execution package, not a complete documentation checkout. It downloads nothing, takes seconds and refuses existing output names or a dirty checkout. Artifacts are ignored locally. Verify archive contents and portable tests from an extracted copy before handoff.

**Before starting the paid job**, use UCloud Files to create/open `Home/dl_binner/e001/e001-gate0/transfer` and upload the two files. This transfers our small code package only, not software environments or research data. Use the [file upload interface](https://docs.cloud.sdu.dk/guide/file-management.html); neither a GitHub remote nor SSH setup is required. Do not use the interface's Uncompress action yet. Then start the job as specified above.

Codex supplies the literal checksum filename in chat. Run only this initial read-only probe, replacing that filename with the supplied one:

```sh
bash <<'SH'
set -eu
cd /work/Home/dl_binner/e001/e001-gate0/transfer
pwd
uname -sm
cat /etc/os-release
df -h .
for cmd in bash git micromamba python3 tar sha256sum timeout curl bzip2; do
    command -v "$cmd" || printf 'MISSING: %s\n' "$cmd"
done
if test -x /usr/bin/time; then /usr/bin/time --version; else printf 'MISSING: GNU time\n'; fi
sha256sum --check e001-code-<commit>.tar.gz.sha256
SH
```

This reads the mounted directory, OS, program availability and uploaded archive; it creates no experiment files, installs/downloads nothing, and should take seconds with negligible RAM/CPU. Shell/session history may be recorded by Terminal itself. Return **all output**, the UI's selected machine name/vCPU/RAM, and job start time. A missing command is a finding, not permission to install ad hoc. A missing path, checksum failure, unexpected architecture or other error means stop. Even if everything passes, stop here for inspection. No code extraction, installs, smoke or inventory yet. `df` reports filesystem capacity, not necessarily the owner's quota; UI allocation is authoritative for vCPU/RAM.

### Later checkpoints: extraction and prerequisites

After inspection, Codex supplies the literal commit in these commands. They extract only the verified package, preserve the upload, and refuse an existing code directory:

```sh
bash <<'SH'
set -euo pipefail
WORK=/work/Home/dl_binner/e001/e001-gate0
CODE="$WORK/e001-code-9c2b0ec6feb3"
cd "$WORK/transfer"
sha256sum --check e001-code-9c2b0ec6feb3.tar.gz.sha256
if test -e "$CODE" || test -L "$CODE"; then
    printf 'STOP: code directory already exists; preserve it for inspection.\n' >&2
    exit 1
fi
tar --keep-old-files -xzf e001-code-9c2b0ec6feb3.tar.gz -C "$WORK"
test "$(cat "$CODE/SOURCE_COMMIT")" = 9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea
printf 'Code extraction verified: %s\n' "$CODE"
cat "$CODE/SOURCE_COMMIT"
SH
```

Expected work: seconds, less than a few MB written, no downloads; return the commit or any error and do not continue after failure. Before setup, verify Git, micromamba, GNU time and timeout. If missing, prepare an explicit reviewed bootstrap from the observed Ubuntu version: persistent micromamba binary under `$WORK/bin`, caches under `$WORK/micromamba`, tool environments still under `$WORK/envs`. Do not assume micromamba is bundled or run a remote installer blindly. System packages, if needed, modify the disposable container, not the persistent project. Bootstrap commands and software download sizes are deferred until the probe identifies what is actually missing.

### Later checkpoints: mapping, then AMBER

Issue each command separately in chat after explaining its row below; inspect returned output before the next command. Variables must be restored after opening a new terminal. Do not paste this entire block as an unattended sequence.

```sh
cd "$CODE"
timeout --signal=TERM --kill-after=60s 45m bash scripts/e001_linux_setup.sh mapping "$WORK"
bash scripts/e001_linux_smoke.sh mapping "$WORK"
timeout --signal=TERM --kill-after=60s 45m bash scripts/e001_linux_setup.sh amber "$WORK"
bash scripts/e001_linux_smoke.sh amber "$WORK"
```

| Command | Purpose and writes | Downloads/resources | Return and stop condition |
| --- | --- | --- | --- |
| Mapping setup | Install pinned strobealign/samtools and fixture dependencies in `envs/mapping`; create `locks/mapping`, caches and empty `sources` directory. Setup stdout/stderr, exit code and elapsed seconds are retained under the lock directory. | Software only. Allow minutes to tens of minutes and several GB disk headroom across both environments; unmeasured Linux solve, 45-minute command cap (6 allocated core-hours at 8 vCPU). | Full terminal output and locks. Stop on any error/timeout, absent completion line, failed pip check or nonzero setup status. Do not delete partial environments. |
| Mapping smoke | Generate tiny synthetic FASTA/reads/BAMs in `fixture`; align and thin them; write `smoke/mapping*`. No research data. | No intended downloads. Threads bounded by the harness; should be minutes, not a benchmark. 30-minute smoke cap (4 allocated core-hours); actual usage saved. | `mapping.stdout`, `.stderr`, `.resources.txt`, `.exit-code.txt`, `mapping/smoke.json` if produced. Stop on any failure; return partial files too. |
| AMBER setup | Clone pinned evaluator to `sources/AMBER_evaluation`, install in `envs/amber`, retain `locks/amber` and caches. | Software/source only, including pip dependencies; 45-minute cap. No reference genomes, GI data or models. | Full output and locks, same failure rules as mapping setup. |
| AMBER smoke | Exercise actual evaluator on small synthetic truth/binning tables; write `smoke/amber*`. No scientific binning. | No intended downloads; small CPU/RAM workload, 30-minute cap. | AMBER stdout/stderr, resource/status files and `amber/smoke.json`; stop for inspection even on success. |

Per-command timeouts are failure bounds, not additive permission to exceed the two-hour job or 32-core-hour preflight budget. Do not start a stage when the job is about to expire. A killed job may lack the final status file; that means incomplete, not success. Return logs before retrying or extending. Setup logs use `tee`; native smoke stdout is saved to files and a successful run can be quiet at the terminal.

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

250 GB is enough for the inventory but **not yet established sufficient for E001**. The owner's execution brief clarifies that storage can expand and is not a current scientific design constraint. The former 200-GB ceiling is now a provisioning review threshold, not a cap: estimate peak storage from one sample and retained outputs and arrange more space when needed. Do not reduce samples, replicates or retention merely to fit the conservative estimate. Still verify sufficient actual free space before writes; an expandable quota is not automatically already allocated.

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
