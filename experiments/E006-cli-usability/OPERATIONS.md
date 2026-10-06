# E006 owner operations: generic-command Linux smoke

Status: **executed and native Linux return accepted, 2026-10-06**. Do not run the
command again. [Independent review](README.md#accepted-native-linux-return-and-independent-review-2026-10-06)
and [Linux receipt](linux-observed.json) accept `generic-linux-smoke-y9xix7p9`:
462 archive members / 447 inventory entries, all 21 native checks and resource
ceilings pass. Cost through collection: 214.793 s / 0.238659 allocated vCPU-hours
at 4 vCPUs / 12 GB; sampled peak 0.422 GB. Archive SHA256
`949bb485bfcaeeaa6ea70678f49cf045640d019e395d61ee708e17b5b35106ad`.
Its exact uncompressed storage is 2,172,376 bytes; original collector accounting
is preserved with a correction in the review. The new linked prefix depends on
the retained E005 base; do not move/delete those libraries. No additional files
or UCloud job are needed now. Next is
[bounded private-PR readiness](../../docs/PROTOTYPE.md#prepared-private-pr-readiness-milestone).

The instructions below are the executed recipe, retained for provenance, not a
current handoff. [Preparation receipt](linux-prepared.json) owns the
passed local owner-driver checks and original limits. This was a tiny compatibility job, not a biological
benchmark or an architecture gate. The accepted E005 scientific runs remain
accepted and are not rerun. [E006](README.md) owns preparation evidence;
[contract](linux-smoke.json) owns the prospectively frozen ceiling.

## Uploads and allocation

Create `/work/Home/dl_binner/e006/transfer/` in UCloud Files. Upload exactly
`e006-linux-smoke-v1.tar.gz` and `e006-linux-smoke-v1.tar.gz.sha256` there,
keeping filenames. The packet is **72,267 bytes**, SHA256
`d15864bd606676991b95c3fe2bb2d4198394106e22aead022fee9b64edc08569`,
source **a8010cb4b4ded237a1f2d4c0b1cfc82a385cb809**. It contains the unchanged
36,310-byte accepted wheel, small scripts/contracts and retained E006 fixture.
There are no runtime copies, heavy reads/BAMs, large references or GLM payloads.

Start a **single-node CPU Terminal job: 4 vCPUs / 12 GB RAM, no GPU**. Mount Home
as before; shared heavy storage and a Slurm cluster are unnecessary for this job.
Run no competing workloads. Keep the healthy E005 binner/workflow prefixes intact:

- `/work/Home/dl_binner/e005/envs/binner-cpu-v1-iz5atsis/runtime/`
- `/work/Home/dl_binner/e005/envs/workflow-cpu-v1-msqvth6v/runtime/`

Bash, tar, sha256sum, tee, env, timeout, mktemp, date and ps are entry prerequisites;
no activation, sudo, container package installation or download is performed.
At least **0.5 GB free** is required for the small owned package/attempt/return;
existing dependency storage is separate. Missing/changed prerequisites stop with
captured logs; preserve the failure and return it instead of rebuilding blindly.

## Purpose, limits and outputs

The driver reprobes full accepted distribution inventories/import paths and CPU
pools. It creates a **new version-qualified E006 venv**, installs only the local
no-dependency binner wheel, and explicitly links reviewed Linux numerical
libraries read-only. Its Python/stdlib remain in the accepted base; do not remove
that base. No old dl_binner, system-site overlay or .pth import path injection is
used. Dependencies/workflow are hashed before/after. The Mac linked environment
is never transferred, copied or treated as a Linux runtime.

The retained panel is **13 contigs / 42,311 bp**: twelve real human-associated GI
DNA windows across all six length strata, plus a named N-only mask sentinel and
explicitly synthetic two-sample mean depths. Same-panel subsets exercise valid
empty partitions and intended failures. Fresh extraction, unchanged 20-epoch
seed-11 training, exact checkpoint reload, fixed label-blind clustering, raw and
learned complete exports/neutral summaries, partial/full resume, tamper refusal,
native input failures, actual RSS/timeout/orphan cleanup, heartbeat logging and
independent CPU/global-RAM scheduling checks run serially. No quality scores,
truth labels, E005 stages or large assets are consumed.

Exactly four numerical threads, interop one, loader zero and **8 GB sampled
aggregate working RSS**. Execution is capped at **1,800 seconds including entry
verification/setup**, setup subset 900 seconds, native-contract subset 900 seconds.
Evidence collection has a separate 120-second cap. An outer 1,930-second watchdog
plus five-second kill grace covers checksum/extraction and protects stalled Python startup/driver cleanup; it
does not extend the permitted execution clock. Internal sampled process metrics
are estimates. Allocation accounting uses four allocated CPUs times full entry
wall through collection, including hashing/setup; owner idle/upload is excluded.

Final complete local envelope took **186.669 seconds / 0.360-GB sampled peak**; plan **3–10 minutes as a rough estimate**,
not a Linux timing claim. Execution ceiling corresponds to **2 allocated
vCPU-hours**, plus at most 0.1333 for bounded collection; emergency watchdog grace
and owner idle remain separate. Tiny/startup work will not saturate all four CPUs.

Every command invocation creates a uniquely named retained attempt under
`/work/Home/dl_binner/e006/`, and a fresh package prefix under `envs/`. Earlier
attempts are never removed or modified. Internal `--resume` checks use the same
run workdir and verify that completed scientific stages are not scheduled again.
Launches, external terminal logs, collection receipts and returned archive/checksum
stay under `transfer/`. Both success and verified-driver failure return the
submitted manifest, status, provenance, native logs/exit/resource receipts and
available outputs. Fail-fast unexpected errors stop subsequent tests. There is
no automatic retry after an unexpected failure.

## Executed owner command — do not repeat

After uploading both files, paste this in Terminal. It is the default mode of
[the locally tested shell envelope](owner-command.sh); its explicit local harness
mode bypasses only Linux platform/baseline paths and grants no Linux credit.

```bash
bash <<'BASH'
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
BASH
```

On success the final shell `EXIT_CODE` is zero. Expected negative tests appear as
`Contract passed: ...`; individual intentional exit-1 receipts do not mean the
whole smoke failed. Any unexpected case failure stops the job and final exit is
nonzero. Do not run another attempt automatically.

Return the three printed files: **RETURN_ARCHIVE**, **RETURN_CHECKSUM**, and
**TERMINAL_LOG**, even if the final status failed. The external terminal contains
collection-inclusive cost/status after the archive snapshot. No runtime or
large-file download is needed. Stop for independent returned-evidence review.

If the shell stops before the verified driver starts, an archive may not exist;
return its captured TERMINAL_LOG. A verified-driver failure retains the manifest
and available evidence in the printed return archive.
