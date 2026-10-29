# E026: calibrated evidence and biological bin construction

Prospective local design, October 29, 2026. No changed community outcomes have
been computed. E025 remains immutable. This block holds each community's learning,
native vectors, input axes, measured parent means and physical marker calls fixed.
It changes evidence fusion, the core retrieval population and bin construction
together; a later comparison establishes a bundle result, not isolated causality.

## Problem, sources and alternatives

E025's accurate retrieval improved Oral recovery but lost target-90 support versus
E019. Its positive/zero links were weak, depth omission changed score comparability,
and whole-forest density selection admitted one mixed component. See the accepted
[assessment](../../docs/evidence/2026-10-29-e025-depth-evidence-and-next-block.md).
MetaBAT2's [primary methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC6662567/)
justify rank alignment, effective coverage contrasts and reliable graph cores
with later recruitment. Its variance likelihoods cannot be inferred from means.
The retained SemiBin/source and physical-locus audits justify independent context
agreement and soft marker quality, not hard genome counts or universal cannot-links.
[PyNNDescent's API](https://pynndescent.readthedocs.io/en/stable/api.html) supports
compiled non-metric distances; a new exact recall audit is still essential.

Depth-enabled learning is the strongest alternative. Prefer this cached coherent
block first because the score/selection defect is directly observed; do not
require perfect grouping before the next justified learning upgrade. Larger
context/GLM extraction, external reference and more data remain alternatives,
not additions. No threshold grid, truth-selected K or community-specific router.

## Single prospective rule

1. Use native squared unit distance, squared Hellinger TNF distance and squared
   Euclidean `log1p(parent mean) / eligible-population column std`. The column
   spread is between parent means, never measured coverage variance. Drop globally
   constant channels; retain every measured zero. A zero-positive contrast is
   observed depth evidence; two zero profiles provide neutral depth evidence.
2. Select up to 8,192 parents by SHA256 of opaque ID. Calibrate each channel on
   their hash-cycle pairs plus their first retained native neighbour, excluding
   self/duplicate pairs. For depth use pairs with either endpoint positive and
   both measured. Map distances through 129 empirical quantile knots, collapsing
   positive-distance ties at their mid-rank, with zero distance anchored to zero
   and linear interpolation. Identical informative profiles must remain strongest
   agreement even if many calibration pairs tie; co-absence is separately neutral.
   These
   are relative ranks in a declared mixed local/random reference population,
   **not probabilities, p-values or calibrated biological confidence**. Save pair
   IDs, raw values, knots, availability and all transformations.
3. Average active channel ranks on a fixed denominator. Shrink short-contig TNF
   and depth ranks toward neutral 0.5 with
   `sqrt(L_i/(L_i+2500) * L_j/(L_j+2500))`; native ranks stay unshrunk. A missing
   pair channel is neutral 0.5, not a zero distance or a smaller denominator.
   Co-absence is neutral even though measured. Length shrinkage is a declared
   heuristic, not estimated confidence. Symmetric score; no triangle-inequality claim.
4. Cores are all valid contigs at least 2,500 bp, including measured-zero and
   marker-negative contigs. Prepare one new core-only custom-distance index
   (61 neighbours, seed 11, 15 iterations, 60 candidates, delta .001, no RP tree;
   retained core neighbours initialize, remaining slots random). Construction
   uses four workers; query batches use the tested serial native search path
   because the pinned parallel query heap mixes integer types. Query all valid
   parents in batches; exact-rerank 60 proposals plus retained native core links
   to 30. Old candidate arrays do not certify the changed score/target population.
   Audit 32 hash queries plus 16 each positive/zero core and non-core queries,
   deduplicated, against exhaustive core distances, with tie tolerance 1e-10.
   Each nonempty declared query stratum must have mean recall at least 0.90.
   Save numeric answers/arrays before refusal; no automatic widening or fallback.
5. Reliable core edges are reciprocal top-10 links with each informative raw
   channel rank at most 0.20. Co-absence/missing is not an agreement vote; at
   least two informative channels must agree. These channels can be correlated;
   agreement is not statistical independence or a probability product.
   Use the resulting sparse
   mutual-reachability MST forest and retained E023 2-contig/10-kb condensation.
   Components/singletons without bin support remain unassigned, not discarded.
6. Retain whole-parent and supported child alternatives. For each tree node,
   compute exact length-weighted mean pair distances from additive moments;
   calibrate those moments with the same knots and neutral-depth semantics.
   The coherence proxy is one minus their fixed-denominator mean rank. Utility
   is `bp * max(coherence - 0.5, 0) * (1 + marker breadth) /
   (1 + 5 * marker excess)`, with breadth/excess scaled by panel size. Cached
   physical reliabilities remain soft; separate loci/contigs are not collapsed.
   Choose children only when their summed utility exceeds the whole-parent
   utility by more than 5%; protect parent ties. This fragmentation margin is a
   prospective heuristic, not a biological standard. A coherent marker-negative
   component can form a bin. Zero utility permits abstention.
7. Recruit once against the selected, immutable core bins. Require at least two
   distinct supporting core neighbours, informative-channel agreement as above,
   at least two-thirds of accepted neighbour weight for the best bin, and a
   1.5-fold margin over the runner-up. Check both aggregate native/TNF/depth
   context via representative supported edges and soft reliable-marker excess:
   a candidate cannot introduce more than 0.05 panel-normalized new reliable
   excess into a bin in total. Rank candidates by vote margin, support and opaque
   ID; accumulate marker changes deterministically, never grow geometric profiles
   or let recruits vote. Keep core and recruited partitions, all alternatives,
   channel ranks/votes/rejection reasons and full assigned/unassigned/excluded DNA.

## Frozen decision and evaluation

Later cached comparison only: E009 fixed E022 learner/ten depths/GLM and Oral
fixed E019 learner plus E024 ten measured depths. Upstream learning is not matched.
Reuse E023/E025 and all older summaries, without refit or rescore. New core and
recruited partitions are the cheap paired utility control, not a new campaign.

KEEP requires final full-reference R95 at least E023 E009 and E025 Oral, at least
0.5 percentage-point gain in one community, and no target-50/90 regression versus
those anchors. MODIFY otherwise if either recovery or target coverage improves;
ABANDON this frozen policy if neither community improves either recovery or target
coverage. Preserve per-target losses and availability/length/marker/unassigned
trade-offs regardless of disposition; thresholds are practical, not significance.
Do not select per-bin or per-community winners from truth. E019 Oral's 33 target-90
count remains a stricter contextual trade-off, not hidden by the E025 anchor.

Use full 156/799 references, conservative E009 v2 and 3.3034% N quarantine, and
separate Oral provided-origin and known-shared sensitivity. Secondary completeness,
conservative impurity upper bounds and threshold HQ/MQ/LQ are not formal MIMAG HQ.
Skin stays unscored pending full source/replicon/taxonomy/overlap/competitive
unique-versus-origin/depth/evaluator/cost/retention admission.

## Authorization and operational scope

This task authorizes local implementation and tiny engineering checks only:
four numerical threads, 8 GB sampled RSS, an initial six-hour engineering clock
with headroom and measured local disk. The owner's standing direction permits a
recorded justified forecast increase, not weaker science. No community outcomes,
VM starts, paid cloud work, DNA acquisition, mapping, aligners, new training,
marker detection, native-index rebuild, GLM, external tool or confirmation now.
Prepare a separately priced comparison with fresh live credit/product/delay/
price/storage/runtime gates and process/boot watcher plus provider STOP. Existing
storage ends **November 4, 00:00 Copenhagen**; no renewal or deletion is implied.
