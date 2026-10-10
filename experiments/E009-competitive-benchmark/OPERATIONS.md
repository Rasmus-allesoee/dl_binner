# E009 runtime recovery operations

Status: **v5 persistent-file read failure verified; full native preflight suspended**.
[The v5 receipt](linux-startup-failure-v5.json) records 175 read waits: 162 bytecode,
8 shared-library, 2 source and 3 metadata files. Fifteen minutes consumed only
10.51 sampled CPU seconds; increasing the timeout did not make reuse practical.
No tool/data setup, downloads, native contracts, fits or scores started.

## Next owner job: cheap source-cache recovery only

Use **CPU/Linux x86-64, 1 vCPU / 4 GB**, Home mounted, no competing workload or
Slurm needed. This job does **not** run the eight-vCPU preflight. It compares actual
source/cache reads, then tests the accepted COMEBin prefix's complete inventory,
origins, full freeze and all ten imports while bypassing old bytecode caches.
There are no installs, environment moves/copies, payload downloads or binning.

Upload the new `e009-preflight-v6.tar.gz` and its matching `.tar.gz.sha256` into
`/work/Home/dl_binner/e009/transfer/`. Local pair: `artifacts/e009-preparation/transfer-v6/`.
[transfer.json](transfer.json) binds the final source/archive/command. This small
recovery packet contains no micromamba, DNA fixture, model or Mac environment.
Preserve every older packet, failed attempt and environment. Paste this entire block:

```bash
bash <<'BASH'
set -Eeuo pipefail
transfer=/work/Home/dl_binner/e009/transfer
mkdir -p "$transfer"
terminal_log=$(python3 -I -B -S - "$transfer" <<'LOGPY'
import os, sys, tempfile
fd,path=tempfile.mkstemp(prefix='e009-recovery.',suffix='.log',dir=sys.argv[1])
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
archive=transfer/'e009-preflight-v6.tar.gz'
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
        if not member.isfile() or path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!='e009-preflight-v6' or member.name in names:
            raise ValueError('Unsafe or duplicate packet member')
        names.add(member.name)
    for member in members:
        target=launch/member.name;target.parent.mkdir(parents=True,exist_ok=True)
        with tar.extractfile(member) as src,target.open('xb') as out:shutil.copyfileobj(src,out)
packet=launch/'e009-preflight-v6'
env=os.environ.copy()
for key in ('PYTHONPATH','PYTHONHOME','PYTHONUSERBASE'):env.pop(key,None)
env.update(PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1')
argv=[sys.executable,'-I','-B',str(packet/'scripts/e009_owner.py'),
      '--root','/work/Home/dl_binner/e009',
      '--shared-root','/work/RasmusAllesøeNielsen#2936/dl_binner/e009',
      '--allocated-vcpus','1','--allocated-ram-gb','4',
      '--runtime-recovery-only',
      '--entry-start-epoch',str(started)]
os.execve(sys.executable,argv,env)
PY
BASH
```

The bootstrap and canonical driver terminal `.log` files, launch copies and
archive/checksum/collection receipt remain in transfer/. An immutable snapshot
of the canonical log is included in the return. The whole clock starts before
upload verification/extraction; failures preserve the verified packet manifest.

## Work and stopping conditions

1. Stream two exact source/cache pairs (`numpy/__init__.py`, `torch/utils/weak.py`)
   read-only, reporting actual hash/bytes/read time. Each read has a 15-second
   limit. Unavailable/slow bytecode is a diagnostic result. A failed source read
   stops the recovery, rather than assuming that ignoring caches fixes storage.
2. Run normal site initialization and **all original inventory/import/origin/full
   freeze checks** with `-I -B -X pycache_prefix=<empty job-local namespace>`.
   Python's `-B` forbids cache writes but does not forbid cache reads. Explicit
   `-X` ignores old `__pycache__` directories, loading the same original source;
   an environment variable alone would be ignored by `-I`. Audit cache accesses
   in the inventory and its pip child. Neither original nor temporary caches are
   written. See [Python's cache-prefix contract](https://docs.python.org/3.13/library/sys.html#sys.pycache_prefix).
3. Re-read the sampled source files and verify unchanged bytes. This is a sampled
   read-only check, not acceptance of the whole old prefix's bytes. Whole native
   admission, other prefixes and all tool contracts remain unresolved.

**300 seconds work, 30 seconds normal collection reserve; 3-GB sampled working
RSS, one CPU/loader zero.** Inventory cap: 180 seconds; idle cap: 45 seconds
without observed phase/stack/open-file movement. Fatal causes stop promptly with
owned-process cleanup. The driver snapshots only this small recovery attempt,
not every previous prefix/shared file. Evidence collection after a timeout is
separately bounded/accounted, never presented as execution success. Allocation
cost is declared CPUs times driver wall, including setup/failures/collection,
distinct from sampled CPU time or provider/owner idle. Maximum normal clock is
0.091667 allocated core-hours; post-timeout evidence collection can add up to 120
seconds (0.033333 core-hours). This is not an exact billing prediction.

## Return and subsequent boundary

Return the printed archive/checksum and the **last printed `TERMINAL_LOG` file**.
Review source-versus-cache timings, full distributions/freeze/origins, zero old
bytecode access, no writes, sampled unchanged source bytes, limits/cleanup and
actual allocation costs. A Linux pass establishes this import workaround only;
it does not admit full-scale tools or certify all persistent storage as healthy.

After a pass, prepare the original eight-vCPU native preflight using the validated
cache policy, with source/library byte binding that avoids treating ignored,
regenerable bytecode as executed input. Audit every native Python child (including
shell wrappers/spawned workers) before that transfer. Do not rerun accepted science.
If source/binary reads remain slow, retain the read evidence and replace the direct
Home runtime strategy: evaluate an immutable packed job-local execution snapshot
or a separately pinned runtime. Neither automatic arbitrary Conda relocation nor
unrecorded dependency changes is allowed. Do not launch another prolonged import
on eight CPUs or change the benchmark shortlist/data just to avoid this failure.
