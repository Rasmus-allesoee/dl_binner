# E024 execution admission and reusable alignments

October 27, 2026, before new outcomes. The owner authorized prepared `f7083b2`,
then expressly permitted storage changes, safe verified cleanup, a possible
SemiBin2 reference and a small ceiling increase. This prospective amendment
supersedes only the mean-only retention choice and raises the complete gross
ceiling to **$16**. Original learning, mapper/filters, ten ordered samples,
retrieval/selection, criteria, 36-hour cumulative clock, 36.25-hour STOP, original
VM/disks, 26 GB RSS, 24 GiB working allowance, 25 GiB reserve, 2 GiB compressed
internet return and November 4, 00:00 Copenhagen boundary remain unchanged.
No changed community result was available when choosing this plan.

## Chosen retention: full emitted primary BAM in private GCS

Keep the original unfiltered emitted SAM records, including unmapped reads,
sequence, qualities, mates, flags and MAPQ, as **unsorted compressed BAMs** in the
existing private Iowa bucket, one per sample. Tee before E024's MAPQ/flag filtering;
all scientific means use the same original SAM stream. `samtools view -@ 0 -b`
uses one encoder CPU; mapper, feeder, summary, encoder and bounded transport share
the same eight-CPU affinity/cgroup. No SAM/BAM spool or coordinate-sort files are
written on the work disk. Native streaming upload is write-once, capped at
**13 GiB per sample / 130 GiB aggregate**. Full SHA256/byte readback and an actual
complete samtools BAM decode/record count must pass before raw FASTQ release.
A failed backup is a failed sample, never silent mean-only success. Preserve raw
and failure evidence; no automatic retry or overwrite.

These BAMs are reusable alignments, **not sorted/indexed SemiBin2 inputs yet**.
Restore one at a time on a later authorized GCP allocation, sort/index, then
consume or reseal them. This defers sort cost until a concrete consumer needs it,
without another read download or alignment. Full alignment decode is deliberately
part of this run's pilot cost. No missing/corrupt BAM can be reconstructed from
its inventory. The compact science archive contains backup receipts and exact
remote byte identities; it does not contain the BAMs.

## Alternatives and costs

Planning ranges below are unmeasured until sample 6. All prices are gross list
estimates, distinct from credits/invoices. Ordinary first-party GCP products only;
refresh live coverage/prices before boot. Forecast at $0.02 per GiB-month for Iowa
Standard, $0.10 per GiB-month for balanced disk; internet export $0.12 per GiB.
Existing approved disks continue to cost about $31.20 per month while stopped.

| Option | Additional storage and quota | Transfer, duration and added cost | Reuse and limits |
| --- | --- | --- | --- |
| All ten coordinate-sorted BAMs on a disk | About 45–130 GiB BAM, plus active sort and index/reference/raw coexistence. Historical free space above reserve is only 26.53 GiB. A temporary 128–200 GiB balanced disk may be needed; 128/200 GiB plus current 300 requires quota 428/500 GiB, above the current 404 GiB. | Same-zone transfer free. Disk for 36.25 hours: about $0.64/$0.99; seven days $2.95/$4.60. Sorting/verification approximately 1–4 hours ($0.27–1.10) remains unmeasured. Another worker also adds boot, setup/copy and runtime admission. | Good for supported BAM consumers and new window/variance/filter summaries. Deleting that disk destroys its files; only a separately byte-verified GCS copy survives. STOP alone does not delete or stop disk billing. |
| Sorted BAMs in existing GCS | Same 45–130 GiB remote, one active sample and sort scratch locally; no GCS disk-capacity quota increase, but on-disk sorting can breach E024's fixed 24 GiB allowance. | Upload/readback roughly 90–260 GiB internal traffic, no same-region transfer fee. Seven days storage about $0.21–0.61, plus ordinary operations and sorting CPU. WAN export $5.40–15.60 would exceed the return scope; keep BAMs in GCP. | Same alignment flexibility; restore and index before use. Sorted files are not a new competitive reference or recovery of unreported alternatives. |
| Genuine SemiBin2 Strobealign-AEMB files | Compact split-reference abundance TSVs, roughly 0.1–0.5 GiB for ten samples; separate split FASTA/index. Size/time not yet measured. | Additional AEMB mapping to split contigs, approximately 0.5–3 hours ($0.14–0.82), not a rename of the existing table. Small storage/transfer. | Supports SemiBin2's >=5-sample abundance route when produced by its actual split/reader contracts. Not alignments; cannot recover variance, new windows/filters or ordinary BAM consumers. |
| E024 means alone | Roughly 0.3–1 GiB summaries/matrix, plus features; no new disk/quota. | Negligible incremental storage. A later remap repeats 48.18 GiB public acquisition and an estimated $4–10 mapping allocation, subject to a new pilot. | Our parent-depth features and fixed-reference learner subsets. Not a supported SemiBin2 abundance file and cannot reconstruct per-base/split coverage. |
| **Selected: unsorted full-primary BAMs in GCS plus unchanged means** | **45–130 GiB remote**, 13 GiB per-sample cap, no new local BAM/sort space or quota/resource change. | Same-region streaming upload/readback, plus native decode, are within sample-6 measured forecast and the original clock. Worst new storage/ops reserve **$0.80**, complete forecast **$15.30125**, ceiling **$16**. Future sorting is separately costed; no WAN BAM export. | Retains alignment flexibility now; a later BAM consumer pays sort/index CPU/working-space cost, not a second mapping. |

