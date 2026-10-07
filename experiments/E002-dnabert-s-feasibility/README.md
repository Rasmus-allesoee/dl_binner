# E002: bounded frozen DNABERT-S CPU feasibility

Prepared/completed: 2026-10-03. Status: **technical feasibility accepted for a small
local comparison; bulk affordability unaccepted**. Operational inference check, **not** a genome
recovery experiment. [D011](../../docs/decisions/D011-first-binner-prototype.md)
owns the design decision and stop/revisit rules. No E001 result is reopened.

## Prospective contract

Use one public author checkpoint and one separate Python environment. Unmodified
checkpoint/tokenizer/custom-code files are bound in [model-pin](model-pin.json).
Dependencies are frozen in [requirements](requirements-local.txt); this is a local
Intel macOS runtime, not a validated Linux recipe. Retain downloads and installation
logs in ignored `artifacts/d011-dnabert-s-spike/`. Model metadata declares Apache-2.0;
custom source retains Apache-2.0/SPDX headers. The author repository has no `LICENSE`
at the probed root path. This local probe does not redistribute model/source assets
or resolve final product licensing.

[Configuration](config.json) is the executable source of truth. Four numerical
threads, interop scheduling limit one, no data-loader workers; OpenMP/BLAS caps four,
tokenizer parallelism off. One numerical stage at a time. Supervisor samples worker
and descendant RSS/CPU, stops at 8,000,000,000 bytes or 3,600 seconds and terminates
the worker group on fatal exit. Timing starts at worker launch, stricter than an
hour after setup. After the input-only failure below, the remaining ceiling is
3,560 seconds, preserving a total budget below one hour. No checkpoint search,
automatic retry, quantization, distillation
or full-model training.

Hash-select forty distinct parents at least 10 kb from the accepted canonical
FASTA, and center eight real-DNA windows at each of 500/768/1,000/2,500/10,000 bp.
Selection uses IDs only, no labels or measured features. Long-parent short windows
test speed and contracts; they do not establish native short-contig accuracy.
Bind the source SHA256 and window coordinates/bytes. Preserve the full assembly
length distribution only for a timing projection.

Extract float32 features with the author's PyTorch CPU attention fallback, frozen
weights and evaluation mode. Mean pooling includes attended special tokens to
match the author's unpadded example, but excludes padding. Canonicalize whole-DNA
orientation, divide into nonoverlapping chunks of at most 4,000 bp / 1,024 tokens,
split recursively in base coordinates if either strand exceeds the limit. Average
both strand features per chunk, then weight chunks by base length. These strand/
chunk adaptations are ours; full-contig author output is **not** claimed equivalent.
The token cap bounds quadratic attention; config position size 512 is not silently
treated as a hard native limit. No token truncation is enabled.

## Acceptance and measurements

The [probe](../../scripts/dnabert_s_cpu_spike.py) must check actual native author
single-sequence parity, unequal-length batch versus singles, padding contamination
under a naive mean, ordered IDs, exact chunk coverage/tails, reverse-complement
invariance, token handling beyond 512, finite nonzero embeddings, model freeze,
bound cache save/load and stale-ID rejection, checkpoint reload equivalence and
import origins. Local portable guard/cache/chunk tests are separate and do not
replace native model contracts.

Measure imports/load, first/cold extraction and length-specific warm timing on all
eight independent windows after one excluded warmup. Log compression, chunk counts,
process CPU/RAM, hardware and library limits. Project at this measured four-thread
budget for an explicit 10,000-contig equal-count length panel (29.536 Mb) and the
accepted 22,594-contig / 817.438 Mb FASTA, using nearest tested log-length per-base
rates. Label these rough projections, excluding setup/I/O/learning/clustering and
unmodelled compression/long-tail costs; no scaling to other machines/CPU counts.

Checkpoint loading alone is insufficient. If contracts fail or the resource ceiling
is reached, retain evidence and defer GLM in favor of the inexpensive contrastive
prototype. If contracts pass and a small development comparison is affordable,
prepare **one** short-inclusive representation comparison with frozen data, scoring,
cluster settings and cost before execution. No utility/biological claim follows
from feasibility. Full-assembly projections also inform eventual product choice;
a small comparison being feasible does not establish a cheap production binner.

## Local command and retained attempt

Commit protocol/code/configuration before timing. Run once from the repository root:

