# GI inventory provenance and repair review

Date: 2026-09-19. Scope: returned owner audit, local publisher metadata/header
inspection, and review of inventory-related changes through `7a6b114`.
No research conversion, training, read acquisition or biological scoring ran here.

## Direct observations

- The owner audit archive SHA-256 is
  `9daaf15298207576ad0ca74b1cea8a0120bb5a697d1fb60e12b45e3e5432bfea`.
  It reports 210,632 nonempty FASTA coordinate keys, 210,612 truth keys,
  20 FASTA-only keys and two empty `_from__to_-42_total_0` records.
- Locally downloaded both [fixed truth](https://frl.publisso.de/data/frl%3A6425518/per_bodysite/gastro_bam/gsa_pooled_mapping_fixed.tsv)
  and [original truth](https://frl.publisso.de/data/frl%3A6425518/per_bodysite/gastro_bam/gsa_pooled_mapping.tsv),
  approximately 12.6 MB and 25.2 MB. Their MD5s match the acquisition manifest.
  Their coordinate-key sets are identical. None of the 19 accessions comprising
  the 20 unmatched intervals occurs in either table. The original table is not
  a source from which to restore those rows.
- Read only bytes 0-1048575 of [gastrooral setup](https://frl.publisso.de/data/frl%3A6425518/gastrooral/setup.tar.gz).
  Its early members include `metadata.tsv`, `genome_to_id.tsv`, and `config.ini`.
  All 259 genome/taxonomy identities in the fixed table agree with this metadata.
  Prefix inspection does not independently verify the complete setup checksum;
  the resume driver checks the owner's full archive MD5 and these member hashes.
- The [GI directory](https://frl.publisso.de/data/frl%3A6425518/per_bodysite/gastro_bam/)
  lists 116 BAM files. Read exactly the first 4,096 bytes of each, requiring HTTP
  206 and the requested range. Decoded complete BAM text headers only, not
  alignments. Seven disagree with `genome_to_id.tsv`; the remaining 109 match
  source basenames and contain every accession in their corresponding truth rows.
  Headers for the other 150 truth genomes were not available in this listing.

All seven discrepant headers have an ART `-i` source under
`24112017_airskinurogenital/source_genomes/`, with different genome filenames
and simulator output OTU IDs from the GI BAM filenames. None of these seven
source basenames occurs in gastrooral `genome_to_id.tsv`. Their 19 `@SQ`
accessions account for all 20 unmatched intervals (CP014870.1 has two intervals).

| GI BAM filename stem | Header source assembly | Unmatched accession(s) |
| --- | --- | --- |
| OTU_97.1047.0 | GCA_001278015.1 | CP009236.1 |
| OTU_97.1070.0 | GCA_000143225.1 | CP002039.1 |
| OTU_97.2555.0 | GCA_000182835.1 | CP002341.1, CP002342.1 |
| OTU_97.2555.1 | GCA_001661075.1 | CP014870.1 |
| OTU_97.10356.0 | GCA_001721785.1 | CP012580.1 |
| OTU_97.10592.0 | GCA_000359625.1 | AP012167.1 through AP012176.1 |
| OTU_97.45053.0 | GCA_000194115.1 | CP002609.1, CP002610.1, CP002611.1 |

The intervals total **28,917,470 bp**; every interval exceeds 2,500 bp.
Structured [evidence](2026-09-19-gi-publisher-headers.json) preserves every
inspected header, URL, range hash, and the three setup metadata texts/hashes.
The [collector](../../scripts/e001_publisher_audit.py) uses bounded requests;
the policy records every exact excluded interval and expected source hashes.

## Interpretation and limits

Owner subsequently supplied the local inventory inbox. Repeated the complete
read-only audit against that full FASTA and fixed mapping: both SHA-256s match,
all 20 unmatched intervals equal the policy's exact set, and the tightened
mapping validator reports no error. The supplied folder omits `setup.tar.gz`;
its full hash/member verification remains in the owner resume driver. No real
conversion was executed during this confirmation.

This is strong evidence of foreign-simulation material under mismatched GI
filenames, rather than merely missing annotations. It does not establish how
the publisher produced the inconsistency, nor prove the content of every
retained contig against original source genomes. Assigning these sequences to
the GI filename's OTU would create false truth. Discarding arbitrary unmatched
sequences would also be unjustified. [D005](../decisions/D005-gi-input-derivative.md)
authorizes a narrow derivative with these exact intervals quarantined and all
corrected-truth coordinates retained before the existing length cutoff.

## Code-review findings and corrections

1. Inventory driver pinned execution to the first `9c2b0ec` snapshot, even in new
   bundles. Conversion retries had fixed output names and failure-text-specific
   recovery. Their packaging traps could print success after tar/checksum failure.
   Retire these entry points; use one persistent-environment resume driver with
   unique attempts, visible errors and nonzero packaging-failure status.
2. The chat's asterisk rendering was treated as a literal FASTA ID, and then
   described as Biopython normalization without evidence. Raw returned JSON
   establishes underscores. Remove the asterisk exception; all conversion
   exceptions now require an explicit policy bound to both input SHA-256s.
3. Audit could report success for duplicate truth rows, conflicting anonymous
   IDs or nonpositive coordinates that conversion would reject. It skipped DNA
   validation on malformed headers and ignored all duplicates of the orphan ID,
   including nonempty instances. Reuse conversion's mapping validator, validate
   DNA independently, and exempt only actual empty records from duplicate counts.
4. The previous chat called Gate 0 complete. Only mapping/AMBER native smoke and
   portable checks passed. Other native baselines and CPU feasibility remain open.
5. GNU time was installed in the disposable container. The new inventory resume
   uses Python monotonic time and child resource counters, requires no system
   installation, and probes the persistent environment on every invocation.

The review covers inventory/conversion/audit changes and their tests. It is not
a complete review of every baseline adapter or a proof of native Linux behavior.
