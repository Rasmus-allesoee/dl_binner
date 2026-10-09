# Competitive binner study and benchmark-data assessment

Date/cutoff: 2026-10-08. Scope: a focused update of the completed
[September review](2026-09-30-binner-design-review.md),
[source audit](2026-09-30-design-source-audit.json) and
[architecture reassessment](2026-09-30-architecture-reassessment.md).
Study the owner's seven ranked interests for an assembly-based human-associated
binner, including transferable long-read ideas. This is not a new exhaustive
literature search, numerical headline-claim audit or executed tool comparison.
The ignored `benchmark_tool_study_guide.md` is advisory; its hash is in the
[new provenance record](2026-10-08-competitive-study-provenance.json).
[D013](../decisions/D013-first-comparative-benchmark.md) owns the decision;
[E009](../../experiments/E009-competitive-benchmark/README.md) owns prospective execution.

2026-10-09 amendment: [targeted input/runtime reconciliation](2026-10-09-e009-contract-reconciliation.md)
resolves the supplied GSA assets, includes COMEBin, names CompleteBin max-50,
resolves DCVBin payload availability/CPU exclusion, and revises budget/storage.
The October 8 source interpretations below remain a dated review snapshot;
current execution choices belong to amended D013/E009.

## Evidence reused and refreshed

The earlier review covers independent CAMI, Han, Arangasamy, Kim and MAG-E
benchmarks. Their assembly/platform/version/quality differences preclude a
universal ranking. The thesis's CompleteBin advantage receives weight, with its
historical GPU recipes and duplicate-claim repair explicit. E001's similar
VAMB/COMEBin neighbor purity but very different recovery implicates downstream
decisions as well as representation. E004/E005 show mixed learned utility;
software acceptance did not establish superiority or independent MAG recovery.
E003's GLM grouping gain and short-neighbor loss remain positive and negative
evidence, not a trained-TNF comparison. Nothing accepted was rerun.

Direct refresh: official CAMI pages, download/subject manifests, object HEAD
metadata, the small coverage archive, and eight author repository commit APIs.
Read relevant source paths across all seven tools; new MetaCAT paths received
deeper inspection. Fetch current CompleteBin/SemiBin files separately, preserving
reference caches. Source versions and inspected byte hashes are recorded in JSON.
CompleteBin's current core model/trainer/binning files match the earlier audited
bytes; its CLI/README need the current recipe. SemiBin's current source is newer
than our original clone. No package, model, database, DNA/read archive or native
tool was installed or executed for this task.

Publication qualifications: SCGBinner is the September 2026 preprint, with
long-read emphasis and some reported short-read transfer; independent confirmation
is limited. CompleteBin's reviewed manuscript remains a preprint/versioned source,
not a newly verified journal result. DCVBin's May 2026 journal methods were refreshed.
MetaCAT's September 2026 journal record/abstract and author source/documentation
were reviewed; direct publisher full-text access failed, so no claim of a complete
new MetaCAT manuscript/supplement audit is made. LorBin, COMEBin and SemiBin2
primary-paper interpretations are reused from the completed review. Source
inspection establishes behavior, not CPU runtime or biological performance.

## Separate information, objective, network and downstream decisions

