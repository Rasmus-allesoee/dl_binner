# Project Charter — Next-Generation Deep-Learning Metagenomic Binner

> **Status:** Initial charter. Stable in purpose, deliberately revisable in implementation.
>
> **Primary rule:** This project is both a deep-learning education and a serious research effort, but the education is not a detour. Every major learning phase should compound toward the final destination: **designing, implementing, and rigorously benchmarking our own metagenomic binning method**.

## 1. Mission

Build a scientifically defensible, technically ambitious metagenomic binning method while using the full development process to gain practical, first-principles competence in neural networks, deep learning, representation learning, modern biological machine learning, and relevant transformer/foundation-model ideas.

The project should ultimately produce:

1. a standalone binning method that can take realistic metagenomic inputs and produce genome bins;
2. a clear scientific hypothesis explaining why the method should improve some meaningful aspect of binning;
3. a reproducible implementation suitable for independent use and inspection;
4. a rigorous benchmark against strong contemporary baselines;
5. ablation and failure analyses that reveal what actually causes performance changes;
6. a polished public research repository that demonstrates independent method development rather than tutorial completion;
7. if results justify it, a manuscript/preprint or other research output.

The project is successful even if the final method does **not** dominate every state-of-the-art binner. A negative or mixed result is acceptable if the work is rigorous, the hypothesis was meaningful, the experiments are informative, and the final software/research contribution is real.

## 2. Why this project exists

This project sits at the intersection of three goals.

### 2.1 Learn deep learning by building, not by consuming tutorials

The project owner learns best when technical concepts are required to solve a real problem. Therefore, neural-network concepts should be introduced when they become useful to the binning problem, then implemented and experimentally understood rather than merely invoked through high-level APIs.

The project should progressively build intuition for concepts such as:

- tensors, parameters, forward passes, loss functions, backpropagation, optimization, batching, regularization, and validation;
- representation learning and latent spaces;
- autoencoders and variational autoencoders;
- metric, Siamese, self-supervised, and contrastive learning;
- multi-view and multimodal learning;
- graph neural networks where assembly-graph information is relevant;
- attention and transformers;
- biological sequence embeddings and genome/DNA language models;
- clustering in learned representation spaces;
- uncertainty, calibration, generalization, and distribution shift;
- large-scale model training, profiling, reproducibility, and scientific evaluation.

The goal is not to collect vocabulary. The owner should eventually be able to explain, implement, debug, and modify the important components without treating the model as a black box.

### 2.2 Extend an existing metagenomics foundation rather than discard it

The project owner already has substantial experience in metagenomic genome binning from an MSc thesis and associated reproducible benchmark. The previous work evaluated 11 binning tools, multiple multi-sample workflow architectures, simulated strain-resolution scenarios, ensemble strategies, MAG quality, chimerism, taxonomy, dereplication, and computational efficiency.

This means the new project should not repeat the thesis under a different name. It should leverage the existing domain knowledge, benchmark design, workflow experience, and scientific questions while adding a genuinely new capability: **independent deep-learning method development**.

### 2.3 Build a high-signal research portfolio asset

The project should demonstrate capabilities that are transferable to computational biology, genomics, biomedical research, biotechnology, and future human-health AI work:

- scientific software engineering;
- Python and PyTorch;
- HPC/GPU computing;
- representation learning;
- modern genomics ML;
- experimental design;
- ablation studies;
- benchmark construction;
- reproducibility;
- biological interpretation;
- reading and modifying research code;
- method development rather than only method application.

This project is a stepping stone toward later work in human health, biomedical omics, drug discovery, disease biology, longevity, and related fields. However, it is **not** intended to be abandoned halfway once enough transferable knowledge has been acquired.

## 3. Final destination

The intended endpoint is a finished research-grade binner, not a collection of educational notebooks.

A reasonable definition of "finished" is that all of the following exist:

- a coherent algorithm with a documented rationale;
- a usable training and inference implementation;
- a reproducible data/preprocessing pipeline;
- a reproducible binning pipeline from required input features to final bins;
- comparison against appropriate contemporary baselines;
- controlled simulated evaluation with ground truth;
- real-data evaluation across more than one biological environment if feasible;
- evaluation of quality, contamination/chimerism, recovery, computational cost, and relevant edge cases;
- ablation studies of the method's important components;
- failure-mode analysis;
- clear limitations;
- documentation sufficient for another technically competent user to understand and run the method;
- a versioned release or equivalent research milestone.

Beating every SOTA tool is **not** a completion criterion. Producing a defensible new method and learning what it does and does not improve **is**.

## 4. Core project philosophy

### 4.1 Ambitious destination, small validated steps

The project may be highly ambitious, but individual milestones should be small enough to reason about and validate.

Do not jump from "beginner in deep learning" directly to a giant architecture assembled from six papers. Build progressively until each major idea has earned its place.

