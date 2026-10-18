#!/usr/bin/env python3
"""Hold, verify and collect one E014 evidence-only wake within the original budget.

This driver cannot invoke the science DAG, fit, marker detector, neighbor builder
or evaluator. It checks original graph/readers and packages existing outputs only.
The controller must arm a fresh boot/process watchdog before releasing this parent;
the provider's 45-minute STOP remains independent of the 30-minute boot clock.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

REPO=Path('/srv/dl_binner/repo')
sys.path.insert(1,str(REPO/'scripts'))
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_collect import binding


def admission(cfg,release,now):
    """Require explicit collection-only credit, original clock, retention and STOP gates."""
    if any(release.get(k)is not True for k in ['credit_gate_passed','existing_VM_only','source_bytes_verified','no_scientific_replay','watchdog_verified']):
        raise ValueError('Collection-only release incomplete')
    if release['config']!=binding(cfg['_path'])or release['provider_STOP_seconds']!=2700:
        raise ValueError('Collection config/provider binding differs')
    if now-cfg['vm_start_epoch']>=600 or cfg['original_VM_uptime_seconds']+2700>43200:
        raise ValueError('Original cumulative clock or held setup allowance unavailable')
    if cfg['vm_start_epoch']+2700>=release['storage_valid_until_epoch']or release['estimated_total_original_phase_gross_USD']>10:
        raise ValueError('Original cost/storage allowance exceeded')


def reuse_graph_proofs(prior,proof,expected_completion,expected_reader):
    """Reuse only the three passed original native readers, retaining failed collection evidence."""
    prior,proof=Path(prior),Path(proof)
    if binding(prior/'completion.json')!=expected_completion:raise ValueError('Prior failed journal differs')
    old=json.loads((prior/'completion.json').read_text())
    passed={s['name'] for s in old['stages'] if s['resources']['exit_code']==0 and not s['resources']['stop_reason']}
    if old['status']!='FAILED' or passed!={'graph-'+u for u in ['E009-dev5','oral-dev4','oral-dev5']}:
        raise ValueError('Prior graph-reader contracts did not pass')
    if binding(prior/'helpers/e014_graph_review.py')!=expected_reader:
        raise ValueError('Passed native graph reader source differs')
    for unit in ['E009-dev5','oral-dev4','oral-dev5']:
        source=prior/'proofs'/('graph-'+unit+'.json')
        if source.is_symlink():raise ValueError('Prior graph proof link refused')
        shutil.copyfile(source,proof/source.name)
    (proof/'previous-collection-failure').mkdir()
    for name in ['completion.json','host.json','config.json','started.json','release.json']:
        shutil.copyfile(prior/name,proof/'previous-collection-failure'/name)
    for name in ['parent-terminal.log','collect.log','supervision.json','watchdog-live-before-release.json']:
        shutil.copyfile(prior/'logs'/name,proof/'previous-collection-failure'/name)
    return dict(passed_readers_reused=3,previous_failure=expected_completion,reader_source=expected_reader)


def run(path):
    """Execute fixed restore/verify/collect consumers once, retaining every failed journal."""
    from e009_owner import supervisor
    from e009_controls import PhaseGuard
    from e009_common import write_json
    from e009_exit_watchdog import identity
    path=Path(path);cfg=json.loads(path.read_text());cfg['_path']=str(path)
    root=Path(cfg['root']);proof=root/'proofs';proof.mkdir(exist_ok=False)
    write_json(root/'started.json',dict(pid=os.getpid(),epoch=time.time(),config=binding(path)))
    sup=supervisor();env=sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4',CLOUDSDK_STORAGE_PROCESS_COUNT='1',CLOUDSDK_STORAGE_THREAD_COUNT='2',CLOUDSDK_CORE_DISABLE_PROMPTS='1',TMPDIR=str(root/'tmp'))
    deadline=cfg['vm_start_epoch']+1800;start_used=shutil.disk_usage(root).used
    outcome=dict(status='FAILED',purpose='Retained evidence only; no scientific replay',stages=[],science_repeated=False)
    def command(name,argv):
        print('E014_COLLECTION_STAGE_START',name,flush=True)
        r=sup.supervise(argv,root/'logs'/(name+'.log'),deadline-time.time()-30,8_000_000_000,env,sample_root=os.getpid())
        outcome['stages'].append(dict(name=name,resources=r))
    try:
        with PhaseGuard(root,deadline-time.time(),growth_bytes=5*1024**3)as guard:
            print('E014_COLLECTION_HELD',os.getpid(),flush=True)
            while not (root/'release.json').exists():
                if time.time()-cfg['vm_start_epoch']>=600:raise TimeoutError('Collection held setup exceeded10minutes')
                time.sleep(.2)
            release=json.loads((root/'release.json').read_text());admission(cfg,release,time.time())
            watch=json.loads((root/'logs/watchdog-live-before-release.json').read_text())
            if watch['decision']!='workflow alive'or watch['expected_process']!=identity(os.getpid())or watch['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():
                raise ValueError('Current boot/process collection watcher differs')
            if subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()!=cfg['original_source']or subprocess.check_output(['git','status','--porcelain'],cwd=REPO,text=True).strip():
                raise ValueError('Frozen science checkout differs')
            for name,expected in cfg['helpers'].items():
                if binding(root/'helpers'/name)!=expected:raise ValueError('Transferred helper bytes differ')
            phase=Path(cfg['phase']);done=json.loads((phase/'completion.json').read_text())
            if not done['community_completed']or done['status']!='FAILED'or done['stages'][0]['resources']['exit_code']!=0 or 'Compact export cap exceeded'not in done['collection_error']:
                raise ValueError('Expected collection-only failed phase receipt differs')
            print('ORIGINAL_RETAINED_MEMBERS',len(json.loads(Path(cfg['inventory']).read_text())['all_result_members']),flush=True)
            if cfg.get('reuse_graph_proofs_from'):
                outcome['graph_contract_reuse']=reuse_graph_proofs(cfg['reuse_graph_proofs_from'],proof,cfg['prior_completion'],cfg['helpers']['e014_graph_review.py'])
                print('REUSED_PASSED_NATIVE_GRAPH_READER_CONTRACTS',cfg['reuse_graph_proofs_from'],flush=True)
            else:
                for unit in ['E009-dev5','oral-dev4','oral-dev5']:
                    command('graph-'+unit,[cfg['python'],'-I','-B',str(root/'helpers/e014_graph_review.py'),'--unit',str(phase/'work/units'/unit),'--output',str(proof/('graph-'+unit+'.json')),'--research-scripts',str(REPO/'scripts')])
            for name in ['config.json','started.json','release.json']:shutil.copyfile(root/name,proof/name)
            command('collect',[sys.executable,'-I','-B',str(root/'helpers/e014_collect.py'),'--work',str(phase/'work'),'--inventory',cfg['inventory'],'--phase',str(phase),'--proofs',str(proof),'--output',str(root/'return')])
            collection=json.loads((root/'return/collection.json').read_text());outcome['collection']=collection
            for name in ['e014-review.tar.gz','e014-review.tar.gz.sha256','collection.json']:
                uri=cfg['archive_prefix']+'/'+name
                command('upload-'+name,['/snap/bin/gcloud','storage','cp','--if-generation-match=0',str(root/'return'/name),uri,'--quiet'])
                readback=root/('readback-'+name)
                command('readback-'+name,['/snap/bin/gcloud','storage','cp',uri,str(readback),'--quiet'])
                if binding(readback)!=binding(root/'return'/name):raise ValueError('Private collection readback differs')
            outcome.update(status='SUCCESS',private_readback_verified=True)
            outcome['disk_observations']=guard.observations
    except BaseException as exc:outcome['error']=f'{type(exc).__name__}: {exc}'
    outcome.update(elapsed_since_recovery_VM_start_seconds=time.time()-cfg['vm_start_epoch'],extra_filesystem_used_bytes=shutil.disk_usage(root).used-start_used)
    write_json(root/'completion.json',outcome)
    try:
        command('completion-upload',['/snap/bin/gcloud','storage','cp','--if-generation-match=0',str(root/'completion.json'),cfg['archive_prefix']+'/completion.json','--quiet'])
    except BaseException as exc:print('COLLECTION_COMPLETION_UPLOAD_UNAVAILABLE',str(exc),flush=True)
    print('E014_COLLECTION_EXIT',json.dumps({k:v for k,v in outcome.items()if k!='disk_observations'}),flush=True)
    return 0 if outcome['status']=='SUCCESS'else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text());log=Path(cfg['root'])/'logs/parent-terminal.log'
    from e009_owner import Tee
    with log.open('x')as f:
        old=sys.stdout,sys.stderr;sys.stdout=Tee(sys.stdout,f);sys.stderr=Tee(sys.stderr,f)
        try:code=run(a.config)
        finally:sys.stdout,sys.stderr=old
    raise SystemExit(code)
