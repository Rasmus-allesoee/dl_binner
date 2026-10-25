# Questions and Hypotheses

Updated: 2026-10-23

This register owns the status and resolution history of questions and hypotheses. [STATE](../STATE.md) owns immediate priority. Evidence remains in linked notes and experiments. H001 remains inconclusive at E001 seed-11 scope; its avoidability claim is not established. D010 defers replication; E001 retained-output diagnostics are complete. D011 chooses a bounded prototype after the current review.

Question statuses: `open`, `answered`, `deferred`, `superseded`. Hypothesis statuses: `untested`, `testing`, `supported within scope`, `not supported`, `inconclusive`, `abandoned`, `superseded`. A material revision preserves the previous statement and records why it changed; use a new ID if it is a different scientific claim.

## Q001

**Which recoverable errors remain in correctly configured contemporary binners, and where are they introduced?**

Status: open. Opened: 2026-09-16.

The candidate focus is contig loss/misassignment in fragmented prokaryotic assemblies with weak or distorted coverage. Separate information absence, representation failure, clustering error, and quality/refinement selection. Evidence: [thesis](../evidence/2026-09-16-thesis.md), [landscape](../evidence/2026-09-16-landscape.md). Related: H001; [D002](../decisions/D002-investigate-before-architecture.md).

Needed to resolve: pinned native configurations, stage-level outputs, appropriate known-origin inputs, and matched recovery/contamination measurements. Resolution must name the regime and surviving alternative explanations. No result yet.

2026-09-17: [E001](../../experiments/E001-coverage-thinning/README.md) now specifies the first test, with paired thinning on a fixed public assembly and native stage outputs. The [audit](../evidence/2026-09-17-targeted-audit.md) resolves enough input/normalization questions to implement it. Still open: no performance gap or avoidable loss has been observed.

2026-09-18: the Gate 0 harness and portable fixtures are implemented. Exact native checks are prepared for UCloud, not passed. [D004](../decisions/D004-human-cpu-preflight.md) changes execution choices, not the hypothesis; no scientific gap has been observed.

2026-09-27: the [seed-11 MetaBAT2/VAMB pair](../../experiments/E001-coverage-thinning/paired-pilot-observed.json) is accepted. Thinning decreases MetaBAT2 R95 by 0.24793 but increases VAMB R95 by 0.02586. Native MetaBAT2 support shrinks strongly; this is a stage-localization clue, not proof of avoidable loss. Q001 stays open pending COMEBin, paired replicates and representation/selection diagnostics.

## Q002

**What would make an intervention meaningfully different from the closest prior art?**

Status: open. Opened: 2026-09-16.

TaxVAMB, GenomeFace, CompleteBin, DCVBin, SCGBinner, REMAG, and UncertainGen occupy several initially attractive directions. Their relevance depends on the selected regime. See [review depth and open audit items](../evidence/2026-09-16-landscape.md).

Needed to resolve: full relevant methods and code-path review, publication/release refresh, and a comparison between the proposed mechanism and existing approaches. An unfamiliar architecture or new combination is not evidence of novelty. No candidate method is selected.

2026-09-17: [targeted audit](../evidence/2026-09-17-targeted-audit.md) narrows the novelty space. GenomeFace's inspected balance is global, UncertainGen does not establish calibrated coverage uncertainty, McDevol already augments coverage counts, and current QuickBin contains optional length-aware coverage likelihood code. DCVBin's inspected basic path uses coverage. These resolve specific source questions, not Q002 as a whole. Mechanism-focused comparisons are required after a residual failure is established.

## Q003

**What simulation and real-data design can test the chosen mechanism without importing the thesis's confounders?**

Status: open. Opened: 2026-09-16.

The previous simulation has one pair per ANI region, simplified abundance structure, clean shredded contigs, and pooled-input duplication artifacts. We need a question-specific design with explicit truth and recoverability, realistic follow-up, and distinct development/evaluation roles. Evidence: [thesis limits](../evidence/2026-09-16-thesis.md), [assets](../evidence/assets.md).

Availability update, 2026-09-16: the owner confirmed the original artifacts remain on UCloud and said we should build our own optimized simulations when useful. Data availability is therefore owner-confirmed; file identity and protocol suitability remain open. The old datasets are optional prior evidence, not prescribed evaluation data.

2026-09-17: the owner emphasized **public CAMI benchmarks as well as custom simulations**. [D003](../decisions/D003-coverage-diagnostic.md) chooses CAMI II Marine for E001 development, with fresh downloads (owner-confirmed). [Data audit](../evidence/2026-09-17-benchmark-data.md) separates available CAMI III toy data from the active challenge's scheduled assembly release. Custom CAMISIM data are deferred until a concrete mechanism needs them. Final independent evaluation and real-assembly validation remain open; E001's fixed GSA does not answer them.

2026-09-18: the owner clarified that human-associated microbiomes, not environmental research, are the focus. [D004](../decisions/D004-human-cpu-preflight.md) replaces Marine with CAMI II HMP GI. Full corrected-truth/coordinate joins, historical taxonomy, sample inventory and interpretability floors remain open; prefix inspection alone does not validate them. The shared gastrooral GSA and GI-only GSA must not be conflated.

2026-09-19: complete owner join audit and local publisher-header investigation
identify 20 intervals with foreign-simulation provenance. [D005](../decisions/D005-gi-input-derivative.md)
authorizes their exact hash-bound quarantine for the E001 development derivative.
Both published truth tables omit them. This changes mapping competition and does
not restore missing intended GI sequences. Corrected conversion and historical
taxonomy remain pending; no scientific outcome has been assessed.

