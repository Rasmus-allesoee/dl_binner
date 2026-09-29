# Current Research State

Updated: 2026-09-30. This is the single current handoff.

## Direction and completed work

Build and publish a usable deep-learning metagenomic binner while learning through
implementation. A paper, novelty and SOTA remain optional. See
[PROJECT_INTENT](../PROJECT_INTENT.md), [D010](decisions/D010-bounded-e001-and-prototype.md)
and [D011](decisions/D011-first-binner-prototype.md).

**E001 is closed at its approved amended seed-11 scope.** The diagnostic collection
passed checksum and all 297 retained-file checks. All 240 COMEBin candidates,
marker scores, embedding axes and fixed neighborhood/length diagnostics were
inspected directly. [Closure](../experiments/E001-coverage-thinning/closure.md)
owns results and limitations. The original three-seed criterion and H001 remain
unresolved; seeds 23/47 stay deferred. No accepted preprocessing, feature extraction,
training, clustering or collection should be repeated.

Primary R95 C0→CT: MetaBAT2 0.44294→0.19502; VAMB 0.46177→0.48764;
COMEBin 0.83899→0.80255. COMEBin CT has a 0.03862 truth-best candidate-selection
gap; C0 has zero. Learned short-contig neighborhoods remain better on average than
combined raw features, although localized losses exist. These are one-community
single-seed development observations, not a validated intervention.

The required [current literature/benchmark review](evidence/2026-09-30-binner-design-review.md)
and [source audit](evidence/2026-09-30-design-source-audit.json) are completed at the
2026-09-30 cutoff, with depth/access limits explicit. They considered reconstruction,
contrastive, graph, taxonomy, pretrained sequence and efficient neural merging
before recommending a compact VAE as a provisional first-product tradeoff.

## Exact next step

Implement **D011 milestone one locally**: our own small VAE binner accepting FASTA
and an explicit mean-depth matrix, with feature validation, training, saved-model
inference, one fixed density clustering path, assignments/bin FASTAs, hashes,
progress and resource reporting. Deliver a real tiny end-to-end run plus meaningful
failure/round-trip checks and a raw-feature clustering control. The decision owns
initial defaults, acceptance limits, serious alternatives and revisit conditions.
This is not a VAMB wrapper or a claim to reproduce its scores.

No owner upload or UCloud command is needed now. No large training run, new E001
seed, pretrained download or new simulation is part of the first milestone.
Once the local pipeline works, prepare a separate bounded development evaluation
using retained E001 features and frozen evaluators; commit settings before execution.
Do not tune against the CT oracle or silently convert E001 into an independent test.

## Resources and continuity

COMEBin successful conditions used 39.6462 allocated core-hours; the known recovery
sequence lower bound is 58.1075. MetaBAT2/VAMB pair: 0.76946. The new collection
adds 0.002224 (1 vCPU / 4 GB, 8.0065 driver seconds). These are partial accounting,
not exact billing or a remaining-balance estimate. Successful COMEBin condition
files total 11.313 GB; the diagnostic archive is an additional 235.13 MB copy.
Preserve retained assets/old attempts. No deletion is authorized.

UCloud remains CPU-only and owner-operated. Persistent prefixes stay under
`e001-gate0/envs/` per [D006](decisions/D006-environment-ownership.md). Frozen E001
source/configuration and raw observed records remain unchanged.

Local branch: `e001-gate0`; no remote, push or publication. `agent_context/` is an
ignored inbox. Before publication review licensing and historical source packaging
per [D001](decisions/D001-research-record.md). Update this handoff when direction,
significant evidence or execution dependencies change; details belong to their owners.
