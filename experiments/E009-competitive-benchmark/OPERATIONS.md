# E009 operations: GCP migration and current stop boundary

Updated: 2026-10-13. **UCloud is inaccessible; do not run the old owner command.**
The current operational entry point is [Google Cloud operations](../../docs/CLOUD.md),
with [STATE](../../docs/STATE.md) and [D014](../../docs/decisions/D014-google-cloud-workspace.md).
The full former handoff is [archived](../../docs/history/E009_UCLOUD_OPERATIONS.md);
the text below remains original prepared-command provenance, not a next job.

Phase 1 establishes billing-verified CPU Linux/SSH/Codex/private-archive access;
it excludes v14 archive review, data acquisition, fitting and scoring. After
that passes, independently inspect the already returned v14 evidence, accept
success without replay and resolve 10 versus 20 read samples on one sample-0
assembly with costs/representativeness/peak storage. Freeze protocol/ordered axes
before direct GCP bulk acquisition/assembly/depth/truth. A tiny UCloud runtime
contract does not prove the new GCP runtime or community-scale affordability.
Accepted scientific evidence remains accepted; old prefixes/source/data/chunks
are preserved but inaccessible. No GCP commands have yet been executed.

---

## Historical original handoff (do not execute)

# E009: two remaining native contracts after accepted v10 stages

[The reviewed v10 return](linux-preflight-v10.json) accepts SemiBin, MetaCAT,
CompleteBin, Linux eight-thread assembly/mapping/depth/truth/evaluator and source
acquisition/catalog. No full fits or E009 scores ran. Preserve the original
`native-preflight-95psvpr9`, all acquired source/data/cache/utility files, original
E001 environments and all 151 accepted v8 chunks.

## Next owner job

Use **8-vCPU /24-GB CPU/Linux x86-64 Terminal**, glibc>=2.28, no competing work.
Choose **three hours**. V14 selects **10,200 seconds total work +600 collection**,
20-GB sampled working RSS and eight-CPU affinity. At most **24 allocated core-hours**;
this is a conservative cold-install ceiling, not an expected runtime. Acquisitions
are network-bound; native tools execute serially with phase budgets including
N-1 pools/coordinator and loader zero. Existing 300-second no-progress/startup/
CPU-I/O guards remain; there are no shorter productive-stage wall caps.

Read existing tiny ordered BAMs at the v10 attempt, acquired pinned SCGBinner/
COMEBin archives and retained utility prefix. Restore accepted numerical chunks
only for COMEBin's unchanged dependency recipe, with zero original recopy. Install
**new independent complete SCGBinner and CheckM Conda prefixes** from exact locked
payloads, offline/no solver, including CPU Torch for SCGBinner.
Approximately **577.1 MB** compressed dependency payloads before cache deduplication;
allow >=10 GB free Home plus ~2.2 GB temporary restore space. CheckM alone calls
its own interpreter/library/native-binary stack; frozen E001 marker data remains read-only.
No new environment snapshot, pruning, blanket prefix hashes or old-prefix install.

Writes: new uniquely named E009 attempt, corrected version-qualified prefixes,
new cache, wrappers/logs and transfer archive/checksum. The shared source DNA/catalog
is neither read nor written by this retry. No new bulk source/read download,
assembly, mapping, AMBER, passed-tool contract, community fit or score. Failure
skips dependent work for that path; the other isolated failed path may proceed.
A combined failed status is not admission for science.

## Upload and one grouped command

Upload `e009-preflight-v14.tar.gz` and its matching `.tar.gz.sha256` from
`artifacts/e009-preparation/transfer-v14-final/` to
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
archive=transfer/'e009-preflight-v14.tar.gz'
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
        if not member.isfile() or path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!='e009-preflight-v14' or member.name in names:
            raise ValueError('Unsafe or duplicate packet member')
        names.add(member.name)
    for member in members:
        target=launch/member.name;target.parent.mkdir(parents=True,exist_ok=True)
        with tar.extractfile(member) as src,target.open('xb') as out:shutil.copyfileobj(src,out)
