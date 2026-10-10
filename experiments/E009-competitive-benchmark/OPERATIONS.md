# E009 progress-aware runtime recovery operations

Status: **v7 progressing copy killed by its premature inner cap; no native runtime
admission**. [Verified return](linux-startup-failure-v7.json): 17,989/44,770 entries
at 1,200.068 seconds, 22.53 sampled CPU seconds. Overall 1,800-second ceiling had
not expired. All nine members/seven inventory hashes verify; immutable returned
payload 602,809 logical bytes. Declared one-CPU /4-GB driver cost before collection:
1,200.179870 seconds /0.333383 allocated core-hours. No imports/setup/science began.

## Next owner job: reduced runtime, sealed chunks and one overall clock

Use **CPU/Linux x86-64, 1 vCPU /4 GB**, Home mounted, no competing work/Slurm.
Provision a **two-hour Terminal allocation**; the command explicitly chooses
**90 minutes total work plus up to 120 seconds normal collection**, covering parent
verification/setup, selection, copy, hash, chunk packing/persistence, restore,
local verification and imports. This is a ceiling, not a runtime forecast.
There is **no separate stage wall-time cap**, including no 1,200-second copy limit
or 180-second import limit. Five minutes without observed work triggers the stall
guard. Actual CPU/RAM allocation is declared independently; sampled RSS ceiling
is 75% of declared RAM (3 GB at 4 GB). Native affinity bounds the whole tree to the
declared CPU count; eight storage readers share that budget, loader zero.

At the observed ~15 entries/second, all 44,770 entries project to ~49.8 minutes
before other work; 90 minutes leaves ~40 minutes for variability, byte throughput,
metadata, chunk writes/hashes, verification and imports. Pruning reduces entries,
but **native selected count/bytes and new-path throughput are not yet measured**.
The initial returned selection receipt reports actual counts, bytes, omission
reasons and a rough projection at the measured rate. No laptop timing or assumed
linear CPU speedup determines this clock. The 300-second stall allowance is about
60 times the worker's normal five-second report interval; large files also report
completed bytes. Parent heartbeats, repeated counters and mere phase labels do
not count as work. The owner can select another positive `--work-seconds` value;
all children follow the remaining clock, without hidden lower stage caps.

Upload **only the new v8 pair**, `e009-preflight-v8.tar.gz` and its matching
`.tar.gz.sha256`, into `/work/Home/dl_binner/e009/transfer/`. Local pair:
`artifacts/e009-preparation/transfer-v8-final/`. [transfer.json](transfer.json) owns the
final source `bd7addb6e3e646a80bab57deadf9e847e3f02858`, 61,445 archive bytes,
SHA256 `32c3a9f23cc101982bef8b4d3dc318bc76718cce63f79bee52741eca411888ca`.
Never launch the v7 pair or the local-only provisional v8 packet.
Paste the entire tested block:

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
archive=transfer/'e009-preflight-v8.tar.gz'
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
        if not member.isfile() or path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!='e009-preflight-v8' or member.name in names:
            raise ValueError('Unsafe or duplicate packet member')
        names.add(member.name)
    for member in members:
        target=launch/member.name;target.parent.mkdir(parents=True,exist_ok=True)
        with tar.extractfile(member) as src,target.open('xb') as out:shutil.copyfileobj(src,out)
