# D015: a coherent prototype upgrade with selective ablations

Date: 2026-10-16. Status: **accepted for the first integrated implementation**.
The owner subsequently authorized local implementation/engineering checks and
the normal benchmark-planning PR merge. [E010](../../experiments/E010-coherent-prototype/README.md)
owns the prospective algorithms/defaults, implementation, contracts and separate
future execution request. Community fits, VM wake/spending and retention extension
were not needed for implementation. The later separately approved native run and
its reviewed outcome are recorded below; no retention extension followed.

## Decision and why it changes

Recommend building a substantially stronger, integrated next prototype. Incorporate
marker-conflict handling into its grouping/refinement module; **do not require a
standalone split of dev3 bins first**. That narrower experiment remains an optional
cheap diagnostic, not the next milestone or a gate to implementation.

The concern about slow serial feature experiments is well founded as a workflow
risk. AGENTS had turned a useful causal-inference rule into a requirement to test
one mechanism before combining improvements. Engineering a coherent candidate and
establishing which ingredient caused its gains are different tasks. Existing
literature, source observations and thesis evidence can justify implementing a
bundle; matched ablations are needed for specific causal claims or design choices
whose uncertainty matters, not for permission to build every ingredient.

This does not establish a universal checklist of mandatory SOTA components. Tools
use markers at different stages; repeated use supports a strong engineering prior,
not proof that marker-aware training, grouping and selection must all help here.
Network size is also not the development objective. Choose components that address
the same biological task and fit one explicit computational/data contract.

## Evidence reused, without another review campaign

- [The completed field/source review](../evidence/2026-09-30-binner-design-review.md)
  and [October focused study](../evidence/2026-10-08-competitive-binner-study.md)
  support real sequence views, composition/abundance learning and biological
  grouping/refinement. COMEBin and SemiBin2 combine several of these; MetaCAT
  also illustrates the importance of grouping without requiring a neural encoder.
  Their whole-tool results do not identify individual causal contributions.
- [The thesis reassessment](../evidence/2026-09-30-architecture-reassessment.md)
  reports strong CompleteBin/COMEBin/SemiBin2 recovery, with different resources,
  versions and patched outputs. These are prior thesis results, not reproduced
  project results. Its resource and proxy-quality qualifications still apply.
- [E001](../../experiments/E001-coverage-thinning/closure.md) found similar local
  neighborhoods with very different final recovery. [E003/E004 evidence](D011-first-binner-prototype.md)
  also shows neighbor agreement alone cannot choose a representation or clusterer.
