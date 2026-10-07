# E008: Product execution and private PR validation

Prepared 2026-10-07; status **local checks accepted; private PR CI/review next**, biological outcome **not assessed**.
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
