# E004: first composition-based learned binner

Prepared/completed: 2026-10-04. Execution: **completed**. Software outcome:
**accepted first native implementation**. Scientific outcome: mixed development
fragment-grouping utility; whole-genome recovery and coverage benefit unassessed.
This is [D011](../../docs/decisions/D011-first-binner-prototype.md)'s first software
milestone, not another encoder selection gate. The owner also requests a future
three-way learned TNF/GLM/hybrid comparison; it is recorded in D011 and is neither
implemented nor run here. Reuse accepted [E003](../E003-representation-screen/README.md)
TNF and development DNA; no E002/E003 inference is repeated. No UCloud execution.

## Frozen implementation and inputs

The installable [package](../../pyproject.toml) supplies `dl-binner` and
`python -m dl_binner`: prepare, train, embed, cluster and export. Our own PyTorch
MLP maps 136-dimensional strand-collapsed composition through hidden 128 to a
normalized 64-dimensional embedding. Two independently masked views (0.1, inverted
mask scaling) use symmetric NT-Xent, temperature 0.2. AdamW lr 0.001, weight decay
0.01, betas (0.9, 0.999), eps 1e−8; batch 64, 20 epochs, seed 11 and inference
batch 64. [Training JSON](training.json) fixes the variable settings before the
measured integration. Singleton tail batches merge instead of dropping an ID.
Different-ID negatives can be co-genomic; this is an explicit untested assumption.

[Configuration](config.json) binds the exact accepted E003 assembly/cache/receipt/
panel/raw-partition hashes and training configuration. Native array cache import
checks full ordered IDs, DNA file/per-contig hashes, width, finite frequency sums
and valid-fourmer counts; it does not extract TNF again. The package's fresh
feature reader is tested separately on two real retained fragments. All 320
development fragments / 945,152 bp and five length points remain in accounting.
This is target-data unsupervised/transductive learning on development fragments,
not an independent generalization test or MAG benchmark. Truth enters only the
final evaluator after training, embeddings, partitions and exports exist.

The [input/transform contract](../../docs/PROTOTYPE.md) requires uppercase-preserved
IUPAC FASTA and optional explicit mean-depth TSV (`contig_id`, unique ordered
sample columns; all and only FASTA IDs; finite nonnegative values). TSV rows align
to FASTA order; sample columns must match saved checkpoint order. Missing depth
is explicit sequence-only mode. Original zero-depth masks and all-zero-row masks
are retained. This real integration has **no coverage**, so fixtures establish
depth software correctness only, not biological abundance benefit.

Fit population mean/std only on eligible input rows, then z-score both blocks and
row-L2 TNF. Scale log1p-depth by sqrt(sample count), preserving its magnitude
including single-sample differences. Constant columns (sd≤1e−8) are zero. Whole-row zero depth
stays zero after centering; partially zero samples remain measured observations.
Block scaling is a prospective composition/abundance balance, not a tuned
fusion result. Save all statistics in checkpoint/receipt; inference never refits.
Default eligibility is configurable 500 bp plus at least one unambiguous fourmer.
Keep below-cutoff/no-fourmer exclusions and zero-transformed/cluster noise outcomes.

Checkpoint restricted loading (`weights_only=True`) verifies byte identity,
schema/sample order and finite weights. Retain pre-save inference to test the
actual reload path, including all invalid/zero rows. Raw control is untrained TNF
(plus log1p depth if supplied); in this sequence-only run it must exactly reproduce
E003's accepted neighbor ordering and partition through the new package adapter.

Both spaces use the same fixed label-blind E003 clusterer: population z-score,
row L2, exact cosine 5-NN with ID ties, positive mutual edges, NetworkX greedy
weighted modularity resolution 1, minimum group size 3 and no oracle K. Queries
use row blocks of 128 to avoid a full pair matrix; assembly-scale modularity cost
remains unmeasured. No tuning grid or truth selection. Export all IDs once across
bin FASTAs, unassigned FASTA and excluded FASTA, with assignment status/reason TSV
and hashes. [Workflow](../../workflows/first-binner/Snakefile) invokes installed
native CLI stages serially, then verifies accounting and scores retained partitions
using E003's full-denominator B-cubed/neighbor evaluator and every length stratum.
Keep raw and learned masks, arrays and partitions to separate downstream failure.

