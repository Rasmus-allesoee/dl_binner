#!/usr/bin/env python3
"""Verify the existing Linux host and prepare a fresh owned E014 CPU environment.

Run only on an already authorized VM under the same VM-start clock while the
science parent is held and watched. No community stage or cloud API is launched.
Accepted cache/runtime bytes are checked before reuse, never recopied on failure.
Every native child has a persistent resource/log receipt; failures remain journals.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding,write_json
from e009_owner import supervisor,Tee
from e009_controls import PhaseGuard


def run(config):
    """Prepare/gate once within the original45-minute held setup allowance."""
    config=Path(config);cfg=json.loads(config.read_text());phase=Path(cfg['phase_root']);gates=phase/'gates';gates.mkdir(exist_ok=False)
    repo=Path(cfg['repo']);plan=json.loads(Path(cfg['science_plan']).read_text())
    from e014_comparison import validate_plan
    validate_plan(plan)
    if sys.platform!='linux' or os.cpu_count()!=8 or not os.path.ismount('/srv/dl_binner'):raise ValueError('Existing native allocation/mount required')
    deadline=cfg['vm_start_epoch']+2700;remaining=deadline-time.time()
    if remaining<=60:raise TimeoutError('Original held setup clock exhausted')
    old=cfg['base_environment'];old_python=str(Path(old)/'bin/python');new_python=plan['python'];prefix=str(Path(new_python).parent.parent)
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(phase/'native-cache'),
        TMPDIR=str(phase/'tmp'),PIP_CONFIG_FILE='/dev/null',PIP_NO_INDEX='1',PIP_DISABLE_PIP_VERSION_CHECK='1')
    for name in ['native-cache','tmp']:(phase/name).mkdir(exist_ok=True)
    result=dict(status='FAILED',stages=[],community_science=False,source_commit=cfg['source_commit'])
    def command(name,argv):
        left=deadline-time.time()-30
        if left<=0:raise TimeoutError('No original setup clock remains')
        print('E014_NATIVE_GATE_START',name,flush=True)
        r=sup.supervise(argv,gates/(name+'.log'),left,8_000_000_000,env,sample_root=os.getpid());result['stages'].append(dict(name=name,resources=r))
    try:
        growth=max(0,__import__('shutil').disk_usage(phase).used-cfg['initial_filesystem_used_bytes'])
        with PhaseGuard(phase,remaining,growth_bytes=45*1024**3-growth):
            if subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()!=cfg['source_commit']or subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip():raise ValueError('Exact clean native source required')
            cached=cfg['accepted_cache']
            command('accepted-cache',[old_python,'-I','-B',str(repo/'scripts/e011_cached.py'),'verify-restored','--root',cached,'--output',str(gates/'cache-reuse.json')])
            command('accepted-runtime',[old_python,'-I','-B',str(repo/'scripts/e011_cached.py'),'probe','--root',cached,'--output',str(gates/'base-runtime.json')])
            wheel=Path(cfg['wheel']);lock=json.loads((repo/'experiments/E014-multiview-reconstruction/candidate-lock-v2.json').read_text())
            if binding(wheel)!={k:lock['tested_wheel'][k]for k in ['bytes','sha256']}:raise ValueError('Frozen wheel bytes differ')
            command('owned-env',[old_python,'-I','-B',str(repo/'scripts/e014_runtime.py'),'create','--base',old,'--destination',prefix,'--receipt',str(gates/'owned-env.json')])
            command('install-wheel',[new_python,'-I','-B','-m','pip','install','--no-deps','--no-index',str(wheel)])
            command('complete-runtime',[new_python,'-I','-B',str(repo/'scripts/check_runtime.py'),'--role','candidate','--requirements',str(repo/'requirements/candidate-cpu.txt'),'--threads','4','--output',str(gates/'runtime.json')])
            command('installed-source',[new_python,'-I','-B',str(repo/'scripts/e014_runtime.py'),'probe','--lock',str(repo/'experiments/E014-multiview-reconstruction/candidate-lock-v2.json'),'--inventory',str(gates/'runtime.json'),'--output',str(gates/'installed.json')])
            command('installed-CLI',[new_python,'-I','-B','-m','dl_binner','--help'])
            command('restore-opaque-input',[sys.executable,'-I','-B',str(repo/'scripts/e014_runtime.py'),'restore-input','--compressed',cfg['input_transport'],'--manifest',cfg['input_transport_manifest'],'--destination',plan['units']['oral-dev5']['fasta']])
            command('complete-inputs',[new_python,'-I','-B',str(repo/'scripts/e014_inputs.py'),'--plan',cfg['science_plan'],'--output',str(gates/'inputs.json')])
            command('production-marker-contract',[new_python,'-I','-B',str(repo/'scripts/e010_marker_contract.py'),'--profile',plan['hmm'],'--manifest',plan['asset_manifest'],'--threads','4','--output',str(gates/'marker-positive')])
            command('installed-product',[sys.executable,'-I','-B',str(repo/'scripts/test_product.py'),'--python',new_python,'--threads','4','--timeout','600','--output',str(gates/'product')])
            command('native-scheduler',[sys.executable,'-I','-B',str(repo/'scripts/e014_runtime.py'),'scheduler','--workflow-python',plan['workflow_python'],'--output',str(gates/'scheduler')])
            command('launcher-contracts',[sys.executable,'-I','-B','-m','unittest','discover','-s',str(repo/'tests'),'-p','test_e014_*.py','-v'])
            command('native-exit-detector',[sys.executable,'-I','-B','-m','unittest','discover','-s',str(repo/'tests'),'-p','test_e009_exit_watchdog.py','-v'])
            command('complete-DAG-dry-run',[sys.executable,'-I','-B',str(repo/'scripts/e014_comparison.py'),'--plan',cfg['science_plan'],'--workflow','--dry-run'])
            result.update(status='SUCCESS',full_source_and_runtime_verified=True,full_axes_verified=True,remaining_setup_seconds=deadline-time.time())
    except BaseException as exc:result['error']=f'{type(exc).__name__}: {exc}'
    write_json(phase/'bootstrap-result.json',result);print('E014_BOOTSTRAP_EXIT',json.dumps(result),flush=True)
    return 0 if result['status']=='SUCCESS'else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text());path=Path(cfg['phase_root'])/'logs/bootstrap-terminal.log';path.parent.mkdir(exist_ok=True)
    with path.open('x')as stream:
        old=sys.stdout,sys.stderr;sys.stdout=Tee(sys.stdout,stream);sys.stderr=Tee(sys.stderr,stream)
        try:code=run(a.config)
        finally:sys.stdout,sys.stderr=old
    raise SystemExit(code)