### 4.2 Learn mechanisms before hiding them

When feasible, understand and implement a minimal version of an idea before relying on a high-level abstraction that hides it.

Examples:

- understand a manual PyTorch training loop before adopting training frameworks;
- understand a deterministic autoencoder before a VAE;
- understand the VAE objective and reparameterization before treating VAMB as a black box;
- understand pairwise/contrastive objectives before using a large contrastive framework;
- understand self-attention before using a pretrained transformer;
- understand how a biological sequence embedding is produced before treating a foundation model as a feature oracle.

This does **not** mean reimplementing every low-level numerical primitive or refusing mature libraries. The purpose is conceptual ownership, not performative reinvention.

### 4.3 Research questions before architecture shopping

Never select components merely because successful binners use them.

The preferred sequence is:

1. identify an observed limitation or unresolved question;
2. formulate a falsifiable hypothesis;
3. identify the minimal experiment capable of testing it;
4. choose or design the architecture required by that experiment;
5. compare against strong baselines;
6. run ablations;
7. keep, modify, or discard the idea based on evidence.

Avoid "Frankenstein" architectures built by combining VAE + contrastive learning + GNN + transformer + taxonomy + language-model embeddings simply because each is individually fashionable.

### 4.4 Evidence outranks attachment

Do not protect an idea because substantial time was spent implementing it. If an experiment shows that a simpler method is equal or better, preserve the result and change direction.

The scientific contribution may be discovering that a seemingly sophisticated component adds no value under fair evaluation.

### 4.5 Dynamic implementation, stable purpose

This charter fixes the project's **purpose and research standards**, not its final architecture.

New literature, experiments, datasets, or implementation experience may reveal better directions. Agents should actively update plans when evidence changes, while preserving the overarching mission.

Changes to major research direction should be recorded in the decision log with:

- what changed;
- what evidence motivated the change;
- what previous assumption was invalidated;
- what the new hypothesis or direction is.

### 4.6 Finish the binner

Do not introduce a planned "breadth phase" that diverts the project into unrelated biomedical omics before a final binner exists.

Other domains can be explored later. During this project, learning deep learning is instrumental to completing the method.

If motivation collapses or external circumstances materially change, pausing the project is preferable to pretending that an unfinished educational prototype was the intended endpoint.

## 5. Scientific starting point from the MSc work

The previous benchmark provides several observations that may generate future hypotheses, but none should be accepted uncritically as the new method's design brief.

Important prior findings include:

- no single algorithmic family dominated recovery;
- strong deep-learning binners occupied different yield/purity trade-offs;
- workflow architecture could matter as much as tool choice;
- full multi-against-multi mapping often outperformed concatenated-sample alternatives;
- coverage dilution harmed concatenated-reference workflows;
- current methods appeared to separate into completeness-biased merger and contamination-biased fragmenter behaviours;
- CheckM2 contamination estimates were tool-dependent and could reward particular failure modes;
- ensemble performance was not monotonic with the number of input binners;
- short-read within-sample strain resolution was often bottlenecked by assembly rather than binning;
- reference-dependent methods raise generalization questions in taxonomically novel environments;
- computational efficiency differs by orders of magnitude among competitive tools.

These observations are **candidate research territory**, not predetermined conclusions for the new project.

## 6. Initial scope

### In scope

- prokaryotic metagenomic contig binning;
- deep-learning and hybrid ML approaches;
- sequence composition and abundance/co-abundance features;
- short-read (main), long-read, hybrid binning;
- learned representations;
- simulated and real metagenomic datasets;
- multi-sample and, if scientifically justified, single-sample scenarios;
- taxonomic or pretrained sequence information if supported by the research hypothesis;
- DNA language models / genomic foundation models;
- assembly-graph information if supported by the research hypothesis;
- human-associated and environmental datasets as complementary generalization tests;
- rigorous computational profiling;
- method-level comparison and ablation.

### Not automatically in scope

The following are not banned, but should not be added without a clear reason:

- viral or eukaryotic binning;
- metagenome assembly algorithm development;
- MAG quality-estimator development;
- downstream functional annotation pipelines;
- microbiome phenotype prediction;
- clinical prediction;
- general-purpose biological foundation-model training;
- web application development;
- elaborate UI work;
- commercialization infrastructure.

Each may become relevant later, but scope expansion must be justified by the central binning research question.

## 7. Relationship to the existing benchmark repository

The existing `hadal-binning-benchmark` repository is a **research asset and reference implementation**, not something to copy wholesale into the new repository.

Use it for:

- benchmark methodology;
- workflow patterns;
- known datasets and simulation design;
- evaluation scripts where reuse is scientifically and legally appropriate;
- baseline execution knowledge;
- prior computational profiling;
- understanding tool-specific behaviour;
- future comparison with prior thesis results.

The new repository should remain conceptually clean: it is a **method-development repository**, not a second thesis archive.

