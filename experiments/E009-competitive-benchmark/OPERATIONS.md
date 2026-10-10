# E009 native preflight after accepted v8 runtime recovery

The [v8 return](linux-runtime-recovery-v8.json) passes the **specific numerical
runtime gate**: Linux Python 3.13.14, all 86 accepted distributions, ten module
origins, local stdlib/shared libraries and NumPy/Torch compatibility arithmetic.
Selected 18,977/44,770 entries /1,682,401,752 logical bytes; 151 sealed chunks /
1,716,981,760 archive bytes. Fresh copy used 143.613 s; imports 13.670 s;
verification 3.867 s. Driver before collection: 161.307 s at declared 1 vCPU /4 GB,
0.0448074 allocated core-hours, peak sampled RSS 460,787,712 bytes. /proc confirms
CPU affinity 0. All 24 archive members /22 inventory hashes pass; immutable
payload 1,036,210 logical bytes. Exact after-collection allocation cost is unknown
because its separate receipt was not uploaded. No community was fitted/scored.

Native **fresh creation**, not native restore, was executed. The returned chunk
receipts/hashes are worker evidence; bulk chunks/final inventory stayed on UCloud
and cannot be independently rehashed on Mac. V9 binds their exact final receipt,
all 151 seals, tar hashes/member hashes and population during read-only restore.
The original E001 numerical environment is never recounted or recopied.

## Next owner job: tiny native contracts, no community fits

Use **CPU/Linux x86-64, 8 vCPU /24 GB**, glibc >=2.28, Home and project shared
storage mounted; no competing work/Slurm. Choose **five hours** as the allocation
ceiling. V9 selects **17,400 seconds overall work +600 seconds collection** and
20-GB sampled working RSS. The whole tree has eight-CPU affinity; tools execute
serially. This remains the prospectively bounded <=40-core-hour preflight, not a
runtime forecast. It includes cold utility setup and a 3.2-GB source download;
no native timings yet justify a tighter ceiling. End the allocation after return
collection. Source-genome acquisition is preparatory and is not admitted as
scientific input until its new SHA/source overlap is reviewed. No reads download.

All Python inventories, install/import/feature workers and nested native commands
use the remaining overall clock, **without shorter stage wall caps**. Restore/
hashing watches advancing completed bytes/entries. Other native workers use a
300-second no-activity guard based on launched-tree CPU and physical I/O; quiet
compute is activity, parent heartbeats are not. Import probes retain phase/stack/
file observations. Five-minute stalls preserve causes/waits and stop the owned
process group; the guard has local failure tests, not measured full native timings.
Network connection/socket inactivity remains separately bounded by the existing
60-second transport timeout. The owner can choose another overall `--work-seconds`
value, but an extension requires consistent Terminal time plus collection reserve.

## Upload and exact command

Upload only `e009-preflight-v9.tar.gz` and matching `.tar.gz.sha256` from
`artifacts/e009-preparation/transfer-v9-final/` to
`/work/Home/dl_binner/e009/transfer/`. [transfer.json](transfer.json) binds the final
packet/source, command and tests. Old v1-v8 uploads remain preserved and superseded
for this next native preflight. Paste the entire locally tested block:

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
archive=transfer/'e009-preflight-v9.tar.gz'
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
        if not member.isfile() or path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!='e009-preflight-v9' or member.name in names:
            raise ValueError('Unsafe or duplicate packet member')
        names.add(member.name)
    for member in members:
        target=launch/member.name;target.parent.mkdir(parents=True,exist_ok=True)
        with tar.extractfile(member) as src,target.open('xb') as out:shutil.copyfileobj(src,out)
