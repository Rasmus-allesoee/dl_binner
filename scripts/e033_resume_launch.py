#!/usr/bin/env python3
"""Sync and release the fixed E033 comparison on the existing VM/task filesystem.

No acquisition, new resource, fallback install or accepted science replay. The
first forensic wake owns the common clock. All rendered source/config/payload
programs are retained; provider STOP and a fresh boot/process watcher precede
release. A setup failure stops compute without resetting clocks or deleting data.
"""
import argparse
import base64
import datetime
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e021_portable_cloud import Cloud,CPU,CPU_ZONE
from e031_launch import source_code
from e033_launch import SSH
from e033_forensic_launch import remote
from e033_forensic import write_metadata
from e024_coverage import binding
from e033_recovery import admit,ORIGINAL
from e033_resume import validate_config

BRANCH='multiscale-bam-recovery'


def configuration(ident,financial,clock):
    """Produce the complete actual parent schema and explicit original task baseline."""
    repair,_,candidate=admit();reuse=json.loads((ROOT/'experiments/E033-multiscale-bam/reuse-lock.json').read_text())
    old=json.loads((ROOT/'artifacts/e033-multiscale-bam/inspection/E009-noGLM-verified/evidence/config.json').read_text())
    root=ident['root'];task=ORIGINAL+'/task';common=clock['start_epoch']
    return dict(root=root,repo='/srv/dl_binner/repo',source_commit=ident['source'],operations_source=ident['source'],
        vm_start_epoch=common,boot_start_epoch=ident['start'],review_deadline_epoch=common+108000,
        provider_deadline_epoch=ident['provider_deadline'],setup_deadline_epoch=ident['start']+1800,
        service_name=ident['service_name'],user=old['user'],archive_prefix=ident['archive_prefix'],
        plan=root+'/science-plan.json',python=task+'/env-repair-r1/bin/python',workflow_python=old['workflow_python'],
        base=reuse['native_dependency_base'],reference=reuse['native_runtime_reference'],wheel=root+'/payload/dl_binner-0.1.0.dev9-py3-none-any.whl',
        pysam_wheel=old['pysam_wheel'],gcloud='/snap/bin/gcloud',financial=financial,
        initial_filesystem_used_bytes=24576,initial_filesystem_device=0,source_filesystem='/srv/dl_binner',
        task_filesystem=task,limits=repair['limits'],repair_lock='/srv/dl_binner/repo/experiments/E033-multiscale-bam/repair-lock.json',
        candidate_lock='/srv/dl_binner/repo/experiments/E033-multiscale-bam/repair-candidate-lock.json')


def plan_value(c):
    """Reuse exact measurement/state paths; change only work/runtime and declared clock."""
    plan=json.loads((ROOT/'experiments/E033-multiscale-bam/runtime-plan.json').read_text().replace('NEW_PHASE',Path(ORIGINAL).name+'/task'))
    plan.update(work=ORIGINAL+'/task/work-repair-r1',python=c['python'],limits=c['limits'],
        recovery=dict(lock=c['repair_lock'],binding=binding(ROOT/'experiments/E033-multiscale-bam/repair-lock.json')))
    return plan


