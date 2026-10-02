# Current Research State

Updated: 2026-10-03. This is the single current handoff.

## Direction and completed work

Build and publish a usable deep-learning metagenomic binner while learning through
implementation. A paper, novelty and SOTA remain optional. See
[PROJECT_INTENT](../PROJECT_INTENT.md), [D010](decisions/D010-bounded-e001-and-prototype.md)
and [D011](decisions/D011-first-binner-prototype.md).

**E001 is closed at its approved amended seed-11 scope.** The diagnostic collection
passed checksum and all 297 retained-file checks. All 240 COMEBin candidates,
marker scores, embedding axes and fixed neighborhood/length diagnostics were
inspected directly. [Closure](../experiments/E001-coverage-thinning/closure.md)
owns results and limitations. The original three-seed criterion and H001 remain
unresolved; seeds 23/47 stay deferred. No accepted preprocessing, feature extraction,
training, clustering or collection should be repeated.

Primary R95 C0→CT: MetaBAT2 0.44294→0.19502; VAMB 0.46177→0.48764;
COMEBin 0.83899→0.80255. COMEBin CT has a 0.03862 truth-best candidate-selection
gap; C0 has zero. Learned short-contig neighborhoods remain better on average than
combined raw features, although localized losses exist. These are one-community
single-seed development observations, not a validated intervention.

The required [current literature/benchmark review](evidence/2026-09-30-binner-design-review.md)
and [source audit](evidence/2026-09-30-design-source-audit.json) are completed at the
2026-09-30 cutoff, with depth/access limits explicit. They considered reconstruction,
contrastive, graph, taxonomy, pretrained sequence and efficient neural merging
before the initial compact-VAE recommendation. The owner-requested
[architecture reassessment](evidence/2026-09-30-architecture-reassessment.md) now
replaces that recommendation: lightweight contrastive learning is the leading
default, with sequence encoder choice provisional and frozen GLM features kept
as a serious candidate. Thesis results and full short-contig scope receive explicit weight.

## Exact next step

**D011's frozen-DNABERT-S CPU spike is complete and accepted at local scale.**
[E002](../experiments/E002-dnabert-s-feasibility/README.md) owns checkpoint/runtime
pins, failures, native contracts, actual costs and projection limits. Unmodified
author model on forty real-DNA windows: 182.852 s, peak sampled RSS 1.314 GB,
warm CPU use 3.41–3.88 under four-thread caps. All native extraction/cache/reload
checks passed. One input-only IUPAC validator defect was corrected before model
loading; failed receipt retained. No accepted inference should be repeated.

Prepare and run **one small GLM versus inexpensive composition representation
comparison**, at most 320 fragments on new short-inclusive human-associated
development sources. A controlled genome-fragment panel is sufficient. Around
1 Mb (64 windows at each tested length: 945,152 bp) projects to ~14.2 minutes
extraction. Freeze population/accession/hash/overlap records, nonoverlapping sampling,
metrics, fixed clustering, keep/defer criteria and cost **before scores**. Use
≤4 threads / 8 GB; one-hour feature ceiling and two-hour total local-run ceiling.
Keep all length strata and unassigned outcomes, without oracle K, truth selection
or a tuning grid. Then settle one encoder and complete the small end-to-end product.

Technical feasibility is not bulk affordability: explicit 29.536-Mb and 817.438-Mb
scenarios project to 7.394 and 229.016 local wall hours, with substantial uncertainty;
no Linux/CPU-scaling claim. Lightweight contrastive learning remains the leading
default; GLM must justify its cost through the sole bounded comparison. The
[updated D011](decisions/D011-first-binner-prototype.md) owns the decision. No
full-GLM training, additional architecture campaign or VAE curriculum is planned.

No owner upload or UCloud command is needed now. No E001 run is reopened. Its
2,500-bp cutoff and the thesis's 2,000-bp filter are not product constraints. New
short-inclusive public/simulated development data may be used; eligibility and
claims must be evaluated separately, not extrapolated from E001. No full GLM
pretraining/fine-tuning or expanding benchmark campaign is the next milestone.

## Resources and continuity

COMEBin successful conditions used 39.6462 allocated core-hours; the known recovery
sequence lower bound is 58.1075. MetaBAT2/VAMB pair: 0.76946. The new collection
adds 0.002224 (1 vCPU / 4 GB, 8.0065 driver seconds). These are partial accounting,
not exact billing or a remaining-balance estimate. Successful COMEBin condition
files total 11.313 GB; the diagnostic archive is an additional 235.13 MB copy.
Preserve retained assets/old attempts. No deletion is authorized.

UCloud remains CPU-only and owner-operated. Persistent prefixes stay under
`e001-gate0/envs/` per [D006](decisions/D006-environment-ownership.md). Frozen E001
source/configuration and raw observed records remain unchanged.

Local branch: `first-binner-prototype`, created from `930e6743eac1aadb93ea23b51f2a6ac617155a2e`.
Owner-configured private GitHub origin is present; main/origin-main initially matched
that commit. This task makes local commits only. `agent_context/` is an ignored
inbox. Before public publication review licensing and historical source packaging
per [D001](decisions/D001-research-record.md). Update this handoff when direction,
significant evidence or execution dependencies change; details belong to their owners.
