#!/usr/bin/env bash
# Supplemental driver for the already transferred 9c2b0ec6feb3 execution snapshot.
set -euo pipefail
root=${1:?Usage: bash e001_ucloud_preflight.sh ABSOLUTE_WORK_ROOT}
case "$root" in /*) ;; *) exit 2 ;; esac
[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || { echo 'Linux x86_64 required' >&2; exit 2; }
code="$root/e001-code-9c2b0ec6feb3"
[[ $(cat "$code/SOURCE_COMMIT") == 9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea ]]
for path in bootstrap preflight-return.tar.gz preflight-return.tar.gz.sha256 envs/mapping envs/amber locks/mapping locks/amber smoke/mapping smoke/amber fixture sources/AMBER_evaluation bin/micromamba bin/micromamba.part; do
    [[ ! -e "$root/$path" && ! -L "$root/$path" ]] || { echo "STOP: existing $root/$path; preserve and return for inspection" >&2; exit 2; }
done
mkdir -p "$root/bootstrap" "$root/bin"
logs="$root/bootstrap"
finish() {
    status=$?
    trap - EXIT
    set +e
    printf '%s\n' "$status" > "$logs/exit-code.txt"
    date -u +%FT%TZ > "$logs/finished-utc.txt"
    printf '%s\n' "$SECONDS" > "$logs/elapsed-seconds.txt"
    members=(bootstrap)
    [[ ! -d "$root/locks" ]] || members+=(locks)
    [[ ! -d "$root/smoke" ]] || members+=(smoke)
    if tar -czf "$root/preflight-return.tar.gz" -C "$root" "${members[@]}"; then
        (cd "$root" && sha256sum preflight-return.tar.gz > preflight-return.tar.gz.sha256)
        printf 'Return archive: %s/preflight-return.tar.gz\n' "$root"
    else
        echo 'Return packaging failed; preserve bootstrap/, locks/ and smoke/.' >&2
        [[ $status != 0 ]] || status=1
    fi
    printf 'PREFLIGHT EXIT CODE: %s\n' "$status"
    exit "$status"
}
trap finish EXIT
date -u +%FT%TZ > "$logs/started-utc.txt"
cp -- "${BASH_SOURCE[0]}" "$logs/executed-driver.sh"
sha256sum "$logs/executed-driver.sh" "$code/scripts/e001_linux_setup.sh" "$code/scripts/e001_linux_smoke.sh" > "$logs/scripts.sha256"
cp "$code/SOURCE_COMMIT" "$logs/source-commit.txt"
export PATH="$root/bin:$PATH"
export MAMBA_ROOT_PREFIX="$root/micromamba" PIP_CACHE_DIR="$root/cache/pip"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
run() {
    local label=$1 status
    shift
    printf 'START: %s (output saved in bootstrap/%s.log)\n' "$label" "$label"
    printf '%q ' "$@" > "$logs/$label.command.txt"
    if "$@" > "$logs/$label.log" 2>&1; then status=0; else status=$?; fi
    printf '%s\n' "$status" > "$logs/$label.exit-code.txt"
    tail -n 15 "$logs/$label.log"
    [[ $status == 0 ]] || { echo "STOP: $label failed; do not rerun or delete outputs" >&2; exit "$status"; }
    printf 'PASS: %s\n' "$label"
}

# Official release API asset digest, inspected 2026-09-18; verify before execution.
url=https://github.com/mamba-org/micromamba-releases/releases/download/2.9.0-0/micromamba-linux-64
hash=366cd9cd8be14df1ab8ed50352a82111082a36686b2d389fdb79a92c3fafb3e3
printf '%s\n' "$url" > "$logs/micromamba-url.txt"
run download-micromamba curl --fail --location --proto '=https' --proto-redir '=https' --connect-timeout 30 --max-time 600 --output "$root/bin/micromamba.part" "$url"
printf '%s  %s\n' "$hash" "$root/bin/micromamba.part" > "$logs/micromamba.sha256"
run verify-micromamba sha256sum --check "$logs/micromamba.sha256"
mv "$root/bin/micromamba.part" "$root/bin/micromamba"
chmod 755 "$root/bin/micromamba"
run micromamba-version micromamba --version
[[ $(micromamba --version) == 2.9.0 ]]

if [[ ! -x /usr/bin/time ]]; then
    run apt-update timeout 15m sudo -n apt-get update
    run install-time timeout 15m sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends time
fi
run time-version /usr/bin/time --version
dpkg-query -W time > "$logs/time-package.txt"
sha256sum /usr/bin/time > "$logs/time-binary.sha256"

for tool in mapping amber; do
    run "$tool-setup" timeout --signal=TERM --kill-after=60s 45m bash "$code/scripts/e001_linux_setup.sh" "$tool" "$root"
    run "$tool-smoke" bash "$code/scripts/e001_linux_smoke.sh" "$tool" "$root"
done
echo 'Mapping and AMBER synthetic checks finished. Stop for review; no GI acquisition is authorized.'
