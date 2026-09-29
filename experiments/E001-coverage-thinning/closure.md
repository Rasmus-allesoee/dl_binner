# E001 closure at the amended seed-11 scope

Date: 2026-09-30. Status: **closed at D010's approved pilot scope**.
The original three-seed criterion was not completed. H001 is **inconclusive**;
seeds 23/47 remain deferred. No scientific run was repeated for this review.

## Accepted return and direct inspection

The [collection receipt](diagnostic-collection-observed.json) binds the owner's
archive, checksum, status JSON and terminal log. Archive SHA256:
`a3132a52502289c580e25dbc26fb094f1a55c41069ad89610537e9f9aef3b824`.
All 297 requested files match the frozen manifest's sizes and hashes; the tar has
298 regular members including the identical manifest. Successful collection used
1 vCPU / 4 GB for 8.0065 driver seconds, **0.002224 allocated core-hours**.
It retained 434,557,937 source bytes in a 235,133,219-byte compressed archive.
This excludes job startup/idle time and is not a billing statement.

Independent analysis with [the closure helper](../../scripts/e001_close_diagnostics.py)
loaded the actual arrays, rather than trusting only native receipts:

- Both conditions' 120 distinct candidate files are complete nonnegative integer
  partitions of all 22,594 contigs. IDs/lengths match the frozen population.
- Combined and coverage COMEBin embeddings are finite float32 matrices of
  22,594 × 128; VAMB embeddings are finite 22,594 × 32 with matching retained IDs
  and all-true input masks. No learned embedding has an exact zero row.
- All six marker-quality counts, sums and tie-breaking selections were independently
  reconstructed for every candidate from retained gene tables and pinned CheckM
  taxon marker sets, preserving adjacent-gene handling and multiplicity. Winners
  exactly match the exported primary predictions.
- Existing native schedules and AMBER parity remain accepted from
  [COMEBin](comebin-paired-observed.json) and [MetaBAT2/VAMB](paired-pilot-observed.json).
  All six primary R95 JSON results were independently recomputed exactly.
  COMEBin's native 111/107-epoch early stops and VAMB's 300 epochs are unchanged.
- COMEBin fixed augmentation intervals and composition remain identical under
  thinning. Retained CS mean/variance arrays scale exactly by 0.1/0.01;
  MetaBAT tables do too. COMEBin normalized CS maximum difference is
  2.392e-6 in each view. VAMB native CS invariance remains accepted from the
  feature receipt; its normalized CS arrays were not included in this collection,
  so no new direct VAMB CS-array check is claimed.
- COMEBin raw all-sample-zero mean rows increase from 0 to 49; zero entries from
  107,383 to 137,424. Native normalization makes all normalized coverage rows
  nonzero. Nonzero transformed values do not imply observed reads. Sample axes
  remain bound to the accepted ten-sample feature manifests.

Full results: [diagnostics](seed11-diagnostics.json),
[240 candidate scores](seed11-candidate-scores.tsv),
[paired per-genome results](seed11-per-genome.tsv), and
[fixed C0 coverage strata](seed11-coverage-strata.json).
Bulk per-query neighbors remain in ignored `artifacts/e001-seed11-closure/`, with
hashes recorded in the diagnostic summary. They can be regenerated locally from
this collection and the frozen population; no UCloud scientific work is required.

## Primary recovery and candidate selection

R95 is mean per-genome recovery in the best qualifying bin at ≥95% confirmed
purity, with the frozen population/denominators and minimum bin size retained.

| Tool | C0 R95 | CT R95 | CT − C0 |
| --- | ---: | ---: | ---: |
| MetaBAT2 | 0.44294 | 0.19502 | −0.24793 |
| VAMB | 0.46177 | 0.48764 | +0.02586 |
| COMEBin | 0.83899 | 0.80255 | −0.03643 |

COMEBin C0's marker winner is also its truth-best candidate (gap 0).
For CT, the marker winner is `bandwidth_0.2 / resolution_30 / ratio_50`;
the truth-best retained candidate is `bandwidth_0.15 / resolution_70 / ratio_50`,
with **R95 0.84118 and gap 0.03862**. All use maxedges100 and the native grid.
This exceeds the prespecified 0.03 selection triage threshold. The CT embedding
therefore supports a better partition somewhere in the existing grid. It does
not prove that a truth-free selector can identify it, nor that it recovers the
same genomes/contigs. It is not substituted into primary results.

## Neighborhood and representation diagnostics

Exact cosine 10-neighbor queries used the frozen 10,000 hash-selected IDs against
21,930 eligible reference contigs; 664 population contigs are outside this probe.
There are 7,964 short queries (2,500–9,999 bp), totaling 36,410,149 bp. Whole-contig
views only: no self-neighbors or augmented siblings. Unique-origin eligibility
excludes cross-origin identical copies. Labels score neighbors, never select them.
Every query is scored; no zero/filtered query was silently dropped.

The table reports **base-weighted purity on short queries**, not classification
accuracy or a calibrated probability. Complete unweighted means are also retained.

