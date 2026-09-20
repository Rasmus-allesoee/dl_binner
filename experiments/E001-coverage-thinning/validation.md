# E001 Gate 0 Validation

Date: 2026-09-18. These are software checks, not E001 scientific attempts or biological results.

## Owner population frozen and VAMB step prepared, 2026-09-20

Return `agent_context/inventory-resume-6z45cola-return.tar.gz` verified SHA-256
`1bf9a1b442a31cd069b9d9dffcf587e9365a9627a9ad4b9107a74552fd4a8cb2`.
Executed source `64664ac6860b75d5a92c430c222e59f3418b5909`, code hashes and
taxonomy policy match the reviewed snapshot. All five prepared output hashes,
population counts/gates and all taxonomy member hashes match the local validation.
All 196 tax IDs / 259 genomes resolve as expected. All stage stderr files are
empty; exit 0. Run began 2026-09-20 10:48:22 UTC on `j-12396906-job-0`, took
40.06 seconds and reported child peak RSS 620,856 KiB. These are process statistics,
not full allocated job spend. Accepted UCloud input path and immutable output
identities are recorded in [frozen-inputs.json](frozen-inputs.json).

This closes the taxonomy/population prerequisite. No new biological score exists.
Native VAMB is selected next because its pinned CPU dependencies and simpler model
provide a bounded first learned-baseline check. COMEBin-first could expose the
largest compute risk sooner, but its more complex unresolved environment would
combine additional failure sources; it remains the next learned-runtime check,
not an optional baseline. MetaBAT2-first would not answer learned CPU feasibility.

The [new driver](../../scripts/e001_vamb_cpu.py) groups installation, import/pip
checks, existing native synthetic smoke and synthetic full-dimension CPU timing.
Local source inspection confirms the CLI schedule is 300 epochs with doubling at
25/75/150/225, not the different `trainmodel` Python API defaults. Use native
`make_dataloader`, `VAE.trainepoch` and DAdaptAdam without copying model/loss code.
No true sequences/coverage/labels enter timing and no model is saved.
PyPI metadata checked on 2026-09-20 confirms Linux x86_64 CPython 3.12 wheels for
vambcore 0.1.2, pycoverm 0.6.2, pyhmmer 0.10.15 and pyrodigal 3.6.3; this is not
an installed-runtime claim. Source/dependency pins remain unchanged.

All **95 portable tests passed**, including mocked complete VAMB-driver sequencing,
repeat invocation without reinstallation, setup/partial-environment/missing-fixture
failure returns, packaging failure and a real subprocess timeout. Projection
arithmetic/schedule are checked. Mocked orchestration does not establish native
Linux smoke or throughput: those are explicitly awaiting the owner run. Treat
smoke failure as a runtime blocker; interpret measured training projection with
the recorded per-fit and total budget limits before proceeding to science.

## Historical taxonomy and local population, 2026-09-20

The owner's local taxonomy archive was independently verified against the live
CAMI page and object metadata, then every member hashed. All 196 GI tax IDs resolve
directly to Bacteria for all 259 source genomes. The actual local full-data
`prepare-hmp --nodes` run passes all five population gates without any threshold
change: 224 evaluation genomes and 7,964 short queries spanning 66 genomes.
Canonical FASTA/truth hashes are unchanged from the accepted owner conversion.
See the [evidence and requirements](../../docs/evidence/2026-09-20-gi-taxonomy.md)
and [pinned policy](taxonomy-policy.json) for source/output identities.
Ignored local outputs: `artifacts/e001-taxonomy-reviewed/` and
`artifacts/e001-population-reviewed/`; no raw data or taxonomy is tracked.

All **88 portable tests passed**. New tests exercise complete taxonomy-aware
owner-driver invocation twice, invariant output checks, corrupted archive,
wrong member hash, missing/duplicate members, wrong mapping and domain coverage,
and missing-root/cyclic/duplicate taxonomy nodes. Failed attempts retain logs;
return archives contain coverage reports but not the 145 MB nodes table.
The full-data preparation used the existing macOS environment; owner Linux
taxonomy-aware execution remains pending. No read download or model training ran.

Transfer `artifacts/e001-transfer/e001-code-64664ac6860b.tar.gz` and its checksum
were built from committed code. The archive checksum passed and all 88 tests
also passed from its extracted copy outside the repository (18.14 seconds).

