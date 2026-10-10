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

from e009_common import acquire, binding, extract, write_json
from e009_native import command_plan, patch_completebin, patch_scgbinner
from e009_startup import startup_argv,supervise_startup,source_cache_argv,supervise_work,supervise_activity

BUNDLE=Path(__file__).absolute().parents[1]
EXP='experiments/E009-competitive-benchmark'


def supervisor():
    """Load the exact accepted stdlib process supervisor without importing a package."""
    path=BUNDLE/'payload/supervision.py'
    if not path.exists():path=BUNDLE/'src/dl_binner/supervision.py'
    spec=importlib.util.spec_from_file_location('e009_supervision',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def run_stage(sup,argv,log,seconds,remaining,ram_bytes,env,limits,sample_root=None):
    """Dispatch actual owner stages with one clock and cold-import progress policy.

    Inventory argv must retain lexical Python -I -B and all original arguments.
    Extend only its total startup allowance; unchanged progress, fatal tracebacks,
    RAM and the caller's remaining overall work time remain bounded. Other stages
    use the accepted supervisor unchanged.
    """
    if remaining<=0:raise TimeoutError('Whole preflight work ceiling reached')
    if '--inventory-prefix' in list(map(str,argv)):
        if list(map(str,argv[1:3]))!=['-I','-B']:
            raise ValueError('Inventory stage needs lexical Python -I -B')
        argv=startup_argv(argv[0],argv[3],argv[4:],env=env)
        return supervise_startup(sup,argv,log,min(limits['startup_probe_seconds'],remaining),
            ram_bytes,env,sample_root=sample_root,idle_seconds=limits['startup_idle_seconds'])
    if '--accepted-record' in list(map(str,argv)):
        return supervise_work(sup,source_cache_argv(argv,env),log,remaining,ram_bytes,env,
            sample_root=sample_root,idle_seconds=limits['startup_idle_seconds'])
    if limits.get('native_activity'):
        return supervise_activity(sup,source_cache_argv(argv,env),log,remaining,ram_bytes,env,
            sample_root=sample_root,idle_seconds=limits['startup_idle_seconds'])
    if limits.get('materialization_progress'):
        return supervise_work(sup,source_cache_argv(argv,env),log,remaining,ram_bytes,env,
            sample_root=sample_root,idle_seconds=limits['startup_idle_seconds'])
    return sup.supervise(source_cache_argv(argv,env),log,min(seconds,remaining),ram_bytes,env,sample_root=sample_root)


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


def restored_runtime(accepted_path,attempt,env,stage):
    """Consume an accepted chunk set and probe its new lexical path, without recopy.

    Full package/arithmetic acceptance comes from the reviewed v8 return. This
    per-job entry verifies restored bytes plus interpreter/stdlib identity, and
    returns the accepted distribution table for explicit new tool bindings.
    """
    accepted=json.loads(Path(accepted_path).read_text());base=Path(env['TMPDIR'])/'numerical-runtime'
    stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_materialize.py','--accepted-record',accepted_path,
           '--destination',base,'--summary',attempt/'accepted-restore.json'],'accepted-runtime-restore')
    env['LD_LIBRARY_PATH']=str(base/'lib')
    stage([base/'bin/python','-I','-B','-c',
        'import sys,sysconfig,json;from pathlib import Path;'
        'assert Path(sys.prefix)==Path(sys.argv[1]);'
        'assert sys.version.split()[0]==sys.argv[2];'
        'assert Path(sysconfig.get_path("stdlib")).is_relative_to(Path(sys.argv[1]));'
        'print(json.dumps({"prefix":sys.prefix,"python":sys.version.split()[0]}))',
        base,accepted['numerical_inventory']['python']],'restored-runtime-entry')
    inv={'python':accepted['numerical_inventory']['python'],
         'distributions':[{'name':n,'version':v} for n,v in accepted['numerical_inventory']['distributions'].items()]}
    return base,inv


def tool_environment(base,inv,prefix,stage):
    """Create a new source-only venv bound to the restored numerical runtime.

    Paths deliberately remain lexical. The base lives for this job; old bindings
    and executed environments are never rewritten. Return the precise link map.
    """
    stage([base/'bin/python','-I','-B','-m','venv','--without-pip',prefix],prefix.name+'-venv')
    site=base/'lib'/('python'+'.'.join(inv['python'].split('.')[:2]))/'site-packages'
    newsite=prefix/'lib'/('python'+'.'.join(inv['python'].split('.')[:2]))/'site-packages'
    return link_dependencies(site,newsite)


