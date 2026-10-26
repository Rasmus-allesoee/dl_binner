# E023: adaptive-density bin construction

Prospective, October 26, 2026. Local engineering only. No changed community
partition or score has been produced. Fixed learning anchors: E022 E009 ten-depth
and E019 oral sequence-only, each with its own preserved CPM/E013 comparator.

The hypothesis is that one global CPM partition followed by split-only refinement
leaves recoverable mixed bins and fragments. A density hierarchy provides whole-
parent, child and consolidation alternatives at different **local** densities.
This does not establish that grouping is the sole remaining bottleneck.

Use every eligible native unit vector, including short and marker-negative rows.
Retain the original sparse graph and add one joint learned/Hellinger-composition
candidate index over all eligible rows, not a long-core population. Exact-rerank
the union of its 60 candidates and the retained native neighbors, then retain
30 neighbors. Scale channels with deterministic, source-blind pair medians.
The pair distance averages native squared chord distance, raw Hellinger distance
weighted by the geometric mean of L/(L+2500), and standardized log1p measured
parent-depth distance **only when both endpoints have usable measurements**.
Depth column scales use observed eligible parent means only; missing rows do not
enter those scale estimates.
Missing depth is omitted, never an observed zero or invented coverage variance.
The retrieval index omits depth; abundance enters reranking. This can miss
abundance-only neighbors and must be reported, not silently claimed exact.

Use kth-10 neighbor core distances and max(core_i, core_j, edge_distance) mutual
reachability. A sparse minimum spanning **forest** creates a local-density
hierarchy. Condense by the existing two-contig / 10,000 bp support, retaining
parent/child alternatives and bp-weighted density persistence. Select a disjoint
antichain by bottom-up dynamic programming. Utility is persistence multiplied by
(1 + weighted marker breadth / 100) / (1 + 5 * weighted excess copies / 100).
Use E013's cached physical-locus/partial/overlap reliability interpretation;
repeated families lower utility but never hard-forbid a bin or set truth K.
Marker-negative candidates have neutral factor 1. Density-only and selected
partitions, the whole hierarchy, marker factors and choices all survive.

This is an HDBSCAN-inspired, bp-weighted sparse-forest research rule, **not** the
standard full-distance HDBSCAN algorithm or its calibrated probabilities.
Whole-parent alternatives refer to hierarchy branches; original CPM parents
remain intact as external comparators rather than fixed cores or oracle fallbacks.
Disconnected graph components stay separate. Unsupported components and rows
outside selected candidates stay unassigned. No forced recruitment or universal
graph-gain veto. A supported parent can consolidate fragments across original
CPM bins; supported children can split a mixed parent. The E013 marker proxy is
lineage/panel-limited and may still reward inappropriate alternatives.

Freeze one config, source and protocol before outcomes. No resolution/loss grid,
truth-selected merges, family blacklist, target tuning, new learning, detection,
GLM extraction or acquisition. Exact ties use source-blind row/ID order; equal-
distance binary edges have zero persistence and cannot create positive utility.
Engineering fixtures exercise unequal densities, weak bridges, physical loci,
missing depth, short/no-marker DNA, abstention and reload/export refusal.

Primary joint KEEP: final full-reference R95 improves by at least 0.5 percentage
points in one community, neither community regresses, and neither loses a target
at 90% recovery. ABANDON if neither community improves R95 nor its >=90% count;
otherwise MODIFY. These practical criteria are not significance tests. Baselines
are reused without rescore; all 156/799 denominators, N quarantine and oral shared
sensitivity remain. Per-bin sequence completeness/impurity and threshold-based
HQ/MQ/LQ are secondary, never selection or a replacement primary rule.

Sources: [HDBSCAN implementation documentation](https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html)
for mutual reachability, condensation and stability;
[MetaBAT2 methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC6662567/) for sparse
evidence integration. Reviewed local VAMB `cluster.py` b146fb6 (length-weighted
local density valleys) and MetaBAT `metabat2.cpp` 8eb9602 (coverage graph) inform
the rationale, not a copied implementation or reproduced tool speed claim.

E017/E018 instead fixed >=2,500 bp cores, a single CPM objective and fixed core
profiles/votes, then recruited short rows. E023 forms density alternatives over
all eligible rows and jointly selects whole components, children and consolidated
branches; it does not relax the old recruitment gates or use its profile routing.
