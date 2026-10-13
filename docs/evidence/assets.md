# Assets and Selective Reuse

Updated: 2026-09-18. Each entry distinguishes inspection date and owner-confirmed availability from verified files/checksums.

## A001: Thesis repository

- Local checkout inspected on 2026-09-16: `/Users/rasmusallesoeenielsen/Documents/Speciale/hadal-binning-benchmark`.
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

Source-packaging clarification, 2026-09-17: the thesis is prior research, like the other papers, not project implementation. Its complete text/figures need not be in the eventual public working tree. They are already tracked in local history; [D001](../decisions/D001-research-record.md#source-packaging-clarification-2026-09-17) records why no deletion/history rewrite was performed during this audit.

## A002: Original hadal data and intermediate artifacts

The owner confirmed on 2026-09-16 that original contigs, coverage matrices, and bin assignments remain available on UCloud. Availability is owner-confirmed; precise paths, formats, hashes, and completeness have not been checked here.

The old `docs/data_availability.md` says an external archive is available, but its ENA accession and Zenodo DOI fields are placeholders. Do not treat those links as a working retrieval path. The present available location is the owner's UCloud storage.

Use these artifacts for case studies, inspection of lost contigs, or a later real-data check. They are familiar research data and cannot be described as an untouched final test set.

## A003: Original CAMISIM artifacts

The owner also confirmed UCloud availability of the thesis CAMISIM truth files and associated original artifacts. Their identity and alignment to contig/bin files need a small returned inventory before use.

The existing simulation design is characterized in the [thesis note](2026-09-16-thesis.md). It can help debug truth evaluation and reproduce a specific pathology. The owner explicitly stated that this project should create its own optimized simulations when needed; there is no requirement to use the old design.

## A004: Local tool source cache

On 2026-09-17, `agent_context/tools_repo/` contains 31 directories. The owner explained the previous copies were ZIP downloads and replaced the main binner snapshots with clones, adding AMBER evaluation, CAMISIM, McDevol, BBTools/QuickBin, BASALT-Air, ancient-DNA AMBER and DCVBin sources. ZIP copies remain entirely adequate for background reading.

The [audited snapshot manifest](2026-09-17-tool-snapshots.json) records 13 selected locations, including 12 tool-repository commits and an unversioned GenomeFace copy. The [targeted audit](2026-09-17-targeted-audit.md) defines actual review depth. Nonblocking qualifications: DCVBin's tracked model payload is absent; McDevol has staged-deletion/untracked index anomalies although the two reviewed blobs match HEAD; some clones have untracked Finder files. No cache files or nested Git state were repaired, removed, or committed here.

Before a baseline run, verify the tool's own repository root, exact commit/archive identity, executable environment, model weights and database versions. Git run inside GenomeFace resolves to the enclosing `dl_binner` repo, not a GenomeFace revision. A valid clone is not by itself a validated runnable baseline. Preserve compatibility patches with the run and use separate execution checkouts.

## A005: Local paper cache

On 2026-09-17 the cache contains 41 Markdown files and four PDFs. The owner added UncertainGen, replaced the QuickBin transcription with the journal version, and improved several other transcriptions. Their supplied fingerprint edits were preserved in commit `2b1e51b` before the current audit refresh. `Arangasamy_2025_paper_old.md` is historical, not independent evidence; a PDF's filename alone does not establish its revision.

The [initial landscape](2026-09-16-landscape.md) and [new audit](2026-09-17-targeted-audit.md) distinguish what was read and when. Original online sources were consulted where accessible; GenomeFace's original full text remained unavailable through this browser pass. Extraction graphics and missing equations must not be treated as verified mathematics. Fingerprinted file presence is not proof of reading or transcription fidelity.

## A006: Public benchmark acquisition

[E001](../../experiments/E001-coverage-thinning/README.md) now selects CAMI II HMP gastrointestinal development/diagnostic data under [D004](../decisions/D004-human-cpu-preflight.md), replacing the earlier Marine plan. Fresh acquisition is prepared. [The new audit](2026-09-18-human-cpu-audit.md) owns the human-data interpretation; [acquisition.json](../../experiments/E001-coverage-thinning/acquisition.json) owns URLs, actual GI sample IDs and publisher MD5s. Only metadata and tiny prefixes have been read, not complete payloads or verified experimental input hashes. The [September 17 data audit](2026-09-17-benchmark-data.md) remains historical context for Marine/CAMI III. No thesis artifact is required.

## A007: Current compute access

**2026-10-13 access change:** owner reports SDU account deactivated. All old UCloud
files still exist but are inaccessible; no deletion or restored access is claimed.
The capacities/balances below are historical, not current usable entitlements.
GCP is the selected main compute environment under [D014](../decisions/D014-google-cloud-workspace.md).
Owner reports paid billing, expected USD300 Welcome credit and expiry 2027-01-12;
live verification is pending. [Cloud guide](../CLOUD.md) and
[setup receipt](gcp-workspace.json) own actual state/costs. Initial modest CPU,
separate working disk and private same-region Standard backup are proposed,
not provisioned. No GPU or cloud scientific execution occurs in this phase.

### Historical UCloud availability

Owner clarification 2026-09-21: allocations may be smaller than recommendations.
COMEBin checks used 2 vCPU / 6 GB; native integration used 4 vCPU / 12 GB.
Use actual allocation, not thread count or host capacity, for charged core-hours.
Optional heavy-data destination `/work/RasmusAllesøeNielsen#2936/dl_binner/`
has owner-reported 10+ TB, shared with former colleagues; use only when necessary.
No files have been moved there. Environments remain under the E001 work root.

Owner-confirmed 2026-09-18 in [prompt3](../../agent_context/prompt3_second_step.md): UCloud AMD EPYC 9535, 1-128 vCPU, 3-384 GB DDR5-6000 RAM, approximately 2,100 allocated core-hours, **no GPU**, and initially 250 GB storage. These figures supersede prior H200/2-TB-node assumptions. The [execution brief](../../agent_context/prompt4_ucloud_execution.md) confirms Terminal / Ubuntu / Aug2026 on DeIC Interactive HPC (SDU/K8s), persistent root `/work/Home/dl_binner/e001/e001-gate0`, no UCloud commands run yet, and unknown access expiry. Tool environments stay under this root's `envs/`. The owner can obtain substantially more storage and does not regard it as a current design constraint; the exact expanded quota is not claimed allocated. Installed prerequisites, mount and actual CPU/RAM await returned evidence.

Budget charging is allocated vCPU count times wall-clock allocation time, not just observed process CPU time. Experiment-specific reserves/ceilings belong in [E001 configuration](../../experiments/E001-coverage-thinning/config.json). CPU support, available maximum RAM and a larger storage quota do not establish that an experiment is affordable. Initial preflight needs neither a GPU nor increased storage.

## Before an artifact becomes an experimental input

Create a small input manifest alongside the experiment containing source/accession, immutable version or checksum, sample/genome/contig IDs, preprocessing, storage/retrieval instructions, and split role. Check joins by identifiers and lengths rather than relying on row order. State what is unavailable or uncertain. A recorded UCloud path must not become a hard-coded assumption in reusable code.

A development dataset and E001 protocol are selected; final evaluation datasets are not. Current owner-reported resources are in A007. Consult current experiment receipts for completed native/data evidence; new-host
compatibility and actual-scale feasibility still need the relevant contracts before
scientific launch. Old UCloud locations are inaccessible and must not be guessed.