def python_wrapper(path,python,script,arguments,env):
    """Write a job-bound lexical Python wrapper with isolated source-only imports."""
    argv=[python,'-I','-B','-X','pycache_prefix='+env['E009_SOURCE_CACHE_ROOT'],script,*arguments]
    path=Path(path);path.write_text('#!/bin/sh\nexec '+' '.join(shlex.quote(str(a)) for a in argv)+' "$@"\n')
    path.chmod(0o755)
    return binding(path)


def collect(attempt,transfer,terminal_log=None):
    """Return compact immutable evidence and its inventory, including a terminal snapshot.

    Bulk sources/prefixes/cache are external and receipt-bound. Do not stat an open
    log after collection and call it archived storage. The archive checksum binds
    the precise captured log bytes; collection receipt accounts after-return wall.
    """
    if terminal_log is not None:
        # The live driver terminal is in transfer/. Archive a stable snapshot,
        # rather than statting that live file after collection as retained bytes.
        with Path(terminal_log).open('rb') as source,(attempt/'terminal.log').open('xb') as snapshot:
            shutil.copyfileobj(source,snapshot)
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


def readonly_inputs(baseline):
    """Select only explicit external executables, evaluator sources and marker inputs.

    The numerical runtime is already verified member-by-member during restore.
    This list never traverses an environment or database directory; unused tests,
    headers and unrelated resources are outside its before/after assurance scope.
    """
    original=Path(baseline['comebin_dependencies']['prefix'])
    files={'checkm_entry':original/'bin/checkm'}
    files.update({'mapping/'+name:Path(baseline['mapping']['prefix'])/'bin'/name
                  for name in baseline['mapping']['versions']})
    files.update({'amber_source/'+name:Path(baseline['amber']['source'])/name
                  for name in baseline['amber_source_files']})
    files.update({'checkm_data/'+name:original/'checkm_data'/name
                  for name in baseline['checkm_payloads']})
    expected={'amber_source/'+name:digest for name,digest in baseline['amber_source_files'].items()}
    expected.update({'checkm_data/'+name:digest for name,digest in baseline['checkm_payloads'].items()})
    return files,expected


def bind_readonly_files(files,expected=None):
    """Hash the declared files with visible real-byte progress, never tree enumeration.

    Record lexical and resolved paths so changed symlink targets also fail review.
    Return the precise file table, not a claim that entire prefixes are unchanged.
    The owner-selected overall clock covers these parent-side operations.
    """
    records={}
    for name,path in files.items():
        path=Path(path)
        print('DLBINNER READONLY_FILE begin '+name+' '+str(path),flush=True)
        resolved=path.resolve(strict=True)
        def progress(completed):
            print('DLBINNER WORK_PROGRESS_JSON='+json.dumps(
                {'work_key':'readonly/'+name,'completed_bytes':completed}),flush=True)
        value=binding(resolved,progress=progress)
        if expected and name in expected and value['sha256']!=expected[name]:
            raise ValueError('Accepted read-only input changed: '+name)
        records[name]={'path':str(path),'resolved_path':str(resolved),'file':value}
        print('DLBINNER READONLY_FILE finished '+name,flush=True)
    print('DLBINNER READONLY_FILES finished '+str(len(records))+' explicit files',flush=True)
    return records


def verify_readonly_after(files,before,attempt,work_deadline,overall_deadline):
    """Bound the final explicit-file check even after the work alarm has fired.

    Ordinary verification stays within the work clock. Following a timeout, at
    most the remaining collection reserve can verify these explicit input
    bytes. A blocked/failed check is retained as unverified, never accepted as
    unchanged. Restore any still-live parent alarm when leaving this check.
    """
    started=time.monotonic();previous=signal.getitimer(signal.ITIMER_REAL)
    remaining=work_deadline-started
    seconds=min(remaining,overall_deadline-started) if remaining>0 else overall_deadline-started
    try:
        if seconds<=0:raise TimeoutError('No bounded time remains for read-only verification')
        signal.setitimer(signal.ITIMER_REAL,seconds)
        after=bind_readonly_files(files)
        write_json(attempt/'readonly-after.json',{'bindings':after,'unchanged':after==before,
            'scope':'explicit external files only; no whole-environment mutation claim'})
        if after!=before:raise ValueError('Read-only dependency bytes changed; preserve evidence')
    except BaseException as error:
        write_json(attempt/'readonly-after-failure.json',{'error':repr(error),
                   'unchanged':None,'scope':'final byte verification incomplete or failed; no read-only acceptance'})
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL,max(0,previous[0]-(time.monotonic()-started)) if previous[0] else 0,previous[1])


