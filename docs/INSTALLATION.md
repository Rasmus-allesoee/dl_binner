# Standalone CPU installation and engineering checks

The current candidate is **0.1.0.dev4**, built locally, not published. Keep dev3's
original wheel/runtime and accepted evidence immutable. Use a fresh independently
owned CPU environment; do not upgrade an executed research prefix. Venvs depend
on their base Python/stdlib. Invoke lexical `bin/python`, never its resolved target.

Recommended future Linux target: x86_64/Python 3.12. Current candidate checks use
native Mac x86_64/Python 3.10; new Linux checks are a required gate before a
community run. Earlier dev3 Linux acceptance is not dev4 acceptance. Python
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
build_env="$PWD/.venv/builder-0.1.0.dev4-v1"
build_out="$PWD/artifacts/build-dev4-v1"
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
candidate_env="$PWD/.venv/candidate-0.1.0.dev4-v1"
wheel_path="$PWD/artifacts/build-dev4-v1/rebuilt/dl_binner-0.1.0.dev4-py3-none-any.whl"
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
python3.12 -I -B scripts/test_product.py --python "$candidate_env/bin/python" --threads 2 --timeout 1800 --output "$PWD/artifacts/candidate-product-v1"
BASH
```

Inventory/import checks deliberately isolate tensor, graph and marker libraries
in separate processes. Some Mac wheels ship incompatible Intel/LLVM OpenMP
runtimes: do not co-import them or set a global duplicate-library override.
The production pipeline also isolates train/embed from graph construction.
CPU requests, OpenMP/BLAS pools, Numba jobs and HMM search concurrency are explicit;
loader workers are zero and stages run serially. The test budget is not a product
maximum. Each test run is tiny software evidence, not a community quality result.

## Run product regressions

The installed suite runs outside the checkout, with generated DNA/HMM fixtures,
real training/reload/graph/gene/HMM/export paths and strict recovery/failure
contracts. Research assets and helpers are not required. Inspect actual logs and
exit/resource receipts; test counts alone do not establish readiness.

The base `requirements/binner-cpu.txt` still supports the preserved dev3 algorithm
commands (`run`, etc.) in dev4, but the full package/version/journals are new.
Reproducing accepted dev3 science requires its original hash-bound wheel/source;
never refit it merely to populate an upgraded comparison.

See [candidate usage](PROTOTYPE.md#integrated-dev4-candidate),
[E010 evidence/protocol](../experiments/E010-coherent-prototype/README.md) and its
[separate execution boundary](../experiments/E010-coherent-prototype/OPERATIONS.md).
