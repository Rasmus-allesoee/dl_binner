# Learning and Research Roadmap

> This roadmap is directional, not contractual. The **destination is fixed**: a completed, independently evaluated binning method. The path should change when experiments or literature justify it.

## 1. Roadmap philosophy

This project should not have a separate "learning project" followed by a "real project." The real project begins immediately, but its earliest experiments are intentionally simple.

Each phase should produce four things:

1. **understanding** — a concept the owner can explain and reason about;
2. **software** — reusable code or infrastructure;
3. **evidence** — an experiment that teaches us something about binning;
4. **forward value** — an artifact that reduces uncertainty for the next phase.

Do not advance merely because a checklist is complete. Advance when the next level of complexity is justified.

---

## Phase 0 — Establish the research environment

### Purpose

Create a clean foundation before architecture work begins.

### Tasks

- Create the new repository and minimal package structure.
- Keep method-development code separate from the old thesis benchmark repository.
- Record Python/PyTorch/CUDA environment reproducibly.
- Establish local development and UCloud/HPC execution paths.
- Add deterministic smoke-test data small enough to run locally.
- Define experiment configuration and result-storage conventions.
- Decide how model artifacts, large datasets, and HPC-only outputs will be referenced without committing them to Git.
- Establish CI for fast unit/smoke tests that do not require HPC.
- Inventory reusable assets from `hadal-binning-benchmark`.
- Freeze a copy or reference of the thesis-era benchmark outputs that must remain unchanged for historical comparison.

### Learning targets

- PyTorch installation/runtime model;
- CPU vs GPU tensors;
- reproducible environments;
- experiment/config organization.

### Exit evidence

A tiny end-to-end command can load synthetic contig features, train a trivial model, save a checkpoint, reload it, and reproduce a prediction locally and on UCloud.

---

## Phase 1 — Neural-network fundamentals on controlled metagenomic data

### Purpose

Learn the mechanics of neural-network training using a biologically familiar problem with known labels.

### Candidate learning task

Use simulated contigs with known source genomes and construct a deliberately simple supervised task from features such as:

- tetranucleotide frequency;
- contig length;
- single- or multi-sample abundance/coverage;
- optional simple derived statistics.

The task is educational, not yet a proposed binner.

### Implement and understand

- tensors and feature matrices;
- train/validation/test splits;
- `Dataset`/`DataLoader` concepts;
- `nn.Module`;
- linear layers and nonlinear activation;
- logits and losses;
- manual training loop;
- `loss.backward()`;
- optimizer steps;
- learning rate;
- batches and epochs;
- overfitting;
- regularization;
- validation;
- checkpointing;
- basic experiment reproducibility.

### Required experiments

- compare neural network against at least one simple non-neural baseline;
- deliberately overfit a tiny subset to verify model capacity and training correctness;
- examine effect of input normalization;
- examine composition-only vs abundance-only vs combined inputs;
- inspect errors by contig length and genome abundance.

### Exit evidence

The owner can explain the complete training loop and diagnose common training failures without treating PyTorch as magic.

---

## Phase 2 — Unsupervised representation learning

### Purpose

Move from "predict a known genome label" to the actual binning problem: learn a useful representation without having genome labels at inference time.

### Sequence

1. deterministic autoencoder;
2. latent-space inspection;
3. variational autoencoder;
4. clustering learned embeddings;
5. comparison with clustering raw input features.

### Learn

- encoder/decoder structure;
- bottlenecks;
- reconstruction objectives;
- latent spaces;
- VAE mean/log-variance outputs;
- reparameterization;
- KL divergence;
- reconstruction/KL trade-offs;
- clustering metrics;
- why good reconstruction does not guarantee good binning.

### Research connection

This phase provides the conceptual foundation needed to understand VAMB-like approaches rather than merely run them.

### Required experiments

- raw features vs AE embeddings vs VAE embeddings;
- latent dimensionality ablation;
- composition/coverage weighting;
- effect of contig length;
- latent visualization only where scientifically interpretable;
- downstream clustering quality against simulated ground truth;
- reconstruction quality vs actual binning quality.

### Exit evidence

The owner can explain why a VAE might help binning, when it may fail, and why latent-space quality must be judged downstream rather than from loss alone.

