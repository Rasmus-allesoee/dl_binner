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
in original order with an auditable compressed ID/offset table. The increasing
anonymous E001 R-number invariant catches duplicates without a 20-million-ID set.
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
