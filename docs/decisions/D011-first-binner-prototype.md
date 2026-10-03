# D011: Composition-based contrastive first binner; frozen GLM deferred

Date: 2026-09-30; feasibility and final screen update 2026-10-03. Status: **accepted**
first-prototype direction: 136-dimensional composition input to our own compact
contrastive encoder. Frozen DNABERT-S is deferred under E003's precommitted joint
criterion, with positive grouping evidence retained. This replaces the compact-VAE-first
implementation recommendation in commit `e7d9636`. No binner has been implemented.
The previous rationale is preserved in Git and the dated design review.

## Why the decision changed

The owner requested an objective reconsideration before implementation, including
thesis performance and short-contig utility. The
[reassessment](../evidence/2026-09-30-architecture-reassessment.md) owns the comparison,
source evidence, assumptions and limits; the
[completed field review](../evidence/2026-09-30-binner-design-review.md) is reused.
No review restart or additional E001 run is needed.

The original recommendation over-weighted implementation simplicity and known VAMB
cost. It did not establish likely utility for a tiny VAE with a different clusterer.
Thesis and independent benchmark evidence make a lightweight contrastive binner a
stronger default. E001 nevertheless shows similar VAMB/COMEBin local neighborhoods
with very different final bins, so a VAE objective is not isolated as the cause of
VAMB's recovery deficit. Marker/clustering, inputs and selection matter too.

Prefer **a coherent small contrastive binner**. The reassessment left its sequence
representation open; E003 now chooses composition for the first implementation.
A compact VAE is a useful low-cost
control/fallback, not a required first model or learning curriculum. Transformer,
contrastive objective and reference pretraining are distinct design choices; none
wins merely through novelty or release date.

A frozen GLM is a serious contender because it can import sequence information
and biological priors beyond TNF without training a foundation model ourselves.
Its CPU inference cost is measured locally in E002/E003; E003's short-contig
grouping benefit and neighbor-purity loss are both retained below. Do not
claim a highest ceiling, reject all Transformers on the cost of CompleteBin's
whole workflow, or infer CPU inference cost from GPU pretraining cost.

## Completed initial milestone: one bounded GLM feasibility spike

The [E002 native check](../../experiments/E002-dnabert-s-feasibility/README.md)
passed on 2026-10-03. Accept it without repeating inference. One checkpoint and
one environment were used; an input-only IUPAC-validator failure was retained and
corrected before any model load. Native source/weights were unmodified. The
successful forty-window run took 182.852 seconds, peaked at 1.314 GB sampled RSS
and used 3.41–3.88 CPUs in warm extraction under coherent four-thread limits.
Pool/batch/ID/strand/chunk/cache/checkpoint contracts passed. This establishes
technical feasibility at local scale, **not** bin quality or bulk affordability.
The following original contract is preserved as the acceptance basis.

Implement and locally test **frozen DNABERT-S feature extraction**, using its
public author checkpoint, before committing to the first sequence encoder:

1. Resolve and pin checkpoint, tokenizer/custom-code revision, environment and
   license. Retain hashes and import origins; keep downloaded assets ignored.
   Use a separate local environment and preserve reference/executed caches.
2. Test actual CPU model inference on deterministic real DNA windows spanning
   500, 768, 1,000, 2,500 and 10,000 bp, with enough independent windows for timing
   after warm-up. Existing canonical sequences may supply timing windows only;
   no E001 biological result or eligibility rule changes. Synthetic fixtures are
   contract checks, not biological or throughput evidence.
3. Verify IDs, masking-aware pooling, batching, cache/reload equivalence, explicit
   token limits, long-sequence chunking and strand treatment. No silent truncation,
   padding contamination or accidental model training. Compare direct author-model
   output where contracts are shared; modified paths must be named.
4. Measure warm/cold time, tokenizer compression, process CPU and peak RAM. Run one
   numerical stage at a time: at most four CPU threads, loader workers=0, effective
   library limits reconciled. State the actual local hardware. Project cost for
   explicitly stated assembly size and length distributions at that same allocation;
   no assumed proportional speedup or automatic extrapolation to millions of contigs.
5. Stop at one checkpoint/environment attempt, 8 GB working RAM or one hour of timed
   inference after setup. Limits are prospective ceilings, not measured costs.
   Preserve startup/dependency failures and diagnose them; do not open an indefinite
   compatibility-fork or timeout-increase campaign. No quantization/distillation or
   additional model search in this milestone.

