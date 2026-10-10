# E009: two remaining native contracts after accepted v10 stages

[The reviewed v10 return](linux-preflight-v10.json) accepts SemiBin, MetaCAT,
CompleteBin, Linux eight-thread assembly/mapping/depth/truth/evaluator and source
acquisition/catalog. No full fits or E009 scores ran. Preserve the original
`native-preflight-95psvpr9`, all acquired source/data/cache/utility files, original
E001 environments and all 151 accepted v8 chunks.

## Next owner job

Use **8-vCPU /24-GB CPU/Linux x86-64 Terminal**, glibc>=2.28, no competing work.
Choose **two hours**. V11 selects **6,600 seconds total work +600 collection**,
20-GB sampled working RSS and eight-CPU affinity. At most **16 allocated core-hours**;
this is a conservative cold-install ceiling, not an expected runtime. Acquisitions
are network-bound; native tools execute serially with phase budgets including
N-1 pools/coordinator and loader zero. Existing 300-second no-progress/startup/
CPU-I/O guards remain; there are no shorter productive-stage wall caps.

Read existing tiny ordered BAMs at the v10 attempt, acquired pinned SCGBinner/
COMEBin archives and retained utility prefix. Restore accepted numerical chunks
only for COMEBin's unchanged dependency recipe, with zero original recopy. Install
**new independent complete SCGBinner and CheckM Conda prefixes** from exact locked
payloads, offline/no solver, plus the official CPU Torch wheel for SCGBinner.
Approximately **476.7 MB** compressed dependency payloads before cache deduplication;
allow >=6 GB free Home plus ~2.2 GB temporary restore space. CheckM alone calls
its own interpreter/library stack; frozen E001 marker data remains read-only.
No new environment snapshot, pruning, blanket prefix hashes or old-prefix install.

Writes: new uniquely named E009 attempt, corrected version-qualified prefixes,
new cache, wrappers/logs and transfer archive/checksum. The shared source DNA/catalog
is neither read nor written by this retry. No new bulk source/read download,
assembly, mapping, AMBER, passed-tool contract, community fit or score. Failure
skips dependent work for that path; the other isolated failed path may proceed.
A combined failed status is not admission for science.

## Upload and one grouped command

Upload `e009-preflight-v11.tar.gz` and its matching `.tar.gz.sha256` from
`artifacts/e009-preparation/transfer-v11-final/` to
`/work/Home/dl_binner/e009/transfer/`. [transfer.json](transfer.json) binds final
source, exact packet/command and local checks. Old packets remain unchanged.

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
archive=transfer/'e009-preflight-v11.tar.gz'
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
        if not member.isfile() or path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!='e009-preflight-v11' or member.name in names:
            raise ValueError('Unsafe or duplicate packet member')
        names.add(member.name)
    for member in members:
        target=launch/member.name;target.parent.mkdir(parents=True,exist_ok=True)
        with tar.extractfile(member) as src,target.open('xb') as out:shutil.copyfileobj(src,out)
packet=launch/'e009-preflight-v11'
env=os.environ.copy()
for key in ('PYTHONPATH','PYTHONHOME','PYTHONUSERBASE'):env.pop(key,None)
env.update(PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1')
argv=[sys.executable,'-I','-B',str(packet/'scripts/e009_owner.py'),
      '--root','/work/Home/dl_binner/e009',
      '--shared-root','/work/RasmusAllesøeNielsen#2936/dl_binner/e009',
      '--allocated-vcpus','8','--allocated-ram-gb','24',
      '--failed-native-only','--work-seconds','6600','--stall-seconds','300',
      '--entry-start-epoch',str(started)]
os.execve(sys.executable,argv,env)
PY
BASH
```

Return the printed **RETURN_ARCHIVE**, **RETURN_CHECKSUM** and **last TERMINAL_LOG**,
including on failure. Preserve the optional COLLECTION_RECEIPT; through-collection
allocation cost is also in the live terminal. End the allocation after collection.
Exact immutable archive bytes differ from the growing live log or provider billing.

## Local versus Linux validation

SCGBinner's actual requirements/private imports select sklearn1.6.1, Torch2.0.0+cpu
and the explicitly named Python3.10/NumPy1.26/pandas1.5 CPU compatibility recipe.
CheckM's complete Linux Bioconda1.2.3 payload retains checkm.test. Local Mac checks
use fresh owned Conda dependencies and the official complete CheckM wheel; pinned
Linux pplacer is unavailable on Mac. No Linux install or lineage-fit credit follows
from that local help test. The retry calls actual augmentation writers/readers,
SCGBinner's seeded initializer/HNSW and CheckM help, without full fits or truth K.
Mac overrides/negative checks and final packet checks are explicit in the transfer
receipt. Corrected Linux installs, eight-CPU feature workers and complete CheckM
still need this returned evidence. A passed tiny contract is not community-scale
training affordability or scientific quality.

After returned review, accept successful remaining checks, assess source/sample
scope and prepare the bounded bulk read/assembly/depth/truth step. No automatic
full fits, new seeds, architecture comparison or UCloud execution by Codex.