## Owner conversion accepted, 2026-09-20

Reviewed local inbox archive `agent_context/inventory-resume-ef6z97y9-return.tar.gz`;
SHA-256 `55705be2a9a01c7b4b43340bd61ed4e5fe4350275badc34b7439073282c73086`
matches the supplied checksum. The archive remains untracked. Its originating
attempt is `/work/Home/dl_binner/e001/e001-gate0/inventory-resume-ef6z97y9`.
Source commit: `9e1f939d4585bdf191dd562787932431235ff281`; returned code hashes
match local committed code, and the returned policy matches byte for byte.

- Execution started 2026-09-19 at 21:50:41 UTC on `j-12396660-job-0`.
  Environment, audit and conversion passed with empty stderr and exit code 0.
  Persistent mapping Python 3.12.10 / Biopython 1.85 passed isolation checks.
- Full setup archive/original mapping verification passed; all three setup
  metadata member hashes match the reviewed policy. Source FASTA and corrected
  mapping hashes match D005. The raw join audit still reports false, as expected:
  it describes the unmodified input before the explicit quarantine policy.
- Exactly 20 foreign-provenance intervals (28,917,470 bp), two empty artifacts
  and six coordinate-alias groups were accounted for. No additional invalid DNA,
  length mismatch, duplicate FASTA key or mapping-only key was reported.
- Conversion retained **22,594 contigs / 817,438,232 bp** at the 2,500 bp cutoff
  from 210,612 truth-joined physical contigs. Canonical FASTA SHA-256:
  `14870c27bc9467b5897bd1b65b347d7d5e2733d8bbe48c0085cb708194966fe1`;
  truth TSV: `f6e1b948f2fbbc6ed404ea27e73fb238bd2f34765b585e8e3fbe77f59b25c301`.
  These are returned output hashes, not independently rehashed local outputs.
- Elapsed 31.37 seconds; child peak RSS 614,272 KiB (about 600 MiB).
  These process measurements do not measure total allocated job cost.
- Population status `blocked` is expected: `nodes` is null, domains unresolved,
  and eligible genomes/short queries are zero pending taxonomy. The reported
  817,438,232 excluded retained bp are currently outside the scored population,
  not removed from the canonical FASTA. Population sufficiency is not yet known.

Conclusion: accept the D005 conversion and continue with the declared GI
development derivative; no dataset switch is warranted by this return. This
does not certify the entire publisher dataset or establish biological results.
Next verify the historical taxonomy and resolve the scored population. The
owner-supplied `setup-members.json` contains no taxonomy/nodes payload. No further
UCloud files are required to start that investigation; the owner can supply
specific files up to 10 GB if local inspection becomes useful.

## Prior implementation review, 2026-09-19

[Publisher provenance investigation](../../docs/evidence/2026-09-19-gi-provenance.md)
resolves all 20 FASTA-only intervals through seven conflicting BAM headers.
[D005](../../docs/decisions/D005-gi-input-derivative.md) records the derivative
decision. The new driver validates the source-bound policy, rechecks the persistent
environment on every job, and creates distinct attempts without moving old data.
Legacy inventory/retry drivers are retired to avoid executing the hardcoded first
snapshot or failing on output-name collisions.

All **82 portable tests passed** locally, including full synthetic owner-driver
execution twice with an empty system PATH, injected Python paths, alias
canonicalization, known empty artifacts, explicit
foreign-record quarantine, completed return/checksum verification, and prior-output
preservation. Corrupted setup metadata and a missing persistent environment stop
before conversion and return logs. A packaging failure returns nonzero and marks
the retained status as failed rather than claiming success.
Additional regressions cover policy source changes, missing/overlapping exceptions,
wrong orphan counts, duplicate truth rows and malformed-header DNA validation.
This does not establish a successful conversion of the real GI data or fresh-job
Linux execution. No scientific conversion was rerun locally.

The owner's newly supplied local inventory allowed a full read-only audit with
the corrected validator. FASTA/mapping hashes matched the policy, all 20 unmatched
keys matched its exact interval set, and the mapping contract passed (210,612
keys, six aliases). The setup archive is absent from the supplied local folder;
full setup/member checks will run on its existing UCloud copy.

