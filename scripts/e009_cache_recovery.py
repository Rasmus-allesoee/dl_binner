"""E009 job-local runtime recovery, not benchmark or tool execution.

Snapshot unchanged standalone Conda bytes once, archive persistently, and test the
job-local interpreter/inventory/imports/arithmetic without Home imports. No
downloads, installs, prefix rewriting or science. Original prefix remains intact.
Native owner mode uses one vCPU / 4 GB and a thirty-minute execution ceiling.
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
    if (args.allocated_vcpus,args.allocated_ram_gb)!=(1,4):
        raise ValueError('Runtime-only recovery uses exactly one vCPU / 4 GB')
    if not local:
        if platform.system()!='Linux' or platform.machine()!='x86_64':raise ValueError('Linux x86_64 recovery required')
        if args.root!=Path('/work/Home/dl_binner/e009'):raise ValueError('Use the frozen owned E009 Home root')
        os.sched_setaffinity(0,[min(os.sched_getaffinity(0))])
    os.chdir(attempt)
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    baseline=json.loads((bundle/'experiments/E009-competitive-benchmark/runtime-baseline.json').read_text())
    spec=local or baseline['comebin_dependencies']
    prefix=Path(spec['prefix']);python=prefix/'bin/python'
    freeze=Path(spec['expected_freeze']) if local else bundle/spec['freeze_path']
    version=spec.get('python_version',baseline['comebin_dependencies']['python_version'])
    env=sup.isolated_env(1)
    for key in ('CONDA_PREFIX','CONDA_DEFAULT_ENV','CONDA_PROMPT_MODIFIER','CONDA_PYTHON_EXE',
                'PERL5LIB','PERL_LOCAL_LIB_ROOT','PERL_MB_OPT','PERL_MM_OPT'):
        env.pop(key,None)
    scratch=Path(tempfile.mkdtemp(prefix='e009-cache-recovery-',dir='/tmp'))
    env.update(TMPDIR=str(scratch),E009_SOURCE_CACHE_ROOT=str(scratch/'unused-bytecode'),
               MPLCONFIGDIR=str(scratch/'mpl'),XDG_CACHE_HOME=str(scratch/'cache'),
               PIP_DISABLE_PIP_VERSION_CHECK='1',CUDA_VISIBLE_DEVICES='')
    stages=attempt/'stages';stages.mkdir()
    deadline=started+(args.local_seconds or 1800)
    policy={'startup_probe_seconds':180,'startup_idle_seconds':45}
    def run(argv,name,seconds):
        sup.progress('E009 runtime-only '+name)
        return run_stage(sup,argv,stages/(name+'.log'),seconds,deadline-time.monotonic(),
                         3_000_000_000,env,policy,sample_root=os.getpid())
    local_prefix=scratch/'prefix'
    receipt=getattr(args,'runtime_snapshot',None)
    if receipt:
        receipt=Path(receipt)
        if not local and not receipt.absolute().is_relative_to(args.root/'runtime-snapshots'):
            raise ValueError('Snapshot receipt must be under the owned E009 runtime-snapshots directory')
        run([sys.executable,'-I','-B',bundle/'scripts/e009_snapshot.py','--restore',
             '--receipt',receipt,'--destination',local_prefix],'snapshot-restore',1200)
    else:
        retained=args.root/'runtime-snapshots'/attempt.name;retained.mkdir(parents=True)
        receipt=retained/'snapshot.json'
        run([sys.executable,'-I','-B',bundle/'scripts/e009_snapshot.py','--source',prefix,
             '--destination',local_prefix,'--archive',retained/'comebin-runtime.tar',
             '--receipt',receipt],'snapshot-create',1200)
    snapshot=json.loads(receipt.read_text())
    if snapshot['source_prefix']!=str(prefix.absolute()):raise ValueError('Snapshot belongs to a different original prefix')
    # Do not put the large file inventory or archive in the compact return.
    write_json(attempt/'snapshot-bound.json',{'receipt':str(receipt),'receipt_file':__import__('e009_common').binding(receipt),
        'archive':snapshot['archive'],'logical_bytes':snapshot['logical_bytes'],'files':len(snapshot['files']),
        'source_prefix':snapshot['source_prefix'],'local_prefix':str(local_prefix),
        'excluded':snapshot['excluded'],'scientific_execution_admitted':False})
    prefix=local_prefix;python=prefix/'bin/python'
    env['LD_LIBRARY_PATH']=str(prefix/'lib')
    env['PATH']=str(prefix/'bin')+os.pathsep+os.defpath
    run([python,'-I','-B',bundle/'scripts/e009_native.py','--inventory-prefix',prefix,
         '--expected-freeze',freeze,'--forbidden-prefix',spec['prefix'],
         '--modules',*spec.get('modules',['numpy','torch','pandas','scipy','sklearn','pysam','Bio','hnswlib','igraph','leidenalg'])],
        'local-snapshot-full-inventory',180)
    text=(stages/'local-snapshot-full-inventory.log').read_text()
    inventory=json.loads(next(line.split('=',1)[1] for line in text.splitlines() if line.startswith('INVENTORY_JSON=')))
    audits=[json.loads(line.split('=',1)[1]) for line in text.splitlines() if line.startswith('CACHE_POLICY_JSON=')]
    if not audits or any(a['persistent_bytecode_attempts'] or not a['writes_disabled'] for a in audits):
        raise ValueError('Incomplete/failed source-cache audit')
    if inventory['bytecode_policy']['pycache_prefix']!=env['E009_SOURCE_CACHE_ROOT']:
        raise ValueError('Inventory did not use reviewed source-cache policy')
    if inventory['python'].split()[0]!=version:raise ValueError('Accepted interpreter version changed')
    from e009_snapshot import verify
    verify(local_prefix,snapshot)
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
