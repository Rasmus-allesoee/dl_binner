# D006: Experiment-Owned, Separate Tool Environments

Status: accepted, 2026-09-20.

## Decision

Retain option 1: persistent experiment-owned tool environments. E001's environment
home remains `/work/Home/dl_binner/e001/e001-gate0/envs/`. The `gate0` name is a
historical locator, not a requirement to rebuild environments at each later gate.
Every E001 gate reuses those same validated prefixes:

| Tool | Prefix below the E001 work root |
| --- | --- |
| Mapping | `envs/mapping` |
| AMBER | `envs/amber` |
| VAMB | `envs/vamb` |
| COMEBin | `envs/comebin` |
| MetaBAT2 | `envs/metabat` |

Grouping execution means coordinating separate processes, environments and logs,
not merging dependencies. Do not move/copy a live Conda prefix to a new path,
silently upgrade a used environment or rewrite an executed snapshot. Preserve
attempts, resolved inventories, binaries/patch hashes and source versions. Create
a distinct version-qualified prefix for a changed recipe; explicitly bind future
runs to it after validation. Existing E001 prefixes require no migration.

## Reasoning and Alternatives

- **Option 1, selected:** one experiment owns its dependency lifecycle and results.
  Current scripts already enforce separate prefixes and capture source/package
  records. All live paths are persistent under `/work`; moving upward confers no
  extra UCloud persistence. Mapping, AMBER and VAMB are already validated here.
  Reusing their prefixes across E001 gates avoids installation duplication.
- **Option 2, project-level separate tool environments:** sensible when several
  active experiments demonstrably need identical stacks, but tool-name-only
  prefixes risk shared mutation. Immutable version-qualified environments could
  avoid that risk; we do not yet have multi-experiment reuse that justifies
  relocation/rebuilding or an environment registry. Location alone does not make
  an environment reproducible.
- **Option 3, reusable bases with exceptions:** rejected as the default. VAMB uses
  Python 3.12 / NumPy 1.26 / PyTorch 2.6, whereas this COMEBin snapshot specifies
  Python 3.13 / NumPy 2.4 / PyTorch 2.13; AMBER and mapping have other contracts.
  A common Python base invites solver churn and cross-tool coupling. Conda package
  caches already offer package reuse without sharing mutable import namespaces.

Future experiments may reference an existing accepted prefix read-only, recording
its exact provenance and retention dependency, or recreate an isolated prefix
from preserved package/source records. Cross-experiment reuse must compare the
full runtime inventory and import origins with a clean, hash-identified prefix
record; a `pip freeze` alone may contain user-site packages or direct references.
They must not mutate an older experiment's runtime. Promote proven identical
stacks to project-level immutable prefixes only when real multi-experiment demand
makes the maintenance/storage benefit concrete. No such migration is required now.
The remaining limitation is that pip freeze and Conda records are not a complete
portable wheel archive; keep that distinct from the location decision and improve
replay artifacts as runtimes stabilize.

### Job-local Workflow Execution Copy, 2026-09-23

Narrow exception to the no-copy rule above: E001 may execute the reviewed
workflow snapshot on job-local `/tmp` to avoid observed persistent-filesystem
read stalls. This is an immutable execution copy, not a replacement authoritative
environment, shared base, changed recipe or silent relocation. The original
`envs/workflow` and all other tool environments remain untouched under Home.

The owner-supplied archive is bound to SHA256
`0fb6955cdc6263079d2f8f1a32c14037c29d5c90d16c3b3be233ea257c6ab103`.
The worker extracts only regular files/directories into a unique local prefix,
records provenance persistently, and invokes **that prefix's Python directly**.
Do not execute the copied console-script shebangs: they point to the original
prefix. Validate the local interpreter, standard library and distribution
origins, exact accepted sample-0 pip inventory, actual CLI, and DAG before any
acquisition. Snakemake's local executor uses `sys.executable` for child jobs;
mapping workers still use their explicit persistent mapping interpreter.

No package installation, upgrade, prefix rewriting or deletion is authorized.
The copy needs about 0.75 GB and is disposable at job termination; logs and
scientific outputs remain persistent. Recreate it from the same verified archive
in a fresh job, not from an arbitrary previous temporary directory. This is not
general permission to copy other Conda environments: each has its own binary,
prefix and entry-point constraints. Native validation remains a gate, not an
assumption that every Conda prefix is portable.

## Operational Consequence

