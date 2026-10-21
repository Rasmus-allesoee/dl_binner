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

Record known and unknown pretrained/reference-database overlap as a limitation on
unseen-genome claims. It is distinct from labels entering our feature/training
pipeline. An unavailable complete historical training inventory alone is not an
automatic benchmark blocker; keep the uncertainty visible in interpretation.


For comparative benchmarks, keep native whole-tool comparisons distinct from
matched input/learning/clustering ablations. A winning tool does not identify
which component caused its advantage. Preserve intermediate evidence, native
eligibility and all unassigned/excluded DNA. Existing literature, source reviews
and project evidence can justify a coherent upgrade with several related changes.
Use selective matched ablations for uncertainties that can change the design or
for component-level causal claims; do not require an isolated performance win for
every ingredient before implementation. An integrated upgrade establishes a bundle
result unless further controls isolate its causes. Disabling a loss in a matched control
should preserve module construction, initialization and random-number consumption
unless changing those is the declared treatment. Admit training-only configuration
overrides explicitly against retained cache metadata; never rewrite the accepted
cache to make a new treatment pass. Data inspected to choose
improvements become development data, even when they originate from a public
community benchmark.
Preserve the accepted main implementation as the immutable comparator on a new
research branch; do not quietly tune that baseline to the comparison's scores.

Predeclared practical effect thresholds support the scoped experiment's decision;
they are not biological standards or statistical significance tests. Preserve a
failed criterion unchanged, while allowing an explicitly reasoned provisional
development direction based on the complete paired evidence. Do not turn one
threshold into a permanent ban on a method or retune it after seeing outcomes.

Report lineage/origin and length denominators alongside community-wide diagnostic
aggregates. A representation gain driven by non-target organisms is not evidence
of improvement for the primary cellular targets. Compare the same query populations
and retain unknown/non-target DNA in the appropriate full-population denominators.

For length-dependent methods, distinguish the main/core binning cutoff from
later short-contig recruitment, coverage filters and actual emitted eligibility.
A native whole-tool comparison may have different eligibility from our learner;
keep full-community recovery denominators and length/status strata, and do not
call it a matched-cutoff ablation. Any common-input control must be prospective.

An experiment's contig-length cutoff or available feature set is not a product
constraint. Keep relevant short-contig methods in design comparisons; use separate
prospectively defined data/evaluation for unsupported ranges without automatically
reopening an accepted experiment.

Keep simulator genome IDs, source files/replicons, molecule type, host relationships
and taxonomic nodes separate. A profile may omit genome IDs or use synthetic
taxon labels; record the actual join evidence. Verify separately simulated plasmids
and circular aliases before defining coordinate unions or genome denominators.
Validate native alignment counters against the pinned writer, including ambiguous
bases in gaps or equal CIGAR operations. An unlocalized ambiguity must not create
unique support by silently discarding a competitor. Admit a repaired truth artifact
in a separate review record; never rewrite a failed execution journal as successful.

When uncertainty remains, state it.

For reference-derived benchmark inputs, distinguish a verified simulator/source
origin from DNA that uniquely identifies that origin. Preserve known alternative
sources, shared sequence and ambiguous bases under an explicit evaluation policy;
do not silently turn an origin label into unique support. Headers can expose
genome/accession/coordinate information. When IDs affect view seeds, sorting or
grouping ties, use verified source-blind IDs and retain the reverse source join
outside feature/training paths. Keep zero-bp original records in explicit input
accounting rather than inventing DNA or silently losing the records.

Use public community benchmarks alongside question-specific simulations. Keep unmodified benchmark results distinct from controlled derivatives, and treat data used for mechanism selection as development data. Reuse established evaluators where their contracts fit; add tested diagnostic summaries before considering a replacement framework. Audit the actual input and execution paths rather than inferring them from a paper title or README. For multi-sample features, check native emitted sample and contig axes against the frozen manifest; do not assume filesystem ordering or alias names survive native path resolution. One assembly can still use many read/BAM samples: per-base coverage storage scales with covered assembly bases times BAM count, while multiple assemblies multiply whole run directories. Audit persistent candidates, checkpoints and temporary coexistence before claiming that a smaller epoch count bounds peak disk use.

---

## Planning philosophy