2026-09-20: owner D005 conversion passed. The separate publisher-linked historical
taxonomy is verified, and actual local preparation passes the existing population
floors (224 genomes; 7,964 short queries across 66 genomes), with unchanged FASTA
and truth. See [taxonomy evidence](../evidence/2026-09-20-gi-taxonomy.md). Owner
taxonomy-aware reproduction/freeze and remaining native feasibility gates are next;
no binning outcome or methodological conclusion follows from these input checks.

2026-09-20 owner follow-up: taxonomy-aware outputs match local hashes and the
[population is frozen](../../experiments/E001-coverage-thinning/frozen-inputs.json).
This closes the input-identity/domain/population-floor checks, not the broader
benchmark/generalization question. Proceed to native CPU feasibility without
repeating accepted inventory work.

## Q004

**What biological and computational improvement will count as success for the selected regime?**

Status: open. Opened: 2026-09-16.

Candidate endpoints include true recovered sequence at controlled impurity, genome recovery with missing targets counted, and cost. A new approach might improve one useful part of this tradeoff without winning every aggregate ranking. Proxy quality, origin-based purity, and full MIMAG categories must remain distinct.

Needed to resolve: define the intended use, primary endpoint, denominators, thresholds, resource constraints, comparison population, and uncertainty analysis in the first experiment protocol before results are examined. Do not inherit the thesis's composite score as the project's objective.

2026-09-17: E001 defines a fixed-population, purity-constrained assembled-sequence recovery endpoint, AMBER companion reports, length/stage diagnostics and explicit triage/resource thresholds. This answers protocol requirements for that diagnostic only. The eventual method's biological success criteria and independent validation remain open.

2026-09-18: metric fixtures now pass locally; AMBER parity remains a native Linux check. GPU assumptions were superseded by the actual CPU-only budget. Full-schedule feasibility is required before launch, and removing COMEBin would require revising its specific triage claims prospectively.

## Q005

**Which information can the eventual method reasonably require, and how broadly should it transfer?**

Status: open. Opened: 2026-09-16.

Single/multi-sample coverage, taxonomy, pretrained references, marker genes, and graph/read evidence carry different assumptions and costs. Temporary HPC access affects execution strategy but does not alone justify a permanently expensive method. Evidence: [initial assessment](2026-09-16-initial-assessment.md), [assets](../evidence/assets.md).

Needed to resolve: connect the target biological use to accessible inputs, record available compute/access duration when a job is planned, and audit genome/sample/pretraining overlap. A claim of unseen-genome generalization needs a corresponding evaluation design.

2026-09-17: E001 uses target-data unsupervised fits, sequence/coverage inputs and native COMEBin marker information, explicitly without a pretrained taxonomy/foundation model. It diagnoses transductive behavior. This does not commit the eventual method to those inputs or make public CAMI genomes novel to all prior tools.

## H001

**Some avoidable binning errors arise because coverage reliability varies across contigs or samples in ways that existing preprocessing and feature integration do not adequately handle.**

Status: inconclusive. Proposed: 2026-09-16. Updated: 2026-09-30. Scope: a candidate explanation for Q001, not a novelty claim or model specification.

Motivation: reported coverage dilution and recovery differences in [the thesis](../evidence/2026-09-16-thesis.md). Caveat: absolute depth loss alone is insufficient evidence because normalization can remove scale, and workflow comparisons also change clustering populations. Adaptive weighting and uncertainty modeling already have [prior art](../evidence/2026-09-16-landscape.md).

Discriminating test: hold sequences, truth, sample composition, and clustering conditions fixed while comparing valid coverage inputs with a controlled, characterized distortion; inspect actual post-normalization features. Establish whether a simple reliability treatment changes truth-based recovery at comparable contamination. Check realism separately through mapped or real data. The first paired development results are recorded below; no reliability intervention has been tested.

Competing explanations: nonidentifiable shared sequence, mapping ambiguity, insufficient sequence signal, a clustering/selection issue, or incorrect baseline configuration.

Rejection/modification: the distortion disappears after preprocessing; current methods already handle it; performance does not track the proposed mechanism; improvement only reflects increased contamination or a proxy-score change; or the target sequence is not recoverable from the available evidence. Update the hypothesis or abandon it with a linked result.

2026-09-17 refinement, preserving the original claim: [E001](../../experiments/E001-coverage-thinning/README.md) tests **sampling reliability at fixed assembly**, not every mapping distortion contemplated above. Its scale-only control may eliminate a naive absolute-depth explanation, while its stage diagnostics distinguish reduced information from possible avoidable processing loss. No reliability correction or new model is being proposed yet. Degradation under thinning alone is not support; a null result in one community is not a universal rejection of H001.

2026-09-21 context for H001: the E001 prefix read-origin analysis reveals extensive
ambiguous placement, with nearly equal true-origin-compatible counts for the two
mappers despite different MAPQ scales. [D008](../decisions/D008-mapper-and-first-preprocessing-slice.md)
retains fixed strobealign evidence for C0/CT. This is a confound to distinguish
from sampling reliability, not support for H001 or evidence of a novel solution.

2026-09-27: H001 enters **testing** after the first checksum-bound paired fits. The contrasting MetaBAT2/VAMB effects do not support or refute a general reliability mechanism. COMEBin-specific prospective criteria cannot yet be assessed. No method or architecture is selected.