COMEBin and MetaBAT2 now execute in one owner-run task. Each tool's setup must pass
before its smoke, and smoke before its CPU check. An ordinary tool failure skips
only its dependent stages; the other isolated tool proceeds. Global prerequisite
failure stops both. Return one archive with per-tool outcomes for review. Do not
repeat settled mapping, AMBER, VAMB or input-population checks in this task.


## E009 cache-read isolation, 2026-10-10

The reviewed [v5 return](../../experiments/E009-competitive-benchmark/linux-startup-failure-v5.json)
shows 162 bytecode waits among 175 file waits. The original read-only prefix policy
remains: no installs, upgrades or arbitrary relocation. `-B` does not disable
reading existing caches. E009 may use explicit `-X pycache_prefix` pointing to an
empty job-owned temporary namespace together with `-B`, loading the same source
without cache writes. This is cache lookup isolation, not a new dependency recipe
or a moved authoritative prefix. [Operations](../../experiments/E009-competitive-benchmark/OPERATIONS.md)
freeze a cheap actual-read/import recovery before returning to the full allocation.

Do not claim that this repairs all filesystem waits: the same return includes
source/native-library/metadata waits. A Linux pass, full inventories/origins,
child propagation and original source/library byte binding are required before
full native admission. A later binding may explicitly omit ignored, regenerable
bytecode; it must label that scope and retain actual executable source/binary
bytes. This recovery only binds sample source bytes. Packed-prefix execution or a
changed pinned runtime needs its own reviewed identities/portability checks;
this amendment does not extend E001's snapshot relocation exception automatically.

## E009 numerical execution snapshot, 2026-10-10

The [v6 return](../../experiments/E009-competitive-benchmark/linux-startup-failure-v6.json)
supersedes direct Home imports and the cache-only workaround: all 34 observed
file-read waits were on source files. The unchanged ten-module inventory consumed
2.94 sampled CPU seconds in 180.170 seconds. This is an execution-storage problem,
not evidence against the selected tools or a reason to increase import deadlines.

Permit this **specific E009 COMEBin numerical prefix** to have an immutable
job-local execution snapshot. The original authoritative prefix remains under
E001 and untouched. Copy regular files byte-for-byte and modes unchanged; omit
only regenerable bytecode. Reject venvs, external symlinks and special files;
normalize internal symlinks to equivalent relative targets. Do not activate or
run copied console scripts, whose shebangs can refer to the old prefix. Invoke
the snapshot's lexical Python directly with isolated imports and no cache writes.

The worker hashes original bytes while copying, verifies the complete source file
set/stat identities remained unchanged, and checks every local hash. It retains a
hash-bound, uncompressed archive and inventory under E009 for explicit reuse,
including on an import failure; partial copies are never admitted. Eight I/O
readers overlap filesystem latency under a one-CPU affinity; this is not eight
CPU workers or permission to overcommit numerical threads. No original files,
embedded binary prefixes, package versions or scientific settings are rewritten.