def render_setup(c,wheel):
    """Render the actual existing-device mount, byte/schema writer and source checks."""
    payload=base64.b64encode(Path(wheel).read_bytes()).decode();plan=plan_value(c)
    code=r'''import base64,json,os,pathlib,shutil,subprocess,sys,time
c=@@CFG@@;plan=@@PLAN@@;payload=@@PAYLOAD@@
root=pathlib.Path(c['root']);root.mkdir(parents=True,exist_ok=False)
for n in ['logs','gates','payload','tmp']:root.joinpath(n).mkdir()
repo=pathlib.Path(c['repo'])
if subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()!=c['source_commit'] or subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip():raise ValueError('Exact clean recovery source required')
sys.path.insert(0,str(repo/'scripts'));from e033_recovery import admit,binding
from e033_forensic import write_metadata
from e033_resume import validate_config
repair,_,candidate=admit()
device=pathlib.Path('/dev/disk/by-id/google-e033-task-1793805630');task=pathlib.Path(c['task_filesystem'])
if int(subprocess.check_output(['lsblk','-bn','-o','SIZE',str(device)],text=True).strip())!=100*1024**3:raise ValueError('Original task size differs')
if not os.path.ismount(task):
 if any(task.iterdir()):raise ValueError('Uncovered data at old task mount')
 subprocess.run(['sudo','-n','mount','-o','rw,nodev,nosuid',str(device),str(task)],check=True)
actual=pathlib.Path(subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(task)],text=True).strip())
if actual.resolve()!=device.resolve() or os.stat(task).st_dev==os.stat(root).st_dev:raise ValueError('Original positively identified task device differs')
opts=subprocess.check_output(['findmnt','-n','-o','OPTIONS','--target',str(task)],text=True).strip().split(',')
if 'ro' in opts:subprocess.run(['sudo','-n','mount','-o','remount,rw,nodev,nosuid',str(device),str(task)],check=True)
c['initial_filesystem_device']=os.stat(task).st_dev
if min(shutil.disk_usage(root).free,shutil.disk_usage(task).free)<25*1024**3:raise ValueError('Actual recovery source/task reserve unavailable')
if pathlib.Path(plan['work']).exists() or pathlib.Path(c['python']).parents[1].exists():raise ValueError('Fresh repair work/package path required; inspect existing attempts rather than overwrite')
pathlib.Path(c['wheel']).write_bytes(base64.b64decode(payload))
lock=json.loads(candidate.read_text())
if binding(c['wheel'])!=lock['wheel'] or binding(c['pysam_wheel'])!=lock['pysam_wheel']:raise ValueError('Exact new owned wheel or passed original BAM wheel missing; no fallback')
validate_config(c)
write_metadata(root/'config.json',c);write_metadata(root/'science-plan.json',plan)
host=dict(boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),user=c['user'],source_filesystem=shutil.disk_usage(root)._asdict(),task_filesystem=shutil.disk_usage(task)._asdict(),task_device=c['initial_filesystem_device'],original_task_baseline_used=c['initial_filesystem_used_bytes'],lscpu=subprocess.check_output(['lscpu'],text=True),epoch=time.time())
write_metadata(root/'host.json',host)
print('E033_REPAIRED_SETUP',json.dumps(dict(config=binding(root/'config.json'),plan=binding(root/'science-plan.json'),host=host)),flush=True)
'''.replace('@@CFG@@',repr(c)).replace('@@PLAN@@',repr(plan)).replace('@@PAYLOAD@@',repr(payload))
    compile(code,'actual-recovery-setup','exec');return code


