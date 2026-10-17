#!/usr/bin/env python3
"""Run one explicitly approved held E011 phase under its original VM-start clock.

All setup, restore, native gates, serial CPM/MetaBAT2 commands and collection share
30 minutes. The external boot/process watcher and 45-minute provider STOP own
shutdown. There is no retry, resize, new encoder, scientific tuning or truth path.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding,write_json
from e009_controls import PhaseGuard
from e009_owner import supervisor,Tee
from e010_candidate import collect


def verify_admission(cfg, release, now):
    """Require this run's fresh source/credit/storage/STOP and held-parent proof."""
    if not 0<=now-cfg['vm_start_epoch']<1500:raise TimeoutError('Original 30-minute clock unavailable')
    needed={'credit_gate_passed':True,'pending_usage_accounted':True,'watchdog_release_verified':True,
            'provider_stop_seconds':2700,'incremental_gross_ceiling_usd':1,
            'no_resource_change':True,'storage_retention_extended':False}
    if any(release.get(k)!=v for k,v in needed.items()):raise ValueError('E011 admission incomplete')
    if cfg['vm_start_epoch']+2700>=min(release['credit_valid_until_epoch'],release['storage_valid_until_epoch']):
        raise ValueError('Credit/storage approval expires before STOP')
    if set(release['covered_costs'])!={'compute','disk','storage','network','operations'}:
        raise ValueError('Cost coverage incomplete')


def publish(value):
    """Best-effort compact guest status; never prevent parent exit on API failure."""
    value={k:v for k,v in value.items()if k not in ('stages','disk_observations','collection_disk_observations')}
    if 'control_archive'in value:
        value['control_archive']={k:v for k,v in value['control_archive'].items()if k!='collection'}
    request=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e011-cached/status',
        data=json.dumps(value).encode(),method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=5)as response:response.read()
    except Exception as exc:print('GUEST_STATUS_UNAVAILABLE '+str(exc),flush=True)


