# E022: reliable marker-informed cross-contig learning

**Completed and independently reviewed, October 26, 2026: MODIFY. VM TERMINATED.**
Phase `marker-20261026T012935Z-e88dc8a-r2` ran the sole frozen E009 ten-depth fit.
[Inspection](inspection-observed.json), [comparison](comparison-review.json),
[all 156 targets](comparison-targets.tsv) and [costs](cost-review.json) own the final
evidence. [Operations](OPERATIONS.md#exact-following-prompt) owns the next scope.
The old [native handoff](native-observed.json) is a dated running snapshot,
superseded by this inspection, not a completion receipt.

- [Candidate/wheel/default lock](candidate-lock.json), [used inputs](input-lock.json),
  [pair cache](pair-cache-lock.json) and [native plan template](plan-template.json).
- [Local contracts, failures and resources](local-observed.json).
- [DCVBin efficiency/source audit](../../docs/evidence/2026-10-25-dcvbin-efficiency-and-marker-learning.md).

## Verified execution and scope

Control-plane `TERMINATED`, guest `SUCCESS`, private completion, all five native
gates, seven serial scientific stages and final target agree. Restore, train,
embed, group, refine, export and graph proof each finish once; used-inputs-after,
collection and three upload/readback pairs exit 0. The separate private watchdog
snapshot matches the admitted boot/PID/birth tick/command, observes process exit
for 61.99 seconds and requests clean shutdown. Completion-upload's terminal CLI
exit is absent from its pre-upload receipt; its remote bytes and the guest SHA
independently prove delivery. No wake or science replay was necessary.

Archive `e022-evidence.tar.gz`: **115,627,793 bytes**, SHA256
`d7d709969070ee0831e2a765eacf6e3588de725cf37e2ca914c58022423c4cd9`.
Independent local full sparse-graph/vector reads reproduce the native contract
exactly, including geometry, without model inference or a new index. All **299
regular members / 288,134,191 logical bytes** and the exact-byte
`train/reference.npz -> embeddings.npz` alias pass local verification. Native
scientific source remains `fdad862`; operational source is `e88dc8a`. All 87
original source members, returned native source, owned package/default files and
release bindings match. Earlier source locks remain historical freezes, unchanged.

Full axes: **145,702 contigs / 231,678,157 bp**, with ordered measured depth samples
**0, 2, 3, 4, 6, 9, 10, 11, 14, 17**. Every epoch exposes 89,041 eligible parents,
432,664 available views and all 2,328 cached pairs. Seed 11 / 20 epochs / batch 256,
four threads / no loader workers, the zero-to-0.1 loss ramp, stopped target,
predictors, 6,960 EMA updates, exact native reload and unit geometry pass. Numerical
Python is the original **3.10.15**; workflow Python is **3.12.10**. The previous
prose erratum and failed Mac allclose tolerance remain explicit.

No epoch fails the existing collapse guard. Final fused effective rank is
**38.98** online / **35.97** target, versus E021 36.95 / 34.85. Sampled 30-neighbor
recall is 0.99740 mean / 0.93333 minimum for 64 fixed queries; this is not a
guarantee for every contig. Original GLM/context banks and markers were reused:
no extraction, marker detection, baseline fit/rescore, new DNA or external run.

## Frozen outcome and trade-offs

| Full-reference conservative v2 | Preserved E021 post | E022 post |
| --- | ---: | ---: |
| Weighted R95 | 7.8175% | **7.7497%** |
| At least 50% recovered targets | 14 | **14** |
| At least 90% recovered targets | 6 | **8** |

The exact difference is **−375,929 recovered bp / −0.06778 percentage points**;
13 targets gain, 11 lose and 132 are unchanged. ASV266.11 gains 2,026,650 bp and
reaches 99.20%. ASV150.14 and ASV300.2 cross 90%; ASV406.4 falls from 91.38% to no
passing bin, losing 3,111,747 bp. Its largest new dominant bin retains 3,193,657
confirmed bp but has only **76.28% conservative all-DNA purity**. This identifies
a failed purity gate, not absence of all its DNA or proof that every unconfirmed
base is contamination. No bin is changed using that diagnosis.

Parent, old refinement and frozen E013 post all have **the same R95 and target
counts**, but different partitions, assignments and B3 statistics. E013 selects
four parents, three median-seeded alternatives and one retained alternative at
the eight considered conflicts. Bin counts are 2,027 / 2,032 / 2,031. Post preserves
85,311 assigned contigs / 206,558,934 bp, 3,730 unassigned / 3,083,769 bp and all
56,661 below-cutoff exclusions / 22,035,454 bp. Every short, marker-negative,
unknown/non-target and excluded population remains in the full accounting.

Bacterial native 5-NN agreement rises **0.71257 -> 0.72030**; bp-weighted bacterial
grouping precision/recall rise **0.80848 / 0.57793 -> 0.81556 / 0.59175**.
All-lineage restricted B3 F1 rises 0.48126 -> 0.48704. Eukaryotic neighbor agreement
falls 0.78591 -> 0.76951 and its grouping worsens; aggregate improvements do not
erase this trade-off. The 112 attributable fixed raw/learned query subset is
different from the full emitted native-neighbor population; neither is substituted
for the other. The full subset summary declines 0.82857 -> 0.81071, while its
37 bacterial queries are unchanged at 0.84324. Raw-query geometry is unchanged.

Of 1,963 positive constraints, **1,301** have equal admitted dominant-origin labels,
**4** disagree and **658** remain unresolved. Of 365 negatives, **210** have different
labels, none have equal labels and **155** remain unresolved. These are diagnostic
label agreements, not unique-sequence identity or proof that all loci/replicons
agree. Do not drop unresolved pairs, tune thresholds or blacklist families after
inspection. Native reliability/exposure contracts pass; no critical implementation
mistake is demonstrated, and optimality is not established.

The original KEEP requires a +0.5 percentage-point R95 gain and no target-90 loss;
it **fails unchanged**. ABANDON also fails because target-90 count improves.
Therefore **MODIFY**, with no product-default promotion or general marker verdict.
The control does not isolate every reliability/loss ingredient. This one assembly
is development data, not independent generalization evidence.

All **156 references / 554,661,890 provided bp** and **3.3034% N quarantine** remain.
Only 102,790,342 reference bp have currently admitted confirmed assembly support
(18.5321% of the provided denominator); that support is not guaranteed recoverable
as pure bins. The retained MetaBAT2 reference has 8.5493% R95 / 16 targets at 50% /
5 at 90%, under different native length eligibility. E022 does not uniformly lose
to it, and this is neither native-cutoff parity nor evidence of SOTA performance.

## Resources, costs and preservation

Two provider-reported allocation intervals total **2,735.295 seconds / 45.59 minutes**
or 6.0784 allocated vCPU-hours: first pre-setup parse failure 92.924 seconds,
successful boot 2,642.371 seconds. The original clock includes the intervening
stopped time and was never reset. Science takes **29.34 minutes / 3.889 GB sampled
tree RSS**; training itself takes 23.32 minutes plus its stage setup/verification.
Process CPU is recorded separately from charged uptime. Global sampled disk growth
is **0.655 GiB**, minimum free **55.87 GiB**. Every frozen ceiling passes.

Priced compute/RAM/IP **$0.20746**, existing-disk run attribution **$0.03247**,
conservatively paid download **$0.01303**, new-return storage to the original
boundary **$0.00013**: **$0.25310 subtotal / $0.85310 with reserves**, within the
original new $2. This is measured-allocation pricing, not an invoice or credit-delta
attribution. Disk/storage attribution overlaps the separate storage approval and
must not be added twice. Fresh Welcome credit is **DKK 1,800.33 Available / 91%**,
January 12 expiry; displayed monthly net cost is zero, with unknown >24-hour lag
and a $35 reserve. [GCS pricing](https://cloud.google.com/storage/pricing) and
[Welcome-credit terms](https://docs.cloud.google.com/free/docs/free-cloud-features)
were refreshed before export.

Frozen new-output diagnostics take **32.62 seconds / 1.406 GB sampled RSS**;
staging plus diagnostics use under **0.381 GiB** and 242.25 seconds to the recorded
numerical-review handoff. Subsequent compact summary/check/seal work shares the
same one-hour / 6 GiB review clock. Failed preliminary probes and all original
native/local journals are preserved. No evaluator rerun was needed. A further 5.86-second / 0.440 GB returned-array
contract passes, as do all six pure operational tests without any training.

The archive omits **1,367,669,888 bytes of full frozen vectors** and
**233,607,419 bytes of emitted DNA**, retained on the work disk. Original context,
FASTA/views, runtimes and prior outputs are separate retained dependencies; hashes
are not their backup. No deletion or private inspection upload occurred here.
The approved storage interval still ends **October 28, 00:00 Copenhagen (CET)**;
stopped disks conservatively cost **$31.20/month**. A separately proposed **new $8
storage-only week through November 4** forecasts **$7.73** including current GCS,
2 GiB extra and reserve. It needs owner approval and fresh checks; no automatic
renewal or deletion is authorized.

## Strongest next recovery block

Implement **adaptive-density, abundance/marker-informed bin construction** locally,
holding learning and native vectors fixed. Build one coherent candidate-generation
and conservative selection/refinement path that can address both mixed bins and
fragmented genomes, rather than another global CPM resolution or side-loss grid.
Keep whole-parent alternatives, all DNA and optional unassigned outcomes.

The observed bacterial neighborhood/grouping gain with flat R95, the ASV406.4
purity failure, and **252 bacterial-dominant bins below 200 kb / 10.81 Mb** make
bin construction the most direct next hypothesis. Those diagnostics must not pick
which bins to split/merge. Not all small bins should merge. Existing E017/E018 oral
regressions are strong contrary evidence: do not repeat their single long-core
CPM plus fixed-profile recruitment design under a new name. Test adaptive local
density and bin-level alternatives, with explicit composition/depth/marker
reliability, instead of forced recruitment or a universal graph-gain veto.

The reviewed [MetaBAT2 method](https://doi.org/10.7717/peerj.7359) integrates
composition/abundance graph scores and iteratively expands/partitions its graph.
[VAMB's pinned density source](https://github.com/RasmussenLab/vamb/blob/b146fb610921aef1da8aed5d739f1ce80d21b33a/vamb/cluster.py)
uses length-weighted distance densities and local peak/valley radii. Their inspected
source identities/hashes are in the comparison; they justify investigating a
local-density alternative, not copying their defaults or claiming tool parity.
Mean-only depth does not authorize a measured-variance likelihood.

Prepare a cheap matched cached comparison on **E022 E009 vectors** and **existing
E019 oral sequence-only vectors**, each against its own unchanged CPM/E013 output.
These different frozen learning anchors test the downstream rule's transfer,
not an E022 two-community end-to-end result. Freeze one common label-free rule,
no-regression/gain criteria and cost/runtime/return envelope before new outcomes.
Do not retrain, redetect markers, rescore baselines or acquire another bank/data.
No community execution is authorized by this inspection.

A larger/fine-tuned Transformer or taxonomy branch may add useful information,
but current evidence does not establish capacity or missing taxonomy as the main
failure. A zero-side-loss or zero-GLM control is a possible later attribution
question, not the default next experiment. DCVBin-inspired batching/cheaper exposure
remain useful future efficiency work; its source audit is not a measured speed
comparison and reducing DNA views changes the treatment. Reusing caches makes
this next recovery decision inexpensive without rejecting richer information.

Keep the frozen skin choice **unscored**, with its 610-target provided-origin
protocol and all outstanding molecule/host/circular/taxonomy/near/pretraining/
competitive-ambiguity/unique-support/evaluator/cost limits. Skin has no admitted
contig depth and cannot confirm the active E022 depth-gated mechanism. A future
independent depth-enabled community needs separate prospective source/truth and
read/mapping/storage/compute admission; neither this inspection nor a cached
oral grouping control supplies that evidence.