packet=launch/'e009-preflight-v8'
env=os.environ.copy()
for key in ('PYTHONPATH','PYTHONHOME','PYTHONUSERBASE'):env.pop(key,None)
env.update(PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1')
argv=[sys.executable,'-I','-B',str(packet/'scripts/e009_owner.py'),
      '--root','/work/Home/dl_binner/e009',
      '--shared-root','/work/RasmusAllesøeNielsen#2936/dl_binner/e009',
      '--allocated-vcpus','1','--allocated-ram-gb','4',
      '--runtime-recovery-only',
      '--snapshot-state','/work/Home/dl_binner/e009/runtime-snapshots/comebin-runtime-v8',
      '--work-seconds','5400','--stall-seconds','300',
      '--entry-start-epoch',str(started)]
os.execve(sys.executable,argv,env)
PY
BASH
```

Both live terminal logs, launch copies and returns remain in transfer/. Request
the printed return archive/checksum and **last printed `TERMINAL_LOG`**; end the
allocation after collection. Maximum normal declared-one-CPU work/collection cost
is 1.533333 core-hours, excluding owner idle/upload and provider billing differences.
Failed stages/collection are measured, not equated with process CPU seconds.

## Selection, verification and resume contract

- Retain Python executables, the standard library, numerical/package shared
  libraries, all remaining package sources/resources/models/databases, distribution
  metadata/licences and Conda provenance. Keep public `testing`/`_testing` helpers.
- Omit recorded bundled `test`/`tests` suites, compiler/header trees, static `.a`/
  `.la` libraries, compiler/build metadata, non-Python CLI tools and other
  non-numerical top-level payloads, plus regenerable bytecode. Internal symlink
  targets are included transitively even when the filter would otherwise omit them.
  This is a **numerical execution runtime**, not a whole environment distribution
  or a compiler/pytest/test-data installation. Separate pinned utility tools remain
  required in the later full preflight. No source bytes/versions/science are edited.
- The completed inventory receipt stays byte-identical on resume; operation counts
  belong to the attempt summary. The full source/selection plan and copied hashes
  live under the explicit
  persistent `runtime-snapshots/comebin-runtime-v8/` state. Plans use portable size/
  mtime/mode/link identities across job mounts; within each original read, device/
  inode and stat identities are checked too. Source changes refuse resume.
- Up to 128 members /roughly 128 MB form a chunk; a larger single library is streamed
  as its own chunk. Copy/hash original bytes once to fresh job-local storage, then
  immediately seal a tar and checksum-bound member receipt in Home. The worker
  reports source and persisted-byte progress. Partial/unsealed tar/JSON files are
  retained but ignored. Concurrent writers are rejected by a process-lifetime lock.
- **Rerunning this same v8 command is an explicit resume request for this state**:
  it verifies/restores sealed chunks and only copies missing source contents. Each
  attempt/local prefix/log/return remains uniquely named. Receipt/archive/member
  corruption fails; do not edit receipts to accept it. A changed selection policy
  needs a new versioned state. No valid completed native/scientific step is repeated.
- Finish full local hash verification, then the accepted complete freeze/version/
  distribution/module/stdlib origins, no original-prefix Linux mapped libraries and
  small NumPy/Torch arithmetic. Reverify all local bytes afterward. Copied console
  scripts are never used. This admits only the numerical runtime, not full native
  binner/fixture/scale readiness. See [D006](../../docs/decisions/D006-environment-ownership.md).

A whole prefix is unnecessary for this scope: v7 copied compiler sources, headers
and NumPy/Pandas/SciPy test data while numerical dependencies had not all arrived.
A ten-module-only dependency closure would be more fragile; keeping ordinary
package sources/data/metadata plus shared libraries is the conservative reduction.
Native imports/real tool contracts still must demonstrate that nothing needed was
omitted. Original E001 prefix and all failed attempts remain unchanged.

## What survives and what remains unverified

Persistent sealed chunks survive Terminal resets. Job-local `/tmp` trees do not.
The failed v7 `/tmp/e009-cache-recovery-ttr51i74/prefix`, if still present, has no
per-file hashes/chunk seals and is not silently admitted or reused; preserve it.
Code/source history, original env and immutable failure return remain recoverable.
The new state needs space for only missing chunk bytes/tar headers on resume;
local `/tmp` needs the complete selected runtime. Initial selection reports bytes
and the worker checks free space before copying. No shared colleagues' files move.

Linux reduced selection completeness, native library portability, fresh/resumed
throughput, chunk-lock/filesystem semantics, all ten imports/Torch arithmetic and
cost remain pending. Local cardinality/recovery tests cannot certify these. The
provider filesystem cause remains unidentified. Full eight-CPU preflight stays
disabled until returned native recovery evidence is reviewed; after a pass prepare
its sealed-chunk restore and audit dependent interpreter/shell/tool paths.
No UCloud execution by Codex, community fits/scores or architecture work.
