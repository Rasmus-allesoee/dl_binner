# E009 operations: authorized data-only GCP phase

Updated: 2026-10-14. **Later owner authorization: prepared data-only phase at
5fec4e1; no binner fits/scores/model changes or automatic retries.**
[Actual phase receipt](gcp-data-observed.json) owns execution/outcome/cost.
Keep the clean VM source at that exact SHA while its journals remain active.
[CLOUD](../../docs/CLOUD.md) owns VM/access/credit operations;
[D013](../../docs/decisions/D013-first-comparative-benchmark.md) owns the comparison;
[D014](../../docs/decisions/D014-google-cloud-workspace.md) owns the provider.
Old Terminal/Slurm/Home/shared-storage commands and their budgets are exclusively
[historical](../../docs/history/E009_UCLOUD_OPERATIONS.md). Old receipts/prefix
locators are preserved provenance, never GCP runtime paths.

## Evidence and sample choice

[V14 review](linux-preflight-v14.json) checks the 488,677-byte archive SHA256,
all 174 regular members /172 retained hashes, terminal status/collection, native
exits, package origins and actual finite augmentation arrays. SCGBinner and
COMEBin/complete CheckM pass; SemiBin, MetaCAT and CompleteBin were reused without
execution. V10's utility/data/source/AMBER contracts remain accepted.
Actual v14: 211.422 s through collection, 0.469827 allocated vCPU-hours at
8 CPU/24 GB; peak sampled stage RSS 3,724,357,632 bytes. Immutable archived payload:
8,352,269 bytes. No fit/grid/lineage placement or E009 score ran. These tiny UCloud
contracts do not establish a new GCP runtime or ten-sample fit affordability.

Choose **10 full read samples**, first listed sample from each corrected subject:
**0,2,3,4,6,9,10,11,14,17**, numerically ordered. IDs 0..9 cover only six subjects.
One-per-subject represents all ten subjects at half the sample workload; 20 adds
paired temporal observations and might help binning, with benefit on this single
assembly unmeasured. Selection uses identifiers/subject metadata, not truth
abundance or scores. These are now development coverage, not certified holdouts;
"first listed" does not assert a verified chronological sampling time.

Build **one sample-0 MEGAHIT assembly**, 200-bp emission, and map those ten full
samples to its exact reference. No second assembly/coassembly. One assembly does
not mean one BAM. Primary/raw controls now use TNF+ten-depth; the two sequence-only
controls remain prospective diagnostics. Product source/seed/training/clustering
stay unchanged. D013 supersedes the mandatory shortlist: CompleteBin, COMEBin
full grid and SCGBinner fits are deferred. The stored max-50 patch stays provenance. [Depth axes](depth-samples.tsv),
[protocol](protocol.json) and [data plan](gcp-data-plan.json) own this amendment.
Padded actual BAM paths preserve numerical order under COMEBin's real-path sort.

## Authorized resources, costs and storage rationale

The earlier [read-only preparation snapshot](gcp-preparation.json), 2026-10-14: VM `TERMINATED`,
e2-standard-4/16 GiB, 30-GiB standard boot +50-GiB balanced work, four-hour STOP.
Global CPU quota **12**, regional E2 **24**, balanced/SSD **250 GiB** (50 used).
Compute/IAP/IAM/OS Login/Storage services are enabled. No cloud mutation ran.

The later owner authorized the same VM as **e2-standard-8/32 GiB**, existing
balanced work disk **300 GiB**, existing ext4 expansion without formatting and
**25-hour provider STOP before start**, replacing the setup-only four hours.
Fresh credit/price admission passed; quota request case
`a11cf91a-b76b-4c95-9f79-7dc7538f3611` is effective at **300 GiB** in the API.
The stopped VM/disk were changed, mounted/expanded, and source synced cleanly to
exact 5fec4e1 before execution. CPU quota fits; no extra service/CPU quota/GitHub
write credential was needed. The phase receipt records actual timing/status.
Driver: **24-hour cumulative phase clock**, including setup, parent hashing,
failed attempts and work; resume cannot reset it. The extra provider hour covers
connection/assessment/collection, not an automatic retry.

Current HEAD totals: ten reads **48,632,842,889 bytes /45.29 GiB**; all twenty
**97,278,294,701 bytes /90.60 GiB**. ETags/HEAD are transport identities, not SHA256
admission. Source archive: 3,202,310,417 bytes with accepted v10 SHA. Its required
GCP reacquisition replaces inaccessible UCloud bytes, without scientific replay.

