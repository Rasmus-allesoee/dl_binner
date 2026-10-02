# Architecture reassessment before implementation

Date/cutoff: 2026-09-30. Trigger: owner requested reconsideration of D011, greater
weight on likely bin utility and the thesis results, serious consideration of
pretrained genome language models, and removal of E001's cutoff as a product limit.
This reuses the [completed review](2026-09-30-binner-design-review.md),
[source audit](2026-09-30-design-source-audit.json) and
[E001 closure](../../experiments/E001-coverage-thinning/closure.md). It refreshes only
DNABERT-S's primary paper/model documentation and the relevant local source paths.
No new scientific runs, model downloads or benchmark campaign were performed.
[Provenance](2026-09-30-architecture-reassessment.json) records the inspected bytes.

## What was wrong with the initial choice

D011 v1 made a reasonable case for a cheap learning implementation, but an
insufficient case that its particular small VAE plus HDBSCAN would produce useful
bins. It treated reconstruction's implementation simplicity as a reason to try it
before the better-supported contrastive alternatives. A decoder/KL loss is not
necessarily simpler to validate than a small pair-loss encoder. Neither VAMB's
speed nor E001's available inputs justifies the proposed 128/128 architecture,
50-epoch schedule, HDBSCAN defaults or 2,500-bp product default.

The relevant aim is a usable learned binner with worthwhile recovery, manageable
resource cost and learning through implementation. Fast completion of a weak model
is not the only objective; maximum recovery at any cost is not the only objective
either. There is no evidence-supported scalar score that makes one design globally
optimal. The recommendation below is a conditional product decision, not a
ranking of architecture families proved by these data.

## Evidence carried into the comparison

### Thesis: stronger weight, with its actual contracts

Directly inspected the thesis sections 2.3, 2.15, 3.1–3.2, 3.9–3.10 and 4.8–4.9,
and read its retained MAM summary table. The table agrees on the following counts
and costs. These are **prior thesis results**, not newly reproduced results here.
MQ+ is the table's `MQ_Count`; HQ+ sums `N_HQ` and `N_NC`.

| Tool, MAM | MQ+ MAGs | HQ+ MAGs | NC MAGs | Summed workflow wall hours | Peak PSS GB |
| --- | ---: | ---: | ---: | ---: | ---: |
| CompleteBin | 758 | 180 | 39 | 287.50 | 177.51 |
| COMEBin | 628 | 179 | 45 | 36.74 | 37.07 |
| SemiBin2 | 609 | 176 | 38 | 12.82 | 20.30 |
| VAMB | 499 | 161 | 31 | 5.52 | 2.13 |
| GenomeFace | 466 | 136 | 23 | 8.46 | 6.29 |

CompleteBin was the thesis's integrated first-ranked standalone tool. Its broad
recovery is relevant even though COMEBin led MAM NC counts and SemiBin2 SC led NC
across modes. VAMB's high mean proxy quality partly reflects which genomes it
admits; that average does not erase its recovery deficit. This argues against
choosing a stripped-down VAMB-like design solely for convenience.

Limits: one hadal community, 20 related layers, different mapping/training/clustering
modes, ≥2-kb input, CheckM2 quality estimates plus selective GUNC checks, and
historical versions/patches. CompleteBin required ownership restoration: 35.2% of
raw records were duplicate claims, resolved by a largest-bin rule. That changes
the evaluated output and prevents calling it exact current upstream performance.
Training rules used GPUs (confirmed in the retained Slurm profile); wall hours and
PSS therefore cannot be converted to our current CPU bills or attributed solely
to a Transformer. Much cost also comes from preprocessing/clustering. The supplied
`CPU_Hours` is process accounting, not charged allocated core-hours.

### E001: measured present-day evidence, narrower scope

