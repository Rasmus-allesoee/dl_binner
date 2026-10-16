"""E009 job-local runtime recovery, not benchmark or tool execution.

Snapshot unchanged standalone Conda bytes once, archive persistently, and test the
job-local interpreter/inventory/imports/arithmetic without Home imports. No
downloads, installs, prefix rewriting or science. Original prefix remains intact.
Owner chooses the allocation/overall ceiling; chunk persistence allows safe resume.
Mac tests use explicit local prefixes and receive no Linux validation credit.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import sys
import tempfile
import time
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import write_json


def read_file(path):
    """Stream one existing regular file read-only and report timing/hash, no contents."""
    path=Path(path)
    if path.is_symlink() or not path.is_file():raise ValueError('Expected existing unlinked regular source/cache file')
    print('DLBINNER READ_BEGIN '+str(path),flush=True)
    started=time.monotonic();digest=hashlib.sha256();size=0
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            size+=len(block);digest.update(block)
    print('FILE_READ_JSON='+json.dumps({'path':str(path),'bytes':size,'sha256':digest.hexdigest(),
          'seconds':time.monotonic()-started}),flush=True)


def recover(args,attempt,started,bundle,sup):
    """Run byte-bound snapshot creation/reuse and native compatibility checks.

    A pass accepts only this numerical runtime snapshot, not other environments,
    native binner readiness or full-scale affordability. No original bytes change.
    """
    from e009_owner import run_stage
    local=json.loads(args.local_runtimes.read_text()) if args.local_runtimes else None
    if args.allocated_vcpus<1 or args.allocated_ram_gb<4:
        raise ValueError('Recovery needs >=1 declared CPU and >=4 GB RAM')
    if not local:
        if platform.system()!='Linux' or platform.machine()!='x86_64':raise ValueError('Linux x86_64 recovery required')
        if args.root!=Path('/work/Home/dl_binner/e009'):raise ValueError('Use the frozen owned E009 Home root')
        available=sorted(os.sched_getaffinity(0))
        if len(available)<args.allocated_vcpus:raise ValueError('Declared CPUs exceed available affinity')
        os.sched_setaffinity(0,available[:args.allocated_vcpus])
    os.chdir(attempt)
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    baseline=json.loads((bundle/'experiments/E009-competitive-benchmark/runtime-baseline.json').read_text())
    spec=local or baseline['comebin_dependencies']
    prefix=Path(spec['prefix']);python=prefix/'bin/python'
    freeze=Path(spec['expected_freeze']) if local else bundle/spec['freeze_path']
    version=spec.get('python_version',baseline['comebin_dependencies']['python_version'])
    env=sup.isolated_env(args.allocated_vcpus)
    for key in ('CONDA_PREFIX','CONDA_DEFAULT_ENV','CONDA_PROMPT_MODIFIER','CONDA_PYTHON_EXE',
                'PERL5LIB','PERL_LOCAL_LIB_ROOT','PERL_MB_OPT','PERL_MM_OPT'):
        env.pop(key,None)
    scratch=Path(tempfile.mkdtemp(prefix='e009-cache-recovery-',dir='/tmp'))
    env.update(TMPDIR=str(scratch),E009_SOURCE_CACHE_ROOT=str(scratch/'unused-bytecode'),
               MPLCONFIGDIR=str(scratch/'mpl'),XDG_CACHE_HOME=str(scratch/'cache'),
               PIP_DISABLE_PIP_VERSION_CHECK='1',CUDA_VISIBLE_DEVICES='')
    stages=attempt/'stages';stages.mkdir()
    work_seconds=args.local_seconds or getattr(args,'work_seconds',None) or 5400
    deadline=started+work_seconds
    stall=getattr(args,'stall_seconds',300)
    policy={'startup_probe_seconds':work_seconds,'startup_idle_seconds':stall,
            'materialization_progress':True}
    rss_bytes=int(args.allocated_ram_gb*1_000_000_000*.75)
    def run(argv,name):
        sup.progress('E009 runtime-only '+name)
        return run_stage(sup,argv,stages/(name+'.log'),deadline-time.monotonic(),deadline-time.monotonic(),
                         rss_bytes,env,policy,sample_root=os.getpid())
    local_prefix=scratch/'prefix'
    if getattr(args,'runtime_snapshot',None):
        raise ValueError('V8 uses --snapshot-state for sealed-chunk resume, not an uncompleted v7 archive')
    state=getattr(args,'snapshot_state',None) or args.root/'runtime-snapshots/comebin-runtime-v8'
    state=Path(state).absolute()
    if state.is_symlink() or (not local and not state.resolve().is_relative_to(args.root.resolve()/'runtime-snapshots')):
        raise ValueError('Use an unlinked owned E009 runtime-snapshots state')
    receipt=state/'snapshot.json'
    write_json(attempt/'recovery-config.json',{'state':str(state),'overall_work_seconds':work_seconds,
        'stall_seconds':stall,'allocated_vcpus':args.allocated_vcpus,'allocated_ram_gb':args.allocated_ram_gb,
        'sampled_rss_ceiling':rss_bytes,'stage_wall_caps':None,'source_prefix':str(prefix)})
    print('SNAPSHOT_STATE='+str(state),flush=True)
    run([sys.executable,'-I','-B',bundle/'scripts/e009_materialize.py','--source',prefix,
         '--destination',local_prefix,'--state',state,'--summary',attempt/'selection-observed.json'],
        'snapshot-materialize')
    snapshot=json.loads(receipt.read_text())
    operation=json.loads((attempt/'selection-observed.json').read_text())
    if snapshot['source_prefix']!=str(prefix.absolute()):raise ValueError('Snapshot belongs to a different original prefix')
    write_json(attempt/'snapshot-bound.json',{'receipt':str(receipt),'receipt_file':__import__('e009_common').binding(receipt),
        'state':str(state),'shards':snapshot['shards'],
        'retained_archive_bytes':sum(x['archive']['bytes'] for x in snapshot['shards']),
        'logical_bytes':snapshot['logical_bytes'],'files':len(snapshot['files']),
        'source_copied_entries':operation['source_copied_entries'],'restored_entries':operation['restored_entries'],
        'source_prefix':snapshot['source_prefix'],'local_prefix':str(local_prefix),
        'excluded':snapshot['excluded'],'scientific_execution_admitted':False})
    prefix=local_prefix;python=prefix/'bin/python'
    env['LD_LIBRARY_PATH']=str(prefix/'lib')
    env['PATH']=str(prefix/'bin')+os.pathsep+os.defpath
    run([python,'-I','-B',bundle/'scripts/e009_native.py','--inventory-prefix',prefix,
         '--expected-freeze',freeze,'--forbidden-prefix',spec['prefix'],
         '--modules',*spec.get('modules',['numpy','torch','pandas','scipy','sklearn','pysam','Bio','hnswlib','igraph','leidenalg'])],
        'local-snapshot-full-inventory')
    text=(stages/'local-snapshot-full-inventory.log').read_text()
    inventory=json.loads(next(line.split('=',1)[1] for line in text.splitlines() if line.startswith('INVENTORY_JSON=')))
    audits=[json.loads(line.split('=',1)[1]) for line in text.splitlines() if line.startswith('CACHE_POLICY_JSON=')]
    if not audits or any(a['persistent_bytecode_attempts'] or not a['writes_disabled'] for a in audits):
        raise ValueError('Incomplete/failed source-cache audit')
    if inventory['bytecode_policy']['pycache_prefix']!=env['E009_SOURCE_CACHE_ROOT']:
        raise ValueError('Inventory did not use reviewed source-cache policy')
    if inventory['python'].split()[0]!=version:raise ValueError('Accepted interpreter version changed')
    run([sys.executable,'-I','-B',bundle/'scripts/e009_materialize.py','--source',spec['prefix'],
        '--destination',local_prefix,'--state',state,'--summary',attempt/'selection-observed.json',
        '--verify-receipt',receipt],'snapshot-after-verify')
    if list((scratch/'unused-bytecode').rglob('*.pyc')):raise ValueError('Source-only recovery wrote bytecode')
    write_json(attempt/'recovery-observed.json',{'inventory':inventory,'cache_audits':audits,
        'snapshot_bytes_after_unchanged':True,'snapshot_receipt':str(receipt),
        'scope':'byte-bound job-local runtime, full imports/origins/freeze and compatibility arithmetic; no native-tool admission'})
    return {'status':'passed','native_linux':not bool(local),'runtime_recovery_only':True,
            'scope':'job-local snapshot only; no installs/downloads/native tools/fits/scores',
            'scientific_execution_admitted':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--read-file',type=Path,required=True)
    read_file(parser.parse_args().read_file)
