# E009 input, shortlist and native-contract reconciliation

Date/cutoff: 2026-10-09. This is a targeted amendment to the completed
[competitive study](2026-10-08-competitive-binner-study.md), not a broad review
restart. D013/E009 own execution choices. Direct asset/code observations are in
[the inspection receipt](2026-10-09-e009-asset-inspection.json), selected runtime
and payload identities in [native locks](../../experiments/E009-competitive-benchmark/native-lock.json).
No E009 fit, quality score, architecture comparison or UCloud execution occurred.

## CAMI assets: why a new assembly is necessary

The [official toy page](https://cami-challenge.org/datasets/toy-human-gut/)
links sample-0 `contigs` and `gsa`. Both complete compressed objects were downloaded
and SHA256 checked locally: 289,486,065 and 136,958,228 bytes. `contigs` contains
`anonymous_gsa.fasta.gz`, named `gsa.fasta.gz` and `gsa_mapping.tsv.gz`; `gsa` contains
311 per-source GSA files, including two empty files. All nonempty collections have
665,738 records / 422,673,293 bp. An independent sorted DNA-hash multiset comparison
matches **all three** collections, despite different headers/order. This is stronger
than inferring an assembly type from a URL or matching only lengths.

The origin map has 665,738 rows, 309 nonempty genome labels / 6,408 replicon IDs,
and source taxonomy, interval endpoints and read counts. Its provider coordinates
are one-based inclusive (end-start+1 equals length); our new PAF adapter uses
zero-based half-open coordinates. The per-source headers name exact source spans,
for example `NZ_..._from_1476_to_1722_total_247`. CAMISIM's inspected Nextflow
`sample_wise_simulation.nf` calls `bamToGold.pl` on simulation-to-source BAMs;
`shared/anonymization.nf` copies the anonymized GSA and origin mapping into the
contigs directory. Exact CAMI producer commit/run arguments are not supplied;
this source explains the observed layout, not proof of their exact job SHA.

**Decision:** these are gold-standard reference reconstructions, not a traceable
de novo assembly. Keep MEGAHIT 1.2.9 on full sample-0 reads with its explicit 200-bp
emission floor. The GSA minimum is 149 bp and 544,093 records fall below 500 bp;
this does not predict actual assembler sizes or permit filtering truth denominators.
Each binner's separate native eligibility, all six strata and all rejected/noise
DNA remain accounted for. No simulator coverage is used as measured contig depth.

## Native shortlist and CPU preparation

| Tool | Prepared E009 role/configuration | Operational evidence and remaining limits |
| --- | --- | --- |
| SemiBin2 | Native short-read self-supervised, 15 epochs/default selection | New source pinned; full imports and actual whole/split feature writer checked in owner preflight. No environment-specific pretrained model requested. |
| MetaCAT | Native core, CPU SWDPGMM; no optional CheckM2/GTDB-Tk | Seven worker slots plus coordinator at the 8-CPU preflight; affinity completes before LP tasks and score workers wait for LP. Native C reader, coverage order and marker writer need Linux. |
| SCGBinner | Native six-view/200-epoch schedule and marker-guided selection | Replace two removed `np.int` aliases only in the source-pinned E009 copy; actual reader passed locally. Cap host-wide marker/selection pools and HNSW defaults; loader zero. No full fit/grid validation claimed. |
| COMEBin | Native six-view/200-epoch schedule, 120-candidate grid and marker selection | E001 measured recovery/cost reused. Current source requires a BAM directory and sorts resolved paths; alias names cannot guarantee order. Real small native augmentation/coverage arrays are tested separately from Linux full imports. |
| CompleteBin | **Modified max-50**, all other native automatic decisions retained | Verified DB archive/state dictionary, real BAM coverage writer and CPU forward. Small/large scheduler resolves 50/50/35/39 in actual source; no full fit. |

All source archives, required marker HMMs, selected CompleteBin checkpoint/database,
Linux bootstrap and small extra wheels have size/SHA identities. The standalone
Linux utility recipe was solved without installing/executing Linux packages:
59 package URLs / 227,985,534 download bytes with SHA256 and MD5 locks. The first
cross-platform solve lacked a simulated glibc virtual package; the next found an
unused Galah/dashing–modern-zlib conflict. Galah is omitted from this exact-accession/
sequence catalog; source ANI interpretation remains separate. The final solve is
not runtime validation. Linux must satisfy glibc ≥2.28 and pass actual contracts.

Five new E009 prefixes borrow accepted E001 numerical distributions read-only,
with complete inventories/origins and byte checks. SemiBin owns pinned numexpr/
argcomplete additions; CompleteBin owns psutil. Mapping, AMBER and the accepted
CheckM payloads remain read-only and byte-bound. No installer upgrades old prefixes.
All Python children use lexical `-I -B` interpreters, including the owned CheckM
entry wrapper. Short `/tmp` paths avoid historical AF_UNIX socket-length failures.

Numerical phases use the requested CPU allocation with loader zero. Multiprocess
phases use N-1 worker slots, serial BLAS and a coordinator. CompleteBin uses N-2
coverage/BGZF budgets including main/coordinator. HMMER's `--cpu` counts additional
workers: an owned audited wrapper translates a per-process total of W to W-1,
including `--cpu 0` for a one-CPU process. Thus several `--cpu 1` HMM jobs do not
silently become two active CPUs each. MetaCAT uses this explicit external HMM
path instead of its bundled binary. CPU affinity bounds the complete Linux tree;
returned native plans and sampled CPU/RSS must still be inspected. Serial/I/O
phases need not saturate every CPU and tiny inputs do not prove scaling.

CompleteBin's only scientific source patch changes `train_epoch >200 -> >50` and
assignment 200→50. Native effective sample count includes the sampler's 544×36
minimum step structure and the 115,000 threshold; N50 ≥1536 adds four base epochs.
The contrastive trainer runs that resolved loop, saving selected late checkpoints;
there is **no validation-loss early stop**. A separate extreme-overfit valve caps
at 150 and cannot increase the new 50 maximum. The S/O automatic pretrained-weight
decision uses capped epochs, so the cap can affect pretraining as well as duration.
Keep its actual outcome and resolved eligibility/epochs in future results. A thesis
loss plateau motivates the owner-selected cap but is not proof of equal final bins.
Label this configuration CompleteBin E009 max-50, never upstream/native parity.

## DCVBin: resolved availability, bounded exclusion

The [author code](https://github.com/dengdengf/dcvbin) and
[official Figshare article](https://api.figshare.com/v2/articles/30400258) expose
four parts of `DNABERT_S-main.tar.gz`, total 1,656,742,987 bytes, version 1, CC BY 4.0.
Supplier-computed MD5s/URLs are recorded. An 8-MiB first-part prefix exposes training
source and the 842,366,336-byte `furval_10k.csv`; full expanded storage/checkpoint
SHA/paper parity remain unverified. CUDA calls in both exposed training variants
are direct (`loss.cuda`, input `.cuda`, CUDA autocast). This is available payload,
not missing weights; no full 1.66-GB local acquisition is required for exclusion.

The basic wrapper prepares ≥2-kb contigs, chooses the **first** sorted BAM and runs
sequence features → TNF/RPKM → VAE → SCG-estimated K/KMeans. The encoder has a CPU
fallback, one-sequence-at-a-time inference, a 5,000-token truncation and no explicit
`model.eval()` in that extraction path. The VAE runner constructs `nsamples=1`
with default CUDA true and defaults to 200 epochs (four CUDA loader workers).
The enhanced recipe separately makes 10-kb windows from ≥20-kb sequences and
continues backbone training. Interactive environment paths, hard-coded 64/66-CPU
steps and CPU/pair-depth/CPT repairs need a separate validated adaptation.

**Decision:** exclude DCVBin from this bounded CPU execution shortlist. Five other
comparators cover the immediate whole-tool gap; adding an untested tool port and
backbone training is extra implementation, not a command-flag fix. Coverage is
useful input and receives no penalty. No inference from laptop speed, tool fashion
or this exclusion rejects GLMs or the future matched GLM-head/hybrid comparison.

## Product priorities and interpretation

Learned TNF + measured depth is the primary product comparison. The matched raw
arm and sequence-only pair are diagnostic controls: they locate losses in
information, geometry or grouping, without reopening whether the product should
learn or accept coverage. Their separate cap is 16 core-hours; primary/external
work receives most of the 700-hour prospective budget. COMEBin adds 192 hours to
the former stage sum: 664 +36 reserve =700. Owner balance is approximately 1,980,
leaving 1,280 outside this experiment; ceilings are not forecasts or automatic
retry permission. E001's successful COMEBin stages cost 39.6462 allocated hours,
with a 58.1075 recovery-sequence lower bound, not a prediction for the new assembly.

**High-priority controlled marker follow-up, not executed:** reuse the frozen
learned/raw embeddings and measured depths. Call one fixed bacterial/archaeal SCG
panel; retain gene/hit multiplicity, borderline fragments and all marker-negative
short DNA. Compare current grouping with one deterministic marker-conflict
split/compatible-merge refinement, keeping encoder/training/distance and all other
settings fixed. A duplicated single-copy family is a cannot-link clue, not proof
that any two distinct markers are positive links. Prespecify hit thresholds,
conflict/merge rules and one configuration before testing. Evaluate with independent
sequence truth and all-bin purity, not only the markers used to refine. Keep if
confirmed recovery improves at ≥95% purity without material short-stratum loss
or unjustified noise/CPU/storage growth; revise/defer if conflicts mostly reflect
fragmented/multicopy hits, sparse marker coverage or increased contamination.
Marker-aware training is a serious later alternative, not a simultaneous change.
This record gives the next controlled question; it does not freeze unmeasured
numeric refinement thresholds or alter the E009 baseline.

Our exact development accession/full-replicon hash inventory is committed;
partial/near-genome and historical pretrained corpora remain incompletely known.
Known related training/reference genomes and unknown inventories limit claims of
unseen-genome generalization. They are **not labels entering our evaluator's
feature/training path**, and an unavailable historical inventory alone is not an
automatic blocker. Freeze biological source classes/targets before future scores;
retain host, viruses and separately simulated plasmids as purity contaminants.

Truth uses all emitted qualifying minimap2 all-chain matches with exact PAF/CIGAR
coordinates and conservative ambiguity. Same-genome repeated loci may support
purity but not coordinate-union completeness; cross-genome competing segments
support neither. Native AMBER sees only ≥95%-attributable whole contigs with
original lengths. Full-reference and assembly-conditional denominators remain
separate, missing genomes remain zero, and duplicate DNA cannot inflate recovery.
Alignment-supported provided-reference recovery is not certified whole-MAG/MIMAG
quality, finished-genome completeness or independent clinical generalization.

## Preparation acceptance and unresolved boundaries

[Local validation](../../experiments/E009-competitive-benchmark/local-validation.json)
records actual native paths, versions, source/input hashes, failures and sampled
resources. Portable harness checks do not establish native Linux acceptance. Mac
MEGAHIT 1.2.9 four-thread crashes persisted in old and new builds; one-thread tiny
assembly works, with cause unresolved. The Linux packet must pass **eight threads**,
without silently switching to serial. No scientific community assembly is accepted.

The checksum-bound 8-vCPU/24-GB owner preflight acquires source DNA into owned
shared storage, inventories exact development overlap and exercises tiny native
readers/writers. It does not acquire bulk reads, fit communities or score E009.
Home is for code/new prefixes/transfers/logs; bulk DNA/BAM/temp uses only the owned
shared E009 subtree. The former 200 GB is provisioning, not a hard cap. Actual source
archive SHA and biological classification/near-overlap, bulk-read hashes, assembly
scale and full-schedule affordability still require returned/later evidence before
science. Review results before preparing the next bounded assembly command.