COMEBin R95 was 0.83899/0.80255; VAMB 0.46177/0.48764 in C0/CT. COMEBin's
successful pair cost 39.6462 allocated core-hours, versus 0.76946 for the grouped
MetaBAT2/VAMB pair; the latter is not a separately measured VAMB-only total.
The substantial recovery/cost tradeoff is real in this one development setting.

However, VAMB's short-query learned neighbor purity was 0.77943/0.75708 versus
COMEBin's 0.77236/0.75108 (base-weighted). Similar local neighborhoods produced
very different final recovery. COMEBin CT's 0.03862 candidate-selection gap also
shows downstream decisions matter. Consequently E001 does not isolate a VAE loss
as the reason VAMB loses, or establish contrastive encoders as categorically better.
Our previous VAE-plus-HDBSCAN proposal changes both learning and clustering from
native VAMB; it has no measured recovery guarantee.

### Current literature: why newer designs are plausible

The completed independent benchmark review supports COMEBin/SemiBin2 as strong
practical references; it also finds rankings depend on assembly mode, population,
clustering, quality criterion and versions. Newer mechanisms address real issues:
contrastive objectives shape identity/separation rather than merely reconstructing
inputs; sequence/context encoders can preserve information erased by whole-contig
4-mer summaries; pretraining imports knowledge unavailable in a small target
assembly. These are rational directions, not evidence that every new ingredient
is needed or that release date predicts utility.

