# Prospective E022: reliable cross-contig learning

Frozen locally on October 25, 2026, before new community fits or recovery scores.
Immutable anchor: E021 E009-only f136b2c, executed operationally at 1f62140,
reviewed at 9d02bdc. First supported comparison is E009 with ten measured depth
columns and its exact retained real-view/context/GLM banks. No new extraction.

The encoder, initialization, predictors, stopped EMA target, full-parent/every-
available-view exposure, reconstruction/dropout, seed 11, 20 epochs, batch 256,
unit inference and sole CPM/E013 downstream stay fixed. Add a bounded static
cross-contig side loss, not a larger network. Same-parent positive learning alone
does not explicitly connect different genomic fragments. This hypothesis is not
a proven causal explanation for E021's mixed recovery.

## Static evidence and pairs

Read original features, native unit vectors and sparse 30-neighbor graph, and
cached marker genes/domains/proteins/pinned HMM through strict actual readers.
No marker search, neighbor rebuild, reference annotation, truth or taxonomy.
Keep the full contig axis. Only constraint proposals require >=2,000 bp and
usable composition; the inherited 500 bp learner cutoff and all DNA stay intact.

Training-quality marker support is deliberately stricter than E013's soft quality
proxy: full nonpartial gene, >=80% HMM coverage, >=10 domain-score bits above TC,
one physical locus of that family per contig, no credible multi-family protein,
and no unknown protein residues. Consolidate >=50%-overlapping calls only within
the same contig/family; never collapse loci across contigs. Reliability is coverage
times (1 - 2**(-positive margin)), a heuristic rather than a probability.

Fit raw-context distance calibration without labels: Hellinger TNF and log1p
measured parent depth divided by eligible-column standard deviation. Require at
least two nonconstant depth columns, actual evidence on both endpoints and
nondegenerate calibration. Use up to 65,536 deterministic unordered eligible
parent pairs; save their indices/distances. Near/far boundaries are the 10th/75th
percentiles in each context, fixed before outcomes. No invented window coverage
or variance. Without this independent measured context, abstain from cross-contig
constraints and retain ordinary learning; this is not sequence-only validation
of the active mechanism. Optional GLM inputs do not substitute for measured depth.

Positive candidates are reciprocal retained neighbors, near in both raw contexts,
with at least one strong marker-supported endpoint and no shared credible family.
Marker compatibility does not prove common origin; these remain weak positives,
guarded by two contexts rather than a graph pseudo-label alone. Marker-negative
partners may participate. Ambiguous/multicopy family evidence vetoes positivity.

Negative candidates share a strong family, but that alone is insufficient. Propose
at most eight hash-ordered family-neighbor offsets per occurrence (offsets 1, 2, 4,
8 in both directions), require far separation in both contexts, and abstain if
any supporting protein pair is identical or has >=0.90 protein-5mer Jaccard.
This conservatively removes possible duplicate/near-identical loci, without
claiming different proteins prove different genomes or genuine replicons.
Retain all proposal acceptance/abstention reasons and family evidence. No all-pairs
marker matrix or transitive positive closure. Deduplicate unordered pairs and cap
combined degree at four per contig in descending confidence/stable opaque-ID order.

## Learning and selective control

Keep the original encoder modules and initialization exactly. Distribute every
retained pair once per epoch across existing optimizer updates, max 256 pairs per
side batch, with a separate deterministic sampler. Do not alter original view RNG
or optimizer-step count. Preserve pair evidence, features, embeddings, partitions
and complete exports.

Positive side loss is symmetric online-to-stopped-target cosine distance; negative
side loss is squared hinge max(cosine - 0.2, 0)**2 on online endpoints. Combine
fused/sequence heads in the inherited 1:0.5 ratio. Weight each pair by retained
confidence and divide by pair count, not confidence sum. Disable depth evidence
for side forwards so the side loss cannot be solved directly by its depth-based
pair selector; original measured-parent depth/dropout and reconstruction remain.
This does not prove removal of all abundance/composition shortcuts.

Side weight is 0.1, zero for epochs 1–2 and linearly ramped over epochs 3–5.
No marker-selected genome count, bin, family blacklist or truth-derived threshold.
The one prepared optional ablation sets only side weight to zero, preserving
construction/initialization/pair schedule/RNG and decoder heads. Do not execute a
community ablation here. Actual tiny zero-weight fits must match the anchor.

## Decision, alternatives and bounds

First compare one frozen candidate with retained E021 E009-only results, not a
baseline refit/rescore. Keep the scoped candidate only if full-reference post R95
improves >=0.005 absolute and >=90% count does not fall, with all integrity gates.
Abandon if neither R95 nor >=90% count improves; otherwise modify. These practical
criteria are not significance or a universal marker-family decision. Report all
156 references, 3.3034% N quarantine, target gains/losses and every population.
No product-default promotion or claim of two-community KEEP.

Alternatives are direct SCG-negative batches (unsafe repeated-family assumption
on audited E011/E012 cases), a zero-GLM attribution control, broader grouping
tuning, or larger/fine-tuned sequence models. Prefer reliable new cross-contig
supervision now; no automatic taxonomy, ensemble or another GLM campaign.

Local engineering: four threads, 8 GB sampled tree RSS, 90 cumulative execution
minutes across logged attempts and 4 GiB extra local working data. Authoritative
source/input hash refusal and exact native reload remain. Actual tiny HMM/cache,
pair/loss/gradient/train/reload/group/refine/export paths must run; synthetic
annotations and mock GLM vectors must be labeled. Label-free full cached pair
availability may be audited without fitting/scoring communities.

No paid/cloud job, community fit/score, old rescore, DNA acquisition or retention
extension in this task. Prepare a new separately approved CPU comparison, complete
setup/collection/resources/cost and fresh credit gates; no old budget carries.
Frozen skin stays unscored, with origin/unique/overlap/evaluator limits and no
measured GSA contig depth. It cannot confirm this active depth-gated mechanism.
Storage still ends October 28, 00:00 Copenhagen; preserve the expensive E021 bank
and prepare a priced retention decision rather than renew/delete silently.
