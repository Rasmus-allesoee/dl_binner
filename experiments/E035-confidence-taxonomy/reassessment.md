# E034 policy, data and evaluation reassessment

November 6, 2026. This note reuses checksum-bound retained observations and source
code. It introduces no community classification, fit, graph extraction or score.

## What E034 established, and what it did not

Both real readers passed. E009 sample 0 had 5,414 calibrated unique coordinate
observations and 138 edges with eligible endpoints. Oral sample 18 had 488
calibrated observations on 487 pairs and no three-template pair. These are useful
completed information measurements. NOT_ASSESSED refers specifically to the
conditional recovery comparison, which never ran; it must not mean that nothing
was learned or that the graph hypothesis was rejected.

The policy is the consequential unresolved choice. `genomegraph.links.aggregate`
requires three unique coordinates **within each sample**; `pool` only receives
surviving edges. A pair with two independent templates in each of two libraries
is irretrievably absent there, despite four pooled templates. A new actual tiny
BAM test exercises exactly this counterexample. E034 cannot answer that question
retrospectively: successful extraction deleted the below-threshold coordinate
spool. No multiplication of 488 by ten proves repeated pair support.

Prepare a source-bound pooled-before-support control: same original full ten BAMs
per assembly, MAPQ 20 / identity 0.97 / query fraction 0.90 / actual mate joins /
per-sample insert calibration / duplicate rules; deduplicate coordinates within
library, retain them, pool across independent libraries, then require three
templates, two distinct starts at each endpoint and 90% orientation agreement.
Keep per-sample counts and all refusal reasons. Apply the original pooled utility
floor (100 eligible edges / 1% eligible bp) only after all ten samples close.
This is a new prospective policy experiment, not an E034 repair or relaxed gate.

The new reader also retains joint descriptive MAPQ/identity strata, including
unknown counters, without adding filtered reads to a graph. E034's first-refusal
counters cannot identify the joint filter effects: Oral's 9.43 million MAPQ
refusals and 5.79 million identity refusals are ordered terminal reasons.
Lowering both now would confound pooling with alignment specificity. Keep them
fixed for this decision. Retained endpoint start/end envelopes support a later
localized conservative audit; they are not gap-free CIGAR support or proof of
exhaustive unique mapping. Raw names and read DNA do not enter features.

