# E005: Linux deployment smoke and bounded GI assembly/depth pilot

Prepared: 2026-10-05. Execution: **native Linux smoke accepted**. Pilot scientific
outcome: **not assessed**. [D011](../../docs/decisions/D011-first-binner-prototype.md)
requests product validation after accepted [E004](../E004-first-binner/README.md),
not another architecture screen. No UCloud execution or three-way TNF/GLM/hybrid
comparison by Codex is authorized here. Accepted E001/E002/E003/E004 evidence stays unchanged.

## Deployment boundary

The [smoke configuration](smoke.json) and
[Snakemake DAG](../../workflows/first-binner/linux_smoke.smk) invoke the unchanged
E004 frozen installed wheel through actual prepare/train/save/reload/embed/cluster/
export commands. Twelve cached real E003 TNF rows span 500/768/1,000/2,500/10,000 bp.
Two synthetic sentinels test below-500 and no-fourmer exclusions. Explicit **synthetic**
two-sample depths exercise arbitrary row order, partial/all-zero masks and ordered
columns. The native fresh reader is checked on only two real rows against cached
TNF, not by repeating the accepted inference demonstrations. All rows, including
excluded/noise, remain in both assignment tables and FASTAs. No truth or biological
score is passed to this smoke.

The [owner driver](../../scripts/e005_owner.py) uses separate persistent binner and
workflow prefixes, exact offline hashed wheel locks, import origins, package-source
hashes and explicit 1–4-vCPU/at-least-12-GB allocation inputs. At four vCPUs,
Snakemake/CLI/OMP/BLAS agree on four; Torch interop one, loader zero, one native job
at a time. Linux affinity is limited to four allowed CPUs. Samples and native pool
reports distinguish actual use from thread requests; serial I/O/feature/graph
components and a tiny model will not saturate four CPUs throughout. A bigger node
is unjustified for this deployment smoke. Runtime/step resources are not a scaling
claim or provider invoice.

