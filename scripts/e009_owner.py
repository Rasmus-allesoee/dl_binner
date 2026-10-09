#!/usr/bin/env python3
"""Checksum-bound owner-controlled E009 asset/native preflight, never community fits.

Reuses reviewed E001 mapping/AMBER/numerical prefixes read-only. Five fresh,
version-qualified package-only venvs borrow explicitly bound numerical libraries;
their tool source is owned by E009. New assembler/utilities have a distinct prefix.
Bulk source DNA stays in the project's own shared-storage subtree. All parent
verification, acquisition, setup and children share the five-hour ceiling.
"""
import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import resource
import shutil
import shlex
import signal
import sys
import tarfile
import tempfile
import time
import traceback
sys.path.insert(0,str(Path(__file__).absolute().parent))

from e009_common import acquire, binding, extract, tree_binding, write_json
from e009_native import command_plan, patch_completebin, patch_scgbinner

BUNDLE=Path(__file__).absolute().parents[1]
EXP='experiments/E009-competitive-benchmark'


def supervisor():
    """Load the exact accepted stdlib process supervisor without importing a package."""
    path=BUNDLE/'payload/supervision.py'
    if not path.exists():path=BUNDLE/'src/dl_binner/supervision.py'
    spec=importlib.util.spec_from_file_location('e009_supervision',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def verify_bundle(folder):
    """Verify every submitted byte and exact file set; reject links/extras before work."""
    folder=Path(folder);manifest=json.loads((folder/'bundle-manifest.json').read_text())
    files=set()
    for p in folder.rglob('*'):
        if p.is_symlink():raise ValueError('Packet symlink refused')
        if p.is_file() and p!=folder/'bundle-manifest.json':files.add(str(p.relative_to(folder)))
    if files!=set(manifest['files']):raise ValueError('Packet file set changed')
    for name,expected in manifest['files'].items():
        p=folder/name
        if '..' in Path(name).parts or Path(name).is_absolute() or binding(p)!=expected:
            raise ValueError('Packet path/bytes changed: '+name)
    return manifest


class Tee:
    """Mirror driver messages into the closed return snapshot and owner terminal."""
    def __init__(self,terminal,log):self.terminal,self.log=terminal,log
    def write(self,value):self.terminal.write(value);self.log.write(value);self.flush()
    def flush(self):self.terminal.flush();self.log.flush()


def link_dependencies(source,destination):
    """Link reviewed dependency files, excluding old binners and all path-injecting .pth."""
    excluded={'COMEBin','SCGBinner','SemiBin','CompleteBin','MetaCAT','dl_binner','__pycache__'}
    links={}
    for p in sorted(Path(source).iterdir()):
        if p.name in excluded or p.suffix=='.pth' or p.name=='.DS_Store' or p.name.startswith(('dl_binner-','COMEBin-','SCGBinner-','SemiBin-','CompleteBin-','MetaCAT-')):continue
        target=Path(destination)/p.name
        if target.exists() or target.is_symlink():raise ValueError('New dependency site is not fresh')
        target.symlink_to(p.absolute(),target_is_directory=p.is_dir());links[p.name]=str(p.absolute())
    return links


def collect(attempt,transfer):
    """Return compact immutable evidence and its inventory, including a terminal snapshot.

    Bulk sources/prefixes/cache are external and receipt-bound. Do not stat an open
    log after collection and call it archived storage. The archive checksum binds
    the precise captured log bytes; collection receipt accounts after-return wall.
    """
    paths=[p for p in sorted(attempt.rglob('*')) if p.is_file() and not p.is_symlink()
           and not any(x in ('source-cache','sources','payload-cache','temporary','bootstrap') for x in p.relative_to(attempt).parts)
           and p.suffix not in ('.bam','.sam','.bai')]
    files={str(p.relative_to(attempt)):binding(p) for p in paths if p.name!='terminal.log'}
    write_json(attempt/'retained-files.json',{'files':files,'terminal_scope':'exact immutable archive snapshot; excluded from its own live inventory'})
    paths.append(attempt/'retained-files.json');archive=transfer/(attempt.name+'-return.tar.gz');size=0
    with archive.open('xb') as stream,tarfile.open(fileobj=stream,mode='w:gz') as tar:
        for p in paths:
            member=tar.gettarinfo(p,arcname=attempt.name+'/'+str(p.relative_to(attempt)))
            with p.open('rb') as src:tar.addfile(member,src)
            size+=member.size
    checksum=archive.with_name(archive.name+'.sha256')
    with checksum.open('x') as out:out.write(binding(archive)['sha256']+'  '+archive.name+'\n')
    print('RETURN_ARCHIVE='+str(archive)+'\nRETURN_CHECKSUM='+str(checksum),flush=True)
    return {'archive':str(archive),'file':binding(archive),'checksum':str(checksum),'retained_logical_bytes':size,'members':len(paths)}


def storage_snapshot(root):
    """Report experiment-owned filesystem storage separately from immutable returns.

    Never follow dependency-directory links or count their targets as owned bytes.
    Deduplicate hard links for physical-block estimates; filesystem block reports
    are approximate. This precollection snapshot may include a live terminal log.
    """
    logical=physical=files=links=0;seen=set()
    for path in Path(root).rglob('*'):
        if path.is_symlink():links+=1;continue
        if not path.is_file():continue
        stat=path.stat();files+=1;logical+=stat.st_size
        identity=(stat.st_dev,stat.st_ino)
        if identity not in seen:physical+=stat.st_blocks*512;seen.add(identity)
    return {'files':files,'links_excluding_targets':links,'logical_file_bytes':logical,
            'unique_inode_physical_bytes_estimate':physical,
            'scope':'owned filesystem snapshot before collection, distinct from exact archive-member retained bytes'}


def execute(args,attempt,started):
    """Perform only prospective asset acquisition and real tiny native contracts."""
    limits=json.loads((BUNDLE/EXP/'preflight.json').read_text());sup=supervisor()
    local=json.loads(args.local_runtimes.read_text()) if args.local_runtimes else None
    os.chdir(attempt)  # Keep incidental native files within this unique owned attempt.
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    if not local:
        if (args.allocated_vcpus,args.allocated_ram_gb)!=(8,24):raise ValueError('Frozen owner allocation is 8 vCPU / 24 GB')
        if platform.system()!='Linux' or platform.machine()!='x86_64':raise ValueError('Native Linux x86_64 required')
        if platform.libc_ver()[0]!='glibc' or tuple(map(int,platform.libc_ver()[1].split('.')[:2]))<(2,28):
            raise ValueError('Pinned native utility/wheel recipe needs glibc >=2.28')
        cpus=sorted(os.sched_getaffinity(0))
        if len(cpus)<8:raise ValueError('Affinity smaller than owner allocation')
        os.sched_setaffinity(0,cpus[:8])
    elif args.allocated_vcpus>4 or args.allocated_ram_gb>8:
        raise ValueError('Local harness is bounded at four CPU threads / 8 GB working RAM')
    deadline=started+(args.local_seconds or limits['work_seconds_ceiling'] if local else limits['work_seconds_ceiling'])
    env=sup.isolated_env(args.allocated_vcpus)
    for key in ('CONDA_PREFIX','CONDA_DEFAULT_ENV','CONDA_PROMPT_MODIFIER','CONDA_PYTHON_EXE','PERL5LIB','PERL_LOCAL_LIB_ROOT','PERL_MB_OPT','PERL_MM_OPT'):
        env.pop(key,None)
    env.update(TMPDIR=tempfile.mkdtemp(prefix='e009-',dir='/tmp'),CUDA_VISIBLE_DEVICES='',
               MPLCONFIGDIR=str(attempt/'mpl-cache'),XDG_CACHE_HOME=str(attempt/'cache'),
               TORCH_HOME=str(attempt/'cache/torch'),HF_HOME=str(attempt/'cache/huggingface'),
               PIP_DISABLE_PIP_VERSION_CHECK='1',PYTHONHASHSEED='0')
    stages=attempt/'stages';stages.mkdir();results={}
    def stage(argv,name,seconds=1200,stage_env=None):
        remaining=deadline-time.monotonic()
        if remaining<=0:raise TimeoutError('Whole preflight work ceiling reached')
        sup.progress('E009 stage '+name)
        return sup.supervise(argv,stages/(name+'.log'),min(seconds,remaining),
                             8_000_000_000 if local else limits['working_rss_bytes'],stage_env or env,sample_root=os.getpid())
    inputs=BUNDLE/'input'
    if local:
        # Real production workers; only remote platform/assets/setup are replaced.
        stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_contracts.py','--inputs',inputs,'--output',attempt/'portable',
               '--threads',str(args.allocated_vcpus),'--mapping-bin',local['mapping_bin'],
               '--minimap2',local['minimap2'],'--megahit',local['megahit'],
               '--assembly-threads',str(local.get('assembly_threads',args.allocated_vcpus))],'portable-real-native',120)
        return {'status':'passed','native_linux':False,'scope':'Mac real adapters/owner harness; remote setup and other tool runtimes unexecuted'}
    if args.root!=Path('/work/Home/dl_binner/e009'):raise ValueError('Owner Home root differs from frozen E009 root')
    if args.shared_root!=Path('/work/RasmusAllesøeNielsen#2936/dl_binner/e009') or not args.shared_root.parent.is_dir() or args.shared_root.is_symlink():
        raise ValueError('Mount the project shared-storage directory; only its e009 child is written')
    if shutil.disk_usage(args.root).free<limits['home_free_bytes_min']:raise ValueError('Insufficient Home free space for bounded new prefixes/evidence')
    args.shared_root.mkdir(exist_ok=True)
    if shutil.disk_usage(args.shared_root).free<limits['shared_free_bytes_min']:raise ValueError('Insufficient shared space for source acquisition')
    lock=json.loads((BUNDLE/EXP/'native-lock.json').read_text());baseline=json.loads((BUNDLE/EXP/'runtime-baseline.json').read_text())
    base=Path(baseline['comebin_dependencies']['prefix']);basepython=base/'bin/python';mapping=Path(baseline['mapping']['prefix'])
    checkm_data=base/'checkm_data';env['CHECKM_DATA_PATH']=str(checkm_data)
    for name,digest in baseline['checkm_payloads'].items():
        if binding(checkm_data/name)['sha256']!=digest:raise ValueError('Accepted CheckM marker payload changed: '+name)
    # Full distribution inventory/origins, then all-byte before/after bindings.
    stage([basepython,'-I','-B',BUNDLE/'scripts/e009_native.py','--inventory-prefix',base,
           '--expected-freeze',BUNDLE/baseline['comebin_dependencies']['freeze_path'],
           '--modules','numpy','torch','pandas','scipy','sklearn','pysam','Bio','hnswlib','igraph','leidenalg'],'readonly-comebin-base-probe',90)
    inv=json.loads(next(l.split('=',1)[1] for l in (stages/'readonly-comebin-base-probe.log').read_text().splitlines() if l.startswith('INVENTORY_JSON=')))
    if inv['python'].split()[0]!=baseline['comebin_dependencies']['python_version']:raise ValueError('Accepted base Python version changed')
    site=base/'lib'/('python'+'.'.join(inv['python'].split()[0].split('.')[:2]))/'site-packages'
    amber=Path(baseline['amber']['prefix']);amber_source=Path(baseline['amber']['source'])
    for name,digest in baseline['amber_source_files'].items():
        if binding(amber_source/name)['sha256']!=digest:raise ValueError('Accepted AMBER source changed: '+name)
    expected_amber=attempt/'amber-expected-inventory.json'
    write_json(expected_amber,baseline['amber']['lock_reconciliation']['verified_prefix_inventory']['distributions'])
    stage([amber/'bin/python','-I','-B',BUNDLE/'scripts/e009_native.py','--inventory-prefix',amber,
           '--expected-distributions',expected_amber,'--modules','numpy','pandas','matplotlib','Bio'],
          'readonly-amber-probe',90)
    bindings={'numerical':tree_binding(site),'mapping':tree_binding(mapping),
              'amber':tree_binding(amber),'amber_source':tree_binding(amber_source),
              'checkm_data':tree_binding(checkm_data),'base_executables':tree_binding(base/'bin')}
    write_json(attempt/'readonly-before.json',bindings)
    try:
        for tool,argv in [('strobealign',['--version']),('samtools',['--version'])]:
            stage([mapping/'bin'/tool,*argv],tool+'-version',30)
            if baseline['mapping']['versions'][tool] not in (stages/(tool+'-version.log')).read_text():raise ValueError('Accepted mapping version changed')
        cache=args.root/'cache';cache.mkdir(exist_ok=True);source_cache=cache/'sources';source_cache.mkdir(exist_ok=True)
        sources={}
        for name,spec in lock['sources'].items():
            archive=source_cache/(name+'-'+spec['sha256'][:12]+'.tar.gz')
            stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_worker.py','acquire','--spec-json',json.dumps({k:spec[k] for k in ('url','bytes','sha256')}),
                   '--destination',archive],'source-'+name,900)
            target=attempt/'sources'/name;extract(archive,target,strip_root=True);sources[name]=target
        patched=patch_completebin(sources['CompleteBin'],lock['completebin_modification']['before_sha256'])
        if patched['after']!=lock['completebin_modification']['after']:raise ValueError('Prepared CompleteBin patch bytes differ')
        write_json(attempt/'completebin-modification.json',patched)
        scgpatch=patch_scgbinner(sources['SCGBinner'],lock['scgbinner_modification']['before_sha256'])
        if scgpatch['after']!=lock['scgbinner_modification']['after']:raise ValueError('Prepared SCGBinner dtype patch bytes differ')
        write_json(attempt/'scgbinner-modification.json',scgpatch)
        dbspec=lock['payloads']['CompleteBin_DB'];dbarchive=cache/'CompleteBin-DB-v1.2.3.3.zip'
        stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_worker.py','acquire','--spec-json',json.dumps({k:dbspec[k] for k in ('url','bytes','sha256')}),
               '--destination',dbarchive],'completebin-database',900)
        db=args.root/'payloads'/('completebin-db-'+dbspec['sha256'][:12])
        if not db.exists():extract(dbarchive,db,strip_root=True)
        for item in dbspec['members']:
            rel=Path(*Path(item['path']).parts[1:])
            if binding(db/rel)!={k:item[k] for k in ('bytes','sha256')}:raise ValueError('CompleteBin database member changed')
        bootstrap=attempt/'bootstrap';extract(BUNDLE/'payload/micromamba-linux.tar.bz2',bootstrap)
        mamba=bootstrap/'bin/micromamba';utility=args.root/'envs'/('utilities-v1-'+attempt.name)
        setupenv=dict(env,MAMBA_ROOT_PREFIX=str(args.root/'mamba'),PIP_CACHE_DIR=str(cache/'pip'))
        explicit=attempt/'utilities-explicit.txt'
        stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_worker.py','acquire-utilities',
               '--lock',BUNDLE/EXP/'utilities-linux-lock.json','--destination',cache/'utilities','--explicit',explicit],
              'utilities-pinned-acquisition',1800)
        stage([mamba,'--no-rc','create','-y','-p',utility,'--offline','--file',explicit],
              'utilities-setup',1800,setupenv)
        stage([mamba,'list','-p',utility,'--explicit'],'utilities-resolved-lock',30,setupenv)
        for tool,argv in [('bedtools',['--version']),('hmmsearch',['-h']),('prodigal',['-v']),('perl',['-v'])]:
            stage([utility/'bin'/tool,*argv],tool+'-prerequisite',30,setupenv)
        stage([str(utility/'bin/make'),'-C',sources['minimap2'],'-j','8','CC='+str(utility/'bin/x86_64-conda-linux-gnu-cc'),
               'CFLAGS=-O2 -I'+str(utility/'include'),
               'LIBS=-L'+str(utility/'lib')+' -Wl,-rpath,'+str(utility/'lib')+' -lm -lz -lpthread'],'minimap2-build',300)
        plan_env=dict(env,PATH=':'.join(map(str,[utility/'bin',base/'bin',mapping/'bin']))+':'+env.get('PATH',''))
        stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_contracts.py','--inputs',inputs,'--output',attempt/'portable',
               '--threads','8','--mapping-bin',mapping/'bin','--minimap2',sources['minimap2']/'minimap2','--megahit',utility/'bin/megahit'],
              'portable-real-native',180,plan_env)
        bams=[attempt/'portable'/f'mapping_{i}'/f'sample_{i}.sorted.bam' for i in (0,1)]
        stage([amber/'bin/python','-I','-B',BUNDLE/'scripts/e009_contracts.py','--inputs',inputs,
               '--output',attempt/'amber-contract','--threads','8','--amber-source',amber_source,
               '--truth',attempt/'portable/truth/truth.json'],'amber-native-contract',90,plan_env)
        own_envs={}
        for tool,name in [('semibin','SemiBin'),('metacat','MetaCAT'),('scgbinner','SCGBinner'),('comebin','COMEBin'),('completebin','CompleteBin')]:
            # Each tool owns its venv; borrowed distributions are explicitly read-only.
            try:
                prefix=args.root/'envs'/(tool+'-source-v1-'+attempt.name)
                stage([basepython,'-I','-B','-m','venv','--without-pip',prefix],tool+'-venv',90)
                newsite=prefix/'lib'/('python'+'.'.join(inv['python'].split()[0].split('.')[:2]))/'site-packages'
                links=link_dependencies(site,newsite);write_json(attempt/(tool+'-dependency-links.json'),{'prefix':str(prefix),'base_prefix':str(base),'links':links})
                python=prefix/'bin/python';own_envs[tool]=str(python)
                wrapper=prefix/'bin/hmmsearch'
                wrapper.write_text('#!/bin/sh\nexec '+shlex.quote(str(python))+' -I -B '+
                    shlex.quote(str(BUNDLE/'scripts/e009_hmm.py'))+' --native '+shlex.quote(str(utility/'bin/hmmsearch'))+' -- "$@"\n')
                wrapper.chmod(0o755)
                if tool=='comebin':
                    checkm_wrapper=prefix/'bin/checkm'
                    checkm_wrapper.write_text('#!/bin/sh\nexec '+shlex.quote(str(python))+' -I -B '+shlex.quote(str(base/'bin/checkm'))+' "$@"\n')
                    checkm_wrapper.chmod(0o755)
                tool_env=dict(plan_env,PATH=str(prefix/'bin')+':'+str(base/'bin')+':'+str(utility/'bin')+':'+str(mapping/'bin')+':'+env.get('PATH',''))
                tool_env['E009_HMM_AUDIT']=str(attempt/(tool+'-hmm-budget.jsonl'))
                # Worker pools use serial BLAS; explicit native torch/HMM/HNSW flags
                # supply their declared phase budgets independently.
                for key in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):tool_env[key]='1'
                expected={d['name']:d['version'] for d in inv['distributions'] if not d['name'].lower().startswith(('dl-binner','comebin','scgbinner','semibin','completebin','metacat'))}
                for dependency in lock['per_tool_owned_dependencies'][tool]:
                    spec=lock['dependency_wheels'][dependency];wheel=cache/spec['filename']
                    if dependency in expected:raise ValueError('Owned extra would overwrite a borrowed distribution')
                    stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_worker.py','acquire','--spec-json',
                           json.dumps({k:spec[k] for k in ('url','bytes','sha256')}),'--destination',wheel],tool+'-'+dependency+'-wheel',120)
                    stage([python,'-I','-B','-m','pip','install','--no-deps','--no-compile','--no-index',wheel],tool+'-'+dependency+'-install',90,tool_env)
                    expected[dependency]=spec['version']
                expectedfile=attempt/(tool+'-expected-inventory.json');write_json(expectedfile,expected)
                stage([python,'-I','-B',BUNDLE/'scripts/e009_native.py','--inventory-prefix',prefix,'--dependency-prefix',base,
                       '--expected-distributions',expectedfile,'--modules','numpy','pandas','scipy','sklearn'],tool+'-isolated-probe',90,tool_env)
                plan=command_plan(tool,sources[name],inputs/'assembly.fna',bams,attempt/(tool+'-native'),8,db)
                write_json(attempt/(tool+'-command-plan.json'),plan)
                stage([python,'-I','-B',BUNDLE/'scripts/e009_worker.py','tool-contract','--tool',tool,'--source',sources[name],
                       '--inputs',inputs,'--bams',*bams,'--output',attempt/(tool+'-contract'),'--db',db,'--threads','8'],tool+'-native-contract',1200,tool_env)
                results[tool]={'status':'passed','python':str(python),'full_community_schedule':'not executed or admitted'}
                write_json(attempt/(tool+'-status.json'),results[tool])
            except Exception as error:
                results[tool]={'status':'failed','error':repr(error),'dependent_stages_skipped':True}
                write_json(attempt/(tool+'-failure.json'),results[tool]);print('TOOL_CONTRACT_FAILURE='+json.dumps(results[tool]),flush=True)
                # Another isolated tool may proceed; no failed tool is fitted/retried.
        write_json(attempt/'native-contract-status.json',results)
        # Source acquisition is separate from inputs/training; no bulk reads here.
        data=args.shared_root/'source-preflight-v1';data.mkdir(exist_ok=True)
        spec=lock['payloads']['source_genomes'];sourcearchive=data/'source_genomes.tar.gz'
        stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_worker.py','acquire','--spec-json',json.dumps(spec),'--destination',sourcearchive],
              'source-genome-acquisition',1800)
        sourcefolder=data/('unpacked-'+binding(sourcearchive)['sha256'][:12])
        if not sourcefolder.exists():extract(sourcearchive,sourcefolder,max_bytes=50_000_000_000)
        stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_worker.py','source-catalog','--source',sourcefolder,
               '--development',BUNDLE/EXP/'development-overlap.json','--output',attempt/'source-catalog.json'],'source-overlap-catalog',1800)
        write_json(attempt/'source-acquisition.json',{'archive':str(sourcearchive),'file':binding(sourcearchive),'shared_source_folder':str(sourcefolder),
                   'source_catalog':binding(attempt/'source-catalog.json'),'admitted_scientific_input':False})
    finally:
        after={'numerical':tree_binding(site),'mapping':tree_binding(mapping),
               'amber':tree_binding(amber),'amber_source':tree_binding(amber_source),
               'checkm_data':tree_binding(checkm_data),'base_executables':tree_binding(base/'bin')}
        write_json(attempt/'readonly-after.json',{'bindings':after,'unchanged':after==bindings})
        if after!=bindings:raise ValueError('Read-only dependency bytes changed; preserve evidence')
    failed=[t for t,v in results.items() if v['status']!='passed']
    return {'status':'failed' if failed else 'passed','native_linux':True,'tools':results,'failed_tools':failed,
            'scope':'asset/source-overlap and tiny native CPU contracts only; no full-community fits or E009 scores',
            'scientific_execution_admitted':False,'read_payload_sha256s':'pending later bulk acquisition before assembly',
            'remaining_contracts':'source taxonomy/replicon roles, source overlap interpretation, assembly scale and full-schedule measured affordability'}


