# DCVBin efficiency and reliable cross-contig learning

Reviewed October 25, 2026. This is source interpretation and a workload estimate,
not a reproduced DCVBin performance, hardware or timing result. E022 owns the
candidate; this note owns external-source findings and future efficiency options.

## Sources and identity

The [journal article](https://academic.oup.com/bib/article/27/3/bbag241/8687202)
(DCVBin, DOI 10.1093/bib/bbag241, May 19, 2026), its publisher-linked supplement
retrieved through Europe PMC, and the independently rooted local DCVBin repository
were inspected. The source snapshot is **732ee4257f7da200994f4c105e9dacbc74242883**
(November 15, 2025). [Source bindings](../../experiments/E022-marker-informed-learning/external-sources.json)
include the relevant files, article XML and supplementary archive/TeX. The local
weight deletion and .DS_Store changes predate this review; inspected code matches
that commit. No weights were restored and no tool was executed. This older source
snapshot is not established identical to the published implementation or CPT
weights. Original papers and source caches are unchanged.

I could **not confirm a numerical runtime/hardware comparison** in the accessible
journal main text or its supplied supplementary TeX (Note 1, figures S1–S3). The
article explicitly acknowledges greater Transformer compute/GPU overhead than
pure k-mer methods such as MetaBAT2. Its recovery/quality comparisons do not prove
a speed advantage. The owner's concern remains valid; absence of a verified table
is a limit of this audit, not evidence that another version never contained one.

## What the inspected DCVBin path actually does

| Property | Inspected DCVBin extractor | Accepted E021 E009 bank |
| --- | --- | --- |
| Model eligibility | Contigs >=2,000 bp | Learner-eligible parents >=500 bp |
| DNA exposure | One whole-parent request, truncated | Exact parent plus available real crops; long views chunked |
| Strand exposure | One input orientation | Both orientations, pooled |
| Token limit | 5,000 tokens, truncation enabled | 1,024 tokens per chunk |
| Forward batch | One sequence | Two stranded sequences per chunk |
| Pooling | Mean last hidden states, including special tokens | Pinned strand/chunk pooling and reliability semantics |
| Storage | All retained sequence text/vectors held before stacking | Persistent exact-view frozen bank, reusable by CPU fits |

The [extractor](https://github.com/dengdengf/dcvbin/blob/732ee4257f7da200994f4c105e9dacbc74242883/scripts/featureExtract_gpu_2.py)
loops over individual contigs; it does not batch contigs or reproduce E021's crop
bank. The 5,000 limit is **tokens, not bp**. Truncating one long parent is different
from representing all of its DNA. Auto-CUDA selection is not measured throughput.
The ordinary shell pipeline also consumes BAM-derived abundance/RPKM, despite
sequence-focused paper framing. Its optional assembler/CheckM2 flags request many
threads; those requests are not charged-use observations. The CPT wrapper's Slurm
48-CPU/256-GB/four-GPU header is not proof that the single-device extractor uses
four GPUs. Optional continued-pretraining input generation materializes combinations
of 10 kb segments; that mode has extra cost and can grow quadratically per contig.
No numerical/backend/precision equivalence with E021 was established. Merely
omitting an explicit `eval()` after Hugging Face `from_pretrained` is not proof
that this source accidentally enables dropout.

## Same-assembly workload estimate

[Bound input counts](../../experiments/E022-marker-informed-learning/dcvbin-workload.json)
come only from accepted E009 lengths and E021 view metadata; no tokenizer/model
was rerun. Applying DCVBin's source cutoff would request **13,554** parents /
141,391,731 bp. E021 consumed **89,041** parents, **432,664** DNA views,
**465,059** chunks and **930,118** stranded sequence inputs (157,758,426 tokens).
That is 31.92 times as many views or 68.62 times as many stranded inputs, **not
an elapsed-time speed ratio**. Long-token attention, devices, precision, kernels,
CPT and pipeline boundaries differ. Native extraction took **4.1402 hours**;
GPU allocation including setup/admission/handoff was **8.2387 hours**. CPU learner
training was **19.51 minutes**. The approximate nine-hour experience must not be
reported as nine hours of neural training or compared directly with tool-only
minutes from different hardware/data/excluded stages.

There are **zero exact raw-view SHA256 duplicates** among the 432,664 E009 views.
Global whole-view hash deduplication therefore has no demonstrated savings here;
reverse-complement/chunk redundancy was not measured.

## Practical future options, ordered by evidence and cost

1. **Reuse frozen banks first.** E022 already uses the accepted E021 bank with no
   new GPU, DNA extraction or pretrained-model payload. A native prospective
   extraction forecast should state views, tokens, strands and allocation, not
   just assembly size or epochs.
2. **Engineer the existing math before changing information.** Length-bucket
   requests across views, reuse token IDs instead of tokenizing a chunk again,
   and stream compact arrays. These need actual GPU admission and unchanged
   numerical/pooling checks; batch changes can alter floating-point output. Do
   not call them accepted transparent replacements before testing.
3. **Declare a cheaper exposure treatment separately** if future data make full
   banks unaffordable: a >=2 kb/core-only prior, parent-only representation, fewer
   crops/strands or long-parent truncation can cut inputs dramatically, but
   change available information and short-DNA coverage. Retain short/marker-negative
   DNA through composition/context/recruitment and full denominators. Test one
   decision-relevant alternative, not a silent cache fallback or cutoff match.
4. **Distillation or a smaller prior** could amortize GPU work over many samples.
   It introduces another training/generalization/overlap question and is deferred.

No DCVBin run or new efficiency benchmark is justified in this preparation task.
Its native runtime recipe/weights would need separate verification. Current
priority remains reliable fragment links; GLM capacity is not demonstrated to be
our bottleneck, and cache reuse makes that experiment inexpensive.

## Marker source checks and limits

[SCGBinner's training source](https://github.com/htaohan/SCGBinner/blob/d5ad239af9a1445f0e454c4d4aa9307b922961a9/SCGBinner/simclr.py)
uses same-SCG batches as negative examples. [SemiBin2](https://pmc.ncbi.nlm.nih.gov/articles/PMC10311329/)
uses self-supervised fragment positives and random negatives. These support the
value of cross-fragment information; they do not validate every repeated-family
cannot-link in our assembly. E011/E012 directly found same-origin loci, panel,
replicon and duplication problems. E022 therefore requires strong complete calls,
measured parent-depth and composition context, protects near-identical proteins,
and keeps the original self-positive exposure. Reciprocal learned neighbors are
uncertain proposals, never certain same-genome labels. The exact rule/defaults
and alternatives are frozen in [E022 design](../../experiments/E022-marker-informed-learning/design.md).
