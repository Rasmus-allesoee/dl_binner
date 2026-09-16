> Historical planning. Not the active research strategy. Follow [current state](../STATE.md) to the current assessment and evidence.

# Research Strategy

## 1. Purpose

This document defines **how scientific decisions should be made** during development of the new metagenomic binner. It intentionally does not define the final architecture.

The project should be hypothesis-driven, benchmark-aware, and willing to discard sophisticated ideas that do not survive controlled evaluation.

---

## 2. Starting scientific context

The MSc benchmark established a strong empirical base across classical, deep-learning, and ensemble binners. Relevant observations include:

- representation-learning methods can occupy very different completeness/contamination trade-offs;
- workflow architecture can dominate tool choice;
- full multi-against-multi mapping can preserve useful coverage information that concatenated-reference approaches dilute;
- neural embedding quality is only one part of a complete binner—clustering and workflow choices can change final recovery substantially;
- some tools appear completeness-biased while others are contamination-biased;
- MAG quality estimators can have tool-specific biases;
- reference-dependent deep-learning approaches may be vulnerable in taxonomically novel communities;
- short-read strain separation may be limited upstream by assembly;
- compute efficiency varies dramatically among high-performing methods.

These should be treated as **observations to interrogate**, not a requirement that the new binner solve all of them.

---

## 3. Literature and code review protocol

Before committing to a novel architecture, perform a fresh review of the field.

### 3.1 Minimum method map

At minimum, understand representative methods from these families:

- classical composition/coverage clustering;
- VAE-based representation learning;
- self-/semi-supervised Siamese or contrastive learning;
- multi-view contrastive learning;
- reference-pretrained/metric-learning approaches;
- taxonomy-assisted or multimodal approaches;
- DNA/genome-language-model-assisted approaches;
- graph-aware approaches if current literature supports them;
- relevant long-read methods only if they inform transferable concepts.

The thesis-era reference set includes tools such as MetaBAT2, VAMB, SemiBin2, COMEBin, MetaBinner, CompleteBin, GenomeFace, TaxVAMB, and DCVBin, but the list must be refreshed before novelty claims are made.

### 3.2 For each important method, extract

- problem statement;
- supported input regime;
- feature representation;
- neural architecture;
- training objective;
- supervision source;
- augmentation strategy;
- clustering/bin-construction algorithm;
- post-processing;
- reference database dependence;
- training corpus;
- computational requirements;
- benchmark datasets;
- strongest reported advantage;
- known/reported limitation;
- license and code availability;
- pieces that are genuinely novel vs inherited.

### 3.3 Read papers and code together

Do not trust architecture diagrams alone. Important behaviour can live in:

- preprocessing;
- normalization;
- pair generation;
- sample weighting;
- contig filtering;
- clustering heuristics;
- marker-gene constraints;
- post-processing;
- default hyperparameters.

The research question is about the **whole binner**, not merely the neural network.

---

## 4. Hypothesis-generation framework

Candidate ideas should start from a failure mode.

### Template

**Observation**  
What reproducible behaviour do we observe?

**Why it matters**  
Which genomes/communities/use cases are harmed?

**Mechanistic explanation**  
What information is missing, distorted, or misused?

**Hypothesis**  
What change should improve the behaviour, and why?

**Minimal test**  
What is the smallest experiment that can falsify the hypothesis?

**Relevant baselines**  
Which methods must be compared for the result to mean anything?

**Failure criterion**  
What result would make us abandon or reformulate the idea?

### Good research question examples

These are examples of form, not commitments:

- Do pretrained sequence embeddings retain useful genome identity on short contigs where TNF becomes noisy?
- Can a model learn when abundance profiles are unreliable rather than weighting abundance uniformly?
- Does reference-derived semantic information improve recovery in familiar communities while harming novel-lineage generalization?
- Can domain-invariant representation learning preserve genome identity across human-associated and environmental communities?
- Can assembly-graph information improve ambiguous contig assignment without increasing chimeric mergers?
- Can the completeness-biased/contamination-biased trade-off be controlled explicitly rather than emerging implicitly from clustering heuristics?

### Bad starting point

> "VAMB has a VAE, COMEBin has contrastive learning, GenomeFace has metric learning, and CompleteBin has a language model, so combine all four."

Complexity is not a hypothesis.

---

## 5. Dataset strategy

### 5.1 Separate dataset roles

Maintain conceptual separation between:

- **learning/debug datasets** — tiny, fast, safe to overfit;
- **development datasets** — used for architecture/hyperparameter decisions;
- **validation datasets** — used to choose among candidate variants;
- **final test datasets** — protected from repeated tuning;
- **ground-truth simulation datasets** — provide exact assignments but imperfect realism;
- **real datasets** — realistic but rely on proxy quality estimators.

Do not let one celebrated dataset become every layer at once.

### 5.2 Simulation

The existing CAMISIM experience is a major asset.

Use simulation for questions requiring true contig-to-genome assignments, but make simulation design match the specific hypothesis. Potential axes include:

- genome relatedness/ANI;
- community complexity;
- genome abundance;
- abundance covariance across samples;
- contig length;
- sequencing depth;
- novelty relative to training/reference genomes;
- number of samples;
- strain mixture.

Avoid simulations whose construction gives the new method privileged information or whose simplifications eliminate the failure mode being studied.

### 5.3 Real data

A convincing final method should not rely only on the Atacama dataset.

Aim for biologically distinct environments if feasible, potentially including:

