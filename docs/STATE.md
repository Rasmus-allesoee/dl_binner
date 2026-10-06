# Current Research State

Updated: 2026-10-06. This is the single current handoff.

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

**E005's native Linux smoke and v5 GI assembly/depth pilot are complete and
accepted.** [The independent pilot review](../experiments/E005-linux-pilot/README.md#accepted-v5-native-gi-pilot-and-independent-review-2026-10-06)
and [receipt](../experiments/E005-linux-pilot/pilot-observed.json) verify checksum,
all 477 returned-file hashes, exact source/reference/sample axes, native runtime
isolation, masks, 20-epoch seed-11 schedule, exact reload, complete raw/learned DNA
exports, fixed clustering, AMBER and independently recounted confirmed R95.
No accepted scientific stage was repeated. The v4 AMBER inventory gate failure
is preserved; v5 source `67c2615` resolves its lock comparison without a rebuild.

The frozen four-genome GI GSA derivative retains all 5,309 contigs / 12,924,259 bp,
including 1,097 below-500 exclusions / 341,158 bp and 1,353 all-zero-depth rows.
One million pairs each from retained samples 1/4 were mapped to that exact
short-inclusive reference; E001 depth was not reused or zero-filled. Heavy original/
sampled reads and alignments remain on UCloud and are receipt-bound, not rehashed
locally. All two million returned selection IDs and thresholds were inspected.

Confirmed macro R95 raw→learned **0.16731→0.43443**, bp-weighted **0.14329→0.38295**;
≥50%-recovered genomes **0→2**, ≥90% **0→0**. Bins 113→51, eligible noise
3,414→321, bp-weighted assigned-bin purity 0.98049→0.97424. Learned output is still
fragmented. These are useful development **assembled-sequence recovery** results,
not marker-estimated whole-MAG quality, real-assembler performance, independent
generalization, isolated coverage benefit or architecture superiority. E001's
community and 1,332 IDs overlap; no E001/H001/three-seed conclusion changes.

Actual 4-vCPU / 12-GB cost through collection: **495.121 s / 0.550134 allocated
vCPU-hours**, sampled DAG peak 1.785 GB. Sampling accounts for 408.339 of 470.190
DAG seconds at about one CPU; mapper rules average 2.93–3.15 CPUs and native logs
report four threads. Training itself 1.832 s / 3.41 CPUs. Time/RSS limits pass, but the declared serial schedule overlapped training/raw
work and both evaluators. Current future-launcher code removes simultaneous
`--cores`/`--jobs`, sets global RAM and adds explicit serial DAG barriers; actual
Mac scheduling/partial+completed-resume fixtures pass. The tiny Mac legacy
fixture did not reproduce the Linux overlap; no corrected Linux run is claimed.
Accepted scientific stages remain valid and are not repeated. No
full-community throughput or linear CPU-scaling claim. Retained attempt inventory
3.297 GB; return copy 32.09 MB. Prior runtimes/read sources/attempts are separate.

**E006's generic-command usability milestone is complete and accepted.**
The installed `dl-binner run` (0.1.0.dev1) packages defaults/DAG and produces both
arms, complete DNA exports and byte-bound label-free accounting. The
[guide](PROTOTYPE.md#run-the-binner) owns user-facing commands/outputs/recovery;
[E006](../experiments/E006-cli-usability/README.md) and its
[receipt](../experiments/E006-cli-usability/observed.json) own evidence/costs.
Source/contracts were committed at `e93132b` before native execution; the final
validated wheel binds `e30023c` source. Scientific `io.py`, `model.py`, clustering
and the seed-11 schedule are unchanged. No accepted E002–E005 science was repeated.

Native Mac wheel checks from outside the checkout pass sequence-only/explicit
depth, all six strata, masks, zeros, exact reload, both exports, empty valid bins,
fresh/partial/completed resume and changed/corrupt/missing/extra artifact refusal.
Nine focused tests and native independent CPU/global-RAM scheduling checks pass.
Fatal worker/orphan cleanup and actual RSS/overall timeout checks validate their
intended failure, not any nonzero exit. Parent/child logs, ten-second heartbeats
and exit receipts persist; messages surface the native cause. CLI/journal formats
can evolve without a compatibility commitment.

The 13-contig / 42,311-bp baseline fixture and four-contig / 2,048-bp final fixture
are software tests, not bin-quality evidence. The new accounting reader agrees
with retained E005 raw/learned counts and depth zeros without inference or AMBER.
Final suite: **59.722 s / 0.348-GB sampled peak**; known supervised QA attempts
including failures: **335.212 s / 0.372458 four-thread wall hours**, local planning
not UCloud charges. Initial pre-monitor failure, setup/build, review/debugging/
idle time are outside that accounting. The suite remains within four threads,
loader zero, 8 GB and two hours. Test failures identified monitor receipt, native
error presentation and unreaped-process cleanup defects; all are retained/repaired.
Disk exhaustion stopped v5 setup. Final v7 is a fresh lexical package prefix with
explicit byte-verified numerical/build dependencies reused read-only from v4;
no old prefix was relocated/upgraded/deleted. Origins/inventories and dependency
tree hashes passed review. This local recipe is not a Linux environment transfer.

**Exact next step: the owner runs the prepared tiny E006 CPU/Linux generic-command smoke** in a single-node **4-vCPU / 12-GB Terminal job**, then returns its printed archive, checksum and terminal log for independent review. [Operations](../experiments/E006-cli-usability/OPERATIONS.md) owns the exact checksum-pinned command and two upload files; [Linux contract](../experiments/E006-cli-usability/linux-smoke.json) freezes **1,800 seconds including verification/setup**, a separate 120-second evidence-collection limit, four numerical threads/interop one/loader zero and 8 GB working RSS. The new generic launcher is **not Linux-accepted yet**. This is finite operational compatibility work, not an architecture/quality gate.

The packet reuses the retained **13-contig / 42,311-bp** real-DNA software fixture and unchanged accepted wheel. Its scripts/contracts bind **a8010cb**, archive SHA256 `d15864bd606676991b95c3fe2bb2d4198394106e22aead022fee9b64edc08569` (**72,267 bytes**). Accepted E005 CPU/workflow inventories are reprobed read-only. A new versioned package venv owns the wheel and explicitly borrows Linux dependencies from the persistent accepted base; numerical/import origins and before/after site-tree bytes are checked. No Mac prefix/links, runtime copies, heavy data or accepted scientific stages are transferred or rerun.

Local native owner-driver/command checks and failed-entry returns pass: **21 final native contracts, four focused deployment tests; final full envelope 186.669 s / 0.360-GB sampled peak**. [Preparation receipt](../experiments/E006-cli-usability/linux-prepared.json) records all three full harnesses (**517.585 s / 0.575095 four-thread wall hours**) and scopes. Negative entries and shell-only log-template correction are retained separately; no Linux platform/environment credit follows. The owner controls execution. Keep the two uploads, launch copies, terminal logs and returned archive/checksum under `/work/Home/dl_binner/e006/transfer/`; unique attempts and new prefixes stay under E006. E005 transfers remain under its existing `transfer/`; preserve its attempts/runtimes and do not rerun the accepted v5 recipe. Stop on unexpected failures and return retained evidence; no automatic retry or data expansion.

The future non-blocking learned TNF / frozen-GLM-head / hybrid comparison remains
planned and unrun. No larger datasets, extra seeds, architecture gate, publication
or push is authorized. E004's package source and accepted settings are unchanged.
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
separate new CPU/workflow prefixes under its own root and read-only reuses E001's
accepted mapping/AMBER prefixes. E005 v5 now checks the complete AMBER distribution
inventory against E001's hash-identified clean-prefix review, not only `pip freeze`.
Frozen E001 source/configuration and raw observed records remain unchanged.

Local branch: `first-binner-prototype`, created from `930e6743eac1aadb93ea23b51f2a6ac617155a2e`.
Owner-configured private GitHub origin is present; main/origin-main initially matched
that commit. This task makes local commits only. `agent_context/` is an ignored
inbox. Before public publication review licensing and historical source packaging
per [D001](decisions/D001-research-record.md). Update this handoff when direction,
significant evidence or execution dependencies change; details belong to their owners.