Portability remains conditional, as [Conda-pack](https://conda.github.io/conda-pack/)
documents. A real Linux pass must establish exact Python version, full accepted
freeze, distribution/module/standard-library origins, no old-prefix mapped
libraries, and small NumPy/Torch forward/backward arithmetic. Local copying alone
does not meet this gate. The initial v7 180-second import /20-minute copy caps and 30-minute overall
clock were superseded by the measured-workload amendment below. Preserve the
executed v7 source/packet and its failed return; full tool preflight remains disabled.

Alternative: rebuild pinned environments from original package payloads. That
would add network/solver/version risk before demonstrating that current bytes
can run from local storage. Use it only if snapshot compatibility fails concretely.
No general relocation permission for other experiment prefixes is introduced.

## E009 reduced, resumable runtime amendment, 2026-10-10

[V7 evidence](../../experiments/E009-competitive-benchmark/linux-startup-failure-v7.json)
shows 44,770 entries versus the local 13,829-entry fixture and a steady copy killed
at 1,200 seconds. Full entry-count projection is ~49.8 minutes plus verification/
packing; the local fixture did not justify the cap. Reject that cap/packet for new
execution. Preserve the failed attempt and original E001 prefix.

The snapshot need not reproduce a compiler/tool/test installation. V8 retains
ordinary Python/package sources/resources/models, full distribution metadata and
licences, runtime shared libraries and required internal-link targets. Record
explicit omissions of bundled test suites, compiler/header/build/static payloads,
non-Python executables and other non-numerical top-level files. Preserve public
`testing`/`_testing` helpers. This changes the execution payload, not package
versions, the model, transforms, scientific settings or accepted results. Native
complete inventory/ABI/import/arithmetic checks still gate acceptance; subsequent
real tool/fixture checks must show that the reduced runtime serves their paths.
Do not infer general portability or support for compiling/testing these packages.

Choose persistent checksum-bound chunks instead of one final monolithic archive:
seal every <=128-member /approximately 128-MB group (large single files stream as
individual groups), so interruption preserves completed work across job resets.
Explicit resume validates the source/selection plan, restores verified sealed
bytes, and schedules only missing source copies. Keep the completed inventory
receipt immutable; per-attempt operation counts belong to attempt summaries. No seal means no acceptance;
corrupt/changed inputs or outputs fail, and unsealed partials remain evidence.
Portable source stat identities exclude mount-local device/inode numbers across
jobs; within each copy those numbers and size/mtime are checked. Copied content
hashes and source plan bind the retained payload, not a historical whole-prefix
cryptographic identity that we do not possess. Original files remain untouched.

Use actual completed byte/entry progress with a justified stall guard and one
owner-selected overall ceiling. No arbitrary lower copy/verification/pack/import
caps. The proposed one-CPU 90-minute ceiling uses v7's ~50-minute entry projection
plus ~40 minutes for variability and remaining operations; new native selection/
byte throughput is unmeasured. Five-minute stall allowance exceeds the normal
five-second reports by ~60 times. These are planning choices, not validated Linux
runtimes. Parent setup and all consumers use the same clock. A budget stop retains
sealed progress; it does not authorize automatic retries or accepted-science reruns.
Local tests must cover native-size metadata cardinality, actual readers/writers,
interrupted and complete resume, corruption, drifting sources, productive work
past former subcaps, genuine stalls and cleanup. Operations own the command.


## Accepted E009 numerical runtime and restore-only consumers, 2026-10-10

[The v8 Linux return](../../experiments/E009-competitive-benchmark/linux-runtime-recovery-v8.json)
passes the scoped full inventory/origin/ABI/arithmetic gate for the reduced
numerical runtime. It does not admit the other environments, native tool feature
contracts, compiler capability or community-scale training. All 151 chunks and
final inventory stay authoritative/unchanged; v9 binds their reviewed receipt and
seal/archive/member hashes and restores read-only. Missing/corrupt retained bytes
fail explicitly, without falling back to fresh source copying. The fresh native
v8 attempt did not execute restore; restored consumers remain a native test.

Tool execution venvs bind the restored job-local prefix explicitly; preserve their
lexical interpreter paths. Their retained /tmp-dependent bindings are executed
provenance, not portable/reusable environments after job reset. Future jobs create
new bindings after restore rather than mutate an accepted one. The separately
bound CheckM console source is invoked through isolated Python, never its old
shebang; external marker payloads remain pinned/read-only. Original AMBER/mapping
prefixes still require their own native health and byte/origin checks.

Every native import/install/help/extractor and nested process now shares the
owner-selected overall clock, with no lower stage wall caps. Completed bytes/
entries guard restore; launched-tree CPU/physical I/O guards native computation/
transport, and startup phase/stack/file movement guards cold imports. Heartbeats
are not accepted work. Bound CI/local fixtures separately; a quiet CPU computation
must not be killed merely because it emits no log output. V9's five-hour ceiling
is the existing bounded cold-setup/source/native-contract allocation, not a
performance projection from the 161-second recovery. Native timings remain pending.


## E009 scoped reuse amendment, 2026-10-10

The [cancelled v9 review](../../experiments/E009-competitive-benchmark/linux-cancellation-v9.json)
shows complete restore of all 151 accepted chunks in approximately nine seconds,
then completed AMBER target validation after slow persistent-storage imports.
The next parent path silently hashes five entire directory trees. Remove this
redundant blanket operation; it is not necessary to protect original data.

V10 verifies the accepted numerical members once during read-only restore,
retains full per-tool inventories/origins, isolated no-cache-write Python and
separate owned installation targets. Bind **26 explicitly declared external
files** before/after: two mapping binaries, CheckM console source, three pinned
marker inputs and twenty pinned AMBER source/licence files. Report lexical and
resolved paths, hashes and advancing byte counts. This assurance does not claim
whole-prefix non-mutation or cryptographic identity of all AMBER/mapping libraries.
Do not recursively scan old environments, snapshots or shared data for a storage
summary; report this attempt, immutable returned members and explicit payload
receipts instead. The accepted v8 receipt/chunks and old attempts remain intact.

Fresh separate E009 Conda stacks are practical in principle and preferable when
an incompatible dependency requires a distinct recipe. They do not directly fix
an unnecessary recursive verification call: the same code would scan new stacks,
and Home-based installs could retain the observed cold-read latency. Current
records include numerical inventories but not a complete replayable explicit
Linux payload lock for five independent numerical stacks. Rebuilding would add
network/solver/payload verification and duplicate storage before native tool
compatibility is known. Choose simplified reuse for this retry, rather than add
another setup project. Revisit a fresh per-tool recipe only upon a concrete
compatibility or persistent-runtime failure; never modify the E001 environment.
Benchmark shortlist, sources, models and scientific settings remain unchanged.


## E009 failed-path ownership amendment, 2026-10-10

[The v10 return](../../experiments/E009-competitive-benchmark/linux-preflight-v10.json)
passes three tool contracts, Linux eight-thread assembly/mapping/evaluator, source
acquisition and the 26 scoped read-only checks. It exposes two concrete problems:
SCGBinner imports sklearn's internal `stable_cumsum`, absent in shared 1.9.0;
CheckM imports `checkm.test.test_ecoli`, excluded by the runtime pruning policy.
A venv linked to one base neither owns independent dependency versions nor repairs
missing contents. The earlier simplified-reuse choice is therefore amended for
**these failed paths only**; no reason exists to rebuild the three passed paths.

Choose independent E009-owned Conda stacks for SCGBinner and CheckM, pinned by
[the complete explicit Linux payload lock](../../experiments/E009-competitive-benchmark/failed-paths-lock.json).
SCGBinner's README combines Python3.9/NumPy1.19/pandas1.4 with sklearn>=1.6;
package metadata declares only numpy/pandas. Do not mechanically treat either as
a validated complete recipe. The named CPU compatibility stack uses Python3.10.15,
NumPy1.26.4, pandas1.5.3, sklearn1.6.1 and all-Conda CPU Torch2.0.0 (distribution2.0.0.post104) (the upstream Torch version,
CPU build). This version exports the needed private imports. The existing int
alias repair stays; no new cluster/model/training patch. Omit unused torchvision/
torchaudio CUDA installation; actual source imports and CPU native tests gate use.

COMEBin retains its accepted numerical stack and uses **complete CheckM1.2.3 in a
separate owned Conda prefix**, with its own NumPy/SciPy and setuptools80.9.0 for
`pkg_resources`. Its wrapper replaces inherited numerical LD_LIBRARY_PATH and uses
that prefix's lexical isolated Python. The full package retains test_ecoli and
native dependencies (including Linux pplacer); the import and actual CheckM help
must pass, followed by COMEBin's real augmentation writer/reader. Do not install
CheckM into an accepted snapshot or restore stub test modules. Frozen marker data
stays read-only at E001. This is deliberate separate-tool execution, not a claim
that COMEBin's main numerical stack is independent of its accepted snapshot.

Linux recipes are solved against glibc>=2.28 with exact package URL/size/hash/build
identities; no remote dependency solve occurs in the owner command. Total locked
compressed bytes before shared-cache deduplication: 577,118,190. New prefixes use
complete package contents and copies, with full import-origin/required-version and
Conda identity checks. No whole-environment hashes, new snapshots or pruning.
The corrected Linux recipes remain unexecuted until owner return. On Mac,
CheckM's pinned Linux pplacer build is unavailable; local CheckM validation uses
matched Python dependencies and the complete official 1.2.3 wheel. This tests its
missing-module/CLI contract, not native Linux pplacer or lineage fitting.

Local integration rejected the first mixed Conda/pip SCGBinner Torch2.0 recipe:
CPU thread setup crashed despite successful imports. The all-Conda CPU Torch2.0
build104 stack passes four-thread setup locally. Preserve the rejected v11 packet,
failed logs/prefixes and source a6e88c3; do not extrapolate its Mac crash to Linux.
Use the coherent all-Conda recipe in v13. COMEBin's already accepted full Linux
help is reused; its unchanged feature API and real parser/defaults execute without
training-only AMP imports on the older Mac validation stack. This limits the
local contract to native features, not training or Linux CheckM/pplacer execution.

The next local packet (v12) passed SCGBinner's full feature/initializer/HNSW
contract, then exposed CheckM1.2.3's unsupported top-level --help. Use the actual
lineage_wf -h parser (passes on the complete local package), retaining that failed
attempt. V13 also verifies its owned Linux HMMER/Prodigal/pplacer entry points;
Mac has no pinned pplacer build, so Linux checks and lineage placement receive no
local acceptance. No native implementation/algorithm is patched for this CLI fix.