- the existing hadal sediment dataset as a high-novelty environmental stress test;
- human gut or other host-associated metagenomes for biomedical relevance;
- one or more established community benchmarks/datasets used by contemporary binners.

The final selection should be driven by research question and data access, not by desire for a large table of datasets.

### 5.4 Data leakage

Pay particular attention to leakage when pretrained genome/DNA models or reference-dependent labels are used.

Questions to ask:

- Were evaluation genomes or near-identical relatives present in pretraining/reference databases?
- Is train/test splitting done at a taxonomic level strict enough for the generalization claim?
- Does a taxonomy modality indirectly reveal the desired cluster labels?
- Are contigs from the same genome split across training and test in a way that inflates apparent representation quality?

---

## 6. Evaluation strategy

### 6.1 Evaluate the whole pipeline

Final binning performance can change because of:

1. feature extraction;
2. neural representation;
3. training objective;
4. clustering;
5. marker constraints;
6. post-processing;
7. workflow architecture;
8. quality filtering.

Therefore, a gain should not automatically be attributed to "the model."

### 6.2 Ground-truth evaluation

On simulated data, prioritize metrics that directly compare predicted bins to known genomes rather than proxy MAG quality alone.

Where useful, stratify performance by:

- genome abundance;
- contig length;
- genome completeness in assembly;
- ANI to closest community member;
- taxonomic novelty;
- number of samples;
- coverage covariance;
- community complexity.

### 6.3 Real-data evaluation

Retain the thesis principle of orthogonal quality control.

A candidate stack may include CheckM2, GUNC, GTDB-Tk, dereplication/ANI tools, and structural-RNA checks where appropriate, but the exact stack should be refreshed with current best practice.

Do not optimize a new model against one quality estimator and then claim independent validation using the same estimator.

### 6.4 Per-genome comparison

Where genomes can be matched across tools, prefer head-to-head/per-genome comparisons in addition to aggregate yield. Aggregate metrics can be confounded because different tools recover different subsets of biological difficulty.

### 6.5 Computational performance

Treat efficiency as a scientific outcome, not an afterthought.

Record at minimum:

- wall time;
- CPU hours;
- peak RAM;
- GPU hours;
- GPU model;
- peak VRAM;
- disk footprint where relevant;
- preprocessing cost;
- training cost;
- inference/binning cost.

If a method improves recovery marginally at a 100x compute cost, report that trade-off plainly.

---

## 7. Ablation strategy

Every major component added to the final method should be removable.

Examples:

- no abundance;
- no composition;
- no pretrained sequence embeddings;
- no taxonomy;
- no graph information;
- alternate loss;
- alternate clustering;
- frozen vs fine-tuned pretrained encoder;
- one modality vs fused modalities;
- simple concatenation vs learned fusion.

Ablations should answer mechanistic questions, not merely create a large supplementary table.

---

## 8. Generalization strategy

A final method should clearly state what kind of generalization it claims.

Possible axes include:

- unseen genomes within familiar taxa;
- unseen species/genera/families;
- environmental to host-associated communities;
- host-associated to environmental communities;
- different sequencing depths;
- different numbers of samples;
- single-sample vs multi-sample;
- different contig length distributions;
- different assemblers.

Do not use the word "generalizes" without specifying along which axis.

A particularly valuable long-term test may be whether representations learned in one biome remain useful in another, because the project owner already has strong environmental-metagenomics experience and wants future relevance to human health.

---

## 9. SOTA claims

"State of the art" should be treated as a conclusion, not a project requirement or branding phrase.

Before claiming SOTA:

- compare against current strong baselines;
- use comparable datasets and evaluation definitions;
- account for computational cost;
- verify statistical/stochastic robustness;
- avoid selecting only favorable metrics;
- distinguish overall SOTA from SOTA in a specific regime;
- state trade-offs and failure cases.

The project can succeed scientifically without a universal SOTA result.

---

## 10. Publication strategy

Publication is an aspiration if the results justify it, not a requirement that should bias interpretation.

A publishable contribution could be:

- a new architecture with reproducible gains;
- a new training objective;
- a new way to integrate modalities;
- a strong generalization result;
- a principled efficiency improvement;
- a discovered failure mode in existing methods plus a solution;
- evidence that a popular complex component does not help under fair evaluation;
- a benchmark methodology contribution tightly connected to the new method.

Keep manuscript-quality figures/tables reproducible from code from the beginning rather than rebuilding provenance at the end.

---

## 11. Research stop conditions

An idea should normally be stopped, simplified, or reformulated when:

- it does not beat a simpler baseline after reasonable debugging;
- its gain disappears under proper leakage control;
- its gain comes entirely from downstream clustering or preprocessing unrelated to the claimed novelty;
- it only helps one tuned dataset and fails basic external validation;
- compute cost is disproportionate to benefit;
- a newer published method already solves the same problem more convincingly;
- the data required to test the claim properly are unavailable.

Stopping an idea is not stopping the project.

---

## 12. Research deliverables to maintain continuously

Maintain living versions of:

- `docs/LITERATURE_MAP.md` — structured method comparison;
- `docs/RESEARCH_QUESTIONS.md` — candidate and active hypotheses;
- `experiments/README.md` — experiment registry/index;
- `docs/DECISIONS.md` — major research/architecture decisions;
- `docs/FAILURES.md` — important negative results and dead ends;
- `docs/COMPUTE.md` — environments, UCloud notes, profiling and expensive-run inventory.

These files need not all exist on day one. Create them when the corresponding information first becomes substantial.