Corrections to prior interpretations: raw audit JSON establishes only the underscore
orphan ID, not Biopython normalization of asterisks. The earlier return's absence
of an inventory file did not prove absence of a partial output directory. The
previous chat's claim that Gate 0 was complete was incorrect: other native baseline
checks remain open. Older paragraphs below are dated execution history.

## Executed locally

- macOS Intel, Python 3.13.2; isolated `.venv` with NumPy 2.2.6, Biopython 1.85 and pysam 0.23.3. This is the harness environment, not any native binner environment.
- `.venv/bin/python -m unittest discover -s tests -v`: 56 portable tests passed, including CLI smoke. Fixtures cover perfect/merged/split/missing/empty assignments, ambiguity, exact thresholds, fixed-denominator length strata, malformed joins/coordinates, duplicate predictions, anonymous IDs, reverse-complement duplicate detection, missing taxonomy, zero/filtered feature rows, unsafe archives, mocked download checksums/limits, dry-run acquisition, all-view scaling, stale coverage tensors, and failed-attempt provenance.
- `bash -n scripts/e001_linux_setup.sh scripts/e001_linux_smoke.sh`: passed. Syntax validation does not establish environment solvability or runtime success.
- Public directory/README/checksum metadata and bounded file prefixes were inspected as documented in the [audit](../../docs/evidence/2026-09-18-human-cpu-audit.md). No complete GSA, truth, read archive or scientific feature set was downloaded.

- `verify-source` passed for the four selected native repositories: independent roots, expected commits, no tracked changes, and only allowed Finder metadata untracked. None of the reference caches was modified.
- `python3 scripts/check_docs.py --check-context` passed, including all 83 present source fingerprints. Ten optional missing ZIP-cache paths belong to the explicitly historical September 16 notes, not current baseline provenance.
- Python AST parsing and `git diff --check` passed for the implementation. The separately committed owner brief retains its original trailing space; source briefs were preserved verbatim, not reformatted.

### Transfer preparation, 2026-09-18

At transfer preparation, no UCloud execution had occurred. The updated portable suite passes **59 tests**, including committed-file allowlisting, source-commit/checksum preservation, refusal to overwrite transfers, dirty-checkout rejection and symlink rejection. Shell syntax and documentation/context checks pass. Source validation now reports a contract error even outside a Git checkout, as expected for transferred code. Setup logging and persistent package-cache paths are prepared but not Linux-validated. The bundle contains no environments, source-paper/thesis caches or research data. The later owner-returned probe below updates transfer status; native outcomes remain pending.

The actual transfer archive was built from committed source `9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea` and inspected locally. All **59 tests also passed from its extracted copy outside Git**, using the existing macOS portable environment; this does not validate Linux dependency resolution. `shasum -a 256 -c` passed. Local ignored locator: `artifacts/e001-transfer/e001-code-9c2b0ec6feb3.tar.gz`, with adjacent `.tar.gz.sha256`; approximately 47 KiB. SHA-256: `be85a52dd47eaab8aa9b68f3f9aaa38541d43ed9b68695c26169f95e111a3c85`. Intended owner-side upload locator: `/work/Home/dl_binner/e001/e001-gate0/transfer/`. Upload has not been confirmed. The package intentionally predates this results-only record; its embedded `SOURCE_COMMIT` identifies the executable snapshot. The builder can regenerate equivalent code from that commit, but gzip timestamps mean a rebuilt archive must receive its own checksum.

## Owner-returned initial probe, 2026-09-18

Source: output supplied by the owner in chat, inspected here; not direct HPC access. Job identifier `j-12396047-job-0`, start 15:29 on 2026-09-18 (owner-reported local time; timezone not independently verified). Owner reports **4 vCPU / 12 GB RAM**. Actual submitted duration/end time has not been supplied. The original 8-vCPU/24-GB recommendation was conservative, not a scientific requirement; retain the smaller allocation for extraction and prerequisite bootstrap. Native smoke feasibility remains unmeasured.

