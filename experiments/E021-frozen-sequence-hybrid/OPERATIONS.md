# E021 operations

## Verified final E009-only outcome, October 25, 2026

**Completed and independently reviewed: MODIFY.** [Inspection](inspection-observed.json),
[comparison](comparison-review.json), [all 156 targets](comparison-targets.tsv) and
[cost ledger](cost-review.json) are current. Dated admission/running/failure snapshots
below remain history; they do not override this completion or authorize new science.

| Frozen full-reference diagnostic | Preserved E019 | E021 E009-only |
| --- | ---: | ---: |
| Parent / old / E013 R95 | 7.3058 / 7.6044 / 7.3058% | 7.8175 / 8.2428 / 7.8175% |
| E013 targets >=50% recovered | 12 | 14 |
| E013 targets >=90% recovered | 7 | 6 |
| E013 targets with any passing bin | 23 | 25 |

E013 final gains 2,837,916 bp / 0.51165 percentage points: 10 targets improve,
15 decline and 131 are unchanged. ASV406.4 gains 3,111,747 bp (0 -> 91.38%);
ASV150.14 and ASV300.2 fall below 90%. E013 chooses two alternatives among 2,012
parents without changing any target's recovered bp, although assignments change.
Old refinement gains another 2,359,192 bp / 0.42534 points; it is a retained
alternative, not a truth-selected replacement. [Full target table](comparison-targets.tsv)
retains all pre/old/post alternatives and original reference denominators.

Native all-query bacterial 5-NN purity improves 70.9525 -> 71.2571%, while bacterial
restricted B3 precision/recall decline 81.4478/58.7453 -> 80.8480/57.7927%.
Whole-population 5-NN is 74.8933 -> 75.6927%; eukaryotic queries are numerous,
so that aggregate cannot establish a cellular recovery gain. The fixed label-blind
small raw/learned probe stays 92.8571/82.8571% overall; this raw probe is saved
TNF+depth geometry, not a Mac reread of 768-dimensional GLM arrays. Final online
fused effective rank is 36.9467, std 0.10993; all original collapse guards pass.
Neighbor audit recall@5 is 1.0, recall@30 is 0.998177. Native reload is exact.
No demonstrated axis/source/view/depth/reload/geometry/export bug explains the
mixed result; these checks do not prove optimality or isolate a causal GLM effect.

The original numerical KEEP rule is unchanged: E009 clears the practical R95
gain threshold but loses a >=90% target; oral is unrun, so joint KEEP is unmet.
Scoped MODIFY preserves a useful complementary branch and its expensive bank,
without a product-default/uniform-improvement claim. Full 156 references /
554,661,890 bp, all 145,702 contigs / 231,678,157 bp, 3.3034% N quarantine and all
length/origin/eligibility/marker/unknown/non-target/excluded/unassigned populations
remain in diagnostics. E013 final accounts for 85,744 assigned / 206,919,018 bp,
3,297 unassigned / 2,723,685 bp and 56,661 excluded / 22,035,454 bp. No short DNA
was removed from denominators. Oral and skin have no E021 extraction, fit or score.

### What actually completed and what failed

Original `gpu-native-v6` extraction and full reader passed. Bank and runtime have
identical sender/relay/receiver digests, but original receiver records correctly
remain pending, `consumer_admitted=false`. Original `cpu-E009-consumer-v5` passed
only owned-runtime inventory, then failed on an empty ready JSON command before
any science. The later IAP 4003 followed shutdown; it never proved CPU progress.
Old command files and every failure receipt/archive remain unchanged.

Operational source **1f6214013c359e66fb258faccc9d0052036777fb** fixes atomic command
publication and preloads the complete queue before release. Fresh `cpu-E009-recovery-v7`
verified retained runtime members/tiny/library/source receipts, then actual full
FrozenBank/ContextBank readers and explicit consumer admission. It hardlinked the
existing eight bank files; no GPU wake/extraction, transfer, install, accepted tiny
fit or baseline replay. All three gates, train/embed/group/refine/export/graph-proof
and `PASS_E009_ONLY_COMPLETE` exit 0. One seed 11 / 20-epoch fit exposes all 89,041
parents each epoch and 432,664 views, with 86,708 positive-capable parents and all
ordered ten measured-depth columns. The 43-member f136b2c scientific package and
execution snapshot's 115 source/input bindings match; later governance/doc edits
do not alter the frozen run. Legacy whole-plan `science_completed=false` and
`planned_science_fits=2` do not change scoped success or imply oral execution.

Fresh held-parent supervision passed live/normal/crash tests; exit snapshot has
the same boot/PID/start ticks/command hash and requests shutdown. Provider confirms
original E2 TERMINATED at 14:24:13.903 UTC October 25. Original MIGRATE, STOP 6,300 s,
no automatic restart, security/metadata/service identity and 30/300 GiB disks are
restored unchanged. Temporary L4 worker and both 40/64 GiB disks were deleted only
after bank/runtime/model/journal preservation and actual CPU reader admission;
independent lists confirm absence. No quota or service expansion occurred here.

### Evidence, resource and cost closure

Private final prefix:
`gs://dl-binner-archive-167650584170/e021/portable-20261024T190419Z/cpu-E009-recovery-v7/`.
`completion.json`, `watchdog-exit.json`, `collection.json` and archive/checksum are
retained. Final archive: **98,377,566 bytes**, SHA256
`b99cbcb6c162e109b7be33f3499c509c35c1a7b14f658e4f9916007bdf7aae38`;
all **109 members / 258,370,418 logical bytes** plus exact-byte alias pass locally.
Prior v6 GPU/v5 CPU archives have 44/34 verified members. A separate
[inspection backup](inspection-backup.json) preserves 30 compact members, including
the full independent new-output review, and passes GCS download/readback SHA256
(600,578 compressed bytes). Final documentation/summary additions are in Git.
The compact return omits
bulk GLM/context arrays and emitted FASTA; they remain on original CPU disk and
are not backed up merely by inventory hashes. The complete GLM bank and inert
CUDA runtime archive are preserved from the original handoff. Mac retains the
verified ten-file pinned model and all small failed journals. No full GPU OS backup
is claimed; deleted OS/download/duplicate staging was regenerable.

Local evidence root:
`artifacts/e021-portable-admission/20261024T183844Z/inspection-20261025T1320Z`.
New-output diagnostics use unchanged `scripts/e021_review.py`, retained native
vectors and conservative truth v2, without baseline rescoring or Mac inference.
First local attempt verified/extracted the archive then failed because sandboxed
`ps` was denied, before diagnostics. Second used the same original review clock:
31.34 s child, 335.73 s cumulative wall, 1.448 GB sampled RSS, 392.31 MB peak extra.
Both journals remain. Numerical threads are four; original Mac allclose remains
failed at its unchanged tolerance. [Summary code](journals/summarize-e009-inspection.py)
only joins already evaluated rows and receipts; it launches no scientific work.
[Closeout checks](journals/closeout-checks.json) retain 39 passing local operational
contracts, exact target/accounting reconciliation, documentation and whitespace
checks. Ten unavailable optional source caches are explicitly not reverified.

