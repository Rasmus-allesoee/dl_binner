# Common measured coverage: source review and E033 preparation

November 4, 2026. This note distinguishes retained native observation, source
interpretation and new local engineering. No new community summary, fit, score,
VM, GPU request or paid cloud work occurred. [E033](../../experiments/E033-multiscale-bam/README.md)
owns the prospective design, source locks, checks and separate cost request.

## Why this coherent block

E032's large Oral gain mostly reflects intact genome-length singleton eligibility;
its E009 multi-contig gap survives. [The accepted trace](../../experiments/E032-biological-candidate-selection/trace-audit-reviewed.json)
and [measurement audit](2026-11-03-depth-and-standalone-candidate-audit.md) identify
concrete missing information: inconsistently filtered parent means, no measured
crop-local profiles, no coverage breadth and no within-contig dispersion. A larger
Transformer cannot infer those observations from a repeated parent mean.
COMEBin/SCGBinner and SemiBin's actual split/view paths provide relevant source
precedent. They do not prove our reliability proxy or its coefficients optimal.

Choose one shared measurement/representation bundle with the common E032 selector
fixed. Preserve learned E031 composition/context/depth/optional-GLM state and Adam,
then adapt its own teacher and signed student using newly measured inputs. The
initial checkpoints still encode historical differently measured data; common new
inputs do not erase that history or isolate a single causal ingredient. Two
communities remain development data. No product modality or SOTA claim follows.

## The JGI zero is explained by retained evidence

The previous audit left the no-variance zero unresolved. Inspecting the **retained
stderr**, not just the zero table, finds two huge-mean warnings:

- Covered contig scalar count: 125,243,924,434,293.
- Zero contig scalar count: 125,243,924,433,696.
- Difference: **597**, precisely the expected accepted scalar count after three
  NM substitutions. The native huge-mean guard resets both values to zero.

Released v2.18 source `a51200652a8907629b83d63fa5fa6c2f6612d105` allocates
`new CountType[header->n_targets]` without value-initialization on the fresh path,
then accumulates with `+=`; only the reused-buffer branch calls memset. This is
an uninitialized-counter defect. It strongly explains the matching garbage offset
in the native warning. Separately, the scalar `uint64 CountType / int correctedLen`
truncates before conversion to double: even zero-initialized 597/400 gives 1,
not the old 1.4925 source prediction. A binary/source rebuild was not performed.
The immediate reason for the observed zeros is directly established by the log;
the underlying initialization diagnosis is source-supported, not a reproduced fix.

[Exact hashes and observed values](../../experiments/E033-multiscale-bam/source-audit.json)
bind the old warnings, table and released source. Both failed native evidence and
its earlier interpretation remain unchanged. No-variance JGI remains unadmitted.
E009 used samtools depth and E024 its own reducer, so this diagnosis does not
invalidate their accepted depth artifacts. No aligner or external binner ran here.

