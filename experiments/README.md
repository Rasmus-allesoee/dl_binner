# Experiments

Experiment records distinguish prepared protocols from executed observations.
The thesis remains [prior evidence](../docs/evidence/2026-09-16-thesis.md), not a
reproduced result of this project.

## Register

- [E001: Where does reduced coverage evidence lose recoverable sequence?](E001-coverage-thinning/README.md)
- [E002: Bounded frozen DNABERT-S CPU feasibility](E002-dnabert-s-feasibility/README.md)
- [E003: Final frozen-GLM versus composition development screen](E003-representation-screen/README.md)
- [E004: First composition-based learned binner](E004-first-binner/README.md)
- [E005: Linux deployment smoke and bounded GI assembly/depth pilot](E005-linux-pilot/README.md)
- [E006: Installed generic command usability](E006-cli-usability/README.md)
- [E007: Private implementation PR readiness](E007-pr-readiness/README.md)
- [E008: Product execution and private PR validation](E008-product-execution/README.md)
- [E009: First competitive human-gut read-derived assembly benchmark](E009-competitive-benchmark/README.md)

The individual record owns its status and outcome. A prospective protocol is not an executed experiment.

## Record convention

Use one directory per scientific question/test, for example `E001-short-description/`. Start its README from the [compact template](TEMPLATE.md), removing fields that are irrelevant and explaining any material omission. The template is not an experiment.

The directory holds the protocol and links to actual code, input manifests, configuration, run attempts, and results. Put reusable software in a shared code location only when reuse exists. Keep a one-off analysis with its experiment. Actual configuration files are executable sources of truth; do not maintain a competing configuration table by hand.

Before execution, specify the hypothesis, controls, data roles/truth, metrics, expected distinguishing outcomes, and practical budget. Commit the protocol, code, and configuration first. Append a dated amendment if a protocol changes after seeing results; mark the resulting analysis exploratory where appropriate.

Each execution has a unique attempt ID within the experiment, such as `run-001`, even when it crashes or is canceled. Record command, source commit, resolved configuration, environment, inputs, seeds, hardware, logs, and outputs. A changed configuration gets a new attempt; a substantially different scientific question gets a new experiment.

Use execution states `planned`, `running`, `completed`, `failed`, or `cancelled`. Record scientific outcomes separately as `not assessed`, `supports within scope`, `does not support`, or `inconclusive`. A failed process can be useful operational evidence but cannot establish that a scientific hypothesis failed.

Track small results and the code that produced them. Keep large outputs externally with locators and checksums. Retain unsuccessful runs and negative conclusions in this same record, and link them to the affected question/decision before an implementation branch is removed.

For HPC, Codex prepares the protocol, scripts, smoke checks, resource estimate, and return-artifact instructions. The owner executes. A submitted job is not a completed experiment; inspect returned outputs before interpreting it.
