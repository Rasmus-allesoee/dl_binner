# Oral measured-depth value and actual payloads

2026-10-17/18. Read-only public metadata/header inspection; no bulk reads/BAMs,
mapping, aligner or depth generation. Local records are under
`artifacts/e014-multiview-reconstruction/metadata/` and will be checksum-bound in
the compact evidence inventory. The publisher is
[CAMI II Toy HMB](https://frl.publisso.de/resource/frl:6425518).

## Actual availability and bytes

Oral sample IDs are **6,7,8,13,14,15,16,17,18,19**, not 0–9. Ten direct compressed
interleaved FASTQ objects total **51,731,811,351 bytes (48.18 GiB)** by current HEAD.
The original Swift listing exposes dynamic-large-object manifests with `bytes:0`;
those are not empty read files. Followed object HEADs give the real payload sizes.
The larger FRL `gastrooral/sample_n.tar.gz` packages total **102,625,912,630 bytes**;
they contain additional outputs and must not be counted as FASTQ-only sizes.

An illustrative four-sample budget using **6,13,16,19** is **20,684,706,398 FASTQ
bytes (19.26 GiB)**, versus **40,927,873,589 bytes** for their complete sample
packages. This covers early/middle/late positions in the published sample list;
it is not proven maximally representative or a frozen science selection. All ten
would preserve more available between-sample abundance information and avoid
choosing a weak subset just to save a small compute cost.

FRL exposes **365 genome-named BAMs** in the pooled oral directory. All 365 actual
BGZF/SAM headers and binary reference dictionaries were decoded with bounded
range requests; the source assembly basename matches setup metadata in each.
The original Swift short-read manifest was paginated completely: **4,698 objects,
1,788 per-sample BAMs, 799 source genome IDs**. Its BAM paths are genome-named.
The inspected references are source records such as `CP019433.1`, while GSA IDs
are fragments such as `CP011071.1_from_10978_to_11234_total_257`.

**No matching per-sample BAMs mapped to pooled GSA contigs were found.** These are
simulator/source-genome alignments, not reusable contig-depth BAMs. Coordinate
projection using truth is not an interchangeable measured remapping of all reads
to our exact contigs and can import oracle origin/alignment information. Do not
silently adopt it as model coverage. The raw matching GSA is supplied, and its
sequence-only anonymous copy is independently checked here.

## Recommendation and bounded planning estimates

Use **sequence-only oral GSA in this block**. It tests a different community and
fragment-length population while E009 supplies accepted ten-depth development
data. Read mapping is a separate, much larger I/O phase and is not needed to test
the reconstruction/view bundle on this additional sequence domain. A GSA has no
assembly errors; neither this test nor absence of depth can establish read-assembly,
ten-depth, or unseen-genome performance.

For a later depth-enabled question, prefer all ten if a measured pilot and disk
admission make them affordable. First estimate index/sort/BAM coexistence and
mapping rate on an explicitly admitted small read prefix. Current rough planning
is 4 numerical threads on the existing 8-vCPU/32-GiB VM, 8–24 VM-hours for all ten,
3–10 hours for the illustrative four, and roughly 12–26 GB peak process-tree RSS.
These are uncertain estimates, not successful native gates or fit authorization.
At the current gross compute/IP quote, they correspond to about **$2.18–6.55** or
**$0.82–2.73**, respectively, before disk, export/storage/operations and margins.
Such a phase needs separate clock/cost/credit/retention admission; it is not inside
the current acquisition cap or automatically inside the proposed comparison.

Staging all compressed reads plus retained BAMs, indexes and sort coexistence
could need roughly **100–180 GiB extra**. Serial streaming one sample and retaining
only admitted BAM/depth outputs might reduce this to roughly **45–130 GiB**;
actual alignments/compressibility determine it. Last accepted VM free space was
129.55 GiB, leaving only about104.55 GiB above the reserve; that is historical,
not a fresh guest observation. Do not promise that the existing disk fits the
upper estimate or provision another disk without approval.

Means for 1,286,547 contigs ×10 samples are about **51.5 MB float32**, plus IDs and
text overhead. Ten dense per-base float32 tracks would instead be **66.8 GB**
before format/compression overhead. Generate contig summaries directly if those
are the admitted features; avoid dense tracks merely to produce parent means.
Read-derived window mean/variance would be a separate measurement contract.

No data were deleted or moved to GCS. Existing cloud disk retention remains
subject to the **October 21 review**, without extension. Public inbound data here
incur no new GCP cost; future ordinary GCP products still require a current
Welcome-credit coverage check, not an assumption based on old balance displays.
