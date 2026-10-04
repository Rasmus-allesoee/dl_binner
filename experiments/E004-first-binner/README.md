# E004: first composition-based learned binner

Prepared: 2026-10-04. Execution: planned; biological outcome: not assessed.
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

Commit code/config/contracts before this measured command (one fresh attempt):

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
