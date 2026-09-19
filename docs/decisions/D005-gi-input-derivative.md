# D005: Quarantine foreign-simulation GI intervals

Date: 2026-09-19. Status: accepted for E001 development only.
Evidence: [publisher provenance investigation](../evidence/2026-09-19-gi-provenance.md).
Amends D004/E001's input population, not the coverage-thinning hypothesis.
No binner scores or scientific training were observed before this decision.

## Decision

Use an explicitly documented derivative of the public GI GSA. Quarantine the
20 exact FASTA intervals (28,917,470 bp) whose references are identified in
foreign-simulation BAM headers and absent from both GI truth tables. Also record
the two known zero-length artifacts. Bind these exceptions to the observed FASTA
and fixed-mapping SHA-256s in [the input policy](../../experiments/E001-coverage-thinning/gi-input-policy.json).
Every expected exception must occur with its specified length/count. Unknown
unmatched records, changed inputs, overlapping truth and exclusions, conflicting
aliases, and missing truth sequences remain errors.

Keep the original downloads intact. Record each excluded ID, length, sequence
hash and reason, retain every corrected-truth coordinate before applying the
unchanged 2,500-bp threshold, and anonymize the retained contigs. Preserve all six
equivalent truth-alias groups, counting each physical sequence once.

## Alternatives and reasoning

- Repair truth using the GI BAM filenames: rejected. The headers name different
  source assemblies and simulator OTUs. That would invent incorrect origins.
- Retain the foreign material as unscored input: possible as a later explicit
  contamination stress test; it confounds this GI coverage diagnostic and is not
  the chosen reference population.
- Reconstruct missing intended GI sequence from setup/read archives: potentially
  useful later, but requires a separate assembly/coverage provenance investigation.
- Change dataset: warranted if the retained population or subsequent read
  provenance checks fail. The complete join audit and bounded header evidence
  support this smaller correction first.

## Consequences and stopping criteria

The derivative changes mapping competition. Report E001 as development on this
declared assembly, never as an unmodified CAMI score or a complete reconstruction
of the intended GI genomes. No missing intended genome sequence is restored.
The seven GI filename identities do not justify assigning the foreign records
to those genomes. The retained 259 truth-genome identities agree with setup
taxonomy; historical taxonomy/domain resolution and population thresholds still
precede scientific approval. Future read acquisition must use gastrooral sample
archives with verified sample identity, not the suspect per-genome BAMs.

If new evidence contradicts provenance, hash/count checks fail, or the retained
population cannot answer E001, stop and revise this decision prospectively. A
successful conversion with unresolved taxonomy remains `blocked` for science.
