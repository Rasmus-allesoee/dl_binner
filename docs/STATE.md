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
[architecture reassessment](evidence/2026-09-30-architecture-reassessment.md)
replaced that recommendation with lightweight contrastive learning and a bounded
frozen-GLM inclusion screen. E003 now resolves the first sequence route below.
Thesis results and full short-contig scope receive explicit weight.

## Exact next step

**E002 feasibility and E003's final representation screen are complete and
accepted; do not repeat either inference run.**
[E003](../experiments/E003-representation-screen/README.md) owns the precommitted
protocol, new source/panel hashes, independent retained-output inspection and
actual costs. Sixteen human-associated reference chromosomes supplied 320
nonoverlapping fragments / 945,152 bp, balanced across 500/768/1,000/2,500/10,000 bp.
Native feature axes, masks, chunks, finite arrays, neighbors and all scores passed
inspection; completed-directory Snakemake dry-run schedules nothing.

Frozen GLM has **better sampled-fragment grouping**, but fails the joint keep
criterion: short five-neighbor purity 0.45938 versus raw TNF 0.57396 (−0.11458,
required +0.10). Longer neighbor delta +0.00469 and bp-weighted grouping F1 gain
+0.06863 pass. GLM short grouping F1 0.32558 versus 0.01978 and assigned fraction
0.91146 versus 0.06771 are substantial positive evidence; do not describe TNF as
universally better. All operational ceilings passed: 940.014 s total, sampled
peak RSS 1.436 GB, four-thread budget. Deferral follows the precommitted utility
rule, **not laptop runtime projections**. No trained-composition or whole-MAG
comparison/generalization claim follows; pretraining overlap is not excluded.

**Implement and locally run D011's first end-to-end learned binner:** our own
compact contrastive encoder using 136-dimensional composition, explicit optional
mean-depth inputs, one fixed label-blind clusterer and complete assignment/bin
exports. [D011](decisions/D011-first-binner-prototype.md#exact-next-milestone-first-learned-binner)
fixes the initial learning settings, software contracts and acceptance boundary.
Commit package/config/transform contracts before measured integration. Demonstrate
train→save→reload→embed→cluster→export using accepted E003 TNF cache, alongside the
raw-feature control, with tiny real fresh-feature checks and meaningful failure
tests. Retain all length strata, noise, zero-depth masks and exclusion reasons;
labels must not enter training or selection. Synthetic depth tests establish input
contracts only. Four threads, loader zero, 8 GB and a two-hour first integration
ceiling; separate prototype environment. No superiority requirement for software
acceptance and no further architecture gate unless a concrete failure requires one.

No owner upload or UCloud command is needed now. Frozen GLM weights/features remain
retained, deferred from the first prototype rather than globally rejected. The
completed 2026-09-30 review/source audit is reused. No full-GLM training, VAE
curriculum, additional architecture campaign or E001 rerun is planned. E001's
2,500-bp cutoff and the thesis's 2,000-bp filter are not product constraints. The
first configurable 500-bp default is an engineering choice; independent real-
assembly/whole-genome and unsupported-length evaluation remain future work.

## Resources and continuity

COMEBin successful conditions used 39.6462 allocated core-hours; the known recovery
sequence lower bound is 58.1075. MetaBAT2/VAMB pair: 0.76946. The new collection
adds 0.002224 (1 vCPU / 4 GB, 8.0065 driver seconds). These are partial accounting,
not exact billing or a remaining-balance estimate. Successful COMEBin condition
files total 11.313 GB; the diagnostic archive is an additional 235.13 MB copy.
Preserve retained assets/old attempts. No deletion is authorized.

E003 retains 98 local files / 41.34 MB at acceptance, with a committed hash
inventory; no extra model/environment copy. Its 1.04446 four-thread wall hours
are local budget accounting, not UCloud charges. Sampled CPU/RSS receipts own
interpretation because local extended-benchmark CPU/RAM fields are incomplete.
Source acquisition/setup and analysis are outside the scientific driver clock;
local retained files are not a remote backup.

UCloud remains CPU-only and owner-operated. Persistent prefixes stay under
`e001-gate0/envs/` per [D006](decisions/D006-environment-ownership.md). Frozen E001
source/configuration and raw observed records remain unchanged.

Local branch: `first-binner-prototype`, created from `930e6743eac1aadb93ea23b51f2a6ac617155a2e`.
Owner-configured private GitHub origin is present; main/origin-main initially matched
that commit. This task makes local commits only. `agent_context/` is an ignored
inbox. Before public publication review licensing and historical source packaging
per [D001](decisions/D001-research-record.md). Update this handoff when direction,
significant evidence or execution dependencies change; details belong to their owners.
