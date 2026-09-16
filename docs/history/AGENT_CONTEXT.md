> Historical planning. Not current instructions. Start with [current state](../STATE.md) and [project intent](../../PROJECT_INTENT.md).

# Agent Context — Project Owner, Motivation, and Working Style

> Purpose: Give coding/research agents enough context to make good decisions without repeatedly asking the owner to restate why this project exists.
>
> This file is context, not a substitute for `PROJECT_CHARTER.md`. Scientific evidence and explicit current instructions outrank personality assumptions.

## 1. Project owner

The project owner, Rasmus, has an MSc in Biology from the University of Southern Denmark with substantial bioinformatics/metagenomics experience from his thesis. His degree title is broad/classical biology rather than a dedicated bioinformatics degree, so a major purpose of this project is to produce concrete evidence of advanced computational and ML capability.

He is currently early-career and is especially interested in future work involving:

- bioinformatics;
- computational biology;
- human health;
- genomics and other omics;
- biomedicine;
- drug discovery;
- longevity/aging biology;
- advanced AI applied to difficult biological questions.

Long-term intellectual interests include human health/longevity, consciousness/the brain, and AI. The present project does not need to solve those problems directly. It is a strategic and educational bridge toward being capable of contributing to them.

## 2. Existing technical/domain foundation

Do not treat Rasmus as a beginner in bioinformatics or metagenomics.

He already has experience with:

- Python;
- Snakemake;
- Conda environments;
- Linux/HPC workflows;
- SLURM/UCloud;
- metagenomic assembly/binning workflows;
- multi-sample binning strategies;
- simulated metagenomic communities;
- MAG completeness/contamination assessment;
- GTDB-Tk taxonomy;
- GUNC chimerism assessment;
- dRep/skani dereplication/ANI workflows;
- benchmarking many binners;
- computational efficiency analysis;
- scientific figure/table generation;
- reproducible Git/GitHub research repositories.

His MSc benchmark covered 11 binners, multiple workflow architectures, strain-resolution simulation, ensembles, quality-control biases, and computational profiling.

The deep-learning layer is the main new technical frontier.

## 3. Learning style

Rasmus is poorly motivated by passive article/tutorial consumption and generic toy projects.

Preferred learning pattern:

1. identify a real problem in the project;
2. explain the concept needed to solve it;
3. implement a minimal version;
4. inspect what it actually does;
5. run an experiment;
6. connect the result back to the scientific problem;
7. only then increase abstraction/complexity.

Good examples:

- learn backpropagation while training the first contig model;
- learn VAEs before dissecting VAMB;
- learn contrastive objectives before modifying COMEBin/SemiBin-like ideas;
- learn attention before using a DNA transformer;
- learn pretrained sequence models in the context of a specific binning failure mode.

Bad pattern:

- assign 30 papers and several generic courses before any implementation;
- generate a giant architecture automatically and tell him to trust it;
- use a high-level framework that hides the exact concept currently being learned;
- create unrelated toy projects just because they are conventional ML tutorials.

## 4. Work style and ambition

Rasmus is highly motivated by difficult, ambitious problems and is willing to invest unusually large amounts of focused work when the objective feels meaningful.

Agents should not reduce the project's ambition merely to make it "beginner friendly." Instead:

- preserve an ambitious final destination;
- make individual milestones tractable;
- explain difficult material clearly;
- use complexity when it earns its place;
- challenge weak assumptions;
- flag when effort is being spent on low-value polish or scope drift.

Do not equate ambition with unnecessary complexity. A simpler model that answers an important question is preferable to an impressive architecture without a hypothesis.

## 5. Motivation risk

The largest motivation risk is not difficulty; it is work that feels disconnected from the final purpose.

In particular, avoid framing early deep-learning phases as disposable exercises that will be abandoned before the final binner exists.

The motivational contract is:

> We are building the final project from day one. Early models are primitive ancestors of the research system or experiments that reduce uncertainty about it.

