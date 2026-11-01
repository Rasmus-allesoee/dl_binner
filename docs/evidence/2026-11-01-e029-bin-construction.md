# E029: completed common-version evidence and a bin-construction failure

Reviewed November 1, 2026. [The independent inspection](../../experiments/E029-certifiable-joint-retrieval/inspection-observed.json)
and [frozen diagnostics](../../experiments/E029-certifiable-joint-retrieval/comparison-review.json)
are direct project observations. No older baseline was refitted or rescored.
The successful science remains frozen at `31fb9c7`; subsequent inspection code
does not alter its native vectors, inputs, partitions or failed journals.

## Outcome and scope

| Common mode | Teacher post R95 | Student post R95 | Student target-50 / target-90 |
| --- | ---: | ---: | ---: |
| E009 no GLM, ten measured depths | 7.6657% | 7.2337% | 16 / 5 |
| E009 GLM throughout teacher/proposals/student | 6.9105% | 7.2210% | 16 / 4 |
| Oral no GLM, ten measured depths | 10.7964% | 10.0559% | 79 / 43 |

The original disposition is **ABANDON_THIS_FROZEN_BUNDLE**. Both primary student
arms lose every declared recovery endpoint against their anchors: E023 E009
10.4163% / 19 / 9 and E026 Oral 13.8569% / 108 / 58. E009 GLM student loses
17,723,369 recovered bp, with zero target gains and 24 losses. Oral loses
79,177,868 bp despite 90 target gains versus 73 losses. Gains and losses concern
reference unions, not the number of assigned contigs. Keep the retained MetaBAT2
contexts, E009 8.5493% / 16 / 5 and Oral 17.3260% / 129 / 106, beside these results.
Their native eligibility differs; these are whole-tool references, not cutoff ablations.

The paired density-only partitions have zero R95 in all six components. Physical
marker selection restores 18–19 E009 and 113–117 Oral targets with any passing
bin, without a paired target recovery loss from those zero baselines. This is
useful within this tree, but its size is inflated by the failed density-only
alternative. It does not establish universal marker necessity or optimality.

Full-path E009 GLM student changes R95 by -0.0127 percentage points versus the
same no-GLM implementation. Within GLM, student improves over teacher by 0.3105
points; within no-GLM it loses 0.4320 points. Oral student loses 0.7405 points
versus teacher. This is not an isolated GLM, marker-loss or depth causal study.
Both communities are development data. Oral now uses genuine depth in its common
teacher and student, so the earlier sequence-only information asymmetry is removed
for this declared no-GLM mode. GLM-enabled Oral remains unmeasured.

## Direct failure localization

E009 density-only selects a 209,599,684 bp component with 224 supported origins
and only 9.59% dominant confirmed purity, plus a 43,019 bp component. Oral selects
one 1,443,827,664 bp component containing all eligible DNA. These are explicit
selected outputs, not missing/unrun results. Markers break those roots into
smaller choices, but E009 GLM student still has 17 of 39 large bins below 95%
confirmed purity; Oral student has 28 of 141. Conservative impurity includes
unresolved DNA, so these counts are not measured contaminant fractions.

The retained Oral teacher root choice has own utility 1,525,860,771 versus summed
child utility 299,437,377. The frozen implementation gives each forest root birth
zero, integrates bp-weighted persistence and permits its selection. The physical
marker factor reduces that root to about 0.000825 and rejects it. Source and
native full cached-choice reproduction agree. This is a declared but destructive
selection convention, not an ID permutation, failed cache reader, lost depth
column or newly discovered violation of the frozen implementation. We should
take responsibility for the weak heuristic without rewriting its experiment.

[HDBSCAN's primary implementation documentation](https://hdbscan.readthedocs.io/en/latest/parameter_selection.html#allowing-a-single-cluster)
explains that its default excludes a single root cluster because excess-of-mass
selection can favor the root. Its [API](https://hdbscan.readthedocs.io/en/latest/api.html)
exposes `allow_single_cluster=False`. Our sparse bp-weighted heuristic is
explicitly not standard HDBSCAN; the difference was allowed by the design. The
documentation supports the mechanism concern, not a promise that root exclusion
alone repairs marker-selected recovery.

Retrieval correctness is now closed: all four original E009 caches retain their
passed 0.9985–0.9993 sampled recall; both new Oral exact caches have recall 1.0 in
every frozen stratum and complete boundary certificates. Every native distance,
forest, choice and DNA audit passes. Approximation error cannot explain these
new Oral results. The exact fallback takes about 79 minutes per Oral actor;
quadratic retrieval is a correctness reference, not a scalable default.

Biological geometry remains limited. On the same complete 508,763 eligible Oral
query population, teacher/student joint-score bp-weighted same-origin fractions
are 38.6370% / 37.4822%. Their retained native learned fractions were 32.6092% /
31.2551%. This is a changed geometry on matched queries, not an encoder improvement.
E009 GLM student's overall joint value is 86.3860%, but the primary bacterial
stratum is 82.7616%; non-target gains must not be credited wholesale to targets.
Technical recall does not establish biological homogeneity or recovery.

The accepted E027 proposal audit remains contrary evidence: 3,657 of 13,142
Oral positive links have discordant provided origins, and student neighborhoods
deteriorate. This does not prove every such shared-locus link is false. Improving
proposal reliability remains a serious learning alternative; it would not by
itself correct the observed root/whole-bin selection failure.

## Interpretation and the next decision

Choose one coherent **root-safe, profile-supported bin-construction upgrade**,
with learning fixed and the existing graphs/forests/physical calls cached. Correct
the root/stability convention, judge whole versus child candidates using label-free
within-bin composition and measured-parent-depth support, and integrate supported
recruitment/abstention rather than treating connectivity as a genome. Resolve one
precise algorithm/default prospectively. Do not repeat E026's universal channel-AND
gate, E018's automatic profile veto, arbitrary truth K or a resolution campaign.
At most one root-convention-only control is justified if it changes whether the
profile block is needed; it is not a prerequisite experiment before coding.

This attacks an observed information-to-bin failure and is more decision-relevant
now than enlarging attention, adding taxonomy, retraining another small loss
variant or waiting for GPU capacity. The completed [MetaCAT](2026-10-27-e023-information-and-recovery.md)
and [SemiBin2](2026-10-30-e026-recovery-and-common-version.md) source reviews
support contextual/probabilistic biological construction as an alternative to
raw persistence. They do not authorize variance likelihoods from mean-only depth,
hard repeated-marker cannot-links, an external tool run or borrowed performance claims.

Learning and additional information remain important. A bin-construction gain
would not prove current representations sufficient. After this block, use the
retained matched teacher/student and full-path GLM evidence to choose between
proposal precision and additional sequence information. Keep one common source
and availability policy across datasets. Never route to E023 for E009 and E026
for Oral using their truth scores.

All 156 / 554,661,890 bp and 799 / 2,083,072,211 bp denominators remain. The
already retained represented-reference fractions, 18.5321% E009 and 80.1691%
Oral, are loose evidence bounds, not attainable R95 or replacement denominators.
Keep E009's 7,653,205 bp / 3.3034% N quarantine, Oral's separate provided-origin
oracle/known-shared sensitivity, all length/origin/status populations and secondary
RNA-unchecked threshold tiers. No unseen-genome or SOTA claim follows.