- [E009's completed review](../../experiments/E009-competitive-benchmark/controls-review.json)
  at `cc6dd1c` shows both useful information and multiple losses: bacterial
  ten-depth neighbor agreement 68.63→67.05% after learning, primary restricted
  grouping recall 18.48→37.61%, weighted conservative reference recovery
  4.5765→5.3911%, and substantial mixing/fragmentation. Only 18.5321% of the full
  provided bacterial reference bases have confirmed unique loci in this assembly;
  the 3.3034% N-quarantine remains. These data do not isolate an encoder-only or
  grouping-only cause, and do not decide product feature families.
- Direct source inspection here, at preserved dev3 source
  `5e54538d1799e8d2538621729400f33fbaf017b9`: `Encoder.forward` and `nt_xent` in
  [model.py](../../src/dl_binner/model.py) use normalized dot-product geometry;
  [clustering.geometry](../../src/dl_binner/clustering.py) subsequently z-scores
  embedding dimensions and normalizes again. This changes the metric. It is a
  concrete interface/design issue to resolve, not a newly measured cause of E009
  error or permission to repair the preserved dev3 outputs in place.

Focused primary-source checks on October 16 agree with the existing interpretation:
[COMEBin's author overview](https://github.com/ziyewang/COMEBin#overview) describes
sequence-substring views, a coverage network, a combined network and Leiden;
[SemiBin's grouping source](https://github.com/BigDataBiology/SemiBin/blob/main/SemiBin/cluster.py)
contains graph grouping and marker-seeded reclustering, and its
[training source](https://github.com/BigDataBiology/SemiBin/blob/main/SemiBin/self_supervised_model.py)
contains split-pair learning. These mutable source links are dated observations,
not new executable pins. Publisher paper retrieval failed here; the completed
paper reviews and their versioned source provenance are reused, not claimed reread.

## Recommended first integrated candidate

| Part | Include in the next implementation | Purpose and important boundary |
| --- | --- | --- |
| Biological training views | Actual DNA windows/splits from sufficiently long contigs, with traceable parent/window coordinates and a declared short-contig policy | Learn agreement between genomic fragments rather than only masked copies of one feature vector. A chimeric parent can violate the same-genome assumption; do not claim biological labels from contig identity. |
| Composition and abundance model | Explicit modality-specific encoders/fusion, documented depth scaling/zeros and fitted transforms; consistent declared training/inference/grouping geometry | Retain useful measured coverage while improving the representation contract. Choose a justified compact network and defaults once during implementation; a larger Transformer is not required. Sequence-only and one/multiple-depth inputs remain explicit modes. |
| Genome-scale grouping | One scalable sparse-graph grouping path with a declared metric and parameters, followed by marker-informed refinement including conflict splitting | Address fragmentation and mixing together at the pipeline level. Preserve pre/post-refinement partitions. Avoid a large candidate grid, truth K or a selector tuned to E009 labels. Validate approximate-neighbor contracts if an approximate index is chosen. |
| Reusable marker evidence | Versioned gene/marker detection cache with hit provenance, deduplication and absence/ambiguity handling; use it in grouping/refinement first | Same-SCG hits can provide separation evidence, not positive genome identity. Multicopy biology, split genes and short contigs weaken constraints. Marker-negative DNA needs a real assignment/noise path, never exclusion by default. Evaluate with sequence truth, not solely the markers used to choose bins. |

These are related modules in one prototype, not four sequential biological trials.
Preserve their intermediate contracts and test them while integrating. Reuse sound
product I/O, provenance, accounting and supervision rather than rebuilding those.
The exact view lengths/count, architecture sizes, graph algorithm and refinement
rules belong in a concise prospective implementation decision, followed directly
by code and real tiny contracts in the same work block. No second exhaustive
architecture review or separate sign-off per ingredient is needed.
Pin reusable marker assets/tools and their licenses before using or redistributing
them; do not copy an external binner behind our CLI and call it our new method.

Use the accepted mean-depth matrix initially. Parent-contig means are not measured
window coverage, and within-contig variance cannot be recovered from those means.
If parent depth conditions a sequence window, name that assumption explicitly.
Any request for actual window depth/variance needs an explicit retained-BAM scan
and resource case; it must not imply a new mapping/data-DAG run or silent imputation.

Keep marker-aware training/false-negative handling as a serious later design
choice, rather than automatically adding it to every marker role. Its use can be
reconsidered within implementation if source/availability evidence changes the
case; a new empirical claim needs a matched control. Frozen GLM/context attention,
taxonomy databases, assembly-graph inputs, backbone pretraining and large ensembles
remain alternatives, not defaults for this candidate. Existing GLM evidence and
the separately requested follow-up are preserved; they are not blockers.

## Validation that supports faster development

1. Implement one complete candidate on a new research branch, keeping immutable
   dev3 source/wheel and all E009 data, truth, outputs and failed journals intact.
   Unit tests and tiny end-to-end training/reload/marker/export contracts are
   engineering checks, not separate performance studies. No community fit now.
2. Prepare one bounded candidate-versus-dev3 development comparison. Reuse the
   accepted baseline outputs; do not refit dev3 just to populate a new table.
   Prospectively fix the candidate, inputs, evaluator contracts and budgets.
3. Retain the pre/post-marker-refinement outputs from the same encoder/run. This
   cheap paired comparison can inform whether refinement adds value. A changed
   positive/negative objective would require another fit; run that only if its
   uncertainty could change the design. No full factorial or mandatory ablation
   for every normalizer, layer, graph option and marker role.
4. Choose/freeze additional human-associated confirmation data before changed
   community scores, in parallel with implementation. Dataset preparation is not
   a gate to writing code. E009/E005 remain development data; overlap limitations,
   all length/origin strata and independent truth must stay visible.

A gain of the integrated candidate establishes a **bundle-level** improvement,
not the cause, novelty or necessity of each component. Published ablations and
source studies are reusable prior evidence. Selective ablations of our candidate
or, exceptionally, a justified external tool can resolve remaining consequential
uncertainties. They are not a compulsory external-tool campaign. No external fit,
including CompleteBin, is recommended now.

## Alternatives, reconsideration and boundaries

Standalone marker splitting is cheaper and causally cleaner for that narrow
operation, but keeps weak views/geometry and fixed grouping in place. It may be
useful as a cached diagnostic later; it is too narrow as the default next product
milestone. A maximal stack of GLM, taxonomy, attention, GNN and marker losses would
expand dependencies, costs and failure modes without a coherent current case.
Neither alternative is preferred.

Modify the candidate if real contracts show unusable marker availability, invalid
view/coverage assumptions or an unaffordable grouping path. Retain the failure and
choose an explicit design adjustment, without an automatic family/tool search.
If the integrated version fails to improve useful recovery at controlled impurity,
diagnose the retained stages and select the ablation that can change a decision.
Do not explain away a failed result with ever more components or tuned E009 scores.

The original reassessment changed guidance only; the later owner prompt authorized
the local implementation now recorded in E010. Community fits, bulk acquisition/
assembly/mapping, paid cloud compute, new resources and retention extensions remain
separate scopes; the first bounded candidate run has its own proposed approval.
The prior $20 data and $2 control ceilings are not an open budget for the upgrade.
The October 21 disk-retention review is unchanged. [STATE](../STATE.md) and
[E009 operations](../../experiments/E009-competitive-benchmark/OPERATIONS.md#exact-following-step-prompt)
own the current handoff and exact implementation prompt.

## First native bundle result, 2026-10-17

[E010's independent review](../../experiments/E010-coherent-prototype/review.json)
accepts the completed native workflow and all retained DNA, with an explicit
unresolved Mac inference-tolerance limitation. The scientific outcome is mixed:
weighted full-reference R95 is 1.8763% before refinement, 4.2909% after, versus
preserved dev3 learned ten-depth 5.3911%. The bundle does not establish a stronger
whole binner; implementation acceptance is separate from product-quality adoption.

The new view/modality/unit-geometry bundle improves short bacterial neighbors,
but long/bp-weighted geometry remains weaker and global graph communities are
coarse. One 35.10-Mb bacterial-dominant pre-bin contains 107 supported genomes;
45/57 large bacterial-dominant post-bins remain below 95% confirmed purity.
Refinement has a useful paired recovery effect but newly unassigns 20.50 Mb,
including 8.49 Mb of confirmed bacterial support, and harms one previously
recovered target. No single component is proved solely responsible.

Recommend one cheap **cached CPM-versus-RB grouping-objective control**, keeping
encoder, graph/weights, marker cache and existing refinement fixed. Its incremental
decision is whether a different local-density objective can convert useful
neighborhoods into purer groups without excessive fragmentation. Freeze one
label-free setting before changed scores, rather than a truth-tuned grid. CPM's
density meaning differs from RB's graph-wide configuration model; the dated
[primary API formulas](https://leidenalg.readthedocs.io/en/stable/reference.html#cpmvertexpartition)
support the alternative, not a claim that it will fix this assembly. Changing
long-contig learning or refinement remains a serious alternative if this control
fails. This is a decision-driven selective test, not a return to mandatory isolated
experiments for every ingredient.

The next task prepares that control locally; no new partition, fit, score, VM wake
or budget is authorized here. A later useful frozen mechanism needs the already
prospective oral-GSA confirmation, after source/truth/overlap admission. Keep all
external binners deferred and October 21 retention visible. AGENTS now distinguishes
exact native reload from cross-platform numerical portability; the failed tolerance
is preserved while native-byte diagnostics have their own explicit admission scope.

## Frozen implementation audit and next controlled execution, 2026-10-17

[E011](../../experiments/E011-cached-grouping-reference/audit.json) finds a real
prose/code contract discrepancy in marker seeds: second-largest family count is
executed, providing two independent witnesses for the split count. Four adopted
proposals differ from the largest-count prose. Preserve it in the cached objective
control; changing it would confound that test. It cannot cause the poor pre-stage.
Saved transform arithmetic, disjoint parent pairing, parent-depth semantics,
geometry/graph, refinement accounting and evaluation show no identified fatal bug;
this is not proof of optimality or an exhaustive absence of defects. Limited
window diversity, long-only training, false negatives and depth shortcut remain.
The new owner authorization covers direct E011 execution and one MetaBAT2 external
feasibility reference after gates, not an encoder repair or larger campaign.

E011's first authorized native attempt stopped at a new provenance-helper bug:
normal dynamic-library symlinks were refused before CPM/MetaBAT community runs.
[Failure/repair](../../experiments/E011-cached-grouping-reference/native-observed.json)
preserves the original source/bytes and closes the attempt without recovery.
The fix separates loader aliases/resolved content from scientific artifact rules;
AGENTS records that durable distinction and keeps lexical Python invocation paths.
No biological conclusion or architecture change follows from this gate failure.

## Connected execution recovery clarification, 2026-10-17

The owner explicitly authorizes debugging and operational retries of E011 in the
same task, including reasonable justified envelope changes, without another
ceiling/approval handoff. The earlier no-retry interpretation was too restrictive
for a connected GCP workspace. Preserve the closed failed journal, test the actual
repair and verify passed cache/installation before reuse; keep the scientific CPM
rule, marker policy and sole MetaBAT reference frozen. This authorizes operational
recovery, not outcome-driven tuning or repeating accepted science. Keep fresh
credit coverage, explicit per-attempt limits, shutdown and October 21 storage review.
Follow a short (about 15 minutes or less) supervised job through completion and
local review; healthy longer work may be handed off after verified real progress.

## Completed cached objective/reference, 2026-10-17

[E011's review](../../experiments/E011-cached-grouping-reference/review.json) accepts
all twelve native stages and the checksum-bound return after strict setup reuse.
The original failed native journal and two corrected local reviewer journals stay
intact. The recovery cost about $0.075 before small charges (<$0.105 with reserve);
VM independently TERMINATED, October 21 retention unchanged. Operational debugging
proceeded directly without another approval handoff; no scientific tuning occurred.

Fixed dev4 vectors/graph with CPM yield pre/post weighted R95 5.3990/4.6171%, versus
RB 1.8763/4.2909% and dev3 learned ten-depth 5.3911%. The +0.3261-point post gain
fails the frozen +0.5 keep threshold. Modify the refinement hypothesis; do not
promote or search resolutions. Four high-purity parents fragment, one new target
gains. The harmed seed pairs all have the same admitted genome label, disjoint
whole-contig source spans and different complete proteins. Their repeat counts
are all 2; highest versus second-highest selection cannot explain these losses.
Marker family membership is not proof of universal single-copy behavior; exact
copy/call biology remains unresolved. No fatal feature/graph/evaluator bug was
identified by the scoped audit, without claiming optimality or exhaustive absence.

The one MetaBAT2 cvExt reference reaches 8.5493%, 16 targets >=50% and 5 >=90%:
a material +3.1503-point feasible recovery gap over the best own output on this
assembly/truth/metric. This is useful evidence beyond ranking a weak prototype;
its different eligibility/variance assumption prevents a component-cause claim.
No broad external campaign follows. Full DNA/origin/length/eligibility populations,
provided-reference denominators and 3.3034% N-quarantine remain.

Next selective decision: one local restore-only parent-versus-existing-child
acceptance control, following a marker-copy reliability audit and prospectively
frozen label-free rule. Existing RB/CPM proposals avoid new fits, marker scans or
Leiden execution; $0 new cloud compute. This tests a demonstrated harmful stage
without returning to a mandatory tiny-feature campaign. Oral-GSA confirmation is
still frozen/unacquired, with independent population/truth/overlap/cost admission.
