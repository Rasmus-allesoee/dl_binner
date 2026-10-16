# D014: Google Cloud as the connected Linux research workspace

Date: 2026-10-13; preparation/data/review amendments: 2026-10-14–15. Status: **accepted; infrastructure, separate truth v2 and unchanged controls reviewed; original data-DAG failure preserved**.

## Problem and decision

The owner no longer has a functioning SDU login. UCloud data are reported intact
but inaccessible; its remaining core-hour/storage allowance is not available to
this project. Repeated owner-transfer debugging also hid the actual Linux runtime
from agents. Select GCP as the main cloud provider and a private GitHub-synced,
SSH-connected persistent CPU Linux workspace that Codex can operate within each
explicitly authorized phase. Keep macOS for cheap local work.

[Cloud operations](../CLOUD.md) owns the concrete staged setup/cost/retention guide.
Phase 1 excludes E009 v14 return review, acquisition, all binner installs/fits and
scores. Paid billing and expected USD300/2027-01-12 credit expiry are owner reports,
distinct from the later owner-read kr1,973 remaining/kr0 used display. API billing
status/currency, quota and resources were independently checked before provisioning;
this session could not read the browser display because of a stale plugin loader.
Use only verified trial-credit-covered
products; stop and ask about ambiguous/uncovered/beyond-credit costs.

Owner-approved initial layout: Iowa e2-standard-4 /16 GiB with small separate boot/balanced working disks,
private same-region Standard bucket, IAP-only SSH and an outbound ephemeral IP.
Increase CPU/storage only after the next workload/sample-count decision. No GPU,
public app-server, broad default service account, new orchestration framework,
whole-environment snapshot or automatic paid-cloud spending is implied.

## Alternatives and reasons

- Continue UCloud: currently impossible; preserve evidence/locators without deletion.
- Browser-only Cloud Shell: its small home disk/ephemeral compute is unsuitable as
  the persistent scientific workspace; CLI/browser login can still aid setup.
- Large VM/GPU/terabyte disk now: not justified by setup or the unsettled E009
  then-unsettled 10/20-sample scope; provision based on the next actual peak/work budget.
- No external IP plus NAT: secure but adds a paid gateway and complexity just for
  package/public-read downloads. IAP-restricted inbound plus ephemeral outbound IP
  is simpler; no public SSH firewall is created.
- EU region: lower interactive latency, but higher prices/no small US storage
  allowance. Public simulated DNA currently has no EU residency constraint; revisit
  if latency materially harms usability or future data terms require it.
- Colab/Kaggle: possible future options after credit exhaustion, not configured now.

## Evidence, retention and consequences

Official credit rules, CPU/disk/IP/storage/IAP prices, runtime-limit and SSH docs
were consulted 2026-10-13 and linked in CLOUD. Actual account/VM/app evidence must
be recorded separately. Source history is preserved by normal commit/push of
`benchmark-planning`; no force push, main merge or visibility/publication change.
UCloud instructions are [archived](../history/UCLOUD_OPERATIONS.md); original
experiment records/receipts remain canonical and cannot become GCP run receipts.

Retain irreplaceable inputs and accepted final evidence; checksum/readback compact
private backups. Capture useful failure evidence, then prune obsolete regenerable
bulk after recording what is removed. Whole failed outputs and disk/environment
snapshots are not default backups. Credentials never enter Git or archives.
Stopping a VM stops compute/IP charges but leaves provisioned storage costs.
Expiry/credit exhaustion is an explicit financial review, not a reason to silently
charge the card or automatically delete important data.

## Revisit and next action

