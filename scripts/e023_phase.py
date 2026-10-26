#!/usr/bin/env python3
"""Hold one E023 two-community cached grouping inside its two-hour VM-start envelope.

No VM/resource mutation, retry, installation or fallback occurs in this driver.
The controller must pass fresh financial/storage/native gates and arm a new
boot/process watcher plus independent provider STOP before release. All setup,
verification, science, hashes, upload and readback use the original VM-start clock.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_collect import binding
from e021_control_json import publish


def write_json(path,value):
    """Atomically publish controls polled by the native arm/controller."""
    publish(value,Path(path))
from e009_owner import supervisor,Tee
from e009_controls import PhaseGuard
from e009_exit_watchdog import identity

SECONDS=7200
STOP_SECONDS=8100


def publish_status(value):
    """Best-effort bounded guest status; never substitute it for exits/member review."""
    data=json.dumps(value).encode()
    if len(data)>32768:raise ValueError('Guest status exceeds compact bound')
    request=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e023-candidate/status',
        data=data,method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=3)as response:response.read(1024)
    except Exception as exc:print('GUEST_STATUS_UNAVAILABLE',str(exc),flush=True)


def compact_collection(path):
    """Bind the complete member receipt without duplicating its large maps in controls.

    Full inventory/omission evidence remains in the archive and separately
    uploaded collection.json. The atomic completion control has a 1 MiB cap.
    """
    path=Path(path);value=json.loads(path.read_text())
    if value.get('status')!='SUCCESS'or value.get('every_member_verified')is not True:
        raise ValueError('Complete all-member collection proof required')
    return dict(status=value['status'],archive=value['archive'],regular_members=value['regular_members'],
        logical_member_bytes=value['logical_member_bytes'],every_member_verified=True,
        aliases=len(value['aliases']),omitted_retained_members=len(value['omitted_retained_on_disk']),
        collection_receipt=binding(path),incomplete_failure_evidence=value.get('incomplete_failure_evidence',False),
        scope='Full inventory/omissions are in the archive and collection.json, not duplicated in this compact control')


def configuration(identity,repo,initial_filesystem_used_bytes,bindings):
    """Build the actual held-parent schema from a controller launch identity.

    The controller names its Git identity `source`; every native consumer requires
    `source_commit`. Keep this explicit translation tested rather than passing an
    unchecked controller dictionary through to a running service.
    """
    repo=Path(repo);root=Path(identity['root'])
    value=dict(identity,source_commit=identity['source'],repo=str(repo),
        science_plan=str(root/'science-plan.json'),
        reuse_lock=identity['input_lock'],
        storage_authorization_sha256=binding(repo/'experiments/E023-adaptive-density-bins/storage-admission.json')['sha256'],
        initial_filesystem_used_bytes=initial_filesystem_used_bytes,bindings=bindings)
    required={'root','service_name','source_commit','repo','science_plan','reuse_lock',
              'initial_filesystem_used_bytes','bindings','vm_start_epoch','archive_prefix'}
    if not required<=set(value) or len(value['source_commit'])!=40 or value['vm_start_epoch']<=0:
        raise ValueError('Incomplete held-parent configuration')
    return value


def admission(cfg,release,now):
    """Refuse drift in source, budget, complete credit coverage or original retention."""
    if not 0<=now-cfg['vm_start_epoch']<SECONDS-600:raise TimeoutError('Original two-hour clock unavailable')
    needed=['credit_gate_passed','pending_usage_accounted','native_gates_passed','watchdog_verified','existing_VM_only','full_axes_verified']
    if any(release.get(k)is not True for k in needed):raise ValueError('E023 release gate incomplete')
    if release['config']!=binding(cfg['_path']) or release['provider_STOP_seconds']!=STOP_SECONDS or release['ceiling_USD']!=3:
        raise ValueError('Frozen config/STOP/budget differs')
    import math
    if (release.get('real_money_authorized') is not False or not math.isfinite(release['estimated_incremental_gross_USD'])
            or not 0 <= release['estimated_incremental_gross_USD'] <= 3):
        raise ValueError('Strict credit-only finite gross ceiling required')
    if release['estimated_incremental_gross_USD']>3 or release['storage_retention_extended']is not False:
        raise ValueError('Cost or retention expansion refused')
    if release.get('storage_authorization_sha256')!=cfg['storage_authorization_sha256'] or release['storage_valid_until_epoch']>1793746800:
        raise ValueError('Approved November 4 storage boundary differs')
    if set(release['covered_costs'])!={'compute','disk','storage','network','operations'}:
        raise ValueError('Incomplete credit product coverage')
    if cfg['vm_start_epoch']+STOP_SECONDS>=min(release['credit_valid_until_epoch'],release['storage_valid_until_epoch']):
        raise ValueError('Original storage approval/credit expires before STOP')


def run(path):
    """Wait for the tested live watcher; run exactly one serial two-unit grouping DAG then seal."""
    path=Path(path);cfg=json.loads(path.read_text());cfg['_path']=str(path)
    root=Path(cfg['root']);logs=root/'logs';outcome=dict(status='FAILED',science_completed=False,stages=[],source=cfg['source_commit'])
    deadline=cfg['vm_start_epoch']+SECONDS;sup=supervisor();env=sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),TMPDIR=str(root/'tmp'),
               CLOUDSDK_STORAGE_PROCESS_COUNT='1',CLOUDSDK_STORAGE_THREAD_COUNT='2',CLOUDSDK_CORE_DISABLE_PROMPTS='1')
    write_json(root/'started.json',dict(pid=os.getpid(),epoch=time.time(),config=binding(path)))
    guard=None
    def command(name,argv,reserve=0):
        left=deadline-time.time()-reserve
        if left<10:raise TimeoutError('Original VM-start execution/collection clock exhausted')
        print('E023_STAGE_START',name,flush=True)
        publish_status(dict(status='RUNNING',stage=name,root=str(root),source=cfg['source_commit'],epoch=time.time()))
        r=sup.supervise(argv,logs/(name+'.log'),left,26_000_000_000,env,sample_root=os.getpid())
        outcome['stages'].append(dict(name=name,resources=r))
    try:
        growth=max(0,shutil.disk_usage(root).used-cfg['initial_filesystem_used_bytes'])
        with PhaseGuard(root,deadline-time.time(),growth_bytes=20*1024**3-growth) as guard:
            print('E023_HELD',os.getpid(),flush=True)
            publish_status(dict(status='HELD',root=str(root),source=cfg['source_commit'],epoch=time.time()))
            while not(root/'release.json').exists():
                if (root/'abort.json').exists():raise RuntimeError('Controller aborted held release; inspect retained gate failure')
                if time.time()-cfg['vm_start_epoch']>1800:raise TimeoutError('Held setup exhausted 30 minutes')
                time.sleep(.2)
            release=json.loads((root/'release.json').read_text());admission(cfg,release,time.time())
            watch=json.loads((logs/'watchdog-live-before-release.json').read_text())
            if watch['decision']!='workflow alive' or watch['expected_process']!=identity(os.getpid()) or watch['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():
                raise ValueError('Fresh boot/held-parent watcher differs')
            for filename,wanted in release.get('gate_files',{}).items():
                if binding(filename)!=wanted:raise ValueError('Native admission gate bytes differ')
            if not release.get('gate_files'):raise ValueError('Native gate receipts missing')
            if subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['repo'],text=True).strip()!=cfg['source_commit'] or subprocess.check_output(['git','status','--porcelain'],cwd=cfg['repo'],text=True).strip():
                raise ValueError('Exact clean source differs')
            if os.cpu_count()!=8 or not os.path.ismount('/srv/dl_binner'):raise ValueError('Existing allocation/mount differs')
            for p,b in cfg['bindings'].items():
                if binding(p)!=b:raise ValueError('Source/config/reuse binding differs')
            gate=json.loads((root/'gates/completion.json').read_text())
            if gate['status']!='SUCCESS' or gate['config']!=binding(path):raise ValueError('Native gate/config identity differs')
            argv=[json.loads(Path(cfg['science_plan']).read_text())['python'],'-I','-B',str(Path(cfg['repo'])/'scripts/e023_control.py'),'--plan',cfg['science_plan'],'--workflow']
            command('science',argv,reserve=600)
            plan=json.loads(Path(cfg['science_plan']).read_text())
            for unit in ['E009-E022','oral-E019']:
                accounting=json.loads((Path(plan['work'])/'units'/unit/'export/accounting.json').read_text())
                if set(accounting)!={'density','selected'}:raise ValueError('Missing full pre/post DNA accounting')
                if json.loads((Path(plan['work'])/'units'/unit/'audited.json').read_text())['status']!='PASS':raise ValueError('Native graph proof failed')
            outcome['science_completed']=True
            outcome['scientific_fits_completed']=0
            outcome['grouping_communities_completed']=2
            command('used-inputs-after',[plan['python'],'-I','-B',str(Path(cfg['repo'])/'scripts/e023_control.py'),'--plan',cfg['science_plan'],'--verify-inputs'])
    except BaseException as exc:outcome['error']=f'{type(exc).__name__}: {exc}'
    outcome['disk_observations']=guard.observations if guard else []
    write_json(root/'science-result.json',outcome)
    collection_guard=None
    try:
        growth=max(0,shutil.disk_usage(root).used-cfg['initial_filesystem_used_bytes'])
        with PhaseGuard(root,deadline-time.time(),growth_bytes=20*1024**3-growth) as collection_guard:
            evidence=root/'sealed-evidence';evidence.mkdir(exist_ok=False)
            for folder in ['logs','gates']:
                shutil.copytree(root/folder,evidence/folder)
            for p in root.iterdir():
                if p.is_file() and p.suffix in ['.json','.py']:shutil.copyfile(p,evidence/p.name)
            sources=evidence/'source';sources.mkdir()
            for pattern in ['e023_*.py']:
                for p in (Path(cfg['repo'])/'scripts').glob(pattern):shutil.copyfile(p,sources/p.name)
            for p in (Path(cfg['repo'])/'experiments/E023-adaptive-density-bins').iterdir():
                if p.is_file():shutil.copyfile(p,sources/p.name)
            module=sources/'density';module.mkdir()
            for p in (Path(cfg['repo'])/'src/dl_binner/density').glob('*.py'):shutil.copyfile(p,module/p.name)
            command('collection',[sys.executable,'-I','-B',str(Path(cfg['repo'])/'scripts/e023_collect.py'),'--work',str(root/'work'),'--evidence',str(evidence),'--output',str(root/'return')]+(['--allow-incomplete'] if not outcome['science_completed'] else []))
            outcome['collection']=compact_collection(root/'return/collection.json')
            for name in ['e023-evidence.tar.gz','e023-evidence.tar.gz.sha256','collection.json']:
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
    print('E023_PHASE_EXIT',json.dumps({k:v for k,v in outcome.items() if 'observations'not in k}),flush=True)
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