Prefer reusable interfaces between the new model and benchmark infrastructure rather than tightly coupling all old workflows into the new codebase.

## 8. Compute strategy and temporary opportunity

The project owner currently retains access to university UCloud/HPC infrastructure, including very large-memory nodes, many CPUs, and H200-class GPUs. This access may be temporary.

Therefore:

- use local/cheap compute for small correctness tests and toy experiments;
- use HPC deliberately for experiments that genuinely benefit from it;
- do not waste scarce GPU time on debugging code that can be validated on a small subset;
- capture environments, commands, configs, seeds, logs, and resource usage so results remain reproducible after university access is lost;
- prioritize expensive data generation, embedding extraction, baseline runs, and large experiments that may become difficult to reproduce later;
- avoid designing a final tool that can only function on extraordinary hardware unless that constraint is scientifically unavoidable and explicitly justified.

Compute abundance is an opportunity, not a license for inefficient architecture.

## 9. Learning contract

The owner is new to deep learning but not new to Python, bioinformatics, HPC workflows, benchmarking, or metagenomic binning.

Agents should therefore:

- explain new deep-learning concepts from first principles without explaining basic biology or metagenomics unnecessarily;
- connect mathematical concepts directly to the metagenomic problem;
- distinguish clearly between "learning implementation" and "production/research implementation";
- expose important tensor shapes, objectives, and data transformations;
- explain why a model component is present;
- prefer experiments that build intuition rather than dumping large amounts of theory in advance;
- encourage the owner to inspect outputs, latent spaces, gradients, loss curves, errors, and failure cases;
- avoid turning the project into passive copy-paste coding performed entirely by agents.

The code may be agent-assisted, but understanding must remain human-owned.

## 10. Research integrity and evaluation principles

The project should follow these standards from the beginning:

- prevent train/validation/test leakage at the biological unit that matters;
- keep simulated ground truth separate from real-data proxy metrics;
- distinguish model-selection data from final test data;
- report random seeds and replicate stochastic training when conclusions depend on them;
- compare against meaningful simple baselines, not only complex models;
- report compute and memory costs alongside recovery metrics;
- use orthogonal MAG quality checks rather than relying on one estimator;
- do not claim strain-resolution gains when the assembly process has already erased strain-specific information;
- do not tune against the final benchmark until it becomes another training set;
- inspect whether gains come from architecture, data preprocessing, clustering, post-processing, or benchmark quirks;
- treat negative results as first-class research outputs inside the repository;
- preserve enough intermediate outputs and metadata to audit important claims.

## 11. Anti-goals

This project is **not**:

- a tutorial repository containing disconnected notebooks;
- a wrapper around an existing binner with a new name;
- a benchmark-only continuation of the MSc thesis;
- an LLM project disguised as metagenomics;
- a portfolio project optimized primarily for visual polish;
- a requirement to beat every baseline on every dataset;
- a reason to postpone understanding until after implementation.

## 12. Decision hierarchy

When trade-offs occur, prefer the following order:

1. scientific validity;
2. progress toward a final independent binner;
3. genuine understanding and learning value;
4. reproducibility and interpretability of results;
5. generalization beyond one dataset/environment;
6. computational practicality;
7. portfolio/presentation value;
8. novelty for novelty's sake.

Career value matters, but it should emerge from doing strong research rather than distorting the science for an impressive README.

## 13. Conditions for changing the project's direction

A substantial pivot is justified when one or more of the following is true:

- experiments falsify a central hypothesis;
- new literature makes the intended contribution redundant;
- required data are inaccessible or scientifically inadequate;
- a newly discovered failure mode presents a stronger research opportunity;
- an architecture is computationally infeasible for reasons that cannot be fixed sensibly;
- the project uncovers a more fundamental bottleneck that must be solved before the original idea matters.

A pivot should change **how we reach the destination**, not casually replace the destination with an unrelated project.

## 14. Documents that govern the project

- `PROJECT_CHARTER.md` — stable mission, philosophy, scope, and success criteria.
- `docs/ROADMAP.md` — progressive learning/research phases and milestone logic.
- `docs/RESEARCH_STRATEGY.md` — hypothesis generation, literature review, baselines, datasets, evaluation, and experiment standards.
- `docs/AGENT_CONTEXT.md` — relevant background about the owner and instructions for AI coding/research agents.
- `docs/DECISIONS.md` — living record of major architectural/research decisions and why they changed.
- Initial idea-phase conversation transcript — historical context. Treat it as context, not as a higher-priority specification than the current charter.

If these documents conflict, the most recently deliberate decision should win, but a conflict should be made explicit and resolved rather than silently interpreted.

## 15. One-sentence project test

Before doing substantial work, ask:

> **Does this help us understand, design, validate, or deliver a better metagenomic binning method—or teach a capability we demonstrably need to do so?**

If the answer is no, it is probably not a priority for this project.
