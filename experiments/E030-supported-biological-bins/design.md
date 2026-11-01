# Prospective design: supported biological bin construction

Frozen algorithmic direction before changed community outcomes, November 1, 2026.
This implements E029's next block, holding all six common teacher/student learning
instances, vectors, admitted retrievals, forests, physical marker calls and sample
axes fixed. It is a development bundle, not standard HDBSCAN or a probabilistic
genome classifier. No truth-selected thresholds, K, routes or grid.

## Why this block

E029's density-only parents swallow virtually the entire community. Exact Oral
retrieval is correct, but bin recovery remains below E023/E026. A bigger encoder
cannot correct root eligibility by itself. HDBSCAN's author documentation describes
root bias and normally excludes the root. Its relative cluster-persistence idea
also motivates removing absolute inverse-radius units from a candidate's utility.
Our sparse, bp-weighted adaptation is explicitly a heuristic, not that library.
Sources: https://hdbscan.readthedocs.io/en/latest/parameter_selection.html#allowing-a-single-cluster
and https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html .

The completed MetaCAT/SemiBin2 and E011–E013 source/call reviews support biological
profiles and reliable physical marker evidence. Their performance is not reproduced
here. Mean-only depth cannot support a per-base variance likelihood. Repeated
families are soft evidence, not universal cannot-links or measured contamination.

## One algorithm

1. Restore the exact six E029 results and their existing numeric forests and
   neighbors. Bind all members and original feature/vector/graph/call inputs.
   No MST or neighbor index is rebuilt. Retain the original condensed alternatives.
2. Exclude internal forest-root candidates from antichain selection. A supported
   isolated leaf of at least 200 kb remains eligible with its finite own core
   radius, including marker-negative leaves. The root-only control preserves
   E029's two-reliable-family leaf rule. A community root cannot win simply
   because birth is zero.
3. Normalize bp-weighted persistence by the candidate's bp-weighted mean inverse
   leaf core radius. This retains relative lifetime and mass, without unbounded
   preference for a denser numerical scale. Nonpositive life stays ineligible.
4. Compute additive weighted profile moments on the retained tree: sqrt-TNF with
   weight L * L/(L + 2500), and log1p measured parent means scaled by between-parent
   standard deviation, with weight L for measured rows. Between-contig scatter is
   a profile statistic, never invented measured window/per-base variance. Calibrate
   a channel's radius to half the 90th percentile of source-blind retained local
   pair squared differences. Persist IDs, masks, calibration and constant channels.
   A measured-zero/positive contrast is evidence; co-zero and missing depth provide
   neutral support, not perfect agreement. A constant channel is neutral.
5. Candidate context support is the mean of available channel supports
   1/(1 + scatter/radius). Uninformative depth contributes neutral 0.5. Combine
   relative persistence, context support and the original soft physical-marker
   breadth/excess factor in one bottom-up whole-versus-children antichain. Ties
   prefer children, retaining conservative alternatives and full choice reasons.
   Marker-negative candidates remain eligible. All calls retain their reliability.
6. One bounded merge pass considers only bin pairs connected by retained edges.
   Require mutual best support; score = 0.5 reciprocal vote + 0.5 mean profile
   compatibility + 0.1 bounded marker-quality change; accept at >= 2/3.
   The vote denominator includes all bin bp, not just external edges. No universal channel-AND
   or individual profile veto. Accepted merges are disjoint and deterministic.
7. One synchronous recruitment pass considers only unassigned eligible rows and
   their retained neighbors. Require two distinct assigned neighbors, >= 2/3 vote
   support and 1.5 best/runner-up margin. Combine vote, reliability-shrunk profile
   compatibility and soft marker change with the same 0.5/0.5/0.1 weights;
   accept at combined score >= 0.6. Profiles
   are fixed before the pass; recruited rows cannot recruit more rows. Keep
   abstention, measurement state and every rejection reason. Never invent new
   neighbors, assign excluded rows, force marker-negative DNA, or discard shorts.
   Persist the fixed post-merge profiles and explicit internal-to-canonical bin
   maps, so trace labels cannot be confused with pre/post export labels.

`src/dl_binner/construction/grouping.py` owns exact executable defaults. The source
and defaults must be hash-frozen before native outcome generation. Tiny real
reader/selection/export/reload contracts test roots, child alternatives, partial
calls, marker-negative DNA, zero/missing depth, ties, isolated leaves and complete
DNA accounting. Synthetic labels are engineering fixtures, not native truth.

## Selective control and decision criteria

Retain three new partitions per actor: root-only (unchanged E029 marker antichain
except internal root exclusion), profile-supported pre-recruitment, and final
merge/recruitment. The root-only control asks whether correcting the demonstrated
convention suffices; do not optimize an ingredient grid. All six actors use the
same implementation/defaults. E009 GLM includes teacher/proposals/student; Oral
remains explicitly no GLM with ten genuine depth columns.

Primary endpoints retain >= 200 kb bins and >= 95% confirmed all-bin purity, full
156/799 reference denominators, E009 conservative v2 / 3.3034% N quarantine and
separate Oral origin/shared sensitivity. Keep E023 E009 10.4163% and E026 Oral
13.8569%, both MetaBAT2 references and E029 as frozen context, without rescoring.

KEEP as provisional common development policy only if final GLM E009 and Oral
student R95 both improve over E029, neither loses target-90, and at least one
recovers its older E023/E026 anchor R95. MODIFY if there is a decision-relevant
primary student R95 gain but the joint criterion fails. ABANDON this
frozen bundle if neither primary student R95 improves. Preserve the criteria
unchanged, every target gain/loss and all length/origin/eligibility/measurement/
marker/unassigned DNA. Practical rules are not significance tests or biological
standards. No per-community winner router or product-family verdict.

The root-only and pre/post contrasts inform the next interpretation; they do not
silently override this primary-arm disposition if both primary R95 endpoints fail.

Both communities are development. Skin remains unscored; source/replicon/molecule/
taxonomy, overlap/pretraining, ambiguity/unique-versus-origin truth, depth,
unchanged protocol and separate cost/retention admission remain prerequisites.