Three separate choices are often conflated: **network architecture** (MLP,
Transformer, GNN), **objective** (reconstruction, contrastive, taxonomy prediction),
and **information/training source** (target assembly, reference genomes, graph,
coverage). They overlap. [TaxVAMB](https://doi.org/10.1038/s41587-026-03098-0) is a
new bimodal VAE; DCVBin uses language-model features with VAE fusion. CompleteBin
uses contextual TNF tokens, taxonomy-pretrained embeddings and contrastive learning.
None is a controlled experiment replacing only a VAE with an LLM.

[DNABERT-S](https://doi.org/10.1093/bioinformatics/btaf188), sections 1, 3.3, 4–5
and discussion, is especially relevant: its generic DNA foundation-model controls
can underperform TNF; species-directed contrastive training improves the embedding.
It reports expensive GPU training, but a frozen public checkpoint lets us avoid
that training cost. Its binning evaluation filters above 2,500 bp, so sub-2.5-kb
bin utility remains unestablished by this paper. Species separation is also not
strain separation, assignment confidence or complete MAG quality.

## Objective comparison for our goals

Qualitative judgments below are **inferences**, with confidence limits. 'Cost' is
expected from the execution contract unless a measured value is explicitly given.
No invented numerical utility scores or proportional CPU speedups are used.

| Coherent route | Likely bin utility and limitations | Learning value / first-product work | CPU and dependency cost | Judgment now |
| --- | --- | --- | --- | --- |
| Compact VAE, global composition/coverage | Reconstruction need not preserve genome distinctions; native VAMB loses recovery in thesis/E001, but its E001 neighborhoods are competitive. A better clusterer or objective may change this. | Teaches probabilistic encoding, reconstruction, regularization and full pipeline. Requires decoder and objective balancing; proposed tiny settings are unvalidated. | Small feature matrices/MLPs, PyTorch plus clustering; strongest measured affordability evidence. | Useful low-cost control/fallback; not the preferred first architecture merely because it is easy. |
| Lightweight contrastive MLP with composition/coverage | Most persuasive balance from SemiBin2/COMEBin evidence; identity objective fits binning. Whole-contig TNF still loses local order; false negatives, chimeric positives and augmentation shortcuts are risks. | Teaches representation learning, pair construction, biological assumptions and clustering. Can implement our own encoder/loss without a marker-grid framework. | Small trainable network; no reference model/database. Native tool costs include other stages and do not predict our reduced implementation. | **Leading default for current CPU/product constraints**, with augmentation contract fixed before implementation. |
| Compact context-TNF Transformer with contrastive learning | Retains local composition/order; plausible for short fragments, informed by CompleteBin. A stripped version may lose benefits from pretraining and clustering; local TNFs are noisy on very short fragments. | Attention and token design are accessible without training a foundation model. More input/view contracts than an MLP; beneficial only if context helps. | Fixed few-dozen feature tokens can be much cheaper than raw-DNA attention. Standard PyTorch possible; no basis for assigning all CompleteBin memory/time to this encoder. | Strong second encoder candidate if a small context ablation has value; retain in scope rather than rejecting all Transformers as expensive. |
| Frozen species-aware raw-DNA GLM plus a small learned binning head | Adds sequence information beyond TNF and a reference-trained prior; plausible opportunity with limited target data. Highest achievable ceiling is unknown. Pretraining overlap, HGT/shared sequence and species/strain mismatch remain. | Teaches tokenization, transfer learning, feature caching and learned integration; can be our own learned binner while reusing a backbone. Freezing omits backbone-training practice, not all deep learning. | One costly inference/cache pass, then cheap head training. Author DNABERT-S checkpoint ~469 MB; actual CPU tokens/s, activation RAM and chunking cost unmeasured. Pinned custom model code/tokenizer/PyTorch/Transformers required. | **Serious high-priority contender**. One bounded CPU feasibility check before ruling it in or out; do not assume GPU pretraining cost is inference cost. |
| GLM trained/continually pretrained end to end | Potentially adapts sequence signal, but no project evidence that it is necessary or best. Requires training data/overlap discipline and optimization beyond binning. | Broadest backbone training experience, also greatest delay and engineering burden. | Published DNABERT-S training used eight A100s; our CPU-only access does not establish affordable parity. | Defer for first product. Reconsider with changed resources or concrete evidence that frozen features are insufficient. |
| Taxonomy-VAE / assembly-GNN / neural merging | Extra annotations, links or efficient comparisons can solve specific failures. Their utility depends on reliable labels/graphs/pair-training data. | Valuable specialized learning; expands the first input/payload contract. | Database/reference/graph costs or iterative pair engineering; tool-specific, not uniformly high. | Keep as real alternatives; no evidence that these contracts improve this first implementation enough to require them now. |

### Source implications for GLM and Transformer cost

The [author checkpoint](https://huggingface.co/zhihan1996/DNABERT-S/tree/main) lists
~468 MB weights. The inspected local DNABERT-S config has 12 layers, width 768,
12 heads and float32; `bert_layers.py` includes a slower PyTorch attention fallback.
That is source evidence of a possible CPU path, **not runtime validation**.
The DCVBin extractor's `cuda if available else cpu` is likewise not proof of
feasibility: it processes sequences individually, uses token truncation at 5,000,
and does not establish the inference/strand/long-contig contract we need. Pin and
review the actual author checkpoint, not a locally incomplete payload.

CompleteBin's inspected `CompleteBinBaseModel` instead projects TNF vectors into
a short token sequence and uses Transformer layers with an optional taxonomy
classifier. Its paper calls this a genome language model, but the inspected path
is not simply DNABERT-S on every DNA token. Its frozen taxonomic branch runs with
`no_grad`; the target model trains separately. This is why CompleteBin's success
cannot establish that a large raw-DNA LLM is the winning ingredient. The current
code and thesis/paper recipes also differ; those identities remain separate.

## Short contigs: independent product requirement

E001's 2,500-bp cutoff is an experimental inclusion rule, never a product constraint.
The thesis's 2,000-bp rule also excludes much of CompleteBin's intended range.
Keep short-capable methods and configurable length eligibility in scope. Existing
accepted results cannot be extrapolated to 768–1,999-bp fragments. A transformed
input accepted by a model is not evidence of reliable short-contig assignment.

A later bounded development evaluation should report [500,768), [768,1000),
[1000,2500), [2500,10000) and ≥10-kb strata, with any unsupported range explicit.
Use a public unfiltered short-contig assembly with suitable truth and/or a new
controlled genome-fragment panel; exact inputs and counts must be frozen before
scores. Synthetic fragment evaluation tests sequence separability, not assembly
error or full pipeline recovery; real-assembly validation remains separate.

For whole-bin recovery, keep a fixed eligible denominator within each comparison;
score missing/short contigs explicitly rather than removing failures. Report a
shared-input comparison and native supported-range comparisons separately. Include
long contigs too: improving tiny fragments while harming most bases is not a useful
product gain. Do not force uncertain/shared/chimeric fragments into bins merely to
raise utilization. No additional E001 seed, thinning or native fit is authorized.

## Recommendation and bounded next step

**Change D011 and keep the encoder choice provisional.** Remove compact VAE as the
accepted first implementation and its inherited length/default schedule. Prefer a
lightweight contrastive prototype on current evidence, while giving frozen GLM
features one real feasibility check before choosing the sequence encoder. A VAE
remains a cheap reference; no need to implement it first as a curriculum exercise.
The owner's GLM interest is a legitimate learning priority but is not empirical
proof of utility; neither novelty nor a speculative highest ceiling is the gate.

The exact next step is a **single local frozen-DNABERT-S feasibility spike**, not
backbone training or a full tool comparison. Implement/test an extractor with a
pinned public checkpoint and actual CPU inference on a small deterministic panel
of real DNA windows spanning short and long lengths. Test masking, token limits,
ID order, strand treatment, caching and checkpoint origins. Record tokens/base
ratios, warm/cold timing, peak RAM, effective CPU use and projections for explicit
assembly size/length distributions. A tiny synthetic fixture alone is insufficient
for throughput; no accuracy claim follows from this check.

Bound execution to one checkpoint, one environment attempt, at most four CPUs,
8 GB measured working RAM and one hour of timed inference after setup. These are
planning stop limits, not observed requirements or an inference-cost forecast.
Do not increase a failed timeout or start a dependency-repair campaign automatically;
retain diagnostics and decide whether the contract is viable. Downloaded model/code
bytes stay ignored with hashes/license recorded. Owner operates any later UCloud job.

If CPU inference is untenable or the implementation requires a broad compatibility
fork, proceed with the lightweight contrastive prototype and record the GLM as
resource-deferred. If it is viable, run one small sequence-representation comparison
on new short-inclusive development data before selecting GLM-derived features over
TNF/context. Compare neighbors and a fixed clustering path, with equal eligibility
and no oracle K or quality-based cherry-picking. This is the only follow-up gate,
not permission for an expanding architecture search. Scope/cost is fixed before it
runs. Full-scale performance superiority remains a later claim.

Common product plumbing may proceed alongside that spike: ID validation, masks,
embedding/cache manifests, assignment accounting, FASTA export, logs and resources.
Keep the seam at the existing biological boundary—sequence features to a learned
embedding—rather than building a general plugin framework. Once the choice is made,
complete one real end-to-end prototype. [D011](../decisions/D011-first-binner-prototype.md)
owns this amended next milestone.

## Validation of this reassessment

2026-10-03 follow-up: [E002](../../experiments/E002-dnabert-s-feasibility/README.md)
completes the prescribed frozen-DNABERT-S CPU check. Native contracts pass at
small local scale; measured cost supports one capped representation comparison,
not accepting bulk extraction as cheap. D011/STATE now point to that comparison.
This does not change the dated review's original scope or claim new binning accuracy.

Documentation/provenance only: `python3 scripts/check_docs.py --check-context`
passes (38 maintained documents, 426 links, 84 present fingerprints; ten historical
optional cache paths unavailable). All new source hashes match, and the thesis
cache equals the prior checkout's text. `git diff --check` passes. No code/runtime
change needs the full E001 regression suite; its previously accepted results remain
untouched. No GLM runtime, throughput or new accuracy test is claimed.
