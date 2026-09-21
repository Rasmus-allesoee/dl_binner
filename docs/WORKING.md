# Working with the Research Record

Established: 2026-09-16. Updated: 2026-09-18. This is the operating convention; [D001](decisions/D001-research-record.md) records its rationale.

## Sources of truth

| Information | Canonical location | What belongs elsewhere |
| --- | --- | --- |
| Stable purpose and working relationship | [PROJECT_INTENT.md](../PROJECT_INTENT.md) | Immediate priorities belong in STATE |
| Durable agent instructions | [AGENTS.md](../AGENTS.md) | Results and temporary plans belong in research records |
| Current state and next action | [STATE.md](STATE.md) | Detailed reasoning is linked, not copied |
| Question or hypothesis and its lifecycle | [research/questions.md](research/questions.md) | Evidence is linked to notes or experiments |
| Source interpretation | [evidence/](evidence/README.md) | Original papers and thesis remain source material |
| Significant decision and its rationale | [decisions/](decisions/README.md) | GitHub discussion can inform but does not replace the decision |
| Experimental protocol, attempts, and outcome | [../experiments/](../experiments/README.md) | Large outputs live outside Git, with locations and hashes recorded |
| Historical proposals | [history/](history/README.md) | They do not compete with current guidance |

The README is navigation. It does not become a second status report. Avoid separate failure logs, learning logs, and handoff logs when the information already belongs in an experiment, evidence note, or STATE.

## Record identities and lifecycle

- Questions use `Q001`, hypotheses `H001`, decisions `D001`, and experiments `E001`. Allocate the next unused identifier only when a real record is created; never reuse identifiers.
- Questions and hypotheses begin as sections of one register. Split a long entry into its own file when necessary, retaining a link at the original anchor.
- Decisions have one file each. Their file owns the status: `proposed`, `accepted`, `superseded`, or `rejected`. The index lists links, not a duplicate status table. An accepted provisional choice can have a specific revisit condition.
- Experiments have one directory each. Execution status and scientific outcome are separate: a program crash is not a negative biological result. The [experiment convention](../experiments/README.md) defines the minimum record.
- Evidence and assessments are dated snapshots with an explicit review scope. A later note can replace an interpretation without altering the source or pretending the later knowledge was available earlier.
- Current priorities are the short list in STATE. A hypothesis can remain open without remaining the next priority.

When a direction changes, update the affected question or hypothesis, link the resolving evidence, record a decision if the change is consequential, and update STATE in the same unit of work. Preserve the earlier statement and add a dated resolution or supersession link. Routine prose cleanup needs only Git history.

Do not move old experiment or decision records just to label them historical: changing their status preserves existing links. `docs/history/` houses inherited planning, not a second experiment archive.

## Evidence discipline

Distinguish four things in prose: **source report**, **direct observation here**, **our interpretation**, and **untested hypothesis**. A paper's performance claim is not our reproduced result. A source-code read is not a successful run.

Every consequential claim should identify its source and the relevant section, figure, table, file/function, or experiment result. For changing external resources, record the consulted date and version or commit if available. Keep paper versions distinct from software versions. Record corrections alongside the earlier interpretation. ZIP snapshots are sufficient for reading; executable baselines need an immutable source identity plus verified dependencies/payloads. Check `git rev-parse --show-toplevel` so a nested unversioned cache cannot inherit the project's commit by mistake.

Downloaded paper text can have missing equations, tables, or extraction artifacts. Consult the original when such content matters to a decision. Never silently edit the source to make it agree with our interpretation. The full source and the research note serve different purposes.

## Traceability from question to result

```text
Q/H -> evidence note -> D (when a choice matters) -> E protocol
E protocol -> source commit + input manifests + resolved configuration
run attempt -> environment + command + logs + output hashes
analysis -> exact input outputs + analysis code + small result tables
conclusion -> Q/H update -> D/STATE update when direction changes
```

These are links between ordinary files, not a new database. A small experiment can keep the chain in one README plus its actual configuration and result table.

For a dataset introduced into an experiment, record stable sample/genome/contig identifiers, source/accession, version, checksums, transformations and code, inclusion rules, and train/development/evaluation role. Record taxonomy release and reference/pretraining overlap where relevant. A storage path alone is not dataset identity. A coverage matrix must state both the read samples and the reference assembly against which reads were mapped.

For a run, retain the executable source commit, actual resolved arguments, environment or container digest, tool/database/model versions, seeds, hardware, and input manifest. If code is dirty, preserve a patch and its hash before execution. An experiment's code commit must already exist; record the later results in a separate commit. Avoid self-referential promises to record the commit after the run.