Billing/approved layout, strict SSH, exact pushed source-freeze clone, complete
pinned Linux Codex PATH/help and private archive readback pass. ChatGPT
authentication and the actual desktop remote-project Linux command test pass.
Owner-returned output agrees with independently inspected native session metadata
and the four allowlisted command outputs at clean commit
`bde9fbf49c035286cae713799d48d7d55a3d87a5`. An initial AppArmor/Bubblewrap failure is
retained; the official Ubuntu prerequisite repaired the normal CLI sandbox while
leaving global kernel protections enabled. CLOUD/receipt distinguish desktop
retry proof from the subsequent native CLI check. Final records are normally
pushed/synced; unused compute is stopped, preserving both disks and login state.

The 2026-10-14 preparation independently accepts v14 without replay and chooses
ten first-listed subject samples 0,2,3,4,6,9,10,11,14,17 for one sample-0 assembly.
[E009 operations](../../experiments/E009-competitive-benchmark/OPERATIONS.md) owns
the locally tested data stage and proposed 8 CPU/32 GiB, 300-GiB work disk,
24-hour driver/25-hour provider STOP, $20 run plus seven-day storage envelope.
Current quotas (12 total CPU, 24 E2 regional, 250-GiB balanced/SSD) permit the CPU change but require disk quota >=300 GiB; no
VM/start/provisioning/service mutation or bulk data/scientific work ran now.
Displayed credit scope/balance/pending usage and owner resource/retention approval
remain mandatory before execution. Existing read-only GitHub access suffices;
CLOUD records a separate expiring Contents-write credential as the later direct-
push preference, with permanent write deploy key/App alternatives. No permission
changed. Old UCloud command/budget details now live only in history; durable
storage/startup lessons stay available without requiring GCP snapshots.
Revisit size/provider after measured workflow needs or credit constraints, not as
an architecture gate. No accepted science is repeated to migrate infrastructure.

Owner-approved storage/cost exposure on 2026-10-13 includes an expiry review by
2027-01-10; that original setup did not authorize science.

## Later data-phase authorization and resource admission, 2026-10-14

The later owner message authorizes the exact prepared `5fec4e1` data-only phase,
with one full sample-0 assembly/ten BAMs/depth/provisional truth. It explicitly
excludes binner fits, E009 scores and model changes, and asks that comparisons
serve improvement of our high-performing binner rather than a final ranking of
the weak prototype. [D013](D013-first-comparative-benchmark.md) defers CompleteBin
and selects later runs by incremental decision value, without a mandatory campaign.

