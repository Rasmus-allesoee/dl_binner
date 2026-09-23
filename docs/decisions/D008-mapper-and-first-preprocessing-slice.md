# D008: Retain Strobealign and Start Sample-0 Preprocessing

Status: accepted, 2026-09-21. Completes D004's provisional mapper choice for E001,
not a claim of universally superior mapping.

## Evidence

All three owner mapper attempts are reconciled in [validation](../../experiments/E001-coverage-thinning/validation.md)
and [observations](../../experiments/E001-coverage-thinning/mapper-observed.json).
The final attempt passed; do not repeat it. The owner then supplied both existing
BAMs, which match their accepted hashes. Local [diagnostics](../../experiments/E001-coverage-thinning/mapper-diagnostics.json)
found 91,339 reads with disjoint destination-genome sets. Of these, 90,046 have
strobealign MAPQ 0 and 90,894 have Bowtie2 MAPQ 1. Bowtie2 has 114,509 mapped reads
with equal AS and XS scores. Its [manual](https://bowtie-bio.sourceforge.net/bowtie2/manual.shtml)
defines these as reported and alternative alignment scores; pair scoring can
also produce XS greater than AS. Equal scores support ambiguity, not proof that
every possible genomic origin was enumerated.

We retrieved only sample-0 read-origin metadata locally (293,229,761 bytes),
verified its object MD5, recorded SHA256, and scanned all 33,332,086 rows through
gzip CRC validation. Every mate present in either BAM joined uniquely: 199,036.
On the common 200,000-input-read denominator, the true genome is compatible with
the reported contig for 105,795 strobealign reads (52.8975%) and 105,697 Bowtie2
reads (52.8485%). The 98-read difference is not evidence of superiority. Both
can pick a different origin among similar sequences; wrong-source compatibility
does not itself prove that the read's true source is identifiable. The source
genome is absent from the retained reference for some mapped reads too.

## Choice and Alternatives

Keep **strobealign 0.17.0 full SAM**, primary mapped filtering `-F 2308`, and
**no added MAPQ cutoff**. This preserves the declared E001 contract, has accepted
CPU/storage behavior, and the truth check does not justify replacing it with
Bowtie2. Native downstream tool identity/coverage filters remain native and must
be recorded. Do not compare MAPQ 0 alone across mappers or treat 99% aligned as
99% correct. Keep the prefix results as a development diagnostic, not a held-out
benchmark or a new-method result.

Switching to Bowtie2 for its smaller MAPQ-zero count is unsupported. Running a
new mapper sweep or repeated prefix test adds little now. Filtering away the
ambiguous half of the reads changes the scientific input and is not a neutral
repair; it could become an explicitly separate later intervention. The immediate
question remains thinning at fixed mapped evidence, not changing alignments
between C0 and CT. Revisit mapping if full-data evidence identifies a systematic
correctness issue or if the research claim becomes mapper-dependent.

## Next Bounded Execution

Follow-through, 2026-09-21: the sample-0 slice below has now passed; see
[measured validation](../../experiments/E001-coverage-thinning/validation.md#full-sample-0-preprocessing-accepted-2026-09-21).
It took 42.24 minutes / 2.816 allocated core-hours and created 15.412 GB at
4 vCPU / 12 GB. Proceed to the remaining nine GI samples with unchanged mapping
and replicate-0 thinning, reusing sample 0. The
[bounded plan](../../experiments/E001-coverage-thinning/multisample-plan.json)
opts into acquisition through the owner command, uses the offered shared path
for projected 230.4 GB of new retained data, and leaves environments in Home.
No scientific fits or additional replicates are authorized by this expansion.
This follows the original measured-first boundary rather than repeating it.

Original bounded action (now completed): use Snakemake 9.13.7 to process
**the already downloaded sample 0 only**: validate
all 16,666,043 pairs, stream strobealign SAM through primary filtering and sorting
into C0, then native samtools 10% thinning with E001 replicate-0/sample-0 seed
1000 into CT. Index both, retain reads/BAMs, return counts, hashes, measured cost
and storage. This starts real input preprocessing, not another synthetic smoke
check and not a training run. No new samples, features, fits or biological scores.

Use the accepted mapping environment and a separate experiment-owned workflow
environment. A sequential DAG reserves CPUs for all three concurrent mapping
pipeline processes. Recommend 4 vCPU / 12 GB; minimum 3 vCPU for this driver.
New attempts preserve incomplete files and never overwrite previous attempts.
The engine's dry-run is routine and immediately followed by execution on success.

This slice measures actual full-sample preprocessing before allocating the
remaining nine samples or the paired scientific fits. Its outcomes should decide
data placement and acquisition scope, not alter the scientific population to fit
a quota. The original slice alone did not authorize migration or broad acquisition;
the measured follow-through above now defines the next bounded scope.