---

## Phase 3 — Reproduce and dissect a strong neural binner

### Purpose

Bridge educational implementations to research-grade code.

### Approach

Choose one influential neural binner whose architecture is sufficiently aligned with what has been learned—likely a VAE-based method—and study it deeply.

Do **not** immediately reimplement every tool.

### Tasks

- read the paper and repository together;
- map paper equations/architecture to concrete source code;
- identify preprocessing, network, training, embedding, clustering, and post-processing stages;
- reproduce a small published or documented result where feasible;
- identify which performance comes from neural representation vs downstream clustering/workflow choices;
- document architectural assumptions and hidden heuristics.

### Learning targets

- navigating scientific ML codebases;
- translating papers into implementations;
- distinguishing algorithmic core from engineering details;
- profiling real training workloads.

### Exit evidence

A technical note explains the selected binner end-to-end at the level needed to modify or reimplement its major components.

---

## Phase 4 — Contrastive, metric, and self-supervised learning

### Purpose

Understand modern representation-learning objectives used by binners such as SemiBin2, COMEBin, and GenomeFace-like approaches.

### Learn

- positive/negative pairs;
- must-link/cannot-link logic;
- Siamese networks;
- triplet/metric objectives where relevant;
- contrastive objectives;
- augmentation/view construction;
- false negatives and false positives;
- collapse prevention;
- hard-negative mining;
- self-supervised vs semi-supervised signals.

### Required experiments

- minimal contrastive model on simulated data;
- compare alternative definitions of positive pairs;
- measure whether embedding improvements translate to better final bins;
- inspect where contrastive constraints are biologically wrong;
- compare short vs long contigs;
- evaluate sensitivity to closely related genomes/strains.

### Exit evidence

The owner can reason about how training-pair construction changes what the latent space learns and can separate embedding quality from clustering quality.

---

## Phase 5 — Multi-view, multimodal, and structured information

### Purpose

Learn to combine distinct biological signals without assuming that more modalities automatically improve the model.

### Candidate modalities

- sequence composition;
- multi-sample abundance/co-abundance;
- taxonomic predictions;
- pretrained DNA/genome embeddings;
- marker-gene information;
- assembly-graph structure;
- gene-content/function features.

These are a menu, not a mandatory architecture.

### Learn as needed

- modality-specific encoders;
- early vs late fusion;
- shared vs private latent spaces;
- missing-modality handling;
- attention-based fusion;
- modality dropout;
- graph neural networks if assembly graphs become relevant;
- calibration when external annotations are uncertain.

### Required principle

Every added modality must answer:

> What failure mode does this information address that the existing inputs cannot?

### Exit evidence

At least one multimodal hypothesis has been tested against a simpler model with an ablation that shows whether the added information genuinely matters.

---

## Phase 6 — Transformers and biological sequence models

### Purpose

Gain direct understanding of the machinery behind modern language/foundation models where it becomes relevant to metagenomic sequence representation.

### Learning progression

- tokenization/sequence chunking concepts;
- embeddings and positional information;
- queries, keys, and values;
- scaled dot-product attention;
- multi-head attention;
- feed-forward blocks;
- residual connections and normalization;
- encoder-style transformers;
- pretraining objectives used for biological sequences;
- transfer learning and frozen vs fine-tuned encoders.

### Implementation rule

Implement a small attention/transformer exercise ourselves before using a large pretrained DNA/genome language model as a black-box embedding generator.

### Research questions

Potential examples:

- when do learned sequence embeddings outperform handcrafted TNF for short contigs?
- do pretrained representations generalize to taxonomically novel communities?
- are gains retained after controlling for compute and downstream clustering?
- can sequence embeddings replace some dependency on multi-sample coverage?

### Exit evidence

The owner can explain the core transformer mechanism and critically evaluate whether a pretrained biological language model adds information useful for binning.

---

## Phase 7 — Formal research-gap selection

### Purpose

Stop accumulating techniques and commit to a primary scientific hypothesis for the new binner.

### Inputs

- results from Phases 1–6;
- refreshed literature review;
- source-code study of contemporary binners;
- thesis findings;
- benchmark failure analyses;
- compute constraints;
- available datasets.

