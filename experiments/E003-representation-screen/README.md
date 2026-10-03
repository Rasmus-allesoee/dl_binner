# E003: final frozen-GLM versus composition development screen

Prepared/completed: 2026-10-03. Execution: **completed**; scientific outcome:
**does not support GLM inclusion under the precommitted joint criterion**, with
positive grouping results retained. Sources/panel/settings were committed before
scores. [D011](../../docs/decisions/D011-first-binner-prototype.md) and the owner's
current instruction authorize this **final** bounded representation screen. Reuse
[E002](../E002-dnabert-s-feasibility/README.md); do not rerun its benchmark.

## Decision and scope

Question: do frozen DNABERT-S sequence features show enough additional useful
signal over inexpensive raw composition to merit inclusion in our first prototype?
This is **not a comparison against a contrastive-trained composition encoder**,
whole-genome/MAG recovery, unseen-species validation or strain-resolution testing.
Select one sequence route after this screen and move to implementation; no further
architecture gate unless a concrete implementation failure requires one.

The [configuration](config.json) fixes the joint keep criterion before scoring:

- Short (<2,500-bp) five-neighbor same-origin purity gain ≥0.10 absolute.
- Longer (2,500/10,000-bp) neighbor purity delta ≥−0.05.
- All-fragment base-weighted B-cubed F1 gain ≥0.05 absolute under the same fixed
  label-blind clustering procedure.
- Native extraction completes within its actual one-hour/8-GB ceiling, and the
  whole local workflow within two hours. Failure is operational evidence, not a
  negative biological result. Retain incomplete outputs; do not enlarge ceilings.

If all pass, include frozen GLM as the sole sequence representation feeding our
own learned head; do not automatically stack TNF or other architectures. Otherwise
use inexpensive composition in the first contrastive prototype and retain the
specific reason for deferral. These planning thresholds are practical effect-size
rules, not significance tests or guarantees. **Do not reject GLM solely on this
laptop's rough E002 bulk-runtime projections.** Record actual cost and assess
deployment scale later within implementation, without opening another selection
campaign. The species-aware pretrained model has an information advantage over
raw TNF; a positive result does not rank entire model families.

## Frozen sources and development panel

[Sources](sources.json) bind sixteen versioned public RefSeq chromosomes acquired
through NCBI EFetch, including corresponding GenBank accessions, DNA/file/metadata
hashes, actual organism/strain qualifiers and source references. Total chromosome
sequence: 37,671,129 bp. The panel includes related Rothia, Streptococcus,
Haemophilus and Neisseria species plus other oral/mucosal/skin-associated species.
One chromosome per species: no conspecific strain-resolution claim. This is a
heterogeneous selection of human-associated species, not a reconstructed community.
Most retrieved metadata omit host/isolation source; species association is distinct
from isolate provenance. The C. acnes KPA171202 culture-contamination origin is
explicit in the source record and is not relabelled a human isolate.