Owner direction, 2026-10-14: improve our own binner toward high performance,
potentially SOTA. The accepted simple prototype is a software milestone and
immutable comparator, not the completed performance goal. D010 preserves the
earlier bounded first-product direction. Publication/novelty and a SOTA claim
remain optional and need evidence. Bound investigations by the improvement
decision they inform; reuse thesis, benchmark, source-review and accepted project
evidence. Do not require a complete mature-tool campaign before improving our
method. Data preparation and each later fit are separate authorization scopes.
See PROJECT_INTENT.md and D013 for the current direction.

Before an expensive comparison, name its incremental evidence and the decision it
can change; consider cheaper diagnostics or a matched mechanism test. Preserve
intermediate evidence needed to distinguish information, representation and
grouping failures. One weak prototype and one assembly cannot rule depth, sequence
or taxonomy into/out of the product. Data used to choose improvements are
development data; confirm improvements on prospectively defined additional data.

Owner clarification, 2026-10-16: prefer substantial, coherent prototype upgrades
over a default sequence of tiny feature experiments. Reuse completed reviews to
implement related modules in one bounded development block, with engineering
contracts and selective ablations. This does not prescribe a large network or a
checklist of mandatory SOTA ingredients. Keep the immutable comparator, distinguish
whole-system gains from causal component claims, and obtain separate authorization
for paid/community runs. D015 records the current recommendation.

When one development assembly limits a mechanism decision, preserve the method
and admit prospectively chosen additional data. Perfecting grouping/refinement on
that assembly is not a prerequisite for a justified training/representation
upgrade. A weak or null result here does not establish the mechanism's value in
other communities; source evidence and independent evaluation still matter.

The required first-architecture review and first prototype are already accepted;
STATE points to their scoped records. For a new unresolved design decision, use a
current review of relevant papers/benchmarks and the source of a justified shortlist.
Define its scope/cutoff and concrete design purpose; it informs implementation,
without becoming another novelty or release gate. Do not restart the initial
review or combine methods without a concrete rationale.
Once a scoped review and design decision are complete, reuse those records during
implementation. Refresh specific evidence when a changed dependency or design
question requires it; do not restart the whole review before each milestone.
Once a bounded representation screen selects the first prototype's sequence route,
move to implementation without another architecture gate unless a concrete failure
requires one. A frozen-GLM versus raw-composition screen does not compare against a
contrastive-trained composition encoder or prove whole-genome recovery. Treat local
runtime projections as rough planning estimates, not the sole reason to reject a
sequence route with useful evidence.
An explicitly owner-requested later comparison can remain a non-blocking follow-up
even when the first prototype works. Recording that plan does not authorize its
execution during the current milestone or create another implementation/release gate.

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

When designing retries, consider Snakemake's native resume behavior and its [working-directory and rerun guidance](https://snakemake.readthedocs.io/en/stable/project_info/faq.html): reusing the same work directory can preserve valid completed outputs, while a fresh attempt directory may better protect isolation or provenance. Choose what best fits the workflow, and handle incomplete or stale outputs explicitly.

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

## Cloud compute and resource discipline

As of 2026-10-13 the owner cannot access SDU/UCloud; its files are reported to
still exist but are inaccessible. Google Cloud is the selected main compute
provider. [Cloud operations](docs/CLOUD.md) and [STATE](docs/STATE.md) own actual
setup/access status; provider selection is not proof of a connected VM. Historical
Terminal/Slurm/transfer instructions are archived in
[UCloud operations](docs/history/UCLOUD_OPERATIONS.md). Preserve all UCloud data,
source history, receipts and locators; do not try old paths on a different provider.

Verify live paid billing, displayed credit balance/expiry/scope, relevant SKU
eligibility, quotas, existing resources and full compute/storage/network costs
before provisioning or enabling services. The owner's current authorization is
for products covered by the remaining Free Trial credits only. Stop and ask if
eligibility/cost is unclear or spending could fall outside those credits. Budget
alerts are notifications, not spending caps. Account for running idle time and
storage while stopped; stop compute when unused and review credit expiry before
retaining chargeable storage. No GPU infrastructure is implied by paid billing.

For authorized unattended VM work, make end-of-run shutdown independent of the
chat/SSH connection and bind it to the intended run's process identity. Test live,
normal-exit and crash detection without stopping active science, and retain the
provider's maximum-runtime fallback. A shutdown watcher is not a scientific
progress monitor or permission to retry, extend or start another stage.

