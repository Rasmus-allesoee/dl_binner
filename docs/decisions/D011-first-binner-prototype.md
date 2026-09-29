# D011: A compact, independently implemented first binner

Date: 2026-09-30. Status: accepted provisional technical direction within the
owner-authorized prototype planning scope; implementation is the next task.
No UCloud execution or publication is authorized by this record.

## Evidence and choice

The [current literature/benchmark/source review](../evidence/2026-09-30-binner-design-review.md)
was completed with cutoff 2026-09-30 before this recommendation. It compares input
modalities and learning families, including pretrained sequence, taxonomy and
graph methods. [E001 closure](../../experiments/E001-coverage-thinning/closure.md)
provides a measured cost/recovery tradeoff, not a universal architecture ranking.

Build one small **variational autoencoder (VAE)** binner of our own. It learns a
compact representation by reconstructing composition and observed coverage while
regularizing the latent distribution. Then use one fixed, conventional density
clustering algorithm to form bins. Implement the feature contract, model, training,
inference and exports ourselves; reuse established numerical/clustering libraries.
Calling VAMB behind a new CLI would not satisfy this milestone. No novelty or
baseline-parity claim is intended.

This is chosen for end-to-end learning value, CPU practicality and few external
contracts. It avoids needing fragment-level coverage, artificial biological
negative pairs, reference labels or pretrained assets for the first working path.
It deliberately accepts a recovery risk: VAMB was much weaker than COMEBin in E001.
A first functional release and a competitive research method are separate milestones.

## Serious alternatives

| Alternative | Why it is credible | Why not first; revisit condition |
| --- | --- | --- |
| Small SemiBin-style pair-contrastive model | Strong independent benchmarks; directly shapes neighbor geometry; few training epochs possible. | Split positives need consistent composition/coverage construction; random negatives can be same-genome. Prefer it if the first reconstruction embedding fails the modest development check despite sound inputs/training. |
| COMEBin-style multiview encoder and selection | Best E001 recovery; complementary signals retained. | Native pair cost and 120-way candidate/marker machinery are substantial. Consider a bounded contrastive or clustering comparison after v0, without assuming every COMEBin component is required. |
| Pretrained sequence / taxonomy / graph model | Extra biological or reference/connectivity signal; good published results in suitable regimes. | Model/database/graph contracts, overlap checks and CPU feasibility are additional dependencies. Add one only when target data and an observed failure justify it. |
| QuickBin-style neural pair merging | CPU-oriented product design; indexed comparisons avoid dense all-pairs work. | Pair-training data, calibration and iterative merge behavior form a different sizeable implementation. Keep as a later efficiency comparator, not an ingredient to mix into v0. |
| Non-neural or existing-tool wrapper | Fastest route to bins and useful baseline. | Does not meet the owner's goal of implementing a deep-learning binner. Use as a control, not the deliverable. |

## Bounded v0 contract

Target one prokaryotic assembly with measured coverage from one or more samples
mapped to that same assembly. Human-associated microbiomes are the initial use case.
This is transductive fitting per assembly, not a universal pretrained predictor.
Support a FASTA plus an explicit contig-by-sample **mean-depth TSV**. Reuse E001
features for development; an adapter reads existing mean channels and ignores
variance explicitly. No remapping or BAM download is needed. Ordered sample IDs,
reference/feature hashes and full contig IDs must be retained and validated.
Missing/duplicate IDs or negative/nonfinite depths are errors, not silent joins.

Initial implementation choices (defaults to freeze before measured evaluation):

- Canonical reverse-complement tetranucleotide frequencies; clearly handle ambiguous
  bases, short/zero-valid-k-mer sequences and a documented minimum length. Use a
  2,500-bp default initially to align with available E001 development evidence.
- Relative sample-depth profile plus log total normalized depth; retain an explicit
  zero-depth indicator/mask. Fit and save transformations on the current assembly;
  never silently refit during saved-model inference. Empty sample columns fail.
  Single-sample mode relies on total depth and composition, with no meaningless
  multi-sample cross-entropy term. Zeros must not be interpreted as observed support.
