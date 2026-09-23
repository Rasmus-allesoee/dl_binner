# E001: Validation and UCloud Preflight

Updated: 2026-09-23. This is the execution guide, not a scientific result. Read the [protocol](README.md) and [choice revision](../../docs/decisions/D004-human-cpu-preflight.md) first.

## Current action, 2026-09-23

Full sample-0 preprocessing is accepted: **42.24 minutes, 2.816 allocated
core-hours, 15.412 GB new outputs** at 4 vCPU / 12 GB. Reuse the accepted
`sample0-preprocess-6_gyxp5d` outputs and `envs/workflow`; do not rerun that pilot.
The new traces identify **persistent-filesystem read stalls during imports**.
The next grouped command stages the reviewed workflow snapshot on local `/tmp`,
verifies its interpreter/package origins and exact sample-0 inventory, checks
the actual CLI and DAG, then acquires/preprocesses the remaining nine libraries.
It installs no software and preserves the original environments. See the
[evidence and correction](validation.md#workflow-filesystem-stall-identified-2026-09-23)
and [D006's narrow execution-copy exception](../../docs/decisions/D006-environment-ownership.md#job-local-workflow-execution-copy-2026-09-23).

Use **Terminal / Ubuntu / Aug2026, one node, 8 vCPU / 24 GB RAM**, with both
Home and the offered shared storage mounted. Slurm cluster **No** is simplest
for this command; an already enabled **Yes** is compatible, but this workflow
uses the local executor and does not submit Slurm jobs. No separate app is needed.
Do not run competing jobs within this allocation. See [D009](../../docs/decisions/D009-parallel-preprocessing-terminal.md).

Total allocation and per-sample resources are distinct: two mapping pipelines
at **4 CPUs and a 10-GB scheduling budget each**, with a 23-GB global rule-memory
cap and 1 GB held outside it for the coordinator/OS. Two mappings request 20 GB;
up to 3 GB remains for another rule to overlap. Each mapping uses two strobealign
threads, one filter and one sort CPU. Downloads use one slot and can overlap
compute when the total resource limits permit. Set actual allocation arguments
accurately; the driver rejects insufficient CPU/RAM instead of oversubscribing
or silently reducing concurrency. Serial fallback is 4 vCPU / 12 GB with
`--max-concurrent-samples 1`. The new
data require about **230.4 GB retained**, so shared storage is now justified.
Have **275 GB free and available to this project** there (filesystem free space
does not prove quota). Existing environments and sample 0 remain in Home.

Upload the replacement code bundle/checksum **and**
`e001-workflow-0fb6955cdc62.tar.gz` with its checksum to Home `transfer/`, then:

```sh
bash <<'SH'
set -euo pipefail
WORK=/work/Home/dl_binner/e001/e001-gate0
LOG=$(mktemp "$WORK/transfer/e001-multisample.XXXXXX.log")
echo "Terminal log: $LOG"
(
BUNDLE=e001-code-cccf8c7f7846
CODE="$WORK/$BUNDLE"
SHARED='/work/RasmusAllesøeNielsen#2936'
if ! test -d "$SHARED"; then
    echo "STOP: shared storage is not mounted; do not substitute Home"
    exit 1
fi
DATA="$SHARED/dl_binner/e001"
mkdir -p "$DATA"
cd "$WORK/transfer"
sha256sum --check "$BUNDLE.tar.gz.sha256"
sha256sum --check e001-workflow-0fb6955cdc62.tar.gz.sha256
if test -e "$CODE" || test -L "$CODE"; then
    echo "STOP: code directory already exists"
    exit 1
fi
tar --keep-old-files -xzf "$BUNDLE.tar.gz" -C "$WORK"
python3 -I "$CODE/scripts/e001_multisample.py" "$WORK" \
    --data-root "$DATA" --vcpus 8 --ram-gb 24 \
    --sample-vcpus 4 --sample-ram-gb 10 --max-concurrent-samples 2 \
    --workflow-snapshot "$WORK/transfer/e001-workflow-0fb6955cdc62.tar.gz" \
    --allow-remaining-archives
) 2>&1 | tee "$LOG"
SH
```

Staging needs 2 GB free on local `/tmp` (about 0.75 GB retained until job end),
plus the 267.6-MB persistent snapshot archive. It takes a sequential archive read
and local extraction, with a 600-second fail-fast limit, not an expected duration.
The driver then checks runtime origins, exact inventory, CLI and DAG. A failure
stops dependent work and returns logs; no automatic environment rebuild occurs.
If all gates pass, the same command continues without another chat checkpoint:

1. Checks accepted sample-0 small records/output presence and current runtime
   isolation/versions, without remapping or repeating native smoke checks.
2. Uses the verified job-local Snakemake 9.13.7 execution copy and the original
   separate mapping environment. No software installation, upgrades or changes
   to authoritative environment prefixes.
3. Downloads **91.70 GB** in nine publisher archives for samples
   `1,2,3,4,5,9,10,11,12`, checking size/ETag and complete publisher MD5 and
   recording SHA256. Reads are now explicitly authorized by the command flag;
   this is not another bounded-prefix task.
4. Extracts/validates each complete anonymous read library, maps/filter/sorts/
   indexes C0 with accepted strobealign settings, then thins/indexes CT for
   replicate 0. Seeds are 1001-1009 in frozen sample order, not literal sample
   number (sample 9 uses 1006). No added MAPQ filter or scientific-design change.
5. Writes a ten-sample BAM manifest referencing original sample 0 plus nine new
   samples, per-rule extended benchmarks, detailed tool logs and live
   `progress.log`. Terminal shows stage messages, download/extraction counts,
   mapper logs when emitted, and one-minute heartbeats; a heartbeat is not a
   percentage-complete estimate. Rule stdout may be quiet during native mapping.
6. Packages compact evidence under Home as `multisample-preprocess-...-return.tar.gz`
   and `.sha256`, even after an ordinary driver failure. Research data stay in
   the uniquely named shared `multisample-preprocess-.../` attempt directory.

Expect roughly **4-5 hours**, versus the prior 7-9-hour serial projection.
Parallel throughput is not yet measured; shared storage and network contention
can reduce speedup. Plan around **32-40 allocated core-hours**, not guaranteed
cost savings. The unchanged 80-core-hour ceiling allows **10 hours at 8 vCPU**.
A six-hour initial
job is reasonable; extensions are owner-managed. Driver cost
is total allocated vCPUs times wall time, including download waiting, not the
sum of per-rule CPU time. The previous 12-vCPU bundle is superseded, not rewritten.
No sample-0 rerun, other body sites,
extra CT replicates, feature extraction, model training or biological scoring.

**Stop after completion or failure**, preserve all outputs, and return the
printed archive, checksum and terminal log. Do not rerun the whole group if only
a later sample fails: completed samples are reusable after evidence review.
Nothing deletes archives/FASTQs or touches colleagues' directories. After the
return review, prepare native multi-sample features and resource-aware paired
pilot orchestration; fitting still needs its own tested launch and review.

## Completed sample-0 instructions (historical)

Mapper/storage feasibility and subsequent local BAM/read-origin analysis are
accepted. [D008](../../docs/decisions/D008-mapper-and-first-preprocessing-slice.md)
retains strobealign. Next run the **Snakemake full sample-0 preprocessing slice**,
not a repeated mapper comparison. No more BAM uploads are needed.

Use **4 vCPU / 12 GB RAM** and the existing persistent root. Set the actual values
below if different; this pipeline needs at least 3 vCPU because mapping, primary
filtering and sorting run concurrently. Two of four CPUs are reserved for the
samtools stages, leaving two mapper threads. The driver checks for 25 GB free.

Upload the new code bundle/checksum to `transfer/`, then:

```sh
bash <<'SH'
set -euo pipefail
WORK=/work/Home/dl_binner/e001/e001-gate0
LOG=$(mktemp "$WORK/transfer/e001-preprocess.XXXXXX.log")
echo "Terminal log: $LOG"
(
BUNDLE=e001-code-<commit>
CODE="$WORK/$BUNDLE"
cd "$WORK/transfer"
sha256sum --check "$BUNDLE.tar.gz.sha256"
if test -e "$CODE" || test -L "$CODE"; then
    echo "STOP: code directory already exists"
    exit 1
fi
tar --keep-old-files -xzf "$BUNDLE.tar.gz" -C "$WORK"
python3 -I "$CODE/scripts/e001_preprocess.py" "$WORK" --vcpus 4 --ram-gb 12
) 2>&1 | tee "$LOG"
SH
```

The driver creates a unique `sample0-preprocess-...` directory and installs
Snakemake 9.13.7 in separate `envs/workflow` if absent; mapping keeps its existing
environment. **Downloads are workflow software only, no research data.** The
accepted archive in `mapper-feasibility-13l53afq/sample_0.tar.gz` is reused.
Snakemake performs a dry-run then the three dependent rules: validate/extract all
16,666,043 pairs, map/sort/index C0, and thin/index/report CT (10%, seed 1000).
No full SAM file is stored. New FASTQ and BAMs are retained; nothing is deleted.

At four vCPUs, provision roughly **30-50 minutes** based on the prefix's measured
mapping throughput with fewer mapper threads plus extraction/sorting/QC; full
sample composition and I/O may differ. This is an estimate to test, not a promised
runtime. The workflow has a separate **60-minute execution timeout**, with setup
timeouts outside it. Expected extra data are roughly 11 GB FASTQ plus 5-6 GB BAMs,
subject to full-sample measurement. Shared storage is not used automatically.

Stop after completion or failure; return the printed
`sample0-preprocess-...-return.tar.gz`, `.sha256`, and terminal log. Partial files
remain for inspection. Do not rerun or delete them without reviewing the result.
No new sample acquisition, feature extraction, model training or biological
scoring is included. Full-sample measurements determine the next acquisition/
multi-sample workflow block without repeating accepted preflights.

## Completed local diagnostic instructions (historical)

All three mapper attempts are reviewed; the third passed and operational
mapper/storage feasibility is accepted. **Do not run the historical commands below.**
Next transfer only these existing files for local discrepancy analysis:

- `/work/Home/dl_binner/e001/e001-gate0/mapper-feasibility-89gpt00u/strobealign/mapped.bam`
  -> `agent_context/mapping/strobealign/mapped.bam` (30.7 MB, received)
- `/work/Home/dl_binner/e001/e001-gate0/mapper-feasibility-89gpt00u/bowtie2/mapped.bam`
  -> `agent_context/mapping/bowtie2/mapped.bam` (34.2 MB, received)

No `.bai`, SAM, FASTQ, index or sample-archive transfer is needed. The BAM hashes
are already pinned in [mapper-observed.json](mapper-observed.json); the diagnostic
checks them and uses the frozen local contig metadata. Nothing is installed,
downloaded from publishers, remapped or trained. Existing owner files stay intact.
The owner need not rent a new job to do computations; use ordinary file download.

Agent-side command after receiving both files (not an owner UCloud command):

```sh
.venv/bin/python scripts/e001_mapper_diagnostics.py \
  --strobe-bam agent_context/mapping/strobealign/mapped.bam \
  --bowtie-bam agent_context/mapping/bowtie2/mapped.bam \
  --contigs artifacts/e001-population-reviewed/contigs.jsonl \
  --read-truth artifacts/e001-read-truth/sample0-reads-mapping.tsv.gz \
  --out artifacts/e001-mapper-truth-reviewed
```

Expect seconds/minutes on the local machine with modest memory and small JSON/TSV
outputs. It refuses mismatched files and existing outputs. If files cannot be
transferred, the same analysis can instead be wrapped for owner-run execution;
do not default to another mapper run. See [validation](validation.md) for the
scientific assessment boundary and next Snakemake preprocessing/pilot direction.

## Completed mapper instructions (historical)

Integration has passed; do not rerun it. Next is grouped mapper/storage feasibility.
Use **4 vCPU / 12 GB** initially; this is a recommendation, not an accounting
assumption. Set `--vcpus` and `--ram-gb` to the actual rented machine. All tool
threads in this new task follow the explicit vCPU value.

Acquisition decision: direct CAMI FASTQ payload returns 401 despite readable
metadata. The publisher's accessible sample-0 archive is 9.74 GB. The command
below explicitly opts into **one sample archive**, retained for reuse, not ten
samples. Do not run it unless the owner agrees to this acquisition expansion.
An already downloaded archive can instead be supplied with `--archive PATH`.

Upload the new bundle/checksum to the existing transfer directory, then:

```sh
bash <<'SH'
set -euo pipefail
WORK=/work/Home/dl_binner/e001/e001-gate0
LOG=$(mktemp "$WORK/transfer/e001-mappers.XXXXXX.log")
echo "Terminal log: $LOG"
(
BUNDLE=e001-code-<commit>
CODE="$WORK/$BUNDLE"
cd "$WORK/transfer"
sha256sum --check "$BUNDLE.tar.gz.sha256"
if test -e "$CODE" || test -L "$CODE"; then
    echo "STOP: code directory already exists"
    exit 1
fi
tar --keep-old-files -xzf "$BUNDLE.tar.gz" -C "$WORK"
python3 -I "$CODE/scripts/e001_mapper_feasibility.py" "$WORK" \
    --vcpus 4 --ram-gb 12 --allow-sample-archive
) 2>&1 | tee "$LOG"
SH
```

Writes: new code/attempt directory and a separate `envs/bowtie2` environment;
resolved package list, one sample archive, paired prefix FASTQs, Bowtie2 index,
SAM/BAM files and diagnostics. Other environments and accepted inputs stay intact.
Downloads: Bowtie2 dependencies and the single sample archive only. The archive
is size/ETag-bound and hashed; failed partials are preserved, not silently reused.
No training, binning scores or scientific hypothesis tests are performed.

If a previous attempt completed the archive download but failed later, reuse its
`sample_0.tar.gz` with `--archive <existing-archive>` instead of using
`--allow-sample-archive`; this avoids downloading the same 9.74 GB payload again.

Needs 20 GB free space before fresh acquisition (8 GB with existing archive).
The shared heavy-data location is documented in AGENTS but is not used automatically;
if this check fails, review actual quota and location before retrying. Download
time depends on network throughput; mapping/index time is what this task measures.
Timeout ceilings (one hour download, 30 minutes extraction, 90 minutes mapping
group) are deliberately separate from expected runtime, not an estimate of spend.
Stop after completion or failure and return the printed
`mapper-feasibility-...-return.tar.gz`, `.sha256` and terminal log. No separate
chat turn is needed between setup, acquisition, extraction and mapping success.

## Completed integration instructions (historical)

COMEBin and MetaBAT2 smoke/CPU results are accepted separately; see
[validation](validation.md). Next run native clustering, COMEBin marker-guided
selection and AMBER handoff, not another setup or optimizer check.

Use **8 vCPU / at least 24 GB RAM, CPU only**, with the existing persistent work
root. Upload the new code archive/checksum to its `transfer/` directory. Run:

```sh
bash <<'SH'
set -euo pipefail
WORK=/work/Home/dl_binner/e001/e001-gate0
LOG=$(mktemp "$WORK/transfer/e001-integration.XXXXXX.log")
echo "Terminal log: $LOG"
(
BUNDLE=e001-code-<commit>
CODE="$WORK/$BUNDLE"
cd "$WORK/transfer"
sha256sum --check "$BUNDLE.tar.gz.sha256"
if test -e "$CODE" || test -L "$CODE"; then
    echo "STOP: code directory already exists"
    exit 1
fi
tar --keep-old-files -xzf "$BUNDLE.tar.gz" -C "$WORK"
python3 -I "$CODE/scripts/e001_integration.py" "$WORK"
) 2>&1 | tee "$LOG"
SH
```

This creates a new code directory, log and unique `native-integration-...` attempt
plus return archive/checksum. Existing inputs, separate tool environments and
attempts stay intact. **No installs or downloads.** COMEBin setup already installed
CheckM data; `CHECKM_DATA_PATH` selects that persistent copy without modifying its
configuration. Missing prerequisites stop the affected stage and return diagnostics.

The fixture is 128 frozen GI sequences, 10-100 kb each, selected by ID hash without
truth. Random embeddings exercise VAMB clustering, COMEBin's full 120-candidate
grid, FragGeneScan/HMM marker finding, CheckM profiling and native winner selection.
Full labels, not quality-filtered subsets, go to AMBER. Truth is used only by the
evaluator. These are integration checks, not training or biological results.
Independent tools continue if the other fails; dependent stages require success.

Expect minutes to tens of minutes, with stage timeouts totaling about 50 minutes /
6.7 allocated core-hours plus packaging overhead. Allow a few GB for intermediate
files. Return the printed `native-integration-...-return.tar.gz`, its `.sha256`
and terminal log, including on failure. If packaging fails, retain the attempt
and return the log. Stop for review; no bulk reads or scientific training.

Then resolve bounded read-prefix access for mapping/storage feasibility. The
direct CAMI read object returned HTTP 401 and the publisher archive starts with
BAMs; see validation. Do not silently substitute a bulk archive download.

## Completed grouped setup instructions (historical)

The following records the prior setup/CPU task; it is not the next action.

VAMB passed; see [observed timing](native-vamb-observed.json). The frozen population
and mapping/AMBER/VAMB checks are settled. Next run **COMEBin and MetaBAT2 together**
using the new grouped driver. [D006](../../docs/decisions/D006-environment-ownership.md)
retains all five separate tool environments under the existing work root. No
environment is moved, merged, upgraded or rebuilt merely because of a new gate.

Select **8 vCPU / at least 24 GB RAM, CPU only**, with the same persistent Home
mount. The larger allocation gives headroom for COMEBin's six-view, batch-1024
contrastive loss; do not reduce the native batch to make the preflight fit. Upload
only the new code archive/checksum to the existing `transfer/` directory, then:

```sh
bash <<'SH'
set -euo pipefail
WORK=/work/Home/dl_binner/e001/e001-gate0
LOG=$(mktemp "$WORK/transfer/e001-remaining.XXXXXX.log")
echo "Terminal log: $LOG"
(
BUNDLE=e001-code-<commit>
CODE="$WORK/$BUNDLE"
cd "$WORK/transfer"
sha256sum --check "$BUNDLE.tar.gz.sha256"
if test -e "$CODE" || test -L "$CODE"; then
    echo "STOP: code directory already exists"
    exit 1
fi
tar --keep-old-files -xzf "$BUNDLE.tar.gz" -C "$WORK"
python3 -I "$CODE/scripts/e001_remaining_cpu.py" "$WORK"
) 2>&1 | tee "$LOG"
SH
```

The driver attempts MetaBAT2 then COMEBin, each through setup, isolated imports,
pip consistency, native synthetic smoke, and a bounded CPU check. A failed tool
skips its dependent stages but the other independent tool still runs. Successful
prior setups are reused; incomplete setups remain untouched and are reported.
No separate chat checkpoint is needed between successful routine stages.

Downloads are **software, source and source-bundled marker HMMs**, not reads or
scientific datasets. Writes are separate `envs/metabat` and `envs/comebin`, their
`sources/`, `locks/`, package caches, a MetaBAT build/source copy under `build/`,
and a unique `native-remaining-...` attempt. Other environments, old attempts,
frozen inputs and the reference caches are not modified. No system/root installs.

MetaBAT2 receives generated FASTA/depth data matching E001's 22,594 contigs,
817,438,232 bases and ten samples, with synthetic composition/coverage groups.
COMEBin receives random ten-sample coverage/variance and k-mer features: six
views, batch 1,024, source models and native InfoNCE, one warmup and two measured
forward/backward/AdamW steps. It projects 22 batches per epoch over the 200-epoch
ceiling, reporting a twofold margin. Neither check is scientific training; no
research model/checkpoint is produced. These checks do not yet exercise COMEBin's
complete marker-guided clustering grid or real BAM extraction throughput.

Expect tens of minutes, with roughly 15 GB disk headroom for environments/cache,
build and synthetic files. Each setup has 30 minutes, smoke 5 minutes and CPU
measurement 10 minutes; import/pip checks add small limits. Total upper bound is
about 100 minutes / 13.4 allocated core-hours plus wrapper overhead, within the
32-core-hour preflight ceiling only insofar as earlier allocated usage leaves
that headroom. Actual successful drivers so far are much shorter; do not equate
their time with all owner job/idle spend. Owner manages job duration/extensions.

Return the printed `native-remaining-...-return.tar.gz`, its `.sha256` and automatic
terminal `.log`. No full synthetic FASTA or environment is included in the return.
If no archive exists, return the log. Stop after the grouped task, regardless of
status. Review may accept one tool and investigate the other without rerunning
both. No bulk read downloads or scientific fits are authorized.

## Completed VAMB step, 2026-09-20

The following VAMB-only command is retained as executed history, not the next action.

Taxonomy-aware owner output `inventory-resume-6z45cola` is accepted and the
[input population is frozen](frozen-inputs.json). Do not rerun inventory,
taxonomy, mapping or AMBER smoke. The next action is **VAMB CPU preflight**.

Upload only the new committed code bundle and its checksum to the existing
`/work/Home/dl_binner/e001/e001-gate0/transfer/`. No taxonomy or data reupload.
Use the commit-specific bundle name supplied in chat:

```sh
bash <<'SH'
set -euo pipefail
WORK=/work/Home/dl_binner/e001/e001-gate0
LOG=$(mktemp "$WORK/transfer/e001-vamb.XXXXXX.log")
echo "Terminal log: $LOG"
(
BUNDLE=e001-code-<commit>
CODE="$WORK/$BUNDLE"
cd "$WORK/transfer"
sha256sum --check "$BUNDLE.tar.gz.sha256"
if test -e "$CODE" || test -L "$CODE"; then
    echo "STOP: code directory already exists"
    exit 1
fi
tar --keep-old-files -xzf "$BUNDLE.tar.gz" -C "$WORK"
python3 -I "$CODE/scripts/e001_vamb_cpu.py" "$WORK"
) 2>&1 | tee "$LOG"
SH
```

Use **4 allocated vCPU / 12 GB RAM**. The CPU projection assumes this allocation.
Expect tens of minutes for first software installation, then minutes for checks;
allow approximately 5 GB for environment/cache/source and small synthetic outputs.
These are provisioning estimates, not measured Linux outcomes. Stage timeouts:
45 minutes setup, 2 minutes each environment/pip check, 10 minutes smoke and
10 minutes synthetic timing, roughly 4.6 allocated core-hours maximum plus wrapper
overhead. A timeout kills the command's process group and returns diagnostic logs.

The driver creates a unique `native-vamb-...` attempt, checks fresh-job prerequisites,
uses `$WORK/bin/micromamba` if installing, and keeps the environment at
`$WORK/envs/vamb`, source at `sources/vamb`, caches under the work root and locks
at `locks/vamb`. It downloads **software only** (pinned VAMB source and CPU
dependencies); no research data, model weights, reference databases or read archives.
An intact previously completed VAMB setup can be reused; partial setup is preserved
and reported, not deleted or silently reinstalled. No system/root package installs.

It then checks isolated imports/pip consistency and runs VAMB's previously prepared
native feature/scale/zero-row smoke on existing synthetic BAMs. Finally it times
native VAE forward/backward/optimizer epochs on generated random arrays with
22,594 rows and ten samples, not on the scientific contigs or coverage. Each of
256/512/1024/2048/4096 batch sizes gets one warmup and two measured epochs.
The projection weights them by the CLI's 300-epoch schedule (25/50/75/75/75),
uses the slower measured epoch, and reports a twofold margin. This is an optimizer
microbenchmark, not a scientific fit, and writes no trained model.

Return the printed `native-vamb-...-return.tar.gz`, its `.sha256`, and terminal
`.log`. If no archive is produced, return the log. Stop after either success or
failure. Returned locks, native smoke and timing require inspection; a projection
does not approve the full experiment budget or account for extraction/clustering.
COMEBin/MetaBAT2 native checks and read-prefix feasibility remain subsequent tasks.

## Completed taxonomy step, 2026-09-20

The following command is retained as execution history, not the next action.

The owner completed `inventory-resume-ef6z97y9` successfully with source
`9e1f939d4585bdf191dd562787932431235ff281`. The return was verified on
2026-09-20; see the [accepted conversion](validation.md#owner-conversion-accepted-2026-09-20).
Do not rerun the old taxonomy-free conversion. Historical taxonomy and population
now pass locally; see [evidence](../../docs/evidence/2026-09-20-gi-taxonomy.md).
The next owner step is the new taxonomy-aware command below. No read download or
training is authorized.

Upload the new code bundle/checksum and the owner's local
`agent_context/taxdump_cami2_toy.tar.gz` into the existing persistent directory
`/work/Home/dl_binner/e001/e001-gate0/transfer/`, keeping their filenames.
The taxonomy archive is 93,167,485 bytes, is not included in the code bundle,
and must remain untracked. No upload to UCloud has been performed by the agent.
Its SHA-256 is pinned in `taxonomy-policy.json` and verified automatically.

```sh
bash <<'SH'
set -euo pipefail
WORK=/work/Home/dl_binner/e001/e001-gate0
LOG=$(mktemp "$WORK/transfer/e001-taxonomy.XXXXXX.log")
echo "Terminal log: $LOG"
(
BUNDLE=e001-code-<commit>
CODE="$WORK/$BUNDLE"
cd "$WORK/transfer"
sha256sum --check "$BUNDLE.tar.gz.sha256"
if test -e "$CODE" || test -L "$CODE"; then
    echo "STOP: code directory already exists"
    exit 1
fi
tar --keep-old-files -xzf "$BUNDLE.tar.gz" -C "$WORK"
python3 -I "$CODE/scripts/e001_inventory_resume.py" "$WORK" --convert \
    --taxonomy "$WORK/transfer/taxdump_cami2_toy.tar.gz"
) 2>&1 | tee "$LOG"
SH
```

Use 4 vCPU / 12 GB. Expect minutes, primarily file reads, not training; reserve
roughly 2 GB additional disk space for a new attempt and code. The command
downloads/installs nothing. It probes the persistent environment, verifies the
existing GI/setup inputs and taxonomy archive/all members, and writes only
`nodes.dmp` from the taxonomy archive into the new attempt. It regenerates the
canonical data and population in that attempt and requires unchanged canonical
FASTA/truth hashes plus exact locally verified population/output hashes and all
population gates. Old accepted and failed attempts remain untouched.

Return the printed `inventory-resume-...-return.tar.gz`, its `.sha256`, and the
automatic terminal `.log`; if packaging never starts, return the log alone.
Expect scientific population status `validated`, but this is only the input
population gate, not authorization for scientific execution. Stop after the command
on either success or failure. A mismatch fails closed and requires review.

## Completed conversion command, 2026-09-19

The publisher provenance issue is resolved in [D005](../../docs/decisions/D005-gi-input-derivative.md).
The owner completed the verified conversion of that declared derivative.
Gate 0 is partially complete, Gate 1 is awaiting taxonomy/population approval,
and scientific Gate 2 has not started.

This older command used the [resume driver](../../scripts/e001_inventory_resume.py).
The old `e001_gi_inventory.sh`, `e001_retry_conversion.sh`, and `e001_hmp_audit.sh` are retired.
The resume driver does not acquire data or install software. It:

1. Creates a unique `inventory-resume-...` attempt under the persistent work root.
2. Probes `envs/mapping/bin/python`, NumPy, Biopython and pysam with isolated
   Python paths, verifying their environment location on this new job.
3. Verifies the original mapping and full setup archive checksums, compares
   setup metadata-member hashes with the inspected publisher prefix, and records
   those checks. It reads the archive without unpacking its source genomes.
4. Runs the complete input audit and checks the exact reviewed source hashes.
5. With `--convert`, applies the explicit policy into the attempt's `input/`.
   Every exception, alias and mapped-coordinate count must match. Unknown
   anomalies stop the attempt. Without the flag, it only checks and audits.
6. Packages small logs, audit, policy, exclusion report and inventory into a
   uniquely named return archive/checksum beside the attempt. It prints the exact
   paths and any failure traceback. FASTA and bulk contig metadata stay on UCloud.

The command template below is filled with the exact commit in chat. Upload only
the new bundle/checksum into the existing `transfer/` directory:

```sh
bash <<'SH'
set -euo pipefail
WORK=/work/Home/dl_binner/e001/e001-gate0
LOG=$(mktemp "$WORK/transfer/e001-resume.XXXXXX.log")
echo "Terminal log: $LOG"
(
BUNDLE=e001-code-<commit>
CODE="$WORK/$BUNDLE"
cd "$WORK/transfer"
sha256sum --check "$BUNDLE.tar.gz.sha256"
if test -e "$CODE" || test -L "$CODE"; then
    echo "STOP: code directory already exists"
    exit 1
fi
tar --keep-old-files -xzf "$BUNDLE.tar.gz" -C "$WORK"
python3 -I "$CODE/scripts/e001_inventory_resume.py" "$WORK" --convert
) 2>&1 | tee "$LOG"
SH
```

Keep 4 vCPU / 12 GB for this bounded inventory step. Expect seconds to a few minutes
depending on filesystem speed, hashing approximately 3 GB of existing files and
writing another retained FASTA/metadata set. Native peak RAM on the complete input
remains to be observed. Return the two printed return files and the automatically
captured terminal log; copying text from the terminal is unnecessary.
Exit zero with scientific status `blocked` is expected until taxonomy is resolved.
Stop after the command regardless of status; no read downloads or training follow.
The driver uses Python timing/resource counters, so GNU time, sudo and micromamba
on PATH are unnecessary. Python 3, tar and sha256sum are needed for transfer/run;
the persistent environment is checked before conversion. A missing environment
produces a diagnostic return, not an automatic reinstall.

## New UCloud jobs

The owner confirmed that a new Terminal job resets container-level software.
Preserve and attach the same `/work/Home` mount. Downloads, versioned code,
micromamba binary/cache and `envs/` under the experiment root persist there.
Do not infer persistence of `/usr/bin/time` or other apt-installed utilities.
A fresh job does not require rebuilding intact tool environments; use absolute
paths and repeat small import/binary checks. For later native jobs that require
GNU time, provision it in a pinned persistent environment or explicitly recheck
and bootstrap the disposable package before using it. That later setup is not
part of this no-install resume command.

## Historical commands and setup reference

Everything below describes earlier completed or superseded entry points. Use
the current action above; retained history does not authorize rerunning bootstrap,
acquisition, old audits or conversion-recovery scripts.

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
