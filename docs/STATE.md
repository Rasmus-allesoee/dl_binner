# Current Research State

Updated: 2026-09-16

This is the single current handoff. Detailed evidence belongs in the linked records; this page stays short.

## Where we are

- The intent is defined in [PROJECT_INTENT.md](../PROJECT_INTENT.md).
- Initial repository, thesis, literature, and limited source-code reconnaissance is documented in the [assessment](research/2026-09-16-initial-assessment.md) and [evidence index](evidence/README.md).
- No new model, training run, benchmark, or scientific result has been produced. Existing thesis results are prior evidence, not experiments in this project.
- [D001](decisions/D001-research-record.md) establishes the documentation and provenance system. [D002](decisions/D002-investigate-before-architecture.md) records the provisional choice of the next investigation.

## Immediate direction

Investigate **recoverable sequence lost or misassigned by current binners**, starting with fragmented prokaryotic assemblies and weak or misleading coverage information. This is a diagnostic focus, not a locked target regime or a claim of novelty.

The immediate deliverable is a bounded literature/code audit and a reproducible diagnostic experiment protocol. It must identify a residual failure, a plausible cause, the relevant existing methods, and an affordable test that can disprove our explanation. The [assessment](research/2026-09-16-initial-assessment.md) defines the work and stopping criteria.

Start with [Q001](research/questions.md#q001) and [Q002](research/questions.md#q002). [H001](research/questions.md#h001) is an untested candidate about coverage reliability; it is not an approved model design. Representation learning and clustering both remain possible intervention points.

## Next session

1. Resolve the paper/code/version questions for the small candidate baseline set in the [landscape note](evidence/2026-09-16-landscape.md). Determine native input requirements and how to retain contig assignments and embeddings.
2. Define the information available to each method and draft one diagnostic protocol using the [experiment convention](../experiments/README.md). Design new simulations where the research question requires them.
3. Check a small subset of the [available thesis artifacts](evidence/assets.md) for useful reuse. Obtain a file inventory from the owner before making UCloud-dependent execution plans.
4. Record a decision to pursue, modify, or reject the proposed diagnostic direction once the audit and protocol expose its value and limitations. No large training job is needed to make this decision.

## Open dependencies

- The owner confirmed on 2026-09-16 that the original contigs, coverage matrices, bin assignments, and CAMISIM truth files are available on UCloud. Their exact locations, hashes, and correspondence remain unverified here. They do not prescribe the new benchmark or simulation design.
- HPC is owner-operated. Codex prepares commands, small checks, and expected outputs; the owner launches jobs and returns outputs. Remaining access duration and practical storage/compute budgets are not established.
- Local third-party tool folders have no `.git` metadata. They are readable source snapshots, not pinned runnable baselines.
- The final target regime, train/development/evaluation split, final baseline versions, and success thresholds remain open. See the [question register](research/questions.md).

## Git and continuity

- Local branch: `main`. Baseline commit `2b87cd9` preserves the supplied context before the foundation changes. Use `git log` for subsequent commits rather than copying the current HEAD into this page.
- No remote is configured. An authenticated lookup of `Rasmus-allesoee/dl_binner` on 2026-09-16 could not resolve that repository. This does not rule out another name or account.
- The thesis repository was inspected read-only at commit `4029b810045ff9196be0035e48e7fb32ca4be792`; it was clean and had no local remote configured. Its two thesis Markdown files match this repository's copies byte for byte.
- Original planning remains in [history](history/README.md), explicitly nonbinding. New superseded decisions and experiments retain their own identities and links.

Update this page whenever the immediate direction, significant evidence, or execution dependencies change. Do not turn it into a chronological session log.
