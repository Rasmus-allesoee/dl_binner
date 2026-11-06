# E034: admitted pilot evidence and the next information decision

Reviewed November 6, 2026, after complete shutdown/delivery verification.
[E034 review](../../experiments/E034-genome-graph/completed-review.md) owns the
native outcome. [Exact source identities](../../experiments/E034-genome-graph/next-source-audit.json)
bind eight newly targeted files at the already reviewed VAMB, SemiBin and COMEBin
commits, plus three unchanged own implementation files. This is source inspection
and a research recommendation, not another reproduced tool result.

## What actually changed

The physical-information hypothesis was tested before fitting. E009 sample 0
passes its frozen pilot utility; Oral sample 18 does not. The latter has a valid
mate join and calibrated insert distribution, but no contig pair with three
qualified independent coordinate observations. Do not call this a graph-model
regression or failure of paired reads in general. Neither all-ten raw-support
pooling nor an assembler GFA was assessed. The full comparison is NOT_ASSESSED.

E009 also warns against treating high-MAPQ mate connections as guaranteed genomic
identity. Most resolved dominant-label discordances concern related provided
Faecalibacterium sources. Without retained template loci, these are not measured
template errors. Hard component unions or truth-selected edge deletion would be
unjustified. Preserve the physical reader/model for a suitable information regime;
do not spend the next task forcing this development GSA to satisfy the old gate.

The recovery problem remains substantive. Retained E032 reaches 34.3786% Oral
R95, but 162 of 219 T90 targets use single-contig best bins: only 57 use multiple
contigs. Its E009 R95 is 10.2847% / 10.1760%, below stronger E031 E023-construction
contexts (10.6110% / 10.5684%). E023's original 10.4163% GLM anchor remains.
These are reused summaries, not new scores or a per-dataset version router.
Retained MetaBAT2 is 8.5493% / 17.3260% with different native eligibility, so the
measured statement is not that we still trail that reference. We have no current
matched evidence establishing where we rank against every stronger binner.

E033 already showed noncollapse and accurate retrieval alongside poor Oral
biological neighborhoods and a regressing integrated bundle. Its 128-query raw
comparison and its 14.78% discordant resolved positive proposals are scoped
diagnostic warnings, not whole-population causal proofs about E031 or all learning.
Together, these motivate better biological information and its use across fragments.

## Targeted primary-source observations