## Acceptance, resources and retention

Software acceptance requires a real train→save→reload→embed→cluster→export path,
finite outputs, reload agreement ≤1e−7, complete DNA/ID accounting, validated
failure paths, and success within **four threads / loader zero / 8 GB / two hours**.
It does not require biological superiority. Report utility differences and loss
separately; if learning destroys signal, diagnose the concrete issue without
truth-based tuning or another architecture gate. No architecture family is ranked.

Preflight: twelve focused native tests pass, including independent loss/count
formula checks, two real fresh-reader rows, cache/DNA/ID failures, single/multi-
sample masks and preserved scalar depth magnitude, actual PyTorch training/reload,
new-input schema/fitted-stat reuse, fixed blocked-geometry parity, exclusions and
complete native export. The final built wheel imports outside the checkout with
all package/library origins in the new prefix and matching source hashes.
The complete ten-step (nine computational rule) synthetic fixture DAG passes,
its completed-directory dry-run schedules nothing, and repeated invocation
refuses overwriting. A deliberately malformed FASTA fails the actual DAG in
2.197 s without producing a checkpoint or scores. Time-ceiling child cleanup is
tested. No production worker, extractor, trainer or writer is mocked. These are
software fixtures, not biological/performance evidence. Earlier fixture and
setup logs remain retained. Linux is not tested.

The [driver](../../scripts/e004_integration.py) captures terminal/rule/progress logs,
per-rule extended benchmarks and independently sampled descendant CPU/RSS, with
fatal failure/time/RAM stopping the launched process tree. Charge-style four-thread
wall budget is local planning accounting, not UCloud billing. Setup, contract tests
and retained review are outside the scientific integration clock. Memory samples
are not exact high-water marks; CPU can miss very short-lived processes. Native
training reports its own process CPU/time and effective library pools.

Use the separate `artifacts/e004-first-binner/env-v1` local environment, Python
3.10.15 with [pinned requirements](requirements-local.txt). It shares only the
read-only base interpreter with an existing local Python; site packages are
isolated and import origins verified. E001/E002 environments and E003 caches stay
unchanged. Initial offline Conda setup lacked cached transitive packages; its
failure log remains in `setup/`. The successful new virtual environment uses
downloaded pinned wheels; package wheel/runtime inventories are retained. No
executed environment relocation or source-tool modification.

Source/config/contracts were committed as
`7b24a6b9677d8d7625d392aa0fc0a189952767cb` before this single measured command
(provenance only; **do not repeat the accepted run**):

```sh
env -u PYTHONPATH -u PYTHONHOME -u PYTHONUSERBASE PYTHONNOUSERSITE=1 \
  artifacts/e004-first-binner/env-v1/bin/python scripts/e004_integration.py \
  --mode run --config experiments/E004-first-binner/config.json \
  --output artifacts/e004-first-binner/run-001
```

Retain checkpoints, features, both embeddings/partitions/exports, evaluation and
all failed/preflight logs under ignored `artifacts/e004-first-binner/`. Local files
are not a remote backup. Small observed metrics, hashes and conclusions are
committed after retained-output review. A completed-workdir dry-run must schedule
nothing; do not invoke the fresh driver on an accepted attempt. Linux/assembly-scale
validation and eventual publication are separate milestones; neither is claimed.

## Accepted result and limitations

`run-001` passed all nine native computational rules. The frozen installed wheel,
not an editable source link or mocked baseline, performed actual training and
checkpoint inference. All 320 eligible IDs appeared in every one of twenty
epochs. Pre-save versus separately reloaded embeddings agree **exactly** (maximum
absolute difference 0). Both exports preserve all 320 contig IDs and normalized
DNA exactly once; the learned output has 17 bins, 305 assigned and 15 unassigned,
with no length/evidence exclusions in this particular panel. Separate fixtures
verify exclusion behavior. Native raw-control assignments/neighbors/graph/masks
match accepted E003 exactly. The completed-workdir dry-run schedules nothing.

