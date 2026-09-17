# Targeted Audit: Coverage, Representations, and Selection

Date: 2026-09-17
Scope: paper methods and selected executable code paths traced statically to design [E001](../../experiments/E001-coverage-thinning/README.md). This is not an exhaustive review, software certification, or reproduced performance comparison.
Decision: [D003](../decisions/D003-coverage-diagnostic.md). Questions: [Q001](../research/questions.md#q001), [Q002](../research/questions.md#q002), [H001](../research/questions.md#h001).

## Bottom line

Coverage reliability is a defensible diagnostic question, but neither uncertainty, adaptive modality weighting, nor coverage augmentation is an unexplored method category. The useful next distinction is **lost information versus usable information lost by a particular processing stage**. No residual performance gap has been demonstrated yet.

Use an existing public simulation first. Compare actual read-template thinning with an algebraic rescaling control, holding assembly and sample identities fixed. Read sampling supplies a physically interpretable intervention without claiming to reproduce mapping-reference competition. Do not start by inventing an encoder or a large synthetic benchmark.

## Source identities and review boundaries

[Tool snapshots](2026-09-17-tool-snapshots.json) owns the exact inspected commits, upstream locations, and checkout qualifications. [Fingerprints](context-sources.sha256) identifies the local paper text and selected inspected files. A commit identifies code, not an installed environment or model/database payload. These are pinned **audit snapshots**, not claims about the latest release or the software used in a paper.

The owner replaced many ZIP snapshots with clones. Selected cloned sources have no tracked source changes except the separately noted DCVBin/McDevol states; untracked Finder files are irrelevant to the audit and were left alone. GenomeFace is still an unversioned copy: Git invoked there finds the enclosing project, not a GenomeFace repository. McDevol's README and `byol_model.py` blobs match its HEAD, but its index reports widespread deletions alongside untracked copies. DCVBin's tracked model payload is absent. Neither checkout was repaired or treated as run-ready.

Deepest code review: VAMB preprocessing/encoding, COMEBin feature construction and output selection, DCVBin's launched feature-fusion path, and AMBER genome metrics. Targeted path review: MetaBAT2 filters, SemiBin2 graphs/reclustering, GenomeFace balance selection, QuickBin coverage options/likelihood code, McDevol augmentation. BASALT-Air and ancient-DNA AMBER received README screening only. TaxVAMB/CompleteBin/long-read tools remain relevant contextual alternatives, not fully audited E001 baselines.

## Core baselines

| Method | Actual information and preprocessing | Learning and clustering | Outputs and implication |
| --- | --- | --- | --- |
| MetaBAT2, inspected post-v2.18 snapshot | TNF plus per-sample depth means and variances. `src/metabat2.cpp` defaults to 2,500 bp seed contigs, depth filters `minCV=1`, `minCVSum=1`; supports small-contig recruitment. `--cvExt` substitutes variance equal to mean, so it is not equivalent to measured variance. | Native probabilistic similarities and graph binning; no neural training or taxonomy needed. Absolute-depth thresholds make scale sensitivity possible by design. | `--saveCls`, bin FASTAs, and `--unbinned`; retain excluded IDs too. Use measured variance and a nonzero seed. Do not call threshold-induced loss a representation failure. |
| VAMB, inspected current default VAE | `vamb/encode.py:make_dataloader` column-normalizes coverage, row-normalizes it, and additionally retains z-scored log total abundance. Zero-coverage rows become uniform profiles, but retain a clipped total-abundance value. TNF is standardized and loss is length-weighted. BAM ingestion uses trimmed means in `parsebam.py:run_pycoverm`. | Reconstructs profile, TNF, and total abundance with a latent regularizer. `bin default` uses target-data unsupervised training and native iterative clustering, without the taxonomy/marker inputs of other VAMB modes. | `latent.npz`, `model.pt`, composition identifiers, cluster TSV and optional FASTAs. Total abundance means that per-contig scale changes need not disappear; uniform per-library scaling cancels upstream of that feature, apart from numeric effects. |
| COMEBin 1.1.0 code at inspected HEAD | Six sequence views; per-view TNF, coverage means and, in the wrapper, square-root variances. `get_augfeature.py` adds a coverage pseudocount then scales each sample over its views/contigs by its maximum by default. TNF receives a count pseudocount and row normalization. | Coverage network plus combined contrastive network. Marker-derived seeds, weighted seed K-means, Leiden candidates, and marker-quality selection are part of the native pipeline. Temperature is chosen using assembly N50. | Binary feature and embedding bundles with explicit ID axes, coverage embeddings, candidate labels, estimated quality and final assignments. This differs from the old cache's TSV embedding interface. Keep the complete candidate set and size-filtered final result; do not quietly substitute a quality-filtered subset. |

Relevant local entry points: [MetaBAT2](../../agent_context/tools_repo/metabat/src/metabat2.cpp), [VAMB preprocessing](../../agent_context/tools_repo/vamb/vamb/encode.py), [VAMB CLI](../../agent_context/tools_repo/vamb/vamb/__main__.py), [COMEBin wrapper](../../agent_context/tools_repo/COMEBin/COMEBin/run_comebin.sh), [features](../../agent_context/tools_repo/COMEBin/COMEBin/get_augfeature.py), [coverage intervals](../../agent_context/tools_repo/COMEBin/COMEBin/data_aug/gen_cov.py), [clustering](../../agent_context/tools_repo/COMEBin/COMEBin/cluster.py), [final selection](../../agent_context/tools_repo/COMEBin/COMEBin/get_final_result.py).

These native coverage extractors are not identical. E001's causal comparisons are **within each method**, using identical alignments across methods and paired conditions within a method. Between-method differences cannot automatically be attributed to the encoder. The common minimum length is an explicit diagnostic restriction, not a claim to reproduce each paper's preferred workflow.

### Why SemiBin2 is not an embedding-only clusterer

In [cluster.py](../../agent_context/tools_repo/SemiBin/SemiBin/cluster.py), `run_embed_infomap` intersects embedding and input-feature neighbor graphs. In the non-combined mode it also uses mean/variance-based abundance similarity. `recluster_bins` can add scaled abundance to the embedding before marker-seeded weighted K-means. Pre-reclustering bins can be retained with the native option; embeddings need a small explicit export hook if used later.

[self_supervised_model.py](../../agent_context/tools_repo/SemiBin/SemiBin/self_supervised_model.py) and `utils.py:norm_abundance` also show conditional normalization. An all-purpose clusterer swap would discard native information, not isolate just a different clustering algorithm. Keep SemiBin2 as the first strong alternative if COMEBin cannot be made reproducible within the bounded setup work; document that amendment before results, not after comparing scores.

## Closest prior art and corrections

### UncertainGen: probabilistic geometry is not calibrated coverage confidence

Reviewed [original arXiv v1](https://arxiv.org/html/2509.26116v1), sections 3-5, alongside the [updated local transcription](../../agent_context/papers/bin_tools/UNCERTAINGEN_paper.md). It learns mean/covariance sequence embeddings from k-mer inputs and uses a covariance-dependent pairwise similarity. Evaluation uses reference-derived sequence datasets and modified K-medoids; its quality tiers are F1-based, not AMBER or MIMAG categories. Calibration is explicitly unresolved. No runnable author implementation was verified in this search.

Interpretation: relevant prior art for probabilistic embeddings and selective assignment, but not evidence that read-coverage uncertainty is solved. A distribution can express ambiguity or change geometry; it cannot determine the unique origin of identical, otherwise indistinguishable input. A future uncertainty claim must test calibration and retained recovery, not merely show a variance distribution or better clustering.

### GenomeFace: global balance, not verified per-contig reliability

Reviewed local paper sections 4.3-4.6 and [source copy](../../agent_context/tools_repo/genomeface/genomeface.py), especially `calc_alpha`, `opt_function_generator`, and `main`. The paper describes reference-trained composition features, an abundance network, a sample-count-based modality balance, and optional Bayesian optimization of a marker-derived clustering reward. Its abundance training/tuning uses CAMI II human body-site data, so those datasets cannot automatically be called independent tests of that model.

The source uses a single balance parameter and exposes optional `-b` optimization, disabled by default. This is narrower than a claim that GenomeFace learns reliability separately for every contig/sample. The inspected copy is not proven identical to an upstream package. Its package, CUDA dependencies, pretrained weights, and reference lists must be recovered before execution. The original [preprint](https://doi.org/10.1101/2024.02.07.579326) could not be fetched in this browser pass; no new equation was inferred from missing extraction graphics, and later publication status remains unverified.

### DCVBin: the inspected executable path really uses coverage

The [journal paper](https://doi.org/10.1093/bib/bbag241), especially Related work and feature fusion, frames sequence features as replacing coverage. Direct code observation is more specific:

`bin/my_method.sh` finds a sorted BAM, runs `calc_tnf_and_rpkm_2.py`, and passes the resulting matrix to `vaeTest_2.py`. That script imports `myencode`, constructs `VAE(nsamples=1)`, and supplies coverage, TNF, language-model features and lengths. `myencode.py:forward` concatenates coverage and total abundance with the other features. With one sample the row-normalized profile is constant for covered rows, **but the separate total-abundance feature varies**.

This resolves the initial dormant-code uncertainty for the inspected basic pipeline: coverage is live, not just an unused argument. It does **not** establish which revision generated the publication's results. Do not use this snapshot as a coverage-free comparator, or silently remove its input and call the result native DCVBin. The missing model payload is another execution dependency. See [wrapper](../../agent_context/tools_repo/dcvbin/bin/my_method.sh), [fusion entry](../../agent_context/tools_repo/dcvbin/myvae/mainfiles/vaeTest_2.py), [encoder](../../agent_context/tools_repo/dcvbin/myvae/mainfiles/myencode.py).

### QuickBin and McDevol narrow the opportunity further

The [QuickBin journal article](https://www.nature.com/articles/s42003-026-10782-z), Methods and Code availability, describes conservative merging, short-contig recruitment, optional paired-read edges and a small pretrained classifier. It reports BBTools 39.60, while our inspected development snapshot is newer. These are different artifacts.

The current [quickbin.sh](../../agent_context/tools_repo/BBTools/quickbin.sh) exposes optional sample condensation and length-aware coverage likelihood modes. [CovLR.java](../../agent_context/tools_repo/BBTools/current/bin/CovLR.java) contains an explicit read-sampling/length term, dispersion term and co-absence handling. These options are not enabled by default and are not established here as the published algorithm. Its attribution to `NeLLi-team/warpbin` is a source-code report: that upstream URL returned 404, so we have not independently audited WarpBin. Do not claim a new length-aware coverage likelihood without confronting this code and its assumptions. Native paired-read edges also mean a QuickBin comparison is not automatically equal-information.

[McDevol's README](../../agent_context/tools_repo/McDevol/README.md) and [byol_model.py](../../agent_context/tools_repo/McDevol/mcdevol/byol_model.py) show positive-pair self-supervision, GenomeFace composition features, and read-count sampling augmentations. The inspected `multinomialsampling` implementation uses Poisson draws/rebalancing, not a literal single multinomial call. Coverage-noise augmentation is therefore also prior art. Both methods become required mechanism-focused comparisons if E001 motivates a reliability intervention; they need not inflate the first stage-localization experiment.

### Newly supplied tools with different roles

- [BASALT-Air](../../agent_context/tools_repo/BASALT-Air/README.md): refinement, contig retrieval and reassembly can change inputs and output sequence. Relevant if loss localizes downstream, but not an interchangeable single-binner baseline. README-only screen, no verified quality improvement here.
- [Ancient-DNA AMBER](../../agent_context/tools_repo/amber_binning/README.md): damage/fragment-length-aware binning for a specialized setting. Distinct software from CAMI's AMBER evaluator. Its documented mechanisms are source claims, not a reproduced or fully reviewed method.
- [CAMISIM](../../agent_context/tools_repo/CAMISIM/README.md): current checkout documents the Nextflow-based 2.0 transition; the old Python workflow is at `1.31-final`. Do not reuse thesis configuration against current master without conversion and verification. Not needed to generate E001's public dataset.

## AMBER is suitable, with explicit contracts

Inspected [README](../../agent_context/tools_repo/AMBER_evaluation/README.md), [loader](../../agent_context/tools_repo/AMBER_evaluation/cami_amber/utils/load_data.py), and `GenomeQuery.compute_metrics` / `calc_num_recovered_genomes` in [binning_classes.py](../../agent_context/tools_repo/AMBER_evaluation/cami_amber/binning_classes.py).

Direct observations:

- Genome purity is dominant-origin bases divided by bin bases. Recall uses bases in the supplied gold-standard mapping, not automatically the complete source genome length.
- Missing genomes remain in the per-genome recall calculation. Some summaries are averages over bins and others over genomes; they are not interchangeable.
- At this snapshot, recovery threshold comparisons are strict `>` completeness and `<` contamination. E001 explicitly labels its separate inclusive thresholds.
- Unknown predicted sequence IDs are warned about and removed. Duplicate sequence/bin rows are deduplicated. Our preflight must catch these before evaluation, rather than let input errors silently alter denominators.
- Multi-origin truth has an explicit handling branch, which can change the effective gold-standard association. AMBER is **not** categorically unable to handle shared sequence. Our fixed-origin subset and full standard report have different purposes and must be tested separately.

Decision: reuse AMBER unchanged for standard reports; implement only integrity checks, fixed-denominator/length-stratified summaries and stage comparisons around it. Cross-check the common unique-origin case with hand-calculable fixtures. An independent general evaluator is not justified now.

## What remains unestablished

No method has been run. We do not know whether thinning exposes a meaningful residual error, whether a simple existing configuration resolves it, or whether a proposed reliability mechanism would beat QuickBin/McDevol/GenomeFace. Native feature differences, shared sequence, marker selection, and information loss remain competing explanations.

The audit is complete **for designing E001**, not for claiming novelty. The next work is implementation and preflight of [the protocol](../../experiments/E001-coverage-thinning/README.md), not another unbounded literature sweep. Expand the review only where observed failure points make it necessary.
