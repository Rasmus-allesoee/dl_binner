# E006: Installed generic command usability

Prepared/completed 2026-10-06. Status: **accepted software milestone**;
scientific utility is not assessed here. [Protocol](protocol.json) froze contracts
before measurement; [observed receipt](observed.json) owns hashes, resources,
failures and review limits. D011's model and scope are unchanged.

## Implementation and native acceptance

[Integration](integrate.py), [continuation](finish_checks.py) and
[retained review](review.py) own the checks. Native scientific workers are not
replaced. Source/contracts first committed at **e93132b**. The final accepted
wheel **0.1.0.dev1**, **36,310 bytes**, SHA256
`f093261d726d4b6f42e7401c211e99cf4fdadffbc950112161262bd7fdb804d0`, is under
`artifacts/e006-cli-usability/setup/dist-v7/`. Code/defaults/DAG match source
**e30023c0a9e78c255da3b7abc43ed3025571dcef**. Scientific `io.py`, `model.py` and
`clustering.py` have no diff from E005 acceptance; training JSON is byte-identical
to E004. This prototype makes no compatibility promise.

The installed `dl-binner run` packages defaults and a serial Snakemake DAG, uses
its own binner Python and a separate existing Snakemake 9.16.3 Python, and installs
nothing. Eight native stages produce both arms, checkpoint parity, complete DNA
exports and byte-bound label-free summaries. Source/input/config/runtime/budget
and completed outputs must match before explicit resume. Successful stages publish
from unique staging folders; failed evidence remains. Missing/extra/corrupt outputs
and unreceipted final artifacts are refused, never silently repaired. Native timing
confirms serial stages; local scheduler options use cores/global RAM without jobs.

Native Mac: Python 3.10.15, NumPy 1.26.4, Torch 2.2.2 (CUDA absent), NetworkX
3.4.2, threadpoolctl 3.5.0. Final package prefix:
`artifacts/e006-cli-usability/env-local-v7/`; workflow prefix remains unchanged.
Disk exhaustion stopped v5 setup/build. v6/v7 are fresh lexical package venvs with
explicit numerical/build dependencies linked read-only from intact E006 v4,
excluding its old `dl_binner`. No system-site/PYTHONPATH overlay is used. Origins,
inventory/pip checks and before/after byte-tree hashes pass. Volatile `.DS_Store`
is excluded from dependency binding; no scientific input/library bytes are
excluded. Python children use `-I -B`. This **local reuse is not a portable Linux
prefix**: do not transfer the links or remove v4 while v7 depends on it. No
E004/E005 prefix, cache or scientific attempt was upgraded, relocated or deleted.

Baseline: **13 contigs / 42,311 bp**, new software windows of retained GI DNA
across all six strata plus one N-only mask case. Depth is explicitly synthetic,
with zeros and reversed rows. Final: **four contigs / 2,048 bp**, including two
eligible rows and two exclusions, with spaces in input/output paths. Both final
arms validly produce **zero bins / two noise / two excluded**; empty partitions
are a software contract, not a negative biological result.

Fresh extraction, twenty-epoch seed-11 training, exact reload, fixed clustering,
raw/learned exports and all-stratum masks/reasons pass. Thirteen-contig sequence/
depth paths, partial/full resume and changed input/sample/config/source, corrupt/
missing/extra-output checks are retained/reused. Final-wheel resume preserves
completed bytes/mtimes; native completed DAG dry-run says **Nothing to be done**.
Independent ready four-thread rules and one-thread/8-GB rules serialize under the
production CPU/global-RAM helper. Binner stage timings never overlap.

**Nine focused tests pass**, plus fourteen final native named contracts and
sixteen retained passed contracts. Only an unavailable-ps prerequisite regression
is mocked; scientific workers run, and monitor/scheduler fixtures use real tiny
processes. Bad FASTA/insufficient evidence stop dependencies in **3.60 / 6.15 s**.
The overall 0.3-second timeout retains its intended wall limit with bounded
cleanup and **no cleanup failure**. Actual RSS enforcement and fatal-orphan
termination pass. Native causes/log paths, detailed traces, ten-second heartbeats
and exit codes are captured inside parent/child logs.

Retained E005 accounting agrees: raw/learned **113/51 bins**, **798/3,891 assigned**,
**3,414/321 noise**, **1,097 exclusions**, assigned bp **4,837,013/11,831,674**,
and **1,353 all-zero-depth rows**. All six strata remain. Only retained outputs
were read; no E005 extraction/inference/clustering/evaluation was repeated.
Generic summaries contain no R95, genome counts or MAG-quality estimates.

