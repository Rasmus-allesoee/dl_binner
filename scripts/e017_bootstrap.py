#!/usr/bin/env python3
"""Bounded native E017 source/runtime/cache/tiny gates before grouping release.

No accepted setup/science is repeated. A new package-only prefix explicitly
borrows reviewed complete dependencies. All tests use tiny generated DNA; full
community input reads only verify axes and byte contracts, never a new index.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_collect import binding
from e009_common import write_json
from e009_owner import supervisor,Tee
from e009_controls import PhaseGuard


def inputs(plan,output):
    """Verify complete frozen feature/vector/depth axes without model inference."""
    from e017_control import validate_plan
    from dl_binner.information.grouping import load_inputs
    p=json.loads(Path(plan).read_text());validate_plan(p);records={}
    for unit,u in p['units'].items():
        data,vectors,valid,meta=load_inputs(u['features'],u['embeddings'])
        if unit=='E009-positive':
            samples=['cami3_toy_human_gut_short_read_sample_'+str(i) for i in [0,2,3,4,6,9,10,11,14,17]]
            if len(data['ids'])!=145702 or int(data['lengths'].sum())!=231678157 or meta['samples']!=samples:
                raise ValueError('Complete E009 ordered DNA/depth axes differ')
        elif len(data['ids'])!=1286547 or int(data['lengths'].sum())!=1669981123 or meta['samples']:
            raise ValueError('Complete oral sequence-only axes differ')
        records[unit]=dict(rows=len(data['ids']),bp=int(data['lengths'].sum()),samples=meta['samples'],
                           eligible=int(valid.sum()),core_contigs=int((valid&(data['lengths']>=2500)).sum()),
                           features=binding(u['features']),embeddings=binding(u['embeddings']),
                           measured_parent_depth=meta['depth_semantics'])
        del data,vectors
    write_json(output,dict(status='PASS',units=records,truth_used=False,inference_or_index=False))


def run(path):
    """Run held-parent prerequisites within the original three-hour VM-start clock."""
    path=Path(path);cfg=json.loads(path.read_text());root=Path(cfg['root']);repo=Path(cfg['repo'])
    gates=root/'gates';gates.mkdir(exist_ok=False);plan=json.loads(Path(cfg['science_plan']).read_text())
    py=plan['python'];deadline=min(cfg['vm_start_epoch']+1800,cfg['vm_start_epoch']+10800-600)
    result=dict(status='FAILED',config=binding(path),stages=[],accepted_setup_reinstalled=False)
    sup=supervisor();env=sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),TMPDIR=str(root/'tmp'))
    def command(name,argv):
        if deadline-time.time()<30:raise TimeoutError('Original native gate clock exhausted')
        r=sup.supervise(argv,gates/(name+'.log'),min(600,deadline-time.time()-10),26_000_000_000,env,sample_root=os.getpid())
        result['stages'].append(dict(name=name,resources=r))
    try:
        with PhaseGuard(root,deadline-time.time()-10,
                        growth_bytes=20*1024**3-max(0,__import__('shutil').disk_usage(root).used-cfg['initial_filesystem_used_bytes'])):
            if sys.platform!='linux' or os.cpu_count()!=8 or not os.path.ismount('/srv/dl_binner'):
                raise ValueError('Existing Linux allocation/mount required')
            mem_kib=int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines()
                             if line.startswith('MemTotal:')))
            if mem_kib*1024<30*1024**3:
                raise ValueError('Existing 32-GiB allocation memory unavailable')
            if subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()!=cfg['source_commit'] or subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip():
                raise ValueError('Exact clean source required')
            frozen=json.loads((repo/'experiments/E017-information-aware-grouping/candidate-lock.json').read_text())
            for k,b in frozen['files'].items():
                if binding(repo/k)!=b:raise ValueError('Frozen preparation bytes differ: '+k)
            if binding(cfg['wheel'])!=frozen['tested_wheel']:raise ValueError('Candidate wheel differs')
            command('retained-bytes',[sys.executable,'-I','-B',str(repo/'scripts/e017_reuse.py'),'--lock',cfg['reuse_lock'],'--output',str(gates/'reuse-before.json')])
            lock=json.loads(Path(cfg['reuse_lock']).read_text());base=Path(lock['runtime']['prefix'])
            command('owned-package-env',[str(base/'bin/python'),'-I','-B',str(repo/'scripts/e017_runtime.py'),'create','--base',str(base),
                '--destination',str(Path(py).parent.parent),'--wheel',cfg['wheel'],'--output',str(gates/'environment.json')])
            command('complete-native-runtime-source-library',[py,'-I','-B',str(repo/'scripts/e017_runtime.py'),'probe','--base',str(base),
                '--lock',cfg['reuse_lock'],'--output',str(gates/'runtime.json')])
            command('full-input-axes',[py,'-I','-B',str(repo/'scripts/e017_bootstrap.py'),'--inputs',cfg['science_plan'],'--output',str(gates/'inputs.json')])
            command('actual-sparse-approximate-recruitment',[py,'-I','-B',str(repo/'tests/test_e017_grouping.py')])
            command('cached-native-marker-refiner-export',[py,'-I','-B',str(repo/'experiments/E017-information-aware-grouping/engineering_fixture.py'),
                '--output',str(gates/'tiny-cached'),'--fixture-source',str(repo/'tests/product/candidate_fixture.py'),'--threads','4'])
            command('synthetic-kernel-timing',[py,'-I','-B',str(repo/'experiments/E017-information-aware-grouping/kernel_fixture.py'),
                '--output',str(gates/'kernel'),'--config',plan['config'],'--threads','4'])
            timing=json.loads((gates/'kernel/fixture.json').read_text())
            # One prospective conservative projection, not a score or tuning grid.
            # Includes JIT in every scaled unit and reserves marker/export/collection.
            projection=2*(timing['group_seconds']+timing['audit_seconds'])*(89041+508763)/(4096+8192)+1200
            write_json(gates/'affordability.json',dict(projected_remaining_seconds=projection,
                remaining_original_clock=cfg['vm_start_epoch']+10800-time.time(),
                rule='2x full-width synthetic group+audit scaled by eligible rows, plus1200s; planning heuristic, original clock/disk/RSS guard remains authoritative'))
            if projection>cfg['vm_start_epoch']+10800-time.time():
                raise TimeoutError('Measured native projection exceeds remaining original grouping/collection clock')
            command('launcher-collector-contracts',[sys.executable,'-I','-B',str(repo/'tests/test_e017_operations.py')])
            command('complete-serial-DAG-dryrun',[py,'-I','-B',str(repo/'scripts/e017_control.py'),'--plan',cfg['science_plan'],'--workflow','--dry-run'])
            result['status']='SUCCESS'
    except BaseException as exc:result['error']=f'{type(exc).__name__}: {exc}'
    write_json(gates/'completion.json',result);return 0 if result['status']=='SUCCESS' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path);p.add_argument('--inputs',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.inputs:inputs(a.inputs,a.output)
    else:
        cfg=json.loads(a.config.read_text())
        with (Path(cfg['root'])/'logs/bootstrap-terminal.log').open('x') as f:
            old=sys.stdout,sys.stderr;sys.stdout=Tee(sys.stdout,f);sys.stderr=Tee(sys.stderr,f)
            try:code=run(a.config)
            finally:sys.stdout,sys.stderr=old
        raise SystemExit(code)
