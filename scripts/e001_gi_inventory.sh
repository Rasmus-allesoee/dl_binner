#!/usr/bin/env bash
# Owner-run Gate 1: only manifest-listed assembly/truth/setup, never read archives.
set -euo pipefail
root=${1:?Usage: bash e001_gi_inventory.sh ABSOLUTE_WORK_ROOT}
case "$root" in /*) ;; *) exit 2 ;; esac
[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || { echo 'Linux x86_64 required' >&2; exit 2; }
code="$root/e001-code-9c2b0ec6feb3"
[[ $(cat "$code/SOURCE_COMMIT") == 9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea ]]
if [[ ${2:-} == --retry-missing-time ]]; then
    # Only recover the inspected pre-download failure; never move partial data.
    for name in inventory input-preflight failed-inventory-missing-time; do
        [[ ! -e "$root/$name" && ! -L "$root/$name" ]] || { echo "STOP: unexpected $root/$name" >&2; exit 2; }
    done
    [[ $(cat "$root/inventory-stage/exit-code.txt") == 127 ]]
    [[ $(cat "$root/inventory-stage/prerequisites.exit-code.txt") == 127 ]]
    [[ $(cat "$root/inventory-stage/prerequisites.stderr") == *'/usr/bin/time: No such file or directory'* ]]
    [[ -f "$root/gi-inventory-return.tar.gz" && -f "$root/gi-inventory-return.tar.gz.sha256" ]]
    (cd "$root" && sha256sum --check gi-inventory-return.tar.gz.sha256)
    mkdir "$root/failed-inventory-missing-time"
    mv "$root/inventory-stage" "$root/gi-inventory-return.tar.gz" "$root/gi-inventory-return.tar.gz.sha256" "$root/failed-inventory-missing-time/"
    echo 'Preserved the failed attempt in failed-inventory-missing-time/'
elif [[ -n ${2:-} ]]; then
    echo 'Unknown option' >&2
    exit 2
fi
for name in inventory-stage inventory input-preflight gi-inventory-return.tar.gz gi-inventory-return.tar.gz.sha256; do
    [[ ! -e "$root/$name" && ! -L "$root/$name" ]] || { echo "STOP: existing $root/$name; preserve for inspection" >&2; exit 2; }
done
unset PYTHONPATH PYTHONHOME PYTHONUSERBASE
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=11
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export MAMBA_ROOT_PREFIX="$root/micromamba" PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_INDEX=1
export PATH="$root/bin:$PATH"
logs="$root/inventory-stage"
mkdir "$logs"
finish() {
    status=$?
    trap - EXIT
    set +e
    printf '%s\n' "$status" > "$logs/exit-code.txt"
    date -u +%FT%TZ > "$logs/finished-utc.txt"
    printf '%s\n' "$SECONDS" > "$logs/elapsed-seconds.txt"
    members=(inventory-stage)
    for name in inventory/acquisition-report.json inventory/setup-members.json inventory/README.md inventory/md5sums.tsv input-preflight/inventory.json; do
        [[ ! -f "$root/$name" ]] || members+=("$name")
    done
    if tar -czf "$root/gi-inventory-return.tar.gz" -C "$root" "${members[@]}"; then
        (cd "$root" && sha256sum gi-inventory-return.tar.gz > gi-inventory-return.tar.gz.sha256)
        printf 'Return: %s/gi-inventory-return.tar.gz and its .sha256\n' "$root"
    else
        echo 'Packaging failed; preserve logs and return terminal output.' >&2
        [[ $status != 0 ]] || status=1
    fi
    printf 'INVENTORY COMMAND EXIT CODE: %s\n' "$status"
    exit "$status"
}
trap finish EXIT
date -u +%FT%TZ > "$logs/started-utc.txt"
cp -- "${BASH_SOURCE[0]}" "$logs/executed-driver.sh"
cp "$code/SOURCE_COMMIT" "$logs/source-commit.txt"
cp "$code/experiments/E001-coverage-thinning/acquisition.json" "$logs/acquisition.json"
sha256sum "$logs/executed-driver.sh" "$code/scripts/e001.py" "$code/scripts/e001lib/acquire.py" "$code/scripts/e001lib/records.py" > "$logs/code.sha256"
df -h "$root" > "$logs/disk-before.txt"
if [[ ! -x /usr/bin/time ]]; then
    echo 'Installing missing GNU time in this disposable job container; logs in inventory-stage/time-install.log'
    # Bootstrap cannot itself depend on the utility it is installing.
    if sudo -n apt-get update > "$logs/time-install.log" 2>&1 && \
       sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends time >> "$logs/time-install.log" 2>&1; then
        printf '0\n' > "$logs/time-install.exit-code.txt"
    else
        status=$?
        printf '%s\n' "$status" > "$logs/time-install.exit-code.txt"
        tail -n 30 "$logs/time-install.log"
        exit "$status"
    fi
fi
/usr/bin/time --version > "$logs/time-version.txt"
dpkg-query -W time > "$logs/time-package.txt"
sha256sum /usr/bin/time > "$logs/time-binary.sha256"
run() {
    local label=$1 status
    shift
    printf 'START: %s; details in inventory-stage/%s.stdout and .stderr\n' "$label" "$label"
    printf '%q ' "$@" > "$logs/$label.command.txt"
    if /usr/bin/time -v -o "$logs/$label.resources.txt" "$@" > "$logs/$label.stdout" 2> "$logs/$label.stderr"; then status=0; else status=$?; fi
    printf '%s\n' "$status" > "$logs/$label.exit-code.txt"
    tail -n 20 "$logs/$label.stdout"
    tail -n 20 "$logs/$label.stderr"
    [[ $status == 0 ]] || { echo "STOP: $label failed; return logs, do not retry" >&2; exit "$status"; }
    printf 'PASS: %s\n' "$label"
}
python=(micromamba run -p "$root/envs/mapping" python)
run prerequisites "${python[@]}" -c 'import json,site,sys; from pathlib import Path; import numpy,Bio,pysam; root=Path(sys.argv[1]); prefix=root/"envs/mapping"; assert Path(sys.prefix)==prefix; assert not site.ENABLE_USER_SITE; assert all(Path(m.__file__).resolve().is_relative_to(prefix) for m in (numpy,Bio,pysam)); assert json.loads((root/"environment-review/status.json").read_text())["status"]=="pass"; print("Reviewed clean environment confirmed")' "$root"
run acquisition-plan "${python[@]}" "$code/scripts/e001.py" acquire --root "$root/inventory"
run acquisition "${python[@]}" "$code/scripts/e001.py" acquire --root "$root/inventory" --execute
run coordinate-inventory "${python[@]}" "$code/scripts/e001.py" prepare-hmp \
    --fasta "$root/inventory/per_bodysite/gastro_bam/gsa.fa" \
    --mapping "$root/inventory/per_bodysite/gastro_bam/gsa_pooled_mapping_fixed.tsv" \
    --out "$root/input-preflight"
df -h "$root" > "$logs/disk-after.txt"
echo 'STOP FOR REVIEW: taxonomy is intentionally unresolved; inventory status blocked is expected, not scientific approval.'