Primary source: [v2.18 JGI implementation](https://bitbucket.org/berkeleylab/metabat/src/a51200652a8907629b83d63fa5fa6c2f6612d105/src/jgi_summarize_bam_contig_depths.cpp).

## One exact common measurement

Use primary, non-QCFAIL/nonduplicate/nonsupplementary records; retain MAPQ 0 and
exclude unknown MAPQ 255. Require NM/CIGAR-consistent identity >= 97%, explicit
BQ 0, no contig-end trim, aligned M/=/X including substitutions, no I/D coverage,
full interval denominators and overlapping mates counted twice. Explicit =/X
must agree with NM. Malformed kept records, unknown dictionaries, actual unsorted
records, missing NM or reference skips fail. Sorting header alone is insufficient.
Missing qualities at BQ 0 are allowed and audited. NM is the pinned mapper's edit
counter; it does not certify uniqueness or resolve every ambiguous reference base.

Pinned [SAM v1.6](https://samtools.github.io/hts-specs/SAMv1.pdf),
[pysam 0.23.3](https://pysam.readthedocs.io/en/v0.23.3/api.html) and
[StrobeAlign v0.17.0 writer](https://github.com/ksahlin/strobealign/blob/v0.17.0/src/sam.cpp)
support coordinate/flag/reader semantics. The writer emits primary SEQ/qualities
and NM from alignment edit distance; its omitted secondary SEQ is explicitly
excluded. Actual old dictionaries and source/sequence/view locks remain mandatory.

The new RLE interval sweep keeps integer prefix moments only at full-parent and
four retained DNA-view endpoints. It never allocates assembly × BAM per-base
matrices. Mean, population variance, breadth and high-MAPQ aligned mass share the
same real exposure. Missing/failed measurement cannot become measured zero. An
independent dense **SAM-text/per-base** counter tests the same real encoded BAM,
including clips/indels, ends, reverse/overlapping mates, quality/flags, zeros and
exact windows. The old JGI fixture gives 0.9 full-parent mean under the new explicit
primary-only rule, with population variance 1.89; its different old JGI output is
not redefined as equivalent. Tiny timings are engineering, not native affordability.

## Reliability and training limits

The new compact branch sees actual parent/window means, breadth, dispersion,
high-MAPQ fraction, exposure and zero/validity state. Reliability is a bounded,
predeclared heuristic based on support/length/mapping/overdispersion, not calibrated
same-genome probability. Coabsence is neutral; measured positive-versus-zero can
support a contrast. Measured all-zero intervals retain their state even when they
supply no positive reliability weight. The inherited branch consumes newly shared
parent means, and crops additionally receive genuine local statistics. Normalizing
fused vectors preserves one geometry throughout train/reload/group/export.

A zero-initialized residual still has the declared final unit normalization; one
ULP from renormalization is not a failed old Mac tolerance repaired by widening it.
Old encoder/predictor/EMA/Adam parameter and buffer bytes are restored exactly;
new slots start absent. Actual old reconstruction coefficients are **1.0/0.1**,
verified from retained checkpoint metadata. GLM off/on propagates through new
initialization, own teacher, proposals and student. Only GLM **inference** is mocked
in the tiny GLM fixtures; cache readers, coordinates and learning are real.

Unique-template cross-contig links are deferred. RNEXT/PNEXT or JGI aligned-base
mate support alone does not certify two accepted uniquely placed ends, prevent
QNAME collisions or avoid double counting. A later version would require explicit
read-group/template identity, both ends' MAPQ/NM/flags, reciprocal consistency,
orientation/insert/edge context, repeat/degree/hub guards, independent-template
support and coverage-normalized confidence, with a real name-join contract. Do not
invent those properties from retained means.

## Later selection, Oral GLM and confirmation

[Q006](../research/questions.md#q006) keeps the source-informed standalone candidate
selection question visible. COMEBin partition ranking, SCGBinner iterative
selection, SemiBin's distinct short-/long-read paths and CompleteBin staged
selection are alternatives. E032's current score/pool/greedy claims are provisional;
its two development communities cannot establish optimality. E033 holds that
policy fixed, rather than spending another block tuning it.

[The Oral GLM milestone](../../experiments/E033-multiscale-bam/oral-GLM-milestone.json)
prepares one unchanged 128-view float32 qualification, with the original exposure,
strands/pooling/source/tolerances and separately priced $3 proposal. No new attempt
or measured batching speedup occurred. Original full-bank workload is 508,763
parents, 2,470,549 views, 2,707,640 minimum chunks and 7.815 GB fixed-slot vectors.
Old-rate projection is about 61 GPU hours / $65–85 complete, **not** a current T4
forecast. Use measured stratum throughput before full-bank admission. Also resolve
the model-state transition: Oral has no admitted E031 hybrid checkpoint; shared
state/new zero-output GLM modules and own teacher/pairs/student need a tested
prospective extension, not silent reuse of a no-GLM checkpoint. No cutoff/subset
or feature-quality reduction was applied.

Skin remains unscored. Outstanding confirmation contracts include exact source,
genome/replicon/molecule/host/taxonomy joins, exact/near/pretraining overlap,
ambiguity and unique-versus-origin truth, genuine depth, unchanged prospective
protocol and separate compute/acquisition/retention admission. Existing local skin
payloads remain protected; no additional DNA is acquired here.

## Local storage and complete future cost

[Cleanup](../../experiments/E033-multiscale-bam/local-cleanup.json) removes 7.764 GB
of obsolete installer-cache logical bytes and 1.454 GB of SHA-matched expanded
wheel duplicates, about **9.217 GB logical** total. Retained E005 transfer archives
verify the duplicates. E005 allocated directory size falls from roughly 5.6 GB to
2.85 GB; workflow/mapping runtimes and all historical returned evidence remain.
Current numerical dependency bases, original source/data/models and failed logs
are protected. APFS clones/hardlinks and unrelated machine activity mean these are
not an exact physical-free attribution. A Boost-cache ENOTEMPTY cleanup failure
and its verified same-allowlist recovery are retained. No paid archive upload ran.

[The $20 / 36-hour proposal](../../experiments/E033-multiscale-bam/resources.json)
quotes about **$15.96** complete conservative attribution, including maximum VM
allocation, a conditional new 100 GiB task disk through seven days, 12 GiB WAN
export upper, new archive/tail, operations and contingency. It does not add the
original storage approval twice or assume a credit delta is an invoice.
Source/temporary sort/bank/model/archive coexistence is forecast at 34–55 GiB plus
the 25 GiB reserve; use a native largest-sample pilot before full release.

All 20 source BAMs total 94.85 GB. Stream Oral in-region, one sort at a time;
verify and reuse the two pilot summaries and remove only new verified sorted
copies. Original BAMs remain reusable. Full moment arrays are about 2.292 GB;
parent features and per-mode outputs are separately retained and deduplicated.
100 versus 64 GiB balanced adds about $0.24 per 48 hours; robust headroom is worth
that modest difference. Native cleanup may avoid the new disk, but old source
headroom and a 40 GiB task cannot simply be assumed sufficient. Preserve E032's
closed delivery tail before releasing that disk. Fresh quotas, credits/prices/
coverage/delayed usage and actual native pilot/whole-schedule/RSS gates remain.
No current $20 execution or resource action has been authorized in preparation.
Active retention ends **November 11 at 00:00 Copenhagen**; the approved automatic
tail ends November 18, with no further renewal implied.