## Closed and superseded records

None in this project's active research record yet. Earlier project alternatives and staged learning plans remain in [historical planning](../history/README.md). They were not failed experiments. Close future entries in place, preserving their evidence and resolution dates.


2026-09-29 resolution of current priority (Q001/Q004/H001): all three seed-11
native pairs are accepted in the [combined assessment](../../experiments/E001-coverage-thinning/seed11-assessment.md).
COMEBin loses 0.03643 R95, VAMB gains 0.02586 and MetaBAT2 loses 0.24793.
The original three-seed criterion is not evaluated; H001 is neither supported nor
refuted. [D010](../decisions/D010-bounded-e001-and-prototype.md) defers seeds 23/47
and limits remaining E001 work to diagnostics on retained outputs. A new usable
binner is the primary goal; resolving Q002's novelty question is not an implementation
prerequisite. Biological performance claims still require evidence.

## Resolution update, 2026-09-30: E001 closure and first product

[Final E001 evidence](../../experiments/E001-coverage-thinning/closure.md) closes the
approved seed-11 scope. Q001 remains open in general: selection can account for a
0.03862 CT oracle gap, while local representation losses overlap only part of lost
recovery. Neither identifies a validated truth-free fix. H001 stays **inconclusive**;
its original three-seed criterion is unresolved, and seeds 23/47 are deferred.
No global rejection or reproducibility claim follows.

Q002's novelty question is deferred as a product gate, not answered by architecture
choice. The [current review](../evidence/2026-09-30-binner-design-review.md) covers
relevant families, recent benchmarks and a justified source shortlist through
2026-09-30. Q003 remains open for independent/real-assembly evaluation; E001 is
development data. Q004's first-product acceptance is operationally bounded in
[D011](../decisions/D011-first-binner-prototype.md), distinct from research superiority.
The next task is implementation, not another exploratory benchmark campaign.

2026-09-30 architecture reconsideration: the owner requested greater weight on
thesis recovery and a serious GLM comparison before implementation.
[Reassessment](../evidence/2026-09-30-architecture-reassessment.md) replaces the
VAE-first recommendation with D011's provisional contrastive direction and one
bounded frozen-GLM feasibility check. This answers a product-planning priority,
not Q001/H001 or a claim of architecture superiority. Short-contig-capable methods
remain in scope; new short-inclusive evaluation can be planned independently of E001.

2026-10-03 Q004/D011 feasibility update: [E002](../../experiments/E002-dnabert-s-feasibility/README.md)
accepts actual frozen-DNABERT-S CPU contracts at small local scale (40 real windows,
182.852 s, 1.314 GB sampled peak, coherent four-thread limits). The model was not
trained and no biological utility was evaluated. An input-only IUPAC validator
failure was corrected before model load and retained; one model/environment used.
Bulk extraction projections are expensive and hardware-specific, so encoder choice
remains provisional. The sole next comparison is capped at 320 new short-inclusive
development fragments with scope/evaluation/cost frozen first. No E001 result or
H001 status changes, no additional seeds or architecture campaign authorized.

2026-10-03 Q004/Q005 first-sequence-route resolution:
[E003](../../experiments/E003-representation-screen/README.md) completes the final
bounded screen on 320 new short-inclusive development fragments. All actual
resource limits passed. GLM improves fixed-clusterer sampled grouping but loses
short-neighbor purity; the precommitted joint inclusion criterion fails.
[D011](../decisions/D011-first-binner-prototype.md) selects 136-dimensional
composition input to our own compact contrastive encoder for the first software
milestone, while retaining GLM's grouping benefit as counterevidence to any
universal composition preference. No trained-composition, unseen-species or
whole-genome recovery claim follows; pretraining overlap remains unexcluded.
Q003's independent/real-assembly evaluation remains open. No Q001/H001/E001 status
changes or further architecture gate; implement, retaining raw-feature controls,
short strata and unassigned outcomes, and diagnose concrete failures as they arise.

