# Oral GLM: quality-preserving batching and prospective size alternatives

October 31, 2026. Local preparation only; no GPU or community inference.
The owner's new flexibility permits a smaller future development dataset/cutoff,
not an unrecorded change to E028's full-population cached comparison.

## Implemented execution path

`dl_binner.hybrid.batched` preserves canonical whole-view orientation, both strands,
4000 bp chunks with the same recursive token-overflow boundaries, all attended
special tokens, float32 reference attention, strand mean and bp-weighted chunk
mean. Tokenize each recursive candidate/strand once; retain encodings for inference
and QC rather than encode the same surviving chunk three times. Sort bounded
cross-view queues into length buckets and use up to eight sequences per forward.
Queue limits: 64 views / 2 Mb DNA, with an explicitly allowed single longer view
processed completely. No truncation, view substitution, mixed precision or cutoff.

The new bank schema separately records reference biological policy and actual
execution policy. It cannot masquerade as the old bank. The original Bank refuses
it; the new BatchedBank requires an explicit native admission before community
consumption. Parent-statistic and exact-crop normalization math is inherited
unchanged. Real tiny FASTA/view/token/padding/pooling/scatter/cache/restore and
corruption tests pass. A separately run check uses the retained hash-pinned
published tokenizer; its model is still an analytic CPU mock. No native DNABERT,
GPU throughput, numerical equivalence or quality gain is claimed from these tests.
The original failed Mac model allclose journal/tolerance remains unchanged.

## Prospective native admission

Before a full bank, use one fixed opaque-ID-hash cohort of 128 available original
views, stratified prospectively across length/token count, ambiguity, parent/crop
and both strands, with explicit actual coordinates/hashes. Run the original recipe
and this sole batched recipe on the same verified GPU/model/custom-source/tokenizer
and float32 attention backend. Do not search batch sizes against recovery scores.

Predeclared requirements: identical view/chunk/strand/token/special/unknown counts,
exact coordinate/hash/QC equality, finite float32 vectors, no lost/duplicated
model input, allclose `rtol=1e-5, atol=1e-6`, maximum absolute vector error <=1e-5
and per-view cosine >=0.999999. These are a new same-GPU batch-shape contract,
not a widened repair of old Mac inference tolerances. Retain both vector outputs,
all failures, actual peak VRAM/RSS, tokenizer time, padded/real tokens, batch shapes,
warmup and steady throughput. Any failure requires source diagnosis before use.
A valid native receipt binds this module, exact model, execution policy and
observed contracts; the actual consumer must explicitly choose the new bank.

Forecast every source view from its actual retained exposure, plus tokenization,
I/O, full bank verification, transfer, common teacher/proposal/student learning,
grouping, collection and shutdown. Do not multiply a short-fragment speed by all
long DNA or present a source-only estimate as measured acceleration. GPU admission
needs fresh credits/product/prices/quota/capacity, no payment-card exposure, actual
free space and the full schedule before the retention deadline. A small admitted
GPU probe is the next concrete extraction milestone; it is not authorized here.

## What dataset reduction actually saves

Reuse the accepted E024/E027 workload census; no cutoff sweep or DNA acquisition.
Token counts and old hours below are projections from the original native sample,
not new measurements or a price quote for batching.

| Parent cutoff | Parents | Views | Exposed bp | Projected tokens | Fixed vector bytes | Old hour projection |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 500 bp | 508,763 | 2,470,549 | 2,366,088,186 | 994,274,203 | 7,814,599,680 | 61.05 |
| 1,000 bp | 215,970 | 1,079,839 | 1,861,623,746 | 776,024,750 | 3,317,299,200 | 42.94 |
| 1,500 bp | 123,037 | 615,181 | 1,611,530,729 | 666,072,853 | 1,889,848,320 | 36.41 |
| 2,000 bp | 82,240 | 411,199 | 1,464,409,113 | 602,026,070 | 1,263,206,400 | 33.45 |

