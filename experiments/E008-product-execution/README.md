# E008: Product execution and private PR validation

Prepared 2026-10-07; status **local/native Linux software accepted; private PR merged, no independent review approval**, biological outcome **not assessed**.
[D012](../../docs/decisions/D012-product-execution-and-usability.md) owns the bounded
execution decision; [protocol](protocol.json) freezes prospective contracts and
software-test ceilings. Accepted E006/E007 and science remain retained. Owner
initially authorized push/private PR/real CI/review and stopped before merge;
the later explicit merge authorization and observed completion are recorded below.
Public publication/release remains unauthorized.

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

At this initial local receipt, CI/review acceptance was pending the private PR;
subsequent native Linux acceptance is recorded below. The Linux workflow
uses one runtime, Python 3.12 and two threads with bounded test/RAM/time guards,
never the optional unbounded product setting as its own test guard. No model,
transform, objective, training defaults, clustering, scientific result or old
wheel/source/journal is changed. GPU and Conda remain goals only.

## Accepted native Linux CI and private PR

[Private PR #1](https://github.com/Rasmus-allesoee/dl_binner/pull/1) was opened against
main; source history was preserved and no merge/publication requested at this receipt.
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
after final record-only pushes. The owner explicitly forbade merge/publication
in that preparation task. The next boundary was review and a merge decision;
after an authorized merge, benchmark work belongs on a new branch from updated main.

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

[Post-fix Linux CI](https://github.com/Rasmus-allesoee/dl_binner/actions/runs/37650496218)
passes at `0ec6934`; [independent retained review](linux-timer-repair-observed.json)
verifies 13 tests/19 native cases, all packaged-source bytes, both complete DNA
exports, exact reload, all six strata/masks/zeros, serial stages, strict resume,
intended failure messages and native `1e100` safeguards with lock cleanup.
Product suite **36.198 s / 0.575-GB sampled peak**; full job wall **128 s**.
These are software costs, not biological evidence or exact provider billing.
Retained artifacts live under `artifacts/e008-product-execution/pr/linux-postfix/`;
prior receipts/attempts remain unchanged. Review still has no returned findings
or approval at this receipt. The final head required refreshing after that
record-only update; merge/publication/UCloud/benchmark work was not authorized
in the preparation task. The subsequent authorization is recorded below.

## Authorized private merge, 2026-10-07

The owner subsequently authorized completion and normal merge without another
approval, allowing inspected in-scope head changes. The head remained unchanged.
[PR #1](https://github.com/Rasmus-allesoee/dl_binner/pull/1) is **merged**;
[receipt](merge-observed.json) binds head
`ecf6ab822df741c6f7bb092826957b6ffc4e8771` to merge commit
`5bc824a9bf4b1ca4562acda10735a3fc6b54dc3d` and its two verified parents.
Product/source/default bytes match the accepted head and all referenced source
commits remain ancestors. Local main was fast-forwarded to the merge.

[Final-head native Linux CI](https://github.com/Rasmus-allesoee/dl_binner/actions/runs/37651872364)
passed 13 tests/19 cases; retained evidence was reused, not rerun. Product suite
38.803 s / 573,874,176-byte sampled peak, software evidence only. The fresh watcher
confirmed ready before landing and merged at the authorized head afterward. No
review returned; no required reviewer or actionable finding/unresolved thread
remained. This is not independent review approval. No code fix was needed in
the merge task. The earlier stop-at-ready boundary is now superseded; prior
receipts, including their then-current authorization, remain immutable.

The repository is private; no release, publication, accepted science replay or
UCloud/benchmark/architecture execution occurred. The updated handoff recommends
one bounded independent human-associated benchmark **planning** task on a new
branch from updated main, preserving this software baseline. This is neither
execution authorization nor another architecture gate.
