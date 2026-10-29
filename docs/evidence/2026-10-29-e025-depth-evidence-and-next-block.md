# E025: useful depth, unequal evidence and the next recovery block

Reviewed October 29, 2026. [Inspection](../../experiments/E025-joint-distance-retrieval/inspection-observed.json),
[frozen diagnostics](../../experiments/E025-joint-distance-retrieval/comparison-review.json)
and [all 799 targets](../../experiments/E025-joint-distance-retrieval/comparison-targets.tsv)
are direct observations. The source observations below support a next design;
they are not reproduced external-tool results or proof of an optimal algorithm.

## Result and trade-off

The original E024 all-ten measurements are useful under a valid combined-score
retrieval. E025 passes sampled technical recall **99.7917%** on its unchanged
32-query audit. Oral full-reference weighted R95 is **8.1441%**, compared with
retained E023 **4.0932%** and E019 **6.5077%**. The gains are 84,382,548 bp and
34,085,956 bp respectively. Target-50 rises to **58**, from 30 and 43.

This is not an unconditional improvement. Target-90 is **22**, above E023's 10
but below E019's 33. There are 77 gaining / 6 losing targets versus E023, and
70 gaining / 41 losing versus E019. The original joint KEEP rule fails its
target-90 requirement; **MODIFY** is unchanged. Preserve the failed criterion,
while retaining the measured information as a useful provisional direction.

Density-only returns one mixed 1.444 Gb bin and zero R95. Cached marker-informed
selection yields 188 bins and all passing recovery. It leaves 919,979,029 eligible
bp unassigned, 226,153,459 bp below eligibility and 523,848,635 bp assigned. Among
107 bins at least 200 kb, 27 have supported purity below 95%. The full export
accounts for every original nonempty contig/base and the original zero-bp records
remain separately documented. Neither a density score nor a marker proxy is a
calibrated genome boundary.

## What the retained edges identify

The exact same 508,763 eligible / 1,443,827,664 bp query population has base-weighted
same-origin 5NN fraction **34.7336%**, versus E023's **20.3297%**. The fixed E019
learned geometry remains **20.7688%**. Technical retrieval accuracy and biological
homogeneity are different quantities; most new links still connect different
provided origins.

An additive decomposition of the accepted new edges completed inside the original
local review clock. It does not run a search, select new bins, rescore old outputs
or change a threshold. [The full strata and endpoint counts](../../experiments/E025-joint-distance-retrieval/comparison-review.json)
retain every query, including all measured-zero profiles.

| Query depth / neighbour depth | Base-weighted same-origin edge fraction |
| --- | ---: |
| Positive / positive | **58.1417%** |
| Positive / all-zero | **0.3984%** |
| All-zero / positive | **4.5118%** |
| All-zero / all-zero | **7.0687%** |

All-zero endpoints occupy 30.96% of the base-weighted outgoing links from positive
queries, despite their very low homogeneity. Positive queries below 10 kb have
45.90–59.45% base-weighted same-origin neighbours; all-zero queries in those
length bands have 4.24–8.64%. Above 10 kb the positive-query mean is 62.44%, but
base weighting lowers it to 32.26%, so the long-contig problem is substantial
and cannot be dismissed as short-contig noise. All attributable queries here
are among the 799 bacterial targets; non-target gains do not explain this result.

These are conditional descriptive associations. They do not prove that zero
profiles caused every erroneous link, that suppressing those links will recover
the lost genomes, or that a different learner would fail. Length, abundance,
reference competition, filtering and strain similarity can contribute.

## Source audit: a declared assumption, not a demonstrated execution bug

The accepted axes, full measured cells, transforms/scales, source, integer length
packing, original vectors, sparse local/global ID mapping, native reload, forest,
marker choices and complete exports pass independent review. Compiled and exact
scores agree in the actual tiny contracts. No critical axis/cache/RNG/metric
implementation departure was demonstrated. This does not prove every algorithmic
choice is correct or optimal.

The frozen score explicitly uses depth **only when both endpoints have a positive
profile**, and changes its averaging denominator when it omits depth. A zero
profile therefore avoids an abundance disagreement that can separate two positive
profiles. This can make a poorly supported cross-availability edge competitive;
it does not mean the program fabricated a zero depth distance. Global median
rescaling sets numerical units, not probability or comparable biological
confidence. The symmetric score was never claimed to satisfy the triangle
inequality. Its native implementation matches this declared rule. A new
interpretation of positive-versus-zero evidence must be a new treatment.

The old transform field `depth_missing_rows=969351` counts method-unavailable
rows, including ineligible rows. It is **not** missing coverage: all ten cells
are measured, 576,144 whole-input profiles are all-zero, 317,196 eligible profiles
are positive, and 191,567 eligible profiles are all-zero. Preserve the old field
as executed evidence; use explicit names in the next implementation.