## Costs, failures and next step

Final suite: **59.72182 s**, **347,578,368-byte sampled peak**, **38.09 sampled
CPU-seconds / 0.638 average CPUs**, within four-thread/8-GB/two-hour caps. Final
partial/full invocations: **10.833 + 15.244 s**; learning **0.17507 s / 1.77 CPUs**.
Startup/serial work dominates tiny fixtures; no saturation/bulk-scaling claim.

Known supervised QA attempts **including failures**: **335.21193 s / 0.3724577
four-thread wall hours**, peak at most 367,599,616 bytes. This is local planning,
not provider billing or task-total cost. Initial pre-monitor failure, setup/build,
review/debugging/idle time are excluded. Logical storage counts are in the receipt;
the four earlier full prefixes are about 775 MiB each, and final v7 owns a small
payload with retained v4 dependencies. An ignored cache is not a backup.

- `integration-001`: sandbox denied ps before science and the original exit
  receipt. Prerequisite failures now retain exit evidence; native checks use
  authorized process monitoring, never skip it.
- `integration-002`: sixteen checks and three full fixtures pass. Bad FASTA stops
  in 2.89 s but its cause is hidden by scheduler text. Reporting fixed; successful
  evidence reused.
- `integration-003/004`: science/recovery paths pass; strict timeout checks expose
  EPERM around stopped/unreaped probe cleanup and cause reporting. The exact
  kernel/security reason for the earlier EPERM is not established. Repair reaps leaders,
  independently distinguishes absent/zombie from live groups and retains all
  stop/cleanup reasons. Nonzero exit alone is insufficient acceptance.
- `integration-005`: final contracts and nine focused tests pass. All v1–v7 setup
  records and failed v5 prefix/logs remain; this record authorizes no deletion.