```sh
env -u PYTHONPATH -u PYTHONHOME -u PYTHONUSERBASE PYTHONNOUSERSITE=1 \
  artifacts/d011-dnabert-s-spike/env/bin/python scripts/dnabert_s_cpu_spike.py \
  --config experiments/E002-dnabert-s-feasibility/config.json \
  --output artifacts/d011-dnabert-s-spike/run-002
```

Output directory must be absent. Worker output goes to `terminal.log`; stage
timestamps and incremental `result.json` are retained alongside resource samples,
panel FASTA/provenance and hash-bound feature cache. Live progress can be read with
`tail -f artifacts/d011-dnabert-s-spike/run-002/terminal.log`. Supervisor receipt
records process resource observations and a four-thread wall budget; these are
local costs, **not UCloud billing**. No owner-run UCloud command is prepared.

Actual observations are bound in [observed.json](observed.json), with the small
[timing panel](timing-panel.json). Bulk DNA/features, native logs, supervisor and
setup receipts remain ignored with locators/hashes in that record.

## Input-preparation correction before native inference, 2026-10-03

`run-001`, source `5267241`, stopped after 32.9099 seconds with a strict A/C/G/T/N
validator rejecting the accepted FASTA. A whole-file audit found 162 valid IUPAC
ambiguity symbols across seven contigs (K22/Y33/S18/R44/W29/M16), with no invalid
DNA symbols. This is a probe input-contract defect, not a model/environment or
CPU-feasibility failure. No checkpoint was loaded or inference performed.
The unmodified source checksum remains accepted. Correct the reader/complement
to preserve all IUPAC symbols, retain the failure/audit and continue the same single
checkpoint/environment investigation as `run-002`. This narrow amendment neither
changes window selection nor increases the total time ceiling. Unknown-token
counts/ambiguity must remain explicit; no biological accuracy claim follows.

## Observed native result and acceptance

Source `c9437fc`, `run-002`: **completed**, all native contracts passed. One
checkpoint and one environment were used; the earlier input-only failure remains
retained. The model's 117,068,544 parameters stayed frozen on CPU. Python 3.10.15,
PyTorch 2.2.2, Transformers 4.27.0 (author-required version), NumPy 1.26.4 and
tokenizers 0.13.3 ran in a new venv built from the existing Python interpreter;
no reference/executed environment was modified. Resolved packages are pinned.
All inspected package imports originate inside this venv; executed custom model
code matches the pinned author's SHA256. Triton was absent and the author's
existing PyTorch fallback ran without a compatibility fork. The library's generic
revision warning appeared for a local directory; all its bytes were independently
verified before loading, with network/offline caches isolated.

Actual hardware: Intel i5-1038NG7 @ 2 GHz, four physical cores/eight logical CPUs,
16 GiB host RAM, Intel macOS 26.1. Torch intraop=4, interop=1; OpenMP and OpenBLAS
report four threads, tokenizer parallelism off, loader workers=0. Warm stages used
3.41–3.88 CPU equivalents. Lower aggregate use (2.90 CPUs) includes serial source
scans/loading/contracts; process observations do not imply four cores always stay
busy. No concurrency or missing native thread flag was inferred from a graph.

The forty independently selected parents yielded 118,144 real DNA bases at the
five lengths and a finite, nonzero 40×768 float32 feature matrix. The selected
windows contain no IUPAC ambiguity or unknown tokens; accepting IUPAC input does
not validate assignment quality for ambiguous sequences. Native unpadded author
pooling and unequal-length batch versus singles matched exactly (max difference
0); naive padding-inclusive averaging changed the shorter embedding by up to
0.36868. The attended-token mean avoids that contamination. The native ALiBi path
accepted 841 tokens beyond the config's initial 512; maximum observed chunk size
was 901 tokens under the explicit 1,024 ceiling. Every 10-kb sequence used three
chunks (4k/4k/2k), covering the full DNA and tail. Strand reversal, ID ordering,
freeze, byte-bound cache/reordered-ID rejection and checkpoint reload passed.
Both-strand/bp-weighted chunk features remain an adaptation, not an equivalence
claim for full-contig author features or biological utility.

| Real window | Warm seconds/window | Average CPUs | Tokens/base per strand, including specials |
| --- | ---: | ---: | ---: |
| 500 bp | 0.260 | 3.86 | 0.208 |
| 768 bp | 0.414 | 3.88 | 0.217 |
| 1,000 bp | 0.577 | 3.88 | 0.214 |
| 2,500 bp | 1.819 | 3.54 | 0.205 |
| 10,000 bp | 10.240 | 3.41 | 0.216 |

