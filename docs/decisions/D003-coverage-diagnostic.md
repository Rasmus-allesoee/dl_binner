# D003: Diagnose Coverage Loss on a Fixed Public Assembly

Date: 2026-09-17
Status: superseded in dataset/mapper/compute choices by [D004](D004-human-cpu-preflight.md), 2026-09-18; diagnostic rationale retained
Scope: authorize implementation and preflight of E001; scientific execution remains gated by its data/environment checks and owner-operated UCloud budget
Refines: [D002](D002-investigate-before-architecture.md)

## Evidence and problem

The [targeted audit](../evidence/2026-09-17-targeted-audit.md) finds existing coverage normalization, augmentation, adaptive weighting and uncertainty mechanisms. It does not establish an unaddressed failure. A coverage matrix with smaller numbers is not necessarily less informative after preprocessing, whereas removing mapped read templates changes sampling noise and zero observations.

We need an affordable distinction between preprocessing effects, genuine input-information loss, representation loss and clustering/selection loss. The owner's feedback also correctly requires community benchmarks alongside question-specific simulations; the [data audit](../evidence/2026-09-17-benchmark-data.md) identifies a released known-origin starting point.

## Decision

Create [E001](../../experiments/E001-coverage-thinning/README.md): CAMI II Marine short-read pooled GSA; fixed contigs/sample columns; native MetaBAT2, VAMB default VAE and COMEBin; paired full-versus-thinned read evidence and a feature-rescaling control. Preserve stage outputs and evaluate with AMBER plus a small diagnostic layer. First implement fixtures, source/data verification and a portable preflight, not a new binner.

Treat the experiment as **development and diagnosis**, not SOTA evaluation. It cannot by itself support a new uncertainty method, explain the thesis's pooled-reference dilution, establish real-assembly performance, or demonstrate generalization to unseen genomes.

## Serious alternatives

- New CAMISIM community first: more control over strain and abundance structure, but adds genome selection and simulator validity before the simplest coverage question is tested. Use later when a particular mechanism requires it.
- Newest CAMI III challenge first: valuable independent evaluation, but assembled-data release is scheduled later and challenge data should not become an unrestricted tuning target. The available toy data remain an alternative, not a mandatory dependency.
- UncertainGen/GenomeFace/QuickBin/McDevol as a new-method starting point: important prior art, but no evidence yet chooses their mechanism. Their limitations are not proved by code inspection.
- Large refreshed benchmark: broad relevance but greater execution cost and weaker causal isolation. Expand only after identifying a failure or needing cross-community confirmation.
- A common-clusterer embedding contest: useful later, but may remove native information and reward one geometry. First preserve native stages and make narrower diagnostic comparisons.

## Consequences and revisit criteria

Lower recovery after thinning alone is expected and does not establish H001. Continue toward a mechanism only if a reproducible, materially sized loss coexists with evidence of retained signal or a better existing native candidate partition. An oracle candidate choice is only a bound, not an implementable improvement.

If no informative failure appears, close E001 honestly and redirect; do not add increasingly severe perturbations until a preferred story appears. If the loss is predominantly filtering or selection, move the intervention there. If the data lack the targeted short-contig population, record that limitation and design a separate controlled simulation rather than silently changing this protocol after scores are visible.

Before any proposed reliability method is called novel or superior, directly compare its mechanism with the relevant QuickBin development/published versions, McDevol and GenomeFace, and refresh uncertainty prior art. These are not all required for the first stage-localization run. Final benchmark datasets, novel architecture and publication decisions remain open.
