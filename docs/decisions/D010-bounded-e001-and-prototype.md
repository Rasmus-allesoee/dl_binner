# D010: Finish E001 at a bounded pilot scope, then build a usable prototype

Date: 2026-09-29. Status: accepted owner direction; amended seed-11 closure
completed 2026-09-30. Supersedes D002's requirement to establish a novel,
measurable residual failure before beginning our own implementation.

## Problem and owner intent

The owner clarified that the main deliverable is a usable, publishable deep-learning
metagenomic binner and learning through its development. A paper, novelty and
state-of-the-art performance are optional future outcomes. The ignored progress
note expresses loss of momentum and burnout after repeated infrastructure repairs;
it is not permission to abandon correctness or invent scientific claims.
Source note SHA256: `7749aad9a1e1dcd174dc338526593c6a252154d6a0c771b9b4e24923d88798dc` (original stays in the ignored inbox).

Owner confirmation, 2026-09-29: the outcome-informed amendment after seed 11 is
accepted because the product goal takes priority over additional runs that are
not currently expected to change the next prototype decision. Complete the
retained-output diagnostics before closing E001. This is closure at the amended
seed-11 pilot scope, not completion of the original three-seed protocol; H001
remains inconclusive.

## Evidence and decision

The [COMEBin review](../../experiments/E001-coverage-thinning/comebin-paired-observed.json)
accepts the seed-11 native execution and primary evaluation. C0 was reused, CT
completed. The [combined assessment](../../experiments/E001-coverage-thinning/seed11-assessment.md)
records all three tools, the remaining binary-evidence limitation and measured
cost. No new fits are necessary to finish the retained-output diagnostics.

1. Collect the existing arrays/labels once, using the exact hash allowlist. Complete
   the already specified candidate-selection and neighborhood/length diagnostics
   locally. Do not regenerate features, embeddings or clustering candidates.
2. **Defer seeds 23/47**, including new CT thinning/features. This is an explicit
   outcome-informed scope amendment after seeing seed 11 and measured costs,
   not completion of the original three-seed protocol. Keep the original frozen
   config and thresholds unchanged for provenance. We cannot apply its
   reproducibility criterion, establish an intervention, or reject H001 globally.
3. Close E001 with the bounded seed-11 evidence and limitations, then conduct a
   comprehensive current literature/benchmark review and source-code audit of a
   justified tool shortlist before choosing the first architecture. This is a
   high-priority design input, not a novelty gate or a requirement for a new
   benchmark campaign. Low-risk product scaffolding and learning can proceed
   without locking in the model architecture.

Remaining pairs appear computationally plausible within the original experiment
ceiling, but exact billed headroom is unknown and feasibility alone is not value.
The COMEBin seed-11 loss is 0.03643, below the 0.05 triage threshold; VAMB improves
slightly; MetaBAT2 loses much of its assigned support. These observations do not
establish the proposed reliability mechanism. Two extra COMEBin pairs would cost
about 79.3 allocated core-hours at observed stopping, with new preprocessing and
other tools additional, and longer schedules possible. Prefer getting the useful
stage evidence from what already exists.

## Alternatives and revisit condition

- Complete all three pairs now: stronger sampling/training variability evidence,
  but no guarantee it changes the first prototype; substantial owner/runtime cost.
- Stop immediately: quickest, but would leave cheap retained selection evidence
  and already computed embeddings unexamined. One collection closes this gap.
- Conduct a comprehensive current literature and benchmark review, then inspect
  source code for a justified shortlist: selected as high-priority input to the
  first architecture decision, with scope and cutoff recorded.
- Combine several strong methods immediately: not selected without evidence that
  the combination solves a concrete problem; review components first and combine
  only when there is a clear rationale.

Reconsider additional seeds only if the retained diagnostics identify a concrete
prototype decision that replication would change, with a bounded cost/value case.
Do not lower thresholds, intensify thinning or choose a favorable seed to obtain
support. If diagnostics remain inconclusive, say so and proceed to prototype design.

## Prototype decision boundary

After the comprehensive literature/code review, identify a small shortlist of
viable first-version approaches based on the evidence, intended inputs/use case,
implementation cost and learning value. Autoencoders/VAEs, contrastive learning
or other approaches may be considered if the review supports them; none is a
preset candidate or preferred architecture. Choose one coherent end-to-end first
version, explain the learning objective and input contract, and define a short
implementation milestone with CLI input/output, training/inference, bins, a
reproducible small evaluation and resource reporting.
A documented wrapper around a baseline alone is not our own learned implementation;
a new scientific contribution is not required to begin one. Advanced uncertainty,
graphs, taxonomy and foundation models need evidence to enter the first version.

Keep correctness, honest limitations, leakage controls, provenance and a publication
history/license review. A first working release does not require a paper-scale
benchmark or competitive scores. Actual GitHub publication remains a separate
owner action; this decision authorizes local preparation only.

## Completion, 2026-09-30

[Closure](../../experiments/E001-coverage-thinning/closure.md) completes the approved
retained-output scope, including every candidate, marker selection and fixed
neighborhood/length diagnostics. The CT oracle-selection gap is 0.03862; it is
a research lead, not a truth-free selector or fulfillment of the three-seed rule.
H001 stays inconclusive and seeds 23/47 deferred. The required
[current review](../evidence/2026-09-30-binner-design-review.md) is complete at its
declared cutoff; [D011](D011-first-binner-prototype.md) owns the resulting provisional
first-product choice and implementation milestone.
