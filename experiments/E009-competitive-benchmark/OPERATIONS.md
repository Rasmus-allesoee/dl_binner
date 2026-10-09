# E009 owner preflight operations

Status: **v3 startup failed; v4 instrumented recovery prepared, owner execution pending**.
[Protocol](README.md), [limits](preflight.json), [native payload lock](native-lock.json)
and [Linux package lock](utilities-linux-lock.json) define this job. This is asset
and tiny native-contract preparation, not the benchmark command.

Use a CPU/Linux x86-64 Terminal job with **8 vCPUs / 24 GB**, at least five hours
available. Mount Home and the project's shared storage. Keep all owner uploads,
launch copies, terminal logs and returned archives/checksums under
`/work/Home/dl_binner/e009/transfer/`. Shared bulk data is written only below
`/work/RasmusAllesøeNielsen#2936/dl_binner/e009/`; the parent must already be mounted.
Do not run competing workloads. No Slurm cluster is needed for this serial preflight.

## Upload two files and run once

Upload the source-bound `e009-preflight-v4.tar.gz` and matching `.tar.gz.sha256`
from the local transfer receipt; no Mac environment, large BAM or model upload.
Exact archive/source identities are recorded in [transfer.json](transfer.json).
The new pair belongs in local `artifacts/e009-preparation/transfer-v4/`;
[transfer.json](transfer.json) records its final source/checksum. Preserve the failed
v3 attempt, prior uploads and the accepted E001 runtime. Upload **v4 only**.
Then paste this **entire block** into the Terminal:

```bash
bash <<'BASH'
set -Eeuo pipefail
transfer=/work/Home/dl_binner/e009/transfer
mkdir -p "$transfer"
terminal_log=$(python3 -I -B -S - "$transfer" <<'LOGPY'
import os, sys, tempfile
fd,path=tempfile.mkstemp(prefix='e009-preflight.',suffix='.log',dir=sys.argv[1])
os.close(fd)
print(path)
LOGPY
)
exec > >(tee -a "$terminal_log") 2>&1
printf 'TERMINAL_LOG=%s\n' "$terminal_log"
python3 -I -B -S - "$transfer" <<'PY'
import hashlib, os, pathlib, shutil, sys, tarfile, tempfile, time
started=time.time()
transfer=pathlib.Path(sys.argv[1])
archive=transfer/'e009-preflight-v4.tar.gz'
fields=(transfer/(archive.name+'.sha256')).read_text().split()
if len(fields)!=2 or fields[1]!=archive.name or len(fields[0])!=64:
    raise ValueError('Upload the exact archive and matching printed checksum')
with archive.open('rb') as src:
    digest=hashlib.sha256()
    for block in iter(lambda:src.read(1024*1024),b''):digest.update(block)
if digest.hexdigest()!=fields[0]:raise ValueError('Transfer SHA256 mismatch; preserve files and return terminal log')
launch=pathlib.Path(tempfile.mkdtemp(prefix='launch-',dir=transfer))
with tarfile.open(archive) as tar:
    members=tar.getmembers();names=set()
    if sum(m.size for m in members)>20_000_000:raise ValueError('Unexpected packet expansion')
    for member in members:
        path=pathlib.PurePosixPath(member.name)
        if not member.isfile() or path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!='e009-preflight-v4' or member.name in names:
            raise ValueError('Unsafe or duplicate packet member')
        names.add(member.name)
    for member in members:
        target=launch/member.name;target.parent.mkdir(parents=True,exist_ok=True)
        with tar.extractfile(member) as src,target.open('xb') as out:shutil.copyfileobj(src,out)
packet=launch/'e009-preflight-v4'
env=os.environ.copy()
for key in ('PYTHONPATH','PYTHONHOME','PYTHONUSERBASE'):env.pop(key,None)
env.update(PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1')
argv=[sys.executable,'-I','-B',str(packet/'scripts/e009_owner.py'),
      '--root','/work/Home/dl_binner/e009',
      '--shared-root','/work/RasmusAllesøeNielsen#2936/dl_binner/e009',
      '--allocated-vcpus','8','--allocated-ram-gb','24',
      '--entry-start-epoch',str(started)]
os.execve(sys.executable,argv,env)
PY
BASH
```

The bootstrap uses Python for checksum/path validation, avoiding a dependency on
a missing `sha256sum` utility. Its entry time is passed into the driver, so transfer
verification/extraction counts toward the bounded work clock. The shell captures
output to a named `.log` file in transfer/. The driver also writes its live
`<attempt>-terminal.log` there and prints its path; only a stable terminal snapshot
is copied into the attempt/return. No live driver terminal log remains in attempt/.
A failed outer checksum/prerequisite leaves the outer log even before a trusted
packet can create a return. Never remove an old attempt to retry.

## What this command does and retains

