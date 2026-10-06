# E007: Private implementation PR readiness

Prepared 2026-10-07. Status: **planned**; scientific outcome **not assessed**.
[D011](../../docs/decisions/D011-first-binner-prototype.md) retains the accepted
composition contrastive binner. [Frozen protocol](protocol.json) owns scope,
immutable package bytes and resource/clock acceptance. The accepted
[E006 Linux evidence](../E006-cli-usability/README.md#accepted-native-linux-return-and-independent-review-2026-10-06)
is reused without replay. This task addresses independent installation and routine
regression reproducibility, not another architecture or quality gate.

Build version 0.1.0.dev2 from a committed clean snapshot, then test the wheel and
sdist outside the checkout in new independent environments. Numerical code,
transforms, training defaults, fixed clustering and generic runner remain byte
identical; only package version metadata changes. Ordinary tests live in
`tests/product/`; older research tests/reviews remain explicit opt-in checks.
Version requirements are under `requirements/`, derived from the accepted runtime
inventories. They pin distributions, not every platform's wheel artifact.

One measured attempt is bounded at 7,200 seconds including build/install/setup,
four numerical threads/interop one/loader zero and 8 GB sampled working RSS.
Synthetic software fixtures stay at most 32 contigs / 0.6 Mb. No biological
performance is scored. Prepare minimal Linux CI and a concrete private PR
review description locally; do not push, run remote CI or open/merge/publish.

Actual attempts, receipts and outcome will be recorded after inspection. Existing
caches, runtimes, failed attempts and accepted wheels stay read-only and retained.

## Retained operational attempt 001

`artifacts/e007-pr-readiness/run-001/`, source **e7a44e8**, failed before any
product test/scientific stage. Offline fresh runtime installs and the initial
wheel/sdist build passed; pip rebuilding the sdist correctly rejected its Python
3.13 builder against package Requires-Python <3.13. Cost including setup/byte
checks: **144.066 local seconds**; the original receipt/logs/prefixes are retained.
Use a supported local Python 3.10 builder for a fresh attempt, without bypassing
Requires-Python or expanding package support. The prepared CI builder stays 3.12.
Known attempt clocks are summed under the original two-hour campaign ceiling.

`run-002`, source **991421e**, also stopped before product tests. Its standalone
setup and sdist rebuild passed. Direct backend calls in one Python process
mutated `sys.argv`: the wheel landed under snapshot/sdist instead of the requested
output directory. Inspection refused the missing expected file. Run the two
PEP-517 build hooks in independent Python processes in the driver, guide and CI;
validate retained artifacts before another full setup. Keep both attempts.
