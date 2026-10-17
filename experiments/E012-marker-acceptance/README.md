# E012 — Accept retained marker splits only with independent graph support

Established 2026-10-17. Status: **planned; no changed community scores yet**.
Branch `e012-marker-acceptance-control` starts at completed E011 `3cc3d15`.
The owner authorizes this local control and operational debugging in this task;
no cloud execution, fit, external run or confirmation acquisition is included.

## Decision and prospective rule

Keep **CPM as the working development grouping direction**, with RB retained as a
matched historical context. E011's frozen post-refinement +0.5-point criterion
failed and remains failed. It was a practical development threshold, not a
biological standard or a permanent veto on CPM. Its pre-refinement 5.3990% versus
RB's 1.8763% motivates improving CPM's harmful refinement. CPM pre approximately
ties dev3's aggregate but has fewer targets >=50%; no stronger-binner claim follows.
No resolution search is needed to make this direction choice.

Retain markers as a high-priority product information source. An HMM match and
duplicate count can propose a split, but do not establish contamination. This
control adds one context test: does the **exact existing split** improve the
retained graph's CPM objective at E011's unchanged label-free density?

[Protocol](protocol.json) freezes the only rule, tolerance and criteria.
For each already adopted split, use
`delta = gamma * newly_separated_vertex_pairs - cut_edge_weight`,
where `gamma = median(positive frozen weights)/30 = 0.01294708220433279` and node
sizes remain one. Require positive delta beyond eight ULPs of the larger term;
ties keep the parent. Each proposed noise vertex is a distinct singleton **for
scoring only**: its lost positive edges count and it stays unassigned in exports.
Keep the whole parent or its exact retained children/noise; no new split,
reassignment, optimizer, marker scan, encoder/inference or neighbor build occurs.
Both RB and CPM contexts use the same CPM score, so RB's original objective does
not automatically veto splits that improve the new grouping direction.

This is graph support distinct from marker-conflict removal, not independent
biological evidence. Since CPM already optimized the same score, all its retained
splits might be vetoed. That would support a safety guard, with **no demonstrated
marker refinement benefit**. Failure in RB or loss from accepted graph-positive
children would restrict this gate rather than rule out markers or CPM. No
threshold/blacklist may be changed after these outcomes.

## Targeted source check and marker audit

On 2026-10-17 the [official Leiden API](https://leidenalg.readthedocs.io/en/stable/reference.html#cpmvertexpartition)
supports a fixed-membership CPM quality calculation with unit node sizes. Tiny
native `igraph`/`leidenalg` contracts compare our delta against half its quality
change; no community optimizer is called. [CheckM](https://pmc.ncbi.nlm.nih.gov/articles/PMC4484387/)
(Parks et al., 2015, Genome Research, doi:10.1101/gr.186072.114; marker definition,
lineage-specific sets and limitations) uses single-copy frequency in reference
genomes, not a universal copy guarantee. Its lineage/co-location treatment and
plasmid/phage caveats support checking context, without adding a CheckM runtime.

Primary source inspected locally, with independent repository roots:

| Source | Commit / file SHA256 | Observation, not execution |
| --- | --- | --- |
| SemiBin `SemiBin/markers.py` | `f7c45dcbcdfa81e8fbc3e08b04c54683122e72d6` / `7aad72ed474c8310a5a6eda928eac082560db991e22e9627967a058d05990af4` | Median family count, coverage and per-contig dedup; not unconditional largest count. |
| SemiBin `SemiBin/cluster.py` | same commit / `473f4c488c3f2c79c54003336b96ffc2d013eee35de110947234d4d5cf639a00` | Marker-seeded, length-weighted KMeans reclustering after bin support checks. Not a recovery guarantee. |
| COMEBin `COMEBin/scripts/unitem_markers.py` | `1b476a41fac893294c70212a869573a732560ce5` / `70d91072eefecf4237e03b0d81c670a792cff013b355018a9ebb59e4958a3e77` | Marker-set completeness/contamination selection, distinct from merely eliminating duplicates. |

These extend the completed [design review](../../docs/evidence/2026-09-30-binner-design-review.md),
[competitive source study](../../docs/evidence/2026-10-08-competitive-binner-study.md),
and [D015](../../docs/decisions/D015-coherent-prototype-upgrade.md); no whole-tool
campaign or original review was repeated.

The separate audit projects **all retained adopted seed calls in both contexts**
through the existing minimap2 2.30 PAFs into cached gene and HMM-domain intervals.
It retains all competitors, N-vetoes, repeat-locus uncertainty, exact circular
aliases, simulator IDs and separate pASV/HOST metadata. It reports distinct loci,
provided replicons and overlap compatible with assembly duplication. HMM trusted
cutoffs/domain coverage and complete/nonidentical proteins establish call context,
not validated function or universal single-copy status. No reference reannotation
or gene-specific identity measurement is invented. Truth is diagnostic only;
the selector cannot read this audit or truth.

## Inputs, tests and execution boundary

[Input lock](input-lock.json) binds accepted E010 restore and E011 members plus
complete assembly/depth. [Review lock](review-lock.json) binds admitted truth and
accepted paired results. Restore-only means missing/corrupt evidence fails, without
copy/reinstall fallback. Preserve dev3/dev4, all journals, source freezes and the
failed Mac strict allclose contract without tolerance changes or vector substitution.

[Selector](../../scripts/e012_acceptance.py), [audit](../../scripts/e012_marker_audit.py),
[reviewer](../../scripts/e012_review.py) and [local launcher](../../scripts/e012_local.py)
run from the committed clean branch in the existing independent Mac dev4 runtime.
[Tests](../../tests/test_e012.py) exercise actual NPZ readers, opaque-ID mapping,
fixed native objective, parent/child selection, full DNA exports and malformed/
corrupt-input refusal. Marker fixtures are hand-authored cached metadata/domains;
no detector or optimizer is substituted. No new native Linux or training claim.

Local bounds: four numerical threads, 8 GB sampled tree RSS, 15 minutes per stage,
30 minutes cumulative, about 2 GB additional local disk; **$0 cloud compute**.
All 145,702 contigs /231,678,157 bp, ten ordered depth columns, short/marker-negative/
unknown/non-target DNA and optional unassigned outcomes remain. Evaluator uses
156 primary targets /554,661,890 full provided bp; **3.3034% N-quarantine** stays.
Oral-GSA remains frozen/unacquired. **October 21 storage review** remains; this
local control does not extend the existing cloud storage approval.

Execution and conclusion will be appended here after frozen local execution.
