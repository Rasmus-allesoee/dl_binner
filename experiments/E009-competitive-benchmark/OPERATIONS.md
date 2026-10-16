# E009 operations: reviewed controls and next-prototype handoff

Updated: 2026-10-16. **All four owner-approved unchanged controls completed and are
reviewed; the VM is TERMINATED.** [The execution receipt](controls-observed.json)
preserves launch observations; [the independent review](controls-review.json) owns
completion, acceptance, diagnostics, costs and limitations. No refit, retry, new
resources, VM wake, external binner or retention extension occurred in this review.
[CLOUD](../../docs/CLOUD.md) owns access/cost/retention; [D013](../../docs/decisions/D013-first-comparative-benchmark.md)
owns the improvement decision and [D014](../../docs/decisions/D014-google-cloud-workspace.md)
the provider. The failed original data DAG/source/journals remain intact; truth v2
and accepted reusable data are separately admitted. Old UCloud commands remain in
[history](../../docs/history/E009_UCLOUD_OPERATIONS.md).

## Accepted controls and local diagnostics, 2026-10-16

Phase `controls-20261015T211004Z-cf7bf2a` completed at source
`cf7bf2a17eab0c5a2f70999d04e766af1e14f98a`, immutable dev3/seed11/20epochs/cutoff500
and fixed grouping. All 10 launcher stages, both paired commands and all 16 product
stages exit0; no retry/resume. Independent receipt-chain/output/evidence checks,
full DNA accounting and all 1,457,020 depth cells pass. All 11 product/default bytes,
ordered samples 0,2,3,4,6,9,10,11,14,17 and both TNF matrices agree with locks.
Native exact reload passes both pairs; Mac inference-only full-row replay differs
by at most8.94e-8 (predeclared2e-6absolute/1e-5relative platform tolerance). No feature
extraction, fit or reclustering ran locally. All native neighbor lists are retained;
128 fixed label-blind ID-hash queries/arm independently match exact cosine/tie order.

| Arm | Bins | Assigned bp | Bacterial 5-NN agreement | Whole-reference R95, bp weighted | Targets >=50% / >=90% |
| --- | ---: | ---: | ---: | ---: | ---: |
| raw ten-depth | 2,947 | 109,487,277 | 68.630% | 4.5765% | 6 /1 |
| learned ten-depth | 952 | 180,934,322 | 67.052% | 5.3911% | 13 /1 |
| raw TNF-only | 3,213 | 99,909,686 | 43.069% | 3.9312% | 5 /1 |
| learned TNF-only | 801 | 183,977,452 | 51.075% | 4.5597% | 11 /1 |

All four retain 56,661 below500 contigs /22,035,454 bp as excluded, and every
unassigned base. Geometry uses 25,543 attributable eligible bacterial queries;
unknown neighbors stay unconfirmed in the five-neighbor denominator. Bacterial
bp-weighted agreement is81.76→79.62% with depth,71.77→72.61% without. Overall
unweighted77.18→81.84% with depth is driven by49,520 eukaryotic queries versus 25,543
bacterial; it cannot be reported as a bacterial representation gain. Bacterial
agreement falls in every ten-depth length stratum, most in2500–9999 bp. Primary
restricted B3 recall nevertheless rises 18.48→37.61% with depth; that restricted
quantity counts excluded/noise as zero and is separate from all-bin R95 purity.

Frozen conservative R95 uses >=200kb bins, >=95% confirmed support, full 156 bacterial
provided-reference denominators554,661,890 bp and duplicate-safe coordinate unions.
Macro raw/learned: ten-depth4.9838→6.0264%, TNF-only4.5794→5.5352%. Only 102,790,342
unique bacterial source bp are confirmed in the full assembly: **18.5321% weighted /
19.2155% macro** source-availability ceiling; 38 targets have none,29 reach50%
availability and17 reach90%. This truth-supported ceiling is not biological
completeness or a guarantee that available bases can form a pure bin. N-quarantine
7,653,205 bp /3.3034% and cross-genome ambiguity42,402,631 bp remain unassigned support.
Whole provided MAG/scaffold lengths do not establish formal MIMAG quality.