This was the local feasibility task, with no prepared UCloud command. Owner operates
any later UCloud test. A checkpoint merely loading is insufficient acceptance.
Record a concrete feasibility decision; no genome-recovery claim follows.

The original contract allowed a resource-infeasible route to be deferred and a
viable route to receive **one small representation comparison** with source,
scope/evaluation/cost frozen first. That comparison is now completed in E003
below; it does not authorize another gate. Relevant evidence includes useful
neighborhoods and groups at tolerable end-to-end cost, not an attractive projection
or decreasing loss alone. No full GLM pretraining/fine-tuning is planned.

## Completed final representation screen

2026-10-03 owner clarification: this is the **final** representation screen and
does not compare with a contrastive-trained composition encoder or prove complete
genome recovery. E002 laptop projections are planning estimates, not a sole GLM
rejection criterion. [E003](../../experiments/E003-representation-screen/README.md)
froze the new source/panel manifests, label-blind geometry/clustering and
joint utility criteria before scoring. It has resolved GLM inclusion; move
directly to implementation without a further architecture gate unless a concrete
failure requires one. This clarification also updates the durable agent guidance.

E003 completed once on sixteen new human-associated reference chromosomes:
320 nonoverlapping fragments / 945,152 bp, balanced at 500/768/1,000/2,500/10,000 bp.
Sources/hash/overlap/sampling/metric/cluster/decision records were committed in
`356df725a16375a81b686d867ce5d67c6c57bc1a` before scores. All native outputs were
independently inspected without rerunning inference. Whole workflow: 940.014 s,
1.436-GB sampled peak, four-thread limits; all operational ceilings passed.

**Keep the agreed decision rule and defer GLM for this prototype.** GLM short
five-neighbor purity was 0.45938 versus TNF 0.57396 (−0.11458), failing the required
+0.10 gain. Its longer delta +0.00469 and bp-weighted grouping F1 gain +0.06863
passed the other criteria. Crucially, GLM grouped shorts much better: short F1
0.32558 versus 0.01978; short assigned fraction 0.91146 versus 0.06771. Its advantage
is real within this fixed fragment screen and must not be hidden. TNF's better
local purity did not imply better fixed-clusterer grouping. This conservative
choice follows a joint criterion, not a claim that composition has greater bin
utility overall or that our untested training will solve its grouping deficit.

