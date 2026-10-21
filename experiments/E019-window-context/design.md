# E019: bounded local composition context

Prospective design, October 21, 2026, before changed community outcomes. Local
implementation and engineering are authorized; community execution is not.

E018's original ABANDON remains. Additional assignments contaminated otherwise
recoverable bins, while E016 oral learned neighbors remain weak and long cores
mix sources. Whole-contig TNF erases within-contig composition and its arrangement.
Test a coherent information/encoder upgrade, not another recruitment threshold.
E016 is the immutable comparator and its CPM/E013 is the first fixed downstream
context. E017/E018 and older summaries are retained context, without refit/rescore.

## One candidate

Keep seed 11, 20 epochs, batch 256, all eligible parents once per epoch, full
parent plus every distinct accepted crop, parent-balanced positive-only stopped
EMA target/predictors, existing reconstruction weights and parent-depth dropout.
Use the original E014/E016 feature/view bytes and crop coordinates, not a new
crop draw. Keep all contigs; eligibility is still 500 bp and valid fourmers.

For each available DNA view, choose its lexicographically smaller IUPAC forward
or reverse-complement string. This canonical strand is sequence-only, independently
chosen per view, and exactly strand invariant. It can change discontinuously after
small sequence edits; do not claim rotation or biological-context invariance.
Partition that string into min(8, max(1, floor(length / 256))) intervals. From each
interval take its centered at-most-512-bp window; record coordinates in the canonical
view and the strand needed to map them back to the original parent. Long views
are sampled, not exhaustively tokenized. Global TNF still represents all view DNA.

Each local token contains 136 reverse-complement fourmer class **integer counts**,
normalized using the same frozen parent-fitted sqrt/z-score/L2 transform as the
global branch. Add a learned projection of normalized center, span and valid-
fourmer fraction. All-ambiguous windows are masked; padding carries no evidence.
One global view-TNF token always remains visible, preventing all-masked attention.
No coverage, source ID, coordinate-to-genome join or label enters local tokens.

The 256 bp interval scale reuses the minimum accepted crop scale; 512 bp caps
local counting noise/cost, eight windows bound storage and CPU, and the complete
global branch protects information outside those windows. These are prospective
engineering heuristics, not truth-selected optima. A 500 bp parent has one local
token and gains little new local information; a long parent is only sparsely
sampled. Report those limitations by length rather than claiming full context.

Use one pre-norm self-attention block, width 64, four heads, feed-forward width
128, GELU, zero attention/activation dropout; residual paths and masked mean
pooling over the global/valid local tokens. Normalize its 64-dimensional output
and project it to 128 through a bias-free **zero-initialized residual** added to
E016's unchanged 128-dimensional global composition branch.
Keep an explicit depth branch and fusion/output dimensions 64 as before. Decode
the same full-parent composition and measured parent means. Sequence-only mode
has no depth module; missing-parent depth is masked. Depth is not replicated into
local tokens and is never called measured window coverage or variance.

Initialization is deterministic at seed 11. Original modules are constructed
first, and predictors use their original RNG point in an isolated RNG scope.
The initial student/teacher outputs and shared weights therefore exactly match
E016 for identical inputs; the new residual first learns its projection, then
passes gradients into attention. The teacher is copied without new RNG draws.
This still changes the model/information bundle, not only one attention operator.
Context positions,
token counts and validity may expose length/ambiguity nuisances, reconstruction
may suppress discriminative information, and chimeric-parent positives remain
possible. Retain length/origin/collapse diagnostics rather than assuming context
must help. No new loss or per-bin/community policy is selected from outcomes.

Attention is justified here as a small content-dependent interaction among at most
nine tokens, including position/reliability. A pooled MLP would preserve local
heterogeneity but lose those interactions; a CNN adds a fixed-neighborhood prior.
Neither alternative is biologically disproved. This is not an implementation of
CompleteBin, nor a test isolating attention from token information/fusion. A larger
raw-DNA Transformer is unnecessary for this first information test. Frozen GLM
features can complement it by importing reference-trained sequence information;
old laptop cost and E003's mixed result do not veto that later hybrid. Marker
training still needs reliable links, given same-genome repeats and panel limits.