**Accept D011's usability milestone; no further architecture gate.**
[Usage](../../docs/PROTOTYPE.md#run-the-binner) owns commands/outputs/recovery.
Next prepare one tiny checksum-bound owner-run CPU/Linux generic-launcher smoke,
reusing healthy UCloud assets and a new version-qualified package prefix. Packet,
logs and returned archive/checksum belong under `/work/Home/dl_binner/e006/transfer/`.
Stop
for returned review; do not execute UCloud or repeat E005. Larger data, seeds,
the three-way study and publication remain separate owner decisions.

## Generic-command Linux smoke preparation, 2026-10-06

The owner requested the next finite compatibility check.
[Linux smoke contract](linux-smoke.json) freezes **4 vCPUs / 12 GB allocated**,
four numerical threads, interop one, loader zero, **8 GB working RSS**,
**1,800 seconds total execution including entry verification/setup**, a
900-second setup subset and 900-second native-contract subset. Collection has a
separate 120-second ceiling and is included in allocation-wall accounting.

Reuse the accepted 13-contig / 42,311-bp E006 software panel (twelve real GI DNA
windows, one explicitly synthetic N-only sentinel; synthetic two-sample depth),
not a new biological dataset. The accepted 36,310-byte wheel is unchanged. The
[runtime baseline](runtime-baseline.json) extracts full clean-prefix inventories
and exact lexical interpreter paths from E005's accepted Linux receipt.

[Owner driver](../../scripts/e006_owner.py), [runtime probe](../../scripts/e006_runtime.py),
[actual native contracts](../../scripts/e006_smoke.py) and
[packet builder](../../scripts/e006_bundle.py) own execution and transfer.
A fresh version-qualified venv owns the installed wheel. Its interpreter/stdlib
and explicitly linked numerical dependencies remain in the accepted E005 prefix;
that prefix must persist. No old dl_binner, system-site overlay or .pth path
injection is used. Reused site trees are hashed before/after; complete inventories
and import origins are checked before work. Separate accepted Snakemake 9.16.3
is reused read-only. There are no downloads, solvers, environment upgrades,
runtime relocation, reference data changes or E005 scientific stages.

Four small deployment tests pass. At source freeze `05069f1`, the full fresh/repeated owner harness and its native readers/writers were pending; the completed local results are below. Local Mac testing
will not establish Linux compatibility; the owner-return review is the boundary.
No UCloud execution, data expansion, extra seeds, three-way study, architecture
gate or publication is authorized. Uploads/logs/returns will remain under
`/work/Home/dl_binner/e006/transfer/`; unique attempts and new prefixes stay
under the E006 root. Failed attempts and verified manifests are retained.

## Owner transfer locally accepted; Linux review pending

[Preparation receipt](linux-prepared.json) owns the exact source/input/wheel/packet
bindings, three retained full harness runs, entry failures and actual local costs.
[Operations](OPERATIONS.md) owns the two upload filenames, paths, allocation,
purposes, ceilings, stopping conditions, exact command and required return files.

Source/contracts were committed at **05069f1** before measurement; final packet
scripts bind **a8010cb**. The packet is **72,267 bytes**, SHA256
`d15864bd606676991b95c3fe2bb2d4198394106e22aead022fee9b64edc08569`, retained in
`artifacts/e006-cli-usability/transfer/v1/`. The accepted wheel and scientific
code/defaults are unchanged. All twelve packet members, source/config bindings,
returned file inventories and archive checksums were independently recounted.

The real owner driver creates a fresh lexical version-qualified package venv,
links only reviewed dependencies and installs the wheel offline. Full inventories,
actual origins, wheel code/default/DAG bytes and before/after reused site-tree
hashes pass. The complete command/driver runs from a separate entry cwd, without
adding project source to imports. Two invocations in the same persistent root
produce distinct preserved attempts/prefixes. Raw and learned actual readers/
training/inference/clustering/writers run, not mocks. Both complete exports,
13 ordered IDs / 42,311 bp, all six strata, exclusions, original zeros and exact
reload pass. Same-panel four-contig / 2,048-bp subsets retain valid empty partitions.
Native 20-epoch seed-11 schedule, four threads/interop one/loader zero and pools
are confirmed. Partial resume preserves features/train bytes and mtimes and
does not schedule those workers; completed resume schedules no science. Actual
CPU/global-RAM ready-rule placements and all native-stage intervals serialize.

**Twenty-one final native named checks pass**, plus four focused deployment tests.
Changed FASTA/sample axes and corrupt checkpoint/export are rejected; malformed
IUPAC, missing depth IDs and insufficient training evidence stop their dependencies
with the intended error. Whole-command timeout, actual RSS enforcement, a fatal
worker's orphan cleanup and ten-second heartbeat logging pass with intended
receipts and no cleanup error. Entry fixtures deliberately fail allocation,
full inventory, absent interpreter and packet bytes: each returns an archive,
checksum, status and submitted manifest, before installation/science. These are
real prerequisite/input failures; no scientific adapter is replaced.

The full checksum-pinned Bash envelope also passes extraction/logging/driver/return
checks. Native Mac revealed that suffix-after-X `mktemp` did not randomize the log
name. Its final template ends in X, with ps explicitly checked at entry. Two
actual bad-checksum invocations verify distinct logs, the intended cause and exit
2 before any driver/science. The final outer watchdog also encloses checksum
verification/extraction/startup; an actual extracted-packet inventory failure
confirms its forwarded arguments, captured error and verified-manifest return.
Prior successful native outputs are reused; the source-frozen driver/wheel are
unchanged by these shell-only corrections.

Final full envelope **186.669 seconds through collection**, sampled stage-tree
peak **360,407,040 bytes (0.360 GB)**. The final direct driver is 179.638 seconds;
initial narrower harness 151.278 seconds. Known full local harnesses total
**517.585 seconds / 0.575095 four-thread wall hours**, including setup/hash/collection.
These are local planning estimates, not UCloud charges or all-task cost. Negative
entries, tiny shell failures, setup scripting/checks/review and owner idle are
separate. Owned regular files in each new package prefix and retained/returned
logical bytes are recorded; shared dependency storage is not duplicated or counted
as new owned payload. No old prefix, attempt or cache is upgraded/deleted.

**Prepared, not native-Linux accepted.** Mac tests use explicit local runtime
baselines (Python 3.10.15 / workflow 3.13.12) and ps sampling. Linux Python 3.12.10,
CPU `+cpu` build, /proc sampler, cpuset limits, venv/site behavior and reset-container
prerequisites remain actual owner checks. The linked Mac prefix is never shipped;
the new Linux venv depends on its retained accepted Linux base.

Next the owner runs exactly one [prepared Terminal command](OPERATIONS.md) and
returns the printed archive, checksum and terminal log. Unexpected errors stop
without automatic retry. Review before another product action. No quality score,
whole-MAG/generalization claim, E005 rerun, extra data/seed, three-way comparison,
architecture gate or publication follows from these software checks.
