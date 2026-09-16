# Project Intent

## Purpose

This repository is the beginning of a long-term research project to develop, implement, and rigorously evaluate our own novel metagenomic genome-binning method.

The ambition is high: produce a scientifically defensible method that can compete with contemporary state-of-the-art approaches, either overall or in a clearly defined and biologically meaningful regime.

The project is not intended to be a tutorial exercise, a simple reproduction of an existing binner, or a portfolio-only demo. It should grow into a serious research and method-development effort.

At the same time, this project is also my route into modern deep learning and AI for computational biology. I want to learn the important concepts by using them in a real research problem rather than by following a predetermined beginner curriculum.

The final goal is fixed. The path is not.

---

## Background

I recently completed an MSc in Biology with a strong computational/bioinformatics focus.

My MSc thesis centered on metagenomic genome binning. During that work I developed substantial practical experience with:

- metagenomic assembly and genome binning;
- modern binning tools and their different strategies;
- multi-sample binning workflows;
- strain-resolution challenges;
- simulated and real metagenomic datasets;
- MAG quality assessment;
- taxonomy, contamination, and chimerism evaluation;
- benchmarking methodology;
- Snakemake;
- HPC/UCloud;
- reproducible computational workflows;
- scientific analysis and interpretation.

My previous benchmark project is available under `agent_context/` and should be treated as important prior work and background knowledge.

This new project should build on that foundation rather than recreate it.

---

## Why this project

There are three main reasons for choosing this project.

### 1. Scientific and technical continuity

Metagenomic binning is currently the area of bioinformatics where I have the deepest knowledge. Developing a new binner lets me compound that existing expertise rather than starting from zero in an unrelated domain.

### 2. Deep-learning development

Modern binning methods increasingly use deep representation learning, self-supervision, contrastive learning, variational models, graph methods, transformers, genome-language-model representations, and related ideas.

This creates a natural environment for learning modern deep learning through a real scientific problem.

### 3. Career and research value

The project should demonstrate that I can do more than apply existing bioinformatics tools.

The long-term goal is to show that I can:

- understand a difficult computational-biology problem deeply;
- study and critique existing methods;
- formulate research hypotheses;
- design and implement new methods;
- train and evaluate modern ML models;
- work with large biological datasets and HPC;
- benchmark methods rigorously;
- interpret results scientifically;
- produce research-quality software and potentially publishable work.

The project should strengthen my path toward computational biology, biomedical AI, genomics, human health, drug discovery, and related research areas.

---

## Ultimate destination

The destination of this project is a completed metagenomic binning method of our own.

“Completed” means more than having a model that runs.

The eventual method should have:

- a coherent scientific motivation;
- a clearly defined problem or limitation it aims to address;
- an architecture and algorithm justified by that problem;
- a reproducible implementation;
- appropriate training and inference workflows;
- rigorous evaluation against relevant existing methods;
- meaningful ablations and controls where needed;
- computational-resource measurements;
- honest analysis of strengths and limitations;
- enough evidence to support whatever performance or novelty claims we make.

State-of-the-art performance is an ambition, not something to assume in advance.

A method that produces a meaningful improvement in a specific regime, exposes an important trade-off, or introduces a genuinely useful new approach can still be a successful research outcome even if it does not dominate every benchmark.

However, the project should not be intentionally stopped at the “learning exercise” stage. The learning process exists to help us reach the final method.

---

## How I want to work

Codex should act as my primary research engineer, coding agent, and technical guide.

I do not intend to manually write the implementation myself.

My role is mainly to:

- define and refine the scientific goal;
- bring my biological and metagenomic knowledge;
- understand the important concepts and how they connect;
- question assumptions;
- evaluate scientific reasoning;
- interpret results;
- make high-level decisions together with Codex;
- decide which problems are worth pursuing.

Codex should handle most of the detailed coding, repository maintenance, implementation, debugging, literature/code investigation, and technical execution.

This does **not** mean that understanding is unimportant.

I want enough conceptual understanding to reason intelligently about the system and the research.

When a concept becomes relevant, explain:

- what it is;
- why it matters here;
- how it connects to the rest of the method;
- what assumptions it makes;
- what alternatives exist;
- what the practical consequences are.

Small educational experiments, diagrams, toy examples, or focused explanations are welcome when they materially improve understanding.

They are tools for the research, not mandatory milestones.

---

## Learning philosophy

Learning should primarily be **just in time**.

Do not force the project through a predetermined sequence such as:

1. basic MLP;
2. CNN;
3. VAE;
4. contrastive learning;
5. transformer;
6. final model.

If a VAE becomes important, teach me VAEs then.

