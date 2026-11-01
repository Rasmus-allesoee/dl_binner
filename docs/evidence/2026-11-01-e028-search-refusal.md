# E028: complete candidate lists still fail Oral search accuracy

Reviewed November 1, 2026. This note separates native observations, source
interpretation and an unadmitted implementation route. [The inspection](../../experiments/E028-global-discovery-repair/inspection-observed.json)
owns exact exits and bytes. [The next block](../../experiments/E028-global-discovery-repair/next-block.md)
owns the recommendation and resource case.

## Native observations

The original E2 starts October 31 at 20:45:50.098 UTC and stops at 21:12:00.036 UTC.
Workflow exit is 1. Collection and private readbacks pass. The intended watcher
observes its parent exit and requests shutdown. No VM wake is needed for evidence.
The exact archive has 274,627,567 bytes, 542 regular members and seven aliases.
Every member and alias passes verification. No return member is omitted.
Original external data and model banks remain external inputs, not new backups.

All ten native gates pass. All four E009 retrievals complete and pass their
unchanged sampled recall gates. Oral teacher retrieval runs all 15 ANN iterations,
returns complete proposals and completes its 508,763-row exact rerank. Its sampled
recall is 0.86548 overall, 0.58333 on measured-zero depth, 0.99375 on positive depth,
0.88125 on short contigs and 0.95208 on long contigs. The required minimum is 0.90
overall and in every populated stratum. The original refusal is correct.

The global barrier prevents all six bin-construction jobs. Oral student retrieval,
three exports, three audits and final input verification never run. No new bins,
R95, target recovery or secondary quality tiers exist. Biological KEEP/MODIFY/
ABANDON is **NOT ASSESSABLE**, not zero or ABANDON.

Independent sparse readers verify selected rows, finite ordered distances,
unique non-self neighbors, full opaque-ID axes and the original query cohorts.
Existing feature files match their native hashes. Both ordered ten-sample axes
match the frozen protocol. Oral has 191,567 measured-zero eligible contigs,
representing 231,943,792 bp. E009 has no measured-zero eligible contigs. Its 13
zero-depth records are outside the selected geometry. These are measured means,
not missing measurements or invented window coverage.

The accepted E027 Oral teacher audit and E028 audit contain the same 56 query IDs.
All calibration values and exact kth-neighbor scores are identical. Six queries
improve, 13 worsen and 37 stay unchanged. Overall recall falls from 0.88512 to
0.86548. No older biological score is recomputed. This matched comparison isolates
a change in approximate discovery, not a change in the underlying exact score.

## What the source supports

E028 fills every initialization slot and fixes E009's missing-candidate refusals.
Its complete candidate lists do not establish enough Oral recall. The 61-wide
search and 15-iteration budget remain inadequate for this observed case. Neither
the retained runtime nor the inspected initialization shows a library-alias,
axis, missing-input or source-drift error. This does not prove optimality or the
absence of every implementation defect.

The unchanged score is a symmetric dissimilarity, not a mathematical metric.
Measured co-zero depth contributes squared distance 1. A measured zero versus
small positive profile can contribute much less. The length reliability term
also leaves a positive neutral contribution for identical composition.

The actual frozen function admits a three-point counterexample. With identical
native/composition coordinates and 100,000 bp lengths, two zero-depth points are
0.58435 apart. Each is only 0.09017 from a small positive-depth point. The direct
distance exceeds the sum of those two distances. Self distance is also positive.
This synthetic result is not a claim about three selected biological contigs.

[PyNNDescent documents approximate search and custom distances](https://pynndescent.readthedocs.io/en/stable/how_to_use_pynndescent.html).
Support for a custom function does not guarantee this frozen recall contract.
The actual 0.5.13 source hash matches the lock and the native loaded package.
Do not infer that the package promises metric-level guarantees for this score.
Nonmetric geometry is a plausible contributor, not a complete reconstruction of
the native misses. The wide proposal arrays were not retained. Their complete
invalid-row census and final reranked arrays were retained.

## A score-preserving route worth implementing

For query i and candidate j, write r_i = sqrt(L_i / (L_i + 2500)). Let u, c and d
denote native, square-root TNF and transformed parent-depth coordinates. Let p
indicate a measured positive profile. The existing score before its floor obeys:

```text
3 D(i,j)^2 = ||u_i-u_j||^2 / s0
           + r_i r_j ||c_i-c_j||^2 / s1 + 1 - r_i r_j
           + ||d_i-d_j||^2 / s2 + (1-p_i)(1-p_j).
```

Expanding the squared terms gives a query constant plus an inner product of
different query and candidate coordinate maps. The maps have 215 coordinates
for the current 64/136/10 inputs. No biological term changes. No vector norm is
assumed. Do not normalize these lifted coordinates as cosine features.

The [analysis helper](../../scripts/e028_retrieval_audit.py) implements this
formula only as a feasibility check. On 256 synthetic mixed-availability rows,
the maximum distance difference is 8.25e-15. The compiled original function
differs from the subtraction-based reference by at most 2.23e-16. These checks
do not run DNABERT, infer native vectors or create a community graph.

[Faiss describes inner-product search](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances)
and [flat search as its exact reference](https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index).
The immediate candidate can use the existing NumPy runtime instead of adding
Faiss. [NumPy matmul uses BLAS when possible](https://numpy.org/doc/1.26/reference/generated/numpy.matmul.html).
Blocked matrix products can avoid storing an n-by-n matrix. Arithmetic remains
quadratic. This is a bounded completion route, not a solved large-data product.
Faiss also documents a one-coordinate MIPS-to-L2 transformation. That gives a
concrete later indexed route, but its documentation warns about interactions
with quantization and other index structures. Do not claim it guarantees native
recall. An admitted fast path must keep the same score and an exact fallback.

Production still needs a conservative roundoff bound, complete boundary/tie
handling and final subtraction-based reranking. Expanded norms can cancel when
calibration is extreme. A fixed oversampling factor does not certify a boundary.
Test extreme scales, duplicate coordinates, all-zero/missing modalities, lexical
ties and full ID mapping. Preserve the original 0.90 gate and Mac allclose failure.
Native full-shape throughput and full-stage resource admission remain required.

## Decision and alternatives

Choose one evidence-completion block: implement certifiable frozen-score retrieval
and finish the cached common-version comparison. Reuse the four passed E009
caches after byte/source/axis checks. Compute only the unpassed Oral teacher and
unrun Oral student retrievals. Keep all six learners, native vectors, biology,
seed, full populations and the global barrier fixed.

Another seed/width/iteration campaign is less attractive after two native Oral
failures. Changing the neutral score or removing zero/short DNA changes the
biological question. A larger learner cannot repair an unreliable consumer.
More external tools add little before the existing reference comparison works.
The known Oral proposal-origin discordance remains a later learning uncertainty.
It does not authorize truth-selected pair repair or establish unique-source errors.

Qualify the already prepared Oral batching path alongside this work with one
separately authorized native probe. Do not make that probe depend on a recovery
threshold. Do not authorize the full bank merely because the probe passes.
Skin remains unscored. Full source/replicon/taxonomy/overlap/ambiguity/depth,
truth/protocol/cost and retention admission still precede confirmation.
