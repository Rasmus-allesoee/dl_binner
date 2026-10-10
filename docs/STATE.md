# Current Research State

Updated: 2026-10-10. This is the single current handoff.

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
fixture did not reproduce the Linux overlap; no corrected E005 scientific-pilot
rerun is claimed. E006 subsequently validates the generic serial launcher below.
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
loader zero, 8 GB and three hours. Test failures identified monitor receipt, native
error presentation and unreaped-process cleanup defects; all are retained/repaired.
Disk exhaustion stopped v5 setup. Final v7 is a fresh lexical package prefix with
explicit byte-verified numerical/build dependencies reused read-only from v4;
no old prefix was relocated/upgraded/deleted. Origins/inventories and dependency
tree hashes passed review. This local recipe is not a Linux environment transfer.

**E006's generic-command native CPU/Linux gate is now complete and accepted.**
[Independent retained review](../experiments/E006-cli-usability/README.md#accepted-native-linux-return-and-independent-review-2026-10-06)
and [Linux receipt](../experiments/E006-cli-usability/linux-observed.json) verify
`generic-linux-smoke-y9xix7p9`: checksum/all 462 archive members/447 retained-file
entries, exact inventories/import origins and unchanged dependency byte trees,
serial native stages/independent CPU/global-RAM placement, twenty-epoch seed-11
schedule, exact reload, complete raw/learned DNA, masks/zeros/six strata, partial
resume only remaining six stages and completed resume no native work. All 21
native contracts including intended failures/RSS/timeout/orphan handling pass.
No accepted native or scientific stage was repeated. The packet binds `a8010cb`,
unchanged wheel/source `e30023c`; new Linux prefix owns the package and borrows
persistent E005 dependencies read-only. It is not a standalone portable environment.

Actual declared **4 vCPUs / 12 GB**: **214.793 s / 0.238659 allocated vCPU-hours**
through collection, **0.422-GB sampled stage peak**. Original storage reporting
omitted its inventory and statted an open log; the immutable return has exactly
**2,172,376 uncompressed bytes**, plus a **1,174,633-byte archive copy**. The original
receipt is preserved, with correction and a tested future collector fix in
`bee512a`; no retry is needed. Full new-prefix/cache storage, exact peaks and
owner idle/billing are not measured. Preserve all attempts, linked dependencies
and transfer files. [Operations](../experiments/E006-cli-usability/OPERATIONS.md)
now retains the command as executed provenance: **do not run it again**.

**E007's private-PR readiness milestone is complete and accepted locally.**
[Results/limitations](../experiments/E007-pr-readiness/README.md) and
[byte/resource receipt](../experiments/E007-pr-readiness/observed.json) bind
`4c68b19` source to inspected dev2 wheel/sdist and an equivalent sdist-rebuilt
wheel. Fresh separate Mac prefixes own their dependencies; full inventories,
imports/pools, pip checks and read-only old-runtime/cache bytes pass. All eleven
scientific/generic package files match E006; only version/build/readme metadata
changes. Accepted dev1/E002–E006 work remains retained, without replay.

Ordinary `tests/product/` is now independent of ignored research inputs/helpers.
Four-thread clean-snapshot and two-thread physically outside-repository suites
each pass 11 tests/18 named native cases without skips/mocks: all six strata,
masks/zeros/reasons, exact reload, both complete exports, strict partial/full
resume, corruption/change refusal, intended failures, orphan cleanup, heartbeats
and actual CPU/global-RAM placement. Fixture: 13 generated contigs / 42,311 bp,
software evidence only. [Standalone install](INSTALLATION.md) and
[usage](PROTOTYPE.md#private-pr-readiness-milestone) state limits and frozen settings.

Known serial integration clocks including two repaired packaging failures and
artifact preflight total **712.558 s / 0.742910 local thread-budget wall hours**,
under four threads/loader zero/8 GB/three hours. Successful full setup/check attempt
331.511 s; sampled stage peak **0.561 GB**. E007 retains 2.765 GB including all
failed/new prefixes and evidence, plus a 1.465-MB physical outside test copy.
Resource sampling is approximate; source preparation/acquisition/review/idle
are separate, and these are not UCloud costs. No accepted demonstration was
repeated and no architecture change occurred.

**E008's product changes and native Linux CI are accepted; private PR #1 is merged.**
[D012](decisions/D012-product-execution-and-usability.md) implements positive
uncapped CPU choices, optional RAM/time safeguards and a built-in serial dispatcher
requiring one CPU environment. Scientific byte hashes/defaults/results remain
unchanged. GPU/Conda are future goals only; shared people/agent usability is durable
intent. [E008](../experiments/E008-product-execution/README.md) owns source/build
identities, tests and real CI; the initial Mac/native Linux suites passed 12 tests/
18 cases. A reproduced platform timer overflow is repaired with native regression;
post-fix local tests pass 13 tests/19 cases. The independently inspected
[post-fix Linux receipt](../experiments/E008-product-execution/linux-timer-repair-observed.json)
accepts all 13 tests/19 cases, complete exports, exact reload, strict resume,
intended limits/failures/cleanup and native large optional safeguards. Linux
product peak 0.575 GB, 36.198 s; job wall 128 s, not exact billing. Final-head
checks are refreshed after record-only pushes. No accepted science or UCloud
work was repeated.

**Private PR #1 was merged on 2026-10-07 under explicit owner authorization.**
[Merge receipt](../experiments/E008-product-execution/merge-observed.json) binds
head `ecf6ab822df741c6f7bb092826957b6ffc4e8771` to normal merge commit
`5bc824a9bf4b1ca4562acda10735a3fc6b54dc3d`; its two parents preserve the prior
main and all accepted source commits. Final-head Linux CI passed 13 tests/19
native cases (38.803 s / 0.574-GB sampled product peak); docs checks pass.
No returned independent review or approval is claimed: the requested bot did not
respond, no reviewer was required and no actionable finding/unresolved thread
remained. The owner's later merge authorization supersedes the preparation-task
stop. Repository remains private, with no release/tag/package publication.

**E009 v10 accepts all other stages/three tool contracts; v14 retries only SCGBinner and COMEBin.**
[D013](decisions/D013-first-comparative-benchmark.md),
[the targeted evidence](evidence/2026-10-09-e009-contract-reconciliation.md) and
[E009](../experiments/E009-competitive-benchmark/README.md) retain subject S1:
full short-read sample-0 MEGAHIT 1.2.9 assembly (200-bp emission) and measured
sample-0/1 depth on that exact reference. Both official sample-0 contigs/GSA archives
were inspected and have identical 665,738-record / 422,673,293-bp DNA multisets.
They are reference-coordinate gold-standard reconstructions, so they cannot replace
the read-derived assembly. The supplied simulator coverage remains source truth,
never observed depth. Large reads remain unacquired; no community was assembled/fitted.

Preserve dev3 source `5e54538` and scientific defaults. Learned TNF + measured depth
is primary; raw and TNF-only controls are diagnostic, capped at 16 core-hours.
Shortlist: SemiBin2, MetaCAT core, SCGBinner, COMEBin full native grid, plus named
CompleteBin max-50 subject to native-scale admission. DCVBin's official 1.657-GB
payload is available; its single-depth CUDA VAE and CUDA continued-pretraining
recipe require a substantial extra port, so it is excluded from this bounded CPU
comparison. Coverage is not a disadvantage. Markers are a high-priority future
fixed-encoder grouping/refinement ablation, with no baseline change or study now.
Known/unknown pretrained overlap limits generalization; it is not evaluator label
leakage and an unavailable historical inventory alone is not an execution blocker.

Acquisition/overlap, paired-read/assembly/mapping/ordered-depth, competitive PAF/CIGAR
truth, complete exports and narrow AMBER/R95 adapters are implemented. Actual Mac
small-DNA mapping/depth, source truth (including competing genomes/repeats/reverse
orientation/I-D), AMBER and CompleteBin checkpoint/forward paths pass. Operational
SCGBinner dtype/host-pool/HNSW and native HMM master accounting are explicit.
Real COMEBin native writers expose resolved-basename IDs; adapters verify their
relation to ordered original BAM paths rather than guessing from aliases. Local
checks and failures are separately retained; they do not establish full Linux
imports/training or large-community affordability. Mac four-thread MEGAHIT crashes
remain unresolved; the local writer check is explicitly one thread; v10 independently passes
eight-thread native Linux assembly. No accepted science was repeated.

**E009 v10 completed; two native tool contracts failed.**
[Independent review](../experiments/E009-competitive-benchmark/linux-preflight-v10.json)
verifies checksum/all 340 members /338 hashes. Accept SemiBin, MetaCAT, CompleteBin,
eight-thread Linux assembly, ordered mapping/depth, competitive truth, AMBER/R95
software tests, runtime/utility/source/database setup, source acquisition/catalog
and scoped read-only identities. No full fits/E009 scores. Actual 456.278 seconds
through collection /1.01395 allocated core-hours at 8 vCPU/24 GB, peak sampled
stage RSS 1.364 GB. Acquired 3.2-GB source archive/catalog remains retained; source
catalog 2,078 files /65,571 records /10.252 Gbp, zero exact development matches,
with near/pretraining independence not established. Preserve all accepted evidence.

SCGBinner's shared sklearn1.9.0 lacks stable_cumsum; COMEBin's own help passed,
CheckM imports a pruned checkm.test module. **Exact next step:** owner runs the
**v14 two-path retry, 8 vCPU/24 GB, three-hour allocation**, from
[Operations](../experiments/E009-competitive-benchmark/OPERATIONS.md). Upload pair
under `artifacts/e009-preparation/transfer-v14-final/`; [transfer.json](../experiments/E009-competitive-benchmark/transfer.json)
binds final source/command/packet/tests. Install independently owned compatible
SCGBinner and complete CheckM Conda stacks; retain COMEBin's accepted numerical
recipe and use separate CheckM interpreter/libraries. [D006](decisions/D006-environment-ownership.md)
records the concrete failures triggering this scoped ownership amendment.
The first local mixed Conda/pip recipe failed and is retained; v14 replaces it
with all-Conda CPU Torch and reuses accepted Linux COMEBin help while checking
the unchanged native augmentation API. A second local packet passed SCGBinner
but exposed CheckM's unsupported global --help; v14 uses actual lineage_wf -h
and checks owned Linux native entry points without fitting. Only the two failed native contracts execute; retained tiny BAMs, acquired sources
and utility prefix are reused. Passed tools, source download/catalog and all
assembler/mapping/evaluator checks stay accepted, unscheduled. Original E001,
v8 snapshot/151 chunks, old attempts/packets/data/prefixes remain untouched. The final three-hour clock and10-GB Home floor follow actual Linux package
inventories (94,327 cache/prefix payload paths; old copy-rate comparison~105min
before overhead), rather than the much faster Mac run. Linux
corrected-runtime compatibility and native contracts remain unverified until return.
No scientific design/defaults/results change and no full fit/score is admitted.

After native preflight admission and source/sample-count review, prepare the
bounded bulk-read/assembly/depth/truth step. No community fits/scores/architecture
comparisons, source-history rewrite, remote push or UCloud execution by Codex.
All old packets/attempts and accepted scientific evidence remain preserved.

The revised prospective budget is **700 allocated core-hours** (664 stages +36
reserve), against the owner's approximately **1,980** balance: **1,280 headroom**.
The preflight costs at most 40 within that plan; caps are not runtime forecasts or
automatic retry permission. No UCloud spend occurs in this preparation. The former
200 GB is a provisioning estimate, not a hard cap. Home (50–100 GB) owns code/new
prefixes/transfers/logs; heavy source/read/BAM/temp lives only in the project's
shared E009 child (8–10 TB shared capacity). Colleagues' files and old attempts
remain untouched. Exact identities/tests are in E009's maintained receipts.

The future non-blocking learned TNF / frozen-GLM-head / hybrid comparison remains
planned and unrun. E009's local adapters/tests/owner-preflight preparation and commits are authorized;
no UCloud execution, community fits/scores, extra seeds, architecture implementation,
private push/PR or publication occurs in this task.
E008's private push/PR/merge is authorized and completed; accepted
scientific source and settings are unchanged.
Frozen GLM weights/features remain
retained, deferred from the first prototype rather than globally rejected. The
completed 2026-09-30 review/source audit is reused. No full-GLM training, VAE
curriculum, automatic architecture campaign or E001 rerun is planned. E001's
2,500-bp cutoff and the thesis's 2,000-bp filter are not product constraints. The
first configurable 500-bp default is an engineering choice; E009 prepares real-
assembly/whole-reference evaluation, with unsupported ranges and source completeness
explicit. It does not certify formal real-sample MAG quality or universal superiority.

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

Local branch: `benchmark-planning`, created from refreshed synchronized main/origin-main
`5e54538d1799e8d2538621729400f33fbaf017b9`; merged `first-binner-prototype` source history
is preserved. Owner-configured private GitHub origin is present. This task makes local
commits only; no push/PR/release. `agent_context/` is an ignored
inbox. Before public publication review licensing and historical source packaging
per [D001](decisions/D001-research-record.md). Update this handoff when direction,
significant evidence or execution dependencies change; details belong to their owners.