Owner clarification, 2026-10-17: during an authorized connected-GCP execution,
debug recoverable operational failures and retry within the same task when the
owner has authorized that recovery. Do not turn a launcher/runtime/provenance bug
into another owner-transfer or approval loop. Preserve failed journals, repair and
test the actual failing path, create a fresh recorded attempt, and reuse passed
stages only after their byte/source/runtime contracts pass. Operational recovery
is distinct from repeating accepted science, changing a frozen scientific rule,
tuning to outcomes or expanding the tool campaign. Keep concrete clock/cost/disk
limits and verified shutdown for each attempt; record justified envelope changes
when already authorized instead of asking again. Credit coverage and evidence
integrity still apply. A short supervised job expected to finish within about
15 minutes should normally be followed through collection, independently verified
shutdown and available local review. For a healthy longer job, verify supervision
and real progress, wait a few minutes, then hand off without polling to completion.

Use local development for cheap checks; use a verified SSH-connected GCP repository
and shell for authorized Linux/cloud phases. Agents may operate that VM within the
current task's explicit execution boundary; an infrastructure task does not
implicitly authorize acquisition, scientific fits or benchmark scores. Owner login,
app connection and IAM/quota approvals may need owner action. Never claim remote
app access from a plain SSH test or local harness alone. Reuse the established
strictly pinned SSH entry point in CLOUD before invoking cloud CLI SSH defaults;
a missing generic default key or known-hosts file is not evidence that the
project-specific credentials or host pin need replacement. Keep SSH/auth credentials
outside Git and backups; prefer narrowly scoped access without public app-server
listeners. Install the documented Linux sandbox prerequisites when the host needs
them; prefer the distro's scoped Bubblewrap/AppArmor profile and retain global
kernel protections. [Cloud operations](docs/CLOUD.md) records the tested path.
Native CPU support is not full-schedule affordability. Record actual
machine/allocation, elapsed time, process usage and estimated monetary spend
separately; allocated core-hours remain useful comparisons, not GCP prices.

For owner-run execution, group commands into fail-fast scripts when later steps depend only on explicit machine-checkable success, not on scientific or operational interpretation. Pause for returned-output review at genuine assessment boundaries, not after every routine command. Explain each command group's purpose, files changed, software/data downloads, expected resource use, requested outputs, and stopping conditions in chat. For owner-run jobs, the owner manages extensions; do not repeatedly request remaining time. Direct connected-VM work needs persistent logs and review at real assessment boundaries, without an artificial upload/return round trip. Retain actual VM uptime, allocation and costs separately from child timing. Keep per-tool environments inside the experiment's persistent work directory. Record actual setup and return-artifact status in the experiment guide and STATE; never infer execution from prepared commands. Storage estimates should inform provisioning, not silently change scientific design when the owner can expand storage.

Remote scientific commands, including direct SSH runs, must automatically capture
terminal output to a log file; this also applies to any remaining owner-run command. Request the resulting file instead of asking the owner to copy terminal text. For long native steps, also expose timestamped stage progress and periodic heartbeats to the terminal or a dedicated progress log. Preserve the detailed per-tool logs and command provenance; progress is not a replacement for them. Use Snakemake per-rule `benchmark:` and `--benchmark-extended` for new substantial rules when useful, without rerunning accepted work solely to obtain measurements. Keep sampled process CPU/RAM metrics distinct from charged allocated vCPU-hours.

When an owner transfer is needed, keep uploads, launch copies, terminal logs and
returned archive/checksum files in that experiment's persistent `transfer/`
directory. Direct connected-VM work still uses persistent per-experiment logs
and records; it need not produce transfer packets for every step. Keep attempts and environments in their established experiment
directories. Do not move or delete prior artifacts just to adopt this organization.

For simple single-node research DAGs, use the local workflow executor. Add a
scheduler only when placement/concurrency needs justify it; do not copy old UCloud
accounts, Slurm profiles or GPU/node requests. Separate node CPUs/RAM, per-rule
budgets and maximum concurrency, leaving coordinator headroom. Do not run competing
unaccounted workloads in the same allocation.

