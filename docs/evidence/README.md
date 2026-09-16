# Evidence

Evidence notes distinguish what a source reports, what we inspected directly, and what we infer. None of the initial notes reports a newly executed binning experiment.

| Record | Scope |
| --- | --- |
| [Thesis assessment, 2026-09-16](2026-09-16-thesis.md) | Findings worth building on, limits, and claims requiring rechecking |
| [Landscape reconnaissance, 2026-09-16](2026-09-16-landscape.md) | Recent comparison studies and methods, source/code discrepancies, review depth, and missing prior art |
| [Assets and reuse](assets.md) | Available prior work, data availability, provenance, and unresolved reproducibility details |
| [Context fingerprints](context-sources.sha256) | SHA-256 fingerprints of 42 local paper files, two thesis Markdown files, and 12 selected tool source/README files at foundation setup |

The fingerprints are an inventory, not a claim that every file has been read. Paths in that file are relative to the repository root. `python3 scripts/check_docs.py --check-context` checks files that are present and reports missing optional caches.

Add a focused note when an investigation produces useful reasoning. Give it a date, scope, source/version locators, findings, limitations, and the questions or experiments it informs. If a later investigation changes the interpretation, link the new note from the earlier one and update the affected current question. Keep full papers separate from our notes.
