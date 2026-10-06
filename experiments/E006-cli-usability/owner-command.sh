#!/usr/bin/env bash
# Verify the exact tiny packet, retain a unique launch/log and run one smoke.
# --local-harness ROOT RUNTIMES is solely the Mac envelope test; it grants no Linux credit.
set -euo pipefail
root=/work/Home/dl_binner/e006
python=/work/Home/dl_binner/e005/envs/binner-cpu-v1-iz5atsis/runtime/bin/python3
local_runtimes=
if [[ $# -gt 0 ]]; then
  [[ $# == 3 && $1 == --local-harness && $2 == /* && $3 == /* ]] || { echo 'Invalid local harness arguments'; exit 2; }
  root=$2
  python=$(python3 -I -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["binner"]["python"])' "$3")
  local_runtimes=$3
fi
transfer="$root/transfer"
mkdir -p "$transfer/launches"
cd "$transfer"
log=$(mktemp "$transfer/e006-linux-smoke.log.XXXXXX")
trap 'rc=$?; printf "\nTERMINAL_LOG=%s\nEXIT_CODE=%s\n" "$log" "$rc" | tee -a "$log"; exit "$rc"' EXIT
(
  entry=$(date +%s)
  # Emergency watchdog covers checksum verification/extraction and Python startup.
  # The driver enforces 1800s execution plus separately bounded 120s collection.
  timeout --signal=TERM --kill-after=5s 1930s \
    bash -s -- "$root" "$python" "$entry" "$local_runtimes" <<'RUN'
set -euo pipefail
root=$1
python=$2
entry=$3
transfer="$root/transfer"
if [[ -n $4 ]]; then set -- --local-runtimes "$4"; else set --; fi
cd "$transfer"
for tool in tar sha256sum tee env timeout ps; do
  command -v "$tool" >/dev/null || { echo "Missing prerequisite: $tool"; exit 2; }
done
[[ -x "$python" ]] || { echo "Missing accepted interpreter: $python; do not rebuild it automatically"; exit 2; }
archive=e006-linux-smoke-v1.tar.gz
expected=d15864bd606676991b95c3fe2bb2d4198394106e22aead022fee9b64edc08569
[[ $(< "$archive.sha256") == "$expected  $archive" ]] || { echo 'Uploaded checksum differs from frozen packet'; exit 2; }
printf '%s  %s\n' "$expected" "$archive" | sha256sum -c -
launch=$(mktemp -d "$transfer/launches/generic-smoke.XXXXXX")
tar -xzf "$transfer/$archive" -C "$launch"
exec env -u PYTHONPATH -u PYTHONHOME -u PYTHONUSERBASE PYTHONNOUSERSITE=1 \
  "$python" -I -B -S -u "$launch/e006-linux-smoke/scripts/e006_owner.py" \
  --root "$root" --allocated-vcpus 4 --allocated-ram-gb 12 \
  --entry-start-epoch "$entry" "$@"
RUN
) 2>&1 | tee "$log"
