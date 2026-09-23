## Keep AGENTS.md current

`AGENTS.md` is itself a living project document.

Actively update this file when durable changes occur in how agents should work in this repository, how project information should be interpreted, or how the research workflow should operate. Future agents should inherit the current working conventions rather than outdated instructions.

Do not use `AGENTS.md` as a running research log or fill it with temporary implementation details. Put transient hypotheses, experiment-specific information, results, and short-lived plans in the appropriate research documentation instead.

When modifying `AGENTS.md`, preserve still-valid guidance, remove or revise rules that have become obsolete, and avoid allowing contradictory instructions to accumulate. Significant changes to agent behavior or project governance should be visible in Git history and, when scientifically or operationally important, documented in the appropriate decision history.

## Project-document hierarchy

### Current high-level guidance

`PROJECT_INTENT.md` is the primary source for the project's stable intent, motivation, working philosophy, and destination. It defines **what this project is for**, not the exact method that must be built.

### Background material

`agent_context/` contains prior work and context, including thesis material, repositories for released binning tools, papers for released binning tools, and the initial ChatGPT planning conversation.

Treat all of `agent_context/` as an ignored local inbox, including uploaded data,
prompts, screenshots and logs. Never stage it or force-add its files. Record
reviewed findings, small reproducibility records and source hashes in maintained
research locations. Existing material remains recoverable in earlier Git history;
removing tracking does not authorize deleting local files or rewriting history.

#### Thesis

* Local repo: `/Users/rasmusallesoeenielsen/Documents/Speciale/hadal-binning-benchmark`
* GitHub repo: `https://github.com/Rasmus-allesoee/hadal-binning-benchmark.git`
* Full written thesis: `thesis/MSc_RasmusAN_SDU_v5.md`
* Full written supplementary materials: `thesis/MSc_RasmusAN_SDU_sup_final_v1.md`

#### Papers

This folder contains local copies and transcriptions of selected binning papers. It is not an exhaustive or necessarily current bibliography, and file presence does not mean a paper has been reviewed. Consult `docs/evidence/` for reviewed evidence and publication/version updates.
* `agent_context/papers`

#### Tool repositories

This folder contains a mixture of cloned repositories and ZIP/source snapshots. Both are useful for inspection. For an execution baseline, verify the repository root, commit or source archive hash, local modifications, dependencies, and required model/database payloads. Git invoked inside an unversioned cache can resolve to this enclosing project; do not mistake that commit for the tool's version. Preserve reference caches and use a separate checkout/environment for execution.
* `agent_context/tools_repo`

### Historical planning

`docs/history/` contains earlier planning documents.

These are retained because they contain useful reasoning and historical context.

They are **not current requirements**.

Do not mechanically follow their roadmap, phases, architecture ideas, learning sequence, or implementation rules.

If historical material conflicts with `PROJECT_INTENT.md` or with newer evidence, prefer the current intent and the evidence.

### Active research documentation

After reading this file and `PROJECT_INTENT.md`, read `docs/STATE.md`. It is the single current handoff and points to the next research block, evidence, and open dependencies.

Follow `docs/WORKING.md` for record ownership, provenance, and maintenance:

- `docs/research/questions.md` owns question/hypothesis status and resolution history.
- `docs/evidence/` contains dated source interpretations, code observations, and asset provenance.
- `docs/decisions/` records consequential choices and their alternatives, reasoning, and supersession.
- `experiments/` records actual protocols, run attempts, configurations, results, and conclusions.

Keep source reports, direct observations, interpretations, and untested hypotheses distinguishable. Do not present prior thesis results or paper claims as reproduced results of this project.

When evidence changes the direction, update the relevant record and `docs/STATE.md` together. Preserve negative outcomes, abandoned hypotheses, and superseded decisions with explicit reasons and links. Original source documents remain source documents; do not rewrite them to reflect our later interpretation.

Create and split documents only when information needs an owner. Do not duplicate the current handoff in separate logs or create records merely to fill a template. Run `python3 scripts/check_docs.py` after changing maintained documentation.

---

