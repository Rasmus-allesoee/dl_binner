# E030: supported bins help, but do not recover the stronger anchors

Reviewed November 1, 2026. These are admitted development observations from the
[frozen comparison](../../experiments/E030-supported-biological-bins/comparison-review.json),
[all 2,222 target rows](../../experiments/E030-supported-biological-bins/comparison-targets.tsv),
[paired diagnostics](../../experiments/E030-supported-biological-bins/grouping-diagnostics.json)
and [independent inspection](../../experiments/E030-supported-biological-bins/inspection-observed.json).
Older outputs and scores are reused, not refitted or rescored. Scientific source
is 638084d; subsequent operational repairs do not change the candidate or evaluator.

## Direct result

| Same frozen implementation and policy | Root-only R95 | Profile pre R95 | Final R95 | Final targets >= 50% / >= 90% |
| --- | ---: | ---: | ---: | ---: |
| E009 no GLM, teacher | 7.6657% | 7.6657% | 7.9814% | 17 / 6 |
| E009 no GLM, student | 7.2337% | 7.2337% | 7.8971% | 16 / 7 |
| E009 full-path GLM, teacher | 6.9105% | 7.4354% | 8.7274% | 18 / 5 |
| E009 full-path GLM, student | 7.2210% | 7.2210% | 7.6509% | 16 / 7 |
| Oral measured ten-depth, teacher | 10.7964% | 11.0327% | 10.9060% | 88 / 55 |
| Oral measured ten-depth, student | 10.0559% | 10.5917% | 10.5446% | 83 / 50 |

The prospective disposition is **MODIFY**. Both primary students improve over E029,
by 0.4299 and 0.4887 percentage points, and target-90 counts increase from 4 to 7
and 43 to 50. Neither reaches its stronger frozen anchor: E023 E009 remains
**10.4163% / 19 / 9**, E026 Oral **13.8569% / 108 / 58**. Consequently the original
KEEP criterion fails unchanged. Retain MetaBAT2 **8.5493% / 16 / 5** E009 and
**17.3260% / 129 / 106** Oral. The GLM teacher now exceeds that E009 reference's R95
by 0.1782 points; the main student still trails it. Native eligibility differs,
so these are whole-tool contexts, not matched-cutoff or isolated-feature claims.

Against E029, GLM student gains 2,384,566 recovered bp: 15 target gains, one loss,
140 unchanged. Oral gains 10,179,750 bp: 63 gains, 18 losses, 718 unchanged.
Against E023/E026 both remain below the declared reference. Target counts and
recovered reference unions are not assigned-contig counts.

## What the paired evidence identifies

Root-only R95 exactly equals retained E029 marker-selected R95 in all six actors.
The root bias explained the failed density-only alternative, but marker selection
had already avoided that root. Correcting root eligibility alone is therefore not
a new gain over the working marker comparator. This does not invalidate the
mechanism diagnosis; it limits its practical contribution here.

Profile selection adds 2,911,111 recovered bp for the GLM teacher and 11,161,089 bp
for Oral student, but no student E009 primary R95 gain. The final update adds
recovery on E009; it loses a net 981,339 bp for Oral student and 2,638,335 bp for
Oral teacher relative to their new pre partitions, while increasing target-90
counts. A common rule can have gains and harmful individual assignments.

Pre/post bin counts are unchanged in all six actors. **Inference:** no merge is
accepted, because the frozen update path can only merge existing bins or recruit
into them, and cannot create replacement bins. This is not a replay or claim to
have independently decoded every large recruitment trace. All raw choices,
profiles, maps and updates remain checksum-bound in the private archive.

Two illustrative failures come directly from the frozen per-bin/target tables:

- E009 GLM student, ASV300.8: pre contains 3,374,678 bp at 97.5830% confirmed purity,
  recovering 3,271,350 reference bp. Post contains 3,585,019 bp at 92.8146%;
  confirmed other-origin DNA is 174,536 bp. Although source-union completeness
  rises from 94.5397% to 95.5167%, no bin passes the unchanged 95% primary purity.
- Oral student, OTU_97.2092.0: pre is 6,648,196 bp at 100% origin purity and 95.4585%
  completeness. Post becomes 11,948,372 bp at 58.1303% purity, with 5,002,749 bp of
  confirmed other-origin DNA. It loses 6,648,196 R95 bp. This is a substantive
  wrong-recruitment example, not merely the conservative N-quarantine convention.

Canonical bin labels can change after recruitment. These examples join through
the independently reviewed dominant origin/target records, not assumed equal
integer labels. Truth diagnoses the failures and never selects a protected bin,
threshold, assignment, K or training input.

Large mixed bins remain: GLM student has 16 of 40 bins >= 200 kb below 95%
confirmed purity; Oral student 45 of 143. Oral student assigns 414,571,838 bp,
leaves 1,029,255,826 eligible bp unassigned and 226,153,459 bp method-excluded.
All sum to 1,669,981,123 bp. E009 GLM student similarly preserves all 231,678,157 bp:
129,407,644 assigned, 80,235,059 unassigned and 22,035,454 excluded.
No low-quality bin or short DNA was removed to improve metrics.

