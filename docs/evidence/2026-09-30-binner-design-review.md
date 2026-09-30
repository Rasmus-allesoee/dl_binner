# Binner design review: scope and cutoff

Opened and completed: 2026-09-30. Scope was defined before architecture selection.

Interpretation update: the VAE-first synthesis below is superseded by the
owner-requested [architecture reassessment](2026-09-30-architecture-reassessment.md)
and revised D011. The completed source/benchmark review remains evidence; it is
not restarted. E001's cutoff is not a product length constraint.

Cutoff: publicly accessible papers, preprints, benchmark studies and source releases
available by 2026-09-30. Emphasis: 2023–2026 methods and 2024–2026 independent
benchmarks, with earlier foundational methods needed to interpret current designs.
Target: assembly-based bacterial/archaeal genome binning relevant to human-associated
microbiomes. Screen single/multi-sample, short/long/hybrid reads, sequence/coverage,
markers, taxonomy, assembly graphs, pretrained sequence models and uncertainty.
Screen viral, plasmid and eukaryotic methods as boundary/transfer evidence, not
interchangeable baselines. General read classification and foundation models with
no binning validation are outside the core comparison.

Search broad method/benchmark queries and named-method follow-ups; follow citations
and current author repositories. Review benchmark methods, populations, versions,
quality definitions and compute before comparing rankings. Reuse earlier local
papers/source snapshots, but refresh publication/version status. Source audit
shortlist is selected for empirical relevance, architectural diversity and practical
first-product implications, not only reported rank. Distinguish paper claims,
source observations and E001 measurements. Record inaccessible/newer artifacts as
gaps; no claim of proving that every unindexed preprint has been discovered.

## Completed review and evidence levels

Completed 2026-09-30 at the declared cutoff. This is a design review, not a
systematic meta-analysis or reproduction campaign. Methods/results sections of
cached primary papers, current publisher/preprint records, author repositories
and the source paths below were examined. Recent independent benchmarks receive
more weight than a method's own ranking. A source read establishes implementation
behavior, not execution success or performance. E001 is the only new measured
binning evidence in this review.

Search record: broad queries combined `metagenomic binning`, `deep learning`,
`benchmark`, `2025`, `2026`, `short long reads`, `graph`, `foundation model` and
`uncertainty`; named follow-ups covered every recent method in the matrix below,
publication versions and author code. Citation follow-up added GraphMB/CCVAE,
RepBin, UnitigBIN, MBGCCA, CLMB and PlasMAAG. Searches of recent benchmarks added
MAG-E and the 2025 CAMI portal. The final broad 2026 search on September 30 found
no additional decision-changing family beyond this scope. This is a discovery
record, not an invented count of screened database records.

The [source inventory](2026-09-30-design-source-audit.json) records repository roots,
local modifications, upstream commits queried at the cutoff and SHA256 for
inspected files. Current SemiBin and BBTools differ from our earlier cache;
selected current files were fetched into a separate ignored directory. No reference
cache, executed environment or E001 pin was changed. Earlier
[landscape](2026-09-16-landscape.md) and [targeted audit](2026-09-17-targeted-audit.md)
remain useful background but do not substitute for this refreshed review.

## What the benchmarks actually establish

