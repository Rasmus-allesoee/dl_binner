# GI Historical Taxonomy and Population

Reviewed 2026-09-20. Scope: historical taxonomy identity and E001 population
preparation, not a binning experiment or independent source-genome validation.

## Provenance

The live [CAMI HMP dataset page](https://cami-challenge.org/datasets/toy-human-microbiome-project/)
explicitly links `taxdump_cami2_toy.tar.gz` as the taxonomy used. Its statement
about RefSeq genomes dated 07.08.2017 is a genome-source date, not a taxonomy
release date. The owner's local description matches this linkage. The supplied
other-agent assessment was treated as a lead and independently checked.

The [CAMISIM paper](https://link.springer.com/article/10.1186/s40168-019-0633-6)
describes simulation and assembly/binning gold standards. It does not replace
verification of this specific archive. Publisher HEAD on the
[taxonomy object](https://openstack.cebitec.uni-bielefeld.de:8080/swift/v1/CAMI_DATABASES/taxdump_cami2_toy.tar.gz)
returned HTTP 200, size 93,167,485 bytes, ETag
`cb872dfedf4d97cd5b5c032bc5a2aa13`, Last-Modified 2018-02-26 13:13:14 GMT.
The local archive has exactly that size and MD5. This is an ETag/MD5 comparison,
not a signed checksum or a separate full redownload. Locally computed SHA-256:
`686cc8b07b5c8248cc2626fe32ee6ce87a136b3b48977729ac5426e303948bf4`.

All 13 members are regular files dated 2018-02-26: citations, delnodes, division,
fullnamelineage, gencode, host, merged, names, nodes, rankedlineage, taxidlineage,
typematerial and typeoftype (`.dmp`). Sizes and hashes of every member are pinned
in the [execution policy](../../experiments/E001-coverage-thinning/taxonomy-policy.json).
Only `nodes.dmp` is extracted (145,628,187 bytes; SHA-256
`69397ef3fdaa790319f17044208fe072f33ce27290eb1dcd12825fb9627e7827`).
The archive is read completely and its members hashed; no archive path is used
as an extraction destination. Unsafe, unexpected, duplicate or missing members
and mismatched input identities stop the step.

## Coverage and Interpretation

All **196 distinct truth tax IDs**, belonging to **259 source genomes**, occur
directly in the historical nodes table and trace to Bacteria (taxid 2). No merged
ID translation, deleted-ID inference, name lookup or current-taxonomy substitution
is needed. The taxonomy report retains every genome/taxid and taxid/domain mapping.
This confirms the supplied assessment's counts independently.

CAMI did supply taxonomy. Our earlier blocked conversion meant that the separate
archive had not yet been integrated, not that CAMI omitted taxonomy or that its
absence from the setup archive was a dataset defect.

## Population Check

Actual local preparation on the owner's full GI FASTA and corrected mapping,
with D005 unchanged and the verified nodes table, passes all five population
gates. It writes new ignored artifacts, never edits source data or prior attempts.

| Quantity | Observed | Existing requirement |
| --- | ---: | --- |
| Retained contigs | 22,594 | At least 2,500 bp each; at most 250,000 |
| Retained bases | 817,438,232 | At most 4 billion |
| Genomes represented after length cutoff | 238 | Not itself an eligibility criterion |
| Evaluation genomes | 224 | At least 20, each with at least 200,000 uniquely attributable retained bp |
| Probe candidate contigs | 21,930 | Eligible genome with at least 11 eligible contigs for k=10 |
| Deterministic probe queries | 10,000 | Existing cap 10,000 |
| Short queries (2,500 to below 10,000 bp) | 7,964 | At least 100 |
| Genomes represented by short queries | 66 | At least 10 |
| Retained bases excluded for domain/ambiguous origin | 0 | Report, do not silently remove |

The 21 source genomes absent after length filtering and 14 represented genomes
below the 200 kb evaluation threshold are not converted into failed binner
recoveries. The latter's contigs still enter mapping/binning and bin-purity
denominators. Recovery is measured against retained uniquely attributable sequence,
not whole reference-genome completeness. Taxonomy is evaluation metadata, not a
training feature. All thresholds, deterministic query selection and D005 exclusions
are unchanged. No scientific scores were computed and no training was launched.

Canonical FASTA and truth hashes are identical to the accepted owner conversion.
New population SHA-256:
`a4616aacf343eb65d7b0d7facd531fb2e4b47ed5a1271cc7335ebc1347d02ac2`.
All expected output hashes/counts are pinned in the policy; the owner driver must
reproduce them, rather than accepting any population that happens to pass gates.

## Next Boundary

Reuse the publisher-linked archive rather than current NCBI taxonomy: it resolves
all required IDs and avoids introducing taxonomy drift. No dataset change or new
scientific decision is needed. Replicate this preparation in the persistent UCloud
environment and inspect the returned output before freezing the population.
Remaining native binner/CPU and read-prefix feasibility gates still block science.