The original $8 retained-storage forecast stays scoped to its original assets.
New BAM storage through November 4 is attributed to E024's new allowance. At the
130 GiB maximum, ongoing storage is about **$2.60/month / $0.086/day**. Review
retention by November 4; no renewal or automatic destruction is authorized. The
bucket's seven-day soft-delete policy would add about $0.61 after deletion at that
maximum; it is not permission to retain indefinitely or assume automatic deletion.
No temporary disk is selected, and no new capacity/quota is requested.

Full-GSA BAMs and means can be sliced for a higher learner cutoff or selected
contigs while retaining original competitive mapping semantics. A changed mapping
reference, new read population or missing alternative alignments can require
remapping. BAMs support many new measured windows/variance/filter questions; means
alone do not. GLM extraction itself needs DNA, not BAMs, but future hybrid learners
can reuse the measured depth or derive genuine window information from BAMs.

## SemiBin2 recommendation and correct mode

[Author usage](https://semibin.readthedocs.io/en/stable/usage/) and pinned
[v2.4.1 source](https://github.com/BigDataBiology/SemiBin/tree/v2.4.1) distinguish one
assembly with several BAMs from concatenated independently assembled samples.
For E009 or pooled Oral, use **`single_easy_bin --self-supervised`**, short reads,
the actual assembly and its ordered ten sorted/indexed BAMs. Do not use
`multi_easy_bin` or a habitat-pretrained model with multiple BAMs. Default native
length eligibility, self-supervised schedule/reclustering and one prospective seed
need freezing in a separate external-reference protocol; no taxonomy/MMseqs DB.
The advertised minutes can refer to prebuilt-model use, not this trained case.

The [supported AEMB route](https://semibin.readthedocs.io/en/stable/aemb/) maps reads
to SemiBin's split contigs, then bins original contigs with ten genuine abundance
files. E024 full-parent MAPQ-filtered means are not those inputs. BAM extraction
uses real edge-trimmed/split coverage; no parent mean may be substituted for halves.
Native existing E009 BAM availability, full hashes, headers and quickcheck are
required on this approved boot; the forthcoming receipt owns the actual result.

**Defer a SemiBin2 fit from E024.** First complete the missing-information decision
on Oral and retain reusable alignment data. E009 is the cheaper first future
reference: its existing ten BAMs avoid acquisition/mapping and its primary R95 now
exceeds retained MetaBAT2, so a stronger reference can identify remaining targets
recoverable by a mature pipeline. Allow roughly 1–4 hours CPU, 8–24 GB RAM and
5–15 GiB extra including independent environment/features/pre/post bins: about
$0.27–1.10 compute/IP, or $1–2 complete with setup/return reserves, unmeasured.
A full native pilot is still needed; no fast-runtime claim is made from source.

Oral is more directly relevant to its regression, but is about 1.67 Gb / 1.29
million contigs versus the much smaller E009 assembly. Forecast roughly 4–12 hours,
16–32 GB RAM, 10–30 GiB scratch plus one sorted BAM at a time, $1.10–3.30 compute/IP
or $3–5 complete before further resources. Both would cost about $4–7 with setup
and uncertainty, could breach the current RAM/disk/clock, and create a broader
campaign before the Oral depth result. These are planning ranges, not measured
scalings. After E024, choose one reference only if its target/length recovery can
change the next learning/grouping decision. No external installation/fit runs now.

## Native cleanup and remaining admission

Inventory original experiment ownership, consumers, open/running processes and
large candidates on boot. Delete only exact verified regenerable unused temporary
or duplicate files, retaining an identity/regeneration/removal ledger and compact
failure evidence. Do not count hoped-for cleanup in admission; do not remove the
E009 BAMs, accepted banks/caches, transferred runtime dependencies or unique outputs.
Current retained assets do not become disposable because a compact manifest exists.
The native receipt records actual headroom and any deletion; local preparation
has deleted no historical files.
