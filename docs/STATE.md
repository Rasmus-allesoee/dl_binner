# Current Research State

Updated: 2026-10-05. This is the single current handoff.

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

**E004's first native learned binner is complete and accepted.**
The installable package provides FASTA/optional explicit mean-depth inputs, our own
25,792-parameter contrastive encoder, fitted transforms, checkpoint inference,
fixed label-blind clustering and complete assignment/bin FASTA exports.
[E004](../experiments/E004-first-binner/README.md) owns source/config/input hashes,
all-stratum scores, independent retained diagnostics and actual resource receipts.
Source/contracts were committed at `7b24a6b` before the single measured run.
Accepted E003 TNF was reused; no E002/E003 inference was repeated. Reload matched
exactly; both export paths preserve all 320 IDs/DNA; raw control matches E003.
Completed-workdir dry-run schedules nothing. Thirteen focused checks and the real
fixture DAG, fatal-input/repeated-invocation/resume checks pass without worker mocks.

Utility is **mixed**, not a whole-MAG claim: bp-weighted grouping F1
0.30801→0.42455 and short F1 0.01978→0.26065, but short-neighbor purity
0.57396→0.42604 and bp-weighted precision 0.53209→0.44150 decline. Learned output:
17 bins, 305 assigned / 15 noise. No constant collapse; retrospective batches have
6.0124% co-genomic negative-ID pairs, a plausible contributor with causation
untested. No truth tuning/retraining or new architecture gate. Coverage has input/
mask tests only, with no biological benefit measured. Native Mac only; no Linux
or assembly-scale throughput/quality validation. Scientific driver 17.797 s,
0.411-GB sampled peak, 1.227 average CPUs under four-thread caps; learning itself
0.595 s / 2.401 CPUs. Startup/serial work dominates, so caps do not imply full use.

**E005 prepares the next owner-controlled CPU/Linux smoke job and freezes one
capped human-associated assembly/explicit mean-depth pilot.**
[D011](decisions/D011-first-binner-prototype.md#next-bounded-product-validation-after-e004)
owns the scope: freeze data/overlap/evaluation/resource contracts, retain raw
controls, shorts/masks/noise, validate native runtime/stage costs before increasing
input size. [E005](../experiments/E005-linux-pilot/README.md) owns the offline runtime/
smoke source, input hashes, local tests and bounded pilot protocol; its
[operations guide](../experiments/E005-linux-pilot/OPERATIONS.md) owns the exact
four-vCPU/12-GB Terminal command and return procedure. Codex must not execute
UCloud. These check the implemented product's untested contracts rather than add
an architecture selection gate. No automatic E001 rerun or new seed.

The owner requests a **future non-blocking** comparison of learned TNF, frozen GLM
plus a contrastive head, and TNF–GLM hybrid with the same objective, even if this
prototype works. [D011](decisions/D011-first-binner-prototype.md#planned-non-blocking-learned-representation-comparison)
records its concrete rationale and matched bin-quality/resource requirements.
Planned only, not implemented/run in E004 and not a release prerequisite.

**Exact next step: owner runs only the E005 Linux smoke and returns its archive,
checksum and automatically captured terminal log for inspection.** Native Linux
validation is pending; the driver cannot launch the pilot. The pilot is frozen at
four GI GSA genomes / 5,309 contigs / 12,924,259 bp, with 1,097 below-500 contigs
retained as exclusions in the full denominators. It overlaps E001's community and
1,332 retained IDs, so remains a controlled development derivative. Ordered samples
1 and 4 supply capped retained-read subsets mapped to this exact reference in a
later tested command. Existing E001 depth has no short rows and must not be zero-
filled. AMBER/R95 with raw controls is fixed; no mapping/feature/training/scoring
of this pilot has run. After smoke review, implement/test only the remaining
sampling/mapping/mean-depth/evaluation adapters and prepare its owner command.
Frozen GLM weights/features remain
retained, deferred from the first prototype rather than globally rejected. The
completed 2026-09-30 review/source audit is reused. No full-GLM training, VAE
curriculum, automatic architecture campaign or E001 rerun is planned. E001's
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

E004 retains 93 run files / 2.94 MB, plus its isolated environment, package wheel
and setup/fixture logs. Actual four-thread scientific wall budget is 0.0197744
hours, not UCloud charges; setup/tests/review excluded. Keep all artifacts and
accepted E001/E002/E003 snapshots. The receipt-helper path repair affects only
post-run collection; native scientific source/functions remain frozen.

UCloud remains CPU-only and owner-operated. E001's persistent prefixes stay under
`e001-gate0/envs/` per [D006](decisions/D006-environment-ownership.md); E005 owns
separate new CPU/workflow prefixes under its own root. Frozen E001
source/configuration and raw observed records remain unchanged.

Local branch: `first-binner-prototype`, created from `930e6743eac1aadb93ea23b51f2a6ac617155a2e`.
Owner-configured private GitHub origin is present; main/origin-main initially matched
that commit. This task makes local commits only. `agent_context/` is an ignored
inbox. Before public publication review licensing and historical source packaging
per [D001](decisions/D001-research-record.md). Update this handoff when direction,
significant evidence or execution dependencies change; details belong to their owners.
