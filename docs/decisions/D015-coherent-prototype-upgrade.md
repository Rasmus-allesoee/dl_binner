# D015: a coherent prototype upgrade with selective ablations

Date: 2026-10-16. Status: **accepted for the first integrated implementation**.
The owner subsequently authorized local implementation/engineering checks and
the normal benchmark-planning PR merge. [E010](../../experiments/E010-coherent-prototype/README.md)
owns the prospective algorithms/defaults, implementation, contracts and separate
future execution request. Community fits, VM wake/spending and retention extension
were not needed for implementation and have not occurred.

## Decision and why it changes

Recommend building a substantially stronger, integrated next prototype. Incorporate
marker-conflict handling into its grouping/refinement module; **do not require a
standalone split of dev3 bins first**. That narrower experiment remains an optional
cheap diagnostic, not the next milestone or a gate to implementation.

The concern about slow serial feature experiments is well founded as a workflow
risk. AGENTS had turned a useful causal-inference rule into a requirement to test
one mechanism before combining improvements. Engineering a coherent candidate and
establishing which ingredient caused its gains are different tasks. Existing
literature, source observations and thesis evidence can justify implementing a
bundle; matched ablations are needed for specific causal claims or design choices
whose uncertainty matters, not for permission to build every ingredient.

This does not establish a universal checklist of mandatory SOTA components. Tools
use markers at different stages; repeated use supports a strong engineering prior,
not proof that marker-aware training, grouping and selection must all help here.
Network size is also not the development objective. Choose components that address
the same biological task and fit one explicit computational/data contract.

## Evidence reused, without another review campaign

- [The completed field/source review](../evidence/2026-09-30-binner-design-review.md)
  and [October focused study](../evidence/2026-10-08-competitive-binner-study.md)
  support real sequence views, composition/abundance learning and biological
  grouping/refinement. COMEBin and SemiBin2 combine several of these; MetaCAT
  also illustrates the importance of grouping without requiring a neural encoder.
  Their whole-tool results do not identify individual causal contributions.
- [The thesis reassessment](../evidence/2026-09-30-architecture-reassessment.md)
  reports strong CompleteBin/COMEBin/SemiBin2 recovery, with different resources,
  versions and patched outputs. These are prior thesis results, not reproduced
  project results. Its resource and proxy-quality qualifications still apply.
- [E001](../../experiments/E001-coverage-thinning/closure.md) found similar local
  neighborhoods with very different final recovery. [E003/E004 evidence](D011-first-binner-prototype.md)
  also shows neighbor agreement alone cannot choose a representation or clusterer.