- Working directory `/work/Home/dl_binner/e001/e001-gate0/transfer`; mounted filesystem `/work/Home`.
- Ubuntu 24.04.4 LTS, Linux x86_64. Bash, Git, Python 3, tar, sha256sum, timeout, curl and bzip2 are present at `/usr/bin/` paths. **micromamba and `/usr/bin/time` are missing**. Presence alone does not validate program versions.
- Owner's `sha256sum --check` reports `e001-code-9c2b0ec6feb3.tar.gz: OK`. This supersedes the pending upload status at package preparation. Code extraction and all installations remain unconfirmed.
- Startup banner reports AMD EPYC 9535, 256 visible CPUs, roughly 755 GiB host RAM and 13-day uptime. These are not the owner's 4-vCPU/12-GB allocation or elapsed job time. `df` reports shared filesystem capacity (7.2P total, 2.1P available), not personal quota. The ASPEED graphics listing does not establish an allocated ML accelerator; the job remains CPU-only.
- SSH/ttyd startup messages contain no reported failure and do not require SSH configuration for this browser-terminal workflow.

The next checkpoint at that time was extraction. The owner has subsequently returned a successful checksum, `Code extraction verified` at the expected path, and full source commit `9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea`. Extraction is now confirmed. No software installation, native smoke or research-data acquisition has been reported.

## Grouped driver preparation, 2026-09-18

