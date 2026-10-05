# E005 owner operations

This task runs **only the CPU/Linux software smoke**. The capped GI/depth pilot
is frozen in [pilot.json](pilot.json) and stops at a returned-evidence review.
The driver has no scientific-pilot launch mode. [README](README.md) owns scope,
controls and limitations; [smoke.json](smoke.json) owns resource/time ceilings.

## Files and job

Upload `e005-linux-smoke-v1.tar.gz` and `e005-linux-smoke-v1.tar.gz.sha256` to
`/work/Home/`. Keep both filenames. The bundle contains all required Python/CPU/
workflow wheels, frozen source, tiny DNA/TNF/depth inputs and the pilot protocol.
No large source DNA/reads/BAM upload is required. Binary download/metadata checks
were local; native Linux execution remains unverified until this return is reviewed.

Start a **single-node Terminal job: 4 vCPUs, 12 GB RAM, no GPU**. Use the local
executor; no Slurm cluster is needed. Mount the existing Home directory. Nothing
needs activation, sudo or an E001 environment upgrade. The bootstrap requires
the Terminal's normal Bash, system Python ≥3.10, tar, sha256sum, tee and mktemp;
missing prerequisites fail before setup and are captured in the external log.
At least **4 GB free persistent space** is required (prefer 6 GB).

Run this exact command after both uploads:

```bash
bash <<'BASH'
set -euo pipefail
cd /work/Home
log=$(mktemp /work/Home/e005-linux-smoke.XXXXXX.log)
trap 'rc=$?; printf "\nTERMINAL_LOG=%s\nEXIT_CODE=%s\n" "$log" "$rc"; exit "$rc"' EXIT
(
  for tool in python3 tar sha256sum tee; do command -v "$tool" >/dev/null || { echo "Missing prerequisite: $tool"; exit 2; }; done
  sha256sum -c e005-linux-smoke-v1.tar.gz.sha256
  launch=$(mktemp -d /work/Home/e005-launch.XXXXXX)
  tar -xzf /work/Home/e005-linux-smoke-v1.tar.gz -C "$launch"
  env -u PYTHONPATH -u PYTHONHOME -u PYTHONUSERBASE \
    PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
    python3 -I -u "$launch/e005-linux-smoke/scripts/e005_owner.py" \
    --root /work/Home/dl_binner/e005 \
    --allocated-vcpus 4 --allocated-ram-gb 12
) 2>&1 | tee "$log"
BASH
```

Allocation inputs must describe the rented node, not host `nproc`. The driver
supports smaller 1–4-vCPU declarations with matched thread/pool/affinity limits,
but this prepared command is for **4/12**. No competing workload is budgeted.
Large 8/16-vCPU nodes bring no justified benefit to a fourteen-row smoke and the
CLI's current tested CPU contract is 1–4. The four-thread training uses loader
zero; serial work/startup may use less than four CPUs. Native reports/benchmarks/
independent samples will show effective use, rather than assuming saturation.

## What happens and stops

The driver verifies all bundle bytes, creates unique attempts under the new E005
root, and installs separate offline binner/workflow environments only if a matching
healthy completed prefix is absent. New/partial prefixes are preserved. A completed
prefix is reprobed, not reinstalled. Accepted E001/E002/E003/E004 runtimes and caches
are untouched. Job-local TMPDIR is short, outputs/environments persistent.

It captures pre-site/import origins, exact inventories/CPU pools, all CLI stages,
save/reload parity, fresh-tiny/cached reader agreement, both exports, masks,
exclusion/noise accounting, native fatal-input/corrupt-checkpoint/overwrite checks
and a completed-workdir dry-run. All computational rules run serially with
four-thread limits. Setup has a 30-minute ceiling, DAG ten minutes and whole driver
one hour at ≤8-GB sampled subtree RSS. **Expect roughly 1–10 minutes on an intact
normal filesystem; this is a planning estimate, not measured Linux time.** The
one-hour ceiling allows bounded first setup but does not justify ignoring a hung
child. Child diagnostics, 20-second heartbeats and per-stage ceilings expose hangs.

Fatal worker/setup failures stop dependent work and kill observed launched children;
failure evidence is collected, and the outer command remains nonzero. Global
input/prerequisite failures are not interpreted as a negative binning result.
Repeated invocation makes a new attempt and can reuse healthy environment prefixes;
it never removes the old attempt. It does not automatically retry failed science.

Successful return includes `status.json`, `runtime.json`, resolved configuration,
stage commands/logs/CPU/RSS receipts, per-rule extended benchmarks, caches/masks,
checkpoint/reference/reloaded embeddings, both complete partitions and exports,
verification and failure checks. A read-only existence/size inventory reports
future pilot source/evaluator locators without hashing/scoring/mapping those inputs.
Environment/setup disk remains persistent; payload caches are excluded from the
small return archive. Retained file hashes and return archive SHA permit independent
review. Sampled CPU/RSS differs from an exact peak or the owner's bill; complete
driver wall includes setup and collection, while upload/owner idle lie outside it.

## Return for review

The last lines print absolute **return archive**, **checksum** and **TERMINAL_LOG**
paths. Download and upload those three files here, including when the driver fails.
Preserve failed attempts and prefixes. If SIGKILL/container termination prevents
collection, return the external terminal log and ask for evidence-only recovery;
do not delete/move old directories or run the pilot.

After checksum/native-output/resource inspection, prepare the **already frozen**
pilot's tested sampling/mapping/mean-depth/AMBER adapters and owner command. Reuse
healthy E005/E001 read-only runtimes with current probes. No full benchmark,
architecture campaign or planned TNF/GLM/hybrid comparison follows automatically.
