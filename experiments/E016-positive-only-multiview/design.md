# E016 prospective positive-only learning bundle

2026-10-20, before changed community outcomes. This is one coherent learning
upgrade, not an implementation of McDevol or a claim that false negatives caused
E014/E015. Preserve all older science and failed journals. The owner now authorizes
local engineering and one conditional new $3 two-fit comparison; October 21 is
still the storage review boundary.

Keep the dev5 composition/depth/fusion encoders and widths, original parent and
four-real-crop banks, all eligible parents every epoch, every usable positive,
parent weighting, measured-parent depth and independent per-view 0.5 depth dropout.
Keep reconstruction 1.0/0.1, AdamW .001/1e-5, seed11/20epochs/batch256, native unit
geometry, the sole median-edge CPM rule and E013 refinement. No depth jitter,
window variance, taxonomy, markers in training, pretrained input or pseudo-links.

For each head, add an online-only 64->128->64 predictor with BatchNorm/ReLU in
its hidden layer. The existing unit head serves as the target representation;
there is no extra inference projector or larger encoder. Initialize the online
encoder/decoders exactly as dev5, copy it without RNG draws to a frozen target,
then construct predictors. This preserves encoder initialization but deliberately
adds predictor RNG consumption. Only within-parent, different-view pairs are
positive. Normalize the prediction and each stopped target separately; average
squared distance over every ordered distinct same-parent pair, then anchors per
parent, then the original length weights. Do not normalize the mean target into
a different objective. Singleton parents have reconstruction only, never fabricated
self-positives. Predictor BatchNorm sees only anchors with actual positives (at
least two views), including a one-parent tail, so no singleton BatchNorm fallback
or dropped parent is needed. Batch statistics couple examples but add no negative
labels. Fusion and sequence predictors are separate; their losses have weights
1 and 0.5. Teacher sees the same retained per-view branch mask, without new random
draws; opposing views still have independently dropped masks.

After each AdamW step, update target parameters and floating buffers by EMA with
cosine tau from .996 toward 1 over the declared total optimizer steps; copy integer
buffers. Target stays eval/frozen and never enters the optimizer. The current
encoder uses LayerNorm without running statistics; generic buffer semantics are
still tested. Predictor BatchNorm is online-only. Save online, target, predictors,
optimizer, update count and full history; inference uses the online encoder only,
without predictors or teacher. Exact independent native reload remains mandatory.

Monitor online/target fused and sequence unit vectors on up to 8,192 evenly spaced
eligible parents before training and after each epoch. Record centered covariance
effective rank, mean dimension std and pairwise mean cosine. Refuse nonfinite or
zero vectors; for >=128 rows, fail catastrophic collapse if mean std <.001 or
effective rank <2. These are label-free engineering refusal bounds, not biological
performance thresholds or a guarantee of useful discrimination. Keep diagnostics
even on failure; no automatic alternative model or retry of accepted science.

The BYOL paper (arXiv:2006.07733v3, method/EMA/loss and implementation) and reviewed
McDevol source justify predictor/stop-gradient/moving target as a bundle. Their
projection, normalization, coverage sampling and optimization recipes differ.
Reconstruction supplies information pressure here; it does not prove noncollapse.
Risks include low-rank but nonconstant outputs, depth shortcuts, weak/chimeric
within-parent views and poor separation without explicit negatives.

## Prospective decision

Compare only new E009 ten-depth and oral sequence-only fits with preserved E014,
E015, dev4/E013 and dev3 summaries. No rescoring, grid, oracle policy or new baseline.
Keep if both separately scoped post R95 endpoints do not decrease from E014,
at least one rises >=0.5 percentage points, neither >=90% target count falls,
and all contracts/collapse checks pass with no material hidden population loss.
Modify if useful recovery or >=90% gains coexist with losses; abandon this bundle
if both R95 endpoints fail to improve and neither >=90% count improves, or if it
collapses. Preserve the criterion even if a reasoned later direction differs.
Report target gains/losses, parent/old/post interactions, B3/neighborhood geometry,
all length/origin/marker/eligibility/unassigned populations, full 156/799 provided
denominators, E009 N-quarantine and oral known-shared sensitivity. Oral is a
provided-origin oracle, not unique sequence truth or measured-depth validation.

Closing the stronger-method recovery gap is the goal. Report descriptive E009
gap closure against retained MetaBAT2 (8.5493%), without executing it again or
claiming a single scalar diagnoses a mechanism. After results, choose between a
broader information/feature upgrade and a narrower follow-up using actual failure
patterns and the existing GLM/context/marker reviews, rather than another default
loss grid. Both communities are development; untouched confirmation still needs
separate full data/truth/overlap/cost admission.
