#!/usr/bin/env python3
"""Hold one E021 two-fit candidate inside its 48-hour VM-start envelope.

This is a separately locked operational GPU envelope; the f136b2c science stays fixed.
No VM/resource mutation, retry, installation or fallback occurs in this driver.
The controller must pass fresh financial/storage/native gates and arm a new
boot/process watcher plus independent provider STOP before release. All setup,
verification, science, hashes, upload and readback use the original VM-start clock.
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

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_collect import binding
from e009_common import write_json
from e009_owner import supervisor,Tee
from e021_gpu_guard import GPUPhaseGuard as PhaseGuard, sample_gpu
from e009_controls import PhaseGuard as CollectionGuard
from e009_exit_watchdog import identity

SECONDS=48*3600
STOP_SECONDS=48*3600+900


def publish_status(value):
    """Best-effort bounded guest status; never substitute it for exits/member review."""
    data=json.dumps(value).encode()
    if len(data)>32768:raise ValueError('Guest status exceeds compact bound')
    request=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e021-candidate/status',
        data=data,method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=3)as response:response.read(1024)
    except Exception as exc:print('GUEST_STATUS_UNAVAILABLE',str(exc),flush=True)


def configuration(identity,repo,initial_filesystem_used_bytes,bindings):
    """Build the actual held-parent schema from a controller launch identity.

    The controller names its Git identity `source`; every native consumer requires
    `source_commit`. Keep this explicit translation tested rather than passing an
    unchecked controller dictionary through to a running service.
    """
    repo=Path(repo);root=Path(identity['root'])
    value=dict(identity,source_commit=identity['source'],repo=str(repo),
        science_plan=str(root/'science-plan.json'),
        reuse_lock=str(repo/'experiments/E021-frozen-sequence-hybrid/reuse-lock.json'),
        wheel=identity.get('wheel',str(root/'payload/dl_binner-0.1.0.dev8-py3-none-any.whl')),
        initial_filesystem_used_bytes=initial_filesystem_used_bytes,bindings=bindings)
    required={'root','service_name','source_commit','repo','science_plan','reuse_lock',
              'initial_filesystem_used_bytes','bindings','vm_start_epoch','archive_prefix','wheel'}
    if not required<=set(value) or len(value['source_commit'])!=40 or value['vm_start_epoch']<=0:
        raise ValueError('Incomplete held-parent configuration')
    return value


def admission(cfg,release,now):
    """Refuse drift in source, budget, complete credit coverage or original retention."""
    if not 0<=now-cfg['vm_start_epoch']<SECONDS-600:raise TimeoutError('Original 48-hour clock unavailable')
    needed=['credit_gate_passed','pending_usage_accounted','native_gates_passed','watchdog_verified','existing_VM_only','full_axes_verified','frozen_extraction_runtime_passed','full_scale_RAM_passed','native_throughput_and_return_admitted','local_review_headroom_passed','GPU_credit_coverage_passed','GPU_runtime_and_numerics_passed','storage_cleanup_review_passed','GPU_guard_verified']
    if any(release.get(k)is not True for k in needed):raise ValueError('E021 release gate incomplete')
    if release['config']!=binding(cfg['_path']) or release['provider_STOP_seconds']!=STOP_SECONDS or release['ceiling_USD']!=45:
        raise ValueError('Frozen config/STOP/budget differs')
    cost=release.get('estimated_incremental_gross_USD')
    if (type(cost)not in [int,float]or not math.isfinite(cost)or not 0<=cost<=45
            or release.get('storage_retention_extended')is not False or release.get('compressed_export_GiB')!=2
            or release['storage_valid_until_epoch']>1793142000):
        raise ValueError('Cost, return or retention expansion refused')
    if set(release['covered_costs'])!={'compute','gpu','disk','storage','network','operations'}:
        raise ValueError('Incomplete credit product coverage')
    if cfg['vm_start_epoch']+STOP_SECONDS>=min(release['credit_valid_until_epoch'],release['storage_valid_until_epoch']):
        raise ValueError('Original storage approval/credit expires before STOP')


def run(path):
    """Wait for the tested live watcher; run exactly one serial two-unit DAG then seal."""
    path=Path(path);cfg=json.loads(path.read_text());cfg['_path']=str(path)
    root=Path(cfg['root']);logs=root/'logs';outcome=dict(status='FAILED',science_completed=False,stages=[],source=cfg['source_commit'])
    deadline=cfg['vm_start_epoch']+SECONDS;sup=supervisor();env=sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),TMPDIR=str(root/'tmp'),
               NVIDIA_TF32_OVERRIDE='0',CUBLAS_WORKSPACE_CONFIG=':4096:8',
               HF_MODULES_CACHE=str(root/'model-module-cache'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',
               CLOUDSDK_STORAGE_PROCESS_COUNT='1',CLOUDSDK_STORAGE_THREAD_COUNT='2',CLOUDSDK_CORE_DISABLE_PROMPTS='1')
    write_json(root/'started.json',dict(pid=os.getpid(),epoch=time.time(),config=binding(path)))
    guard=None
    def command(name,argv,reserve=0):
        left=deadline-time.time()-reserve
        if left<10:raise TimeoutError('Original VM-start execution/collection clock exhausted')
        print('E021_STAGE_START',name,flush=True)
        publish_status(dict(status='RUNNING',stage=name,root=str(root),source=cfg['source_commit'],epoch=time.time()))
        r=sup.supervise(argv,logs/(name+'.log'),left,26_000_000_000,env,sample_root=os.getpid())
        outcome['stages'].append(dict(name=name,resources=r))
    try:
        growth=max(0,shutil.disk_usage(root).used-cfg['initial_filesystem_used_bytes'])
        with PhaseGuard(root,deadline-time.time(),growth_bytes=32*1024**3-growth,wait_for_ready=True) as guard:
            print('E021_HELD',os.getpid(),flush=True)
            publish_status(dict(status='HELD',root=str(root),source=cfg['source_commit'],epoch=time.time()))
            while not(root/'release.json').exists():
                if (root/'abort.json').exists():raise RuntimeError('Controller aborted held release; inspect retained gate failure')
                if time.time()-cfg['vm_start_epoch']>7200:raise TimeoutError('Held setup exhausted two hours within original 48-hour clock')
                time.sleep(.2)
            release=json.loads((root/'release.json').read_text());admission(cfg,release,time.time())
            watch=json.loads((logs/'watchdog-live-before-release.json').read_text())
            if watch['decision']!='workflow alive' or watch['expected_process']!=identity(os.getpid()) or watch['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():
                raise ValueError('Fresh boot/held-parent watcher differs')
            if subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['repo'],text=True).strip()!=cfg['source_commit'] or subprocess.check_output(['git','status','--porcelain'],cwd=cfg['repo'],text=True).strip():
                raise ValueError('Exact clean source differs')
            if os.cpu_count()!=8 or not os.path.ismount('/srv/dl_binner'):raise ValueError('Existing allocation/mount differs')
            gpu=sample_gpu()
            live=json.loads((root/'logs/gpu-guard-live.json').read_text())
            if live.get('status')!='LIVE_NATIVE_TELEMETRY'or live.get('gpu_uuid')!=gpu['uuid']or live.get('guard_pid')!=os.getpid():raise ValueError('Current held-parent GPU guard not verified')
            if release.get('gpu_uuid')!=gpu['uuid']or release.get('gpu_ready')!=binding(root/'gpu-ready.json'):raise ValueError('Admitted native GPU identity differs')
            if json.loads(Path(cfg['science_plan']).read_text())['extract_device']!='cuda':raise ValueError('Frozen GPU extraction plan required')
            for p,b in cfg['bindings'].items():
                if binding(p)!=b:raise ValueError('Source/config/reuse binding differs')
            gate=json.loads((root/'gates/completion.json').read_text())
            if gate['status']!='SUCCESS' or gate['config']!=binding(path):raise ValueError('Native gate/config identity differs')
            argv=[json.loads(Path(cfg['science_plan']).read_text())['python'],'-I','-B',str(Path(cfg['repo'])/'scripts/e021_control.py'),'--plan',cfg['science_plan'],'--workflow']
            command('science',argv,reserve=600)
            plan=json.loads(Path(cfg['science_plan']).read_text())
            for unit in ['E009-hybrid','oral-hybrid']:
                accounting=json.loads((Path(plan['work'])/'units'/unit/'export/accounting.json').read_text())
                if set(accounting)!={'pre','old','post'}:raise ValueError('Missing full pre/post DNA accounting')
                if json.loads((Path(plan['work'])/'units'/unit/'graph-proof.json').read_text())['status']!='PASS':raise ValueError('Native graph proof failed')
            outcome['science_completed']=True
            command('reuse-after',[sys.executable,'-I','-B',str(Path(cfg['repo'])/'scripts/e020_reuse.py'),'--lock',cfg['reuse_lock'],'--output',str(root/'reuse-after.json')])
    except BaseException as exc:outcome['error']=f'{type(exc).__name__}: {exc}'
    outcome['disk_observations']=guard.observations if guard else []
    if outcome['science_completed']and'error'not in outcome:outcome['status']='SCIENCE_COMPLETED_PENDING_COLLECTION'
    write_json(root/'science-result.json',outcome)
    collection_guard=None
    try:
        growth=max(0,shutil.disk_usage(root).used-cfg['initial_filesystem_used_bytes'])
        with CollectionGuard(root,deadline-time.time(),growth_bytes=32*1024**3-growth) as collection_guard:
            evidence=root/'sealed-evidence';evidence.mkdir(exist_ok=False)
            for folder in ['logs','gates']:
                shutil.copytree(root/folder,evidence/folder)
            for p in root.iterdir():
                if p.is_file() and p.suffix in ['.json','.py']:shutil.copyfile(p,evidence/p.name)
            sources=evidence/'source';sources.mkdir()
            for pattern in ['e021_*.py']:
                for p in (Path(cfg['repo'])/'scripts').glob(pattern):shutil.copyfile(p,sources/p.name)
            for p in (Path(cfg['repo'])/'experiments/E021-frozen-sequence-hybrid').iterdir():
                if p.is_file():shutil.copyfile(p,sources/p.name)
            command('collection',[sys.executable,'-I','-B',str(Path(cfg['repo'])/'scripts/e021_collect.py'),'--work',str(root/'work'),'--evidence',str(evidence),'--output',str(root/'return')]+(['--allow-incomplete'] if not outcome['science_completed'] else []))
            collection=json.loads((root/'return/collection.json').read_text());outcome['collection']=collection
            for name in ['e021-evidence.tar.gz','e021-evidence.tar.gz.sha256','collection.json']:
                uri=cfg['archive_prefix']+'/'+name
                command('upload-'+name,['/snap/bin/gcloud','storage','cp','--if-generation-match=0',str(root/'return'/name),uri,'--quiet'])
                command('readback-'+name,['/snap/bin/gcloud','storage','cp',uri,str(root/('readback-'+name)),'--quiet'])
                if binding(root/('readback-'+name))!=binding(root/'return'/name):raise ValueError('Private archive readback differs')
            outcome['private_readback_verified']=True
            if outcome['science_completed'] and 'error' not in outcome:outcome['status']='SUCCESS'
    except BaseException as exc:outcome['collection_error']=f'{type(exc).__name__}: {exc}'
    outcome['collection_disk_observations']=collection_guard.observations if collection_guard else []
    outcome['elapsed_since_VM_start_seconds']=time.time()-cfg['vm_start_epoch']
    write_json(root/'completion.json',outcome)
    try:command('completion-upload',['/snap/bin/gcloud','storage','cp','--if-generation-match=0',str(root/'completion.json'),cfg['archive_prefix']+'/completion.json','--quiet'])
    except BaseException as exc:print('COMPLETION_UPLOAD_UNAVAILABLE',str(exc),flush=True)
    print('E021_PHASE_EXIT',json.dumps({k:v for k,v in outcome.items() if 'observations'not in k}),flush=True)
    publish_status(dict(status=outcome['status'],science_completed=outcome['science_completed'],
        private_readback_verified=outcome.get('private_readback_verified',False),root=str(root),
        source=cfg['source_commit'],completion=binding(root/'completion.json'),epoch=time.time()))
    return 0 if outcome['status']=='SUCCESS'else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text());log=Path(cfg['root'])/'logs/parent-terminal.log'
    with log.open('x') as f:
        old=sys.stdout,sys.stderr;sys.stdout=Tee(sys.stdout,f);sys.stderr=Tee(sys.stderr,f)
        try:code=run(a.config)
        finally:sys.stdout,sys.stderr=old
    raise SystemExit(code)
