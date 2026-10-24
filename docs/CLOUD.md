# Google Cloud workspace operations

Updated: 2026-10-24 (Copenhagen; initial provisioning receipts are October 13 UTC).

**October 24 E021 GPU admission: capacity blocked, stopped and rolled back.**
[Native observation](../experiments/E021-frozen-sequence-hybrid/native-observed.json)
records approved global GPU quota 0 -> 1 (Iowa T4 also 1), the only N1/T4 start
refused with ZONE_RESOURCE_POOL_EXHAUSTED, and independent TERMINATED E2 readback.
No successful boot/guest SSH/setup/science. Temporary N1/T4/173,700-second STOP
configuration was removed; original 300/30 GiB disks, Secure Boot/integrity/vTPM,
metadata, service accounts, network, enabled services and original scheduling
match. No alternative VM/zone/service/disk, cleanup or retention extension.

Operational order is stopped E2 -> N1 -> TERMINATE maintenance/provider STOP ->
GPU -> start. E2 refuses that maintenance setting. For rollback, remove GPU ->
restore original MIGRATE/scheduling while still N1 -> E2. The inspected SDK lacks
`gcloud compute operations wait`; read the submitted zonal operation with
`operations describe` rather than replaying a mutation. Preserve all failed
journals. Eight local tests pass; no native driver, CUDA, systemd or throughput
contract is claimed. See [operational lock](../experiments/E021-frozen-sequence-hybrid/gpu-launch-lock.json).

A failed restart can advance `lastStopTimestamp` while `lastStartTimestamp` still
names an older successful allocation. Do not subtract those fields to price a
new run. Bind allocation accounting to the actual start operation and successful
boot; preserve the failed operation and rollback evidence separately.

Latest Welcome balance **DKK 1,865.82 / 95%**, January 12, 2027 expiry; paid account,
Certain usage / net pricing, delayed usage unknown with $35 reserve. Ordinary
first-party GPU coverage was checked against retained-credit paid-upgrade terms;
this is not free-tier eligibility. Expected new compute/GPU **$0**, no export;
control-operation allowance separate, not an invoice/credit-delta attribution.
Existing stopped disks continue at **$31.20/month**, separate $8 full-interval
forecast ~$7.63 through **October 28, 00:00 Copenhagen (CET)**. No new cloud objects.

The same frozen candidate remains the next admission decision under the owner's
existing $45/48-hour scope. Maximum quote ~$39.23, not actual cost. No automatic
capacity retry/alternative or storage renewal. [Operations](../experiments/E021-frozen-sequence-hybrid/OPERATIONS.md)
owns the precise continuation, last full-window start and unresolved original
30 GiB boot versus provider 40 GiB guidance. Verify actual space/old-file inventory
and a compatible signed-driver route before installation; no silent resize or
Secure Boot bypass. The following is the **dated October 23 snapshot**.

**E021 implementation/admission is local; VM remains TERMINATED. No new job or
resource/retention change.** [Operations](../experiments/E021-frozen-sequence-hybrid/OPERATIONS.md)
and [resource plan](../experiments/E021-frozen-sequence-hybrid/resource-plan.json)
own the conditional-comparison decision: defer because complete native model runtime,
throughput/full RAM/20 GiB growth and local-review gates are unadmitted. Credits
are healthy: DKK 1,871.23 / 95%, January 12, 2027 expiry; paid account, Certain usage,
net pricing, >24-hour delayed usage possible/$35 reserve. No credit delta is an invoice.
Fresh Catalog reads include E2/N1/T4 SKUs; no GPU coverage inference from paid billing.
Global GPU quota is zero, regional T4 is one. No quota request, GPU/type/service/IAM
change, VM wake, SSH, private upload or new cloud compute ($0) occurred.

Next proposed scope is temporary existing-VM n1-standard-8 / 30 GiB + one T4 / 16 GiB,
original disks unformatted, new $45/48-hour clock/48.25-hour STOP, 32 GiB growth;
about $39.23 max allocation/disks/export/reserves at conservative current marginal
SKUs. It needs new explicit resource/quota approval and complete native CUDA,
credit coverage, availability, throughput/VRAM/RAM/return proof before release.
The current $25/72-hour CPU preparation is not a validated GPU launcher. Existing
300 GiB work +30 GiB boot disks still cost $31.20/month while stopped; current
104 object versions /9,384,180,741 bytes and separate approved $8 interval forecast
~$7.63 still end **October 28 at 00:00 Copenhagen (UTC+01:00)**. No extension/deletion
or backup of native omitted vectors is implied. Run disk is attribution within
that storage interval, not double billing. Local five-file public acquisition
adds $0 GCP cost; small control/metadata reads are operation estimates, not invoices.

The following E020 record is a **dated completed snapshot**, not current authorization.

**E020 completed/returned/reviewed; VM independently TERMINATED.**
[Inspection](../experiments/E020-context-information-integration/inspection-observed.json)
records phase `integration-20261023T111835Z-99af96f`, exact source **99af96f**, all
seven gates/eight serial science rules+target/reuse-after/collection/three upload-
readback pairs and matching completion bytes. Scientific outcome **MODIFY**, not
inferred from shutdown; [operations](../experiments/E020-context-information-integration/OPERATIONS.md)
owns results and a proposed local hybrid/skin-admission prompt, not another paid run.

Measured allocation **October 23 11:18:30.392–11:48:45.064 UTC / 13:18:30.392–13:48:45.064
Copenhagen**, **1,814.672 seconds / 30.24 minutes / 4.0326 vCPU-hours**, existing
8 vCPU / 32 GiB / 300 GiB work + 30 GiB boot. Science 1,218.609 seconds, sampled CPU
1,367.01 seconds / peak RSS 9.360 GB; global sampled growth 5.499 GiB, minimum free
63.051 GiB. Matching boot/PID/start/command watcher requested shutdown 11:46:05 UTC;
independent provider state verifies it. Original 90-minute clock / 105-minute
STOP/no restart and all reserves pass. No VM wake or SSH/science replay in inspection.

Private archive **1,038,909,515 bytes**, generation `1792755883690041`, SHA256
`5a13a09f67ae13dabe3082a2e764e041307554f408642887c1b54e1fc03d2d41`;
one admitted download, MD5 and every **201 members / 1,815,169,682 logical bytes**
verify, no aliases. Full omission inventory records 943 DNA members / 1,991,073,738
bytes retained only on stopped VM. Shared inputs/environment hashes are not backups.
Final completion delivery is proven by private bytes and guest digest; its own
post-upload CLI exit is not contained in its receipt. The new compact inspection
seal is local only; no cloud write/private upload was performed or implied.

