# E007: Private implementation PR readiness

Completed 2026-10-07. Status: **accepted local software milestone**; biological
outcome **not assessed**. [D011](../../docs/decisions/D011-first-binner-prototype.md)
retains the composition contrastive binner. [Frozen protocol](protocol.json) was
committed at `3574d94` before measured integration; operational amendments retain
failed attempts and never change scientific settings. [Acceptance receipt](observed.json)
and [retained-only review](review.py) bind actual builds/runtimes/tests/resources.
Accepted E002–E006 science and E006 real-DNA/Linux work were not replayed.

## Accepted product work

- Standalone [CPU installation guidance](../../docs/INSTALLATION.md), product-first
  README and full distribution-version pins under `requirements/`. Separate fresh
  versioned builder/binner/workflow prefixes own their packages, with no numerical
  dependency links, source checkout imports or user-site overlays. Lexical Python
  paths, complete inventories/import origins, CPU pools and `pip check` pass.
- Clean committed source **`4c68b19acc95ab841b46e030a8aa00043da42900`** builds a
  **0.1.0.dev2** wheel and sdist. All 17 wheel members/35 sdist files are inspected:
  metadata, CLI, every RECORD digest/size, defaults/DAG, accepted package bytes,
  rebuild recipe and ordinary tests. No research payload is packaged. Rebuilding
  the sdist yields identical logical wheel bytes; timestamp-dependent archive
  hashes differ. An actually damaged wheel fails on its intended RECORD mismatch.
- Scientific/generic package bytes match **`e30023c`** in all eleven unchanged
  files; only the initializer version changes. Python range/scientific dependencies,
  encoder, transforms, objective, seed-11/20-epoch defaults, clustering and runner
  remain unchanged. The dev1 wheel's `f093261d…` hash and all old environments stay
  preserved. New source/version journals do not retrofit accepted old runs.
- Self-contained `tests/product/` runs actual installed readers/writers, model,
  CLI, Snakemake and supervisor; no mocked worker, ignored research input, truth,
  scientific score or required skip. Four-thread clean-snapshot checks and
  **two-thread checks physically outside the repository** each pass **11 tests**
  with **18 named native cases**, plus invalid-option assertions. The latter uses
  the prepared CI allocation and does not claim native Linux execution.

Fixture: 13 deterministic generated IUPAC contigs / **42,311 bp**, all six strata,
including below-500 DNA and an N-only row; synthetic two-sample mean depth has
three all-zero rows. Both sequence-only/depth paths retain every ID and exact DNA
in matched raw/learned exports, original masks, exclusion reasons and noise.
Checkpoint reload is exact. Eight completed stages are serial; partial run has
only two stages, its continuation six, completed resume zero. Reused bytes/mtimes
stay identical. Changed FASTA/sample order, corrupt checkpoint/export, extra output
and fresh populated paths fail. Invalid native IUPAC stops dependents with its
actual cause. The real overall timeout and sampled-RSS limit retain intended
failure receipts. Fatal exit 7 returns in **0.920/0.928 s**, with retained native
`ps` snapshots showing absent orphans. Ten-second supervisor heartbeats are captured
in the parent suite log, distinct from child stdout logs. Independent ready-rule
CPU and aggregate-RAM fixtures prove serial placement at both CPU budgets.

Local targets: builder/binner **Python 3.10.15**, workflow **3.13.12**, Mac x86_64.
Exact native distribution inventories contain **3/16/51** distributions. Numerical
limits are four or two threads as selected, interop one and loader zero. Old
base library bytes and all 66 cached wheel hashes stay unchanged; new venvs still
require their base Python/stdlib. Version pins are not cross-platform artifact
hashes or an exhaustive Python/OS matrix. Full local logs, samples, failures,
package inspection, source archives and runtime inventories are in
`artifacts/e007-pr-readiness/`; copied physical-outside evidence is under
`external-two-thread-001/`, with originals retained in `/private/tmp`.

## Build identities and costs

The [receipt](observed.json) owns full SHA-256/byte identities. Direct wheel:
**34,360 bytes**, `2ee2141d7f27a430c11b5858d1e98c1cf7021b6bafd6983dc982ac1627dd5664`.
Sdist: **55,045 bytes**, `0394ac7473e18f108c2c923d58ba6f66683ded0dac2557522dfa7edd5bae311c`.
Installed sdist-rebuilt wheel: **34,360 bytes**,
`226a91789dac29bb0c5a3958a82f0fdcc45d756a942613d526a006dc329999ef`.
These bind the measured source snapshot; later record-only commits do not rewrite
the archives or claim a rebuilt final-head artifact.

Successful full attempt: **331.511 s**, including snapshot/hash/setup/build/
installation/probes/product tests/final read-only checks; sampled stage peak
**560,525,312 bytes (0.561 GB)**. The four-thread suite's enclosing monitored stage
is 146.398 s; its inner test/cleanup receipt is 114.432 s (unittest body 94.972 s).
The distinct outside two-thread invocation is **87.878 s / 0.539-GB sampled peak**
(unittest body 73.078 s). Nested receipts must not be summed as independent costs.