## Learning and source reassessment

Under the same new constructor, student minus teacher final R95 is -0.0843 points
without GLM, **-1.0765 with GLM**, and **-0.3614 on Oral**. GLM helps teacher by
0.7461 points but student changes by -0.2462 points relative to its no-GLM path.
Do not reject GLM or markers: this is evidence that the current student does not
consistently preserve/use available bootstrap information.

The retained E027 audit finds 3,657 / 13,142 Oral positive links discordant in
provided origin (27.8%), while all 1,644 negative links differ. Origin discordance
is not exhaustive unique-source error labeling, and it does not prove which loss
causes the teacher/student difference. E029's matched joint-neighbor fractions
remain 38.6370% / 37.4822% for Oral teacher/student, versus native learned
32.6092% / 31.2551%. Retrieval recall 1.0 is technical correctness, not biological
homogeneity; none of those old geometry scores was recalculated.

Targeted current-source inspection:

- unified/training.py::information_contract and E027's design explicitly say
  the student starts from the seed, **not bootstrap weights**. The bootstrap
  supplies pair proposals, distinct from the moving stopped EMA target. Thus the
  current comparison is not already pretrained-teacher fine-tuning.
- relational/pairs.py::contexts/choose uses positive measured-depth evidence,
  reciprocal teacher neighbors, marker endpoint reliability and global random-pair
  quantiles. depth_evidence is (coverage > 0).any(1) in multiview/views.py;
  it excludes measured-zero rows from pair constraints. We found no co-zero-as-near
  implementation bug in that proposal path. Zeros remain observed elsewhere.
- Recruitment uses one synchronous fixed-profile pass. The source does not chain
  new assignments, but neither does it jointly guarantee the quality of all
  independently admitted recruits. The bad bins above are consistent with the
  declared heuristic; they do not demonstrate an axis/ID or implementation violation.

The previous SemiBin2/SCGBinner marker-learning and self-view reviews remain useful
design evidence. No native run of those tools is claimed. A fresh primary
[HDBSCAN documentation check](https://hdbscan.readthedocs.io/en/latest/parameter_selection.html#allowing-a-single-cluster)
confirms root bias/default exclusion; our bp-weighted forest adaptation is not
standard HDBSCAN, and that source does not predict these recovery gains. The PMC
refresh of the SemiBin2 page returned a browser challenge; reuse the previously
versioned/source-hashed review rather than inventing fresh paper observations.

## Strongest next coherent block

Choose **bootstrap-preserving, confidence-aware relational learning**, retaining
the current encoder topology, exact real views and available GLM bank initially.
Resolve and implement together: explicit admitted bootstrap checkpoint/state
initialization, reliable/abstaining cross-contig proposals, soft confidence-aware
signed supervision, and a teacher-preservation mechanism that can retain useful
geometry without freezing every erroneous teacher neighbor. Keep guaranteed
same-parent real DNA positives, measured-parent depth, optional-modality masks
and all marker-negative/short/unknown DNA. Exact defaults and any selective control
must be declared prospectively, not chosen by these origin labels.

Hold E030's common constructor fixed for the first learning comparison and retain
both pre/post outcomes. This isolates a new learning bundle from more grouping
tuning; it does **not** certify recruitment safe. A later whole-bin acceptance
guard remains justified if harmful recruitment persists. At most one matched
continuation-only or signed-positive control is justified if it changes the design,
with module/RNG/BatchNorm/optimizer exposure explicitly accounted for. Extra
training versus fresh initialization is a declared treatment, not a pure marker-loss
causal claim.

Why now instead of the main alternatives:

1. More grouping thresholds do not address the reproducible student/teacher loss
   and poor Oral biological neighborhoods. Even Oral pre is only 10.5917%, well
   below the 17.3260% retained reference; eliminating the single recruitment
   failure is not evidence of closing the whole gap.
2. A larger Transformer or another small loss-weight grid is not supported by a
   diagnosed capacity/collapse failure. A reliable supervision/target upgrade can
   be substantial without increasing parameter count.
3. Full Oral GLM remains a valuable concrete main-mode milestone, not a rejected
   information family. One fresh L4 attempt again stockouts; no native batching
   throughput exists. Retain its prepared 128-view qualification and $65–85 /
   61.05 unbatched-hour full-bank planning case. Do not make GPU availability a
   prerequisite for this CPU learning block, or claim the no-GLM Oral result tests
   full GLM transfer.
4. More datasets and stronger external runs remain useful later. Current
   teacher/student evidence already identifies a cross-community development
   decision. Skin stays unscored and needs its existing admission/protocol
   dependencies; no new external campaign is needed to establish headroom.

This recommendation is a supported next hypothesis, not proof of optimality or
a promise that fine-tuning alone closes the recovery gap. Both communities are
development data. Preserve full 156/799 denominators, 3.3034% E009 N quarantine,
separate Oral origin/shared sensitivity and RNA-unchecked secondary tiers.
