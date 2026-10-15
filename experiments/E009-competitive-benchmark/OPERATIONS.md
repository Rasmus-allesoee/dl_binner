# E009 operations: reviewed data outputs and provisional truth

Updated: 2026-10-15. **Later owner authorization: prepared data-only phase at
5fec4e1; no binner fits/scores/model changes or automatic retries.**
[Actual phase receipt](gcp-data-observed.json) owns execution/outcome/cost.
The data DAG has exited; keep its source/journals/outputs bound to that exact SHA.
[CLOUD](../../docs/CLOUD.md) owns VM/access/credit operations;
[D013](../../docs/decisions/D013-first-comparative-benchmark.md) owns the comparison;
[D014](../../docs/decisions/D014-google-cloud-workspace.md) owns the provider.
Old Terminal/Slurm/Home/shared-storage commands and their budgets are exclusively
[historical](../../docs/history/E009_UCLOUD_OPERATIONS.md). Old receipts/prefix
locators are preserved provenance, never GCP runtime paths.

## Verified data outcome and next boundary, 2026-10-15

**The complete data DAG failed; reusable assembly/BAM/depth data are accepted.**
The original driver records exit 1 after **47,025.069 s /104.500153 allocated
vCPU-hours** at 8 CPU/32 GiB. The failure is in `e009_truth.parse_paf`, not acquisition,
assembly, mapping, measured depth or minimap2. All ten aligner batches have exit-0
receipts; no retry or native stage replay occurred. The watchdog's closed snapshot
contains the failed attempt and stage seals. GCP independently reports the first
stop at **2026-10-15T09:32:21.624Z /11:32 Copenhagen**, after **13.179723 provider
hours**, distinct from driver wall time and sampled process CPU.

The full assembly remains **145,702 contigs /231,678,157 bp**, SHA256
`d8ea66f546d9ae74078fb0db59a96b0521be1c3612dc3923ec16a9d245442f33`.
Exactly **89,041 contigs >=500 bp** are eligible for the prospective unchanged
prototype; the other 56,661 contigs /22,035,454 bp are retained. No cost-based
subsampling, extra cutoff, coassembly or model change occurred.

Independent [feature acceptance](../../scripts/e009_data_acceptance.py), source
`9409f1a`, verified actual critical hashes against the sealed/watchdog manifests,
all ten native BAM `quickcheck`/ordered SQ axes, all per-sample depth axes/zeros,
and **every one of 1,457,020 combined-matrix cells**. Ordered samples are exactly
**0,2,3,4,6,9,10,11,14,17**, with columns from [the frozen manifest](depth-samples.tsv).
All BAMs are coordinate-sorted and indexed. Thirteen all-zero matrix rows remain;
there is no imputation or removal. The combined matrix in `parts/final/depth.tsv`
was closed and byte-bound before the parser failed; its independent acceptance
does **not** create `parts/final/done.json` or authorize a consumer to infer missing
outputs. Future consumers must use the reviewed acceptance/manifest bindings.
Bulk read archives/unused intermediates were not rehashed merely for this review;
sample-0 FASTQ/origins and all consumed feature bytes were explicitly verified.