Actual pinned AMBER API executes in the existing E005 local runtime after an actual
tiny native-export contract; all 20 f8b3a601 source-file hashes match before/after.
It scores 125,848 attributable contigs/165,477,813 bp, including non-target lineages;
19,854 contigs remain outside that view. Assigned-bin weighted purity in this
restricted view falls91.80→85.41% with depth,84.21→66.31% without. These are not
whole-DNA purity or whole-reference recovery. All 624 R95 genome records agree across
the native-AMBER evaluator path and separate retained-output review. No required
runtime/contract remains missing. The old unexecuted evaluator's column mismatch
(`exclusion_reason` versus native `reason`) was repaired/tested without editing
exports. A failed local checker attempt used zero-based bin names; its log remains,
and the corrected +1 export check passes in a fresh local review. No science retry.

**Subsequent owner-requested reassessment, 2026-10-16:**
[D015](../../docs/decisions/D015-coherent-prototype-upgrade.md) recommends incorporating
marker-conflict handling into a coherent next prototype alongside better sequence
views, modality learning and grouping. The frozen-encoder marker split is no longer
a required standalone milestone. The earlier narrow recommendation stays in the
immutable [review snapshot](controls-review.json) as its dated interpretation;
all measurements, source bindings and accepted artifacts remain unchanged.

Both modest bacterial geometry damage and mixed/fragmented grouping motivate a
broader candidate; this does not establish either as the sole cause. Reuse completed
reviews to implement related modules in one block, retain intermediates and choose
selective ablations where they can change the design. A bundle-level gain does
not prove individual ingredients necessary. No marker preparation, new code, fit,
score or cloud action occurred in this strategic reassessment. External binners
remain deferred; the next prompt authorizes local implementation only when used.

### Shutdown, retained evidence, costs and storage

GCP independently confirms **TERMINATED**, start 21:10:04.207 UTC and
stop 22:55:19.426 UTC October 15 (**00:55 October 16 Copenhagen**), no external IP,
unchanged 8 CPU/32 GiB and 30/300 GiB disks. Guest `e009-controls/status` and private
`completion.json` reportSUCCESS; closure binds actual launcher exit0 and result.
Provider STOP fallback was 01:25 UTC October 16, so stop occurred well before it.
The post-exit watcher snapshot remains only on the stopped disk; this collector
had closed/uploaded before watcher exit detection. Serial-output API refuses the
stopped instance. We do not claim a directly reviewed final watcher snapshot or
wake the VM merely to obtain one; success comes from stage evidence, not shutdown.

Private prefix `gs://dl-binner-archive-167650584170/e009/controls-cf7bf2a-20261015T211004Z/`:
control archive **484,269,399B**, SHA256
`3b3f50ba91f6552fb7c8b7b1b83d3d1a5ddec7f8771631e2dec95cd45e7199c3`,
**8,067 regular members /1,249,401,871 logical bytes**; all 8,066 inventory hashes pass.
Closure **447,655B**, SHA256
`50bd9ffda5a3fc4c01bf23e9d8a8065d9b97b9e2a86b76239e47699594b48725`,24members /
3,240,687logical bytes; every extracted member matches the checksum-bound tar.
Finder-created local .DS_Store files were absent from the tar and removed only
from this fresh extraction before review. Original cloud/native evidence untouched.
The native collection/readback and independent Mac checksum/member checks agree.

The new local review is also privately backed up under the same prefix at
`review-20261016/e009-controls-reviewed-20261016-v1.tar.gz`: **484,012B /77 regular
members /2,632,002 logical bytes**, SHA256
`aca28fbbc415576353e428f5a21ec6061100faf15e8be49db300f4f473fac764`. Upload/readback
and every inventory member hash pass. It retains closed diagnostics, code, failure
logs, local runtime and billing gates; no bulk DNA, credentials or environments.