2026-10-04 Q004 software milestone completed:
[E004](../../experiments/E004-first-binner/README.md) accepts the actual installed
composition/contrastive train→checkpoint reload→embed→fixed cluster→export path,
with complete ID/DNA accounting, raw control and measured costs. Grouping improves
within this development panel while precision/short-neighbor purity decline;
co-genomic negatives are observed but their causal role untested. This is not
whole-genome recovery or independent biological validation. Q003 and coverage's
biological value remain open; the next bounded product task is CPU/Linux native
validation and an assembly/explicit-depth pilot protocol. H001/E001 are unchanged.
The owner also requests a later **non-blocking** matched TNF/contrastive,
frozen-GLM/contrastive-head and hybrid comparison even if the prototype works.
[D011](../decisions/D011-first-binner-prototype.md#planned-non-blocking-learned-representation-comparison)
owns that plan; nothing from it is implemented or run during E004.


2026-10-06 Q004 product-validation update: [E005](../../experiments/E005-linux-pilot/README.md#accepted-v5-native-gi-pilot-and-independent-review-2026-10-06)
accepts native Linux and the bounded short-inclusive GI GSA/explicit-depth pilot.
Learned confirmed R95 improves over raw, with lower assigned-bin purity and
fragmentation retained; time/RSS ceilings pass. A serial scheduling deviation
is retained and corrected locally without repeating science. Q003's independent
real-assembly/whole-MAG evaluation and isolated coverage value remain open.
[D011](../decisions/D011-first-binner-prototype.md#e005-acceptance-and-next-bounded-usability-milestone-2026-10-06)
now prepares a bounded generic-command usability milestone, without another
architecture gate or benchmark expansion. H001, E001 and deferred seeds are unchanged.

2026-10-06 Q004 usability update: [E006](../../experiments/E006-cli-usability/README.md)
accepts an installed learned/raw workflow, complete byte-bound label-free
summaries and strict recovery/failure/resource contracts. Model/training/clustering
remain unchanged; no accepted science is repeated and no biological utility is
asserted. Next prepare a tiny owner-controlled Linux generic-launcher smoke.
Independent quality/coverage questions and the non-blocking comparison stay open.

2026-10-08 Q001/Q003/Q004/Q005 comparative-planning update: the first usable
prototype is merged and its native product evidence remains accepted.
[D013](../decisions/D013-first-comparative-benchmark.md) and
[E009](../../experiments/E009-competitive-benchmark/README.md) prepare a new
sample-0 actual short-read gut assembly, paired observed depth and a bounded
native-tool comparison with matched raw/learned and sequence/depth controls.
Whole-reference versus assembly-conditional recovery, ambiguous DNA, all length
strata and native cost are prospectively separated. The seven ranked tools'
[focused source/method assessment](../evidence/2026-10-08-competitive-binner-study.md)
identifies promising mechanism tests, not a causal architecture winner. Exact
source/pretraining overlap and native CPU/evaluator feasibility are unresolved;
new sample identity alone does not establish independent genome generalization.
No benchmark or architecture comparison has executed, no accepted science is
repeated and H001/E001 remain unchanged. E009 will be development evidence after
its errors guide changes; broader validation stays open. The GLM/head/hybrid
follow-up is still planned, not an implementation/release gate.


2026-10-09 E009 reconciliation: learned TNF plus measured depth remains the primary
product; raw/sequence-only runs are capped diagnostics, not product/architecture
gates. Supplied sample-0 contigs are verified GSA, so the read-derived MEGAHIT plan
remains. COMEBin joins the bounded comparison, CompleteBin is explicitly max-50,
and DCVBin is excluded for its unadapted CUDA/single-depth/CPT recipe, not missing
weights or coverage use. Markers are a high-priority grouping/refinement candidate
with one controlled follow-up recorded in the [targeted review](../evidence/2026-10-09-e009-contract-reconciliation.md).
No quality scores or causal mechanism finding follow from adapter tests; Q001/Q003
remain open and H001/E001 are unchanged. Unknown pretrained overlap limits
unseen-genome claims without becoming evaluation-pipeline label leakage.

2026-10-14 E009 operational/input amendment: v10/v14 tiny native contracts are
independently accepted without replay, not bin-quality evidence.
[D013](../decisions/D013-first-comparative-benchmark.md) now uses one sample-0
assembly and ten first-listed corrected-subject coverage samples; this is a
prospective representation/storage tradeoff, not proof of an optimal sample count.
The locally tested GCP data stage and [storage audit](../evidence/2026-10-14-completebin-storage.md)
are preparation only. Data/truth population, new-host scale/cost and all full-fit
quality questions remain open; Q001/Q003 and H001/E001 outcomes are unchanged.

2026-10-14 later owner clarification: [PROJECT_INTENT](../../PROJECT_INTENT.md)
now prioritizes improving our own high-performing, potentially SOTA binner;
software acceptance of the simple prototype is a milestone, not competitive
success. [D013](../decisions/D013-first-comparative-benchmark.md) records why an
expensive expected ranking adds little architecture evidence, and replaces the
mandatory five-tool campaign with reusable full assembly/ten-depth data, selective
native references and one prospectively justified mechanism test. CompleteBin,
COMEBin's full grid and SCGBinner full runs are deferred; SemiBin2 is a later first
candidate and MetaCAT core conditional on a grouping question. No fit/score is
authorized in the [data-only phase](../../experiments/E009-competitive-benchmark/gcp-data-observed.json).
Data/results inspected to choose changes remain development evidence; one weak
prototype/dataset cannot decide depth/sequence/taxonomy product membership.
Additional prospectively selected data are needed to confirm improvements, with
separate untouched evaluation for broad/SOTA claims. Q001/Q003/Q004/Q005 and
H001/E001 outcomes remain unchanged; no architecture is selected in this phase.

2026-10-15 E009 data-review update: full sample-0 assembly and all ten BAM/depth
axes are independently accepted; the complete DAG failed in final truth parsing.
[The retained native failure](../../experiments/E009-competitive-benchmark/truth-failure-example.json)
is explained by minimap2 ambiguous-base accounting. The complete sample-0 read/
source audit verifies 309 positive genome IDs and separate plasmid/host identities;
[the population review](../../experiments/E009-competitive-benchmark/truth-population-review.json)
does not admit coordinate truth. Repair/test a fresh truth derivation from retained
PAFs, then prepare unchanged raw/learned TNF+ten-depth/TNF-only diagnostics under
a separately proposed $2 fit cap. No native data stage or alignment is replayed,
no fit/score runs and no external tool belongs in the immediate next step. This
supplies reusable development data, not a mechanism or performance answer;
Q001/Q003/Q004/Q005 and H001/E001 scientific outcomes remain unchanged. D013's
one-mechanism decision rule and prospective additional-data confirmation remain.

2026-10-15 E009 truth repair: [v2](../../experiments/E009-competitive-benchmark/truth-v2-admission.json)
is admitted as conservative supplied-reference alignment truth, derived from
retained PAFs on the Mac with no new aligner or VM wake. Observed genome IDs,
separate plasmid/HOST, exact circular coordinates, full provided lengths and all
competitors pass review. Fixed qualifying-N span quarantine leaves 3.3034% of
query DNA unknown; this is an evaluator limitation, not binner performance.
The unchanged-control launcher is prepared and locally safety-tested, with a
separate $2 approval still required. No fit, score, mechanism result or scientific
question resolution follows from this repair; the above question statuses remain.

2026-10-16 E009 control review: [four unchanged controls](../../experiments/E009-competitive-benchmark/controls-review.json)
completed successfully and the VM stopped within the separate $2. Learned ten-depth
improves weighted conservative reference recovery4.5765→5.3911%, with full bacterial
source availability only18.5321%. Overall neighbor gain is driven by non-target
queries; bacterial neighbors worsen modestly. Grouping recall rises but mixed bins
remain. [D013](../decisions/D013-first-comparative-benchmark.md) selects preparation
of one fixed-encoder marker-conflict splitting test, subject to marker availability
and a prospective second-community confirmation protocol. No marker benefit,
mechanism causation, feature-family rejection or broad performance result is yet
established; scientific question statuses remain open. No external binner or new
fit is authorized by this review.

2026-10-16 subsequent development-pace reassessment: the owner asked whether the
standalone marker split is too narrow and serial feature trials too slow.
[D015](../decisions/D015-coherent-prototype-upgrade.md) recommends one integrated
next prototype using biological views, composition/depth learning and marker-informed
grouping/refinement, with selective decision-driven ablations. This supersedes the
marker-split-first recommendation, not E009's accepted measurements or scientific
question status. Existing evidence can justify implementation without first proving
every ingredient separately; an integrated gain alone would not identify causal
components. No new marker preparation, product code, fit, score or cloud work ran.

2026-10-16 implementation update: [E010](../../experiments/E010-coherent-prototype/README.md)
implements the accepted D015 bundle locally with retained real-window, modality,
geometry and marker/refinement interfaces. Tiny native software checks are not
biological resolution of Q001/Q003/Q005 or H001. The first candidate development
fit and frozen additional oral-GSA confirmation remain unrun/separate approvals.
A bundle gain would not establish each ingredient's causal contribution.

2026-10-17 E010 reviewed outcome: the frozen integrated workflow completes and all
native output contracts pass, with a separately retained Mac numerical-portability
limitation. Weighted conservative R95 pre 1.8763% /post 4.2909% remains below dev3
learned ten-depth 5.3911%; short bacterial neighbors improve while long/bp-weighted
geometry and coarse/mixed grouping remain concerns. The paired refinement helps
but adds 20.50 Mb unassigned. [Review](../../experiments/E010-coherent-prototype/review.json)
and [D015](../decisions/D015-coherent-prototype-upgrade.md) select preparation of one
cached CPM-versus-RB grouping-objective control, not another encoder/external fit.
Q001/Q003/Q005 remain open generally; this does not decide product feature families,
novelty or generalization. H001/E001 are unchanged. Oral-GSA confirmation stays
prospectively fixed and unacquired; next execution needs its own budget/credit gate.

2026-10-17: [E011](../../experiments/E011-cached-grouping-reference/README.md) freezes
one label-free CPM density rule on retained dev4 vectors/graph, holding actual
marker refinement fixed. Its source audit documents the seed prose discrepancy
and plausible representation risks without asserting a proven cause. One MetaBAT2
mean-depth reference adds an achievable-recovery/difficulty observation, not a
causal component claim or verdict on simulation quality. Keep Q001/Q003/Q005 and
feature-family conclusions open; confirmation/overlap admission stays separate.
The owner authorizes this bounded execution directly after gates.

E011 native attempt at ab80312 failed in the new library-provenance probe before
both community consumers. No new biological score or resolution of Q001/Q003/Q005
follows. [The failure and local repair](../../experiments/E011-cached-grouping-reference/native-observed.json)
retain successful setup, strict reuse and pending repaired Linux gates; another
explicitly authorized bounded attempt is the next execution, with no new mechanism.

2026-10-17 completed E011: [the review](../../experiments/E011-cached-grouping-reference/review.json)
finds that a frozen cached objective materially changes pre grouping (R95
1.8763 to 5.3990%), but paired refinement reduces it to 4.6171%; CPM's post gain
fails the prospective keep threshold. Four high-purity same-source parents split
on repeated markers at disjoint source spans; a local parent/child acceptance
control is the next selective question. The sole MetaBAT reference reaches
8.5493%, demonstrating better attainable recovery under these conservative
contracts, without a causal component or simulation-validity verdict. General
Q001/Q003/Q005 and H001/E001 conclusions remain open/unchanged. No product feature
family, optimality or SOTA claim; oral-GSA unacquired, October 21 review retained.

2026-10-17 prospective E012: retain CPM as the working development grouping
direction, preserving the failed E011 practical criterion. Test one local graph
CPM-gain guard on exact cached parent/child alternatives in RB/CPM contexts, with
a separate all-adopted-seed locus/call audit. Marker information remains a product
priority; duplicate removal alone is insufficient acceptance evidence. The
[frozen protocol](../../experiments/E012-marker-acceptance/protocol.json) predates
changed community selection/scores. No feature-family or generalization claim;
oral-GSA remains unacquired and October 21 storage review remains.

2026-10-17 E012 completed: the frozen local guard retains 16/18 RB splits (R95
4.5232% versus 4.2909%) and no CPM split, exactly protecting its 5.3990% parent.
Four targets recover losses but one useful marker split is forgone. This supports
protection within scope, without proving extra CPM marker benefit. Gene/domain
mapping distinguishes provided loci, partial/overlapping calls and unresolved
functional/reference specificity. [D015](../decisions/D015-coherent-prototype-upgrade.md#e012-observed-protection-and-next-coherent-upgrade-2026-10-17)
retains CPM and recommends one coherent marker-quality/context refinement upgrade.
Q001/Q003/Q005 remain open generally; no product feature-family, optimality or
SOTA conclusion. Source freezes/failures remain, oral-GSA unacquired and October 21
storage review unchanged.


2026-10-17 prospective E013: one coherent call-quality/proposal/context refinement
bundle on frozen CPM parents, with preserved E012 guard and old refinement controls.
The owner highlights marker value across communities and possible training limits;
neither is settled by this single assembly. Freeze the rule before changed scores,
then use the bounded local outcome to choose additional-data admission and the
next reviewed training/representation block, without requiring perfect refinement.
[Protocol](../../experiments/E013-marker-quality/protocol.json) owns exact criteria;
oral-GSA remains frozen/unacquired, October 21 review unchanged.

2026-10-17 E013 completed: [the frozen coherent refiner](../../experiments/E013-marker-quality/review.json)
selects five retained CPM proposals, raises weighted full-reference R95
5.3990→5.7388% with one target gain/no loss and protects the four formerly harmed
parents. More DNA becomes unassigned and restricted grouping recall/F1 fall
slightly; no new supported median proposal. Keep this provisional bundle rather
than declaring markers solved or disproved. Q001/Q003/Q005 remain open generally;
mixing, fragmentation and representation/objective limits remain unresolved.
[D015](../decisions/D015-coherent-prototype-upgrade.md#e013-outcome-and-next-trainingdata-block-2026-10-17)
chooses broader-data admission plus coherent multiview/reconstruction training
engineering as the next block, without requiring perfect refinement first.
Oral-GSA stays unacquired/unadmitted; no community fit, source-truth admission or
generalization claim follows. All accepted evidence/failures and October 21
storage review remain.

2026-10-18 E014: the coherent dev5 multiview/reconstruction candidate is
[implemented and locally exercised](../../experiments/E014-multiview-reconstruction/review.json),
with explicit measured-parent depth and unchanged CPM/E013 policy. Native tiny
training/reload/marker/grouping/refinement/export and the serial DAG pass, without
a changed community outcome. The quartet/approved source archive and every GSA
source interval verify; full799-genome oral denominators retain two zero-GSA
targets. Shared/identical DNA needs explicit origin-versus-identifiability truth
and a tested full-reference evaluator before fitting; truth remains provisional.
Exact/species overlap constrains generalization, not a claim that simulator data
are defective. Q001/Q003/Q005 remain open generally; no ingredient, feature-family,
performance or SOTA conclusion. [D015](../decisions/D015-coherent-prototype-upgrade.md#e014-implemented-bundle-and-source-admission-2026-10-18)
keeps the candidate fixed and finishes truth admission next. No cloud execution or
external expansion; oral stays sequence-only and October21 review remains.

Later E014 admission: [provided-source origin truth](../../experiments/E014-multiview-reconstruction/oral-truth-admission.json)
passes actual derivation/every-row independent review and five tiny evaluator
contracts. Unique-sequence support stays provisional; known-shared masking is a
separate sensitivity. Keep all799 targets, full DNA and localized non-ACGT support
quarantine. This permits the frozen paired comparison after native/financial
gates, without changing the candidate or making a performance claim.

E014 native release, 2026-10-18: all 15 Linux gates pass and the frozen three-fit
comparison is [running under supervision](../../experiments/E014-multiview-reconstruction/native-observed.json).
This changes execution status only; no community quality result or feature-family
conclusion yet. Retain both truth scopes and the unchanged October21 review.


2026-10-19 E014 completed: [the reviewed frozen bundle](../../experiments/E014-multiview-reconstruction/comparison-review.json)
passes native/byte/axes/reload/geometry/marker/DNA contracts but misses its improve-
both criterion. E009 conservative R95 is5.5196% versus retained5.7388%; oral
provided-origin R95 is6.2432% versus5.7242%. Bacterial/short-neighbor improvements,
length/grouping/assignment trade-offs and paired marker effects are separately
recorded, with full denominators and both quarantine policies. No metric pooling,
feature-family verdict or SOTA/causal ingredient claim. Q001/Q003/Q005 remain open.
D015 selects one zero-reconstruction condition to decide that block's value while
holding the rest fixed; no new fit is authorized by the completed inspection.
Both communities now serve development; independent confirmation still needs
prospective additional data/source/overlap/truth/protocol/cost admission. All
failed journals and dev3/dev4/dev5 stay preserved. VM is independently TERMINATED;
original$10 remains bounded and October21 storage review is unchanged.

2026-10-19 E015 completed: [the matched zero-reconstruction control](../../experiments/E015-zero-reconstruction/comparison-review.json)
passes native/input/exposure/reload/geometry/marker/DNA and all199return-member
contracts after explicitly approved collection-only recovery. Original failure
journals remain. Zero lowers E009 R955.5196→5.3329% but raises oral-origin post
6.2432→6.5548%, with target-count/assignment gains and oral parent/length-weighted
geometry/grouping trade-offs. The frozen modify criterion applies, not a universal
reconstruction verdict. Q001/Q003/Q005 remain open generally; no product-family,
optimality or SOTA conclusion. D015 selects one coherent positive-only online/
target learning candidate next, testing an unresolved negative-pair assumption
without claiming it is the cause. Both communities remain development; untouched
confirmation still requires prospective naming/protocol and full admission.
Final VM TERMINATED14:00:31UTC; no scientific replay or retention/resource change.
OriginalE015$2 covers~$0.639 including stopped gap/<$0.80with reserve. October21
storage review remains; next paid work needs a fresh separately authorized scope.


2026-10-20 prospective E016: [one coherent positive-only learner](../../experiments/E016-positive-only-multiview/README.md)
now implements the next D015 hypothesis using original real within-parent views,
explicit composition/depth branches and a stoppedEMA target. Co-genomic negative
repulsion is unproven; actual local target/gradient/noncollapse/reload/full-DNA
contracts pass, native two-fit development comparison remains gated. The owner
prioritizes gap closure and decision-relevant coherent upgrades over a default
sequence of small loss controls. Keep broader window/context/GLM/marker-aware/
information-aware grouping alternatives live; new outcomes will choose one next
block. Skin pooled GSA is prospectively selected with metadata only; source/truth/
overlap/denominator/cost admission remains, no confirmation payload acquired.


2026-10-20 E016 reviewed: [positive-only bundle](../../experiments/E016-positive-only-multiview/comparison-review.json)
meets its scoped KEEP rule: E009/oral-originR955.8219/6.7719%, both aboveE014,
oral+0.5287pp and >=90%counts4/34. Full156/799denominators/N-quarantine/known-shared
sensitivity and every length/origin/marker/eligibility/assignment population remain.
Bacterial/oral neighbors worsen and more DNA becomes unassigned; oral's unchanged
E013 refiner contributes a large lift from4.6429%, while E009's R95 is unchanged by
refinement. Q001/Q003/Q005 remain open: no false-negative causal conclusion,
family verdict, independent confirmation or uniform advantage. Keep E016 as a
provisional recovery anchor, no product-default change. D015 chooses a coherent
length-aware multi-evidence grouper/core/short-recruitment block next, holding
learning fixed and explicitly weighing context/GLM/marker training. No new science
runs here; skin remains unacquired. All failures/source freezes remain; October21
retention decision and separate future-execution authorization are still needed.


2026-10-20 E017: [one coherent information-aware grouper](../../experiments/E017-information-aware-grouping/README.md)
is locally implemented on fixed E016 learning, addressing the unresolved
information-use/fragmentation/short-DNA question. Native whole-tool cutoffs,
recruitment and learner eligibility are explicitly separated; no accepted score
or full denominator changes. Tiny engineering contracts and synthetic throughput
are not biological evidence. The new cached comparison remains separately
unauthorized, with prospective criteria and full paired/population diagnostics.
Q001/Q003/Q005 remain open. Context/GLM/marker-aware alternatives and untouched
skin confirmation remain; source/overlap/truth/protocol/cost admission still
precedes confirmation. Fresh storage-only approval resolves October 21 through
October 28 at 00:00 Copenhagen, without compute, new resources or deletion.

2026-10-21 E017 execution: the owner separately authorizes the single cached
comparison under a new $2. [Native admission](../../experiments/E017-information-aware-grouping/native-observed.json)
passes all nine gates and releases the sole DAG under verified supervision,
holding E016 learning fixed. This moves the scoped question into testing; no
community quality result or scientific resolution is yet admitted.


2026-10-21 E017 reviewed: [fixed-learning information-use bundle](../../experiments/E017-information-aware-grouping/comparison-review.json)
is mixed (MODIFY): E009 post R95 5.8219 → 7.5284%, oral-origin 6.7719 → 4.9664%,
>=90% targets 4 → 8 / 34 → 21. All DNA/full denominators/N-quarantine remain;
large unassignment and oral core mixing are explicit. Q001/Q003/Q005 stay open.
D015 selects one cached vote-led/profile-admissibility control because retained
existing gate overlap exposes competing rankers; no rule/score/encoder change or
new cloud job is executed in inspection. Larger context/GLM/marker-learning
alternatives remain, with untouched skin admission and October 28 retention visible.


2026-10-21 — E018 prospectively freezes the owner-authorized single cached
vote-led/profile-admissibility acceptance control, preserving E016 learning and
E017 cores/profiles. [Its assessment](../../experiments/E018-vote-led-recruitment/robustness-and-data.md)
treats oral regression as a robustness problem with unisolated depth/community/
assembly/truth causes. Sequence-only remains valid for this acceptance question;
current depth benefit, measured-depth transfer and untouched-community robustness
remain open. Genuine oral mapping and additional-data admission are separately
costed, not silently added. No new scientific outcome yet.


2026-10-21 — [E018 completed](../../experiments/E018-vote-led-recruitment/README.md):
ABANDON the sole vote-led/profile-admissibility acceptance policy. All contracts
pass, but post R95 and >=90% target counts fall in both communities despite less
unassigned DNA. Some targets/B3/old-refinement diagnostics improve; preserve the
full paired trade-off without tuning. Original E017 protection remains useful,
E017 MODIFY and E016 anchor stay. This does not isolate depth, settle architecture
families or show a coding failure. Next is one coherent window-context composition/
information learner as the previously leading later route, with local engineering
and separately priced future execution. Untouched skin and current-system depth
questions retain explicit admission/cost/retention dependencies; no new DNA/cloud.


2026-10-22 — [E019](../../experiments/E019-window-context/README.md) implements the
prospectively selected compact window-context information/encoder block locally.
Q001/Q003/Q005 remain open: attention plus local tokens/fusion is a bundle, and
no community quality/transfer outcome exists. E016 learning and CPM/E013 anchor
the first separately priced comparison; all earlier results/failures remain.
Engineering fixtures do not prove full-schedule stability/affordability; native
rank/resource/credit/source gates precede community work. No score/grid/refit or
new data occurs. A frozen GLM may complement context; skin and oral depth keep
separate source/truth/cost/retention admissions. October 28 storage remains.


E019 execution update, October 22, 2026: the coherent context question above now
has one newly authorized comparison [released after all ten native gates](../../experiments/E019-window-context/native-observed.json).
No community result yet. Keep the original hypothesis/criteria and E016 comparator;
no score-driven tuning, confirmation or product-family decision follows.


E019 inspected resolution, October 23, 2026: [the frozen comparison](../../experiments/E019-window-context/comparison-review.json)
is MODIFY. Local/global context improves conservative E009 R95 (5.8219 ->7.3058%)
and parent recovery in both scopes, but oral final origin R95 declines (6.7719 ->
6.5077%). Keep all trade-offs and development/portability/truth limits. The next
question is one fixed-learning integration with original E017 grouping/E013, not
additive gain assumed from two partial results, a threshold grid or an automatic
larger model. New proposed $1 requires separate authorization/fresh gates. Skin
remains frozen/unacquired pending source/truth/overlap/protocol/cost admission;
October 28 storage boundary remains.


E020 prospective integration, October 23, 2026: [the owner-authorized cached block](../../experiments/E020-context-information-integration/README.md)
tests whether fixed E019 learning benefits from every original E017 grouping rule
with E013 unchanged. No new community outcome yet. Keep original criteria and both
scopes, full populations and negative evidence; no assumption of additive gains,
product-default promotion or new information-family conclusion. Skin remains
unacquired; fresh execution/credit/source/headroom/retention gates still apply.


E020 execution update, October 23, 2026: [all seven Linux gates pass](../../experiments/E020-context-information-integration/native-observed.json),
and the one cached integration is released under verified fresh supervision.
This moves the prospective interaction question into testing, not resolution.
No recovery outcome or default/promotion claim yet; all immutable baselines,
full truth/population contracts and October 28 storage boundary remain.


E020 inspected resolution, October 23, 2026: [the completed comparison](../../experiments/E020-context-information-integration/comparison-review.json)
is **MODIFY** with E009 final R95 +0.2357 points / >=90% 7 -> 8, oral origin -0.8389
points / 33 -> 27. All contracts/target populations pass and no demonstrated adapter
or missing-depth bug explains the trade-off. E013 rescues weak oral parents; learned
neighbors are fixed and assignment/B3 trade-offs persist. The integration question
is answered in scope, without promoting a universal policy. Q001/Q003/Q005 remain
open. Next propose one frozen pretrained-sequence/context/depth hybrid with untouched-
skin admission in parallel, ordinary E019 downstream retained. E003's failed short-
neighbor criterion remains contrary evidence, not a family veto. No new score/grid,
fit, data, VM/resource or retention change in inspection. Skin source/genome/replicon/
molecule/taxonomy/overlap/ambiguity/origin-vs-unique truth and prospective candidate/
protocol/cost still require admission; no unseen-genome or product-family conclusion.


E021 local update, October 23, 2026: [the view-exact frozen-sequence hybrid](../../experiments/E021-frozen-sequence-hybrid/README.md)
is implemented with actual local extraction/train/reload/marker/graph/export and
strict source/cache contracts. Q001/Q003/Q005 remain open; no new community quality
result or feature-family conclusion. CPU full-scale throughput/RAM/space gates
are unadmitted despite trial balance; proposed GPU native admission is separate.
Five-file skin audit admits only a full-denominator origin oracle (610 targets,
one zero origin); 313 complete provided inventories match oral-observed genomes.
Keep all populations/overlap/ambiguity/host limits and original frozen skin choice,
with separate evaluator/confirmation cost scope. No skin fit/score or cloud job;
October 28 retention remains. This block moves complementary information into
engineering readiness, not scientific support.


E021 inspected resolution, October 25, 2026: [full E009-only review](../../experiments/E021-frozen-sequence-hybrid/comparison-review.json)
is MODIFY, not a GLM-family decision. Weighted R95 gains 0.51165 points but >=90%
counts fall 7 -> 6; 10 gains / 15 losses and one 3.112 Mb target dominates. Original
joint KEEP is unmet; oral/skin unrun. All native contracts pass, with a preserved
operational failure repaired before the sole fit. Q001/Q003/Q005 remain open.
D015's next coherent block is reliable marker-informed cross-contig learning on
retained caches: source/context-supported constraints with abstention, no naive
repeated-family hard negatives or truth-selected pairs. No new fit/score/confirmation
is authorized by the local preparation prompt. Frozen skin source/origin/unique/
overlap/evaluator/resource limits and October 28 retention remain explicit.
