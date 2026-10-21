# Robustness, depth and the timing of additional data

2026-10-21, prospective E018 assessment. This is interpretation of accepted
[E017 results](../E017-information-aware-grouping/comparison-review.json), actual
native transform metadata and frozen source, not a new score or causal depth test.

The oral decline is serious: full-reference weighted R95 falls 6.7719% to 4.9664%,
with 45 targets losing recovery, 23 gaining and 34 -> 21 reaching 90%. E009 gains
do not cancel that failure. Extra unassignment and many mixed oral core bins make
this a robustness problem for a system that supports sequence-only inputs. Keep
E016 as the broader provisional anchor; no per-community routing oracle.

Depth is an important difference, not the only difference. Oral has 1,286,547
nonempty contigs / 1.670 Gb, versus E009's 145,702 / 231.68 Mb. Its 799 source
targets, long-core/fragment population and error-free pooled GSA differ from the
156-target read-derived gut assembly with conservative alignment truth. Origin
oracle versus conservative unique support also changes interpretation. These
confounders prevent attributing the endpoint difference to depth or declaring a
sequence feature/architecture universally inadequate.

## Implementation audit and plausible mechanisms

`information/grouping.py:contexts` retains an empty depth matrix for oral. Native
metadata reports `depth_usable_columns=[]`, all 1,286,547 rows depth-unavailable,
and the depth calibration channel constant. E009 has ten usable columns and only
13 depth-unavailable rows. `distances` gives missing depth zero weight, divides by
available evidence weights, and gates depth agreement only when available.
`core_profiles`/`recruit` similarly exclude absent depth from profile means. It
does not substitute measured zero coverage, invent variance or divide by a missing
depth scale. All native affinity/profile/selection readback and axes contracts
passed; both actual tiny depth/sequence paths are exercised locally for E018.
No demonstrated missing-depth implementation bug explains the difference.

Several correctly implemented choices can still fail. Without depth, composition
and learned vectors are more correlated; they offer less independent evidence
against near strains/shared sequence. The joint retrieval index uses only those
two channels even when depth later reranks; missing good candidates or mixed long
cores can therefore constrain either mode. Finite-length affinity/background
gates, the supported-core population and per-bin empirical profile radii can
behave differently across communities. In particular those radii are not
calibrated cross-bin probabilities. Requiring their distance winner/margin to
agree with votes can discard a unique candidate that already passes every
existing profile/support/vote gate. E018 isolates that acceptance mechanism; it
does not fix mixed cores or prove that this mechanism explains all oral loss.
The strict native `<` margin versus original prose `<=` shorthand is preserved
in E017 as a discrepancy, not silently changed or claimed as the cause.

The new consumer also explicitly checks opaque-ID-to-FASTA indices and canonical
bin-label permutations, distinct candidate IDs/votes, old-accept preservation,
native cache/source identities and all excluded/short/non-target DNA. No tuning
or biological optimality claim follows from those engineering checks. The
original failed cross-platform numerical tolerance remains unresolved.

## Oral mapping: valuable, separately costed and deferred from E018

Sequence-only oral remains adequate for this *fixed-input acceptance question*
and is a useful stress test of the supported no-depth mode. It is inadequate to
measure current-system depth benefit, depth-enabled cross-community recovery,
read-assembly realism or unseen-genome generalization. Old dev3 TNF/depth controls
do not answer those questions for E016/E017.

The prior [publisher/read/header assessment](../E014-multiview-reconstruction/depth-assessment.md)
identified ten oral samples 6,7,8,13,14,15,16,17,18,19 with **51,731,811,351 bytes /
48.18 GiB** compressed interleaved FASTQ. The illustrative four-sample subset is
20,684,706,398 bytes / 19.26 GiB and is not a scientifically frozen choice. Source-
genome BAMs do not provide measured depth on the pooled GSA contigs. Projecting
their coordinates through truth would create a different, potentially oracle-
assisted feature. Genuine depth requires remapping actual reads to the exact
admitted GSA DNA and declared multihit/filter/summary semantics.

Fresh metadata-only HEAD verification is retained with this preparation; any
unavailable endpoints remain explicitly historical sizes, never downloaded data.
No reads are acquired. Current rough all-ten mapping estimate remains 8–24 hours
on four numerical threads / existing 8-vCPU, 32-GiB VM, 12–26 GB RSS. At current
existing-resource prices, compute/IP is **$2.18–6.55**, run-period disks
**$0.34–1.01**, before operations, storage, export, safety margin or subsequent
feature/learning/grouping work. A **rough $4–10 mapping-only scope** could be
reasonable if a bounded pilot passes; it is not a frozen budget or execution
approval. Cost is not inherently prohibitive given credits. The uncertainty and
information question matter more than saving a few dollars.

Disk is the sharper practical risk: old estimates are 100–180 GiB extra if all
reads/BAMs coexist, or 45–130 GiB with serial streaming; the last E017 minimum free
was 84.67 GiB, leaving about 59.67 GiB over the reserve. Thus upper estimates do
not fit the current disk. A future plan needs measured index/sort/BAM coexistence,
an exact retention/export policy and possibly separately approved storage. Ten
contig means are only ~51.5 MB float32; dense per-base float32 tracks would be
~66.8 GB and should not be created merely to obtain parent means. No promise is
made that serial streaming fits before native measurement.

Adding depth to the frozen E016 representation is not a retroactive explanation
of its original result. A grouping-only depth control can hold vectors fixed and
test downstream use; a whole-system depth comparison requires fresh feature/view/
learning/protocol admission. Revisit after E018 if oral remains the limiting
failure, or before choosing a depth-specific product policy. A prospective
current-system test on E009's already measured depth may first separate learning
from downstream effects more cheaply, but is not an additional automatic test.

## More communities

Do not expand into a broad benchmark campaign during this control. Two inspected
communities already reveal a material transfer failure; adding many can consume
engineering/compute while the same flaw remains. Nor should additional data wait
until we look competitive: repeated decisions on two communities can overfit.
Keep the existing untouched skin choice frozen now; admit one additional dataset
at the next coherent candidate milestone and before any robustness/confirmation
or product-default claim. A read-derived community with genuine multi-sample
depth is particularly relevant if current depth dependence drives that decision.

Skin remains unacquired pending actual sample/source/genome/replicon/molecule/
taxonomy joins, exact/near/pretraining overlap, duplicate-safe denominators and
zero-origin DNA, competitive ambiguity and unique-versus-origin truth, an
unchanged confirmation protocol and separate acquisition/compute/cost/retention
admission. If it influences a design choice, call it development and reserve a
later untouched confirmation. E018 has no permission to add those payloads.
