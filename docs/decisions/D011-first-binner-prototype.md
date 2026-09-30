# D011: Contrastive-first prototype direction; sequence encoder provisional

Date: 2026-09-30. Status: accepted revised planning direction; final encoder choice
is provisional pending the bounded check below. This replaces the compact-VAE-first
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

Prefer **a coherent small contrastive binner**, with the sequence representation
still open between inexpensive composition/context features and a frozen
species-aware genome-language-model encoder. A compact VAE is a useful low-cost
control/fallback, not a required first model or learning curriculum. Transformer,
contrastive objective and reference pretraining are distinct design choices; none
wins merely through novelty or release date.

A frozen GLM is a serious contender because it can import sequence information
and biological priors beyond TNF without training a foundation model ourselves.
Its CPU inference cost and short-contig benefit remain unmeasured here. Do not
claim a highest ceiling, reject all Transformers on the cost of CompleteBin's
whole workflow, or infer CPU inference cost from GPU pretraining cost.

## Exact next milestone: one bounded GLM feasibility spike

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

This is the next local task, with no prepared UCloud command today. Owner operates
any later UCloud test. A checkpoint merely loading is insufficient acceptance.
Record a concrete feasibility decision; no genome-recovery claim follows.

If the frozen route is resource-infeasible or needs a broad compatibility fork,
proceed to the inexpensive contrastive prototype and retain the reason for deferral.
If viable, permit **one small representation comparison** on new short-inclusive
development data before choosing frozen GLM features over TNF/context. Freeze its
scope, population, evaluation and cost first; this is the only follow-up selection
gate, not a new large architecture/benchmark campaign. Relevant evidence is useful
neighborhoods and bins at tolerable end-to-end cost, not an attractive projection
or decreasing loss alone. No full GLM pretraining/fine-tuning is planned.

## First usable product after the encoder choice

Keep the first product coherent: our own learned embedding/head, one fixed
clustering procedure and complete assignment/bin exports. Reuse numerical libraries
and, if chosen, the frozen backbone; a baseline executable behind a new CLI is not
our learned implementation. A fixed clusterer is an initial engineering control,
not an assumption that representation quality guarantees bins. Keep masks/embeddings
and assignments so downstream failures can be distinguished from encoder failures.

The intended inputs remain an assembly FASTA and explicit mean-depth matrix for
one or more samples mapped to that same assembly. Ordered contig/sample IDs,
missing/duplicate/nonfinite-data checks, zero-evidence masks, transformation state,
cache provenance and checkpoint inference are required. Coverage's complementary
value must be measured, especially in single-sample mode. If GLM features enter,
test replacing the composition representation first; do not automatically stack
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

Common CLI/input validation, assignment accounting, embedding/cache manifests,
FASTA export, progress/resource logging and a minimal Snakemake evaluation path
can proceed alongside the spike. Avoid general plugin infrastructure. Deliver a
real small train→save→reload→embed→cluster→export run after the encoder choice,
with an unlearned-feature control and meaningful failure tests. Package/training
settings must be committed before measured evaluation. No proposed CLI is called
runnable until implemented and tested.

## Alternatives and revisit conditions

- **Compact VAE:** restore as preferred only if a matched inexpensive test gives
  worthwhile utility or the contrastive contract is unjustified. Native VAMB's
  cheap runtime alone does not establish our prototype's bin quality.
- **Context-TNF Transformer:** credible short-context option, supported indirectly
  by CompleteBin; its stripped encoder's benefit is unmeasured. It may be efficient
  with a short fixed token sequence. Do not assume every large tool component is needed.
- **Frozen GLM:** choose if actual inference is practical and the bounded comparison
  shows useful signal/utility at its cost. If not, keep a resource or evidence deferral.
- **Full GLM training, taxonomy, graphs or neural merging:** reconsider with a
  concrete failure/input/resource case, not simply because another method uses them.

E001 remains closed at amended seed-11 scope; H001 and its original three-seed
criterion remain unresolved, seeds 23/47 deferred. New short-inclusive data are
allowed without reopening E001. Publication remains a separate owner action with
license/history review.
