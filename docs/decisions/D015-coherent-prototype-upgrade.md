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