Fresh paid-account credit **DKK 1,871.70 Available / 95%**, Certain usage/net pricing,
expiry **January 12, 2027**. October 1–23 Overview costs/savings DKK 99.86 / net zero;
>24-hour delay remains unknown with $35 reserve. Five account-local SKU expressions
and ordinary E2/Ubuntu/PD/IPv4/Iowa Standard/network/operations coverage pass.
Measured uptime/SKU attribution **$0.137636 compute/IP + $0.021139 run disks +
$0.116107 archive export upper = $0.274881 / <$0.426 with metadata/operations reserve**,
within original new $1. Not a reconciled invoice, sampled CPU bill or credit delta.
Post-stop disks to admission $0.226324 are part of the storage interval, not a
second disk invoice. Current all-version archive inventory 104 / 9,384,180,741 bytes,
zero soft-deleted; 169-hour approved storage forecast **$7.6276 of $8**, ending
**October 28 at 00:00 Copenhagen (CET, UTC+01:00)**. Existing stopped disks remain
**$31.20/month**. No automatic renewal/deletion, new service/resource or retention
extension. Next paid extraction/fits require a new concrete envelope/approval and
fresh credits/product/quota/source/runtime/headroom; no GPU eligibility assumed.
[Trial terms](https://docs.cloud.google.com/free/docs/free-cloud-features) and
[storage/network pricing](https://cloud.google.com/storage/pricing?hl=en) were refreshed.

The following E019 completed-review snapshot is preserved context.

[D014](decisions/D014-google-cloud-workspace.md) owns provider choice;
[STATE](STATE.md) owns the next action; this guide owns access, costs and retention.

**E019 completed/returned/reviewed; VM TERMINATED. Scoped scientific outcome MODIFY.**
[Inspection](../experiments/E019-window-context/inspection-observed.json) records
all ten native gates/fourteen serial science rules+target/reuse-after/collection/
upload/readback, source b47b916, all 309 members/two aliases and frozen diagnostics.
No wake, scientific replay, inference/old score, new data or resource/retention
change occurred during inspection. [Operations](../experiments/E019-window-context/OPERATIONS.md)
contains the separately proposed $1 cached integration, not current authorization.

Measured allocation **October 22 21:51:19.424 -> October 23 00:40:57.754 UTC**
(**23:51:19.424 -> 02:40:57.754 Copenhagen**), **10,178.33 s / 2.8273 hours** on the
same 8 vCPU / 32 GiB / 300 GiB work + 30 GiB boot. Science 9,448.36 s, sampled process
CPU 29,458.86 s, sampled RSS peak **17.334 GB**, allocation **22.6185 vCPU-hours**.
Global peak growth **12.590 GiB**, minimum free **68.558 GiB**. Matching boot/PID/
start/command watcher confirms parent exit and requests shutdown at 00:39:02 UTC;
independent provider TERMINATED confirms the stop. 29,700-second STOP/no restart
remains a fallback. No new resource/service, recovery or retention extension.

Fresh five Catalog SKUs/coverage and paid billing pass; credit **DKK 1,874.97
Available / 95%**, Certain usage/net pricing, expires January 12, 2027. October 1–23
Overview costs/savings DKK 92.22, net zero; >24-hour usage lag remains unknown with
$35 reserve, not an invoice. Current measured-uptime quote **$0.77199 compute/IP +
$0.11856 run disks + $0.12558 archive export**, subtotal **$1.01613 / <$1.268 with
metadata/operations reserve**, within original new $5. No credit-delta attribution;
run disk is part of separate storage interval, not a second disk invoice.

Private archive **1,123,690,164 bytes**, SHA256
`859b32ce555b13e7b494cd1d42b2383b65bbcb9b5a655c75686e5b0c9611c950`,
309 physical members / 2,078,927,328 logical bytes / all members and two exact aliases
pass. Token NPY/full FASTAs remain natively retained, not backed up by hashes.
99 listed versions/8,345,160,022 bytes, zero soft-deleted. Separate approved $8
169-hour storage forecast ~**$7.63**, ending **October 28 at 00:00 Copenhagen**;
existing stopped disks **$31.20/month**. No automatic renewal/deletion. The E019
compact local inspection seal is separate from native return and private upload
is not implied. E018 inspection backup remains already verified, not repeated.

Fresh official coverage/prices: [Free Trial terms](https://docs.cloud.google.com/free/docs/free-cloud-features),
[storage/network pricing](https://cloud.google.com/storage/pricing?hl=en), plus
read-only account-local Catalog/credit observations in the inspection receipt.

The following E018 execution/cost snapshot is **dated completed history**, not
a new current authorization. Its old credit balance is retained as observed.

**E018 completed, privately returned, checksum-verified and reviewed: ABANDON.
VM independently TERMINATED.** [Inspection](../experiments/E018-vote-led-recruitment/inspection-observed.json)
records seven native gates/eight serial science rules+target, unchanged source/
vector/cache axes, reuse-after, collection and all upload/readback exits. Source
`b996f6a` remains; no science replay, fit/inference/index/profile rebuild, marker
scan, new data, resource/service or retention change. E017/E016 remain preserved.

Allocation October 21 **12:29:42.797 -> 12:47:49.812 UTC**
(**14:29:42.797 -> 14:47:49.812 Copenhagen**), **1,087.015 seconds / 18.12 minutes**,
existing 8 vCPU / 32 GiB / 300 GiB work / 30 GiB boot. Science 553.37 seconds,
sampled CPU 627.22 seconds, sampled tree RSS 8.407 GB; charged allocation 2.4156
vCPU-hours. Fresh matching boot/PID/start/command watcher requested shutdown at
12:46:42 UTC; provider STOP 4,500 seconds/no restart remains a fallback. Global
sampled growth **3.524 GiB** from original launch snapshot; per-guard max 2.786 GiB
is separate. Minimum free 81.148 GiB. All execution limits pass.

Return **388,461,386 bytes / 174 members / 997,690,598 logical bytes**, SHA256
`3afd966ea07ca6c67e7bbcf92d310e31d56bd4365799dbbab8f9cc4ca0dcab88`.
Private guest/completion SHA, GCS generation/MD5 and every member verify; aliases
empty. The immutable inventory accounts for 975 new work files / 2,987,565,784
bytes, with 912 full-DNA files / 1,991,073,738 bytes omitted and retained on VM.
Omission hashes do not back up DNA/shared inputs or runnable prefixes.

Fresh Credits: **DKK 1,893.83 Available / 96%**, Certain usage/net pricing,
January 12, 2027 expiry, paid billing; Overview cost/savings DKK 79.66, net zero,
>24-hour delay possible and $35 prior/pending/storage reserve. Current five SKU
expressions/regions unchanged; existing eligible ordinary E2/Ubuntu/PD/IPv4/Iowa
Standard/network/operations only. [Terms](https://docs.cloud.google.com/free/docs/free-cloud-features)
and [storage pricing](https://cloud.google.com/storage/pricing?hl=en) refreshed.
Measured allocation/SKU quotes: compute/IP **$0.082446**, run disks **$0.012662**,
one export **$0.043414**, metadata small: **~$0.139 / <$0.389 with reserve**, within
original new $1. No cost increase needed; sampled CPU and credit deltas are not
invoices. Idle disks are separately retained, not counted twice as a storage bill.

Separate storage approval stays **$8 through October 28 at 00:00 Copenhagen**,
169 physical hours from October 21 midnight across DST. Current all-version
inventory 92 objects / 7,213,856,396 bytes, zero soft-deleted; disks/listed objects
plus $0.50 reserve forecast **$7.618**, below $8. Stopped disks remain $31.20/month.
No extension, automatic renewal/deletion, pruning or bulk backup/migration occurs.
The owner-approved earlier E017 compact inspection backup is uploaded/read back;
[receipt](../experiments/E017-information-aware-grouping/inspection-backup.json).
E018's then-local seal was later explicitly approved/uploaded; see the new backup receipt above.

The dated E018 [prompt](../experiments/E018-vote-led-recruitment/OPERATIONS.md#exact-following-prompt)
was invoked for E019 local implementation; E019 now owns the next execution request.
It does not authorize new VM work under this $1. Oral reads/mapping/new datasets
are separately costed scopes, not implicit extensions. Source/runtime/credit/
headroom/original retention gates remain necessary for any later native work.

The following E017 record is **dated completed history**, not another current
execution authorization or current cost snapshot.

**E017 completed and was independently reviewed; VM TERMINATED.**
[Inspection](../experiments/E017-information-aware-grouping/inspection-observed.json)
binds control-plane state, guest/private completion SHA, matching boot/PID/start/
command watchdog exit, nine native gates, eight serial science rules plus target,
retained reuse-before/after, collection and three upload/readback pairs. Source
`e78d766` and prepared `067ceb2` remain; no VM wake/new job, resource/service or
retention change occurred in inspection. Original Mac and local reader failures
are preserved; the local schema adapter repair does not change native science.

Allocation: **October 21, 01:26:31.522 → 01:57:35.627 Copenhagen**
(October 20, 23:26:31.522 → 23:57:35.627 UTC), **1,864.105 seconds / 31.07 minutes**,
8 vCPU / 32 GiB, existing 300 GiB work + 30 GiB boot. Watcher requested shutdown
at 01:55 Copenhagen after its bound parent exited. Provider independently reports
TERMINATED; 11,700-second STOP / no automatic restart remains a fallback, not
permission for another start. Science 1,238.96 seconds, sampled CPU 1,389.23 seconds,
sampled tree RSS 9.347 GB. Charged allocation is 4.1425 vCPU-hours; sampled CPU is
not provider pricing. Sampled growth 5.567 GiB / minimum free 84.671 GiB fit the
20 GiB extra / 25 GiB reserve bounds.

All **1,055,048,062 archive bytes / 245 members / 1,835,035,318 logical bytes**
verify, SHA256 `7b45916a0b7bd2dc938595c40a501af97ae8d1585a67b23b34103f985a6ca5fc`.
No aliases. Complete sparse/candidate/profile/selection/assignment and source/axes
contracts pass. Full native FASTAs and shared science/runtime bytes remain on disk;
omission hashes are not backups. Private/guest completion delivery agrees; a
self-contained completion-upload exit is not invented inside its pre-upload record.

Fresh Credits/Overview: **DKK 1,893.83 Available / 96%**, Certain usage, net pricing,
paid billing, expiry January 12, 2027. October 1–21 cost/savings both DKK 78.24,
net zero. Reporting may exceed 24 hours; pending use remains unknown with $30
prior-usage / $5 prior-storage reserves. Five current SKU pricing expressions,
regions and categories are unchanged. Existing ordinary E2 / nonpremium Ubuntu /
PD / IPv4 / Iowa private Standard storage/network/operations remain eligible under
[current credit terms](https://docs.cloud.google.com/free/docs/free-cloud-features)
and [storage pricing](https://cloud.google.com/storage/pricing?hl=en). No free
allowance, reconciled invoice or credit-delta attribution is assumed.

Measured-uptime/current-SKU gross quotes: compute/IP **$0.141385**, run disks
**$0.021714**, one archive export **$0.117911**, small metadata/operations:
about **$0.282**, below **$0.54 with reserve**, within original new $2. Storage
while stopped is separate within the $8 interval; run disks must not be counted
twice. Idle provisioned disks remain **$31.20/month / $0.0419355 per hour**.

Storage approval remains **up to $8, October 21 at 00:00 through October 28 at
00:00 Copenhagen**, 169 physical hours across DST. Fresh inventory before compact
inspection backup is **85 versions / 6,824,427,944 bytes**, zero soft-deleted bytes;
Iowa Standard private controls unchanged. Disks + listed bytes + $0.50 reserve
forecast about **$7.62**, below $8. The compact review adds negligible bytes inside
that reserve. No automatic renewal/deletion follows; October 28 is the next
retention boundary.

The next [proposed control](../experiments/E017-information-aware-grouping/OPERATIONS.md#exact-following-prompt)
needs a **new $1** after fresh gates: one-hour cumulative existing-VM clock,
75-minute STOP, four threads / 26 GB sampled RSS, 25 GiB reserve / 20 GiB extra /
2 GiB compressed export. Max forecast **$0.884**; no old compute budget carries
over. It is neither started nor authorized by this completed inspection.

Backup gaps remain: existing compact archives omit some full bin FASTAs, shared
reads/BAMs/features/views/markers and runnable dependency bytes. Inspect exact
inventories before later backup/migration or deleting regenerable duplicates.
No old local/VM artifact is pruned in E017. Hashes and locators are not backups.

The following E016/E015/E014 records are **dated completed history**. Their earlier
October 21 boundary/proposed extension wording describes those inspections; the
new owner-approved E017 storage decision above is current.

**E016 completed and independently reviewed; VM TERMINATED.**
[E016 inspection](../experiments/E016-positive-only-multiview/inspection-observed.json)
binds provider state, boot/process exit snapshot, guest/private completion bytes,
all10native gates/12serial scientific exits+final target and221archive members.
Native source2cfefa3 and all older inputs/results stay immutable; no wake or new
job/resource/service/retention change in inspection. Current scheduling15300sSTOP/
automaticRestart=false is historical fallback, not permission to start a new phase.

Single allocation start22:31:25.463UTC October19, stop23:29:21.065UTC (00:31→01:29
CopenhagenOctober20), **3475.602s /57.93min** at8vCPU/32GiB, existing300GiBwork+
30GiBboot. Watcher requested shutdown23:27:20UTC with matching bootd7b01a9d,
PID1847/start5180/command hash. Private completion SUCCESS, science/reuse/collection/
three upload-readback pairs exit0; final completion delivery separately matches
its guest SHA256. No self-contained completion-upload exit is invented. The sealed
science snapshot's pre-collection FAILED sentinel remains; final receipts resolve it.

All **1,058,172,524archive bytes /221members /1,921,098,467logical bytes** and two
size/SHA-identical aliases verify locally; SHA256
`dca4d686ce3feb2d4c0fef5058df70b7e5c25fdccb11ad9df6179b4a5919188c`.
All25,972work files/6.090GB are accounted, including3.982GB omitted full FASTAs
retained on disk. Shared data/features/views/marker/runtime and full FASTAs are
not backed up just by hashes. Native measured growth7.736GiB/minimum free90.239GiB
fit20GiBextra/25GiBreserve; science tree peak11.177GB under26GB. Sampled science
CPU7663.55s/wall2825.60s are separate from charged8vCPU uptime7.724allocated core-hours.

Fresh read-only Billing Credits: **DKK1,901.15Available/96%**, Certain usage/net
pricing, expiry2027-01-12, paid account. OverviewOctober1–20cost70.51/savings70.51/
net0; the tooltip confirms possible>24h delay. Pending usage unknown, with$30prior+
$5approved-storage reserves. Five current official SKU expressions/regions/currency
conversion are unchanged; only the daily effective timestamp changed. Ordinary
existing E2/nonpremiumUbuntu/PD/IPv4/privateIowaStandard/network/operations remain
eligible; no new product, unused allowance or credit-delta attribution assumed.

Measured-uptime/current-SKU gross quotes: **compute/IP$0.263611**, run disks
**$0.040486**, native export upper **$0.118260**, tiny metadata~$0.000025. Subtotal
~**$0.4224**, **<$0.68with$0.25reserve**, under original new$3. Pre-start approved
stopped gap$0.357085 and post-stop storage through inspection are separate; even
including both observed intervals/reserve remains<$1.50. Exact observation times
and amounts are in the inspection receipt. This is not a reconciled invoice or
sampled-CPU pricing. New native archive storage is~$0.020/month; local review
costs$0GCPcompute. Compact review backup/readback is separately byte-bound below.

Existing stopped disks continue **$31.20/month (~$1/day)**. **October21 review is
still required; current phase retention gate expires at00:00CopenhagenOctober21.**
No renewal/deletion is automatic. A seven-day continuation throughOctober28 would
need explicit new approval; a fresh read-only object inventory and proposed cost
are recorded with this inspection. All confirmation payloads remain unacquired;
new execution needs a fresh source/protocol/resource/credit/budget admission.
Original$3 remainder does not authorize another comparison.

E016 compact inspection backup2,250,990bytes/all132members, private archive and
checksum readback PASS, export upper$0.000252. Final source/evidence entry proof
and independent final TERMINATED check pass; original failed journals remain.
Local review/sealing31.87min/4.840GBsampled peak/2.3282GiBnew storage
fits the one-hour/8GB/4GiB ceiling. No numerical environment/auth or bulk DNA
is in the compact backup. Live object inventory76Standard objects/5.3704GiB
pre-backup; seven calendar days cross October25DST (169hours), disks/liveobjects~$7.087+$0.025,
with a proposed$8storage-only ceiling including reserve. This extension needs
explicit owner approval and fresh checks; it is not enacted. Noncurrent/soft-
deleted/uncommitted bytes are not included in that live-object inventory.

**E015 reviewed; final VM independently TERMINATED.**
[Recovery receipt](../experiments/E015-zero-reconstruction/recovery-observed.json)
and [comparison](../experiments/E015-zero-reconstruction/comparison-review.json)
bind actual exits, source/input/reader contracts, costs and complete archive checks.
The original science DAG and input recheck exit0; its phase remains FAILED because
isolated collection could not import its sibling helper. Preserve that journal.
No archive was present in the original prefix, and the inspection did not infer
quality from shutdown. The owner then explicitly approved one collection-only
wake with a fresh30-minute clock/45-minute provider STOP, up to$0.65 additional
within original E015$2. No science, installation, resource or retention replay.

| Existing VM purpose | Start UTC, October19 | Stop UTC | Uptime seconds |
| --- | --- | --- | ---: |
| Original two-fit science, failed collection | 10:25:22.165 | 11:38:44.496 | 4402.331 |
| Approved collection-only recovery | 13:52:04.943 | 14:00:31.103 | 506.160 |

The recovery kept `/srv/dl_binner/repo` clean at scientific sourceb259dca, transferring
only four byte-locked repair89dcd61 helpers into a fresh directory. Actual Linux
isolated pack/verify/link-refusal and fresh boot/process live/normal/crash watcher
checks passed before release13:54:17UTC. Private completion SUCCESS/readback true,
watcher exit13:58:54.936UTC and explicit provider STOP independently precede the
verified final TERMINATED state. Current policy2700sSTOP/automaticRestart=false;
this is not permission to start another phase. No provisioning/resize/quota/service
change or retention extension. Original failed config/collection and Mac journals
remain; exact isolated CLI testing is now durable AGENTS guidance.

Return **1,042,061,418bytes /199members**, SHA256
`27b0941a108df73ba7e983e39563d282833f79a74fbb83b74bb04f23af0ec643`,
all1,892,209,736 logical bytes/member aliases verify locally. All16,480 work files /
6,072,312,382 bytes were hashed in place, including16,399 omitted full FASTA files.
Omitted DNA/shared features/views/runtime are still on disk; hashes are not backups.
Recovery completion325.641s from boot; sampled peak0.287GB, growth1.951GiB,
minimum free97.975GiB, within new30min/8GB/5GiB/25GiB/2GiB limits. Original science
wall3732.172s/sampled CPU11644.78s/peak11.64GB are separate from paid allocation.

Fresh credit **DKK1,909.55 Available**,97%, Certain usage/net pricing, through
2027-01-12. Paid Overview October1–19 cost/savings62.36/net0 may lag>24h; pending
unknown, with$30 prior-exposure+$5 approved-storage reserves. Fresh official five
SKUs/ordinary existing E2/Ubuntu/PD/IPv4/private Iowa Standard/network/operations
remain covered; no new product. Total measured VM uptime4908.491s: compute/IP
**$0.372290**, run disk intervals **$0.057178**, native export upper **$0.116459**
plus compact exports~$0.000035: subtotal **$0.545961**. The intervening8000.447s
shared stopped-disk interval adds **$0.093195**, total **$0.639157**, **<$0.80 with
reserve**, within original$2 and new$0.65 recovery allowance. These are current-SKU
measured-allocation estimates, not invoice or sampled-CPU/credit-delta pricing.
Later stopped hours continue at **$31.20/month /$0.04194hour**, with **October21
storage review unchanged**. New native archive adds~$0.0194/month object storage.
Private compact review3,285,918bytes/all140members verify/read back; assessed
export adds$0.000367 and storage~$0.000061/month. Final priced total including
stopped gap/compact export~$0.639524; pooled small/storage reserves give<$0.80
(two separate phase reserves instead give<$0.95), below original$2. Full local
review/backup closes28.90min,5.413GB sampled numerical-stage RSS/2.297GiB extra;
no old artifact is deleted. Compact sealing/readback child RSS was not separately
sampled; its small standard-library payload scope is explicit in the receipt.
The proposed next training candidate needs its own source/protocol and conditional
new$3 authorization; E015's remainder does not carry over. No new data/confirmation
or external-tool run follows from this inspection.

The following E014 sections are completed dated history, not current VM state.

**E014 science completed; evidence recovered; VM independently TERMINATED.**
[Inspection](../experiments/E014-multiview-reconstruction/inspection-observed.json)
and [review](../experiments/E014-multiview-reconstruction/comparison-review.json)
bind phase `comparison-20261018T183446Z-858b7cc`, frozen science858b7cc, all15 gates,
19 scientific rule exits and final DAG target. Original FAILED phase status means
collection exceeded2GiB, despite science exit0. Preserve it, both failed partial
archives and the first collection-only wake's failure. Owner's latest instruction
expressly allowed collection wakes; it did not authorize another science run.

Measured VM intervals (UTC):

| Purpose | Start | Independently verified stop | Uptime seconds |
| --- | --- | --- | ---: |
| Original science + failed collection | Oct18 18:35:08.455 | Oct18 21:10:55.585 | 9347.130 |
| First collection-only wake, cap failure | Oct18 22:26:48.569 | Oct18 22:38:33.348 | 704.779 |
| Repaired collection-only wake, SUCCESS | Oct18 22:44:12.814 | Oct18 22:57:25.491 | 792.677 |

Total **10,844.586s /3.0124h**, compute/IP quote **$0.82252**, priced from charged
8-vCPU/32-GiB allocation and uptime, not sampled child CPU. Science child
8106.268s, sampled CPU18217.5s and peak sampled tree RSS18.266GB remain separate.
Persistent disks through final stop, including stopped gaps, add**$0.18332** using
the current catalog's October31-day conversion factor. Earlier730-hour normalized
estimates remain their dated quotes. Disks keep accruing after final stop.

Second collection helpers5030964 reused the three passed native sparse/unit graph
readers, reverified all27,207 original work files/13,653,291,886bytes, omitted only
three graph binaries and exact-byte duplicate reference payloads from the return,
then uploaded/read back every selected byte in the existing private Iowa prefix.
Archive **1,971,407,357bytes /657members**, SHA256
`6ddc8a7d01603432d79b7f24f4157fdc51c1b123ef6870e3332c0269afd32301`,
all4,125,997,517logical member bytes verify locally. Scientific outputs, full
view banks/DNA and failed journals remain intact on the existing disk. Omitted
bytes' hashes do not constitute a cloud backup of those bytes.

Fresh boot/process-bound held parentPID1551/start ticks4168, boot
`50675c55-0100-4483-a32c-04010e50f394`, live/normal/crash tests and2700s provider
STOP passed before release. Private completion SUCCESS/private readback true and
watchdog exit22:55:38.652UTC match; final provider stop22:57:25.491UTC confirms
TERMINATED. No new machine/disk/service/quota/resize or retention extension.
Collection consumed604.187s from its boot, extra3.673GiB under5GiB, with minimum
sampled free**105.62GiB**, above25GiB. No scientific replay or scoring on VM.

New archive export assessed**$0.22032**; earlier compact-admission export$0.02148,
gate export reserve$0.001 give subtotal**$1.2492**, **<$1.40 with$0.15 reserve**
for storage/operations/small charges, below original**$10**. These are measured-
uptime/current-SKU gross estimates, **not reconciled billing**. The final directly
refreshed Credits page shows **DKK1,915.36 Available**,97%, Certain usage/net
pricing, expiry**2027-01-12**. Delayed usage remains unknown; retain$30 prior
exposure+$5 approved-storage reserve. Ordinary existingE2/Ubuntu/PD/IP/privateIowa
Standard/network/operations coverage passed; no new product or service.

The original three-fit authorization is used. Its then-proposed zero-reconstruction
control needed its **own new$2** and fresh gates; the later E015 execution is above.
The original planning estimate was70–100min and
uses the existing allocation,2h cumulative/2.25h STOP,4threads/26GB/20GiBextra/
25GiBreserve/2GiBreturn, with accepted caches/runtime reuse and tested smaller
collection. Stop if original retention no longer covers its dates. No external
binner, extra data acquisition or confirmation follows from the original$10.

Existing disks continue at **$31.20/month (~$1.03/day)** while stopped. New compact
native/admission archive storage is~**$0.0403/month**, plus tiny review metadata.
**October21 storage review remains**, without extension. Local review used a
separate4GiB temporary allowance, peak3.5273GiB and5.511GB sampled RSS; only newly
created reproducible scratch copies were removed. No old local artifact was
migrated/deleted. Keep51.73GB oral reads/mapping outside this sequence-only phase.

**E011 recovery completed; VM independently TERMINATED.**
[Recovery receipt](../experiments/E011-cached-grouping-reference/recovery-observed.json)
binds phase `cached-20261017T080610Z-7a43eb6`, clean pushed source, strict cache/
installation reuse, all twelve successful native stages and the 327,025,885-byte
archive. All 1,905 members/997,707,722 logical bytes verify locally. Private/guest
SUCCESS agree; scientific success is established by exits/contracts, not the stop.
Start October 17 **08:06:10.549 UTC**; stop **08:13:23.285 UTC /10:13 Copenhagen**;
measured 432.736 s. The boot/process watcher recorded exit and shutdown request at
08:11:59 UTC; an explicit provider stop was also issued after collection. Do not
attribute final shutdown solely to the watcher. Fresh held/live/normal/crash
checks passed; 45-minute STOP remained armed. Initial SSH boot-banner timeout was
retried successfully on the same boot. No science/setup replay, provisioning,
resize, new service or retention extension.

Compute/IP **$0.03282**, disk interval **$0.00514**, assessed native export upper
**$0.03655** plus tiny compact-review export and small storage/operations: ~$0.075,
**<$0.105 including reserve**, below the retained $1 recovery envelope. The owner
permitted reasonable operational expansion/retries, but no expansion was needed.
These are measured-uptime/current-SKU estimates, not reconciled billing. Native
sampled child CPU 208.5 s is distinct from billed uptime/allocated 0.961636 vCPUh.
Initial free 131.09 GiB /minimum sampled 129.55 GiB; sampled increase 1.543 GiB.
The source/clock/25 GiB reserve/20 GiB extra/2 GiB export contracts passed.

Fresh paid-account Welcome credit **DKK 1,929.71 Available**, original 1,973.43,
Certain usage/Free Trial terms/net pricing, through **2027-01-12**. Overview
October 1–17 cost/savings 41.58/net 0 is delayed; pending usage is unknown, with $30
prior exposure and $5 approved-storage reserves. Catalog rates/eligible ordinary
E2/Ubuntu/PD/IP/Iowa Standard Storage/network/operations were refreshed before
start; no new product. **Existing disks still cost $31.20/month while stopped.**
Native E011 return adds ~$0.0061/month object storage; **October 21 review remains**.
No new cloud compute is needed for the recommended local cached-selector control.

The [first failed native journal](../experiments/E011-cached-grouping-reference/native-observed.json)
remains unchanged: libz loader-alias refusal before either community consumer,
404.884 s/~$0.043 before small charges. Operational recovery now proceeds inside
an authorized connected task with verified reuse and preserved failures; it must
not become another approval/upload handoff. Scientific tuning/extra campaigns
remain a different scope. The later local reviewer ASLR-text/schema failures are
also retained, without changing native outputs or the strict Mac tolerance.

**E010 is complete and the VM is independently TERMINATED.**
[The completed review](../experiments/E010-coherent-prototype/review.json) binds
GCP status, matching guest/private completion, the verified 335,636,093-byte science
archive/all 692 members and all seven successful native stages at frozen source
6917c3f. Start October 16 21:25:49.946 UTC; stop 21:47:33.061 UTC /23:47 Copenhagen.
Measured uptime 1,303.115 s /0.361976 h; no wake/resource/service/IAM/quota changes,
retry or retention extension occurred in this review. The verified watchdog and
4.25-hour STOP were retained; its post-exit snapshot remains on stopped disk and was
not fetched by waking the VM. Scientific success follows receipts, not shutdown.

Fresh paid-account Welcome credit **DKK1,933.15 Available through 2027-01-12**;
reported October 1–17 cost/savings 38.35/net 0 is delayed and pending usage unknown.
Fresh DKK SKUs remain unchanged. Measured compute/IP~**$0.09884**, disk interval
~**$0.01547**, actual bounded archive export upper ~**$0.03752**, prior asset readbacks
~$0.00250 plus small object storage/operations: ~$0.1543 before small charges,
**<$0.19 including reserve**, inside the original $2. These are measured-uptime/list
price estimates, not a reconciled invoice or credit-display subtraction.

Existing 30/300 GiB disks still cost **$31.20/month while stopped**. Native sampled
candidate/collection filesystem peak 162.69 GiB, minimum free 132.28 GiB; later outer
readback's 335.6 MB copy is outside that persisted sample scope. No new capacity is
needed. Review retention **October 21**, without extension, migration or deletion.
The complete prefix/data survive on the existing work disk; compact native outputs
are privately archived/readback-verified. Keep GitHub access read-only; branch is
`dev4-coherent-prototype`, frozen VM source 6917c3f. A proposed cached grouping
control needs its own prepared protocol, fresh credit/retention gate and separate
budget; unused $2 authorization does not carry over.

**E009's four unchanged controls completed; the preceding reviewed VM state was TERMINATED.**
[The reviewed result](../experiments/E009-competitive-benchmark/controls-review.json)
binds actual stage exits, archive/member checks, local diagnostics and costs.
Provider stop was **2026-10-15 22:55:19.426 UTC /October 16 00:55 Copenhagen**,
after 1.7542275 h; gross compute/IP~$0.479, export~$0.0542, under the separate $2.
No VM wake/resource change/retry/external tool ran in the local review. The current
policy remains 4.25 h/STOP/automaticRestart=false. That prior approval did not
authorize E010; the later owner message separately did. Previously checked Welcome
credit **DKK1,936.57 Available through 2027-01-12**; reported
cost/savings 31.92/net0 still lag actual usage. Disks remain 30/300 GiB and cost
**$31.20/month while stopped**; retention review **October 21**, no extension.
[D015](decisions/D015-coherent-prototype-upgrade.md) is implemented locally in
[E010](../experiments/E010-coherent-prototype/README.md); its separate $2 execution
was subsequently approved. No cloud action occurred during implementation; values
above are dated checks, not a fresh credit/control-plane refresh. Read-only GitHub access stays unchanged. Earlier
launch/one-hour/25-hour observations below are dated history, not active work.
**Phase 1 accepted: strict IAP SSH, exact private repository clone, pinned Linux
Codex CLI, ChatGPT authentication, actual desktop remote-project commands and
private archive upload/readback pass. The Ubuntu sandbox prerequisite was repaired
and the normal installed CLI sandbox passes.** See the
[structured receipt](evidence/gcp-workspace.json) for observations and hashes.

## Phase boundary and account verification

The completed phase 1 established a CPU Linux workspace, private backup and actual
Codex SSH access; it excluded v14 review and science. The first 2026-10-14 follow-up
accepted v14 and prepared the data stage locally. The **later owner message
authorizes the data-only phase at `5fec4e1`**, conditional on live credit/price/quota
admission: one full sample-0 assembly and ten ordered coverage sources. No binner
fit, score or architecture change is authorized. [D013](decisions/D013-first-comparative-benchmark.md)
replaces the mandatory shortlist with decisions that improve our own binner and
defers CompleteBin. [The phase receipt](../experiments/E009-competitive-benchmark/gcp-data-observed.json)
owns actual resource/execution outcomes. The owner's SDU login is deactivated;
UCloud files are reported intact but inaccessible. Do not delete them or rerun its
old transfer command. [The archived UCloud guide](history/UCLOUD_OPERATIONS.md)
and [E009 command](history/E009_UCLOUD_OPERATIONS.md) preserve that provenance.

Owner reports paid billing, expected USD300 remaining, expiry 2027-01-12 and a
budget alert. The owner subsequently read the current display as **kr1,973 remaining, none used,
expiring 2027-01-12**. APIs independently confirm account open/project billing
enabled and DKK currency; paid upgrade is owner-reported. The browser could not
read scope/status labels because of the loader mismatch below. Keep those evidence
sources distinct; USD300 is the original expected value, not a new displayed
USD balance.
Before any service activation/resource creation:

1. Inspect Billing → Overview for active paid billing and the selected account.
2. Inspect Billing → Credits for the Welcome credit's displayed remaining and
   original values, currency, available status, scope and exact start/end dates.
   Also inspect current costs/pending usage and the existing budget alert.
3. Inspect existing projects, billing linkage, enabled services, VM/disks/buckets,
   regional CPU/disk/IP quotas and current IAM access. Reuse a suitable project;
   do not create a second billable footprint by assumption.
4. Verify each proposed product/SKU is covered by that credit. Compute Engine CPU,
   ordinary Persistent Disk, non-premium Ubuntu, private Standard Cloud Storage
   and basic GCP IAP are the proposed path. Google documents VPC network charges
   as payable from trial credits; IAP for GCP itself has no service fee. No GPU,
   Marketplace image, Ubuntu Pro, partner model, Cloud NAT, load balancer or paid
   support is required. Paid access does not establish trial-credit eligibility.
5. Reconcile the complete estimate with remaining credit, expiry and existing
   account usage. **Stop and ask before unclear/uncovered costs or possible
   spending beyond credits.** Alerts and API quotas are not a credit hard stop.
   Persistent storage must be addressed before expiry; do not silently accept
   post-expiry payment-card billing or destroy evidence to avoid it.

Official rules: [credit/upgrade terms](https://docs.cloud.google.com/free/docs/free-cloud-features),
[displayed credit fields](https://docs.cloud.google.com/billing/docs/how-to/resolve-issues#viewing_promotional_credits),
[budget behavior](https://docs.cloud.google.com/billing/docs/how-to/budgets).
No credit amount is inferred from account upgrade or absence of known jobs.

### Live data-phase credit gate, 2026-10-14

The supported Chrome connection now reads the console; the earlier loader failure
is historical. Billing Overview shows **Paid account**. Credits shows the upgraded
Free Trial credit **Available**, **DKK1,972.04 remaining of DKK1,973.43**, starting
2026-10-13, ending **2027-01-12**, scope “Certain usage; see the terms for free trial”,
net-pricing application. The pre-upgrade row expired on 2026-10-13 and is not extra
credit. Overview reports DKK1.15 usage/DKK1.15 savings/DKK0 net for October 1–14;
credit consumption is DKK1.39. The UI explicitly warns costs may lag more than
24 hours: pending usage is not zero or precisely observable. Only this project is
linked to this billing account; the API found no running CPU allocation before
the phase, the existing 30/50-GiB disks and compact regional bucket. The known
small setup/storage exposure plus the bounded phase leaves ample credit margin.

Fresh official terms retain remaining Welcome credit after paid upgrade for the
original 90 days. Ordinary E2/non-premium Ubuntu/Persistent Disk/Standard Storage
and VPC/IP are eligible; no GPU, Marketplace, partner model, NAT or premium image
is needed. The existing Billing Catalog API was queried read-only with the existing
login, without creating an API key or enabling a service. Current DKK SKUs price
E2 core at **0.143478820/hour**, RAM **0.019231272/GiB-hour**, balanced disk
**0.657809999/GiB-month** and standard disk **0.263123999/GiB-month** beyond its
allowance. Account Pricing displays list prices in DKK, updated 2026-10-14.
Its quoted conversion is 6.5781 DKK/USD. IPv4's non-free rate is DKK0.032890499/hour;
current allowance tiers are not assumed available in the gross envelope.

At 8 CPU/32 GiB with 300-GiB work/30-GiB boot, the conservative 25-hour compute/IP
plus seven-day disk subtotal is about **USD14.01 /DKK92.13**, leaving the rest of
the **USD20 /DKK131.56** envelope for compact archive/operations/rounding. List
estimates are not invoices; current credits and allowances can reduce them.
The ongoing disks cost **USD31.20 /DKK205.24 per 730-hour month gross while stopped**.
That cost continues after day seven: review retention then; stopping alone does
not shrink capacity. Copy/restore to a smaller disk and deletion of accepted
evidence are separate decisions. Keep the 2027-01-10 expiry review.

The **300-GiB quota request is granted in the Compute API** (`SSD_TOTAL_GB=300`,
50 used before growth), case `a11cf91a-b76b-4c95-9f79-7dc7538f3611`. No extra service
or CPU quota was needed. The 300-GiB estimate excludes CompleteBin: the data-only
upper planning components are 232.29 GiB plus 25-GiB free reserve and filesystem
overhead. Reducing to 250 would save about USD1.15 over seven days while weakening
the reserve. Retain 300 and the complete data; no cost-driven DNA filtering.

[Official credit coverage](https://docs.cloud.google.com/free/docs/free-cloud-features?gclsrc=aw.ds),
[VPC prices/credit coverage](https://cloud.google.com/vpc/network-pricing?hl=en),
[localized public SKU method](https://docs.cloud.google.com/billing/v1/how-tos/catalog-api).

## Established initial layout and costs

The workspace uses `us-central1` (Iowa), zone `us-central1-a`. Live quota and
capacity checks passed: 12 global CPUs and 24 regional E2 CPUs available at entry.
CPU work on public simulated DNA does not presently need an EU-only
location. Iowa offers low E2 pricing and small US Free Tier storage allowances;
EU locations reduce interactive latency but raise costs/lose these allowances.
Co-locate VM and bucket to avoid cross-region transfers. This is not a data-residency
choice for future private clinical data.

Created **`dl-binner-cpu`, regular e2-standard-4, 4 vCPU /16 GiB**, with pinned
non-Pro x86-64 image `ubuntu-2404-noble-amd64-v20261009`, **30-GiB pd-standard boot**
(`dl-binner-cpu`) and **50-GiB pd-balanced working disk** (`dl-binner-work`), mounted
at `/srv/dl_binner`. Native Linux reports four CPUs; the UUID-based persistent
mount configuration passed verification after systemd reload. This fits code/setup
and small checks now, not bulk E009.
Balanced working storage provides better small-file/random-I/O behavior than a
tiny standard disk; the large UCloud copy problem is not a reason to recreate
snapshots here. Exact image/VM/disk descriptions are recorded in the receipt.
Secure Boot, vTPM
and integrity monitoring are enabled; both disks have `autoDelete=false`.
No GPU, local SSD or Spot
interruption risk. Grow working storage only after sample-count/peak-space review;
resize the stopped CPU VM for the next phase when its measured needs justify it.

Official USD list prices fetched 2026-10-13 (730-hour month for comparisons):

| Item | Running/ongoing rate | Behavior while VM stopped |
| --- | --- | --- |
| e2-standard-4 /16 GiB | $0.13402284/hour | Compute $0 |
| Alternative e2-standard-8 /32 GiB for later work | $0.26804568/hour | Compute $0 |
| One ephemeral external IPv4 | $0.005/hour while running | Released; $0 |
| 30-GiB standard boot | $1.20/month gross; potentially $0 under unused 30-GiB-month US allowance | Still provisioned/billable |
| 50-GiB balanced working disk | $5/month | Still $5/month |
| Same-region Standard bucket | $0.020/GiB-month gross; small US allowance up to 5 GB-month subject to aggregate limits | Stored/soft-deleted bytes continue accruing |
| Basic IAP to GCP | No IAP service fee | No IAP service fee |

Thus VM+IP is about **$0.139/hour**. The verified four-hour setup STOP policy
targets about **$0.56** compute/IP per start, plus about **$0.034** gross disk cost
over four hours. Provider termination can begin up to 30 seconds after the target
and stopping takes time; this is not a billing or remaining-credit hard cap.
Stopped disks are **$6.20/month gross**, or about $5 if the
boot-disk allowance is available; 5 GiB compact archive is $0.10/month gross.
Do not assume allowances are unused until the account inventory is checked.
Leaving this VM running for a 730-hour month is about **$101.49** compute/IP,
plus disks/archive/transfer/operations. No automatic deletion is proposed.
Owner approved this layout/recurring-storage exposure with a review **by 2027-01-10**.
This is not authorization for further compute, beyond-credit services, GPU or
scientific execution. The four-hour setup safety stop is a spending safeguard for this phase, not a
scientific-stage timeout. Set a deliberate future duration for real jobs.

[CPU rates](https://cloud.google.com/products/compute/pricing/general-purpose),
[disk rates](https://cloud.google.com/compute/disks-image-pricing),
[network/IP rates](https://cloud.google.com/vpc/network-pricing),
[storage/operation/transfer rates](https://cloud.google.com/storage/pricing),
[IAP pricing](https://cloud.google.com/iap/pricing),
[provider-side auto-stop](https://docs.cloud.google.com/compute/docs/instances/limit-vm-runtime).
Disk is charged by provisioned capacity, bucket by actual live/noncurrent/soft-deleted
storage. Prices exclude tax/currency conversion and any unrelated account usage.
The API verifies DKK billing currency; the USD list-price estimates are not a
DKK invoice or a fresh console estimate.

Inbound public downloads have no GCP ingress charge. Same-region bucket↔VM data
transfer has no transfer fee, while requests still have operation charges.
Select Standard network tier for the VM's internet egress: first 200 GiB/month
per account is free; then $0.085/GiB through 10 TiB at the consulted rate. Cloud
Storage has its own allowance/rates (100 GB US→eligible destinations; thereafter
about $0.12/GiB for ordinary internet transfer to Europe at the first tier).
These are distinct allowances, not unlimited downloads or a guarantee of $0.
Only compact setup data transfer is authorized now. Record large future transfers
before use; keep working data and archived outputs in the same region.

## Login and secure remote access

No connected browser or prior `gcloud` login was available at initial inspection.
Official Google CLI **589.0.0** is installed under ignored
`artifacts/gcp-workspace/tools/google-cloud-sdk/`. Its downloaded Mac x86-64
archive is 54,268,176 bytes, SHA256
`b49e8cb9d348267d46fade7b9c916a1aed7ce0ec07e142ce41cc0d24a95a9651`,
matching the official install page. `gcloud version`, no-account auth listing and
actual `compute instances create --help` ran locally. No cloud API was enabled at this initial inspection.
Credentials use an ignored owner-only configuration directory; never commit it
or include it in an archive. Local validation is not Linux installation proof.

Owner action, from Mac Terminal (normal Google login; no credentials in chat):

```bash
cd /Users/rasmusallesoeenielsen/Documents/dl_binner
CLOUDSDK_CONFIG="$PWD/artifacts/gcp-workspace/private-gcloud-config" \
  "$PWD/artifacts/gcp-workspace/tools/google-cloud-sdk/bin/gcloud" auth login
```

The owner completed this login and CLI auth now passes. Read-only APIs verify an
open billing account, billed My First Project and owner IAM role. Compute, IAP,
IAM and OS Login were subsequently enabled for the approved layout. At that
initial setup browser access remained unavailable despite the owner enabling it,
so credit fields were supplied by the owner. The old Browser tool identified a
concrete loader mismatch: it imported absent plugin
`26.930.61225/scripts/browser-service.mjs`, whereas installed plugin is
`26.1007.30912`. A supported Node reset/retry produced the same error. Vendor diagnostics confirm
Chrome running, extension installed/enabled and native-host manifest correct;
That loader failure was distinct from Google login; current supported Chrome
access succeeds in the data phase. Do not modify vendor/native-host files or use
raw cookies/CDP to recover a future browser failure. No API key/JSON service-account key is
needed on the Mac. Do not replace credentials merely because a sandboxed GitHub
network probe failed: the authorized network probe verified the existing private
GitHub login successfully.

The dedicated `dl-binner` VPC / `dl-binner-us-central1` subnet (`10.50.0.0/24`)
allows only IAP's `35.235.240.0/20` to tcp22 on the `dl-binner-iap` VM tag. Private
Google access is enabled; there is no public SSH/HTTP rule. The project's default
network is unchanged. The ephemeral external IP permits outbound
apt/Git/CAMI access without NAT; it does not open inbound SSH. OS Login uses the
owner's dedicated Mac key outside Git. Guest attributes were
enabled before first boot, and authenticated Compute API host keys seed a dedicated
known-hosts file;
[Google's host-key guidance](https://docs.cloud.google.com/solutions/connecting-securely)
explains the trusted back channel. Verify host keys
through a trusted cloud/serial identity, not `StrictHostKeyChecking=no`. Prefer
an unprivileged working user; use sudo only for OS/disk setup. No default broad
Editor service account: if backup access needs an attached service account, grant
only bucket-specific object access and no key file. Do not grant project-wide
Storage Admin merely to copy archives.

The concrete **`dl-binner-gcp`** alias in the Mac's `~/.ssh/config` uses an absolute
`gcloud compute start-iap-tunnel ... --listen-on-stdin` ProxyCommand and the ignored
Google login configuration. `ssh dl-binner-gcp` passed with strict pinned host keys,
OS Login user `rasmus_allesoee_gmail_com` and a dedicated key. The host's Ed25519
fingerprint is `SHA256:EnphGEWw80eNITGEQcbIFyhdXS2dvuz1NhtW85x7h/4`. Disable agent
forwarding/password/root SSH. Do not start an
unauthenticated WebSocket app-server on the VM's public interface.

## Git and Codex app acceptance

The initial clean branch is `benchmark-planning` at
`2109998a230a0757be424e6f55c3a1bf17971ebe`. Live GitHub inspection verified
`Rasmus-allesoee/dl_binner` remains private; `origin/main` is
`5e54538d1799e8d2538621729400f33fbaf017b9`, and the benchmark branch was not remote
at entry. The owner authorizes a normal push of this working branch, preserving
all accepted commits; no force push, merge, visibility change or release.
Source-freeze commit **`440911904e8342c2f3a27254f95caa51871cf706`** was normally
pushed with upstream and cloned byte-identically onto the VM. Main remains
unchanged. Subsequent setup receipts must be normally pushed and synced before
handoff; the final verified Git state is reported in chat without a self-referential
commit hash inside its own committed receipt.

The VM uses a repo-specific **read-only deploy key** for cloning/fetching; no Mac
GitHub token was copied. Repo-local commit identity matches the existing Mac project.
`/srv/dl_binner/repo` was cloned at the source-freeze SHA and subsequently synced
cleanly to `bde9fbf49c035286cae713799d48d7d55a3d87a5` for desktop acceptance.
Repo-local `core.sshCommand` pins GitHub host keys
and this key. Linux push rights are not configured; later authorization can use
a separately scoped choice. Keep environments under
`/srv/dl_binner/experiments/e009/envs/`, data/tmp/runs separately from the checkout,
and compact archives under `/srv/dl_binner/archive/`. Do not forge UCloud paths
or copy linked Mac environments to Linux.

Official **Codex 0.160.1** complete Linux package is installed at
`/srv/dl_binner/tools/codex-0.160.1`; `~/.local/bin/codex` is a wrapper preserving
that package's resource paths. Actual login-shell PATH, version and app-server help
pass. The 160,785,122-byte release archive passed SHA256
`340801565906a7028f6baaa9ab6853addaef221f0016a1417a7c1ffdd96c21f0`; its regenerable
download was removed after installation. Native image-supplied Google CLI is
588.0.0. Authenticate with the existing ChatGPT plan through device login or an
SSH-forwarded localhost callback; do not
silently switch to metered OpenAI API billing or copy a general auth cache to
Git/backup. App-server must remain SSH-managed/private.

**Authentication command** (owner completed it; status independently reports
`Logged in using ChatGPT`; no tokens/login codes in chat):

```bash
ssh -t dl-binner-gcp 'bash -lc "codex login --device-auth"'
```

For a future fresh login, complete the browser flow with the existing ChatGPT account. If device login is
blocked by an account setting, return the non-secret error; do not switch to a
metered API key. In the desktop app: **Settings → Connections → SSH → enable/add
`dl-binner-gcp`**, then choose `/srv/dl_binner/repo`. Start a chat there and run only
`pwd`, `git rev-parse HEAD`, `git status --short --branch`, and `uname -s`. Native
app controls are unavailable in this session, so the owner performed this app action.
[Official SSH workflow](https://learn.chatgpt.com/docs/remote-connections#connect-to-an-ssh-host),
[login](https://learn.chatgpt.com/docs/auth#login-on-headless-devices).

Acceptance needs two separate observations: (1) SSH reads exact HEAD and runs a
harmless shell command on Linux, and (2) a chat on the saved remote project runs
`pwd`, `git rev-parse HEAD`, `git status --short --branch`, and `uname -s` there.
A locally executed `ssh ...` or remote CLI `--version` alone is not verified app
workflow. Record raw small outputs/commit/runtime identity; no scientific test.
The next phase starts only after this actual connection and billing gate pass.

**Observed acceptance, 2026-10-14 Copenhagen:** the owner returned
`/srv/dl_binner/repo`, exact HEAD `bde9fbf49c035286cae713799d48d7d55a3d87a5`, clean
`benchmark-planning...origin/benchmark-planning` and `Linux`. Independently inspected
native session metadata identifies `Codex Desktop`, CLI 0.160.1 and that remote
directory; the allowlisted four-command outputs agree. No chat messages or auth
cache were collected. The first sandboxed calls failed with
`bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`; the desktop retry
succeeded with escalation. Keep both observations: desktop access passed, while
ordinary sandbox operation needed a host prerequisite repair.

### Ubuntu sandbox prerequisite

The native kernel log attributes the failure to Ubuntu 24.04's AppArmor user-namespace
restriction. The official Codex documentation prescribes a system Bubblewrap and
the distro's scoped `bwrap-userns-restrict` profile. This host now has
`bubblewrap 0.9.0-1ubuntu0.3` and AppArmor tools/profiles
`4.0.1really4.0.1-0ubuntu0.24.04.8`. The following OS setup ran once; reuse the healthy
installation, and inspect any existing custom profile before changing it:

```bash
sudo apt-get update
sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  bubblewrap apparmor-profiles apparmor-utils
sudo install -m 0644 /usr/share/apparmor/extra-profiles/bwrap-userns-restrict \
  /etc/apparmor.d/bwrap-userns-restrict
sudo apparmor_parser -r /etc/apparmor.d/bwrap-userns-restrict
```

The installed CLI's actual 0.160.1 contract is `codex sandbox -- COMMAND`, with no
`linux` subcommand. Its normal sandbox ran the same harmless four commands with
exit zero after this repair. `kernel.apparmor_restrict_unprivileged_userns` remains
**1**; no global sandbox/kernel restriction was disabled. This is native CLI proof
after repair, separate from the earlier actual desktop retry. The final sync
restarts the host, clearing the previous app-server's helper selection.
[Official Ubuntu prerequisite](https://learn.chatgpt.com/docs/sandboxing) and
[installed-version sandbox implementation](https://github.com/openai/codex/blob/rust-v0.160.1/codex-rs/linux-sandbox/README.md)
explain the system-helper selection and scoped profile.

## GitHub write-access recommendation

The VM's existing **read-only deploy key is sufficient for the next data phase**:
fetch the normally pushed source commit, run data work and retain outputs/logs on
the VM. No repository permission is changed in this preparation. ChatGPT/Codex
login and GCP OS Login do not confer GitHub push rights. Keep credentials outside
Git, research archives and terminal output.

If the owner wants direct VM pushes later, prefer a **separate fine-grained PAT**
limited to `Rasmus-allesoee/dl_binner`, Contents read/write +required Metadata read,
with an explicit short expiry (e.g. 30 days). Keep the current SSH key for fetch;
configure a separate HTTPS push transport and an owner-only memory/secure credential
helper. The owner creates/enters the token in a protected interactive session;
never paste it into chat, a Git remote URL or a logged shell command. Workflow
permission is a separate grant only if changing workflow files is actually needed.
Token presence is capability, not authorization to push/merge/publish on every task.

A **separate write-enabled deploy key** is a reasonable simple single-repository
alternative, and safer to revoke independently than converting the current read
key. It has no automatic expiry and grants repository write. Neither this key nor a
Contents-write PAT is branch-specific by itself; branch protections/rulesets
govern allowed pushes. A compromised VM/private key can exercise those rights.
GitHub explicitly recommends Apps for finer control; a private App's one-hour
installation tokens suit ongoing automation but require app/key/token-refresh
setup that this single-owner workspace does not presently need. SSH agent forwarding
would expose the owner's existing authority to the remote session and remains
disabled. A broad classic PAT or copied Mac authentication cache is unnecessary.

Recommendation now: **retain read-only**. Optional later direct-push choice:
**short-lived single-repo Contents-write PAT**, or a separate write deploy key if
its simplicity is preferred after accepting non-expiring write scope. Owner action
is choosing/creating that credential and approving its exact scope/revocation;
no action is required for read-only data execution itself. Do not create/register
keys, tokens, an App or an extra cloud secret service without that later direction.
[GitHub deploy-key comparison](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys),
[fine-grained PAT permissions/expiry](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

## Private archive and retention

The created bucket is **`gs://dl-binner-archive-167650584170/`**, regional Standard
in `us-central1`, uniform bucket-level access and **public access prevention enforced**. No public ACL/link, versioning,
Autoclass, Archive/Nearline minimum-duration fee, bucket lock or paid intelligence
feature. Keep default short soft-delete protection visible in stored-byte costs.
Use append-only uniquely named compact checksum-bound archives of accepted outputs
and diagnostic summaries; no whole-disk/environment snapshots or automatic copy
of raw reads/BAMs. An accepted input that cannot be reacquired needs explicit backup.

Phase-1 backup contains only harmless setup receipts/source commit/config summaries,
never `.ssh`, `.codex/auth.json`, `gcloud` databases, private keys, signed URLs,
GitHub tokens, machine credentials, inbox/history caches or numerical environments.
Upload it, read it back and compare SHA256/byte count; verify bucket IAM and public
access prevention. A future archive is not a backup until its readback succeeds.

The VM's own `dl-binner-archive` service account uploaded and read back the seven-member
setup archive at `workspace/20261013T220405Z/`: **6,126 bytes** compressed /15,748
logical archived bytes, SHA256 `2d88d5c0f1c2cf648f359b487135589e98d77556b1b918f8f3ea03b603a5295b`.
`cmp` and SHA256 pass; the checksum is the second object. The account has only
bucket-scoped Object Creator/Viewer, no project-wide role or JSON key.
Default soft delete is seven days; no public principals, versioning or Autoclass.
This backs up phase-1 setup evidence, not scientific outputs or authenticated app
state. Source history is on private GitHub; existing scientific assets were not migrated.

The separate acceptance checkpoint at `workspace/20261013T223943Z-acceptance/`
is **5,858 bytes** compressed /19,836 logical archived bytes, eight allowlisted
members, SHA256 `d6fc40d656b855e018091452faf433e4774ee2088a76c5760c2e06c9d9c9d0ca`.
Mac upload and byte/SHA256 readback pass while the VM is stopped. It retains the
actual desktop command metadata/outputs, repaired sandbox output, scoped OS
prerequisite and the first provider stop/cost checkpoint. The full live Codex
session, auth state and inbox are excluded. The initial archive is preserved.

For accepted science retain final partitions/required checkpoints/evaluation,
axes/masks/exclusions, compact logs/metrics/provenance and exact regeneration input
identities. For obsolete failures retain exit causes/useful native diagnostic
snippets/config/hashes, then record and remove bulky regenerable outputs after
review. Do not delete accepted/irreplaceable evidence or old inaccessible UCloud
files. Do not retain all scratch/temp/failed BAMs by default. Only the newly
downloaded Codex installer was removed; no original research files were deleted.
Installed tools are about 447 MB logical, checkout 34.5 MB and the work disk has
about 461 MiB used, leaving its rest available; bulk E009 will need a new space review.

## VM start, stop and cost control

From the Mac checkout, use the isolated authenticated CLI. Start only for an
explicit task and verify its approved allocation/runtime policy first. The initial
setup used four hours; the authorized data phase uses **25-hour automatic STOP**.
Each start recomputes the current policy; do not assume that 25 hours is the
approved duration of a future small task.
Both disks, source and login state persist. IAP uses the instance identity, so
an external IP change does not require replacing the SSH alias or host keys.

```bash
cd /Users/rasmusallesoeenielsen/Documents/dl_binner
CLOUDSDK_CONFIG="$PWD/artifacts/gcp-workspace/private-gcloud-config" \
  "$PWD/artifacts/gcp-workspace/tools/google-cloud-sdk/bin/gcloud" \
  compute instances start dl-binner-cpu \
  --project=project-d17bd588-df31-488f-b16 --zone=us-central1-a
```

After the job, use the same command with `stop` instead of `start`; inspect with
`compute instances describe dl-binner-cpu --project=... --zone=us-central1-a
--format='value(status)'` (the exact project is above). `TERMINATED` means stopped
in Compute Engine; the VM and disks have not been deleted. A stopped VM cannot
accept SSH; start it before the desktop remote project. Changing the policy or
CPU/storage allocation is a separate workload/cost decision.

Record actual running elapsed time and projected compute/IP/disk/bucket cost;
reported billing can lag and must be checked separately. Confirm what remains
billable while stopped. The approved credit-expiry review is **by 2027-01-10**;
no automatic billing-disable/data-destruction mechanism is assumed safe.

**Recorded setup checkpoint:** the first provider-confirmed stop is
2026-10-13 22:39:43.273 UTC (2026-10-14 Copenhagen); status `TERMINATED`, no external
IP. Start-to-stop elapsed is **2,643.825 seconds /44.064 minutes**, or **2.93758
allocated vCPU-hours**. At the consulted rates this is **$0.10210 VM/IP** plus
about **$0.00624 gross disks over the same elapsed period**, excluding tax/FX,
requests and any allowance discount. This is measured allocation priced at list
rates, not an invoice or a newly displayed remaining-credit balance. Disk billing
also continues during stopped time. A brief additional start synchronizes the
final records and verifies persistence; its provider timestamps and aggregate
allocation estimate are retained separately in the checksum-bound private
`workspace/20261013T223943Z-acceptance/final-sync-stop.json` receipt, reported after
the final stop. This avoids a committed record claiming its own Git hash.

The installed sandbox prerequisite and UUID mount configuration are persistent
OS settings. The source-sync restart checks the mount, exact clean Git HEAD,
ChatGPT login status and normal CLI sandbox; it does not repeat a scientific
runtime test. New GCP binner environments/native-scale execution remain unverified
and belong to the authorized scientific phase.

## Data-phase resources and later scope

V14 remains accepted without replay. The later owner message authorizes exact
prepared commit **5fec4e1d1700c64c4bdd9945bad4e116ade73c57**, normally pushed from
the Mac and cleanly fetched/fast-forwarded by the VM's read-only GitHub key.
[The phase receipt](../experiments/E009-competitive-benchmark/gcp-data-observed.json)
owns actual native/data status, provider timestamps, disk changes and costs;
[operations](../experiments/E009-competitive-benchmark/OPERATIONS.md) owns commands
and review boundaries. The older [preparation API snapshot](../experiments/E009-competitive-benchmark/gcp-preparation.json)
remains dated evidence of the initial 4 CPU/16 GiB, 30/50-GiB disks and 250-GiB quota.

Live credit/price admission and effective **SSD_TOTAL_GB=300** passed. The existing
Iowa VM was changed to **e2-standard-8/32 GiB**, existing work disk grown **50→300
GiB**, and existing ext4 filesystem expanded with `resize2fs`, **without formatting**.
Provider STOP was set to **25 hours before start**. SSH verifies eight CPUs,
33,646,948,352 memory bytes, glibc/architecture, the same UUID-backed mount and
clean exact source. No additional VM, GPU, service or GitHub write credential was
created. Full samples **0,2,3,4,6,9,10,11,14,17** use one full sample-0 assembly.
The complete independently owned pinned Linux data runtime and real tiny changed-
driver fixture pass. Runtime/fixture time is counted in the cumulative 24-hour
production allowance; 25-GiB free reserve and existing activity/RAM guards remain.
No new capacity, automatic retry, clock extension or data filtering is permitted.

Stopping compute preserves **USD31.20 /DKK205.24 per 730-hour month** of provisioned
boot/work disks, less any available allowances, plus actual bucket storage.
Review grown retention **by 2026-10-21**, then before **2027-01-10** credit expiry
review. Disk capacity cannot simply be shrunk. An approved smaller replacement
requires verified copy/restore and an explicit decision about accepted evidence.
No unapproved payment-card billing or automatic important-data deletion follows.

## Verified data exit and bounded review, 2026-10-15

The original E009 data driver failed only in final PAF parsing after all assembly/
ten BAM/depth stages completed. Its watchdog snapshot requested shutdown at
**09:29:52 UTC**; the control plane confirms **TERMINATED at 09:32:21.624 UTC /
11:32 Copenhagen**. First provider uptime was **13.179723 h**. A stop is not success;
[the reviewed experiment](../experiments/E009-competitive-benchmark/OPERATIONS.md#earlier-data-review-and-failed-dag-evidence-2026-10-15)
and its original receipts distinguish accepted feature data from then-unadmitted
truth. The separate [v2 admission](../experiments/E009-competitive-benchmark/truth-v2-admission.json)
now resolves that boundary locally without a new wake.

The owner's review request needed evidence on that stopped disk. Before wake,
current console/API checks verified **DKK1,952.79 available**, expiry **2027-01-12**,
paid billing, billing enabled, ordinary eligible resources and unchanged DKK SKU
rates. Reported October cost/savings were **DKK5.16/DKK5.16, net DKK0**; issued-credit
use was DKK20.64. These displays lag and are not a reconciled invoice or zero
pending usage. No extra service, IAM grant, quota, VM or disk was created.

The same 8-CPU/32-GiB VM was set to **one-hour STOP before wake**. The bounded
review ran **12:51:17.410–13:19:53.611 UTC /14:51–15:19 Copenhagen**, **0.4767225 h**,
without resizing, reinstalling or replaying the data DAG. Current API state is
**TERMINATED**, external IP absent, both **30/300-GiB** disks preserved with
`autoDelete=false`; its current provider maximum remains **3,600 seconds /STOP**.
The old boot-bound watchdog is not active on a new boot. Re-arm a suitable end-of-
phase stop only for an authorized future phase; never reuse the old PID binding.

Measured priced uptime gives **$3.5987 original +$0.1302 review = $3.7288 gross
compute/IP** before allowances/credits. Both running intervals total **13.656446 h /
109.251564 allocated vCPU-hours**; sampled native CPU is a different quantity.
Seven-day provisioned boot/work planning cost remains **$7.1803** at the conservative
730-hour conversion. The run/review plus seven-day disk subtotal is **$10.9091**,
before small archive/operations/export and well inside the **$20 data-only** cap.
Seven days is planned retention exposure, not all already-spent cash. The actual
phase invoice remains unavailable while billing catches up.

The exact private 246,936,673-byte archive has verified native upload/readback and
all member hashes independently verified on the Mac. Its ~0.230-GiB regional
Standard storage is **~$0.0046/month gross**. Raw reads, BAMs and environments stay
on working storage. The original production filesystem peak was **170.66 GiB**,
minimum sampled free **124.52 GiB**; the 25-GiB guard was not approached. A future
225–250-GiB data disk may suffice, but shrinking requires a new approved copy/
verification/capacity plan; no resource change or bulk-data deletion ran here.

Stopped provisioned disks still cost **$31.20/month gross**. Review retention by
**2026-10-21** and credit expiry by 2027-01-10. No retention extension or post-credit
card spending is authorized. A later proposed **$2 diagnostic-fit ceiling** is
separate from the data-only $20 and remains unapproved; no external fit is the
immediate next step. CLOUD does not authorize any scientific action from a low
monetary estimate alone.

No binner fits/scores are authorized. [D013's later recommendations](decisions/D013-first-comparative-benchmark.md)
prioritize our unchanged diagnostic controls and at most one resource-admitted
SemiBin2 reference; MetaCAT core is conditional on a useful grouping question.
SCGBinner/COMEBin full runs and **CompleteBin are deferred**, with architecture
ideas and accepted contracts preserved. A future CompleteBin run could require
400–500-GiB work/64–128-GiB RAM, but that is an unapproved source-derived possibility,
not the next provisioning step. Reassess measured input/peak costs and live prices
only when its incremental evidence justifies a run. Native CPU availability and
50 epochs do not imply affordability. Healthy GCP prefixes persist while stopped.

If credits run out, assess Colab/Kaggle as future alternatives; neither is
configured or used. Do not silently charge the card or delete accepted evidence.

## Unchanged-control launch observation, 2026-10-15 (completed October 16)

The existing eight-CPU VM started at **21:10:04.207 UTC**, with 30/300-GiB disks
and no resize/provisioning/service/IAM changes. Fresh paid-account credit check
shows **DKK1,942.67 Available through 2027-01-12**; reported usage/savings27.89, net0,
with pending usage not assumed zero. Fresh SKUs price gross compute/IP at
**$0.273045676/h**, max4.25 h **$1.160444124**, within the separate approved **$2**.
Existing storage remains within its October 21 retention review, ~$31.20/month gross.
The truth evidence archive now has a private upload and verified SHA256 readback.

The VM is clean at **cf7bf2a17eab0c5a2f70999d04e766af1e14f98a**; its GitHub key
remains read-only. Initial IAP connection preceded SSH readiness; serial boot
completion was checked before connecting, and no scientific command was retried.
Native mount/8 CPU/basePython3.12 and148.2-GB free-space checks pass. Fresh control
env owns its numeric dependencies; actual source/default/inventory/import/CLI gates
pass. Latest snapshot is live ten-depth feature preparation with ~1 CPU native
work and no failure. It is not a completed fit or a quality result.

The root systemd watcher pins boot63cf3041-14ae-4ce2-82f8-5a1df18e8abc /PID1975,
start tick27468 and exact command hash, every30 s with60 s exit grace. Live/normal0/
crash7 native detection tests pass without host shutdown. Its timer is active only
for this boot. The service also has a boot-relative four-hour cgroup runtime bound;
provider4.25 h STOP/automaticRestart=false remains independent. Hard phase/provider
ends are **October 16 01:10/01:25 UTC =03:10/03:25 Copenhagen**. The held parent was
released only after actual watcher verification. It archives/readbacks completed
results and compact status, then exits to trigger shutdown. Do not stop active
science merely because this chat ends. Do not wait/poll until completion; owner
will request inspection later. Guest attribute `e009-controls/status` and private
completion URI are pointers, not substitutes for actual stage/artifact review.

## E010 preparation boundary, 2026-10-16

The integrated candidate is implemented locally on `codex/coherent-prototype`
after normal PR #2 merge. [E010 operations](../experiments/E010-coherent-prototype/OPERATIONS.md)
own the new proposed $2 phase, native gates, four-hour cumulative clock/4.25-hour
STOP, estimates and exact approval prompt. No VM, credit refresh, resource change
or spending occurred during implementation. Last observed TERMINATED is dated
E009 evidence, not a new control-plane check. Existing stopped-disk charges and
October 21 retention review remain; no extension. Main/VM scientific data stay
immutable and the VM GitHub key stays read-only.