- Two hidden fully connected layers (128 units), 32-dimensional diagonal Gaussian
  latent, mirrored decoder. Standard reconstruction plus KL objective, separate
  composition, relative-depth and total-depth terms. Record scaling/weights rather
  than quietly inheriting a baseline's coefficients. No added contrastive, taxonomy,
  uncertainty-calibration or graph objective. Latent variance is a training device,
  not claimed calibrated bin-assignment uncertainty.
- One [scikit-learn HDBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.HDBSCAN.html)
  clustering of normalized posterior means, with fixed documented
  parameters (`min_cluster_size=5`, `min_samples=5`, Euclidean metric after L2
  normalization) for the first milestone. No truth-supplied K, marker/parameter
  search, or rescue pass. Noise stays explicitly unassigned. Export all cluster
  assignments; separately mark/export bins meeting a 200-kb FASTA size threshold.
  Pin the library version during implementation, including its `min_samples`
  self-count convention and `n_jobs` budget. These are engineering defaults, not
  biologically optimal settings.
- Seeded minibatch training with a finite epoch limit, finite-loss/gradient checks
  and checkpoint/reload equivalence. Start at 50 epochs, batch 256; this is our
  prototype schedule, not a shortened native baseline. Report reconstruction
  components and latent variance/collapse diagnostics.

## First implementation milestone: one real end-to-end local command

Implement a package and CLI with `features`, `train`, `embed`, `cluster` and `bin`
(the grouped path), plus a minimal Snakemake workflow for reproducible evaluation.
Freeze the exact CLI in implementation; do not present a nonexistent command as
runnable today. The intended user experience is:

```text
dl-binner bin --fasta assembly.fna --coverage depth.tsv --out run --threads 4 --seed 11
```

Deliver assignments including explicit unassigned reasons, eligible bin FASTAs,
embeddings with IDs, checkpoint/normalization, resolved configuration, hashes,
version inventory, training/progress logs and wall/CPU/peak-RAM report. Existing
outputs must be protected; failure must produce nonzero exit and no success receipt.
Saved-checkpoint inference must reproduce embeddings without training again.

Acceptance is a tiny **real** end-to-end run, not a mocked model: feature generation,
backpropagation/changed weights, reload, clustering and FASTA export. Include ID
permutation/missing-data/zero-depth/single-sample cases, failed-input behavior and
assignment completeness. A deterministic toy with known distinct profiles checks
plumbing; it is not biological performance evidence. Run a raw-feature clustering
control to show the comparison exists; do not tune to beat its toy score.

Local acceptance envelope: at most 4 CPUs, one numerical stage at a time, loader
workers=0 and explicit native-library limits; at most 4 GB estimated working memory
and a 10-minute smoke-test stop limit. Measure actual use. A thread cap does not
guarantee full utilization; choose the smallest measured efficient allocation for
any later UCloud run. Do not create a new environment/transfer/retry system when
ordinary local execution suffices.

After local acceptance, prepare one separate bounded development evaluation using
accepted E001 features and existing truth/evaluators (unmodified native results
reused). Commit its settings before running; compare recovery, retained support,
raw versus learned neighbors and resources without truth-driven parameter search.
A poor result must remain visible. Real-assembly and independent public-community
validation belong before robustness/performance claims, not before a functioning
local prototype. No large benchmark campaign is part of milestone one.

## Stop and reconsider

Keep the design if the real pipeline is reproducible, numerically sound and cheap
and produces nondegenerate useful bins in bounded development evaluation. Modify
clustering first if neighborhoods are useful but bins fail; modify representation
if it destroys available signal. If costs or quality make the chosen route unusable,
compare one coherent contrastive alternative, not a stack of untested additions.
A loss that decreases is not alone evidence of useful genome separation.

No more E001 seeds, simulations, pretrained downloads or paper-scale evaluation
are prerequisites. License and history review remain required before publication;
this milestone prepares local software, not a public release.