For each single-node CPU run, either run tools serially at the node's full allocated CPU budget or cap concurrent tools so their summed process budgets fit the allocation. Reconcile Snakemake `threads`, each native tool's thread flag, effective OpenMP/BLAS limits and child/data-loader workers. Count those workers in the per-tool budget; do not set a native thread flag to the full allocation when it also starts CPU workers. Confirm effective use from native thread reports and per-rule CPU benchmarks, rather than assuming the requested thread count took effect.
For a local Snakemake executor, use `--cores` without simultaneously supplying
`--jobs`; in inspected 9.16.3 those combined arguments can disable the scheduler's
core cap. Make aggregate RAM scope explicit and use DAG barriers for a promised
serial workflow. Verify actual scheduling events/overlap on independent ready
rules; a driver label or tiny fixture that happens to serialize is insufficient.

For installed product workflows, test the actual built wheel outside the checkout
and package its defaults and any required DAG. Preserve journaled completed outputs: use explicit
resume only after matching source/input/config/runtime/artifact bytes; never edit
manifests to make a retry pass. Prototype interfaces may evolve without a
compatibility promise; current contracts belong in `docs/PROTOTYPE.md`.
Ordinary installed-product regressions belong in `tests/product/` and must run
without ignored research assets or experiment helpers. Keep retained-evidence
reviews explicitly separate; do not silently skip them and call the product
suite scientific validation. Use the pinned standalone installation guide for
fresh environments that own their numerical distributions. Preserve prior linked
research runtimes as executed provenance. Inspect both wheel and sdist, including
the rebuilt wheel's logical contents, before accepting changed packaging. Use a
builder within the package's supported Python range and separate backend hook
processes; CI preparation is not a successful native CI run.
Ordinary product CPU counts and optional RAM/time safeguards are user choices,
without project-imposed maxima. Keep validation/CI/resource allocations bounded
explicitly and distinguish their ceilings from product policy. A fixed serial
product pipeline may use the built-in dispatcher; retain workflow engines for
research/HPC where their scheduling or DAG features help. Favor clear shared
commands/contracts, structured outputs and actionable errors for people and AI
agents. Future GPU/Conda goals belong in product guidance, not automatic work.
Keep parent prerequisites within the bounded clock and retain failures even
before a child starts. Surface native causes beyond scheduler trailers. Distinguish
exited/zombie from live processes during cleanup and verify the intended stop and
absence of running orphans. Label-free size/assignment summaries must not imply
genome recovery or MAG quality without a separate evaluator.

Forecast both compressed return size and the uncompressed local review working
set. For large retained evidence, stage only needed copies and distinguish native
in-place verification from a local reread. Lossless deduplication requires explicit
aliases with identical byte counts and content hashes; omitted on-disk artifacts
are not backed up merely because their inventory is archived. Keep scientific
completion, contract review and evidence delivery as separate statuses.

Report retained storage from the immutable archive members, including its
inventory and terminal snapshot. Do not sum an open log after collection and
present that as the archived payload; retain and append corrections to older
receipts without rewriting them.

Before transferring an owner-run driver, test the changed production adapter and
its real input/output contracts, including fresh and recovered directory layouts.
A fixture that replaces the changed worker/extractor does not validate that path.
Use actual native readers/writers and tiny real inputs where locally available;
keep mocks for external dependencies outside the contract under test. Record
which paths ran, which were mocked or skipped, and which still need Linux
validation. Passing test counts alone are not evidence of native readiness.
For helpers launched with isolated Python (`-I`), test the exact subprocess argv
from outside the checkout, including any transferred helper layout. In-process
imports can mask a missing sibling import that isolated execution will refuse.
Failure checks must verify the intended worker error or enforced limit in retained
evidence, not just any nonzero exit; a monitoring/prerequisite failure can otherwise
produce a false pass.
On recovery, test that completed stages are not scheduled again and that every
remaining consumer follows the reused manifests rather than inferred paths.
For an accepted hash-bound runtime payload, prepare a restore-only consumer that
verifies retained receipts, archives and member bytes without rereading original
source contents. Missing/corrupt retained payloads must fail explicitly rather
than silently trigger a fresh copy. Treat job-local dependency bindings as
provenance with an explicit lifetime; they are not portable environments.

For new bounded owner-run drivers, cover parent-side verification, hashing and
setup with the overall execution ceiling as well as timing child stages. Retain
the verified transfer manifest in failure returns, not only successful ones.
Evidence-only collection may follow a timeout; distinguish its cost from the
bounded execution clock and include it in allocation accounting.