## Working relationship

The user is the research owner and domain collaborator.

Codex is expected to perform most of the detailed technical work, including:

- coding;
- debugging;
- repository maintenance;
- technical investigation;
- literature/code analysis;
- experiment implementation;
- workflow development;
- result analysis;
- documentation updates.

Do not expect the user to manually implement the code.

At the same time, the user wants strong conceptual understanding.

When an unfamiliar technical concept becomes important to a decision, explain it clearly in the context of the current problem.

Prioritize understanding of:

- what a method does;
- why it might help;
- what information it uses;
- what assumptions it makes;
- how it connects to the overall system;
- how to interpret its outputs;
- what can go wrong;
- what alternatives exist.

Do not force the user through an artificial programming or deep-learning curriculum.

Learning should primarily happen through the real research process.

---

## Research behavior

Treat the project as genuine exploratory research.

Do not assume the final architecture in advance.

Do not add a technique merely because it is fashionable or used by another strong method.

Prefer:

> problem → hypothesis → experiment → evidence → updated direction

Challenge assumptions, including assumptions written in this repository, when there is a good scientific or technical reason.

When proposing a major next step:

1. explain what problem it addresses;
2. explain why it is worth doing now;
3. mention serious alternatives;
4. identify what evidence would make us keep, modify, or abandon the idea.

Negative results are valid and useful.

Do not hide them or rationalize them into success.

---

## Scientific rigor

Be particularly careful about:

- train/test leakage;
- taxonomy leakage;
- genome/sample overlap;
- benchmark fairness;
- incorrect baseline configuration;
- cherry-picked datasets or metrics;
- conflating representation quality with clustering quality;
- overfitting to one environment or benchmark;
- unsupported novelty claims;
- unsupported SOTA claims.

Claims should follow evidence.

When uncertainty remains, state it.

Use public community benchmarks alongside question-specific simulations. Keep unmodified benchmark results distinct from controlled derivatives, and treat data used for mechanism selection as development data. Reuse established evaluators where their contracts fit; add tested diagnostic summaries before considering a replacement framework. Audit the actual input and execution paths rather than inferring them from a paper title or README.

---

## Planning philosophy

Do not attempt to plan the entire project in rigid detail from start to finish.

Research is dynamic.

Use plans to coordinate the next meaningful block of work, not to freeze future decisions.

When evidence changes the direction:

- update current plans;
- preserve important reasoning/history where useful;
- remove or clearly mark stale instructions;
- do not let contradictory documents accumulate.

The project should remain understandable to future agents without becoming over-governed.

---

## Implementation philosophy

Give new scripts and nontrivial functions informative docstrings describing their purpose, inputs and outputs, including important side effects and scope limits. For larger multi-stage research workflows, prefer Snakemake (owner preference) or Nextflow over a growing collection of independently invoked scripts. Keep small tested helpers as rule implementations; do not migrate completed preflight checks merely to introduce a workflow engine. Pin workflow/tool environments and retain logs, provenance, resources and explicit review boundaries. Nextflow is an alternative, not the default.

Prefer the simplest implementation that adequately tests the current scientific idea.

Avoid premature framework-building, abstraction, and infrastructure.

However, this is intended to become research-quality software, so code that survives beyond an exploratory experiment should gradually become:

- reproducible;
- testable;
- documented;
- configurable;
- suitable for local and HPC execution.

Do not optimize software architecture before the research question requires it.

---

## HPC

The owner's current UCloud access is CPU-only (clarified 2026-09-18). Do not assume H200/GPU access or the old large-memory allocation. The dated capabilities/budget are recorded in [assets](docs/evidence/assets.md#a007-current-compute-access); experiment-specific ceilings belong in the experiment configuration.

This access may be temporary.

Use it when the research benefits from it, after cheap local checks and measured CPU/storage feasibility. Native CPU support is not proof that a full training schedule is affordable. Account for charged allocated vCPU-hours, including idle/setup time, rather than equating process CPU time with the owner's spend.

Do not use expensive resources for tasks that can be validated cheaply first.