- [E009's completed review](../../experiments/E009-competitive-benchmark/controls-review.json)
  at `cc6dd1c` shows both useful information and multiple losses: bacterial
  ten-depth neighbor agreement 68.63→67.05% after learning, primary restricted
  grouping recall 18.48→37.61%, weighted conservative reference recovery
  4.5765→5.3911%, and substantial mixing/fragmentation. Only 18.5321% of the full
  provided bacterial reference bases have confirmed unique loci in this assembly;
  the 3.3034% N-quarantine remains. These data do not isolate an encoder-only or
  grouping-only cause, and do not decide product feature families.
- Direct source inspection here, at preserved dev3 source
  `5e54538d1799e8d2538621729400f33fbaf017b9`: `Encoder.forward` and `nt_xent` in
  [model.py](../../src/dl_binner/model.py) use normalized dot-product geometry;
  [clustering.geometry](../../src/dl_binner/clustering.py) subsequently z-scores
  embedding dimensions and normalizes again. This changes the metric. It is a
  concrete interface/design issue to resolve, not a newly measured cause of E009
  error or permission to repair the preserved dev3 outputs in place.

Focused primary-source checks on October 16 agree with the existing interpretation:
[COMEBin's author overview](https://github.com/ziyewang/COMEBin#overview) describes
sequence-substring views, a coverage network, a combined network and Leiden;
[SemiBin's grouping source](https://github.com/BigDataBiology/SemiBin/blob/main/SemiBin/cluster.py)
contains graph grouping and marker-seeded reclustering, and its
[training source](https://github.com/BigDataBiology/SemiBin/blob/main/SemiBin/self_supervised_model.py)
contains split-pair learning. These mutable source links are dated observations,
not new executable pins. Publisher paper retrieval failed here; the completed
paper reviews and their versioned source provenance are reused, not claimed reread.

## Recommended first integrated candidate

| Part | Include in the next implementation | Purpose and important boundary |
| --- | --- | --- |
| Biological training views | Actual DNA windows/splits from sufficiently long contigs, with traceable parent/window coordinates and a declared short-contig policy | Learn agreement between genomic fragments rather than only masked copies of one feature vector. A chimeric parent can violate the same-genome assumption; do not claim biological labels from contig identity. |
| Composition and abundance model | Explicit modality-specific encoders/fusion, documented depth scaling/zeros and fitted transforms; consistent declared training/inference/grouping geometry | Retain useful measured coverage while improving the representation contract. Choose a justified compact network and defaults once during implementation; a larger Transformer is not required. Sequence-only and one/multiple-depth inputs remain explicit modes. |
| Genome-scale grouping | One scalable sparse-graph grouping path with a declared metric and parameters, followed by marker-informed refinement including conflict splitting | Address fragmentation and mixing together at the pipeline level. Preserve pre/post-refinement partitions. Avoid a large candidate grid, truth K or a selector tuned to E009 labels. Validate approximate-neighbor contracts if an approximate index is chosen. |
| Reusable marker evidence | Versioned gene/marker detection cache with hit provenance, deduplication and absence/ambiguity handling; use it in grouping/refinement first | Same-SCG hits can provide separation evidence, not positive genome identity. Multicopy biology, split genes and short contigs weaken constraints. Marker-negative DNA needs a real assignment/noise path, never exclusion by default. Evaluate with sequence truth, not solely the markers used to choose bins. |

These are related modules in one prototype, not four sequential biological trials.
Preserve their intermediate contracts and test them while integrating. Reuse sound
product I/O, provenance, accounting and supervision rather than rebuilding those.
The exact view lengths/count, architecture sizes, graph algorithm and refinement
rules belong in a concise prospective implementation decision, followed directly
by code and real tiny contracts in the same work block. No second exhaustive
architecture review or separate sign-off per ingredient is needed.
Pin reusable marker assets/tools and their licenses before using or redistributing
them; do not copy an external binner behind our CLI and call it our new method.

Use the accepted mean-depth matrix initially. Parent-contig means are not measured
window coverage, and within-contig variance cannot be recovered from those means.
If parent depth conditions a sequence window, name that assumption explicitly.
Any request for actual window depth/variance needs an explicit retained-BAM scan
and resource case; it must not imply a new mapping/data-DAG run or silent imputation.

Keep marker-aware training/false-negative handling as a serious later design
choice, rather than automatically adding it to every marker role. Its use can be
reconsidered within implementation if source/availability evidence changes the
case; a new empirical claim needs a matched control. Frozen GLM/context attention,
taxonomy databases, assembly-graph inputs, backbone pretraining and large ensembles
remain alternatives, not defaults for this candidate. Existing GLM evidence and
the separately requested follow-up are preserved; they are not blockers.

## Validation that supports faster development

1. Implement one complete candidate on a new research branch, keeping immutable
   dev3 source/wheel and all E009 data, truth, outputs and failed journals intact.
   Unit tests and tiny end-to-end training/reload/marker/export contracts are
   engineering checks, not separate performance studies. No community fit now.
2. Prepare one bounded candidate-versus-dev3 development comparison. Reuse the
   accepted baseline outputs; do not refit dev3 just to populate a new table.
   Prospectively fix the candidate, inputs, evaluator contracts and budgets.
3. Retain the pre/post-marker-refinement outputs from the same encoder/run. This
   cheap paired comparison can inform whether refinement adds value. A changed
   positive/negative objective would require another fit; run that only if its
   uncertainty could change the design. No full factorial or mandatory ablation
   for every normalizer, layer, graph option and marker role.
4. Choose/freeze additional human-associated confirmation data before changed
   community scores, in parallel with implementation. Dataset preparation is not
   a gate to writing code. E009/E005 remain development data; overlap limitations,
   all length/origin strata and independent truth must stay visible.

A gain of the integrated candidate establishes a **bundle-level** improvement,
not the cause, novelty or necessity of each component. Published ablations and
source studies are reusable prior evidence. Selective ablations of our candidate
or, exceptionally, a justified external tool can resolve remaining consequential
uncertainties. They are not a compulsory external-tool campaign. No external fit,
including CompleteBin, is recommended now.

## Alternatives, reconsideration and boundaries

Standalone marker splitting is cheaper and causally cleaner for that narrow
operation, but keeps weak views/geometry and fixed grouping in place. It may be
useful as a cached diagnostic later; it is too narrow as the default next product
milestone. A maximal stack of GLM, taxonomy, attention, GNN and marker losses would
expand dependencies, costs and failure modes without a coherent current case.
Neither alternative is preferred.

Modify the candidate if real contracts show unusable marker availability, invalid
view/coverage assumptions or an unaffordable grouping path. Retain the failure and
choose an explicit design adjustment, without an automatic family/tool search.
If the integrated version fails to improve useful recovery at controlled impurity,
diagnose the retained stages and select the ablation that can change a decision.
Do not explain away a failed result with ever more components or tuned E009 scores.

The original reassessment changed guidance only; the later owner prompt authorized
the local implementation now recorded in E010. Community fits, bulk acquisition/
assembly/mapping, paid cloud compute, new resources and retention extensions remain
separate scopes; the first bounded candidate run has its own proposed approval.
The prior $20 data and $2 control ceilings are not an open budget for the upgrade.
The October 21 disk-retention review is unchanged. [STATE](../STATE.md) and
[E009 operations](../../experiments/E009-competitive-benchmark/OPERATIONS.md#exact-following-step-prompt)
own the current handoff and exact implementation prompt.
