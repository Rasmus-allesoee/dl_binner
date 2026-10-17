# Prospective dev5 learning bundle

2026-10-17, before changed community fits/scores. This implements the E013/D015
recommendation directly. It is a coherent hypothesis, not VAMB/COMEBin parity or
a claim to have identified the dominant E009 bottleneck.

## One algorithm and defaults

- Preserve the dev4 136-feature composition branch, measured-parent-depth branch,
  64-D unit fused geometry and sequence head, with existing hidden widths. Add
  small composition/depth decoders; no larger encoder, probabilistic latent/KL,
  taxonomy, marker-aware training, transformer, teacher or ensemble.
- Stream FASTA into complete full-parent features. Reuse accepted E009 parent
  features only after exact DNA/ID/length/depth/eligibility/hash verification.
  Preserve short/no-fourmer/zero-depth DNA and explicit exclusion reasons.
- Draw a **fixed cached bank of four real crops**: two disjoint-half pairs,
  seed11 + opaque parent ID. Length is uniform from 256 to
  `min(10000, max(256, floor(.8*half_length)))`, start uniform within its half.
  Parents <512 bp have no crops and train on full-parent reconstruction. A crop
  with no valid fourmers or a duplicate same-parent DNA hash supplies no positive
  evidence; retain coordinates/hashes/masks anyway. This is diverse cached
  augmentation, **not fresh per-epoch windows or measured crop depth**.
- Every eligible parent trains, each epoch, without dropping a singleton tail.
  The full parent plus **every available distinct crop** are the positive set;
  no old random selection that leaves available pairs unused. Average the
  log-positive probabilities outside the log, then anchors within each parent,
  then parent weights `log1p(min(length,10000)/500)`. This prevents parents with
  more usable views getting extra weight and mildly tempers noisy short exposure.
  Other IDs remain possible co-genomic false negatives. No truth/taxon/reference
  or marker counts identify positive/negative pairs.
- Apply the saved dev4 sqrt-TNF/parent-zscore/row-L2 and log1p-parent-depth/zscore
  divided by sqrt(sample count) transforms. All-zero depth branch is masked;
  absent depth is a zero-column mode. Each available training view independently
  drops the depth branch with probability **0.5**. Inference uses original measured
  full-parent depth. This attacks the shared-depth shortcut without pretending
  dropout is sampling/mapping variability or changing the measured matrix.
- From both fused and sequence unit heads, the shared composition decoder predicts
  the normalized transformed **full-parent** composition, averaged squared-L2
  error across the two heads. From fused units, a depth decoder predicts the
  transformed **measured-parent** vector with mean SmoothL1 over nonconstant
  observed columns; no depth loss for absent/all-zero evidence. Unavailable/zero
  observations do not become invented coverage. Parent targets make this a
  denoising/information-retention hypothesis, not exact substring reconstruction.
- Loss = fused all-positive contrastive + **0.5** sequence contrastive +
  **1.0** composition reconstruction + **0.1** depth reconstruction. Temperature
  .2, AdamW .001/weight decay 1e-5, seed11/20 epochs, 256-parent batches, zero
  loader workers, four numerical threads. One rule; no score grid. Preserve all
  component losses/exposure/dropout counts, features, bank, checkpoint/reference
  and independent exact reload, unit embeddings and pre/post partitions.
- Build the same positive symmetric native kNN graph/weights with exact reranking
  and the frozen approximate-recall gate. Apply **only CPM**, with unchanged
  `median_positive_edge_weight / neighbors` density rule. Apply the unchanged
  E013 call-quality/context policy, retaining whole parents and old/new child
  alternatives. The packaged pure selector is byte-identical to frozen E013;
  no objective/resolution/refinement tuning. Old proposals are now computed for
  new parents; accepted old E009 proposals/outputs are never regenerated.

## Evidence, alternatives and risks

[SupCon Eq.2](https://papers.nips.cc/paper_files/paper/2020/file/d89a66c7c80a29b1bdbab0f2a1a94af8-Paper.pdf)
and the [author implementation](https://github.com/HobbitLong/SupContrast/blob/master/losses.py)
support averaging log probabilities over available positives. Here parent identity
defines augmentation positives; this is **self-supervision**, not genome-class
labels. We independently test a two-view NT-Xent equivalence and a ragged-view
manual oracle, including no-positive anchors.

Engineering memory follow-through, before any community fit/score: the input-byte
audit observes over a million original GSA rows. The new NPZ reader therefore
retains each already-owned NPZ member without a redundant `.copy()` and streams
the exact historical JSON ID hash. Release the crop bank before full parent
inference. Tiny equivalence/corruption tests preserve values, masks and ID
contracts; this changes memory lifetime, not loss, schedule or the scientific rule.
Preserve the earlier v1 build/test journals.

[COMEBin's Methods](https://www.nature.com/articles/s41467-023-44290-z) support
real-substring views and explicit coverage/fusion branches. Our retained means
do not implement its measured substring mean/std features. [VAMB's primary
paper](https://www.nature.com/articles/s41587-020-00777-4) and
[author reconstruction source](https://github.com/RasmussenLab/vamb/blob/master/vamb/encode.py)
support retaining composition/abundance information through reconstruction. Our
normalized composition/SmoothL1 loss is a declared choice, not copied VAMB's
abundance cross-entropy, variational formulation or proof of optimal weights.
Publisher VAMB full-text retrieval failed; the accepted review and available
author source are the evidence, not a claimed complete new paper read.

The E011 exposure audit is reused, not rerun. More short parents can add noisy
positives/negatives; a chimeric parent violates the co-genomic assumption. Depth
dropout may discard useful discrimination, reconstruction may retain nuisance,
and false negatives can still fragment sources. Alternatives include positive-only
teacher learning, explicit false-negative handling, raw-DNA/context information
and residual merging. None is automatically added. No extra ablation is required
to implement this bundle. The sole prepared optional control is zero reconstruction
weights if a later result makes that decision consequential; **do not run it now**.

## Prospective evaluation and admission

[Comparison protocol](comparison-protocol.json) owns the one paired development
comparison and gates. No community fit/score until independent oral truth/full
denominators, source/runtime/resource contracts and live credit/storage coverage
pass. Engineering tests are actual tiny installed native stages, with explicit
synthetic DNA/HMMs; do not interpret them as community utility. Exact same-runtime
reload is distinct from the old failed Mac portability contract, which remains.
