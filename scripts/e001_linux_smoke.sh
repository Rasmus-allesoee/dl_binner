#!/usr/bin/env bash
# One synthetic native smoke job in an already prepared environment.
set -euo pipefail
tool=${1:?Usage: bash scripts/e001_linux_smoke.sh TOOL WORK_ROOT}
root=${2:?Provide an absolute external work directory}
[[ $(uname -s) == Linux ]] || { printf '%s\n' 'Linux required' >&2; exit 2; }
case "$root" in /*) ;; *) exit 2 ;; esac
case "$tool" in mapping|amber|vamb|comebin|metabat) ;; *) exit 2 ;; esac
code=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
[[ ! -e "$root/smoke/$tool" && ! -e "$root/smoke/$tool.stdout" ]] || { printf '%s\n' 'Smoke output exists; preserve it and inspect before retrying' >&2; exit 2; }
mkdir -p "$root/smoke"
export MAMBA_ROOT_PREFIX="$root/micromamba" PIP_CACHE_DIR="$root/cache/pip"
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=11
unset PYTHONPATH PYTHONHOME PYTHONUSERBASE
export PYTHONNOUSERSITE=1 PIP_DISABLE_PIP_VERSION_CHECK=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export E001_METABAT_PREFIX="$root/envs/metabat"
if [[ "$tool" == mapping ]]; then
    micromamba run -p "$root/envs/mapping" python "$code/scripts/e001.py" fixture --out "$root/fixture"
    args=(mapping --fixture "$root/fixture")
elif [[ "$tool" == amber ]]; then
    args=(amber --source "$root/sources/AMBER_evaluation")
elif [[ "$tool" == metabat ]]; then
    sha256sum --check "$root/locks/metabat/binaries.sha256"
    args=(metabat --source "$root/sources/metabat" --fixture "$root/fixture")
else
    source_dir="$root/sources/$tool"
    [[ "$tool" != comebin ]] || source_dir="$root/sources/COMEBin"
    args=("$tool" --source "$source_dir" --fixture "$root/fixture" --mapping "$root/smoke/mapping")
fi
set +e
/usr/bin/time -v -o "$root/smoke/$tool.resources.txt" timeout --signal=TERM --kill-after=60s 30m \
    micromamba run -p "$root/envs/$tool" python "$code/scripts/e001.py" native-smoke "${args[@]}" --out "$root/smoke/$tool" \
    > "$root/smoke/$tool.stdout" 2> "$root/smoke/$tool.stderr"
status=$?
set -e
printf '%s\n' "$status" > "$root/smoke/$tool.exit-code.txt"
exit "$status"
