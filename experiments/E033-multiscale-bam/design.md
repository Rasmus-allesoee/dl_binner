# E033: common measured multiscale coverage and bootstrap-preserving learning

Prospective November 4, 2026, before any changed community measurements or scores.
Parent source is `ba7f9b5`. Local implementation and engineering only are authorized.
[E032](../E032-biological-candidate-selection/comparison-review.json) remains MODIFY;
its Oral long-singleton improvement is distinct from fragmented-genome learning.
One common E032 constructor is provisional, not optimal or selected per dataset.

## Information and measurement treatment

Use all twenty retained complete-reference BAMs, without remapping or reading them
locally during preparation. One pinned pysam 0.23.3 / HTSlib reader verifies actual
coordinate order, complete reference dictionary and explicit ordered sample IDs.
Match the BAM dictionary to the retained source-blind feature axis explicitly;
no header-origin label enters learning. Keep all original rows, including empty
original records outside the emitted BAM dictionary when explicitly declared.

Retain primary mapped records only, excluding flags 0xF04 (unmapped, secondary,
QCFAIL, duplicate, supplementary). MAPQ >= 0, but reject 255 as unavailable.
Require integer NM and exact CIGAR accounting: identity =
(aligned M/=/X length minus inferred substitutions)/(M/=/X + I + D), >= 0.97.
Validate NM-I-D against explicit X and =; reject malformed/inconsistent input,
reference skips and missing sequence. Clipping does not enter identity. NM follows
the mapper's treatment of ambiguous bases, which is not unique-placement proof.
BQ threshold is explicitly 0 (missing qualities are allowed and counted in audit).
Count all aligned M/=/X bases, including substitutions, excluding I/D/skips/clips.
Overlapping mates count twice; moments describe aligned-read depth, not independent
templates. No implicit pileup depth cap, quality default or contig-end trimming.

Measure full-parent and the four exact **retained** DNA-view intervals. Full
interval length, including zero positions, is the denominator. Keep sum depth,
sum squared depth, covered bases, and MAPQ >= 20 aligned-base mass. Population
variance is E[d²]-E[d]²; breadth is covered/length. No sample-variance switch
changes a mean. Compact arrays carry explicit interval and sample validity; an
unmeasured interval is not a zero. Accumulate interval events with a coordinate
sweep, never an assembly × samples dense per-base matrix. Validate integer sums
and retain read/filter counters and source/coordinate/content hashes.

The JGI no-variance path remains unadmitted. The retained stderr explains its
zero: huge scalar counters were reset by the guard. The pinned source has an
uninitialized fresh CountType array; the logged counters differ by exactly the
expected 597-base scalar increment, strongly supporting that source diagnosis.
Integer division is a separate defect. Test our independent counter on the same
fixture; no Linux binary rebuild/rerun or corrected JGI production claim is made.

Unique-template cross-contig links are **deferred** from this candidate. The
retained coordinate streams do not certify both mates' uniqueness merely from
RNEXT/PNEXT, and a name-join/dedup pass adds a different information contract.
Keep a concrete reader/safeguard specification, rather than turn JGI aligned-base
mate support into template counts. Breadth/dispersion are reliability observations,
not contamination probabilities or invented window coverage.

## Shared representation and full information policy

Restore each mode's exact E031 online/EMA/predictor/Adam state and transforms.
Keep its useful composition, bounded DNA context and admitted optional GLM state.
**Replace the inherited scalar-depth input with the new shared parent means at
every forward**; no old depth table enters teacher/proposals/student. Refit only
the parent-depth transform on eligible newly measured parents, preserving TNF/GLM
transforms and all learned parameters/optimizer state. Add one compact, zero-output-initialized
residual coverage branch to the fused unit vector. Its cells contain measured
parent/window log means, breadth, log dispersion, high-MAPQ fraction, exposure and
validity. Per-sample shared MLP then fixed ordered-sample fusion preserves both
abundance magnitude and multi-sample shape. Bound reliability by interval length,
positive support, mapping confidence and overdispersion; do not equate co-zero
with positive agreement. Missing samples and measured zeros have separate states.
Full parents use their actual full interval; crops use their own measured interval
plus explicit parent context. Depth dropout acts on the entire new branch.

