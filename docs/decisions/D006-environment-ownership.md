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
from preserved package/source records. They must not mutate an older experiment's
runtime. Promote proven identical stacks to project-level immutable prefixes only
when real multi-experiment demand makes the maintenance/storage benefit concrete.
No such migration is required now. The remaining limitation is that pip freeze
and Conda records are not a complete portable wheel archive; keep that distinct
from the location decision and improve replay artifacts as runtimes stabilize.

## Operational Consequence

COMEBin and MetaBAT2 now execute in one owner-run task. Each tool's setup must pass
before its smoke, and smoke before its CPU check. An ordinary tool failure skips
only its dependent stages; the other isolated tool proceeds. Global prerequisite
failure stops both. Return one archive with per-tool outcomes for review. Do not
repeat settled mapping, AMBER, VAMB or input-population checks in this task.