[Observed receipt](observed.json) binds actual source/configuration, costs and
93 retained-file hashes; [all-stratum metrics](observed.metrics.tsv) include every
length point and noise. [Independent diagnostics](diagnose_retained.py) and
[diagnostic result](diagnostics.json) recompute neighbor ordering and every
per-fragment B-cubed contribution from retained arrays without training or fitting
new communities. The receipt helper initially mixed relative and absolute paths;
its post-run path normalization was fixed and specifically tested. Native run/
evaluator functions and package source remain unchanged; this did not repeat
science. Thirteen focused tests now pass (twelve native contracts plus the
receipt-path regression), alongside the full fixture DAG/fatal/repeated/resume
checks. No production path was mocked; Linux remains untested.

| Development outcome | Raw control | Learned composition |
| --- | ---: | ---: |
| Overall bp-weighted grouping F1 | 0.30801 | 0.42455 |
| Overall bp-weighted grouping precision | 0.53209 | 0.44150 |
| Overall bp-weighted grouping recall | 0.21674 | 0.40885 |
| Short grouping F1 | 0.01978 | 0.26065 |
| Short five-neighbor purity | 0.57396 | 0.42604 |
| Longer five-neighbor purity | 0.64844 | 0.63281 |
| Unassigned fragments | 209 | 15 |

**Interpretation:** learning improves grouping/coverage of the sampled fragments,
but reduces precision and short-neighbor purity. Higher assignment is not proof
of better bins; bp-weighted F1 improves partly through greater recall while groups
remain mixed. The 10-kb neighbor point improves (0.70000→0.74688), while the other
four points decline; all are retained. Do not hide these losses or apply E003's
different inclusion criterion retroactively as a software gate. There was no
constant-output collapse: all 320 vectors are distinct, all 64 dimensions vary,
norms are approximately one, and outputs are finite. Loss decreases 4.04156→1.14037;
that alone does not establish genomic signal.

Retrospectively reconstructing the deterministic batches finds **6.0124%** of
negative-ID comparisons are co-genomic, averaging **3.7878** co-genomic negative
IDs per anchor/batch. The implemented objective discriminates contig identities
and can push same-genome fragments apart. This measured exposure is a plausible
explanation for neighborhood loss, **not a causal attribution or proof of the
only cause**. No truth-based correction, extra objective, architecture gate,
retraining or hyperparameter tuning follows. Preserve the raw control and the
owner's future matched TNF/GLM/hybrid plan. The software milestone passes; bin
quality still requires a bounded assembly/coverage pilot and honest evaluation.

## Actual resources and retained storage

The scientific driver took **17.79698 s**, peak sampled subtree RSS
**410,550,272 bytes (0.411 GB)** and sampled average **1.227 CPUs** under the
four-thread cap. Native learning itself: **0.59505 s**, process CPU **1.42882 s**,
average **2.401 CPUs**, Torch intraop four/interop one, loader zero, reconciled
four-thread library pools. The model has **25,792 parameters**. Imports/serial I/O/
orchestration dominate this tiny run; a four-thread cap is not evidence of full
four-core use or assembly-scale throughput. Four-thread wall budget: **0.0197744
hours**, local accounting only. Setup/downloads/tests/review are excluded. Same
Intel i5-1038NG7 / 16-GiB host as E002/E003; no GPU or UCloud work.

Per-rule benchmarks/logs remain retained, but local extended benchmark RAM and
`cpu_time` fields again report zero/unavailable. Use the independent supervisor
and native training clock instead; do not rerun accepted science for those fields.
The accepted run snapshot has **93 files / 2,944,028 bytes (2.94 MB)**, excluding
the separately retained environment, wheel/download/setup caches and old fixtures.
No accepted E002/E003 assets were changed or deleted. An ignored local directory
is not a backup. Future Linux validation must use a CPU wheel recipe and retain
effective resources, payload/setup and total allocated-cost measurements; do not
infer linear speedup from this small local run. Fresh TNF extraction and greedy
modularity include serial work and are not yet validated at assembly scale.

Local `du -sk` at closure reports 808,332 KiB for the isolated environment
(827.73 MB of allocated filesystem blocks) and 179,236 KiB for setup/wheel/download/
fixture evidence (183.54 MB). These are separate from the run's logical file-byte
inventory and do not include the shared read-only base interpreter. Preserve
them; no cleanup is authorized or needed for this milestone.
