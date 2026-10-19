#!/usr/bin/env python3
"""Collect retained E015 results only after a separately approved bounded VM wake.

Never call the science DAG, trainer, detector, inference, neighbor builder, graph
reviewer or evaluator. The original failed journal/source stay untouched. Verify
passed reader receipts against their retained file bytes and create the first full
work inventory: the original collector failed before it could write one.
A fresh boot/process watcher and 45-minute provider STOP must precede release.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

sys.path.insert(0,str(Path(__file__).absolute().parent))
sys.path.insert(1,'/srv/dl_binner/repo/scripts')
from e014_collect import binding

SECONDS=1800
STOP_SECONDS=2700
SOURCE='b259dcac12968b38b909ce7733a4a12ee07eae5a'


def retained(phase,expected_completion,expected_config,output):
    """Verify existing journal/reader/checkpoint/selection bindings, without replay.

    Graph and exact-reload validators already ran inside the successful science
    DAG. Reuse those proofs only after hashing their actual graph/vector/partition
    and checkpoint bytes. This is byte/integrity admission, not quality admission.
    """
    phase,output=Path(phase),Path(output)
    if binding(phase/'completion.json')!=expected_completion:raise ValueError('Original failed journal differs')
    if binding(phase/'config.json')!=expected_config:raise ValueError('Original phase config differs')
    original_config=json.loads((phase/'config.json').read_text())
    if original_config['source_commit']!=SOURCE:raise ValueError('Original phase source differs')
    for name,expected in original_config['bindings'].items():
        if binding(name)!=expected:raise ValueError('Original source/input plan differs: '+name)
    done=json.loads((phase/'completion.json').read_text())
    if (done['status']!='FAILED' or done['science_completed']is not True or done['source']!=SOURCE
            or "ModuleNotFoundError: No module named 'e014_collect'"not in done['collection_error']):
        raise ValueError('Expected isolated collector failure after successful science required')
    if [s['name']for s in done['stages']]!=['science','reuse-after'] or any(s['resources']['exit_code']!=0 or s['resources']['stop_reason'] for s in done['stages']):
        raise ValueError('Successful science and retained-input recheck required')
    lock=json.loads((phase/'sealed-evidence/source/reuse-lock.json').read_text())
    before=json.loads((phase/'gates/reuse-before.json').read_text());after=json.loads((phase/'reuse-after.json').read_text())
    if before['status']!='PASS' or after['status']!='PASS' or before['files']!=lock['files'] or after['files']!=lock['files']:
        raise ValueError('Passed retained-input before/after contracts differ')
    gate=json.loads((phase/'gates/completion.json').read_text())
    if gate['config']!=expected_config or gate['status']!='SUCCESS' or len(gate['stages'])!=7 or any(s['resources']['exit_code']!=0 or s['resources']['stop_reason'] for s in gate['stages']):
        raise ValueError('Original seven native gates did not pass')
    checked={}
    def check(path,expected):
        if binding(path)!=expected:raise ValueError('Retained scientific bytes differ: '+str(path))
        checked[str(path)]=expected
    proofs={}
    for unit in ['E009-zero','oral-zero']:
        root=phase/'work/units'/unit;proof=json.loads((root/'graph-proof.json').read_text())
        if proof['status']!='PASS' or proof['unit']!=unit:raise ValueError('Passed graph reader missing')
        for key,name in [('graph','group/graph.npz'),('embedding','embeddings.npz'),('partition','group/partition.json')]:check(root/name,proof[key])
        checkpoint=json.loads((root/'train/checkpoint.json').read_text());em=json.loads((root/'embeddings.json').read_text())
        if (checkpoint['config']['composition_reconstruction_weight']!=0 or checkpoint['config']['depth_reconstruction_weight']!=0
                or len(checkpoint['history'])!=20 or not em['reload_exact'] or em['checkpoint_sha256']!=checkpoint['sha256']):
            raise ValueError('Frozen completed fit/reload receipt differs')
        check(root/'train/checkpoint.pt',dict(bytes=(root/'train/checkpoint.pt').stat().st_size,sha256=checkpoint['sha256']))
        if binding(root/'train/reference.npz')!=proof['embedding']:raise ValueError('Exact native reload/reference differs')
        final=json.loads((root/'refine/completed.json').read_text())
        if final['status']!='SUCCESS' or final['policy']!='unchanged E013' or final['truth_accessed']is not False:raise ValueError('Completed fixed refinement missing')
        check(root/'refine/partition.json',dict(bytes=(root/'refine/partition.json').stat().st_size,sha256=final['partition_sha256']))
        if set(json.loads((root/'export/accounting.json').read_text()))!={'pre','post'}:raise ValueError('Complete export accounting absent')
        proofs[unit]=dict(graph_reader=binding(root/'graph-proof.json'),checkpoint=binding(root/'train/checkpoint.json'),
            refinement=binding(root/'refine/completed.json'),accounting=binding(root/'export/accounting.json'))
    result=dict(status='PASS',original_completion=expected_completion,checked_new_output_bytes=checked,passed_proofs=proofs,
        science_reader_fit_or_score_replayed=False,full_quality_admission=False,
        inventory_scope='First full work snapshot will be created by collection; original collector failed before any inventory/archive.')
    with output.open('x')as f:json.dump(result,f,indent=2);f.write('\n')
    return result


def admission(cfg,release,now):
    """Require explicit new collection clock, original-budget coverage and current STOP."""
    if not 0<=now-cfg['vm_start_epoch']<600:raise TimeoutError('Fresh held collection setup exceeded10minutes')
    for key in ['collection_only_approved','new_clock_authorized','credit_gate_passed',
                'pending_usage_accounted','watchdog_verified','existing_VM_only','no_scientific_replay']:
        if release.get(key)is not True:raise ValueError('Collection-only release incomplete')
    if release['config']!=binding(cfg['_path']) or release['provider_STOP_seconds']!=STOP_SECONDS:
        raise ValueError('Fresh collection config/provider STOP differs')
    if (release['additional_gross_USD_upper']>.65 or release['combined_E015_gross_USD_upper']>2
            or release['storage_retention_extended']is not False
            or cfg['vm_start_epoch']+STOP_SECONDS>=min(release['storage_valid_until_epoch'],release['credit_valid_until_epoch'])):
        raise ValueError('Collection credit/cost/original-retention envelope unavailable')
    if set(release['covered_costs'])!={'compute','disk','storage','network','operations'}:
        raise ValueError('Complete eligible-product coverage required')


def run(path):
    """Hold, verify passed outputs, pack once and read back within a fresh30-minute clock."""
    from e009_owner import supervisor,Tee
    from e009_controls import PhaseGuard
    from e009_exit_watchdog import identity
    from e009_common import write_json
    path=Path(path);cfg=json.loads(path.read_text());cfg['_path']=str(path)
    root=Path(cfg['root']);phase=Path(cfg['phase']);repo=Path('/srv/dl_binner/repo')
    if sys.platform!='linux' or os.cpu_count()!=8 or not os.path.ismount('/srv/dl_binner'):raise ValueError('Existing native allocation/mount required')
    deadline=cfg['vm_start_epoch']+SECONDS;sup=supervisor();env=sup.isolated_env(4)
    env.update(CLOUDSDK_STORAGE_PROCESS_COUNT='1',CLOUDSDK_STORAGE_THREAD_COUNT='2',CLOUDSDK_CORE_DISABLE_PROMPTS='1',TMPDIR=str(root/'tmp'))
    write_json(root/'started.json',dict(pid=os.getpid(),epoch=time.time(),config=binding(path)))
    outcome=dict(status='FAILED',science_repeated=False,stages=[]);guard=None
    def command(name,argv):
        left=deadline-time.time()-15
        if left<=10:raise TimeoutError('Fresh collection clock exhausted')
        print('E015_RECOVERY_STAGE',name,flush=True)
        result=sup.supervise(argv,root/'logs'/(name+'.log'),left,8_000_000_000,env,sample_root=os.getpid())
        outcome['stages'].append(dict(name=name,resources=result))
    try:
        growth=max(0,shutil.disk_usage(root).used-cfg['initial_filesystem_used_bytes'])
        with PhaseGuard(root,deadline-time.time(),growth_bytes=5*1024**3-growth)as guard:
            while not(root/'release.json').exists():
                if (root/'abort.json').exists():raise RuntimeError('Controller aborted collection release; inspect retained gate failure')
                if time.time()-cfg['vm_start_epoch']>=600:raise TimeoutError('Held collection setup exhausted10minutes')
                time.sleep(.2)
            release=json.loads((root/'release.json').read_text());admission(cfg,release,time.time())
            live=json.loads((root/'logs/watchdog-live-before-release.json').read_text())
            if live['decision']!='workflow alive' or live['expected_process']!=identity(os.getpid()) or live['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Fresh boot/process watcher differs')
            if subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()!=SOURCE or subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip():raise ValueError('Frozen original science checkout differs')
            helpers=root/'helpers'
            names={'e015_recover.py','e015_collect.py','e014_collect.py','e015_recovery_arm.py'}
            if set(cfg['helpers'])!=names or {p.name for p in helpers.iterdir()}!=names:
                raise ValueError('Exact four-file recovery helper set required')
            for name,expected in cfg['helpers'].items():
                if binding(root/'helpers'/name)!=expected:raise ValueError('Transferred collector helper differs')
            retained(phase,cfg['original_completion'],cfg['original_config'],root/'retained-proof.json')
            evidence=root/'evidence';shutil.copytree(phase/'sealed-evidence',evidence)
            for name in ['completion.json','science-result.json','reuse-after.json','config.json','science-plan.json','host.json','started.json','release.json']:
                shutil.copyfile(phase/name,evidence/('original-'+name))
            logs=evidence/'original-closed-logs';logs.mkdir()
            for p in (phase/'logs').iterdir():
                if p.is_file():shutil.copyfile(p,logs/p.name)
            recovery=evidence/'recovery';recovery.mkdir()
            for name in ['config.json','started.json','release.json','retained-proof.json']:shutil.copyfile(root/name,recovery/name)
            shutil.copytree(root/'helpers',recovery/'helpers');shutil.copytree(root/'logs',recovery/'logs')
            collector=root/'helpers/e015_collect.py'
            command('collection',[sys.executable,'-I','-B',str(collector),'--work',str(phase/'work'),'--evidence',str(evidence),'--output',str(root/'return')])
            outcome['collection']=json.loads((root/'return/collection.json').read_text())
            for name in ['e015-evidence.tar.gz','e015-evidence.tar.gz.sha256','collection.json']:
                uri=cfg['archive_prefix']+'/'+name
                command('upload-'+name,['/snap/bin/gcloud','storage','cp','--if-generation-match=0',str(root/'return'/name),uri,'--quiet'])
                command('readback-'+name,['/snap/bin/gcloud','storage','cp',uri,str(root/('readback-'+name)),'--quiet'])
                if binding(root/'return'/name)!=binding(root/('readback-'+name)):raise ValueError('Private recovery readback differs')
            outcome.update(status='SUCCESS',private_readback_verified=True)
    except BaseException as exc:outcome['error']=f'{type(exc).__name__}: {exc}'
    outcome['disk_observations']=guard.observations if guard else []
    outcome['elapsed_since_recovery_VM_start_seconds']=time.time()-cfg['vm_start_epoch']
    write_json(root/'completion.json',outcome)
    try:command('completion-upload',['/snap/bin/gcloud','storage','cp','--if-generation-match=0',str(root/'completion.json'),cfg['archive_prefix']+'/completion.json','--quiet'])
    except BaseException as exc:print('RECOVERY_COMPLETION_UPLOAD_UNAVAILABLE',str(exc),flush=True)
    print('E015_RECOVERY_EXIT',json.dumps({k:v for k,v in outcome.items()if k!='disk_observations'}),flush=True)
    return 0 if outcome['status']=='SUCCESS'else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--config',type=Path,required=True);a=parser.parse_args()
    cfg=json.loads(a.config.read_text());log=Path(cfg['root'])/'logs/parent-terminal.log'
    from e009_owner import Tee
    with log.open('x')as f:
        old=sys.stdout,sys.stderr;sys.stdout=Tee(sys.stdout,f);sys.stderr=Tee(sys.stderr,f)
        try:code=run(a.config)
        finally:sys.stdout,sys.stderr=old
    raise SystemExit(code)
