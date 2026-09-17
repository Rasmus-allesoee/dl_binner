# Initial Scientific Assessment

Date: 2026-09-16
Status: foundation assessment; current applicability is determined by [STATE](../STATE.md)
Decision: [D002](../decisions/D002-investigate-before-architecture.md)

Follow-up, 2026-09-17: the proposed audit/protocol block is complete. [D003](../decisions/D003-coverage-diagnostic.md) selects a public-data coverage diagnostic, with [E001](../../experiments/E001-coverage-thinning/README.md) as the prospective protocol. The earlier preference below for a new simulation is refined: use released CAMI data first when they already test the question, and custom simulations when additional causal control is needed. This assessment is retained as the starting reasoning, not a second current task list.

## Recommendation

The strongest immediate step is a **focused diagnosis of a recoverable failure in current binning methods**, supported by a targeted paper/code audit. Start by investigating missing or misassigned contigs in fragmented prokaryotic assemblies when coverage is weak or misleading. Establish whether the cause lies in the available information, its learned representation, or the clustering and selection procedure.

This is a provisional place to investigate, not a commitment to a new architecture. No residual gap, improvement, or novelty has yet been demonstrated. The first outcome may be that a current method or correct workflow already solves the apparent problem.

## Why this is the strongest starting point

The [thesis](../evidence/2026-09-16-thesis.md) provides unusual leverage: experience with real binning workflows, ground-truth simulation, contig and genome quality, tool failures, and computational costs. It identifies concrete phenomena to explain. Its strongest contribution to this project is that diagnostic understanding and infrastructure, rather than a fixed ranking of tools.

Three lessons matter immediately. First, changing mapping and clustering populations can change results substantially without changing the neural network. Second, better estimated MAG quality can conceal misassignment or selective loss. Third, some missing biological information never reaches the binner because of assembly. A new model cannot be justified until we know which of these situations we are addressing.

The [current method map](../evidence/2026-09-16-landscape.md) also narrows the opportunity. Taxonomy fusion, pretrained sequence representations, marker-guided contrastive learning, adaptive feature weighting, and probabilistic sequence representations all have prior art. Combining them is not by itself a novel method. A defensible contribution would show that a particular change fixes a measurable problem, beyond appropriate current alternatives, under conditions that matter biologically.

Fragmented assemblies and unreliable coverage are a useful initial focus because they connect directly to the thesis, allow controlled interventions, and may expose a meaningful recovery-versus-contamination tradeoff. The evidence does not yet show that they are the best final target. Long-read, graph, and reference-informed approaches stay in consideration.

## Working explanation to investigate