| Primary study and inspected scope | Useful result reported by source | Constraint on our interpretation |
| --- | --- | --- |
| [CAMI II, Meyer 2022](https://doi.org/10.1038/s41592-022-01431-4), benchmark design and genome-binning results; [CAMI portal 2025](https://academic.oup.com/nar/article/53/W1/W102/8126258), evaluation/ranking methods | Public simulated truth exposes strain complexity; portal adds more recent submissions and several recovery/purity measures. | A GSA removes assembly error. Submission versions, ecosystems and denominators differ. Portal rankings are not a current head-to-head of every method. E001 modifies one HMP GI GSA and is development evidence. |
| [Han 2025](https://www.nature.com/articles/s41467-025-57957-6), methods and platform/mode/resource comparisons | Thirteen binners across seven combinations of short/long/hybrid data and binning modes on five real datasets; optimal choices depend on assembly and sequencing mode. | Real MAG quality is proxy-based; contiguity, RNA requirements and assembly mode affect rankings. Large CPU allocations and two-week timeouts do not establish our CPU cost. |
| [Arangasamy 2025, final article](https://doi.org/10.1093/bib/bbaf617), embedding classifier, native/common clustering, reassembly and resource results | GenomeFace's strong representations do not consistently yield best native bins. COMEBin/SemiBin2 are strong on real assemblies. Changing clustering or sample/coassembly mode can change the ranking. | Five-fold within-community classification is not unseen-community transfer. Common COMEBin clustering is not neutral for all representations. Use the final November article, not the earlier cached preprint's method list/ranking. |
| [Kim 2026](https://www.nature.com/articles/s41467-026-71521-w), custom/CAMI/real datasets, methods and chimerism | Strong neural binners can outperform older ensembles; depth, community complexity and sample count matter. GUNC exposes chimerism that quality counts alone miss. | Tested versions include VAMB 3.0.9 and COMEBin 1.0.4, not today's heads. The reported sample-count optimum is conditional. Simulation truth and CheckM2/GUNC real-data proxies must remain separate. |
| [Coleman/MAG-E 2026 preprint](https://doi.org/10.64898/2026.04.06.712906), simulation, pipeline and contig-level evaluation; [author code](https://github.com/korem-lab/MAG-E) | Gut simulations expose assembly, refinement and quality-filter errors. COMEBin/SemiBin2 have different precision/recall tradeoffs; shared contigs and prophages are difficult. Refinement is not automatically beneficial. | Not peer-reviewed at this review; one ecosystem/simulation construction. Supports end-to-end evaluation later, not replacing E001's fixed-population evaluator or generating another large simulation now. |
| [Mattock and Watson 2023](https://doi.org/10.1038/s41592-023-01934-8), single/multi-coverage contamination | Coverage mode can conceal substantial contamination behind quality estimates. | Does not mean one mode universally wins; assess actual assemblies and independent chimerism. Read with newer benchmark results, not as a blanket rule. |

Additional boundary screens: [Peng 2026](https://doi.org/10.1111/2041-210x.70306)
concerns short/long-read workflow choices; [nf-core/mag v5](https://academic.oup.com/bioinformatics/article/42/9/btag628/8770536)
shows current pipeline integration. Neither isolates the best learning objective.
CheckM/CheckM2, GUNC, AMBER and MAG-E answer different questions: proxy genome
quality, chimerism, known-origin assignments, and whole-pipeline recovery.
We should retain AMBER plus explicit denominators on known truth, and later add
CheckM2/GUNC on real assemblies. Selecting bins with markers and then reporting
only the same marker criterion is insufficient independent evaluation.

## Method families, inputs and reasons to keep or defer them

These are **source reports and design interpretations**, not reproduced performance.
The shortlist was chosen across plausible alternatives before selecting a prototype.

| Method / primary source | Information and learning/clustering mechanism | Implication for a first product |
| --- | --- | --- |
| [VAMB](https://doi.org/10.1038/s41587-020-00777-4) | Composition and multi-sample abundance compressed by a VAE; iterative density clustering without a truth-supplied genome count. Current code also models total abundance. | Coherent, small, CPU-practical reconstruction approach; no positive/negative-pair construction. E001 demonstrates affordability but materially lower recovery than COMEBin. Not a performance winner by default. |
| [SemiBin2](https://doi.org/10.1093/bioinformatics/btad209) | Siamese metric learning from split-contig positives and randomly sampled negatives. Removes the original SemiBin training requirement for taxonomic cannot-links. Short-read graph clustering/reclustering differs from its long-read DBSCAN path. | Strong serious alternative: direct neighborhood objective and shorter published training. Fragment coverage and false negatives remain concrete design contracts. Its self-supervised code uses margin contrastive loss, not a reconstruction loss. |
| [COMEBin](https://doi.org/10.1038/s41467-023-44290-z) | Six views of composition/coverage; contrastive MLP representation plus native candidate clustering and marker selection. | Strong benchmark/E001 recovery; expensive full workflow here. E001's CT oracle gap shows why a better encoder alone is an incomplete product plan. No evidence that copying its entire grid is necessary for a first tool. |
| [CLMB](https://arxiv.org/abs/2111.09656) | Noise-augmented composition/coverage and contrastive representation learning. | Robustness augmentation already has prior art. Perturbations need a biological/input rationale; not automatically a new reliability mechanism. |
| [McDevol](https://github.com/soedinglab/McDevol), author method/source | BYOL-style online/target networks, pretrained composition and augmented coverage counts, Leiden clustering. | Positive-only learning avoids explicit false negatives, but introduces teacher dynamics and collapse checks. Current implementation's sampling is Poisson despite the function name; do not infer a multinomial model from prose. |
| [TaxVAMB, 2026](https://doi.org/10.1038/s41587-026-03098-0) | Intrinsic features plus hierarchical taxonomy in a semisupervised multimodal VAE; partial labels supported. | Useful when reliable annotations exist, especially relevant to human data. Adds a taxonomy database, reference overlap and erroneous-label dependence. Not evidence that taxonomy is mandatory for v0. |
| [GenomeFace, 2024 preprint](https://doi.org/10.1101/2024.02.07.579326) | Pretrained composition and permutation-invariant abundance representations, followed by specialized clustering. | Strong representation evidence and reusable inference are attractive. Pretraining overlap, model assets and GPU-oriented clustering complicate CPU deployment. HMP-related abundance training makes E001 unsuitable as an independent transfer test. No journal replacement was verified. |
| [CompleteBin, 2025 preprint](https://doi.org/10.1101/2025.04.20.649691), cached v3 and current code | Fragment composition tokens, coverage and pretrained taxonomic information; Transformer-based multiview learning and staged clustering. | Targets shorter fragments, but E001 has no sub-2.5-kb evaluation. Larger model/assets and current debiased-loss implementation require separate recipe validation. Paper and latest code must not be conflated. |
| [SCGBinner, September 2026 preprint](https://doi.org/10.64898/2026.09.07.749871), author source | Adds single-copy-gene-informed batches to contrastive training and cluster selection; long-read emphasis. | Biological constraints can improve pair construction. Marker absence, multicopy biology and reuse of marker criteria in evaluation need independent truth checks. Very recent author evidence, not yet mature independent confirmation. |
| [LorBin](https://doi.org/10.1038/s41467-025-64916-8) | VAE representation plus adaptive multi-scale clustering and learned quality/keep decisions, aimed at long reads. | Shows innovation may lie after the encoder. Needs quality-model assets and validation in our target assembly regime; not a simple universally superior VAE replacement. |
| [DCVBin, 2026 journal article](https://doi.org/10.1093/bib/bbag241) | DNA-language-model embeddings fused with composition and VAE-based features, marker-informed clustering. | A serious pretrained-sequence option, but the inspected runnable path also requires BAM coverage/total abundance. Published-recipe parity and missing weight payload remain unresolved. Do not call it coverage-free. |
| [DNABERT-S, 2025 journal article](https://doi.org/10.1093/bioinformatics/btaf188) | Species-aware foundation embeddings trained using contrastive curriculum/mixup; demonstrated sequence-only clustering/binning. | Makes sequence-only learning a real alternative. Read-level/task-specific evaluations and reference training are not proof of end-to-end CPU practicality or assembly-bin quality here. Pretraining overlap must be audited before a generalization claim. |
| [UncertainGen, arXiv v1](https://arxiv.org/abs/2509.26116) and [k-mer antecedent](https://arxiv.org/abs/2411.02125) | Lightweight sequence composition models; UncertainGen predicts distributions and uses learned geometry to separate fragments. | Distributional embeddings are not calibrated coverage uncertainty. Code/runtime and independent benchmark confirmation remain gaps. No uncertainty head is justified merely by H001. |
| [GraphMB](https://doi.org/10.1093/bioinformatics/btac557), [CCVAE](https://openreview.net/pdf?id=id8OSRGeew) | Composition/coverage plus assembly connectivity; graph representation or connectivity constraints. | Assembly edges are extra evidence, but need real graph inputs and ambiguity handling. E001 GSA cannot test their benefit. Current GraphMB includes more than the original published path. |
| [RepBin](https://arxiv.org/abs/2112.11696), [UnitigBIN](https://openreview.net/pdf?id=vBw8JGBJWj), [MBGCCA](https://doi.org/10.3390/e27090921) | Graph/constraint/self-supervised alternatives; unitig or contig graphs change the input and evaluation contract. | Screened for family coverage; no new runtime audit. Additional graph dependencies and reconstruction of an appropriate evaluation dataset are not justified for the first milestone. MBGCCA full-text access was blocked; abstract-level screen only. |
| [QuickBin, August 2026](https://www.nature.com/articles/s42003-026-10782-z) | Indexed, staged composition/depth comparison with small neural similarity decisions; optional additional links. | Strong deployment alternative and comparator. Current optional length-aware depth likelihood means such a feature would not itself be novel. Published and newer development modes differ; strict proxy-quality rankings are not interchangeable with E001 R95. |
| [MetaBAT2](https://doi.org/10.7717/peerj.7359), CONCOCT, MaxBin2, MetaDecoder, binny, MetaBinner | Probabilistic composition/depth, mixture/graph/density or ensemble approaches; screened through primary methods cited by the benchmark studies and earlier evidence notes. | Essential non-neural/ensemble reference points. A wrapper or ensemble alone does not meet the owner's goal of implementing a learned binner. MetaBAT's native filtering cost under CT is directly observed in E001. |

CoCoBin (2025 preprint; [author manuscript](https://doi.org/10.1101/2025.08.27.672549))
adds separate feature-graph learning; it does not remove the need to justify their
fusion. DAS Tool, MAGScoT, Binette and BASALT-style refinement are downstream
selection alternatives, not evidence for a particular encoder. BIgMAG/MAGFlow is
an interactive quality workflow rather than a distinct first encoder. Boundary
methods include [PlasMAAG](https://doi.org/10.1038/s41587-026-03005-7), which combines
assembly/alignment graphs with a contrastive VAE for cellular/plasmid reconstruction,
and [REMAG](https://doi.org/10.64898/2026.03.05.709928), aimed at eukaryotic recovery.
Their target biology and partition/quality contracts differ from our prokaryotic v0.
They establish alternatives, not required modalities for this milestone.

## Focused source-code audit

The machine-readable inventory pins each observation's files. This is a justified
shortlist across reconstruction, contrastive, pretrained, graph, marker and efficient
hybrid approaches; it is not a claim to have audited every dependency or tool.

| Inspected path/function | Direct observation | Design consequence |
| --- | --- | --- |
| VAMB `encode.make_dataloader`, `VAE.calc_loss`; `cluster.py` | Sample-total normalization, relative coverage and log total abundance; zero-total coverage becomes uniform. Separate reconstruction terms and mean penalty; current basic encoder uses fixed latent variance. Native clustering does not receive truth K. | Zero transformed vectors are not the same as absent raw coverage. An independently implemented full diagonal VAE would be a declared new prototype, not exact current VAMB parity. |
| VAMB `taxvamb_encode.make_graph`, dataloaders and hierarchical losses | Explicit taxonomy tree/label branches with extra losses. | Taxonomy is a separately supervised input, not a free augmentation. |
| SemiBin `self_supervised_model.train_self/loss_function`, `cluster.run_embed_infomap/recluster_bins`, `long_read_cluster.cluster_long_read` at September 29 head | Margin pair loss; split pairs and random unequal indices; 15-epoch default, up to four million cannot-links, loader workers=0. Infomap graph combines embedding/k-mer/coverage evidence; marker-seeded KMeans differs from long-read DBSCAN. | Runtime/selection are more than a Siamese net. Current changes prepare data once before epochs. Short/long paths must be named when comparing. |
| COMEBin `get_augfeature`, `simclr`, `get_final_result`, `unitem_markers` | Normalized variance/mean/TNF ordering; contrastive positives from views; complete 120-candidate marker scoring and grouped marker completeness/contamination. | Source contracts enabled independent E001 byte/selection verification. Native winner is not guaranteed to maximize truth recovery. |
| CompleteBin `Model/model`, `Trainer/trainer`, `Binning_steps` | Coverage mean/variance encoders, optional frozen pretrained branch, token fusion; current trainer calls optimized debiased InfoNCE; pipeline describes two Leiden stages. | More contracts/assets and evolving recipe than a generic 'Transformer binner' label suggests. Current code is not automatically the v3-paper implementation. |
| SCGBinner `simclr.info_nce_loss/train_addpretrain`, training and cluster adapters | Standard view contrastive updates interleaved with single-copy-gene batches; marker-informed processing outside the encoder too. | Additional signal and selection must be isolated in evaluation; no basis for combining this with another loss by default. |
| McDevol `byol_model.forward/update_moving_average/multinomialsampling`, `clustering.run_leiden` | Detached moving-average target, online predictor; Poisson count draws; HNSW/Leiden. | Coverage augmentation already exists; BYOL adds teacher/collapse and approximate-neighbor contracts. Local missing files are recorded; no complete runnable checkout claimed. |
| GenomeFace `assemble_model`, `embed_contigs`, clustering branches | Loads separate fixed composition/abundance weights; optional global Bayesian balance and cuML HDBSCAN/MST paths. | A source snapshot is sufficient for this observation, not an immutable executable identity; CPU and payload feasibility unverified. |
| DCVBin `bin/my_method.sh`, `myvae/mainfiles/myencode.py` | Wrapper expects FASTA and sorted BAM; input includes coverage, TNF, language-model features and log abundance. | Do not build a sequence-only product assumption from its title. No weights downloaded or claimed validated. |
| LorBin `lorbin.train_vae`, `cluster.bin_cluster` | VAE then multiple distance thresholds/BIRCH candidates and learned keep/quality models; inspected neighbor calls use hardcoded jobs=10. | A future wrapper must audit nested CPU counts, not merely set the CLI flag. Extra model assets would enter provenance. |
| QuickBin `quickbin.sh`, `CovLR.lrCov`, `Oracle.similarity`, `binmap/BinMap` at September 28 head | GC/depth index narrows candidates; layered comparisons. Optional `covlr=f` default, length-dependent variance and calibrated coabsence; separate perfect-oracle debug branch exists. | Keep development likelihood mode and truth-oracle paths out of an ordinary baseline unless explicitly configured/audited. Recheck flags at each pin. |
| GraphMB `train_ccvae.prepare_data_for_gnn/run_model_ccvae`, models/main | Assembly edges, optional same-SCG edge removal, reconstruction/GNN/SCG losses with configurable branches. | Graph input, marker use and chosen path must be named; adopting a library does not define the scientific method. |

## Synthesis for this project

The most defensible first-product alternatives are a compact reconstruction model,
a lightweight pair-contrastive model, or a pretrained/graph-informed model with a
larger external-input contract. A fast neural pair-merging design is also credible,
but adds merge-order/training-pair engineering before we have a working product.
There is no universal winning family. Strong evidence for COMEBin/SemiBin2 does
not establish which individual ingredient causes their advantage.

Our recommendation is the compact reconstruction route for **v0 only**, with explicit
composition and measured multi-sample coverage. This follows the review, rather
than presupposing those modalities: they are available, complementary in the E001
probes, cheap to consume and require neither taxonomy nor graph/model databases.
A VAE supplies a coherent training objective without inventing fragment coverage
or declaring unrelated contigs biological negatives. E001 measured a much cheaper
VAMB path; its lower recovery is an explicit tradeoff, not hidden evidence of parity.

Use one conventional density clustering procedure with frozen settings initially;
retain embeddings and complete assignment accounting so later representation and
clustering changes can be evaluated separately. Do not copy COMEBin's 120-way grid
or select with truth. The CT selection gap is a useful future research lead, not a
reason to append a marker selector, uncertainty module or new replication campaign
before the first working tool. [D011](../decisions/D011-first-binner-prototype.md)
owns the bounded implementation contract, alternatives and revisit conditions.

Limitations: newest preprints lack independent confirmation; several direct publisher
pages were blocked and were checked against local manuscripts/author records;
MBGCCA was only screened at abstract level. No full-scale runtimes beyond E001 were
reproduced. No generalization claim is justified by a single development community.
Code reuse and pretrained assets would need their own license/overlap checks; this
review authorizes no copying or redistribution of those assets.
