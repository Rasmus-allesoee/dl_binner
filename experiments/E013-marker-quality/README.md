# E013 — Confidence, quality and context in marker refinement

2026-10-17. Status: **planned; engineering checks before changed community outcomes**.
Branch `e013-marker-quality-refinement` starts at E012 review commit `17b715f`.
The owner authorizes local implementation and one bounded cached comparison in
this task. Preserve all dev3/dev4 and E009–E012 inputs, truth, outputs, source
freezes and failures. No cloud, acquisition, external fit, encoder/inference,
marker detection, neighbor rebuild or new graph objective/resolution is included.

## Purpose and prospective design

E012 establishes a useful safety guard but no additional CPM marker recovery.
It protects four targets and misses one useful split. Its raw locus/call audit
distinguishes distinct provided loci from partial/overlapping/marginal evidence;
source assemblies and HMM families do not establish universal single-copy biology.
The owner's observation that markers can help other communities is consistent
with the reviewed tools. Keep marker refinement as a product candidate; this
block tests one coherent policy, rather than deciding the feature family's fate.

The [protocol](protocol.json) freezes **one** confidence/quality/context design.
Implementation follows immediately, without a separate ingredient-by-ingredient
performance campaign. Serious alternatives are the original hard-constraint
refiner, E012's graph-only guard, or a new training/representation block. We retain
the two refinement controls while keeping encoder/vectors/graph fixed to locate
the value and limitations of this bundle. New learning remains a justified later
candidate, rather than a claim that the current encoder is the proven bottleneck.

The implemented research refiner has four related parts:

1. **Call reliability.** For each retained trusted domain, use coverage times
   `1 - 2**(-max(0, domain_bits - trusted_domain_cutoff))`; partial gene calls
   multiply another coverage factor. Consolidate same-contig genomic overlap
   >=half the shorter interval at maximum reliability; quarantine multi-family
   genes. Keep all raw evidence and distinct loci. Cross-contig identical families
   or proteins do not establish one physical copy. The weights are heuristic
   evidence strength, **not posterior probabilities** or functional annotation.
2. **Conservative proposals.** Retain the old adopted children/noise. Additionally,
   make at most one new proposal per CPM parent, seeded by the upper-median count
   over all observed reliable families, including singletons. Two families must
   support K; same-contig multiple copies cannot seed different genomes. Seeds
   initialize at most ten sqrt-length-weighted spherical Lloyd iterations on
   unchanged native unit vectors. No hard cannot-links, anchors, forced noise,
   reseeding, random schedule or parameter grid. Unsupported/collapsed proposals
   leave the parent available. Every marker-negative member participates.
3. **Marker-quality proxies.** With weighted physical calls `r`, breadth is
   `100/107 * sum_family max(r)` and excess evidence is
   `100/107 * sum_family(sum(r)-max(r))`. Use `Q=breadth-5*excess`. Compare the
   bp-weighted mean of child Q against parent Q, on the **full parent denominator**.
   Unassigned DNA contributes its original parent Q; discarding DNA alone is no
   free quality gain. This borrowed form is a new panel-dependent proxy, not
   CheckM completeness/contamination or calibrated bacterial/archaeal MAG quality.
4. **Context-supported selection.** Require strict Q improvement (eight ULP
   numerical tie protection), positive bp-weighted leave-one-out native cosine
   centroid silhouette and positive composition **or** available depth context.
   Composition is sqrt TNF; depth is log1p measured parent means divided by the
   eligible-population column std. Constant columns/all-zero depth rows supply
   no depth support. Unassigned DNA contributes -1, missing information zero,
   with full parent bp denominator. This is between-contig feature geometry,
   **not measured per-base/window coverage variance**. Choose highest eligible Q;
   numerical ties prefer more assigned bp, fewer children, then retained route.
   Keep the parent on no strict gain. Graph delta is logged **after** selection,
   allowing biological/context evidence to support a graph-negative split.

Both proposal routes are fixed ingredients of one rule, not a resolution/score
grid. Keep every candidate partition and its components for cheap selective
controls. No truth K, genome/taxon labels, score-based family blacklist or
post-outcome cutoff changes may enter the selector. A null candidate or trade-off
triggers an additional-data/training readiness decision, not indefinite E009 tuning.
This block does not merge separate CPM parents; residual fragmentation remains
a separate grouping limitation, rather than automatic evidence against training.

## Targeted source checks (2026-10-17)