**TaxVAMB.** The [2026 publisher record](https://www.nature.com/articles/s41587-026-03098-0)
describes joint intrinsic/taxonomic representation learning, reports particular
benefit with limited sample counts and incomplete genomes, and discusses annotation
quality/reference bias. These are author reports, not gains measured here. Relevant
indexed Results/Methods passages were readable; direct page opening redirected to
authentication, so this is not a claim of a complete supplementary-methods audit.
The inspected paper uses GTDB release 220 for MMseqs2. Its cutoff and quality
endpoints differ from our full-reference, all-DNA diagnostics.

Direct source at VAMB commit `b146fb610921aef1da8aed5d739f1ce80d21b33a` supplies
the stronger algorithmic evidence. `taxvamb_encode.py:make_graph` constructs a
hierarchy from annotation paths. Its intrinsic, taxonomy and joint models use
separate modality paths and hierarchical label reconstruction, with cross-modality
latent regularization; this is more than appending a species name to TNF.
`taxonomy.py` distinguishes absent/truncated paths and predicted rank scores.
`doc/inputs_outputs.md` recommends MMseqs2/GTDB, requires a verified classifier
format, and distinguishes supplied taxonomy from optional Taxometer predictions.
The source can propagate uncertain predictions; we should not automatically regard
those inferred labels as independent new measurements or probabilities calibrated
for genome identity. No TaxVAMB/Taxometer executable or reference database ran.

**Intrinsic-learning alternatives.** The same VAMB source separates sample-normalized
relative abundance from log total abundance, reconstructs those differently and
uses length-weighted training. [SemiBin2's primary paper](https://academic.oup.com/bioinformatics/article/39/Supplement_1/i21/7210480)
and `self_supervised_model.py` at `f7c45dcbcdfa81e8fbc3e08b04c54683122e72d6`
use long-contig split positives and resampled distinct-parent negatives, not
unconditional biological truth about every pair. [COMEBin's paper](https://www.nature.com/articles/s41467-023-44290-z)
and `simclr.py` at `1b476a41fac893294c70212a869573a732560ce5` contrast each real
view against other-parent views, with separate coverage processing. Their
discriminative losses are serious alternatives to our dominant positive-only loss;
source/paper success does not prove that negatives will help our frozen model.

Our actual `bootstrap/model.py` already uses capped log length weights,
parent-balanced real-view losses, a sequence head, reconstruction, signed pairs
and a bootstrap anchor. Claiming that it simply lacks weighting, real DNA views,
modality branches or every form of negative supervision would be wrong. E016's
positive-only bundle also improved its then comparators. Reintroducing broad
random negatives now would be a new matched hypothesis, not correction of a
known bug or an inevitable consequence of the source review.

Short-parent exposure remains worth monitoring: 292,793/508,763 eligible Oral
parents are 500–999 bp, contributing 203,177,403/1,443,827,664 eligible bp.
E009 has 51,922/89,041 such parents and 36,085,206/209,642,703 bp. Existing weights
moderate this mismatch; these counts do not establish the actual gradient budget
or justify silently removing short DNA. A larger Transformer alone supplies
neither a new source signal nor a demonstrated remedy.

## Recommendation and serious alternatives

Choose **one optional, confidence-aware hierarchical-taxonomy representation
upgrade** around the strong common bootstrap, with a reference-free fallback and
fixed provisional E032 construction. This is an explicit evidence-based change
from keeping taxonomy out of earlier scoped candidates, not a claim that every
product needs it. It offers independent sequence-to-reference information when
ten coverage samples and sparse physical links do not distinguish fragments well.
It is more promising now than another selector coefficient or larger attention
stack over the same evidence. The [next block](../../experiments/E034-genome-graph/next-block.md)
requires actual database/classifier admission before biological use.

Use labels from a frozen independent classifier/reference only, never simulator
origin IDs, benchmark taxonomy tables, coordinates or source headers. Learn from
partial paths and uncertainty; absence is not a taxon and taxonomic agreement is
not proof of a common genome. Shared genus/species must not force strains into one
bin. Keep intrinsic evidence and all unannotated/novel/non-target DNA. Reference
overlap is expected to matter and must be measured/reported separately from labels
leaking from the evaluator. Any gain is a **reference-assisted-mode** result;
it cannot establish unseen-genome generalization or an input-matched advantage
over a reference-free tool.

Compare this against: (1) a carefully masked contrastive/intrinsic learner, which
is cheaper but supplies no independent annotation; (2) full Oral GLM, which remains
important but has no native batched throughput/full-bank admission and has not
consistently improved E009 recovery; (3) pooled-before-support physical links,
which could rescue weak samples but would be a new information treatment with
unresolved specificity, not reuse of the current zero graph; and (4) a stronger
external reference, which would contextualize recovery but not itself fix it.
None is rejected as a method family. Taxonomy is a justified next hypothesis, not
a guaranteed winner, a novelty claim or a permanent product commitment.

Keep Q006 selection methods open without another tuning sequence. Advance Oral
GLM's exact 128-view native batching/full-bank/cost and full teacher/proposal/student
milestone; the tested state extension alone does not pass it. Skin remains acquired
and unscored, with source/replicon/molecule/taxonomy, exact/near/reference overlap,
ambiguity/unique-versus-origin truth, feature/depth, frozen protocol and separate
cost/retention dependencies. A new classifier/reference strengthens the need to
audit overlap before any independent-confirmation claim. No community annotation,
new fit, database payload, external binner or cloud job is added by this review.