If contrastive learning becomes important, teach me contrastive learning then.

If a transformer or something else is irrelevant to the best research direction, do not use one merely because it is fashionable or because an old roadmap mentioned it. However, I still want to understand how various deep learning concepts works even though we may not use them. We should always explore options.

The research problem should determine what we learn.

The purpose is not to prove that I can manually type PyTorch code. The purpose is to understand the important machinery well enough to direct and critique the research.

---

## Research philosophy

This is an open research problem.

The following are deliberately **not fixed in advance**:

- the final architecture;
- the learning objective;
- the input modalities;
- the clustering strategy;
- the role of abundance;
- the role of sequence composition;
- the role of taxonomy;
- the role of assembly graphs;
- the role of genome-language-model embeddings;
- whether the model uses a VAE, contrastive learning, a transformer, a GNN, or none of these;
- the exact datasets;
- the exact benchmark design;
- the intermediate research questions.

We should first understand the current field, identify real limitations or opportunities, and let evidence guide the design. This is obviously best done by reading the most recently released benchmark and tool release papers instead of old papers.

Do not create a Frankenstein model by combining techniques simply because strong existing tools use them.

Every major component and their combination should have a reason to exist.

A useful pattern is:

> observation/problem → hypothesis → experiment → evidence → updated hypothesis/design

Negative results are useful if they eliminate bad ideas or improve our understanding.

---

## Scientific standard

The project should prefer evidence over narrative.

Important principles include:

- separate training, tuning, and final evaluation appropriately;
- avoid information leakage;
- compare against relevant and properly configured baselines;
- distinguish representation improvements from downstream clustering improvements;
- use ground truth where available;
- test on real data as well as controlled/simulated data when appropriate;
- use multiple datasets or domains when needed to test generalization;
- report computational cost, not only biological performance;
- use ablations when they are necessary to identify what actually caused an improvement;
- avoid cherry-picking favorable datasets, metrics, seeds, or configurations;
- document failed hypotheses when they matter;
- do not claim novelty or SOTA performance without evidence.

The exact benchmark design should emerge from the research rather than being frozen now.

---

## Relationship to previous thesis work

The previous metagenomic benchmark is prior work and useful infrastructure, not the new project itself.

Material in `agent_context/thesis/` and `agent_context/tools_repo/` may contain:

- benchmarking workflows;
- tool configurations;
- simulated-data infrastructure;
- evaluation scripts;
- HPC conventions;
- datasets or dataset references;
- analyses;
- notes about tool behavior and limitations.

Reuse should be selective.

Do not copy the previous repository wholesale into this one.

The new repository should develop its own clean identity around method research and deep learning while reusing proven infrastructure where doing so genuinely saves time or improves rigor.

---

## Practical compute context

I currently still have access to SDU/UCloud HPC resources.

This can include:

- H200-class NVIDIA GPUs;
- large-memory systems approaching 2 TB RAM;
- many CPU cores;
- cluster-scale storage and compute.

This access may eventually disappear.

That makes it strategically useful to perform compute-intensive research while the resources remain available.

At the same time, do not waste HPC resources merely because they exist.

Prefer cheap local experiments for debugging and small-scale validation, and scale to UCloud when the experiment genuinely benefits from it.

Local development is on macOS.

---

## Project-document philosophy

The project should maintain enough documentation that future Codex agents can understand:

- what we are trying to achieve;
- what has been tried;
- what evidence exists;
- what decisions were made and why;
- what the current research direction is;
- why previous directions where abandoned

But documentation must not become a bureaucratic constraint.

Plans and research notes are living artifacts.

Update or replace them when evidence changes the direction. But always make sure to document why things have changed.

Do not continue following an outdated plan merely because it exists in the repository.

Historical documents should remain identifiable as history rather than silently competing with current guidance.

---

## Historical planning material

The initial project-planning conversation and earlier planning documents are intentionally preserved.

They contain useful context about:

- why this project was selected;
- alternatives such as SkullNet;
- career motivation;
- learning philosophy;
- breadth versus specialization;
- the relationship between metagenomics and future biomedical work;
- earlier ideas about possible project structure.

These materials are historical context only.

They are **not** a specification of what the research must do.

Current scientific decisions should be made from present evidence and reasoning.

---

## Long-term perspective

This project is intended to be ambitious.

It may take a long time.

That is acceptable.

The purpose is not to rush toward a superficial final model. The purpose is to build enough understanding, evidence, and technical capability to produce something genuinely strong.

At the same time, avoid unnecessary work that does not contribute to the overarching goal.

The central principle is:

> **The goal is fixed; the path is dynamic.**

Build our own scientifically defensible metagenomic binner.

Let the research determine how.
