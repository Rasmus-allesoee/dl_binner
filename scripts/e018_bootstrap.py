#!/usr/bin/env python3
"""Bounded E018 native gates reuse the passed E017 environment without reinstall.

Every child uses the original VM-start clock, isolated lexical Python, four
threads and an owned compiler cache. Full-input reads verify identities/axes;
only retained tiny caches exercise the changed consumer before release.
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
    """Check original native unit geometry, full DNA and ordered sample axes."""
    from e018_control import validate_plan
    from dl_binner.information.grouping import load_inputs
    p=json.loads(Path(plan).read_text());validate_plan(p);units={}
    for unit,u in p['units'].items():
        data,vectors,valid,meta=load_inputs(u['features'],u['embeddings'])
        if unit=='E009-positive':
            expected=['cami3_toy_human_gut_short_read_sample_'+str(i)for i in [0,2,3,4,6,9,10,11,14,17]];n,bp=145702,231678157
        else:expected=[];n,bp=1286547,1669981123
        if len(data['ids'])!=n or int(data['lengths'].sum())!=bp or meta['samples']!=expected:
            raise ValueError('Full DNA/ordered measured-parent depth axes differ')
        units[unit]=dict(rows=n,bp=bp,samples=expected,eligible=int(valid.sum()),
            features=binding(u['features']),embeddings=binding(u['embeddings']),depth_semantics=meta['depth_semantics'])
        del data,vectors
    write_json(output,dict(status='PASS',units=units,truth_used=False,inference_or_index=False))


def run(path):
    """Reuse passed complete setup, then gate only new native cached consumers."""
    path=Path(path);cfg=json.loads(path.read_text());root=Path(cfg['root']);repo=Path(cfg['repo'])
    gates=root/'gates';gates.mkdir(exist_ok=False);plan=json.loads(Path(cfg['science_plan']).read_text());py=plan['python']
    deadline=cfg['vm_start_epoch']+900;result=dict(status='FAILED',config=binding(path),stages=[],accepted_setup_reinstalled=False)
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),TMPDIR=str(root/'tmp'))
    def command(name,argv):
        if deadline-time.time()<15:raise TimeoutError('Original setup/verification clock exhausted')
        r=sup.supervise(argv,gates/(name+'.log'),min(600,deadline-time.time()-10),26_000_000_000,env,sample_root=os.getpid())
        result['stages'].append(dict(name=name,resources=r))
    try:
        with PhaseGuard(root,deadline-time.time()-10,growth_bytes=20*1024**3-max(0,__import__('shutil').disk_usage(root).used-cfg['initial_filesystem_used_bytes'])):
            if sys.platform!='linux'or os.cpu_count()!=8 or not os.path.ismount('/srv/dl_binner'):raise ValueError('Existing Linux allocation/mount required')
            if subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()!=cfg['source_commit']or subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip():
                raise ValueError('Exact clean source required')
            frozen=json.loads((repo/'experiments/E018-vote-led-recruitment/candidate-lock.json').read_text())
            for key,b in frozen['files'].items():
                if binding(repo/key)!=b:raise ValueError('Frozen new source differs: '+key)
            command('retained-byte-reuse',[sys.executable,'-I','-B',str(repo/'scripts/e018_reuse.py'),'--lock',cfg['reuse_lock'],'--output',str(gates/'reuse-before.json')])
            lock=json.loads(Path(cfg['reuse_lock']).read_text());base=lock['runtime']['prefix']
            command('complete-existing-runtime-source-library',[py,'-I','-B',str(repo/'scripts/e017_runtime.py'),'probe','--base',base,'--lock',cfg['reuse_lock'],'--output',str(gates/'runtime.json')])
            command('full-input-axes',[py,'-I','-B',str(repo/'scripts/e018_bootstrap.py'),'--inputs',cfg['science_plan'],'--output',str(gates/'inputs.json')])
            command('new-selection-refusal-contracts',[py,'-I','-B',str(repo/'tests/test_e018_recruit.py')])
            command('actual-cached-reader-marker-refiner-export',[py,'-I','-B',str(repo/'experiments/E018-vote-led-recruitment/engineering_fixture.py'),'--cached',lock['tiny_cached'],'--output',str(gates/'tiny-cached')])
            command('launcher-collector-contracts',[sys.executable,'-I','-B',str(repo/'tests/test_e018_operations.py')])
            command('serial-new-output-DAG-dryrun',[py,'-I','-B',str(repo/'scripts/e018_control.py'),'--plan',cfg['science_plan'],'--workflow','--dry-run'])
            result['status']='SUCCESS'
    except BaseException as exc:result['error']=f'{type(exc).__name__}: {exc}'
    write_json(gates/'completion.json',result);return 0 if result['status']=='SUCCESS'else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path);p.add_argument('--inputs',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.inputs:inputs(a.inputs,a.output)
    else:
        cfg=json.loads(a.config.read_text())
        with (Path(cfg['root'])/'logs/bootstrap-terminal.log').open('x')as f:
            old=sys.stdout,sys.stderr;sys.stdout=Tee(sys.stdout,f);sys.stderr=Tee(sys.stderr,f)
            try:code=run(a.config)
            finally:sys.stdout,sys.stderr=old
        raise SystemExit(code)