| Coexisting component | Estimated GiB | Assumption |
| --- | --- | --- |
| Retained ten read archives | 45.29 | Current HEAD bytes |
| Compressed FASTQ +sample-0 origins | 40–50 | Full native layout pending acquisition; plain FASTQ is losslessly compressed during extraction |
| Sample-0 compressed assembly mates | 4–5 | Deinterleave only sample 0 |
| Ten sorted BAMs/indexes | 20–45 | Mapping/compression unmeasured; retain all reads |
| One SAM/sort scratch | 15–30 | Serial; remove SAM only after BAM quickcheck/axis receipt, retaining its identity/size |
| Sources/catalog/reference batches | 19–22 | Full catalog 10.25 Gbp; conservative sample-0 universe 3.95 Gbp includes non-target/human DNA |
| Assembly intermediates, runtime, truth/logs | 15–35 | No all-binner installs/checkpoints in this phase |

This estimate contains **no CompleteBin files**. Deferring its fit does not
remove the common read/BAM/source/scratch footprint. The upper component estimate
is 232.29 GiB; adding the 25-GiB reserve exceeds the current 250-GiB quota. The selected 300-GiB proposal adds about 43 GiB beyond that estimate/reserve. Monitor a **25-GiB free reserve**, actual
growth and stop/flush latency. This is a provisioning estimate, not a scientific
data cap or instantaneous hard write quota. Failure retains evidence and stops;
no automatic growth, filtering or deletion. Twenty samples would likely need
roughly 350–500 GiB and twice the sample mapping/depth work, with disk quota growth;
assembly/truth work does not double. Neither peak nor runtime is measured.

Iowa list rates: $0.26804568/hour VM +$0.005 IPv4 = **$0.27304568/hour**;
25 hours **$6.83** compute/IP. Boot+300-GiB work is **$31.20/month gross**, even
stopped, versus today's $6.20. Seven days is about **$7.18**. The owner approved a **$20 gross
phase envelope** for that run, <=seven-day storage and small compact-archive/
operations reserve. A roughly 8–20-hour data run is an unmeasured planning range;
24 hours is a ceiling. No allocation core-hour figure is substituted for money.