A reduced runtime smoke establishes only its exercised imports; directories named test can be runtime dependencies. When a tool fails on incompatible versions or missing package contents, prefer a complete independently owned compatible recipe for that failed path when practical. Do not apply placeholder modules or assume that a new prefix alone proves compatibility; test the actual import/CLI/readers. Preserve passed tool contracts instead of rebuilding them alongside failed paths.

Keep incompatible native library families in separate processes, including
inventory probes. A single environment can contain libraries that must not be
loaded together (for example conflicting OpenMP runtimes); do not suppress that
conflict with global duplicate-library workarounds. Build changed distributions
from a fresh source/build directory so stale generated files cannot enter a wheel.

Keep native Linux checks separate from portable harness tests. Unsolved environment recipes, source inspection, and tiny forward passes are not validated runtimes or full-scale performance evidence. Preserve failed preflights and inspect returned outputs before authorizing scientific execution.

When a short learning smoke approaches an existing collapse/variance guard and
a longer engineering schedule is cheap, exercise that schedule before claiming
readiness. Distinguish a shared low-information fixture failure from a treatment
regression using a bounded unchanged engineering anchor when it can change the
implementation decision. Preserve failed guards; do not relax their thresholds
or call passing tiny training a full-community stability result.

Keep exact same-runtime checkpoint reload checks separate from cross-platform
numerical comparisons. Preserve failed numerical tolerances without widening them
after inspection. A separately admitted review of original native artifacts needs
passing input/output/geometry contracts and must state any unresolved portability
limitation; it does not make the failed portability contract pass.

For native startup hangs, retain child-side traces and process wait state before
changing budgets or storage paths. Real file/byte/checkpoint movement is progress;
parent heartbeats are not. Use one prospective overall cost/clock limit plus a
justified stall interval, and reconcile nested limits before launch. A source-cache
or snapshot repair needs explicit byte/link/interpreter/library verification;
`-B` prevents bytecode writes, not reads. Reuse accepted sealed work without
original recopy and refuse corruption or drift. Do not apply UCloud's slow-storage
snapshot workaround to a healthy persistent GCP prefix by default. The detailed
case history is in [E009 UCloud operations](docs/history/E009_UCLOUD_OPERATIONS.md).

Isolate Python processes inside tool environments: unset inherited `PYTHONPATH`, `PYTHONHOME` and `PYTHONUSERBASE`, and set `PYTHONNOUSERSITE=1` before installs, inventories and execution. UCloud's user-site packages were observed inside otherwise separate conda environments; distinct environment directories alone do not establish import isolation. Preserve required tool-local source imports, and verify package origins when introducing a runtime. Cross-experiment reuse must be read-only and validate a full distribution inventory and import origins against a clean, hash-identified prefix record; a `pip freeze` alone may include user-site entries or direct references. A new package-only venv may explicitly borrow reviewed dependencies read-only, with its own installed wheel and byte-bound before/after checks. Scope byte verification to the actual execution contract: accepted sealed runtime members need no repeated whole-prefix hash, and explicit external source/binary/model inputs can be bound before/after. Do not recursively hash unused tests, headers or unrelated databases merely to demonstrate non-mutation. Label the verification scope honestly; this is not proof that every file in a prefix stayed unchanged. Expose real file/byte progress for substantial verification. Record the dependency/base-prefix relationship, exclude the old package and path-injecting overlays, and never transfer such links as a portable environment or remove their required base. For all Python children using a reused environment, including scientific rules, pass `-B` on the Python command line to prevent `.pyc` writes: `-I` implies `-E` and ignores `PYTHONDONTWRITEBYTECODE`. Set `NUMBA_CACHE_DIR` to a fresh job-owned directory before native JIT imports when borrowing dependencies. Python `-B` does not prevent third-party compiler caches from being written beside imported source. Distinguish cache-only writes from changes to protected source, libraries or scientific evidence; do not claim whole-prefix non-mutation from a scoped verification. Do not modify an already executed/transferred snapshot in place; use explicit wrappers or a new versioned transfer.