The owner explicitly authorizes grouping steps that do not require intermediate interpretation and takes responsibility for requesting job extensions. This supersedes per-command chat pauses and repeated remaining-time questions. The supplemental [driver](../../scripts/e001_ucloud_preflight.sh) groups verified micromamba bootstrap, GNU time installation and unchanged mapping/AMBER setup/smoke, with fail-fast stages and return packaging. Its micromamba pin/checksum comes from the official release API as documented in [operations](OPERATIONS.md#current-grouped-execution). It does not acquire GI data or run scientific training.

Local validation: **60 portable tests passed**, including a mocked failed download that packages logs, never reaches system/tool installation and refuses a second attempt over the same outputs. Shell syntax passed. This tests orchestration failure handling, not actual Linux installs or native parity. The actual driver and all native stages remain owner-run and unexecuted at this handoff. The old execution snapshot remains unchanged; the separate driver's hash and exact executed copy are recorded by the driver itself.

## First native return reviewed, 2026-09-18

Owner-supplied [terminal output](../../agent_context/e001_ucloud_preflight_output.txt), [return archive](../../agent_context/preflight-return.tar.gz) and [checksum](../../agent_context/preflight-return.tar.gz.sha256) are preserved as a compact synthetic-check record (approximately 97 KiB archive; no research data). SHA-256 `45b5887fdbc80a43eb25a55a960000c5da57399d6cff33c0f47e323d793ad820` verified. All 108 archive members were inspected for path/type/duplicate safety without extraction. The returned driver matches our local driver hash, and returned setup/smoke hashes identify the transferred scripts.

All setup, pip-check, pipeline and smoke exit codes are zero. micromamba 2.9.0 and Ubuntu GNU time package `1.9-0.2build1` installed successfully; GNU time's display string `UNKNOWN` is not an installation failure. Native mapping reports strobealign 0.17.0 and samtools 1.24. AMBER reports the intended `f8b3a601043d13fc4227d5691c13561eb4490e50` source commit. Package-script security warnings are advisory; no reported solver/import/command failure occurred.

- Mapping: 1,870 records; correct-reference fraction 1.0 on the tiny unique-reference fixture. Both thinning checks preserve mates: 107/935 and 111/1,045 retained templates. Random 10% sampling need not retain exactly 10% in small fixtures. No inference about metagenomic mapping accuracy or throughput follows.
- AMBER: perfect, merged, split, missing, unassigned, strict threshold boundary and multi-origin assertions pass. The conservative E001 R95 agrees with AMBER-derived purity-filtered recovery on unique-origin cases. Unconstrained AMBER recall intentionally differs for merged bins (1.0 versus R95 0.0), and multi-origin behavior intentionally differs (1.0 versus 0.5). Neither difference is an evaluator bug.
- Driver timestamps: 14:25:02-14:26:02 UTC, 60 seconds total. Mapping smoke: 0.40 seconds, maximum RSS 53,528 KiB; AMBER: 1.58 seconds, 164,744 KiB. Setup: mapping 17 seconds, AMBER 37 seconds. The batch interval corresponds to approximately 0.067 allocated core-hours at 4 vCPU, not total job cost; idle/earlier allocation remains additional.

**Reproducibility caveat:** both pip inventories expose `easybuild`, `easybuild-easyblocks`, `easybuild-easyconfigs` and `easybuild-framework` 5.3.1, absent from our install recipes and conda inventories. External Python paths or user-site exposure are a hypothesis, not a confirmed cause. Core fixture assertions passed, but do not call these fully isolated/reconstructable environments yet. The micromamba `list --explicit` outputs also lack an `@EXPLICIT` header/checksums and include blank entries; pip freeze contains conda build-time `file://` paths. Preserve them as observed inventories, not directly replayable locks.

Next: [environment review](../../scripts/e001_environment_review.py), no downloads or reinstallations. It records package/import origins with inherited paths, removes PYTHONPATH/PYTHONHOME/PYTHONUSERBASE and disables user-site for child processes, asserts distribution/import containment, records structured conda package provenance, and reruns both native checks into a new directory. Existing installs and first outputs stay intact. Return the resulting archive for inspection before GI acquisition. Python's [environment documentation](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONNOUSERSITE) grounds the process-local isolation controls; these do not edit shell startup files.

Review-driver preparation: 63 portable tests passed, including external-distribution injection/detection, successful clean-process exclusion and failure-status recording. No native clean-environment rerun has yet occurred. Documentation links and whitespace checks pass for maintained edits; original owner terminal output is preserved verbatim.

## Native check status

### GI download succeeded; coordinate collision found

The alias-aware conversion retry [return](../../agent_context/conversion-alias-return.tar.gz) verifies against [checksum](../../agent_context/conversion-alias-return.tar.gz.sha256) (`39658135488174f911bcbac7a010270c4bb7904bcc63a86fa6172877fefa0c00`) but exits 1 after two seconds. No `input-preflight-v2` was created. Stderr reports `Invalid DNA: _from__to_-42_total_0` (the complete scan reports the literal Biopython ID `*from__to*-42_total_0`). The owner's complete local scan found exactly two such records, both length zero and SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; no other malformed records were found. They have no accession or valid coordinates and cannot match the corrected truth table.

Correction: `prepare_hmp` now records and excludes only the two exact empty orphan spellings observed in the scan/error evidence (`*from__to*-42_total_0` and `_from__to_-42_total_0`), writing `excluded-fasta.json` and `excluded_fasta_records` in `inventory.json`. A nonempty record with either ID still fails. All other malformed headers, invalid DNA, duplicate IDs and join failures remain strict errors. This is explicit handling of a source-file artifact, not arbitrary filtering or a biological result.

The correction is covered by portable tests for both exact empty-orphan spellings, nonempty orphan rejection, alias preservation, conflicting metadata and preservation of repeated failed conversions. With `TMPDIR=/var/tmp`, all **73 portable tests pass**; the first local test invocation failed before test execution because the default macOS temporary directory was unusable. Documentation and shell checks pass. The next bundle contains this correction and the guarded conversion-only retry script.

The first guarded retry was stopped because `input-preflight-v2/` already existed. This was a partial output directory left by the failed parser, not a completed inventory; the return packager intentionally omitted it. The next retry moved it with the prior stage/return under a numbered `failed-conversion-malformed-fasta*` directory, but still failed because the runtime identifier spelling was not in the exception set. Recovery now selects the next unused numbered preservation directory and the parser accepts only the two exact observed empty spellings before creating fresh output. Completed or ambiguous directories remain fatal.

The following retry, from source commit `c8ec39581bfa12d903f89111f274379494738c38`, passed those orphan/recovery checks and reached the next strict input contract. It stopped on `Missing/duplicate coordinate join: CP002609.1_from_3_to_1894400_total_1894398` after four seconds. That message conflates a missing mapping key with a duplicate FASTA coordinate, so it is not yet evidence for either interpretation. The new [read-only HMP join audit](../../scripts/e001_hmp_audit.sh) reports both categories across the complete files before another conversion attempt. The owner's return archive and terminal output are preserved as the latest failure evidence.

The owner-run audit from source commit `6901be8153c2e25f075716b6c72712025a6b096a` completed in ten seconds and returned `join_contract_passes: false`. It inspected 210,634 FASTA records, including the two known empty orphan records. There are 210,632 non-orphan coordinate keys in the FASTA and 210,612 unique keys in the corrected mapping: 20 FASTA keys are absent from the mapping, while no mapping keys are absent from the FASTA. FASTA duplicate-coordinate, duplicate-ID, malformed-header, invalid-DNA and length-mismatch counts are all zero. The mapping contains six duplicate coordinate groups, all with identical non-ID metadata and therefore consistent with the six documented anonymous-ID aliases. Source SHA-256 values are `67aeeeb70e5ba0e1506bf95c79bb25b06869c0486e6c0ea111763c3b060c0baf` (FASTA) and `4353f05be6a94c0c05be083088148eac01bcf34dc05c6a061709ff5fbd61d720` (corrected mapping). This is a data-contract checkpoint, not a scientific result. The 20 FASTA-only records must be compared with the original mapping and setup metadata before conversion is changed.

Owner's targeted FASTA scan subsequently confirmed exactly one sequence for each truth alias pair, with matching declared/actual lengths. Pairs and lengths: PC21351/PC21352 (2,466 bp), PC24985/PC24986 (1,259), PC52686/PC52687 (1,360), PC97787/PC97788 (136,176), PC100714/PC100715 (4,140,334), PC210631/PC210632 (202,292). The three longer sequences total 4,478,802 bp and must not be dropped or counted twice. The three shorter sequences remain below the unchanged 2,500-bp input cutoff.

Correction: coordinates still define the FASTA join. Distinct source IDs at one coordinate are aliases only if every other truth field agrees exactly, including genome, taxonomy and number_reads. Choose the numerically smallest PC ID (stable lexical tie-break), retain all source IDs in `contigs.jsonl` and `inventory.json`, and count the physical sequence once. Duplicate same-ID/same-genome rows, conflicting aliases and multiple FASTA occurrences still fail; same-ID multi-origin truth remains ambiguous, not merged into a unique origin. Source files are never modified. Regression tests cover row-order independence, numeric ID selection, count preservation, below-cutoff reporting, conflicting fields and preserved multi-origin behavior. Corrected real-data conversion remains pending; retry only conversion into new output using a new committed code bundle.

The new owner [terminal output](../../agent_context/e001_gi_inventory_terminal_output.txt) and checksum-verified return replace the earlier same-named local return; the earlier failure remains preserved in Git and UCloud's `failed-inventory-missing-time/`. Recovery installed GNU time, prerequisites passed, and all six manifest-listed files downloaded: GSA 972,133,785 bytes; corrected mapping 12,597,447; original mapping 25,194,106; setup archive 1,906,532,721; README 741; checksum manifest 709,793. The setup member list includes `metadata.tsv`, `genome_to_id.tsv`, per-sample taxonomic profiles and `config.ini`; no extraction is authorized yet.

Conversion failed with `Duplicate truth row` while reading mapping rows, before output-directory creation. Independent read-only inspection of the publisher's corrected mapping (MD5 verified as `954106872f9af342c0b7fd4422d8db9f`) finds 210,618 rows and six duplicated (contig_id,start_position,end_position,genome_id) groups; all six contain differing rows, including differing anonymous IDs. Example: PC21351 and PC21352 both describe HG917869.1:696659-699124 in OTU_97.20215.0. This violates our assumed one-coordinate/one-anonymous-ID join, rather than showing corrupt downloads. Do not drop truth rows blindly. A targeted scan of the already downloaded FASTA is required to count corresponding records and compare sequence hashes before choosing a correction. No biological result or scientific approval follows.

### GI inventory attempt failed before acquisition

Owner return verified: [archive](../../agent_context/gi-inventory-return.tar.gz), [checksum](../../agent_context/gi-inventory-return.tar.gz.sha256), SHA-256 `05287ad75941a1120034c78c9834b264fb4e158cf8d8136b7bf6946ffc8af80e`. Safe archive members and the executed driver match the prepared inventory wrapper. At 2026-09-18 19:37:08 UTC the prerequisites command failed with exit 127 because `/usr/bin/time` was absent. The timing wrapper could not launch Python; acquisition and conversion never ran. This is an infrastructure failure, not a dataset or scientific result. A container restart/replacement would explain loss of the system package, but that event is not confirmed by the return.

Root cause in our wrapper: it assumed the earlier container's system utility persisted, although only experiment files/environments under `/work` are intended to persist. The corrected inventory wrapper checks/install GNU time before timed commands and records package/version/hash and bootstrap logs. Its explicit `--retry-missing-time` mode checks the known failure signature and absence of inventory/conversion data, verifies the old return checksum, and moves the failed stage and return files intact into `failed-inventory-missing-time/`. It refuses existing recovery destinations or partial data; no automatic deletion/retry loop. Only then does the normal grouped inventory resume. The already executed source snapshot and installed tool environments are unchanged.

Local verification: 65 portable tests pass, including failed-attempt preservation and refusal to recover over existing inventory data. Shell syntax and documentation checks pass. Actual recovery and GI acquisition remain owner-run and unexecuted at this handoff.

### Environment review resolved, 2026-09-18

The owner-returned [review archive](../../agent_context/environment-review-return.tar.gz) verifies against its [checksum](../../agent_context/environment-review-return.tar.gz.sha256): `b00b14cc6665b6ff7a6c12fb8a0a284596ff75bebc5a4f923864fec64e7a6819`. All 71 members passed path/type/duplicate checks; the executed review script matches the locally prepared source. All ten recorded commands, pip checks, both native smoke reports and final status pass.

Confirmed cause: the four EasyBuild distributions came from `/home/ucloud/.local/lib/python3.12/site-packages` with `site.ENABLE_USER_SITE=true`; PYTHONPATH and PYTHONHOME were unset even in the observed processes. With clean-process controls, user-site is disabled, all discovered distributions are inside the intended environment prefix, and NumPy/Biopython/pysam (plus pandas for AMBER) resolve inside that prefix. Required module origins were already correct in the first run. No installation changes were needed.

The isolated mapping report preserves 1,870 records, correct-reference fraction 1.0, and exactly the same retained-template counts/pair-consistency results. AMBER's checks match the first return. The mapping BAM byte hash differs between output locations; no byte-identical-output claim is made. Command timings for the clean smoke reruns were approximately 0.52 and 1.67 seconds, not research-scale benchmarks.

Structured conda metadata now contains 52 mapping and 27 AMBER package records, all with URLs and at least one package checksum. This repairs provenance missing from the first text exports, but does not establish tested environment reconstruction or hashed pip wheel locks. Those remain runtime-freeze work before science, not blockers for bounded GI inventory.

**Disposition:** the isolation concern is resolved for these checked imports/distributions. Proceed to GI assembly/truth/setup acquisition and initial coordinate inventory, with process-local Python isolation retained. Other binner smoke, taxonomy resolution, CPU feasibility and scientific launch remain gated. The new inventory driver wraps the unchanged transferred snapshot and returns summaries only; no GI acquisition has run yet.

Local preparation checks: 64 portable tests passed, including refusal to overwrite an existing inventory before starting work; shell syntax and documentation checks passed. Maintained setup/smoke scripts now apply the observed isolation fix for future transfers. Existing UCloud code stays untouched, and the new inventory wrapper supplies the same controls around the old snapshot. The inventory download/conversion itself remains unexecuted here.

| Native check | Current status and what it must establish |
| --- | --- |
| strobealign 0.17.0 / samtools 1.24 | Synthetic native checks and isolation rerun passed. Real-read mapping remains untested. |
| Pinned AMBER | Native fixtures and isolation rerun passed, including intended unique/multi-origin and threshold semantics. No scientific dataset evaluated. |
| Pinned VAMB | Unexecuted. Actual BAM/TNF extraction, native scale invariance including total abundance, zero-row/zero-column behavior and CPU forward pass under its specified dependencies. |
| Pinned COMEBin | Unexecuted. Fixed augmentation identity, full native six-view coverage recomputation, measured variance, pseudocount-aware scaling and CPU forward pass. |
| Pinned MetaBAT2 | Unexecuted. Source-built executable, native mean/variance extraction and assignment format, including genuine empty output versus command failure. |
| Linux environment recipes | Mapping/AMBER installed and process isolation verified; structured provenance captured. Reconstructable locks and other tool recipes remain pending. |

Full native training/clustering, marker payload verification, CPU throughput projection, real-read prefix mapping comparison, full data/truth/taxonomy joins and research launch remain later gates. The smoke job is deliberately not a surrogate benchmark. A failure is retained and investigated; no older PyTorch/tool substitution is allowed under the original pin.
