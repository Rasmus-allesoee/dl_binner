# Historical UCloud operating guidance

Archived: 2026-10-13 from local source `2109998a230a0757be424e6f55c3a1bf17971ebe`.
**Historical only: SDU access is deactivated. Do not run these commands or treat the old balance/storage as accessible.**
The owner reports files still exist; none were deleted or migrated. Current guidance is
[Google Cloud operations](../CLOUD.md) and [STATE](../STATE.md). Experiment records,
source commits, packets and raw receipts remain in their canonical locations.

## Former agent HPC guidance


The owner's current UCloud access is CPU-only (clarified 2026-09-18). Do not assume H200/GPU access or the old large-memory allocation. The dated capabilities/budget are recorded in [assets](../../docs/evidence/assets.md#a007-current-compute-access); experiment-specific ceilings belong in the experiment configuration.

This access may be temporary.

Use it when the research benefits from it, after cheap local checks and measured CPU/storage feasibility. Native CPU support is not proof that a full training schedule is affordable. Account for charged allocated vCPU-hours, including idle/setup time, rather than equating process CPU time with the owner's spend.

Do not use expensive resources for tasks that can be validated cheaply first.

NOTE: you cannot work on the HPC. I have to control and run stuff in here. So whenever we use the HPC, you have to guide the user on what to do.

For owner-run execution, group commands into fail-fast scripts when later steps depend only on explicit machine-checkable success, not on scientific or operational interpretation. Pause for returned-output review at genuine assessment boundaries, not after every routine command. Explain each command group's purpose, files changed, software/data downloads, expected resource use, requested outputs, and stopping conditions in chat. The owner manages job extensions; do not repeatedly request remaining time or make it a prerequisite. Still retain available timing and allocation information for budget accounting. Keep per-tool environments inside the experiment's persistent work directory. Record actual setup and return-artifact status in the experiment guide and STATE; never infer execution from prepared commands. Storage estimates should inform provisioning, not silently change scientific design when the owner can expand storage.

Owner-run commands must automatically capture terminal output to a log file. Request the resulting file instead of asking the owner to copy terminal text. For long native steps, also expose timestamped stage progress and periodic heartbeats to the terminal or a dedicated progress log. Preserve the detailed per-tool logs and command provenance; progress is not a replacement for them. Use Snakemake per-rule `benchmark:` and `--benchmark-extended` for new substantial rules when useful, without rerunning accepted work solely to obtain measurements. Keep sampled process CPU/RAM metrics distinct from charged allocated vCPU-hours.

Keep new owner uploads, launch copies, terminal logs and returned archive/checksum
files in the experiment's persistent `transfer/` directory, rather than the
`/work/Home` root. Keep attempts and environments in their established experiment
directories. Do not move or delete prior artifacts just to adopt this organization.

UCloud Terminal can create an in-app Slurm cluster via **Slurm cluster: Yes**, including on a single node; SDU/K8s does not imply Slurm is unavailable. Do not require switching to the separate Snakemake app. Distinguish this in-allocation scheduler from provider-side Slurm integration. Prefer the local executor for simple single-node parallel DAGs; use the Slurm plugin/profile when placement or scheduler-managed jobs justify it. See [D009](../../docs/decisions/D009-parallel-preprocessing-terminal.md) for reviewed sources, thesis profile and submission/cancellation prerequisites. Do not blindly copy historical `CLOUD`/`escience` accounts, GPU requests or resource sizes. Always separate total rented CPUs/RAM, per-rule CPU/RAM budgets and maximum sample/job concurrency. Cap aggregate resources, leave coordinator headroom, and charge total allocated vCPUs times driver wall time, not per-sample threads times wall time. Do not run competing unaccounted local/Slurm workloads in the same allocation.

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

Keep native Linux checks separate from portable harness tests. Unsolved environment recipes, source inspection, and tiny forward passes are not validated runtimes or full-scale performance evidence. Preserve failed preflights and inspect returned outputs before authorizing scientific execution.