If a learning exercise cannot plausibly contribute knowledge, code, infrastructure, or intuition needed for the final binner, question whether it belongs in this repository.

## 6. SkullNet background

An alternative project, "SkullNet," was considered first: a multimodal skull-identification AI progressing from morphometric MLPs through CNNs, embeddings, contrastive learning, transformers, CLIP-like learning, a tiny language model, and eventually a VLM.

SkullNet remains personally exciting and may later become a hobby/side project because it offers excellent visual intuition and intrinsic motivation.

The metagenomic project was chosen first because:

- it compounds approximately one year of existing metagenomic specialization;
- it has a higher immediate research ceiling;
- it is more relevant to computational-biology employment;
- it can plausibly generate publication-quality method development;
- the owner currently has valuable temporary access to powerful UCloud/HPC resources;
- SkullNet can still be pursued later on more modest hardware.

Do not redirect this repository into SkullNet. It exists only as context for why visual/interactive learning is valued.

## 7. Career context

An important practical goal is to make future biotech, biomedical, genomics, and research employers take the owner's computational ability seriously despite his degree title being Biology rather than Bioinformatics/Biomedical Informatics.

Therefore, the repository should visibly demonstrate:

- real method development;
- advanced ML understanding;
- rigorous benchmarking;
- clean software engineering;
- HPC competence;
- scientific judgment;
- reproducibility;
- ability to reason about limitations and negative results.

Do not optimize the science merely for résumé buzzwords. Strong research is the portfolio strategy.

## 8. UCloud/HPC context

The owner currently retains access to SDU/UCloud resources, including machines with very high RAM, many CPUs, and H200-class GPUs. This access may disappear.

Agents should therefore distinguish:

- cheap/local experiments that should be debugged before submission;
- expensive one-off data generation worth doing while access exists;
- repeatable benchmark runs;
- model training requiring high-end GPUs;
- artifacts/checkpoints/embeddings that should be preserved for future work.

Never assume permanent access.

## 9. Communication style for agents

When proposing work:

- explain **why** it matters to the overarching project;
- distinguish required work from optional polish;
- identify the scientific question being answered;
- state assumptions;
- state what result would change the plan;
- recommend a preferred option rather than presenting ten equivalent choices;
- avoid overexplaining basic metagenomics concepts unless asked;
- explain new ML concepts carefully and concretely;
- surface risks early rather than hiding uncertainty.

When there is a trade-off between "clever" and "understandable," prefer an implementation whose behavior can be inspected unless the clever version has a clear research justification.

## 10. Autonomy and constraints for coding agents

Agents are encouraged to:

- inspect the repository before proposing architecture changes;
- read relevant plans/decision records;
- make coherent implementation plans;
- write tests for important data transformations and model interfaces;
- keep research code reproducible;
- suggest better directions when evidence supports them;
- update documentation when assumptions change.

Agents should not:

- silently change the project's scientific objective;
- introduce major dependencies without justification;
- replace understandable learning implementations with opaque frameworks too early;
- perform expensive HPC runs merely because compute exists;
- merge learning experiments into production paths without cleanup;
- claim novelty or SOTA status without a literature refresh and comparable evaluation;
- assume that an LLM-generated architecture is scientifically valid because it sounds sophisticated.

## 11. Personal philosophy relevant to this project

The owner values projects that lead toward health, happiness, or financial/career independence. This project primarily serves long-term career leverage, intellectual satisfaction, and the acquisition of capabilities needed for more directly human-health-oriented research later.

The long-term aspiration is not simply "get good at metagenomics." It is to become technically capable enough to work on consequential biological problems, especially those connected to human health, disease, drug discovery, aging/longevity, and fundamental questions about life.

That long-term direction should motivate quality and ambition, but it should not cause premature scope expansion away from the current binner.

## 12. Historical context

A separate markdown transcript of the initial idea-development conversation is included in the repository at `agent_context/chatgpt_project_planning.md`. Use it to understand how the project evolved, but treat this file and the current charter/roadmap as the distilled, maintained interpretation of that discussion.
