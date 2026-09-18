# Public Benchmarks and the First Data Contract

Follow-up, 2026-09-18: E001's Marine choice is superseded by [D004](../decisions/D004-human-cpu-preflight.md) and the [human-data/CPU audit](2026-09-18-human-cpu-audit.md). This dated note remains evidence about the earlier options, not current acquisition instructions.

Checked: 2026-09-17
Scope: official CAMI pages, archive listings and Zenodo metadata; no dataset payload downloaded or checksum verified. Related: [Q003](../research/questions.md#q003), [E001](../../experiments/E001-coverage-thinning/README.md).

## Public and custom simulations have complementary roles

Use released community benchmarks to make results comparable, and controlled interventions/custom simulations to distinguish causes. Neither substitutes for the other. A dataset used to choose a mechanism is development data even if it is a famous benchmark; it cannot later become our untouched final test set.

E001 uses **CAMI II Marine**, rather than requiring the owner's thesis data or building a new community immediately. Its fixed-assembly thinning experiment is a modified coverage condition, not an official CAMI submission or a full reproduction of the challenge. Later method validation must include unmodified public benchmark workflows, different communities and assemblies. No final test suite is frozen yet.

The owner confirmed on 2026-09-17: **no existing CAMI II Marine copy is available for reuse; plan fresh downloads**. Start with metadata/setup/truth, not all archives. Bulk acquisition and processing belong on owner-operated UCloud.

## CAMI II Marine: selected development dataset

The [official dataset page](https://cami-challenge.org/datasets/marine/) specifies ten short-read samples, 50 Gbp total, paired 150 bp reads, and a pooled gold-standard assembly made from reference regions covered by simulated reads. It also links an actual MEGAHIT assembly. These are distinct inputs with distinct truth requirements.

| Needed artifact | Verified locator / archive member information | Acquisition status |
| --- | --- | --- |
| Dataset identity | [10.4126/FRL01-006425521](https://doi.org/10.4126/FRL01-006425521), Marine, short-read branch | Metadata checked; role: development/diagnosis |
| Setup and pooled GSA | [Short-read archive listing](https://frl.publisso.de/data/frl:6425521/marine/short_read/), `marmgCAMI2_setup.tar.gz`, listed 914M; official page names `anonymous_gsa_pooled.fasta.gz` inside | Resolve complete member list, metadata and local hashes before use |
| Reads | Same listing, `marmgCAMI2_sample_{0..9}_reads.tar.gz`, each listed about 5.2G | Not downloaded; archive sizes are compressed storage, not base counts |
| Genome truth / published binnings | [Zenodo 4964422 v1](https://zenodo.org/records/4964422), `genome_binning_cami2.tar.gz`; provider MD5 `c97aad9730a51a0d5d905c025e243b31` | Identify the **gold-standard**, not a participant prediction, and verify exact FASTA ID/length correspondence |
| Source genomes, if needed for ambiguity audit | [Marine listing](https://frl.publisso.de/data/frl:6425521/marine/), `marmgCAMI2_genomes.tar.gz`, listed 798M | Not required to launch metadata inspection; provenance must be checked before using sequences |
| Actual assemblies, later realism check | [Zenodo 5013479 v1](https://zenodo.org/records/5013479), `marine.zip`, 9.4 GB; provider MD5 `1c054a45f83f6475d50198274823886f` | Deferred. A GSA truth map must never be applied to MEGAHIT contigs |

The archive directory also contains per-sample `*_bam.tar.gz` files. Do **not** assume these are reads mapped competitively to the pooled assembly. Simulator BAMs may instead map to source genomes. Verify reference names, lengths, coordinates and provenance; E001 plans fresh mapping to its declared assembly reference.

At acquisition, record exact resolved URLs, archive members, download date, bytes, provider checksum where available, local SHA-256, license/terms, sample IDs and the unmodified source FASTA/truth checksums. Keep originals. The present table is an acquisition specification, not a completed input manifest. No UCloud path is known or hard-coded.

## CAMI III: available, but distinguish toy and challenge

The [July 14 announcement, updated August 3](https://cami-challenge.org/cami-iii-challenges/), and [current schedule](https://cami-challenge.org/schedule/) supersede the stale About page's "in preparation" wording. The longitudinal human-gut challenge has begun. Its published schedule places assembled-data availability on **2026-10-15**, after this audit. This is a schedule, not verification of a downloaded assembly or public ground truth.

The [CAMI III toy dataset](https://cami-challenge.org/datasets/toy-human-gut/) is already published with explicit download lists and assembly/truth links. It comprises 20 samples from ten individuals and short/long-read data. The page contains a correction to subject/sample pairing; a future subject-held-out split must use the provided `sample_subject_mapping.tsv`, not assume adjacent sample indices.

The toy download list includes `coverages.tar.gz`. Its name is not evidence that it contains measured contig-by-sample coverage suitable for a binner; it could contain genome-level truth coverage. Inspect its schema and mapping reference before reuse. Truth-derived abundance cannot be silently supplied as observed coverage.

CAMI III is a useful future independent challenge opportunity. Do not tune against its hidden evaluation or make a challenge submission without a separate decision. Waiting for it is unnecessary for E001. The CAMI II mouse-gut "toy" dataset is also not automatically a small download: its official page describes 64 short-read samples and 320 Gbp.

## Why not generate a new CAMISIM dataset now?

The first intervention only needs known contig origins and reads that can be thinned while assembly stays fixed. The released data already supply these. A fresh simulation becomes useful for a specific unresolved mechanism, such as mapping competition, controlled strain relatedness, or coverage-profile covariance absent from this test.

If that becomes necessary, pin the actual CAMISIM generation workflow and verify its truth semantics. The [current author repository](https://github.com/CAMI-challenge/CAMISIM) documents a Nextflow-based 2.0 workflow and the older `1.31-final` Python tag. A working old thesis configuration is not a validated configuration for 2.0. E001 uses neither simulator version to regenerate CAMI II.
