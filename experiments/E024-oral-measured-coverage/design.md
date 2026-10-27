# E024 design and the next information decision

Prospective design, October 27, 2026. No new community outcomes have been produced.
The [protocol](protocol.json) and [source freeze](source-lock.json) are authoritative
for the treatment; [E023's review](../E023-adaptive-density-bins/comparison-review.json)
and [information assessment](../../docs/evidence/2026-10-27-e023-information-and-recovery.md)
own the observed problem. Frozen E019/E022/E023 remain immutable comparators.
The original failed Mac portability/allclose evidence and its tolerance remain
unchanged. This block reads unchanged native vectors; it performs no portable
model inference and does not claim that the earlier failure is repaired.

## Why depth now, and what a matched latest-version test would require

The owner's concern is correct: E023 did not compare one identical latest learner
across two communities. E009 had measured depth, a frozen GLM prior and E022
marker-informed links; oral had E019 sequence-only learning. Community, length,
truth and training also differ. Neither a depth explanation nor a general latest-
model ranking follows from the between-community result.

[A small publisher-distribution audit](source-profile-limits.json) gives an
additional limit: all ten columns differ and all 799 sources vary, but **432**
sources are positive in just one sample; **565** share a normalized direction with
another source, at 12-decimal summary precision. There are 293 such directions,
with a largest group of 117 sources. These are source-table calculations, **not
measured contig coverage**, equivalent genomes or an allowed truth-derived K.
Absolute abundances, sampling, MAPQ and reference competition may differ. Depth
may primarily separate cohorts and still need strong sequence information within
them. Do not feed these tables into the pipeline or set bins/thresholds from them.
All ten measurements remain justified: choosing fewer can discard the only
positive column for some sources. The full-model matching question stays open.

Recommend **all-ten measured oral depth first, with fixed learning**, followed by
one new cached grouping result. This tests whether independent abundance improves
retrieval/source separation and recovery in the difficult oral community. It also
creates a reusable input for a later complete learner; it is not a compulsory
one-ingredient-at-a-time campaign. The E023 E009 grouping gain already demonstrates
that useful recovery was left downstream of its fixed representation.

| Option | Decision supplied | Main limitation/cost |
| --- | --- | --- |
| Measured depth + fixed E019 vectors, selected now | Can real abundance improve oral retrieval/grouping? | No depth-trained encoder or GLM effect; new retrieval bundle |
| Oral GLM without depth | Does the sequence prior help this sequence-only community? | Large extraction; still lacks the binner's multisample input |
| Depth + GLM + E022 learning together | How does the coherent latest feature/learning bundle perform on both? | New bank and training, substantial GPU time, bundle attribution |
| Full 2 × 2 GLM/depth campaign | Separate component effects | Not justified by a decision that currently needs four fits |

A later **single matched full-bundle comparison** is a reasonable stronger-model
step if the new information is useful or representation remains limiting. Freeze
one common candidate, exposure and downstream protocol, and preserve the existing
anchors. A full factorial study is optional, only if attribution could change the
design. This preparation does not authorize that comparison or turn the fixed-
learning test into proof of cross-community robustness. E021's mixed E009 GLM
gain and [DCVBin efficiency audit](../../docs/evidence/2026-10-25-dcvbin-efficiency-and-marker-learning.md)
remain evidence and alternatives, not oral measurements or permission to change
the frozen model/view semantics silently.

## Genuine coverage policy

Use the **exact accepted opaque-ID pooled GSA**, SHA256
`ecf1c24c01f3c9498c79703dfe82fff20422b907954f0b11ef4e87ea342ff65d`:
1,286,547 nonempty contigs / 1,669,981,123 bp. The two original zero-bp records
remain explicitly in input accounting, without invented DNA. Map all ten public
interleaved read objects in the frozen publisher order. No source IDs, simulator
coordinates, taxonomic labels or origin truth enter the scientific path. The
published source-genome BAMs still do not provide contig depth; see the accepted
[E014 assessment](../E014-multiview-reconstruction/depth-assessment.md).

Reuse pinned **strobealign 0.17.0** and **samtools 1.24** from the existing E009
environment, without reinstall/copy fallback. The
[pinned author documentation](https://github.com/ksahlin/strobealign/blob/v0.17.0/README.md)
distinguishes SAM alignment from `--aemb` abundance estimation. Use actual SAM
alignments, `-N 0`, paired/interleaved stdin and a reusable STI. The index profile
is the uniform read length measured from the first 500 pairs; refuse nonuniform
or unsupported 100–500 bp input, and require the entire stream to match. This is
a format/index gate, not a truth-selected length cutoff. All contigs are indexed.

Count **M, = and X** aligned read bases for primary reads with **MAPQ ≥ 20**, reject
unknown MAPQ 255, and exclude flags `0xF04` (unmapped, secondary, supplementary,
QCFAIL, duplicate). Do not require a proper pair. Base-quality threshold is zero;
deletions, skipped regions, insertions and clipping do not add covered reference
bases. Divide by the full original contig length, including uncovered/ambiguous
positions, with no edge trimming. Overlapping mates count twice. This is an
aligned **read-base mean**, not fragment coverage, breadth, uniquely sourced DNA,
per-base variance or measured window coverage. The
[samtools 1.24 manual](https://www.htslib.org/doc/samtools-depth.html)
supports the independently tested comparison; its `-Q` is MAPQ and `-q` is BQ.
Accepted E009 used MAPQ 0, so this is not a matched mapping-filter comparison.

Ambiguous equally mapping reads commonly have low MAPQ and contribute no accepted
support here; no arbitrary primary is treated as known origin. Retain the MAPQ
histogram and every exclusion/read counter. This filter does not prove exhaustive
unique sequence or correct mapping. Measured zeros are full successful streams
with zero retained aligned bases; missing rows/cells/failed producers are fatal,
never zero-filled. The old `depth_evidence` mask means at least one positive mean:
all-zero contigs remain measured/accounted, but supply no informative depth
distance/index vote. No variance is created. Column standard deviations across
parent means are normalization statistics, not per-base coverage variance.

## Acquisition, serial pilot and storage

Fresh HEADs/segment manifests still total **51,731,811,351 bytes / 48.18 GiB**.
Each ~5.17 GB object has five publisher segments. Swift DLO ETag is the MD5 of
concatenated segment-MD5 hex strings, **not whole FASTQ MD5**. Validate all 50
published segment MD5s while downloading; calculate whole-file SHA256 and MD5
separately, then validate complete gzip CRC, paired names, sequence/quality and
input/read-identity totals against primary SAM records. Publisher archive MD5s
for ~102.6 GB sample tar packages do not replace this direct-object contract.
The refreshed metadata helper also tests the required trailing-slash listing
endpoint; an unrelated/unfiltered response is refused, not accepted as metadata.

Use one full **sample 6** as the native pilot, then reuse its accepted summary
without remapping. The remaining nine proceed only if 1.5 × the byte-scaled
first-sample acquisition/mapping time, plus three hours for comparison/collection,
fits the original remaining clock. The pilot must have positive accepted support.
Runtime, RSS, index size, disk headroom and producer exits remain independent
gates. A projection is not a completion guarantee or permission to extend.

Use four mapper workers, one input-validation feeder, one summary process and
an allowance for two mapper I/O helpers within the existing eight-vCPU node.
Indexing uses six workers plus coordinator/I/O headroom; grouping stays at four
numerical threads. Linux affinity and serial DAG barriers bound the total.
The native pilot must record actual thread/CPU use; a thread cap is not throughput.

The selected path stores one compressed FASTQ, one index/reference copy and
O(contigs) sums. It uses **no full SAM, BAM, sort scratch or dense per-base files**.
After full-axis summary re-read and byte admission, record and remove only that
new raw FASTQ; retain publisher checksums, whole hashes, acquisition/mapper logs,
read counters, aligned-base integer numerator, contig length and mean. No raw
read is backed up by that receipt. Failures stay journaled and require assessed
recovery, never hidden redownload/remap of completed science.

The [resource plan](resource-plan.json) forecasts roughly **11–23 GiB** additional
working space, with a **24 GiB** hard cap and **25 GiB** free reserve. The index has
an **8 GiB** cap, plus the 1.64 GiB reference copy. Historic native minimum free
was 51.53 GiB, giving 26.53 GiB above reserve. This is not a fresh guest measure.
Before full release, measure actual space and enforce whole-allocation growth,
including setup, index, summaries, new features, both partitions, exported DNA,
collection and JIT caches. Do not promise that all ten retained BAMs fit; their
old 45–130 GiB serial estimate is avoided, not newly measured or disproved.

## GLM cutoff and small-community alternatives

[Exact retained-DNA workload audit](oral-workload.json) replays only the original
source-blind crop coordinates/availability for costing. It writes no bank or
features; its 500 bp totals exactly match the accepted E021 Linux full-bank reader.
Time and full-token figures below use actual native stratum probes, **not new
inference or measured full-bank runtime**. Tokenization recursively splits overflow
without truncation; minimum bp-chunk counts are lower counts, not actual token-
split totals. All figures include full parents and every available real crop.

| Minimum parent length | Parents | Parent bp | Available views | Exposed bp | Projected both-strand tokens | Projected GPU hours |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 500 bp | 508,763 | 1,443,827,664 | 2,470,549 | 2,366,088,186 | 994.3 million | 61.05 |
| 1,000 bp | 215,970 | 1,240,650,261 | 1,079,839 | 1,861,623,746 | 776.0 million | 42.94 |
| 1,500 bp | 123,037 | 1,128,118,673 | 615,181 | 1,611,530,729 | 666.1 million | 36.41 |
| 2,000 bp | 82,240 | 1,057,905,759 | 411,199 | 1,464,409,113 | 602.0 million | 33.45 |

The native probes actually processed **124 views / 2,211 chunks / 3,472,161
forward tokens** across length/view strata. Full-bank tokens are extrapolated;
the original 500 bp timing forecast was 61.05 GPU hours. Timing is device/recipe/
stratum-specific, not a speed ratio measured against DCVBin. Lowering batch cost,
changing strand/chunk exposure, parent-only vectors or a different extractor would
be explicit scientific/efficiency treatments, not cache fallbacks.

A 1,000 bp cutoff removes 56.3% of views but only 21.3% of exposed DNA and projects
29.7% less GPU time. At 2,000 bp, 83.4% fewer views still leaves 33.45 hours because
the longer parents/chunks dominate. These cutoffs remove **203.18, 315.71 and
385.92 Mb** of currently eligible parent DNA at 1,000/1,500/2,000 bp, respectively.
That does not establish that short contigs are unhelpful. A later core-only GLM
with explicitly non-GLM short recruitment is possible, but must preserve the
short DNA, account for its different treatment and use the full 799-reference
denominator. A cutoff sweep is not prepared or run here.

[One illustrative 100-genome workload](illustrative-subset-cost.json) selects the
100 lowest hashes of the fixed string `E024-cost-only-genome-subset-v1` plus each
provided genome ID, before any derivative outcomes. It contains 165,647 original
contigs / 229,580,556 bp, 66,455 eligible parents / 200,679,426 bp and **322,892
available views / 320,705,907 exposed bp**. The projected 134.6 million tokens /
8.04 GPU hours are much cheaper; selected full references total 284,141,521 bp.
This is a cost illustration, **not a selected execution/confirmation dataset**.
Truth is used for benchmark construction only, outside the feature pipeline.
It changes community complexity, abundance competition and full-reference scope;
it cannot support full-oral recovery, unseen-genome or general robustness claims.
Any later derivative needs a separately frozen protocol, all chosen references
including zero-origin cases, shared/non-target competitors and explicit full-799
context. Do not silently replace the original denominator with 100 targets.

At an illustrative $1/GPU-hour (not a quote/admission), extraction alone would
be about $61, $43, $36 or $33 for those cutoffs, or $8 for the illustrative subset,
before setup, bank transfer, CPU training, grouping and collection. E021's rough
9-hour E009 run is not an Oral cost estimate. Fresh GPU eligibility/availability,
prices, actual token/throughput/space gates and separate approval are required.
No Oral GLM work or GPU request belongs in the proposed $15 E024 phase.

Before discarding short DNA or choosing a truth-defined smaller community solely
for GLM cost, assess **extraction efficiency at unchanged exposure**. These forecasts
use E021's exact serial-view, batch-2 float32 recipe. Cross-view batching or another
faithful execution adapter might reduce overhead without removing DNA, whereas
DCVBin's different input/view exposure is not a measured speed ratio for ours.
Any later efficiency admission must preserve model/tokenizer/coordinates/strands/
pooling and test against the original numerical tolerance; no parent-vector crop
substitution, silent precision change or promised speedup. This is future work,
not a changed E024 candidate or an authorized GPU test.

## Safe cleanup versus temporary resources, and later reuse

No files were deleted or moved. The local audit measured **89.58 GB allocated**
under artifacts and **19.52 GB free** at its snapshot. Much of it is accepted data,
archives and numerical prefixes with linked consumers; a name suggesting an old
failure does not prove disposable. There is enough room for bounded preparation
and sequential review, so do not prune accepted evidence merely to reach a smaller
folder. The retained E021 inventory and E023 terminal snapshot likewise identify
no freshly verified, unneeded old native bulk. Recheck `df` and ownership/consumers
on the next authorized boot; do not assume cleanup savings or wake just to inspect.

Streaming avoids needing more storage in the selected forecast. A temporary
128 GiB balanced disk would cost about **$0.64 for 36.25 hours**, or **$2.95 for a
week**, using the [current official hourly disk quote](https://cloud.google.com/compute/disks-image-pricing).
It needs separate provisioning/quota/mount/cleanup approval and a measured peak;
even 128 GiB is not proof that the old worst-case retained-BAM plan fits.
Cleaning inside a provisioned disk frees space but does not lower its capacity
bill. Stopping a VM also leaves disks chargeable.

A separate temporary worker additionally needs a boot disk (~$0.06 for 36.25
hours), about 1–2 hours of setup/copy/verification (~$0.27–0.55 of extra compute/IP
at the planning rate), roughly 8–10 GiB of full-consumer inputs, and its own
source/runtime/watchdog/collection gates. Mapping-only needs fewer inputs.
A job-linked numerical prefix is not automatically portable: a complete admitted
restore or fresh complete environment and native loader checks are required, and
can exceed that setup estimate. Do not silently copy an executed linked venv.
[Same-zone internal transfer is free; cross-zone transfer is $0.01/GiB](https://cloud.google.com/vpc/network-pricing).
Original retained disks remain billable. Verified collection and actual **deletion**
of temporary resources, not just STOP, must end their costs. No such resource is
requested now; stop and reassess if the existing-disk pilot cannot fit.

Retaining all BAMs is a legitimate alternative, not prohibitively expensive
storage by itself. For example, a **200 GiB** temporary balanced disk for 36.25
hours is about **$0.99**. Archiving 45–130 GiB of BAMs in same-region Standard GCS
for one week would add roughly **$0.21–0.61**, before operations/soft-delete tail;
do not download those BAMs to this Mac (130 GiB internet export alone is about
$15.60 at the conservative GCS rate). Native sorting, simultaneous unsorted/sorted
data, upload/readback time and a 25 GiB reserve must still pass a measured pilot.
At the previously observed 404 GiB regional balanced quota, 300 + 200 GiB would
need at least **500 GiB** if no other consumers exist; recheck rather than assume.

That BAM plan could be cheaper than a later $4–10 remap if near-term window/
breadth/variance or alignment-filter studies were already selected. It would need
a separately expanded resource/storage request, approximately **$18–20 complete**
as a starting proposal, not merely permission to attach a disk. The old $8 storage
forecast does not automatically cover those extra retained objects or a later
soft-delete tail. The chosen next learner/information question uses parent means,
and a later matched E022 bundle also accepts those means; no such alignment-level
study is selected. Therefore choose the existing-disk summary plan now, explicitly
accepting the possible future remap. A retained primary-only BAM would still not
recover unreported alternative alignments or equal a changed competitive reference.

| Later change | Reuse of full-GSA measurements |
| --- | --- |
| Higher learner cutoff or a chosen genome/contig subset, same mapping reference/filters | Slice the full-axis summaries; no remapping. Keep full-reference competitive mapping semantics and all excluded DNA |
| Different normalization/grouping/learner with same parent means | Reuse the summaries with a new exact input/rebind receipt; no mapping needed |
| Different grouping of existing sample columns | Reuse existing measurements; any new read sample needs its own new mapping |
| Mapping against a reduced reference with competitors removed | Remap: primary choices/MAPQ/paired placement can change; filtered full-GSA BAM is not equivalent |
| Changed contig DNA/assembly, or newly demanded window/breadth/variance/filter information absent from summaries | Remap, unless suitable retained full alignments genuinely support that exact measurement |

A retained full-GSA BAM could be filtered to a learner subset while preserving
the original competitive placements, or support some new coverage/filter summaries.
Contig means alone cannot reconstruct per-base coverage/variance or new alignment
filters. This selected workflow deliberately keeps no community BAM, trading that
future flexibility for ~tens of GiB of savings. That tradeoff is declared before
acquisition; all-ten parent means remain useful for both later full-community and
small-derivative work. No truth-coordinate projection substitutes for mapping.
If a derivative also removes reads from nonselected genomes, full-community means
are not that different read population. Suitable full-GSA BAMs could support an
explicit read filter; without them, the changed read/reference/filter treatment
needs remapping. Merely restricting which contigs the learner consumes does not.

## Decision and confirmation boundary

The primary KEEP rule requires selected R95 ≥ **7.0077%** (retained E019 + 0.5
percentage points), at least **43** targets ≥ 50% and **33** ≥ 90%, with every
source/resource/full-population contract passed. MODIFY preserves useful mixed
information; the declared ABANDON condition rejects this frozen retrieval policy,
not depth as a product feature or the reusable data. Density-only versus selected
is a cheap retained comparison, without another fit or truth-selected bins.

Oral remains a provided-origin oracle with full 799 / 2,083,072,211 bp denominators,
known-shared sensitivity and all length/origin/eligibility/marker/unknown/non-target/
zero/excluded/unassigned populations. E009's conservative v2 / 3.3034% N quarantine
is retained context and is not rescored. Secondary HQ/MQ/LQ tiers have no RNA
checks and are not formal MIMAG HQ. No one result settles feature families.
The original unscored skin choice and its source/genome/replicon/molecule/host/
circular/taxonomy/near/pretraining/competitive/unique-versus-origin/evaluator/depth/
cost dependencies stay unchanged. Both inspected communities are development data.