Measured provider uptime **1.7542275h /14.03382 allocated vCPUh**, gross
**$0.478984 compute/IP** at freshly rechecked DKK E2 rates. Conservative export
<=484,725,419B at $0.12/GiB is **$0.054172**; small operations/rounding reserve$0.05
keeps the new phase under**$0.584**, below$2. Review used**$0 new VM compute**.
The existing disks add~$0.07497 during that uptime, separately within original
seven-day storage approval; do not double-charge a new provisioned disk. Welcome
credit now **DKK1,936.57 Available through 2027-01-12**. Overview cost/savings 31.92/net0;
credit-use 36.86 and unobserved pending usage are not a final phase invoice. Export
was admitted before download; no free-tier allowance was assumed in gross prices.
[Storage/export price](https://cloud.google.com/storage/pricing),
[credit coverage](https://docs.cloud.google.com/free/docs/free-cloud-features).

Inner launcher sampled minimum free**135.18 GiB**, maximum growth**2.78 GiB** through
collection, against 25 GiB reserve/20 GiB growth. Outer guard also included conservative
1.08 GiB preparation charge and private readbacks; final outer disk observations
were not exported, so exact stopped-disk occupancy is not claimed. Largest native
stage sampled process-tree RSS~1.06 GB; launcher tree~1.12 GB. Training uses ~7.53–7.54
CPUs for94–98s; fixed clustering~2.00–2.34CPUs for1002–1191s; features~1.06 CPU for
237–240s. These sampled process figures differ from charged8 vCPU uptime. Do not
assume proportional speedup or a smaller-node forecast. Local inference/accounting
review 118.91s/2.107 GB peak own RSS, native AMBER28.11s/0.585 GB; no training locally.

Retained controls cost~**$0.00903/month** regional Standard object storage. Existing
boot/work disks stay **$31.20/month gross even while stopped**. Retention review is
**October 21**, not extended by this review; no cleanup, new capacity or automatic
post-credit billing is authorized. Git holds compact summaries/code; bulk outputs,
checkpoints and archives remain private/ignored. Current budget does not authorize
the proposed next mechanism.

## Launch observation retained as history, 2026-10-15


**The four unchanged controls are launched once and left supervised per the owner's
explicit instruction.** [The actual control receipt](controls-observed.json) owns
full gates, source, environment, process/watchdog identity, current observations
and later result pointers. At **23:20 Copenhagen**, the ten-depth pair is preparing
features (native PID2260, ~100% of one CPU, 178s sampled process CPU); TNF-only is
queued. This finite Python TNF stage is serial despite the eight-thread setting.
Parent heartbeats alone are not credited as scientific progress. No operational
failure or competing scientific workload is observed; no control completion,
recovery score or feature-family conclusion is claimed.

VM start **21:10:04.207 UTC**, unchanged e2-standard8/32 GiB and 30/300 GiB disks;
initial filesystem free148,207,960,064B, later146,857,697,280B. Fresh live paid-account
Welcome credit **DKK1,942.67 Available**, expiry2027-01-12, certain-usage/net-pricing
scope. October1–15 cost/savings27.89/net0, issued-credit consumption30.76; billing
lag and unobserved pending usage remain explicit. Current DKK SKUs/ordinary E2,
PD/IP/Standard Storage eligibility pass. Compute/IP max4.25h is **$1.16045 gross**
inside the new **$2**; no extra resources/services or retention are introduced.
Actual priced uptime to observation is in the receipt, not a final invoice.

Mac normal push and VM clean source **cf7bf2a17eab0c5a2f70999d04e766af1e14f98a**
pass; GitHub access stays read-only. The admitted truth archive and exact dev3 wheel
have byte-verified restore into a fresh phase directory. Private truth upload and
SHA256 readback pass. Original data, DAG journals and truth artifact remain intact.
Fresh complete owned Python3.12 CPU env, all 16 distribution versions/import origins,
all 11 installed code/default hashes, pip check and actual CLI checks pass before
community work. No tiny binner fit or earlier scientific contract was replayed.

Parent service `e009-controls-20261015T211004Z.service` is PID1975, boot/start/command
bound. Root timer `e009-controls-watchdog-20261015.timer` is active, checks every30s
and requests clean shutdown after60s absence. Current Linux live/normal0/crash7
contracts and actual held-parent matching pass before release at 21:16:42.882 UTC.
The held parent retains identity while its one child launcher runs. Runtime/cgroup
cleanup and outer budget include time since boot; phase end **October 16 03:10
Copenhagen**, independent providerSTOP **03:25**, automaticRestart=false. No restart,
retry or limit extension. The existing 25-GiB reserve and20-GiB growth allowance
remain, including a conservative1-GiB preparation charge before the first baseline.

Logs on `dl-binner-gcp`:

- `/srv/dl_binner/experiments/e009/controls-phase-20261015T211004Z/logs/parent-terminal.log`
- `/srv/dl_binner/experiments/e009/controls-phase-20261015T211004Z/logs/launcher.log`
- `/srv/dl_binner/experiments/e009/controls-v1-20261015T211004Z/09-ten-depth.log`
- Native stage logs under `/srv/dl_binner/experiments/e009/controls-v1-20261015T211004Z/ten-depth/logs/`.

The parent plans private `controls-evidence.tar.gz`, checksum, closure and completion
under `gs://dl-binner-archive-167650584170/e009/controls-cf7bf2a-20261015T211004Z/`,
with readback verification before normal exit. It also best-effort publishes
compact status to the already-enabled guest attribute `e009-controls/status`.
A missing/failed collection must not be inferred successful from VM STOP. Inspect
actual receipts/checksums and budget before exporting bulk. Local-only diagnostic
evaluation follows accepted outputs and shutdown, with no new cloud compute.

Owner steering: **finish the response once this healthy supervised launch is
verified; do not repeatedly poll until completion**. The exact following inspection
prompt below supersedes the earlier launch prompt; no further execution approval
is needed merely to let this already-approved phase continue.

## Truth-v2 admission and then-prepared control boundary, 2026-10-15

**Truth repair succeeded locally; no fit, score, new alignment or VM wake ran.**
[The admission](truth-v2-admission.json) binds the new immutable artifact separately
from the original failed data DAG, which remains failed/unsealed. Accepted assembly,
BAMs, depth, source freeze, origin audits and all earlier evidence stay intact.
The predeclared [policy](truth-v2-policy.json), committed with the reader/tests at
`e60d1e3` before community derivation, keeps identity .99, paired bp >=200 and
contig attribution .95. All 300,499 rows are validated before filtering, including
required typed `cg/nn/NM`, exact axes/endpoints and minimap2 2.30's `blen+nn`
accounting. `=` can encode N:N while matches exclude it; the old equality test is
not retained. No malformed low-quality row is silently accepted.

Since PAF alone does not localize every ambiguous base, each **qualifying** nn>0
query span is globally unknown, even where a clean chain overlaps. This preserves
competition rather than dropping a chain to manufacture uniqueness. Of 191,509
qualifying rows, 158 are quarantined: **7,653,205 unique query bp /3.3034% of all
assembly DNA**. This is a prospective conservative uncertainty policy, not tuning
to a binner's result. Nonqualifying rows remain outside support by the frozen
thresholds. Gaps supply no paired support. Cross-genome overlaps remain ambiguous;
same-genome genuine multi-locus matches supply genome purity support only.

The actual 309 positive simulator genome IDs remain distinct. All nine separately
simulated pASV plasmids keep their HOST metadata; host-like filenames never merge
them into bacterial genomes. All ninety circular aliases are catalog-byte/DNA
verified exact unique forward rotations, normalized modulo molecule length with
wraps split on either query strand. They count as **nine physical molecules**,
not ninety repeated loci. All **7,688 competitive PAF aliases /7,607 canonical
records**, two zero-origin files and 1,280 unobserved replicons remain. The 156
bacterial primary targets retain **554,661,890 provided reference bp**, including
unassembled/unobserved DNA. Viral/eukaryotic/plasmid/zero-origin DNA remains in
competition and future all-bin purity denominators, outside primary recovery.

Whole-assembly accounting: 178,135,884 genome-confirmed bp; 42,402,631 cross-genome
ambiguous bp; 7,653,205 quarantined bp; 3,486,437 other unsupported bp. Within genome
support, 449,938 bp have unresolved repeated loci. The restricted AMBER truth view
has 125,848 contigs /165,477,813 bp (including non-target lineages); none is labelled
to a zero-origin genome. These are truth coverage counts, **not binner scores**.

The stdlib [new reader](../../scripts/e009_truth_v2.py) ran once successfully on
the Mac: **45.390 s**, sampled peak **0.494 GB**. An initial 0.022-s attempt failed
on sandbox permission for `ps` after launch and left no truth result; its failure
receipt is preserved. [The independent reader](../../scripts/e009_truth_review.py)
uses direct interval clipping and an independent raw-PAF oracle, not the production
parser/splitter/sweep. It verifies all serialized contigs/denominators and recounts
all 300,499 native rows; oracle results agree for **all 348 queries involving nn or
circular aliases plus 128 fixed SHA256-selected queries**, 476 total. Final review
52.941 s /1.220-GB sampled peak passes; its preceding review is also retained.
Six local truth tests cover real native failure bytes, source-supported N in
I/D/X/=, malformed rows, circular/reverse repeats, HOST/zero-origin/full-length
population and a random independent per-base oracle. No fresh tiny aligner was
invoked: actual retained native rows are the exercised writer evidence.

This admits **conservative supplied-reference alignment truth** only. Aligner
sensitivity, whole-span N uncertainty, MAG/scaffold provided-reference meaning,
near-genome/pretraining overlap and development-data status remain limitations.
No biological performance, final-evaluation independence or SOTA claim follows.
The raw artifact retains `scientific_truth_admitted:false` as derivation provenance;
the separate reviewed admission owns the later acceptance. Never edit the old
stage journal, original axes or frozen parser to make them appear successful.

The VM is still **TERMINATED**, without an external IP, disks 30/300 GiB and current
one-hour STOP. New cloud compute spend is **$0**; prior compute/IP ~$3.7288 and
seven-day disk planning exposure ~$7.1803 are unchanged, not a final invoice.
Stopped disks remain ~$31.20/month gross; retention review remains **October 21**.
No original data-clock time was consumed on GCP in this task (about 10.34 hours
conservatively remain). No capacity, service, key or quota change was made.
A fresh Console read timed out; no cloud write/spending was attempted. The last
credit display below is historical, not a newly verified balance. The checksum-
bound new evidence archive is retained locally; a private Cloud Storage copy/readback
can follow a successful fresh credit gate in the next approved phase.
The [new local evidence receipt](truth-v2-retained-evidence.json) binds
**5,218,978 compressed bytes /112 regular members /76,654,870 logical bytes**,
SHA256 `699cede72476a165bb3712d5368bd65ce1d9d543cc997b7604ff653d6c6dd761`.
All 111 non-inventory member hashes pass; the inventory is the remaining member.
It contains the admitted truth, closed reviews/failures/test receipts, source/policy
snapshots and the frozen wheel. Original assembly/PAF/depth inputs remain bound to
the earlier private archive instead of being duplicated. These source snapshots
precede adding this locator paragraph; the immutable artifact/admission bytes match.

## Earlier data review and failed DAG evidence, 2026-10-15

This section records the pre-v2 review. Its provisional truth boundary is resolved
by the separate v2 admission above; the original data DAG failure is unchanged.

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

**At this preceding review truth was provisional.** The then-required work was a fresh simulator-genome reference axis,
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

### Earlier control proposal (executed once under later approval)

The truth prerequisite is resolved. Recommend **only the unchanged four diagnostic
controls**, after a new **$2 incremental gross approval**. Two serial product calls
use immutable dev3 `5e54538`, seed 11, 20 epochs, cutoff 500 and fixed grouping.
They can distinguish raw-feature geometry, loss in this encoder and loss in fixed
grouping, with ten-depth versus sequence-only context. They do not determine the
product membership of depth/sequence/taxonomy. An external tool is still unnecessary.
Choose one matched mechanism after diagnostics; confirm on prospectively defined data.

[The bounded parent](../../scripts/e009_controls.py) is prepared and default-plan
only. It owns a fresh complete CPU env, exact package/default/distribution checks,
two serial runs and compact collection within four hours. It enforces 25-GiB free
reserve and 20-GiB growth allowance, stops/reaps children on failure and never
implicitly resumes. [Feature locks](diagnostic-feature-inputs.json) bind the
accepted full FASTA/matrix and ordered columns; [package locks](diagnostic-package-lock.json)
bind the actual 33,599-byte retained wheel and all eleven immutable source/default
files. Truth admission is verified separately and no labels enter binner argv.

Eight local safety tests pass with real **inert** children: serial placement,
shared setup/child/parent clocks, explicit approval/default refusal, intended
failure/timeout, reserve/growth sensors, and killed/reaped live child/orphan. Disk
growth sensor input is mocked; alarm delivery and process cleanup are native.
These are not Linux package installation, native scientific fit or scale/cost
validation. The exact retained wheel verification passes. Linux setup/import/CLI
probe must pass before the first fit within the new budget; it is not authorized
now. No GPU/runtime borrowing or whole product-contract replay is needed.

Proposed existing 8 CPU/32-GiB/300-GiB layout, four-hour phase/4.25-hour provider
STOP costs at most **$1.16045 gross compute/IP** at the last verified same-day
$0.27304568/h rate. This leaves the rest of $2 for compact archive/transfer/rounding.
10 GiB expected /20 GiB conservative additional disk is a ceiling, not a forecast;
exact kNN/sorting and graph grouping on 89,041 eligible contigs remain unmeasured.
Keep retention within the original October-21 review; no new ongoing capacity is
needed. Fresh prices/credits/headroom and the current approved commit are mandatory
before a wake; do not fund fits from the original data-only $20. A cap failure
preserves partials and triggers reassessment, not schedule or eligibility changes.

The launcher performs **no scoring**. The separate following prompt can authorize
bounded local diagnostic evaluation after accepted outputs/shutdown using tested
contracts, without another VM wake. Native AMBER runtime availability remains an
explicit check; do not install external binners or invent scores from partitions.
The [approval template](diagnostic-approval-template.json) is explicitly unapproved;
copy/populate it only after the human grants the following execution request and
the live credit/STOP/watchdog checks pass. Do not edit its `approved:false` now.

## Exact following-step prompt

The owner executed the prior local-implementation prompt on October 16. Dev4 now
belongs to [E010](../E010-coherent-prototype/README.md); its
[exact next execution approval request](../E010-coherent-prototype/OPERATIONS.md#exact-following-step-prompt)
is current. It proposes one separately budgeted candidate fit and reuses accepted
dev3 outputs, with no baseline refit or external binner. The earlier implementation
prompt remains in Git history; no accepted E009 result, lock, truth or journal is
rewritten by this handoff. Existing storage review remains October 21.

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
