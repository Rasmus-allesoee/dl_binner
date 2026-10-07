# E008: Product execution and private PR validation

Prepared 2026-10-07; status **local/native Linux software accepted; private PR open, review pending**, biological outcome **not assessed**.
[D012](../../docs/decisions/D012-product-execution-and-usability.md) owns the bounded
execution decision; [protocol](protocol.json) freezes prospective contracts and
software-test ceilings. Accepted E006/E007 and science remain retained. Owner
authorizes push/private PR/real CI/review, **not merge or public publication**.

Product resource choices are independent of the four-thread/8-GB/two-hour test
budget. Remove the fixed product maxima and make RAM/time safeguards opt-in.
Use one installed environment and a built-in serial dispatcher reusing the
existing supervised native stages, immutable receipts, staging and resume.
No model/transform/training/clustering change, GPU execution, Conda publication,
UCloud, scientific replay or benchmark work. Native software validation will be
recorded here with source/build identities, bounded costs, CI and review evidence.

## Accepted local dev3 integration

Source `8da3da4` built inspected wheel/sdist and a logically identical rebuilt
wheel, installed in fresh builder/binner prefixes. [Receipt](observed.json) owns
exact identities/costs. The installed suite physically outside the checkout
passes **12 tests/18 native cases**, on 13 generated contigs / 42,311 bp. Both
arms, six strata, masks/zeros/reasons, exact reload, complete DNA and serial stages
pass. Optional safeguards omitted are actually executed and logged as null;
bounded depth execution, partial continuation (2→6 stages), complete resume
(zero), byte/change refusal, intended fatal/RSS/timeout/orphan and heartbeat checks
pass. Large thread/RAM/time CLI acceptance is a parser-only stub to avoid
allocating large resources; actual native workers are never mocked.

Full setup/build/install/probe/test/read-only byte-check attempt **252.180 s**,
sampled stage peak **488,042,496 bytes (0.488 GB)**, four numerical threads/interop
one/loader zero. At four threads, local wall budget is 0.280200 hours, not provider
billing or exact process CPU time. Acquisition/development/review/idle are outside
the measured clock. Existing base libraries and wheel caches remain unchanged.
Retained attempt storage and artifacts are byte-counted in the receipt; physical
`/private/tmp` test originals are an additional retained copy. No UCloud execution.

CI/review acceptance remains pending the actual private PR. The Linux workflow
uses one runtime, Python 3.12 and two threads with bounded test/RAM/time guards,
never the optional unbounded product setting as its own test guard. No model,
transform, objective, training defaults, clustering, scientific result or old
wheel/source/journal is changed. GPU and Conda remain goals only.

## Accepted native Linux CI and private PR

[Private PR #1](https://github.com/Rasmus-allesoee/dl_binner/pull/1) is open against
main; source history is preserved and no merge/publication requested.
[Actual CI](https://github.com/Rasmus-allesoee/dl_binner/actions/runs/37646636562)
passed for `5a0d753`; [retained review receipt](linux-observed.json) binds exact
head/build/runtime/test bytes. Ubuntu CPU/Python 3.12 uses one fresh owned prefix,
CPU-only Torch and two numerical threads/interop one/loader zero. All **12 tests/18
native cases** pass, including actual no-safeguard and explicit-safeguard execution,
eight nonoverlapping stages, partial/full resume, exact reload, both complete
exports, masks/zeros/strata, intended errors/limits, heartbeat and absent-orphan
snapshots. No ignored research asset or biological score is used.

Product checks: **39.726 s / 574,414,848-byte sampled peak (0.574 GB)**. Runner job
wall time **111 s**, including setup/build/checks/artifact upload. Two threads is
the explicit software-test budget; whole-job allocation/billing and exact peaks
are not inferred from sampled product work. Full Linux logs/builds/native outputs
and inventories are retained in `artifacts/e008-product-execution/pr/linux-001/`.
There is no CI failure to repair on this head. The all-check watcher reports
clean/mergeable and no unresolved review threads, but is not review approval.

An implementation review was requested through `@codex review`. No review was
returned at this record; capture/triage any later findings rather than inventing
approval or bypassing review. Exact current-head checks still need refreshing
after final record-only pushes. The owner explicitly forbids merge/publication
in this task. Next is review and an explicit exact-head merge decision; after a
later authorized merge, benchmark work belongs on a new branch from updated main.

## Native timer boundary repair

Final source inspection reproduced `OverflowError: timestamp out of range for
platform time_t` for a valid finite `1e100` timeout. The previous timer arm was
before the run's protected cleanup region, so this could leak the lock/log state.
Day-sized alarm pulses now re-arm until the actual user deadline (not a product
ceiling), with timer setup inside cleanup protection. The regression includes
actual native feature execution at huge RAM/time safeguards, still under the
external test CPU/RAM/time limits, plus small-timeout/unset/expired cases. Preserve
prior accepted attempts/CI; this is a concrete operational repair, not a model gate.

The [repair receipt](timer-repair-observed.json) accepts source `b297019` in fresh
`run-002` prefixes: **13 tests/19 native cases**, including real large-safeguard
feature execution and lock cleanup. Setup/build/install/all checks **261.662 s**,
sampled stage peak **0.501 GB**. Both known local attempt clocks total **513.842 s**
under 7,200 s; four-thread wall budget 0.570936 hours, not billing. Prior prefixes,
wheel/source bytes, logs and CI returns remain preserved. Post-fix exact-head Linux
CI is the final validation boundary; no scientific settings or results change.
