# Current Research State

Updated: 2026-10-15. This is the single current handoff.

## Exact next step

**Execute the owner-authorized unchanged E009 diagnostic controls if live gates pass.**
The latest message explicitly approves the new $2 ceiling, existing resources and
four-hour phase/4.25-hour STOP. [The control receipt](../experiments/E009-competitive-benchmark/controls-observed.json)
owns current gates, source and actual outcome. No external binner/model change,
retry, resource or retention extension is authorized. Once a healthy launcher and
its watchdog are verified, leave it supervised and finish the response; do not poll
to completion. Local diagnostics follow accepted outputs and shutdown.
[Operations](../experiments/E009-competitive-benchmark/OPERATIONS.md) owns the exact
following prompt, budgets and records. [D013](decisions/D013-first-comparative-benchmark.md)
keeps improvement evidence as the purpose; the unchanged prototype is the control.

The data-only DAG at **5fec4e1d1700c64c4bdd9945bad4e116ade73c57 failed in its final
truth parser** (`CIGAR/endpoints/block length disagree`). Ten minimap2 invocations
exited 0; the retained first failing row has 2,948 CIGAR columns, PAF block 2,947
and `nn:i:1`, consistent with minimap2 2.30 excluding ambiguous bases from its block
count. This is an adapter failure, not a biological result or a reason to repeat
native alignment. The watchdog correctly observed the failed driver and stopped
the VM at **2026-10-15 11:32 Copenhagen**, independently verified in GCP.

**Accepted reusable feature data:** the complete sample-0 assembly, **145,702
contigs /231,678,157 bp** (89,041 >=500 bp); all ten full read samples
**0,2,3,4,6,9,10,11,14,17**, coordinate-sorted/indexed BAMs and measured depths.
Independent byte/header/axis review passes all **1,457,020 matrix cells**, retaining
13 all-zero rows and all short DNA. The closed combined matrix inside the failed
final stage has an explicit separate acceptance receipt; its parent stage remains
unsealed. [Actual phase/review receipt](../experiments/E009-competitive-benchmark/gcp-data-observed.json)
owns bindings, verification scope, costs, private archive and stop proof.

The completed read/source audit proves identical full **33,267,026 mate-ID sets**
and exact source joins. [Population review](../experiments/E009-competitive-benchmark/truth-population-review.json):
309 positive simulator genomes, **156 bacterial /0 archaeal /133 viral /11
eukaryotic /9 separately simulated plasmids**. Two taxonomy joins use exact taxon
rows without a provider genome ID; 110 preserve synthetic strain identifiers.
All nine permuted files are ten exact circular rotations of separately simulated
`pASV` plasmids. Their filename host IDs and `HOST` relationships do not merge them
with host genomes. Two zero-origin source files and 1,280 unobserved replicons stay
in the competitive universe. No rounded profile percentage determines presence.

**Fresh conservative supplied-reference truth v2 is admitted.** The separate
[admission](../experiments/E009-competitive-benchmark/truth-v2-admission.json) binds
all 300,499 retained native PAF rows, actual simulator genome IDs, separate pASV/HOST,
exact circular coordinates and 156 primary targets /554,661,890 full provided bp.
All 7,688 competitive aliases become 7,607 canonical records; no non-target,
zero-origin file or unobserved reference is discarded. Thresholds remain .99/200 bp
and .95 attribution. Qualifying `nn>0` alignments quarantine their whole query span
globally: **7,653,205 bp /3.3034%** remains unknown rather than falsely supported.
This conservative limit is fixed before any binner outcome. Every contig's DNA
accounting passes; an independent raw-PAF oracle agrees on all 348 nn/circular
queries plus 128 fixed SHA256-selected queries. The original failed DAG stays failed.
No new aligner, data replay, VM wake, fit or score was needed. This is provided-
reference alignment truth, not MAG quality or independent-genome/pretraining proof.
The new [retained evidence](../experiments/E009-competitive-benchmark/truth-v2-retained-evidence.json)
is a **5,218,978-byte local archive**, 112 regular members /76,654,870 logical bytes;
all 111 non-inventory hashes pass. The later control-phase credit gate passed and
its private cloud upload/readback now verifies; the original input archive is also
privately backed up. The truth derivation itself used no VM compute.

The prepared [diagnostic proposal](../experiments/E009-competitive-benchmark/diagnostic-controls-plan.json)
keeps dev3 source **5e54538d1799e8d2538621729400f33fbaf017b9**, seed 11, 20 epochs and
fixed grouping: raw/learned TNF+ten-depth and TNF-only. A proposed **new $2
incremental fit budget**, four-hour cumulative phase/4.25-hour provider STOP on the
existing 8 CPU/32-GiB VM, is now explicitly owner-approved subject to live gates. The new parent passes eight Mac
safety contracts with inert native children and verifies the exact retained wheel;
fresh Linux setup/runtime probe remains before the first fit within that clock.
This is a ceiling, not measured affordability. **No external tool is recommended in
the immediate next step.** SemiBin2 remains at most one later conditional reference;
CompleteBin/COMEBin full grid/SCGBinner remain deferred. Select one mechanism only
after diagnostics and confirm improvements on prospectively chosen additional data.

