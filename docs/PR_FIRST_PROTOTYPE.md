# Prepared private implementation PR

Status: **draft description, not an opened PR**. Target branch `main`; source
`first-binner-prototype`. Title: **Add the first usable CPU metagenomic binner**.
Do not push/open/merge/publish without the owner's next authorization.

## Proposed PR body

This adds our first usable composition-based contrastive metagenomic binner.
Given an assembly FASTA and optional explicit mean-depth matrix, the installed
`dl-binner run` trains our own compact encoder, saves/reloads its checkpoint,
embeds, applies fixed label-blind clustering and exports complete assignments/DNA.
A matched raw-feature arm is included. Short exclusions, original depth zeros,
noise and all length strata remain visible; summaries do not claim MAG quality.

The implementation follows [D011](decisions/D011-first-binner-prototype.md).
Scientific inputs/transforms/training/clustering are frozen, while the generic
launcher packages defaults/DAG, enforces serial CPU/RAM budgets, retains progress/
logs/exit receipts and verifies bytes before explicit partial/completed resume.
Fresh runs refuse populated outputs; changed/corrupted artifacts stop safely.
Version 0.1.0.dev2 changes packaging/version metadata, not accepted scientific code.

Validation is separated by scope:

- [E004](../experiments/E004-first-binner/README.md): end-to-end learned implementation
  with exact reload, complete exports and mixed fragment-development utility.
- [E005](../experiments/E005-linux-pilot/README.md): accepted native Linux and a capped
  GI assembled-sequence/depth development pilot. Confirmed macro R95 raw→learned
  0.16731→0.43443; recovery remains fragmented, with no ≥90% recovered genome.
- [E006](../experiments/E006-cli-usability/README.md): generic installed-command
  native Mac/CPU-Linux behavior, all masks/strata, strict resume, serial placement
  and intended failure/resource/orphan handling. Successful work was not repeated.
- [E007](../experiments/E007-pr-readiness/README.md): clean-source wheel/sdist inspection,
  standalone fresh local environments and self-contained installed-product
  regressions. Its actual receipt owns test/build identities and resource costs;
  prepared Linux CI requires its first real remote run before merge acceptance.

The ordinary suite uses bounded generated software DNA and owns no ignored
research dependencies. Earlier evidence reviews remain explicit opt-in research
checks. CI builds/installs the CPU wheel on Linux with separate workflow Python,
two-thread budgets and retained artifacts; no benchmark/data/GLM download or
publication is part of the workflow. [Installation](INSTALLATION.md) and
[usage](PROTOTYPE.md#run-the-binner) state exact contracts and limitations.

This is development software, not an independent whole-MAG/generalization,
full-community-scaling or SOTA result. Different-ID negatives can be co-genomic;
depth's separate benefit is not isolated. E001/H001/three-seed conclusions do not
change. No architecture comparison or benchmark expansion is included.

Review this as the stable first-prototype baseline. After a separately authorized
merge, benchmark and matched architecture work starts on a new branch from updated
main; experimental changes can then be compared against these accepted bytes.

## Before opening and merging

Check the live branch/remote/base state and use the actual final head in the PR.
Opening the private PR and running its CI is the next separately authorized
action; do not merge automatically. Before merge, require successful real Linux
CI (including native installed tests), inspect review findings, and retain the
validated source commits. Prefer a merge preserving referenced source history;
do not squash away the sole source commits behind accepted evidence.

No project license has been selected. This does not block a private implementation
PR. Public redistribution is a separate owner choice with dependency/source
packaging review. The current tree tracks no local inbox or heavy run payloads;
earlier Git history still contains local-context/source objects. The bounded E007
audit identifies that fact, not a complete legal/security clearance, and authorizes
neither deletion nor history rewriting. No public release/tag/package publication
is requested by this PR preparation.
