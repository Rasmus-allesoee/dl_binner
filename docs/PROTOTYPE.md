# Binner prototypes and current contracts

## Compact window-context candidate, dev7

[E019](../experiments/E019-window-context/README.md) adds a separate experimental
`context-stage` interface. It consumes existing complete multiview features and
real DNA crop banks; no truth, marker labels, downloads or regenerated crop draw
enter learning. The compact attention branch uses at most eight local TNF windows
and one global token with canonical strand, positional/reliability inputs and
masked pooling. A zero-initialized residual preserves E016 global composition
and predictor initialization; explicit depth fusion, E016 positive-only
predictor/stopped EMA target and reconstruction remain. This is local engineering,
not a new community-validated/default product. Dev3/dev4/dev5/E016 freezes remain.

```
python -I -B -m dl_binner context-stage --stage tokens --threads 4 \
  --fasta assembly.fa --features retained/features.npz --views retained/views.npz \
  --output new-context
python -I -B -m dl_binner context-stage --stage train --threads 4 \
  --features retained/features.npz --views retained/views.npz --tokens new-context \
  --output new-context-train
python -I -B -m dl_binner context-stage --stage embed --threads 4 \
  --features retained/features.npz --views retained/views.npz --tokens new-context \
  --checkpoint new-context-train/checkpoint.pt --output new-context-units.npz
```

`--config` is the complete strict context-plus-E016 schema. Default schedule is
20 epochs/seed 11/batch 256; the bank's old policy must match. Existing/corrupt
outputs are refused, without fallback. The indexed uint16 bank records original
eligible-row mapping and canonical-window coordinates/strand. It samples bounded
windows, not all DNA positions; global TNF still includes all DNA. Padding and
ambiguous windows are masked, absent depth cannot leak, and no local coverage or
variance is invented. Checkpoints retain online/target/predictor/optimizer and
collapse/exposure histories. Exact native reload is distinct from the original
failed cross-platform tolerance. Research CPM/E013 and pre/old/post exports run
as separate processes; product `run`, `candidate` and `multiview-stage` keep their
existing algorithms. Runtime/compute limits belong to the experiment, not ordinary
product policy. A pretrained GLM could later complement this composition context.

## Multiview reconstruction candidate, dev5

The experimental [E014 design](../experiments/E014-multiview-reconstruction/design.md)
adds a four-crop variable-length DNA bank, full-parent exposure, all-available
positive contrastive loss, small reconstruction heads and measured-depth branch
dropout. It retains the dev4 encoder widths and unit geometry. `multiview-stage`
provides explicit `features`, `markers`, `train`, `embed`, `group`, `refine` and
`export` commands for the bounded research DAG. These are separate processes;
there is no new automatic download/retry or claim to resume an old dev4 journal.
`candidate` below intentionally retains its original dev4 algorithms, including
RB/old refinement. Reproducing frozen evidence still requires its original runtime.

```sh
python -I -B -m dl_binner multiview-stage --stage features --threads 4 \
  --fasta assembly.fa --depth depth.tsv --output new-features
python -I -B -m dl_binner multiview-stage --stage train --threads 4 \
  --features new-features/features.npz --views new-features/views.npz --output new-train
python -I -B -m dl_binner multiview-stage --stage embed --threads 4 \
  --features new-features/features.npz --checkpoint new-train/checkpoint.pt --output new-units.npz
```

`--config` supplies the strict packaged `resources/multiview.json` schema. Omit
depth for explicit zero-column sequence-only mode. Optional `--parent-features`
in feature preparation verifies and reuses sealed full-parent input arrays, not
old crop banks. Every parent stays assigned/unassigned/excluded, including DNA
too short for crop positives. Crops carry coordinates/hash/distinctness masks and
the parent's measured mean, never measured crop depth/variance. All available
positives are used; the bank is fixed, not fresh per epoch. Other contigs may still
be co-genomic negatives. Inference restores original observed depth.

