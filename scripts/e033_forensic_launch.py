#!/usr/bin/env python3
"""Wake only the existing E033 VM for the authorized bounded forensic collection.

Provider STOP, original task-disk identity/read-only mount, complete actual config,
helper bytes and fresh held-parent watcher are verified before release. Failure
stops the VM with a retained local journal. This controller cannot fit, measure,
install packages, change disks or execute the scientific workflow.
"""
import argparse
import base64
import datetime
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e021_portable_cloud import Cloud,CPU,CPU_ZONE
from e033_launch import SSH
from e024_coverage import binding
from e033_forensic import validate_config


def configuration(ident, financial):
    """Produce every exact field consumed by the native held forensic parent."""
    old=json.loads((ROOT/'artifacts/e033-multiscale-bam/admission/recovery-r2/identity.json').read_text())
    source=ROOT/'artifacts/e033-multiscale-bam/inspection/E009-noGLM-verified/evidence/config.json'
    return dict(root=ident['root'],repo=old['repo'],original=old['root'],source_commit=old['source'],
        operations_source=ident['source'],old_config=binding(source),
        old_boot='e82bc613-05f6-4b6e-beea-9a19108edca7',old_service=old['service_name'],
        disk_name='e033-task-1793805630',disk_id='1578633013833953331',vm_start_epoch=ident['start'],
        common_clock_start_epoch=ident.get('common_start',ident['start']),
        common_deadline_epoch=ident.get('common_start',ident['start'])+30*3600,
        provider_deadline_epoch=ident['start']+2700,archive_prefix=ident['archive_prefix'],
        service_name=ident['service_name'],user=old['user'],financial=financial,
        helpers={n:binding(ROOT/'scripts'/n) for n in ['e033_forensic.py','e033_forensic_arm.py']},
        task_device=0,source_initial_used_bytes=0)


def render_setup(c):
    """Render the real mount/helper/schema consumer before any cost-bearing start."""
    payload={n:base64.b64encode((ROOT/'scripts'/n).read_bytes()).decode() for n in c['helpers']}
    code=r'''import base64,json,os,pathlib,shutil,subprocess,sys,time
c=@@CONFIG@@;payload=@@PAYLOAD@@
root=pathlib.Path(c['root']);root.mkdir(parents=True,exist_ok=False)
for n in ['helpers','logs','tmp']:root.joinpath(n).mkdir()
if subprocess.check_output(['git','rev-parse','HEAD'],cwd=c['repo'],text=True).strip()!=c['source_commit']:raise ValueError('Protected original source differs')
task=pathlib.Path(c['original'])/'task';device=pathlib.Path('/dev/disk/by-id/google-'+c['disk_name'])
if int(subprocess.check_output(['lsblk','-bn','-o','SIZE',str(device)],text=True).strip())!=100*1024**3:raise ValueError('Positively identified existing task size differs')
if not os.path.ismount(task):
 if any(task.iterdir()):raise ValueError('Uncovered files under old unmounted task path')
 subprocess.run(['sudo','-n','mount','-o','ro,nodev,nosuid,noload',str(device),str(task)],check=True)
actual=pathlib.Path(subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(task)],text=True).strip())
opts=subprocess.check_output(['findmnt','-n','-o','OPTIONS','--target',str(task)],text=True).strip().split(',')
if actual.resolve()!=device.resolve() or 'ro' not in opts or os.stat(task).st_dev==os.stat(root).st_dev:raise ValueError('Existing task read-only mount differs')
for name,data in payload.items():
 target=root/'helpers'/name;target.write_bytes(base64.b64decode(data))
 compile(target.read_text(),str(target),'exec')
sys.path.insert(0,str(root/'helpers'));from e033_forensic import binding,validate_config,write_metadata
if any(binding(root/'helpers'/name)!=wanted for name,wanted in c['helpers'].items()):raise ValueError('Transferred forensic helper differs')
if binding(pathlib.Path(c['original'])/'config.json')!=c['old_config']:raise ValueError('Original failed configuration differs')
c['task_device']=os.stat(task).st_dev;c['source_initial_used_bytes']=shutil.disk_usage(root).used
validate_config(c)
write_metadata(root/'config.json',c)
host=dict(boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),user=c['user'],source_filesystem=shutil.disk_usage(root)._asdict(),task_filesystem=shutil.disk_usage(task)._asdict(),device=str(device),task_device=c['task_device'],epoch=time.time())
write_metadata(root/'host.json',host)
print('E033_FORENSIC_SETUP',json.dumps(dict(config=binding(root/'config.json'),host=host)),flush=True)
'''
    code=code.replace('@@CONFIG@@',repr(c)).replace('@@PAYLOAD@@',repr(payload))
    compile(code,'actual-E033-forensic-setup','exec')
    return code


def remote(out,label,code,seconds=180):
    """Retain the actual compiled SSH program and every terminal byte once."""
    compile(code,label,'exec');at=out/(label+'-'+str(time.time_ns()))
    at.with_suffix('.py').write_text(code)
    p=subprocess.run(SSH+['/usr/bin/python3','-I','-B','-'],input=code,capture_output=True,text=True,timeout=seconds)
    at.with_suffix('.log').write_text(p.stdout+p.stderr)
    print(p.stdout+p.stderr,flush=True);p.check_returncode();return p.stdout


