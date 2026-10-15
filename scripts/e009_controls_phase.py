#!/usr/bin/env python3
"""Hold the approved E009 launcher until its fresh exit watchdog is verified.

The persistent parent retains its PID/command identity across release and child
exit. Its shared clock starts at this VM boot, including setup already performed.
It invokes the unchanged control launcher once, archives status to the existing
private bucket, then exits for the independent watchdog to stop compute. No retry,
provisioning, fit modification, scoring or shutdown command occurs here.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import time
import urllib.request
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e009_controls import PhaseGuard
from e009_owner import supervisor, Tee


def publish_status(value):
    """Expose compact non-secret status via the already-enabled GCE guest attribute.

    Best effort only; an unavailable metadata endpoint never prevents VM shutdown.
    This grants no access and uses no credential or additional cloud service.
    """
    data=json.dumps(value).encode()
    req=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/guest-attributes/e009-controls/status',
                              data=data,method='PUT',headers={'Metadata-Flavor':'Google','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=5)as r:r.read()
    except Exception as exc:print('STATUS_PUBLISH_UNAVAILABLE '+str(exc),flush=True)


def run(config_path):
    """Run one held parent under a boot-relative four-hour clock and disk allowance."""
    config_path=Path(config_path);cfg=json.loads(config_path.read_text());phase=Path(cfg['phase_root'])
    result_root=Path(cfg['controls_root']);logs=phase/'logs';logs.mkdir(exist_ok=True)
    if (phase/'started.json').exists():raise ValueError('Existing phase; no retry or resume')
    initial=time.time();remaining=14400-(initial-cfg['vm_start_epoch'])
    if not 300<remaining<=14400:raise ValueError('Insufficient original phase clock; no fit launched')
    initial_growth=max(0,shutil.disk_usage(phase).used-cfg['initial_filesystem_used_bytes'])
    if initial_growth>=20*1024**3:raise ValueError('Preparation exhausted disk-growth allowance')
    write_json(phase/'started.json',{'pid':os.getpid(),'epoch':initial,'boot_clock_seconds_remaining':remaining,
                                   'config':binding(config_path),'preparation_growth_bytes':initial_growth})
    outcome={'status':'FAILED','phase_id':cfg['phase_id'],'source_commit':cfg['source_commit'],
             'four_arms_completed':False,'cloud_collection_verified':False}
    deadline=time.monotonic()+remaining;sup=supervisor();env=sup.isolated_env(8)
    env.update(CLOUDSDK_STORAGE_PROCESS_COUNT='1',CLOUDSDK_STORAGE_THREAD_COUNT='2',CLOUDSDK_CORE_DISABLE_PROMPTS='1')
    def command(argv,name,reserve=0):
        seconds=deadline-time.monotonic()-reserve
        if seconds<=0:raise TimeoutError('Whole boot-relative control phase clock exhausted')
        return sup.supervise(argv,logs/(name+'.log'),seconds,30_000_000_000,env,sample_root=os.getpid())
    def transfer(path,name):
        uri=cfg['archive_prefix']+'/'+name
        command(['/snap/bin/gcloud','storage','cp','--if-generation-match=0',path,uri,'--quiet'],'upload-'+name)
        returned=phase/('readback-'+name)
        command(['/snap/bin/gcloud','storage','cp',uri,returned,'--quiet'],'readback-'+name)
        actual=binding(path)
        if binding(returned)!=actual:raise ValueError('Private archive readback mismatch')
        return {'uri':uri,**actual,'readback_verified':True}
    try:
        with PhaseGuard(phase,remaining,growth_bytes=20*1024**3-initial_growth):
            print('PHASE_HELD_FOR_WATCHDOG pid='+str(os.getpid()),flush=True)
            while not Path(cfg['release_file']).exists():time.sleep(.2)
            release=json.loads(Path(cfg['release_file']).read_text())
            if release['phase_config']!=binding(config_path):raise ValueError('Release/config binding differs')
            print('PHASE_RELEASED_ONCE',flush=True)
            command(cfg['launcher_argv'],'launcher',reserve=180)
            child=json.loads((result_root/'phase-result.json').read_text())
            if child.get('status')!='SUCCESS' or not child.get('four_arms_completed'):raise ValueError('Control launcher incomplete')
            outcome.update(status='SUCCESS',four_arms_completed=True,launcher_result=binding(result_root/'phase-result.json'))
            outcome['control_archive']=transfer(result_root/'controls-evidence.tar.gz','controls-evidence.tar.gz')
            outcome['control_checksum']=transfer(result_root/'controls-evidence.tar.gz.sha256','controls-evidence.tar.gz.sha256')
            outcome['cloud_collection_verified']=True
    except BaseException as exc:
        outcome.update(status='FAILED',error=f'{type(exc).__name__}: {exc}')
    # Evidence-only closure never launches another fit. Preserve an actual failure
    # even if storage/metadata is unavailable; the watcher will still stop the VM.
    outcome['elapsed_since_VM_start_seconds']=time.time()-cfg['vm_start_epoch']
    if (result_root/'phase-result.json').exists():
        child=json.loads((result_root/'phase-result.json').read_text())
        outcome['launcher_status']={k:v for k,v in child.items()if k in('status','error','wall_seconds','four_arms_completed','collection')}
    write_json(phase/'attempt-controls.json',outcome)
    try:
        closure=phase/'closure.tar.gz'
        terminal=logs/'parent-terminal.log'
        snapshot=phase/'terminal.snapshot.log'
        if terminal.exists():snapshot.write_bytes(terminal.read_bytes())
        with closure.open('xb')as f,tarfile.open(fileobj=f,mode='w:gz')as t:
            paths=[phase/'attempt-controls.json',phase/'started.json',config_path,
                   *[p for p in sorted(logs.glob('*'))if p.name!='parent-terminal.log']]
            if snapshot.exists():paths.append(snapshot)
            if (result_root/'phase-result.json').exists():paths.append(result_root/'phase-result.json')
            for p in paths:
                if p.is_file():t.add(p,arcname=('controls-phase-result.json'if p.parent==result_root else str(p.relative_to(phase))),recursive=False)
        outcome['closure_archive']=transfer(closure,'closure.tar.gz')
        write_json(phase/'completion.json',outcome)
        outcome['completion_uri']=cfg['archive_prefix']+'/completion.json'
        transfer(phase/'completion.json','completion.json')
    except Exception as exc:outcome['closure_error']=str(exc)
    publish_status(outcome)
    print('PHASE_EXIT_JSON='+json.dumps(outcome,sort_keys=True),flush=True)
    return 0 if outcome['status']=='SUCCESS'else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--config',type=Path,required=True)
    args=parser.parse_args();cfg=json.loads(args.config.read_text());terminal=Path(cfg['phase_root'])/'logs/parent-terminal.log'
    terminal.parent.mkdir(exist_ok=True);old_out,old_err=sys.stdout,sys.stderr
    with terminal.open('x')as f:
        sys.stdout=Tee(old_out,f);sys.stderr=Tee(old_err,f)
        try:exit_code=run(args.config)
        finally:sys.stdout,sys.stderr=old_out,old_err
    raise SystemExit(exit_code)
