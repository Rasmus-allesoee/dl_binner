# Experiments

No experiments have been run in this project. The thesis is [prior evidence](../docs/evidence/2026-09-16-thesis.md), and the current assessment is a research recommendation, not an experimental result.

## Register

No experiment IDs have been allocated. Add a link here when an actual protocol is created; the individual record owns its status and outcome.

## Record convention

Use one directory per scientific question/test, for example `E001-short-description/`. Start its README from the [compact template](TEMPLATE.md), removing fields that are irrelevant and explaining any material omission. The template is not an experiment.

The directory holds the protocol and links to actual code, input manifests, configuration, run attempts, and results. Put reusable software in a shared code location only when reuse exists. Keep a one-off analysis with its experiment. Actual configuration files are executable sources of truth; do not maintain a competing configuration table by hand.

Before execution, specify the hypothesis, controls, data roles/truth, metrics, expected distinguishing outcomes, and practical budget. Commit the protocol, code, and configuration first. Append a dated amendment if a protocol changes after seeing results; mark the resulting analysis exploratory where appropriate.

Each execution has a unique attempt ID within the experiment, such as `run-001`, even when it crashes or is canceled. Record command, source commit, resolved configuration, environment, inputs, seeds, hardware, logs, and outputs. A changed configuration gets a new attempt; a substantially different scientific question gets a new experiment.

Use execution states `planned`, `running`, `completed`, `failed`, or `cancelled`. Record scientific outcomes separately as `not assessed`, `supports within scope`, `does not support`, or `inconclusive`. A failed process can be useful operational evidence but cannot establish that a scientific hypothesis failed.

Track small results and the code that produced them. Keep large outputs externally with locators and checksums. Retain unsuccessful runs and negative conclusions in this same record, and link them to the affected question/decision before an implementation branch is removed.

For HPC, Codex prepares the protocol, scripts, smoke checks, resource estimate, and return-artifact instructions. The owner executes. A submitted job is not a completed experiment; inspect returned outputs before interpreting it.