The bounded review reused the existing VM/disks with a **one-hour provider STOP**,
without provisioning/resizing or DAG/fit execution. Its stop and priced uptime are
in the receipt. Keep the **$20 data-only/seven-day envelope**, original cumulative
24-hour data clock and 25-GiB reserve. Measured production peak filesystem use was
**170.66 GiB**, minimum sampled free **124.52 GiB**. The existing 300-GiB work disk
cannot be shrunk in place. Stopped boot/work disks remain **$31.20/month gross**;
review retention by **2026-10-21** and credit expiry by 2027-01-10. No storage
migration, deletion, new capacity or retention extension is authorized. Keep the
read-only GitHub key, immutable baseline and old UCloud evidence.

## Direction and completed work

Improve our own deep-learning metagenomic binner toward high performance,
potentially SOTA, while learning through implementation. Usability/reproducibility
remain essential; paper/novelty and strong claims require separate evidence. See
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

## Accepted prototype evidence

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

**E009 v10/v14 tiny native evidence is accepted; community fits/scores are unstarted.**
[E009](../experiments/E009-competitive-benchmark/README.md) owns the chronological
attempts and limitations. V10 accepts SemiBin/MetaCAT/CompleteBin, eight-thread
Linux utility/assembly/mapping/depth/competitive truth/AMBER contracts, source
acquisition/catalog and scoped immutable identities. V14 repairs only independent
SCGBinner and complete CheckM/COMEBin paths; all other stages remain unscheduled.
No old prefix/source/chunk or scientific output was modified/replayed.

Official sample-0 contigs/GSA share the 665,738-record /422,673,293-bp DNA multiset
and are reference-coordinate reconstructions, not a traceable de novo assembly.
The full released source catalog has 2,078 files /65,571 records /10,251,869,096 bp;
exact accession/full-replicon development comparisons found no match, with near/
pretraining independence unresolved. Its inaccessible UCloud archive has an
accepted SHA for new-host reacquisition, not a GCP acquisition receipt.

The old mandatory five-tool shortlist is superseded by D013. CompleteBin max-50,
COMEBin full grid and SCGBinner are deferred; SemiBin2 is a later first candidate,
MetaCAT core conditional, with no fits approved. DCVBin's payload exists but its CUDA/single-BAM port is
outside this bounded CPU comparison; LorBin is deferred. Marker-guided fixed-
encoder grouping remains a high-priority controlled follow-up, not an automatic
change. A whole-tool win cannot identify the responsible component.

Current input/resource amendment is one sample-0 assembly with ten cross-subject
depth sources and unchanged raw/learned/sequence-only controls. Old two-depth
700-hour UCloud budgets/commands are [history](history/E009_UCLOUD_OPERATIONS.md),
not current entitlements. The authorized data-only GCP stage stops for actual
source/truth/resource review; no full-fit monetary budget is approved.

The future learned-TNF/frozen-GLM-head/hybrid study is planned and unrun; frozen
GLM evidence remains accepted and deferred, not globally rejected. Reuse the
completed review/source audit and accepted E001–E008 science. No new architecture
or release gate, inferred whole-MAG quality, unseen-genome claim, E001 rerun,
VAE curriculum, full-GLM training or automatic comparison campaign follows.
The configurable 500-bp default is a prototype choice, not a product restriction.

## Resources and continuity

COMEBin successful conditions used 39.6462 allocated core-hours; the known recovery
sequence lower bound is 58.1075. MetaBAT2/VAMB pair: 0.76946. The new collection
adds 0.002224 (1 vCPU / 4 GB, 8.0065 driver seconds). These are partial accounting,
not exact billing or a remaining-balance estimate. Successful COMEBin condition
files total 11.313 GB; the diagnostic archive is an additional 235.13 MB copy.
Preserve accepted/irreplaceable evidence and old UCloud files. For future obsolete
failures, retain compact diagnostics/provenance before pruning regenerable bulk
under the new storage policy; no existing files are deleted in phase 1.

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

UCloud was CPU-only and owner-operated; it is now inaccessible. Recorded paths
below remain historical dependencies, not remotely available runtimes. E001's persistent prefixes stay under
`e001-gate0/envs/` per [D006](decisions/D006-environment-ownership.md); E005 owns
separate new CPU/workflow prefixes under its own root and read-only reuses E001's
accepted mapping/AMBER prefixes. E005 v5 now checks the complete AMBER distribution
inventory against E001's hash-identified clean-prefix review, not only `pip freeze`.
Frozen E001 source/configuration and raw observed records remain unchanged.

Local branch: `benchmark-planning`, created from refreshed synchronized main/origin-main
`5e54538d1799e8d2538621729400f33fbaf017b9`; merged `first-binner-prototype` source history
is preserved. Owner-configured private GitHub origin is present. The owner-authorized normal
prepared-branch push through 5fec4e1 and exact VM sync are completed. This phase
requests a local result/decision commit; no main merge,
PR/release or visibility change. `agent_context/` is an ignored
inbox. Before public publication review licensing and historical source packaging
per [D001](decisions/D001-research-record.md). Update this handoff when direction,
significant evidence or execution dependencies change; details belong to their owners.
