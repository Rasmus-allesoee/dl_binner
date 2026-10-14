# Historical E009 UCloud v14 handoff

Archived: 2026-10-13 from `2109998a230a0757be424e6f55c3a1bf17971ebe`.
**Do not execute: UCloud is inaccessible. V14 was independently accepted on 2026-10-14; its successful contracts are not a new job.**
Preserved as prepared/executed provenance, not a Google Cloud command.
Current entry points: [STATE](../STATE.md), [Google Cloud operations](../CLOUD.md).

# E009: two remaining native contracts after accepted v10 stages

[The reviewed v10 return](../../experiments/E009-competitive-benchmark/linux-preflight-v10.json) accepts SemiBin, MetaCAT,
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
`/work/Home/dl_binner/e009/transfer/`. [transfer.json](../../experiments/E009-competitive-benchmark/transfer.json) binds final
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

[Actual Linux/noarch payload inventories](../../experiments/E009-competitive-benchmark/linux-package-inventory-v14.json) were
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
prior accepted receipts remain unchanged. [Local evidence](../../experiments/E009-competitive-benchmark/local-failed-paths-v14.json)
records actual paths, platform substitutions, preserved negative packets, timings,
immutable returns and Linux omissions. Final53 regressions/docs checks pass.

## Retained storage/startup lessons from the UCloud recovery

Archived from AGENTS.md on 2026-10-14. These preserve the failure-specific
reasoning; they do not require snapshots or old UCloud paths on a healthy GCP VM.
The v14 return is now independently accepted in E009/linux-preflight-v14.json.

For repeated native startup hangs, capture evidence inside the child (including
before Python site initialization) and process wait state, not only a parent
timeout traceback. Do not bypass a failed probe or raise its timeout and call
that a root-cause repair. Prior successful execution does not establish current
runtime health; retain explicit unresolved status until evidence identifies it.
When retained traces establish forward progress through cold persistent-file reads,
correct a prematurely short startup budget prospectively, with an absolute clock
and an idle-progress limit. Distinguish that wrapper correction from repairing
filesystem latency or accepting an uncompleted runtime probe.
If that bounded correction still spends mostly wall time waiting on persistent
files, stop repeating the full allocation and change the observed read path in
a cheap native recovery. Python -B forbids bytecode writes, not reads; source-cache
isolation needs explicit -X flags under -I, verified child propagation and no
scientific-setting changes. Keep failed attempts and distinguish a locally repaired
cache-loader reproduction from actual storage/runtime acceptance.

For long owner-run preparation, prefer progress-aware stall detection and one
explicit owner-selected overall cost ceiling over arbitrary short per-stage wall
caps. Completed bytes/files/checkpoints are progress; parent heartbeats alone are
not. Justify stall intervals and any hard ceilings from retained workload/rate,
allocation and uncertainty, including copy, verification and packing. Test the
observed workload cardinality and recovery path, not just a smaller convenient
fixture. Local throughput remains distinct from native performance. Persist
checksum-bound completed work across job resets where useful; make resume reject
source/config/output drift and ignore unsealed partials without deleting them.
Before handoff, reconcile every nested timeout with the advertised command budget.

When changing an observed storage execution path, distinguish one-time materialization
from repeated native imports. Bind snapshot bytes and internal links, retain a
reusable artifact, and validate interpreter, library origins and actual numerical
operations before admission. CPU-capped I/O concurrency may overlap storage
latency; it does not authorize extra numerical workers or silent relocation.

D006's old E001 job-local-copy exception is historical provenance; it does not
authorize relocating old prefixes onto GCP. Recreate complete independently owned
compatible runtimes from accepted version/source records where inaccessible bases
prevent reuse. Linux compatibility must be tested on the new host when relevant;
accepted scientific stages stay accepted and are not replayed merely to migrate.