At 1,000 bp, 56.3% fewer views removes only 21.3% of exposed DNA and about 22.0%
of tokens; long contigs still dominate computation. The original per-view writer
has substantial call/tokenization overhead that the new implementation addresses.
A smaller row count alone therefore does not establish an equally large GPU speedup.

Prefer full-exposure batching if the native complete schedule is practical. If it
is not, a prospective 1,000 bp development cutoff is the first reasonable size
alternative, not a 1,000/1,500/2,000 score grid. It removes a further 203,177,403 bp
of 500–999 bp DNA from learned eligibility. Preserve that DNA in accounting and
full 799-reference denominators for an original-community claim; report its
excluded/unassigned and short-recruitment outcomes separately. Apply a declared
common availability/cutoff policy to E009 too for a whole-version comparison.
Existing strict bank/learner consumers do not already implement a selective
GLM-missing mask for these parents: that would need an explicit candidate, not
zero vectors or hidden parent substitution. Do not claim short-contig GLM quality
or generalization in unsupported ranges from the cutoff arm.

A fixed smaller genome community is also now a legitimate owner-permitted option.
Before outcomes, sample source IDs with a declared random seed and source-only
strata; retain unknown/non-target background under an explicit derivative protocol.
Using admitted origin IDs to construct data is not labels entering training, but
it changes community competition and difficulty. A derivative's full references
are the selected genomes' complete references, not their observed assembly bases;
retain a separate full-community accounting and do not compare its R95 as the
original 799-genome benchmark. Randomly dropping contigs is a weaker default:
it leaves many genomes partly represented and confounds recovery with removed DNA.
No subset is acquired, selected or scored in E028.

## Resources, storage and next execution case

The unaccelerated full-bank projection is 61.05 GPU hours / about $65–85 complete
at dated rates. It is not a fresh admission or a reason to abandon GLM. Native
batching speed and feature equivalence must be measured first. Plan one separately
authorized <=1 hour temporary GPU admission probe at roughly $2–3 gross including
setup, small disks and transfer, subject to live first-party credit coverage and
capacity. If it forecasts a practical full bank, then admit the complete extraction
and common learning with one frozen recipe; otherwise propose the single cutoff
or controlled derivative with explicit claims, rather than silently weakening it.

The fixed full vector array is 7.815 GB; quality/masks/IDs/details add storage, and
checkpoints, simultaneous old/new banks, compressed return and transfer coexist.
A provisional full worker needs about 20–30 GiB peak work including verified model/
runtime and collection, >=16 GB VRAM and 32 GiB RAM; measure it in the probe.
The original CPU work disk had only about 30 GiB free at E027 shutdown; adding a
roughly 9–12 GB bank while preserving 25 GiB free needs safe cleanup or separately
approved temporary storage. Audit exact-byte duplicate transfer archives and
unused compiler/temp caches first, with locators/hashes/no-current-user proof;
never delete original inputs or accepted unique evidence. A disposable 64 GiB work
+ 40 GiB boot GPU worker is a later separately admitted option, not provisioned now.
Moving vectors to GCS does not remove simultaneous local training/verification needs.

Existing ten-sample means and full-reference mappings remain reusable for a later
ID/length/genome subset with their original competitive mapping semantics. Slice
rows/columns explicitly; do not invent variance/window coverage. Mapping against
a reduced reference or changing alignment filters requires new mapping/suitable
retained alignments, separately authorized. No mapping is proposed for this block.

November 4, 00:00 Copenhagen remains hard. A full unaccelerated GPU schedule may
not fit after this CPU comparison and review. If the complete admitted schedule
cannot fit, obtain a separate retention decision before execution; cost flexibility
and remaining credits do not extend storage. Skin remains unscored with its
already admitted origin bytes and outstanding biological/unique-support/depth/
evaluator/overlap/protocol/cost dependencies, not another automatic dataset campaign.