1. Verify every packet member; retain the manifest even if later verification fails.
   The first mandatory COMEBin probe retains its **90-second** ceiling. Capture
   repeated stacks before normal site initialization, metadata/import/freeze progress,
   and owned Linux process wait/syscall/fd states before cleanup. Permission-denied
   kernel views are explicit unavailable evidence. No prefix relocation, reinstall,
   skipped inventory, timeout increase or claimed runtime repair. If the underlying
   stall persists, return diagnosis and stop before downloads/new environments.
2. Probe accepted E001 COMEBin numerical, mapping, AMBER and CheckM prefixes without
   installs; verify complete inventories/origins, accepted marker files, and byte
   trees before/after. Create new version-qualified E009 tool prefixes only.
3. Acquire exact selected source archives (~129 MB), CompleteBin DB (~156 MB),
   three small extra wheels, and 59 checksum-pinned Linux utility packages (~228 MB).
   The ~6.5-MB micromamba bootstrap is already in the packet. Native package identity
   locks are exact; local cross-platform solve is not a successful Linux install.
4. Test the 22-FASTA-contig / 407,631-total-DNA-bp software panel: real 740/370 paired
   reads, map/sort/index/depth, full eight-thread tiny MEGAHIT, all-chain truth and
   native AMBER; native tool feature readers/writers, markers, CPU plans and
   CompleteBin's actual 152-MB checkpoint/BAM reader/forward. No model fit/grid or
   biological E009 scores. Native defaults/schedules are prepared, not admitted.
5. Acquire the ~3.202-GB source-genome archive provisionally into owned shared
   storage, return its actual SHA256/member catalog and exact development overlap.
   Bulk reads (~9.732 GB compressed) are **not** acquired here. Source classification,
   near-overlap and actual-scale affordability remain later review work.
6. Keep new prefixes/cache/source DNA for subsequent reuse. Return compact logs,
   commands, inventories, input/output receipts, masks/axes, sampled CPU/RSS, failures
   and storage accounting. Large source/prefix/cache/BAM files remain on UCloud;
   their receipts/paths are returned. No colleagues' files or old attempts are touched.

Home must have ≥6 GB free; shared storage ≥30 GB free for this preflight. The older
200-GB estimate is future provisioning, not a hard cap or a request to provision
Home to 200 GB. Local byte-bound fixtures and new prefixes live in Home; heavy
sources live in the shared E009 child. Preserve the quoted Unicode/# path.

The job has **20-GB sampled working RSS**, **17,400 work seconds +600 collection
seconds**, at most **40 allocated core-hours** before optional evidence collection
following a timeout. Collection after a timeout is labelled, bounded and charged
separately, not hidden inside an execution success. Actual elapsed allocation cost
includes setup, failures and collection; owner idle/upload/provider billing are
separate. Final read-only hashing stays bounded even after the work timer expires;
an incomplete byte check is retained as unverified and cannot pass. Packets v1/v2/v3 are
retained locally, never edited into v4. Heartbeats
appear every ten seconds; native detail is in stage/tool logs.
Actual tools run serially. Torch phases may use eight threads/loader zero; process
pools and HMM/BGZF child budgets include their main/coordinator. Allocation caps
are not a promise that small or serial phases saturate eight CPUs.

Global prerequisite/verification/portable/evaluator failures stop dependent work.
An isolated tool contract failure is retained and skips that tool's dependent work;
other isolated contracts may finish. Overall status remains failed if any chosen
tool fails. Fatal Python tracebacks, live-worker hangs, clocks/RSS and cancellation
stop the supervised process groups promptly. No automatic fit, repair or retry.
The Mac four-thread MEGAHIT issue is **not repaired** by testing it serially: this
Linux job must pass its real eight-thread assembly contract.

## Return review and next boundary

Return the printed `RETURN_ARCHIVE`, `RETURN_CHECKSUM` and the `TERMINAL_LOG` file.
The driver also writes a compact collection receipt beside them. Logs remain in
transfer/ and attempt/. Preserve all created prefixes and shared source files.

Review checksums/member inventory; source SHA/catalog/development matches;
full isolated distributions/imports and unchanged read-only trees; actual effective
CPU/loader/HMM child limits; complete finite native axes/masks/zeros; CompleteBin
patch/checkpoint; competitive truth/repeats/orientation; AMBER length denominators;
failures/cleanup; actual wall/RSS/allocated cost and immutable return storage.
A preflight pass admits its tested software paths only. It does not certify native
full-community affordability or independent whole-MAG quality.

Only after returned review prepare the bounded **16-vCPU / 48-GB** acquisition,
sample-0 MEGAHIT, two-sample mapping/depth and full-reference truth job. Freeze
actual read/source hashes, biological target membership, assembly axes/strata,
ordered native BAM manifests and representative full-schedule projections before
any community fit or scores. Keep the modified CompleteBin-50 label. Do not launch
extra communities/seeds, marker interventions or the GLM/hybrid study automatically.