Group builds the preserved weighted sparse graph and directly applies the sole
CPM density rule. Refine requires `--features`, `--embeddings`, `--parent`,
`--marker-cache`, `--fasta` and `--marker-hmm`; it verifies the native cache and
uses the unchanged E013 quality/context selector, retaining all alternatives,
old/selected partitions and full DNA exports. It is not the old destructive
duplicate-marker policy. Marker weights remain panel-dependent proxies, not MAG
quality. Truth is absent from all stage APIs and belongs in a separate evaluator.

Mac installed-wheel tiny native training/reload/markers/CPM/refinement/export
contracts pass. New community results and dev5 Linux support remain gated by
E014 admission; native dev4 acceptance cannot establish them. The preserved Mac
cross-platform allclose failure is unchanged. This is a research candidate with
explicit stage commands, not a newly validated high-performing product release.

## Integrated dev4 candidate

`dl-binner candidate` implements [D015](decisions/D015-coherent-prototype-upgrade.md)
and [E010](../experiments/E010-coherent-prototype/README.md). Native Linux and the
development comparison completed; later CPM/refinement controls are in E011–E013.
Those results do not establish generally strong performance. Preserve immutable dev3 at
`5e54538d1799e8d2538621729400f33fbaf017b9` and its accepted E009 outputs.

```sh
/absolute/candidate/bin/dl-binner candidate --fasta assembly.fna \
  --depth mean-depth.tsv --marker-hmm markers.hmm \
  --marker-manifest marker-asset.json --output candidate-result --threads 8
```

Omit `--depth` for explicit sequence-only mode; one/multiple sample columns are
supported without inventing variance or missing values. The full ordered depth
schema below applies. Marker assets must be supplied locally with their exact
hash, canonical-family map, source/version and license. No payload downloads at
runtime. `--marker-cache cache-directory` instead verifies complete cached genes,
domain hits and evidence without a new scan or needing the original HMM. Drift,
corruption and malformed cached evidence fail; no automatic rescan.

The seven serial stages are features, markers, train, embed, group, refine and
export. Separate embedding/graph processes avoid conflicting numerical libraries.
Actual disjoint DNA windows train the model; 500–1,999-bp contigs enter inference,
and every short/no-evidence contig is still exported with its reason. Windows
carry their parent's **measured mean depth**, not measured window coverage.
The auxiliary composition loss reduces an exclusively depth-based shortcut; it
does not resolve false negatives or chimeric-positive assumptions.

Saved unit vectors pass unchanged into one sparse kNN/Leiden graph. A fixed
sampled exact neighbor audit must pass; it is not a search over graph settings.
Marker refinement requires two repeated clean SCG families, checks compatible
assignments, and can leave ambiguous DNA unassigned. Multicopy/ambiguous hits do
not silently become trusted constraints. Marker-negative contigs retain a real
assignment path. Some conflicts may remain explicitly unresolved.

Outputs retain `features/features.npz`, real `views.npz` and coordinates/hashes;
all genes/domains and marker cache; `train/checkpoint.pt` and pre-save inference;
`embed/embeddings.npz` with exact reload parity; `group/graph.npz` and pre-partition;
`refine/partition.json`; and **both** `export/pre/` and `export/post/` with complete
assignments and assigned/unassigned/excluded DNA. `export/accounting.json` has no
biological quality claims. Independent sequence truth belongs only in later
evaluation. Retain pre/post partitions for a cheap paired refinement comparison.

Use optional `--memory-gb`/`--timeout` safeguards, explicit `--resume` with matching
bytes/runtime/config, and `--stop-after STAGE` for inspectable boundaries. Parent
hash/setup/collection and native child work share the invocation clock. Failed
staging directories/logs remain; no retry, repair or limit extension is automatic.
Product defaults are in `resources/candidate.json`; the experiment owns its
approved ceilings, input locks and interpretation. See the
[current installation guide](INSTALLATION.md) and
[separate execution request](../experiments/E010-coherent-prototype/OPERATIONS.md).

## Preserved dev3 algorithm route

The `run`, `prepare`, `train`, `embed`, `cluster` and `export` commands below retain
the original scientific implementation/defaults. Dev4's metadata/CLI/journals are
new; replaying accepted dev3 evidence still requires its original wheel/source,
not a claim that the whole new package is identical.

