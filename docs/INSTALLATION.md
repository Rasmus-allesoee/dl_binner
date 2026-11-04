# Standalone CPU installation and engineering checks

The current research package is **0.1.0.dev9**, built locally, not published. Keep dev3/dev4's
original wheels/runtimes and accepted evidence immutable. Use a fresh independently
owned CPU environment; do not upgrade an executed research prefix. Venvs depend
on their base Python/stdlib. Invoke lexical `bin/python`, never its resolved target.

Recommended future Linux target: x86_64/Python 3.12. Current candidate checks use
native Mac x86_64/Python 3.10; each new candidate needs its own Linux/source/runtime gates before community work. Native dev4
acceptance does not validate the changed learning code. Python
3.10–3.12 is supported by package metadata; Windows/GPU are unvalidated.

## Build from fresh source

A dirty reused build directory previously leaked an obsolete file. This bounded
helper copies only current package/reproducibility files into a fresh snapshot,
retains every source hash, invokes separate backend hooks and checks wheel/sdist/
rebuilt-wheel logical contents. It installs/publishes nothing. Keep its failed
attempts too. Run from the repository, with a new output path each time.

```sh
bash <<'BASH'
set -euo pipefail
unset PYTHONPATH PYTHONHOME PYTHONUSERBASE
export PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 NUMEXPR_NUM_THREADS=2
build_env="$PWD/.venv/builder-current"
build_out="$PWD/artifacts/build-current"
test ! -e "$build_env"
python3.12 -I -B -m venv --copies "$build_env"
"$build_env/bin/python" -I -B -m pip --isolated install --only-binary=:all: -r requirements/build.txt
python3.12 -I -B scripts/build_candidate.py --python "$build_env/bin/python" --output "$build_out" --threads 2 --timeout 300
BASH
```

For the tested Mac recipe, use an explicit Python 3.10 in those creation/helper
commands. Fresh clone/snapshot builds avoid copying ignored data, old build
products or numerical prefixes. The helper also checks all preserved dev3
scientific files against their original hashes.

## Install the complete candidate runtime

Version pins include transitives; they are not cross-platform wheel hashes.
Linux Torch CPU is installed first from the official CPU index; Mac uses its
platform Torch wheel. Candidate requirements add the graph and gene/HMM libraries.
This setup needs a few GB of free disk; no read/model/database payload is fetched.
Marker profiles are a separate explicitly supplied asset, never auto-downloaded.

```sh
bash <<'BASH'
set -euo pipefail
unset PYTHONPATH PYTHONHOME PYTHONUSERBASE
export PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 NUMEXPR_NUM_THREADS=2 NUMBA_NUM_THREADS=2
candidate_env="$PWD/.venv/candidate-0.1.0.dev9-v1"
wheel_path="$PWD/artifacts/build-current/rebuilt/dl_binner-0.1.0.dev9-py3-none-any.whl"
test -f "$wheel_path"
test ! -e "$candidate_env"
python3.12 -I -B -m venv --copies "$candidate_env"
if [[ $(uname -s) == Linux ]]; then
  "$candidate_env/bin/python" -I -B -m pip --isolated install --no-deps --only-binary=:all: 'torch==2.2.2+cpu' --index-url https://download.pytorch.org/whl/cpu
elif [[ $(uname -s) != Darwin ]]; then
  exit 2
fi
"$candidate_env/bin/python" -I -B -m pip --isolated install --no-cache-dir --only-binary=:all: -r requirements/candidate-cpu.txt
"$candidate_env/bin/python" -I -B -m pip --isolated install --no-deps "$wheel_path"
"$candidate_env/bin/python" -I -B -m pip check
"$candidate_env/bin/python" -I -B scripts/check_runtime.py --role candidate --requirements requirements/candidate-cpu.txt --threads 2 --output "$PWD/artifacts/candidate-runtime-v1.json"
"$candidate_env/bin/dl-binner" candidate --help
python3.12 -I -B scripts/test_product.py --python "$candidate_env/bin/python" --threads 4 --timeout 1800 --output "$PWD/artifacts/candidate-product-v1"
BASH
```

Inventory/import checks deliberately isolate tensor, graph and marker libraries
in separate processes. Some Mac wheels ship incompatible Intel/LLVM OpenMP
runtimes: do not co-import them or set a global duplicate-library override.
The production pipeline also isolates train/embed from graph construction.
CPU requests, OpenMP/BLAS pools, Numba jobs and HMM search concurrency are explicit;
loader workers are zero and stages run serially. The full regression suite uses
four numerical threads because retained graph fixtures bind that geometry. Run it
on a host with at least four logical CPUs. Each test module starts a fresh process,
so tensor imports cannot contaminate graph-only workers. This validation allocation
is not a product maximum. Each test run is tiny software evidence, not a community
quality result.

## Run product regressions

The installed suite runs outside the checkout, with generated DNA/HMM fixtures,
real training/reload/graph/gene/HMM/export paths and strict recovery/failure
contracts. Research assets and helpers are not required. Inspect actual logs and
exit/resource receipts; test counts alone do not establish readiness.

The base `requirements/binner-cpu.txt` still supports the preserved dev3 algorithm
commands (`run`, etc.) in dev5, but the full package/version/journals are new.
Reproducing accepted dev3 science requires its original hash-bound wheel/source;
never refit it merely to populate an upgraded comparison.

See [candidate usage](PROTOTYPE.md#integrated-dev4-candidate),
[E010 evidence/protocol](../experiments/E010-coherent-prototype/README.md) and its
[separate execution boundary](../experiments/E010-coherent-prototype/OPERATIONS.md).

Dev5 adds the explicit [multiview stage interface](PROTOTYPE.md#multiview-reconstruction-candidate-dev5).
Its CPM/E013 downstream path is distinct from the preserved `candidate` command.
E014 records actual installed Mac contracts and the separate unpassed community/
Linux admission. Do not apply changed package metadata to prior executed journals.

The E033 `dl_binner.multiscale` research stages require pinned pysam 0.23.3 (now
in the candidate recipe; also available as the smaller `multiscale` extra). The
[experimental protocol](../experiments/E033-multiscale-bam/OPERATIONS.md) has real
local tiny checks and a separately authorized native comparison; it is not a
promotion of a new default or an instruction to replay accepted cloud science.
Its current research environment explicitly borrows the complete accepted
numerical base read-only and owns the new package/BAM extension. That linked
environment is not a portable standalone installation. Use this fresh recipe
for an independent installation, and a builder in the package's supported
Python range (>= 3.10, < 3.13). Native CI/platform validation remains separate.