| Method | Information and representation | Learning objective / pair construction | Clustering, selection and refinement | Implication and important limitation |
| --- | --- | --- | --- | --- |
| Our accepted dev3 | Whole-contig 136-D TNF; optional explicit log-transformed mean depths; compact 128→64 MLP | Twenty-epoch NT-Xent; two feature-masked views of the same contig; other IDs are negatives | Exact cosine mutual 5-NN, positive edges, greedy modularity, minimum three contigs; no markers | Small working control. Feature masking does not teach invariance between different genomic windows. Co-genomic negatives and fragmentation are plausible failures; neither is established causal. Exact neighbors still require quadratic work despite bounded query memory. |
| **SCGBinner** | TNF plus mean/variance coverage, separate coverage/combined MLPs, six actual contig-fragment views | Standard contrastive batches interleaved with same-SCG batches; the average of other views is the positive; same-SCG contigs supply biologically motivated hard negatives | Leiden candidate partitions and marker-based selection outside the encoder too | Same single-copy gene on distinct contigs usually indicates different genomes, not a positive link. Multicopy genes, fragmented hits and sparse short-contig markers weaken that assumption. Marker-guided training does not eliminate all random false negatives. Main evidence is long-read; measure marker availability on our short-read assembly. |
| **CompleteBin** | Global/local TNF context tokens, coverage mean/variance and coverage-weighted composition; Transformer plus optional frozen taxonomy-pretrained branch | Dynamic multiview contrastive training; current code softens suspected false negatives using high-confidence taxonomic class agreement after warmup | Staged Leiden clustering, marker-based decisions, polishing/dereplication | Context, pretraining, objective and refinement all change together. It is not simply a large raw-DNA DNABERT backbone. Taxonomic agreement does not prove identical strain/genome. Current code can automatically disable pretraining and alter eligibility/epochs: retain those decisions before attributing a win to a GLM. |
| **DCVBin** | Paper: domain-adapted DNABERT-S semantic vectors fused with TNF through a VAE. Inspected wrapper additionally consumes BAM-derived abundance | Paper: three-epoch continued backbone pretraining using same-long-contig windows, then VAE fusion; released wrapper's ordinary path does not establish that full recipe | SCG-estimated K and KMeans, rather than truth K | Genuine sequence-context candidate, but not an established coverage-free product. The wrapper filters ≥2 kb, truncates tokens, uses interactive environment setup/hard-coded CPU counts; weight availability and paper/code parity remain unresolved. A frozen GLM + our contrastive head is a different, cheaper proposed experiment. |
| **MetaCAT core** | TNF and BAM-derived coverage mean/variance; length-dependent composition probability and coverage affinity models | No neural contig encoder required by the inspected core; biological seed constraints | SCG seeds; multiple affinity weights; label propagation/recursive decomposition; conditional sparse weighted Dirichlet-process Gaussian mixture model (SWDPGMM); marker scoring | A strong counterexample to assuming a new network is the necessary fix. Mixture machinery is conditional, not always active. CPU engine is explicit. CheckM2/GTDB-Tk/host association are optional later commands, not core-binning prerequisites. |
| **COMEBin** | TNF and local mean/variance depth for original plus five sampled sequence views; coverage/combined MLPs | Multiview contrastive identity/separation learning | Native 120-candidate grid and SCG selection | Strong directly measured E001 comparator; both realistic views and downstream selection are credible leads. Expensive CPU execution/retention here argues against automatically running its full grid again at much larger scale. E001's selection gap is not an implementable truth-free selector. |
| **SemiBin2** | Whole/split-contig composition and abundance; compact Siamese MLP | Same-long-contig split positives and sampled different-ID negatives; margin pair loss, native 15 epochs | Short-read Infomap graph combining learned/raw/coverage evidence, followed by marker-seeded reclustering; separate long-read DBSCAN path | Strong practical short-read baseline. Split positives are a coherent inexpensive augmentation; random negatives still can be co-genomic. Native clustering can succeed where our small modularity graph fragments. |
| **LorBin** | Composition/abundance VAE | Reconstruction; useful novelty is substantially downstream | Adaptive distance/BIRCH/DBSCAN candidates and learned quality/keep decisions | Study refinement/uncertainty tradeoffs without equating a quality model with calibrated assignment confidence. Long-read emphasis, extra model assets, hard-coded neighbor jobs=10 and DBSCAN jobs=8 require operational review. Not first-wave execution here. |

Source anchors: SCGBinner `simclr.py:info_nce_loss/train_addpretrain`,
`train_CLmodel.py:main`, `run_scgbinner.sh`; CompleteBin `Model/model.py`,
`Trainer/trainer.py`, `Trainer/debiased_loss.py:build_same_genome_mask`,
`Trainer/optimized_debiased_loss.py`, `Binning_steps.py`, `cli.py`;
DCVBin `bin/my_method.sh`, `scripts/featureExtract_gpu_2.py`,
`scripts/myCluster_2.py`, `myvae/mainfiles/myencode.py`;
MetaCAT `cluster.py:main`, `semi_supervised_model.py:seedModel/sequenceModel`,
`score_model.py`, `kmer_frequency_model.py`, `coverage_model.py`;
COMEBin and SemiBin source anchors in the reused audit; LorBin `lorbin/cluster.py`.
The JSON binds these paths to actual bytes; no upstream algorithm is vendored.