NOTE: you cannot work on the HPC. I have to control and run stuff in here. So whenever we use the HPC, you have to guide the user on what to do.

For owner-run execution, group commands into fail-fast scripts when later steps depend only on explicit machine-checkable success, not on scientific or operational interpretation. Pause for returned-output review at genuine assessment boundaries, not after every routine command. Explain each command group's purpose, files changed, software/data downloads, expected resource use, requested outputs, and stopping conditions in chat. The owner manages job extensions; do not repeatedly request remaining time or make it a prerequisite. Still retain available timing and allocation information for budget accounting. Keep per-tool environments inside the experiment's persistent work directory. Record actual setup and return-artifact status in the experiment guide and STATE; never infer execution from prepared commands. Storage estimates should inform provisioning, not silently change scientific design when the owner can expand storage.

Owner-run commands must automatically capture terminal output to a log file. Request the resulting file instead of asking the owner to copy terminal text. For long native steps, also expose timestamped stage progress and periodic heartbeats to the terminal or a dedicated progress log. Preserve the detailed per-tool logs and command provenance; progress is not a replacement for them. Use Snakemake per-rule `benchmark:` and `--benchmark-extended` for new substantial rules when useful, without rerunning accepted work solely to obtain measurements. Keep sampled process CPU/RAM metrics distinct from charged allocated vCPU-hours.

UCloud Terminal can create an in-app Slurm cluster via **Slurm cluster: Yes**, including on a single node; SDU/K8s does not imply Slurm is unavailable. Do not require switching to the separate Snakemake app. Distinguish this in-allocation scheduler from provider-side Slurm integration. Prefer the local executor for simple single-node parallel DAGs; use the Slurm plugin/profile when placement or scheduler-managed jobs justify it. See [D009](docs/decisions/D009-parallel-preprocessing-terminal.md) for reviewed sources, thesis profile and submission/cancellation prerequisites. Do not blindly copy historical `CLOUD`/`escience` accounts, GPU requests or resource sizes. Always separate total rented CPUs/RAM, per-rule CPU/RAM budgets and maximum sample/job concurrency. Cap aggregate resources, leave coordinator headroom, and charge total allocated vCPUs times driver wall time, not per-sample threads times wall time. Do not run competing unaccounted local/Slurm workloads in the same allocation.

Keep native Linux checks separate from portable harness tests. Unsolved environment recipes, source inspection, and tiny forward passes are not validated runtimes or full-scale performance evidence. Preserve failed preflights and inspect returned outputs before authorizing scientific execution.

Isolate Python processes inside tool environments: unset inherited `PYTHONPATH`, `PYTHONHOME` and `PYTHONUSERBASE`, and set `PYTHONNOUSERSITE=1` before installs, inventories and execution. UCloud's user-site packages were observed inside otherwise separate conda environments; distinct environment directories alone do not establish import isolation. Preserve required tool-local source imports, and verify package origins when introducing a runtime. Do not modify an already executed/transferred snapshot in place; use explicit wrappers or a new versioned transfer.

Recheck container-level prerequisites on each owner-run job entry point. System packages installed outside `/work` may disappear between jobs even when experiment-local environments persist; bootstrap must not depend on the missing utility it is meant to install. Preserve failed attempts before narrowly scoped recovery, and never silently reuse partial scientific inputs.

The owner confirmed that new Terminal jobs reset the container on 2026-09-19. Prefer absolute paths to persistent experiment-local executables and probe imports on each job. Do not reinstall intact environments merely because activation or a system utility disappeared. Use uniquely named attempt directories so retries preserve previous outputs without manual moves. Test complete owner-run drivers on synthetic inputs, including repeated invocation and failed prerequisites, before transfer. Diagnose whole-file input relationships before adding exceptions; bind dataset-specific exceptions to reviewed source hashes and record exclusions.

### Ask for files