## Storage and retention

- Track code, protocols, actual small configurations/manifests, analysis scripts, compact result tables/figures, decisions, and conclusions.
- Keep raw sequences, alignments, checkpoints, bulk embeddings, and temporary run outputs in external storage or ignored `data/raw/`, `data/processed/`, `artifacts/`, `runs/`, and `scratch/` locations. These directories need not exist before use.
- Give retained external artifacts a locator, checksum, owner/storage location, and recovery method. An ignore rule is not a backup. Preserve irreplaceable artifacts before temporary UCloud access ends.
- Before removing a large intermediate, record whether it is regenerable and what evidence would be lost. Keep enough output to recheck negative conclusions as well as positive ones. Removing raw data or irreplaceable outputs is an owner decision.
- Keep local paper/tool caches under `agent_context/`. Our interpretation and provenance are versioned; downloads are not vendored as project software. Replace an inspected cache only after recording its identity.

## Git and GitHub

Use ordinary commits on `main` for small coherent documentation and maintenance work. Use a branch for a substantial hypothesis implementation, risky infrastructure change, or parallel line of work. A branch is an implementation workspace, not the only record of the idea's outcome.

Commit experimental protocols and executable configurations before expensive runs, then commit outputs and conclusions after validation. Use informative subjects and explain nontrivial changes with `What changed:` and `Why:` paragraphs. Keep code, interpretation, and current state synchronized when they change together. Never rewrite completed run provenance by rebasing away its only source commit.

Before finishing substantial work, inspect the diff, run appropriate checks, update affected records, commit the coherent local unit, and report the Git state. Preserve unrelated owner changes. Check what is staged; do not use broad staging to collect unreviewed data.

When a GitHub remote is established, use issues for bounded work or unresolved implementation problems, and PRs for substantial reviewable changes. Link `Q`/`H`/`D`/`E` identifiers. Close issues with a link to the durable record, including negative outcomes. Use milestones only for actual deliverables, tags for verified reproducible states, and releases plus an appropriate archive for material supporting a paper. Introduce automated checks when there is a remote and a useful check to run; do not require elaborate labels or project boards now.

Repository creation, visibility, licensing, and first publication are separate owner choices when publication is requested. Local work continues without them. No remote, public repository, CI service, or publication was created during foundation setup. Before first push, review source-paper/thesis packaging and the full history: an ignore rule or `git rm --cached` does not remove files from earlier commits. See [D001's clarification](decisions/D001-research-record.md#source-packaging-clarification-2026-09-17); do not rewrite history without owner agreement.

## Working on UCloud

Owner preferences clarified 2026-09-21: use Snakemake when execution grows into
a multi-stage research workflow, keeping tested helpers as rule implementations.
Do not retrofit already completed preflights for ceremony. Record actual allocated
vCPU/RAM explicitly, distinguish runtime expectations from timeout ceilings, and
preserve raw results with dated accounting corrections rather than rewriting them.

Codex does not operate UCloud. For each relevant experiment, prepare a tested local smoke check, a job command or script, configuration, expected outputs, approximate resource needs, and a collection/checksum command. The owner runs it. Do not mark a run complete until returned outputs have been inspected. Document queue failures, incomplete runs, and unavailable outputs explicitly.

Use thesis assets selectively and public field benchmarks alongside custom simulations. The owner confirmed thesis availability and allows new simulations optimized for the question. Public data used for development are not an untouched final test set; clearly label changed assemblies, reference populations, read subsets or synthetic coverage. Reuse a standard evaluator where appropriate and test any supplementary metrics against explicit truth contracts. E001's current choice is recorded in [D004](decisions/D004-human-cpu-preflight.md).

Portable software fixtures and native compatibility smoke checks are recorded separately from scientific `run-NNN` attempts; they do not test the biological hypothesis. Record actual allocated vCPU-hours as well as process resource measurements. Do not treat a version-pinned recipe as a resolved environment lock or a tiny smoke as proof that full training fits the budget.

## End-of-task check

Check that a new agent can find the current recommendation, its evidence, the unresolved dependencies, and the next concrete action from STATE. Check links with `python3 scripts/check_docs.py`; use `--check-context` when consulting or updating recorded local sources. A missing optional cache is different from a broken link in the maintained research record.

Add a document only when it owns information that would otherwise be hard to find. Add just-in-time explanations beside the decision or experiment they clarify. The objective is a usable scientific record, not a completed set of templates.
