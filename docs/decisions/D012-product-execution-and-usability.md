# D012: Product resources, serial execution and shared usability

Date: 2026-10-07. Status: **accepted; local and native Linux product checks pass**.
Owner direction extends the private-PR preparation in D011/E007. It changes
product execution, not model selection or scientific settings.

## Problem and decision

E006/E007's four-thread, 8-GB and two-hour budgets are validation limits, not
limits on a user's machine. Accept any positive thread count, keep four as the
existing convenience default, and make finite positive RAM/time safeguards
optional with no project maximum. Omitted safeguards mean no product ceiling.
Always retain resource samples, logs, progress, exit status and safe cleanup.
Tests/CI explicitly supply their own bounded budgets; no large-thread native
work is needed to check argument acceptance.

The fixed eight-stage product has no branching, placement or parallel scheduling
decision. `runner.py` already owns stage argv, immutable input/source/runtime
bindings, ordered receipts, staging/publication, failure inspection, exact reload
and accounting. Snakemake adds a separate 51-distribution workflow prefix and
dispatches that serial list. Use a small built-in loop over the same stage adapter,
with native subprocess isolation and the existing supervisor. One CPU environment
is enough. Keep Snakemake for existing research/HPC DAGs; do not migrate accepted
experiments. The new dev3 source/version cannot resume old dev1/dev2 journals;
their environments/manifests remain unchanged and usable with their original code.

## Alternatives and evidence

Keeping Snakemake is technically valid and has native placement evidence, but
requires users/agents to provision and bind a second runtime for a fixed serial
list. Adding interchangeable engines would retain that burden and double the
execution paths without a current product need. Rebuilding a workflow framework
or executing model functions in the parent would expand scope or weaken native
failure isolation. The small dispatcher is straightforward because supervision
and journal logic already live outside Snakemake. Keep it only if installed native
resume, resource/failure/cleanup and output tests pass; otherwise retain the old
dispatcher and record a concrete revisit before public release.

The bounded source inspection covers our dispatcher and four local tool entry
points, **not** a new literature/model review. [Source identities and modifications](../../experiments/E008-product-execution/source-audit.json)
bind the 2026-10-07 snapshot: VAMB's Python dispatcher, SemiBin's easy-binning
functions/subprocess calls, COMEBin's command dispatch and CompleteBin's lazy
pipeline entry point. CompleteBin has local modifications; that inspected wrapper
is not asserted to be an unmodified released interface. These show viable wrapper
patterns, not equivalent recovery guarantees or a reason to copy their architecture.
Our fixed pipeline and existing receipts determine this choice. Python's
[subprocess API](https://docs.python.org/3.12/library/subprocess.html) supplies
argument-vector execution and exit handling; our supervisor retains group cleanup.

## Durable product goals and consequences

Make both installed tool and repository discoverable and usable by people and AI
agents: concise commands/help, explicit inputs/outputs/recovery, structured neutral
results and errors that identify the cause and retained evidence. Keep one shared
interface; no agent framework, model API or special protocol is required now.
Record optional GPU support while retaining CPU, and Conda/mamba installation as
future product/distribution goals. Neither is implemented or published here.

[E008](../../experiments/E008-product-execution/README.md) owns prospective contracts,
tests and actual execution/PR records. Scientific byte hashes stay frozen.
The initial preparation task stopped after real Linux CI and review-status
inspection; the later authorized merge is recorded below.
After a later authorized merge, benchmark work uses a new branch from updated main.

## Initial validation and preparation boundary

E008's fresh Mac installation and actual private Linux CI pass 12 tests/18 native
cases. Scientific byte hashes/defaults remain unchanged. The dispatcher is retained
because it preserves the native worker, staging/receipt, resume, export and failure
contracts while removing the second runtime. Large CLI choices are tested through
parser-only inspection, never by allocating more than the test budget. This is
software acceptance, not an architecture or biological performance comparison.
At that preparation boundary, the private PR remained open; requested review
and exact-head checks were distinct from merge authorization. No merge or
publication occurred in that task.

## Private merge boundary completed, 2026-10-07

Later explicit owner authorization permits normal merge without another approval.
[E008](../../experiments/E008-product-execution/merge-observed.json) records the
completed private merge, refreshed exact-head gates and preserved source history.
Final native checks pass 13 tests/19 cases after the concrete large-timer repair.
No independent review approval is claimed. Product choices/scientific settings
are unchanged; GPU/Conda remain future goals and no public release occurs.
