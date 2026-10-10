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
does not meet this gate. The 180-second import cap is unchanged; the new bounded
30-minute clock covers the one-time copy/pack operation too (copy cap 20 minutes).
This is a ceiling, not a runtime forecast. Full tool preflight remains disabled.

Alternative: rebuild pinned environments from original package payloads. That
would add network/solver/version risk before demonstrating that current bytes
can run from local storage. Use it only if snapshot compatibility fails concretely.
No general relocation permission for other experiment prefixes is introduced.