## Focused improvements worth testing after the baseline

These are hypotheses and proposed ablations, not components approved for implementation.

1. **Real sequence-view positives and better negatives.** Our same-vector masking
   and all-other-ID negatives are weaker biological contracts than split-window
   positives. SCG hard-negative batches or confident false-negative softening
   solve different problems. Start with one mechanism, preserve the encoder and
   clusterer, and test short-contig damage as well as long-contig gains. Do not
   combine marker batches, taxonomy masks and a new encoder in one first change.
2. **Genome-scale grouping and conservative refinement.** If embeddings separate
   origins but native bins fragment or mix them, assess one marker-guided
   grouping/splitting step using retained embeddings. Markers supply biological
   information, not ground-truth K. Measure with independent sequence truth,
   preserving marker-negative contigs and all discarded DNA. A marker-selected
   bin count alone cannot validate the step.
3. **Context/frozen GLM information for short contigs.** CompleteBin's context-TNF
   tokens and DCVBin's raw-DNA semantic features are distinct routes. Keep the
   planned TNF / frozen-GLM-head / hybrid comparison, matching objective, depth,
   eligibility, head capacity as far as possible, clustering and budgets. Test
   bin quality and cost, not just neighbor purity. Frozen GLM inference/cache
   cost is separate from cheap head training; local E002 projections are rough,
   not a veto. Backbone adaptation is a later additional variable, not included
   in that three-way screen.

Before choosing which to implement, use E009's raw/learned and sequence/depth
controls plus stage diagnostics. A whole-tool ranking cannot isolate a causal
ingredient. If representation and grouping both fail, pre-register one small
ablation, not an automatic architecture campaign. Retain serious alternatives:
stronger composition views/objective, marker-aware grouping, context-TNF attention,
frozen species-aware features, and graph information if an actual assembly graph
later addresses observed ambiguity. No new model family wins by release date.

## Dataset assessment at this cutoff

| Source | Truth, terms, overlap and scale | Decision |
| --- | --- | --- |
| **CAMI II Toy HMB** | Official page: 49 samples across five body sites, 245 Gbp per read technology, 2017 RefSeq/HMP source community. GI supplies E001/E002/E005 development; E005 is four genomes from that same GSA. Other sites are new samples but may overlap reference genomes. Public toy use is unrestricted per CAMI FAQ. Simulator BAMs are source-genome mappings. | Reuse healthy runtimes/evaluators and accepted GI evidence; do not rerun GI as independent evidence. Another site remains a useful later domain test, not the first choice merely because its plumbing is familiar. |
| **CAMI III Toy Longitudinal Human Gut** | Public toy data from published genomes; 20 samples, ten subjects × two time points; 100 Gbp each short/long modality. Corrected subject table maps sample 0/1 to S1. Download lists supply GSA/contig-truth artifacts and source genomes; no verified read-derived assembly/truth pair was found in this inspection. Public-source pretraining/database overlap is possible. | **Choose S1, short reads, assemble sample 0 once and map both 0/1 to it.** New sample/source release and realistic assembler errors; a documented derivative, not an official whole-dataset score. Leave other subjects unconsumed by this milestone. |
| **CAMI III active Longitudinal Human Gut challenge** | Thirty-six samples, nine subjects × four time points, 180 Gbp per modality; contains unpublished genomes. Official schedule lists assembled data on 2026-10-15, after this cutoff. Access requires registration/participation; pre-release use/redistribution is restricted. No local public scoring truth verified. | Defer as a later genuine challenge/holdout opportunity. Do not use restricted challenge data for this product-development task, submit results or assume a scheduled release has occurred. |
| **Custom CAMISIM** | Complete controlled truth and configurable strain/coverage interventions; genome choice and simulator/source overlap still matter. Current author code is Nextflow-based 2.0; old thesis recipes are a different version. Simulating and assembling new communities adds cost and ecological assumptions. | Defer until an observed error requires a controlled strain, coverage or chimera mechanism test that public data cannot answer. Not needed for the first comparative assembly baseline. |