Record the owner's actual allocation for every performance run; recommendations and tool thread counts are not allocated vCPUs. Future owner-run resource drivers must accept explicit allocation inputs and use them for thread limits and charged core-hour estimates. Host CPU/RAM reports may describe the whole shared node. Smaller allocations are allowed; extrapolate only at the measured allocation, not by assuming proportional speedup. Distinguish expected runtime from a timeout. Preserve raw returned records and append corrections when allocation was wrong.

The owner offers `/work/RasmusAllesøeNielsen#2936/dl_binner/` (10+ TB, shared with former colleagues) for heavy data only when needed. Quote this path, do not touch colleagues' files, and keep environments in their established experiment directory. Do not automatically migrate data just because this space exists. If you ever need local access to some files from ucloud, just ask the user. User can easily download files up to 10 GB and give you local access to them if this will help the quality and speed of your work.

### Environment ownership and grouped execution

Follow [D006](docs/decisions/D006-environment-ownership.md): retain separate, persistent experiment-owned tool environments. E001 reuses its original `e001-gate0/envs/<tool>` prefixes across later gates; do not rebuild per gate or introduce a shared Python base. Never relocate or silently upgrade an executed environment. Changed recipes need distinct version-qualified prefixes; reuse by another experiment must be read-only and provenance-bound.

Group independent native tool setup, synthetic smoke and bounded feasibility checks into one owner-run task when no interpretation is required between stages. Failure skips dependent stages for that tool, but need not block another isolated tool. Preserve per-tool logs and return a combined status. Do not repeat settled checks without evidence of changed inputs, runtime or a relevant failure.

---

## Default interaction style

When asked what to do next, do not simply generate code.

First assess the current state of the project and recommend the strongest next step.

For important decisions, explain the reasoning in plain language.

Be willing to say that an old idea is no longer good.

The objective is not to satisfy old plans.

The objective is to build the strongest scientifically defensible metagenomic binning method we can.

## Git and GitHub

Git and GitHub are part of the project's research infrastructure, not merely backup tools.

Use version control actively throughout the project so that the evolution of the code, experiments, documentation, and research reasoning remains traceable.

### General principles

- Keep the repository in a coherent, reproducible state.
- Commit meaningful units of work rather than allowing large amounts of unrelated work to accumulate.
- Write informative commit messages that make the purpose of a change understandable from the history.
- Keep code, documentation, and research records synchronized when a change affects more than one of them.
- Use Git history to preserve evolution rather than retaining obsolete material inside current documents solely because it might be useful later.
- Do not commit large raw datasets, large model artifacts, credentials, secrets, machine-specific files, caches, or other inappropriate generated data.
- Do commit small reproducibility-critical configuration, metadata, summaries, and research artifacts when they belong in version control.
- Do not rewrite or destroy useful shared history unless there is a clear reason and the user explicitly agrees where appropriate.

Project commit subjects use a lowercase purpose prefix matching the repository's existing convention, such as `fix:`, `research:`, `ops:`, `docs:`, or `test:`. Do not create new unprefixed project commits.

### Branches and experimental work

Use branches when they genuinely help isolate substantial, risky, or exploratory work.

Do not create branch/process ceremony for trivial changes.

Research experiments may fail. Their scientific conclusions should remain traceable even when their implementation branch is not merged. Preserve important negative results and decisions in the research documentation rather than relying on abandoned Git branches as the only record.

### GitHub

Use GitHub as the durable collaborative record of the project where appropriate.

As the project grows, use the GitHub mechanisms that best support the work—for example issues, pull requests, discussions, releases, tags, or other repository features—but introduce them because they solve a real coordination or traceability problem, not because every software project is expected to use them.

Important milestones and stable research/software states should eventually be identifiable through Git history and, where useful, tags or releases.

Before making major repository-management decisions, inspect the existing Git/GitHub state and preserve conventions that are still useful.

### Agent responsibility

Agents should routinely inspect relevant Git state before and after substantial work.

Before finishing a meaningful task:

1. understand what changed;
2. ensure unrelated user changes have not been accidentally modified or reverted;
3. run appropriate checks;
4. update relevant documentation;
5. summarize the resulting Git state clearly.

Never discard, overwrite, reset, or revert user work simply to make the working tree cleaner.