### Deliverable

A short research proposal containing:

1. observed problem;
2. evidence the problem matters;
3. why current methods do not adequately solve it;
4. falsifiable hypothesis;
5. minimal proposed method;
6. baselines;
7. evaluation datasets;
8. primary metrics;
9. ablations;
10. failure criteria;
11. expected computational cost;
12. what would count as a meaningful contribution even if the hypothesis fails.

### Exit evidence

The project's novel method can be described in one paragraph without resorting to "combines the best parts of X, Y, and Z."

---

## Phase 8 — Build the actual binner

### Purpose

Turn the selected hypothesis into a complete method.

### Components likely required

- feature extraction/preprocessing;
- model architecture;
- training objective;
- embedding generation;
- clustering/bin formation;
- quality-aware or biological constraints only where justified;
- checkpoint/version management;
- inference pipeline;
- reproducible configuration;
- user-facing CLI or equivalent;
- clear output format.

### Engineering principles

- separate model code from experiment code;
- make preprocessing deterministic and testable;
- make model outputs inspectable;
- permit component-level ablation;
- log data/model/config versions;
- avoid embedding benchmark-specific assumptions in the core tool;
- keep a small end-to-end dataset for regression tests.

### Exit evidence

A technically competent external user could install the tool, provide supported inputs, run the binner, and obtain bins without manually reproducing the developer's notebook state.

---

## Phase 9 — Benchmark and falsify the method

### Purpose

Try to prove the new method wrong before claiming it is good.

### Evaluation layers

#### Controlled simulation

Use known contig-to-genome truth to assess:

- completeness;
- contamination;
- precision/recall-style binning measures;
- genome recovery;
- strain/near-neighbour failure modes where assembly permits meaningful evaluation;
- low-abundance genomes;
- short contigs;
- community complexity;
- abundance-profile variation.

#### Real data

Use orthogonal quality assessment rather than a single proxy metric.

Candidate categories include:

- environmental dataset(s), including prior hadal data where appropriate;
- human-associated microbiome dataset(s);
- taxonomically novel datasets;
- datasets with differing complexity/coverage characteristics.

#### Computational evaluation

Report:

- wall-clock time;
- CPU usage;
- peak RAM;
- GPU type/time;
- peak VRAM;
- preprocessing cost;
- model-training cost;
- inference cost.

### Baseline philosophy

Include:

- simple classical baseline(s);
- strong neural baseline(s);
- methods most directly related to the hypothesis;
- strong current methods even if they use different architectures.

Do not choose only baselines the new method can easily beat.

### Exit evidence

The final claims are supported by reproducible tables/figures and remain defensible under ablation, alternate metrics, and failure analysis.

---

## Phase 10 — Release, paper-quality documentation, and finalization

### Purpose

Convert research code into a durable scientific artifact.

### Deliverables

- tagged software release;
- installation documentation;
- minimal runnable example;
- architecture/method documentation;
- benchmark reproduction instructions;
- model/data provenance;
- limitations;
- computational requirements;
- citation metadata;
- archived result tables needed to support claims;
- manuscript/preprint if warranted;
- concise portfolio-facing summary distinct from the technical documentation.

### Final question

At completion, another researcher should be able to answer:

> What problem does this binner solve, why should the method help, how was it tested, where does it work, where does it fail, and can I reproduce the evidence?

If those questions cannot be answered, the project is not finished.

---

## 2. Parallel tracks that support the roadmap

These tracks run throughout the project rather than forming separate destinations.

### A. Literature and source-code tracking

Maintain a living table of relevant methods, inputs, objectives, clustering strategies, training data, reference dependence, compute, strengths, and failure modes.

### B. Experiment registry

Every meaningful experiment should record:

- hypothesis/question;
- code commit;
- data version;
- config;
- random seed(s);
- hardware;
- output location;
- result summary;
- conclusion;
- next action.

### C. Learning notes

Maintain short concept notes written in the owner's own understanding for major topics. Avoid turning them into textbook chapters.

### D. Failure log

Record experiments that fail and why. Repeated failed ideas are scientific information, not clutter.

### E. Compute ledger

Track expensive runs and their resource use so UCloud access is spent intentionally and future cloud cost can be estimated.
