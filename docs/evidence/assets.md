# Assets and Selective Reuse

Last checked: 2026-09-16. "Owner-confirmed" availability is distinct from a file or checksum verified by Codex.

## A001: Thesis repository

- Local checkout inspected: `/Users/rasmusallesoeenielsen/Documents/Speciale/hadal-binning-benchmark`.
- Commit: `4029b810045ff9196be0035e48e7fb32ca4be792`; branch `main`; clean on inspection; no remote configured in that checkout.
- Upstream locator supplied by project guidance: [Rasmus-allesoee/hadal-binning-benchmark](https://github.com/Rasmus-allesoee/hadal-binning-benchmark). The local checkout was the source inspected for this task.
- Documentation inspected: `README.md`, `docs/limitations.md`, `docs/data_availability.md`, `strain_sim/README.md`, and the relevant beginning of `strain_sim/config/config_strain.yaml`.
- The repository describes a portable analysis layer based on tracked small tables, and a heavy workflow layer with UCloud paths and incompletely pinned external environments. No workflow or analysis was executed here.

| Candidate reuse | Location in that repository | Required check before reuse |
| --- | --- | --- |
| Per-genome and QC summaries | `real_benchmark/data/`, `real_benchmark/analysis/` | Exact filtering population, identifiers, quality definitions, and selection bias |
| Workflow definitions | `real_benchmark/workflow/Snakefile` | Native tool modes, patches, paths, environment/database versions, and input contracts |
| Simulations and AMBER conversion | `strain_sim/workflow/Snakefile_strain`, `strain_sim/workflow/scripts/` | Truth construction, unique IDs, duplicate contigs, sequence identity, shared-region handling |
| Strain result tables | `strain_sim/analysis/tables/` | Strain/pair denominators and pairing of configurations to results |
| Ensemble diagnosis | `ensemble/analysis/`, `ensemble/workflow/` | Coupling to the simulation, selector version, pre/post-refinement outputs |
| Compute accounting | `real_benchmark/benchmarks/`, `docs/compute_requirements.md` | Preprocessing attribution, parallelism, hardware comparability |

These are reuse candidates, not dependencies imported into this project. Port a small component with attribution and tests only when the first protocol needs it.

## A002: Original hadal data and intermediate artifacts

The owner confirmed on 2026-09-16 that original contigs, coverage matrices, and bin assignments remain available on UCloud. Availability is owner-confirmed; precise paths, formats, hashes, and completeness have not been checked here.

The old `docs/data_availability.md` says an external archive is available, but its ENA accession and Zenodo DOI fields are placeholders. Do not treat those links as a working retrieval path. The present available location is the owner's UCloud storage.

Use these artifacts for case studies, inspection of lost contigs, or a later real-data check. They are familiar research data and cannot be described as an untouched final test set.

## A003: Original CAMISIM artifacts

The owner also confirmed UCloud availability of the thesis CAMISIM truth files and associated original artifacts. Their identity and alignment to contig/bin files need a small returned inventory before use.

The existing simulation design is characterized in the [thesis note](2026-09-16-thesis.md). It can help debug truth evaluation and reproduce a specific pathology. The owner explicitly stated that this project should create its own optimized simulations when needed; there is no requirement to use the old design.

## A004: Local tool source cache

`agent_context/tools_repo/` contains 25 tool directories (about 324 MB), with no `.git` directories found within the inspected depth. Examples include VAMB/TaxVAMB, COMEBin, SemiBin, CompleteBin, GenomeFace, SCGBinner, DCVBin, REMAG, and LorBin, plus evaluation/workflow dependencies.

Directory names ending in `main` or `master` do not identify a release. Selected files consulted in the [landscape note](2026-09-16-landscape.md) have [recorded hashes](context-sources.sha256). Before a baseline run, obtain a verified upstream tag or commit, environment, model weights, and database versions. Keep any compatibility patch explicit and report it with the baseline.

## A005: Local paper cache

The cache contains 40 Markdown paper files and two PDFs across methods, benchmarks, evaluation, and foundation models. File names can be stale: the QuickBin cache points to a preprint, while a journal article was found during the current search. `Arangasamy_2025_paper_old.md` is a separate historical copy, not independent evidence.

The [landscape](2026-09-16-landscape.md) records what was actually screened. Mathematical expressions are missing in portions of some extracted text; verify the original before using such expressions. Full paper text is preserved locally, with a fingerprint inventory, instead of being replaced by our summaries.

## Before an artifact becomes an experimental input

Create a small input manifest alongside the experiment containing source/accession, immutable version or checksum, sample/genome/contig IDs, preprocessing, storage/retrieval instructions, and split role. Check joins by identifiers and lengths rather than relying on row order. State what is unavailable or uncertain. A recorded UCloud path must not become a hard-coded assumption in reusable code.

There is no project training or evaluation dataset selected yet. H200-class GPU and large-memory access are owner-reported capabilities, not allocated resources or executed jobs.
