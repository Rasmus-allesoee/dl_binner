# E013 — Confidence, quality and context in marker refinement

2026-10-17. Status: **completed locally and reviewed**. The prospective design
below and [protocol](protocol.json) remain frozen at clean source `6d06560`,
before changed community outcomes. [Review](review.json) binds the completed
evidence; [operations](OPERATIONS.md) owns the following step.
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

## Completed local comparison

The refiner and independent reviewer both exited zero, without recovery. The
original 30-minute driver, including setup/hash verification, selection, evaluation,
collection and every-member readback, completed in **79.120 s**. Four numerical
threads were capped; sampled tree CPU was **78.36 s**, peak RSS **1.496 GB** and
peak attributed working files **266,744,230 bytes /0.2484 GiB**. These are sampled
resource observations, not exact peaks or GCP billing. New cloud cost **$0**.

| Preserved comparison | Full-reference weighted R95 | Targets >=50% /90% |
| --- | ---: | ---: |
| E012 protected CPM /native parent | 5.3990% | 8 /2 |
| Old CPM refinement | 4.6171% | 6 /2 |
| **E013 quality/context selection** | **5.7388%** | **9 /2** |
| Preserved dev3 learned ten-depth | 5.3911% | 13 /1 |
| Previously accepted sole MetaBAT2 reference | 8.5493% | 16 /5 |

The frozen directional keep criteria pass. Keep E013 as the **provisional research
refiner around CPM**, not a validated product default or uniformly superior
binner. Against protected CPM, one target gains **1,885,026 bp**, with no target
loss; versus old refinement four targets regain **6,221,970 bp**, with no loss.
The useful ASV300.2 split returns while the four previously harmed parents remain
protected. The weighted gain is **0.3399 percentage points**, on one inspected
development community. Dev3 still has more targets above 50%; MetaBAT's accepted
reference remains higher. No refit or repeat baseline score occurred.

Five retained splits are accepted, from CPM parents 116, 314, 450, 546 and 790.
Nine assessed parents remain whole; the other 827 are unchanged. All five accepted
splits reduce the fixed CPM graph objective, so graph gain is indeed evidence,
not a universal veto. All twelve old candidates pass context-sign checks; quality
gain separates the five accepted from seven rejected here. This does not isolate
the causal value of each new weighting/context ingredient. **No new supported
median-seeded proposal was produced**; that route has real tiny engineering
coverage, without a demonstrated community recovery gain. The 3,462 weighted
loci include 615 partial calls, 3,223 weights >=0.5, no ambiguous genes and no new
overlap consolidations in this already-reduced native cache. Tiny fixtures
exercise ambiguity/overlap and proposal generation explicitly.

All **145,702 contigs /231,678,157 bp** survive: 88,960 assigned /209,181,564 bp,
81 unassigned /461,139 bp, and 56,661 excluded-short /22,035,454 bp, across 846
bins. The selector adds **45 unassigned contigs /424,264 bp** versus the parent,
including 342,037 confirmed bacterial bp and seven clean-marker contigs
/317,944 bp. Those sequences remain exported and count in full denominators.
Restricted attributable-B3 recall falls **29.3002→28.9566%** and F1
**42.3078→41.9661%**, despite slightly higher precision and primary R95. The
restricted 165,477,813-bp denominator differs from full-reference recovery and
includes non-target lineages. Full length/origin/eligibility/marker/status cells,
target pairs and unchanged native geometry are in the bound raw review.

The independent reviewer checks every whole-parent/child alternative, all export
DNA and admitted v2 truth. The 156 targets /554,661,890 full provided bp,
all-bin DNA purity and **7,653,205-bp /3.3034% N-quarantine** remain. There are
still 137/193 bins >=200 kb below 95% confirmed purity, and 653 smaller bins;
both mixing and fragmentation remain. Neither that pattern nor this refinement
gain proves that the encoder is the sole bottleneck. Panel/lineage-dependent
marker proxies are not calibrated MAG completeness/contamination.

The **4,176,382-byte archive /29 members** passed independent archive and every
member readback. Its SHA256 is
`a4ca2466d0d9a6cbdc7947a5f1890a009ce51e4177d021aaad3ae78cbf10bfc7`.
Full DNA FASTAs stay locally and are bound by archived export manifests; this is
not a cloud backup. [Review](review.json) binds closed logs, sources, final
postcollection receipts and the original clock separately. The original strict
Mac allclose failure, native vectors, prior journals and frozen installed dev4
remain unchanged. Seven new and 28 related engineering contracts passed; no new
Linux, detector, neural training/reload or packaged CLI path is claimed.

## Next decision: broader evidence and coherent training work

Do not tune this refiner further on E009 now. Its small single-target gain is
enough to retain it provisionally and triggers the protocol's broader-data
decision. Admit the already frozen oral-GSA community, while implementing one
reviewed training upgrade locally in parallel. Grouping need not be perfected
first. A reconstruction-regularized multiview composition/depth candidate, with
more varied real DNA views and use of available positives, is the first choice
to implement; precise losses/weights require a prospective source/config freeze
and tiny contracts before changed community outcomes. No new training runs here.

This ranking reuses the accepted [E011 implementation audit](../E011-cached-grouping-reference/audit.json):
12,337/13,554 training parents (**91.02%**) have coincident coordinates for their
two fixed positive pairs; only 15.22% of eligible parents train, with 75,487 used
only for inference. Real-window pairing is correct, but diversity/exposure is
limited. The accepted E010 inner training loop took 18.265 s at 20 epochs;
cached markers avoid repeating its much longer native detection. Short training
time is a resource observation, not proof of inadequate learning. False negatives,
depth shortcuts, residual grouping, teacher objectives and pretrained/context
models remain serious alternatives. No automatic marker-aware training, taxonomy,
ensemble or larger network is prescribed.

Planning-only HTTP HEAD checks returned all four frozen oral-GSA files, totaling
**2,445,246,434 bytes /2.277 GiB**; **zero response-body bytes were downloaded**.
These checks establish sizes/locators, not checksums or truth admission. Preserve
the [original choice](../E010-coherent-prototype/confirmation-plan.json), verify
publisher MD5/new SHA256 on later authorized acquisition, then audit independent
source/genome/replicon/taxonomy/overlap truth and duplicate-safe full-reference
denominators. Assess any additional source-reference payload before download;
unresolved joins/coordinates/denominators keep truth provisional. Stream compressed
truth/index joins instead of materializing unbounded expanded tables. Oral GSA
has no assembly errors and no ten-depth features: it can test sequence/refinement
transfer, not depth benefit or unseen-genome performance by itself. No acquisition,
community fit or confirmation score occurred in E013. October 21 storage review
remains; the quoted existing disks' $31.20/month while stopped is an earlier
observation, not a refreshed quote or retention extension.