CPU recovery allocation was **29.02 minutes**, including setup/collection/idle,
not the 19.51-minute training child. All six CPU stages took 22.83 minutes with
3.791 GB peak sampled tree RSS; sampled CPU seconds are separate from charges.
Original failed consumer plus recovery use 53.64 minutes of the four-hour allowance.
Whole phase: **8.239 GPU hours / 2.996 E2 hours**; extraction child 4.140 hours,
plus admission/setup/handoff idle. The same 48-hour clock began October 24 at
19:04:19 UTC; it was never reset. No budget, resource or retention increase.

Fresh October 25 Welcome credit is **DKK 1,808.22 / 92%**, January 12, 2027 expiry,
Certain usage / net pricing, delayed usage unknown / $35 reserve. Fresh official
Catalog rates match earlier ordinary E2/G2/L4/PD/IP pricing; retained-credit scope
covers the actual first-party products. [Credit terms](https://docs.cloud.google.com/free/docs/free-cloud-features)
and [Free Trial terms](https://cloud.google.com/terms/free-trial) were refreshed.
No real-money spending is authorized. Export was assessed before download.

| Priced measured component | USD |
| --- | ---: |
| GPU allocation + IP, including setup/idle | 7.0739 |
| E2 allocation + IP, including all recovery | 0.8181 |
| Temporary disks through verified deletion | 0.2633 |
| Original disk attribution, overlapping existing $8 approval | 0.8107 |
| All 9,036,044,288 stream bytes at conservative paid WAN rate | 1.0099 |
| All compact archive downloads at conservative paid WAN rate | 0.0157 |
| Subtotal | **9.9916** |
| Small GCS/control/network allowance + unmetered reserve | 1.6000 |
| Conservative total including reserves | **11.5916** |

These are allocation/storage/byte-priced estimates, not a billing invoice or a
credit-delta attribution. Recovery compute+IP adds ~$0.1321 inside original $45.
Temporary disk charges are stopped; original stopped disks remain $31.20/month.
Existing $8 storage approval still ends **October 28, 00:00 Copenhagen (CET)**;
no renewal is implied. No VM is running or awaiting a controller.

### Strongest next recovery decision

Choose one reliable marker-informed cross-contig learning block locally. Current
same-parent crops do not directly teach which distinct fragments belong together;
E021's modest, concentrated gain and persistent grouping loss justify adding
biological constraints before more GLM capacity/extraction or another threshold
grid. This is a hypothesis, not a proven cause. Reliability and abstention are
central: repeated-family hits alone cannot be hard negatives given accepted
E011/E012 locus/panel/replicon/duplication failures. Use label-free call/context
support, protect marker-negative DNA and retain original self-positive learning.

For retained whole-tool context, MetaBAT2 R95 is 8.5493% versus E021 7.8175%;
its native length eligibility differs, so this is not a matched-cutoff ablation.
No external score was recomputed. A zero-GLM control is a serious cheap attribution option, but is lower priority
unless its answer changes the next design: it does not itself connect fragmented
genomes. Bigger/fine-tuned GLMs and full oral extraction cost substantially more
without evidence capacity is limiting. Retain the optional E021 bank for future
CPU consumers; no new GPU campaign. New community runs require a separately frozen
comparator/data scope and budget. Skin remains unscored with its source/origin/
unique-support/overlap/evaluator/resource limitations; 313/610 exact inventory
overlaps with oral preclude unseen-genome claims. No confirmation or new score here.

---

All sections below, except the new Exact following prompt, preserve dated attempts.

**Owner has now approved the revised portable scope under the same remaining $45.**
[Approved policy](portable-policy.json) supersedes the pending-approval wording in the dated reassessment below.
Actual native preparation/execution must pass every gate; no new start at this source freeze.

## Historical decision after repeated capacity failures, October 24, 18 UTC

**Change execution strategy; no new job or resource mutation in this task.**
The owner reports repeated unavailability over hours; live operations confirm
four more failed starts after the original, last at 17:43 UTC. The VM is still
TERMINATED / E2 / no GPU, original protected resources unchanged. The [execution
strategy](execution-strategy.md) gives the verdict and [priced record](execution-strategy.json)
binds fresh credit/quotas/SKUs and actual restore-only tests. Old receipts remain
unchanged; their single-attempt status is a dated observation, not the cumulative
history of later owner actions.

Do not keep submitting the same N1/T4-a tuple as the ordinary development plan.
Do not replace full frozen GLM extraction with an unadmitted long CPU run. Keep
CPU as the regular learning/grouping path, and propose a short-lived extraction
worker with a fixed small placement list and immutable cache return. Exact
source/views/math/schedule/criteria and all populations remain fixed.

The proposed L4-b / L4-c / T4-f scope fits the **remaining original $45**, with
conservative maxima ~$42.70 / $37.17 including new temporary disks and charged
streaming transport. It needs explicit resource exceptions to the current
same-existing-VM authorization; no approval is inferred from having credit.
Fresh balance is DKK 1,865.13 / 95%, expiry January 12, unknown delayed usage/$35
reserve. Original $8 storage ends October 28 00:00 Copenhagen, without renewal.

Real installed Mac readers restored both original tiny GLM banks unchanged at
new paths and refused corrupt/overwrite cases. No GLM/Torch loaded or science
repeated. This supports cache portability only; it is not Linux/CUDA, full-scale,
SSH-stream or native-launch admission. The exact proposed owner approval is below.
The following admission/rollback section is the **preserved earlier snapshot**.

## GPU admission outcome, October 24, 2026

**Capacity blocked before guest boot; comparison not executed. VM independently
TERMINATED and restored to e2-standard-8, with no GPU.**
[Native observation](native-observed.json) owns the actual provider operations,
failures and rollback. [Prelaunch admission](gpu-admission.json) is a dated snapshot,
not proof of a native runtime or scientific completion.

The owner authorized **$45 gross, Welcome-credit coverage only** and the temporary
existing-VM N1/T4 configuration. Fresh signed-in credit was DKK 1,866.09 / 95%,
January 12, 2027 expiry; the post-attempt read is **DKK 1,865.82 / 95%**. Scope is
Certain usage / net pricing; >24-hour delayed usage remains unknown with a $35
reserve. Official paid-upgrade terms admit the retained credit for the specified
ordinary first-party N1/T4/PD/IP/GCS/network/operations products. This is not a
free-tier GPU claim, reconciled invoice, or attribution of the credit delta.
Conservative full-window quote remains **$39.23 maximum** within $45.

Global GPU quota was successfully raised **0 -> 1**, case
`c8d8dfd3-aa67-4fa1-aa68-37d19d2e841b`; regional T4 limit is also 1. Both final usages
are zero. Quota permission does not establish physical zonal capacity. The first
command was refused because ordinary E2 does not support TERMINATE maintenance.
The repaired order is stopped N1 type -> maintenance/STOP -> ordinary T4 attachment.
That configuration passed exact disk/security and **173,700-second STOP** readback.
One start request then failed with **ZONE_RESOURCE_POOL_EXHAUSTED**: no
n1-standard-8 + one T4 capacity in us-central1-a. It did not reach RUNNING; the
last successful start remains October 23. No zone, accelerator, VM, disk or
retention substitution and no repeated start request followed.

Rollback removed the T4, restored original MIGRATE / no restart / 6,300-second
STOP scheduling, then restored E2. An initial CLI operation-wait helper failed
because that subcommand is absent; the submitted GPU-removal operation itself
succeeded. The repaired helper reads the already submitted operation rather than
resubmitting it. Independent final control reads prove original 300 GiB balanced
work / 30 GiB standard boot disks, Secure Boot/integrity/vTPM, metadata, service
accounts, network configuration and enabled services unchanged. Both failed
helpers/journals remain. No guest SSH, package/driver install, model transfer,
science, native watcher, completion or science-return archive exists for this
attempt. This is **NOT EVALUATED**, not a failed biological criterion.

The original **f136b2c** candidate / 115 bindings and 43 package source members stay
unchanged. [Operational lock](gpu-launch-lock.json) freezes the new 48-hour parent,
14 GiB device monitor, 13 GiB Torch allocator cap and 32 GiB extra-space envelope.
**Eight local operational contracts pass**, including the real CSV/clock guard,
with explicit telemetry doubles, exact command order and submitted-operation
readback. These are not native CUDA/systemd proof. [Native plan](gpu-native-plan.json)
still requires a complete independently owned compatible Python/CUDA recipe,
hash-pinned author float32 attention, separate prospective CPU/GPU numerical gates,
real tiny scientific paths, actual resource/throughput/return admission and a fresh
boot/process watcher before release. Old Mac failures/tolerances stay unchanged.

No files were deleted and no storage increase was requested. Actual local free
space exceeds 22 GiB. Last accepted guest work free was 63.05 GiB; it is **not** a
fresh guest measurement. Before installation, require actual root/work df and old-file
du, 57 GiB work headroom (32 GiB cap + 25 GiB reserve), and safe cleanup review.
The provider GPU guide directs checking a boot disk of at least **40 GiB**, while
the authorized original is **30 GiB**. Configuration acceptance is not proof of
boot/driver suitability. Resolve the actual signed-driver/root-space contract
without silently resizing or disabling Secure Boot; report a concrete incompatibility
if it cannot fit. Full CUDA runtime belongs on the existing work disk, not a full
toolkit on boot. No claim of native readiness follows from quota or source tests.

Expected new CPU/GPU allocation **$0** (no successful boot / RUNNING interval),
science/export **$0**; small control-read operation allowance is recorded separately.
Original stopped disks remain **$31.20/month**, about $1/day. The separately approved
$8 storage forecast remains ~$7.63 and ends **October 28, 00:00 Copenhagen (CET)**.
No storage was extended and no new cloud object uploaded. The compact checksum-
verified [local admission seal](gpu-inspection-seal.json) contains control evidence,
not science; omitted raw snapshots are retained locally and not backed up by hashes.

**Strongest next decision:** complete admission of this same frozen candidate when
same-zone capacity is available. A provider refusal gives no reason to change the
model, substitute a costly CPU run or acquire more data. All Linux/resource gates
remain. Full 48.25-hour window must start before **October 25, 23:45 Copenhagen
(CET, UTC+01:00)**, with preparation margin; recheck the absolute retention epoch
and fresh billing before any later attempt. No automatic loop, alternative resource,
new budget, retention extension or capacity-monitor automation is authorized here.

The following is the **preserved October 23 local-implementation snapshot**.

**Local hybrid implementation and five-file skin admission complete. No community
extraction, fit, score or VM start.** This invokes E020's following prompt under
the owner's added conditional VM authorization. The owner allowed this task to
choose whether execution should wait. **Wait for native GPU/resource admission:**
credit balance passes, but complete Linux runtime, throughput, full-scale RAM,
20 GiB working-space and local return/review gates do not pass. Starting the E2
would spend before establishing an affordable complete job.

[Design](design.md), [protocol](protocol.json), [candidate lock](candidate-lock.json),
[local evidence](local-evidence.json), [skin admission](skin-admission.json),
[confirmation plan](confirmation-plan.json) and [resource plan](resource-plan.json)
own the exact contracts. Immutable E019 and all accepted E009–E020 science remain.
The owner’s pre-existing edit to E020 operations is preserved; it is not silently
replaced by the older no-VM wording.

## What actually works

Dev8 adds `hybrid-stage extract/train/embed`, separate from existing product and
historical stage algorithms. The exact E002/E003 DNABERT-S model/tokenizer/custom
sources are read-only. Parent and every available retained crop use their own DNA,
both strands, canonical orientation, nontruncated chunks and attended-token/bp
pooling. An indexed float32 cache records every ID, crop coordinate/DNA hash and
mask; partial/corrupt banks are refused. It never substitutes parent vectors for
crops. Parent-only fitted GLM normalization, a compact gated residual and E019's
explicit context/composition/measured-parent-depth branches preserve the learning,
EMA/predictor/reconstruction and unit geometry anchors. The gate is not calibrated
confidence. No backbone tuning, marker training, taxonomy or ensemble.

Pinned author `bert_layers.py` lines 161–186 reveal that optional Triton attention
casts float32 inputs to fp16. The adapter explicitly selects the author's existing
Torch float32 reference path after verifying every source hash and all 12 layers;
it does not edit the model source or add placeholder modules. The old CPU recipe
already followed that path. Actual same-platform cached parity is checked exactly,
without widening the original failed Mac portability tolerance. Linux/CUDA remains
unadmitted; choosing this branch does not establish GPU compatibility or speed.

Actual synthetic DNA extraction, native Pyrodigal/PyHMMER, two 20-epoch fits,
exact reload, sparse CPM graph, E013 refinement and complete pre/old/post export
pass in a serial 15-job DAG. Names `E009-hybrid` and `oral-hybrid` in that tiny DAG
refer to synthetic fixtures, not community runs. There are 39 original records,
36 eligible parents; excluded/ambiguous/short DNA remains accounted for. The
extraction exposes 171 exact views / 118,536 bp / 55,618 forward tokens / 177 chunks.
It takes 114.71 seconds; the full tiny DAG takes 150.71 seconds and peaks at
1.210 GB sampled tree RSS. Final online fused effective ranks are 2.6192 with
synthetic depth and 3.1322 sequence-only, above unchanged guards. This is engineering
stability, not recovery evidence. The synthetic marker panel is not the community
marker asset; that original asset is separately hash locked and not redetected.

The final wheel is tested outside the checkout in a complete independently owned
Mac Python 3.10.15 numerical prefix, with actual installed console entry point,
isolated tensor/graph/marker library groups and bounded pools. Wheel, sdist and
fresh sdist-rebuilt logical contents are checked. Cache unit fixtures mock only the
external extractor; real model extraction is independently exercised. The collector
is exercised on actual tiny outputs with exact aliases, every member/readback and
explicit omitted full-GLM/DNA inventory. Its compressed writer enforces 2 GiB before
overshoot, including the gzip footer; logical members including the inventory are capped at 6 GiB, and the manifest
itself at 64 MiB. A hash
of omitted native bytes is not a backup. Full community evaluation/review adapters
have no E021 community output to validate yet.

The local evidence record names final test counts, runtime identities, full logs,
resources and successful/failed attempts. Failures are preserved in [journals](journals/README.md),
including fixture/config refusal, entry-point/owned-runtime corrections, headerless
publisher-map parsing and sandbox process-monitor refusal. No failure is relabeled
as a pass. The metadata helper's mistaken old-E020 destination was repaired:
accepted E020 sealed receipt bytes were restored and every original binding
reverified; new observations live under E021. No old scientific artifact changed.

[Local compact evidence seal](local-inspection-seal.json) preserves the implementation,
compact local proofs and failed journals with every member verified. It excludes
DNA, bulk caches, model weights, environments and credentials; no private upload.

## Skin source and truth admission

All five frozen files total **4,605,403,023 bytes**; fresh HEAD, publisher MD5 and
new whole-file SHA256 pass. Transfer takes 1,949.15 seconds under the original
four-hour acquisition/validation clock. No reads, BAMs, new reference collection
or source-collection extraction. SQLite/indexed streaming verifies every GSA,
anonymous ID, corrected map, raw-map historical alternative, source locus and
sequence without clipping or invented circular aliases. The publisher's skin
samples are **1,13,14,15,16,17,18,19,20,28**, distinct from the oral sample indices.

There are **753,143 contigs / 1,527,051,918 bp**, no original zero-bp records,
**610 positive cellular targets / 1,740,112,046 full reference bp**, including
one zero-origin target. All **1,394 provided genomes / 2,394 records /
4,266,674,864 bp** remain competitive references. Raw and exact-DNA-deduplicated
within-genome denominators agree. All historical domain joins are bacterial;
source filenames, records/replicons, simulated genome IDs and taxon nodes remain
separate. Molecule/host annotations are incomplete, so no biological host or
circular-alias inference is admitted. A source-blind FASTA and external reverse
join are produced; neither truth nor source IDs enter training.

Independent full-byte/row review admits only **CAMI-II-HMB-skin-provided-origin-
oracle-v1**. Every non-ACGT base is localized and quarantined (**1,427 bp**), with
full reference denominators; **67 known-shared queries** retain a prospective
masked sensitivity (forward-query or canonical-complete-reference duplicates;
reverse-complement substrings and near alternatives are not exhaustively searched). Unique competitive/near-homology support is unadmitted.
The raw origin union is data availability, not a binner score. GSA has no assembly
errors and no measured pooled-contig depth. No skin model extraction, fit or score.

**313 of 610** positive skin genomes have exactly the same full provided record
DNA/length inventory as a genome observed in oral GSA; 314 match admitted oral
targets, and 359 match the entire retained gastrooral reference pool. A bounded
motif-anchored 32-mer screen finds additional shared sequence; it is not ANI,
exhaustive near-overlap or absence evidence. The other 297 are not proven unseen.
Historical GLM/panel inventory and broader near-overlap remain incomplete. Skin
can test a new community setting, not unseen-genome transfer. The original skin
choice is preserved, with all 610 primary targets and predeclared 313/297 strata;
no replacement dataset is selected after this audit. A real tiny skin evaluator
adapter and separate confirmation execution/cost admission are still required.

## Cost, storage and why execution waits

Fresh paid-account Credits shows **DKK 1,871.23 Available / 95%**, Certain usage /
net pricing, expiry **January 12, 2027**. October 1–23 costs/savings display DKK 101,
net zero; usage can arrive more than 24 hours late and a **$35 delayed-usage reserve**
is retained. The account-local Catalog observations include actual E2, N1 and T4
SKUs. Coverage for a future GPU must still be established; paid upgrade or a listed
GPU price alone does not prove its credit eligibility. No credit delta is an invoice.

The VM remains **TERMINATED**, existing e2-standard-8 / 32 GiB, 300 GiB work and
30 GiB boot. No cloud job, write/upload, type/quota/service/IAM change or retention
extension occurred. New cloud compute is **$0**; public local download adds **$0 GCP**.
Metadata reads remain tiny operations, not a claimed reconciled zero invoice.
Existing stopped disks cost **$31.20/month** at conservative marginal prices;
current listed versions are 104 objects / 9,384,180,741 bytes. The original separate
**$8 storage interval ends October 28 at 00:00 Copenhagen (CET, UTC+01:00)**,
forecast about **$7.63**. No automatic renewal/deletion. New native raw GLM caches
would live on the already provisioned disk, but a new return object's retained
bytes/operations must still fit that storage approval. Run-disk attribution is
part of that interval, not a second disk bill.

Two communities have 597,804 eligible parents and about **2.244–3.242 billion exposed
bp** including retained crops. GLM arrays alone require **9,350,150,516 bytes /
8.708 GiB**, including axes/quality/masks. Same-Mac tiny linear projection is
444 parent-only hours / 603–871 full-exposure hours; this is a warning, **not an E2
or GPU runtime estimate**. Batching/token length and hardware change throughput.
Do not reject the information family solely on that projection.

A conditional CPU ceiling of **$25 / 72 hours / 72.25-hour STOP** prices financially,
but native throughput/RAM are unadmitted and predicted total growth is about
**19.5–23.0 GiB**, above the 20 GiB cap at the upper end. The current local task is
also near its 10 GiB total-extra allowance; a 2 GiB compressed return plus 2.2–4.5 GiB
sequential review would need its own bounded scope. These failed gates are sufficient
to defer, despite ample credits. No CPU phase was released.

Recommend a **separate GPU resource/native admission block**, then this one frozen
comparison if its gates pass: temporarily use the same VM as n1-standard-8 /
30 GiB plus one T4 / 16 GiB, original disks unformatted. At current conservative
marginal SKUs this is about **$0.735/hour compute/GPU/IP + $0.04194/hour disks**;
48.25 hours plus 2 GiB export, operations and $1.50 execution reserve is about
**$39.23**, so propose a new **$45 ceiling**. This is an upper-envelope planning
quote, not observed cost or guaranteed runtime. Global GPU quota is **0**, regional
T4 quota is 1; quota >=1 and available capacity are prerequisites, not proof that a
new VM/service is required. No quota request or type/GPU change was made here.

Propose four CPU threads, 26 GB sampled host RSS, 14 GiB GPU memory, 32 GiB new work,
25 GiB free reserve, 2 GiB compressed/6 GiB logical return and 6 GiB extra sequential
local review; last accepted VM free space is 63.05 GiB, not a fresh guest measure.
The 48-hour cumulative setup/verification/extraction/head-fit/group/collection/upload
clock and 48.25-hour independent STOP must end before the existing storage deadline.
Prepare and test that new launcher envelope before start; the current CPU template
is not an already validated GPU launcher. Complete Linux/CUDA/model imports,
prospectively fixed tiny CPU/GPU numerical checks, full-size RAM/VRAM/space and
measured throughput must pass before community release. Do not promise all tokens
fit or that a tiny 1.21 GB RSS result bounds full-community memory.

[Official trial terms](https://docs.cloud.google.com/free/docs/free-cloud-features),
[ordinary GPU pricing](https://cloud.google.com/products/compute/gpus-pricing?hl=en)
and [GPU regions](https://docs.cloud.google.com/compute/docs/regions-zones/gpu-regions-zones)
were checked October 23; account-local SKU/quota/credit evidence is hash-bound in
the resource/local records. Capacity and GPU-specific credit coverage remain fresh
gates. Original E019 mixed evidence and E003 failed short-neighbor criterion remain.

## Authorized GPU execution prompt (invoked October 24)

The owner has invoked this **new $45 credit-only resource/execution authorization**.
It is not an old budget carry-over and must not trigger another approval request
for actions already covered here. No scientific run is inferred from authorization. The strongest next
step is native affordability/admission of this frozen candidate, followed by its one
development comparison if viable; no further architecture/grid before that evidence.

Our goal is substantially closing the recovery gap. Read AGENTS.md, PROJECT_INTENT.md, STATE/CLOUD, D013/D015 and E021's design, prospective protocol, candidate/reuse locks, local evidence, skin admission, confirmation plan, resource plan and operations. Preserve dev3/dev4/dev5/E016/E019 and all accepted E009–E021 data/truth/results/source freezes and failures. Use the prepared E021 branch and exact clean commit, without a codex/ prefix.

I authorize preparing/testing a GPU-native envelope and, only after fresh credit/product/quota/runtime/storage/throughput gates pass, the single frozen E021-versus-preserved-E019 two-development-community comparison under a new $45 incremental gross ceiling covered entirely by remaining Welcome credits. I explicitly authorize requesting global GPU quota >=1 and temporarily changing only the existing stopped Iowa VM to n1-standard-8 / 30 GiB with one ordinary T4 / 16 GiB, original 300 GiB work and 30 GiB boot disks without formatting. No new VM/disk, service/IAM expansion, resource grid or retention extension. Verify GPU SKU coverage rather than inferring it from paid billing or Free Tier rules; stop before unclear/uncovered cost. Restore its E2 configuration after independent stop and record all mutations. If capacity/quota/runtime or completing before October 28 at 00:00 Copenhagen fails, do not substitute another resource or extend retention automatically.

Use four CPU numerical threads / zero loader workers, 26 GB sampled host RSS, 14 GiB GPU memory, 32 GiB maximum extra work, 25 GiB free reserve, 2 GiB compressed/6 GiB logical export and a fresh 6 GiB sequential local-review allowance after physical headroom checks. Count every setup, verification, extraction, two head fits, grouping/refinement, collection/upload/readback minute from VM start inside 48 cumulative hours; provider STOP at 48.25 hours, earlier than original storage expiry. First update/test the prepared CPU phase to this explicit envelope and capture the exact Linux/CUDA recipe; do not simply release the old CPU template. Refresh Welcome balance/scope/expiry, delayed usage/$35 reserve, applicable compute/GPU/disk/network/operation prices, quotas/capacity, original $8 storage balance and actual disk/return/local-review headroom before cost-bearing changes.

Push the exact clean branch from Mac and sync VM read-only. Verify original model/tokenizer/custom-source, retained E019 features/crops/context/marker assets, full contig/sample axes, source/wheel/default bytes and no truth path. Reuse accepted science without recopy/reinstall fallback. Create a complete independent compatible Linux/CUDA runtime, test actual imports/library origins and the pinned author's float32 reference attention; no placeholder modules or silent fp16. Freeze CPU/GPU tiny numerical tolerances before running them; retain the original failed Mac allclose and do not alter native vectors. Run real tiny exact-view extraction/cache/gradient/EMA/noncollapse/reload/geometry/CPM/marker/refiner/full-export/collector gates. Measure representative admitted throughput, RAM/VRAM and projected complete peak disk/return/time before release; partial extraction cache is not automatically resumable. If it cannot fit, collect/stop/report without beginning an unaffordable community DAG.

Arm/test a fresh current-boot/process held-parent exit watcher and independent provider STOP before release. Run the one fixed E009 ten-depth / oral sequence-only E021 DAG, all exact parent/crop DNA and frozen schedule, ordinary sole CPM/E013 uniformly. Reuse E019 and all older summaries without refitting/rescoring; no skin features/fit/score, new data/mapping/aligners/external binner, ablation, threshold/grid, model change or retention extension. Retain native full GLM cache, features/embeddings/pre/old/post/accounting and every failed journal; explicit omitted-byte inventory is not backup. Debug recoverable operational errors with fresh attempts and verified reuse within the same clock/budget; never silently replay accepted science or extend.

If healthy and long, verify fresh supervision and real scientific progress, wait a few minutes then report stage/logs and finish rather than polling to completion; follow a <=15-minute job through collection. Collect on failure/limit, stop and independently verify TERMINATED. After successful shutdown verify completion, archive/member/alias bytes and allocation/storage/export cost before bounded local frozen E009-v2 and separately named oral provided-origin diagnostics. Keep all 156/799 full denominators, 3.3034% E009 N-quarantine, oral known-shared sensitivity and every length/origin/eligibility/marker/unknown/non-target/excluded/unassigned population. Apply original keep/modify/abandon criteria unchanged. This is a development bundle, not causal isolation or SOTA/feature-family proof. Skin remains unscored, with its 610-target origin-only/overlap limitations and separate evaluator/compute/retention admission. Update records/check/commit with structured what changed/why; report measured resources/costs, results/limits, one next strongest decision and exact next prompt.

## Prior same-resource continuation, superseded as the recommended next step

This preserves the earlier bounded authorization. The owner's later repeated-
capacity concern prompted the strategy above; it does not authorize new resources.

Continue E021 under the existing October 24 $45 credit-only authorization. Read
AGENTS.md, PROJECT_INTENT.md, STATE/CLOUD, D013/D015 and E021's native-observed.json,
local admission seal, original f136b2c candidate/protocol/criteria/reuse locks,
GPU operational lock/native plan and operations. The prior single start request
failed with ZONE_RESOURCE_POOL_EXHAUSTED before boot. Global/regional T4 quotas
are 1, usage 0; the VM is TERMINATED and restored to E2. Preserve both operational
failures, every accepted source/input/result and the original Mac tolerance.

Refresh live credit/scope/expiry/delayed usage, eligible SKUs/prices, the original
$8 storage interval and physical/local return headroom. Finish and test the exact
native bootstrap/runtime/gate/release tools before scientific release; a planned
Python/CUDA recipe is not an installed admission. Push the exact clean branch
from Mac and use the existing read-only VM Git key. Make one fresh recorded
same-existing-VM/us-central1-a N1-standard-8 + ordinary T4 capacity attempt only
when the whole original 48-hour clock / 48.25-hour STOP can end before October 28
00:00 Copenhagen. Start before October 25 23:45 CET with preparation margin.
No new VM, zone, accelerator alternative, disk increase, service/IAM change,
reservation, automatic capacity loop or retention extension. If capacity still
fails, independently confirm TERMINATED and restore original E2/scheduling.

On successful boot, capture actual root/work free space and old-file inventory
before installing. Resolve the provider 40 GiB boot guidance versus original
30 GiB disk using a documented signed-driver/root-space admission; do not silently
resize or weaken Secure Boot. Clean only proven disposable, unneeded files after
recording their identities; preserve accepted evidence and required inputs.
Verify source/model/tokenizer/custom-code/input/full-axis/runtime bytes without
reinstall/recopy fallback. Arm/test the fresh held-parent current-boot/process exit
watcher and independently verify 173,700-second provider STOP. All setup/gates and
science remain within 48 cumulative hours / $45, four numerical threads / zero
loaders, 26 GB host RSS, 14 GiB device, 32 GiB new work, 25 GiB free reserve,
2 GiB compressed / 6 GiB logical return and 6 GiB sequential local review.

Only after real Linux/CUDA float32 attention/parity, tiny extraction/cache/gradient/
EMA/noncollapse/reload/geometry/marker/CPM/E013/export/collection and representative
full-stage throughput/RAM/VRAM/space/return gates pass, release the original sole
E009 ten-depth / oral sequence-only frozen comparison. Reuse E019/older summaries;
no baseline refit/rescore, new grid/loss/model, skin work, data/mapping/aligner or
external tool. Debug operational errors within the same original clock/budget
with verified reuse and fresh journals; never repeat accepted science implicitly.
For a healthy long job verify supervision/progress, wait a few minutes and hand
off without polling to completion; follow a short job through collection. On
failure collect, stop/verify and restore E2. After successful shutdown verify
archive/members/aliases/costs before the frozen diagnostics, full 156/799 reference
denominators, N-quarantine and every population. Update records/check/commit with
structured what changed/why; report actual status/costs/limits, one next strongest
decision and exact following prompt. Stop before unclear or uncovered spending.

## Prior portable resource approval, executed October 24

**Proposed resource-scope approval, not effective yet.** The current authorization
says “No new VM, zone, accelerator alternative, disk increase”. This request changes
those explicit resource restrictions while keeping the remaining original $45,
scientific scope, credit-only condition and October 28 boundary. No new budget or
permission to repeat accepted science is requested.

Our goal is a substantially stronger binner without a recurring GPU-placement
bottleneck. Read AGENTS.md, PROJECT_INTENT.md, STATE/CLOUD, D013/D014/D015 and E021's
execution-strategy.md/json, prior native/failed receipts, original f136b2c source/
candidate/protocol/criteria/reuse locks and operations. Preserve every accepted
source/input/truth/output, original Mac failure/tolerance and all failed journals.

I approve the revised E021 resource scope under the REMAINING original $45 gross,
Welcome-credit-only ceiling. Permit one temporary extraction worker in this fixed
capacity order: g2-standard-8 + ordinary L4 in us-central1-b; then the same in -c;
then n1-standard-8 + ordinary T4 in -f. At most three sequential placement attempts,
at most one worker present and one successful science execution. Only capacity
rejection before science permits the next placement; no quality/numerical/grid
selection or automatic loop. Allow its 40 GiB boot + 64 GiB work disks: balanced
for G2, standard for T4. Allow balanced quota >=404 GiB if needed, after fresh
space/old-file review. Keep the original E2 VM and 30/300 GiB disks unchanged;
no detach/format/resize, no new service/IAM/public listener, credential copy,
reservation, Spot/DWS, Marketplace/vWS or other provider spend.

First prepare and locally test/freeze the actual selective input transport,
complete-bank restore-only consumer and bounded GPU-extraction/CPU-consumer
launchers. The current strategy and Mac relocation proof are not those launchers.
Use exact science/wheel/model/default bytes and original six extraction inputs;
no regenerated views, markers, neighbor inputs or baseline fits. Source transfer
must not copy SSH/GitHub credentials. Preserve the float32 reference path and
predeclared CPU/GPU tolerances, including on L4; no quantization/fp16/TF32 or new
backbone. Test actual readers/writers, safe fresh/failure/resume layouts, partial/
corrupt refusal and complete-axis/DNA export. Missing accepted bytes must refuse.

Refresh paid-account Welcome balance/scope/expiry, unknown delayed usage/$35
reserve, all eligible compute/GPU/disk/network/operation prices, quotas and the
original retention. Before provisioning/requesting storage, a bounded inventory
of the original node must measure df/du and assess safe disposable-file cleanup.
New disks are for placement compatibility; do not grow the original disk. Stop
before unclear/uncovered or >$45 spending. Proposed maxima ~$42.70 L4 / $37.17
T4 are not measured speed or a passing native gate.

Use the existing E2 for verified staging and later CPU learning/grouping; use the
worker only for exact parent/crop frozen extraction. Permit <=20 GiB total bounded
encrypted bulk transport, source-node -> Mac -> worker and worker -> Mac -> original
node, without bulk Mac retention, plus original <=2 GiB compact science evidence;
price <=22 GiB total outbound. Retain fixed small buffers, every byte/member/axis
receipt and a tested restore-only return. Do not silently classify WAN traffic as
free internal traffic. Keep original 6 GiB logical evidence / 6 GiB local review.
Avoid large bucket staging/soft-delete retention tails. Preserve complete caches
and necessary runtime/source/log payloads on the original node before deleting
only authorized disposable temporary copies/resources; do not delete the only
accepted copy or extend storage implicitly.

All starts/setup/quota wait/verification/transfers/extraction/two CPU head fits/
group/refine/export/collection/upload/readback share <=48 hours from the first
VM start, independent provider STOP <=48.25 hours and before October 28 00:00
Copenhagen. GPU running <=38 hours / STOP <=38.25; original E2 running <=8 hours /
STOP <=8.25 across boots, all also bounded by the original common absolute deadline.
Do not reset a clock on restart or admission failure. Four numerical threads,
zero loaders, 26 GB sampled host tree RSS, 14 GiB device / 13 GiB allocator,
32 GiB aggregate extra work across both nodes including staging/runtime/coexisting
copies, and 25 GiB free reserve on each remain. Verify measured peak space/time/
throughput/full RAM/return before science; stop if the complete work cannot fit.
Arm/test fresh boot/PID/start/command held-parent exit watchers and provider STOP
on each relevant boot before release. Inspect the real GPU/driver/Secure Boot,
complete independently owned runtime/import/library/source/CLI, CPU/GPU parity,
native tiny extraction/cache/gradient/EMA/noncollapse/reload/geometry/CPM/marker/
refiner/export/collection paths. Restore original-node prerequisites without
altering accepted environments. Every operational recovery needs fresh journals
and verified reuse inside this same clock/budget; never replay passed science.

Only after all gates pass, run the unchanged E009 ten-depth / oral sequence-only
E021 candidate and fixed CPM/E013, on full axes/all DNA; truth stays outside
features/training. Reuse E019 and older summaries without refit/rescore. No new
data, skin features/fit/score, mapping, aligner, external tool, ablation/grid,
model/default/threshold change or retention extension. For a healthy long phase,
verify current supervision/progress, wait a few minutes, report and hand off;
follow a short phase through collection. On failure collect, stop and independently
confirm TERMINATED, retaining failures. After completion verify cache/compact
archives/members/aliases and actual allocation/storage/export costs before frozen
E009-v2 / oral provided-origin review, all 156/799 full denominators, N quarantine,
known-shared and every length/origin/eligibility/marker/excluded/unassigned population.
Apply the original criteria without tuning. Update records/check/commit with
structured what changed/why and report actual status/costs/limits, one next decision
and exact following prompt. Keep the October 28 storage review visible.

## Current E009-only execution amendment

The owner authorized considering E009 alone after the complete native L4 probe
forecast 69.92 GPU hours for both communities. Adopt the
[E009-only prospective protocol](E009-only-protocol.md), preserving full exposure
and all original scientific settings. Oral accounts for 61.05 conservative GPU
hours versus E009 8.37; adding original I/O gives E009 8.87 hours.
Original f136b2c science, clean native 26374b7 and failed attempts stay immutable.
The owner-approved [20 E2 / 30 GPU time reallocation](allocation-reassessment.json)
supersedes the historical 8 / 38 wording. No new budget or clock reset.
The next exact inspection prompt will identify the actual released attempt.

## Exact following prompt

Our goal is substantially closing the recovery gap with coherent upgrades and
selective controls. Read AGENTS.md, PROJECT_INTENT.md, STATE/CLOUD, D013/D015,
the completed competitive/source/thesis reviews, E011/E012's marker-locus/call
and training-view audits, and E021's completed E009-only comparison, target table,
inspection/cost records, immutable locks and operations. Preserve dev3/dev4/dev5,
E016/E019/E021 and every accepted E009–E021 input, truth, output, source freeze and
failed journal. Use a new descriptive research branch without a codex/ prefix.

Implement and locally test one coherent reliable marker-informed cross-contig
learning candidate. The problem is that same-parent positive views provide no
explicit same-genome connection between distinct contigs, while E021's modest
R95 gain remains concentrated and high-recovery counts regress. Reuse retained
marker calls/genes/domains/locus audits, real parent/crop features, measured-parent
depth, context and optional frozen GLM banks; do not extract GLM DNA again. Keep
CPM/E013 as the provisional downstream anchor for this block, rather than tuning
another grouping grid. A larger network is not the objective.

Use judgment and targeted primary-source checks to resolve one label-free
reliability, cross-contig constraint and learning rule before changed outcomes.
Repeated marker families alone are not cannot-links: distinguish partial/overlapping
calls, independent loci, panel/lineage specificity, replicons and assembly duplication.
Use composition/depth/context to support or withhold constraints; abstain when
insufficient. Avoid reinforcing graph errors as certain positive labels. Keep
marker-negative, short, unknown/non-target DNA and optional unassigned outcomes;
truth/source identities must not choose pairs, thresholds, families, K or training
inputs. Do not invent measured window depth/variance, taxonomy labels or coverage.
Retain the original self-positive/full-parent exposure unless a prospectively
justified treatment requires a change; document initialization/RNG and missing-
modality behavior. Cached E009 GLM use does not establish oral sequence-only
transfer. Choose the immutable comparator and supported data scope prospectively.

Record a concise prospective design, serious alternatives, source/default locks
and keep/modify/abandon criteria, then implement in this task. Run actual tiny
reader/reliability/pair-selection/loss/gradient/train/reload/geometry/marker/
refinement/export and complete-DNA contracts. Keep features, pair evidence,
embeddings and pre/post alternatives for selective later controls. At most one
additional ablation should be prepared if it can change the design; no compulsory
grid/factorial or isolated win required for every ingredient. Preserve failures
and original Mac portability tolerance; distinguish actual versus mocked paths.

This prompt authorizes local implementation and bounded tiny engineering only.
Do not fit/score communities, rescore accepted baselines, run external binners,
acquire/map DNA, start/provision cloud resources, change hardware or extend storage.
Prepare the first bounded candidate-versus-immutable-anchor execution, using
retained CPU-readable caches where appropriate. Measure/estimate complete setup,
fit, RAM, peak disk, collection/export/review and cost, with fresh credit/product/
retention gates and a separate exact execution-approval request. No old remaining
$45 or clock carries into new science. Keep original two-community E021 KEEP
unmet and both inspected communities marked development.

Keep frozen skin unscored. State its source/genome/replicon/molecule/host/circular/
taxonomy/overlap/pretraining/competitive ambiguity and provided-origin-versus-unique
truth limitations, unchanged protocol/evaluator and separate resource/cost admission
before confirmation; no new DNA now. Original stopped 30/300 GiB disks cost
$31.20/month and their existing $8 approval ends October 28 at 00:00 Copenhagen
(CET). Surface exact preservation/retention needs before that boundary; prepare a
priced owner decision rather than silently renewing or deleting accepted bulk.
Update records/check/commit with structured what changed/why; report what works,
remaining uncertainty, the matched scope/resources and exact next approval prompt.

## Superseded October 24 inspection prompt

Continue E021's owner-directed E009-only phase `portable-20261024T190419Z`.
Read AGENTS.md, PROJECT_INTENT.md, STATE/CLOUD, D013/D015, E021's E009-only
scope/protocol, allocation reassessment, portable-observed.json, original frozen
candidate/reuse/criteria and operations. Preserve all accepted science and failures.
Check the Mac handoff controller receipt/log under
`artifacts/e021-portable-admission/20261024T183844Z/continuation-v6`, existing L4 worker
`e021-portable-20261024-b` in Iowa b and original E2 `dl-binner-cpu` in Iowa a.
Check `e021-portable/status`, GPU `gpu-native-v6` and CPU
`cpu-E009-consumer-v5` completion/exit evidence under
`gs://dl-binner-archive-167650584170/e021/portable-20261024T190419Z/`.
Do not infer scientific success from shutdown or confuse legacy two-community
science_completed=false with the separately required E009 scoped target.
If healthy, report actual extraction/handoff/CPU stage and leave verified native
watchers/provider STOP intact without polling a long job to completion.

After independently verified shutdown, establish the extraction, actual restored
bank/context/runtime gates and every one of six E009 CPU exits, scoped target,
collection/upload/readback and watchdog outcome. Verify exact full axes/source/
seed/schedule/reload/geometry, retained native bank and every archive member/alias
before bounded frozen E009 conservative-v2 diagnostics on NEW outputs only.
Keep full 156 denominators, 3.3034% N-quarantine and all populations; reuse E019
and older summaries without refit/rescore. Original joint two-community KEEP
remains unmet; oral and skin were not run. No truth tuning or new comparison.

Refresh credit/prices before export or any assessed recovery; price actual
provider allocation, stopped disks and WAN bytes separately from sampled CPU.
Keep the same original $45 credit-only / 48-hour clock from October 24 19:04:19
UTC, approved 20 E2 / 30 GPU cumulative hours, all resource/return caps and
October 28 00:00 Copenhagen retention. No budget or clock reset. A missing
handoff may require bounded collection/consumer recovery within that original
allowance; assess it first, never repeat accepted extraction or fits. Preserve
verified cache/runtime/journals before deleting only the temporary worker/disks.
Restore original E2 scheduling after independently stopped. Do not resize,
provision, acquire DNA, run oral/skin/external tools or extend retention.
Update records/check/commit with structured what changed/why, report actual costs,
scoped results/limits and one next recovery-focused decision.

## Verified long-job handoff, October 24 22:49 UTC

Operational preparation 721c63f is committed/pushed; scientific native 26374b7
and f136b2c package/default/view locks remain unchanged. E009 extraction is
actually progressing in gpu-native-v6: 1,500 / 89,041 parents, 136 live device
samples, 1.96 GB device peak, 56.75 GB work free. Current parent/watchdog/UUID
contracts pass. E2 is TERMINATED; CPU bank/runtime readers and scientific fits
remain pending. The controller lives under continuation-v6; older controller
failure receipts in its parent directory are preserved history.

The fresh-runtime reuse repair creates actual boot/UUID readiness before arming
and verifies LIVE_NATIVE_TELEMETRY against the held PID. V5 was collected and
stopped before any science child when that receipt was missing; its 40 archive
members/checksum pass. Prior failed v4 has 113 members and passed CPU evidence
return has 180; every member was verified locally. No accepted science was replayed.

Priced allocation/storage/transport components through 22:47 UTC are about $3.48,
including ongoing GPU allocation, not a final bill. The maximum all-subcap quote
remains $39.11 inside the original $45 and current reserved credits. Original
stopped disks remain$31.20/month; temporary 104 GiB balanced disks are about
$0.014/hour until verified cleanup, all inside the unchanged October 28 review.

Legacy collector planned_science_fits=2 describes the original whole plan.
Legacy science_completed also covers both communities and stays false here.
Require the new scoped E009 target, actual six CPU exits and full accounting;
never present either legacy field as evidence that oral ran or a fit failed.

## October 25 verified handoff failure and restore-only recovery

Both machines are independently TERMINATED. The GPU scientific extraction and
full-bank reader passed; its completion is extraction-only, not a completed fit.
CPU inventory passed. CPU then failed parsing a queue JSON file before either
remaining gate or any scientific child was recorded. The later IAP 4003 was a
consequence of shutdown, not proof that the scientific work ran. GPU and CPU
archives and every member pass local verification (44 / 34 physical members).

The old controller opened a ready command file before dumping JSON. The new
regression reproduces that empty-file visibility; publishing a fully serialized,
fsynced sibling under an exclusive atomic ready name removes the race. Recovery
preloads every command before arming the parent. It reuses the original transferred
1.49 GB bank and 3.20 GB inert CUDA-runtime archive, preserving all old pending
receiver receipts. Three equal stream digests establish transport; a new receipt
and actual CPU FrozenBank/ContextBank readers establish consumer admission.

[Recovery assessment](recovery-assessment.json) prices only the remaining CPU
consumer, no GPU wake, recopy, reinstall, extraction or baseline replay. Of the
stricter original four-hour active consumer allowance, 24.62 minutes were spent;
3 hours 35 minutes remain, with provider STOP also reduced by that allocation.
The 48-hour wall clock still ends October 26 at 19:04:19 UTC. Original cumulative
20 CPU / 30 GPU hours, $45 credit-only ceiling, resource/export limits and
October 28 retention remain. Fresh Welcome credit is DKK 1,808.22 / 92%, January
12 expiry, with unknown delayed usage / $35 reserve. Ordinary existing E2/PD/IP/
network/archive products remain covered under retained-credit terms. Current
Catalog prices match the earlier rate: approximately $0.27305 per E2 hour with
IP; the remaining consumer's provider-limit compute maximum is about $1.05.

Reuse every verified successful stage. New gates verify retained archive members,
reused library/source identities, passed tiny receipts and actual bank/context
readers. Only then release the unchanged six E009 consumers once. Source, full
DNA/views/depth axes, seed/schedule, unit geometry and CPM/E013 remain frozen.
The new native scoped completion receipt records one fit; original two-community
science_completed remains false and the joint KEEP criterion remains unmet.
