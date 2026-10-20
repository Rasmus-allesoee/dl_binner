# E017 prospective information-aware grouping

2026-10-20, before any changed community grouping or scores. Local implementation
and engineering fixtures are authorized; community execution is not. E016 learning,
its native vectors and all accepted evidence remain immutable.

## Problem and one coherent treatment

E016 improves final recovery but worsens short-contig neighborhoods, and its oral
CPM parent needs substantial E013 refinement. The current initial graph uses only
learned vectors and gives every eligible contig equal authority. Test whether
using retained raw composition and measured depth directly, with long-contig cores
and conservative recruitment, makes more useful genome groups. This is a grouping
bundle, not a causal test of each ingredient or proof that learning is sufficient.

Use the original eligible/evidence population (currently >=500 bp with usable TNF).
Only >=2,500 bp contigs with native unit vectors enter the core graph. Shorter
eligible contigs and unsupported long contigs remain recruitment candidates;
<500 bp or featureless DNA remains accounted as excluded, without inventing
embeddings. This cutoff is a prospective grouping-reliability choice, not a new
training cutoff or a product ban on short contigs. No truth, taxonomy, K or marker
multiplicity chooses cores.

1. Retain native learned unit vectors. Raw composition is sqrt(TNF), so squared
   Euclidean distance is twice squared Hellinger distance. Depth is log1p of the
   measured parent means, divided by core-population column standard deviation;
   constant columns are absent, and an all-zero row supplies no depth evidence.
   These are between-contig observed means, not measured per-base/window variance.
2. Calibrate learned/composition distance scales using up to 8,192 deterministic
   source-blind core pairs: median strictly positive squared distance, with an
   explicit constant-channel floor. Use equal scaled learned/composition channels
   in one joint approximate core index. Depth reranks affinities rather than
   inserting fabricated values into a missing-depth index. One fixed 60-candidate
   index, 30 retained neighbors, seed 11; exact readers/reranking and a fixed sampled
   recall audit must pass. No grid or fallback index is allowed.
   This audits retrieval in the joint learned/composition index, not global
   nearest profiles or depth-aware affinities; those may have missed candidates.
3. Combine exponential learned/composition/depth affinities with an available-
   channel weighted mean of normalized squared distances. Composition weight is
   sqrt(r_i*r_j), r_i=N_valid/(N_valid+2500); learned weight is 1, depth weight 1
   only when both rows have usable measured depth. This reliability is a finite-
   length heuristic with overlapping fourmers, not an independent-count confidence
   interval. Multiply the resulting affinity by sqrt(r_i*r_j), symmetrize by max,
   admit an edge only when learned and composition distances are strictly below
   their background pair medians, native cosine is positive, and measured depth
   (when available for both) also agrees better than its background median. This
   explicit background gate avoids forced weak edges in small or diffuse cores;
   it is a conservative heuristic, not a calibrated same-genome probability. Then
   retain positive edges and apply the sole CPM rule median(edge weight)/30,
   node sizes 1, seed 11, two Leiden iterations. Existing 2-contig/10-kb support
   remains. Save every directed candidate/channel distance and sparse final edge.
4. From supported cores form fixed length-weighted profiles, without any truth.
   For each available modality retain the 95th percentile leave-one-contig-out
   squared distance to its core profile. Floors are 1% of the global pair scale,
   preventing exact duplicate/small cores from having zero numerical envelopes.
   These are empirical spread proxies, not biological error probabilities.
5. Query the same fixed core index once for each unassigned eligible contig; no
   propagation, iterative merging or new centroid index. Score candidate bins by
   available-channel profile distance / envelope. Inflate learned/composition
   envelopes by max(1,2500/max(N_valid,1)) for finite-length uncertainty; do not
   inflate measured-depth spread using an invented coverage-variance model.
   Require at least two distinct positive-affinity supporting core contigs, >=2/3 of affinity-weight
   support, best average normalized distance <=1 and best <=2/3 runner-up distance
   (a sole candidate has no runner). Otherwise explicitly leave the contig
   unassigned. Save all offered scores, votes, gates and reasons. A short contig
   cannot alter profiles or recruit the next contig. Markers are not cannot-links.