packet=launch/'e009-preflight-v14'
env=os.environ.copy()
for key in ('PYTHONPATH','PYTHONHOME','PYTHONUSERBASE'):env.pop(key,None)
env.update(PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1')
argv=[sys.executable,'-I','-B',str(packet/'scripts/e009_owner.py'),
      '--root','/work/Home/dl_binner/e009',
      '--shared-root','/work/RasmusAllesøeNielsen#2936/dl_binner/e009',
      '--allocated-vcpus','8','--allocated-ram-gb','24',
      '--failed-native-only','--work-seconds','10200','--stall-seconds','300',
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

SCGBinner's actual requirements/private imports select sklearn1.6.1, all-Conda CPU Torch2.0.0 (distribution2.0.0.post104)
and the explicitly named Python3.10/NumPy1.26/pandas1.5 CPU compatibility recipe.
CheckM's complete Linux Bioconda1.2.3 payload retains checkm.test. Local Mac checks
use fresh owned Conda dependencies and the official complete CheckM wheel; pinned
Linux pplacer is unavailable on Mac. No Linux install or lineage-fit credit follows
from that local help test. COMEBin’s accepted full Linux help is receipt-bound and not repeated. Its feature
probe invokes the exact pinned native augmentation functions with the actual
parser/defaults, avoiding unrelated training-only AMP imports on the older Mac
validation runtime. The retry calls actual augmentation writers/readers,
SCGBinner's seeded initializer/HNSW and CheckM `lineage_wf -h`, without full fits or truth K.
Mac overrides/negative checks and final packet checks are explicit in the transfer
receipt. Corrected Linux installs, eight-CPU feature workers and complete CheckM
still need this returned evidence. A passed tiny contract is not community-scale
training affordability or scientific quality.

After returned review, accept successful remaining checks, assess source/sample
scope and prepare the bounded bulk read/assembly/depth/truth step. No automatic
full fits, new seeds, architecture comparison or UCloud execution by Codex.

The first proposed local v11 packet was rejected before owner transfer: a mixed
Conda/pip Torch2.0 stack crashed at CPU thread setup, and the older Mac COMEBin
runtime lacks modern training AMP imports. Preserve that packet, its failed local
attempt and prefixes. V14 uses one all-Conda CPU SCGBinner stack (four-thread
setup passes locally) and reuses already accepted Linux full-help evidence while
checking the unchanged native feature API. A local probe-observer shutdown race
also reproduced: a late SIGUSR1 could kill a finished interpreter. Restoring an
ignored signal disposition before registering faulthandler fixes that race,
without suppressing active stack dumps or relaxing failure/resource guards.

The second local packet (v12) passed the complete SCGBinner contract but rejected
CheckM's top-level `--help`: its actual 1.2.3 parser disables global help and has
an upstream list/string comparison bug. V14 uses `lineage_wf -h`, exercising the
relevant native command's parser without a fit. The complete CheckM wrapper passes
locally with this invocation. Linux additionally checks its own HMMER, Prodigal
and pplacer entry points; Mac lacks the pinned Linux pplacer and grants no credit
for those Linux checks or lineage placement. Preserve the v12 packet/failed return.

### Final cold-install allowance

[Actual Linux/noarch payload inventories](linux-package-inventory-v14.json) were
hash-verified locally: 36,207 SCGBinner +16,866 CheckM paths, and 41,254 paths in
151 shared-cache packages. Cache extraction plus the two copied prefixes means
**94,327 payload path materializations**, excluding metadata/directories/generated
bytecode. Deduplicated download is **497,171,498 bytes**; the two-lock sum is
577,118,190. Cache, both prefixes and two compressed copies require at least
7.45 GB before overhead: provision >=10 GB free Home plus ~2.2 GB temporary restore.
At the old observed 17,989 copies/1,200 seconds, just the payload path comparison
is ~105 minutes. This is not Conda throughput evidence, but it makes the initial
two-hour proposal too tight. Final owner allocation is **three hours /24 core-hour
maximum**, 10,200 seconds shared work +600 collection, with no shorter stage caps.
New Linux install throughput is still unknown; end the allocation after return.
The passed local v13 packet remains immutable; v14 changes only operational clock/
space defaults and packaging version, with the scientific/native adapters unchanged.

The final exact v14 packet/command passes local integration: real SCGBinner full
help/augmentation/reader/initializer/HNSW and complete CheckM lineage help followed
by COMEBin native augmentation/axis validation. Only the two failed contracts run;
prior accepted receipts remain unchanged. [Local evidence](local-failed-paths-v14.json)
records actual paths, platform substitutions, preserved negative packets, timings,
immutable returns and Linux omissions. Final53 regressions/docs checks pass.