For repeated native startup hangs, capture evidence inside the child (including
before Python site initialization) and process wait state, not only a parent
timeout traceback. Do not bypass a failed probe or raise its timeout and call
that a root-cause repair. Prior successful execution does not establish current
runtime health; retain explicit unresolved status until evidence identifies it.
When retained traces establish forward progress through cold persistent-file reads,
correct a prematurely short startup budget prospectively, with an absolute clock
and an idle-progress limit. Distinguish that wrapper correction from repairing
filesystem latency or accepting an uncompleted runtime probe.
If that bounded correction still spends mostly wall time waiting on persistent
files, stop repeating the full allocation and change the observed read path in
a cheap native recovery. Python -B forbids bytecode writes, not reads; source-cache
isolation needs explicit -X flags under -I, verified child propagation and no
scientific-setting changes. Keep failed attempts and distinguish a locally repaired
cache-loader reproduction from actual storage/runtime acceptance.

For long owner-run preparation, prefer progress-aware stall detection and one
explicit owner-selected overall cost ceiling over arbitrary short per-stage wall
caps. Completed bytes/files/checkpoints are progress; parent heartbeats alone are
not. Justify stall intervals and any hard ceilings from retained workload/rate,
allocation and uncertainty, including copy, verification and packing. Test the
observed workload cardinality and recovery path, not just a smaller convenient
fixture. Local throughput remains distinct from native performance. Persist
checksum-bound completed work across job resets where useful; make resume reject
source/config/output drift and ignore unsealed partials without deleting them.
Before handoff, reconcile every nested timeout with the advertised command budget.

When changing an observed storage execution path, distinguish one-time materialization
from repeated native imports. Bind snapshot bytes and internal links, retain a
reusable artifact, and validate interpreter, library origins and actual numerical
operations before admission. CPU-capped I/O concurrency may overlap storage
latency; it does not authorize extra numerical workers or silent relocation.

For the reviewed E001 workflow snapshot only, D006 permits a checksum-bound
job-local execution copy when persistent filesystem reads stall. Preserve the
authoritative experiment-owned environment; invoke the copied Python directly,
verify prefix/import origins and the accepted inventory, and pass native CLI/DAG
checks before work. Do not generalize this to arbitrary Conda-prefix relocation.

Isolate Python processes inside tool environments: unset inherited `PYTHONPATH`, `PYTHONHOME` and `PYTHONUSERBASE`, and set `PYTHONNOUSERSITE=1` before installs, inventories and execution. UCloud's user-site packages were observed inside otherwise separate conda environments; distinct environment directories alone do not establish import isolation. Preserve required tool-local source imports, and verify package origins when introducing a runtime. Cross-experiment reuse must be read-only and validate a full distribution inventory and import origins against a clean, hash-identified prefix record; a `pip freeze` alone may include user-site entries or direct references. A new package-only venv may explicitly borrow reviewed dependencies read-only, with its own installed wheel and byte-bound before/after checks. Scope byte verification to the actual execution contract: accepted sealed runtime members need no repeated whole-prefix hash, and explicit external source/binary/model inputs can be bound before/after. Do not recursively hash unused tests, headers or unrelated databases merely to demonstrate non-mutation. Label the verification scope honestly; this is not proof that every file in a prefix stayed unchanged. Expose real file/byte progress for substantial verification. Record the dependency/base-prefix relationship, exclude the old package and path-injecting overlays, and never transfer such links as a portable environment or remove their required base. For all Python children using a reused environment, including scientific rules, pass `-B` on the Python command line to prevent `.pyc` writes: `-I` implies `-E` and ignores `PYTHONDONTWRITEBYTECODE`. Do not modify an already executed/transferred snapshot in place; use explicit wrappers or a new versioned transfer.

Recheck container-level prerequisites on each owner-run job entry point. System packages installed outside `/work` may disappear between jobs even when experiment-local environments persist; bootstrap must not depend on the missing utility it is meant to install. Preserve failed attempts before narrowly scoped recovery, and never silently reuse partial scientific inputs.