packet=launch/'e009-preflight-v9'
env=os.environ.copy()
for key in ('PYTHONPATH','PYTHONHOME','PYTHONUSERBASE'):env.pop(key,None)
env.update(PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1')
argv=[sys.executable,'-I','-B',str(packet/'scripts/e009_owner.py'),
      '--root','/work/Home/dl_binner/e009',
      '--shared-root','/work/RasmusAllesøeNielsen#2936/dl_binner/e009',
      '--allocated-vcpus','8','--allocated-ram-gb','24',
      '--work-seconds','17400','--stall-seconds','300',
      '--entry-start-epoch',str(started)]
os.execve(sys.executable,argv,env)
PY
BASH
```

Return the printed archive, matching checksum and **last printed `TERMINAL_LOG`**.
Keep the printed `COLLECTION_RECEIPT` too (optional upload); its allocation cost
is now also printed in the live log. Return payload bytes come from the immutable
archive, not a log that continues growing after collection. Provider billing/
owner idle is distinct from process CPU or driver allocation estimates.

## What this changes and reuses

- Restore the accepted **comebin-runtime-v8** chunks into a fresh job-local prefix.
  The name/state stays v8; v9 is the consumer packet. Missing/corrupt seals or bytes
  fail; there is no fallback to original source copying or new materialization.
  The persistent state stays unchanged and is protected by a shared read lock.
  Job-local free space must cover 1.68 GB plus 500 MB overhead.
- Reuse the accepted numerical inventory by restored bytes; a cheap per-job probe
  verifies lexical Python/version/stdlib. New source-only venvs receive explicit
  dependency links to this restored prefix. Full per-tool distributions/origins
  and no original-prefix mapped libraries are checked before their native paths.
  Every Python child uses `-I -B` and the job-local cache namespace.
- Use **new `source-v2`/`utilities-v2` prefixes**. Tool venvs and wrapper paths bind
  this attempt's job-local restored runtime; they are retained provenance, **not
  portable environments or ready-to-reuse interpreters after /tmp resets**.
  Future jobs must restore and create explicitly bound execution environments;
  never edit an executed binding in place or delete its required source evidence.
- Invoke the tiny original CheckM console **source** via the restored lexical
  interpreter, bound before/after. Do not invoke its old shebang; omitted numerical
  console scripts stay omitted. Its actual source hash is returned for review.
  CheckM markers remain hash-bound read-only under E001. Native CheckM help is
  pending; this does not generalize snapshot permission to other prefixes.
- Keep original mapping/AMBER prefixes and AMBER source read-only, with actual
  versions/inventories/source hashes and before/after bindings. AMBER receives
  its own library path. The v8 numerical pass does not validate their cold startup.
- Acquire pinned sources, CompleteBin database (155.9 MB), 59 explicit Linux utility
  packages (228 MB compressed), and per-tool extra wheels. Compile minimap2 in an
  E009 copy; retain setup logs/resolved package identities. No reference cache edit.
  CompleteBin remains **modified max-50**, SCGBinner's operational dtype fix is
  unchanged. Sources/models/defaults/training/clustering are otherwise unchanged.
- Exercise tiny real 11-contig /59,232-bp fixtures: Linux eight-thread MEGAHIT,
  mapping/ordered depth, competitive coordinates/truth, AMBER/confirmed R95
  software contracts; five native tool CLI/features and CompleteBin checkpoint/
  forward. **No native model fit, learned embeddings, candidate grid or E009 score.**
  One tool failure skips its dependent stages and remains a failed combined gate;
  another isolated tool may proceed. No automatic retry or failure bypass.

Home owns code, caches/prefixes/transfers/logs (>=6 GB free). Only the owned shared
`/work/RasmusAllesøeNielsen#2936/dl_binner/e009/source-preflight-v1/` receives the
3.2-GB source archive/unpacked catalog (>=30 GB free). Quote this path; do not touch
colleagues' files. Original environments/failed attempts/chunks remain unchanged.
Provisioning estimates are separate from scientific design and actual receipts.

## Acceptance boundary

Local actual reader/writer/restore/venv-wrapper/clock/cleanup checks are required
before transfer; native Linux validation remains pending for restored consumers,
AMBER/mapping/utility bindings, tool feature axes/checkpoint and eight-thread
assembly. A local fixture does not prove all runtime imports, full native schedules,
community quality, assembly-scale affordability or near-genome independence.
After the return, accept successful stages and inspect failures before preparing
the bulk assembly/depth/truth step. Resolve the documented two-sample scope before
that scientific job. No UCloud execution by Codex, fits/scores or architectures.