[METAMVGL's primary source](https://github.com/ZhangZhenmiao/METAMVGL) uses MAPQ 10,
identity 0.95 and three PE reads by default; its single input BAM and separate
assembly graph are not our ten-library policy. The retained UnitigBIN/GraphMB
audits likewise do not establish the value of this precise pooled graph. These
sources justify keeping physical evidence live, while requiring our own source-
bound test. No external tool is run here.

## Is the evaluation obscuring progress?

Yes, a bare headline is incomplete; no, the retained evidence does not establish
that the evaluator is broken. The unchanged `e009_truth.recovery` counts the best
qualifying bin per provided genome, at least 200 kb and 95% confirmed all-bin
support, using duplicate-safe reference-locus unions. It includes unrepresented
genomes and full replicons in the denominator. Unknown/quarantined DNA is not
silently dropped from bin purity. This is conservative sequence recovery, not
measured contamination, CheckM quality or formal MIMAG HQ.

Arithmetic on the already accepted E033 target table, bound in
[evaluation-foundation.json](evaluation-foundation.json), gives:

| Population | Full target bp | Confirmed represented bp | Representation upper bound | Targets with any support | Targets at least 90% represented |
|---|---:|---:|---:|---:|---:|
| E009, either mode | 554,661,890 | 102,790,342 | 18.5321% | 118 / 156 | 17 |
| Oral provided-origin | 2,083,072,211 | 1,669,979,389 | 80.1691% | 797 / 799 | 478 |

These ceilings ignore bin-size/purity constraints and do not prove attainability.
E032's 10.2847% / 10.1760% E009 recovery is roughly 55% of that represented-bp
ceiling; its 34.3786% Oral recovery is roughly 43%. Those ratios are descriptive,
not a replacement decision rule or new score. Full-reference 10% is not 10% of
the recoverable assembly. Missing references still matter for a truthful whole-
community claim. Never lower denominators to manufacture improvement.

The communities also pose different questions. E009 is a real sample-0 assembly
with ten measured coverage columns and conservative alignment/ambiguity truth.
Oral is a pooled, error-free provided GSA and an origin oracle, with long intact
contigs; E032's 162 / 219 Oral T90 targets use singleton best bins. Its result
does not validate fragmentation handling on real assemblies. The two primary
percentages cannot be pooled or compared as if their truth were identical.
E009's 3.3034% N quarantine and Oral known-shared sensitivity remain explicit.

The retained E024 acquisition manifest really names Oral public read samples
6, 7, 8, 13, 14, 15, 16, 17, 18, 19. This is the publisher's admitted sample set,
not an assumed numerical 0–9 axis or a second assembly. Its generation-bound BAM
manifest matches the sample-18 pilot. The mapper/identity arithmetic and actual
QNAME joins were inspected; no demonstrated input-swap or counter bug explains
the zero graph. Strain competition, short inserts, GSA endpoints, reference
representation and filters remain plausible contributions, not established causes.

The new reader records qualifying read-length distributions and same-contig
reference-span mate overlap. Short inserts/overlapping mates can limit the chance
of linking separate GSA records even with ample calibration; those counters are
descriptive until all twenty readers run. Neither high MAPQ nor a dominant
whole-contig origin verifies the source of the actual mate loci.

Add hand-computed evaluator contracts here for full absent-source denominators,
separate replicons, duplicate unions, unresolved bin DNA, short bins and missing
axes. Keep primary scores and all old summaries unchanged. Future reports must
include represented ceilings, assembly-conditional recovery and multi-contig
versus singleton results before attributing a change to representation. Historical
depth-filter priors remain encoded in frozen E031; the rejected E033 bundle does
not isolate shared mean-depth resummary or reject that information family.

Both communities have been used repeatedly for design and remain development.
Skin stays unscored with exact/near source overlap, molecule/replicon/taxonomy,
ambiguity, unique-versus-origin truth, feature/depth and cost/retention admission
outstanding. A separate real-assembly/depth confirmation protocol is needed for
broad robustness claims; repeatedly scoring the same two communities cannot supply
that confirmation. No new data are acquired to resolve it in this task.

## Direction

**Do the inexpensive pooled-support information audit before expensive taxonomy
database acquisition.** It resolves a specific untested policy and avoids treating
an early single-sample gate as the end of graph work. Prepare its separate cost
and source-bound consumer now. A useful pooled graph would justify carrying the
already implemented graph candidate into a separately admitted common comparison;
a sparse/ambiguous pooled graph would make the taxonomy route more attractive.
Neither outcome licenses truth-selected edges, a threshold grid or dataset routing.

**Implement taxonomy locally in parallel**, as requested. Independent biological
annotation is still the strongest complementary representation hypothesis, given
weak fragmented-genome exchange and sparse short-insert evidence. Preserve E031
learning, real crop information, explicit composition/depth and full optional GLM
ancestry; train a small confidence-gated adapter with hierarchical reconstruction
and intrinsic preservation, fixing E032 construction. Its safe fallback concerns
parents without usable classifier evidence; benchmark-unknown/non-target DNA may
receive annotations and change vectors. Changed neighbors/partitions can affect
either population, which must be evaluated. No guaranteed MAG gain follows from
the paper or these engineering tests.

The [TaxVAMB paper](https://www.nature.com/articles/s41587-026-03098-0) and pinned
source support hierarchical biological context in small-sample/incomplete-genome
settings. We do not copy its whole VAE or automatically propagate Taxometer labels.
Larger Transformers/GLMs, renewed contrastive negatives, selector tuning and an
external-tool campaign do not resolve the explicit pooled-support uncertainty or
add this independent annotation. Full Oral GLM remains complementary, with its
unchanged native 128-view qualification, bank and teacher/proposal admission due.
