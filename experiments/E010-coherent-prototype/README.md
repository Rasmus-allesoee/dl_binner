# E010: an integrated window/depth/marker prototype

Opened 2026-10-16. Status: implementation and engineering contracts; **no community
fit, changed E009 score or paid/cloud action authorized by this record**.
[D015](../../docs/decisions/D015-coherent-prototype-upgrade.md) owns the rationale.

## Prospective design, fixed before implementation/results

Implement dev4 as a separate candidate CLI path, preserving dev3 algorithms,
defaults, wheel and all E009 evidence. PR #2 merged benchmark-planning head
`bd902f4721aa780338fe961feba4ed15e4d96141` into main at
`5bd59d774306f586c22b23a2f6ee36d64947d052`, whose parents are the unchanged dev3
main `5e54538d1799e8d2538621729400f33fbaf017b9` and that research head. New branch:
`codex/coherent-prototype`. Product Linux CI passed; local E009 contracts passed
91 tests (one Linux /proc test explicitly unavailable on Mac). Local technical
review found no actionable issues; no independent approval/bot reply is claimed.

1. **Views.** Retain full ordered DNA, all length strata, depth columns, zero masks
   and exclusion reasons. For contigs >=2,000 bp, generate two independently
   seeded pairs of disjoint real windows, one from each parent half, each
   1,000–10,000 bp. Retain zero-based half-open coordinates and exact sequence
   hashes. Train on parents with usable window pairs; 500–1,999-bp contigs enter
   inference/grouping, not artificial split-positive training. Below the default
   500-bp cutoff/no usable composition stays explicitly excluded and exported;
   that configurable default is not a product performance claim. No new coverage:
   each window is conditioned on its **parent's measured mean depth**.
2. **Model.** Square-root TNF, fitted composition statistics and unit-normalized
   composition input; fitted log1p sample depth scaled by sqrt(sample count),
   preserving original zero masks. Composition MLP 136→256→128, depth MLP
   S→64→64 (absent/all-zero depth branch explicitly zero), fused MLP→128→64,
   LayerNorm/ReLU and L2 output. Symmetric NT-Xent on paired real windows plus a
   half-weight composition-only auxiliary NT-Xent to discourage an exclusively
   parent-depth shortcut. Twenty epochs, seed 11, batch 512, temperature .2,
   AdamW learning rate .001/weight decay .00001; no marker or taxonomy training,
   truth inputs, checkpoint selection or parameter grid. Other parents can be
   co-genomic negatives; chimeric parents can violate positive assumptions.
3. **Geometry/grouping.** Use the learned unit vectors directly: cosine ordering
   equals Euclidean ordering on the unit sphere. No population z-score after
   learning. Build one sparse 30-neighbor graph with PyNNDescent, exact candidate
   reranking, symmetric positive locally scaled weights; small <=2,048-row
   contracts use bounded exact neighbors. Fixed SHA-selected exact audit queries
   must achieve tie-aware recall >=.90, otherwise fail without a new search/retry.
   Leiden RB configuration partition, resolution 1, seed 11, two iterations;
   no truth K, candidate grid or marker-selected score. Groups below two contigs
   or 10 kb stay accounted unassigned. Preserve native neighbors and sparse graph.
4. **Markers/refinement.** Own native Pyrodigal meta gene calls and PyHMMER trusted
   cutoff searches with >=.5 HMM coverage, supplied hash/version/license-bound
   SCG profile asset. Cache genes, domains, chosen evidence and skipped/ambiguous
   calls by complete FASTA/asset/policy/runtime identity. No external binner.
   Deduplicate overlapping hits and ambiguous same-protein family assignments;
   same-contig duplicated markers are explicitly unreliable for constraints.
   In a pre-bin, split only on at least two independent clean repeated marker
   families whose distinct-contig conflicts support separation. Use the most
   repeated clean family as deterministic seeds for constrained spherical
   refinement; at most 10 iterations. Ambiguous/no-confident-affinity assignments
   may remain unassigned. Keep unsplittable/unreliable evidence explicit, never
   claim marker absence is genome absence or discard marker-negative DNA.
   Preserve both pre/post partitions and exports, including every DNA record.

These defaults are engineering priors informed by the completed source/literature
review and E009, not independently established optimal settings. Alternatives
(marker training, taxonomy, GLM, context attention, assembly graphs and ensembles)
remain deferred. Candidate-vs-dev3 will establish a bundle result. Pre/post
refinement is the cheap paired diagnostic; another fit ablation requires a
decision-changing uncertainty. No factorial campaign is required.

## Contracts and execution boundary

Local checks: independent owned CPU environment; native tiny DNA-window, training,
reload, approximate/exact-neighbor, marker cache/refinement and complete export
contracts; built wheel tested outside checkout; wheel/sdist/rebuild inspection.
Retain failed attempts and distinguish actual native paths from substituted tests.
Cheap engineering fixtures do not establish biological accuracy/full-scale cost.
Keep truth outside the training/feature CLI and use admitted v2 and independent
sequence truth only during later authorized evaluation.

The first community comparison will reuse E009's full sample-0 assembly and
ordered samples 0,2,3,4,6,9,10,11,14,17; reuse accepted dev3 outputs without a refit.
Before changed scores, freeze additional confirmation inputs/protocol and preserve
their development/source overlap limitations. No data acquisition in this task.
Resource/cost bounds and the exact future approval prompt will be added after
local engineering checks. Prior $20/$2 authorizations do not carry over.
Existing cloud storage retention review remains **2026-10-21**; no extension.