The inherited depth encoder remains useful on the newly normalized shared means;
reliability additionally conditions the new residual branch. The initial model is
the retained base function followed by the declared final unit normalization
**on the new inputs**, not necessarily
the old run output. That final normalization can introduce one-ULP roundoff at
zero residual; this does not relax any old portability/reload tolerance. This is a prospective information treatment, not a cache repair.

New modules use a declared seed-11 stream. Base weights, buffers and optimizer
moments/steps are copied exactly; new Adam slots remain absent until gradients.
Copy EMA without RNG draws. Keep frozen base sequence/context/GLM anchors with the
same newly measured parent-depth policy. Train a 20-epoch self-view adaptation teacher,
then a 20-epoch confidence-filtered signed-marker continuation of that same teacher.
Both have lower-rate AdamW 0.0002, anchor weight 0.1, batch 256, every available real
view/full-parent exposure, stopped EMA targets, trained online predictors and unit
geometry. Preserve
the admitted reconstruction coefficients and original EMA/collapse safeguards;
the new depth decoder targets actual measured parent/window log means only where
valid. The composition decoder still targets parent composition. An inactive
old scalar-depth decoder is retained for state provenance, not silently reused
with changed target semantics. No taxonomy,
new GLM extraction, marker redetection or truth enters this path. The restored
weights/moments still encode their historical E031 inputs, including the old
dataset-specific depth filters. Shared new inputs do not erase that history.
This is one common warm-start upgrade, not a measurement-from-scratch isolation
or proof that all historical between-community confounding has disappeared.

Fresh teacher vectors and graph drive fresh pair proposals using the new shared
parent means and cached physical markers, followed by reciprocal/shared-neighbor
and measured-reliability attenuation. Preserve original proposal-slot denominators.
GLM availability applies to initialization, teacher, pair proposals and student,
not just a student input flag. Retain feature/view inputs, new summaries, models,
optimizer/EMA histories, exact reload vectors, neighbors, both forests, candidate
alternatives and E032 pre/post partitions. New downstream parent depth is the
shared measurement; E032 mathematical selection/defaults stay unchanged.

## Comparison and selective control

Prepare three modes: E009 ten-depth GLM off/on and Oral ten-depth GLM off, with
one implementation/defaults. Compare new outputs only against frozen E032 and
stronger E031/E023/MetaBAT2 summaries. This integrated information/learning bundle
does not isolate measurement, extra exposure or architecture individually.
At most one later decision-changing control is reserved: the identical model,
initialization, schedule and shared measurements with the new branch restricted
to parent means. It is not included in the first execution by default; no grid.

Use full 156/799 provided denominators, E009 conservative v2/3.3034% N quarantine,
Oral provided-origin and known-shared sensitivity, every length/origin/eligibility/
marker/zero/unknown/non-target/unassigned population and single-/multi-contig strata.
KEEP requires no R95/T90 loss against E032 in all three modes, >= 0.5 percentage
point R95 improvement in an E009 mode, and no loss in best-bin multi-contig R95
contribution (total recovered bases minus those whose primary best bin is a singleton,
same full reference denominator). This is a decomposition of the primary metric,
not a multi-contig-only search for another best bin. MODIFY retains
useful trade-offs; ABANDON the bundle if no mode improves R95 or an E009 mode loses
>= 1 point without >= 0.5 point gain in another mode. Integrity failures remain
NOT ASSESSED. These practical criteria are not significance tests or product bans.

Source-informed alternative bin-generation/selection methods in standalone binners
remain an open later question. E032's greedy marker/profile proxy is neither
optimality evidence nor a permanent design commitment. This block holds it fixed
to learn about new information, rather than tune it on the development scores.

## Local and later native boundaries

Real tiny BAM/filter/identity/moment/window readers, independent counters, real
training/gradient/EMA/reload/geometry/cache and grouping/marker/export contracts
are required. Explicitly mark synthetic marker calls and mocked GLM inference.
Four numerical threads, bounded tiny DNA only; preserve failures and old Mac
portability tolerance. No community measurement, fit, score, bulk BAM/read transfer,
VM/GPU request, paid work, resource change or retention extension in preparation.
Prepare a serial in-region BAM pilot and complete six-fit/three-mode comparison,
with measured shape, sort/spool coexistence, setup/collection/review and cost gates.
Protect E032's task disk until its closed-delivery tail is verified during a later
explicitly authorized session. Active retention ends November 11 at 00:00
Copenhagen; the approved automatic tail ends November 18. Old budgets do not carry.
