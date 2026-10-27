#!/usr/bin/env python3
"""Hold/run/collect one future E024 phase under externally admitted supervision.

Preparation only: this module has no VM-start, resize, quota or IAM operation.
All setup/science/verification/upload use the original VM-start clock. A fresh
boot/process-bound exit watcher and provider STOP must be independently proved
before release; the watcher, not this chat/SSH session, owns eventual shutdown.
Operational recovery uses a fresh recorded attempt and verified seals within
the same cumulative allocation; this driver never retries automatically.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e024_coverage import binding
from e021_control_json import publish
from e009_owner import supervisor
from e009_controls import PhaseGuard
from e009_exit_watchdog import identity

SECONDS=36*3600
STOP_SECONDS=int(36.25*3600)
RETENTION_EPOCH=1793746800  # November 4 00:00 Copenhagen = November 3 23:00 UTC.


def disk_summary(samples, initial_used):
    """Keep long-run controls compact; raw two-second observations are separate.

    A 36-hour run can have about 65,000 observations, exceeding the atomic JSON
    control limit if embedded verbatim. Report global sampled growth against the
    first allocation snapshot, not a reset guard-local counter.
    """
    return dict(samples=len(samples),minimum_free_bytes=min((s['free'] for s in samples),default=None),
                maximum_sampled_global_growth_bytes=max(0,max((s['used']-initial_used for s in samples),default=0)),
                scope='Sampled whole-filesystem usage; first-allocation baseline, not exact attributable bytes')


def save_disk_samples(path,samples):
    """Preserve closed raw observations without the polled-control size limit."""
    with Path(path).open('x') as f:
        for value in samples:f.write(json.dumps(value,separators=(',',':'))+'\n')


def upload_command(gcloud,local,remote):
    """Require a new private object; never overwrite an accepted generation."""
    return [str(gcloud),'storage','cp','--if-generation-match=0',str(local),str(remote)]


def status(value):
    """Publish compact timestamped guest progress; logs/receipts remain authoritative."""
    data=json.dumps(dict(value,epoch=time.time())).encode()
    if len(data)>32768:raise ValueError('Compact guest attribute exceeded')
    request=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e024-candidate/status',
        data=data,method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=3) as response:response.read(1024)
    except Exception as exc:print('E024_GUEST_STATUS_UNAVAILABLE',repr(exc),flush=True)


def admission(cfg, release, now):
    """Require finite fresh credit-only complete-cost coverage and original limits."""
    import math
    needed=['credit_gate_passed','pending_usage_accounted','native_gates_passed',
            'watchdog_verified','provider_STOP_verified','existing_VM_only','full_axes_verified',
            'headroom_measured','retention_passed']
    if any(release.get(k) is not True for k in needed):
        raise ValueError('Fresh complete external admission required')
    if (not 0 <= now-cfg['vm_start_epoch'] < SECONDS-3600 or release.get('real_money_authorized') is not False
            or type(release.get('estimated_incremental_gross_USD')) not in (int,float)
            or not math.isfinite(release['estimated_incremental_gross_USD'])
            or not 0 <= release['estimated_incremental_gross_USD'] <= 15
            or release.get('ceiling_USD') != 15 or release.get('provider_STOP_seconds') != STOP_SECONDS
            or release.get('storage_retention_extended') is not False):
        raise ValueError('Original clock/credit-only gross ceiling/STOP differs')
    if (set(release.get('covered_costs',[])) != {'compute','disk','storage','network','operations'}
            or cfg['vm_start_epoch']+STOP_SECONDS >= min(release['credit_valid_until_epoch'],release['storage_valid_until_epoch'])
            or release['storage_valid_until_epoch'] > RETENTION_EPOCH
            or release['config'] != binding(cfg['_path']) or not release.get('gate_files')):
        raise ValueError('Complete product/config/retention binding differs')
    if 'plan' in cfg and (release.get('plan')!=binding(cfg['plan']) or release.get('vm_start_epoch')!=cfg['vm_start_epoch']):
        raise ValueError('Active plan/original cumulative start differs')
    for path,wanted in release['gate_files'].items():
        if binding(path) != wanted:
            raise ValueError('Gate/source/runtime proof bytes differ')


def service_content(root, python, script, cfg, user):
    """Render the actual held-parent service without shell interpolation hazards."""
    import shlex
    if any('\n' in str(x) or '%' in str(x) for x in [root,python,script,cfg,user]):
        raise ValueError('Unsafe service field')
    argv=' '.join(shlex.quote(str(x)) for x in [python,'-I','-B',script,'--config',cfg])
    return ('[Unit]\nDescription=E024 bounded oral measured coverage\nAfter=network-online.target\n'
            '[Service]\nType=simple\nUser='+str(user)+'\nWorkingDirectory='+str(root)+'\n'
            'ExecStart='+argv+'\nRestart=no\nKillMode=control-group\nTimeoutStopSec=20\n'
            'StandardOutput=append:'+str(root)+'/terminal.log\nStandardError=append:'+str(root)+'/terminal.log\n')


def run(config):
    """Wait held, verify watcher/release, run the sole DAG, seal/upload/read back once."""
    config=Path(config);cfg=json.loads(config.read_text());cfg['_path']=str(config)
    root=Path(cfg['root']);work=Path(cfg['work']);work.mkdir(parents=True,exist_ok=True)
    logs=root/'phase-logs';logs.mkdir(exist_ok=False)
    deadline=cfg['vm_start_epoch']+SECONDS
    p=json.loads(Path(cfg['plan']).read_text())
    if str(work) != p['work'] or cfg['limits'] != p['limits'] or not root.is_relative_to('/srv/dl_binner/experiments/e024'):
        raise ValueError('Plan/config work or limits differ')
    sup=supervisor();env=sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),
               TMPDIR=str(root/'tmp'),CLOUDSDK_CORE_DISABLE_PROMPTS='1',
               CLOUDSDK_STORAGE_PROCESS_COUNT='1',CLOUDSDK_STORAGE_THREAD_COUNT='2',
               E024_RELEASE_FILE=str(root/'release.json'),XDG_CACHE_HOME=str(root/'tool-cache'))
    (root/'tmp').mkdir(exist_ok=True)
    result=dict(status='FAILED',stages=[],science_completed=False,scientific_fits_completed=0)
    command_samples=[];science_guard=None;collection_guard=None
    publish(dict(pid=os.getpid(),identity=identity(os.getpid()),epoch=time.time()),root/'started.json')
    def command(label,argv,reserve=0):
        remaining=deadline-time.time()-reserve
        if remaining < 10:raise TimeoutError('Original cumulative E024 clock exhausted')
        def disk_check():
            usage=shutil.disk_usage(root)
            command_samples.append(dict(stage=label,epoch=time.time(),used=usage.used,free=usage.free))
            if usage.free<25*1024**3 or usage.used-cfg['initial_filesystem_used_bytes']>24*1024**3:
                raise RuntimeError('Whole-allocation disk reserve/growth exceeded')
        disk_check()
        print('E024_STAGE_START',label,flush=True)
        status(dict(status='RUNNING',stage=label,root=str(root)))
        result['stages'].append(dict(name=label,resources=sup.supervise(argv,logs/(label+'.log'),
            remaining,26_000_000_000,env,sample_root=os.getpid())))
        disk_check()
    try:
        growth=max(0,shutil.disk_usage(root).used-cfg['initial_filesystem_used_bytes'])
        with PhaseGuard(root,deadline-time.time(),growth_bytes=max(0,24*1024**3-growth)) as science_guard:
            status(dict(status='HELD',root=str(root),process=identity(os.getpid())))
            while not (root/'release.json').exists():
                if (root/'abort.json').exists():raise RuntimeError('External controller refused release')
                if time.time() >= min(deadline-3600,cfg['vm_start_epoch']+3600):
                    raise TimeoutError('One-hour held native setup admission exhausted')
                time.sleep(.2)
            release=json.loads((root/'release.json').read_text());admission(cfg,release,time.time())
            watch=json.loads(Path(cfg['watchdog_live']).read_text())
            if (watch['decision'] != 'workflow alive' or watch['expected_process'] != identity(os.getpid())
                    or watch['boot_id'] != Path('/proc/sys/kernel/random/boot_id').read_text().strip()):
                raise ValueError('Fresh current-boot held-process watcher proof differs')
            if (subprocess.check_output(['git','rev-parse','HEAD'],cwd=cfg['repo'],text=True).strip() != cfg['source_commit']
                    or subprocess.check_output(['git','status','--porcelain'],cwd=cfg['repo'],text=True).strip()):
                raise ValueError('Exact clean committed source required')
            if os.cpu_count() != 8 or not os.path.ismount('/srv/dl_binner'):
                raise ValueError('Original existing CPU/mount differs')
            from e024_gates import freeze
            freeze()
            gate=json.loads((root/'gates/completion.json').read_text())
            if gate.get('status')!='PASS' or gate['config']!=binding(config):
                raise ValueError('Native gate/config identity differs')
            if hasattr(os,'sched_setaffinity'):
                os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[:8])
            command('workflow',[p['python'],'-I','-B',p['worker'],'--plan',cfg['plan'],'--workflow'],reserve=3600)
            if not (work/'audited/done.json').is_file():raise ValueError('Final target not accepted')
            result['science_completed']=True
            result['sample_summaries_completed']=10
            result['grouping_communities_completed']=1
    except BaseException as exc:
        result['error']=repr(exc)
    science_samples=science_guard.observations if science_guard else []
    save_disk_samples(root/'science-disk.jsonl',science_samples)
    result['science_disk']=dict(summary=disk_summary(science_samples,cfg['initial_filesystem_used_bytes']),
                                raw=binding(root/'science-disk.jsonl'))
    publish(result,root/'science-result.json')
    try:
        growth=max(0,shutil.disk_usage(root).used-cfg['initial_filesystem_used_bytes'])
        with PhaseGuard(root,deadline-time.time(),growth_bytes=max(0,24*1024**3-growth)) as collection_guard:
            evidence=root/'sealed-evidence';evidence.mkdir(exist_ok=False)
            for name in ['science-result.json','started.json','release.json']:
                if (root/name).is_file():shutil.copyfile(root/name,evidence/name)
            shutil.copyfile(root/'science-disk.jsonl',evidence/'science-disk.jsonl')
            shutil.copyfile(config,evidence/'config.json')
            shutil.copyfile(cfg['plan'],evidence/'plan.json')
            for folder in [root/'gates',logs]:
                if not folder.is_dir():continue
                for source in sorted(folder.rglob('*')):
                    if source.is_symlink():raise ValueError('Gate/log artifact links refused')
                    if source.is_file():
                        target=evidence/folder.name/source.relative_to(folder)
                        target.parent.mkdir(parents=True,exist_ok=True)
                        shutil.copyfile(source,target)
            if Path(cfg['watchdog_live']).is_file():
                shutil.copyfile(cfg['watchdog_live'],evidence/'watchdog-live.json')
            lock=json.loads((Path(cfg['repo'])/'experiments/E024-oral-measured-coverage/source-lock.json').read_text())
            for name,expected in lock['files'].items():
                source=Path(cfg['repo'])/name
                if binding(source)!=expected:raise ValueError('Frozen preparation source differs')
                target=evidence/'source'/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(source,target)
            # The real collector is invoked through its isolated production path.
            command('collect',[p['python'],'-I','-B',str(Path(cfg['repo'])/'scripts/e024_collect.py'),
                '--work',str(work),'--evidence',str(evidence),'--output',str(root/'collection')]
                + ([] if result['science_completed'] else ['--allow-incomplete']),reserve=600)
            for name in ['e024-evidence.tar.gz','e024-evidence.tar.gz.sha256','collection.json']:
                local=root/'collection'/name
                remote=cfg['archive_prefix']+name
                command('upload-'+name,upload_command(cfg['gcloud'],local,remote),reserve=120)
                command('readback-'+name,[p['workflow_python'],'-I','-B',str(Path(cfg['repo'])/'scripts/e024_phase.py'),
                    '--readback',remote,'--gcloud',cfg['gcloud'],'--bytes',str(local.stat().st_size),
                    '--sha256',binding(local)['sha256']],reserve=60)
            result['collection_readback_verified']=True
            if result['science_completed']:result['status']='SUCCESS'
    except BaseException as exc:
        result['collection_error']=repr(exc)
    collection_samples=collection_guard.observations if collection_guard else []
    save_disk_samples(root/'collection-disk.jsonl',collection_samples)
    publish(dict(summary=disk_summary(science_samples+collection_samples+command_samples,cfg['initial_filesystem_used_bytes']),
                 science_raw=binding(root/'science-disk.jsonl'),collection_raw=binding(root/'collection-disk.jsonl'),
                 command_boundary_samples=command_samples,
                 scope='Through archive collection/upload/readback; final compact proof delivery follows this closed snapshot'),root/'terminal-disk.json')
    if deadline-time.time()>60:
        try:
            for name in ['collection-disk.jsonl','terminal-disk.json']:
                path=root/name
                command('upload-'+name,upload_command(cfg['gcloud'],path,cfg['archive_prefix']+name),reserve=30)
                command('readback-'+name,[p['workflow_python'],'-I','-B',str(Path(cfg['repo'])/'scripts/e024_phase.py'),
                    '--readback',cfg['archive_prefix']+name,'--gcloud',cfg['gcloud'],'--bytes',str(path.stat().st_size),
                    '--sha256',binding(path)['sha256']],reserve=30)
            result['terminal_disk']=binding(root/'terminal-disk.json')
        except BaseException as exc:
            result['terminal_delivery_error']=repr(exc);result['status']='FAILED'
    else:
        result['terminal_delivery_error']='Original clock cannot admit closed terminal resource delivery'
        result['status']='FAILED'
    result.update(finished_epoch=time.time(),source_commit=cfg['source_commit'])
    publish(result,root/'completion.json')
    status(dict(status=result['status'],science_completed=result['science_completed'],
                root=str(root),completion=binding(root/'completion.json')))
    # Final delivery is independently proved by GCS bytes on later inspection.
    if deadline-time.time()>30:
        try:command('upload-completion',upload_command(cfg['gcloud'],root/'completion.json',cfg['archive_prefix']+'completion.json'))
        except BaseException as exc:print('E024_COMPLETION_UPLOAD_FAILED',repr(exc),flush=True)
    return result


def readback(gcloud,url,expected_bytes,expected_sha):
    """Stream-hash the actual private object without an extra archive-sized copy."""
    process=subprocess.Popen([gcloud,'storage','cat',url],stdout=subprocess.PIPE)
    h=hashlib.sha256();size=0
    try:
        for b in iter(lambda:process.stdout.read(1024**2),b''):
            size+=len(b)
            if size>expected_bytes:raise ValueError('Private readback larger than admitted object')
            h.update(b)
        if process.wait(timeout=30) or size!=expected_bytes or h.hexdigest()!=expected_sha:
            raise ValueError('Private upload/readback bytes differ')
        print('E024_PRIVATE_READBACK_PASS',size,h.hexdigest(),flush=True)
    finally:
        if process.poll() is None:process.terminate();process.wait(timeout=5)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path)
    parser.add_argument('--readback');parser.add_argument('--gcloud')
    parser.add_argument('--bytes',type=int);parser.add_argument('--sha256')
    a=parser.parse_args()
    if a.config:run(a.config)
    elif a.readback:readback(a.gcloud,a.readback,a.bytes,a.sha256)
    else:parser.error('Select held phase or exact readback')
