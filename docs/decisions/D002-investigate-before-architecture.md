# D002: Investigate Recoverable Failures Before Choosing an Architecture

Date: 2026-09-16
Status: superseded in its implementation gate by [D010](D010-bounded-e001-and-prototype.md), 2026-09-29; the completed evidence audit remains useful. Original status: accepted
Scope: provisional next research block; no model or final benchmark selected

Progress, 2026-09-17: the targeted audit and first protocol are complete. [D003](D003-coverage-diagnostic.md) refines the next action to E001 implementation/preflight, preserving this decision's failure-before-architecture principle. No residual error or new method has yet been demonstrated.

## Problem and evidence

The [thesis](../evidence/2026-09-16-thesis.md) identifies workflow effects, quality-estimator disagreements, and different loss/contamination patterns. It does not establish which residual failure in current software is both solvable and insufficiently addressed. The [landscape reconnaissance](../evidence/2026-09-16-landscape.md) shows substantial existing work on taxonomy, learned sequence features, marker guidance, and uncertainty.

## Decision

Prioritize a bounded literature/code audit followed by specification of a small diagnostic experiment. Investigate recoverable contig loss and incorrect assignments under fragmented assemblies and weak or misleading coverage as the initial candidate focus. Separate input information, representation learning, clustering, and evaluation effects before choosing an intervention.

The immediate protocol and its keep/modify/abandon criteria are described in the [assessment](../research/2026-09-16-initial-assessment.md). Track [Q001](../research/questions.md#q001), [Q002](../research/questions.md#q002), and the untested [H001](../research/questions.md#h001).

## Alternatives

- Begin a new VAE, transformer, or multimodal binner now: fast to obtain runnable code, but the causal target and difference from existing methods are not established.
- Repeat the whole thesis benchmark with every new tool: valuable eventual validation, but unnecessarily broad for identifying the first intervention.
- Prioritize long-read or graph-based recovery: serious alternative, especially if assembly irreversibly removes the relevant information; requires different data and baselines.
- Develop a quality estimator or ensemble first: addresses thesis findings directly, but changes the immediate methodological task and risks optimizing another proxy.

## Consequences and revisit condition

Do not train a large new model during this foundation task. Reuse thesis code and artifacts where useful, while designing fresh simulations for the chosen question. The owner confirmed availability on UCloud and explicitly rejected treating the thesis datasets as compulsory.

Modify or replace this direction if the audit shows the failure disappears with correct configuration, is already handled by current methods, or reflects information absent from the input. Continue only with a measurable remaining failure, a discriminating experiment, and a plausible methodological contribution. No improvement or novelty is claimed at this point.
