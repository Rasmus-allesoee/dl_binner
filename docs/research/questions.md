# Questions and Hypotheses

Updated: 2026-10-03

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