Isolate Python processes inside tool environments: unset inherited `PYTHONPATH`, `PYTHONHOME` and `PYTHONUSERBASE`, and set `PYTHONNOUSERSITE=1` before installs, inventories and execution. UCloud's user-site packages were observed inside otherwise separate conda environments; distinct environment directories alone do not establish import isolation. Preserve required tool-local source imports, and verify package origins when introducing a runtime. Cross-experiment reuse must be read-only and validate a full distribution inventory and import origins against a clean, hash-identified prefix record; a `pip freeze` alone may include user-site entries or direct references. A new package-only venv may explicitly borrow reviewed dependencies read-only, with its own installed wheel and byte-bound before/after checks. Scope byte verification to the actual execution contract: accepted sealed runtime members need no repeated whole-prefix hash, and explicit external source/binary/model inputs can be bound before/after. Do not recursively hash unused tests, headers or unrelated databases merely to demonstrate non-mutation. Label the verification scope honestly; this is not proof that every file in a prefix stayed unchanged. Expose real file/byte progress for substantial verification. Record the dependency/base-prefix relationship, exclude the old package and path-injecting overlays, and never transfer such links as a portable environment or remove their required base. For all Python children using a reused environment, including scientific rules, pass `-B` on the Python command line to prevent `.pyc` writes: `-I` implies `-E` and ignores `PYTHONDONTWRITEBYTECODE`. Do not modify an already executed/transferred snapshot in place; use explicit wrappers or a new versioned transfer.


## Superseded two-depth resource protocol

The following 2026-10-09 prospective resources/paths were archived on 2026-10-14.
The old 700 allocated core-hours and 1,980 UCloud balance are not GCP credits.
They are ceilings/planning history, not evidence of expenditure or authorization.

```json
{
  "resources": {
    "stage_budgets": [
      {
        "stage": "asset_setup_native_preflight",
        "allocated_vcpus": 8,
        "allocated_ram_gb": 24,
        "hours_ceiling": 5,
        "allocated_core_hours_ceiling": 40
      },
      {
        "stage": "assembly_mapping_source_truth",
        "allocated_vcpus": 16,
        "allocated_ram_gb": 48,
        "hours_ceiling": 6,
        "allocated_core_hours_ceiling": 96
      },
      {
        "stage": "primary_product_and_bounded_diagnostic_controls",
        "allocated_vcpus": 16,
        "allocated_ram_gb": 48,
        "hours_ceiling": 3,
        "allocated_core_hours_ceiling": 48,
        "diagnostic_core_hours_ceiling": 16
      },
      {
        "stage": "semibin2",
        "allocated_vcpus": 16,
        "allocated_ram_gb": 48,
        "hours_ceiling": 2,
        "allocated_core_hours_ceiling": 32
      },
      {
        "stage": "metacat_core",
        "allocated_vcpus": 16,
        "allocated_ram_gb": 48,
        "hours_ceiling": 2,
        "allocated_core_hours_ceiling": 32
      },
      {
        "stage": "scgbinner_native",
        "allocated_vcpus": 16,
        "allocated_ram_gb": 48,
        "hours_ceiling": 6,
        "allocated_core_hours_ceiling": 96
      },
      {
        "stage": "completebin_modified_max50",
        "allocated_vcpus": 16,
        "allocated_ram_gb": 48,
        "hours_ceiling": 6,
        "allocated_core_hours_ceiling": 96
      },
      {
        "stage": "comebin_native_grid",
        "allocated_vcpus": 16,
        "allocated_ram_gb": 48,
        "hours_ceiling": 12,
        "allocated_core_hours_ceiling": 192
      },
      {
        "stage": "evaluation_diagnostics",
        "allocated_vcpus": 16,
        "allocated_ram_gb": 48,
        "hours_ceiling": 2,
        "allocated_core_hours_ceiling": 32
      }
    ],
    "stage_sum_core_hours": 664,
    "reserve_core_hours": 36,
    "total_allocated_core_hours_ceiling": 700,
    "includes_failed_attempts_setup_download_collection": true,
    "remaining_owner_credits": 1980,
    "preflight_working_rss_bytes_ceiling": 20000000000,
    "science_working_rss_bytes_ceiling": 40000000000,
    "max_concurrent_tools": 1,
    "eligible_contig_scale_stop": 100000,
    "assembly_bp_scale_stop": 600000000,
    "local_checks": {
      "threads": 4,
      "loader": 0,
      "rss_bytes": 8000000000,
      "seconds": 7200,
      "fixture_contigs": 32,
      "fixture_bp": 600000
    },
    "estimates_are_not_measurements": true,
    "auto_increase_or_retry": false,
    "balance_date": "2026-10-09 owner approximately",
    "headroom_core_hours": 1280,
    "storage": {
      "provisioning_estimate_gb": 200,
      "hard_experiment_cap": false,
      "home_capacity_owner_gb": [
        50,
        100
      ],
      "shared_capacity_owner_tb": [
        8,
        10
      ],
      "home_contents": "code, versioned environments, transfers, logs, compact evidence",
      "shared_contents": "own e009 subtree: reads, source references, BAM/SAM and heavy temporary/native products",
      "free_space_checked_before_writes": true
    }
  },
  "owner_paths": {
    "root": "/work/Home/dl_binner/e009/",
    "transfer": "/work/Home/dl_binner/e009/transfer/",
    "data_heavy_destination": "/work/RasmusAlles\u00f8eNielsen#2936/dl_binner/e009/"
  },
  "depth_samples": [
    0,
    1
  ]
}
```

