# E012 — Accept retained marker splits only with independent graph support

Established 2026-10-17. Status: **completed; supports protection within scope**.
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

## Completed local comparison

Clean source **`a90a8d8`** froze the rule/code/locks before changed community
selection or scores. Attempt `attempt-001-a90a8d8` completed selection, all-seed
locus audit and independent evaluation, all exits zero. A separate descriptive
context audit reused ten projections and added eight for the four loss cases
already identified in E011; it did not change selection. [Review](review.json)
binds raw evidence, resources, checks and the exact unchanged rule.

| Context | Original parent weighted R95 | Old children | Accepted selection | Splits retained | Targets >=50% / >=90% |
| --- | ---: | ---: | ---: | ---: | ---: |
| RB | 1.8763% | 4.2909% | **4.5232%** | 16 /18 | 7 /2 |
| CPM | 5.3990% | 4.6171% | **5.3990%** | 0 /12 | 8 /2 |

CPM selected IDs, assignments, validity, reasons and neighbors are **exactly** its
native parent, rather than merely equal scores. Four harmed targets regain
6,221,970 source bp, but the former ASV300.2 gain of 1,885,026 bp is lost: net
**+4,336,944 bp /+0.7819 percentage points** over old CPM children. RB regains
**1,288,186 bp /+0.2322 points** for ASV399.6, with no target losing against its old
children. Neither selected context loses a target against its own parent here.
CPM still approximately ties dev3's 5.3911%, with 8 versus 13 targets >=50%.
This is a protective result, with no demonstrated extra CPM marker recovery or
generalization and no claim that graph quality is biological quality.

The primary audit covered **74 genes/contigs, all 30 adopted RB/CPM proposals and
840 retained competing PAF rows**. All four destructive seed pairs have uniquely
localized gene/domain spans, different complete proteins and distinct provided
records within the same simulator genome. The expanded four-case audit covers
every repeated family: eight of nine pairs occupy distinct records; TIGR01030
in ASV150.14 overlaps one source locus and includes a partial call. ASV456.0's
other TIGR00115 evidence includes a near-cutoff score (180.2155 versus TC180.20)
and a partial 56.10%-coverage call. Frozen trusted/coverage contracts passed;
they do not make every call a reliable cross-contig cannot-link.

Here “provided replicon” in inherited schemas means a FASTA sequence record.
These draft WGS records do **not** prove separate biological replicons. Distinct
loci do not establish functional paralogy or exclude source-reference assembly
redundancy/contamination or HMM family cross-reactivity. The primary audit's raw
any-gene-overlap flags also include one 9-bp boundary overlap with disjoint HMM
domains; this is insufficient duplication evidence. Three other RB flags have
substantial domain overlap, compatible with assembly fragments/redundancy.
All raw coordinates, flags and unresolved cases remain. No family blacklist,
increased cutoff or changed seed count was introduced.

Full exports retain **231,678,157 bp** in each context, including 56,661 excluded
short contigs /22,035,454 bp. CPM has 841 bins, 89,005 assigned contigs /209,605,828
bp and 36 unassigned /36,875 bp. RB has 71 bins, 80,195 assigned /189,567,480 bp
and 8,846 unassigned /20,075,223 bp. All length/origin/eligibility/marker cells,
unknown/non-target DNA, 156 full reference denominators and N-quarantine remain.
Native top-five geometry is unchanged; restricted B3 and all-bin purity have
different explicit denominators. No new AMBER, training or marker detection ran.

Local primary phase **192.469 s**, context **5.334 s**, combined sampled CPU
**196.38 s**, peak sampled tree RSS **1.257 GB** on the 8-logical-CPU/16-GiB Mac
(four numerical threads). Retained outputs before compact collection: **517,736,630
bytes /0.4822 GiB**. The closed **7,042,851-byte archive**, 51 regular members /
50,608,793 logical bytes, passed every-member readback. Full DNA FASTAs remain
locally; their included export manifests bind them. New cloud cost **$0**, no VM
or storage action/upload/extension. This is local evidence, not a new private
cloud backup. Last verified VM state remains E011's dated TERMINATED observation;
the existing $31.20/month disk quote and **October 21 review** remain separate.

Keep CPM as the working path and retain this guard as a safety comparison.
Next implement a coherent marker refinement upgrade that accounts for call
reliability, marker-quality proxies and measured parent-depth/composition context.
The ASV300.2 trade-off shows why requiring every useful marker split to improve
the already optimized graph cannot be the final quality model. The
[operations guide](OPERATIONS.md#exact-following-prompt) owns the next exact prompt.