This experimental package implements our own composition-based contrastive
encoder, checkpoint inference, fixed clustering and complete FASTA/assignment
export. It is development software, not validated whole-MAG recovery or a
published release. [D011](decisions/D011-first-binner-prototype.md) owns the design;
[E004](../experiments/E004-first-binner/README.md) owns integration evidence;
[E005](../experiments/E005-linux-pilot/README.md#accepted-v5-native-gi-pilot-and-independent-review-2026-10-06)
accepts native Linux and a capped GI assembly/explicit-depth development pilot.

Follow the [standalone CPU installation guide](INSTALLATION.md) for a locally
built **0.1.0.dev3** wheel and a fresh versioned CPU environment.
The executable is `dl-binner`; `python -m dl_binner` provides the same CLI.
The built-in dispatcher runs numerical stages serially at the selected positive
CPU thread count; there is no product maximum. Linux selects CPU PyTorch
explicitly; E008 accepts actual independent-install CPU/Linux CI on its recorded head.
The declared Python 3.10–3.12 range is not an exhaustively tested matrix.
[E005](../experiments/E005-linux-pilot/OPERATIONS.md)
has accepted the checksum-bound native CPU/Linux smoke and bounded
GI pilot. Its protocol preserves shorter
contigs and requires depth from that exact reference, never fabricated missing rows.

The first actual local integration is accepted in E004: a frozen installed wheel
trained and exported bins, checkpoint reload matched exactly, and the raw control
matched E003. Grouping improved while short-neighbor purity/precision declined.
This is working experimental software, not an established improvement in MAG
recovery. The measured demo used sequence only; optional depth has native contract
tests and a development TNF+measured-depth recovery result in E005. The two arms
share depth, so coverage's separate biological benefit is not isolated.

The installed **`dl-binner run`** command now groups the complete learned path and
matched raw control. [E006](../experiments/E006-cli-usability/README.md) accepts its
built-wheel native Mac checks, recovery, resource enforcement and truthful
accounting. [E006's Linux return](../experiments/E006-cli-usability/README.md#accepted-native-linux-return-and-independent-review-2026-10-06)
now accepts that generic command, native serial placement, strict resume and
failure/resource handling on the reviewed CPU/Linux runtime. This is an evolving
prototype, not a compatibility promise or whole-MAG validation. The
individual commands `prepare`, `train`, `embed`, `cluster`, and `export` remain,
with `--help` on each. `prepare` reads assembly FASTA and optional mean-depth TSV. Its header is
`contig_id` followed by unique ordered sample names. Every FASTA ID needs one
nonnegative finite depth row; row order may vary, but extra/missing IDs fail.
Absent depth is explicit sequence-only mode. Zero depth remains an observation,
with original masks retained. Sample-column order must match the checkpoint at
inference. Full IUPAC DNA is accepted; ambiguous fourmers do not supply TNF counts.
Matching table IDs verifies the input axis, not read-mapping provenance: depth
must originate from this assembly, with reference/alignment hashes recorded in
the pilot. Coverage's biological value has not been established here.

The default length cutoff is configurable 500 bp. Every original ID remains in
the outputs, including excluded short/zero-evidence contigs and cluster noise.
Training uses only eligible data, without labels. It fits and saves transforms;
inference reuses them without refitting. Different contigs are in-batch negatives
and may be co-genomic: this false-negative assumption is explicit and unproven.

Export writes `assignments.tsv`, bin FASTAs, `unassigned.fna`, `excluded.fna` and
a byte-bound manifest. Each input contig appears in exactly one exported FASTA.
Output paths must be fresh; no command silently overwrites an accepted artifact.
Feature/cache/embedding manifests bind ordered IDs, DNA, arrays and parents.
Checkpoints contain tensor state and fitted transforms and use restricted
`weights_only=True` loading. They must still come from a trusted provenance.

Fixed clustering uses exact cosine neighbors, positive mutual five-neighbor
edges, NetworkX greedy weighted modularity at resolution one, and minimum
community size three. It never receives a genome count or truth. Exact neighbor
queries are blocked to bound matrix memory, but greedy modularity is not yet
benchmarked on a full community. E005 checks 5,309 contigs / 12.92 Mb; neither that
cap nor its timing establishes bulk scaling. Retain the raw-feature control;
declining training loss alone does not establish useful bins.

## Prepared next milestone: one end-to-end command

The E005→E006 preparation contract is completed and retained in E006's records.
Its four-thread/8-GB/two-hour bounds and packaged Snakemake DAG describe that
executed snapshot, not present product limits. E007 preserves its dev2 build and
independent-install evidence. [D012](decisions/D012-product-execution-and-usability.md)
now changes orchestration/resource interfaces only; accepted scientific settings
and results remain unchanged. Use the current commands below for dev3; old
version journals require their original environments/code.

## Run the binner

Use the installed package in one CPU environment with its built-in serial
dispatcher. The command installs nothing and needs no repository
checkout, internet connection, marker database or truth labels. Defaults are inside the wheel. Keep interpreter paths lexical: resolving a venv's `python`
symlink can bypass that environment.

```sh
dl-binner run --fasta assembly.fna --output result --threads 4
```

Add `--depth mean-depth.tsv` for explicitly supplied mean depth on this exact
assembly. Its `contig_id` header and ordered sample columns follow the contract
above. Depth zeros remain observations; absent depth stays sequence-only. No separate workflow Python is needed.
`dl-binner run --help` shows examples, limits, output paths and recovery options.

The initial defaults remain seed 11, 20 epochs, hidden 128/output 64, mask 0.1,
NT-Xent temperature 0.2, AdamW 0.001/weight decay 0.01 and batch/inference 64.
`--training-config` explicitly selects a JSON matching the existing contract.
`--min-length` defaults to 500; all excluded DNA is preserved. Any positive `--threads` count is accepted (default 4); interop remains one and
loader zero. `--memory-gb` and `--timeout` are optional positive finite safeguards
with no project maximum. Omitted safeguards are disabled, while resource sampling,
progress and cleanup remain active. Timeout covers hashing, native work and final
accounting per invocation. CI/tests set bounded budgets explicitly. Native library/
hardware availability still determines feasible execution; more threads do not
guarantee speedup for tiny or serial stages.

Outputs are predictable:

```text
result/
  run-manifest.json       input, source, config, environment and budget bindings
  run-summary.json       both arms, masks/reasons/strata and resource receipts
  run-summary.tsv        concise status counts and bp in every length stratum
  completion.json        summary/stage-receipt hashes
  learned/bins/          assignments.tsv, bin_*.fna, unassigned.fna, excluded.fna
  raw/bins/              matched raw control with the same complete exports
  features/              original TNF/depth, ordered axes and masks
  training/              checkpoint, transforms, epochs and pre-save embeddings
  receipts/              successful stage output/evidence hashes
  logs/invocation-*/     terminal.log, status.json, native logs/samples
  staging/               uniquely named retained stage attempts
```

Status/progress lines name each of eight stages; long steps print ten-second
heartbeats. The terminal log captures final exit codes (0 success/intentional
partial stop, 1 failure, 130 cancellation). Errors name the native cause and log
when available. Verbose traces stay in the invocation log. Resources are sampled
process-tree estimates, not exact peaks or provider invoices; the JSON explains
its clocks and preserves each completed stage's original resource receipt.

Fresh execution refuses a populated output directory. To continue the same run,
repeat its input/options and add `--resume`:

```sh
dl-binner run --fasta assembly.fna --output result --threads 4 --resume
```

FASTA/depth/config/source/runtime/budget and every completed artifact must match.
Finished stages are reused; completed runs schedule no scientific work. Changed,
missing or extra published artifacts fail with evidence retained. Failed work
uses a new staging folder on retry; unreceipted published final artifacts are
refused, never silently repaired. `--stop-after train` makes a deliberate partial
run; omit that flag when continuing. Wall time is per invocation. A stale
`.run-lock` names its PID/host; verify that process has stopped before removing it.

Summary assignment/bin size is **not** genome recovery, completeness,
contamination or MAG quality. AMBER/R95 remain separate evaluation with explicit
truth. E006's synthetic-depth/tiny-DNA fixtures establish software behavior, not
coverage benefit or biological generalization. Accepted E005 accounting was read
from retained outputs; no inference/clustering/evaluation was repeated.

The E006 owner smoke is accepted; do not repeat it or transfer a linked test
environment. Its immutable wheel remains the reference for the next milestone.

## Private-PR readiness milestone

Completed locally on 2026-10-07 in [E007](../experiments/E007-pr-readiness/README.md),
under its [prospectively frozen contract](../experiments/E007-pr-readiness/protocol.json).
This paragraph records E007's historical local readiness. E008 subsequently
passed real independent-install Linux CI and private PR #1 was merged under owner
authorization on 2026-10-07. The [PR record](PR_FIRST_PROTOTYPE.md) owns the exact
head/merge/review evidence; no public publication has occurred.

The locally built **0.1.0.dev2** wheel and sdist are inspected, the sdist rebuild
has identical logical wheel contents, and fresh versioned environments own their
numerical distributions. [Installation](INSTALLATION.md) provides accepted version
pins, explicit CPU-PyTorch selection and separate builder/binner/workflow recipes.
Only package version/readme/build metadata changed: encoder, transforms, objective,
training defaults, clusterer, runner and packaged defaults/DAG remain byte-identical
to accepted E006. Its dev1 wheel/source and executed environments remain retained;
new version journals do not retrofit or silently resume old manifests.

The self-contained ordinary suite is `tests/product/`, invoked through
`scripts/test_product.py` with installed interpreters. It needs no ignored research
assets, truth or external experiment helpers. Tiny deterministic software DNA/depth
checks cover all six strata, masks/zeros/reasons, train/save/exact reload, both
complete exports, accounting, fresh/partial/completed resume, changed/corrupted
bytes, native errors, resource limits, heartbeat and orphan handling. Four-thread
checks from the clean snapshot and two-thread checks physically outside the
repository pass; retained biological evidence is reviewed separately, never
silently skipped and called product-test success. Neither suite scores bin utility.

The minimal prepared Linux workflow builds/inspects/installs the CPU wheel in fresh
prefixes, uses its own two-thread budget, retains failure evidence and checks docs.
It has not run remotely. Python 3.10 Mac and E006's borrowed-dependency Python 3.12
Linux evidence are not a complete platform matrix or proof of the new standalone
Linux install. Version pins do not bind every possible platform wheel hash.

Accept reproducible software without requiring superiority. E005 remains a capped
development assembled-sequence recovery result with fragmentation, no >=90%
recovered genome and overlap; whole-MAG quality, independent generalization,
full-community scaling and isolated depth benefit remain unresolved. E001/H001
and the original three-seed criterion are unchanged. Public licensing and historical
source packaging need a later owner decision; no license is invented for this
private PR and no history is rewritten.

The next step is separately authorized private push/PR/real CI and implementation
review, then an explicit merge decision. After merging while preserving referenced
source commits, start benchmark/matched architecture work on a new branch from
updated main. Keep this prototype as a stable baseline. The planned TNF / frozen
GLM contrastive-head / hybrid comparison remains unrun and non-blocking. No further
model gate, dataset/seed expansion, release framework or owner UCloud smoke is
required for opening this PR; repair a concrete CI/review failure if one appears.

## Current product execution update

[E008](../experiments/E008-product-execution/README.md) implements the owner-requested
resource/orchestration change and owns its native/CI validation. Dev1/dev2 wheels,
source hashes, runs and environment bindings remain immutable evidence. Dev3 does
not retrofit their journals. Local and actual CPU/Linux checks now pass; see E008
for exact source/build heads and review status. Product installation has no Snakemake dependency;
existing research/HPC workflows retain it where useful.

People and AI agents use the same CLI/help, explicit FASTA/depth contracts, neutral
JSON/TSV summaries, stage/exit receipts and actionable retained errors. Optional
GPU and Conda/mamba distribution are future goals only. No scientific settings,
architecture or accepted scores change. Private push/PR/CI/review are authorized;
merge and public publication are not.