Primary context includes [human oral metapangenomics](https://pmc.ncbi.nlm.nih.gov/articles/PMC7739467/),
[S. sanguinis provenance](https://www.ncbi.nlm.nih.gov/bioproject/13942),
[N. gonorrhoeae FA1090 provenance](https://www.atcc.org/products/700825) and
[the C. acnes genome paper](https://doi.org/10.1126/science.1100330)/
[DSMZ culture record](https://www.dsmz.de/collection/catalogue/details/culture/DSM-16379).
Individual chromosome records own sequence/strain identities; association does not
prove every historical culture's original host.

No RefSeq/GenBank accession-stem match was found in the retained E001 contig
manifest. This limited audit does not exclude related taxa, version differences
or homologous DNA. DNABERT-2/DNABERT-S pretraining overlap is **not excluded**:
legacy genomes/species may have contributed to pretraining. The reviewed
[author repository](https://github.com/MAGICS-LAB/DNABERT_S) distributes large
sequence-pair training archives; no inspected accession-level exclusion list is
available here. Do not describe this as an independent test or download the full
training corpus for this bounded decision.

The [panel manifest](panel.json) freezes **320 fragments / 945,152 bp**: four
independent fragments at each exact 500/768/1,000/2,500/10,000-bp length per genome.
The [helper](../../scripts/e003_representation_screen.py) SHA-ranks disjoint 20-kb
chromosome cells, then chooses hash-derived within-cell offsets; no truth/model
score selects regions. Coordinates are zero-based half-open; chromosome wrapping
is not used. Opaque globally sorted IDs do not encode a genome label. All fragment
DNA/hashes/coordinates are retained; no augmented sibling is a neighbor.
There are no identical canonical-strand fragments, and three ambiguity bases are
preserved. TNF skips ambiguous fourmers; GLM unknown-token counts are recorded.
All fragments remain in the denominator, including zero/unassigned outcomes.
The five exact lengths sample the declared strata; they do not validate every
length within those ranges. No E001 fitting, thinning or eligibility is changed.

## Two representations and fixed evaluation

Raw TNF: independent 136-dimensional reverse-complement-collapsed fourmer frequency
implementation. No learned composition model, external kernel or coverage input.
Frozen GLM: reuse E002's hash-pinned author weights/custom code, read-only runtime,
CPU fallback, attended-token mean including specials, both-strand and bp-weighted
nonoverlapping ≤4,000-bp/1,024-token chunks. No model training, truncation, additional
checkpoint, quantization or architecture fusion. This remains our named chunk/
strand adaptation, not full-contig author-output parity.

For both spaces, column population z-score (drop constant dimensions with sd≤1e−8)
then row L2 normalization, learned without labels. Statistics use the whole panel:
this is transductive development, not training/test separation. Preserve zero raw
rows as invalid/noise. Exact cosine five-neighbor queries exclude self, tie-break
by opaque ID. Build a positive-weight mutual-five-neighbor graph and run
[NetworkX 3.4.2 greedy weighted modularity](https://networkx.org/documentation/networkx-3.4.2/reference/algorithms/generated/networkx.algorithms.community.modularity_max.greedy_modularity_communities.html)
at resolution 1, with default unrestricted community count (`best_n=None`), keeping
communities of size ≥3. Isolated/smaller communities are unassigned. There is **no
oracle species count, truth-selected setting or tuning grid**. Geometry writes its
partition before the separate score rule reads truth.

Report all length points, pooled short/long and all-fragment results. Primary
neighbor purity averages same-origin matches/5; missing neighbors count zero.
Balanced genome/length sampling makes the short mean an equal-genome mean.
B-cubed precision per fragment is same-origin fragments in its predicted group /
group size; recall is same-origin fragments in that group / all 20 sampled origin
fragments. Unassigned fragments contribute zero to both. Average P/R then take
their harmonic mean, with ordinary and bp-weighted means separately. These are
**sampled-fragment grouping** metrics; denominators are not complete genomes and
no AMBER/R95/HQ/NC recovery claim is made. Retain all assignments and neighbors.

## Execution and resource contract

[Snakemake workflow](../../workflows/e003-screen/Snakefile): TNF and GLM extraction,
one partition per space, then scoring. Local executor, serial jobs=1, cores=4,
mem_mb=8000, per-rule thread/OpenMP/BLAS limits four; Torch interop=1, loader
workers=0 and tokenizer parallelism off. E002 environment stays unchanged and
read-only; Snakemake coordinator uses the existing local 9.16.3 installation,
with inventory retained. No UCloud run. Setup/acquisition is recorded separately
from supervised scientific workflow time.

Each rule has a captured log and extended benchmark. Nested GLM supervisor enforces
one hour and the outer supervisor two hours, each monitoring RSS/CPU descendants
and stopping at 8,000,000,000 bytes. Fatal failure stops dependent scoring promptly.
The total cap includes the coordinator; sampled CPU and four-thread wall budget
are local observations, not billed vCPU-hours. Outputs/failed attempts remain in
ignored `artifacts/e003-representation-screen/`; raw/model data are never staged.

The protocol/code/manifests were frozen in source commit
`356df725a16375a81b686d867ce5d67c6c57bc1a` before this executed scientific command
(provenance only; **do not repeat the accepted run**):

```sh
env -u PYTHONPATH -u PYTHONHOME -u PYTHONUSERBASE PYTHONNOUSERSITE=1 \
  artifacts/d011-dnabert-s-spike/env/bin/python scripts/e003_representation_screen.py \
  --mode run --config experiments/E003-representation-screen/config.json \
  --output artifacts/e003-representation-screen/run-001
```

Fresh output directory required. Native progress/resource receipts are in
`run-001/glm-monitor/terminal.log` and `resources.jsonl`; aggregate workflow output
is `run-001/terminal.log`. No repeated E002 benchmark or new warmup campaign.
The completed-directory dry-run schedules nothing. Do not invoke the fresh driver
there again. Accepted native extraction is not repeated for analysis.

## Accepted run and independent review, 2026-10-03

`run-001` completed without a scientific failure/retry. All five computational
rules ran on real inputs; no worker/model/clustering/scoring path was mocked.
[Observed record](observed.json), [all-stratum metrics](metrics.tsv) and
[retained-file hashes](retained-files.json) bind the result to source/config/input/
model bytes. The E002 runtime and author model were reused read-only; its accepted
inference benchmark was not repeated. A documentation-only D011 milestone draft
was written during execution; the scientific producer, workflow, configuration,
sources and sampling match the committed source exactly.

[Independent retained-output review](review_retained.py) verified all source
FASTA/XML hashes, source-to-fragment coordinates and hash sampling, nonoverlap,
opaque ordered IDs, five length points and all 320 outcomes. Arrays are finite,
nonzero 320×136 TNF and 320×768 GLM. No evidence-zero row was dropped. Independent
fourmer counting agrees exactly with retained TNF; independent standardization,
cosine neighbor ordering, graph edge counts and full-denominator per-fragment/
aggregate scoring agree within 1e−12. No new communities were fitted. GLM receipts
verify frozen weights, four numerical threads, interop one, loader zero, contiguous
≤4,000-bp chunks covering every fragment and token limits. Three retained ambiguity
bases produced six unknown tokens across both strands. No truncation/exclusion.

| Fixed outcome | Raw TNF | Frozen DNABERT-S | GLM−TNF |
| --- | ---: | ---: | ---: |
| Short five-neighbor purity | 0.57396 | 0.45938 | −0.11458 |
| Longer five-neighbor purity | 0.64844 | 0.65313 | +0.00469 |
| All bp-weighted grouping B-cubed F1 | 0.30801 | 0.37664 | +0.06863 |
| Short grouping B-cubed F1 | 0.01978 | 0.32558 | +0.30580 |
| Short assigned fraction | 0.06771 | 0.91146 | +0.84375 |
| All unassigned fragments | 209 | 40 | — |
| Accepted communities (count was not supplied) | 14 | 19 | — |

**Interpretation:** GLM clearly improved sampled-fragment grouping and assignment
under this fixed clusterer. Better TNF short-neighbor purity did not translate to
better grouping: the mutual-neighbor graph stranded most short TNF fragments.
Assignment alone is not accuracy; B-cubed penalizes mixed/incomplete groups and
counts noise as zero. This mixed result demonstrates why neighborhoods and final
groups must be reported separately. It does not make raw TNF a uniformly better
binner, nor establish that contrastive training will fix its grouping deficit.

The joint rule required a short-neighbor gain of +0.10; the actual −0.11458 fails.
Long-neighbor tolerance and the +0.05 bp-weighted F1 gain both pass, as do actual
operational ceilings. **Follow the precommitted decision: defer frozen GLM from
the first prototype and use 136-dimensional composition for our own compact
contrastive encoder.** This is a conservative product choice under the stated
joint criterion, not a rejection of GLM as a family. Its grouping advantage is
substantial counterevidence to a blanket TNF preference. Do not change thresholds
or tune this clusterer post hoc. Cost/projection alone did not cause deferral.

## Actual cost, retention and verification limits

On the same Intel i5-1038NG7 / 16-GiB Intel Mac as E002, the serial four-thread
workflow took **940.014 s (15 min 40 s)**, with **1,435,561,984-byte** sampled peak
subtree RSS and 3.395 sampled average CPUs. GLM supervision took 933.751 s with
1,374,109,696-byte peak and 3.270 average CPUs; the native per-fragment extraction
clock records 920.299 s. Whole workflow four-thread wall budget: 1.04446 thread
hours, **not billed UCloud core-hours**. No HPC execution or proportional CPU
scaling inference follows. Setup/source acquisition/review are outside these
scientific clocks; this is not total project labor or spend. Memory is sampled,
not an exact high-water mark. Subtree CPU counters can miss terminated children;
they are observations rather than exact total CPU time.

Retain per-rule extended benchmarks, but their local RAM and `cpu_time` fields
are zero/unavailable and GLM `cpu_usage` is unsuitable as a percentage. These are
not evidence of zero usage. The independent supervisors above own resource
interpretation; do not rerun inference merely to repair benchmark reporting.

At acceptance, the ignored E003 directory holds **98 files / 41,338,995 bytes**
(41.34 MB), including source chromosomes/XML, panel FASTA, both feature caches,
partitions, scores, command/progress/resource logs and preflight attempts. No new
model/environment copy was made. These are local retained files, not a remote
backup; preserve them. Versioned source URLs/hashes support reacquisition, and the
committed source/pins support reconstruction if loss forces it. Normal analysis
and the next milestone must reuse accepted caches, not reconstruct them.

Five focused tests passed: independent TNF/strand/ambiguity counts, label-blind
geometry/ties/noise, full-denominator metrics, joint thresholds and safe nested
process cleanup. The initial cleanup test had an incorrect Popen exit-status
assertion after psutil reaped the child; it was corrected before execution and
the prior log retained. Initial dry-run sandbox cache access was resolved before
execution using the explicit workdir cache. Neither was a failed scientific run.
The completed-workdir dry-run confirms all valid stages are skipped. Independent
native retained-array review above uses no mocks. Linux runtime remains untested;
E002's unchanged extraction contracts supply pooling/strand/cache parity evidence.

This closes the final bounded screen. Pretraining overlap remains unexcluded,
the panel is transductive development, and grouping is not whole-MAG recovery.
No comparison with contrastive-trained TNF has occurred. Proceed to
[D011's first end-to-end implementation](../../docs/decisions/D011-first-binner-prototype.md#exact-next-milestone-first-learned-binner),
keeping the raw control, all short strata and noise outcomes; no further architecture
gate unless a concrete failure requires one. E001/H001 status is unchanged.
