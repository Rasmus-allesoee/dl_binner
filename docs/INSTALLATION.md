# Standalone CPU installation and product checks

Use a locally built **0.1.0.dev3** wheel and a fresh binner CPU environment. It owns its dependency payloads,
not links to research prefixes. The built-in serial runner needs no Snakemake.
Existing runtimes/wheels stay untouched. Python venvs still depend on their base
Python/stdlib; retain that base. Invoke lexical `bin/python` paths, not resolved
interpreter symlinks.

The recommended CPU/Linux target is **x86_64 / Python 3.12** for the binner runtime.
E006's accepted Linux execution borrowed reviewed dependencies; E008 accepts an independent
CPU/Linux installation and actual native product CI on the recorded head. E007
tested Mac x86_64 Python 3.10; E008 validates the changed product;
read its actual CI status before claiming native Linux acceptance. Neither is an
exhaustive matrix. Binner requires 3.10–3.12. Windows is unsupported.

## Install a wheel

From the source tree, keep `requirements/` available for setup. Those files pin
complete accepted distribution versions, including transitives; they are **not
cross-platform wheel hashes**. Linux explicitly uses `torch==2.2.2+cpu` from the
[official CPU wheel index](https://pytorch.org/get-started/previous-versions/#v222).
Mac uses `torch==2.2.2`. No torchvision/torchaudio, GPU, data or model download.

This fail-fast Bash group creates fresh version-qualified prefixes, downloads
pinned binary dependencies and installs a local wheel. A few GB of free disk
permits runtime/cache copies; actual storage varies. Setup is not a binning run.

```sh
bash <<'BASH'
set -euo pipefail
unset PYTHONPATH PYTHONHOME PYTHONUSERBASE
export PYTHONNOUSERSITE=1
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4 VECLIB_MAXIMUM_THREADS=4 NUMEXPR_NUM_THREADS=4
binner_env="$PWD/.venv/binner-0.1.0.dev3-v1"
wheel_path="$PWD/dist/dl_binner-0.1.0.dev3-py3-none-any.whl"
test -f "$wheel_path"
test ! -e "$binner_env"
python3.12 -I -B -m venv --copies "$binner_env"
"$binner_env/bin/python" -I -B -m pip --isolated install --only-binary=:all: pip==25.1.1 setuptools==65.5.0 wheel==0.45.1
if [[ $(uname -s) == Linux ]]; then
  "$binner_env/bin/python" -I -B -m pip --isolated install --no-deps --only-binary=:all: 'torch==2.2.2+cpu' --index-url https://download.pytorch.org/whl/cpu
elif [[ $(uname -s) != Darwin ]]; then
  echo 'Supported native systems: Linux and macOS' >&2; exit 2
fi
"$binner_env/bin/python" -I -B -m pip --isolated install --only-binary=:all: -r requirements/binner-cpu.txt
"$binner_env/bin/python" -I -B -m pip --isolated install --no-deps "$wheel_path"
"$binner_env/bin/python" -I -B -m pip check
"$binner_env/bin/python" -I -B -c 'import sys,torch,numpy,dl_binner; print(sys.executable,sys.prefix,dl_binner.__file__,torch.__file__,numpy.__file__); assert torch.version.cuda is None'
"$binner_env/bin/dl-binner" --version
"$binner_env/bin/dl-binner" run --help
BASH
```

For the locally tested Mac recipe, use explicit Python 3.10 for binner/builder
at the creation lines. Keep pins; diagnose actual install errors.
Offline setup adds `--no-index --find-links /absolute/wheelhouse` to pip commands
instead of the online index. It needs the full compatible Python/OS/architecture
closure. Linux cp312 wheels cannot serve Mac cp310. E007 tests actual installation
from hash-recorded read-only caches, not importing their libraries directly.

## Build and inspect wheel plus sdist

Use a fresh builder with [build pins](../requirements/build.txt). Build-only
setuptools **78.1.1** supports newer Python; runtime setuptools stays 65.5.0.
The old backend accessed `pkgutil.ImpImporter`, removed in Python 3.12. This is
a packaging compatibility correction, with scientific dependencies unchanged.
Never upgrade an accepted runtime to build the package.

From the repository root, build **committed HEAD** without local inboxes/caches
or uncommitted changes. Commit intended implementation first:

```sh
bash <<'BASH'
set -euo pipefail
unset PYTHONPATH PYTHONHOME PYTHONUSERBASE
export PYTHONNOUSERSITE=1
builder_env="$PWD/.venv/builder-0.1.0.dev3-v1"
build_out="$PWD/dist"
test ! -e "$builder_env"
test ! -e "$build_out"
python3.12 -I -B -m venv --copies "$builder_env"
"$builder_env/bin/python" -I -B -m pip --isolated install --only-binary=:all: -r requirements/build.txt
snapshot=$(mktemp -d)
git archive HEAD | tar -x -C "$snapshot"
mkdir "$build_out"
cd "$snapshot"
"$builder_env/bin/python" -I -B -c 'from setuptools.build_meta import build_sdist; import sys; build_sdist(sys.argv[1])' "$build_out"
"$builder_env/bin/python" -I -B -c 'from setuptools.build_meta import build_wheel; import sys; build_wheel(sys.argv[1])' "$build_out"
"$builder_env/bin/python" -I -B scripts/check_distribution.py \
  --wheel "$build_out/dl_binner-0.1.0.dev3-py3-none-any.whl" \
  --sdist "$build_out/dl_binner-0.1.0.dev3.tar.gz" --output "$build_out/inspection.json"
BASH
```

Inspection validates wheel RECORD, metadata/CLI/dependencies, accepted unchanged
package bytes except the version initializer, defaults, matching sdist code
and no research payload. E007 also rebuilds from the sdist, compares logical
member bytes and tests the rebuilt wheel installation. Archive timestamps can
change hashes; logical equivalence is checked separately. Accepted dev1 is retained.

## Run product regressions

Use an installed binner interpreter and a fresh evidence path outside the checkout:

```sh
python3 -I -B scripts/test_product.py \
  --python /absolute/binner/bin/python \
  --threads 4 --timeout 1800 --output /absolute/new-product-check
```

The stdlib parent copies `tests/product/` outside the checkout and runs the installed
wheel with `-I -B`. Tests assert owned package/numerical origins, without Git/research
caches. At most four numerical threads, interop one, loader zero, sampled 8 GB
working RSS and a bounded clock. Prepared Linux CI uses **two** threads, with
matching native flags/pools/rule budgets; it does not assume four CPUs on a private
standard runner. No required case is silently skipped or scientifically scored.

Synthetic ≤32-contig / 0.6-Mb fixtures exercise reader/transform/train/reload/embed/
cluster/export/accounting, all strata/masks/zeros, matched raw control, partial/full
resume, changed/corrupt/extra outputs, fatal input, actual serial stage placement and
timeout/RSS/orphan handling. Preserve `product-tests.log`, `.exit.json`,
`.samples.jsonl` and `native-run/` for failure review. Detailed logs, native causes,
heartbeats and exits persist. Snakemake remains in research workflows; `requirements/workflow.txt` is their
retained version pin file, not a product dependency. Older `tests/test_*.py` and experiment reviews remain
separate opt-in retained-evidence checks with their original dependencies.

See [PROTOTYPE](PROTOTYPE.md#run-the-binner) for use/contracts and
[E007](../experiments/E007-pr-readiness/README.md) and
[E008](../experiments/E008-product-execution/README.md) for measured validation and
CI/publication limits. Use old runtimes for valid resume of old journals; never
rewrite accepted manifests to match a new package.

## Future distribution

Optional GPU support with CPU retained, and Conda/mamba installation, are planned
product/distribution goals. No GPU path, Conda recipe, package-index publication
or release automation is implemented by this task. Current version pins/clean
builds support that future work; they do not claim distribution availability.
