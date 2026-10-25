# D015: a coherent prototype upgrade with selective ablations

Current handoff: [E021 completed E009-only review](../../experiments/E021-frozen-sequence-hybrid/comparison-review.json) is MODIFY: weighted R95 7.3058 -> 7.8175%, but >=90% targets 7 -> 6; oral/skin unrun and original joint KEEP unmet. [Inspection/costs](../../experiments/E021-frozen-sequence-hybrid/inspection-observed.json) verifies shutdown, restore-only recovery and temporary GPU cleanup. Next implement a reliable marker-informed cross-contig learning block locally using retained caches; no automatic GPU/community run or storage renewal. [Operations](../../experiments/E021-frozen-sequence-hybrid/OPERATIONS.md#exact-following-prompt) owns the exact next scope and October 28 boundary.

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

## Owner clarification and E012 prospective acceptance control, 2026-10-17

The previous "do not promote" recommendation was too rigid. Preserve E011's failed
numeric keep criterion, but **retain CPM as the provisional working development
grouping direction**: with fixed vectors/graph it materially improves pre grouping
and its harmful marker stage is separately identifiable. RB is a historical
matched diagnostic control, not a recommended return path. No resolution grid or
claim to outperform dev3 follows; target-level coverage remains relevant alongside
the aggregate. Practical effect thresholds are decision aids rather than biology
or significance tests.

Markers remain a strong product priority supported by the completed source/thesis
reviews. Adjust the confidence and context with which repeated calls are used;
do not equate family membership with universal single-copy specificity or allow
duplicate removal alone to justify a destructive split. [E012](../../experiments/E012-marker-acceptance/README.md)
freezes one label-free graph CPM-gain acceptance rule for exact retained RB/CPM
parent/child alternatives, with no regeneration, grid or new runtime science.
A separate retained-PAF gene/domain audit diagnoses loci, replicons, copy/call
specificity and possible duplication; truth never selects an alternative. This
local control is authorized now, with engineering tests before one matched
comparison. A null all-veto outcome can demonstrate protection only. Neither
success nor failure decides a feature family or validates generalization.

## E012 observed protection and next coherent upgrade, 2026-10-17

[E012](../../experiments/E012-marker-acceptance/review.json) completed the authorized
local comparison without cloud spend. The frozen graph-gain guard accepts 16/18
RB splits (R95 4.5232% versus 4.2909%) and 0/12 CPM splits, exactly retaining CPM's
5.3990% parent versus 4.6171% old children. CPM restores four harmed targets but
forgoes the ASV300.2 gain; no extra CPM marker recovery or generalization follows.
Keep CPM as the working direction and the guard as a safety comparison. This
preserves the failed E011 threshold rather than changing it retroactively.

Gene/domain-level evidence now distinguishes strong calls at distinct provided
loci from a partial overlapping-locus call and barely passing/partial additional
conflict evidence. Draft reference records do not prove biological replicons;
paralogy, panel specificity and reference-assembly purity remain unresolved. Do
not blacklist the affected families from truth or claim all duplicates are false.
The old hard count-to-K/cannot-link assumptions and conflict-removal acceptance
were implemented as documented choices; their quality assumptions failed here.
The seed-count prose discrepancy is irrelevant to these four k=2 cases.

Next implement one coherent marker refinement upgrade with call reliability,
label-free marker-quality proxies and measured parent-depth/composition context,
retaining whole-parent alternatives. Graph gain informs that model without being
a universal veto. Keep encoder/vectors/graph fixed for one selective cached
comparison; no default factorial campaign, new architecture or external expansion.
The [following prompt](../../experiments/E012-marker-acceptance/OPERATIONS.md#exact-following-prompt)
permits local implementation and one prospectively frozen cached comparison.
Oral-GSA and its independent admission stay separate; October 21 review unchanged.


## E013 authorized coherent refinement and development breadth, 2026-10-17

The owner authorizes one local [E013 implementation/comparison](../../experiments/E013-marker-quality/README.md)
on retained CPM parents. It combines call reliability/physical-locus handling,
conservative median-family seeding, supported soft spherical proposals and a
whole-parent quality/context comparison. No family is blacklisted from truth,
no graph/objective/seed or encoder changes, no new marker search or data acquisition.
The frozen protocol owns exact algorithms/defaults and directional keep/modify
criteria before changed outcomes; the two preserved CPM refinement controls stay.
This is a coherent refinement bundle, not another compulsory per-ingredient study.

Owner concern is recorded as a hypothesis, not a verdict: refinement could help
other communities even if E009 gains are absent; the neural training/objective may
also limit performance. Do not perfect grouping on this assembly indefinitely or
require that perfection before justified representation/training work. Existing
reviews support more varied/all-positive real-window learning, explicit
composition/abundance reconstruction, false-negative caution, positive-only
teacher methods and sequence-context models as serious later candidates.
A reconstruction-regularized multiview composition/depth objective is the first
training upgrade to assess for preparation: it complements the current contrastive
loss and real-window encoders without treating markers as unquestioned hard
negatives or requiring a large pretrained backbone. It is not implemented or
established causal here. Revisit this ranking after E013 and wider-data admission;
retain GLM/context-attention and teacher approaches as alternatives rather than
automatic additions or a factorial campaign.

If this single inspected community limits the decision, move to prospective
additional-data admission alongside a coherent training design. Keep oral-GSA
fixed, including its sequence-only/depth-absent limitation; require independent
source/genome/replicon/taxonomy/overlap/truth and separate acquisition/cost admission.
Additional read-depth assemblies may later be valuable, but mapping ten samples
to one assembly is not ten independent assembly tests. No such new work or paid
resource/retention change is authorized in this block. October 21 review remains.

## E013 outcome and next training/data block, 2026-10-17

The [completed E013 comparison](../../experiments/E013-marker-quality/review.json)
passes its prospectively frozen directional criteria: full-reference weighted R95
**5.7388%** versus protected CPM **5.3990%**, 9 versus 8 targets >=50%, one target
gain and no loss. It selects five retained splits, preserves the four formerly
harmed parents and admits the useful ASV300.2 split. All accepted splits reduce
the fixed CPM objective. This is evidence against a universal graph-gain veto,
within this inspected community; it does not invalidate graph information.

**Keep E013 provisionally as the research refiner around CPM.** The quality score
separates candidates here; all twelve retained alternatives pass context signs.
There is no supported new median-seeded community proposal, so that route has
engineering coverage without a demonstrated recovery contribution. Panel/lineage
proxies are not calibrated MAG estimates. The bundle adds 424,264 unassigned bp,
including 342,037 confirmed bacterial bp, and slightly lowers restricted B3
recall/F1. Dev3 still has more >=50%-recovered targets, MetaBAT's accepted single
reference remains higher, and mixing/fragmentation persist. Preserve the rule and
all alternatives rather than tuning away those trade-offs after seeing truth.

**Do not perfect refinement/grouping on E009 before improving training.** The
modest single-target gain is the protocol's reason to broaden evidence. The
strongest next block is prospectively chosen additional-community admission and
coherent training implementation in parallel. This builds on existing reviews
rather than restarting a field review or a tiny-feature campaign. The accepted
[E011 window audit](../../experiments/E011-cached-grouping-reference/audit.json)
already found that 91.02% of 13,554 training parents have coincident fixed-pair
coordinates and that only 15.22% of eligible parents train. Correct real-window
sampling can still offer limited augmentation/exposure. It is not an implementation
bug or proof of the dominant causal bottleneck. The accepted E010 inner training
loop's 18.265 s/20 epochs makes a cached later training test plausible, but is not
an affordability guarantee for larger data or evidence of inadequate learning.

Prioritize a **reconstruction-regularized multiview composition/depth candidate**
with more varied DNA positives and use of available positive views. Reconstruction
can require an embedding to retain input information beyond pair agreement;
different fragment exposure addresses the narrow fixed view set. It can also
preserve nuisance/lineage-independent variation or strengthen depth shortcuts,
so the precise targets, normalization, weights and depth-absent behavior must be
declared/tested before new scores. Use one coherent implementation and at most
one selective loss/view control that could change the design. Positive-only/teacher
objectives, false-negative handling, pretrained/context representations and
residual grouping/merging are serious alternatives, not automatic additions.
Marker-aware training, taxonomy and ensembles remain unjustified in this block.

Retain the original oral-GSA choice. Planning-only HEADs find four frozen files
totaling 2,445,246,434 bytes; no bodies were downloaded and no truth admitted.
Source/reference payload beyond these is unknown. A future local block can admit
checksums, sample/source/genome/replicon/molecule/taxonomy joins, overlap, coordinates
and duplicate-safe full-reference denominators with streaming/indexed readers,
while implementing/tiny-testing the training candidate. Do not fit/score a community
until its truth/resources and the frozen candidate/protocol pass their admissions.
Oral GSA tests sequence-only transfer without assembly errors; it cannot establish
depth benefit or pretraining-independent generalization. Data inspected for design
become development data, requiring later prospective confirmation for broader claims.
E013's [following prompt](../../experiments/E013-marker-quality/OPERATIONS.md#exact-following-prompt)
owns the proposed local block. Existing storage review is still October 21;
no cloud action, paid work or retention extension follows from this recommendation.

## E014 implemented bundle and source admission, 2026-10-18

The [local E014 block](../../experiments/E014-multiview-reconstruction/review.json)
implements the recommendation directly, preserving dev3/dev4 and E013 science.
The [prospective design](../../experiments/E014-multiview-reconstruction/design.md)
uses full-parent plus four varied real crops, every available positive,
parent-balanced exposure, composition/depth reconstruction and independent depth
dropout. The composition/depth encoder widths and unit inference/grouping geometry
remain; measured parent means are not crop coverage. Sole CPM/E013 downstream
defaults remain fixed. SupCon/COMEBin/VAMB evidence informs this coherent bundle,
without claiming their equivalence or a causal win for each ingredient. A larger
network is not the intervention. False negatives, chimeric parents, nuisance
reconstruction and depth shortcuts remain hypotheses for selective diagnosis.

Installed native Mac engineering, exact reload/legacy-array parity, wheel/sdist,
real marker/graph/refinement/export contracts and the serial tiny DAG pass. A
fresh Linux/full-scale runtime has not passed; there is no changed community
result. Preserve the failed Mac allclose and all acquisition/build/workflow/source
audit failures. Operational repairs used fresh recorded attempts and verified
reuse, including the unrelated oversized compressed setup member; no data DAG,
accepted science, download or cloud run was repeated.

The quartet and separately approved setup provide complete bytes: every nonempty
GSA locus matches source sequence; all799 oral-positive provided genomes contribute
full denominators, including two absent from GSA. Source-blind IDs retain all DNA
and account for the two empty original records. Cross-genome identical queries,
shared reference records and unannotated molecule/host context remain explicit.
The new durable AGENTS guidance separates known simulator origin from unique
sequence support and keeps origin-bearing IDs/reverse joins out of model paths.

**Keep the dev5 candidate frozen and finish oral truth/evaluator admission next.**
That is an evaluation-integrity dependency, not another architecture review or
requirement for perfect grouping. Define/test source-origin versus identifiable
support, ambiguity/non-ACGT handling, full-bin purity, coordinate unions and all
provided denominators before community outcomes. Exact/reference and species
overlap limit unseen-genome claims; unknown historical/pretraining inventory alone
does not invalidate a paired comparison. The currently conservative protocol has
not admitted oral truth, so the conditionally authorized three-fit comparison
did not run. No performance hypothesis has failed or succeeded from engineering.

The [first comparison protocol](../../experiments/E014-multiview-reconstruction/comparison-protocol.json)
uses E009 dev5 versus retained dev4/E013/dev3, and oral sequence-only dev4 versus
dev5. Only three new fits, no new external reference or compulsory ablation grid.
Keep all pre/post alternatives for a cheap refinement contrast; the sole prepared
optional loss control is zero reconstruction if a later outcome makes that
decision consequential. Oral lacks assembly errors and admitted measured depth,
so it cannot establish depth or read-assembly benefits. A later additional-data
confirmation must be prospective; inspected outcomes used for design become
development evidence. October21 storage review is unchanged.

Later E014 follow-through, before community outcomes: do not mistake inability to
prove sequence uniqueness for absence of valid publisher origins. A separately
[frozen provided-origin policy](../../experiments/E014-multiview-reconstruction/oral-truth-policy.json)
and tested adapter count localized ACGT origin support, every bin/reference base,
duplicate-safe source unions and all799 targets. Every model DNA/reverse source
row and mask independently passes review; [admission](../../experiments/E014-multiview-reconstruction/oral-truth-admission.json)
is specifically for that oracle.49 known-shared queries remain flagged, with a
predeclared mask sensitivity. Unique-sequence support, biological host annotations
and unseen-genome claims remain unadmitted. This explicit prospective scope
resolves the earlier hold without silently weakening or rewriting the conservative
journals. It allows the one paired development comparison after native/financial
gates, keeping the candidate fixed and its two dataset truth modes separate.

E014 native release, 2026-10-18: the same frozen bundle now passes all 15 Linux
gates, including 25 installed product tests, and the [authorized three-fit DAG](../../experiments/E014-multiview-reconstruction/native-observed.json)
is progressing under the verified original limits. No new scientific rule, model
or architecture choice follows from native readiness; compare the complete outputs
after shutdown before deciding whether to keep or selectively modify the bundle.


## E014 mixed bundle result and one selective loss control, 2026-10-19

The [frozen comparison](../../experiments/E014-multiview-reconstruction/comparison-review.json)
passes all native/input/reload/geometry/marker/DNA contracts, with independent
TERMINATED and checksum-bound collection recovery. Science source858b7cc and all
prior comparators/failures remain unchanged. The collection-cap failures are
delivery failures, not an invitation to replay accepted science. AGENTS now makes
compressed/uncompressed evidence working sets, lossless aliases and native-versus-
local/backup scope explicit.

E009 dev5 post R95 is5.5196% versus retained dev4/E0135.7388%; oral provided-origin
post is6.2432% versus5.7242%. Never pool the two truth scopes. E009 target>=90%
increases2→4, bacterial5NN72.5882→80.5066% and restricted F1 improves; oral short-
contig neighborhoods improve, while long-contig/bp-weighted geometry, grouping
recall and unassigned-DNA trade-offs remain. The improve-both criterion fails;
classify **modify**, without calling the coherent bundle universally better or
rejecting its feature families. Native correctness is not optimality.

Hold CPM/E013 provisionally: it adds3.1547points on oral dev4 and0.6795points on
oral dev5 relative to their parents, with no per-target losses in those pairs.
It is not uniformly best: oral dev5 old refinement has6.3443% weighted R95 versus
E0136.2432%, with fewer50/90% targets. Do not choose a truth-assisted per-bin
oracle or tune the selector to E009 now.

Choose **one joint zero-reconstruction condition** next, already contemplated
before outcomes: both reconstruction weights0, all view/exposure/positives,
encoder+decoder initialization, measured-depth/dropout, seed/schedule and downstream
policy held fixed. Reconstruction may retain nuisance/length signals; broad
exposure and co-genomic false negatives are serious alternatives. This control
can change whether the reconstruction block stays, without requiring a factorial
campaign or proving the other ingredients causal. Pure grouping tuning, a larger
network and extra mature-tool runs are lower-priority alternatives here. Keep
them deferred rather than declaring them scientifically excluded.

Proposal: two new matched fits with complete retained caches and accepted results
reused, new$2 ceiling,2h cumulative/2.25h STOP, existing8vCPU/32GiB/300GiB,4threads/
26GB/20GiBextra/25GiBreserve/2GiBreturn. Expected70–100min includes setup/collection,
using measured E0096.4min/oral38.2min training-rule costs; fresh native/financial/
retention gates remain. No current authorization or fit follows from this record;
[the next prompt](../../experiments/E014-multiview-reconstruction/OPERATIONS.md#exact-following-prompt)
requests the separate scope. Both inspected communities now count as development.
Later independent confirmation needs a prospectively frozen additional-community
protocol and source/overlap/truth/cost admission. Original oral choice and E014
admission stay historical evidence. October21 storage review remains.


## E015 matched reconstruction control authorization, 2026-10-19

The owner now authorizes [E015](../../experiments/E015-zero-reconstruction/README.md)
under a separate conditional$2. Preserve both decoder heads and their initialization/
RNG use; zero only the two loss coefficients, reusing retained banks and all
accepted evaluations. A narrow research train-function adapter admits those two
configuration overrides without altering the original view metadata or dev5 package;
its remaining statements have an AST equality contract. This is the already
contemplated decision-changing control, not a compulsory one-feature campaign or
attempt to optimize both datasets by a weight grid. Credit abundance permits
larger scientifically justified work later; keep this treatment interpretable.
New loss/source/protocol/criteria and fit-to-cap collection are frozen before any
new outcome. Both communities remain development; additional untouched confirmation
requires prospective admission. Existing$2/2h/2.25hSTOP and October21 remain.


E015 native follow-through: clean pushedb259dca passes7new Linux gates and releases
the frozen two-fit DAG at10:33:30UTC. An operational config-key failure before all
science/gate children remains preserved; a tested factory repair/fresh attempt uses
the same10:25VM-start clock without extension or accepted replay. At10:37E009-zero
reaches epoch12/20 with E014-matched exact parent/view/dropout counts, under fresh
process-bound shutdown and8100sSTOP. This is healthy execution, not a quality result.
Inspect complete outputs only after independently verified shutdown/delivery.

## E015 science reported complete, delivery repair pending approval, 2026-10-19

The [stopped-phase receipt](../../experiments/E015-zero-reconstruction/inspection-observed.json)
verifies science-DAG/reuse-after exits 0 and the expected process-bound shutdown,
with provider TERMINATED at 11:38:44.496 UTC. Original FAILED status is preserved:
the isolated collector could not import its sibling helper, before creating an
inventory/archive. The new two-arm checkpoints/partitions/graphs and individual
rule resource records remain on stopped disk and are not independently admitted.
Reconstruction's keep/modify/abandon decision remains unresolved; delivery status
is not a model-quality result and does not justify another architecture change.

The collector repair changes only adjacent helper-path admission and passes real
isolated checkout/transferred CLI archive/alias/refusal contracts. In-process tests
had hidden that path failure; AGENTS now requires the exact isolated subprocess
layout. [Collection-only recovery](../../experiments/E015-zero-reconstruction/collection-recovery-plan.json)
is prepared with original clean science source b259dca, four hash-bound helpers,
passed-proof/byte reuse, a fresh held-parent watcher and 30-minute/45-minute STOP.
No training, inference, reader replay, marker redetection or graph rebuilding.
Portable byte/journal/clock tests pass; Linux/root execution remains unrun.

The current inspection prompt prohibits waking for missing evidence and the
original clock expired. Request explicit approval for that new bounded wake,
then review only the new outputs with unchanged E009/oral truth scopes, denominators,
N-quarantine, populations and original criteria. Up to $0.65 additional fits the
remaining original E015 $2; no larger dollar envelope or storage extension is
needed. October 21 remains. Independent confirmation still needs a new untouched
prospectively named input/protocol and full source/truth/overlap/cost admission;
neither inspected community becomes confirmation by repeating it.

Same-task owner follow-through: an explicit reply now approves the prepared
collection-only wake/local review, with a fresh30-minute clock/45-minute STOP and
up to$0.65additional within original$2. Fresh financial/native transfer/supervision
gates still precede release; no new science or retention extension is authorized.

## E015 mixed loss control and next positive-only candidate, 2026-10-19

The [independently reviewed E015 outputs](../../experiments/E015-zero-reconstruction/comparison-review.json)
retain exactly the two zero reconstruction coefficients, original construction/
seed/RNG, all20epoch parent/view/dropout counts, transforms, inputs, native geometry
and fixed CPM/E013. All gates/rule/reload/full-DNA/export contracts pass. The
isolated collector failure stays FAILED; a separately approved source-bound
collection-only wake recovers every compact member without repeating science.
Final VM TERMINATED14:00:31UTC; both boots/run disks/export/shared stopped gap total
~$0.639/<$0.80 with reserve. October21 review is unchanged. No default/model changed.

Zero lowers E009 R95 **5.5196→5.3329%**, while oral post rises **6.2432→6.5548%**.
E009 gains one>=50% target, slightly better bacterial5NN/B3 and less unassigned
DNA; oral gains two>=50%/one>=90% targets and better assignment. Oral parent R95,
bp-weighted neighborhoods and post B3 worsen, with a larger fixed-refiner lift.
Apply **modify**: neither original universal keep condition passes. Keep original
reconstruction/defaults provisionally as the implementation anchor and zero as a
useful retained alternative; do not choose a policy separately for each dataset
or retune coefficients. Full denominators/N-quarantine/known-shared sensitivity and
all per-target/length/origin/marker/eligibility populations remain. All eligible
parents are exposed, but zero removes the reconstruction signal for2,333E009/
13,716oral parents with no usable positive crop; they still provide negatives.
This is a scoped treatment consequence, not a silent data exclusion.

**Choose one coherent positive-only online/target multiview training candidate.**
The current instance-discrimination objective treats every distinct parent as a
negative, including co-genomic contigs. That is an explicit unresolved assumption,
not a demonstrated cause of these losses. Removing reconstruction alone did not
produce a strong common direction; another weight grid is lower value. The
existing [source review](../evidence/2026-09-30-binner-design-review.md) already
identifies McDevol's BYOL route as a serious alternative. A targeted primary
refresh reads the [BYOL paper abstract](https://arxiv.org/abs/2006.07733v3) and
[McDevol author README](https://github.com/soedinglab/McDevol): an online network
predicts the representation of another real view from a slowly averaged target.
This is a mechanism reference, not reproduced tool performance, a complete new
code audit or permission to execute McDevol. Its pretrained composition/coverage
sampling choices are distinct from our retained measured-parent inputs.

A small predictor, stop-gradient target, moving average and noncollapse contracts
are necessary parts of that single learning bundle; do not demand a separate
performance study before implementing each. Keep current encoder widths, real
parent/crop bank, full exposure, reconstruction1.0/0.1, measured-parent depth,
depth dropout, seed/schedule, unit inference geometry and CPM/E013 initially fixed.
No larger network, taxonomy, marker-aware training, context model or ensemble is
automatically justified. Resolve exact algorithm/defaults through targeted source
checks before changed outcomes; preserve all intermediary/checkpoint evidence.

Conservative false-negative masking or cross-contig mining remains serious, but
the current oral native5NN origin agreement is only20.6%; unfiltered pseudo-
positive links would mostly join different provided origins. A reliable confidence
rule is not admitted. Positive-only learning preserves verified parent positives
while testing a different loss assumption. Collapse, weak discrimination,
chimeric/weak views and sequence-only behavior are real risks; test actual gradients,
target updates/buffers, exposure, variance/effective rank and exact reload rather
than assuming a teacher guarantees success. This is a prospective hypothesis.

The [following prompt](../../experiments/E015-zero-reconstruction/OPERATIONS.md#exact-following-prompt)
proposes one local coherent implementation and one conditionally authorized new
two-fit development comparison, reusing all accepted baselines without rescoring.
Proposed new$3, existing8vCPU/32GiB/300GiB,4threads/26GB/20GiBextra/25GiBreserve/
2GiBreturn,4h cumulative/4.25hSTOP; forecast~1–2.5h, maximum ordinary-rate envelope
~$1.74 before any required revision. It remains a proposal until the owner sends
that prompt. Source/data/native/credit/price/headroom/original-retention gates
precede release; no resource increase, automatic extension or retention change.
Both communities are development. Freeze a genuinely untouched additional input/
protocol and its source/genome/replicon/taxonomy/overlap/truth/full-denominator/
length/depth/cost admission prospectively; acquire no confirmation payload here.


## E016 coherent positive-only candidate and recovery-gap priority, 2026-10-20

The owner authorizes [E016](../../experiments/E016-positive-only-multiview/README.md)
local implementation and one conditional new$3 two-fit development comparison.
[The design](../../experiments/E016-positive-only-multiview/design.md) freezes one
online-only predictor/stopped target/cosineEMA bundle, preserving dev5 encoders,
real views/full exposure/measured-parent depth/reconstruction/geometry/CPM/E013.
It avoids unvalidated cross-contig positive links; no evidence yet proves that
co-genomic negatives caused earlier losses. Real tiny gradient/EMA/buffer/collapse/
reload/graph/marker/export/member contracts pass. Native scientific utility and
full runtime/source/headroom/affordability gates remain pending. Preserve all
accepted comparator outputs, source freezes and failed journals without rescoring.

The owner's additional recovery-gap concern changes the interpretation priority,
not the frozen treatment: judge whether the next block should add information or
redesign grouping/training more broadly, rather than automatically continuing
small loss tests. The completed reviews keep window/context-TNF, frozen GLM/head/
hybrid representations, reliable marker-aware learning and raw/depth-informed
probabilistic grouping serious. E003's grouping benefit and short-neighbor loss
remain counterevidence to simplistic GLM verdicts. Marker call/repeated-locus audits
caution against naive cannot-links; neither a Transformer label nor adding every
successful-tool ingredient identifies the useful next mechanism. Prefer a coherent
broader block if E016 remains weak and retained diagnostics identify a substantive
limitation. A narrow follow-up earns its place only if it resolves an uncertainty
that can change that design. Do not declare which cause won before outcomes.

[Skin pooled GSA](../../experiments/E016-positive-only-multiview/confirmation-plan.json)
is frozen as the next untouched outcome input: ten HMB skin samples, sequence-only
pooled GSA, a distinct source group with unknown exact/near genome overlap. Only
1.73MB public metadata inspected, no DNA/reference/read body. Four files total
2,137,995,181 HEAD bytes; shared source setup2,467,407,842bytes. It is not admitted
unique-sequence truth, genome independence, assembly-error or ten-depth evidence.
Actual sample/source/replicon/taxonomy/full-denominator/overlap/truth/cost admission
is still required before separately authorized confirmation. October21 review and
existing disks$31.20/month remain, with no automatic retention/resource change.


E016 same-task native follow-through: [source2cfefa3 release](../../experiments/E016-positive-only-multiview/native-observed.json)
passes all ten Linux runtime/source/input/tiny/export/collector/timing gates on
existing VM/disks, starts the sole two-fit comparison at00:36Copenhagen and shows
actual E009 epoch/view/EMA progress without collapse refusal. Fresh current-boot
watcher and04:46providerSTOP verified. Keep it supervised rather than polling the
long job. Final outcome/gap-closure/architecture recommendation remains pending
independent completed-output review; this execution is not a quality claim.
No extra budget/resource/retention, external tool or confirmation DNA follows.


## E016 reviewed recovery gain and next information-aware grouper, 2026-10-20

[The completed comparison](../../experiments/E016-positive-only-multiview/comparison-review.json)
and [inspection](../../experiments/E016-positive-only-multiview/inspection-observed.json)
verify all ten Linux gates/twelve science rules+final target, native exact reload,
unit geometry/neighbor/cache/selector/DNA contracts and221return members/two exact
aliases. The VM is independently TERMINATED; no wake or scientific replay occurs
in review. All older source/results, native release snapshot and failed Mac/local
journals remain. Core frozen diagnostics close9.22min,4.840GBsampled RSS/2.324GiB;
final sealing/records remain within the same1h/4GiB envelope.

**Keep the positive-only bundle as a provisional recovery-focused research anchor.**
Frozen E014-referenced numerical conditions pass: E0095.5196→5.8219%, oral-origin
6.2432→6.7719%, oral gain+0.5287pp, >=90%targets4→4/30→34, full-population contracts
and noncollapse pass. E009 gains1,677,003bp (17 targets gain/6 lose, any-passing22→21), oral11,013,185bp
(55gain/19lose), with full156/799provided denominators/N-quarantine/known-shared
sensitivity intact. This does not promote a product default, prove a false-negative
cause or establish uniform improvement. E016 also exceeds retained E015 recovery
in both scopes, but only~10% of the E014→MetaBAT2 E009 gap closes. E0165.8219% still
trails8.5493%, and exceeds dev4/E013 by only0.0831pp.

The original population safeguard requires complete, visible accounting; it does
not authorize hiding trade-offs behind KEEP. E009 bacterial5NN falls80.51→72.63%
(bp-weighted84.60→82.05%), oral20.43→17.86% (bp-weighted22.25→20.68%). E009 short-bin
precision worsens while >=10kb grouping improves. Unassigned DNA rises0.723→2.376Mb/
7.595→11.584Mb, with confirmed bacterial E009 unassignment259,869→633,285bp. Oral
B3F1 falls31.21→30.68% despite higher recall and recovery. Full length/origin/
marker/eligibility/unknown/non-target/excluded/unassigned cells remain. Online/
target ranks32.83/30.56E009 and26.75/26.58oral rule out the predeclared catastrophic
collapse, not weak discrimination. Target/predictor/EMA saved-state and all20epoch
exposure checks pass; no full gradient trajectory or initial community tensor
snapshot exists. Original Mac portability tolerance is not weakened.

Most decision-relevant: oral parent/old/E013 recoveries are4.6429/5.0723/6.7719%.
The unchanged E013 selector adds44.35Mb over the parent,18target gains/1loss, while
the candidate parent itself is worse than E014's5.5638%. E009 refinement selects
two alternatives with no R95 change. Better final recovery therefore does not mean
uniformly better local embeddings; genome-scale grouping and biological selection
remain important. Do not select the old/current refiner separately per genome.

**Choose one coherent length-aware, multi-evidence grouping module next, holding
E016 learning fixed.** Use the retained learned representation alongside raw
composition and measured parent means, with explicit absent-depth/length reliability,
reliable genome cores and conservative short-contig recruitment/unassignment.
Keep one scalable path and initially retain CPM/E013 as the fixed context where
applicable. Any necessary replacement is declared in the new prospective bundle,
not hidden in a resolution/threshold grid. Preserve all alternatives and all DNA.
No community grouping or architecture change runs in this inspection.

This is broader than another marker-split guard or loss coefficient. It addresses
how the system uses available evidence to assemble genomes: current initial graphs
use only unit embeddings and one global node-density rule; raw composition/depth
are available downstream mainly for refinement. Direct affinity/reliability and
long-core/short-recruitment contracts can protect information the embedding blurs
and reduce fragmentation without forcing ambiguous DNA. The retained MetaBAT2
run shows headroom on the same assembly and ten mean-depth inputs; it does not
prove its specific affinity formula is causal or that our features are sufficient.
The E001/thesis reviews also show similar neighborhoods with different recovery.

Serious alternatives, weighed against this decision:

| Route | Evidence and limitation | Priority now |
| --- | --- | --- |
| Multi-evidence, length-aware grouping + conservative recruitment | Large oral parent/refiner interaction, short precision/assignment losses, existing raw/depth signal and retained same-input reference gap; no guarantee of complete separation | **Next coherent block**, using fixed E016 caches and one prospective matched comparison |
| Window-context TNF/compact attention | Adds local composition arrangement lost by whole-contig TNF; supported by reviewed CompleteBin source, but its whole-tool win combines pretraining/views/grouping and local tokens can be noisy on short DNA | Leading later information upgrade if the new grouper still encounters mixed/indistinguishable affinities; no assumption a larger network itself helps |
| Frozen GLM/TNF/depth hybrid | External sequence prior can complement composition. E003 improved fixed-fragment grouping while hurting short-neighbor agreement; it never compared our trained/hybrid whole-binner or proved a family verdict. E002's CPU projection is old laptop planning, not a cloud veto | Serious alternative, not rejected for cost or old threshold alone. Full native inference/cache/strand/token/runtime/license/overlap and resource admission still needed; no blind bulk extraction/GPU provisioning now |
| Reliable marker-aware learning | Current oral refinement lift supports keeping marker information, while E011–E013 reveal partial calls/same-genome distinct loci/replicons/panel limits | Keep cached marker quality/refinement. A new training-link rule must establish reliability; same-family duplicates alone are not universal negatives |
| Narrow loss/EMA/resolution follow-up | Could isolate a bundle cause, but does not directly address the observed genome-assembly/short-DNA decision and would prolong small controls | Lower priority now; no default grid, causal dissection campaign, larger MLP or extra external tool |

A targeted primary refresh reads author SemiBin grouping source at
[b06c7d53bef28f46cb7030845913279f94dfa6bf](https://github.com/BigDataBiology/SemiBin/blob/b06c7d53bef28f46cb7030845913279f94dfa6bf/SemiBin/cluster.py):
`run_embed_infomap` combines learned/kmer edge evidence and length-weighted graph
partitioning; its non-combined coverage path's `cal_kl` needs means **and variances**.
Our accepted ten means cannot silently supply that recipe. The read is18,749bytes,
SHA256`e1e5690d23f23c0ce5fb5875ca5c8d2d1374df1116e7bcc280b2bd4735e95ee0`, dated
October20. This supports information-use design, not source parity or reproduced
performance. Reuse the completed MetaCAT/MetaBAT2/context/GLM/thesis reviews;
no new whole-tool campaign, source vendoring or mandatory ingredient list follows.

Next local work should resolve the actual affinity/reliability/core/recruitment
algorithm with targeted primary sources, implement/test real tiny readers/export/
cache/missing-depth/marker boundaries, then freeze one candidate and a cached
matched comparison. Use no truth K, target-specific thresholds, native benchmark
labels or per-bin oracle; preserve E016/CPM/E013 as the comparator. A one-hour local
review here is not permission for another community grouping. New execution needs
new source/protocol/native/headroom/credit/price/cost and explicit budget admission;
prior$3 does not carry. Resources should serve likely recovery value, not an
arbitrary preference for the smallest run. This is the strongest next judgment
under current evidence, not a proved globally optimal architecture.

The frozen skin choice remains untouched/unacquired. Admit actual sample/source/
genome/replicon/molecule/taxonomy joins, exact/near and reference/pretraining overlap,
full duplicate-safe denominators including zero-origin targets, ambiguity/competitive
sources and separately named unique-versus-provided-origin truth before confirmation.
GSA lacks assembly errors and admitted GSA-contig depth. Freeze one candidate and
comparator before skin outcomes; source/acquisition/cost/retention approval remains
separate. Both currently scored communities remain development.

October21 storage review remains; current gate expires00:00Copenhagen. Existing
stopped disks cost$31.20/month. Read-only inventory finds76liveStandard objects/
5.3704GiB; a proposed additional seven days throughOctober28 crosses the October25DST switch (169hours):~$7.087disks+
$0.025liveobjects, plus reserve for metadata/operations/unlisted versions. Propose
an explicit new$8storage-only ceiling after fresh coverage/inventory checks; **no
extension is enacted here**. Preserve accepted data and audit backup omissions
before proposing any later cleanup. The [next exact prompt](../../experiments/E016-positive-only-multiview/OPERATIONS.md#exact-following-prompt)
separates that prospective approval and local implementation from a later paid run.


## E017 local information-use implementation, 2026-10-20

The owner sends E016's next prompt and approves the separate $8 storage-only
interval after fresh checks. [E017](../../experiments/E017-information-aware-grouping/README.md)
implements the coherent length-aware core/recruitment block around fixed E016
learning. Learned/raw composition and observed parent means inform one sparse
core graph, the sole CPM density rule, fixed profiles and conservative single-pass
recruitment; unchanged E013 follows. All core/recruited/old/post alternatives and
all DNA survive. No community grouping, score, encoder change, new data, external
run or VM start occurs. [Design](../../experiments/E017-information-aware-grouping/design.md)
owns the prospective heuristics, alternatives and failure risks; [local evidence](../../experiments/E017-information-aware-grouping/local-evidence.json)
owns actual paths/failures and pending Linux contracts. This is implementation,
not evidence that the recovery gap has closed.

The owner's length concern is well founded for the named native reference.
Retained MetaBAT2 2.18 uses main minContig 2,500 bp, allowed >=1,500, and separate
short recruitment from 1,000 bp by default (allowed >=500), plus depth filters.
Actual E011 counts are 9,812 large and 27,307 small candidate contigs, with only
102,650 small-contig bp recruited. E016's 500 bp learner population is different.
Keep native whole-tool/full-reference scores, explicit length/eligibility strata
and all unassigned/excluded DNA; do not retrospectively create an equal-cutoff
comparison or claim all strong tools exclude short DNA. E017 gives >=2,500 bp
contigs core authority while retaining >=500 bp recruitment and the original
learning population. This does not isolate the cutoff from other grouping changes.

The first exponential-only graph draft had no meaningful zero-edge rule for
forced distant neighbors. Inspection of a tiny separated fixture exposed that
contract issue; the final prospective background-agreement gate is frozen before
any changed community outcome. Initial sources/designs and local failed journals
remain. Tiny labels are explicit generated engineering cases, never benchmark
labels used to select a threshold. Full-width synthetic array timing informs only
resource planning; native approximation/profile/affordability still need gates.

The single next comparison can decide whether direct information use and
core/recruitment improve recovery with fixed learning, retaining four cheap paired
partitions. It proposes new $2, three hours/3.25-hour STOP and a 3 GiB complete
cache return, rather than another reduced community or loss grid. The measured
Mac kernel plus complete-evidence uncertainty justifies that clock; max gross
forecast is about $1.64. This execution remains separately gated/unauthorized.
The prior broad context/GLM/marker-learning alternatives remain serious if useful
information cannot be recovered by this module; no family is settled.

Fresh [storage admission](../../experiments/E017-information-aware-grouping/storage-admission.json)
resolves the October 21 review for the explicit 169-hour interval through
October 28 at 00:00 Copenhagen: forecast $7.61 including reserve, up to $8
approved, credit DKK 1,897.28 Available through January 12, 2027; VM still
TERMINATED. No resource/deletion/compute/retention action beyond that interval.
Inspect backup omissions before later savings; no accepted evidence is deleted.
Skin confirmation stays frozen and unacquired with the source/overlap/truth/
protocol/acquisition/cost dependencies stated in E016/E017. Both inspected
communities remain development. AGENTS now explicitly separates core cutoffs,
recruitment/native eligibility and prospective matched-cutoff controls.

A local reuse audit also found eight regenerable Numba compiler-cache entries
written beside the borrowed local NN library during early direct tests. They
remain recorded; protected source/library and scientific evidence did not change.
Subsequent work uses an owned JIT-cache directory, the actual worker refuses an
absent setting, and the corrected real tiny DAG/negative contract pass. AGENTS
now makes this distinction explicit: `-B` alone does not control third-party JIT
caches, and scoped source checks are not whole-prefix non-mutation proof.


## E017 reviewed mixed result and next ranking control, 2026-10-21

[The completed comparison](../../experiments/E017-information-aware-grouping/comparison-review.json)
uses fixed E016 learning/native vectors and all full denominators. E009 post R95
improves 5.8219 → 7.5284%, +9,465,205 recovered bp, 14 target gains / 9 losses,
>=90% targets 4 → 8. Oral provided-origin R95 falls 6.7719 → 4.9664%,
-37,609,955 bp, 23 gains / 45 losses, >=90% targets 34 → 21. Original MODIFY applies.
E016 remains the provisional research anchor; no per-community product routing,
new default, threshold tuning, family verdict or SOTA claim follows.

New unassigned DNA is substantial: 59.75 Mb E009 and 410.55 Mb oral, versus
2.38 / 11.58 Mb. Fixed learned 5-NN metrics remain exactly E016's. Oral's core
and recruited parents recover only 1.9045 / 1.9449%; E013 adds 62.94 Mb but cannot
restore the old result. Most large oral cores are mixed under the origin oracle.
Thus neither new information use nor conservative abstention uniformly helps.
Community, assembly, length distribution and depth availability differ together;
this does not isolate the presence of depth or prove missing sequence information.

One specific control can change the next design decision cheaply. Existing
profile-normalized distances are empirical per-bin spread proxies, not calibrated
cross-bin probabilities. E017 nevertheless ranks bins by those scores and applies
a runner margin before requiring agreement with >=2/3 core votes. The saved
label-free gate census finds an otherwise admissible candidate in 13,635 rejected
E009 rows / 14.46 Mb and 99,067 oral rows / 95.98 Mb. Counts alone are not expected
recovery: many new assignments could contaminate bins, and mixed cores/other
rejections remain. Removing the margin alone would expose only 39.24 Mb oral DNA;
competing winner rankings also matter.

Recommend exactly one **vote-led/profile-admissibility** control. Hold cores,
learned vectors, graph/weights, cached candidates/affinities/profiles, seed and E013
fixed. A unique existing >=2/3 vote candidate with >=2 distinct positive core
supporters and profile score <=1 may recruit; otherwise abstain. Do not rank
incommensurate profile scores across bins or impose their runner margin. Preserve
already accepted recruits, every alternative and all DNA. This is one coherent
acceptance hypothesis, not a label-selected cutoff/grid or a claim that original
E017 violated its implementation contract. The final source used a strict margin
(best ×1.5 < runner); the earlier design's <= shorthand is preserved as a prose
discrepancy, not silently changed in this review.

Weighing alternatives: another encoder/Transformer/GLM/context block could add
useful information, but cannot by itself resolve this demonstrated disagreement
between existing group-level evidence. Source reviews keep those routes live.
A new core objective/resolution campaign would confound the acceptance question
and discard cached reuse. The one ranking control is narrow because its observed
mechanism is concrete and its result can decide whether the veto protects purity
or wastes supported DNA; it is not a default demand to isolate every ingredient.
No guarantee is made that it restores oral recovery or fixes core mixing. Freeze
criteria before its changed outcomes, anchor both E016 and E017, and require
additional-data admission before a transfer claim.

The [next prompt](../../experiments/E017-information-aware-grouping/OPERATIONS.md#exact-following-prompt)
proposes one new $1 existing-VM control after local contracts/fresh gates:
15–35 minutes expected, one-hour cumulative / 75-minute STOP, four threads /
26 GB sampled RSS, 25 GiB reserve / 20 GiB extra / 2 GiB export. Maximum gross
forecast about $0.884 including reserve. Current inspection executes none of it.
Skin stays frozen/unacquired pending actual source/genome/replicon/molecule/
taxonomy joins, overlap/pretraining, duplicate-safe denominators, ambiguity and
unique-versus-origin truth, unchanged comparator/protocol and separate acquisition/
compute/cost/retention admission. The October 28 storage boundary remains.


## E018 authorization and robustness/data scope, 2026-10-21

The owner authorizes the previously proposed sole cached acceptance control and
permits a justified cost increase; the prepared $1 remains sufficient, with all
other one-hour/75-minute STOP/resource/retention gates fixed. E017 stays MODIFY;
E016 remains the broader development anchor. [E018’s assessment](../../experiments/E018-vote-led-recruitment/robustness-and-data.md)
records why the oral regression matters, the audited absent-depth mask and other
community/assembly/length/truth confounders. No demonstrated missing-depth coding
bug explains the difference; correctly implemented policies may still be poor.

Sequence-only oral adequately tests the fixed-input acceptance question, but not
current depth benefit or depth-enabled transfer. Fresh public metadata confirms
51.73 GB compressed reads; genuine pooled-GSA mapping has a rough $4–10 mapping-
only cost and uncertain 45–130 GiB serial peak. Those upper disk needs do not fit
the last free-space reserve. New input/training/downstream comparisons need their
own declared question and admission; old dev3 depth controls cannot establish
E016/E017 depth effects. Do not add mapping merely to remove an inconvenient
sequence-only failure. Revisit if this control leaves oral unresolved or before
a depth-specific design/default decision.

Defer a broad dataset campaign during this concrete control, not all validation
until competitiveness. Keep skin prospectively frozen and admit one additional
community at the next coherent-candidate milestone before robustness/promotion
claims, with all source/overlap/truth and separate cost/retention dependencies.
This remains development work; no external tool or confirmation payload is added.


## E018 negative matched result and next context information block, 2026-10-21

[Completed E018](../../experiments/E018-vote-led-recruitment/comparison-review.json)
passes all source/runtime/axes/cached decision/export/collection contracts and
applies original **ABANDON**: E009 7.5284 -> 7.2124%, oral 4.9664 -> 4.0538%;
>=90% counts 8 -> 7 / 21 -> 18. Same cores/graphs/profiles/native vectors and
E013, no new learning/index/detection or source repair during science. Native
VM is TERMINATED, actual quote ~ $0.139 / < $0.389 with reserve within $1.
The authorized cost increase was not needed. No prior budget carries onward.

Additional 14.46 / 95.98 Mb were assigned exactly as the label-free census, but
that did not translate to high-purity recovery. E009 has twelve small target gains
and one dominating loss: ASV551.0 main-bin purity 97.18 -> 93.28% removes its former
2.24 Mb passing recovery. E009 B3 improves; oral recall improves with lower
precision/F1. Oral old refinement gains against E017 old but E013 post loses.
Preserve those trade-offs and all alternatives; no score-driven refiner choice,
threshold/margin search or method-family conclusion. The original E017 veto has
useful protection. E017 stays MODIFY, E016 broader research anchor, neither a
universally optimal product default. Local Mac tolerance remains failed.

**Choose one coherent window-context composition/information learner next.**
Stop the recruitment-gate sequence here. Current composition averages discard
local heterogeneity/arrangement, and fixed oral learned neighborhoods remain weak
(bp-weighted agreement 20.68%) while many long cores mix origins. The already
reviewed CompleteBin context-TNF/global-local tokens motivate an information
route; its whole-tool performance is not causal proof for the module. Implement
one justified compact view/token/fusion/strand/length/inference design in the next
local block, with real contracts and one prospective comparison, rather than
another feature-by-feature campaign or a larger MLP for its own sake.

Retain explicit composition/depth branches, measured-parent semantics, E016
positive-only predictor/stopped-EMA target/reconstruction as initial anchors and
E016 CPM/E013 as the first fixed downstream context. Declare necessary integrated
changes before outcomes; do not choose E016/E017/E018 per community/genome from
truth. Keep all short/marker-negative/unknown/non-target DNA and optional noise,
features/tokens/embeddings/pre-post alternatives. Test real DNA views, strand,
exposure, gradients/EMA/noncollapse/reload/unit geometry/marker/export and owned
wheel contracts. Use chunked/indexed/lazy contexts, not all overlapping crop banks;
persistent candidates and temporary coexistence determine peak disk, not epochs.

Serious alternatives: frozen GLM/TNF/depth hybrid can add an external sequence
prior and remains a later candidate; E003's grouping gain/short-neighbor loss and
old laptop runtime do not dismiss it. Reliable marker-aware training could improve
biological separation, but same-genome copies/partial calls/replicons/panel limits
make duplicate-family hard negatives unsafe without a link rule. Extra resolution/
loss/acceptance grids would now reuse the same inadequate confidence evidence.
Genuine oral depth could help but is a different input experiment and does not
explain the E018 loss on depth-present E009. No option is proved optimal or ruled
out as a product family. Reuse the completed reviews; target primary refreshes to
precise design gaps and proceed directly to engineering.

[The focused data assessment](../../experiments/E018-vote-led-recruitment/robustness-and-data.md)
keeps oral sequence-only for this completed matched question, explicitly leaving
current-system depth benefit/depth-enabled transfer untested. Revisit separately
costed all-ten mapping or a current-system existing-depth control when that
question can change the design; no old dev3 causal extrapolation. Do not add a
broad dataset campaign to a solved acceptance test, or wait for competitive scores
before independent data. Keep skin frozen/unacquired and plan source/genome/
replicon/molecule/taxonomy/overlap/full-denominator/ambiguity/unique-vs-origin truth,
unchanged confirmation protocol and separate cost/retention admission alongside
the next coherent implementation. Two inspected communities remain development.

The next exact prompt is local implementation/engineering and complete priced
native preparation, not another cloud authorization. Source/candidate/criteria
freeze precedes changed community outcomes. October 28 at 00:00 Copenhagen stays
the storage boundary. AGENTS clarifies global vs per-guard peak growth: E018's
3.524 GiB global snapshot delta is the whole-run sampled growth, not the 2.786 GiB
maximum of reset guard counters. No original journal is rewritten.


## E019 local context implementation, October 21–22, 2026

[The prospective design](../../experiments/E019-window-context/design.md) implements
one bounded local/global composition information route after E018's negative
acceptance result. Up to eight real canonical-strand TNF windows interact with a
global token in one width-64/four-head pre-norm attention block, followed by zero-initialized
residual composition fusion and preserved original predictor initialization and explicit measured-parent depth. E016's real views/full-
parent exposure, positive-only predictor/stopped EMA target/reconstruction and
CPM/E013 remain anchors. Original accepted data/model/journals are immutable.

Attention is explicitly considered and chosen for content-dependent local/global
interaction with bounded sequence size, not as a mandatory fashionable ingredient.
Pooling/CNN are serious simpler alternatives with different interaction priors.
A pretrained GLM is complementary: it can add reference-trained sequence knowledge
these target-trained TNF tokens lack. No payload, taxonomy, marker training or
ensemble is implied, nor a family rejection based on old laptop projections.
CompleteBin's source informs the concept; neither its whole-tool success nor its
larger pretrained model is reproduced or causally isolated here. New context
construction/fusion and deterministic initialization make this a bundle treatment.

Integer indexed caches are ~6.42 GiB for the unchanged two-community eligible
axes. No all-overlapping-crop bank or measured window coverage is invented. Tiny
real reader/attention/gradient/EMA/reload/marker/CPM/E013/export/collection paths and
ordinary installed regressions are engineering evidence only. The original concatenation version failed longer engineering stability on two
profiles. E016 also fails GC-iid stress but passes oligomer20, exposing a new
fusion/initialization regression. A prospective zero residual/preserved predictor
correction passes 20 oligomer epochs in both modes without a new loss, seed,
schedule or guard relaxation. Earlier journals stay failed, GC stress remains a
limitation and native/full-community stability is still unproven. AGENTS records
the durable lesson to investigate near-floor smoke dynamics with cheap longer
engineering schedules before readiness, rather than weakening guards. Old Mac portability remains failed.

Prepare one candidate-versus-preserved-E016 comparison, no baseline refit/rescore,
no compulsory ablation campaign, same full populations/truth scope. Original
practical KEEP requires >=0.5 percentage-point R95 gains in both scopes and no
>=90% count loss; ABANDON if neither R95 nor either count improves, else MODIFY.
No product/default or isolated-attention claim follows from one bundle result.
A new $5 / eight-hour existing-VM request is separately priced (~$3.48 max quote),
with native feasibility gate before community tokens/fits and all resource/STOP/
credit/retention/return contracts. Current task starts none of it. October 28
remains the storage boundary; no prior fit budgets carry onward.

[Skin admission](../../experiments/E019-window-context/confirmation-plan.json)
proceeds as protocol/source planning only. Actual source/genome/replicon/molecule/
taxonomy joins, overlap/pretraining, duplicate-safe/zero-origin denominators,
competitive ambiguity/unique-versus-origin truth and separate acquisition/compute/
cost/retention still precede untouched confirmation. Genuine oral depth is also
separate; these two communities do not isolate current depth benefit or unseen-
genome/read-assembly robustness. Seek broader data at the coherent-candidate
milestone before promotion, without a broad campaign to rescue E018.


## E019 authorized native comparison, October 22, 2026

[Native admission](../../experiments/E019-window-context/native-observed.json) passes
all ten Linux gates, actual 20-epoch two-mode engineering/reload/learned-state,
complete source/runtime/retained axes and conservative affordability before the
sole two-community fit release. This run can decide whether the coherent local/
global context bundle improves recovery over preserved E016, not isolate attention
or establish product defaults/general robustness. No extra ablation/tool or old
fit/rescore is added. The owner newly approves $5; no older ceiling carries.

Existing machine/disks, original eight-hour clock / 8.25-hour provider STOP,
four threads / 26 GB sampled RSS / 25 GiB reserve / 20 GiB extra / 3 GiB return
remain. Fresh boot/process watcher and normal/crash/live tests pass. Current quote
~$3.48 with reserve, available credit DKK 1,882.53 / January 12 expiry and separate
$8 storage forecast ~$7.63 through October 28 pass. Costs/quality await completion
and independent evidence review; no final result from progress/shutdown alone.
All earlier failures and source freezes remain. Skin and genuine oral depth stay
separate/unacquired with their unchanged provenance/truth/cost admission needs.


## E019 mixed recovery and one coherent integration next, October 23, 2026

[Completed inspection](../../experiments/E019-window-context/inspection-observed.json)
accepts all science/native/member/resource/learning/geometry/DNA contracts. The
original joint criterion yields **MODIFY**: E009 post 5.8219 ->7.3058% (+8.231 Mb,
>=90% targets 4 -> 7), oral origin post 6.7719 ->6.5077% (-5.503 Mb, 34 -> 33). Parent
recovery improves in both scopes; oral old refinement improves too, but its E013
lift is smaller. E009 neighborhoods worsen, oral slightly improve; neither is a
whole-genome recovery proxy. Preserve all target/length/origin/unknown/non-target/
marker/unassigned strata, original Mac tolerance and failed engineering/review
journals. This is useful bundle evidence, not universal promotion or proof of a
missing-depth, attention-only or destructive-refiner cause.

Choose one cached E019-learning + **original E017** grouping integration with
fixed E013/defaults. The new learning closes about 54.4% of the prior E016-to-MetaBAT2
E009 gap, and the earlier grouping block improved that same endpoint under older
learning. Their interaction is untested. A one-off cheap coherent combination can
change which pipeline to retain, without a new threshold/selector/grid or claiming
additive gains. E017's oral regression is serious contrary evidence, so both scopes
must use the same frozen rule and no E018 permissive acceptance/per-bin oracle.
Original grouping/audit/E013 source is already byte-identical in E019's package;
prepare only a restore/schema/launcher contract, preserving science source freezes.

A frozen GLM/context/depth hybrid remains a serious complementary architecture;
E003's original failed criterion is no veto of the current family. Defer its new
inference/cache/runtime cost for this one decision-changing integration. Larger
Transformers/marker training lack a demonstrated capacity/safe-link case; do not
add them automatically. This is a bounded interaction question, not a default
return to many small feature tests. Skin admission/protocol should proceed at
this coherent milestone before robustness/promotion, with no DNA acquisition now.

[Operations](../../experiments/E019-window-context/OPERATIONS.md#exact-following-prompt)
proposes a separate new $1 /90-minute cumulative /105-minute STOP on existing
resources, four threads/26 GB/25 GiB reserve/20 GiB growth/2 GiB return, max quote
~$0.952 with reserve and fresh financial/source/native/retention gates. It is not
authorized by this inspection. Actual E019 subtotal ~$1.0162 /<$1.268 with reserve
fits original $5; VM terminated. Separate $8 storage still ends October 28 at 00:00
Copenhagen; no extension/deletion or old budget carries into the next comparison.


## E020 authorized cached integration, October 23, 2026

[The new E020 protocol](../../experiments/E020-context-information-integration/protocol.json)
freezes the owner-authorized $1 comparison of exact E019 learned vectors and
original E017 grouping/defaults with fixed E013. This is one cheap decision-changing
interaction of coherent existing modules, not a new threshold/loss grid. Both
communities use the same policy; original E017 oral harm is serious contrary
evidence, not ignored or assumed repaired. A GLM/context/depth hybrid remains a
strong complementary information direction after this interaction question.
No changed community result is present at preparation. Actual tiny reader/worker/
sparse/refiner/four-export/collector contracts pass; native source/runtime/credit/
headroom/retention gates precede execution. All sources/results/failures remain.
90-minute cumulative / 105-minute STOP, $1 new ceiling and original October 28
storage boundary apply; no old budget, scientific replay or extra resource.


E020 native follow-through: all seven retained-byte/runtime/full-context-axis/real
tiny marker/refiner/export/launcher/DAG gates pass under a fresh process/boot-bound
watcher. The sole original-policy cached comparison is released, not scored or
complete. Existing source/package/vectors and full populations remain; no retry
of accepted science, model/threshold change, new DNA or retention extension.
[Operations](../../experiments/E020-context-information-integration/OPERATIONS.md)
owns exact clock, logs, original $1 and subsequent frozen inspection boundary.


## E020 reviewed integration and next semantic information block, October 23, 2026

[Independent completed inspection](../../experiments/E020-context-information-integration/inspection-observed.json)
accepts science/source/runtime/full axes/cache policy/complete DNA and every return
member. The frozen rule remains **MODIFY**: E009 post 7.3058 -> 7.5416% (+1.308 Mb,
>=90% targets 7 -> 8), oral origin 6.5077 -> 5.6688% (-17.475 Mb, 33 -> 27). E009
misses the original 0.5-point practical gain and oral loses; this is no promotion.
All 955 target gains/losses and length/origin/eligibility/marker/unknown/non-target/
excluded/unassigned populations remain. More eligible DNA is unassigned (+57.931 /
392.555 Mb), B3 F1 falls in both scopes, and fixed E019 learned neighbors do not
change. Oral parent recovery is already weak; E013 rescues +72.694 Mb over that
parent with no target loss. Do not select old refinement by its higher E009 R95,
blame missing depth, or call current-parent refinement destructively causal.
Native/source and independent all-row cache checks find no critical adapter/ID/
depth error, without proving all biology or policy optimality. Full denominators,
N quarantine, oral origin-versus-unique limitation and Mac failures remain.

**Choose a coherent frozen pretrained-sequence/context/composition/measured-depth
hybrid, with frozen untouched-skin source/truth admission in parallel.** This
resolves the now-completed integration question and uses the reviewed GLM route
rather than another grouping threshold/selector grid. Current context summarizes
composition within windows; a frozen semantic sequence prior offers base-order
information learned outside the small target training set. A small trainable
reliability/fusion adapter can use that evidence while retaining explicit depth,
real views and consistent geometry. Use ordinary E019 CPM/E013 uniformly as the
provisional downstream anchor; E020, E017 and E018 remain scoped evidence/modules,
not permanently banned families or per-community routing choices.

Contrary evidence matters: accepted E003 GLM short 5NN 0.45938 trails raw TNF 0.57396,
failing its original criterion, while bp-weighted grouping B3 F1 0.37664 exceeds
0.30801. These were not current-context or full-genome recovery comparisons. Reuse
that failure and reviewed field/source/thesis evidence, exact model/tokenizer/custom
source pins and retained cache; do not declare a semantic prior certain to help.
[Author source](https://github.com/MAGICS-LAB/DNABERT_S) supports a species-aware
DNABERT-2-based frozen 768-dimensional/mean-pooling route. The publisher redirect
could not be refreshed; use the maintained completed paper review rather than claim
it was freshly read. Resolve one precise view/cache/strand/exposure/fusion design
in the implementation task, then perform real tiny extraction/training/reload tests.

| Serious alternative | Current judgment and uncertainty |
| --- | --- |
| Larger Transformer or new raw-DNA encoder | Base-order processing is valuable to test; capacity is not shown to be limiting. A frozen GLM is itself Transformer based and may complement existing compact attention. A compact new sequence encoder is a fallback if pinned model/licensing/runtime proves unsuitable, not an extra model campaign. |
| Reliable marker-aware learning | Keep visible, but E011/E012 same-genome duplicate families/partial/locus/panel limits make naive SCG cannot-links unsafe. A safe label-free pair rule and marker-negative handling are prerequisites. No automatic new marker loss or taxonomy. |
| More grouping/refinement tuning | E017/E018/E020 provide enough mixed/negative two-community evidence to move to information now. Preserve modules/alternatives, no grid or perfect-grouping prerequisite. |
| Untouched data alone | Admit skin alongside coding now, before promotion. Different body site does not establish genome/pretraining independence. More data cannot substitute for a justified candidate. Genuine oral depth remains separately costed. |

The [proposed exact next prompt](../../experiments/E020-context-information-integration/OPERATIONS.md#exact-following-prompt)
is local implementation/tiny engineering plus a newly explicit five-file skin
acquisition/admission (4,605,403,023 prior HEAD bytes and <=10 MiB metadata; <=10 GiB
extra / four threads / 8 GB sampled RSS / four-hour acquisition-validation clock).
No DNA or new implementation occurs in this inspection. Stream/index source joins;
remain provisional if molecule/circular/host/taxonomy/competitive-ambiguity truth
or exact/near/reference/pretraining overlap is unresolved. Preserve full/zero-origin
reference denominators, source-blind IDs and original zero-bp records. Freeze one
candidate/comparator/criteria before confirmation scores. Skin is sequence-only
GSA without assembly errors or admitted contig-depth, not unseen-genome evidence.

At most one decision-changing control may be prepared. One later candidate-versus-
preserved-E019 comparison must price full extraction, setup, fits, collection and
review, reusing baseline outputs. The old Mac projection is ~447 parent-only hours
for current eligible DNA, not an E2/GPU quote or a reason alone to reject the route;
view exposure may add work. Measure tiny throughput, complete source/runtime/library
contracts and CPU/GPU/RAM/peak-disk/cache/export/credit/product/quota prerequisites
before a separate execution approval. No GPU availability/eligibility, old budget,
service/permission/VM/resource change or storage extension is implied. E020 subtotal
~$0.2749 / <$0.426 with reserves fits its $1; original $8 storage ends October 28
at 00:00 Copenhagen. Both inspected communities remain development, not final
validation, SOTA evidence or a product-family decision.

## E021 implemented hybrid and parallel skin admission, October 23, 2026

The owner invoked E020's local prompt and conditionally authorized a comparison
if every resource/runtime/financial gate passed, allowing this task to defer.
[E021](../../experiments/E021-frozen-sequence-hybrid/OPERATIONS.md) implements one
coherent information upgrade directly, rather than another selector/loss grid.
The exact retained frozen Transformer prior supplies base-order information to
real parent/crop views; a compact reliability residual complements E019's local
composition attention and explicit measured-parent depth. No backbone fine-tuning,
marker-aware training, taxonomy or ensemble. Original E019 CPM/E013 remains uniform.
The model's author float32 reference attention is selected explicitly because its
optional Triton branch changes dtype; no source/weights are patched. Full-view
provenance, zero initial residual, same-runtime reload and original guards matter
more than treating tiny training as evidence of genome recovery.

Actual local contracts pass; no community outcome is admitted and E003's contrary
short-neighbor result remains. A current CPU launch is not justified: full native
throughput/RAM are unknown, 8.708 GiB cache arrays plus working coexistence can
exceed the 20 GiB cap, and current local staging cannot absorb a full return/review
within its 10 GiB scope. Ample trial balance does not resolve those gates. **Defer,
then admit one native GPU/resource envelope before this candidate comparison.**
The proposed existing-VM N1/T4 route needs explicit quota/type/32 GiB growth scope,
complete compatible Linux/CUDA checks and measured throughput; it is not a family
rejection based on slow Mac extrapolation. New $45/48-hour planning bound is not
spent or an extension of old budgets. Ordinary CPU learning/grouping remains four
threads. No automatic alternative machine or retention extension.

Five authorized skin files are acquired/audited in parallel. Independent origin
admission retains all 610 full positive targets, one zero origin, every competitor,
localized ambiguous bases and known exact-shared sensitivity. **313/610** target
inventories exactly match oral-GSA-observed genomes; broader near/pretraining
inventory and biological host/molecule grouping remain uncertain. Keep the original
skin choice as a new-community-setting check, with prospective overlap strata;
do not market it as unseen-genome confirmation or select a replacement after
metadata inspection. No skin score/fit now; its real evaluator and later resource/
cost/retention admission remain. GSA lacks assembly errors and measured contig depth.
Independent sequence identifiability is still distinct from verified simulator origin.

This block updates durable agent guidance only for exact-view/DNA cache bindings,
explicit depth-only rebind proof and actual wheel entry-point installation. The
experiment owns failures/resources, not AGENTS. The strongest next decision is
whether this frozen complementary information is natively affordable and improves
both development scopes under its original criteria; do not add more architecture
before resolving that result. Storage review remains October 28 at 00:00 Copenhagen.

## E021 E009-only completed review and next learning block, October 25, 2026

[Completed review](../../experiments/E021-frozen-sequence-hybrid/comparison-review.json)
is **MODIFY**, with every native scientific/reader/reload/accounting contract
passing. Full-reference R95 7.3058 -> 7.8175% gains 2,837,916 bp, but >=90% targets
7 -> 6; 10 targets gain / 15 lose. ASV406.4 contributes 3.112 Mb, with two high-
recovery losses elsewhere. The practical gain threshold passes unchanged; no-count-
loss and original two-community KEEP do not. Oral/skin remain unrun. Slightly
better bacterial nearest neighbors coexist with worse bacterial restricted grouping
precision/recall. Noncollapse, exact reload and graph proofs reject several critical
implementation explanations, without proving the design optimal or isolating the
GLM contribution from changed branch initialization/training.

Keep E021's view-exact bank and optional branch as development evidence, not a
uniform default. The old destructive refinement's higher 8.2428% R95 cannot select
that policy after truth; frozen E013 remains uniform and all alternatives survive.
A zero-GLM matched control could isolate attribution cheaply, but is secondary
unless it changes a design decision. More large-model capacity or full oral GPU
extraction is not the strongest next use of resources after this narrow gain.

**Next implement reliable marker-informed cross-contig learning locally.** Existing
self-positive crops explicitly link views of one parent, not different genomic
fragments. Add a justified biological/context constraint to the compact learner,
using cached information and abstention. This is a new hypothesis, not a diagnosed
causal explanation of E021. E011/E012 distinct loci, partial/overlap, panel/lineage,
replicon and assembly-duplication findings rule out naive repeated-family hard
negatives. Source-reviewed reliability and composition/depth support must precede
constraints; preserve marker-negative/short/non-target DNA and unknown/unassigned
outcomes. Truth may evaluate/diagnose, never choose pairs, thresholds or bins.

Resolve one coherent learning rule prospectively, keep CPM/E013 provisional,
retain immutable E019/E021 and prepare one separately priced comparison using
CPU-readable caches. No new GPU extraction, broad grid or mandatory factorial.
Additional sequence-only transfer and original skin remain untested; freeze a
supported comparator/data protocol and evaluator before changed outcomes. Skin's
313/610 exact oral-inventory overlap and unresolved unique/near/pretraining/molecule
limits remain, without silently acquiring a different community.

[Final operational inspection](../../experiments/E021-frozen-sequence-hybrid/inspection-observed.json)
closes the CPU queue publication race with atomic preloaded controls, restore-only
reader/source/runtime admission and six actual consumer exits. Old pending receivers
and failed journals are preserved. Transport verification alone is not consumer
admission or completion. This durable distinction/atomic publication enters AGENTS;
transient phase details remain in E021. E2 is stopped/restored; temporary GPU/disks
are removed after verified preservation. Costs are $9.992 priced subtotal / $11.592
with reserves inside the original $45, not an invoice. Existing stopped storage
remains $31.20/month and the $8 approval ends October 28 at 00:00 Copenhagen; the
next local preparation must surface preservation needs before that boundary.


## E022 reliable cross-contig candidate prepared, October 25, 2026

[E022 design](../../experiments/E022-marker-informed-learning/design.md) implements
the selected learning block directly: strong cached marker calls plus measured
parent depth/composition support bounded soft links, with original real views,
encoder/initialization/predictors/EMA, seed/schedule and CPM/E013 intact. Protein
near-identity, partial/overlapping/ambiguous calls and context disagreement can
withhold a constraint. Repeated-family hits alone do not define negatives.
Marker-negative partners may receive supported positives; no DNA is discarded.
This is a useful hypothesis about fragmented-genome supervision, not a diagnosis
proved by E021's scores. Pair thresholds are label-free and frozen before new
outcomes, with no truth/family/K/grid tuning.

Actual installed local reader/loss/gradient/20-epoch/reload/refiner/export and
zero-weight-state checks support engineering readiness, not recovery or Linux
admission. Label-free E009 availability gives 1,963 positives / 365 negatives in
23.96 seconds, 1.343 GB sampled RSS. Only one first candidate E009 fit is proposed;
E021 outputs are reused. The optional zero-side-loss ablation is prepared but not
part of that execution. Sequence-only input runs ordinary learning and abstains
from this depth-gated mechanism; skin cannot silently become active confirmation.

[DCVBin audit](../evidence/2026-10-25-dcvbin-efficiency-and-marker-learning.md) records
a much smaller parent-only/truncated >=2 kb workload, not measured speed. No
quantitative runtime table could be confirmed in the accessible current paper and
supplement. Preserve GLM bank reuse now; length-bucket batching/token reuse and
explicit cheaper exposure/distillation remain future choices. Do not add another
GPU job or larger model merely because E021 allocation was long.

[Operations](../../experiments/E022-marker-informed-learning/OPERATIONS.md) proposes
a new $2 CPU-only / two-hour comparison, all native/live-credit/resource gates
still pending. No old budget, community execution, resource or retention change
is authorized here. Original stopped storage ends October 28, 00:00 Copenhagen;
a separate storage decision must preserve non-backed-up bulk before that date.
