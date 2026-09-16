# Table of Contents

[Supplementary Materials - METHODS [2](#supplementary-materials---methods)](#supplementary-materials---methods)

[Table S1: Per-Sample Assembly Statistics [2](#table-s1-per-sample-assembly-statistics)](#table-s1-per-sample-assembly-statistics)

[Table S2. Heatmap Metric Selection and Non-Redundancy Justification [3](#table-s2.-heatmap-metric-selection-and-non-redundancy-justification)](#table-s2.-heatmap-metric-selection-and-non-redundancy-justification)

[Supplementary Methods S1: CompleteBin Multi-View Duplication and Restoration [4](#supplementary-methods-s1-completebin-multi-view-duplication-and-restoration)](#supplementary-methods-s1-completebin-multi-view-duplication-and-restoration)

[Supplementary Methods S2: Validation of Genome Size Estimation Against Simulated Ground Truth [5](#supplementary-methods-s2-validation-of-genome-size-estimation-against-simulated-ground-truth)](#supplementary-methods-s2-validation-of-genome-size-estimation-against-simulated-ground-truth)

[Supplementary Materials - RESULTS [7](#supplementary-materials---results)](#supplementary-materials---results)

[S2.4 CheckM2 Trustworthiness Calibration: Completeness Stratification [7](#s2.4-checkm2-trustworthiness-calibration-completeness-stratification)](#s2.4-checkm2-trustworthiness-calibration-completeness-stratification)

[S2.9 Computational Efficiency [7](#s2.9-computational-efficiency)](#s2.9-computational-efficiency)

[S2.11 Ensemble Tool Analysis: Competitive Exclusion Forensics [9](#s2.11-ensemble-tool-analysis-competitive-exclusion-forensics)](#s2.11-ensemble-tool-analysis-competitive-exclusion-forensics)

[S2.12 Legacy Pipeline Comparison: DAS Tool vs CompleteBin MAM [10](#s2.12-legacy-pipeline-comparison-das-tool-vs-completebin-mam)](#s2.12-legacy-pipeline-comparison-das-tool-vs-completebin-mam)

[Supplementary Materials - DISCUSSION [13](#supplementary-materials---discussion)](#supplementary-materials---discussion)

[S3.2 Algorithmic Incompatibility of GenomeFace and SemiBin2 with Cluster-and-Split Workflows [13](#s3.2-algorithmic-incompatibility-of-genomeface-and-semibin2-with-cluster-and-split-workflows)](#s3.2-algorithmic-incompatibility-of-genomeface-and-semibin2-with-cluster-and-split-workflows)

[Supplementary Materials - FIGURES [15](#supplementary-materials---figures)](#supplementary-materials---figures)

[References [51](#references)](#references)

# Supplementary Materials - METHODS

## Table S1: Per-Sample Assembly Statistics

| Sample | Contigs (≥ 2 kb) | Assembly Size (Mb) | Longest Contig (bp) | N50 (bp) |
|----|----|----|----|----|
| HSo261_ST4_CT1_0_1 | 20,283 | 79.71 | 72,963 | 3,908 |
| HSo261_ST4_CT1_1_2 | 106,749 | 404.24 | 142,450 | 3,728 |
| HSo261_ST4_CT1_2_3 | 115,707 | 456.03 | 286,847 | 3,911 |
| HSo261_ST4_CT1_3_4 | 102,947 | 414.84 | 146,745 | 4,094 |
| HSo261_ST4_CT1_4_5 | 110,003 | 420.73 | 178,317 | 3,779 |
| HSo261_ST4_CT1_5_6 | 61,415 | 245.69 | 197,375 | 4,090 |
| HSo261_ST4_CT1_6_7 | 36,043 | 141.28 | 140,191 | 3,989 |
| HSo261_ST4_CT1_7_8 | 79,018 | 339.87 | 183,678 | 4,553 |
| HSo261_ST4_CT1_8_9 | 56,699 | 244.00 | 124,941 | 4,531 |
| HSo261_ST4_CT1_9_10 | 121,060 | 528.03 | 307,500 | 4,631 |
| HSo261_ST4_CT1_10_12.5 | 37,034 | 144.00 | 188,851 | 3,830 |
| HSo261_ST4_CT1_12.5_15 | 104,212 | 418.71 | 142,137 | 4,082 |
| HSo261_ST4_CT1_15_17.5 | 101,678 | 422.53 | 211,139 | 4,293 |
| HSo261_ST4_CT1_17.5_20 | 79,431 | 336.23 | 210,458 | 4,414 |
| HSo261_ST4_CT1_20_22.5 | 5,340 | 24.65 | 114,346 | 5,135 |
| HSo261_ST4_CT1_22.5_25 | 38,609 | 150.06 | 256,878 | 3,912 |
| HSo261_ST4_CT1_25_27.5 | 102,844 | 438.60 | 164,224 | 4,506 |
| HSo261_ST4_CT1_27.5_30 | 80,573 | 337.62 | 314,052 | 4,368 |
| HSo261_ST4_CT1_30_32.5 | 50,908 | 218.94 | 131,010 | 4,584 |
| HSo261_ST4_CT1_32.5_35 | 106,887 | 443.18 | 117,341 | 4,282 |
| Total / Mean | **1,517,440** | **6,208.93 Mb** | — | **4,231 (mean)** |

Table S1: Summary statistics of the 20 per-sample MEGAHIT assemblies after filtering to contigs ≥ 2,000 bp. N50 values, longest contig lengths, and assembly sizes are reported per sample.

## Table S2. Heatmap Metric Selection and Non-Redundancy Justification

| Category | Metric | Why Included | Why Not Redundant | In Score? |
|----|----|----|----|----|
| Yield | NC_Count | Highest-quality tier; most stringent test of genome recovery | Subsumes HQ completeness requirement plus rRNA/tRNA | Yes |
| Yield | HQ_Count | Standard high-quality threshold; primary yield benchmark | Distinct from NC (NC adds rRNA/tRNA filter) | Yes |
| Yield | MQ_Count | Broadest quality-passing count; total genome recovery | Some tools recover many MQ but fewer HQ; distinct information | Yes |
| Quality | Mean_Completeness | Core quality axis; visual decomposition of QS | Shown for interpretability; in score, combined with contamination as Mean_QS_5x | Via QS_5x |
| Quality | Mean_Contamination | Core quality axis (inverted); visual decomposition of QS | Shown for interpretability; in score, combined with completeness as Mean_QS_5x | Via QS_5x |
| Quality | GUNC_Pass_Rate | Chimerism detection; catches contamination CheckM2 misses. Rate-based because chimerism tendency is a tool-intrinsic property | Orthogonal to CheckM2-based metrics | Yes |
| Quality | Total_Wins | Per-genome head-to-head quality competition (absolute count). Heatmap only, informational | Captures quality relative to competitors, not just mean quality | No |
| Quality | All-FDR | CheckM2 trustworthiness: frequency of tier inflation | Unique dimension: measures reliability of quality estimates, not quality itself | Yes |
| Quality | QS_Error_mean | CheckM2 trustworthiness: magnitude of QS bias. Weakly correlated with All-FDR | Complementary to All-FDR: frequency vs magnitude of CheckM2 error | Yes |
| Taxonomic Reach | Exclusive_Genomes | Unique biological contribution; genomes no other tool recovers | Not captured by yield (a high-yield tool may recover only shared genomes) | Yes |
| Taxonomic Reach | Total_Novel_MAGs | Absolute count of taxonomically novel MAGs. Count-based because absolute novel discovery matters biologically | Partially correlated with MQ_Count, but different category with different weight | Yes |
| Taxonomic Reach | delta_N_MQ | Strain resolution: additional MQ+ MAGs gained at 99% vs 95% ANI | Unique dimension not captured by species-level metrics | Yes |
| Assembly | Median_Contig_N50_KB | Assembly contiguity of recovered MAGs | Not captured by completeness (a complete MAG can be highly fragmented) | Yes |
| Assembly | Data_Utilization | Fraction of assembly bp captured in all raw bins (no quality filter), following Kim et al. [2026]. Measures tool aggressiveness | Low correlation with MQ_Count (aggressive binning does not equal quality MAGs) | Yes |
| Efficiency | Runtime_Hours | Wall-clock cost | Practical for users choosing tools | No |
| Efficiency | Peak_Memory_GB | Memory footprint | Practical for resource-constrained environments | No |

Table S2: Inclusion rationale and non-redundancy justification for each of the 16 heatmap metrics. Metrics are grouped by category. "In Score?" indicates whether the metric contributes to the weighted composite score (Section 1.16). "Via QS_5x" indicates that the metric is displayed in the heatmap but enters the score as a component of Mean_QS_5x. Total: 16 metrics across 6 categories (12 in score, 4 informational).

## Supplementary Methods S1: CompleteBin Multi-View Duplication and Restoration

This section provides the full diagnosis and restoration procedure for the CompleteBin duplication problem.

Inspection of CompleteBin's raw output bins revealed a critical data corruption caused by multi-view leakage from its contrastive learning pipeline. CompleteBin's training code generates multiple augmented "views" per contig (subsequence fragments) for contrastive learning. These views should be merged back into a single consensus entity before output, but the tool fails to do so, causing the augmented views to leak into the output bins as separate records sharing the same contig header ID.

This multi-view leakage showed as cross-bin contig overlap: the same contig ID is claimed by multiple different bins simultaneously. Across all 20 MAM samples, the raw CompleteBin output contained 2,134,370 total records from 1,382,148 unique contig IDs, meaning 752,222 records (35.2%) were duplicate copies. A total of 537,176 unique contig IDs (38.9% of all unique IDs) exhibited cross-bin overlap, affecting 4,925 of 5,144 raw bins (95.7%). Each duplicated contig appeared in an average of 2.42 bins (maximum 6.9 across samples). The duplicated records accounted for approximately 3.05 Gb (34.6% of raw total base pairs).

These duplications have severe downstream consequences. First, they crash ensemble tools: Binette attempted to calculate every possible unique combination of overlapping contigs, triggering a combinatorial explosion. Second, they produce impossible evaluation metrics: AMBER reported accuracy values exceeding 1.0 (e.g., 1.143), because identical sequences were counted multiple times. Third, they inflate apparent completeness: duplicated contigs artificially increase the count of single-copy marker genes within bins.

To correct these errors, a custom post-processing script (restore_bins.py) was developed. The script treats the raw bin FASTA files purely as cluster membership maps and rebuilds the bins using the original, clean input FASTA as the reference. The restoration proceeds in two steps. First, contig ownership is resolved using a winner-takes-all rule: if a contig ID appears in multiple bins, it is assigned exclusively to the bin with the largest total raw base-pair content, with ties resolved by first-observed order. This approach is appropriate because a bin containing more base pairs is most likely the primary genomic cluster that the contrastive learning algorithm designated as the dominant owner of that contig. Discarding all multiply-claimed contigs would eliminate too much data and leave bins undersized; random assignment would introduce non-determinism. The winner-takes-all rule based on bin size is therefore the most principled and reproducible resolution consistent with what a correctly functioning binner should have output. Second, the bin files are rewritten by looking up the clean, original reference sequence for each assigned contig ID, bypassing the augmented views entirely. Any bin resulting in 0 bytes (ghost bins consisting entirely of duplicate data) or smaller than 200 kb after restoration is discarded.

Across all 20 MAM samples, restoration removed all 752,222 duplicate records (35.2% of raw records) and 3.05 Gb of duplicate base pairs (34.6% of raw base pairs). A total of 319 empty ghost bins were produced after overlap resolution, leaving the 5,144 bins restored with zero remaining duplicates and zero remaining cross-bin overlaps. The highest-quality bins retained their size and completeness after restoration, confirming that the winner-takes-all logic correctly favoured the primary genomic clusters.

## Supplementary Methods S2: Validation of Genome Size Estimation Against Simulated Ground Truth

The genome size estimation formula (Section 1.11) was validated against AMBER ground-truth genome sizes from the CAMISIM strain simulation dataset (Section 1.2). MAGs were filtered using CheckM2 estimates (Completeness > 50%, Contamination < 10%), matching the real-data pipeline, retaining 7,665 of 14,915 simulated MAGs. Of these, 436 (5.7%) were actually low-quality by ground truth, mirroring the real-world scenario where CheckM2 misclassification introduces noise.

### Formula Accuracy

With ground-truth completeness and contamination, the formula produced 0.00% error, confirming mathematical correctness. With CheckM2 predictions, the formula exhibited a mean percentage error of -3.76% (systematic underestimation), a median error of -2.69%, a MAPE of 5.81%, and a MAE of 0.297 MB.

CheckM2 overestimated completeness by a mean of +3.21 pp (std = 6.39 pp, Q10 = -2.68, Q90 = +10.82) and overestimated contamination by a mean of +0.04 pp (std = 4.64 pp, Q10 = -2.56, Q90 = +2.86). Completeness error dominated the genome size estimation error (r = -0.83, p < 10<sup>-300</sup>), while contamination error had a weaker but still significant effect (r = -0.10, p = 1.8 x 10<sup>-19</sup>). The error amplitude scaled inversely with completeness (Supplementary Table S3).

| CheckM2 Completeness | N MAGs | MAPE (uncorrected) | MAPE (corrected) | Within +/-5% (corrected) |
|----|----|----|----|----|
| 90-100% | 5,836 | 4.8% | 4.2% | 71.1% |
| 80-90% | 1,205 | 6.5% | 6.5% | 48.9% |
| 70-80% | 307 | 11.7% | 10.3% | 30.6% |
| 60-70% | 157 | 13.8% | 12.7% | 29.3% |
| 50-60% | 160 | 17.6% | 16.6% | 23.8% |

Table S3: Genome size estimation accuracy by CheckM2 completeness bucket, before and after application of the 1.024 global correction factor. MAPE = mean absolute percentage error. The correction improved estimates across all buckets, but error remained substantial at low completeness (50-70%), where CheckM2 predictions are least reliable.

### Extreme Error Analysis

Among 29 MAGs with extreme genome size overestimation (>20% error), the dominant driver was CheckM2 underestimation of contamination: mean true contamination was 26.9% versus predicted 5.2% (mean error = -21.7 pp). Of these, 21 (72.4%) had contamination underestimation exceeding 5 pp, while completeness prediction error was minimal (mean = -2.0 pp).

Conversely, among 228 MAGs with extreme underestimation (<-20% error), the driver was completeness overestimation: mean true completeness was 53.8% versus predicted 76.5% (mean error = +22.7 pp). This asymmetric structure means that in the real dataset, extreme overestimates are most likely caused by chimeric MAGs where CheckM2 fails to detect contamination, while extreme underestimates arise from MAGs whose true completeness is far lower than predicted.

### Quality Misclassification

Of 7,665 MAGs passing CheckM2 filters, 436 (5.7%) were low-quality by ground truth. These misclassified MAGs had mean predicted completeness of 78.2% versus true 67.9%, and mean predicted contamination of 4.8% versus true 16.6%, yielding a MAPE of 14.2%. This confirms that quality misclassification disproportionately harms estimation accuracy.

### Correction Strategy Selection

Three correction strategies were evaluated:

(1) **Global scalar correction (x1.024), selected.** Derived by minimizing MAPE across all 7,665 MAGs. Reduced MAPE from 5.81% to 5.26% and shifted median error from -2.69% to approximately -0.3%. Simple, interpretable, and carries no overfitting risk.

(2) **Per-completeness-bucket corrections, rejected.** Separate factors per bucket ranged from x1.011 (80-90%) to x1.111 (60-70%). The large factors at low completeness further amplify estimates in the regime where CheckM2 is least reliable, the 50-60% bucket contained only 160 calibration MAGs limiting statistical stability, and the consensus pipeline's cross-tool median already handles noise at low completeness, making per-bucket correction redundant.

(3) **Gradient Boosting Regressor (8 features), rejected.** Achieved the best cross-validated MAPE of 3.55%, but was rejected due to generalizability concerns. The simulated dataset had substantially different assembly characteristics: median N50 of 14.3 KB versus 5.6 KB in the real data, completeness skewed to 90-100% (median 94.4% versus 80.2%), genome sizes 1.9x larger (median 4.4 MB versus 2.3 MB), and an extremely narrow N50 range (12-17 KB versus 2.5-117 KB). Feature importance analysis showed total_length accounted for 90.8%, indicating the model learned the formula plus genome-specific patterns from only 58 unique simulated genomes, making deployment on the structurally different real dataset risky.

# Supplementary Materials - RESULTS

## S2.4 CheckM2 Trustworthiness Calibration: Completeness Stratification

This section provides the full per-completeness-bucket stratification of the CheckM2 All-FDR summarised in Results Section 2.4.

The simulated dataset has higher median completeness (~94%) than the real deep-sea data (~80%), with nearly 88% of simulated bins falling in the 90-100% range (Section 1.10). Many tools (CoCoBin, MAGScoT, DAS Tool, COMEBin, CompleteBin) produce zero or near-zero bins below 80% completeness, limiting statistical power for lower-completeness regimes. At 90-100% completeness, the trustworthy/unreliable distinction was preserved: CompleteBin (13.1%, n = 274), GenomeFace (14.9%, n = 161), and MAGScoT (15.4%, n = 273) remained the most trustworthy, while MetaBAT2 (38.8%, n = 165), VAMB (32.5%, n = 123), and MetaBinner (32.4%, n = 111) remained the most inflated (Figure S19).

At 50-60% completeness, tools with data showed near-total All-FDR (Binette 100% n = 7, SemiBin2 100% n = 5, MetaBinner 93.8% n = 16), though sample sizes are very small. This is mechanistically expected: bins at 50-60% CheckM2 completeness that are truly LQ had their completeness overestimated across the 50% MQ threshold. At 80-90%, All-FDR drops sharply (most tools 0-6%), because bins in this range sit far from both the MQ (50%) and HQ (90%) boundaries, requiring large errors to cross a tier. All-FDR rises again at 90-100% because the 90% completeness mark coincides with the MQ/HQ border, where even small overestimation pushes truly MQ bins into the HQ tier. Absolute All-FDR values should be treated as optimistic lower bounds for the real dataset, as the simulated data lacks assembly artefacts (chimeric contigs, misassemblies) that would increase CheckM2 error in real data. The relative tool rankings are the primary transferable finding.

## S2.9 Computational Efficiency

### Parallel Efficiency and CPU Utilisation

Figure S46 and Figure S47 present parallel efficiency as a horizontal bar chart alongside CPU time versus wall-clock time on a log-log scatter plot with a 1:1 diagonal marking single-threaded equivalence.

CoCoBin achieved the highest parallel efficiency at 99.4% in CS and 92.2% in MAM, saturating nearly all 32 allocated threads. MetaBAT2 followed with 96.8% in CS and 76.2% in MAM. CompleteBin achieved 82.7% in MAM, high for a multi-step GPU/CPU tool. MetaBinner achieved 59.9% in MAM. COMEBin showed 49 to 53% across workflows, consistent with its split architecture where the GPU embedding step (12 threads) and the CPU clustering step (32 threads) have different utilisation profiles.

At the other extreme, MAGScoT achieved only 3.3% in MAM and 3.9% in CS, indicating that its R-based implementation is effectively single-threaded despite being allocated 32 cores. VAMB showed 7.7 to 11.8% efficiency and GenomeFace 8.3 to 21.7%, reflecting that their GPU-accelerated computation leaves the CPU largely idle. Low CPU parallel efficiency for GPU tools does not imply poor performance, only that the computational bottleneck is on the GPU.

### I/O Intensity

Figure S48 reveals substantial variation in disk I/O intensity across tools. In the MAM workflow, MetaBAT2 exhibited the highest I/O intensity at 55.4 MB/s, followed by VAMB (37.5 MB/s), CoCoBin (36.1 MB/s), and GenomeFace (29.0 MB/s). At the low end, MAGScoT consumed only 0.3 MB/s and Binette 0.9 MB/s. Tools with high I/O intensity may see their performance differ between HDD and NVMe storage configurations. MAM I/O intensity was consistently higher than CS and SC for all standalone binning tools, because per-sample I/O overhead (file opens, index reads) is spread across many shorter individual runs rather than a single long run. The sole exception was COMEBin, where CS (16.2 MB/s) and SC (22.5 MB/s) exceeded MAM (14.2 MB/s). The reason for this reversal is unclear.

### Preprocessing Surcharge

Figure S38 reveals that several tools' total runtime is dominated by preprocessing rather than binning. GenomeFace had the largest preprocessing share across all workflows: 94.8% in MAM, 93.0% in CS, and 97.5% in SC, meaning its actual binning consumed only 0.44 hours, 0.46 hours, and 0.16 hours respectively, making it the fastest raw binner. MAGScoT's preprocessing (Prodigal plus HMMER) consumed 91.6% of its CS total and 62.2% of its MAM total. MetaBAT2 showed 85.8% preprocessing in MAM, where JGI abundance computation consumed 3.51 hours compared to only 0.58 hours of binning.

The preprocessing share was zero for VAMB, COMEBin, SemiBin2, CompleteBin, and DAS Tool, because these tools either integrate preprocessing internally or consume only shared BAM files directly. CoCoBin's preprocessing share reversed dramatically between workflows: 66.9% in MAM (4.33 hours preprocessing, 2.14 hours binning) versus only 2.8% in CS (1.13 hours preprocessing, 38.64 hours binning), because its binning time on the large CSB assembly dwarfed the already lower preprocessing.

### Per-Sample Variability (MAM)

Figure S49 presents per-sample runtime and peak PSS distributions across the 20 MAM samples. CompleteBin exhibited the widest runtime distribution, with a median per-sample runtime of approximately 11 hours and several samples exceeding 15 hours. COMEBin and MetaBinner showed moderate spread, while MetaBAT2, VAMB, GenomeFace, and CoCoBin clustered tightly near zero relative to CompleteBin's scale.

For peak memory, CompleteBin dominated with the widest range and highest values (IQR spanning approximately 49 to 195 GB). COMEBin showed a relatively tight cluster around 29 to 44 GB. SemiBin2 and MetaBinner had moderate and compact distributions. MetaBAT2, VAMB, GenomeFace, and CoCoBin all had peak PSS values below 10 GB with narrow spread, confirming their suitability for commodity hardware.

### Cost per Bin

Figure S40 presents cost per bin in minutes for each quality tier on a logarithmic scale. MetaBAT2 was the cheapest tool per MQ+ bin at 0.4 minutes, followed by VAMB at 0.7 minutes. At the HQ+ tier, MetaBAT2 remained cheapest at 1.5 minutes per bin. CompleteBin was the most expensive at every tier: 22.8 minutes per MQ+ bin, 95.8 minutes per HQ+ bin, and 442.3 minutes (7.4 hours) per NC bin. COMEBin, despite being the second-highest yielding tool, cost 3.5 minutes per MQ+ bin, 8.8x more than MetaBAT2, and 12.3 minutes per HQ+ bin, 8.2x more. SemiBin2 offered a compelling intermediate position at 1.3 minutes per MQ+ bin and 4.4 minutes per HQ+ bin.

Across workflows, the SC workflow often provided the best cost-per-bin ratio for tools that support it. SemiBin2 SC cost 0.9 minutes per MQ+ bin versus 1.3 minutes in MAM, reflecting its marginally higher SC yield (610 versus 609 MQ+) achieved in less time (9.5 versus 12.8 hours).

## S2.11 Ensemble Tool Analysis: Competitive Exclusion Forensics

### The Mechanism of Competitive Exclusion

To understand why Binette produces Botched Bins (outputs where both AMBER and CheckM2 scores are worse than the best available input), a contig-level forensic audit was performed on all 85 identified Botched events across the three input strategies.

Binette employs a greedy selection strategy with a strict non-redundancy constraint: when a bin is selected into the final output, any other candidate bin sharing even a single contig is immediately discarded. To mitigate this, the algorithm generates "Difference Bins" for each excluded candidate. A Difference Bin is the excluded bin with the overlapping contigs removed (e.g., if the Victim bin V overlaps with a selected Rival bin R, the Difference Bin is V \\ R). In principle, this mechanism should allow valid genomes to survive by trimming away the conflicting contigs. However, the forensic audit revealed that this safety mechanism collapses in the majority of cases.

The failure proceeds as follows. First, the best input bin for a given genome (the "Victim") shares contigs with a bin assigned to a different genome (the "Rival"). If the Rival carries a higher CheckM2 score than the Victim, Binette's greedy algorithm selects the Rival first, which forces the deletion of the original Victim bin. The only remaining candidate for the Victim's genome is the Difference Bin (V \\ R), the Victim stripped of the overlapping contigs. The fate of this Difference Bin depends on two factors: whether the overlapping contigs belonged to the Victim's core genome or its contamination fraction, and whether CheckM2 scores the trimmed bin accurately.

### Classification of Competitive Exclusion Events

Of the 85 Botched events, 62 (73%) were traced to competitive exclusion by identifying the specific Rival bin whose contigs replaced the Victim's in the ensemble output. The remaining 23 events (27%) were classified as "Self-Fragmentation," where no external Rival was identified, indicating internal algorithmic drift or complex multi-way conflicts.

The 62 competitive exclusion events were further classified by the biological origin of the contigs that the Rival appropriated from the Victim:

**Core-dominant theft** (27 cases, 32% of all Botched events): The Rival primarily appropriated contigs belonging to the Victim's core genome, causing the Difference Bin to lose essential marker genes and completeness. The mean theoretical quality delta for these trimmed Difference Bins was -0.82, confirming that loss of core contigs degraded the bin as expected. In these cases, the Rival's contigs overlapping the Victim represent contamination in the Rival, meaning the Rival grew larger by incorporating foreign DNA. Because CheckM2 systematically underdetects contamination in certain regimes (Section 2.11), the contaminated Rival can still outscore the clean but now incomplete Victim.

**Contamination-dominant theft** (23 cases, 27%): The Rival primarily appropriated contigs that were part of the Victim's contamination fraction. Removing these contigs should biologically improve the Victim. Indeed, the mean theoretical quality delta for the Difference Bins was +0.66, confirming that the trimmed bins were biologically superior to the originals. Despite this improvement, CheckM2 scored the cleaned Difference Bins lower than the contaminated originals, because the removed contigs contained marker genes that CheckM2 interpreted as evidence of completeness rather than contamination. This is the most direct evidence that CheckM2's precision blindness actively penalizes decontamination.

**Equal theft** (12 cases, 14%): Core and contamination contigs were appropriated in equal numbers (mean theoretical delta +0.67).

### Case Study: The Assassination of bg_46

The genome bg_46 provides a concrete illustration of the competitive exclusion mechanism (Figure S50). The best input bin for this genome was produced by CompleteBin and carried a CheckM2 quality score of 87.8. This bin overlapped with a Rival bin assigned to genome bg_22, which carried a marginally higher CheckM2 score of 89.4. Because 89.4 > 87.8, Binette selected the Rival, necessitating the destruction of the Victim.

The contig fate matrix (Figure S50) shows that the overlap consisted of 7 contigs, 4 of which were located in the Victim's contamination fraction. Removing these contamination contigs should have improved the bin biologically, and indeed the theoretical AMBER score for the Difference Bin (V \\ R) was 88.7, an improvement of +0.77 over the original 87.9. However, CheckM2 scored the cleaned Difference Bin far below its original score, causing Binette to reject it in favour of a GenomeFace input with a CheckM2 score of only 76.0 and an AMBER score of 66.1, a quality degradation of -25.1 AMBER points relative to the original Victim. This outcome confirms that CheckM2 penalized the removal of contamination contigs, likely because it identified marker genes on those contigs as evidence of genome completeness rather than foreign DNA.

### Global Impact of Competitive Exclusion

The forensic audit demonstrates that the majority of Botched events are collateral damage of a greedy optimization process operating under an imperfect proxy metric. The Rival bins that triggered exclusion carried a mean CheckM2 score advantage of +4.3 to +7.3 over their Victims. While the algorithm secured a quality gain for the Rival genome, it inflicted a disproportionately larger loss on the Victim genome, resulting in a mean net negative impact on total quality across both genomes (mean global CheckM2 delta = -2.53). A global optimization strategy that maximizes the sum of quality scores across all genomes, rather than greedily selecting the highest-scoring individual candidates, could theoretically resolve these trade-offs, but such an approach would be computationally expensive compared to the current greedy heuristic.

## S2.12 Legacy Pipeline Comparison: DAS Tool vs CompleteBin MAM

The deep-sea sediment samples in this benchmark were originally processed using a well-established pipeline: per-sample MetaBAT2, CONCOCT, and MaxBin2 binning followed by DAS Tool ensemble refinement. This analysis compares those legacy MAGs against CompleteBin MAM, the top-ranked standalone binner in the integrated summary score (Section 2.10), to quantify the practical gain from reprocessing with a modern tool. Both pipeline outputs were evaluated through an identical assessment stack: CheckM2, 95% ANI dereplication (dRep with skani), GTDB-Tk r220, Anvi'o (tRNAScan-SE) for tRNA, Barrnap for rRNA, and GUNC with proGenomes 2.1.

To enable per-genome head-to-head comparison, legacy MAGs were assigned to the 920 genome clusters defined in the main benchmark (Section 1.8). Each legacy MAG's full GTDB-Tk classification string was matched against the classification strings present in existing clusters. When multiple clusters shared the same classification (cases where ANI sub-clustering resolved multiple species within one classification group), the legacy MAG was assigned to the cluster with the highest ANI similarity, computed directly with skani. Legacy MAGs whose classification strings were absent from any benchmark cluster were designated as legacy-exclusive genome clusters.

Community diversity was quantified at genus, family, and order levels using Shannon diversity ($`H' = - \sum_{}^{}{p_{i}\ln p_{i}}`$), Simpson's diversity ($`1 - D`$, where $`D = \sum_{}^{}p_{i}^{2}`$), and Inverse Simpson ($`1/D`$). Average Taxonomic Distinctness ($`\Delta^{+}`$) was computed following Clarke and Warwick (1998) as the mean taxonomic path length between all pairs of taxa in the presence/absence taxon list, where $`\omega_{ij}`$ is the taxonomic distance between taxa i and j (same genus = 1, same family = 2, through same domain = 6). Because CompleteBin recovers substantially more MAGs, raw Shannon and Simpson values are inflated by differences in richness and sampling effort. Rarefied diversity was therefore computed by randomly subsampling CompleteBin's MAG pool to the legacy pool size (n = 451) over 1,000 bootstrap iterations, producing 95% confidence intervals. $`\Delta^{+}`$ was reported without rarefaction because, unlike richness-dependent diversity indices, it is an average pairwise taxonomic-distance measure with low dependence on sample size when computed from presence/absence taxon lists (Clarke & Warwick, 1998).

### Yield and Quality Overview

CompleteBin MAM recovered 758 MQ+ MAGs compared to 451 for the legacy pipeline, a 68.1% increase (Figure S51A, Figure S51E). The advantage was present across all quality tiers: MQ bins increased from 321 to 578 (+80.1%), HQ from 113 to 141 (+24.8%), NC from 17 to 39 (+129.4%), and NC_QUNC from 13 to 29 (+123.1%). Per-MAG quality distributions showed the expected composition effect: legacy MAGs had higher median completeness (82.5% vs 73.6%), lower median contamination (1.45% vs 2.68%), higher median QS_5x (70.4 vs 59.4), and higher median contig N50 (7,181 vs 4,385 bp), all significant by Mann-Whitney U (p < 0.001; Figure S52). CompleteBin's distributions were broader across all four metrics, with higher density at lower completeness, higher contamination, and lower N50 values, reflecting the additional ~300 harder-to-bin MAGs at the lower end of the MQ spectrum. The aggregate quality gap is therefore driven by the composition of the MAG pool rather than per-genome inferiority, as confirmed by the head-to-head competition below.

### Head-to-Head Per-Genome Competition

The genome cluster matching identified 412 shared genome clusters where both pipelines recovered a representative. CompleteBin won 228 (55.3%), the legacy pipeline won 143 (34.7%), and 41 (10.0%) were ties within 1.0 QS_5x (Figure S51B). CompleteBin's wins were overwhelmingly completeness-driven (206 of 228, 90.4%), with a mean margin of 10.1 QS_5x per win. Legacy wins were primarily contamination-driven (87 of 143, 60.8%), with a mean margin of 9.6 QS_5x per win. Mean QS_5x for shared genomes was nearly identical (CompleteBin 73.5 vs Legacy 72.7), confirming that the aggregate quality difference is a composition artefact, not a per-genome deficit.

### Genome Exclusivity and Taxonomic Diversity

Of the 714 total genome clusters recovered by either pipeline, 412 were shared, 22 were legacy-exclusive, and 280 were CompleteBin-exclusive (Figure S51F). The 280 CompleteBin-exclusive clusters had lower median completeness (58.9% vs 68.4% for legacy-exclusive) and substantially higher median contamination (4.06% vs 1.17%), confirming they are harder-to-bin organisms recovered at the lower end of the MQ spectrum. CompleteBin-exclusive clusters contributed 58 novel families or deeper, compared to only 1 for legacy-exclusive clusters.

CompleteBin recovered more unique taxa at every rank: 47 vs 44 phyla (+6.8%), 82 vs 74 classes (+10.8%), 165 vs 143 orders (+15.4%), 236 vs 198 families (+19.2%), and 252 vs 202 genera (+24.8%; Figure S51C). Novelty depth comparison showed CompleteBin recovering more MAGs at every novelty level (Figure S51D), with the largest absolute gains at the novel species and novel genus levels. The number of novel families or deeper increased from 33 to 46 (+39.4%).

However, genus-level rarefaction (Figure S53) revealed that the raw diversity advantage is partly driven by sample size. At equal pool size (n = 451), CompleteBin's rarefied genus count was approximately 178, below the legacy pipeline's 202. Rarefied Shannon H' (95% CI: 4.92 to 5.08) fell below the legacy value of 5.17. This means legacy MAGs are more evenly distributed across genera per-MAG, while CompleteBin recovers more representatives within existing genera. Average Taxonomic Distinctiveness, which is inherently sample-size independent, told the complementary story. CompleteBin's $`\Delta^{+}`$ of 6.058 exceeded the legacy's 5.954, indicating that CompleteBin's MAGs span a more phylogenetically spread community, reaching into more distantly related lineages even if within-genus density is higher.

### Data Utilization, Purity, and Per-Sample Consistency

After dereplication and quality filtering (MQ+), CompleteBin captured 28.8% of total assembled sequence (1,786 MB) versus 16.9% for legacy (1,047 MB), a +70.6% increase. GUNC chimerism rates among HQ and NC MAGs were low for both pipelines: 3 of 130 (2.3%) for legacy and 7 of 180 (3.9%) for CompleteBin, indicating no meaningful purity trade-off.

Pre-dereplication per-sample recovery (Figure S54) confirmed that CompleteBin's advantage was consistent across depth layers, with a mean ratio of 1.56x (range 1.38x to 1.80x) across the 18 unaffected samples. Two samples (0 to 1 cm and 20 to 22.5 cm) showed a reversed pattern (CompleteBin recovering 10 and 1 MQ+ bins versus legacy's 40 and 86), attributable to assembly errors in the main benchmark pipeline that did not affect the legacy workflow.

### Summary

Replacing the legacy DAS Tool pipeline with CompleteBin MAM increases total MAG yield by 68.1%, NC MAG count by 129.4%, and recovers 280 additional genome lineages previously invisible, including 58 novel families or deeper. The per-genome quality for the 412 shared genomes is not compromised (CompleteBin wins 55.3% of head-to-head comparisons). The aggregate quality deficit (median QS_5x 59.4 vs 70.4) is explained by the composition of the additional harder-to-bin genomes, not by per-genome inferiority. The legacy pipeline's three input tools, in particular CONCOCT and MaxBin2 represent a 7 to 10 year technology gap relative to CompleteBin from 2025, and the yield difference reflects the cumulative improvement in binning algorithms over this period.

# Supplementary Materials - DISCUSSION

## S3.2 Algorithmic Incompatibility of GenomeFace and SemiBin2 with Cluster-and-Split Workflows

The Cluster-and-Split (CS) workflow induced only moderate yield degradation in most tools but caused severe failures in GenomeFace (HQ+NC drops from 136 to 35, -75%) and SemiBin2 (HQ+NC drops from 176 to 95, -46%) (Section 2.1). Both failures trace to specific algorithmic mechanisms triggered by the artificial sequence redundancy introduced when per-sample assemblies are concatenated: highly prevalent species present across many depth layers appear as up to 20 nearly identical contig copies in the concatenated reference, an artefact absent in true co-assemblies.

### Why Marker-Agnostic Binners Survive

VAMB (variational autoencoder), MetaBAT2 (graph-based composite-distance clustering), and COMEBin (contrastive multi-view clustering) cluster contigs strictly on latent feature-space proximity, with no internal evaluation of biological validity during partitioning. When presented with redundant contig copies of the same species, they project all copies into a single dense region of the latent space and assign them to a single Mega-Bin. The Mega-Bin is biologically aberrant (effectively 2000% completeness and 2000% contamination) but topologically coherent, and the post-processing demultiplexing step uses the original sample-of-origin headers to split the Mega-Bin into 20 valid per-sample sub-bins. Deferring redundancy resolution to post-processing is therefore the structural reason these tools tolerate the CS architecture.

### GenomeFace: Marker-Purity Collapse in the Acumen4 Step

GenomeFace constructs a Geodesic Minimum Spanning Tree from contig embeddings via HDBSCAN, then uses a custom algorithm class (Acumen4) to cut the tree by evaluating candidate clusters against Universal Single-Copy Marker Genes (USCGs). Acumen4 enforces a hard minimum purity threshold of 85% (min_purity default), computed as the fraction of unique markers over total marker copies. Under CS, the 20 redundant contig copies of a single species carry 20 copies of every standard marker gene. Acumen4 sees a candidate Mega-Bin with purity of approximately 5% (40 unique markers out of 800 total) and aggressively fractures the spanning tree in an attempt to reach 85% purity, slicing apart valid genomic structures because the redundant strains have near-identical sequence composition and cannot be cleanly separated. Lowering min_purity would allow the Mega-Bin to form but would also disable the algorithm's protection against true biological chimeras.

### SemiBin2: K-NN Edge Saturation in the Infomap Step

SemiBin2 generates contig embeddings via a Siamese neural network and clusters them with Infomap community detection on a k-nearest-neighbour (K-NN) graph, with the per-contig edge budget capped by the --max-edges parameter (default 200). To recover a complete genome spanning hundreds of contigs, Infomap requires an unbroken chain of stepping-stone edges that traverse the genome. Under CS in single_easy_bin mode, identical contigs from 20 samples land in the same dense region of the latent space, and a given contig's 200 closest neighbours are predominantly its own cross-sample clones rather than adjacent contigs of the same genome. The edge budget is exhausted on within-clone connections, the K-NN graph fractures into dense isolated cliques, and Infomap's random-walk traversal becomes trapped inside these cliques rather than completing genome-spanning communities. The result is heavily fragmented bins and a sharp HQ yield drop.

### Split-and-Cluster as the Designed Solution

Both tools provide native Split-and-Cluster (SC) modes that bypass these failures. GenomeFace's -s flag partitions the minimum spanning tree by sample-of-origin before invoking Acumen4, so the purity calculation operates on per-sample contig subsets that contain at most one copy of each marker gene and easily clear the 85% threshold. SemiBin2's multi_easy_bin command computes global co-abundance matrices across all BAM files but separates the concatenated FASTA back into individual sample FASTAs before K-NN graph construction, so the K-NN search operates within a single sample and never encounters inter-sample redundancy. Both tools recover near-MAM yields under SC.

### Implication for Workflow Choice

The CS architecture is safe for binners whose partitioning step does not actively evaluate marker-gene purity or rely on edge-limited graph clustering (VAMB, MetaBAT2, COMEBin, CoCoBin), because these tools defer redundancy resolution to post-processing. The architecture is incompatible with binners that enforce biological constraints during partitioning (GenomeFace) or rely on bounded graph topology (SemiBin2), and SC should be used in place of CS for these tools whenever the dataset is large enough to make CS computationally attractive in the first place.

# Supplementary Materials - FIGURES

![Figure S1: **Per-tool MAG yield by quality tier across all tool–workflow combina](MSc_RasmusAN_SDU_sup_final_v1_media/media/image1.png)

Figure S1: **Per-tool MAG yield by quality tier across all tool–workflow combinations.** Horizontal stacked bar chart in which each row is one tool–workflow combination and the bar length is the number of 95% ANI dereplicated MAGs, partitioned into MQ, HQ, and NC tiers (light-to-dark blue segments). All combinations are ranked top-to-bottom by total MQ+ yield, irrespective of workflow; workflow identity is conveyed by the semi-transparent row background (MAM blue, CS orange, SC green) rather than by grouping, so tools can be ranked directly across workflows. Each row is annotated with its NC count (just past the bar end, bold) and its total MQ+ count (at the right margin); MQ and HQ segment counts are printed inside segments. Ensemble tools (Binette, DAS Tool, MAGScoT) carry bold y-axis labels. The x-axis is the number of MAGs (95% ANI dereplicated).

![Figure S2: **Workflow-level MAG yield by quality tier under three tool-membershi](MSc_RasmusAN_SDU_sup_final_v1_media/media/image2.png)

Figure S2: **Workflow-level MAG yield by quality tier under three tool-membership strata.** Three stacked-bar panels of the total MAG count (MQ light, HQ medium, NC dark blue) summed within each workflow, with the total MQ+ count annotated above each bar. **(A)** Unrestricted: every tool that ran each workflow is pooled, so the bars reflect both per-tool performance and the differing number of tools per workflow. **(B)** Common-9 (MAM vs CS): restricted to the nine tools that ran both MAM and CS, making that pair directly comparable (SC is omitted because common-9 includes tools absent from SC). **(C)** Common-4 (All 3): restricted to the four tools that ran all three workflows (COMEBin, GenomeFace, SemiBin2, VAMB), the only fair three-way comparison.

![Figure S3: **Per-MAG QS_5x distribution by tool (MAM workflow)](MSc_RasmusAN_SDU_sup_final_v1_media/media/image3.png)

Figure S3: **Per-MAG QS_5x distribution by tool (MAM workflow).** Violin plots (light blue) of the QS_5x distribution of every MAG produced by each tool, overlaid with a jittered strip of individual MAGs (dark blue) and a black horizontal tick marking the tool median; tools are ordered left-to-right by descending median QS_5x. Horizontal dashed reference lines mark QS_5x = 50 (orange, the approximate HQ threshold) and QS_5x = 0 (red, where the 5× contamination penalty cancels completeness). Median QS_5x varies only modestly across tools while the lower tails differ markedly: tools recovering many low-quality MAGs show long downward tails and lower medians despite high total yield.

![Figure S4: **Per-tool workflow deltas, MAM minus CS and MAM minus SC (real bench](MSc_RasmusAN_SDU_sup_final_v1_media/media/image4.png)

Figure S4: **Per-tool workflow deltas, MAM minus CS and MAM minus SC (real benchmark).** Eight Cleveland dot panels (4×2) showing, for each tool, the difference between its MAM value and its CS value (orange circles, MAM − CS, common-9 tools) and its SC value (green diamonds, MAM − SC, common-4 tools), with a vertical line at zero marking parity. The sign convention is fixed so that positive always favours MAM. Panels, in reading order: ΔMQ+ yield, ΔHQ+ yield, ΔNC yield, and ΔNC_GUNC yield (counts of MAGs); ΔContamination (percentage points, computed as the CS/SC value minus the MAM value so that positive means MAM is less contaminated); ΔMean Completeness (pp); ΔMean QS_5x (QS points); and ΔData Utilization (pp, standalone tools only, ensemble tools excluded). Within each panel tools are sorted by the MAM − CS delta.

![Figure S5: **Competition size distribution (MAM workflow)](MSc_RasmusAN_SDU_sup_final_v1_media/media/image5.png)

Figure S5: **Competition size distribution (MAM workflow).** Bar chart of the number of genome clusters (y-axis) recovered by exactly N tools (x-axis, 1–11), with the count annotated above each bar. This defines the substrate of the per-genome competition framework: each genome cluster is one competition contested by the tools that recovered it. The distribution is U-shaped, with a fairly large number of clusters recovered by a single tool (uncontested singletons) and a large number recovered by 10–11 tools (near-universal), separated by a sparse middle.

![Figure S6: **Sensitivity of the per-genome contested win rate to the contaminati](MSc_RasmusAN_SDU_sup_final_v1_media/media/image6.png)

Figure S6: **Sensitivity of the per-genome contested win rate to the contamination penalty (MAM workflow).** Grouped horizontal bar chart of each tool's contested win rate, the percentage of the contested genome clusters it participates in (clusters also recovered by at least one competitor) that it wins, computed under two scoring functions: QS_5x (k = 5, strict contamination penalty; blue) and QS_2x (k = 2, moderate penalty; orange). Values are annotated beside each bar. The near-identical bar pairs for most tools show the win-rate ranking is robust to the contamination-penalty coefficient; the main exception is MAGScoT, whose more-complete-but-more-contaminated bins win substantially more often under the milder k = 2 penalty.

![Figure S7: **Pairwise win matrix (MAM workflow)](MSc_RasmusAN_SDU_sup_final_v1_media/media/image7.png)

Figure S7: **Pairwise win matrix (MAM workflow).** Heatmap in which cell (row tool A, column tool B) gives the percentage of the genome clusters recovered by both A and B in which A's best representative outscores B's on QS_5x; the diverging colour scale runs red (0%) through white (50%, parity) to blue (100%), and the diagonal is masked. The matrix is approximately antisymmetric (cells A,B and B,A sum to ≈ 100% minus ties) and exposes the full dominance hierarchy: the Binette row is uniformly blue (it wins 88–96% of head-to-head clusters against every other tool), while the CoCoBin row is uniformly red.

![Figure S8: **Properties of singleton versus multi-tool genome clusters (MAM work](MSc_RasmusAN_SDU_sup_final_v1_media/media/image8.png)

Figure S8: **Properties of singleton versus multi-tool genome clusters (MAM workflow).** Six box-plot panels comparing the MAGs from genome clusters recovered by only one tool (Singleton, red) against the MAGs from clusters recovered by two or more tools (Multi-tool, blue): Completeness (%), Contamination (%), Quality Score (QS_5x), Contig N50 (bp, log-scaled y-axis), Total Contigs, and Genome Size (MB). White diamonds mark means, the dark label inside each box marks the median, the sample size n (number of MAGs) is annotated above each box, and the two-sided Mann-Whitney U p-value with its significance marker is printed beneath each panel. Singletons are significantly less complete, more contaminated, lower-QS, more fragmented (lower N50, slightly more contigs), and smaller, confirming that the genomes only a single tool recovers are predominantly harder-to-bin organisms rather than high-value unique finds.

![Figure S9: **Completeness versus contamination sub-competition win rates in cros](MSc_RasmusAN_SDU_sup_final_v1_media/media/image9.png)

Figure S9: **Completeness versus contamination sub-competition win rates in cross-workflow head-to-head comparison (pooled, real benchmark).** Three panels, one per workflow pair (CS vs MAM, MAM vs SC, CS vs SC), each decomposing the pooled cross-workflow per-genome competition (the same tool reconstructing the same genome cluster under two workflows) into two independent sub-competitions: which workflow's MAG is more complete (Completeness) and which is less contaminated (Contamination). Paired bars give each workflow's pooled win rate on each axis (MAM blue, CS orange, SC green), with a dashed 50% parity line; the CS vs MAM pair is pooled over the common-9 tools and the SC pairs over the common-4 tools (within-pair bars do not sum to 100% because tied competitions are excluded). The decomposition shows MAM's overall advantage is driven by completeness, where it wins decisively, rather than by contamination, where the workflows are near parity.

![Figure S10: **Cross-workflow QS_5x margin distributions (real benchmark)](MSc_RasmusAN_SDU_sup_final_v1_media/media/image10.png)

Figure S10: **Cross-workflow QS_5x margin distributions (real benchmark).** A 3×2 grid of box plots with jittered points (tied competitions excluded). Rows are the three workflow pairs (CS vs MAM over the common-9 tools; MAM vs SC and CS vs SC over the common-4 tools); the left column shows each workflow's Margin of Victory (the QS_5x gap to the other workflow on the genome clusters it wins) and the right column its Margin of Loss (the QS_5x gap on the clusters it loses). Each box is one workflow (MAM blue, CS orange, SC green) and the y-axis is the absolute QS_5x margin. Contrasting a workflow's victory margins against its loss margins quantifies not just how often but by how much each workflow outperforms the other on matched genomes.

![Figure S11:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image11.png)

Figure S11:

![Figure S12:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image12.png)

Figure S12:

![Figure S13:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image13.png)

Figure S13:

![Figure S14:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image14.png)

Figure S14:

![Figure S15:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image15.png)

Figure S15:

![Figure S16:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image16.png)

Figure S16:

![Figure S17:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image17.png)

Figure S17:

![Figure S18:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image18.png)

Figure S18:

![Figure S19:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image19.png)

Figure S19:

![Figure S20:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image20.png)

Figure S20:

![Figure S21:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image21.png)

Figure S21:

![Figure S22:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image22.png)

Figure S22:

![Figure S23:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image23.png)

Figure S23:

![Figure S24:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image24.png)

Figure S24:

![Figure S25:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image25.png)

Figure S25:

![Figure S26:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image26.png)

Figure S26:

![Figure S27:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image27.png)

Figure S27:

![Figure S28:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image28.png)

Figure S28:

![Figure S29:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image29.png)

Figure S29:

![Figure S30:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image30.png)

Figure S30:

![Figure S31:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image31.png)

Figure S31:

![Figure S32:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image32.png)

Figure S32:

![Figure S33:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image33.png)

Figure S33:

![Figure S34:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image34.png)

Figure S34:

![Figure S35:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image35.png)

Figure S35:

![Figure S36:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image36.png)

Figure S36:

![Figure S37:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image37.png)

Figure S37:

![Figure S38:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image38.png)

Figure S38:

![Figure S39:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image39.png)

Figure S39:

![Figure S40:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image40.png)

Figure S40:

![Figure S41:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image41.png)

Figure S41:

![Figure S42:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image42.png)

Figure S42:

![Figure S43:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image43.png)

Figure S43:

![Figure S44:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image44.png)

Figure S44:

![Figure S45:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image45.png)

Figure S45:

![Figure S46:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image46.png)

Figure S46:

![Figure S47:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image47.png)

Figure S47:

![Figure S48:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image48.png)

Figure S48:

![Figure S49:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image49.png)

Figure S49:

![Figure S50:](MSc_RasmusAN_SDU_sup_final_v1_media/media/image50.png)

Figure S50:

![Figure S51: **Overview of the legacy DAS Tool pipeline versus CompleteBin MAM**](MSc_RasmusAN_SDU_sup_final_v1_media/media/image51.png)

Figure S51: **Overview of the legacy DAS Tool pipeline versus CompleteBin MAM**. **(A)** Quality-tier yield: paired vertical bars giving the MAG count in each tier (MQ, HQ, NC, and NC_QUNC), legacy vs CompleteBin MAM, with the count annotated above each bar and the CompleteBin/legacy fold change (×) above each tier pair. **(B)** Head-to-head per-genome quality: for every genome cluster recovered by both pipelines, the best (highest-QS_5x) legacy MAG (x-axis) is plotted against the best CompleteBin MAG (y-axis), with a dashed 1:1 parity line; points are coloured by winner (legacy, CompleteBin, or tie, where a tie is |ΔQS_5x| ≤ 1). **(C)** Taxonomic richness: paired horizontal bars of the number of unique taxa recovered at Phylum, Class, Order, Family, and Genus, annotated with each count and CompleteBin's percentage difference relative to legacy. **(D)** Novelty depth: paired horizontal bars of MAG counts by novelty rank parsed from the highest unassigned level of each MAG's GTDB-Tk classification (Known Species, Novel Species, Genus, Family, Order, Class, Phylum); MAGs carrying destructive GTDB-Tk placement warnings are excluded. **(E)** Percentage change vs legacy: horizontal diverging bars giving CompleteBin's percentage change relative to legacy on ten metrics (Total MQ+ Yield, HQ+NC Yield, Median QS_5x, Median Completeness, Purity [1 − median Contamination/100], GUNC Pass Rate, Median Contig N50, Data Utilization, Genus Richness, and Dark Matter Depth [count of Novel Family-or-deeper MAGs]); bars extend right (teal where CompleteBin is better and left (orange) where legacy is better, about a zero line. Data Utilization here is the all-bin, pre-dereplication metric (fraction of total assembly base pairs captured by every raw bin), distinct from the MQ+ dereplicated utilization reported in the text. **(F)** Genome-cluster overlap: an area-proportional two-circle Venn of genome clusters that are legacy-exclusive, shared, or CompleteBin-exclusive, with each pipeline's total MAG count labelled.

![Figure S52: **Per-MAG quality distributions: legacy DAS Tool versus CompleteBin ](MSc_RasmusAN_SDU_sup_final_v1_media/media/image52.png)

Figure S52: **Per-MAG quality distributions: legacy DAS Tool versus CompleteBin MAM.** Four split-violin panels, each showing the full per-MAG distribution of one quality metric with the legacy pipeline on the left half (orange) and CompleteBin MAM on the right half (teal): **(top-left)** Completeness (%), **(top-right)** Contamination (%), **(bottom-left)** QS_5x, and **(bottom-right)** Contig N50 (bp, log-scaled y-axis). In every panel the solid black line marks each pipeline's median (value annotated beside it) and the dashed lines mark the first and third quartiles; the boxed annotation reports the Mann-Whitney U two-sided p-value for the legacy-versus-CompleteBin difference. The panels visualise the composition effect underlying the aggregate quality gap: CompleteBin's distributions are broader and shifted toward lower completeness, higher contamination, and lower N50, reflecting the additional harder-to-bin MAGs it recovers at the lower end of the MQ spectrum.

![Figure S53: **Genus-level rarefaction of taxonomic richness](MSc_RasmusAN_SDU_sup_final_v1_media/media/image53.png)

Figure S53: **Genus-level rarefaction of taxonomic richness.** Bootstrapped rarefaction curves of the number of unique genera accumulated as a function of the number of MAGs randomly subsampled, for the legacy pipeline (orange) and CompleteBin MAM (teal); the solid line is the bootstrap mean and the shaded band the 95% confidence interval. A vertical dashed line marks the legacy pool size (n = 451), and the annotation box reports each pipeline's rarefied genus count at this equal sample size. The figure separates genuine richness from sample-size inflation: at equal n, the CompleteBin curve lies below the legacy curve, showing that CompleteBin recovers more representatives within fewer genera (denser within-genus sampling) rather than a more even spread of genera per MAG.

![Figure S54: **Pre-dereplication per-sample MAG recovery by quality tier](MSc_RasmusAN_SDU_sup_final_v1_media/media/image54.png)

Figure S54: **Pre-dereplication per-sample MAG recovery by quality tier.** Stacked grouped bar chart with two bars per depth-layer sample (legacy in amber, CompleteBin MAM in teal) along the x-axis, ordered over the 20 samples (depth layer in cm); the y-axis is the number of pre-dereplication bins. Within each bar, segments stack from bottom to top as MQ (lightest shade), HQ (mid), and NC (darkest), where tiers are assigned from CheckM2 alone (MQ: Completeness ≥ 50%, Contamination &lt; 10%; HQ: ≥ 90%, &lt; 5%). The legend distinguishes pipeline (colour) from tier (shade). CompleteBin's recovery advantage is consistent across depth layers, with two exceptions (0–1 cm and 20–22.5 cm) where legacy recovers far more bins; these two samples carry main-benchmark assembly errors that did not affect the legacy workflow.

# References

Clarke, K. R., & Warwick, R. M. (1998). A taxonomic distinctness index and its statistical properties. *Journal of Applied Ecology*, *35*(4), 523-531. <https://doi.org/https://doi.org/10.1046/j.1365-2664.1998.3540523.x>
