#!/usr/bin/env bash
# Conversion only: reuse verified downloads, preserve previous code and attempts.
set -euo pipefail
root=${1:?Provide the absolute experiment work root}
case "$root" in /*) ;; *) exit 2 ;; esac
code=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
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
