#!/usr/bin/env python3
"""Gate reuse of the accepted E014 Linux prefix and retained control inputs.

Runs only after an explicitly authorized VM start under its original clock and
fresh held-parent watcher. No prefix installation, cache recopy, marker detection
on communities, accepted fit replay or scientific fallback is available.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import write_json
from e014_collect import binding
from e009_owner import supervisor,Tee
from e009_controls import PhaseGuard


def inputs(plan,output):
    """Read complete retained axes/crop contracts; verify exact original policies."""
    import numpy as np
    from dl_binner.multiview.views import load
    from e015_control import validate_plan
    p=json.loads(Path(plan).read_text());cfg,base=validate_plan(p);result={}
    for unit,u in p['units'].items():
        data,meta,v,vm=load(u['features'],u['views'])
        if vm['policy']!=base:raise ValueError('Original view bank policy differs')
        if unit=='E009-zero':
            samples=['cami3_toy_human_gut_short_read_sample_'+str(s) for s in [0,2,3,4,6,9,10,11,14,17]]
            if meta['samples']!=samples or len(data['ids'])!=145702 or int(data['lengths'].sum())!=231678157 or data['depth'].shape!=(145702,10):raise ValueError('Complete E009 DNA/depth axes differ')
        else:
            if meta['samples'] or len(data['ids'])!=1286547 or int(data['lengths'].sum())!=1669981123:raise ValueError('Complete sequence-only oral DNA axes differ')
        result[unit]=dict(rows=len(data['ids']),bp=int(data['lengths'].sum()),samples=meta['samples'],
            training_parents=int(data['eligible'].sum()),features=binding(u['features']),views=binding(u['views']),
            parent_depth_semantics=meta['depth_semantics'],bank_policy_unchanged=True)
        del data,v
    write_json(output,dict(status='PASS',units=result,truth_read=False,source_science_replayed=False))


def run(path):
    """Verify source, inventory/native imports and new tiny path within the same clock."""
    path=Path(path);cfg=json.loads(path.read_text());root=Path(cfg['root']);repo=Path(cfg['repo']);gates=root/'gates';gates.mkdir(exist_ok=False)
    plan=json.loads(Path(cfg['science_plan']).read_text());py=plan['python'];deadline=cfg['vm_start_epoch']+7200
    result=dict(status='FAILED',config=binding(path),stages=[],retained_setup_reinstalled=False)
    sup=supervisor();env=sup.isolated_env(4);env.update(E015_WORKFLOW_PYTHON=plan['workflow_python'],NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),TMPDIR=str(root/'tmp'))
    def command(name,argv):
        if deadline-time.time()<900:raise TimeoutError('Insufficient original clock for setup and collection')
        print('E015_NATIVE_GATE',name,flush=True)
        r=sup.supervise(argv,gates/(name+'.log'),min(600,deadline-time.time()-900),26_000_000_000,env,sample_root=os.getpid())
        result['stages'].append(dict(name=name,resources=r))
    try:
        growth=max(0,__import__('shutil').disk_usage(root).used-cfg['initial_filesystem_used_bytes'])
        with PhaseGuard(root,deadline-time.time()-600,growth_bytes=20*1024**3-growth) as guard:
            if sys.platform!='linux' or os.cpu_count()!=8 or not os.path.ismount('/srv/dl_binner'):raise ValueError('Existing native allocation/mount required')
            if subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()!=cfg['source_commit'] or subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip():raise ValueError('Clean exact source required')
            frozen=json.loads((repo/'experiments/E015-zero-reconstruction/candidate-lock.json').read_text())
            for key,expected in frozen['files'].items():
                if binding(repo/key)!=expected:raise ValueError('Frozen E015 source/config differs: '+key)
            command('retained-bytes',[sys.executable,'-I','-B',str(repo/'scripts/e015_reuse.py'),'--lock',cfg['reuse_lock'],'--output',str(gates/'reuse-before.json')])
            command('complete-runtime',[py,'-I','-B',str(repo/'scripts/check_runtime.py'),'--role','candidate','--requirements',str(repo/'requirements/candidate-cpu.txt'),'--threads','4','--output',str(gates/'runtime.json')])
            lock=json.loads(Path(cfg['reuse_lock']).read_text());runtime=json.loads((gates/'runtime.json').read_text())
            for key in ['python','python_version','prefix','base_prefix','system','distributions','distribution_locations','role','threads','user_site_enabled']:
                if runtime[key]!=lock['runtime'][key]:raise ValueError('Retained runtime identity differs: '+key)
            command('installed-source-library',[py,'-I','-B',str(repo/'scripts/e014_runtime.py'),'probe','--lock',str(repo/'experiments/E014-multiview-reconstruction/candidate-lock-v2.json'),'--inventory',str(gates/'runtime.json'),'--output',str(gates/'installed.json')])
            installed=json.loads((gates/'installed.json').read_text())
            if installed['loaded_math_libraries']!=lock['installed']['loaded_math_libraries']:raise ValueError('Loaded native execution library identity differs')
            command('retained-input-axes',[py,'-I','-B',str(repo/'scripts/e015_bootstrap.py'),'--inputs',cfg['science_plan'],'--output',str(gates/'inputs.json')])
            command('new-contracts',[sys.executable,'-I','-B','-m','unittest','discover','-s',str(repo/'tests'),'-p','test_e015_contracts.py','-v'])
            command('native-zero-path',[py,'-I','-B','-m','unittest','discover','-s',str(repo/'tests'),'-p','test_e015_native.py','-v'])
            command('complete-DAG-dry-run',[sys.executable,'-I','-B',str(repo/'scripts/e015_control.py'),'--plan',cfg['science_plan'],'--workflow','--dry-run'])
            result.update(status='SUCCESS',disk_observations=guard.observations)
    except BaseException as exc:result['error']=f'{type(exc).__name__}: {exc}'
    write_json(gates/'completion.json',result);print('E015_NATIVE_GATES_EXIT',result['status'],result.get('error'),flush=True)
    return 0 if result['status']=='SUCCESS' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path);p.add_argument('--inputs',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.inputs:inputs(a.inputs,a.output)
    else:
        cfg=json.loads(a.config.read_text());log=Path(cfg['root'])/'logs/bootstrap-terminal.log'
        with log.open('x') as f:
            old=sys.stdout,sys.stderr;sys.stdout=Tee(sys.stdout,f);sys.stderr=Tee(sys.stderr,f)
            try:code=run(a.config)
            finally:sys.stdout,sys.stderr=old
        raise SystemExit(code)