Eight independent windows per length after an excluded warmup. Model load took
8.641 s, first 500-bp extraction 0.364 s; these are first-use process measurements,
**not** cold-boot/disk-cache benchmarks. Successful supervisor wall time: 182.852 s;
peak sampled worker RSS: 1,313,681,408 bytes (1.314 GB / 1.223 GiB). Initial failure
plus success: 215.762 s, 0.239735 four-thread wall-budget hours; sampled process CPU
time totals 534.086 s. No UCloud resources were rented. Setup/idle costs were not
instrumented; peak is sampled at 0.2-second intervals, not a guaranteed absolute
maximum. All attempts, logs, model assets and pip cache remain retained (about
1.501 GB regular-file logical bytes excluding symlinks: environment ~835 MB,
model 468.580 MB, pip cache ~196 MB, plus receipts/features). Storage is regenerable
via pinned public model URLs and requirements; ignored local storage is not a backup.

## Cost interpretation and exact next bounded step

The explicit 10,000-contig / 29.536-Mb equal-count length scenario projects to
**7.394 wall hours / 29.576 four-thread hours**. The accepted E001 length distribution
(22,594 contigs / 817.438 Mb) projects to **229.016 / 916.062 hours**, solely a timing
scenario. Neither input population is a product constraint or a new scientific
run. Eight windows per length, sequence-dependent tokenization, thermal effects,
unmodelled long tails and excluded stages make these rough projections, not Linux
measurements or precise billing. There is no assumed speedup on 8/16 CPUs.

**Accept technical CPU feasibility; retain encoder choice as provisional.** Native
contracts and low RAM permit one small diagnostic comparison. These costs do not
justify making bulk DNABERT-S extraction the default first-product input. The
lightweight contrastive route remains the leading default; frozen GLM features
must show enough useful signal to justify their cost. A loading-only smoke, a
sequence embedding or falling loss is not a bin-quality result.

Next prepare and execute **one** comparison, at most 320 fragments on new
short-inclusive human-associated development sources (a controlled genome-fragment
panel is sufficient). At 64 windows at each tested length this is 945,152 bp and
projects to ~852 s / 14.2 minutes of extraction. This is a prospective ceiling,
not a frozen population: source/accession/hash manifest, taxonomic closeness and
pretraining-overlap limits, nonoverlapping fragment sampling, eligibility,
controls/metrics, fixed clustering and stop rules must be committed before scores.
Use ≤4 threads / 8 GB, a one-hour feature ceiling and two-hour total local run
ceiling; report actual cost. Stop on failure/ceiling rather than enlarge the panel.

Compare frozen GLM with inexpensive composition features under the same eligible
IDs using label-blind neighbors and one fixed clusterer, without oracle species
count, truth selection or a tuning grid. Assess all length strata and unassigned
outcomes. This tests fragment grouping, not full-MAG recovery or held-out species
generalization. A pretrained encoder versus raw TNF also does not establish
superiority over a trained contrastive TNF encoder. Record the keep/defer criterion
prospectively; it must consider gain and cost together, including which tractable
assembly size is intended. Then settle one encoder and implement the first small
train→save→reload→embed→cluster→export product. No third architecture campaign,
full-GLM training, E001 rerun or automatic UCloud execution is prepared.

## Verification scope

Seven final tests pass: portable DNA/chunk/cache/guard tests plus the actual pinned
tokenizer on real DNA, forcing recursive over-budget splits at 64 tokens on both
strands. Guard tests verify fatal exit/orphan cleanup and time/RAM ceilings.
Initial process tests were blocked by the macOS sandbox's process inventory;
they passed with the required process-metric access. This was not a native runtime
failure. Native model batching/pooling/strand/chunk/cache/reload tests ran in
`run-002`, with **no mocked model/worker**. Independent retained-only inspection
confirmed all DNA coordinates/hashes, 40 independent parents, feature axes/content,
chunk coverage/tails and every model-file hash without rerunning inference.
The full E001 suite was not rerun: its code, inputs and accepted results are
unchanged. Documentation/context checks and `git diff --check` pass. Linux and
full-scale training/clustering remain untested; no biological gate was assessed.
