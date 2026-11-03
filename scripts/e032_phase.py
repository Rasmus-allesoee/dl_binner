#!/usr/bin/env python3
"""Hold, gate, execute and collect one supervised E032 cached comparison.

Every setup/restore/consumer/delivery stage shares the first VM-start deadline.
There is no resource creation, retry, training, truth or retention extension.
The independent process watcher stops the node after this held parent exits.
"""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e021_control_json import publish
from e009_owner import supervisor
from e009_controls import PhaseGuard
from e009_exit_watchdog import identity

RETENTION=1794351600  # November 11 00:00 Copenhagen.


def validate_config(cfg,now=None):
    """Validate complete producer/consumer schema before starting any held service."""
    fields={'root','repo','source_commit','operations_source','vm_start_epoch','review_deadline_epoch',
        'provider_deadline_epoch','setup_deadline_epoch','service_name','user','archive_prefix','plan',
        'python','workflow_python','base','reference','wheel','gcloud','financial','initial_filesystem_used_bytes',
        'source_filesystem','limits'}
    if set(cfg)!=fields:raise ValueError('Incomplete/unknown E032 configuration')
    now=time.time() if now is None else now;f=cfg['financial'];limits=cfg['limits']
    if (cfg['source_commit']!=cfg['operations_source'] or len(cfg['source_commit'])!=40
        or cfg['review_deadline_epoch']!=cfg['vm_start_epoch']+limits['seconds']
        or not cfg['vm_start_epoch']<=now<cfg['review_deadline_epoch']
        or not cfg['review_deadline_epoch']<cfg['provider_deadline_epoch']<=cfg['vm_start_epoch']+limits['provider_STOP_seconds']
        or cfg['provider_deadline_epoch']>=RETENTION or limits['threads']!=4 or limits['RSS_bytes']!=26000000000
        or limits['reserve_bytes']!=25*1024**3 or limits['extra_bytes']!=12*1024**3
        or f['real_money_authorized'] is not False or f['coverage_status']!='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'
        or f['ceiling_USD']!=limits['ceiling_USD']
        or not 0<=now-f['credit_checked_epoch']<7200 or not 0<=now-f['checked_epoch']<7200
        or not math.isfinite(f['estimated_complete_gross_USD'])
        or not 0<=f['estimated_complete_gross_USD']<=f['ceiling_USD']
        or cfg['provider_deadline_epoch']>=min(f['storage_valid_until_epoch'],f['credit_valid_until_epoch'])):
        raise ValueError('E032 clock/credit/resource/source contract differs')
    return True


def status(value):
    """Publish compact progress only; stage receipts remain authoritative."""
    raw=json.dumps(dict(value,epoch=time.time())).encode()
    request=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e032-candidate/status',
        data=raw,method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=3) as f:f.read(1024)
    except Exception as e:print('E032_STATUS_UNAVAILABLE',repr(e),flush=True)