- [HMMER's official guide](https://eddylab.org/software/hmmer/CURRENT/Userguide.pdf)
  describes bit scores as log odds. [PyHMMER's pipeline API](https://pyhmmer.readthedocs.io/en/stable/api/plan7/pli.html)
  documents per-model trusted cutoffs and separate domain thresholds. These
  justify consulting TC and relative margin. They do **not** validate our bounded
  reliability transform or partial-call multiplier; those are declared hypotheses.
- SemiBin `SemiBin/markers.py` at independent root/HEAD
  `f7c45dcbcdfa81e8fbc3e08b04c54683122e72d6`, SHA256
  `7aad72ed474c8310a5a6eda928eac082560db991e22e9627967a058d05990af4`,
  selects the median observed family count and a corresponding seed family.
  We borrow the median principle, adding confidence and multi-family support;
  this is not exact SemiBin parity or an external execution.
- COMEBin `COMEBin/scripts/unitem_profile.py` at independent root/HEAD
  `1b476a41fac893294c70212a869573a732560ce5`, SHA256
  `7d6ca810941f60d3b984845e05d12522f2fa6888b95a079c45be2aaf8415dbf8`,
  reports `comp - 5*cont`. Its [primary paper](https://www.nature.com/articles/s41467-023-44290-z)
  uses marker quality for candidate selection. We reuse that conservative penalty
  form, with explicit weighted panel proxies and a DNA-weighted parent comparison,
  instead of copying its native candidate grid/domain marker estimates.
- CheckM lineage/copy and draft-source limitations are reused from the completed
  [E012 audit](../E012-marker-acceptance/README.md#targeted-source-check-and-marker-audit).
  Its direct PMC page challenged this turn; no claim of a new complete paper read.
  Existing [field/source review](../../docs/evidence/2026-10-08-competitive-binner-study.md)
  and [D015](../../docs/decisions/D015-coherent-prototype-upgrade.md) remain the
  architecture foundation. No exhaustive review or mature-tool campaign restarted.

## Engineering and execution contract

[Refiner](../../scripts/e013_refinement.py) is new research code, consuming the
immutable installed dev4 package's native readers/exporter in the existing owned
Mac environment. Its installed source remains the frozen 18-file dev4 lock; no
old prefix or default CLI is changed. [Consumer](../../scripts/e013_control.py),
[reviewer](../../scripts/e013_review.py) and [local launcher](../../scripts/e013_local.py)
retain config, sources, logs, evidence weights, transforms, alternatives, selected
partition, assignments and every DNA export. This is a runnable research candidate,
not a new packaged/CLI release or a claim to repair the original Mac numerical
portability failure. No new Linux, neural reload or marker detector is claimed.

[Tests](../../tests/test_e013.py) exercise the real production consumer on small
sealed payloads, native PyHMMER HMM readers/writers, hand-authored cached domains,
opaque-ID graph mapping, real refiner, graph-negative selection, full exporter
and independent accounting, cached reload, missing/corrupt refusal, collapsed/
insufficient marker support, no-depth mode and actual clock/disk guard failures.
No reader, selector or exporter is mocked; annotations/vectors are explicit tiny
engineering fixtures rather than biology or neural/detector outputs.

Run once on the full retained CPM parent, after clean source/protocol commit.
All 145,702 contigs /231,678,157 bp, ten depth columns, 13 all-zero rows, short/
marker-negative/non-target/unknown DNA and optional unassigned outcomes survive.
Evaluation is separate, with admitted conservative v2, 156 targets /554,661,890
full provided bp and unchanged 3.3034% N-quarantine. Reuse preserved control scores.
Keep/modify/abandon and data-saturation criteria are in the frozen protocol;
equality supports safety, not a performance gain. Report target losses even if
aggregate recovery improves.

Four numerical threads, 8 GB sampled tree RSS, **30-minute original cumulative
clock across operational repairs**, **2 GiB actual attributed working-space cap**.
Expected 2–6 minutes /~2 GB peak RAM /~0.5 GB extra disk; ceilings are not predictions.
The launcher covers setup/hashing, refiner, review and checksum/member-readback
collection under the same clock. Retain failed journals; explicit reuse verifies
completed bytes instead of repeating accepted refinement. New cloud cost **$0**.
Oral-GSA stays frozen/unacquired; its source/genome/replicon/taxonomy/overlap/truth
and cost admission remain separate. **October 21 storage review is unchanged.**

Execution/result and the next data/training decision will be appended after the
prospectively frozen comparison.
