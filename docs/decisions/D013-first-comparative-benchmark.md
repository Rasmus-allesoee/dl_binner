# D013: one bounded competitive assembly baseline before improvements

Date: 2026-10-08; amended 2026-10-09. Status: **accepted preparation decision**; scientific execution unstarted.
The original authorization was preparation only. On 2026-10-13 the owner selected
GCP after SDU access deactivation and authorized phase-1 workspace setup plus
normal private branch push; [D014](D014-google-cloud-workspace.md) owns that change.
No benchmark scientific execution or v14 return review is authorized in that
phase. Old UCloud budgets/paths are historical. After setup/return admission,
resolve **10 versus 20 read samples** for the one-assembly design and amend ordered
axes/costs before bulk acquisition. The original two-source protocol remains
source history, not the final expanded-sample choice. No scientific baseline,
architecture, eligibility or evaluator is changed here.

## Problem and evidence

The usable first CPU prototype is merged and tested, but E003/E004 are controlled
development fragments and E005 is a four-genome development GSA derivative.
Independent read-derived whole-reference/binning quality and assembly-scale costs
remain unknown. We need a useful native-tool gap assessment before attributing
performance to fashionable architectures or copying a complex pipeline.

Reuse the completed review/source audit and accepted E001–E008 records.
[The October focused study](../evidence/2026-10-08-competitive-binner-study.md)
separates inputs/pretraining, learning objective, network architecture and
grouping/refinement for all seven owner-ranked tools. It identifies actual sequence
views/negative handling, biological grouping and sequence context as serious
alternatives, with source and evidence limits explicit. A tool ranking is not a
causal component experiment. Our binner's inferiority is a hypothesis to measure,
not a software acceptance finding or universal family conclusion.

## Choice and alternatives

Prepare [E009](../../experiments/E009-competitive-benchmark/README.md): one actual
MEGAHIT assembly from **CAMI III Toy Longitudinal Human Gut short-read sample 0**,
with sample 0/1 measured depth on that same reference (verified subject S1).
Keep the full community, short strata, native eligibility, masks, discarded/noise
DNA and all whole-reference failures. This is a public-toy derivative, not an
official challenge score. New samples do not establish genome/pretraining independence.
Overlap must be inventoried before scoring and retained in claims. The October 9
[input/runtime reconciliation](../evidence/2026-10-09-e009-contract-reconciliation.md)
directly inspects both complete sample-0 archives: `contigs` is anonymized GSA
plus origin mapping; `gsa` contains per-genome reference-coordinate intervals.
CAMISIM's anonymization/GSA source explains that relationship. Neither is a
traceable de novo assembly; MEGAHIT remains necessary for the chosen question.

CAMI II GI is accepted development evidence; another HMB site offers transfer
later but shares old source populations/plumbing. Toy III offers a more current
gut community without active-challenge restrictions. The active III challenge has
no verified public local truth/assembled input at this cutoff, scheduled assemblies
on October 15 and restricted pre-release participation terms; defer it. Custom
CAMISIM remains a targeted mechanism instrument after a real observed deficit,
not extra setup for a question public reads can answer. A GSA-only comparison would
be cheaper but would repeat the main E005 realism limitation.

Preserve dev3 main as immutable baseline. Run matched raw/learned **TNF+two-depth**
and **TNF-only** pairs with unchanged settings/seed 11. Learned TNF plus measured
depth is the primary product. Raw and sequence-only runs are inexpensive diagnostic
controls, not product alternatives or another architecture gate. Their separate
cost ceiling is 16 core-hours. Execution shortlist: **SemiBin2, MetaCAT core,
SCGBinner, COMEBin**, plus **CompleteBin with a modified maximum of 50 epochs**;
all need measured Linux/scale admission before full fitting. No replacement list.
This balances a mature short-read reference, distinct non-neural grouping and the
owner's strongest biological-constraint interest. CompleteBin retains the thesis
priority, with honest CPU feasibility instead of assuming that CPU availability
or thesis GPU timing proves affordability.

