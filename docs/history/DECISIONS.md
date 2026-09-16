# Major Decisions and Research Direction Log

> Record decisions that materially affect the scientific question, architecture, datasets, evaluation, project scope, or reproducibility. Do not log trivial code choices.

## Decision 0001 — Build a metagenomic binner before SkullNet

**Status:** Accepted  
**Date:** 2026-09-15

### Context

The original plan was to learn deep learning through a multimodal skull-identification system ("SkullNet"). SkullNet offered excellent visual intuition and personal motivation, but the project owner already has roughly one year of concentrated experience in metagenomic binning through his MSc thesis and benchmark repository.

He also currently retains temporary access to powerful university HPC resources that are substantially more useful for large metagenomic experiments than for the early stages of SkullNet.

### Decision

The primary deep-learning project will be development of a new metagenomic binning method. SkullNet is preserved as a possible later hobby/side project.

### Rationale

The metagenomic project:

- compounds existing domain expertise;
- can begin with simple learning experiments while retaining a very high research ceiling;
- is strongly relevant to computational biology and genomics employment;
- can exploit existing benchmark infrastructure;
- has plausible publication potential;
- benefits materially from current HPC access.

### Consequence

Deep-learning education must be integrated into the method-development path rather than treated as a prerequisite course.

---

## Decision 0002 — The final binner is the destination, not a temporary learning vehicle

**Status:** Accepted  
**Date:** 2026-09-15

### Context

An earlier idea proposed branching into unrelated human-health omics once sufficient deep-learning competence had been acquired, even if the binner remained unfinished. This framing was judged demotivating and inconsistent with the reason for choosing the harder project.

### Decision

The project should continue through design, implementation, and rigorous benchmarking of an independent final binning method.

### Rationale

The owner is motivated by difficult final objectives. The learning phases are valuable precisely because they accumulate toward a concrete research destination.

### Consequence

Breadth into other biomedical omics is deferred until after this project's core destination is reached, unless external circumstances force a deliberate pause or pivot.

---

## Decision 0003 — Do not preselect the final neural architecture

**Status:** Accepted  
**Date:** 2026-09-15

### Context

The contemporary binning field contains VAEs, Siamese/self-supervised learning, multi-view contrastive learning, pretrained/reference-informed representations, taxonomic modalities, DNA language models, and other approaches.

### Decision

No final architecture will be chosen at repository creation.

### Rationale

Combining fashionable components without a failure-mode hypothesis risks a complex but scientifically unjustified system. Early phases should build understanding and generate evidence. Formal architecture selection occurs only after a refreshed literature/code review and targeted experiments.

### Consequence

Initial code should remain modular enough to support experiments but should not create speculative abstraction layers for every architecture that might someday be tried.

---

## Decision 0004 — Reuse benchmark knowledge, not the entire old repository

**Status:** Accepted  
**Date:** 2026-09-15

### Context

The MSc repository contains extensive Snakemake workflows, simulations, evaluation code, and historical results.

### Decision

The new repository will be a clean method-development repository. Relevant benchmark components may be reused or interfaced with deliberately, but the thesis repository will not simply be copied into it.

### Rationale

This keeps the new project's purpose clear and reduces inherited coupling while preserving the value of proven benchmark infrastructure.

### Consequence

Early repository planning should explicitly identify which old assets are imported, wrapped, referenced externally, or left untouched.

---

## Decision 0005 — Treat UCloud access as temporary

**Status:** Accepted  
**Date:** 2026-09-15

### Context

The owner currently has access to high-memory/CPU nodes and H200-class GPUs through university UCloud despite having finished the MSc.

### Decision

Large compute will be used strategically, and all HPC-dependent work should be reproducible/documented with the assumption that this access can disappear.

### Consequence

Prioritize expensive artifacts worth preserving, but debug cheaply before large runs and avoid designing unnecessary hardware dependence.

---

# Decision template

## Decision XXXX — Short title

**Status:** Proposed / Accepted / Superseded / Rejected  
**Date:** YYYY-MM-DD

### Context

What problem or new evidence forced a decision?

### Options considered

What realistic alternatives existed?

### Decision

What was chosen?

### Rationale

Why is this the best choice given current evidence?

### Consequences

What changes in code, experiments, scope, or assumptions?

### Revisit when

What future evidence would justify reopening the decision?