6. Apply unchanged E013 refinement once to the recruited parent, using original
   vectors, retained calls/genes/domains and measured parent means. Preserve core,
   recruited-parent, old-refiner and E013 partitions and all alternatives. The
   panel/partial-call/same-genome-locus/replicon limitations remain. No detector,
   encoder inference, training, feature extraction or baseline rescore is allowed.

## Evidence and serious alternatives

[MetaBAT2's primary methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC6662567/)
support length-dependent composition reliability and distinct graph/recruitment
stages; its probabilistic TNF/coverage formulas are not copied or calibrated here.
Retained native 2.18 help/protocol confirms main minContig=2500, allowed >=1500,
minSmallContig=1000 (allowed >=500), plus native depth filters. Thus the accepted
MetaBAT2 whole-tool result has different eligibility from our 500-bp learned
population; it is not a matched cutoff/component ablation. Keep all length and
native-eligibility strata and full 156-reference denominators; no historical score
changes or inferred matched-cutoff win. Longer contigs give more stable TNF and
reduce graph noise; short DNA can still contribute recovery when recruited safely.

Author [SemiBin grouping source](https://github.com/BigDataBiology/SemiBin/blob/b06c7d53bef28f46cb7030845913279f94dfa6bf/SemiBin/cluster.py)
combines raw/learned graph evidence and length information. Its KL abundance path
needs measured variances we lack. [CPM's native documentation](https://leidenalg.readthedocs.io/en/stable/reference.html#cpmvertexpartition)
explains density semantics; changing edges/cores changes the bundle, not the frozen
single gamma rule. This design is our unvalidated synthesis, not method parity.
A raw-TNF-only replacement, representation/context upgrade or full MetaBAT-style
probability calibration are serious alternatives; one coherent information-use
block is justified now by E016's grouping interaction and available feature caches.

## Prospective decision and limits

Compare only new E017 on E009 ten-depth and oral sequence-only with retained E016
CPM/E013 summaries. Keep provisionally if both post full-reference weighted R95
endpoints do not decline, at least one improves by >=0.5 percentage points, neither
>=90%-recovered target count declines, and integrity/full-population contracts pass.
Modify if useful target/recovery gains coexist with endpoint/population losses;
abandon this bundle if neither endpoint nor >=90% count improves, or if the
label-free assignment/core contracts fail. A failed engineering gate invalidates
execution, not a biological family. Report all target/length/origin/eligibility/
marker/unknown/non-target/excluded/unassigned effects and core→recruit→old→E013
interactions; no hidden loss or per-bin oracle. Do not retune after outcomes.

Use unchanged E009 conservative v2 (156 full references, 3.3034% N-quarantine)
and separately named oral provided-origin oracle (799 full references, known-shared
mask sensitivity), without pooling scopes or claiming unique support. Both are
development. Skin confirmation remains frozen, unacquired and subject to full
source/genome/replicon/molecule/taxonomy/overlap/ambiguity/unique-vs-origin truth,
unchanged candidate/comparator protocol and separate acquisition/cost admission.

Local engineering correction before community execution: the first exponential-only
proposal gave every distant candidate a positive edge, especially when fewer than
30 cores force all neighbors. Tiny separated fixtures exposed this contract gap.
The final prospective background-agreement gate above fixes that issue; initial
source/design and failed fixture journals are preserved in E017 artifacts. No
community outcome or label was consulted to choose it.

## Return representation and review footprint

Complete numeric neighbor/candidate axes are retained once in hash-bound sparse
caches. New partitions use an explicitly empty legacy display-only `neighbors`
field and name that cache; unchanged E013 only copies this field and does not
consume it. Full ID/valid/assignment/reason axes remain. This avoids four repeated
million-row neighbor-ID lists. Integer candidate/bin indices may be stored as
int32 only when lossless; native vectors and affinity precision remain unchanged.
Only the final post partition writes full FASTAs; core/pre/old alternatives retain
complete assignment tables/accounting. No omitted FASTA is described as backed up.