All known serial attempt clocks, including two failures and the 4.813-second
artifact-only preflight, total **712.558 s** under the original **7,200-second**
campaign cap. Budget-weighted local wall allocation is **0.742910 thread-hours**
(four for attempts/preflight, two for the outside check); a four-thread upper budget
is 0.791731 hours. Neither is process CPU time, UCloud billing or total task cost.
Source preparation, build-wheel acquisition, review/debugging/docs/idle are separate.
Sampling includes stage coordinators, may double-count shared pages and does not
continuously sample between-stage hashing or establish exact peaks. Tiny startup,
verification, deliberate waits and cleanup dominate; thread caps are not saturation
or assembly-scale speedup evidence. No UCloud execution/cost occurred.

Closed E007 retained files total **2,765,478,462 regular bytes (2.765 GB)**, including
all three independently owned environment sets, failures, clean source copies,
artifacts, setup/test evidence and the 1,465,161-byte copied outside check. Its
physical `/private/tmp` originals add another 1,465,161-byte copy. Counts exclude
external base libraries, filesystem block overhead and old wheel caches; no deletion
is authorized. Reused cache inputs total 206,444,169 bytes; the new build-only wheel
is stored in E007 acquisition and already included in E007 storage.

## Retained operational failures and repairs

`run-001`, source **e7a44e8**, failed before product/native tests. Offline setup and
initial wheel/sdist build passed; pip rebuilding the sdist correctly rejected
Python 3.13 against package Requires-Python <3.13. **144.066 s**, retained receipt,
logs and prefixes. Select supported Python 3.10 locally/3.12 in CI; do not bypass
Requires-Python or expand support. The original summary omitted its failed-stage
resource dictionary entry; review includes the existing `.exit.json` without
rewriting the original receipt.

`run-002`, source **991421e**, also stopped before product tests. Setup and sdist
rebuild passed, but two backend hooks in one Python process mutated `sys.argv`:
the direct wheel landed under snapshot/sdist. Inspection refused the missing
expected file. **144.290 s**. Separate hook processes in the driver/guide/CI repair
the cause; the artifact-only preflight passed before fresh `run-003`. Both attempts
and the preflight remain preserved. No failed packaging stage is biological evidence.

## CI, review and next action

[Minimal prepared Linux CI](../../.github/workflows/product.yml) uses Python 3.12,
fresh owned runtimes, explicit CPU Torch, a **two-thread** budget, 55-minute bounded
shell/60-minute job and 30-minute product ceiling. It builds/inspects the wheel and
sdist rebuild, runs installed native product/docs checks and retains logs/receipts
on failure. Actions use inspected immutable commits, read-only repository permission
and no persisted checkout credentials. YAML/triggers/pins/permissions and Bash syntax
pass local checks. This is prepared CI, **not an executed independent Linux install**.
The two-thread Mac suite validates budgets/contracts, not this pending platform path.

The source payload audit at `4c68b19` finds 270 tracked files, no tracked local inbox
or heavy run artifacts, and no research payload in wheel/sdist. Historical Git
contains 112 local-context objects over 108 paths, including original source material
and run evidence. This bounded locator audit is **not** exhaustive legal/security
clearance. Preserve history; no project license is selected, deletion/history rewrite
or public distribution authorized. A private implementation PR is not blocked by
inventing a public-license choice.

**Decision: retain D011; ready to open the private implementation PR.** The exact
next action is separately authorized push/PR, real Linux CI and review using
[the prepared description](../../docs/PR_FIRST_PROTOTYPE.md). Do not merge without
the owner's later explicit decision. No additional software milestone or owner
UCloud smoke is required before opening; fix a concrete CI/review failure if found.
After merging with referenced source history preserved, use a new branch from
updated main for prospective benchmark/matched architecture work.

Accept reproducible software, not superiority. E005's fragmented development
assembled-sequence recovery is not whole-MAG quality, real-assembly generalization,
full-community scaling or isolated depth benefit. E001/H001 and the original
three-seed criterion remain unresolved. The TNF/frozen-GLM-head/hybrid follow-up
is planned and unrun. No dataset/seed expansion, architecture gate, remote action
or publication occurred.

Tooling sources inspected 2026-10-07 (scope: installation/CI only, not a reopened
architecture review): [official PyTorch 2.2.2 CPU recipe](https://pytorch.org/get-started/previous-versions/#v222),
[private standard runner resources](https://docs.github.com/en/actions/reference/runners/github-hosted-runners),
[Python 3.12 removed APIs](https://docs.python.org/3.12/whatsnew/3.12.html),
and pinned [checkout](https://github.com/actions/checkout/commit/11bd71901bbe5b1630ceea73d27597364c9af683),
[setup-python](https://github.com/actions/setup-python/commit/a26af69be951a213d495a4c3e4e4022e16d87065)
and [upload-artifact](https://github.com/actions/upload-artifact/commit/ea165f8d65b6e75b540449e92b4886f43607fa02)
commits. Build-only setuptools 78.1.1 avoids old pkg_resources' removed
`pkgutil.ImpImporter` access; accepted runtime versions remain unchanged. These
pins are the selected stable snapshots, not a claim that they are the latest.
