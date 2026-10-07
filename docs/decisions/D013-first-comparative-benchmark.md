# D013: one bounded competitive assembly baseline before improvements

Date: 2026-10-08. Status: **accepted planning decision**; execution unstarted.
Owner authorizes analysis, a new branch and local commits; not UCloud execution,
architecture implementation, private push/PR or public release in this task.

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
Overlap must be inventoried before scoring and retained in claims.

CAMI II GI is accepted development evidence; another HMB site offers transfer
later but shares old source populations/plumbing. Toy III offers a more current
gut community without active-challenge restrictions. The active III challenge has
no verified public local truth/assembled input at this cutoff, scheduled assemblies
on October 15 and restricted pre-release participation terms; defer it. Custom
CAMISIM remains a targeted mechanism instrument after a real observed deficit,
not extra setup for a question public reads can answer. A GSA-only comparison would
be cheaper but would repeat the main E005 realism limitation.

Preserve dev3 main as immutable baseline. Run matched raw/learned **TNF+two-depth**
and **TNF-only** pairs with unchanged settings/seed 11. The secondary pair is a
small justified information ablation, not a new architecture. Native external
shortlist: **SemiBin2, MetaCAT core, SCGBinner**, plus **CompleteBin conditional on
native CPU/payload affordability before scoring**. No unplanned replacement list.
This balances a mature short-read reference, distinct non-neural grouping and the
owner's strongest biological-constraint interest. CompleteBin retains the thesis
priority, with honest CPU feasibility instead of assuming that CPU availability
or thesis GPU timing proves affordability.

COMEBin's directly measured quality/source/selection evidence is reused; its full
CPU grid was expensive even at E001 scale and largely overlaps the initial
contrastive/marker comparison. Defer a fresh larger fit. DCVBin remains a sequence
candidate with unresolved published-recipe/payload/coverage parity; LorBin adds
long-read/quality-model dependencies. They remain studied, not globally inferior.
VAMB/MetaBAT2 would be cheap familiar controls but add less new mechanism evidence
than this shortlist; they do not replace the newer tools merely for convenience.

## Cost and decision limits

Use local Mac for small adapter/evaluator checks and returned-output analysis;
UCloud CPU/Linux for bulk acquisition, assembly, mapping and tool fits. Plan an
8-vCPU/24-GB bounded preflight, then 16-vCPU/48-GB serial scientific work, with
explicit child/loader/OpenMP reconciliation and measured admission projections.
Native schedules remain native; no shortened training disguised as parity.
The prospective total ceiling is 500 allocated core-hours / 200-GB new storage,
including failures/setup/collection; current remaining credit is unknown. These
are experiment choices, not product maxima or a promise the runs consume the cap.
Budget/scale failures cause evidence retention and prospective reassessment, not
silent data filtering, quota increases or automatic repairs/retries.

Use AMBER on its validated contig truth view and alignment-supported conservative
whole-reference recovery with all-bin purity denominators and duplicate-safe
coordinate unions. Keep assembly-conditional recovery separate. Real-assembly
truth adapters still require implementation/native tests; E005's GSA evaluator
cannot be applied unchanged. Whole *provided reference* recovery is not formal
MIMAG quality or completeness of an unknown finished genome when a source is a MAG.

If learning damages raw signal, prioritize one view/negative-construction change;
if embeddings separate but bins fail, prioritize one grouping/refinement ablation;
if short-sequence information remains limiting, the planned matched TNF/GLM-head/
hybrid comparison is a strong next candidate. Its complementary-information
rationale is retained, not assumed proven. Do not adopt several mechanisms from
one native-tool victory or tune to E009 and claim held-out validation.

## Boundary and exact next action

E009 is prospective, with no scientific results or executable transfer accepted.
Implement/test acquisition/overlap/assembly/depth/truth and runtime adapters,
then prepare one checksum-bound **8-vCPU/24-GB ≤5-hour owner preflight**.
The owner runs UCloud; Codex reviews returned evidence before scientific admission
and the subsequent 16-vCPU command. Freeze actual sources/manifests/native settings
and code before scores. No accepted science is rerun, no architecture comparison
executes, and this is not another gate on the already merged product.

Owner direction enters a second development chapter: the stable prototype is
the control; comparative evidence should select incremental improvements. Data
inspected for those choices become development data. Later independent validation,
GPU/Conda distribution and publication remain separate tasks.
