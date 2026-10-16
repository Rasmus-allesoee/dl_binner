# Questions and Hypotheses

Updated: 2026-10-08

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
