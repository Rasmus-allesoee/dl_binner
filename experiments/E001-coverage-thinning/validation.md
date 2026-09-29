# E001 Gate 0 Validation

Date: 2026-09-18; appended through 2026-09-29. Software checks and reviewed scientific attempts are identified separately below.

## Successful COMEBin CT resume accepted, 2026-09-29

The [compact-return review](comebin-paired-observed.json) and
[combined assessment](seed11-assessment.md) supersede the in-progress recovery
handoffs below. Archive SHA256:
`ad422e367d27f2abb4b2b5d56f9beea8da93e71c80921156542c64a79f9b363f`.
The return and terminal log confirm successful CT-only execution under `9ceeb08`;
C0 remains from `8a03ca2`, with its retained receipt unchanged. Contiguous native
schedules stop legally at 111/107; complete selected partitions and AMBER/R95
recomputation pass. All 120 candidate hash receipts and marker-score rows per
condition pass grid/arithmetic/winner checks. Binary arrays are omitted from the
return; direct inspection remains pending the read-only collection, not a rerun.

The whole implementation/correction sequence `6ba21ce`–`07ff631` was reviewed.
There is no outstanding native failure in this return. Historical interrupted
CT and stale-lock failures stay under recovery and do not invalidate completion.
[D010](../../docs/decisions/D010-bounded-e001-and-prototype.md) defers other seeds
and sets a bounded diagnostic closure followed by prototype design.

Local verification: new review tests exercise the real uploaded archive and
reject malformed schedules/marker grids. The collector tests use real NumPy
files and actual hashing/tar I/O across separate retained/resumed roots; repeat
runs preserve outputs, altered/missing bytes stop, escaped paths are rejected.
No production collection logic is mocked. The native Linux binners are not rerun;
current UCloud files will be verified by the owner collector. The broad suite's
first sandboxed run hit macOS cache/process-counter permissions; this is separate
from returned UCloud scientific execution.

With native cache/process access, 218/219 tests passed. The remaining feature-driver
fixture demanded the production 15-GB free-space floor despite using tiny mocked
native inputs; available local disk was below that floor. Only the fixture plan
was changed to a 1-KiB requirement, leaving production limits untouched. All 22
feature tests then passed, including its real Snakemake driver, repeated execution
and recovery DAGs. The three COMEBin review and two collector tests were rerun
successfully after final changes. Isolated system-Python collector CLI/returned
bytes, Python compilation, exact owner-command shell syntax and docs/link checks
passed. Native scientific fits were never run locally or remotely by the agent.

## COMEBin CT attempt stopped; return packaging failed, 2026-09-28

The owner supplied a terminal log for attempt `paired-pilot-comebin-istuh_2t`,
source commit `8a03ca287c057f24f21f09442f710a5914b32703`, at 8 vCPU / 24 GB.
The local inbox copy is
[e001-pilot.CBTiiZ_new.log](../../agent_context/e001-pilot.CBTiiZ_new.log),
SHA-256 `324800dbf87a78bb511dfc4b2fb7a1ad9a1020c4bae939b7f2be2e69f912976c`.
Snakemake recorded the C0 condition as finished. CT training logged epoch 100/200,
then the workflow returned code 1 at about 304 minutes elapsed. The log contains
no underlying worker exception, signal or scheduler reason, so the cause of CT's
stop is **unresolved**. The heartbeat corresponds to about 40.5 allocated
core-hours at the recorded allocation; exact status accounting awaits the retained
`status.json`.

The driver's separate packaging step then raised `FileNotFoundError` for
`/work/Home/dl_binner/e001/e001-gate0/paired-pilot-comebin-istuh_2t-return.tar.gz`.
The attempt remains incomplete and is not accepted as a paired C0/CT result. At
the time, the terminal log could not establish why CT stopped; the later
checksum-bound return below resolves the driver-level failure evidence and
supersedes that open diagnosis.

The first package-only recovery used source commit `f1eed69` and the owner-supplied
[terminal log](../../agent_context/e001-pilot-recover.6dU9xz.log), SHA-256
`3a1982d6e32457311da58373a15c6eb6a51c3e64b2ef50f5630b72d46eb5c5e4`. The bundle
checksum passed, but recovery stopped because `status.json` is absent from the
attempt; it produced no archive. This is a recovery-script assumption, not the CT
worker failure, and the log does not show that the attempt was modified. The
revised salvage mode treats expected records as optional, reports absences, and
packages the small logs/receipts that remain.

## COMEBin CT driver failure and guarded resume, 2026-09-28

The owner supplied the return archive, checksum and package-only terminal log.
The archive checksum passed: SHA-256
`c589a318308b467650fdff5be274c353d232056fa3bbbfbdf2d591e471f467af`; the
package-only log SHA-256 is
`81612a8a05774ba682df37552561ef5cf55220e463b625b433e60a352c8d9452`. It contains
514 regular members / 785,281,998 uncompressed bytes. **418** files named
`hmmer.analyze.txt` account for 776,570,812 bytes; these are repeated
CheckM/HMMER per-bin diagnostics from C0 candidate marker selection. The previous
package filter admitted every `.txt`, causing the 117-MiB compressed return.
Future bundles omit this exact diagnostic filename; the retained attempt is
unchanged.

`logs/comebin-CT.log` shows epochs 94–100 completing normally at roughly 75
seconds per epoch. Immediately afterward, `checked()` raised `FileNotFoundError`
while resolving `comebin/CT/fit.stderr` by pathname. Writes of `fit.command.json`
and `failure.json` to that same CT directory then failed. No COMEBin stack trace,
OOM message or native fatal marker appears. The archived Snakemake shutdown log
also reports that job-local `/work/Home/.../transfer` no longer existed when it
tried to restore its working directory. This is consistent with UCloud job/mount
teardown or a transient path loss; the exact Hours allocation was not included in
the return, so the provider trigger is not proven. The driver now monitors the
already-open stderr file descriptor and makes secondary receipt writes best-effort
so they cannot replace the original exception.