The first failing PAF row is retained in [the failure example](truth-failure-example.json).
Both coordinate consumptions agree, but its 2,948 CIGAR columns differ from PAF
block 2,947 by `nn:i:1`. Minimap2 2.30's
[actual writer](https://github.com/lh3/minimap2/blob/v2.30/format.c) emits its stored
`blen`; [its alignment accounting](https://github.com/lh3/minimap2/blob/v2.30/align.c#L242)
subtracts ambiguous bases from that value and emits their count separately.
All **300,499 retained PAF rows** pass exact axes, strands, coordinate bounds and
CIGAR endpoint consumption; **459 rows** have ambiguous bases, and every block
difference equals its `nn` count. Our equality check is therefore too strict for a
valid native row. The exact
exception is reproduced locally; a heuristic aligner failure, exhausted budget,
RAM failure or bad BAM is not inferred from the scheduler trailer. No parser fix,
truth regeneration, binning or scoring ran during this review.

### Origin, genome and taxonomy review

[The final audit](../../scripts/e009_data_review.py), source `b9a5289`, independently
checks full canonical FASTQ and simulator-origin ID sets: **33,267,026 mate records /
16,633,513 pairs**, identical sets without relying on order. Every positive origin
joins an exact unique source record in the frozen 311-file universe. There are no
unknown source IDs, multiple genome assignments per source record/file or positive
records outside that universe. Two selected files have zero origins; 1,280 full
reference replicons are unobserved and remain competitive references.

[The reviewed population](truth-population-review.json) contains **309 positive
simulator genome IDs**: **156 bacterial, zero archaeal, 133 viral, 11 eukaryotic and
nine separately simulated plasmids**. Each positive genome maps to one source file.
The 156 bacterial genomes meet the prospectively fixed >=200-kb provided-reference
length criterion; these are reviewed candidate targets, not completed recovery
truth or finished-MAG quality. The source catalog reports zero exact/accession
development matches, without excluding near-genome or pretrained-reference overlap.

Two first audit attempts are preserved: v1 rejected an origin whose provider
genome-ID cell is blank; v2 exposed synthetic viral strain nodes absent as literal
integer lineage nodes. The tested v3 uses **197 explicit genome joins, 110 explicit
genome joins with the exact synthetic origin-taxon suffix, and two exact taxon-only
rows**. It retains original and synthetic IDs separately; taxon-only joins supply
lineage and never merge genomes. All observed relationships resolve; arbitrary
unknown/ambiguous joins are retained as unresolved evidence, never admitted truth.
V1/v2 outputs and timing are preserved. These were separate versioned review
consumers; the failed scientific data DAG was not retried.

All nine `.permuted.fna` files are ten exact forward circular rotations, confirmed
against their native catalog file hashes: **4,033,410 literal bp /403,341 one-copy
molecule bp**. Actual origins assign them to `pASV42`, `pASV43`, `pASV62`–`pASV68`;
their `HOST` values are the three bacterial host IDs. In particular the filename
beginning `ASV134.7` is **pASV43**, separately simulated from host ASV134.7. Preserve
that distinction; neither filename prefixes nor HOST fields authorize merging.

Measured mate-record fractions are **83.32% bacterial, 14.42% eukaryotic, 1.57%
viral and 0.69% other/plasmid**. These differ markedly from the provider's reported
profile percentages; do not substitute profile percentages for read/DNA fractions
or infer product feature choices from either one-community composition.

**Truth remains provisional.** Next derive a fresh simulator-genome reference axis,
normalize exact circular coordinates and validate full provided-reference lengths,
non-target/zero-origin competitors and global chain ambiguity. Repair/test the
ambiguous-base PAF/CIGAR contract against the pinned source and tiny actual native
N-containing alignments, preserving malformed-row refusal and a stated ambiguity/
identity policy. Reuse the retained PAFs: no minimap2/assembly/mapping/depth replay.
Do not edit old stage manifests to make a resume pass or call the failed DAG
successful. An admitted versioned truth artifact must precede any quality score.

### Cost, storage and retained evidence

The owner's review request authorizes necessary evidence access within the
remaining **$20 data-only** envelope. Before waking the stopped VM, fresh console/API
checks found **DKK1,952.79 Available Welcome credit, expiry 2027-01-12**, paid billing,
billing enabled and unchanged ordinary E2/disk/Storage/IP SKU eligibility/prices.
Reported October usage was DKK5.16, savings DKK5.16, net DKK0; issued-credit
consumption was DKK20.64. These lagged views are not a reconciled phase invoice.
Unreported usage is not assumed zero.

The same existing 8 CPU/32-GiB VM and 30/300-GiB disks were reused, with **one-hour
provider STOP before wake**, no new service, provisioning, resize, runtime install
or scientific DAG. Review, hashing and collection fit within that cap and the
remaining original cumulative data allowance. The actual second uptime/stop and
price calculation are in [the receipt](gcp-data-observed.json). First-run compute/IP
is **$3.5987 gross** from measured uptime; the review's one-hour maximum was **$0.2731**. Actual review uptime was **0.4767225 h**,
priced at **$0.1302 gross**, and the VM is again **TERMINATED**, IP absent, at
**13:19:53.611 UTC /15:19 Copenhagen**, with both disks preserved. Total measured
priced compute/IP is **$3.7288 gross**; adding seven-day disk exposure gives
**$10.9091** before the small archive/operations/export reserve.
Seven-day provisioned disks are **$7.1803**, leaving ample room below $20 for the
compact archive/operations and small export. Seven-day storage is future exposure,
not already-spent cash; list-cost accounting is distinct from a delayed invoice.

Production sampled peak working-filesystem use was **170.66 GiB**, minimum sampled
free **124.52 GiB**; sampling can miss a transient peak. About 156.4 GiB were used
after the data run. The original 300-GiB disk was conservative; measured data-only
use suggests 225–250 GiB could serve a similar future run with reserve. The disk
cannot shrink in place: a smaller replacement needs an approved copy/verification
and simultaneous-capacity/quota/cost plan. Savings at 250 GiB are only $5/month.
This is a capacity estimate, not a claim of unchanged disk performance. A 225–250-GiB
replacement copied alongside the original 300-GiB disk would require temporary
balanced/SSD quota of 525–550 GiB plus a separately approved copy/wake cost.
No migration/deletion is performed. Current stopped disks remain **$31.20/month
gross**, review by **2026-10-21**; an explicit retention decision is still needed.

The private checksum/readback archive contains **554 regular members /
1,362,258,256 logical bytes**, **246,936,673 compressed bytes**, SHA256
`f1616f08533b57609c2e09d212cc40aade068e51e968ee554735a5b8e21f9312`.
It retains exact closed inventory/terminal/log/receipt bytes, full assembly,
depths, all emitted PAFs, source catalog/axes, tiny circular sources and review
code/results. It excludes raw reads, BAMs, environments and credentials; those
bulk working files remain on disk. Same-region private Standard Storage upload and
SHA256 readback passed. Archive-only storage is about **$0.0046/month gross**.
The phase receipt records the bucket locator, Mac verification and exact member
inventory; an open log was not substituted for this immutable payload.

### Strongest next step and later fit approval

**Do truth repair/admission and control preparation next; no immediate external
tool execution.** It is the prerequisite for useful recovery diagnostics and can
reuse the expensive accepted data. Paying for a mature-tool win now cannot fix
this evaluator or distinguish feature, representation and grouping failures.

[The prospective diagnostic plan](diagnostic-controls-plan.json) preserves dev3
`5e54538`, seed 11, 20 epochs, cutoff 500, fixed transforms/clusterer and all DNA:
two serial paired product invocations give raw/learned TNF+ten-depth and TNF-only.
It is a configuration/command proposal, **not an execution-ready native launcher**.
A complete independent owned CPU environment and bounded parent remain to be
prepared/validated. Existing tiny UCloud/E008 Linux acceptance is not this full
89,041-contig runtime/cost measurement. Exact kNN/sorting and graph grouping can
dominate, so the proposed four-hour cap is not a finish-time promise.

Propose a separately approved **$2 incremental gross fit envelope**, existing
8 CPU/32 GiB and 300-GiB disk, **four-hour cumulative setup/verification/fit/
collection clock**, **4.25-hour provider STOP**, 25-GiB reserve and **10-GiB expected /
20-GiB conservative extra disk**. Compute/IP ceiling is about **$1.16**, with the
rest for small archive/transfer/rounding; retained disks stay within their existing
seven-day approval. No resize or retention extension. An exhausted cap means
retain partials and reassess, without changing schedules/eligibility or rejecting
a method family. This fit money cannot be taken silently from the data-only $20.

These controls can show whether the fixed encoder damages useful raw geometry,
whether useful geometry is lost by grouping, and how these ten columns behave in
this setting. If learned geometry degrades, investigate one view/objective change;
if geometry helps but bins fragment/mix, prefer one fixed-encoder grouping test.
Neither outcome universally selects/rejects depth, sequence or taxonomy. Confirm
improvements on prospectively defined additional data. Keep **SemiBin2** as at most
one conditional later reference, only if retained feature/embedding/reclustering
evidence changes an unresolved decision; measure its full schedule before a new
budget. Defer MetaCAT pending that decision, and keep CompleteBin/COMEBin full grid/
SCGBinner deferred. No whole-tool ranking is a required gate.

Conditional fit approval text, **for a later request after admitted truth**:

> After the versioned E009 truth and unchanged diagnostic launcher are admitted,
> I authorize only the four frozen dev3 raw/learned TNF+ten-depth/TNF-only controls
> under a new $2 incremental gross ceiling, existing 8 CPU/32-GiB VM and 300-GiB
> disk, four-hour cumulative setup/verification/fit/collection clock and 4.25-hour
> provider STOP. First verify current credit coverage, prices and storage headroom.
> Preserve all assembly DNA, the fixed seed/schedule/clusterer and exact input axes.
> No external binner, model change, extra resources, retry, automatic extension or
> retention extension. Stop after success/failure and retain checksum-bound evidence.

## Exact following-step prompt

> Read AGENTS.md, PROJECT_INTENT.md, STATE, CLOUD, D013/D014 and the reviewed E009
> receipts, population and failure example. Repair and locally test a fresh E009
> truth derivation from the retained minimap2 2.30 PAFs, including ambiguous-base
> accounting, observed simulator genome IDs, separate pASV/HOST relationships,
> exact circular-coordinate normalization, full provided-reference denominators
> and non-target/zero-origin competitive DNA. Preserve malformed-input refusal and
> predeclare ambiguity/identity semantics; do not silently weaken checks. Keep the
> old failed journals, source freeze and accepted data intact. Do not rerun the data
> DAG, acquisition, assembly, mapping, depth or aligners. If native truth-only
> derivation is needed, first assess current credits/prices and remaining original
> $20 data-only/24-hour allowance; use only the existing VM/disks with at most a
> one-hour provider STOP, capture logs and stop afterward. Do not provision, resize,
> retry or extend automatically; stop before unclear/uncovered spending. Review the
> new truth independently and admit it only if its population, coordinates and
> ambiguity contracts pass. Prepare/test the bounded unchanged diagnostic-control
> launcher and its separate $2 approval request; do not fit or score any binner or
> change model architecture in this step. Keep external tools, including CompleteBin,
> deferred. Update records, check and commit; report truth status, cost and the next
> exact approval prompt.

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

## Original data-phase resource admission and planning estimates

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

## Executed workflow contract and original admission boundary

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
taxonomy mismatch and ambiguous source formats. This was the original post-driver
review plan; the versioned native v1/v2/v3 attempts and final complete audit are
recorded above. Do not repeat them merely to follow this earlier handoff. The final
helper verifies full FASTQ/origin-ID sets and exact original-record/genome/lineage
joins, with explicit synthetic/taxon-only modes and unresolved evidence. It cannot
by itself admit coordinate truth or a whole-genome denominator, and never opens
bins/scores or edits stage journals.
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

## Closed data-stage launch provenance (do not relaunch)

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
The reviewed partial result and current exact following prompt are at the top of
this guide. No fit phase, resource extension or retry follows this closed launch.

## Overnight exit watchdog record, 2026-10-15 (completed)

The owner reported chat cancellation at the five-hour usage limit and requested
verified autonomous shutdown after the current workflow completes or crashes.
Read-only inspection at 00:41–00:46 UTC confirms the original driver survived:
sources/reads-0/assembly/map-0 are sealed and map-2 is acquiring. The full assembly
is **145,702 contigs /231,678,157 bp**, **89,041 >=500 bp**, FASTA SHA256
`d8ea66f546d9ae74078fb0db59a96b0521be1c3612dc3923ec16a9d245442f33`.
No scale failure, truncation, retry or changed execution checkout occurred.
00:46 UTC free space is **269,894,918,144 bytes /251.36 GiB**; the reserve remains 25 GiB.

[The watcher](../../scripts/e009_exit_watchdog.py), source commit `a6e351f`, is
installed root-owned at `/usr/local/sbin/e009-exit-watchdog.py` with the reviewed
[service](../../workflows/e009-data/watchdog/e009-exit-watchdog.service) and
[timer](../../workflows/e009-data/watchdog/e009-exit-watchdog.timer) in
`/etc/systemd/system/`. Root configuration `/etc/e009-exit-watchdog/current.json`
pins boot `e6cb1c71-5bd3-4c87-8e2e-f0de8b3b1cc1`, driver PID **3167**, birth tick
**18291**, command SHA256 and the original data root. PID reuse, zombies and a
different boot cannot masquerade as this live driver. It runs independently of
SSH/the user's login/chat, at idle I/O priority, nice 19, 5% of one CPU and 96-MiB
memory cap. It does not inspect model scores, change data or run the deferred audit.

At installation the timer was **active/waiting**, polling every 30 seconds. Once the pinned driver
is absent for 60 seconds, it records stage-manifest hashes, closed attempt records
if present and short log tails at `/var/lib/e009-exit-watchdog/exit-snapshot.json`,
mirrored to the persistent phase `watchdog/exit-snapshot.json`. It then syncs disks
and invokes `/usr/sbin/shutdown -h now`. Typical detection/grace is 60–90 seconds,
plus small snapshot/OS shutdown time. Missing optional logs do not block shutdown.
The timer retries a failed shutdown command on its next tick; it never retries the
experiment. No disk or evidence deletion follows. Both disks remain persistent.
The timer is started for this boot, **not enabled for future boots**, and the boot
identity is an additional safeguard. Re-arm explicitly for a later authorized run.

Verification: local decision tests pass; actual Linux `/proc` and root systemd
fixtures pass for exit 0 and exit 7, with a harmless substituted shutdown action.
No real power-off test was performed because it would interrupt the active run.
`systemd-analyze verify` passes; production service returns success and repeated
timer-triggered journal/status timestamps show the exact live process and
`shutdown:false`. Code/config/install/test/activation/tick evidence is retained in
`artifacts/e009-gcp-data/20261015-watchdog` on the Mac and the versioned installer
folder under the persistent phase. The actual receipt binds these small records.

The independently verified GCP policy still has `automaticRestart=false`,
`maxRunDuration=90000`, action `STOP`; API effective deadline is
**2026-10-15T21:21:21.686843Z /23:21 Copenhagen**. This covers a failed watcher or
unresponsive guest without depending on local code. It is a maximum, not an
eight-hour completion forecast or proof the workflow will finish successfully.
Guest shutdown is a supported [GCE stop method](https://docs.cloud.google.com/compute/docs/instances/stop-start-instance).
No new GCP service/IAM grant/capacity or budget extension was required. Stopped
disks still cost ~$31.20/month gross; the October-21 retention review remains.

This owner amendment prioritized prompt automatic stop over keeping compute idle
for interactive analysis. The exact read-origin audit and archive were pending at
shutdown; they were completed in the later bounded review above. Biological
coordinate truth remains provisional. The snapshot proves the watchdog stopped
after a failed driver; the current review boot did not activate that old timer.

Historical prompt after waking (superseded by the current prompt above):

> Read AGENTS.md, PROJECT_INTENT.md, docs/STATE.md, docs/CLOUD.md and E009 operations
> and receipts. Inspect the VM's control-plane status and overnight shutdown first.
> If it is still running, inspect the existing driver/watchdog without disrupting
> or relaunching it. If stopped, do not start or provision anything yet. Review
> locally retained evidence, report the outcome and any bounded restart/access
> needed to collect and review the completed or partial result. Preserve accepted
> stages and provisional truth. No retries, binner fits, E009 scores, architecture
> changes or extra resources; retain CompleteBin's deferral.