[Targeted primary checks](source-review.json) bind author CompleteBin's TNF
projection/position/Transformer path at its retained commit, PyTorch 2.2.2's
actual attention mask/fast-path implementation, and the accepted E016 source.
The one-block width 64 / four-head / feed-forward 128 choice bounds interaction
cost near the existing output width. It is a fresh model, not a pretrained GLM or
a claim to reproduce CompleteBin's larger, multimodal/pretrained pipeline.

## Bounded storage and numerical contracts

Write only eligible-parent x five-view x eight-token counts as uint16 indexed NPY
files, with int64 coordinates and parent-row map. Read-only memory maps serve
batches; never copy the entire token bank into RAM. No overlapping-crop cartesian
bank, dense per-base coverage, automatic downloads or token regeneration on cache
failure. Verify full source/input/view hashes, every member, coordinates, masks,
counts and original ordered axes. Preserve zero/short/ambiguous DNA in the parent
accounting. Store manifests, teacher/optimizer histories, features, embeddings and
pre/old/E013 partitions. Full DNA exports are accounted for separately from return
archives; omitted bytes are not backed up by inventory hashes.

Local checks use four numerical threads, 8 GB sampled tree RSS, per-attempt 30-minute
engineering clocks and 4 GiB new local space. Only generated engineering DNA and
accepted tiny native fixtures may be fitted. Actual native readers, attention,
gradients/stop-target/EMA, strand/padding/short modes, reload, CPM/E013 and complete
export are tested in the built wheel outside the checkout. No community scores
or bulk context bank in this task. Mac/native portability failure remains failed.

## Prospective decision

First compare one candidate on E009 ten-depth and oral sequence-only against
preserved E016, with all parent/old/E013 alternatives. Keep if post weighted R95
improves in both truth scopes by at least 0.5 percentage point and neither >=90%
target count falls. Abandon this frozen bundle if neither post improves and neither
>=90% count improves; otherwise modify after retained error/geometry diagnostics.
These practical thresholds are not significance tests or product-family rules.
Also report target/length/origin/eligibility/marker/unassigned effects, neighborhood
agreement/effective rank and computational trade-offs. No per-community/bin oracle,
threshold search, new seed or compulsory factorial study. No extra fit ablation is
planned now: a bundle comparison can decide whether this information route merits
development. Later ablate at most one element if it would change a design decision.

Both communities are development. Use conservative E009 v2 (156 references,
3.3034% N quarantine) and separately named oral provided-origin oracle (799 full
references and known-shared sensitivity). Unique-origin oral truth, genuine GSA
depth, read-assembly transfer and unseen-genome robustness remain unestablished.
Skin remains frozen/unacquired, pending separate source/genome/replicon/molecule/
taxonomy/overlap/ambiguity/full-denominator/unique-versus-origin and cost/retention
admission before untouched confirmation. Do not wait for competitive scores before
broader validation, or add data to rescue a failed mechanism post hoc.

## Engineering amendment before community execution

The initial concatenation/projection bottleneck passed two epochs, but the actual
20-epoch contract stopped at epoch 3 on GC-iid DNA (sequence rank 1.5067) and at
epoch 5 on a higher-dimensional oligomer fixture. Both source builds, data, failed
geometry/terminal journals and the original threshold remain. The unchanged E016
engineering comparator also stops on GC-iid DNA, but completes all 20 oligomer
epochs with sequence rank 23.43. Thus the GC case is not evidence isolating a new
bug, whereas the oligomer differential exposes a stability regression in the new
fusion. No community score was inspected and no family is rejected.

Before testing another version, replace that bottleneck with the zero-initialized
residual above and preserve original predictor initialization. This starts from
the working E016 map, rather than relearning it through a new random bottleneck;
it changes no loss, seed, schedule, real-view bank, depth or downstream rule. Test
exact initialization and first/second-step gradient flow, full 20-epoch oligomer
stability/reload and the actual native adapters again. The original failed tests
do not become passes. Keep the GC stress failure as a limitation and retain the
strict rank/variance refusal on future inputs. Residual initialization is supported
by the targeted official torchvision ResNet source and residual-learning paper,
as a generic optimization principle, not binning performance evidence.