The pinned COMEBin source saves its checkpoint only after the training loop
finishes (`agent_context/tools_repo/COMEBin/COMEBin/simclr.py`, lines 257–266),
so epoch 100 cannot be resumed as a model checkpoint. The prepared owner runner
rehashes every C0 retained artifact and uses the existing Snakemake work
directory. It moves partial CT files to `recovery/`, then requires a dry-run with
CT and paired-summary only; C0 in the DAG is a hard stop. It restarts CT from
epoch 1 and prefers Home `transfer/` for the compact return, falling back to the
persistent attempt if Home is unavailable. See the [current operations action](OPERATIONS.md#current-action-2026-09-29-collect-retained-diagnostics).

The repair is source commit `889d76a1f234b7ccb787cc7c37a1f5ff1f69b31b`, transferred
as `e001-code-889d76a1f234.tar.gz`, SHA-256
`36ff4861672f9863ab17ae8623eb36d679eee3dcbbc647462d0cfa8bd15311e3`. The checksum
and embedded source commit were verified locally. Seven focused pilot tests, two
feature packaging/progress tests, and the 32-document/381-link check passed. The
broader pilot suite's two remaining failures come from this macOS sandbox denying
Snakemake's `psutil` process-tree query (`sysctl`, Operation not permitted); the
NumPy-dependent review test was skipped because NumPy is not installed locally.
At the time this first resume bundle was prepared, no owner-run resume had yet occurred.

## COMEBin resume stopped on a stale Snakemake lock, 2026-09-28

The checksum-bound `paired-pilot-comebin-istuh_2t-resume-i5qfl46l-return.tar.gz`
passes SHA-256 `10fccc949fab2592efe1fbe4ae50b66414805dbffcf60c5822e72383bc1efa06`;
the terminal log SHA-256 is
`9c706d17cc7d77dfaa0d7c53deb9348bdecbb305264cba3ddda09ce36bc4f791`. The 1.3-MiB
archive has 122 members. C0 was revalidated unchanged: 5,227 artifacts,
5,656,492,243 bytes. The driver spent 7.51 seconds (0.0167 allocated core-hours
at eight vCPUs) and no training rule ran.

Snakemake's new log ends immediately after `Building DAG of jobs...` with
`LockException: Directory cannot be locked` for the shared attempt. Its documented
`--unlock` operation removes a stale work-directory lock; the workflow was not
run with `--nolock`. The returned status said `execution_started: true`, but that
was a driver bookkeeping bug: it marked the workflow command as started before
knowing whether Snakemake launched any rule. Consequently, the earlier CT partial
was left under `recovery/.../comebin-CT-partial`, rather than restored to the live
CT path. The files remain preserved in both the returned archive and UCloud
recovery directory.

Source commit `9ceeb087441d06ff69b6a639233781ddad674d58` fixes both issues. The
resume can restore a copy of the newest retained CT partial without consuming
that recovery evidence. It distinguishes workflow invocation from rule launch,
restores moved files after pre-rule failures, and permits `snakemake --unlock`
only with the explicit `--unlock-stale-snakemake-locks` owner flag and a check
that no other workflow is active. It records pre-unlock lock hashes, then still
requires a dry-run that schedules CT and the paired summary but not C0. No
scientific training or UCloud execution has been performed with this fix yet.

Transfer bundle `e001-code-9ceeb087441d.tar.gz` SHA-256 is
`9df30700587eb8f9fbdbb12034e58528865e91b507a3eb7c8b47a61eb6a90eea`; its
embedded source commit and checksum were verified. Three targeted recovery tests
pass from the extracted bundle. A separate test-only commit
`4f664188399aed0c9bcdaccdac3af59d496e55b6` also ran the pinned Snakemake 9.13.7
executable's real `--unlock` against synthetic stale locks successfully; it does
not change the execution bundle. The broader pilot suite still has the two known
macOS sandbox failures when Snakemake/psutil queries the process tree; one
NumPy-dependent archive-review test is skipped locally. Native UCloud behavior
remains unverified. See the updated [owner action](OPERATIONS.md#current-action-2026-09-29-collect-retained-diagnostics).

## COMEBin first-pilot driver guard failure and retry, 2026-09-27

The [checksum-bound failure record](comebin-pilot-failure-observed.json) reviews
`paired-pilot-comebin-p3983hy8-return.tar.gz` SHA256
`fa5453f078a2f9c2d07e6c7c93be21b0f48f4990efe08d0523a937d03179d35f` and terminal
`e001-pilot.OaThZ8.log` SHA256
`cb2781c695deb4da45b834027703bddddfdfa560a51002d5fcec1cfb08c9a35a`. Actual
allocation was 8 vCPU / 24 GB. Driver wall time was **679.990 seconds / 11.33
minutes**, charged **1.51109 allocated core-hours**, and retained **386,464 bytes**.
Packaging and outside-driver idle time are not included.

This is an **adapter guard failure**, not a COMEBin exception, OOM or completed
fit. COMEBin's own log reports CPU training, `--num_threads=4` and its source-fixed
four DataLoader workers. Its first two persisted complete epochs took 120.119 and
121.543 seconds. The wrapper reached an epoch-three progress marker, then raised
`Measured full-schedule projection exceeds fit cost ceiling`; its watcher estimate
was 44,443.85 seconds against the 36,000-second / 80-core-hour limit. That estimate
multiplied full process elapsed time (including roughly five minutes of startup
and feature reads) by 200. The uploaded UCloud graph showed about 350% peak CPU on
the allocated eight vCPU. Peak child-tree PSS was 6,192 MB; no memory-limit failure
is present. No full embeddings, checkpoint, selected partition or scientific
score was produced. Preserve this unique attempt.

[The correction](../../scripts/e001_pilot.py) estimates the remaining schedule
from native per-epoch elapsed times, counts current fit wall time once, and adds a
25% margin. It does not assume native early stopping. The eight-vCPU worker split
is now **seven PyTorch threads + one DataLoader worker**; the adapter overrides
the pinned COMEBin source's fixed count at runtime, without editing the checkout.
The training data are precomputed TensorDataset views and parent-seeded shuffling,
so this changes queue parallelism, not scientific features or the example order.
A bounded CPU DataLoader smoke now drains synthetic batches with the same one-worker
queue under short private `/tmp` before every full fit. The owner log will show the
effective resource values. No local PyTorch/COMEBin runtime is installed, so the
actual smoke and training still require the owner-run Linux retry. Existing
preprocessing, native features and MetaBAT2/VAMB pair remain accepted and will not
be repeated.

## Seed-11 MetaBAT2/VAMB accepted and COMEBin prepared, 2026-09-27

The [independent reviewer](../../scripts/e001_review_pilot.py) accepts
`paired-pilot-metabat-vamb-kru6t8dq-return.tar.gz` with SHA256
`e1bf4b7243abd82debeb564943445d3169366421786adac2e21bf119a74d5d68` and terminal
`e001-pilot.PkrRsg.log` SHA256
`c614aa8cdb04f0819e3e9cd53d01c21e563d2ac81ce89a736f15190835369ee1`.
[Observed evidence](paired-pilot-observed.json) pins execution commit
`ac7159f8d1c7c4e94db62f301c7714d101be9214`, every returned retained-member hash,
commands, source versions, resource measurements and per-condition results.
The archive is successful, all four completion receipts agree, and all native
commands exited zero. Preserve and accept it without another fit.

Both VAMB conditions ran exactly epochs 1–300, batch 256 with native batchsteps
25/75/150/225, 512/512 hidden dimensions, 32 latent dimensions, ten samples and
seed 11 on CPU. Their embedding IDs cover the same 22,594 contigs. Native code
validated finite embedding rows and model existence; hashes/sizes for latent.npz
and model.pt are retained. These binaries remain on UCloud and were **not read
locally**. Complete native assignments equal the CAMI exports with no duplicate
or unknown IDs. MetaBAT2 reports four threads and uses -t 4. Missing/cluster-zero
MetaBAT IDs remain unassigned in the frozen 817,438,232-bp denominator.

| Tool | C0 R95 | CT R95 | CT minus C0 | Assigned contigs C0 / CT |
| --- | ---: | ---: | ---: | ---: |
| MetaBAT2 | 0.442944 | 0.195018 | -0.247926 | 19,193 / 1,827 |
| VAMB | 0.461772 | 0.487635 | +0.025863 | 22,594 / 22,594 |

R95 recomputes exactly for every genome on the frozen 224-genome population.
AMBER bin totals, winning origins, purity, denominators and per-genome recovery
independently match the full frozen 238-origin truth and unfiltered partitions.
The historical exporter omitted its BINID index in both AMBER tables; complete
numeric row multisets and genome identities are still auditable from retained
native partitions. This is an export limitation, not an invalid score. The next
export preserves BINID. No rerun is needed to establish existing metric values.

MetaBAT's emitted matrix contains 22,432 C0 versus 1,949 CT IDs; respectively
162 and 20,645 frozen IDs are omitted, plus 3,239 / 122 explicit zero labels.
Thus native support filtering is a prominent stage-level observation, not proof
that learned representation failed. VAMB's small gain further prevents a general
loss claim from this seed. COMEBin, later seeds and representation/selection
analysis remain open; no scientific thresholds have changed after seeing scores.

Actual driver time is **692.5138 s / 11.5419 min**, costing **0.7694598 allocated
core-hours at 4 vCPU / 12 GB**. Retained attempt storage is **1,679,703,225 bytes**;
this excludes external accepted inputs. Cost excludes return packaging and
outside-driver idle time. MetaBAT C0/CT rule CPU-time/wall ratios are **2.33 / 0.87**;
VAMB C0/CT are **2.39 / 2.49**. Four requested CPUs are not four continuously busy
CPUs: MetaBAT's small CT workload remains mostly serial. Sampled fit-tree peak
PSS is approximately 4,718 / 783 MB for MetaBAT and 1,108 / 1,120 MB for VAMB.
The failed first pilot remains a separate **1.5385 core-hour** cost; the known
failed+successful MetaBAT2/VAMB attempts total **2.30796 core-hours**.

The next COMEBin resource contract is amended in [D007](../../docs/decisions/D007-comebin-resource-envelope.md#pilot-resource-clarification-2026-09-27)
and the [plan](paired-pilot-plan.json): **8 vCPU / 24 GB**, four PyTorch threads +
four native loader workers, serial conditions, eight native Leiden candidate
workers. The former two-vCPU plan undercounted workers. Short IPC paths and fatal
loader handling now cover COMEBin as well. Native schedules, 120 candidates and
marker selection are unchanged. Full-schedule cost is checked starting after
three epochs; existing fit/group ceilings stay fixed. Native COMEBin scalability
and full training remain unmeasured, so no equal-cost speedup is claimed.

**Local checks:** 205 tests passed, including the returned archive audit, exact
R95 recalculation and independent AMBER checks, corrupted-checksum and table
rejection, actual pinned parser / worker-count contracts, production worker
short-temp cleanup and stop-before-cluster behavior, real child-process cost
projection termination and real Snakemake execution/resume. External native
training/clustering is mocked only in orchestration tests; no local PyTorch or
COMEBin clustering runtime is installed. These checks do not establish native
Linux full-fit readiness or eight-worker clustering performance. Documentation,
Python compilation, owner-shell syntax and transfer checks are recorded with the
bundle handoff. An initial sandbox-only Snakemake attempt hit macOS sysctl
permission limits; the complete suite passed with that local restriction lifted.

Reproduce the acceptance without native execution:

```sh
.venv/bin/python scripts/e001_review_pilot.py \
  agent_context/paired-pilot-metabat-vamb-kru6t8dq-return.tar.gz \
  agent_context/paired-pilot-metabat-vamb-kru6t8dq-return.tar.gz.sha256 \
  agent_context/e001-pilot.PkrRsg.log artifacts/e001-population-reviewed \
  /tmp/e001-paired-pilot-review.json
```

## Recovery-path defect and validation correction, 2026-09-25

Return `multisample-features-6q5yss2p` matches its checksum. VAMB remains accepted;
MetaBAT C0/CT/CS now completes and all native depth rows/sample axes validate.
[Reviewed evidence](feature-recovery-observed.json) records 249.718 seconds /
0.277464 allocated core-hours at 4 vCPU / 12 GB. COMEBin's isolated imports
completed within the unchanged timeout. Its diagnostic stacks show progress
through Torch imports and metadata reads, not proof of a permanent deadlock or
an environment repair. Keep the diagnostics; do not reinstall or relocate it.

COMEBin subsequently failed because our recovery copied `inputs.json` with the
correct old BAM paths, but the COMEBin branch still constructed `new_stage/bams`.
That directory intentionally did not exist. This was our integration defect.
The former recovery test replaced the actual extractor, so it proved scheduling
only and could not detect the consumer-path mismatch. Prior blanket readiness
claims from its passing count were too strong.

The corrected adapter accepts the ordered BAM list from `inputs.json`. Before
any augmentation it verifies existing files, a common native directory, exact
resolved sorting, unique paths and absence of extra BAMs. Source algorithms and
scientific settings remain unchanged. The sequence/coverage portion is exposed
as the same production helper used by the full adapter so it can be exercised
without a local PyTorch installation.

[Native contract evidence](native-coverage-local-validation.json) records a real
local build of bedtools 2.31.1 and the pinned COMEBin source. The regression runs
actual sequence augmentation, native BAM parsing/bedGraph processing and all six
coverage views on tiny real BAMs, for both fresh and recovered paths. No coverage
extractor, bedtools process or native reader is mocked. It checks expected means,
zero-depth contigs, dimensions, sample order, identical fresh/recovered arrays,
fixed intervals and rejection of missing/reordered/extra BAMs before writing.
This proves the raw path/coverage contract on macOS, not full Linux/PyTorch parity.
Existing returned Linux smoke evidence covers normalization separately. A real
Snakemake regression also verifies that completed VAMB and MetaBAT are not rerun.
All **185 repository tests passed**, including this native regression.
AGENTS.md now requires tests of changed production contracts and explicit
mock/skip/platform limits; test counts alone cannot establish native readiness.

The next command reuses accepted VAMB and complete MetaBAT features from `6q5yss2p`
and the BAM aliases still located in `t8lpankx`. Preserve both attempts. Only
COMEBin and the aggregate receipt remain. Its incomplete sequence augmentation
will repeat: the previous return has no binary hashes for that incomplete bundle.
The corrected adapter records an augmentation receipt before coverage so a later
failure retains that provenance. No new BAM copy, mapping, VAMB or MetaBAT
extraction is needed; source environments stay unchanged.

## Seed-11 MetaBAT2/VAMB failure and retry correction, 2026-09-27

The uploaded archive sidecar verifies for
`paired-pilot-metabat-vamb-fvfqsea2-return.tar.gz`
(`c1e0b74aac90e964f0886b29ec1acf27bf6a0770e256122177682ea27cf71bc4`). The
terminal log SHA256 is `c2c2aa9c431e619d4fe3e9fa7cb66c733df966221fb699b6bdea72a59e65473b`.
The [observed failure record](pilot-failure-observed.json) validates the archive's
status, benchmark rows, native commands and MetaBAT assignment hashes against
their evaluation receipts.

The owner allocation was 4 vCPU / 12 GB. Driver wall time was 1,384.65 seconds
(23.08 minutes), or **1.538498 allocated core-hours**; 1,667,661,833 bytes remained
in the unique attempt. External idle and packaging time are excluded. MetaBAT2
C0/CT outputs and per-condition evaluations completed, but each command and
Snakemake rule requested three threads while the isolated worker forced
`OMP_NUM_THREADS=1`. Both native logs said “Executing with 1 threads”; process CPU
time was 0.86 and 0.79 of wall time. These outputs are preserved, but this failed
pair does not replace the corrected four-thread run.

VAMB C0 loaded the full 22,594-contig/10-sample feature set and began setup. Python
3.12's multiprocessing resource-sharing queue feeder then raised
`OSError: AF_UNIX path too long` while trying to bind its listener below the shared
attempt `TMPDIR`. The feeder traceback was logged twice; no `Epoch:` lines appeared,
and periodic wall-time heartbeats continued until the owner cancelled the job.
VAMB CT never started. The process stayed alive after the feeder error, so a normal
child-exit check alone could not fail the rule.

The revised [driver](../../scripts/e001_pilot.py) creates a private `<40`-byte
directory under `/tmp` only for VAMB IPC and restores shared TMPDIR for evaluation.
Before the DAG launches any full fit, it imports the verified pinned VAMB runtime
and consumes all batches from its actual CPU `make_dataloader` with one worker,
using small synthetic abundance/TNF arrays. The smoke is bounded to 120 seconds,
monitors the known socket-error marker and is recorded in the return. The fit
wrapper monitors stderr for that fatal marker and kills the process tree promptly;
it also records native `Epoch:` progress and stops after ten minutes without an
epoch. This distinguishes heartbeat time from actual training progress.

On the four-CPU serial run, Snakemake and MetaBAT2 now both receive four threads,
and the MetaBAT2 worker gets `OMP_NUM_THREADS=4`. VAMB stays at `-p 3` because its
pinned CPU loader uses one additional worker; three PyTorch intra-op threads plus
that loader consume the four allocated CPUs. The native schedules/data/seed are
unchanged. A fresh attempt reruns both MetaBAT conditions under the corrected
resource settings and runs the DataLoader smoke before them. The prior attempt,
features and environments remain intact.

Local checks cover the actual pinned VAMB CLI parser and loader-worker contract,
MetaBAT command/thread/environment agreement, unique short-temp dispatch, fatal
background-thread traceback cancellation, native epoch/stall monitoring,
process cleanup, the real Snakemake serial DAG and complete synthetic-worker
driver packaging/repeated-invocation/failure paths. The local Python 3.13
environment has no PyTorch, so the real pinned VAMB/PyTorch DataLoader smoke could
not run on this Mac. It is the first bounded operation in the owner job; no
scientific fit starts unless it passes. The full repository suite and maintained
documentation checks are rerun for the final execution snapshot.

## Partial native features and targeted recovery, 2026-09-24

Return `multisample-features-t8lpankx` passed its SHA256 sidecar and input gate.
[Reviewed receipts](feature-partial-observed.json) accept VAMB C0/CT features:
22,594 contigs, ten ordered columns, matching paired IDs/masks and expected BAM
hashes. Maximum normalized scale-control differences are below 2e-6. MetaBAT
completed C0 depth extraction; all 22,594 rows/817,438,232 bases and sample columns
validate after correcting our header expectation. Its pinned native writer
`get_basename` removes the final extension, so emitted names omit `.bam`.
Our validator incorrectly required that suffix. The fix follows the native
contract and retains strict order checking. CT extraction did not start.

COMEBin timed out during the 60-second isolated import probe. Both child streams
were empty; the return cannot identify the stalled import or prove a cause.
Do not infer filesystem failure, reinstall, relocate its environment, bypass
the check or increase the timeout. The replacement probe installs repeated
tracebacks before site initialization, prints each import stage, preserves
normal site processing, and captures Linux process wait state before killing
a timed-out child. If healthy it continues normally; otherwise return this new
evidence. Runtime repair remains unresolved until that evidence is available.

Actual failed-driver cost: 611.007 seconds / 0.678897 core-hours at 4 vCPU / 12 GB.
Recovery uses a fresh attempt with an explicit checksum-bound `--reuse-attempt`.
It rehashes the existing BAM aliases/indexes and VAMB artifacts, copies only
small accepted features and the C0 depth table, and schedules missing work.
It does not regenerate VAMB, recalculate MetaBAT C0, recopy sample-0 BAMs, remap
or modify the preserved attempt. Source and output hashes retain original
provenance. The old attempt must remain mounted because its BAM aliases are used.
Local tests cover native headers, real-DAG reuse without scheduling VAMB/input
creation, modified-artifact rejection, startup markers and timeout diagnostics.
All 21 focused feature tests passed; documentation checks passed.

## Feature worker directory failure corrected, 2026-09-24

The checksum-verified `multisample-features-z6n2qvya` return records a successful
20-BAM input integrity gate, followed by identical `FileExistsError` failures in
all three tool workers. Snakemake created each declared output's parent directory
before launching the worker; our exclusive `mkdir` rejected that empty directory.
No tool environment probe or feature extraction began. This was a wrapper error,
not a BAM, native tool or environment failure. [The observed record](feature-startup-observed.json)
preserves source/checksum, exact errors, allocation and cost: 121.093 seconds,
0.134548 allocated core-hours at 4 vCPU / 12 GB. The attempt also retains
4,797,210,311 bytes of copied sample-0 BAMs plus indexes; all other BAMs are links.

The worker now accepts empty engine-created directories, rejects symlinks and
nonempty directories, and exclusively creates a start receipt before commands.
A new real-Snakemake regression invokes the actual worker with only native
commands stubbed; the earlier fixture workers had hidden this directory contract.
Another test verifies prior partial outputs remain protected. All 19 focused
feature tests and the maintained-document check pass.

Retry in a fresh attempt with the replacement code bundle; preserve the failed
attempt. No preprocessing, environment rebuild or native feature recomputation
is needed. The normal input integrity gate runs again against the original BAMs
and creates a new sample-0 copy (about 4.8 GB); the 15-GB free-space check still
applies. Resource limits and scientific settings are unchanged.

## Remaining-nine preprocessing accepted, 2026-09-24

The completed `multisample-preprocess-rau3rfod-return.tar.gz` SHA256 is
`1d143773607eeb3f515ab8359c347a988a0c514a0ff63df8bede78c660ac8a1d` and matches the supplied sidecar. The completed terminal
log SHA256 is `713eb421a57100f8f3995d5e96ca45d33ca75e34a3453fc8a81afa4a58407a5a`. Source is
`4dd3cb9f594495fe2981af4df74a35e1d24d1ad8`, not the subsequently prepared
four-thread retry. The original job finished: no retry, remapping, rethinning
or new download is needed. This supersedes the in-progress/retry handoff below;
its earlier partial-log observations remain historical evidence.

[The review script](../../scripts/e001_review_multisample.py) independently
checks the checksum, unique returned file names, success statuses, all nine
publisher-checksum/read receipts, mapping pipeline exits and filtering arguments,
index exits, per-sample QC/summary equality, CT seeds/fractions and native rule
benchmarks (download benchmarks are absent for the two legitimately reused
archives). Terminal and workflow records show all **35/35 steps complete**.
The exact returned [ordered BAM manifest](multisample-bam-manifest.json) is
preserved byte-for-byte; SHA256 `72fa803ae2a556269a889f0bd55bc648bc76ef6d781722464548c1afb40af962`. It binds the original
accepted sample 0 and all nine new samples to the frozen canonical reference.
Per-sample BAM hashes, byte sizes and paths remain in that manifest; command
records and all returned member hashes are in [observed evidence](multisample-preprocess-observed.json).

| Sample | CT seed | C0 records | CT records | CT/C0 |
| --- | --- | --- | --- | --- |
| 0 | 1000 | 33,158,847 | 3,314,822 | 9.9968% |
| 1 | 1001 | 33,132,912 | 3,310,592 | 9.9919% |
| 2 | 1002 | 32,933,648 | 3,289,999 | 9.9898% |
| 3 | 1003 | 33,177,597 | 3,321,496 | 10.0113% |
| 4 | 1004 | 33,290,348 | 3,330,469 | 10.0043% |
| 5 | 1005 | 33,331,315 | 3,332,346 | 9.9976% |
| 9 | 1006 | 33,252,934 | 3,323,388 | 9.9943% |
| 10 | 1007 | 33,303,665 | 3,330,935 | 10.0017% |
| 11 | 1008 | 32,157,224 | 3,214,428 | 9.9960% |
| 12 | 1009 | 32,602,743 | 3,255,786 | 9.9862% |

Acceptance is based on the returned full-BAM QC and provenance, not a claim
that the large BAMs were downloaded or independently inspected locally. The
next feature input gate verifies their recorded hashes and native header/index
contracts on UCloud, without repeating preprocessing. No model fit, biological
score or H001 result follows from preprocessing success.

Actual run settings: **8 vCPU / 24 GB**, local executor, two sample lanes with
4-vCPU / 10-GB rule reservations, 23-GB aggregate rule-memory cap, one download
slot, **two Strobealign threads per sample**, single-threaded Samtools filter
and sort, 150-bp read profile, `-F 2308`, no extra MAPQ cutoff. CT is replicate
0, 10%, with seeds based on frozen sample index, not literal sample number.
Sources 1/2 reused publisher-verified hardlinked archives; seven were downloaded.

Measured driver time is **9,107.525 seconds = 151.792 minutes**, giving
**20.238946 allocated core-hours**. With accepted sample 0's 2.816146, these two
successful preprocessing drivers total **23.055091 core-hours**. This subtotal
excludes prior failed attempts, setup and owner time outside the drivers; no
complete UCloud invoice or remaining account balance is inferred. Sampled
process CPU/RAM in native benchmarks is separate from allocation charging.

The return records **230,181,868,545 bytes (230.182 decimal GB)** retained inside
this attempt. This is logical file size, including **20.421 GB of hardlinked
reused archives**; it is not additional physical usage on top of the earlier
attempt. Sample 0 contributes another 15.412 GB of retained attempt outputs,
so the two accepted attempt-directory sizes sum to **245.593 GB**, excluding
other attempts, the separately retained sample-0 archive, environments/caches
and temporary job-local workflow copies. All 20 BAMs together are **47.654 GB**.
Nothing was deleted or migrated. Preserve earlier failures and original files.

## Grouped feature workflow prepared, 2026-09-24

[scripts/e001_features.py](../../scripts/e001_features.py) and the
[Snakemake DAG](../../workflows/e001-preprocess/features.smk) implement a shared
hash/header/index gate, three independent native C0/CT/CS tool branches, and an
aggregate receipt that requires every branch to pass. The owner [command](OPERATIONS.md#completed-feature-extraction-and-recovery-instructions-historical)
uses persistent per-tool runtimes plus the reviewed job-local workflow snapshot.
It captures isolated imports, inventories, commands, native streams, interval
and output hashes, zero counts, CS differences, timing and extended benchmarks.
No native scientific tool algorithm or frozen configuration was changed.

Source inspection found that native COMEBin resolves BAM paths **before**
sorting and records resolved basenames (`data_aug/gen_cov.py:run_gen_coverage`).
Symlinks would produce lexically reordered paths and repeated `mapped.bam`
identifiers. Ordered numbered hardlinks preserve the intended axis; cross-device
sample-0 copies are verified. A synthetic regression explicitly demonstrates
that resolving/sorting these aliases preserves the manifest order. Each native
extractor's emitted sample/contig axes are checked, not inferred from arguments.
This convention is now recorded in AGENTS.md.

The [feature plan](feature-plan.json) uses 4 vCPU / 12 GB with one tool active,
3 reserved worker CPUs and 10 GB worker memory. COMEBin uses one coverage worker
plus bedtools; MetaBAT OpenMP and VAMB extraction are capped at three threads.
15 GB additional storage covers the approximately 4.8-GB sample-0 copies,
feature arrays and temporary margin. The 40-core-hour group deadline is a stop
bound, not a runtime forecast. Native full-size extraction remains unexecuted.

The [paired-pilot resource plan](paired-pilot-plan.json) fixes seed 11/C0/CT
without fitting yet. First review these real features and overhead; then finish
the fit/cluster/selection/evaluator launcher with the native full schedules,
complete retained outputs, explicit process/memory budgets and unchanged
80-per-fit/800-total ceilings. Alternatives were immediate fits (premature
before feature validity/CS/resource review) or repeating synthetic preflights
(no new needed evidence). No score has been observed or used to select scope.

Local validation: **17 new focused tests**, including tiny actual BAMs,
checksum/corruption/order failures, cross-filesystem copying, native MetaBAT
scale-table validation, shell logging success/failure, complete driver repeated
invocation with the real Snakemake engine and fixture workers, native command
failure/timeout records, failure packaging, heartbeats, actual DAG success/no-op
repeat, independent tool failure and shared-input failure. Existing native
adapters retain their previous separate Linux smoke evidence. All **179 repository tests passed** (`.venv/bin/python -m unittest discover -s tests -v`);
`python3 scripts/check_docs.py` passed 32 documents/358 links (ten optional legacy
cache paths remain unavailable). Local fixture success is not a native Linux
or scientific result. The committed transfer bundle checksum, required runtime
files, source identity and cache/data exclusions were verified. Its extracted
portable suite passed (17 tests, five expected skips for the unbundled local
engine/owner return); all corresponding engine tests ran in the 179-test local
suite above.

## Remaining-nine Thread Allocation Review, 2026-09-24

The earlier partial snapshot of the owner-run terminal log had SHA-256
`d7b018a592ac2b8228be42e074e2f9260a58fec9283db34ee37543d18c5355a5`.
The same filename now contains the completed log accepted above; the earlier
digest identifies the partial snapshot reviewed at that time. Its source bundle
is `e001-code-4dd3cb9f5944`. That partial log records 8 provided
cores, two concurrent mapping rules each reserved four rule threads, and both
Strobealign processes announcing `Processing paired-end reads using 2 threads`.
The last captured heartbeat is at 17.2 minutes with 47.12 GB retained. The owner
reported the live UCloud CPU graph at about 398.2%. These observations confirm
that Snakemake launched both sample lanes; the log ends while both mappings are
still in progress, so there is no completed C0/CT result or performance result.

The exact setting was deliberate: `scripts/e001_preprocess.py` passed
`cfg["vcpus"] - 2` to the mapper, saving one CPU each for Samtools view and
single-threaded sort. The cloned Strobealign README says `-t N` selects the
mapping/indexing thread count; `src/main.rs` creates N mapping workers. Thus
Strobealign was not failing to see an allocation: it was asked to use two
threads per sample. The inspected local source files have SHA-256
`41c1eaa83263525096599c5747952c2de1f9b6178c24d8c7146551186e9016a5`
(`README.md`) and
`8d3d500175fcb9fd6a69b3d0029d3bd8c9c3b40144e49b6dd51552481e1478ce`
(`src/main.rs`). No conda environment or software installation is needed to
enable four.

For a reversible resource retune, the grouped driver now accepts
`--mapper-threads`; the sample-0 path keeps its original default. The next owner
attempt is planned for 4 vCPU / 12 GB, one sample lane, and four Strobealign
threads. Samtools' single-threaded streaming helpers remain concurrent and can
compete for CPU time within the allocation; the E001 map-rule benchmark will
measure end-to-end wall and CPU time. Do not assume linear scaling or call this
a scientific result. After the current run is stopped, reuse its publisher-
verified sample 1 and 2 archives only if its final `status.json` records
`exit_code: 1`; partial BAMs are not reused. The other seven archives remain
authorized for download. No population, mapping filter, seed, or scientific
scope changed.

## Workflow Filesystem Stall Identified, 2026-09-23

Inspected `e001-multisample.FVzcBP.log` and the complete checksummed
`multisample-preprocess-w_0dxbgy-return.tar.gz`, SHA256
`d7f7a37bc9607a6f8c75ec0f81b081d9e08db6174fd71d8b8450c524df1fa2b4`.
The startup-only run used 8 vCPU / 24 GB, lasted 101.452 seconds and charged
0.225449 allocated core-hours. Mapping checks passed; no DAG/download began.

**Observed proximate cause:** both workflow Python processes reached package
imports and then waited for filesystem reads. Child stacks repeatedly show
`importlib._bootstrap_external.get_data`; pip later reaches distribution
metadata reads. At each timeout Linux reports `D (disk sleep)`,
`folio_wait_bit_common`, and syscall 0 (`read`, x86-64). Different imports
complete between dumps: this is severely delayed I/O, not evidence of a fixed
Python deadlock, site-hook failure or Snakefile parsing error. One small storage
plugin import takes 8.74 seconds. The pip process took another ~11 seconds to
exit after the timeout signal, consistent with blocked kernel I/O. Timeouts are
termination requests, not guarantees of immediate exit from uninterruptible I/O.
The physical/provider-side reason for the storage delay remains unknown.

The new driver introduced short fail-fast limits that expose this condition;
the original unbounded version probe would appear silent. Accepted sample-0
startup was fast in its earlier job. Neither that history nor the new stacks
support changing mapping, thinning, sample selection or Snakemake rules.

Owner-supplied `workflow.tar.gz`: 267,595,287 bytes; SHA256
`0fb6955cdc6263079d2f8f1a32c14037c29d5c90d16c3b3be233ea257c6ab103`.
The archive has 20,402 members (18,719 regular files, 1,683 directories),
744,756,842 extracted bytes, no links. Python is a Linux ELF executable.
Top-level package metadata agrees with every `==` version in accepted sample-0
inventory; packaging retains its recorded Conda direct-origin metadata.
Of 1,818 checked top-level wheel RECORD SHA256 entries, 1,816 match; the two
differences are the `INSTALLER` labels for packaging and pip, not executable
package code. This is a scoped snapshot audit, not a complete supply-chain
attestation. Vendored package metadata is not mistaken for installed top-level
versions. The archive is an ignored transfer asset, not committed data.

**Correction:** use a fresh job-local execution copy of this exact snapshot,
avoiding thousands of reads from the affected persistent prefix. No reinstall,
upgrade or change to the original environment. D006 records the narrow exception
and its portability checks. The grouped command verifies local interpreter and
import origins, requires byte-identical pip inventory to sample 0, checks the CLI
and constructs the real DAG before acquiring reads. Any failure stops before
dependent work and packages evidence. No arbitrary timeout increase or probe
bypass. Scientific commands, two sample lanes and accepted sample-0 reuse stay
unchanged. Native efficacy of the local-copy remedy is pending the owner run;
the storage-read blockage itself is directly observed.

Local verification: **157 portable tests pass**, including corrupt-archive and
unsafe-member rejection, repeated staging without overwrites, executable-mode
preservation, mismatched-inventory stop before DAG, and actual pinned Snakemake
fixture execution. The entire uploaded snapshot extracts successfully with the
production worker on a disposable case-sensitive APFS volume: all 20,402
members and 744,756,842 bytes. Initial extraction on the Mac's default
case-insensitive filesystem correctly refused colliding Linux terminfo names;
no overwrite bypass was added. Linux binaries cannot execute on this Mac;
native prefix/CLI/DAG checks therefore remain in the grouped owner command.

Prepared code transfer: `e001-code-cccf8c7f7846.tar.gz`, source `cccf8c7f7846`,
SHA256 `fbc9c92b9dfb873f291784f304a2b1936507b94d39b852c19d583789898ca8e9`.
The separately transferred software snapshot is
`e001-workflow-0fb6955cdc62.tar.gz` with the owner-archive SHA256 above; each has
an adjacent checksum file. Neither binary archive is tracked. Native upload/run
is pending. This package intentionally predates its documentation-only pin.
The extracted code archive passes 156 tests with one optional older sample-0
engine test skipped because its fixed local environment path is absent; the
remaining-nine real-engine fixtures run. Archive checksum/source identity,
owner-command shell syntax, documentation checks and whitespace checks pass.

## Remaining-nine Member Contract Correction, 2026-09-23

Owner return `multisample-preprocess-i_e659el-return.tar.gz` checksum
`a71f6b6c82d9d520a2df41a6245a4974b74c6d5e696216244b542ecefe1aec96` matches.
The code and workflow snapshot hashes passed at the start of the owner command.
At 8 vCPU / 24 GB, workflow staging, mapping versions, snapshot origin checks,
exact pip inventory, Snakemake startup and DAG all passed. The workflow then
started; this resolves the previous environment startup block for this run.

The first `download` jobs completed for samples 2 and 1. Their acquisition
receipts confirm full publisher MD5 verification and size/ETag matches:
sample 2 is 10,170,187,766 bytes (SHA256
`63910aa2e4a84ecfadaab57b104b3929405bfd5f77986fca1efa26570a76cf23`), sample 1
is 10,250,974,699 bytes (SHA256
`083de4de9c85269b9ae2303e19a56601c1bb1ea26bd7e7dae607d3a4303cc993`). Both
archives and receipts remain in the failed attempt under the shared data root.
Driver elapsed time was 530.819 seconds; cost 1.179599 allocated core-hours.
No FASTQ, C0/CT BAM, features, model fit or biological score was produced.

Extraction raised `ValueError: Inventoried anonymous FASTQ member missing` for
sample 2. The defect was our input-contract assumption: we applied sample 0's
plain member name to each archive without confirming that member for each one.
The dataset description allows `anonymous_reads.fq.gz`; the compact return
does not contain sample 2's member listing, so this record does not claim that
the actual file was gzip-compressed. The sample-specific full-read path must be
selected from the archive, not inferred from the prefix probe or sample 0.

Correction: retain the exact known sample-0 member path. For another sample,
scan the publisher-verified tar and require exactly one regular
`reads/anonymous_reads.fq` or `reads/anonymous_reads.fq.gz` beneath its dated
sample folder. Parse gzip contents when selected; validate paired orientation,
150-bp lengths, that sample's `S{sample}R` read-ID prefix, all pairs through EOF,
and the existing 20-million-pair resource guard. Zero or multiple candidates
fail before creating FASTQ output and include candidate paths. Subsamples and
arbitrary FASTQs are never accepted.

The next run hardlinks the sample 1 and 2 archives from this preserved failed
attempt only after their complete acquisition receipts match frozen publisher
path, MD5, size, ETag and sample directory, then recalculates both MD5 and
SHA-256 over each on-disk archive in one read. A content/receipt mismatch stops
before linking or Snakemake. This adds a local sequential read of about 20.42 GB
but avoids repeating 20.42 GB of network downloads; the remaining seven total
about 71.28 GB. Hardlinked bytes count once in attempt storage reporting. It
writes new receipts in a unique attempt and leaves the originals untouched. The
retry is still the same authorized remaining-nine acquisition;
its data manifest, mapping, thinning seeds, concurrency and allocation do not
change. Failure history is preserved. Focused verification passes: 32 tests
cover plain and gzip extraction, ambiguous-member rejection, archive receipt
and content-mismatch stops, and the local synthetic Snakemake workflow DAG. The full
portable suite was not rerun for this narrow correction. Source commit
`4dd3cb9f594495fe2981af4df74a35e1d24d1ad8` was packaged as
`e001-code-4dd3cb9f5944.tar.gz`, SHA-256
`cc2eb1dc29a845b4496c408ca3aea483878820f62ec40563f64a07504d4a9bc6`; its
embedded `SOURCE_COMMIT` matches and the adjacent checksum verifies.

The previous audit below is preserved; its unresolved-child-operation status is
superseded by the filesystem evidence above. The previous member-path assumption
is superseded by the per-archive correction here.

## Remaining-nine startup audit, 2026-09-23

Audit baseline: `743816624a13` and `cdb4208295fb`; audited all five subsequent
commits through `5a31310`. No history was rewritten and no owner attempt removed.

| Commit | Disposition |
| --- | --- |
| `daf516279eb5` | Retain owner-requested 8-vCPU/24-GB allocation, two lanes and matching tests/docs. No mapper/scientific change. |
| `fe2ae8350db4` | Retain bounded mapper probes, captured streams, failure records and process-group cleanup. These fix silent waiting, not the underlying startup stall. |
| `1b4351252954` | Historical pin to the then-current probe bundle; superseded for next execution. |
| `26e1c03240c2` | Retain inventory pin validation, but reject the inference that bypassing the CLI version check repairs startup. Restore independent CLI validation with early diagnostics. |
| `5a31310df6fc` | Historical package record/pin; its pending-run statements are superseded by the returned failure below. |

Both terminal logs and all regular members of both returns were inspected.
Checksums match; no unsafe paths, links or duplicate members. The original
`daf516` hang remains owner-reported without a returned stack or command record.
It cannot retrospectively be attributed to a specific subprocess with certainty.

| Returned attempt | SHA256 | Observed outcome |
| --- | --- | --- |
| `multisample-preprocess-rptssx2r-return.tar.gz` | `5c7d69041373122a0f6c5df27c22c24122008ff4bed2e3aa59c3369fead2b10b` | `fe2ae83`: mapper probes passed; Snakemake version timed out after 30 s, empty streams. 31.638 s driver, 0.070307 allocated core-hours. |
| `multisample-preprocess-xq_739jv-return.tar.gz` | `644c17ce9de742304802890a60288e9e7b4332cbe69cc6c2ee0f164a50601c65` | `26e1c03`: mapper probes passed; workflow `python -I -m pip freeze` timed out after 60 s, empty streams. 60.178 s driver, 0.133729 allocated core-hours. |

Both used 8 vCPU / 24 GB and neither reached DAG construction, downloads or
preprocessing. Parent `TimeoutExpired` tracebacks do **not** reveal the child's
blocked operation. Earlier successful sample-0 execution does not establish
current environment health. Shared-storage `TMPDIR`, Python startup hooks,
imports and filesystem stalls are possible explanations, not established causes.
No environment rebuild, speculative hook suppression or timeout increase is
justified by these artifacts.

All five existing executable bundles have matching adjacent checksums, safe
unique members, the expected `SOURCE_COMMIT`, and byte-identical files to their
committed source. Each contains 61 regular files including `SOURCE_COMMIT`:

| Source | Bundle SHA256 |
| --- | --- |
| `743816624a13` | `89e0fc30e4595c4c19bd493ede9a8840ffa1c0d498dc80fb9efe6b7fc6cee0cc` |
| `cdb4208295fb` | `2e9a3d71f755e0b120abf5a1dd5660424fced08eb126a5793713d7403efc884c` |
| `daf516279eb5` | `fc428d8c2e351a8cd2b6de34b624971fc15a9463fab004db91f49ed0a059490c` |
| `fe2ae8350db4` | `e134b25cb88692d995c114a31cc5add2dc0bdaa18a10b9ed71f9eb247906a510` |
| `26e1c03240c2` | `834ecdf027c60536ccd8b8be3761d7395b4f45377e428150aab6fe26e28e0564` |

The new launcher enables Python stack dumps before explicitly initializing
`site`, retains normal prefix startup hooks, logs import timing, and executes
pip/Snakemake in the existing isolated interpreter. Both independent probes
are attempted in one return even if one fails. Command provenance is written
at launch with PID/cwd, and Linux process wait state is captured before killing
a timed-out process group. No installed environment is modified. Actual workflow
execution disables the diagnostic timer/import trace to avoid long-run log noise.

**Current boundary:** root cause remains unresolved pending native child evidence.
Use the new `--startup-only` command: at most pip 60 s, Snakemake version 30 s,
and a 120-s DAG dry-run, plus small input checks. It cannot execute rules or
acquire reads. It retains the shared TMPDIR setting for comparability rather
than silently treating an unverified storage hypothesis as a fix.
Local checks include real pinned-engine startup and a complete tiny DAG,
a deliberately hanging `.pth` fixture with captured child stack, probe failure
ordering, startup-only no-acquisition behavior and the existing two-lane DAG.
These validate diagnostics/control flow, not resolution of the UCloud hang.
The full local portable suite passed **153 tests**. The final two-lane fixture
also uses the production launcher, not a substitute CLI path.

Transfer: `artifacts/e001-transfer/e001-code-fcd70c643628.tar.gz`, source
`fcd70c643628`, SHA256
`2a2a067634fdfc2437fc868f6644c0581a12c5be2ffc1640888aec3114ea0c94`.
This new snapshot includes the runtime helper and tests; older snapshots remain
unchanged. The archive precedes this documentation-only pin by design.
Its checksum, safe member paths and embedded source identity pass. From the
extracted archive outside Git, 152 tests pass and one optional older sample-0
engine test skips (its fixed local environment path is absent). Both new runtime
and remaining-nine real-engine tests run using the explicit test-engine path.
Owner-command shell syntax, documentation checks and `git diff --check` pass.
Native upload/execution is pending; no UCloud root-cause resolution is claimed.

The sections below preserve earlier preparation claims and failed attempts;
this audit supersedes their current-action and pending-execution wording.

## Initial bounded version-probe repair, 2026-09-23

The owner reported the grouped preprocessing driver became silent immediately
after `PASS: mapping-environment`. No `workflow-lock`, DAG or workflow stage was
observed, and CPU/network activity was idle. The previous direct
`subprocess.check_output()` calls for strobealign, samtools and Snakemake had no
timeout or command records. This is a driver-observability failure, not evidence
of a mapper or workflow failure; no bulk read acquisition or DAG execution was
reported as started.

The initial replacement ran the three version checks sequentially through the
shared isolated command runner, each with a 30-second timeout and its own
`START`/`PASS`/`FAIL` message,
stdout, stderr and command JSON. The JSON records argv, elapsed time, timeout
status and final return code; timeout handling kills the probe's process group.
Nonzero exits, launch errors, absent output and unexpected versions stop before
the next probe with an explicit failure message. Regression coverage exercises
probe order, nonzero exit, version mismatch and a real short-lived hanging child.

Version pins and the scientific workload were unchanged. That fix changed only
bounded diagnostics and fail-fast behavior; the subsequent owner attempt below
found a separate startup stall before acquisition.

The replacement package was built from clean source commit
`fe2ae8350db46576f2232992269c3e4a7c588322` as
`artifacts/e001-transfer/e001-code-fe2ae8350db4.tar.gz` with SHA256
`e134b25cb88692d995c114a31cc5add2dc0bdaa18a10b9ed71f9eb247906a510`.
Its embedded `SOURCE_COMMIT` matches, `sha256sum --check` passes, and the
extracted archive passes all 12 targeted synthetic probe/command-runner tests.
At package time, UCloud upload and execution were pending; the subsequent owner
attempt and outcome are documented below.
The archive predates this package-record and owner-side bundle-pin documentation
commit; its executable snapshot is the stated source commit.

## Snakemake CLI version-probe follow-up, 2026-09-23

The owner ran the `fe2ae83` bundle. The checksum-verified return
`multisample-preprocess-rptssx2r-return.tar.gz` has SHA256
`5c7d69041373122a0f6c5df27c22c24122008ff4bed2e3aa59c3369fead2b10b`.
`mapping-environment`, strobealign 0.17.0 and samtools 1.24 checks passed.
The `snakemake --version` subprocess emitted no stdout or stderr, exceeded its
30-second limit, and was killed with return code -9. Driver elapsed time was
31.64 seconds and allocated cost 0.0703 core-hours at 8 vCPU / 24 GB. No
workflow-lock, DAG, read download or preprocessing stage began; no software or
research data were downloaded. The archive preserves all command and failure
records. This is evidence of one stalled CLI startup, not proof the persistent
Snakemake environment is broken.

The same persistent workflow environment's earlier accepted sample-0
Snakemake DAG returned 0 in 1.52 seconds, and its recorded package inventory
contains `snakemake==9.13.7`. To avoid paying for a duplicate CLI startup,
the new driver checks the pin from the captured, isolated `pip freeze` record.
The actual Snakemake CLI remains tested by the existing 120-second DAG dry-run,
which is required and occurs before any read download. A failed dry-run will
package evidence and stop before acquisition. Scientific inputs, workflow,
resource allocation and mapper settings are unchanged.

The corrected bundle was built from source commit
`26e1c03240c21ea1eff7e37a97bba1837f51973f` as
`artifacts/e001-transfer/e001-code-26e1c03240c2.tar.gz`; SHA256 is
`834ecdf027c60536ccd8b8be3761d7395b4f45377e428150aab6fe26e28e0564`.
The embedded source commit matches and checksum verification passes. All 14
targeted tests pass in the checkout. In an extracted archive, 13 pass and the
real-engine test is skipped because that temporary copy has no pinned workflow
environment; the same real fixture DAG passed from the checkout. UCloud upload
and rerun are pending. This archive predates the following documentation-only
commit that pins its filename and records its checksum.

## Parallel scheduling reassessment, 2026-09-23

The owner has not begun remaining-nine acquisition or preprocessing; the first
attempt stopped during preflight. [D009](../../docs/decisions/D009-parallel-preprocessing-terminal.md)
corrects the earlier Slurm availability inference: Terminal can initialize an
in-app Slurm cluster, including one node. Thesis profile/workflow/config and
all three requested documentation sources were inspected. No separate app or
provider switch is required. For the present single-node workload, use the
already installed local executor to avoid unnecessary plugin/setup work.

The owner corrected the machine menu using a screenshot: available choices
include **8 vCPU / 24 GB** and **16 vCPU**, not 12. The earlier three-lane
recommendation was prepared but has not run. Current choice is **8 vCPU / 24 GB**,
two 4-vCPU sample lanes, 10-GB sample memory budgets, and a 23-GB global Snakemake
rule-memory cap. Two map workers request 20 GB, leaving 3 GB for overlapping
work. These are scheduler budgets, not hard OS limits. Each lane waits for its
prior sample's CT summary; download concurrency stays at one. Scientific
commands, seeds and data scope remain fixed.

At sample 0's observed 42-minute full preprocessing rate, nine samples on two
lanes imply about 3.5 hours of sample processing before acquisition/I/O effects.
Plan **4-5 elapsed hours / 32-40 allocated core-hours**, not measured runtime.
The 80-core-hour group ceiling permits 10 hours at 8 vCPU. A 16-vCPU allocation
could run more lanes, but may reduce elapsed time without reducing charged
core-hours because the final sample can leave most of that allocation idle. We
prefer 8 vCPU to limit charged resources; no parallel native run has established
actual speedup or cost.

The earlier portable tests passed for the three-lane scheduler implementation.
The actual Snakemake fixture verified that concurrency mode; the updated
8-vCPU/two-lane owner configuration has not been run on UCloud. No result here
establishes native concurrent throughput or peak RAM.

## Full sample-0 preprocessing accepted, 2026-09-21

Return `sample0-preprocess-6_gyxp5d-return.tar.gz` matches SHA256
`4e0e4e64131d11ac42450cae6460a3c7ad06a5add29a4049b3fa540a42c33a8e`.
All 38 archive members are unique safe regular files. Terminal and detailed logs,
all command records, runtime configuration and QC were reviewed. Source is
`4235aa4426e252ab8f3c8a52817a6e2dd3eeae14`; reference and sample archive match
the accepted identities. [Observed record](sample0-preprocess-observed.json)
preserves original JSON and every member hash, plus the terminal-log hash.

Workflow environment creation/install, dry-run, full extraction, streamed
mapping/filter/sort, both indexes, thinning and complete BAM QC all passed.
Only routine package-install warnings occurred; no failed commands. Snakemake
9.13.7 and its returned package inventory are now native-executed, not just a recipe.

| Measurement | Observed |
| --- | --- |
| Actual allocation | 4 vCPU / 12 GB RAM |
| Driver wall time / allocated cost | 2,534.53 s (42.24 min) / 2.81615 core-hours |
| Full read pairs | 16,666,043; exactly the independently counted sample-0 truth total |
| Extraction including archive verification | 141.09 s; FASTQ 10,610,713,214 bytes |
| Map/sort/index/QC rule | 2,316.83 s; mapper itself reports 2,013.15 s mapping |
| C0 primary mapped records / BAM bytes | 33,158,847 / 4,319,070,969 |
| CT records / BAM bytes | 3,314,822 / 478,139,342 |
| CT fraction and seed | 0.0999679512 observed; 0.1 requested; seed 1000 |
| CT thinning/index/QC rule | 42.39 s |
| New attempt storage | 15,411,548,225 bytes (15.412 decimal GB) |

Cost excludes owner idle time outside the driver. Storage excludes the original
9.739 GB archive, existing environments and earlier attempts. No peak RAM was
measured; successful execution within the reported allocation is the evidence.
**Accepted: preserve and reuse sample 0; do not remap, rethin or reinstall it.**
This is operational preprocessing, not a biological result or H001 test.

### Next grouped acquisition/preprocessing

[Plan](multisample-plan.json) and [workflow](../../workflows/e001-preprocess/multisample.smk)
cover samples 1,2,3,4,5,9,10,11,12, in frozen order. HTTP HEAD plus 64 KiB
range probes confirmed each archive's size, ETag and dated sample directory;
the nine archives total **91,698,809,375 bytes**. Full payloads were not downloaded
locally. Publisher MD5s are verified on owner download before extraction. Sample 0
proved its own plain `reads/anonymous_reads.fq` member only; it did not establish
the other nine members. The corrected per-sample resolver requires one unique
full `anonymous_reads.fq` or `.fq.gz`, never a subsample or simulator BAM. Small
public read-origin metadata prefixes confirm `S{sample}R` IDs in each library.
Extraction validates every pair to EOF; other libraries are not forced to have
sample 0's exact count. The 20-million-pair bound is a stop-for-review resource
guard, never truncation or sample selection.

Nine times the measured 2,503.92-second workflow gives **6.26 hours / 25.04
allocated core-hours** at the same allocation, before acquisition. Allow roughly
7-9 hours total at comparable network/I/O throughput; this is a projection,
not a guarantee. The driver has an **80 allocated-core-hour group ceiling**
(20 hours at 4 vCPU), including download/wait/setup probes, within the 200-hour
preprocessing envelope. No linear speedup assumption for other allocations.

Projected new retained storage is **230.40 GB** including all nine archives,
FASTQs and C0/CT outputs; future features/replicates add space. With existing
data/environments this does not safely fit the initial 250 GB Home quota.
The explicit owner command therefore uses the offered shared project directory
for new heavy data, checks 275 GB free initially and 35 GB before each sample,
and leaves environments/sample 0 in Home. No files are deleted or moved.
Filesystem free space is not a project-quota measurement; the owner must mount
the shared directory with sufficient quota. Sequential sample dependencies keep
download/extraction/sort workspaces from overlapping. A failure stops the group,
preserves completed outputs and packages logs for targeted continuation.

### Observability and scheduler choice

New rules have one-shot `benchmark:` TSVs with `--benchmark-extended`, recording
wall time, sampled process-tree RSS/CPU/I/O and requested rule resources. No
benchmark repeats and no sample-0 rerun. These complement, not replace, driver
wall-time times allocated-vCPU accounting. Sampled RSS can miss short peaks and
does not include the entire UCloud container. Detailed per-tool stderr/commands
are retained, with live timestamped mirroring and a 60-second progress heartbeat.

[Snakemake documentation](https://snakemake.readthedocs.io/en/stable/snakefiles/rules.html#benchmark-rules)
was checked alongside the locally installed **9.13.7** implementation; the live
documentation currently describes a newer release, so the pinned engine itself
is tested. The [Slurm executor](https://snakemake.github.io/snakemake-plugin-catalog/plugins/executor/slurm.html)
submits to a Slurm scheduler. The original assessment inferred that the SDU/K8s
Terminal setup required another provider for Slurm. **Corrected by D009:** Terminal
can itself create the scheduler, including on one node. The local executor is
retained for this workload's simplicity, not because Terminal lacks Slurm.

Local implementation validation finalized 2026-09-23: **143 portable tests pass**.
New coverage includes bounded/checksummed acquisition failures, partial-file
preservation, complete read/sample validation, accepted-sample reuse, explicit
allocation/acquisition guards, grouped driver order and repeat preservation,
packaging failure, live progress, sample-9 read group/seed, and ordered manifests.
The actual pinned Snakemake engine executed a two-sample fixture DAG, produced
eight extended benchmark TSVs, and reported nothing to do on a second invocation.
This validates orchestration with a fixture worker, not a new native mapper run.
Documentation/link checks and whitespace checks pass. Native execution of the
remaining-nine-sample workflow is prepared, not completed; no model was trained.

## All three mapper attempts reviewed, 2026-09-21

The [observed record](mapper-observed.json) preserves all three checksum-verified
archives, exact source/driver identities, command records, allocation, prefix
hashes and successful summary. All terminal logs and captured stdout/stderr were
reviewed. Bowtie2's resolved package list has the same SHA256 in every attempt.
Both corrective commits remain intact.

| Attempt | Source | Outcome | Allocated core-hours |
| --- | --- | --- | --- |
| `13l53afq` | `601cae3` | Bowtie2 setup and sample-0 acquisition passed; wrong `.fq.gz` member stopped extraction before mapping | 0.793842 |
| `3nyb_km0` | `dbee019` | Reused identical archive; the guessed replacement member also failed before mapping | 0.054069 |
| `89gpt00u` | `216c896` | Verified plain anonymous FASTQ, 100,000 pairs, both mappings/filter/sort/index and summaries passed | 0.827075 |

The publisher archive SHA256 is unchanged across attempts:
`6f349a6f3299b4595f8c5acfb9ad7d8e2fc56fe657c1a451cde90e92c364f113`.
The third attempt used the existing archive, not another download. All used
4 vCPU / 12 GB. Combined driver accounting is 1.674986 core-hours, excluding
job time outside the drivers. The accepted attempt took 744.37 seconds, dominated
by Bowtie2 index construction, not read mapping.

| Measurement | strobealign 0.17.0 | Bowtie2 2.5.4 |
| --- | --- | --- |
| Command mapping time | 17.390 s, including reference indexing | 27.300 s, excluding index build |
| Reference indexing | 10.96 s, native log (inside mapping command) | 676.320 s, separate build command |
| Native mapping-only time | 5.83 s, native log | Not separately reported from command |
| Primary mapped reads / 200,000 | 199,036 (99.518%) | 198,731 (99.3655%) |
| MAPQ-zero mapped reads | 111,641 | 42 |
| Sorted BAM bytes | 30,684,630 | 34,158,421 |
| BAM bytes per input pair | 306.8463 | 341.58421 |

Completed-child peak RSS was 4,312,244 KiB (~4.11 GiB), a maximum across sequential
subprocesses, not per-mapper or aggregate whole-job RAM. Successful attempt disk
use was 1,526,832,160 bytes, excluding the retained 9.74 GB archive in the first
attempt. For **planning only**, 16.67 million pairs/sample (5 Gbp at 2x150 bp)
would imply ~5.11 GB strobealign BAM/sample, ~51.1 GB for ten samples. This is a
linear prefix-based estimate, not a measured full-sample size; indexes, raw
archives/reads, other tool features and intermediate files add storage. No need
to move existing small artifacts to shared storage now.

**Accept operational mapper/storage feasibility. Do not rerun this task.** This
does not establish mapping accuracy or finalize the provisional mapper. Only
98,232/200,000 reads (49.116%) have the same mapped reference/start/strand, with
964 unmapped by both. Bowtie2 itself reports 61,799 pairs with multiple concordant
alignments, despite only 42 MAPQ-zero records. Thus MAPQ-zero alone is not a
cross-mapper ambiguity comparison, and mapped percentage cannot choose a winner.
Ambiguity/tie handling is a plausible explanation, not a demonstrated one.

### Local follow-through completed

[e001_mapper_diagnostics.py](../../scripts/e001_mapper_diagnostics.py) analyzes
the existing BAMs against frozen destination-contig origins. It separates exact
placement, same-contig differences, shared-origin different contigs, disjoint-origin
contigs and one-mapper-only assignments; records complete MAPQ/NM/AS-XS histograms,
per-category MAPQ and per-contig read counts. Score scales are not treated as
interchangeable, and destination-origin agreement is not read-origin truth.

The owner supplied both BAMs during this session under `agent_context/mapping/`.
Both match their accepted hashes; local analysis reproduced all earlier counts.
91,339 reads move between disjoint destination-genome sets, 8,954 differ within
one contig, 206 move between contigs sharing a genome origin, and 305 map only
with strobealign. The summed absolute per-contig read-count difference is 32,349;
this is not a base-coverage or accuracy measure. Most cross-genome disagreements
are low-confidence under both tools: 90,046 strobealign MAPQ 0, 90,894 Bowtie2
MAPQ 1. Bowtie2 reports equal AS/XS for 114,509 mapped reads; different confidence
conventions explain why MAPQ-zero counts alone were misleading.

Because cross-genome disagreements were substantial, local analysis continued
directly to read-origin truth, without another owner task. Unlike the FASTQ,
the public `reads/reads_mapping.tsv.gz` object is readable. The 293,229,761-byte
download matches its object MD5 `15cbaa7866defbf486043533e293faf3` and SHA256
`691dc251b267fe301d8f5ef0cf3cf34333648a146539843da0b2a735106fe296`.
All 33,332,086 metadata rows were scanned with gzip CRC validation; all 199,036
mates mapped by either tool joined uniquely. No read sequences were downloaded.
[Diagnostic record](mapper-diagnostics.json) owns URL, identities and results.

True-source-genome compatibility is 105,795 reads for strobealign versus 105,697
for Bowtie2 on the same 200,000-read denominator. Both are compatible for 93,735;
only strobealign for 12,060; only Bowtie2 for 11,962. This is not a significant
accuracy advantage, nor does it establish that ambiguous reads are uniquely
identifiable. [D008](../../docs/decisions/D008-mapper-and-first-preprocessing-slice.md)
retains strobealign and no added MAPQ cutoff, with native downstream filters.
The population is not changed and no mapping rerun is needed.

The next implemented task is the [Snakemake preprocessing slice](../../workflows/e001-preprocess/Snakefile):
full existing sample 0 only, validated interleaved FASTQ, streamed C0 mapping,
seed-1000 10% CT and compact QC/resource reporting. Source truth establishes the
expected 16,666,043 pairs. Snakemake 9.13.7 was installed in an isolated local
test environment and its actual DAG dry-run passed. Portable tests exercise
full extraction/count mismatch, overwrite protection, actual allocation, grouped
driver order, failed prerequisites and repeated-attempt preservation.
All **130 portable tests pass**, including the real pinned-engine DAG dry-run.
At that checkpoint native preprocessing was **prepared, not run**. The subsequent
accepted sample-0 return and bounded next scope are recorded above; scientific
model fits remain unlaunched.

## Integration accepted and accounting corrected, 2026-09-21

`native-integration-p1upv3gg-return.tar.gz` matches its supplied SHA256; source
0855646, driver hash and frozen input identity match. [Observed record](native-integration-observed.json)
records 128 contigs / 2,841,187 bp, both complete AMBER handoffs, 128 VAMB clusters,
52 COMEBin marker hits / 2 seeds, and all 120 native candidates with 128 rows each.
Native CheckM profiling and winner selection completed. Stderr contains the
known pkg_resources deprecation and the marker HMM fallback to E=1e-5 because
the source HMM lacks model-wide TC cutoffs; no failed commands. No biological
quality claim is made from random embeddings.

Total 105.522 seconds at owner-reported **4 vCPU / 12 GB** = **0.117 core-hours**.
The returned driver incorrectly assumed 8; raw evidence is preserved.
COMEBin's earlier optimizer check actually used **2 vCPU / 6 GB**, so its charged
projection is **23.946 / 47.891 core-hours per fit** (central / twofold), and
**143.674 / 287.348 for six fits**. These recalculate measured wall time, not a
speedup extrapolation. [Corrections](allocation-corrections.json) and amended
[D007](../../docs/decisions/D007-comebin-resource-envelope.md) supersede earlier
cost conclusions; no repeat of accepted native checks is necessary. No change
is inferred to the separate MetaBAT2/VAMB allocations.

### Next mapper task and acquisition boundary

On 2026-09-21 the direct Swift object's HEAD returns HTTP 200, size 5,166,013,564
and `x-object-manifest` pointing to a segmented object. A 64 KiB Range GET still
returns HTTP 401. This establishes that a listing/HEAD is not proof of readable
contents; it suggests a segmented-object access issue, not a confirmed diagnosis.
The public publisher archive remains the explicit fallback, not an authentication
workaround. It is one 9.74 GB sample archive, with size/ETag pinned from the earlier
probe. No such archive was downloaded locally.

The new [mapper driver](../../scripts/e001_mapper_feasibility.py) requires either
an existing sample archive or explicit `--allow-sample-archive` authorization.
It installs Bowtie2 2.5.4 separately, extracts only the first 100,000 complete
150-bp pairs, maps identical reads to the frozen assembly with both mappers,
and records index cost, mapping/filter/sort time, primary alignment agreement,
MAPQ-zero counts, BAM bytes per input pair and attempt disk size. Agreement is
not accuracy; an input-order prefix is not a representative community sample.
Expected runtime and network transfer speed remain unmeasured. Timeouts are stop
limits, not expected runtimes. Actual allocation is mandatory CLI input.
Portable tests cover extraction, mate mismatch, short/missing input, changed
remote metadata, opt-in, grouped stage order, allocation accounting and retries.
Native Bowtie2 solve and real-read execution remain owner-run and unvalidated.
All 119 portable tests pass. Publisher HEAD was rechecked on 2026-09-21 and
matches the pinned 9,738,621,091-byte size and ETag; no payload was fetched.

### Mapper owner attempt failed at archive-member lookup, 2026-09-21

The owner ran the mapper feasibility bundle at 4 vCPU / 12 GB. The Bowtie2
environment setup and package lock passed. The single 9,738,621,091-byte
publisher archive was downloaded and its recorded SHA-256 is
`6f349a6f3299b4595f8c5acfb9ad7d8e2fc56fe657c1a451cde90e92c364f113`.
Extraction then stopped before any index build or mapper execution because the
driver searched for
`2017.12.04_18.45.54_sample_0/reads/anonymous_reads.fq.gz`; the archive
member had not yet been inventoried. The earlier suggestion that the member
was below `short_read/` came from a separate publisher object listing and was
not an inner-archive observation. The attempt used 0.794 allocated core-hours
and preserved the archive for reuse.

The owner subsequently listed the retained archive and found exactly these
read-like members:

```text
2017.12.04_18.45.54_sample_0/reads/anonymous_reads.fq
2017.12.04_18.45.54_sample_0/reads/subsample_0.fq
```

CAMISIM documents `anonymous_reads.fq` as the complete anonymized read file;
the mapper therefore pins that plain FASTQ and does not silently use
`subsample_0.fq`. The driver now supports both plain and gzip FASTQ members,
and must be rerun with the retained archive through `--archive`.

## COMEBin and MetaBAT2 accepted separately, 2026-09-21

Both archives match their supplied SHA256 checksums. Recorded driver hashes match
the executed Git snapshots and frozen-input identity. Intentional fixes f4cf0c0
(isolated imports), 41d0f9d (zlib pin), and f9c983a (expected empty MetaBAT2 scale
control) remain intact, without duplicate fixes.

- **COMEBin:** `native-remaining-2sf0rot9` passes imports, pip check, native smoke
  and full-batch CPU measurement at source f4cf0c0. Group exit 1 reflects the
  separate MetaBAT2 failure. [Observed record](native-comebin-observed.json):
  six views, batch 1024, 17,928,576 parameters, logits 30,720 x 6,139. Measured
  steps 9.796/9.399 seconds project 95.783 allocated core-hours per 200-epoch fit,
  191.565 with margin, excluding downstream work. Parent peak RSS 4,688,072 KiB.
  All six views changed 22 mean/variance entries; CS maximum difference 2.1333e-5.
  Setup stdout confirms CheckM database postlink download/extraction into the
  persistent COMEBin environment. Do not download it again for integration.
- **MetaBAT2:** `native-remaining-uvkhdn0o`, source f9c983a, passes its separate
  rerun. [Observed record](native-metabat-observed.json) preserves the legitimate
  expected-empty tiny CS result. At frozen population size, synthetic binning
  assigned 21,405 of 22,594 contigs in 152.450 seconds / 0.339 allocated core-hours;
  completed-child peak RSS 4,759,524 KiB. This excludes BAM extraction and is not
  a real-data runtime guarantee. Whole attempt: 0.421 core-hours.

[D007](../../docs/decisions/D007-comebin-resource-envelope.md) records a prospective
COMEBin-only limit of 200 core-hours, following owner acceptance, while retaining
the 800 total. Six conservative fits exceed that total: actual pilot cost must
inform remaining replicate authorization, independently of biological scores.

The [integration driver](../../scripts/e001_integration.py) groups VAMB/COMEBin
clustering and AMBER handoff, including COMEBin's full grid and marker selection.
Local portable suite: **110 tests passed**, covering repeated unique attempts,
isolated entrypoint, independent failure handling, packaging failure and changed
frozen inputs. Fixture preparation passed on the actual local frozen input too:
128 contigs, 2,841,187 bp, FASTA SHA256
`532315bd216c16daca50af6867a5dba26ea26a73286ffa5ab0196b9fcb1f5355`.
Native Linux clustering/marker/evaluator execution is prepared, **not yet run**.

### Read-prefix access observation, 2026-09-20

A 65,536-byte Range request to
`https://frl.publisso.de/data/frl%3A6425518/gastrooral/sample_0.tar.gz`
returned HTTP 206, total 9,738,621,091 bytes, ETag
`"2447790a3-5d68d6c44295d"`. Its tar prefix begins with
`2017.12.04_18.45.54_sample_0/bam/`, not FASTQ. The container listing at
`https://openstack.cebitec.uni-bielefeld.de:8080/swift/v1/CAMI_Gastrointestinal_tract`
lists `short_read/2017.12.04_18.45.54_sample_0/reads/anonymous_reads.fq.gz`,
but a Range request to that object returned HTTP 401. No read prefix was acquired
and no bulk archive downloaded. Resolve access or explicitly choose a bounded
alternative before mapper throughput work; this is not a reason to reopen the
settled assembly inventory or silently authorize a 9.74 GB download.

## VAMB accepted and remaining tools grouped, 2026-09-20

Owner return `agent_context/native-vamb-rdow5991-return.tar.gz` matches checksum
`01cd6239ccae05551b7882c42ac5ba2737880a24be69c837e2d5e4a0bae1f77e`.
Its driver and frozen-input hashes match the executed snapshot. Source commit
`e129cefe6f5d0eeac9c17be43b885b8b1d225129`; run began 2026-09-20 18:09:39 UTC
on `j-12397090-job-0`. All setup/import/pip/native-smoke/CPU stages passed.
Setup stderr has ordinary clone/package-script notices, no reported error;
smoke and CPU stderr are empty. Python 3.12.10, NumPy 1.26.4 and CPU PyTorch
2.6.0+cpu are isolated at the expected VAMB prefix. Resolved locks were inspected.

[Observed data](native-vamb-observed.json) preserve per-batch timings and provenance.
Total driver 170.91 seconds / 0.190 allocated core-hours (4 vCPU); optimizer
process peak RSS 826,980 KiB. Native normalized C0/CS composition, total abundance
and weights match exactly; largest coverage difference is 5.96e-8.
The 300-epoch schedule projects **0.814 core-hours per fit**, **1.628 with a twofold
margin**. Accept VAMB native synthetic compatibility and optimizer feasibility,
not full-pipeline cost or biological performance. Do not rerun it in the group.

[D006](../../docs/decisions/D006-environment-ownership.md) retains separate
experiment-owned environments for all five E001 tools, reused across gates.
The grouped driver attempts MetaBAT2 and COMEBin independently, preserves partial
failures and packages both outcomes. It leaves accepted runtimes and inputs alone.

Two previously unexecuted setup recipes were hardened after source inspection:
- COMEBin's hnswlib pip dependency may compile; add the pinned C++ compiler to
  the environment-file solve and explicitly select its executable. The tool's
  scientific dependency pins/source remain unchanged. Micromamba's official
  [setup documentation](https://github.com/mamba-org/setup-micromamba) describes
  extra create specs with environment files (not explicit lockfiles).
- MetaBAT source `src/CMakeLists.txt` forces static Boost. Build with the pinned
  Conda shared Boost libraries via the one-line [build patch](metabat-shared-boost.patch)
  in a separate `build/metabat-source` copy. The original execution checkout
  remains pristine; preserve patch/hash and binary hashes in locks. This changes
  linkage, not binning logic, and native smoke remains required. The patch passes
  `git apply --check` against the exact cached commit. Anaconda package metadata
  confirms the pinned libboost/libboost-devel 1.85.0 packages; no native build is
  claimed from metadata or patch inspection alone.

All **102 portable tests passed**, including two isolated tool prefixes, repeat
invocation without reinstall, continuing the second tool after first-tool setup
or smoke failure, preserving partial environments, packaging failure and small
synthetic MetaBAT generation/membership parsing, and selecting only a failed tool
for reviewed recovery without rerunning its accepted peer. Shell syntax and documentation
checks passed. Native grouped Linux execution remains pending. COMEBin timing
uses its source model/InfoNCE at the full six-view batch, without changing loss,
batch or native scientific schedule to improve the projection. MetaBAT CPU timing
uses synthetic uniform lengths/groups and is not a real-data runtime guarantee.

## Owner population frozen and VAMB step prepared, 2026-09-20

Return `agent_context/inventory-resume-6z45cola-return.tar.gz` verified SHA-256
`1bf9a1b442a31cd069b9d9dffcf587e9365a9627a9ad4b9107a74552fd4a8cb2`.
Executed source `64664ac6860b75d5a92c430c222e59f3418b5909`, code hashes and
taxonomy policy match the reviewed snapshot. All five prepared output hashes,
population counts/gates and all taxonomy member hashes match the local validation.
All 196 tax IDs / 259 genomes resolve as expected. All stage stderr files are
empty; exit 0. Run began 2026-09-20 10:48:22 UTC on `j-12396906-job-0`, took
40.06 seconds and reported child peak RSS 620,856 KiB. These are process statistics,
not full allocated job spend. Accepted UCloud input path and immutable output
identities are recorded in [frozen-inputs.json](frozen-inputs.json).

This closes the taxonomy/population prerequisite. No new biological score exists.
Native VAMB is selected next because its pinned CPU dependencies and simpler model
provide a bounded first learned-baseline check. COMEBin-first could expose the
largest compute risk sooner, but its more complex unresolved environment would
combine additional failure sources; it remains the next learned-runtime check,
not an optional baseline. MetaBAT2-first would not answer learned CPU feasibility.

The [new driver](../../scripts/e001_vamb_cpu.py) groups installation, import/pip
checks, existing native synthetic smoke and synthetic full-dimension CPU timing.
Local source inspection confirms the CLI schedule is 300 epochs with doubling at
25/75/150/225, not the different `trainmodel` Python API defaults. Use native
`make_dataloader`, `VAE.trainepoch` and DAdaptAdam without copying model/loss code.
No true sequences/coverage/labels enter timing and no model is saved.
PyPI metadata checked on 2026-09-20 confirms Linux x86_64 CPython 3.12 wheels for
vambcore 0.1.2, pycoverm 0.6.2, pyhmmer 0.10.15 and pyrodigal 3.6.3; this is not
an installed-runtime claim. Source/dependency pins remain unchanged.

All **95 portable tests passed**, including mocked complete VAMB-driver sequencing,
repeat invocation without reinstallation, setup/partial-environment/missing-fixture
failure returns, packaging failure and a real subprocess timeout. Projection
arithmetic/schedule are checked. Mocked orchestration does not establish native
Linux smoke or throughput: those are explicitly awaiting the owner run. Treat
smoke failure as a runtime blocker; interpret measured training projection with
the recorded per-fit and total budget limits before proceeding to science.

## Historical taxonomy and local population, 2026-09-20

The owner's local taxonomy archive was independently verified against the live
CAMI page and object metadata, then every member hashed. All 196 GI tax IDs resolve
directly to Bacteria for all 259 source genomes. The actual local full-data
`prepare-hmp --nodes` run passes all five population gates without any threshold
change: 224 evaluation genomes and 7,964 short queries spanning 66 genomes.
Canonical FASTA/truth hashes are unchanged from the accepted owner conversion.
See the [evidence and requirements](../../docs/evidence/2026-09-20-gi-taxonomy.md)
and [pinned policy](taxonomy-policy.json) for source/output identities.
Ignored local outputs: `artifacts/e001-taxonomy-reviewed/` and
`artifacts/e001-population-reviewed/`; no raw data or taxonomy is tracked.

All **88 portable tests passed**. New tests exercise complete taxonomy-aware
owner-driver invocation twice, invariant output checks, corrupted archive,
wrong member hash, missing/duplicate members, wrong mapping and domain coverage,
and missing-root/cyclic/duplicate taxonomy nodes. Failed attempts retain logs;
return archives contain coverage reports but not the 145 MB nodes table.
The full-data preparation used the existing macOS environment; owner Linux
taxonomy-aware execution remains pending. No read download or model training ran.

Transfer `artifacts/e001-transfer/e001-code-64664ac6860b.tar.gz` and its checksum
were built from committed code. The archive checksum passed and all 88 tests
also passed from its extracted copy outside the repository (18.14 seconds).

## Owner conversion accepted, 2026-09-20

Reviewed local inbox archive `agent_context/inventory-resume-ef6z97y9-return.tar.gz`;
SHA-256 `55705be2a9a01c7b4b43340bd61ed4e5fe4350275badc34b7439073282c73086`
matches the supplied checksum. The archive remains untracked. Its originating
attempt is `/work/Home/dl_binner/e001/e001-gate0/inventory-resume-ef6z97y9`.
Source commit: `9e1f939d4585bdf191dd562787932431235ff281`; returned code hashes
match local committed code, and the returned policy matches byte for byte.

- Execution started 2026-09-19 at 21:50:41 UTC on `j-12396660-job-0`.
  Environment, audit and conversion passed with empty stderr and exit code 0.
  Persistent mapping Python 3.12.10 / Biopython 1.85 passed isolation checks.
- Full setup archive/original mapping verification passed; all three setup
  metadata member hashes match the reviewed policy. Source FASTA and corrected
  mapping hashes match D005. The raw join audit still reports false, as expected:
  it describes the unmodified input before the explicit quarantine policy.
- Exactly 20 foreign-provenance intervals (28,917,470 bp), two empty artifacts
  and six coordinate-alias groups were accounted for. No additional invalid DNA,
  length mismatch, duplicate FASTA key or mapping-only key was reported.
- Conversion retained **22,594 contigs / 817,438,232 bp** at the 2,500 bp cutoff
  from 210,612 truth-joined physical contigs. Canonical FASTA SHA-256:
  `14870c27bc9467b5897bd1b65b347d7d5e2733d8bbe48c0085cb708194966fe1`;
  truth TSV: `f6e1b948f2fbbc6ed404ea27e73fb238bd2f34765b585e8e3fbe77f59b25c301`.
  These are returned output hashes, not independently rehashed local outputs.
- Elapsed 31.37 seconds; child peak RSS 614,272 KiB (about 600 MiB).
  These process measurements do not measure total allocated job cost.
- Population status `blocked` is expected: `nodes` is null, domains unresolved,
  and eligible genomes/short queries are zero pending taxonomy. The reported
  817,438,232 excluded retained bp are currently outside the scored population,
  not removed from the canonical FASTA. Population sufficiency is not yet known.

Conclusion: accept the D005 conversion and continue with the declared GI
development derivative; no dataset switch is warranted by this return. This
does not certify the entire publisher dataset or establish biological results.
Next verify the historical taxonomy and resolve the scored population. The
owner-supplied `setup-members.json` contains no taxonomy/nodes payload. No further
UCloud files are required to start that investigation; the owner can supply
specific files up to 10 GB if local inspection becomes useful.

## Prior implementation review, 2026-09-19

[Publisher provenance investigation](../../docs/evidence/2026-09-19-gi-provenance.md)
resolves all 20 FASTA-only intervals through seven conflicting BAM headers.
[D005](../../docs/decisions/D005-gi-input-derivative.md) records the derivative
decision. The new driver validates the source-bound policy, rechecks the persistent
environment on every job, and creates distinct attempts without moving old data.
Legacy inventory/retry drivers are retired to avoid executing the hardcoded first
snapshot or failing on output-name collisions.

All **82 portable tests passed** locally, including full synthetic owner-driver
execution twice with an empty system PATH, injected Python paths, alias
canonicalization, known empty artifacts, explicit
foreign-record quarantine, completed return/checksum verification, and prior-output
preservation. Corrupted setup metadata and a missing persistent environment stop
before conversion and return logs. A packaging failure returns nonzero and marks
the retained status as failed rather than claiming success.
Additional regressions cover policy source changes, missing/overlapping exceptions,
wrong orphan counts, duplicate truth rows and malformed-header DNA validation.
This does not establish a successful conversion of the real GI data or fresh-job
Linux execution. No scientific conversion was rerun locally.

The owner's newly supplied local inventory allowed a full read-only audit with
the corrected validator. FASTA/mapping hashes matched the policy, all 20 unmatched
keys matched its exact interval set, and the mapping contract passed (210,612
keys, six aliases). The setup archive is absent from the supplied local folder;
full setup/member checks will run on its existing UCloud copy.

Corrections to prior interpretations: raw audit JSON establishes only the underscore
orphan ID, not Biopython normalization of asterisks. The earlier return's absence
of an inventory file did not prove absence of a partial output directory. The
previous chat's claim that Gate 0 was complete was incorrect: other native baseline
checks remain open. Older paragraphs below are dated execution history.

## Executed locally

- macOS Intel, Python 3.13.2; isolated `.venv` with NumPy 2.2.6, Biopython 1.85 and pysam 0.23.3. This is the harness environment, not any native binner environment.
- `.venv/bin/python -m unittest discover -s tests -v`: 56 portable tests passed, including CLI smoke. Fixtures cover perfect/merged/split/missing/empty assignments, ambiguity, exact thresholds, fixed-denominator length strata, malformed joins/coordinates, duplicate predictions, anonymous IDs, reverse-complement duplicate detection, missing taxonomy, zero/filtered feature rows, unsafe archives, mocked download checksums/limits, dry-run acquisition, all-view scaling, stale coverage tensors, and failed-attempt provenance.
- `bash -n scripts/e001_linux_setup.sh scripts/e001_linux_smoke.sh`: passed. Syntax validation does not establish environment solvability or runtime success.
- Public directory/README/checksum metadata and bounded file prefixes were inspected as documented in the [audit](../../docs/evidence/2026-09-18-human-cpu-audit.md). No complete GSA, truth, read archive or scientific feature set was downloaded.

- `verify-source` passed for the four selected native repositories: independent roots, expected commits, no tracked changes, and only allowed Finder metadata untracked. None of the reference caches was modified.
- `python3 scripts/check_docs.py --check-context` passed, including all 83 present source fingerprints. Ten optional missing ZIP-cache paths belong to the explicitly historical September 16 notes, not current baseline provenance.
- Python AST parsing and `git diff --check` passed for the implementation. The separately committed owner brief retains its original trailing space; source briefs were preserved verbatim, not reformatted.

### Transfer preparation, 2026-09-18

At transfer preparation, no UCloud execution had occurred. The updated portable suite passes **59 tests**, including committed-file allowlisting, source-commit/checksum preservation, refusal to overwrite transfers, dirty-checkout rejection and symlink rejection. Shell syntax and documentation/context checks pass. Source validation now reports a contract error even outside a Git checkout, as expected for transferred code. Setup logging and persistent package-cache paths are prepared but not Linux-validated. The bundle contains no environments, source-paper/thesis caches or research data. The later owner-returned probe below updates transfer status; native outcomes remain pending.

The actual transfer archive was built from committed source `9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea` and inspected locally. All **59 tests also passed from its extracted copy outside Git**, using the existing macOS portable environment; this does not validate Linux dependency resolution. `shasum -a 256 -c` passed. Local ignored locator: `artifacts/e001-transfer/e001-code-9c2b0ec6feb3.tar.gz`, with adjacent `.tar.gz.sha256`; approximately 47 KiB. SHA-256: `be85a52dd47eaab8aa9b68f3f9aaa38541d43ed9b68695c26169f95e111a3c85`. Intended owner-side upload locator: `/work/Home/dl_binner/e001/e001-gate0/transfer/`. Upload has not been confirmed. The package intentionally predates this results-only record; its embedded `SOURCE_COMMIT` identifies the executable snapshot. The builder can regenerate equivalent code from that commit, but gzip timestamps mean a rebuilt archive must receive its own checksum.

## Owner-returned initial probe, 2026-09-18

Source: output supplied by the owner in chat, inspected here; not direct HPC access. Job identifier `j-12396047-job-0`, start 15:29 on 2026-09-18 (owner-reported local time; timezone not independently verified). Owner reports **4 vCPU / 12 GB RAM**. Actual submitted duration/end time has not been supplied. The original 8-vCPU/24-GB recommendation was conservative, not a scientific requirement; retain the smaller allocation for extraction and prerequisite bootstrap. Native smoke feasibility remains unmeasured.

- Working directory `/work/Home/dl_binner/e001/e001-gate0/transfer`; mounted filesystem `/work/Home`.
- Ubuntu 24.04.4 LTS, Linux x86_64. Bash, Git, Python 3, tar, sha256sum, timeout, curl and bzip2 are present at `/usr/bin/` paths. **micromamba and `/usr/bin/time` are missing**. Presence alone does not validate program versions.
- Owner's `sha256sum --check` reports `e001-code-9c2b0ec6feb3.tar.gz: OK`. This supersedes the pending upload status at package preparation. Code extraction and all installations remain unconfirmed.
- Startup banner reports AMD EPYC 9535, 256 visible CPUs, roughly 755 GiB host RAM and 13-day uptime. These are not the owner's 4-vCPU/12-GB allocation or elapsed job time. `df` reports shared filesystem capacity (7.2P total, 2.1P available), not personal quota. The ASPEED graphics listing does not establish an allocated ML accelerator; the job remains CPU-only.
- SSH/ttyd startup messages contain no reported failure and do not require SSH configuration for this browser-terminal workflow.

The next checkpoint at that time was extraction. The owner has subsequently returned a successful checksum, `Code extraction verified` at the expected path, and full source commit `9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea`. Extraction is now confirmed. No software installation, native smoke or research-data acquisition has been reported.

## Grouped driver preparation, 2026-09-18

The owner explicitly authorizes grouping steps that do not require intermediate interpretation and takes responsibility for requesting job extensions. This supersedes per-command chat pauses and repeated remaining-time questions. The supplemental [driver](../../scripts/e001_ucloud_preflight.sh) groups verified micromamba bootstrap, GNU time installation and unchanged mapping/AMBER setup/smoke, with fail-fast stages and return packaging. Its micromamba pin/checksum comes from the official release API as documented in [operations](OPERATIONS.md#current-grouped-execution). It does not acquire GI data or run scientific training.

Local validation: **60 portable tests passed**, including a mocked failed download that packages logs, never reaches system/tool installation and refuses a second attempt over the same outputs. Shell syntax passed. This tests orchestration failure handling, not actual Linux installs or native parity. The actual driver and all native stages remain owner-run and unexecuted at this handoff. The old execution snapshot remains unchanged; the separate driver's hash and exact executed copy are recorded by the driver itself.

## First native return reviewed, 2026-09-18

Owner-supplied [terminal output](../../agent_context/e001_ucloud_preflight_output.txt), [return archive](../../agent_context/preflight-return.tar.gz) and [checksum](../../agent_context/preflight-return.tar.gz.sha256) are preserved as a compact synthetic-check record (approximately 97 KiB archive; no research data). SHA-256 `45b5887fdbc80a43eb25a55a960000c5da57399d6cff33c0f47e323d793ad820` verified. All 108 archive members were inspected for path/type/duplicate safety without extraction. The returned driver matches our local driver hash, and returned setup/smoke hashes identify the transferred scripts.

All setup, pip-check, pipeline and smoke exit codes are zero. micromamba 2.9.0 and Ubuntu GNU time package `1.9-0.2build1` installed successfully; GNU time's display string `UNKNOWN` is not an installation failure. Native mapping reports strobealign 0.17.0 and samtools 1.24. AMBER reports the intended `f8b3a601043d13fc4227d5691c13561eb4490e50` source commit. Package-script security warnings are advisory; no reported solver/import/command failure occurred.

- Mapping: 1,870 records; correct-reference fraction 1.0 on the tiny unique-reference fixture. Both thinning checks preserve mates: 107/935 and 111/1,045 retained templates. Random 10% sampling need not retain exactly 10% in small fixtures. No inference about metagenomic mapping accuracy or throughput follows.
- AMBER: perfect, merged, split, missing, unassigned, strict threshold boundary and multi-origin assertions pass. The conservative E001 R95 agrees with AMBER-derived purity-filtered recovery on unique-origin cases. Unconstrained AMBER recall intentionally differs for merged bins (1.0 versus R95 0.0), and multi-origin behavior intentionally differs (1.0 versus 0.5). Neither difference is an evaluator bug.
- Driver timestamps: 14:25:02-14:26:02 UTC, 60 seconds total. Mapping smoke: 0.40 seconds, maximum RSS 53,528 KiB; AMBER: 1.58 seconds, 164,744 KiB. Setup: mapping 17 seconds, AMBER 37 seconds. The batch interval corresponds to approximately 0.067 allocated core-hours at 4 vCPU, not total job cost; idle/earlier allocation remains additional.

**Reproducibility caveat:** both pip inventories expose `easybuild`, `easybuild-easyblocks`, `easybuild-easyconfigs` and `easybuild-framework` 5.3.1, absent from our install recipes and conda inventories. External Python paths or user-site exposure are a hypothesis, not a confirmed cause. Core fixture assertions passed, but do not call these fully isolated/reconstructable environments yet. The micromamba `list --explicit` outputs also lack an `@EXPLICIT` header/checksums and include blank entries; pip freeze contains conda build-time `file://` paths. Preserve them as observed inventories, not directly replayable locks.

Next: [environment review](../../scripts/e001_environment_review.py), no downloads or reinstallations. It records package/import origins with inherited paths, removes PYTHONPATH/PYTHONHOME/PYTHONUSERBASE and disables user-site for child processes, asserts distribution/import containment, records structured conda package provenance, and reruns both native checks into a new directory. Existing installs and first outputs stay intact. Return the resulting archive for inspection before GI acquisition. Python's [environment documentation](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONNOUSERSITE) grounds the process-local isolation controls; these do not edit shell startup files.

Review-driver preparation: 63 portable tests passed, including external-distribution injection/detection, successful clean-process exclusion and failure-status recording. No native clean-environment rerun has yet occurred. Documentation links and whitespace checks pass for maintained edits; original owner terminal output is preserved verbatim.

## Native check status

### GI download succeeded; coordinate collision found

The alias-aware conversion retry [return](../../agent_context/conversion-alias-return.tar.gz) verifies against [checksum](../../agent_context/conversion-alias-return.tar.gz.sha256) (`39658135488174f911bcbac7a010270c4bb7904bcc63a86fa6172877fefa0c00`) but exits 1 after two seconds. No `input-preflight-v2` was created. Stderr reports `Invalid DNA: _from__to_-42_total_0` (the complete scan reports the literal Biopython ID `*from__to*-42_total_0`). The owner's complete local scan found exactly two such records, both length zero and SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; no other malformed records were found. They have no accession or valid coordinates and cannot match the corrected truth table.

Correction: `prepare_hmp` now records and excludes only the two exact empty orphan spellings observed in the scan/error evidence (`*from__to*-42_total_0` and `_from__to_-42_total_0`), writing `excluded-fasta.json` and `excluded_fasta_records` in `inventory.json`. A nonempty record with either ID still fails. All other malformed headers, invalid DNA, duplicate IDs and join failures remain strict errors. This is explicit handling of a source-file artifact, not arbitrary filtering or a biological result.

The correction is covered by portable tests for both exact empty-orphan spellings, nonempty orphan rejection, alias preservation, conflicting metadata and preservation of repeated failed conversions. With `TMPDIR=/var/tmp`, all **73 portable tests pass**; the first local test invocation failed before test execution because the default macOS temporary directory was unusable. Documentation and shell checks pass. The next bundle contains this correction and the guarded conversion-only retry script.

The first guarded retry was stopped because `input-preflight-v2/` already existed. This was a partial output directory left by the failed parser, not a completed inventory; the return packager intentionally omitted it. The next retry moved it with the prior stage/return under a numbered `failed-conversion-malformed-fasta*` directory, but still failed because the runtime identifier spelling was not in the exception set. Recovery now selects the next unused numbered preservation directory and the parser accepts only the two exact observed empty spellings before creating fresh output. Completed or ambiguous directories remain fatal.

The following retry, from source commit `c8ec39581bfa12d903f89111f274379494738c38`, passed those orphan/recovery checks and reached the next strict input contract. It stopped on `Missing/duplicate coordinate join: CP002609.1_from_3_to_1894400_total_1894398` after four seconds. That message conflates a missing mapping key with a duplicate FASTA coordinate, so it is not yet evidence for either interpretation. The new [read-only HMP join audit](../../scripts/e001_hmp_audit.sh) reports both categories across the complete files before another conversion attempt. The owner's return archive and terminal output are preserved as the latest failure evidence.

The owner-run audit from source commit `6901be8153c2e25f075716b6c72712025a6b096a` completed in ten seconds and returned `join_contract_passes: false`. It inspected 210,634 FASTA records, including the two known empty orphan records. There are 210,632 non-orphan coordinate keys in the FASTA and 210,612 unique keys in the corrected mapping: 20 FASTA keys are absent from the mapping, while no mapping keys are absent from the FASTA. FASTA duplicate-coordinate, duplicate-ID, malformed-header, invalid-DNA and length-mismatch counts are all zero. The mapping contains six duplicate coordinate groups, all with identical non-ID metadata and therefore consistent with the six documented anonymous-ID aliases. Source SHA-256 values are `67aeeeb70e5ba0e1506bf95c79bb25b06869c0486e6c0ea111763c3b060c0baf` (FASTA) and `4353f05be6a94c0c05be083088148eac01bcf34dc05c6a061709ff5fbd61d720` (corrected mapping). This is a data-contract checkpoint, not a scientific result. The 20 FASTA-only records must be compared with the original mapping and setup metadata before conversion is changed.

Owner's targeted FASTA scan subsequently confirmed exactly one sequence for each truth alias pair, with matching declared/actual lengths. Pairs and lengths: PC21351/PC21352 (2,466 bp), PC24985/PC24986 (1,259), PC52686/PC52687 (1,360), PC97787/PC97788 (136,176), PC100714/PC100715 (4,140,334), PC210631/PC210632 (202,292). The three longer sequences total 4,478,802 bp and must not be dropped or counted twice. The three shorter sequences remain below the unchanged 2,500-bp input cutoff.

Correction: coordinates still define the FASTA join. Distinct source IDs at one coordinate are aliases only if every other truth field agrees exactly, including genome, taxonomy and number_reads. Choose the numerically smallest PC ID (stable lexical tie-break), retain all source IDs in `contigs.jsonl` and `inventory.json`, and count the physical sequence once. Duplicate same-ID/same-genome rows, conflicting aliases and multiple FASTA occurrences still fail; same-ID multi-origin truth remains ambiguous, not merged into a unique origin. Source files are never modified. Regression tests cover row-order independence, numeric ID selection, count preservation, below-cutoff reporting, conflicting fields and preserved multi-origin behavior. Corrected real-data conversion remains pending; retry only conversion into new output using a new committed code bundle.

The new owner [terminal output](../../agent_context/e001_gi_inventory_terminal_output.txt) and checksum-verified return replace the earlier same-named local return; the earlier failure remains preserved in Git and UCloud's `failed-inventory-missing-time/`. Recovery installed GNU time, prerequisites passed, and all six manifest-listed files downloaded: GSA 972,133,785 bytes; corrected mapping 12,597,447; original mapping 25,194,106; setup archive 1,906,532,721; README 741; checksum manifest 709,793. The setup member list includes `metadata.tsv`, `genome_to_id.tsv`, per-sample taxonomic profiles and `config.ini`; no extraction is authorized yet.

Conversion failed with `Duplicate truth row` while reading mapping rows, before output-directory creation. Independent read-only inspection of the publisher's corrected mapping (MD5 verified as `954106872f9af342c0b7fd4422d8db9f`) finds 210,618 rows and six duplicated (contig_id,start_position,end_position,genome_id) groups; all six contain differing rows, including differing anonymous IDs. Example: PC21351 and PC21352 both describe HG917869.1:696659-699124 in OTU_97.20215.0. This violates our assumed one-coordinate/one-anonymous-ID join, rather than showing corrupt downloads. Do not drop truth rows blindly. A targeted scan of the already downloaded FASTA is required to count corresponding records and compare sequence hashes before choosing a correction. No biological result or scientific approval follows.

### GI inventory attempt failed before acquisition

Owner return verified: [archive](../../agent_context/gi-inventory-return.tar.gz), [checksum](../../agent_context/gi-inventory-return.tar.gz.sha256), SHA-256 `05287ad75941a1120034c78c9834b264fb4e158cf8d8136b7bf6946ffc8af80e`. Safe archive members and the executed driver match the prepared inventory wrapper. At 2026-09-18 19:37:08 UTC the prerequisites command failed with exit 127 because `/usr/bin/time` was absent. The timing wrapper could not launch Python; acquisition and conversion never ran. This is an infrastructure failure, not a dataset or scientific result. A container restart/replacement would explain loss of the system package, but that event is not confirmed by the return.

Root cause in our wrapper: it assumed the earlier container's system utility persisted, although only experiment files/environments under `/work` are intended to persist. The corrected inventory wrapper checks/install GNU time before timed commands and records package/version/hash and bootstrap logs. Its explicit `--retry-missing-time` mode checks the known failure signature and absence of inventory/conversion data, verifies the old return checksum, and moves the failed stage and return files intact into `failed-inventory-missing-time/`. It refuses existing recovery destinations or partial data; no automatic deletion/retry loop. Only then does the normal grouped inventory resume. The already executed source snapshot and installed tool environments are unchanged.

Local verification: 65 portable tests pass, including failed-attempt preservation and refusal to recover over existing inventory data. Shell syntax and documentation checks pass. Actual recovery and GI acquisition remain owner-run and unexecuted at this handoff.

### Environment review resolved, 2026-09-18

The owner-returned [review archive](../../agent_context/environment-review-return.tar.gz) verifies against its [checksum](../../agent_context/environment-review-return.tar.gz.sha256): `b00b14cc6665b6ff7a6c12fb8a0a284596ff75bebc5a4f923864fec64e7a6819`. All 71 members passed path/type/duplicate checks; the executed review script matches the locally prepared source. All ten recorded commands, pip checks, both native smoke reports and final status pass.

Confirmed cause: the four EasyBuild distributions came from `/home/ucloud/.local/lib/python3.12/site-packages` with `site.ENABLE_USER_SITE=true`; PYTHONPATH and PYTHONHOME were unset even in the observed processes. With clean-process controls, user-site is disabled, all discovered distributions are inside the intended environment prefix, and NumPy/Biopython/pysam (plus pandas for AMBER) resolve inside that prefix. Required module origins were already correct in the first run. No installation changes were needed.

The isolated mapping report preserves 1,870 records, correct-reference fraction 1.0, and exactly the same retained-template counts/pair-consistency results. AMBER's checks match the first return. The mapping BAM byte hash differs between output locations; no byte-identical-output claim is made. Command timings for the clean smoke reruns were approximately 0.52 and 1.67 seconds, not research-scale benchmarks.

Structured conda metadata now contains 52 mapping and 27 AMBER package records, all with URLs and at least one package checksum. This repairs provenance missing from the first text exports, but does not establish tested environment reconstruction or hashed pip wheel locks. Those remain runtime-freeze work before science, not blockers for bounded GI inventory.

**Disposition:** the isolation concern is resolved for these checked imports/distributions. Proceed to GI assembly/truth/setup acquisition and initial coordinate inventory, with process-local Python isolation retained. Other binner smoke, taxonomy resolution, CPU feasibility and scientific launch remain gated. The new inventory driver wraps the unchanged transferred snapshot and returns summaries only; no GI acquisition has run yet.

Local preparation checks: 64 portable tests passed, including refusal to overwrite an existing inventory before starting work; shell syntax and documentation checks passed. Maintained setup/smoke scripts now apply the observed isolation fix for future transfers. Existing UCloud code stays untouched, and the new inventory wrapper supplies the same controls around the old snapshot. The inventory download/conversion itself remains unexecuted here.

| Native check | Current status and what it must establish |
| --- | --- |
| strobealign 0.17.0 / samtools 1.24 | Synthetic native checks and isolation rerun passed. Real-read mapping remains untested. |
| Pinned AMBER | Native fixtures and isolation rerun passed, including intended unique/multi-origin and threshold semantics. No scientific dataset evaluated. |
| Pinned VAMB | Unexecuted. Actual BAM/TNF extraction, native scale invariance including total abundance, zero-row/zero-column behavior and CPU forward pass under its specified dependencies. |
| Pinned COMEBin | Unexecuted. Fixed augmentation identity, full native six-view coverage recomputation, measured variance, pseudocount-aware scaling and CPU forward pass. |
| Pinned MetaBAT2 | Unexecuted. Source-built executable, native mean/variance extraction and assignment format, including genuine empty output versus command failure. |
| Linux environment recipes | Mapping/AMBER installed and process isolation verified; structured provenance captured. Reconstructable locks and other tool recipes remain pending. |

Full native training/clustering, marker payload verification, CPU throughput projection, real-read prefix mapping comparison, full data/truth/taxonomy joins and research launch remain later gates. The smoke job is deliberately not a surrogate benchmark. A failure is retained and investigated; no older PyTorch/tool substitution is allowed under the original pin.


## Native features accepted and pilot prepared, 2026-09-25

The local auditor [e001_review_features.py](../../scripts/e001_review_features.py)
verified `multisample-features-69_32jz9-return.tar.gz` against its sidecar SHA256
`6a8ebd182fa75fe2d6566f6182083387f5bdbf6a34272ebbe7bcfa7004711e1c`
and `e001-features.3qiYVJ.log`. The [observed record](features-observed.json) preserves
source `86642eeaa28c`, receipt hashes, benchmarks and complete native QC.
Workflow exit status is zero. VAMB/MetaBAT results were reused provenance-bound;
COMEBin and aggregation completed. Previous failed attempts remain valid negative
operational evidence, but their retry handoffs are superseded.

All 22,594 contigs (817,438,232 bp) and ordered ten-sample axes agree. C0/CT
VAMB composition and input masks are identical; COMEBin contig lengths, k-mers and
augmentation intervals match across C0/CT/CS. Fixed interval SHA256 is
`8dd26d50a24f9a5e0ecfa3c8febea4dda112a3ae2ecef099f6bcb2e3647c9922`.
Coverage tensors have shape 10 samples x 6 views x 22,594 contigs. COMEBin zero
means increase from 739,613 to 895,405 sample/view/contig entries; every sample/view
is nondecreasing. These are repeated view entries, not distinct contig counts.
Native normalized CS differences are below 1e-5 (COMEBin maximum
2.3916561531223124e-6); the pseudocount effect is numerically small and retained,
not claimed bit-identical. Returned MetaBAT CS tables independently satisfy means
x0.1 / variances x0.01; its absolute thresholds need not be scale-invariant.
Bulk arrays were not returned: local acceptance combines native validation and
hash receipts; the pilot rehashes them on UCloud before fitting.

Actual allocation 4 vCPU / 12 GB, worker budget 3 threads / 10 GB, one tool at a
time. Elapsed 3,612.171 seconds = 4.013523 allocated core-hours. Logical retained
feature attempt is 608,309,522 bytes excluding external BAMs. Known four feature
attempts sum to 5.104432 core-hours; accepted preprocessing drivers sum to
23.055091. Neither subtotal includes all historical setup/failure/idle billing.
No repeat extraction is justified. Feature/resource evidence supports a bounded
first pilot, not a guarantee of full-scale training affordability.

The new [pilot driver](../../scripts/e001_pilot.py) and
[Snakemake DAG](../../workflows/e001-preprocess/pilot.smk) use the accepted feature
locator, native seed-11 schedules, separate tool prefixes and serial conditions.
The [plan](paired-pilot-plan.json) splits allocations to preserve measured cost
assumptions. Models, full native partitions, COMEBin candidate grid/marker selection,
AMBER filter=0 tables and frozen-population R95 are retained. No pilot was executed
here; first-group returned-output review precedes COMEBin and additional seeds.

Validation distinguishes real pinned CLI-parser execution, real subprocess timeout/
child cleanup and memory stops, input corruption rejection, real Snakemake DAG
execution/resume, and synthetic-worker whole-driver tests. These portable tests
cannot validate Torch/Linux training; the local Mac Python has no compatible Torch
runtime. Previous accepted native preflights/integration are reused without
repeating them. Native VAMB's Python entry point is called explicitly; its import
resets thread environment variables, which the wrapper restores before execution.
No scientific schedule or tool source was changed.

Final local results: 193 repository tests passed before adding the complete-driver test; all 9 focused pilot tests subsequently passed, including that additional test. Documentation/link and shell syntax checks are recorded with the execution commit.