def run(config_path):
    """Hold for supervision, run each command once, seal/verify and upload closed evidence."""
    config_path=Path(config_path);cfg=json.loads(config_path.read_text());phase=Path(cfg['phase_root']);logs=phase/'logs'
    results=phase/'run';results.mkdir(exist_ok=False);logs.mkdir(exist_ok=True)
    if (phase/'started.json').exists():raise ValueError('Existing phase; no retry/resume')
    remaining=1800-(time.time()-cfg['vm_start_epoch'])
    if not 300<remaining<=1800:raise TimeoutError('Insufficient original clock for setup/work/collection')
    initial_growth=max(0,shutil.disk_usage(phase).used-cfg['initial_filesystem_used_bytes'])
    if initial_growth>=20*1024**3:raise ValueError('Preparation exhausted extra-space allowance')
    write_json(phase/'started.json',dict(pid=os.getpid(),config=binding(config_path),remaining_seconds=remaining,preparation_growth_bytes=initial_growth))
    deadline=time.monotonic()+remaining;sup=supervisor();env=sup.isolated_env(8)
    env.update(CLOUDSDK_STORAGE_PROCESS_COUNT='1',CLOUDSDK_STORAGE_THREAD_COUNT='2',CLOUDSDK_CORE_DISABLE_PROMPTS='1')
    outcome=dict(status='FAILED',phase_id=cfg['phase_id'],source_commit=cfg['source_commit'],
                 cpm_completed=False,metabat_completed=False,cloud_collection_verified=False,stages=[])
    def command(argv,name,reserve=0):
        seconds=deadline-time.monotonic()-reserve
        if seconds<=0:raise TimeoutError('Original cumulative E011 clock exhausted')
        return sup.supervise(argv,logs/(name+'.log'),seconds,26_000_000_000,env,sample_root=os.getpid())
    def transfer(path,name):
        path=Path(path);uri=cfg['archive_prefix']+'/'+name
        command(['/snap/bin/gcloud','storage','cp','--if-generation-match=0',str(path),uri,'--quiet'],'upload-'+name)
        back=phase/('readback-'+name)
        command(['/snap/bin/gcloud','storage','cp',uri,str(back),'--quiet'],'readback-'+name)
        if binding(path)!=binding(back):raise ValueError('Private readback differs')
        return dict(uri=uri,**binding(path),readback_verified=True)
    try:
        with PhaseGuard(phase,remaining,growth_bytes=20*1024**3-initial_growth)as guard:
            print('E011_HELD_FOR_CURRENT_WATCHDOG pid='+str(os.getpid()),flush=True)
            while not Path(cfg['release_file']).exists():time.sleep(.2)
            release=json.loads(Path(cfg['release_file']).read_text());verify_admission(cfg,release,time.time())
            if release['phase_config']!=binding(config_path):raise ValueError('Release/config differs')
            from e009_exit_watchdog import identity
            watched=json.loads((logs/'watchdog-live-before-release.json').read_text())
            if (watched['decision']!='workflow alive' or watched['expected_process']!=identity(os.getpid())
                    or watched['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip()):
                raise ValueError('Current held parent watchdog identity differs')
            actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['repo'],text=True).strip()
            if actual!=cfg['source_commit'] or subprocess.check_output(['git','status','--porcelain'],cwd=cfg['repo'],text=True).strip():
                raise ValueError('Exact clean pushed source required')
            if not os.path.ismount('/srv/dl_binner')or os.cpu_count()!=8:raise ValueError('Existing native VM/mount differs')
            ram_kib=int(next(line.split()[1]for line in Path('/proc/meminfo').read_text().splitlines()if line.startswith('MemTotal:')))
            if not 30*1024**2<=ram_kib<=35*1024**2:raise ValueError('Existing 32-GiB VM RAM differs')
            for step in cfg['stages']:
                print('E011_STAGE_START '+step['name'],flush=True)
                receipt=command(step['argv'],step['name'],reserve=180)
                outcome['stages'].append(dict(name=step['name'],resources=receipt))
                if step['name']=='cpm':outcome['cpm_completed']=True
                if step['name']=='metabat-export':outcome['metabat_completed']=True
                publish({k:v for k,v in outcome.items()if k!='stages'}|{'status':'RUNNING','latest_completed':step['name']})
            if not outcome['cpm_completed']or not outcome['metabat_completed']:raise ValueError('Missing control/reference completion')
            outcome.update(status='SUCCESS',disk_observations=guard.observations)
    except BaseException as exc:outcome.update(status='FAILED',error=f'{type(exc).__name__}: {exc}')
    outcome['elapsed_since_VM_start_seconds']=time.time()-cfg['vm_start_epoch']
    # Collection remains inside the same deadline and cannot launch scientific work.
    try:
        if deadline-time.monotonic()<20:raise TimeoutError('No original clock for compact collection; evidence retained on disk')
        growth=max(0,shutil.disk_usage(phase).used-cfg['initial_filesystem_used_bytes'])
        with PhaseGuard(phase,deadline-time.monotonic(),growth_bytes=20*1024**3-growth)as collection_guard:
            write_json(results/'phase-result.json',outcome)
            for path in sorted(logs.iterdir()):
                if path.is_file()and path.name!='parent-terminal.log':shutil.copyfile(path,results/('log-'+path.name))
            for path in [config_path,phase/'release.json',phase/'started.json']:
                if path.is_file():shutil.copyfile(path,results/path.name)
            terminal=logs/'parent-terminal.log'
            if terminal.exists():(results/'terminal.snapshot.log').write_bytes(terminal.read_bytes())
            collection=collect(results)
            archive_name=Path(collection['path']).name
            outcome['control_archive']=transfer(collection['path'],archive_name)
            outcome['control_archive']['collection']=collection
            outcome['control_checksum']=transfer(collection['path']+'.sha256',archive_name+'.sha256')
            outcome['cloud_collection_verified']=True
        outcome['collection_disk_observations']=collection_guard.observations
    except BaseException as exc:outcome.update(status='FAILED',collection_error=f'{type(exc).__name__}: {exc}')
    write_json(phase/'completion.json',outcome)
    try:transfer(phase/'completion.json','completion.json')
    except BaseException as exc:outcome['completion_upload_error']=str(exc)
    publish(outcome);print('E011_PHASE_EXIT='+json.dumps(outcome,sort_keys=True),flush=True)
    return 0 if outcome['status']=='SUCCESS'else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text());terminal=Path(cfg['phase_root'])/'logs/parent-terminal.log'
    terminal.parent.mkdir(exist_ok=True);previous=sys.stdout,sys.stderr
    with terminal.open('x')as stream:
        sys.stdout=Tee(sys.stdout,stream);sys.stderr=Tee(sys.stderr,stream)
        try:code=run(a.config)
        finally:sys.stdout,sys.stderr=previous
    raise SystemExit(code)
