# E035: taxonomy source contracts, pooled support and the evaluation foundation

Reviewed November 6, 2026. Scope: local source/metadata/native engineering and
reassessment of accepted E034/E033 evidence. No community annotations, new fits,
scores, bulk protein database or paid execution. [E035](../../experiments/E035-confidence-taxonomy/README.md)
owns implementation, receipts and prospective protocols; [reassessment](../../experiments/E035-confidence-taxonomy/reassessment.md)
owns the detailed recovery/policy decision. Earlier E034 sources remain unchanged.

## Source report and inspected implementation

[TaxVAMB's publisher paper](https://www.nature.com/articles/s41587-026-03098-0)
and the inspected VAMB source at commit
`b146fb610921aef1da8aed5d739f1ce80d21b33a` support hierarchical annotation as
complementary biological context. Inspected `vamb/taxvamb_encode.py`,
`vamb/taxonomy.py` and `vamb/encode.py` implement conditional hierarchy and
composition/abundance context, not an automatic taxon-equals-genome rule. Direct
publisher access was restricted; the indexed publisher text and pinned code,
rather than an assumed complete supplement read, support this interpretation.
The source is retained in the ignored E034 next-source audit and its provenance.

Our interpretation is to test a bounded optional residual around **frozen strong
E031 actual crop/parent heads**, not copy the whole TaxVAMB VAE or automatically
propagate Taxometer labels. Partial paths, uncalibrated support, missing/conflicting
states and intrinsic within-taxon distinctions are essential. Ground-truth origin,
source headers and evaluator taxonomy never provide annotations. Reference-assisted
performance cannot establish reference-free or unseen-genome generalization.

[MMseqs2 release 18-8cc5c](https://github.com/soedinglab/MMseqs2/releases/tag/18-8cc5c),
its [taxonomy documentation](https://github.com/soedinglab/MMseqs2/wiki) and the
pinned [`aggregatetax.cpp`](https://raw.githubusercontent.com/soedinglab/MMseqs2/18-8cc5c/src/taxonomy/aggregatetax.cpp)
define translated contig classification, approximate LCA and ORF aggregation.
The raw eight columns preserve retained/assigned/agreeing ORF counts and weighted
support. They are not eight independent measurements or calibrated correctness.
The frozen heuristic combines weighted support, consensus and assignment fraction.
Native ORF filtering can omit a query entirely; the real query lookup and swapped
ORF-header index prove a zero-retained-ORF complement. Missing positive-ORF rows
still refuse. A no-hit N-rich query can retain an unassigned ORF; the tests preserve
that distinction instead of inventing zero-ORF status.

Freeze native contig defaults: ORF filter 1, sensitivity 2, E-value 1, approximate
2bLCA mode 3 and weighted majority 0.5, translation table 11, four threads and
16 G split-index budget. These replace an early tiny short-read-style override
before community outcomes. The exact full command and schema live in code/locks.
Actual macOS translated classification and streamed nested-gzip reference building
pass; the downloaded Linux binary has only been byte-verified, not executed.

[GTDB R220/220.0 publisher listing](https://data.ace.uq.edu.au/public/gtdb/data/releases/release220/220.0/)
and [license](https://gtdb.ecogenomic.org/licenses) are pinned independently of
benchmark origins. Both small taxonomy files pass publisher MD5 and new SHA256.
Their tree contains 596,859 accessions / 146,381 nodes, maximum 1,070 siblings.
Species-representative proteins are 71,733,563,809 bytes, with known publisher MD5;
only HEAD and a 4,096-byte range were read. Whole SHA256, member/genome-ID inventory,
actual classifier reliability, full-index peak/RSS and throughput are **not admitted**.
MMseqs2 is MIT; GTDB is CC BY-SA 4.0. Derived reference/annotation redistribution
must retain applicable attribution/license and reference-overlap limitations.

## Direct engineering observations

The full real metadata hierarchy exposed repeated full-table gradient allocation
in the first clear conditional-loss implementation. Gathering each required label
union once per batch keeps every sibling/denominator; small-tree losses and all
gradients match the retained reference expression. The actual full-tree synthetic
probe improves mean update time from 2.6041 to 0.4618 seconds on this Mac, with
exact model/Adam state and reload. This is neither GCP throughput nor biological
performance. Linux full-shape admission still controls the complete future plan.

E031 `depth_evidence` is a positive-profile mask, not measurement presence. The
adapter inherits it explicitly so this block does not silently change depth
treatment. Measured all-zero data remain in the original depth/zero-depth arrays;
future diagnostics must distinguish them from missing modality. The rejected E033
integrated bundle does not isolate this policy or reject BAM-derived information.

## Why pooled support comes before a large reference

E034's implementation applies three-template support within each sample before
pooling. An actual tiny BAM counterexample has two unique templates in each of
two libraries: neither old sample emits an edge, while the new prospective pooled
ledger emits four-template support. E034 deleted its below-threshold spool, so
its output cannot answer all-ten pooling without new retained-BAM readers.
Keep the old refusal unchanged. The new rule retains the same mapping/identity/
mate/insert/dedup semantics and applies support only after all ten libraries.

[METAMVGL source](https://github.com/ZhangZhenmiao/METAMVGL) uses different default
MAPQ/identity and combines a separate assembly graph. Together with the retained
UnitigBIN/GraphMB audits, it supports keeping the information question open, not
copying thresholds until a graph passes. Joint screening and read-length/overlap
counters plus compact endpoint spans will help distinguish policy and assembly
limits. Dominant-contig labels are not localized mate truth; endpoint envelopes
are not gap-free CIGAR support. Even a useful graph is not yet a recovery gain.

## Evaluation and recommendation

Hand-computed tests exercise the unchanged conservative evaluator: absent full
references, separate replicons, duplicate-safe unions, unresolved bin DNA,
minimum-bin size and malformed axes. Accepted target-table arithmetic finds
confirmed represented reference fractions of **18.5321% E009 / 80.1691% Oral**;
the full 156/799 denominators stay unchanged. These are upper representation bounds,
not attainable R95. Oral's many intact singleton genomes and origin-oracle truth
also prevent a simple same-metric interpretation as E009's real assembly/v2 truth.

Recommend the separately priced **$4 all-ten information audit first**, while the
taxonomy candidate is already implemented/locally tested and its proposed $50
full-reference comparison is explicit. This resolves a consequential untested
policy before spending on a roughly 67 GiB reference. A useful reliable graph
supports its separately frozen recovery comparison; continued sparse/ambiguous
support strengthens the case for the prepared taxonomy path. Neither outcome
licenses score-selected edges, per-dataset routing or another automatic method jump.
No gain is guaranteed. Skin confirmation, Oral GLM and selection optimality remain
explicit later dependencies; November 11/18 are not renewed by preparation.
