# Depth measurement and standalone candidate construction

November 3, 2026. Source/retained-record audit for E032, not a coverage experiment,
external-tool run or causal attribution. The owner's ignored
`agent_context/depth_info_improvement.md` was reviewed, not staged. Exact inspected
commits/files are in [source-audit.json](../../experiments/E032-biological-candidate-selection/standalone-source-audit.json).
Every accepted input, depth table, result and failed journal remains immutable.

## Actual measurement mismatch and reuse

E009 `scripts/e009_data.py:mean_depth` runs samtools depth `-aa -q 0 -Q 0 -g 0x600
-G 0x800`: primary aligned M/=/X bases, MAPQ/BQ 0, duplicates/QCFAIL retained, no
edge/deletion/overlap trimming, full contig-length denominator and explicit zeros.
The ten competitive StrobeAlign assembly mappings are sorted/indexed BAMs on the
original disk. A new bounded native inventory checks current files/quickcheck/a
header; this is not another full hash/decode or re-summary.

E024 reuses the pinned StrobeAlign 0.17.0 route, but its streaming reducer requires
MAPQ >=20, rejects unknown MAPQ 255 and excludes 0xF04 (unmapped, secondary,
supplementary, QCFAIL, duplicate). It sums M/=/X with BQ 0, full contig denominators
and overlapping mates counted twice. Same mapper does not mean same measurement.
Crucially, `scripts/e024_alignment.py` tees SAM to BAM **before** that filter.
Oral private BAMs retain all emitted records/DNA/qualities, unsorted/unindexed.
They are not MAPQ-filtered BAMs. `-N 0` does limit emitted alternatives, which no
later summary can recover.

Fresh November 3 GCS metadata finds all ten declared Oral alignment generations,
**53,744,784,551 bytes** (~50.05 GiB), plus a separate 1,100-byte tiny gate BAM.
Do not count the fixture as an eleventh sample. Original E024 SHA/readback/full
decode receipts remain the payload proof; new generation/size/CRC metadata does
not claim another 53.7 GB decode. Retain ordered sample IDs 6,7,8,13,14,15,16,17,18,19.

Accepted Oral has 576,144 all-zero full-assembly rows / 341,271,658 bp, including
191,567 eligible parents. E009's 13 zero records / 3,258 bp are below eligibility.
These are measured zeros, not missing cells. MAPQ 0 can restore rejected aligned
bases, while identity/edge filters can remove support: the net new zero population
is **unknown until measured**. Related sources, mapping competition, length,
simulation/origin structure and learning/construction also differ. Existing
contrasts do not isolate MAPQ as the inverse-recovery cause. Neither mapper marks
duplicates itself, so differing flag rules need not imply many affected reads.

## JGI: actual source rather than only help text

Released MetaBAT v2.18 is `a51200652a8907629b83d63fa5fa6c2f6612d105`. Current
inspected cache `8eb96023ef627d1955c05e3aca348c84b8757914` is distinct. Existing E011
Bioconda MetaBAT 2.18 is a separate binary/build identity; retain its actual JGI
hash/help and real tiny outputs. No MetaBAT binner is executed in this audit.

- Defaults: identity 97%, MAPQ 0. Actual identity is exact matches divided by exact
  matches + substitutions + insertions + deletions. Soft/hard clips are absent
  from that denominator despite the help's “end-to-end” wording. NM/CIGAR or the
  optional exact reference supplies mismatch counters; M alone is ambiguous.
- Unsupported reads exclude secondary/QCFAIL/duplicate, **not supplementary**.
  An upstream primary-only filter must exclude supplementary explicitly. MAPQ 255
  is not automatically unknown/missing to the minimum-MAPQ check. The examined
  loop has no base-quality threshold or template overlap deduplication.
- Actual coordinate order is checked by reference ID/position, not merely SO.
  All BAM dictionaries must match names/lengths/order. Oral must be sorted first.
- Effective default edge trim is **min(75, average read length / 3)** at each end:
  150 bp reads normally imply 50 bp, not 75 bp. `--includeEdgeBases` disables it;
  short-contig fallback branches also need fixtures.
