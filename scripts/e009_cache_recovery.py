"""Cheap E009 source-versus-bytecode recovery, not benchmark or tool execution.

Read two concrete source/cache pairs under individual short limits, then test the
unchanged complete numerical inventory with isolated cache lookup. No downloads,
installs, copied/relocated environments or science. Native owner mode uses one
vCPU / 4 GB; parent setup and execution share a five-minute ceiling. Mac tests
use explicit local prefixes and receive no Linux validation credit.
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
    """Run actual cache/source readers and full prefix checks within a cheap clock.

    Bytecode read timeouts are diagnostic outcomes; source and isolated-import
    failures stop promptly. A pass accepts only this runtime/import workaround,
    not unchanged whole-prefix bytes, other environments or native-tool readiness.
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
    site=prefix/'lib'/('python'+'.'.join(version.split('.')[:2]))/'site-packages'
    tag='cpython-'+''.join(version.split('.')[:2])
    env=sup.isolated_env(1)
    for key in ('CONDA_PREFIX','CONDA_DEFAULT_ENV','CONDA_PROMPT_MODIFIER','CONDA_PYTHON_EXE',
                'PERL5LIB','PERL_LOCAL_LIB_ROOT','PERL_MB_OPT','PERL_MM_OPT'):
        env.pop(key,None)
    scratch=Path(tempfile.mkdtemp(prefix='e009-cache-recovery-',dir='/tmp'))
    env.update(TMPDIR=str(scratch),E009_SOURCE_CACHE_ROOT=str(scratch/'unused-bytecode'),
               MPLCONFIGDIR=str(scratch/'mpl'),XDG_CACHE_HOME=str(scratch/'cache'),
               PIP_DISABLE_PIP_VERSION_CHECK='1',CUDA_VISIBLE_DEVICES='')
    stages=attempt/'stages';stages.mkdir();readings=[]
    pairs=spec.get('source_pairs',['numpy/__init__.py','torch/utils/weak.py'])
    deadline=started+(args.local_seconds or 300)
    policy={'startup_probe_seconds':180,'startup_idle_seconds':45}
    def run(argv,name,seconds):
        sup.progress('E009 runtime-only '+name)
        return run_stage(sup,argv,stages/(name+'.log'),seconds,deadline-time.monotonic(),
                         3_000_000_000,env,policy,sample_root=os.getpid())
    for i,rel in enumerate(pairs):
        source=site/rel
        if not source.is_relative_to(site) or '..' in Path(rel).parts:raise ValueError('Unsafe source probe path')
        cache=source.parent/'__pycache__'/(source.stem+'.'+tag+'.pyc')
        for kind,path in [('source',source),('bytecode',cache)]:
            name=f'read-{i}-{kind}'
            try:
                run([sys.executable,'-I','-B',Path(__file__),'--read-file',path],name,15)
                data=json.loads(next(line.split('=',1)[1] for line in (stages/(name+'.log')).read_text().splitlines() if line.startswith('FILE_READ_JSON=')))
                readings.append(dict(kind=kind,status='read',**data))
            except RuntimeError:
                receipt=json.loads((stages/(name+'.exit.json')).read_text())
                readings.append({'kind':kind,'path':str(path),'status':'unavailable or timed out','exit':receipt})
                write_json(attempt/(name+'-failure.json'),readings[-1])
                if kind=='source':
                    raise RuntimeError('Original Python source is also unreadable/too slow; source-cache workaround not established')
    write_json(attempt/'source-cache-readings.json',readings)
    run([python,'-I','-B',bundle/'scripts/e009_native.py','--inventory-prefix',prefix,
         '--expected-freeze',freeze,'--modules',*spec.get('modules',['numpy','torch','pandas','scipy','sklearn','pysam','Bio','hnswlib','igraph','leidenalg'])],
        'source-only-full-inventory',180)
    text=(stages/'source-only-full-inventory.log').read_text()
    inventory=json.loads(next(line.split('=',1)[1] for line in text.splitlines() if line.startswith('INVENTORY_JSON=')))
    audits=[json.loads(line.split('=',1)[1]) for line in text.splitlines() if line.startswith('CACHE_POLICY_JSON=')]
    if not audits or any(a['persistent_bytecode_attempts'] or not a['writes_disabled'] for a in audits):
        raise ValueError('Incomplete/failed source-cache audit')
    if inventory['bytecode_policy']['pycache_prefix']!=env['E009_SOURCE_CACHE_ROOT']:
        raise ValueError('Inventory did not use reviewed source-cache policy')
    if inventory['python'].split()[0]!=version:raise ValueError('Accepted interpreter version changed')
    after=[]
    for i,rel in enumerate(pairs):
        run([sys.executable,'-I','-B',Path(__file__),'--read-file',site/rel],f'after-{i}-source',15)
        data=json.loads(next(line.split('=',1)[1] for line in (stages/f'after-{i}-source.log').read_text().splitlines() if line.startswith('FILE_READ_JSON=')))
        old=next(row for row in readings if row['kind']=='source' and row['path']==data['path'])
        if (data['bytes'],data['sha256'])!=(old['bytes'],old['sha256']):raise ValueError('Probe source bytes changed')
        after.append(data)
    if list((scratch/'unused-bytecode').rglob('*.pyc')):raise ValueError('Source-only recovery wrote bytecode')
    write_json(attempt/'recovery-observed.json',{'inventory':inventory,'cache_audits':audits,
        'source_samples_before_after_unchanged':True,'source_samples_after':after,
        'scope':'full imports/origins/freeze and sampled source bytes; no entire-prefix byte comparison or native-tool admission'})
    return {'status':'passed','native_linux':not bool(local),'runtime_recovery_only':True,
            'scope':'source cache lookup workaround only; no installs/downloads/native tools/fits/scores',
            'scientific_execution_admitted':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--read-file',type=Path,required=True)
    read_file(parser.parse_args().read_file)