The inherited audit also constructs the same 508,763-ID set for each of 23,686
cached-call membership checks. Source inspection explains an avoidable cost in
its long CPU-bound tail, without a profiler claim. Native rule benchmarks record
614.27 seconds for grouping and 1,862.97 seconds for the old audit; these are
separate from new learning, which did not run. A separate hoisted-set adapter
passes actual tiny proof/refusal equivalence; the completed native audit used
the original source. The frozen review function ran successfully through its
explicit API. Its standalone CLI lacks the two external-data arguments; no
successful direct CLI invocation is claimed. Correct entrypoint/collector
packaging in the next local block without replaying accepted science.

## Targeted primary/source checks

The [MetaBAT2 methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC6662567/), checked
again October 29, describe rank/quantile alignment of evidence, effective-sample
weighting, progressive graph construction and separate small-contig recruitment.
Inspected author source `8eb96023ef627d1955c05e3aca348c84b8757914`,
`src/metabat2.cpp:790–870,1487–1506`, uses a sample when **either** contig exceeds
`minCV`, rather than requiring both. Its variance-dependent normal model and
`cvExt` variance assumption cannot be relabelled as measurements from our mean-only
matrix. Transfer the evidence-calibration question, not unverified likelihoods.

The [SemiBin primary methods](https://www.nature.com/articles/s41467-022-29843-y)
and inspected `SemiBin/cluster.py:64–166` at
`f7c45dcbcdfa81e8fbc3e08b04c54683122e72d6` intersect learned/raw candidate edges,
then weight and partition a graph. This supports checking independent agreement
before biological assignment; its exact-retrieval scale and variance path are
not a ready-made solution here. [Source byte bindings](../../experiments/E025-joint-distance-retrieval/next-block-source-review.json)
record the actual inspected files, versions and limitations. Prior MetaCAT/source
and marker-reliability reviews remain applicable; none authorizes a tool run.

## Strongest next coherent block

**Implement availability-aware calibrated evidence fusion and biological bin
construction locally, with learning fixed.** This is more than changing one
weight: distinguish co-absence from reliable positive-versus-zero contrasts,
put available composition/depth/native evidence on comparable label-free scales,
construct reliable cores, retain supported whole/child marker alternatives, and
recruit uncertain/short/zero-profile DNA conservatively with explicit abstention.
Use cached physical marker reliability; do not convert every repeated family into
a hard cannot-link. Keep sequence-only or weakly supported components possible,
so the zero population is accounted for rather than deleted or forcibly attached.

Freeze one prospective rule from primary sources and unlabelled statistics before
changed outcomes. Resolve exact scoring, core/recruitment and selection defaults
in implementation; this note does not approve a parameter sweep, a truth-trained
router or a new experiment from old outcomes. Reuse E025's saved candidate union
only if exact source-blind audits prove recall for the **new** score. Different
scores can require a newly admitted sparse search; do not assume old top-30 edges
are sufficient. Keep all original vectors, input DNA, samples and marker calls fixed.

Prepare a single cached E009/Oral comparison: fixed E022/E023 inputs on E009,
fixed E019/E024/E025 inputs on Oral, and their preserved accepted summaries.
That tests one grouping policy in two development regimes; it still does not
match their upstream learners. Predeclare joint recovery/target trade-offs,
calibration/availability diagnostics, optional unassigned DNA and a keep/modify/
abandon decision. No community outcomes, cloud wake or new scientific treatment
is executed by this inspection. The [next prompt](../../experiments/E025-joint-distance-retrieval/OPERATIONS.md#exact-following-prompt)
authorizes a future local implementation/preparation task only when invoked.

Serious alternatives and revisit conditions:

- **Depth-enabled learning is the strongest alternative.** It could learn how
  sequence and coverage complement one another, and current Oral learning is
  sequence-only. It would not itself repair incomparable downstream scores or
  automatic whole-forest selection. Prefer it next if calibrated fixed-learning
  construction still has poor coherent neighbourhoods or cannot improve recovery
  without trading away the other community. Admit original DNA views plus new
  parent-depth semantics explicitly; never rewrite an old training cache.
- **Efficient GLM/hybrid or a larger context network:** useful reviewed candidates,
  but full Oral extraction remains an estimated ~61 GPU hours under the prior
  exposure. The present failure has a directly observed grouping/evidence target.
  Revisit efficient prior exposure after this block if sequence ambiguity remains;
  do not dismiss it because a larger budget would be needed.
- **One SemiBin2 reference:** could bound attainable recovery and provide practical
  comparison, but a whole-tool win would not identify this mechanism. Defer until
  there is a concrete unresolved decision it can change. No broader tool campaign.
- **New data/confirmation:** both inspected communities are development data.
  Skin's 610 targets include 313 exact Oral overlaps and it lacks admitted matched
  contig depth. Source/genome/replicon/molecule/host/circular/taxonomy/near and
  pretraining overlap, competitive ambiguity/unique-versus-origin truth, evaluator,
  real depth, cost and retention admission remain. No acquisition or score now.

This priority is driven by recovery evidence, not the old $2 / three-hour limit.
The owner's longer-runtime authorization enabled the intact comparison; measured
allocation was only 59.32 minutes. New execution should receive a realistic full
schedule and separate credit/storage admission, without weakening science to fit
a laptop forecast. Existing storage still ends November 4 at 00:00 Copenhagen.
