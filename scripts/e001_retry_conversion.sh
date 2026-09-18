#!/usr/bin/env bash
# Conversion only: reuse verified downloads, preserve previous code and attempts.
set -euo pipefail
root=${1:?Provide the absolute experiment work root}
case "$root" in /*) ;; *) exit 2 ;; esac
code=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
if [[ ${2:-} == --retry-known-failure ]]; then
    for name in failed-conversion-malformed-fasta; do
        [[ ! -e "$root/$name" && ! -L "$root/$name" ]] || { echo "STOP: existing $name" >&2; exit 2; }
    done
    [[ -f "$root/conversion-alias-stage/exit-code.txt" ]] && [[ $(cat "$root/conversion-alias-stage/exit-code.txt") == 1 ]]
    [[ -f "$root/conversion-alias-stage/stderr.txt" ]] && grep -Fq 'Invalid DNA' "$root/conversion-alias-stage/stderr.txt"
    [[ -f "$root/conversion-alias-return.tar.gz" && -f "$root/conversion-alias-return.tar.gz.sha256" ]]
    (cd "$root" && sha256sum --check conversion-alias-return.tar.gz.sha256)
    if [[ -e "$root/input-preflight-v2" || -L "$root/input-preflight-v2" ]]; then
        [[ -d "$root/input-preflight-v2" && ! -L "$root/input-preflight-v2" ]] || { echo 'STOP: input-preflight-v2 is not a directory' >&2; exit 2; }
        [[ ! -e "$root/input-preflight-v2/inventory.json" ]] || { echo 'STOP: input-preflight-v2 contains a completed inventory' >&2; exit 2; }
        partial=("$root/input-preflight-v2")
    else
        partial=()
    fi
    mkdir "$root/failed-conversion-malformed-fasta"
    mv "$root/conversion-alias-stage" "$root/conversion-alias-return.tar.gz" "$root/conversion-alias-return.tar.gz.sha256" "${partial[@]}" "$root/failed-conversion-malformed-fasta/"
    echo 'Preserved the failed malformed-FASTA attempt in failed-conversion-malformed-fasta/'
elif [[ -n ${2:-} ]]; then
    echo 'Unknown option' >&2
    exit 2
fi
for name in conversion-alias-stage input-preflight-v2 conversion-alias-return.tar.gz conversion-alias-return.tar.gz.sha256; do
    [[ ! -e "$root/$name" && ! -L "$root/$name" ]] || { echo "STOP: existing $name" >&2; exit 2; }
done
unset PYTHONPATH PYTHONHOME PYTHONUSERBASE
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export MAMBA_ROOT_PREFIX="$root/micromamba"
logs="$root/conversion-alias-stage"
mkdir "$logs"
finish() {
    status=$?
    trap - EXIT
    set +e
    printf '%s\n' "$status" > "$logs/exit-code.txt"
    printf '%s\n' "$SECONDS" > "$logs/elapsed-seconds.txt"
    members=(conversion-alias-stage)
    [[ ! -f "$root/input-preflight-v2/inventory.json" ]] || members+=(input-preflight-v2/inventory.json)
    tar -czf "$root/conversion-alias-return.tar.gz" -C "$root" "${members[@]}"
    (cd "$root" && sha256sum conversion-alias-return.tar.gz > conversion-alias-return.tar.gz.sha256)
    echo "CONVERSION EXIT CODE: $status; return conversion-alias-return.tar.gz and .sha256"
    exit "$status"
}
trap finish EXIT
cp "$code/SOURCE_COMMIT" "$logs/source-commit.txt"
sha256sum "$code/scripts/e001lib/records.py" "${BASH_SOURCE[0]}" > "$logs/code.sha256"
echo 'Converting existing GI files; no downloads or installations.'
"$root/bin/micromamba" run -p "$root/envs/mapping" python "$code/scripts/e001.py" prepare-hmp \
    --fasta "$root/inventory/per_bodysite/gastro_bam/gsa.fa" \
    --mapping "$root/inventory/per_bodysite/gastro_bam/gsa_pooled_mapping_fixed.tsv" \
    --out "$root/input-preflight-v2" > "$logs/stdout.txt" 2> "$logs/stderr.txt"
cat "$logs/stdout.txt"
