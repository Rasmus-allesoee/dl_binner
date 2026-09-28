# E001: Where Does Reduced Coverage Evidence Lose Recoverable Sequence?

Date: 2026-09-17. Updated: 2026-09-27
Execution status: seed-11 MetaBAT2/VAMB pair accepted; COMEBin paired pilot prepared at 8 vCPU / 24 GB
Scientific outcome: preliminary paired effects differ by tool; no conclusion on H001 or COMEBin-specific criteria
Protocol: prospective v2; [config.json](config.json) owns numerical settings; only the next seed-11 COMEBin pair is prepared, not the remaining seeds
Questions: [Q001](../../docs/research/questions.md#q001), [Q003](../../docs/research/questions.md#q003), [Q004](../../docs/research/questions.md#q004); hypothesis [H001](../../docs/research/questions.md#h001)
Decision: [D004](../../docs/decisions/D004-human-cpu-preflight.md), superseding D003's execution choices; evidence: [method audit](../../docs/evidence/2026-09-17-targeted-audit.md), [human/CPU audit](../../docs/evidence/2026-09-18-human-cpu-audit.md). Execution: [operations guide](OPERATIONS.md); checks: [validation record](validation.md).

## Question and limits

Input-contract clarification (2026-09-18): six corrected-truth coordinate groups have two anonymous IDs but only one physical FASTA record. Accept these as aliases only when every non-ID truth field agrees; choose the numerically smallest PC ID and preserve all source IDs in provenance. Count the FASTA sequence once; leave conflicting mappings as errors and the 2,500-bp cutoff unchanged. The [validation record](validation.md) owns the observed cases and tests. This is a documented canonicalization of this development dataset, not a change to scientific endpoints or an unmodified anonymous benchmark input.

On one fixed known-origin assembly, does reducing mapped read evidence cause a material recovery loss in current binners, and does the evidence point to filtering, available signal, representation, or clustering/selection?

The first target is **sampling reliability**, not all forms of misleading coverage. Holding assembly fixed isolates the binner's response; it deliberately omits the assembly deterioration that lower sequencing depth would cause in an end-to-end workflow. Neither weaker performance after thinning nor better performance with truth labels proves an avoidable methodological failure.

An embedding is a learned numerical representation; clustering turns it into bins. We preserve both because a useful representation can still produce poor bins. This experiment diagnoses where to investigate next; it does not create our new method.

## Data and fixed population

2026-09-19 amendment: [D005](../../docs/decisions/D005-gi-input-derivative.md)
quarantines 20 exact foreign-simulation intervals (28,917,470 bp) and two empty
artifacts under a source-hash-bound policy. All corrected-truth coordinates remain
subject to the same length cutoff. This supersedes the all-GSA wording below only
for these enumerated records. E001 uses a declared development derivative;
mapping competition changes and the intended missing GI genomes are not restored.

Use CAMI II HMP's ten **gastrointestinal** short-read samples and the D005 derivative of its body-site-specific pooled GSA, with corrected contig-origin truth. This is human-associated development data, not clinical evidence or an untouched final test. Locators, publisher checksums and actual GI sample IDs are in the [acquisition manifest](acquisition.json). Do not use the shared gastrooral pooled reference or assume that samples 0-9 are all GI. Owner taxonomy-aware preparation is accepted; [frozen inputs](frozen-inputs.json) fix the reference, truth and evaluation population. Any subsequent population change requires a recorded amendment, not overwriting this accepted attempt.

Before any binning scores are examined:

1. Verify the original GSA/truth ID and length joins, sample identities, source metadata and hashes. Retain the original files unchanged.
2. Create one canonical input FASTA with all GSA sequences **at least 2,500 bp**, preserving sequence content. Join the GI FASTA's source-coordinate headers to the corrected mapping's anonymous `PC...` IDs by accession, inclusive interval and exact length, never row order. Preserve the ID translation and sequence hashes; source-bearing names do not enter binners. Selection uses length only, not taxonomy, coverage or tool success. Map against this exact reference. This common support restriction excludes shorter contigs and changes mapping competition relative to the complete GSA; conclusions are restricted accordingly.
3. Establish an immutable manifest for every input contig: ID, length, sequence hash, source genome(s), domain if known, ambiguity flags, and inclusion/exclusion reasons. No source labels appear in model features or renamed FASTA IDs.
4. Define `U`, the conservative evaluation subset: single-owner truth contigs assigned to bacteria/archaea, excluding confirmed chimeras and exact sequence/reverse-complement duplicates assigned to different source genomes. Keep excluded/ambiguous/non-prokaryotic sequences in the binner's input and account for their bases separately. Single-owner truth does not prove that available features identify that origin.
5. Freeze genome population `G`: every source genome with at least 200,000 bp in `U`. Report genomes/bases outside G, rather than silently dropping them. All members of G remain in every condition, including wholly unassigned genomes. If domain/source identity cannot be established, resolve that contract before calling the primary endpoint prokaryotic.

No genome selection based on preliminary binner performance. No extra fragmentation, strain selection, or assembly is performed in this protocol. The original GSA is error-free source sequence, not a realistic assembler output. Before training, require at least 20 genomes in G and at least 100 eligible short probe queries (2,500-9,999 bp) spanning at least ten genomes. These are minimum interpretability checks, not a statistical power calculation. Failure triggers a documented redesign before scores, not hidden replacement. Report ambiguity fractions even when these gates pass.

## Conditions

| Condition | Intervention | Purpose |
| --- | --- | --- |
| C0: full mapped evidence | All canonical primary mapped alignments from all ten samples | Reference condition; not called perfect coverage or an oracle |
| CS: scale-only control | Multiply each C0 coverage mean by 0.1 and depth variance by 0.01 before native normalization; recompute dependent totals and square roots consistently | Feature/preprocessing control for multiplicative depth scaling, with no sampling noise. Not simulated low-depth reads |
| CT: thinned evidence | Keep 10% of read templates independently within each sample; both mates and retained alignments of each template receive the same selection. Recompute all native coverage features from the thinned BAMs | Paired stochastic reduction in observations at fixed assembly, reference and sample count |

Use [samtools 1.24 `view --subsample`](https://www.htslib.org/doc/samtools-view.html), not a new sampling algorithm. Always thin the original C0 BAM, never an already thinned file. Use explicit seeds and verify pair consistency on fixtures. Do not multiply variance by 0.01 for CT: thinning changes variance and zeros, so these must be measured again. The CS variance rule instead describes deterministic scaling of a depth signal.

CS is initially a **preprocessing-only** control: compare accepted IDs, profile features, total-abundance features, variance channels and zero handling with C0. VAMB's uniform column scaling should cancel up to numerical effects. COMEBin's fixed pseudocount can prevent exact cancellation, particularly near zero. MetaBAT2's absolute-depth filters need not be invariant. Record actual differences; never assert a blanket invariance across tools. CS does not require redundant full model runs when features are effectively unchanged. A material discrepancy is investigated before interpreting CT.

This test does not model contig-specific mapping bias, competing assembly references, compositional GC bias, or correlated biological samples. A follow-up custom simulation would be needed to distinguish those mechanisms. Do not label arbitrary matrix noise as read-mapping competition.

## Native baselines and information access

Use the exact `metabat`, `vamb`, `COMEBin` and `AMBER_evaluation` audit commits in [tool snapshots](../../docs/evidence/2026-09-17-tool-snapshots.json). Pin runtime dependencies and bundled marker-file hashes during preflight; cloning a branch head again is not a version pin. If a release replaces an audited snapshot, trace the affected paths and amend this protocol before runs.

- **MetaBAT2:** native depth-mean/variance input, default scientific thresholds, nonzero random seed, `--saveCls` and `--unbinned`. Do not use `--cvExt` or disable recruitment merely to simplify the adapter.
- **VAMB:** `bin default`, native VAE and clustering, no TaxVAMB/Taxometer or marker reclustering. Use native BAM-derived trimmed coverage. Retain `latent.npz`, `model.pt`, identifiers and the full cluster assignments. Keep default training schedule (300 epochs at this snapshot), with explicit seeds/resources.
- **COMEBin:** the inspected 1.1.0 pipeline, six views, mean plus square-root variance, default max normalization, 200-epoch maximum with native early stopping, batch size 1,024 and native N50-dependent temperature. Generate augmentation intervals once and reuse them across C0/CT and replicates; preserve their hash. Recompute coverage for **every view** after thinning. Retain the complete Leiden candidate grid, marker estimates, chosen partition, full labels and final bins. Quality-threshold output subsets are supplementary, not the primary result.

The canonical input population is common; native feature estimators and marker use are not artificially made identical. Comparisons between tools are descriptive. The controlled causal contrast is within a tool. No source genome IDs, truth-derived abundances, taxonomic labels or oracle cluster counts enter training/selection. Target-data unsupervised fitting is declared transductive, not an unseen-genome generalization experiment.

Use existing model implementations; permissible adapter changes only export intermediate arrays/IDs, isolate run directories, or fix documented compatibility issues without changing the scientific algorithm. Preserve patches with hashes and fixture tests. Use a fresh clone/worktree for execution rather than editing the owner's reference caches.

## Mapping and reproducibility

Use **strobealign 0.17.0**, provisionally, for paired-read full SAM alignment to the canonical FASTA, with native defaults, explicit 150 bp read profile, thread/read-group settings and verified mate layout. Do not use `--aemb`, PAF mode, mutable development `main` or secondary-alignment reporting. Use samtools 1.24 for sorting, indexing, validation and thinning. Record exact package builds/binary hashes before execution. Retain primary mapped records (`-F 2308` excludes unmapped, secondary and supplementary records), with no extra MAPQ cutoff; low-MAPQ evidence remains visible. Do not use source-genome simulator BAMs as competitive contig mappings. A bounded fixed-prefix comparison with Bowtie2 and measured resource use precede full mapping; scientific binner scores cannot select the mapper. See [alternatives and rationale](../../docs/evidence/2026-09-18-human-cpu-audit.md#mapper-alternatives).

Verify archive read layout before writing the final mapping command: interleaved and separate-mate files are not interchangeable. Preserve read/sample identities. Record mapper arguments, library statistics, flag/MAPQ distributions, mapped pairs, reference `SN/LN` headers, and all feature-extractor options. A mapper failure or wrong-reference BAM stops the experiment.

Replicates are fixed prospectively:

- Training/clustering seeds: **11, 23, 47**, paired between C0 and CT for each method. MetaBAT2 seed zero means random and is not used.
- CT sampling seed for sample index `s` in replicate `r`: `1000 * (r + 1) + s`, with `r=0..2`, `s=0..9`. Reuse each thinned BAM across all methods.
- COMEBin sequence-augmentation seed: **101**, fixed across all conditions; training stochasticity remains separate.
- Run the first paired replicate across the three methods as the resource pilot, then the other two if integrity/resource checks pass. The pilot remains in the results; never retain only the best seed. Maximum: **18 native binner runs, including 12 learned-model fits**, excluding optional follow-up work.

Three paired replicates measure combined sampling/training variability, not three independent microbial communities. If separating these variance components becomes necessary, that requires an explicit later factorial design.

## Endpoints

### Primary: purity-constrained assembled-sequence recovery

For genome `g` in fixed G, let `A_g` be its total bases in U. For predicted bin `b`, let `L_b` include **all** assigned input bases, and let `T_bg` be bases from U belonging to g. Define:

```text
P_bg = T_bg / L_b
R95_g = max({T_bg / A_g : L_b >= 200000 and P_bg >= 0.95} union {0})
R95 = mean over the fixed genome set G of R95_g
Delta = R95(C0) - R95(CT)
```

`P_bg` is a conservative confirmed-origin fraction: ambiguous/unscored bases are not credited as true positives, but remain in the bin denominator. Its complement is an upper bound on impurity, not proof that every ambiguous base is contamination. Report the excluded mass and the standard AMBER result beside it. This construction keeps primary denominators fixed even if an evaluator supports alternative truth associations.

Count unassigned genomes as zero, and use only the best qualifying bin per genome so fragmentation is penalized. Break equal-recovery bin ties by lexicographic native bin ID, never by favorable short-contig recovery. Also report the base-weighted version, all per-genome values, and inclusive recovery counts at `R95_g >= 0.5` and `>= 0.9`. These are **assembled-sequence** endpoints, not whole-source-genome completeness or MIMAG quality.

Run the pinned AMBER unchanged on the canonical input truth and native assignments with no small-bin-tail exclusion (`--filter 0`). Retain its per-bin/per-genome tables and strict-threshold labels. E001's inclusive thresholds intentionally differ at exact boundaries. Do not claim identical values for the conservative subset and AMBER's full/multi-origin population.

### Secondary: locate the loss

- Base accounting: assigned, unassigned, filtered, ambiguous, out-of-domain and wrong-origin bases; raw clusters versus output-size/quality filtering. Preserve all contig IDs, including zero-depth rows.
- Fixed length strata: `[2500,5000)`, `[5000,10000)`, `[10000,50000)`, `[50000,infinity)` bp. Within each genome use its qualifying primary bin when scoring recovery of a length stratum; never recompute purity only on convenient short fragments.
- Coverage reliability: C0/CT native means, variances, read support, zeros and post-normalization changes. Fix coverage strata from C0 (genome median depth quartiles); do not reclassify genomes after treatment.
- Representation diagnostics: exact 10-neighbor same-origin fraction in composition-only, coverage-only, equal-block normalized concatenation, and learned embeddings. Use cosine distance on L2-normalized nonzero blocks; zero rows have no evidence and are reported separately. Use each method's actual normalized feature blocks. For VAMB include its total-abundance feature in the coverage block. Freeze query IDs before looking at results; exclude self, augmented siblings, and cross-origin identical-sequence copies. Restrict this probe to fixed unique-origin genomes with at least 11 eligible contigs, reporting the excluded population. Cap at 10,000 hash-selected queries (`SHA256("E001-probe:" + ID)`, lowest hashes), searching against the full eligible reference set in batches. Labels only score neighbors, never choose them. These are conditional separability diagnostics, not an implementable oracle binner or calibrated probabilities.
- Selection diagnostic: for each fixed COMEBin embedding, evaluate all **already generated native** candidate partitions and compare native selection with the truth-best candidate under R95. This is a clearly labeled oracle upper bound using evaluation truth. Do not return its choice as an ordinary baseline or mix it into the main method ranking.
- Runtime, peak RAM, allocated vCPU-hours and observed process CPU time, separated into setup, mapping, feature extraction, training, clustering and evaluation. No GPU is available. Count allocation/idle time for the owner's budget, not just process CPU time or neural inference.

Report per-replicate paired effects and distributions over fixed genomes. Contigs and ten coverage columns are not independent biological replicates. No population-level significance or cross-environment robustness claim follows from this single-community experiment.

## Decision rules fixed before results

- **Proceed to a focused intervention test:** mean Delta is at least **0.05 absolute R95** in COMEBin, positive in all three paired replicates, and stage evidence identifies a plausible avoidable component. A candidate-selection gap of at least **0.03 R95** at fixed embeddings supports examining selection. Alternatively, a raw-feature-to-embedding neighbor-purity drop of at least **0.10** on at least **5% of the fixed eligible short-query bases** supports investigating representation loss. These are project triage thresholds, not statistical significance or novelty criteria. Neighborhood evidence must involve the same contigs that lose correct recovery, not a disjoint easy subset.
- **Modify direction:** a reproducible error is predominantly input filtering, final size/marker selection, or ordinary configuration. Test that narrower cause. If a contemporary alternative already handles it, do not build a redundant method.
- **No support in this setting:** no material reproducible loss, or degraded neighborhoods in both raw and learned spaces without evidence of retained signal. Do not escalate noise severity to manufacture a gap. This does not refute H001 for all communities or mapping biases.
- **Inconclusive:** joins, truth, source versions, baseline convergence or resources are invalid; the target length stratum is insufficient; or seed variability dominates the proposed effect. Technical failure is not zero biological recovery.

Prior art comparisons with QuickBin's appropriate published/development mode, McDevol and GenomeFace are required before promoting a resulting reliability idea to a new-method claim. A high oracle score only motivates a test of a realizable procedure.

## Implementation and execution gates

**Gate 0: native smoke/CPU, clustering/marker/evaluator and mapper/storage checks accepted.** The [harness](../../scripts/e001.py), [tests](../../tests/test_e001.py), native feature/output adapters and synthetic smoke jobs implement input/provenance checks, conservative summaries, neighborhood probes and controls. Established Biopython/pysam parsers and samtools are used. The [validation record](validation.md) separates software checks and real prefix diagnostics. No model training was required. [D008](../../docs/decisions/D008-mapper-and-first-preprocessing-slice.md) retains strobealign after the existing BAM/read-truth analysis; do not repeat preflight.

Each predicted partition must assign a contig to at most one bin; unknown IDs, duplicate rows and cross-bin duplicate assignments fail preflight. Multiple possible origins in the **truth** are different and must be retained explicitly. Export feature/embedding masks and IDs, verify every join, and account for dropped input rows as unassigned rather than removing them from evaluation. Never repair overlapping predictions by silently assigning a contig to the largest bin.

The [operations guide](OPERATIONS.md) owns commands and runtime status. Core tool installations and the Snakemake 9.13.7 workflow environment have accepted native execution and returned dependency records. Preserve resolved identities and inspect returned outputs before scientific fits. Do not substitute tool/PyTorch versions and call it native parity. Scientific fitting/clustering orchestration completed for MetaBAT2/VAMB; COMEBin full training and selection remain owner-run validation.

**Gate 1: acquire and inventory the public data.** The prepared acquisition command downloads only GI GSA, corrected/original truth, setup and small metadata, verifies publisher checksums, and safely inventories archives without extracting them. It cannot download read archives. Resolve historical taxonomy and full coordinate joins before freezing the population. An initial taxonomy-free inventory is explicitly blocked, not approved for science. The [operations guide](OPERATIONS.md) owns commands, storage estimates and return-artifact instructions. If data access or an input contract fails, amend rather than fabricate a path/checksum.

**Gate 2: CPU feasibility, then owner-run pilot and paired runs.** Return-artifact inspection, native parity, full-batch CPU throughput, read-prefix mapping/storage checks and owner confirmation are prerequisites. The [configuration](config.json) replaces every old GPU/resource allowance: CPU only, a bounded fraction of the owner's allocation, nested preflight/preprocessing/per-fit ceilings, and storage headroom. These are stop/review limits, not measured requirements. If the full schedule or retained population exceeds a ceiling, stop and amend before scientific results. Storage exceeding the planning threshold instead triggers provisioning review: the owner can expand storage, so do not shrink the scientific design to fit the initial quota. Do not take a score-dependent subset, shorten native training or silently remove COMEBin. A COMEBin-free diagnostic cannot satisfy the current COMEBin-specific triage rule. The complete three-seed design remains intended, not promised affordable.

Before Gate 2, commit executable code/configuration and record that pre-existing Git commit, resolved tool/dependency versions, database/model hashes, commands, inputs, seeds, hardware and environment. Numerical settings are owned by `config.json`; this document explains their scientific meaning. Runtime locks and scientific launch validation remain outstanding, not silently implied by the source pins.

## Attempts and results

The seed-11 MetaBAT2/VAMB pair is accepted in [paired-pilot-observed.json](paired-pilot-observed.json). Both 300-epoch VAMB fits completed; native partitions, frozen denominators, paired embedding axes and AMBER/R95 results pass independent checks. R95 is 0.44294→0.19502 for MetaBAT2 and 0.46177→0.48764 for VAMB (C0→CT). These are single-seed development observations, not evidence that coverage thinning consistently hurts learned representation. MetaBAT2's native emitted support falls from 22,432 to 1,949 contigs; missing/zero-cluster contigs remain unassigned in the fixed evaluation population. VAMB assigns all 22,594 in both conditions. Stage diagnostics and COMEBin remain necessary.

Preprocessing, [features](features-observed.json), and the seed-11 MetaBAT2/VAMB pair remain accepted; do not repeat them. COMEBin C0 completed, while CT reached epoch 100/200 before the driver hit a missing attempt-path error during log monitoring. The returned evidence shows normal native progress, not a COMEBin training/OOM exception. The prepared [resume](OPERATIONS.md#current-action-2026-09-28-resume-the-unfinished-comebin-condition) verifies and reuses C0, preserves CT's partial files, and restarts CT from epoch 1 because COMEBin did not save a mid-fit checkpoint. Snakemake dry-run must exclude C0 before execution. Environment ownership follows [D006](../../docs/decisions/D006-environment-ownership.md).

Resource correction, 2026-09-21: [D007](../../docs/decisions/D007-comebin-resource-envelope.md) and [compute-policy.json](compute-policy.json) restore COMEBin's 80-core-hour limit after the owner clarified actual 2-vCPU allocation. Six fits project 287.3 core-hours with margin, no longer exceeding the 800 total before overhead. Frozen configuration and raw observed records remain unchanged. Remaining replicates still require measured pilot cost before authorization, independent of biological scores.

Every later attempt gets a unique `run-NNN` entry with status, condition/seed, source/config/input hashes, logs and output locations, including crashes/timeouts. Never overwrite a previous run directory. Legal empty output is evaluated as zero recovery with undefined purity where appropriate; a crashed or truncated output is not.

## Retention and amendments

Retain source archives/checksums, canonical FASTA/truth and inclusion manifests, C0 mapping provenance, fixed augmentation intervals, native features/embeddings with IDs, all candidate/final labels, logs, complete resolved configurations and compact result tables. Bulk artifacts remain outside Git. Thinned BAMs are regenerable from pinned C0 BAMs, samtools version and seeds; deletion still requires a recorded retention decision. Return compact manifests, checks, resource logs and tables from UCloud; inspect them before interpreting or marking completion.

2026-09-17: initial prospective design. No results were available when conditions, thresholds and gates were selected. Subsequent changes must state date, reason and whether any outcome was already visible.

2026-09-18, v2, [D004](../../docs/decisions/D004-human-cpu-preflight.md): replace Marine with HMP GI, BWA-MEM2 with provisional released strobealign, and GPU/large-storage assumptions with CPU-only measured-feasibility gates. Add explicit source-header anonymization after inspecting GI file prefixes. No scientific outcomes had been observed. The v1 protocol remains recoverable in commit `bc1a3c5`; its old resource allowances are not current.