| Tool/space | C0 | CT |
| --- | ---: | ---: |
| COMEBin composition | 0.51043 | 0.51043 |
| COMEBin coverage | 0.57384 | 0.49172 |
| COMEBin equal normalized blocks | 0.74427 | 0.73149 |
| COMEBin learned embedding | 0.77236 | 0.75108 |
| VAMB composition | 0.52504 | 0.52504 |
| VAMB coverage including total abundance | 0.61757 | 0.43909 |
| VAMB equal normalized blocks | 0.74868 | 0.72973 |
| VAMB learned embedding | 0.77943 | 0.75708 |

Within CT, raw-combined minus learned purity is ≥0.10 on **19.99%** of COMEBin's
short-query bases (12.78% in C0): the marginal 5% representation triage threshold
is met. The intersection with contigs that lose correct primary recovery is
**1.86% of all short-query bases**, or **13.33% of lost short-query bases**.
These denominators matter: the full 19.99% is not an explanation of recovery loss.
The other prespecified raw spaces are reported separately: COMEBin CT composition
and coverage exceed learned purity by ≥0.10 on 8.47% and 16.97% of short bases,
with lost-recovery intersections of 0.41% and 1.89% of all short bases respectively.
No favorable raw space is chosen as a new primary endpoint.
Among those lost short queries, mean base-weighted raw/learned purity changes
from 0.92164/0.96944 in C0 to 0.85379/0.92562 in CT. Both spaces deteriorate, while
the learned space remains better on average. Local representation damage exists;
its avoidability, causal contribution and seed reproducibility are unestablished.

VAMB similarly has a CT marginal drop on 11.36% of short-query bases, but only
1.20% of all short bases overlap lost recovery, despite improved aggregate R95.
A local neighborhood defect alone does not establish a worse complete binner.
These probes do not test within-bin graph geometry, absolute distance calibration,
or all clustering behavior; no t-SNE picture or truth-trained classifier is used
as a substitute for these fixed diagnostics.

## Length, coverage and retained support

These percentages pool **recovered bases / eligible bases within each length
stratum**, using each genome's same qualifying primary bin. They are descriptive
base-weighted secondary endpoints, not the macro-averaged primary R95.

| Tool | 2.5–5 kb C0→CT | 5–10 kb | 10–50 kb | ≥50 kb |
| --- | ---: | ---: | ---: | ---: |
| MetaBAT2 | 25.50→0.00% | 33.92→0.00% | 36.13→0.05% | 48.58→24.81% |
| VAMB | 38.81→37.59% | 40.40→38.32% | 47.45→44.08% | 47.88→52.82% |
| COMEBin | 58.19→46.93% | 67.09→59.45% | 75.34→62.25% | 91.42→91.13% |

COMEBin loses 39.34 Mb of previously correctly recovered sequence and gains
20.37 Mb elsewhere. Its CT loss is concentrated below 50 kb; ≥50-kb recovery is
nearly unchanged. Fixed genome quartiles based on C0 median summed mean depth
show R95 losses of 0.08520, 0.05528, 0.00771 and a gain of 0.00245 from lowest to
highest quartile. Quartiles are a declared descriptive summary, not a prespecified
hypothesis test or independently randomized groups.

MetaBAT2 leaves 539.63 Mb unassigned in CT versus 17.94 Mb in C0. VAMB and COMEBin
assign all 817.44 Mb in both conditions. Thus retained support/assignment rules
matter alongside learned features; the contrast is not solely an encoder contest.

## Closure, costs and decision

The [cost assessment](seed11-cost-assessment.json) remains authoritative for native
runs: COMEBin successful stages 39.6462 allocated core-hours, recovery-sequence
known lower bound 58.1075; MetaBAT2/VAMB pair 0.76946. Add the collection's 0.002224
separately. Successful COMEBin condition manifests retain 11.313 GB; collection
and local analysis are additional copies, not additional unique scientific data.
No old attempt or large asset was deleted. Actual total billing/remaining balance
is unknown; idle/setup/recovery accounting is incomplete.

Two further COMEBin pairs project ~79.3 core-hours at observed stopping, before
new thinning/features and other tools. They could test whether the selection gap
repeats, but that answer is not required to implement a modest first binner.
Do not spend those resources automatically. Revisit only if a concrete,
implementable selector comparison would change a product decision.

The COMEBin primary loss is below 0.05 and the three-pair reproducibility criterion
cannot be applied. Selection and localized representation signals are retained as
leads, not promoted to a validated intervention or new-method claim. **H001 remains
inconclusive, neither confirmed nor refuted.** The amendment was outcome-informed
and approved before this closure. This is one modified error-free GI assembly,
one thinning/training seed and transductive fitting; it cannot establish real
assembly, strain, ecosystem or unseen-genome generalization.

E001 is now finished at the amended scope. The next decision is product design
using the [current review](../../docs/evidence/2026-09-30-binner-design-review.md)
and [D011](../../docs/decisions/D011-first-binner-prototype.md), not another E001 run.