def run(path):
    """Gate all actual Linux consumers before the new serial scientific DAG."""
    path=Path(path);cfg=json.loads(path.read_text());validate_config(cfg)
    root=Path(cfg['root']);deadline=cfg['review_deadline_epoch'];work=root/'work';work.mkdir()
    logs=root/'logs';logs.mkdir(exist_ok=True);gates=root/'gates';gates.mkdir()
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),
        TMPDIR=str(root/'tmp'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',
        E032_RELEASE_FILE=str(root/'release.json'),CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED='false')
    result=dict(status='FAILED',science_completed=False,stages=[],scientific_fits=0)
    publish(dict(pid=os.getpid(),identity=identity(os.getpid()),epoch=time.time()),root/'started.json')
    def guard_space():
        current=shutil.disk_usage(root);source=shutil.disk_usage(cfg['source_filesystem'])
        if (min(current.free,source.free)<cfg['limits']['reserve_bytes']
            or current.used-cfg['initial_filesystem_used_bytes']>cfg['limits']['extra_bytes']):
            raise RuntimeError('E032 source/task reserve or cumulative growth refused')
    def command(label,argv,reserve=900):
        guard_space();remaining=deadline-time.time()-reserve
        if remaining<10:raise TimeoutError('Original E032 cumulative clock exhausted')
        status(dict(status='RUNNING',stage=label,root=str(root)))
        print('E032_STAGE_START',label,flush=True)
        try:v=sup.supervise(list(map(str,argv)),logs/(label+'.log'),remaining,26000000000,env,sample_root=os.getpid())
        except BaseException:
            r=logs/(label+'.exit.json');result['stages'].append(dict(stage=label,resources=json.loads(r.read_text()) if r.exists() else dict(exit_code=None)))
            raise
        result['stages'].append(dict(stage=label,resources=v));guard_space()
    try:
        status(dict(status='HELD',root=str(root)))
        while not(root/'release.json').exists():
            if time.time()>=cfg['setup_deadline_epoch']:raise TimeoutError('Held setup clock exhausted')
            time.sleep(.2)
        release=json.loads((root/'release.json').read_text());watch=json.loads((root/'logs/watchdog-live-before-release.json').read_text())
        if release['config']!=binding(path) or release['plan']!=binding(cfg['plan']) or not release['provider_STOP_verified'] or watch['expected_process']!=identity(os.getpid()) or watch['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():
            raise ValueError('Current boot/process/config/provider release differs')
        if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=cfg['source_commit'] or subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():
            raise ValueError('Exact clean scientific source differs')
        from e032_control import freeze
        write(gates/'source.json',freeze())
        with PhaseGuard(root,max(.001,deadline-time.time()),reserve_bytes=25*1024**3,growth_bytes=12*1024**3) as disk:
            from e023_gates import workflow_probe
            command('workflow-native-origin',[cfg['workflow_python'],'-I','-B','-c',workflow_probe('3.12.10','9.16.3')])
            command('package-install',[Path(cfg['base'])/'bin/python','-I','-B',ROOT/'scripts/e019_runtime.py','create',
                '--base',cfg['base'],'--destination',root/'env','--wheel',cfg['wheel'],'--output',gates/'package-install.json'])
            command('complete-native-runtime',[cfg['python'],'-I','-B',ROOT/'scripts/e027_runtime.py','--base',cfg['base'],
                '--reference',cfg['reference'],'--candidate-lock',ROOT/'experiments/E032-biological-candidate-selection/candidate-lock.json','--output',gates/'runtime.json'])
            from e029_gates import unit_command
            command('native-selection-unit-contracts',[cfg['python'],'-I','-B','-c',unit_command(ROOT,'test_selection')])
            command('native-tiny-readers-export-reload',[cfg['python'],'-I','-B',ROOT/'scripts/e032_tiny.py','--root',gates/'tiny',
                '--workflow-python',cfg['workflow_python']])
            command('native-synthetic-scale',[cfg['python'],'-I','-B',ROOT/'scripts/e032_scale.py','--output',gates/'scale.json'])
            command('read-only-depth-input-audit',['/usr/bin/python3','-I','-B',ROOT/'scripts/e032_depth_audit.py','--output',gates/'depth-audit'])
            command('generation-bound-E031-restore',['/usr/bin/python3','-I','-B',ROOT/'scripts/e032_restore.py',
                '--lock',ROOT/'experiments/E032-biological-candidate-selection/restore-lock.json','--root',root/'restored','--gcloud',cfg['gcloud']])
            scale=json.loads((gates/'scale.json').read_text())
            shapes=json.loads((ROOT/'experiments/E032-biological-candidate-selection/reuse-lock.json').read_text())['axes']
            forecast=max(3600.,scale['wall_seconds']*sum(v['eligible'] for v in shapes.values())/scale['rows']*4+1200)
            passed=time.time()+forecast+900<deadline
            write(gates/'complete-schedule.json',dict(status='PASS' if passed else 'REFUSED',
                forecast_remaining_seconds=forecast,remaining_seconds=deadline-time.time(),
                scope='Native synthetic profile/selection scaling with 4x allowance plus restore/collection; no measured community guarantee'))
            if not passed:raise ValueError('Complete E032 forecast needs a recorded credit-covered envelope revision')
            publish(dict(status='PASS',stages=result['stages'],source=freeze()),gates/'completion.json')
            command('serial-cached-comparison',[cfg['python'],'-I','-B',ROOT/'scripts/e032_control.py','--plan',cfg['plan'],'--workflow'])
            if not all((work/u/'audit/done.json').is_file() for u in ['E009-noGLM','E009-GLM','oral-noGLM']):
                raise ValueError('All three independent final targets required')
            command('restored-inputs-after',['/usr/bin/python3','-I','-B',ROOT/'scripts/e032_restore.py',
                '--root',root/'restored','--verify-after',work/'used-inputs-after.json'])
            result['science_completed']=True
            with(root/'disk-samples.jsonl').open('x') as f:
                for value in disk.observations:f.write(json.dumps(value)+'\n')
    except BaseException as e:result['error']=repr(e)
    result['status']='SCIENCE_COMPLETED_PENDING_COLLECTION' if result['science_completed'] else 'FAILED'
    publish(result,root/'science-result.json')
    try:
        evidence=root/'sealed-evidence';evidence.mkdir()
        for name in ['config.json','host.json','release.json','started.json','science-plan.json','science-result.json','disk-samples.jsonl']:
            if(root/name).is_file():shutil.copyfile(root/name,evidence/name)
        for folder in ['logs','gates']:
            shutil.copytree(root/folder,evidence/folder)
        command('collect',['/usr/bin/python3','-I','-B',ROOT/'scripts/e032_collect.py',
            '--work',work,'--evidence',evidence,'--output',root/'collection'],reserve=600)
        from e030_phase import upload_command
        for name in ['e032-evidence.tar.gz','e032-evidence.tar.gz.sha256','collection.json']:
            local=root/'collection'/name;uri=cfg['archive_prefix']+name
            command('upload-'+name,upload_command(cfg['gcloud'],local,uri),reserve=120)
            command('readback-'+name,['/usr/bin/python3','-I','-B',ROOT/'scripts/e030_phase.py','--readback',uri,
                '--gcloud',cfg['gcloud'],'--bytes',str(local.stat().st_size),'--sha256',binding(local)['sha256']],reserve=60)
        result.update(collection_readback_verified=True,status='SUCCESS' if result['science_completed'] else 'FAILED')
    except BaseException as e:result['collection_error']=repr(e)
    result['finished_epoch']=time.time();result['source']=cfg['source_commit'];result['root']=str(root)
    publish(result,root/'completion.json')
    status(dict(status='PENDING_COMPLETION_DELIVERY',root=str(root),science_completed=result['science_completed']))
    from e021_portable_node import storage_upload
    try:
        if time.time()>deadline-30:raise TimeoutError('Original clock cannot admit final delivery')
        delivered=storage_upload(root/'completion.json',cfg['archive_prefix']+'completion.json')
        receipt=dict(exit_code=0,private_readback=delivered,epoch=time.time())
        write(root/'logs/completion-upload.exit.json',receipt)
        tail=storage_upload(root/'logs/completion-upload.exit.json',cfg['archive_prefix']+'completion-upload-exit.json')
        write(root/'closed-delivery-tail.json',dict(status='PASS',completion=delivered,completion_exit=tail))
    except BaseException as e:
        if not(root/'logs/completion-upload.exit.json').exists():
            write(root/'logs/completion-upload.exit.json',dict(exit_code=1,error=repr(e),epoch=time.time()))
        status(dict(status='FAILED_FINAL_DELIVERY',root=str(root),science_completed=result['science_completed']))
        print('E032_COMPLETION_DELIVERY_FAILED',repr(e),flush=True);return 1
    status(dict(status=result['status'],root=str(root),science_completed=result['science_completed'],completion_delivery_verified=True))
    return 0 if result['status']=='SUCCESS' else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True)
    a=p.parse_args();sys.exit(run(a.config))
