# Prospective E021 design

Frozen before candidate or skin scores, October 23, 2026. Base: accepted E019
dev7 source and E020 reviewed integration, preserved on their original commits.
The user authorizes a new descriptive branch and conditional comparison, not a
new resource/service/retention scope.

Use exact E002/E003 DNABERT-S weights/tokenizer/custom-source pins read-only.
For each retained eligible parent and every available original crop, extract
that exact DNA with canonical whole-view orientation, both strands, attended-token
mean including specials and base-weighted nonoverlapping <=4,000 bp / <=1,024-token
chunks. Explicitly select the hash-verified author Torch float32 attention fallback;
its optional Triton path downcasts QKV/bias to fp16. No source/weight patch or
placeholder module. No truncation, parent-GLM substitution for crops or regenerated views.
Cache float32 768-dimensional features in indexed NPY arrays with explicit IDs,
view coordinates, DNA SHA256, availability and model/source/runtime receipts.
Short/excluded parents remain in input accounting; the inherited 500 bp training
cutoff is experimental eligibility, not product policy.

Fit GLM column statistics only on eligible full parents; apply saved z-score and
L2 geometry to all views. Add a 768 -> 128 -> 64 GELU/LayerNorm branch and a
zero-initialized 64 -> sequence-output residual into E019 sequence fusion. A
sigmoid gate uses only log view length and ambiguity fraction. It is a learned
reliability adapter, not calibrated confidence or a truth label. Keep full-parent
exposure, every available positive, stopped EMA targets/predictors, reconstruction,
measured-parent depth/dropout, seed 11 / 20 epochs / batch 256 and exact unit geometry.
Keep E019 ordinary sole CPM/E013 uniformly; no marker-aware training, taxonomy,
backbone tuning or ensemble. Retain all features, embeddings and pre/post partitions.

Test real tiny native extraction on synthetic DNA and complete cache/view/gradient/
EMA/reload/group/marker/refiner/export paths; mocks establish only their own boundary.
E003's failed short-neighbor criterion and original portability/collapse guards
remain. Review primary author source/pinned code; do not repeat old community science.

One prospective two-development-community candidate vs preserved E019 comparison,
no baseline refit/rescore. Keep if neither final R95 declines, at least one gains
>=0.005 absolute and neither >=90%-recovered target count declines, with all contracts;
abandon if neither R95 nor either count improves, otherwise modify. Practical
thresholds are scoped decisions, not significance. Full 156/799 denominators,
N quarantine, oral origin oracle/known-shared sensitivity and every length/origin/
eligibility/marker/unknown/non-target/unassigned population remain. No score grid.

Admit only the five frozen skin files plus <=10 MiB small metadata, <=10 GiB total
extra local storage, four threads, 8 GB sampled RSS and four cumulative acquisition/
validation hours. Stream/index full source joins and preserve zero-bp/zero-origin,
replicon/molecule/host/taxonomy ambiguity and exact/near/pretraining overlap. No
skin fit/score before frozen candidate/comparator/protocol and independent truth
admission. GSA lacks assembly errors and admitted contig-level depth. A missing
historical pretraining inventory is a limitation, not an automatic truth blocker.

Full CPU/GPU extraction runtime, complete native source/library compatibility,
peak disk/coexistence, return/review footprint, fresh trial product eligibility
and the October 28 storage deadline must pass before paid execution. No old budget
carries over; do not claim Mac extrapolation is native affordability.

Primary-source checks, October 23: the exact retained model custom source and
[revision](https://huggingface.co/zhihan1996/DNABERT-S/tree/00e47f96cdea35e4b6f5df89e5419cbe47d490c6)
resolve attention/pooling/tokenization behavior. E002/E003 model/runtime records
and the completed competitive/thesis reviews are reused; no new whole-field
review or reproduced paper result is claimed. E003's short-neighbor criterion
failed despite better restricted grouping: this hybrid is a complementary
information hypothesis, not guaranteed recovery. The frozen Transformer prior
and compact E019 self-attention are complementary. A larger raw-DNA model,
fine-tuning and reliable marker learning remain serious alternatives if this
information route fails, not automatic additions before the matched evidence.