## Superseded mandatory comparison planning, 2026-10-14

The following E009 README text at `5fec4e1` preserved the older two-depth control
wording and UCloud allocation-hour reservations. It is historical planning, not
a current GCP budget or an authorized tool schedule. The later owner clarification
changes E009 to reusable data and selectively justified improvement evidence;
CompleteBin/COMEBin/SCGBinner full runs are deferred. Current [D013](../decisions/D013-first-comparative-benchmark.md)
and [operations](../../experiments/E009-competitive-benchmark/OPERATIONS.md) own that scope.

## Question and informative comparisons

How useful are our accepted raw and learned bins on a real read-derived
human-associated assembly, compared with a small native-tool shortlist, and
does the main deficit concern information, learned geometry or grouping?
No prior result establishes a globally poor or strong binner. Measure the gap.

Freeze our stable main source at `5e54538d1799e8d2538621729400f33fbaf017b9`
(dev3; normal prototype merge `5bc824a9bf4b1ca4562acda10735a3fc6b54dc3d`).
No model, fitted-transform procedure, training default or clusterer changes.
Run one seed-11 target-specific fit with its matched raw control for each of:

- TNF plus the same two explicitly observed mean-depth columns: primary product pair.
- TNF alone: matched secondary pair, isolating the value of added depth within
  our product. Absent depth is not fabricated zeros. These are diagnostic controls,
  not product alternatives or a gate on learning/depth. Their cost is reported
  separately and capped at 24 allocated core-hours within the 48-core-hour product budget.

All four partitions retain the same complete input DNA, exclusions/masks and
unassigned outcomes. Raw versus learned isolates the learning pipeline under
fixed inputs/geometry/clustering, including its saved transforms; it is not a
controlled comparison of every embedding normalization decision. Depth versus
sequence changes the declared information contract, keeping scientific defaults.

External shortlist: **SemiBin2 short-read self-supervised, MetaCAT core CPU,
SCGBinner, COMEBin native full 120-candidate grid** and **CompleteBin modified
max-50**, subject to Linux and actual-scale affordability admission before fits.
One configuration/attempt per tool. Preserve native schedules/eligibility/selection
except the explicitly named CompleteBin cap. No replacement list or automatic retry.

COMEBin's successful E001 stages cost 39.6462 allocated core-hours (known recovery
sequence lower bound 58.1075), with high seed-11 R95; a whole-tool comparison on
this same new assembly is valuable despite mechanism overlap. Those results and
failed attempts remain accepted, with no replay. Reserve 192 hours for its new
native run/grid; this is a conservative cap, not a size-scaled runtime forecast.

CompleteBin's current data-dependent schedule uses a 115,000 effective-contig
threshold, base 35 epochs (39 at N50 ≥1536), and can otherwise reach 200 epochs.
The isolated E009 source changes only that maximum to **50**. Training loops over
resolved epochs; it does not stop on validation-loss stabilization. The separate
150-epoch extreme-overfit safety valve cannot increase our 50 cap. Automatic
pretraining decisions use the capped epoch count, so this modification can also
change that decision; retain the outcome. Leiden's adaptive convergence is a
separate stop. This is a modified configuration, **not upstream parity**.

DCVBin's official 1.657-GB continued-pretraining payload is available. Its actual
basic wrapper selects one BAM, constructs `VAE(nsamples=1)` with unconditional
CUDA and 200 epochs; the encoder alone has a CPU fallback and a 5,000-token cap,
with ≥2-kb eligibility. The enhanced source also calls CUDA directly. A tested
CPU/multi-depth/continued-pretraining adaptation would be substantial extra tool
implementation, so **DCVBin is excluded from E009**, rather than treating coverage
as a disadvantage or claiming its weights are missing. LorBin remains deferred
for long-read/model contracts. See the [targeted reconciliation](../../docs/evidence/2026-10-09-e009-contract-reconciliation.md)
and [asset inspection](../../docs/evidence/2026-10-09-e009-asset-inspection.json).