COMEBin's directly measured E001 quality justifies a new whole-tool comparison on
the same assembly; overlapping mechanisms do not make that comparison redundant.
Reserve its full 120-candidate grid, without repeating E001. CompleteBin's epoch
cap is an owner-requested scientific configuration change, not upstream parity;
retain native automatic pretraining/eligibility decisions and any lower safety cap.
DCVBin's payload is available, but its basic VAE runner unconditionally requests
CUDA, takes one BAM and defaults to 200 VAE epochs; enhanced training is a separate
GPU-oriented recipe. A CPU/pair-depth repair would be substantial additional tool
development here, so **DCVBin does not join E009**. Coverage is useful input and
not a disadvantage. Frozen-GLM comparison remains planned separately. LorBin adds
long-read/quality-model dependencies. They remain studied, not globally inferior.
VAMB/MetaBAT2 would be cheap familiar controls but add less new mechanism evidence
than this shortlist; they do not replace the newer tools merely for convenience.

## Cost and decision limits

Use local Mac for small adapter/evaluator checks and returned-output analysis;
UCloud CPU/Linux for bulk acquisition, assembly, mapping and tool fits. Plan an
8-vCPU/24-GB bounded preflight, then 16-vCPU/48-GB serial scientific work, with
explicit child/loader/OpenMP reconciliation and measured admission projections.
Schedules remain native except the named CompleteBin-50 modification.
The prospective total ceiling is **700 allocated core-hours**, including
failures/setup/collection, against the owner's approximately **1,980** balance:
**1,280 core-hours remain outside E009's ceiling**. This replaces the 500-hour plan
to fund the same-dataset COMEBin grid. The former 200-GB figure is a provisioning
estimate, not an experiment cap or permission to delete/filter data. Keep Home
code/environments/transfers/logs separate from bulk reads/BAMs/source/temporary data
in the project's own shared-storage E009 subtree; never touch colleagues' files. These
are experiment choices, not product maxima or a promise the runs consume the cap.
Budget/scale failures cause evidence retention and prospective reassessment, not
silent data filtering, quota increases or automatic repairs/retries.

Use AMBER on its validated contig truth view and alignment-supported conservative
whole-reference recovery with all-bin purity denominators and duplicate-safe
coordinate unions. Keep assembly-conditional recovery separate. Real-assembly
truth adapters now pass real small-DNA local tests, with Linux/scale unvalidated; E005's GSA evaluator
cannot be applied unchanged. Pin minimap2's all-chain PAF/CIGAR output for the
narrow adapter instead of depending on MetaQUAST's filtered internal alignments;
MetaQUAST remains a possible supplemental misassembly report. Whole *provided reference* recovery is not formal
MIMAG quality or completeness of an unknown finished genome when a source is a MAG.

Marker-aware grouping/refinement is a **high-priority** next product candidate:
it directly addresses the accepted prototype's fragmented grouping, preserves the
encoder and can reuse embeddings. Plan one fixed marker-conflict splitting/merging
ablation against identical frozen grouping, retaining marker-negative and short
DNA and evaluating with independent sequence truth. Marker-aware training remains
a serious alternative, not an automatic simultaneous addition.

If learning damages raw signal, prioritize one view/negative-construction change;
if embeddings separate but bins fail, prioritize one grouping/refinement ablation;
if short-sequence information remains limiting, the planned matched TNF/GLM-head/
hybrid comparison is a strong next candidate. Its complementary-information
rationale is retained, not assumed proven. Do not adopt several mechanisms from
one native-tool victory or tune to E009 and claim held-out validation.

## Boundary and exact next action

E009 is prospective, with no scientific results. Preparation does not authorize a job.
Implemented/local-tested acquisition/overlap/assembly/depth/truth and runtime
adapters now prepare one checksum-bound **8-vCPU/24-GB ≤5-hour owner preflight**.
The owner runs UCloud; Codex reviews returned evidence before scientific admission
and the subsequent 16-vCPU command. Freeze actual sources/manifests/native settings
and code before scores. No accepted science is rerun, no architecture comparison
executes, and this is not another gate on the already merged product.

Owner direction enters a second development chapter: the stable prototype is
the control; comparative evidence should select incremental improvements. Data
inspected for those choices become development data. Later independent validation,
GPU/Conda distribution and publication remain separate tasks.
