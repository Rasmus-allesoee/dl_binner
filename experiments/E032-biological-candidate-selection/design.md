# E032: common biological candidate selection and joint recruitment

Prospective, November 3, 2026. Owner invocation of E031 at `1ea748a` authorizes
local implementation, a new $6 cached comparison and one separate $3 T4 probe.
No E032 community outcome has been inspected. E031 learning, vectors, both
retained retrievals/forests, source-blind axes, physical markers and seed 11 stay
fixed. This is a construction bundle, not a new learning or depth treatment.

## Problem and general method

The same new vectors have opposing E023/E030 construction effects. Whole/child
and pre-update alternatives contain complementary targets; synchronous individual
recruitment can jointly damage a bin. Use a generic candidate-pool interface,
not a dataset-name router or truth-selected mixture. Internal candidate integration
also occurs in standalone binners: COMEBin selects a marker-scored partition;
SCGBinner and SemiBin's long-read path iteratively select/rescore competing bins;
CompleteBin performs staged candidate generation/refinement/dereplication. These
are precedents, not evidence that their proxies or this new rule are optimal.
The current two communities are development data. Untouched confirmation remains
necessary, and this block must not become an indefinite sequence of selection tweaks.

## One frozen rule

Use every supported condensed whole/child alternative in the two retained forests,
excluding internal forest roots, plus the five retained density/selected/root-only/
pre/post partitions. Preserve an entire long singleton as an alternative. Hierarchy
membership uses shared DFS leaf orders and intervals, not a full leaf list per
ancestor. Partition membership uses shared sorted row arrays. No new clustering,
resolution, search, fit, marker detection or thresholds selected with truth.

For a candidate, cached physical-locus weights give soft marker breadth
`C=sum(max family weight)/panel` and excess `X=sum(sum-max)/panel`. They are
quality proxies, not measured completeness/contamination. Composition and actual
parent-depth means use unchanged E030 source-blind local-pair scaling. Within-bin
scatter is between contig profiles; it is not within-contig coverage variance.
Let H be the mean of the available composition/depth profile supports (neutral
0.5 for a missing or entirely measured-zero depth comparison). Score:

`S = C - 5*X + 0.25*(2*H-1)*sqrt(bp/(bp+200000))`.

Require at least 10 kb and positive S. A marker-negative candidate additionally
requires 200 kb; it uses the same profile term, with no fabricated marker hits.
Short/marker-negative contigs remain eligible for membership/recruitment and all
excluded/unassigned DNA remains in exports. Repeated loci are soft penalties;
they are not proof of contamination or an automatic split trigger.

Rank by descending full-candidate S, then descending bp, then source-blind ID and
stable candidate key. Take candidates in that single fixed order. Remove already
claimed rows; if partial, recompute S once on the residual and apply the same
admissibility rule. Do not regenerate candidates or run a subset/grid optimizer.
Keep the whole and residual decisions/reasons. This deterministic greedy heuristic
is not a globally optimal weighted set-packing solution. Fenwick occupancy counts
skip fully claimed hierarchy branches without enumerating them again.

For one synchronous recruitment pass, combine normalized inverse-distance votes
equally from the two retained neighbor contexts. Use at least two distinct assigned
neighbors, vote >=2/3, best/runner >=1.5, and the existing length-shrunk composition/
depth compatibility with combined half-vote/half-profile score >=0.6. All proposed
recruits to each bin are evaluated together: retain the update only if the same
bin score S does not decrease (roundoff tolerance 1e-12). Otherwise retain the
unchanged bin. No truth-selected subset, chaining or iterative parameter search.
Measured positive, measured zero and unavailable depth remain distinct in traces.

## Decision and scope

KEEP requires no R95 or T90 loss versus the stronger retained within-mode E031
constructor in all three modes, and >=0.5 percentage point R95 gain in at least
one mode. MODIFY records useful gains with a trade-off or smaller effect. ABANDON
this frozen bundle if no mode improves R95, or any mode loses >=1 percentage point
without a >=0.5 point gain elsewhere. Operational/integrity failure is NOT ASSESSED.
These practical thresholds are not biological standards or significance tests.
Preserve E023 10.4163%, E026 13.8569%, all E031 teachers/students and MetaBAT2.
No result authorizes a dataset-specific router or settles modality/model families.

Depth harmonization, within-contig variance/breadth and pair links are audited
separately. E032 retains every accepted depth byte. A new common BAM summary
would change learning/proposals/geometry and needs its own prospective comparison.
Full Oral GLM and skin confirmation remain separate unadmitted work. The authorized
T4 probe measures only the unchanged 128-view batching contract, not a full bank.

Native admission must include actual tiny restore/read/selection/export/reload,
whole-child overlap, marker-negative, measured-zero/missing, grouped-recruit
refusal, source/config/axes and bounded synthetic scale contracts. Return limits
are 3 GiB compressed / 6 GiB logical with tested exact aliases, no fallback.
Existing E2/32 GiB, four threads, 26 GB sampled RSS, eight cumulative hours,
8.25-hour provider STOP, separate 25 GiB source/task reserves and 12 GiB growth;
one 40 GiB task disk only if verified cleanup is insufficient. Fresh complete
credit/cost and November 11 storage gates precede any cost-bearing action.