Ordinary CPU Compute Engine, Persistent Disk, Standard Storage and outbound IPv4
are the intended Welcome-credit-covered products; basic IAP has no service fee.
Ingress and same-region bucket/VM transfer have no transfer charge; operations
and stored/soft-deleted bytes still accrue. No GPU, premium image, NAT, Marketplace
or new paid service. The live console now verifies **DKK1,972.04 Available upgraded Free Trial credit
through 2027-01-12**, paid billing and the restricted ordinary-usage scope. Current
DKK SKUs and pending/reporting lag were checked before mutations; see
[CLOUD](../../docs/CLOUD.md#live-data-phase-credit-gate-2026-10-14) and the phase receipt.
The earlier owner DKK1,973 display remains dated history. Estimates exclude unused
Free Tier discounts, tax/FX and unrelated usage.

Disk growth cannot simply be shrunk back. Review retention **by 2026-10-21**
and by 2027-01-10. After seven days the provisioned disks still cost **$31.20/month
(~DKK205.24 at the current quote)** gross while stopped; a 250-GiB alternative
would save only ~$1.15 in seven days while weakening the conservative reserve. A smaller replacement needs a separately reviewed
copy/restore plan and verified important evidence. No destructive/card-billing
action follows automatically. [Compute prices](https://cloud.google.com/products/compute/pricing/general-purpose),
[disk](https://cloud.google.com/compute/disks-image-pricing),
[network](https://cloud.google.com/vpc/network-pricing),
[credit rules](https://docs.cloud.google.com/free/docs/free-cloud-features).

## Prepared workflow and admission

[Launcher](../../scripts/e009_gcp_run.py) defaults to plan-only inspection.
[DAG](../../workflows/e009-data/Snakefile): sources →reads 0 →assembly →ordered
per-sample acquisition/map/depth →matrix/provisional alignment truth.
[Workers](../../scripts/e009_gcp_stage.py) run actual archive readers and native
MEGAHIT/strobealign/samtools/minimap2; no scientific worker is mocked.
[Independent Linux lock](gcp-data-linux-lock.json): 120 packages /146,456,191 download
bytes, including Python3.12.10, Snakemake9.16.3, samtools1.24, strobealign0.17.0,
MEGAHIT1.2.9, minimap2 2.30; declared package constraints require glibc >=2.34
(the local solver used virtual glibc2.35). The complete independently owned recipe installed on the VM and its actual
Python/native origins, versions and tiny 14-rule changed-driver contracts passed.
Runtime/QA took 42.501 s and is recorded as a setup attempt in the data root, so
the production launcher subtracts it from the original 24-hour clock. The portable
fixture factory retains its historical Mac/no-scale label and one-thread assembly;
actual host provenance proves the exercised Linux contracts, not full-scale
assembly or biological truth admission.

Use clean reviewed `/srv/dl_binner/repo`, persistent data
`/srv/dl_binner/experiments/e009/data-stage-v1`, and sibling lock-named owned
`envs/` and `cache/`. No five-binner install or inaccessible UCloud/Mac dependency
borrowing. New-host data-runtime identity/health passed; full data/truth acceptance remains
separate. No accepted five-binner contract was repeated.

Retain terminal/stage/native-error logs, actual byte progress, CPU/RSS/physical-I/O
activity, commands, per-rule extended benchmarks and attempt allocation receipts.
Setup/resume/hashing shares the work clock. Libraries are serial; count native
pools/extra BGZF/reducer/I/O threads. Use `--cores` without `--jobs`; explicit
predecessors serialize the complete DAG. Disk reserve stops the supervised tree.
Provider uptime includes connection/idle/collection and is separate from sampled
CPU/RAM, rule benchmarks and driver timing.

Seal closed stage bytes and follow manifest paths. Explicit `--resume` requires
identical source/config/runtime/artifacts and only the original remaining clock.
Failed unsealed stages are preserved/refused for assessment. Never overwrite,
delete or silently redownload them. Completed DAG resume schedules no native rules.

Truth inputs are separate and opened after depth/features, with all DNA/zeros
retained. Align <=500-Mb reference batches then globally reconcile **all** emitted
qualifying PAF/CIGAR chains. The 311-file source universe is conservative retained
metadata; labels/whole-source lengths remain **provisional**. Source records include
permuted strains/replicons and human DNA. Independently reconcile exact positive
sample-0 origins, genome/replicon grouping and cellular target taxonomy before
final truth admission or any fits/scores. The origin summary checks complete
counts/provider tax IDs, not an exact read-ID join/domain classification. Do not
guess bacteria from filenames or invent a whole-genome denominator. Retain PAFs
for reviewed regrouping without blindly repeating alignments.

The independent [read/source review helper](../../scripts/e009_data_review.py) is
locally tested with actual gzip files/manifests, late-ID duplicates, byte drift,
taxonomy mismatch and ambiguous source formats. After the production driver exits,
run it under the **remaining original clock/resource envelope**, with the provider's
explicit sample-0 profile, without changing the clean 5fec4e1 execution checkout.
It verifies full FASTQ/origin-ID sets and exact original-record/genome/lineage joins.
It cannot by itself admit chromosome/plasmid identity, permuted-copy meaning or a
whole-genome denominator, and never opens bins/scores or edits stage journals.
The [phase receipt](gcp-data-observed.json) retains the provider profile and an
actual plasmid/copy example requiring that review. Do not infer absent genomes
from rounded-zero abundance or bacterial cellular genomes from taxonomy alone.

Stop on source/ETag/hash drift, malformed archives/mates, assembly >100,000 eligible
>=500-bp contigs or >600 Mb, native/axis error or RAM/clock/stall/disk limit. No
automatic extension, retry, DNA filtering or native schedule change. Review actual
data/truth and costs before the separate fit phase.
[CompleteBin audit](../../docs/evidence/2026-10-14-completebin-storage.md) explains
why this 300-GiB/32-GiB layout is not its fit admission: later 400–500-GiB disk and
64/128-GiB RAM may be needed, with quota, credit and owner approval then.

## Recorded launch and next review boundary

Safe local inspection (no writes/downloads):

```bash
python3 -I -B scripts/e009_gcp_run.py
```

The owner-approved normal Mac push/read-only VM sync, quota/resource/mount
checks and STOP change are complete. The following is **launch provenance**;
do not invoke it again while the current driver is active. On the clean VM:

```bash
cd /srv/dl_binner/repo
python3 -I -B scripts/e009_gcp_run.py \
  --source-commit 5fec4e1d1700c64c4bdd9945bad4e116ade73c57 \
  --allocated-vcpus 8 --allocated-ram-gib 32 \
  --hours 24 --free-gib 25 --stall-seconds 1800 --execute
```

Add `--resume` only after intact partial-stage review; it does not reset the clock.
Return persistent log/attempt paths or compact archive/checksum, not terminal
copy-paste. Direct VM work needs no UCloud transfer packet. Stop/verify the VM
after collection, preserving disks and accepted outputs.

The prepared prompt at Git commit `5fec4e1` is historical. The actual owner
message authorized this data phase and superseded the compulsory tool shortlist.
The next prompt will be updated here after independently reviewing the complete
or partial result. No fit phase, resource extension or retry follows a launch.
