# E021 execution strategy after repeated capacity failures

Dated October 24, 2026. This reassesses execution, not the frozen model or its
scientific criteria. [Observed facts, prices and proposal](execution-strategy.json)
own the numerical details. [Operations](OPERATIONS.md#exact-following-prompt) owns
the proposed resource exception; it is not yet authorized.

## Verdict

Stop spending development time on repeated identical `n1-standard-8 + T4` requests
in `us-central1-a`. **Keep CPU as the ordinary development path and use occasional,
placement-flexible GPU extraction with immutable caches. Do not make full CPU GLM
extraction the automatic fallback.** This changes the earlier same-zone-retry
recommendation after further evidence, without treating infrastructure as a
biological result or deciding whether GLMs belong in the product.

The owner's report of hours of failure is supported by four additional rejected
starts at approximately 14:54, 15:08, 16:15 and 17:43 UTC, after the original 14:10
rejection. All five report exhausted capacity. The existing VM is independently
TERMINATED / E2 / no GPU; original disk/security/network/metadata/scheduling fields
match. No new start or mutation was attempted during this reassessment. These
snapshots do not prove that every moment or other GPU pool lacked capacity.

Google's [availability guidance](https://docs.cloud.google.com/compute/docs/troubleshooting/troubleshooting-resource-availability)
distinguishes physical capacity from quota and says the error applies to the
requested resources, not all resources in a zone. Its remedies include changing
placement or configuration. The [location catalog](https://docs.cloud.google.com/compute/docs/regions-zones/gpu-regions-zones)
lists Iowa T4 in a/b/c/f and G2/L4 in a/b/c; that catalog is not a live reservation.
Another zone/model might also fail. We cannot promise uninterrupted GPU access.

## Why CPU-only is not the best response

Our compact composition/depth/window-context learner and grouping already run on
CPU. Accepted E019 used about **2.83 allocated VM hours** for both communities.
The E021 heavy component is a frozen 12-layer DNABERT-S extraction on every exact
parent/crop, not training that backbone. Raw arrays are **9,350,150,516 bytes**,
plus view provenance. Once admitted, they can support compatible downstream
learning/grouping changes without another GLM forward pass.

The existing own-DNA Mac measurement projects **603–871 hours** for full exposure,
roughly 25–36 days. This is **not native E2 timing**; stronger CPUs could differ.
At the same speed, present E2 plus disk rates imply roughly **$190–275**, rather
than a cheap, reliable completion inside $45 / 48 hours. A large CPU substitute
has no measured full-stage admission. We should not launch that gamble or silently
use fewer crops, another backbone, quantization, fp16 or a shorter schedule.

Cache reuse has precise limits. Exact DNA, IDs/order, available crop coordinates,
model/tokenizer/custom source, pooling and precision remain bound. New DNA/views
or extraction semantics need new declared features. Current `Bank` also binds the
complete hybrid policy, including fusion fields: not every future head change
will pass automatically. Explicit compatibility or depth-rebind admission must
preserve original manifests; a failed check must not invoke extraction silently.
End-to-end backbone tuning would need recurring GPU compute and is a different
future decision. No such addition is made now.

The actual installed Mac reader restored **both retained tiny native GLM banks**
at new paths with identical member bytes/arrays. It refused overwrite and an
intentionally corrupted copy. Original members stayed unchanged; neither Torch
nor the GLM loaded, and no fit/inference/score ran. This took 0.40 seconds / 34.3 MB
OS-reported peak RSS, four BLAS threads. It establishes path relocation only,
not Linux/CUDA, encrypted streaming, full-scale resources or native readiness.

## Proposed next execution, within the remaining original $45

Use **one temporary extraction worker**, keeping the existing E2 and accepted
300 GiB disk unchanged. Prefer `g2-standard-8 + L4` in `us-central1-b`, then `-c`;
if capacity is rejected, one final `n1-standard-8 + T4` attempt in `us-central1-f`.
At most three sequential placement attempts, no capacity loop, at most one worker
present and one successful scientific execution. Failover is for capacity before
science, not a response to fit results or a numerical criterion. A passed stage
must not be repeated. Native affordability and every scientific contract still gate release.

L4 is another eligible pool at a modest hourly premium, not a claim of better
availability or measured speed. [G2 specifications](https://docs.cloud.google.com/compute/docs/accelerator-optimized-machines)
give eight vCPU / 32 GiB / one 24 GiB L4. Preserve four numerical threads, zero
loaders, 26 GB host RSS, 14 GiB device use and the 13 GiB allocator limit. The
original author float32 path and numerical tolerances stay fixed on either GPU.

Both variants need a **40 GiB boot + 64 GiB work disk**. G2 needs balanced disks;
T4 can use standard disks for the sequential extraction-only worker. Current
Iowa balanced quota is 300 GiB, all used, so L4 needs **at least 404 GiB** total.
Global/T4/L4 GPU limits already show one each, usage zero. The original boot is
`pd-standard`, which G2 does not support; this is not a drop-in type switch.
A [zonal disk](https://docs.cloud.google.com/compute/docs/disks/persistent-disks)
cannot follow a worker into another zone. Cleaning old files cannot remove either
constraint. Do not resize, detach or reformat the original disks. Before requesting
or provisioning new storage, inspect actual original-node free space/old-file
inventory and preserve useful evidence; current 63.05 GiB guest headroom is only
the last accepted observation, not a fresh `df`.

Copy only the six required extraction inputs (**2,852,120,484 bytes / 2.656 GiB**),
the pinned model/wheel/source and a new owned compatible runtime. GPU extraction
does not need the 6.894 GB context token bank or marker/truth data. Restore complete
new GLM banks to the original node, then run unchanged CPU train/embed/CPM/E013/
export/graph checks there. Keep full source, cache, logs and pre/old/post partitions.

A bounded encrypted SSH/IAP stream through the Mac avoids copying credentials,
adding public listeners or placing bulk staging objects into the bucket's seven-day
soft-delete lifecycle. It is **charged WAN transfer**, not free internal traffic.
The proposed scope explicitly adds **20 GiB total bulk transport / 22 GiB total
outbound including compact evidence**, with small fixed buffers and no bulk Mac
retention. It does not silently enlarge the original **2 GiB compressed / 6 GiB
logical scientific return or 6 GiB local review**. Actual transport/restore and
full footprint/throughput need tested native admission before community work.

Use the original **48-hour common clock / 48.25-hour STOP maximum**, from the first
VM start including inventory, quota wait, setup, transfers, verification, extraction,
CPU fits and collection. Add stricter **38 GPU hours / 8 original-E2 hours** across
all starts; respective STOP maxima 38.25 / 8.25 hours also obey the original
absolute common deadline. Every boot/process gets a fresh verified watcher.
Preserve the **aggregate 32 GiB extra-work limit / 25 GiB per-node free reserve**;
measure coexistence, prune only verified disposable copies and never exclude
staging/setup to make that accounting pass. Do not begin an unaffordable DAG.

At current Catalog rates, including IP: **$0.859/hour G2/L4**, **$0.735/hour N1/T4**,
**$0.273/hour original E2**. Conservative envelopes are **$42.70 L4 / $37.17 T4**,
including STOP bounds, temporary disks priced for 96 hours, original-disk attribution,
22 GiB outbound at $0.12/GiB, operations and $1.50 contingency. The 96-hour factor
is a costing upper, not permission to retain anything past October 28. Disk
attribution overlaps the original $8 interval and is not another invoice. Temporary
worker disks are charged to the $45 scope. These are maxima, not native runtime
forecasts; measured gates may still refuse. No new $45 or larger ceiling is proposed.

Current visible credit is **DKK 1,865.13 / 95%**, expiry January 12, 2027; pending
usage is unknown with a $35 reserve. Ordinary first-party Compute coverage is
consistent with [paid-upgrade retained-credit terms](https://docs.cloud.google.com/free/docs/free-cloud-features).
Fresh checks remain mandatory before spending. No Marketplace, vWS, commitments,
Spot/DWS or unrelated vendor spend. The original $8 storage review and **October
28, 00:00 Copenhagen** boundary remain; no new raw cache is admitted as retained
beyond it. V100's ~$2.865/hour with VM/IP is not a speculative fallback; idle
reservations or a different provider need their own case and authorization.

This task adds **no compute, bulk transfer, quota/resource change or upload**.
The replacement launcher, Linux/CUDA/runtime, network and scale gates remain
unprepared/unadmitted; only actual cache relocation and this costed resource plan
are complete. Current authority explicitly excludes new VMs/zones/accelerators/
disks, so owner approval of the resource exception is needed before provision.
Keep E021 scientific criteria and all 156/799 denominators, N-quarantine, oral
origin/known-shared limitations and skin exclusions unchanged. This is an execution
repair proposal, not a change in the evidence we require or a product-family verdict.