def launch(out):
    """Verify stopped resources and current finance, start held, then release logs only."""
    out=Path(out).absolute();financial=json.loads((out/'financial-gate.json').read_text());cloud=Cloud(out/'control')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Exact clean committed operations source required')
    before=cloud.state();disks=cloud.call(['compute','disks','list'])
    if before['status']!='TERMINATED' or not before['machineType'].endswith('/e2-standard-8') or before.get('guestAccelerators') or sorted(int(d['diskSizeGb']) for d in before['disks'])!=[30,100,300]:raise ValueError('Original stopped CPU/disks required')
    task=[d for d in disks if d['name']=='e033-task-1793805630']
    if len(task)!=1 or task[0]['id']!='1578633013833953331' or int(task[0]['sizeGb'])!=100:raise ValueError('Existing task ID differs')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    tag='forensic-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+source[:7]
    ident=dict(root='/srv/dl_binner/experiments/e033/'+tag,source=source,service_name='e033-'+tag,
               archive_prefix='gs://dl-binner-archive-167650584170/e033/'+tag,start=time.time())
    if (out/'common-clock.json').exists():
        ident['common_start']=json.loads((out/'common-clock.json').read_text())['start_epoch']
    validate_config(configuration(ident,financial));render_setup(configuration(ident,financial))
    try:
        cloud.call(['compute','instances','set-scheduling',CPU,'--no-restart-on-failure','--max-run-duration=2700s','--instance-termination-action=STOP'],CPU_ZONE)
        state=cloud.state();(out/'provider-before-start.json').write_text(json.dumps(state,indent=2)+'\n')
        if str(state['scheduling']['maxRunDuration']['seconds'])!='2700' or state['scheduling']['instanceTerminationAction']!='STOP' or state['disks']!=before['disks']:raise ValueError('Forensic provider STOP/resource readback differs')
        cloud.call(['compute','instances','start',CPU],CPU_ZONE)
        live=cloud.state()
        if live['status']!='RUNNING' or live['lastStartTimestamp']==before['lastStartTimestamp']:raise ValueError('Fresh native forensic boot missing')
        ident['start']=datetime.datetime.fromisoformat(live['lastStartTimestamp']).timestamp()
        if not (out/'common-clock.json').exists():
            (out/'common-clock.json').write_text(json.dumps(dict(start_epoch=ident['start'],deadline_epoch=ident['start']+30*3600,provider_deadline_epoch=ident['start']+30.25*3600),indent=2)+'\n')
        ident['common_start']=json.loads((out/'common-clock.json').read_text())['start_epoch']
        (out/'identity.json').write_text(json.dumps(ident,indent=2)+'\n');(out/'provider-start.json').write_text(json.dumps(live,indent=2)+'\n')
        c=configuration(ident,financial)
        # SSH connection readiness only: never replay a submitted mutating program.
        probe=None
        for i in range(5):
            probe=subprocess.run(SSH+['true'],capture_output=True,text=True,timeout=60)
            (out/('connection-%d.log'%i)).write_text(probe.stdout+probe.stderr)
            if probe.returncode==0:break
        if probe.returncode:raise RuntimeError('Pinned SSH not ready: '+probe.stderr)
        remote(out,'setup',render_setup(c))
        remote(out,'arm',"import subprocess\nsubprocess.run(['sudo','-n','/usr/bin/python3','-I','-B',"+repr(c['root']+'/helpers/e033_forensic_arm.py')+",'--config',"+repr(c['root']+'/config.json')+"],check=True)\n")
        state=cloud.state();(out/'provider-before-release.json').write_text(json.dumps(state,indent=2)+'\n')
        if state['status']!='RUNNING' or state['lastStartTimestamp']!=live['lastStartTimestamp'] or state['scheduling']!=live['scheduling']:raise ValueError('Current forensic provider fallback changed')
        release=r'''import json,pathlib,sys
root=pathlib.Path(@@ROOT@@);sys.path.insert(0,str(root/'helpers'));from e033_forensic import binding
sys.path.insert(0,'/srv/dl_binner/repo/scripts');from e021_control_json import publish
watch=json.loads((root/'logs/watchdog-live-before-release.json').read_text());supervision=json.loads((root/'logs/supervision.json').read_text())
if watch['decision']!='workflow alive' or supervision['process']!=watch['expected_process'] or not supervision['native_normal_exit_and_crash_tests_passed']:raise ValueError('Fresh forensic watcher unverified')
publish(dict(config=binding(root/'config.json'),provider_STOP_seconds=2700,watchdog_verified=True,forensics_only=True),root/'release.json')
print('E033_FORENSICS_RELEASED',json.dumps(dict(root=str(root),watchdog=supervision)),flush=True)
'''.replace('@@ROOT@@',repr(c['root']))
        remote(out,'release',release)
        (out/'released.json').write_text(json.dumps(dict(identity=ident,forensics_only=True,epoch=time.time()),indent=2)+'\n')
        return ident
    except BaseException as error:
        (out/('failure-'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=repr(error),identity=ident),indent=2)+'\n')
        cloud.stop();raise


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True,type=Path)
    launch(p.parse_args().root)