def launch(out,wheel):
    """Verify private exact source sync, current provider and held parent before release."""
    out=Path(out).absolute();out.mkdir(parents=True,exist_ok=False)
    parent=out.parent;financial=json.loads((parent/'financial-gate.json').read_text());clock=json.loads((parent/'common-clock.json').read_text())
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Committed clean repaired branch required')
    admit();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    tag='resume-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+source[:7]
    ident=dict(root='/srv/dl_binner/experiments/e033/'+tag,repo='/srv/dl_binner/repo',source=source,service_name='e033-'+tag,
               archive_prefix='gs://dl-binner-archive-167650584170/e033/'+tag+'/',start=time.time(),provider_deadline=clock['provider_deadline_epoch']-1)
    c=configuration(ident,financial,clock);validate_config(c);render_setup(c,wheel)
    bundle=out/'source.bundle';subprocess.run(['git','bundle','create',str(bundle),BRANCH,'^5911e2587d5c8353937fb71260464a038a1f46de'],cwd=ROOT,check=True)
    transport=dict(kind='private_exact_Git_bundle',path=str(bundle),bundle=binding(bundle),base='5911e2587d5c8353937fb71260464a038a1f46de')
    sync=source_code(ident,transport).replace('bootstrap-preserving-learning',BRANCH).replace('experiments/e031/source-transports','experiments/e033/source-transports')
    compile(sync,'actual-exact-source-consumer','exec')
    cloud=Cloud(out/'control');before=cloud.state();disks=cloud.call(['compute','disks','list'])
    if before['status']!='TERMINATED' or not before['machineType'].endswith('/e2-standard-8') or before.get('guestAccelerators') or sorted(int(d['diskSizeGb']) for d in before['disks'])!=[30,100,300]:raise ValueError('Existing stopped resources differ')
    task=[d for d in disks if d['name']=='e033-task-1793805630']
    if len(task)!=1 or task[0]['id']!='1578633013833953331':raise ValueError('Existing original task ID differs')
    try:
        seconds=int(clock['provider_deadline_epoch']-time.time()-120)
        if seconds<1800:raise TimeoutError('Common recovery clock cannot admit setup')
        cloud.call(['compute','instances','set-scheduling',CPU,'--no-restart-on-failure','--max-run-duration='+str(seconds)+'s','--instance-termination-action=STOP'],CPU_ZONE)
        cloud.call(['compute','instances','start',CPU],CPU_ZONE);live=cloud.state()
        ident['start']=datetime.datetime.fromisoformat(live['lastStartTimestamp']).timestamp()
        if live['status']!='RUNNING' or live['lastStartTimestamp']==before['lastStartTimestamp']:raise ValueError('Fresh scientific recovery boot required')
        remaining=int(clock['provider_deadline_epoch']-ident['start'])
        cloud.call(['compute','instances','set-scheduling',CPU,'--no-restart-on-failure','--max-run-duration='+str(remaining)+'s','--instance-termination-action=STOP'],CPU_ZONE)
        live=cloud.state();ident['provider_deadline']=ident['start']+int(live['scheduling']['maxRunDuration']['seconds'])
        if not clock['deadline_epoch']<ident['provider_deadline']<=clock['provider_deadline_epoch'] or live['disks']!=before['disks']:raise ValueError('Common-clock provider STOP/resources differ')
        write_metadata(out/'identity.json',ident);write_metadata(out/'provider-start.json',live)
        probe=None
        for i in range(5):
            probe=subprocess.run(SSH+['true'],capture_output=True,text=True,timeout=60);(out/('connection-%d.log'%i)).write_text(probe.stdout+probe.stderr)
            if probe.returncode==0:break
        if probe.returncode:raise RuntimeError('Pinned SSH unavailable: '+probe.stderr)
        sync=source_code(ident,transport).replace('bootstrap-preserving-learning',BRANCH).replace('experiments/e031/source-transports','experiments/e033/source-transports')
        # The shared accepted source importer owns actual SHA/prerequisite/head
        # checks; only its private task path and branch name are substituted.
        remote(out,'exact-source',sync,240)
        c=configuration(ident,financial,clock);remote(out,'setup',render_setup(c,wheel))
        remote(out,'arm',"import subprocess\nsubprocess.run(['sudo','-n','/usr/bin/python3','-I','-B','/srv/dl_binner/repo/scripts/e033_resume_arm.py','--config',"+repr(c['root']+'/config.json')+"],check=True)\n")
        state=cloud.state();write_metadata(out/'provider-before-release.json',state)
        if state['status']!='RUNNING' or state['lastStartTimestamp']!=live['lastStartTimestamp'] or state['scheduling']!=live['scheduling']:raise ValueError('Provider fallback changed before release')
        code=r'''import json,pathlib,sys
root=pathlib.Path(@@ROOT@@);sys.path.insert(0,'/srv/dl_binner/repo/scripts')
from e024_coverage import binding
from e021_control_json import publish
from e009_exit_watchdog import identity
watch=json.loads((root/'logs/watchdog-live-before-release.json').read_text());sup=json.loads((root/'logs/supervision.json').read_text())
if watch['decision']!='workflow alive' or identity(watch['expected_process']['pid'])!=watch['expected_process'] or not sup['native_normal_exit_and_crash_tests_passed']:raise ValueError('Current boot/process supervision missing')
publish(dict(config=binding(root/'config.json'),plan=binding(root/'science-plan.json'),provider_STOP_verified=True,watchdog_verified=True,conditional_native_gate_release=True),root/'release.json')
print('E033_REPAIRED_RELEASED',json.dumps(dict(root=str(root),watchdog=sup)),flush=True)
'''.replace('@@ROOT@@',repr(c['root']))
        remote(out,'release',code);write_metadata(out/'released.json',dict(identity=ident,epoch=time.time(),gates_then_frozen_science=True));return ident
    except BaseException as error:
        (out/('failure-'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=repr(error),identity=ident),indent=2)+'\n');cloud.stop();raise


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True,type=Path);p.add_argument('--wheel',required=True,type=Path)
    a=p.parse_args();launch(a.root,a.wheel)
