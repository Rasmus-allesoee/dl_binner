# Evidence

Evidence notes distinguish what a source reports, what we inspected directly, and what we infer. Experiment directories own execution records; notes can interpret their accepted results and audit the next decision.

| Record | Scope |
| --- | --- |
| [Thesis assessment, 2026-09-16](2026-09-16-thesis.md) | Findings worth building on, limits, and claims requiring rechecking |
| [Landscape reconnaissance, 2026-09-16](2026-09-16-landscape.md) | Recent comparison studies and methods, source/code discrepancies, review depth, and missing prior art |
| [Targeted paper/code audit, 2026-09-17](2026-09-17-targeted-audit.md) | Native information paths, normalization, relevant uncertainty/weighting prior art and AMBER semantics for E001 |
| [Public benchmark audit, 2026-09-17](2026-09-17-benchmark-data.md) | CAMI II development-data contract, fresh acquisition and verified CAMI III distinctions |
| [Tool snapshots, 2026-09-17](2026-09-17-tool-snapshots.json) | Exact selected source commits and checkout qualifications; not an executable environment lock |
| [Human-data and CPU audit, 2026-09-18](2026-09-18-human-cpu-audit.md) | GI acquisition/ID contract, mapper alternatives, CPU-only reassessment and unresolved native feasibility |
| [GI provenance review, 2026-09-19](2026-09-19-gi-provenance.md) | Foreign-simulation header evidence, source-bound quarantine, inventory code corrections and fresh-job handling |
| [GI historical taxonomy, 2026-09-20](2026-09-20-gi-taxonomy.md) | Verified CAMI archive, complete taxid coverage and locally validated evaluation population |
| [Assets and reuse](assets.md) | Available prior work, data availability, provenance, and unresolved reproducibility details |
| [Context fingerprints](context-sources.sha256) | Current local fingerprints: 45 paper files, two thesis Markdown files, and 36 selected source/README files; historical versions remain in Git |

The fingerprints are an inventory, not a claim that every file has been read. Paths are relative to the repository root. `python3 scripts/check_docs.py --check-context` checks present files and reports missing optional caches. The foundation commit `2d1b6ce` retains the original inventory; `2b1e51b` preserves the owner's updated paper fingerprints. On 2026-09-17, replaced ZIP-tool entries were retired from the current inventory and inspected clone/source paths were added. Historical notes' old local paths may therefore be unavailable; use the newer audit for current source access.

Add a focused note when an investigation produces useful reasoning. Give it a date, scope, source/version locators, findings, limitations, and the questions or experiments it informs. If a later investigation changes the interpretation, link the new note from the earlier one and update the affected current question. Keep full papers separate from our notes.

- [2026-09-30: current binner design review and source audit](2026-09-30-binner-design-review.md)

- [2026-09-30: D011 architecture reassessment, thesis and GLM tradeoffs](2026-09-30-architecture-reassessment.md)
- [2026-10-08: focused competitive study, CAMI data and source/overlap provenance](2026-10-08-competitive-binner-study.md)

- [2026-10-14: CompleteBin peak storage, BAM/assembly multipliers and native retention](2026-10-14-completebin-storage.md)

- [2026-10-25: DCVBin input workload and reliable marker-learning source audit](2026-10-25-dcvbin-efficiency-and-marker-learning.md)

- [E023 information, recovery and the next measured-depth block](2026-10-27-e023-information-and-recovery.md)

- [E024 accepted data, failed retrieval and the next recovery block](2026-10-28-e024-retrieval-failure-and-next-block.md)
- [E025 useful depth, unequal evidence and the next recovery block](2026-10-29-e025-depth-evidence-and-next-block.md)

- [E026 recovery, source reassessment and one common full version](2026-10-30-e026-recovery-and-common-version.md)
