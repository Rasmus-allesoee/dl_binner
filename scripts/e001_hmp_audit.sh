#!/usr/bin/env bash
# Read-only coordinate audit: reuse verified GI files and the mapping environment.
set -euo pipefail
root=${1:?Provide the absolute experiment work root}
case "$root" in /*) ;; *) exit 2 ;; esac
code=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
for name in hmp-join-audit-v1 hmp-join-audit-return.tar.gz hmp-join-audit-return.tar.gz.sha256; do
    [[ ! -e "$root/$name" && ! -L "$root/$name" ]] || { echo "STOP: existing $name" >&2; exit 2; }
done
unset PYTHONPATH PYTHONHOME PYTHONUSERBASE
export PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export MAMBA_ROOT_PREFIX="$root/micromamba"
stage="$root/hmp-join-audit-v1"
mkdir "$stage"
finish() {
    status=$?
    trap - EXIT
    set +e
    printf '%s\n' "$status" > "$stage/exit-code.txt"
    printf '%s\n' "$SECONDS" > "$stage/elapsed-seconds.txt"
    tar -czf "$root/hmp-join-audit-return.tar.gz" -C "$root" hmp-join-audit-v1
    (cd "$root" && sha256sum hmp-join-audit-return.tar.gz > hmp-join-audit-return.tar.gz.sha256)
    echo "HMP AUDIT EXIT CODE: $status; return hmp-join-audit-return.tar.gz and .sha256"
    exit "$status"
}
trap finish EXIT
cp "$code/SOURCE_COMMIT" "$stage/source-commit.txt"
sha256sum "$code/scripts/e001lib/records.py" "${BASH_SOURCE[0]}" > "$stage/code.sha256"
echo 'Auditing existing GI FASTA and corrected mapping; no downloads or installations.'
"$root/bin/micromamba" run -p "$root/envs/mapping" python "$code/scripts/e001.py" audit-hmp \
    --fasta "$root/inventory/per_bodysite/gastro_bam/gsa.fa" \
    --mapping "$root/inventory/per_bodysite/gastro_bam/gsa_pooled_mapping_fixed.tsv" \
    --out "$stage/report.json" > "$stage/stdout.txt" 2> "$stage/stderr.txt"
cat "$stage/stdout.txt"
