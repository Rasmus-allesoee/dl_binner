#!/usr/bin/env bash
# Capture the entire owner invocation; scientific inputs are selected by the pinned manifest.
set -euo pipefail
root=${1:?Usage: e001_pilot_run.sh WORK_ROOT DATA_ROOT ACTUAL_VCPUS ACTUAL_RAM_GB GROUP}
data=${2:?DATA_ROOT required}
cpus=${3:?ACTUAL_VCPUS required}
ram=${4:?ACTUAL_RAM_GB required}
code=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
[[ -d "$root/transfer" && -d "$data" ]] || { echo 'STOP: existing work/transfer and mounted data directory required'; exit 2; }
log=$(mktemp "$root/transfer/e001-pilot.XXXXXX.log")
echo "Terminal log: $log"
(
    date -u +%FT%TZ
    printf 'Actual allocation: %s vCPU / %s GB RAM\n' "$cpus" "$ram"
    [[ $(uname -s) == Linux ]] || { echo 'STOP: owner execution is Linux-only'; exit 2; }
    cat "$code/SOURCE_COMMIT"
    unset PYTHONPATH PYTHONHOME PYTHONUSERBASE
    export PYTHONNOUSERSITE=1
    group=${5:?GROUP required: metabat-vamb or comebin}
    python3 -I "$code/scripts/e001_pilot.py" "$root" --data-root "$data" \
        --group "$group" --vcpus "$cpus" --ram-gb "$ram" \
        --workflow-snapshot "$root/transfer/e001-workflow-0fb6955cdc62.tar.gz"
) 2>&1 | tee "$log"