The owner confirmed that new Terminal jobs reset the container on 2026-09-19. Prefer absolute paths to persistent experiment-local executables and probe imports on each job. Do not reinstall intact environments merely because activation or a system utility disappeared. Use uniquely named attempt directories so retries preserve previous outputs without manual moves. Test complete owner-run drivers on synthetic inputs, including repeated invocation and failed prerequisites, before transfer. Diagnose whole-file input relationships before adding exceptions; bind dataset-specific exceptions to reviewed source hashes and record exclusions.
Preserve a virtual environment's lexical interpreter path when invoking it:
resolving its `bin/python` symlink can bypass `pyvenv.cfg` and execute the base
environment. Probe version/prefix before giving a harness runtime-validation credit.

### Ask for files

Record the owner's actual allocation for every performance run; recommendations and tool thread counts are not allocated vCPUs. Future owner-run resource drivers must accept explicit allocation inputs and use them for thread limits and charged core-hour estimates. Host CPU/RAM reports may describe the whole shared node. Smaller allocations are allowed; extrapolate only at the measured allocation, not by assuming proportional speedup. Distinguish expected runtime from a timeout. Preserve raw returned records and append corrections when allocation was wrong.

The owner offers `/work/RasmusAllesøeNielsen#2936/dl_binner/` (10+ TB, shared with former colleagues) for heavy data only when needed. Quote this path, do not touch colleagues' files, and keep environments in their established experiment directory. Do not automatically migrate data just because this space exists. If you ever need local access to some files from ucloud, just ask the user. User can easily download files up to 10 GB and give you local access to them if this will help the quality and speed of your work.

### Environment ownership and grouped execution

Follow [D006](../../docs/decisions/D006-environment-ownership.md): retain separate, persistent experiment-owned tool environments. E001 reuses its original `e001-gate0/envs/<tool>` prefixes across later gates; do not rebuild per gate or introduce a shared Python base. Never relocate or silently upgrade an executed environment. Changed recipes need distinct version-qualified prefixes; reuse by another experiment must be read-only and provenance-bound.

Group independent native tool setup, synthetic smoke and bounded feasibility checks into one owner-run task when no interpretation is required between stages. Failure skips dependent stages for that tool, but need not block another isolated tool. Preserve per-tool logs and return a combined status. Do not repeat settled checks without evidence of changed inputs, runtime or a relevant failure.

---


## Former research-record UCloud convention


Owner preferences clarified 2026-09-21: use Snakemake when execution grows into
a multi-stage research workflow, keeping tested helpers as rule implementations.
Do not retrofit already completed preflights for ceremony. Record actual allocated
vCPU/RAM explicitly, distinguish runtime expectations from timeout ceilings, and
preserve raw results with dated accounting corrections rather than rewriting them.

Codex does not operate UCloud. For each relevant experiment, prepare a tested local smoke check, a job command or script, configuration, expected outputs, approximate resource needs, and a collection/checksum command. The owner runs it. Do not mark a run complete until returned outputs have been inspected. Document queue failures, incomplete runs, and unavailable outputs explicitly.

Use thesis assets selectively and public field benchmarks alongside custom simulations. The owner confirmed thesis availability and allows new simulations optimized for the question. Public data used for development are not an untouched final test set; clearly label changed assemblies, reference populations, read subsets or synthetic coverage. Reuse a standard evaluator where appropriate and test any supplementary metrics against explicit truth contracts. E001's current choice is recorded in [D004](../../docs/decisions/D004-human-cpu-preflight.md).

Portable software fixtures and native compatibility smoke checks are recorded separately from scientific `run-NNN` attempts; they do not test the biological hypothesis. Record actual allocated vCPU-hours as well as process resource measurements. Do not treat a version-pinned recipe as a resolved environment lock or a tiny smoke as proof that full training fits the budget.

