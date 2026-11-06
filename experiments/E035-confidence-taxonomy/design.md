# E035: confidence-aware hierarchical information

Prospective design, November 6, 2026. Local implementation and engineering only.
No community annotation, fit, new score, bulk database or cloud action is admitted.
E034, E031/E032, older comparators and all failure journals remain immutable.

## Decision and the graph question

E034 did not test all-ten pooled weak support. Its per-sample min-support filter
destroys information that its later pool cannot reconstruct. Oral's 488 calibrated
observations / 487 pairs are evidence of sparse single-library support, not a
negative result for pooled links or graph learning. The most direct next native
information decision is a separate, cheaper all-ten **support ledger** audit before
committing to a large taxonomy reference. Prepare that path here, without running
it. Preserve MAPQ 20, identity 0.97, mate/insert/orientation/duplicate semantics;
pool independent library support before the three-template floor and retain the
support coordinates. Do not reopen E034 or promise links from ten times a count.

Meanwhile implement taxonomy as the stronger complementary information candidate.
It can connect biological context beyond short-insert contig ends, particularly
for fragmented genomes. It is not permission to abandon the graph question or
another larger model on the same inputs. Classification can be wrong, incomplete
or reference biased, so its use must be optional and conservative.

## Representation and information contract

Freeze the entire admitted E031 online encoder and its complete mode-specific
teacher/proposal ancestry. Cache actual fused **and sequence** vectors for each
available parent / four real DNA views using the exact restored model, context
tokens and, in E009 GLM only, actual coordinate-bound GLM bank. Require exact native
parent reproduction against retained vectors. Never substitute a parent vector
for a crop. Preserve the original model, buffers and RNG. This new adapter does
not fine-tune E031, restore its optimizer into new parameters, regenerate pairs,
or repeat an old bootstrap fit. New AdamW state belongs only to new modules.

Train a small residual adapter with separate intrinsic-vector, composition,
measured-parent depth and sparse hierarchical-taxonomy branches. Use partial
root-to-leaf paths; a parent annotation is explicitly parent context for its crop
views, not a measured crop classification. Parent depth is also parent context.
Confidence is a bounded evidence proxy from assigned/retained ORFs, agreeing
ORFs and MMseqs2 weighted support, not calibrated correctness. Retain raw rows,
every confidence component, no-hit, insufficient, partial and conflicting states.

Use a zero-initialized residual capped at 0.25 times confidence before unit
normalization. Taxonomically unknown/conflicting/no-hit/disabled and method-excluded rows return
their original E031 vectors exactly. Two equal taxa cannot force a genome merge;
the intrinsic vectors and an anchor penalty retain within-taxon distinctions.
No new taxonomic must-links/cannot-links, teacher or pair proposals are introduced.
Benchmark-unknown and non-target DNA can have classifier evidence and therefore
change vectors. Exact fallback depends on annotation availability, never truth.
Changed neighbors and partitions can also affect otherwise unchanged rows.
Use taxonomy dropout 0.25 only on annotated view contexts. Supervise hierarchical
conditional sibling cross-entropy, averaging observed ranks per parent, with
confidence on the original parent denominator. Do not allocate dense N-by-taxon
one-hot matrices. Retain sparse paths and batch/group conditional logits.

The additional objective combines hierarchical reconstruction, available-view
consistency, a fixed intrinsic anchor and explicit composition / measured-parent
depth reconstruction. Twenty epochs, seed 11, batch 256, four numerical threads,
64 hidden / 16 taxonomy dimensions, AdamW lr 0.001 / decay 0.0001. This is an
information-plus-adapter bundle, not proof of taxonomy causality. No loss grid.
The reference-free fallback is tested, not a second obligatory community fit.

Depth audit: frozen E031's `depth_evidence` is a **positive-profile** gate, not a
measurement-presence mask. This adapter deliberately inherits that gate and its
saved transform; it does not silently repair the historical depth treatment.
Measured all-zero profiles remain in `depth` / `zero_depth` and are distinct from
no depth table. Future diagnostics must report positive measured, measured all-zero
and unavailable depth separately. The frozen encoder also retains historical
E009/Oral filter priors. Neither this block nor E033's negative integrated bundle
isolates those choices. ORF votes can overlap and are not independent genes.

