# E001 Gate 0 Validation

Date: 2026-09-18. These are software checks, not E001 scientific attempts or biological results.

## Executed locally

- macOS Intel, Python 3.13.2; isolated `.venv` with NumPy 2.2.6, Biopython 1.85 and pysam 0.23.3. This is the harness environment, not any native binner environment.
- `.venv/bin/python -m unittest discover -s tests -v`: 56 portable tests passed, including CLI smoke. Fixtures cover perfect/merged/split/missing/empty assignments, ambiguity, exact thresholds, fixed-denominator length strata, malformed joins/coordinates, duplicate predictions, anonymous IDs, reverse-complement duplicate detection, missing taxonomy, zero/filtered feature rows, unsafe archives, mocked download checksums/limits, dry-run acquisition, all-view scaling, stale coverage tensors, and failed-attempt provenance.
- `bash -n scripts/e001_linux_setup.sh scripts/e001_linux_smoke.sh`: passed. Syntax validation does not establish environment solvability or runtime success.
- Public directory/README/checksum metadata and bounded file prefixes were inspected as documented in the [audit](../../docs/evidence/2026-09-18-human-cpu-audit.md). No complete GSA, truth, read archive or scientific feature set was downloaded.

- `verify-source` passed for the four selected native repositories: independent roots, expected commits, no tracked changes, and only allowed Finder metadata untracked. None of the reference caches was modified.
- `python3 scripts/check_docs.py --check-context` passed, including all 83 present source fingerprints. Ten optional missing ZIP-cache paths belong to the explicitly historical September 16 notes, not current baseline provenance.
- Python AST parsing and `git diff --check` passed for the implementation. The separately committed owner brief retains its original trailing space; source briefs were preserved verbatim, not reformatted.

## Prepared but not executed

### Transfer preparation, 2026-09-18

The owner confirms no UCloud execution yet. The updated portable suite passes **59 tests**, including committed-file allowlisting, source-commit/checksum preservation, refusal to overwrite transfers, dirty-checkout rejection and symlink rejection. Shell syntax and documentation/context checks pass. Source validation now reports a contract error even outside a Git checkout, as expected for transferred code. Setup logging and persistent package-cache paths are prepared but not Linux-validated. The bundle contains no environments, source-paper/thesis caches or research data. Actual upload checksum, installed prerequisites and all native outcomes remain pending.

The actual transfer archive was built from committed source `9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea` and inspected locally. All **59 tests also passed from its extracted copy outside Git**, using the existing macOS portable environment; this does not validate Linux dependency resolution. `shasum -a 256 -c` passed. Local ignored locator: `artifacts/e001-transfer/e001-code-9c2b0ec6feb3.tar.gz`, with adjacent `.tar.gz.sha256`; approximately 47 KiB. SHA-256: `be85a52dd47eaab8aa9b68f3f9aaa38541d43ed9b68695c26169f95e111a3c85`. Intended owner-side upload locator: `/work/Home/dl_binner/e001/e001-gate0/transfer/`. Upload has not been confirmed. The package intentionally predates this results-only record; its embedded `SOURCE_COMMIT` identifies the executable snapshot. The builder can regenerate equivalent code from that commit, but gzip timestamps mean a rebuilt archive must receive its own checksum.

| Native check | Current status and what it must establish |
| --- | --- |
| strobealign 0.17.0 / samtools 1.24 | Unexecuted. Actual SAM/BAM compatibility, primary flags, NM tags, sorting, mate-preserving thinning and executable identities. Portable tests exercise validators only; pysam's bundled HTSlib is not substituted for samtools 1.24. |
| Pinned AMBER | Unexecuted. File-parser/metric parity on unique-origin fixtures, missing genomes, strict boundaries and separately characterized multi-origin behavior. |
| Pinned VAMB | Unexecuted. Actual BAM/TNF extraction, native scale invariance including total abundance, zero-row/zero-column behavior and CPU forward pass under its specified dependencies. |
| Pinned COMEBin | Unexecuted. Fixed augmentation identity, full native six-view coverage recomputation, measured variance, pseudocount-aware scaling and CPU forward pass. |
| Pinned MetaBAT2 | Unexecuted. Source-built executable, native mean/variance extraction and assignment format, including genuine empty output versus command failure. |
| Linux environment recipes | Unresolved. Produce and inspect explicit conda package URLs, pip versions, binary hashes and source identities before claiming a frozen runtime. |

Full native training/clustering, marker payload verification, CPU throughput projection, real-read prefix mapping comparison, full data/truth/taxonomy joins and research launch remain later gates. The smoke job is deliberately not a surrogate benchmark. A failure is retained and investigated; no older PyTorch/tool substitution is allowed under the original pin.