def execute(args,attempt,started):
    """Perform only prospective asset acquisition and real tiny native contracts."""
    limits=json.loads((BUNDLE/EXP/'preflight.json').read_text());sup=supervisor()
    if args.runtime_recovery_only:
        from e009_cache_recovery import recover
        return recover(args,attempt,started,BUNDLE,sup)
    local=json.loads(args.local_runtimes.read_text()) if args.local_runtimes else None
    if not local and not limits.get('full_native_preflight_enabled',True):
        raise ValueError('Full native preflight is not enabled by this packet; review its current handoff')
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
    deadline=started+(args.local_seconds or args.work_seconds or limits['work_seconds_ceiling'])
    limits.update(startup_probe_seconds=deadline-started,startup_idle_seconds=args.stall_seconds,native_activity=True)
    env=sup.isolated_env(args.allocated_vcpus)
    for key in ('CONDA_PREFIX','CONDA_DEFAULT_ENV','CONDA_PROMPT_MODIFIER','CONDA_PYTHON_EXE','PERL5LIB','PERL_LOCAL_LIB_ROOT','PERL_MB_OPT','PERL_MM_OPT'):
        env.pop(key,None)
    env.update(TMPDIR=tempfile.mkdtemp(prefix='e009-',dir='/tmp'),CUDA_VISIBLE_DEVICES='',
               MPLCONFIGDIR=str(attempt/'mpl-cache'),XDG_CACHE_HOME=str(attempt/'cache'),
               TORCH_HOME=str(attempt/'cache/torch'),HF_HOME=str(attempt/'cache/huggingface'),
               PIP_DISABLE_PIP_VERSION_CHECK='1',PYTHONHASHSEED='0')
    env['E009_SOURCE_CACHE_ROOT']=str(Path(env['TMPDIR'])/'unused-bytecode')
    env['E009_PARENT_DEADLINE']=str(deadline)
    stages=attempt/'stages';stages.mkdir();results={}
    def stage(argv,name,stage_env=None):
        remaining=deadline-time.monotonic()
        if remaining<=0:raise TimeoutError('Whole preflight work ceiling reached')
        sup.progress('E009 stage '+name)
        receipt=run_stage(sup,argv,stages/(name+'.log'),remaining,remaining,
                         8_000_000_000 if local else limits['working_rss_bytes'],
                         stage_env or env,limits,sample_root=os.getpid())
        sup.progress('E009 stage finished '+name+' (exit '+str(receipt['exit_code'])+')')
        return receipt
    inputs=BUNDLE/'input'
    if local:
        # Local accepted-record injection changes only the remote runtime identity.
        # The production restore, lexical venv bindings and inventory run unchanged.
        if local.get('accepted_record'):
            base,inv=restored_runtime(Path(local['accepted_record']),attempt,env,stage)
            prefix=args.root/'envs'/('contract-source-v2-'+attempt.name);prefix.parent.mkdir(exist_ok=True)
            links=tool_environment(base,inv,prefix,stage)
            write_json(attempt/'contract-dependency-links.json',{'prefix':str(prefix),'base_prefix':str(base),'links':links})
            expected=attempt/'contract-expected-inventory.json'
            write_json(expected,{d['name']:d['version'] for d in inv['distributions']})
            stage([prefix/'bin/python','-I','-B',BUNDLE/'scripts/e009_native.py','--inventory-prefix',prefix,
                '--dependency-prefix',base,'--expected-distributions',expected,'--modules','numpy','pandas',
                '--forbidden-prefix',json.loads(Path(local['accepted_record']).read_text())['snapshot']['source_prefix']],
                'contract-restored-venv-probe')
        # Real production workers; only remote platform/assets/setup are replaced.
        stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_contracts.py','--inputs',inputs,'--output',attempt/'portable',
               '--threads',str(args.allocated_vcpus),'--mapping-bin',local['mapping_bin'],
               '--minimap2',local['minimap2'],'--megahit',local['megahit'],
               '--assembly-threads',str(local.get('assembly_threads',args.allocated_vcpus))],'portable-real-native')
        return {'status':'passed','native_linux':False,'scope':'Mac real adapters/owner harness; remote setup and other tool runtimes unexecuted'}
    if args.root!=Path('/work/Home/dl_binner/e009'):raise ValueError('Owner Home root differs from frozen E009 root')
    if args.shared_root!=Path('/work/RasmusAllesøeNielsen#2936/dl_binner/e009') or not args.shared_root.parent.is_dir() or args.shared_root.is_symlink():
        raise ValueError('Mount the project shared-storage directory; only its e009 child is written')
    if shutil.disk_usage(args.root).free<limits['home_free_bytes_min']:raise ValueError('Insufficient Home free space for bounded new prefixes/evidence')
    args.shared_root.mkdir(exist_ok=True)
    if shutil.disk_usage(args.shared_root).free<limits['shared_free_bytes_min']:raise ValueError('Insufficient shared space for source acquisition')
    lock=json.loads((BUNDLE/EXP/'native-lock.json').read_text());baseline=json.loads((BUNDLE/EXP/'runtime-baseline.json').read_text())
    original_base=Path(baseline['comebin_dependencies']['prefix'])
    accepted_path=BUNDLE/EXP/'linux-runtime-recovery-v8.json'
    accepted=json.loads(accepted_path.read_text())
    if accepted['snapshot']['source_prefix']!=str(original_base):raise ValueError('Accepted numerical source differs')
    base,inv=restored_runtime(accepted_path,attempt,env,stage)
    basepython=base/'bin/python';mapping=Path(baseline['mapping']['prefix'])
    site=base/'lib'/('python'+'.'.join(inv['python'].split('.')[:2]))/'site-packages'
    # CheckM's console source and external marker database were intentionally not
    # part of the numerical selection. Bind the tiny source explicitly; do not
    # invoke its old shebang or add the original bin directory to PATH.
    checkm_entry=attempt/'checkm-entry.py';shutil.copyfile(original_base/'bin/checkm',checkm_entry)
    write_json(attempt/'checkm-entry-bound.json',{'source':str(original_base/'bin/checkm'),
        'source_file':binding(original_base/'bin/checkm'),'copy_file':binding(checkm_entry)})
    if binding(checkm_entry)!=binding(original_base/'bin/checkm'):raise ValueError('CheckM entry copy differs')
    checkm_data=original_base/'checkm_data';env['CHECKM_DATA_PATH']=str(checkm_data)
    amber=Path(baseline['amber']['prefix']);amber_source=Path(baseline['amber']['source'])
    readonly_files,expected=readonly_inputs(baseline)
    bindings=bind_readonly_files(readonly_files,expected)
    write_json(attempt/'readonly-before.json',{'bindings':bindings,
        'scope':'explicit external files only; numerical members already verified at restore'})
    expected_amber=attempt/'amber-expected-inventory.json'
    write_json(expected_amber,baseline['amber']['lock_reconciliation']['verified_prefix_inventory']['distributions'])
    stage([amber/'bin/python','-I','-B',BUNDLE/'scripts/e009_native.py','--inventory-prefix',amber,
           '--expected-distributions',expected_amber,'--modules','numpy','pandas','matplotlib','Bio'],
          'readonly-amber-probe',dict(env,LD_LIBRARY_PATH=str(amber/'lib')))
    try:
        for tool,argv in [('strobealign',['--version']),('samtools',['--version'])]:
            stage([mapping/'bin'/tool,*argv],tool+'-version')
            if baseline['mapping']['versions'][tool] not in (stages/(tool+'-version.log')).read_text():raise ValueError('Accepted mapping version changed')
        cache=args.root/'cache';cache.mkdir(exist_ok=True);source_cache=cache/'sources';source_cache.mkdir(exist_ok=True)
        sources={}
        for name,spec in lock['sources'].items():
            archive=source_cache/(name+'-'+spec['sha256'][:12]+'.tar.gz')
            stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_worker.py','acquire','--spec-json',json.dumps({k:spec[k] for k in ('url','bytes','sha256')}),
                   '--destination',archive],'source-'+name)
            target=attempt/'sources'/name;extract(archive,target,strip_root=True);sources[name]=target
        patched=patch_completebin(sources['CompleteBin'],lock['completebin_modification']['before_sha256'])
        if patched['after']!=lock['completebin_modification']['after']:raise ValueError('Prepared CompleteBin patch bytes differ')
        write_json(attempt/'completebin-modification.json',patched)
        scgpatch=patch_scgbinner(sources['SCGBinner'],lock['scgbinner_modification']['before_sha256'])
        if scgpatch['after']!=lock['scgbinner_modification']['after']:raise ValueError('Prepared SCGBinner dtype patch bytes differ')
        write_json(attempt/'scgbinner-modification.json',scgpatch)
        dbspec=lock['payloads']['CompleteBin_DB'];dbarchive=cache/'CompleteBin-DB-v1.2.3.3.zip'
        stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_worker.py','acquire','--spec-json',json.dumps({k:dbspec[k] for k in ('url','bytes','sha256')}),
               '--destination',dbarchive],'completebin-database')
        db=args.root/'payloads'/('completebin-db-'+dbspec['sha256'][:12])
        if not db.exists():extract(dbarchive,db,strip_root=True)
        for item in dbspec['members']:
            rel=Path(*Path(item['path']).parts[1:])
            if binding(db/rel)!={k:item[k] for k in ('bytes','sha256')}:raise ValueError('CompleteBin database member changed')
        bootstrap=attempt/'bootstrap';extract(BUNDLE/'payload/micromamba-linux.tar.bz2',bootstrap)
        mamba=bootstrap/'bin/micromamba';utility=args.root/'envs'/('utilities-v2-'+attempt.name)
        setupenv=dict(env,MAMBA_ROOT_PREFIX=str(args.root/'mamba'),PIP_CACHE_DIR=str(cache/'pip'))
        explicit=attempt/'utilities-explicit.txt'
        stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_worker.py','acquire-utilities',
               '--lock',BUNDLE/EXP/'utilities-linux-lock.json','--destination',cache/'utilities','--explicit',explicit],
              'utilities-pinned-acquisition')
        stage([mamba,'--no-rc','create','-y','-p',utility,'--offline','--file',explicit],
              'utilities-setup',setupenv)
        stage([mamba,'list','-p',utility,'--explicit'],'utilities-resolved-lock',setupenv)
        for tool,argv in [('bedtools',['--version']),('hmmsearch',['-h']),('prodigal',['-v']),('perl',['-v'])]:
            stage([utility/'bin'/tool,*argv],tool+'-prerequisite',setupenv)
        stage([str(utility/'bin/make'),'-C',sources['minimap2'],'-j','8','CC='+str(utility/'bin/x86_64-conda-linux-gnu-cc'),
               'CFLAGS=-O2 -I'+str(utility/'include'),
               'LIBS=-L'+str(utility/'lib')+' -Wl,-rpath,'+str(utility/'lib')+' -lm -lz -lpthread'],'minimap2-build')
        plan_env=dict(env,PATH=':'.join(map(str,[utility/'bin',base/'bin',mapping/'bin']))+':'+env.get('PATH',''))
        stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_contracts.py','--inputs',inputs,'--output',attempt/'portable',
               '--threads','8','--mapping-bin',mapping/'bin','--minimap2',sources['minimap2']/'minimap2','--megahit',utility/'bin/megahit'],
              'portable-real-native',plan_env)
        bams=[attempt/'portable'/f'mapping_{i}'/f'sample_{i}.sorted.bam' for i in (0,1)]
        stage([amber/'bin/python','-I','-B',BUNDLE/'scripts/e009_contracts.py','--inputs',inputs,
               '--output',attempt/'amber-contract','--threads','8','--amber-source',amber_source,
               '--truth',attempt/'portable/truth/truth.json'],'amber-native-contract',dict(plan_env,LD_LIBRARY_PATH=str(amber/'lib')))
        own_envs={}
        for tool,name in [('semibin','SemiBin'),('metacat','MetaCAT'),('scgbinner','SCGBinner'),('comebin','COMEBin'),('completebin','CompleteBin')]:
            # Each tool owns its venv; borrowed distributions are explicitly read-only.
            try:
                prefix=args.root/'envs'/(tool+'-source-v2-'+attempt.name)
                links=tool_environment(base,inv,prefix,stage);write_json(attempt/(tool+'-dependency-links.json'),{'prefix':str(prefix),'base_prefix':str(base),'links':links})
                python=prefix/'bin/python';own_envs[tool]=str(python)
                wrapper=prefix/'bin/hmmsearch'
                python_wrapper(wrapper,python,BUNDLE/'scripts/e009_hmm.py',['--native',utility/'bin/hmmsearch','--'],env)
                if tool=='comebin':
                    python_wrapper(prefix/'bin/checkm',python,checkm_entry,[],env)
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
                           json.dumps({k:spec[k] for k in ('url','bytes','sha256')}),'--destination',wheel],tool+'-'+dependency+'-wheel')
                    stage([python,'-I','-B','-m','pip','install','--no-deps','--no-compile','--no-index',wheel],tool+'-'+dependency+'-install',tool_env)
                    expected[dependency]=spec['version']
                expectedfile=attempt/(tool+'-expected-inventory.json');write_json(expectedfile,expected)
                stage([python,'-I','-B',BUNDLE/'scripts/e009_native.py','--inventory-prefix',prefix,'--dependency-prefix',base,
                       '--expected-distributions',expectedfile,'--forbidden-prefix',original_base,'--modules','numpy','torch','pandas','scipy','sklearn'],tool+'-isolated-probe',tool_env)
                plan=command_plan(tool,sources[name],inputs/'assembly.fna',bams,attempt/(tool+'-native'),8,db)
                write_json(attempt/(tool+'-command-plan.json'),plan)
                stage([python,'-I','-B',BUNDLE/'scripts/e009_worker.py','tool-contract','--tool',tool,'--source',sources[name],
                       '--inputs',inputs,'--bams',*bams,'--output',attempt/(tool+'-contract'),'--db',db,'--threads','8'],tool+'-native-contract',tool_env)
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
              'source-genome-acquisition')
        sourcefolder=data/('unpacked-'+binding(sourcearchive)['sha256'][:12])
        if not sourcefolder.exists():extract(sourcearchive,sourcefolder,max_bytes=50_000_000_000)
        stage([sys.executable,'-I','-B',BUNDLE/'scripts/e009_worker.py','source-catalog','--source',sourcefolder,
               '--development',BUNDLE/EXP/'development-overlap.json','--output',attempt/'source-catalog.json'],'source-overlap-catalog')
        write_json(attempt/'source-acquisition.json',{'archive':str(sourcearchive),'file':binding(sourcearchive),'shared_source_folder':str(sourcefolder),
                   'source_catalog':binding(attempt/'source-catalog.json'),'admitted_scientific_input':False})
    finally:
        if binding(original_base/'bin/checkm')!=binding(checkm_entry):raise ValueError('Original CheckM entry changed')
        verify_readonly_after(readonly_files,bindings,attempt,deadline,
                              deadline+limits['collection_reserve_seconds'])
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
    p.add_argument('--runtime-recovery-only',action='store_true',help='Byte-bound job-local runtime snapshot and compatibility checks only; no installs/downloads/science')
    p.add_argument('--runtime-snapshot',type=Path,help='Explicit retained E009 snapshot receipt for verified archive reuse')
    p.add_argument('--snapshot-state',type=Path,help='Persistent v8 sealed-chunk state; explicit resume validates source plan and all reused bytes')
    p.add_argument('--work-seconds',type=float,help='Owner-selected overall work ceiling covering setup and all native consumers')
    p.add_argument('--stall-seconds',type=float,default=300,help='Stop after this long without observed real work (default 300s)')
    args=p.parse_args()
    if args.local_seconds is not None and (not args.local_runtimes or not math.isfinite(args.local_seconds) or not 0<args.local_seconds<=7200):
        p.error('--local-seconds is only a positive <=7200-second local-harness limit')
    if args.allocated_vcpus<=0 or args.allocated_ram_gb<=0:p.error('Allocation values must be positive')
    if args.work_seconds is not None and (not math.isfinite(args.work_seconds) or args.work_seconds<=0):
        p.error('--work-seconds requires a positive finite overall ceiling')
    if not math.isfinite(args.stall_seconds) or args.stall_seconds<=0:p.error('Positive finite --stall-seconds required')
    if not args.root.is_absolute() or not args.shared_root.is_absolute() or args.root.is_symlink():p.error('Explicit absolute owned unlinked paths required')
    args.root.mkdir(parents=True,exist_ok=True);transfer=args.root/'transfer';transfer.mkdir(exist_ok=True)
    attempt=Path(tempfile.mkdtemp(prefix='native-preflight-',dir=args.root));started=time.monotonic()-max(0,time.time()-(args.entry_start_epoch or time.time()))
    status={'status':'failed','verification_passed':False};code=1;original=sys.stdout,sys.stderr
    work_seconds=args.local_seconds or args.work_seconds or (5400 if args.runtime_recovery_only else 17400)
    overall_seconds=work_seconds+(120 if args.runtime_recovery_only else 600)
    def alarm(signum,frame):raise TimeoutError('Overall E009 preflight ceiling reached')
    old_handlers={s:signal.getsignal(s) for s in (signal.SIGALRM,signal.SIGINT,signal.SIGTERM)}
    signal.signal(signal.SIGALRM,alarm)
    def cancel(signum,frame):raise KeyboardInterrupt('Owner cancelled signal '+str(signum))
    signal.signal(signal.SIGINT,cancel);signal.signal(signal.SIGTERM,cancel)
    terminal_log=transfer/(attempt.name+'-terminal.log')
    with terminal_log.open('x') as log:
        sys.stdout,sys.stderr=Tee(original[0],log),Tee(original[1],log)
        try:
            print('TERMINAL_LOG='+str(terminal_log),flush=True)
            signal.setitimer(signal.ITIMER_REAL,max(.001,work_seconds-(time.monotonic()-started)))
            shutil.copyfile(BUNDLE/'bundle-manifest.json',attempt/'bundle-manifest.json')
            manifest=verify_bundle(BUNDLE);status['verification_passed']=True
            write_json(attempt/'verification.json',{'passed':True,'source_commit':manifest['source_commit']})
            status=execute(args,attempt,started);status['verification_passed']=True
            code=0 if status['status']=='passed' else 1
        except BaseException as error:
            status.update(error=repr(error),execution_timed_out=isinstance(error,TimeoutError) or time.monotonic()-started>=work_seconds)
            traceback.print_exc()
        finally:
            signal.setitimer(signal.ITIMER_REAL,0)
            try:
                signal.setitimer(signal.ITIMER_REAL,max(.001,overall_seconds-(time.monotonic()-started)))
                print('DLBINNER STORAGE begin this attempt only',flush=True)
                write_json(attempt/'storage-before-collection.json',{'home':storage_snapshot(attempt),
                    'shared':None,
                    'scope':'this attempt only; no recursive scans of prior attempts, environments, chunks or shared sources'})
                print('DLBINNER STORAGE finished',flush=True)
            except BaseException as error:print('STORAGE_SNAPSHOT_UNAVAILABLE='+repr(error),flush=True)
            signal.setitimer(signal.ITIMER_REAL,0)
            elapsed=time.monotonic()-started
            status.update(exit_code=code,allocated_vcpus=args.allocated_vcpus,allocated_ram_gb=args.allocated_ram_gb,
                          seconds_before_collection=elapsed,allocated_core_hours_before_collection=args.allocated_vcpus*elapsed/3600,
                          accounting='declared allocation times entry-to-driver wall; includes setup/failures; excludes owner idle/upload')
            write_json(attempt/'status.json',status);print('PREFLIGHT_STATUS='+json.dumps(status),flush=True)
            try:
                remaining=overall_seconds-(time.monotonic()-started)
                signal.setitimer(signal.ITIMER_REAL,min(600,remaining) if remaining>0 else 120)
                result=collect(attempt,transfer,terminal_log);elapsed=time.monotonic()-started
                result['terminal_log']=str(terminal_log)
                result.update(seconds_through_collection=elapsed,allocated_core_hours_through_collection=args.allocated_vcpus*elapsed/3600)
                result['collection_after_execution_timeout']=bool(status.get('execution_timed_out')) or remaining<=0
                collection_receipt=transfer/(attempt.name+'-collection.json')
                write_json(collection_receipt,result)
                print('COLLECTION_RECEIPT='+str(collection_receipt),flush=True)
                print('ALLOCATION_COST_JSON='+json.dumps({k:result[k] for k in
                    ('seconds_through_collection','allocated_core_hours_through_collection','retained_logical_bytes')}),flush=True)
            except BaseException:traceback.print_exc();code=1
            signal.setitimer(signal.ITIMER_REAL,0)
            for sig,handler in old_handlers.items():signal.signal(sig,handler)
            sys.stdout,sys.stderr=original
    return code


if __name__=='__main__':raise SystemExit(main())