Live supported Chrome/API admission in [CLOUD](../CLOUD.md#live-data-phase-credit-gate-2026-10-14)
now verifies paid billing, DKK1,972.04 available upgraded Free Trial credit through
2027-01-12, current DKK SKUs, ordinary resource eligibility and explicit billing
lag. Only this project is linked; existing CPU usage was zero. The requested
SSD-backed disk quota **250→300 GiB** is effective in the API, case
`a11cf91a-b76b-4c95-9f79-7dc7538f3611`. No extra service/CPU quota was needed.

Reuse the same Iowa VM at **8 CPU/32 GiB**, work disk **300 GiB** and existing ext4
expanded without formatting; set **25-hour STOP before start**. The original
**24-hour cumulative setup/QA/data clock**, **25-GiB reserve** and **$20 gross
run/seven-day envelope** remain. The 300-GiB estimate contains no CompleteBin
files: full read/archive/BAM/source data and serial scratch plus reserve justify
it; 250 would save only ~$1.15 in seven days. Ongoing stopped boot/work is
$31.20/month gross (~DKK205.24 at the fresh quote); review by **2026-10-21**.
No automatic growth, retry, extension, filtering, unsafe shrinking or card billing.

The prepared Mac branch was normally pushed and the VM clone stays clean at exact
5fec4e1 with its read-only key. A complete independent pinned data runtime and
the actual tiny changed-driver/DAG Linux contracts passed; setup/QA time counts
in the cumulative allowance. No accepted five-binner/scientific stage was replayed.
[The actual phase receipt](../../experiments/E009-competitive-benchmark/gcp-data-observed.json)
owns final execution/status/cost/storage; this decision does not infer completion
or admitted truth from a launch. Stop compute after collection and preserve compact
checksum/readback evidence. Full-fit admission remains a separate future choice.

## Verified partial data result and review access, 2026-10-15

E009's first live GCP data phase completed acquisition, full assembly, ten BAMs and
measured depths, then failed in the provisional-truth parser. The exit watchdog
stopped it correctly; GCP status and the failed driver receipt agree. The separately
authorized evidence review assessed credit coverage and the remaining $20 budget,
reused the same VM/disks under a one-hour provider STOP and stopped again after
**0.4767225 h**, without any provisioning, resize, data/alignment replay or fit.

[CLOUD](../CLOUD.md#verified-data-exit-and-bounded-review-2026-10-15) owns exact
start/stop/balance/price evidence. Both intervals total **13.656446 provider hours**,
about **$3.7288 gross compute/IP**; seven-day disk planning exposure is **$7.1803**.
This remains inside $20 with compact private archive/transfer reserve. A delayed
invoice is not replaced with allocated core-hours or a credit-display subtraction.
The private archive/readback and independent Mac member verification pass.
Current VM is **TERMINATED**, IP released, disks **30/300 GiB**, one-hour STOP policy.
The original data-phase 25-hour setting is historical, not current authorization.

The measured 170.66-GiB filesystem peak makes smaller future working storage
plausible. Retain this disk through the approved October-21 review; do not shrink,
copy, expand quota or delete accepted data automatically. Provider selection does
not authorize a new fit budget: D013 now prioritizes truth repair/admission and
unchanged diagnostic preparation, with no immediate external tool. CompleteBin
stays deferred and read-only GitHub access remains adequate.

The next owner-authorized truth repair was completed locally from the private
retained archive; [truth v2](../../experiments/E009-competitive-benchmark/truth-v2-admission.json)
is independently admitted. The VM was **not woken**, no resources/services changed
and new VM compute spend is **$0**. Current control-plane evidence still shows
TERMINATED, no external IP, 30/300-GiB retained disks and one-hour STOP policy.
Do not apply the proposed 4.25-hour control STOP until a separate $2 fit approval
and fresh live credit/cost gate. The new launcher is locally safety-tested, without
claiming Linux setup or full-scale fit feasibility. D013 keeps external fits deferred.

The owner's subsequent new $2 control phase is now running on the same VM/disks
at clean cf7bf2a after fresh credit, actual headroom, source and native-runtime
gates. [The control receipt](../../experiments/E009-competitive-benchmark/controls-observed.json)
records the current boot/PID watchdog and4.25h STOP. No resize, provisioning, IAM,
new service or external binner is involved. Leave the healthy run supervised;
inspect completion/shutdown later without another VM wake or automatic retry.

## Control completion and stopped review, 2026-10-16

All four separately approved unchanged controls completed and passed independent
local review in [the result](../../experiments/E009-competitive-benchmark/controls-review.json).
GCP confirms TERMINATED at 22:55:19.426 UTC October 15 /00:55 October 16 Copenhagen.
No new VM wake or resource/service/IAM change followed. The4.25hSTOP policy remains
configured, not authorization for another run. Measured 1.7542275h costs~$0.479
compute/IP; conservative private evidence export~$0.0542, within$2. Refreshed
Welcome credit DKK1,936.57/expiry2027-01-12 and unchanged DKK SKUs admit the export;
reported net0 is lagged billing, not a reconciled phase invoice.

The compact scientific evidence is privately retained/readback-verified and all
archive/member bytes independently checked. Post-exit watcher snapshot is only
on stopped disk; stage/private completion evidence establishes success separately
from shutdown. No wake is justified merely to retrieve that redundant stop detail.
Existing30/300 GiB disks still cost$31.20/month; review byOctober 21, no retention
extension. The strongest next step is local preparation of D013's one grouping
mechanism, with full resource/credit admission and separate authorization before
any later execution. Read-only GitHub remains adequate; no credential change.
