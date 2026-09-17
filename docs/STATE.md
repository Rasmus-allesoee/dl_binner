# Current Research State

Updated: 2026-09-17

This is the single current handoff. Detailed evidence belongs in the linked records; this page stays short.

## Where we are

- The intent is defined in [PROJECT_INTENT.md](../PROJECT_INTENT.md).
- The targeted [paper/code audit](evidence/2026-09-17-targeted-audit.md) and [public-data audit](evidence/2026-09-17-benchmark-data.md) are complete for designing the first diagnostic, building on the [initial assessment](research/2026-09-16-initial-assessment.md).
- [E001](../experiments/E001-coverage-thinning/README.md) is a prospective protocol, not an implemented or executed experiment. No new model, training run, benchmark score or demonstrated methodological gap exists yet.
- [D003](decisions/D003-coverage-diagnostic.md) refines [D002](decisions/D002-investigate-before-architecture.md): implement and preflight a fixed-assembly coverage diagnostic. [D001](decisions/D001-research-record.md) still governs the research record.

## Immediate direction

Investigate **where reduced coverage evidence loses recoverable sequence**, starting with CAMI II Marine's short-read pooled gold-standard assembly and native MetaBAT2, VAMB and COMEBin. Compare pair-preserving read thinning with full evidence, plus a preprocessing-only scale control, holding sequences and sample identities fixed.

The audit found live total-abundance input in current VAMB and coverage in the inspected DCVBin path, native marker/selection effects, and relevant reliability prior art in GenomeFace, UncertainGen, McDevol and QuickBin. Lower scores after removing reads alone will not support H001: we need evidence that usable signal survives but is lost downstream. AMBER is the chosen standard evaluator; the supplementary diagnostic summaries still need implementation and tests.

E001 is development/diagnosis, not SOTA evaluation, real-assembly validation or a demonstration of unseen-genome generalization. [H001](research/questions.md#h001) remains untested; architecture and the final target regime remain open.

## Next session

1. Implement **E001 Gate 0**: minimal experiment-specific configuration, acquisition/provenance checks, native adapters, evaluator/normalization fixtures and a local smoke check. Do not build a new model or general benchmark framework.
2. Prepare Gate 1's fresh-download and inventory commands for owner-operated UCloud, starting with setup/truth. Return exact required outputs and storage estimates. No thesis artifacts are required.
3. Freeze data identities and runtime environments, then inspect returned preflight outputs before preparing the paired scientific pilot. The protocol contains fixed conditions, endpoints, seeds, triage thresholds and resource ceilings.

## Open dependencies

- The owner confirmed **fresh CAMI II Marine downloads are needed** on 2026-09-17. Archive metadata is verified; payloads, members, hashes and exact truth correspondence are not. See [data contract](evidence/2026-09-17-benchmark-data.md).
- HPC is owner-operated. Work directory, practical budget/access duration and available environments must be established before jobs. No local action from the owner is needed for Gate 0.
- Selected source commits are recorded in [tool snapshots](evidence/2026-09-17-tool-snapshots.json); runnable environments are not yet validated. GenomeFace is unversioned, McDevol has an abnormal index state, and DCVBin lacks a model payload. These optional comparisons do not block the core E001 preflight.
- CAMI III is active; its challenge assemblies are scheduled for 2026-10-15. Toy data are available. Neither availability nor public truth should be inferred from the stale About page; see the data audit.
- Original thesis artifacts remain owner-confirmed on UCloud and optional. Final evaluation/success claims remain open in the [question register](research/questions.md); E001 has only scoped diagnostic criteria.

## Git and continuity

- Local branch: `main`. Baseline commit `2b87cd9` preserves the supplied context before the foundation changes. Use `git log` for subsequent commits rather than copying the current HEAD into this page.
- No remote is configured; the owner clarified it has not been created. Nothing has been published or pushed.
- Thesis source and figures need not be part of the eventual public project's working tree. They are already in local Git history; leave them intact until the separate pre-publication packaging decision in [D001](decisions/D001-research-record.md#source-packaging-clarification-2026-09-17). Do not rewrite history silently.
- Original planning remains in [history](history/README.md), explicitly nonbinding. New superseded decisions and experiments retain their own identities and links.

Update this page whenever the immediate direction, significant evidence, or execution dependencies change. Do not turn it into a chronological session log.