- Default within-contig variance uses the per-base buffer (including zeros), with
  sample `(N-1)` denominator in the unweighted path. M/=/X, including mismatching
  aligned bases, enter that buffer. The separate scalar path can subtract NM
  substitutions: `--noIntraDepthVariance` is not safely assumed to drop only a
  column. Keep the variance path and compare actual tiny outputs. Other tools
  may use population variance instead.
- `totalAvgDepth` is a corrected-length weighted aggregate, not an extra sample.
  Parse named mean/variance columns; no ordinary breadth column is emitted.
  `--showDepth` can create huge per-base files.
- `--pairedContigs` accumulates aligned-base support to mate reference IDs. It is
  not unique template counts or calibrated genome probability. Ambiguity, flags,
  orientation, double counting and link-degree normalization need separate rules.

Primary source: [MetaBAT v2.18 summarizer](https://bitbucket.org/berkeleylab/metabat/src/a51200652a8907629b83d63fa5fa6c2f6612d105/src/jgi_summarize_bam_contig_depths.cpp)
and adjacent `.h`/`BamUtils.h`, also verified from the exact local Git objects.

### Actual native tiny result (November 3)

[Retained observations](../../experiments/E032-biological-candidate-selection/depth-audit-reviewed.json)
bind JGI binary SHA256 `5b1885be35cf906151ef5693fa8cac57edc67a022ba4a5b60478e4ef1dfb618e`.
The controlled 500 bp contig / 150 bp-read fixture gives default mean **1.5** /
variance **3.7594**, MAPQ 20 mean **1.125** / variance **2.11466**, and all-edges
mean **1.2** / variance **3.36671**. Its zero-coverage contig is emitted as zero.
Default/MAPQ/edge observations match the source predictions. The no-variance
variant yields **0**, contradicting the simple scalar-path prediction 1.4925.
That mismatch is preserved, not relabelled as a passing production contract.
The released scalar `CountType / correctedLen` expression also uses integer
division before assignment to double; this alone does not explain the observed
zero here. Exact scalar/build behavior remains unresolved. Do not adopt that
flag/path as a common procedure without further tiny native diagnosis.

All ten current E009 assembly BAMs are present, sorted/indexed and pass quickcheck,
total **41,105,302,048 bytes**; one full reference header is retained. This does
not claim new whole-BAM SHA/decode or a community coverage recalculation. All
twenty BAMs together represent about 94.85 GB compressed, making in-region serial
reuse substantially more sensible than another acquisition/mapping campaign.

## Shared procedure: separate prospective information treatment

Reuse both complete-assembly alignments. Verify header/sample/NM axes; sort Oral
serially, then use one admitted JGI build and explicit flags/options for both.
A reasonable starting proposal is primary/non-QCFAIL/nondup (0xF04 excluded),
MAPQ 0, identity 97%, variance retained and explicit edge/weight settings. MAPQ
255 needs an explicit common rule. Freeze only after NM/CIGAR/clip/edge/zero/flag/
mate fixtures; this source audit is not full native admission. Preserve old/new
tables side by side. Remapping is unnecessary for a new summary of retained
placements; changed references/mapper/placement alternatives are separate work.

Read Oral BAMs in-region, one at a time. Streaming raw BAM to sort avoids another
full raw copy, but sort spool and final sorted BAM still coexist. A 40 GiB disk
with 25 GiB reserve is not automatically sufficient: measure the ~5.4 GB/sample
sort peak and retain no unneeded sorted duplicates. Rough planning: 2–8 E2 CPU
hours ($0.55–$2.18 compute/IP), plus task storage/operations/compact return; this
is not measured throughput or authorization to summarize twenty BAMs now.

Compact mean/variance/breadth and genuine coordinate-window summaries could be
reused by a future common learner. Parent means cannot recover window depth.
Changing depth changes teachers, pair proposals, students and grouping; it is not
an innocent cache rebind. E032 keeps its existing depth/learning bytes fixed.

## Standalone methods inspected

Observations apply to the pinned source/path, not every release or measured speed.

| Tool/path | BAM information | Candidate construction/selection |
| --- | --- | --- |
| MetaBAT2 | JGI means/within-contig variance; optional separate pair matrix | Probabilistic composition/abundance graph and iterative bins |
| COMEBin | Bedtools zero-inclusive coverage; actual parent/fragment means and population variance; edge convention | Leiden candidates with marker-quality partition ranking |
| SCGBinner | Mean/optional variance across real views | Leiden/k-means candidates; marker scoring and iterative extraction/rescore |
| SemiBin2 short-read | Bedtools mean/variance in low-sample path; multisample combined path uses means and actual split-half means | Infomap, optional marker-seeded k-means reclustering |
| SemiBin long-read | Declared embedding/depth context | Multiple DBSCAN outcomes and marker F1-like candidate extraction; not its short-read algorithm |
| CompleteBin | Current code counts mapped spans into per-base arrays then clips outliers and builds parent/window moments; spans are not CIGAR-exact depth | Staged clustering/refinement and SCG-guided candidate ordering/dereplication |
| DCVBin basic wrapper | First sorted BAM through VAMB-derived parser, TNF and GLM | Marker-copy K estimate, k-means (`n_init=50` here), later quality assessment |
| VAMB/TaxVAMB | PyCoverM trimmed coverage (10% each tail in inspected call), identity parameter; no variance in that matrix | Latent clustering plus optional marker/taxonomy-informed reclustering |

Primary examples: [COMEBin](https://github.com/ziyewang/COMEBin/blob/1b476a41fac893294c70212a869573a732560ce5/COMEBin/get_final_result.py),
[SemiBin](https://github.com/BigDataBiology/SemiBin/blob/f7c45dcbcdfa81e8fbc3e08b04c54683122e72d6/SemiBin/generate_coverage.py),
[SCGBinner](https://github.com/htaohan/SCGBinner/blob/d5ad239af9a1445f0e454c4d4aa9307b922961a9/SCGBinner/get_final_result.py),
[CompleteBin](https://github.com/zoubohao/CompleteBin/blob/07c5649270646a29dc027d6234d66b048fed6d45/CompleteBin/combine_cluster_derep.py),
[DCVBin](https://github.com/dengdengf/dcvbin/blob/732ee4257f7da200994f4c105e9dacbc74242883/bin/my_method.sh),
[VAMB](https://github.com/RasmussenLab/vamb/blob/b146fb610921aef1da8aed5d739f1ce80d21b33a/vamb/reclustering.py).

E032's source-blind generic pool/rule is a plausible standalone binner component.
Its particular heuristics were developed on these communities and remain exposed
to development overfitting. Source precedent is not transfer validation. Keep one
policy, prospective criteria, all losses and unscored skin. Do not turn this into
an indefinite series of selector adjustments.

## Missing signals and broader direction

Variance/breadth/window profiles can expose weak support, repeats or mixed regions
hidden by means. GC bias, mapping ambiguity, sampling and short contigs also create
variance; a scalar does not locate a boundary. Read-pair links can connect weak
fragments, but repeats/chimeras/ambiguous placement/double counts can create false
edges. These signals need reliability/exposure contracts, not indiscriminate use.

After this one E032 block, provisionally favor a **common BAM-derived multiscale
information/representation upgrade** if the recovery gap persists. Harmonize the
measurement within that block, assess genuine window exposure/uncertainty and
implement one coherent core learner/proposal upgrade. Efficient Oral GLM remains
complementary. A Transformer alone cannot add missing coverage or make inconsistent
availability comparable. E032's reviewed outcomes may change the priority. Skin
stays unscored pending source/genome/replicon/molecule/taxonomy/overlap/ambiguity/
unique-versus-origin/depth/protocol/cost admission; no new DNA is acquired here.

Later the same day, [E032's completed review](2026-11-03-e032-construction-and-information-priority.md)
confirms that priority: most of the large Oral gain is associated with intact
single-contig bins, while the E009 multi-contig gap persists. This changes the
next-block decision, not the frozen measurement bytes or the unmeasured zero-depth
counterfactual. No further selector coefficient is chosen from those outcomes.