[H001](questions.md#h001) asks whether some binners lose usable information when the reliability of coverage varies across contigs or samples, even after their normal preprocessing. Perhaps treating all observed profiles similarly can lead to avoidable merges or unnecessary rejection of uncertain contigs.

This explanation is only one possibility. The same error pattern could arise from ambiguous read mapping, identical source sequence, insufficient sequence signal, badly matched clustering assumptions, marker-based selection, or incorrect baseline configuration. GenomeFace already uses adaptive weighting, and UncertainGen already proposes uncertainty-aware sequence representations. We must identify what remains unsolved before claiming a new idea.

An embedding is a numerical description of each contig, learned so that useful relationships can be represented. Clustering converts those descriptions into bin assignments. Good descriptions do not guarantee good bins: a clusterer can merge adjacent genomes or split one genome, and refinement can discard or reassign contigs afterward. This is why the first investigation must retain outputs from multiple stages.

## Serious alternative next steps

| Alternative | Why it could be worthwhile | Why it is not the first recommendation | Evidence that would change the choice |
| --- | --- | --- | --- |
| Replicate VAMB or train a small VAE immediately | Makes representation learning tangible and supplies a controlled baseline | Does not identify a scientific gap; published baseline code already exists | A small reproduction or toy example is needed to understand or test an important mechanism |
| Build a DNA-language-model binner | Potential extra information for short contigs or limited coverage | CompleteBin/DCVBin and related work already address this; reference overlap and cost need control | A cheap frozen-feature comparison finds complementary genome information on held-out genomes that simpler features lack |
| Start with clustering or selective assignment | May improve recovery/purity without a larger encoder | We have not shown that adequate information survives in the representation | Fixed-embedding experiments consistently recover sequence missed by native clustering, after fair tuning |
| Prioritize long-read/assembly-graph evidence | Could resolve ambiguities absent from short-read contig features | Needs a different data contract and closer comparison with LorBin, SCGBinner, and graph methods | The desired biological distinctions are absent from short-read inputs but supported by accessible graph/read evidence |
| Develop an independent quality estimator or ensemble | Direct response to thesis QC/refinement problems | Changes the immediate task and may reproduce proxy-optimization problems | Ground-truth analysis localizes most avoidable loss to selection/QC rather than representation or clustering |
| Run a large refreshed benchmark first | Establishes broad current performance | Expensive and easy to repeat the thesis without selecting a causal problem | A specific decision cannot be made from the targeted diagnostic set or needs broader confirmation |

## The next bounded block

### 1. Complete the relevant audit

Start with a small set spanning an inexpensive baseline, a simple learned baseline, and a strong contemporary method. The [landscape note](../evidence/2026-09-16-landscape.md) gives candidates and unresolved details. Pin the actual releases, verify recommended modes, and trace the relevant normalization, learning, clustering, and refinement paths. Expand only to the closest prior art for the emerging hypothesis.

Deliver a compact comparison of information used, assumptions, supervision, output access, known confounders, and reproducibility. Resolve the DCVBin input-description discrepancy and the role of marker constraints in the relevant tools if those methods enter the comparison. Do not spend this block exhaustively reviewing every cached tool.

### 2. Specify a diagnostic experiment before executing it

Select one concrete error regime and a small set of controlled conditions. Prefer a new simulation designed to isolate that regime. The thesis artifacts can supply realistic examples or debugging cases, but do not define the protocol. The owner confirmed that new simulations should be created where needed.

The prospective design should distinguish at least two questions:

- **Is the signal present?** On sequence with known origin, compare clean information with the suspected distortion while controlling all other inputs. For coverage, distinguish changes in overall scale from changes in relative profiles, zeros, or mapping ambiguity. Check effects after the tool's own normalization.
- **Where is usable signal lost?** Retain assignments, embeddings where meaningful, and pre/post-refinement outputs. Compare native end-to-end behavior with targeted stage controls. A common clusterer is one diagnostic, not a universal fair ranking of embeddings.

Use simple controls first: composition/coverage separately, a basic similarity or clustering baseline, and a no-intervention condition. An oracle that uses true origin can bound recoverability for diagnosis, but must be labeled as an oracle and never become an ordinary method or leak labels into evaluation-time decisions.

Do not independently add arbitrary noise to a coverage matrix and assume it models read-mapping competition. A perturbation can isolate sensitivity; its realism must later be checked against mapped reads or actual artifacts.

The exact dataset, genome pairs, contig lengths, sample covariance, seeds, repetitions, and budgets belong in the first real experiment protocol after the audit. They are intentionally not invented here. Keep the initial design small enough that a failure is cheap and interpretable.

### 3. Establish validity before interpreting performance

- **Truth and recoverability:** maintain contig origins, lengths, sequence hashes, and sample provenance; distinguish whole-genome recovery from recovery of the sequence actually assembled. Shared or chimeric sequences need an explicit truth policy. Do not assign an artificial unique truth label merely because the evaluator expects one.
- **Input/output integrity:** validate ID joins, filtered contig populations, duplicate assignments, augmented views, unassigned contigs, and base-pair accounting. Verify that assignment formats match the task before trusting a quality score.
- **Comparable information:** separate equal-input experiments from native recommended workflows. Record reads, assembly type, coverage columns, markers, taxonomy, and pretrained/reference information available to each method. Include preprocessing cost.
- **Leakage:** keep training, tuning, and final evaluation roles separate at genome/sample/community levels appropriate to the claim. Record reference and model-pretraining overlap, with `unknown` where it cannot be established. Fit-on-target unsupervised learning is a valid transductive setting when declared and applied comparably; it is not by itself label leakage. It does not demonstrate an encoder's generalization to unseen genomes.
- **Metrics:** use truth-based recovered bases and genome recovery together with purity/contamination, fragmentation, unassigned sequence, and runtime/memory. Record precise formulas and quality thresholds. Do not call completeness/contamination alone full MIMAG high quality; RNA requirements are separate. CheckM2/GUNC on real data are supporting estimates, not truth.
- **Inference:** use matched genomes and a fixed eligible population, not only intersections of successful outputs. Avoid treating thousands of correlated contigs as independent replicates. Record failures, timeouts, seed variability, and any configuration changes.

Use an established evaluator where it supports the truth contract; audit the relevant thesis conversion code before reuse. Do not build a general benchmark framework before this experiment needs one.

### 4. End with a decision

The block is complete when we have a sourced statement of a candidate gap, the closest existing approaches, a runnable or implementation-ready diagnostic protocol, and explicit predictions that distinguish the competing explanations. Record a decision to run it, change it, or move elsewhere. This foundation task stops before those scientific runs.

For the subsequent diagnostic results, use these directional rules; numerical effect sizes and resource limits must be fixed in its protocol before examining outcomes:

- **Keep:** the failure persists under correct native configuration, occurs in a relevant recoverable subset, and a targeted control supports the proposed cause beyond ordinary seed/configuration variation.
- **Modify:** the error is real but mostly reflects clustering, selection, representation geometry, or unrealistic simulation. Move the intervention to the supported cause.
- **Abandon:** the gap vanishes with current methods or preprocessing, the effect is not reproducible, or required information is absent. Preserve that result and choose another question.

## Learning through this work

Introduce composition/coverage geometry, latent representations, clustering, contrastive objectives, and uncertainty as their role becomes important. A small fixed-input example can show how the same embedding gives different bins under different clustering assumptions. A VAE or contrastive training exercise is useful if it resolves a live conceptual question; it is not a gate that must precede research.

Codex prepares and implements the technical work. The owner contributes biological judgment, critiques the reasoning, and controls UCloud execution. This preserves the destination of an original method while allowing evidence to choose the route.