Official source pages:
[toy III](https://cami-challenge.org/datasets/toy-human-gut/),
[toy II HMB](https://cami-challenge.org/datasets/toy-human-microbiome-project/),
[challenge](https://cami-challenge.org/cami-iii-challenges/),
[schedule](https://cami-challenge.org/schedule/),
[data policies](https://cami-challenge.org/faq/),
[CAMISIM](https://github.com/CAMI-challenge/CAMISIM).
Toy access policy is not permission to relicense source genomes/model assets.
Metadata refreshed locally because some web-reader dataset pages failed.

Direct metadata observations: sample 0/1 read objects are 4,866,106,604 and
4,866,087,028 bytes: **9.732 GB compressed together**. The full source archive is
3,202,310,417 bytes; pooled anonymous short-read GSA is 1,308,005,894 bytes and is
not the proposed input. HEAD multipart ETags are object identities, **not verified
MD5/SHA256**. No large payload checksum has been verified yet. The small
`coverages.tar.gz` was downloaded/hashed/inspected: twenty two-column files map
source-genome filenames to simulated coverage, **not observed contig × sample
depth**. Samples 0/1 contain 311/332 listed genome filenames, 355 in their union;
counts include non-target biology and are not assembled/identifiable-genome counts.

## Overlap and truth qualifications

New subject and benchmark release do **not** establish unseen-genome independence.
E005's five accessions/four genomes and E003/E004's sixteen chromosome records are
recorded in the provenance JSON, along with the all-length retained E001 accession
universe. The selected toy III name list contains another **S. mutans** strain;
E003 used UA159. This establishes species-level overlap, not exact sequence identity
or unseen-strain transfer. Genome filenames do not resolve accession/sequence
identity. Exact accession, chromosome/plasmid, canonical DNA-hash and near-genome
overlap remain pending source-archive inspection. Compare with all development
sources, including E002 timing inputs and E005/E006 real smoke DNA, before scoring.
Unknown pretraining inventories for CompleteBin/DNABERT-S and reference-derived
marker/probability models remain explicit; do not demand impossible exclusion
assurances or call them clean unseen-genome evaluation.

Keep the complete community and report overlap/near-overlap strata; do not remove
known genomes after results or invent independence from different IDs. If exact
overlap exists, E009 remains an independent *sample/assembly* assessment with
development-genome overlap, not an independent genome-generalization test.
Because its errors will guide design, **E009 becomes development evidence after
inspection**; further claims need prospectively untouched data.

Read-derived assembly truth requires competitive source-reference alignments and
query/reference interval accounting. GSA origin maps cannot be applied to MEGAHIT
IDs. Reuse AMBER on a validated uniquely attributable contig view, plus conservative
interval-based whole-reference recovery including ambiguous/chimeric/unmapped DNA
in purity denominators. Do not relabel E005's exact-GSA confirmed R95 as whole-MAG
quality. MetaQUAST is an established alignment/misassembly source; MAG-E is relevant
but its default isolate-only evaluation and project/simulation API require an input
audit before adoption. Prefer a narrow tested adapter over replacing our evaluator
or installing a complete new simulation framework.

Primary method/evaluator locators:
[SCGBinner](https://github.com/htaohan/SCGBinner),
[CompleteBin](https://github.com/zoubohao/CompleteBin),
[DCVBin methods](https://doi.org/10.1093/bib/bbag241),
[MetaCAT paper](https://doi.org/10.1038/s41564-026-02472-7) and
[source](https://github.com/liu-congcong/MetaCAT),
[COMEBin](https://github.com/ziyewang/COMEBin),
[SemiBin2](https://doi.org/10.1093/bioinformatics/btad209),
[LorBin](https://doi.org/10.1038/s41467-025-64916-8),
[AMBER](https://github.com/CAMI-challenge/AMBER),
[MetaQUAST](https://quast.sourceforge.net/metaquast.html),
[MAG-E](https://github.com/korem-lab/MAG-E).