[Payload record](runtime-payloads.json), [binner lock](binner-linux.lock) and
[workflow lock](workflow-linux.lock) bind a fresh official standalone Python
3.12.10 distribution and CPU-only Torch 2.2.2+cpu, with Snakemake 9.16.3. The official
Python SHA256 was independently verified. Linux/Python target dependency metadata
closure passes. The returned native Linux execution is accepted below.
The original binary-only Snakemake resolution failed because connection_pool
0.0.3 has no wheel. Its small pure-Python wheel was built locally and bound by hash;
the failed resolution/build evidence is retained. No upstream scientific code or
accepted runtime was modified. Official references consulted 2026-10-05:
[CPU Torch recipe](https://pytorch.org/get-started/previous-versions/#v222),
[standalone distribution](https://github.com/astral-sh/python-build-standalone/releases/tag/20250409),
[standalone use](https://github.com/astral-sh/python-build-standalone/blob/main/docs/running.rst).
No network download, solver or compiler runs on the owner's node.

Only completed, fingerprint-matching prefixes may be reused, with entry probes and
pip/source/inventory checks. Fresh installs use unique prefixes; partial or failed
ones are preserved and never promoted/repaired silently. This is fresh standalone
installation, not relocation of an executed Conda prefix. The identical owner/
harness extraction policy omits the unused bundled terminfo database; its case
aliases caused a retained Mac extraction-test failure. Interpreter, libraries and
licenses remain unchanged; Linux execution passed its native check below. The driver stops on
nonzero exits/time/RSS ceilings and terminates observed children, returning logs
on failure. Before-site child progress/faulthandler distinguishes native startup
from parent waiting. It verifies completed-workdir dry-run schedules nothing,
then tests missing depth, corrupt checkpoint and overwrite refusal against the
actual CLI. New attempts keep prior outputs. Detailed rule logs, extended
benchmarks, terminal/progress, resolved commands/inventories and independent
CPU/RSS receipts are retained. Setup is included in allocated-cost accounting.

## Frozen pilot, launch only after native-smoke review

[Pilot protocol](pilot.json) is frozen before any pilot features or scores.
[Input manifest](pilot-inputs.json) and [all-contig table](pilot-contigs.tsv) bind
four GI genomes, **5,309 contigs / 12,924,259 bp** and every length stratum, including
**1,097 below-500 contigs / 341,158 bp**. The existing GI GSA and accepted all-length
coordinate records supplied these inputs; [input preparation](prepare_inputs.py)
selects by fixed salted genome hash after prospective fragmentation/size criteria,
then keeps **all** GSA contigs of selected genomes. Size ceilings: four genomes,
6,000 contigs, 20 Mb; per-genome fragmentation criteria/caps deliberately bias this
small product test toward a tractable short-inclusive panel. No genome is chosen
using prior binner scores; no genome count reaches the clusterer.

Alternatives considered: E001's filtered input misses the shorter contracts;
a random contig cap would leave partial-genome recovery denominators; the full
210,612-contig GI input is unsuitable for this first exact-neighbor/graph cost
check. A new real-assembler simulation adds acquisition/truth/setup before Linux
deployment is established. This whole-GSA-genome subset keeps a meaningful bounded
recovery denominator while using existing assets; real-assembler validation remains
separate and cannot be inferred from it.

This is a **controlled gold-standard assembly derivative** of the human-associated
CAMI HMP GI simulation, not real-assembler output or a whole-community benchmark.
AMBER and confirmed R95 will measure recovery of available assembled sequence,
not complete genomes absent from an assembly or marker-estimated MAG quality.
It shares E001's community and 1,332 retained IDs, so it is development data.
Selected exact accessions do not overlap E003's accession list; this does not
exclude homolog/strain/sequence overlap or establish independence. No GLM is used.
D005's hash-bound coordinate/alias/quarantine policy remains unchanged. Cross-origin
identical sequence is conservatively unconfirmed in R95, yet remains in bin-purity
denominators. No E001 population, scientific result or three-seed criterion changes.

Use two retained source FASTQs (GI samples **1, 4**) and prospectively select at
most one million complete pairs each by the frozen pair-hash rule. Map those reads
to the **exact E005 reference**, keeping every short reference contig. Define
explicit observed mean depth over the full contig length; bind sampled reads,
reference, BAMs, samples, commands, masks and zero observations. E001's accepted
depth/BAM reference covers only ≥2,500 bp and cannot supply shorter coverage.
Do not fabricate zeros or use truth-derived number_reads as features. Existing
large FASTQs remain on UCloud; no upload/remapping of accepted E001 is requested.
The source FASTA locator is provisional; the smoke returns a cheap read-only
existence/size inventory. Hash acceptance and actual mapping/coverage adapter tests
are requirements of later pilot preparation, not presumed complete now.

Two arms only: learned TNF+measured depth and raw TNF+the same depth, fixed E004
training settings/seed11/500-bp default and the same truth-free clusterer. Full
truth/noise/excluded denominators, AMBER per-bin/per-genome tables and confirmed
R95 (≥95% purity; ≥200-kb bin/genome) are retained, including all six length strata.
No tail filtering, oracle K, truth-selected settings, extra seeds or superiority
software gate. These two arms do not isolate abundance benefit. Empty bins and
declines remain reportable biological outcomes. Reuse E001's audited AMBER source/
prefix **read-only**, with current probes and byte/version provenance before launch.
Actual new adapters and a tiny mapped BAM/evaluation fixture must be tested first.

Initial pilot: four vCPUs / 12 GB, serial tools, working sampled RSS ≤8 GB,
feature ≤30 min, clustering ≤15 min/arm, science ≤2 hours, whole driver ≤3 hours
(at most 12 allocated vCPU-hours). These are ceilings, not runtime estimates.
Fresh source sampling/depth is new work; accepted inference/preprocessing is not
repeated. New storage review 10 GB, besides existing source assets. No automatic
larger data or architecture campaign. Full-community real-assembler validation,
release and the future three-way study are later separate scopes.

## Local checks and retained evidence

Local E005 binner and workflow prefixes are separate from earlier environments.
The binner reuses cached wheel bytes read-only, not old site packages. An initial
read-only coordinator preflight found a missing setuptools dependency and stopped
before the DAG; its prefix remains unchanged. A new isolated 9.16.3 workflow prefix
was installed with separate Mac wheels. All setup failures/logs remain in
ignored `artifacts/e005-linux-pilot/setup/`. Source-only staging/hash/metadata and
portable harness checks cannot prove Linux loader/ABI/native startup health.
The [operations guide](OPERATIONS.md) owns the exact transfer/job/return procedure.
The first staged driver passed real native Mac DAGs at four and one threads.
Transfer v2 additionally retains the verified bundle manifest on failures and
uses a parent alarm across hashing/extraction/setup, followed by evidence-only
collection. Earlier executed v1 snapshots/failed attempts remain untouched.
## Accepted local preparation, native Linux still pending

[Retained review](review_local.py) and [observed receipt](local-observed.json)
independently verify final transfer/return checksums, every retained file hash,
feature/sample axes, finite arrays, exact pre-save/reload equality and complete
DNA accounting without executing training or extraction again. Nine focused
deployment checks pass, including parent-timeout/failure provenance, the real
upstream Python archive's filesystem layout, immutable output/path protection and
observed-child cleanup. The complete unchanged CLI DAG ran from the extracted v2
archive with **no worker mocks**; earlier four/one-thread runs, repeated invocation,
completed-workdir resume and the semantic-invalid-depth DAG are retained. The latter
fails in **3.488 s** with no checkpoint and a checksum-bound failure return.

All **14 contigs / 52,235 bp** are accounted for. Cached real rows: twelve /
51,268 bp; synthetic sentinels: two / 967 bp. Depth is synthetic throughout.
Raw export: ten assigned, two noise, two excluded; learned export: twelve assigned,
zero noise, two excluded. These are **software accounting**, not utility scores.
Twenty epochs see all twelve eligible IDs; checkpoint reload max difference **0**.
Native final training reports four numerical threads, interop one, loader zero,
reconciled four-thread pools and 26,048 parameters (the two depth columns add inputs).

Final Mac DAG: **21.785 s**, **262,209,536-B sampled peak RSS (0.262 GB)**, sampled
average **1.073 CPUs**. Learning itself: **0.291 s / 0.845 process CPU s / 2.902 CPUs**.
Whole driver before collection: **39.513 s**, declared four-thread wall budget
**0.0439032 hours**. Local prefix installation lies outside that clock; these are
not Linux timings or allocated UCloud charges. The one-thread harness also passed,
with a shorter tiny DAG; do not infer four-core speedup or assembly throughput.
The recommended four-vCPU smoke checks the intended four-thread deployment limits,
not a claim that fourteen rows need four CPUs for speed.

The final attempt retains **106 hash-bound files / 958,336 logical bytes** at the
pre-collection inventory, plus its small return copy. Local disk-block reports:
binner prefix 805,248 KiB; workflow prefix 90,576 KiB; setup/download/test evidence
440,864 KiB; prepared ignored pilot DNA 12,828 KiB. These exclude separately retained
transfer/extracted/old-fixture copies. Preserve them; no cleanup is authorized.
The final upload archive is **302,178,719 bytes**, SHA256
`289568e4d000aed8228b9fb119e4586c4c0d94598165b7f7c29a165cadf2a835`,
from source commit `2f0b9a58bcf86f29f23b0f3bed16f31171a359f4`.
Installed-package source remains E004's accepted snapshot. Linux CPU wheels and
full standalone-prefix installation/loader/affinity behavior did not execute on
Mac; real filesystem extraction and target dependency closure were separate
checks. Native Linux acceptance is recorded below; the pilot and three-way study
remain unrun.

## Accepted native Linux return, 2026-10-05

[Independent review](review_linux.py) inspected `linux-smoke-kc6vz1qe` without
rerunning preparation, training or exports. [Receipt](linux-observed.json) owns
source/return/log hashes, runtime inventories, stage costs and observations.
Archive SHA256 `51b09e1589c584b72182c9501bea1e06508316f8f080a76eabed5d6786679773`
matches its uploaded checksum; all **124 retained-file hashes** verify. The two
Python 3.12.10 prefixes are independent, CPU Torch 2.2.2+cpu has no CUDA build,
all import origins stay inside their prefix, and exact wheel inventories match.
Pre-site child logs and pip checks pass. Affinity is `[0,1,2,3]`, numerical pools
and CLI/Snakemake budgets are four, interop one and loader workers zero.

Actual arrays preserve 14 IDs / 52,235 bp, the ordered synthetic two-sample depths,
zeros/masks and the two explicit exclusions. Tiny fresh TNF agrees with the
accepted cache. Twenty epochs see every eligible row; retained saved/reloaded
embeddings match **exactly**. Raw export: 10 assigned / two noise / two excluded;
learned export: 12 / zero / two. Every DNA string is present exactly once in each
export. Missing-depth, corrupt-checkpoint and overwrite checks exit nonzero in
0.256 / 1.339 / 0.049 seconds; completed-directory dry-run schedules nothing.
Accept this software work without repeating it. No synthetic-depth bin-quality
claim follows.

Owner allocation **4 vCPUs / 12 GB**. Driver including setup and evidence collection:
**83.81135 s / 0.0931237 allocated vCPU-hours**. Native DAG: **11.29225 s**, sampled
descendant peak RSS **306,741,248 bytes**, sampled average **0.847 CPUs**. Training
itself: 0.07436 s / 3.356 CPUs; startup and serial work explain lower full-DAG use.
The hashed inventory retains 977,407 logical bytes, excluding its own and open-log
bytes; compressed return is 703,082 bytes. Runtime/payload storage was not
inventoried in this return, so no observed total-storage claim is possible.
These are sampled measurements and allocation accounting, not an exact bill;
upload/owner idle are outside the driver clock. The existence/size inventory
confirms retained source FASTQs, GI GSA and AMBER locators, not their current bytes.

**Next:** implement/test the frozen sampling, mapping, explicit mean-depth and
AMBER/R95 adapters, then prepare one owner pilot packet. Keep all E005 uploads,
launch copies, terminal logs and returned archive/checksum under
`/work/Home/dl_binner/e005/transfer/`; previous smoke assets remain in place.

## Frozen pilot adapters, 2026-10-06

[Rule adapters](../../scripts/e005_pilot.py), [serial DAG](../../workflows/first-binner/gi_pilot.smk)
and [owner driver](../../scripts/e005_pilot_owner.py) implement the existing protocol.
[External runtime contract](external-runtime.json) pins audited AMBER bytes and
read-only E001 mapping/AMBER dependencies; accepted E005 runtime inventories and
installed package hashes are reprobed. No environment install, repair or relocation.
The packet carries the exact 13.13-MB prepared reference derivative, so no whole
GI source or large BAM/FASTQ upload is needed. Both sampled native BAMs are produced
against this reference; old length-filtered E001 coverage is unsuitable.

Sampling validates/hashes each entire interleaved source twice, retains at most one
million digest/ID/offset ranks without a sequence heap, then writes selected pairs
in original order with an auditable compressed ID/offset table. A source-pair-bounded ID set catches duplicates; source ordering and zero padding
are preserved rather than inferred from an anonymous numeric name. The ID set and
one-million-rank heap stay under the enforced 8-GB working cap; an estimated
2–4 GB at the source ceiling is a planning estimate, not a bulk measurement.
Malformed/mismatched/short/changed sources produce no successful receipt. Features
use explicit ordered columns GI_sample_1/GI_sample_4 and actual depth zeros.
Native full-position ID/length axes are required, including unused short references;
missing positions are an error, never synthesized missing observations.

Targeted primary source audit, 2026-10-06: samtools 1.24
[depth manual](https://www.htslib.org/doc/1.24/samtools-depth.html) and
[bam2depth.c](https://github.com/samtools/samtools/blob/1.24/bam2depth.c), plus
[strobealign v0.17.0](https://github.com/ksahlin/strobealign/tree/v0.17.0).
The code initializes the excluded mask to UNMAP/SECONDARY/DUP/QCFAIL; `-g 0x600`
removes DUP/QCFAIL and `-G 0x800` adds SUPPLEMENTARY, giving 0x904. Native `-aa`
includes unused references; omitted `-J`/`-s` preserve the frozen deletion/overlap
semantics. This narrow adapter audit reuses the completed design review and is
not a literature restart. Real native fixture checks must confirm these semantics
before science. [Native contracts](native_contracts.py) use actual real-DNA mapping,
SAM/BAM flags/CIGARs and native AMBER, not substituted workers.

Numerical work is serial: mapper four; sort/index main plus three; depth main plus
two BGZF workers plus one Python aggregator; Torch/BLAS/OpenMP four, interop one,
loader zero. Sampling/parsing and some graph work remain serial or I/O bound.
Rule guards enforce RSS/time and retain commands/resources; setup/science/parent
ceilings remain the precommitted 30 minutes/two hours/three hours. The driver adds
no model family, loss, tuning, coverage arm or seed. Both complete exports must
pass before the only truth-consuming evaluation path runs native AMBER and exact
confirmed R95. Recovery denominators preserve shorts/exclusions/noise and every
assigned unconfirmed base remains in bin-purity denominators. Software success
never requires winning against raw features.

Local adapter tests and measured fixture integration are recorded after their
source commit; they do not run or score the full frozen scientific pilot. Linux
smoke acceptance does not pre-accept the larger pilot. The owner alone executes
its [operations command](OPERATIONS.md), with all new transfers/logs/returns below
`/work/Home/dl_binner/e005/transfer/`. Full native source/lock/large-read Linux
contracts remain subject to this owner return.

Local v1 packet `51d203c` stopped at the native evaluator contract because the
rule dispatcher accessed sample settings even for an evaluation-only config.
The mapper and 71-base flag/CIGAR/depth checks had passed; no pilot training or
scoring ran. The attempt and failure return are retained. Restrict sample lookup
to sample/map/depth actions and prepare a separate v2 packet; never modify the
executed v1 copy. Native adapter checks and the actual DAG remain required.

Local v2 packet `b75e0fb` passed real native mapping/depth/AMBER contracts, then
completed both feature/train/export paths in the fixture before its verifier
incorrectly rounded reference depth to float32. E004 explicitly stores measured
depth in float64; the mismatch was only 8.62e-10 and was a verifier error. Compare
exact float64 values, retaining the same strict zero/mask/reload checks; no tolerance
relaxation or scientific-input change. Preserve the v2 failure and use a new v3
packet. Both local failures stopped dependent scoring and collected evidence.

After the complete v3 local fixture passed, audit the source reader against
E005's frozen pair contract: it never required increasing read-number order or
bare plus lines. V4 removes those unsupported assumptions, accepts zero-padded
names and valid optional plus identifiers, and still rejects duplicate/mismatched
pairs. Sampling ranks, source hashes, output order/counts and scientific protocol
are unchanged. New shuffled-name cases and the actual v4 packet remain required.

## Accepted local pilot adapter integration, 2026-10-06

[Independent retained review](review_pilot_local.py) and
[receipt](pilot-local-observed.json) own all four local attempts, input/return/
source hashes, exact runtime origins, costs and limits. The **actual checksum-
verified extracted v4 packet** from `49dc582b457e12030daab07a5f961a600772d820`
passed the complete production DAG in `gi-pilot-wkqd9q5a`, with no replaced workers.
The explicit local fixture skips Linux ABI/affinity, original large UCloud reads/
E001 installed-lock comparison and the production 10-GB space provision (uses
1 GB for this tiny fixture). Those entry/scale contracts remain pending on UCloud.

The fixture contains **21 real-DNA contigs / 546,369 bp**, 19 eligible / two below
500, and synthetic matching reads: 100 source pairs, 32 selected for each sample.
Shuffled zero-padded names and valid plus identifiers pass actual sampling, native
strobealign 0.17.0, samtools 1.24 mapping/sort/index/depth and ordered two-column
merge. The separate real SAM/BAM fixture confirms **71** aligned observations,
unused/short-reference zeros, MAPQ/BQ0, DUP/QCFAIL inclusion, 0x904 exclusion,
overlapping mates and M/= /X versus insertion/deletion/soft-clip behavior. Actual
AMBER API tables and exact R95 purity/recovery boundaries pass. Empty partitions,
short full denominators, unknown IDs and E001 aggregate-score parity have focused
checks. This narrow source/native audit does not restart architecture review.

Independent inspection verifies float64 depth equality, every zero/evidence mask,
finite ordered arrays, source DNA and all exported rows. Ten fixture rows have no
observed depth. Twenty fixed seed-11 epochs see all 19 eligible rows; saved/reloaded
embeddings match **exactly**. Raw: 13 assigned / six noise / two exclusions; learned:
19 / zero / two. These are fixture **accounting**, not a scientific bin-quality
result. The partial-DAG run finished sampling/mapping/depth first; the complete DAG
reused **62 completed files** with identical hashes and nanosecond mtimes. Final
completed-directory dry-run schedules nothing. The real rule guard stops fatal
workers/time limits and retains evidence. Seven new focused tests pass, including
unordered/padded IDs, duplicate/mismatched/malformed/changed inputs, complete depth
positions, conservative-score boundaries/parity and failed prerequisites. The
existing deployment tests exposed a test glob that selected a return archive as
an attempt; selecting `*/status.json` fixes the test without changing workers.

Final fixture costs: driver through collection **80.83376 s / 0.0898153 declared
four-thread wall hours**, not UCloud spend. Native preprocessing 10.63731 s;
remaining learned/raw/verification/evaluation DAG **22.78865 s**, sampled descendant
peak **417,955,840 bytes**, sampled average **0.960 CPUs**. Training 0.21067 s /
2.218 CPUs. Numerical four, interop one, loader zero remain unchanged. A cold
AMBER import/cache stage took 30.628 s and completed under its existing ceiling;
its child diagnostics are retained, without bypass or timeout enlargement.
Setup/downloads/tests/review lie outside the driver clock. The complete four-
attempt local driver budget was 0.281058 thread-wall hours; failures are included.
These tiny costs are not source-read throughput or large-input memory evidence.

The final inventory verifies **333 files / 1,947,235 logical bytes**, including
small retained native assets; compressed local return is 728,913 bytes. Heavy
FASTQ/SAM/BAM stay in the attempt with byte-bound inventory entries; the return
omits those copies and includes headers/commands/depths/arrays/all exports/scores.
Preserve all attempts, packets, prefixes and setup logs. Separate local mapping
and AMBER environments were created; earlier accepted runtimes/reference caches
were read-only and no E002/E003/E004 inference/demo was repeated. There is no
scientific pilot, Linux bulk-performance or three-way comparison result here.

The locally validated **v4** owner packet was 4,099,196 bytes, SHA256
`91bebee4f0b8f214849af1250ca31d3fbf1224d441ee59ef1a52302c9f561dee`. Its
owner-run preflight failure and replacement are recorded below; do not upload v4.

## Owner v4 preflight failure and v5 repair, 2026-10-06

The owner-returned v4 attempt `gi-pilot-636z_qd1` verified the transfer checksum,
passed the E005 binner/workflow and mapper probes, passed AMBER's `pip check`, and
successfully imported the hash-pinned AMBER source. It then stopped at the full
AMBER-inventory comparison after **172.976 seconds / 0.192216 allocated vCPU-hours**
on 4 vCPUs. No adapter-contract tests, read sampling/mapping, feature extraction,
training, clustering or evaluation ran; this is an execution-gate bug, not a
scientific result. Return archive SHA256:
`e937fc8218adabd7946dc242b27849d8a228971a193753c7bf1e29a886a68cef`.

E005 creates/owns its new binner and workflow runtimes under E005. It does not
install or store E005 environments inside E001; it reuses the existing accepted
E001 mapping and AMBER prefixes at their original paths, read-only, because those
exact tools already passed their native setup/smoke checks and are unchanged inputs
to this pilot. D006 permits this form of reuse. Moving/copying these prefixes would
not repair the failed comparison: the problem was the lock/inventory contract, not
the prefix location or a failed package import.

The supplied E001 `pip-freeze.txt` (SHA256
`685d5ab9472fbcc5d0e212a6a09cfc3563ae4a4569cc3becf71e341faf1a1067`) contains four
EasyBuild 5.3.1 distributions. E001's environment review confirmed these came from
`/home/ucloud/.local/...`, outside the AMBER prefix, and are absent from its clean
isolated inventory ([record](../E001-coverage-thinning/validation.md#environment-review-resolved-2026-09-18)).
The old check incorrectly required them in the isolated prefix. The same lock records
`pip` and `packaging` as direct file URLs rather than `name==version`; the old parser
dropped both. Their versions, 25.1.1 and 26.3, are recorded in the prior clean-prefix
inventory. The clean baseline is `environment-review/amber-clean.stdout` (member
SHA256 `59df159b7c3c2823e91664e1bcb19c6a0e4cadc39f72bef4e52e443c44fb10c3`) from the
E001 environment-review archive (SHA256
`b00b14cc6665b6ff7a6c12fb8a0a284596ff75bebc5a4f923864fec64e7a6819`). V5 records
the complete clean-prefix distribution inventory together with these hashes, then checks the original lock
hash, exact pinned versions, those two direct-reference resolutions, and the live
inventory against that independent baseline. The native probe still requires every
discovered distribution and import to remain inside AMBER. A `runtime-preflight.json`
is returned before this comparison so a future failure preserves both the actual
inventory and original lock.

The v4 read-only Python probes used `-I` while relying on
`PYTHONDONTWRITEBYTECODE`; isolated mode ignores that environment variable, so those
imports may have added `.pyc` cache files under the reused AMBER prefix. The return
does not establish whether any were written. V5 uses command-line `-B` for all
read-only Python checks; it does not delete or alter existing prefix contents.

**Current owner packet: v5.** Its exact source commit, archive size and checksum are
recorded here after the packet is built. [Operations](OPERATIONS.md) supplies the
four-vCPU/12-GB command and requires upload under
`/work/Home/dl_binner/e005/transfer/`. After v5 passes runtime and adapter checks,
the same frozen pilot runs once. Return its archive/checksum/captured terminal log;
then review assembled-recovery quality beside the raw control and measured costs
before choosing a product fix or small release-readiness milestone. No superiority,
extra seed/input or new architecture gate is required.