The [E003 result](../../experiments/E003-representation-screen/README.md#accepted-run-and-independent-review-2026-10-03)
owns metrics, source/runtime hashes, resource/storage accounting and review limits.
This is not a trained contrastive-composition comparison or complete-MAG recovery;
pretraining overlap is not excluded. Do not tune to these scores or add another
architecture gate. Laptop bulk-runtime projections are rough planning estimates
and were **not** the reason for GLM deferral. Preserve frozen features/pins and
their positive findings; reopen an architecture only for a concrete failure or
new product need, not automatically for another benchmark.

## Exact next milestone: first learned binner

Implement and locally execute a small installable Python package with our own
PyTorch composition-based contrastive encoder and CLI. Raw input is the selected
136-dimensional strand-collapsed TNF, plus explicit mean depth when available.
Freeze the package's configuration/transform/input contracts in Git before the
measured integration run. Use the following bounded engineering settings:
one 128-unit hidden layer, 64-dimensional normalized output, two independently
feature-masked views of the same contig (mask probability 0.1), NT-Xent loss,
temperature 0.2, AdamW at 0.001, batch size 64, 20 epochs and seed 11. These are
bounded initial implementation defaults, not evidence-selected optimal values.
Different-ID in-batch negatives can be co-genomic; name that false-negative
assumption and preserve a raw-feature control to expose damage. Labels must not
enter training, transforms or clustering. Do not automatically add more losses.

Validate FASTA plus explicit one/multiple-sample mean-depth TSV on the same
contig axis, and define a sequence-only mode when depth is absent rather than
fabricating observations. Sequence information and measured abundance are
complementary inputs with an explicit rationale; the screen tests only sequence
information. Keep original zero-depth masks and fitted transform statistics in
checkpoints/cache manifests. Coverage fixtures may test the software contract,
but are synthetic and cannot establish biological coverage benefit.
Start with a configurable 500-bp eligibility default, retaining shorter/excluded
IDs with explicit reasons. This is an engineering default, not a product minimum
or an accuracy claim; the fourmer path requires at least one unambiguous fourmer.

Deliver train→save→reload→embed→cluster→assignment TSV/bin FASTA export in a
minimal Snakemake integration run. Reuse the accepted E003 **TNF** feature cache for its
development demonstration instead of repeating the screen; test the package's
fresh feature path on a tiny real input separately. Use the same fixed initial
cluster procedure, retaining noise and all IDs. Measure the learned output beside
the unlearned-feature control without truth tuning or superiority requirements.
If training destroys useful signal or export/input contracts fail, diagnose that
specific failure during implementation, without a new architecture campaign.
Run failure checks for duplicate/missing/nonfinite IDs/depth, reordered caches,
zero evidence, checkpoint reload and complete assignment/FASTA accounting.
Keep numerical work serial within four threads, loader workers zero and 8 GB RAM;
bound the first local integration to two hours. Separate prototype environments
from read-only E001/E002 runtimes. Linux validation/owner deployment comes after
the local implementation, not from extrapolating this laptop's speed.

Keep the first product coherent: our own learned embedding/head, one fixed
clustering procedure and complete assignment/bin exports. Reuse numerical libraries;
a baseline executable behind a new CLI is not
our learned implementation. A fixed clusterer is an initial engineering control,
not an assumption that representation quality guarantees bins. Keep masks/embeddings
and assignments so downstream failures can be distinguished from encoder failures.

The intended inputs remain an assembly FASTA and explicit mean-depth matrix for
one or more samples mapped to that same assembly. Ordered contig/sample IDs,
missing/duplicate/nonfinite-data checks, zero-evidence masks, transformation state,
cache provenance and checkpoint inference are required. Coverage's complementary
value must be measured, especially in single-sample mode. No GLM path enters this
first implementation. If a later concrete need justifies it, test replacing the
composition representation first; do not automatically stack
TNF, GLM, VAE, contrastive, markers and graph components. Additional fusion needs
an explicit information rationale and a control.

The product must handle configurable short-contig eligibility; **2,500 bp is not
a product minimum**. No lower-length accuracy claim follows from E001 or the thesis.
The separate evaluation must include short fragments and retain missing/unsupported
ranges in the accounting. [The reassessment](../evidence/2026-09-30-architecture-reassessment.md)
specifies length strata and public/simulation alternatives; final inputs/defaults
are chosen prospectively, not to fit E001. Preserve optional unassigned outcomes
rather than force contaminated bins. No rule requires waiting for a paper-scale
benchmark or novelty claim before a working tool.

Avoid general plugin infrastructure. A successful milestone means the actual
learned train→save→reload→embed→cluster→export path works on retained development
inputs, with reproducible inference, complete accounting, a raw-feature control
and measured costs. It need not outperform that control to count as a working
software implementation; report any degradation honestly and diagnose concrete
failure. No proposed CLI is called runnable until implemented and tested.

## Alternatives and revisit conditions

These remain serious alternatives, not a queue of new architecture gates. Revisit
only for a concrete implementation failure or a new owner-defined product need.

- **Compact VAE:** restore as preferred only if a matched inexpensive test gives
  worthwhile utility or the contrastive contract is unjustified. Native VAMB's
  cheap runtime alone does not establish our prototype's bin quality.
- **Context-TNF Transformer:** credible short-context option, supported indirectly
  by CompleteBin; its stripped encoder's benefit is unmeasured. It may be efficient
  with a short fixed token sequence. Do not assume every large tool component is needed.
- **Frozen GLM:** E003 gives positive grouping evidence but fails the joint
  short-neighbor criterion. Deferred for this first prototype, not globally
  rejected. Reconsider only for a concrete implementation failure/new product
  need; no automatic second screen or laptop-projection veto.
- **Full GLM training, taxonomy, graphs or neural merging:** reconsider with a
  concrete failure/input/resource case, not simply because another method uses them.

E001 remains closed at amended seed-11 scope; H001 and its original three-seed
criterion remain unresolved, seeds 23/47 deferred. New short-inclusive data are
allowed without reopening E001. Publication remains a separate owner action with
license/history review.
