# E009 runtime recovery operations

Status: **v6 source-file waits verified; direct Home imports superseded; full native
preflight suspended**. [Receipt](linux-startup-failure-v6.json) verifies checksum
and all archive inventory bytes. The Python process spent 180.170 seconds /2.94
CPU seconds importing; all 34 captured file waits were on original `.py` sources.
The source-cache-only workaround is insufficient. This is not Bash syntax or a
scientific failure. No native binner/data setup/fits/scores have begun.

## Next owner job: immutable job-local numerical snapshot

Use **CPU/Linux x86-64, 1 vCPU /4 GB**, Home mounted, no competing workload or
Slurm. Do not rent eight CPUs for this storage recovery. Upload the new
`e009-preflight-v7.tar.gz` and `.tar.gz.sha256` to
`/work/Home/dl_binner/e009/transfer/`; local pair is
`artifacts/e009-preparation/transfer-v7/`. [transfer.json](transfer.json) owns the
final committed source/hash identities. Preserve all older packets and attempts.
The bundle contains only reviewed code/records; no Mac environment or DNA/model.

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
archive=transfer/'e009-preflight-v7.tar.gz'
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
        if not member.isfile() or path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!='e009-preflight-v7' or member.name in names:
            raise ValueError('Unsafe or duplicate packet member')
        names.add(member.name)
    for member in members:
        target=launch/member.name;target.parent.mkdir(parents=True,exist_ok=True)
        with tar.extractfile(member) as src,target.open('xb') as out:shutil.copyfileobj(src,out)
packet=launch/'e009-preflight-v7'
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

Both bootstrap and canonical terminal logs remain in transfer/. Return the
printed archive/checksum and **last printed `TERMINAL_LOG`**. End the allocation
after collection; idle time outside the driver is not in its cost receipt.

## Changed production path and acceptance boundary

1. Read the original standalone COMEBin Conda prefix once using eight I/O readers
   under one-CPU affinity. Hash each regular file while copying to unique `/tmp`
   storage, preserving bytes/modes; omit only `__pycache__`, `.pyc`, `.pyo`.
   Original file/stat identities must be unchanged. Reject external links, venvs
   and special files; normalize internal links to equivalent relative targets.
   No install, upgrade, binary-prefix rewrite, activation or original-prefix edit.
2. Verify all local bytes; retain an uncompressed immutable archive and full
   inventory under `e009/runtime-snapshots/<attempt>/`. Space needed is reported
   from actual original non-bytecode size: that much in job-local `/tmp` and that
   much in Home plus reserves. Large numerical archive is not in the compact
   return. Even a later import failure retains the reusable archive/receipt, so
   we need not reread thousands of Home files again.
3. Invoke **local snapshot `bin/python` directly**, isolated/no bytecode writes,
   with local libraries preferred. Keep the same 180-second inventory limit and
   all ten imports, exact original full freeze/version and origins. Check local
   standard-library origins, no original-prefix Linux mapped binaries, NumPy
   matrix arithmetic and Torch backward. Do not execute copied console scripts.
4. Check local bytes again after execution. A pass admits this numerical snapshot
   only, never other environments, tool CLI/fixture contracts or community work.
   Snapshot copying is not generic Conda portability: see the explicit
   [D006 exception](../../docs/decisions/D006-environment-ownership.md).

**30 minutes work plus 30 seconds normal collection**, copy/verify/pack stage at
most 20 minutes, imports at most 180 seconds /45 seconds without observed progress;
3-GB sampled working RSS, one CPU, loader zero. Eight storage readers are not
numerical workers: their CPU use shares the one-CPU affinity. This new clock pays
for one-time materialization, not a larger import timeout. Expected copy time is
unknown until Linux evidence; the ceiling is not a prediction. Normal maximum is
0.508333 allocated core-hours; post-timeout collection can add at most 120 seconds
(0.033333). Parent verification/setup share the work clock; captured cost includes
those failures. Fatal causes and limits stop/clean owned processes.

For later **explicit** reuse, pass `--runtime-snapshot` with the exact receipt
path returned in `snapshot-bound.json`, under this experiment's runtime-snapshots
folder. The production restore verifies archive SHA and every restored member;
changed/partial receipts or archives cannot receive acceptance. Do not edit a
receipt to accept corruption. This mechanism is prepared/tested, not permission
for another unreviewed run or automatic retry.

## Next review

Review archive/inventory identities, Linux local import/library origins, numerical
compatibility, limits/cleanup and cost. If the copy stalls, its per-file progress
and supervisor evidence are retained; do not return to another direct Home import
or silently increase limits. If compatibility fails, inspect its concrete cause
and decide between a narrowly repaired execution path and a new source/payload-
pinned runtime. Original prefixes, science and the shortlist stay unchanged.
After a native pass, prepare the full eight-CPU preflight with a verified archive
restore and audit all dependent interpreter/shell/loader paths before transfer.
Full native preflight remains disabled in v7. No benchmark execution is authorized.
