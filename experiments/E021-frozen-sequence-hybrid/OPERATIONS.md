# E021 operations

## Current GPU admission, October 24, 2026

The owner authorized the new **$45 credit-only GPU admission and conditional comparison**.
[Admission](gpu-admission.json) verifies live paid-account Welcome credit **DKK 1,866.09 /
95%**, January 12 expiry, >24-hour delayed usage/$35 reserve, unchanged SKU quote
**$39.23 maximum**, and effective global GPU quota **1** after approved request
`c8d8dfd3-aa67-4fa1-aa68-37d19d2e841b`. Regional T4 quota is 1. No new service or IAM.
The original candidate at **f136b2c** and all 115 bindings remain unchanged;
[new operational sources](gpu-launch-lock.json) implement the approved 48-hour /
48.25-hour STOP / 32 GiB / 26 GB host / 14 GiB device envelope. Seven local operational
tests pass, with explicit sampler doubles; actual Linux/CUDA/systemd gates remain
unadmitted. [Native plan](gpu-native-plan.json) predeclares separate CPU/GPU
numerical tolerances, preserving old Mac failures. A 13 GiB Torch allocator cap
leaves headroom below the 14 GiB whole-device monitor; math/precision stay float32.

At this source-freeze point the VM is still stopped; no fit or GPU allocation.
Only the quota request changes external state. Next execute bounded native
admission after source push, exact clean read-only sync and provider STOP. Preserve
Secure Boot; use only matching-kernel Canonical-signed drivers, no security bypass.
Current local free space exceeds 22 GiB; last accepted guest free was 63.05 GiB,
not a fresh guest measure. Capture actual root/work df and old-file du before
installation. No cleanup or disk increase has been needed/requested. All current
runtime/temporary payloads count in 32 GiB; no deletion of required/accepted bytes.
The cloud GPU guide suggests >=40 GiB boot; the frozen boot disk is 30 GiB. Treat
actual provider acceptance, measured free root space and signed-driver needs as
explicit admission checks; do not resize or ignore a refusal. CUDA runtime is
planned on the 300 GiB work disk, without a full toolkit on the boot disk.

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

## Exact following prompt

Continue E021 GPU admission under the owner's existing October 24 $45 credit-only
authorization and all frozen limits. Read the current admission and native receipts
before acting; preserve f136b2c science and failed journals. Do not repeat a passed
stage or start another phase implicitly. If no native phase has started, finish
source/runtime/resource/watchdog gates and execute the authorized comparison only
when they pass. No new budget or retention extension is implied. Native launch or
inspection handoff will replace this generic continuation with its exact phase.
