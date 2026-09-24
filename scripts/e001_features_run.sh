#!/usr/bin/env bash
# Capture the entire owner invocation; scientific inputs are selected by the pinned manifest.
set -euo pipefail
root=${1:?Usage: e001_features_run.sh WORK_ROOT DATA_ROOT ACTUAL_VCPUS ACTUAL_RAM_GB}
data=${2:?DATA_ROOT required}
cpus=${3:?ACTUAL_VCPUS required}
ram=${4:?ACTUAL_RAM_GB required}
code=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
[[ -d "$root/transfer" && -d "$data" ]] || { echo 'STOP: existing work/transfer and mounted data directory required'; exit 2; }
log=$(mktemp "$root/transfer/e001-features.XXXXXX.log")
echo "Terminal log: $log"
(
    date -u +%FT%TZ
    printf 'Actual allocation: %s vCPU / %s GB RAM\n' "$cpus" "$ram"
    [[ $(uname -s) == Linux ]] || { echo 'STOP: owner execution is Linux-only'; exit 2; }
    cat "$code/SOURCE_COMMIT"
    unset PYTHONPATH PYTHONHOME PYTHONUSERBASE
    export PYTHONNOUSERSITE=1
    reuse=${5:-}
    set -- python3 -I "$code/scripts/e001_features.py" "$root" --data-root "$data" \
        --manifest "$code/experiments/E001-coverage-thinning/multisample-bam-manifest.json" \
        --vcpus "$cpus" --ram-gb "$ram" \
        --workflow-snapshot "$root/transfer/e001-workflow-0fb6955cdc62.tar.gz"
    if [[ -n "$reuse" ]]; then set -- "$@" --reuse-attempt "$reuse"; fi
    "$@"
) 2>&1 | tee "$log"