def main():
    """Capture failures even before a child, preserve the manifest and return evidence."""
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True);p.add_argument('--shared-root',type=Path,required=True)
    p.add_argument('--allocated-vcpus',type=int,required=True);p.add_argument('--allocated-ram-gb',type=int,required=True)
    p.add_argument('--entry-start-epoch',type=float);p.add_argument('--local-runtimes',type=Path)
    p.add_argument('--local-seconds',type=float)
    args=p.parse_args()
    if args.local_seconds is not None and (not args.local_runtimes or not math.isfinite(args.local_seconds) or not 0<args.local_seconds<=7200):
        p.error('--local-seconds is only a positive <=7200-second local-harness limit')
    if args.allocated_vcpus<=0 or args.allocated_ram_gb<=0:p.error('Allocation values must be positive')
    if not args.root.is_absolute() or not args.shared_root.is_absolute() or args.root.is_symlink():p.error('Explicit absolute owned unlinked paths required')
    args.root.mkdir(parents=True,exist_ok=True);transfer=args.root/'transfer';transfer.mkdir(exist_ok=True)
    attempt=Path(tempfile.mkdtemp(prefix='native-preflight-',dir=args.root));started=time.monotonic()-max(0,time.time()-(args.entry_start_epoch or time.time()))
    status={'status':'failed','verification_passed':False};code=1;original=sys.stdout,sys.stderr
    def alarm(signum,frame):raise TimeoutError('Overall E009 preflight ceiling reached')
    old_handlers={s:signal.getsignal(s) for s in (signal.SIGALRM,signal.SIGINT,signal.SIGTERM)}
    signal.signal(signal.SIGALRM,alarm)
    def cancel(signum,frame):raise KeyboardInterrupt('Owner cancelled signal '+str(signum))
    signal.signal(signal.SIGINT,cancel);signal.signal(signal.SIGTERM,cancel)
    with (attempt/'terminal.log').open('x') as log:
        sys.stdout,sys.stderr=Tee(original[0],log),Tee(original[1],log)
        try:
            signal.setitimer(signal.ITIMER_REAL,max(.001,(args.local_seconds or 17400)-(time.monotonic()-started)))
            shutil.copyfile(BUNDLE/'bundle-manifest.json',attempt/'bundle-manifest.json')
            manifest=verify_bundle(BUNDLE);status['verification_passed']=True
            write_json(attempt/'verification.json',{'passed':True,'source_commit':manifest['source_commit']})
            status=execute(args,attempt,started);status['verification_passed']=True
            code=0 if status['status']=='passed' else 1
        except BaseException as error:
            status.update(error=repr(error));traceback.print_exc()
        finally:
            signal.setitimer(signal.ITIMER_REAL,0)
            try:
                signal.setitimer(signal.ITIMER_REAL,30)
                write_json(attempt/'storage-before-collection.json',{'home':storage_snapshot(args.root),
                    'shared':storage_snapshot(args.shared_root) if args.shared_root.is_dir() else None})
            except BaseException as error:print('STORAGE_SNAPSHOT_UNAVAILABLE='+repr(error),flush=True)
            signal.setitimer(signal.ITIMER_REAL,0)
            elapsed=time.monotonic()-started
            status.update(exit_code=code,allocated_vcpus=args.allocated_vcpus,allocated_ram_gb=args.allocated_ram_gb,
                          seconds_before_collection=elapsed,allocated_core_hours_before_collection=args.allocated_vcpus*elapsed/3600,
                          accounting='declared allocation times entry-to-driver wall; includes setup/failures; excludes owner idle/upload')
            write_json(attempt/'status.json',status);print('PREFLIGHT_STATUS='+json.dumps(status),flush=True)
            try:
                remaining=(args.local_seconds or 18000)-(time.monotonic()-started)
                signal.setitimer(signal.ITIMER_REAL,min(600,remaining) if remaining>0 else 120)
                result=collect(attempt,transfer);elapsed=time.monotonic()-started
                result.update(seconds_through_collection=elapsed,allocated_core_hours_through_collection=args.allocated_vcpus*elapsed/3600)
                result['collection_after_execution_timeout']=remaining<=0
                write_json(transfer/(attempt.name+'-collection.json'),result)
            except BaseException:traceback.print_exc();code=1
            signal.setitimer(signal.ITIMER_REAL,0)
            for sig,handler in old_handlers.items():signal.signal(sig,handler)
            sys.stdout,sys.stderr=original
    return code


if __name__=='__main__':raise SystemExit(main())