Recheck actual OS/mount/runtime prerequisites before a cloud phase. A stopped GCP
persistent-disk VM normally preserves its OS and packages; do not reinstall healthy
prefixes because the old UCloud container reset between jobs. A replacement VM
still needs an explicit mount and source/runtime identity check. Preserve useful
failed-attempt diagnostics, never silently consume partial scientific inputs, and
test changed production adapters on real tiny contracts before costly work.
Preserve a virtual environment's lexical interpreter path when invoking it:
resolving its `bin/python` symlink can bypass `pyvenv.cfg` and execute the base
environment. Probe version/prefix before giving a harness runtime-validation credit.
For native dependency provenance, retain the dynamic loader's reported alias and
hash its resolved regular target, including any direct link destination. This is
content verification, not a replacement invocation path. Keep scientific artifact
link refusal separate from normal operating-system library aliases. Compare stable loader file identities and content hashes, not randomized load
addresses in raw `ldd` text. Validate the schema the frozen writer actually emits
when reviewing retained outputs; do not rewrite evidence to fit a new reader.

### Allocation and storage records

For a run with multiple storage guards, report total peak growth as the maximum
sampled filesystem usage minus the original launch snapshot. A guard's own
growth counter can reset between setup, science and collection; it is not the
whole-run peak. Retain both scopes when they are useful.

Record the owner's actual allocation for every performance run; recommendations and tool thread counts are not allocated vCPUs. Future owner-run resource drivers must accept explicit allocation inputs and use them for thread limits and charged core-hour estimates. Host CPU/RAM reports may describe the whole shared node. Smaller allocations are allowed; extrapolate only at the measured allocation, not by assuming proportional speedup. Distinguish expected runtime from a timeout. Preserve raw returned records and append corrections when allocation was wrong.

UCloud's former shared-storage quota is inaccessible and is not a GCP entitlement.
Size provisioned working storage from the authorized sample count and peak live
intermediates, then grow it only when useful. Keep code and compact provenance in
Git, accepted/irreplaceable evidence in a private checksum-bound archive, and bulk
regenerable intermediates on the working disk. After capturing useful diagnostics,
record removals and prune obsolete failed-run bulk when no longer needed; do not
retain tens of GB merely for a failure status. Never delete irreplaceable inputs,
accepted evidence or old UCloud files under this general cleanup convention.

### Environment ownership and grouped execution

Follow [D006](docs/decisions/D006-environment-ownership.md): retain separate, persistent experiment-owned tool environments. E001's original prefixes remain historical provenance and inaccessible on UCloud; fresh GCP tool recipes must own complete independent dependencies rather than borrow that unavailable base. Never relocate or silently upgrade an executed environment. Changed recipes need distinct version-qualified prefixes; reuse by another experiment must be read-only and provenance-bound.

Group independent native tool setup, synthetic smoke and bounded feasibility checks into one authorized task or direct-VM phase when no interpretation is required between stages. Failure skips dependent stages for that tool, but need not block another isolated tool. Preserve per-tool logs and return a combined status. Do not repeat settled checks without evidence of changed inputs, runtime or a relevant failure.

---

## Default interaction style

When asked what to do next, do not simply generate code.

First assess the current state of the project and recommend the strongest next step.

For important decisions, explain the reasoning in plain language.

Be willing to say that an old idea is no longer good.

The objective is not to satisfy old plans.

The objective is our own high-performing, usable and reproducible metagenomic
binner with scientifically defensible claims. The current prototype is a starting
point; novelty/publication and a SOTA claim are separate evidence-dependent goals.

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
For nontrivial commits, use `what changed` and `why` sections with bullet points
under each. Explain the concrete changes and their purpose; preserve real newlines
when passing a prepared commit-message file to Git.

### Branches and experimental work

Use branches when they genuinely help isolate substantial, risky, or exploratory work.

Owner preference, 2026-10-17: use descriptive branch names without the `codex/`
prefix. Preserve existing branch names and source commits referenced by evidence.

Do not create branch/process ceremony for trivial changes.

Research experiments may fail. Their scientific conclusions should remain traceable even when their implementation branch is not merged. Preserve important negative results and decisions in the research documentation rather than relying on abandoned Git branches as the only record.

Owner direction, 2026-10-06: bring the first usable prototype through a bounded
private-PR readiness step, then review/merge when separately authorized. Keep
that accepted implementation as a stable baseline on main; start subsequent
benchmark and matched architecture work on a new branch from updated main.
Experimental comparisons are not prerequisites for merging a correctly tested
prototype. Preserve source commits referenced by accepted evidence; do not
squash/rebase away their only durable provenance.

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
