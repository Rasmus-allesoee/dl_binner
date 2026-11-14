# Oral GSA and the next optional-link recovery test

Reviewed November 14, 2026. E035's completed all-ten information audit is reused;
no old BAM, mapping or threshold is replayed/changed. The owner's prior low chat
usage limit was task-specific and has reset. It is not a scientific rejection.

The [CAMISIM paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC6368784/) and
[official construction documentation](https://github.com/CAMI-challenge/CAMISIM/wiki/CAMISIM-1.3#step-4-creation-of-the-gold-standards-and-anonymization)
describe source-genome positions covered by at least one simulated read, split
at uncovered positions, with a pooled GSA using pooled coverage. The inspected
local source is CAMISIM `7ce6013c6d5a0fac8ba8a80e52a03560d3546fa6`:
`pipelines/shared/scripts/bamToGold.pl` reads source bases from mpileup and splits
on a sequence-name or position discontinuity; the sample-wise caller uses length
1 / coverage 1. Anonymization shuffles records; it does not perform de novo assembly.
This current source is corroboration, not proof of the historical Oral builder
commit/options. Original E014 source-substring/origin proofs remain authoritative
for the actual admitted DNA. Small source hashes and an optional streamed
reference-interval summary are retained in E036 preparation.

**Interpretation:** a GSA interval boundary is not a repeat/strain branch created
by an assembler. With 150 bp reads, median inserts 268–269 bp and q99.5 338–339 bp,
overlapping mates generally cover the physical fragment continuously. Such a
fragment normally falls inside one covered source interval. Pooling fills more
gaps, further reducing opportunities for true cross-record links. Genuine bridge
opportunities concentrate on the relatively few nonoverlapping insert gaps.
Different original source records also cannot be connected by one simulated
fragment sampled within a record. Alternative/repetitive placements and filters
remain relevant; this mechanism does not diagnose every refused template or prove
that all apparent links are wrong.

A real assembly may break at repeats, strain branches or coverage/assembler limits
while mates still connect its contigs. Thus Oral's five eligible edges do **not**
establish that such information is generally absent in user data. Oral remains
useful for sequence/depth/eligibility and an exact optional-link fallback test;
it cannot confirm transfer of a graph gain on a second link-rich real assembly.
E009 is an actual sample-0 assembly, with ten measured coverage samples and 1,671
eligible edges; it supplies the current direct recovery test. Both are repeatedly
inspected development communities, with different truth scopes and availability.

Choose [E036's optional graph comparison](../../experiments/E036-optional-pooled-links/design.md)
before independently referenced taxonomy. Reuse the already tested E034 adapter,
unchanged E035 pooled links and strong E031/E032 substrate; use the same label-free
availability rule everywhere, exact fallback when insufficient, soft updates and
no truth-selected edge veto. Keep source/locus discordance visible. The original
E034 gate remains failed; E036 is a new optional-modality question, not a repair of
that biological result. Taxonomy remains the next complementary hypothesis, not
abandoned or automatically authorized for concurrent execution.

The old taxonomy storage model sums approximately 654 GiB of possible concurrent
archive/converted FASTA/native index/joins/query/output/return/log data and rounds
to 750 GiB with reserve and safety margin. None of these full-reference peaks was
measured. Its source builder currently retains the 66.81 GiB compressed archive
and a converted FASTA capped at 250 GiB while building a compressed native target;
serial cleanup after independent reference/native verification could reduce that
coexistence. A future taxonomy admission should measure conversion/native sizes
and declare deletion/recreation contracts before choosing a smaller disk. Do not
assert that 750 GiB is necessary, or that 400 GiB is sufficient, from the rough
caps alone. This task acquires no taxonomy payload and proposes at most 64 GiB
scratch for the cached link comparison, conditional on actual safe-cleanup review.