Full-tree qualification exposed repeated dense label-table gradient allocation.
The optimized loss gathers the exact union of sibling candidates once per batch;
all conditional denominators, coefficients and labels remain unchanged. The old
clear expression remains as a reference, with value/gradient equivalence tests.
This is an implementation optimization, not sampled negatives or a new treatment.

## Classifier

Initially pin MMseqs2 18-8cc5c and GTDB R220 species-representative **proteins**.
Use nucleotide parent DNA with the native translated taxonomy workflow, not source
genome IDs or benchmark taxonomic labels. GTDB-only absence means unknown, not
noncellular. MMseqs2 approximate LCA and ORF aggregation are distinct from our
model's predicted taxonomy. No annotation propagation is automatically added.
Release-specific source/metadata and actual tiny translated classification must
determine the final parser/command before the candidate lock is sealed.

Pre-freeze engineering resolution: retain the native contig ORF prefilter and
taxonomy defaults (ORF filter 1, sensitivity 2, E-value 1, approximate 2bLCA 3,
weighted majority 0.5), with prokaryotic translation table 11, four threads and
16 G target-split limit. The early tiny prototype disabled the ORF filter and used
sensitivity 4 / E-value 0.001; it is retained as engineering history, not the
community treatment. Six-frame fragments make unfiltered full-GSA search a poor
default. Use the source-supported contig workflow rather than paying for a
short-read-oriented override or silently filtering out short assembly DNA.
Native-proven zero-retained-ORF completion is explicit; missing positive-ORF
results still fail. No community annotations or outcomes informed this choice.

## Evaluation and learning value

Keep E032 construction, cached marker/refinement and all pre/post alternatives.
One common candidate for E009 no-GLM, E009 full-path GLM and Oral ten-depth/no-GLM.
Keep E023 10.4163%, E031's stronger construction contexts, E032 and native MetaBAT2
as unchanged references. No per-community version router. Database-assisted claims
must be distinct from reference-free and unseen-genome claims.

Primary R95 keeps all 156 / 799 full provided-reference denominators and all-bin
purity, conservative E009 v2 / 3.3034% N quarantine and separate Oral origin oracle
with known-shared sensitivity. Secondary assembly-conditional recovery, target
presence, represented-reference ceiling, fragmented versus singleton recovery,
length / origin / annotation / marker / eligibility / unassigned populations and
per-bin threshold tiers explain what the primary number cannot. No threshold
change, baseline rescore or use of evaluator labels in training. A large Oral GSA
singleton gain cannot stand for recovery of fragmented real assemblies.

Prospective joint KEEP: no mode loses R95 or T90 against E032; both E009 modes
also meet their stronger E031/E023 R95 and T90 anchors (10.6110% / 10 targets and
10.5684% / 9 targets); and at least one mode gains 0.5 percentage points R95 or
three multi-contig T90 targets against E032. This higher promotion bar is resolved
before any changed community outcomes, rather than settling for a weaker anchor.
MODIFY if
there is a gain with a cross-mode/unknown-stratum trade-off; ABANDON this adapter
if no mode improves R95 or multi-contig T90. These are practical scoped criteria,
not biological constants. Missing contracts remain unavailable, never zero.

Annotation yield is measured and reported, with no arbitrary 100-contig / 1%
admission floor. A genuine zero-information mode requires a byte-proven intrinsic
null closure and verified reuse of its accepted construction before execution,
not an invented fit or an erased result. This path remains a named native
admission dependency; ordinary partial annotation is part of the intended method.

## Boundaries

Existing source free space is not enough for the full GTDB proteins and derived
index. Do not silently substitute a smaller marker database or truth-selected
references. Prepare priced acquisition/index/search/fit/collection gates, including
an admission pilot whose failure closes the information question with evidence.
Old E034 $15 does not carry over. November 11 at 00:00 Copenhagen active storage /
November 18 automatic tail are unchanged. If a complete next execution cannot fit,
request a separate preservation decision. Skin and Oral GLM remain unrun.
