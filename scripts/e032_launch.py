#!/usr/bin/env python3
"""Launch one frozen E032 cached phase on the existing E2 with independent STOP.

Only an explicitly admitted 40 GiB task disk may be added after measured cleanup/
headroom review. Private exact-commit import preserves read-only GitHub access.
All rendered consumers and the full configuration schema are tested before start.
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
from e024_coverage import binding
from e031_launch import remote,SSH,save,source_code
from e032_phase import validate_config
from e032_control import freeze


def source_sync(ident,transport):
    """Reuse strict Git import with the new branch's explicitly advertised head."""
    return source_code(ident,transport).replace('bootstrap-preserving-learning','biological-candidate-selection').replace(
        'experiments/e031/source-transports','experiments/e032/source-transports')


def config_value(ident,financial,used):
    """Produce the exact complete consumer schema, without undeclared fields."""
    p=json.loads((ROOT/'experiments/E032-biological-candidate-selection/runtime-plan.json').read_text())
    reuse=json.loads((ROOT/'experiments/E032-biological-candidate-selection/reuse-lock.json').read_text())
    start=ident['vm_start_epoch'];root=ident['root'];limits=p['limits']
    return dict(root=root,repo=ident['repo'],source_commit=ident['source'],operations_source=ident['source'],
        vm_start_epoch=start,review_deadline_epoch=start+limits['seconds'],provider_deadline_epoch=start+limits['provider_STOP_seconds'],
        setup_deadline_epoch=start+2700,service_name=ident['service_name'],user=ident['user'],
        archive_prefix=ident['archive_prefix'],plan=root+'/science-plan.json',python=root+'/env/bin/python',
        workflow_python=p['workflow_python'],base=reuse['native_dependency_base'],reference=reuse['native_runtime_reference'],
        wheel=root+'/payload/dl_binner-0.1.0.dev9-py3-none-any.whl',gcloud='/snap/bin/gcloud',financial=financial,
        initial_filesystem_used_bytes=used,source_filesystem='/srv/dl_binner',limits=limits)


def render_host(ident,financial,disk=None):
    """Render exact new-device mounting, package transport and held-parent arming."""
    wheel=Path(financial['wheel_path'])
    if binding(wheel)!=financial['wheel_binding']:raise ValueError('Frozen wheel transport differs')
    cfg=config_value(ident,financial,0)
    code=r'''import base64,json,os,pathlib,pwd,shutil,subprocess,sys,time
ident=@@IDENT@@;disk=@@DISK@@;cfg=@@CONFIG@@
repo=pathlib.Path(ident['repo']);root=pathlib.Path(ident['root'])
if not os.path.ismount('/srv/dl_binner') or os.cpu_count()!=8:raise ValueError('Original CPU/mount required')
if disk:
 script=r"""import os,pathlib,subprocess,json,pwd
root=pathlib.Path(@@ROOT@@);name=@@NAME@@;dev=pathlib.Path('/dev/disk/by-id/google-'+name)
if not name.startswith('e032-task-') or root.exists():raise ValueError('Fresh exact task scope required')
subprocess.run(['udevadm','settle','--timeout=15'],check=True)
rows=json.loads(subprocess.check_output(['lsblk','-J','-b','-o','NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT',str(dev)],text=True))['blockdevices']
if len(rows)!=1 or rows[0]['size']!=40*1024**3 or rows[0]['type']!='disk' or rows[0].get('fstype') or rows[0].get('mountpoint') or rows[0].get('children'):raise ValueError('Only new empty 40 GiB task disk can be formatted')
if subprocess.run(['blkid',str(dev)],capture_output=True).returncode!=2:raise ValueError('Existing device signature refused')
subprocess.run(['mkfs.ext4','-m','0','-L','e032-task',str(dev)],check=True,capture_output=True)
root.mkdir(parents=True,exist_ok=False);subprocess.run(['mount','-o','nodev,nosuid',str(dev),str(root)],check=True)
account=pwd.getpwnam(@@USER@@);os.chown(root,account.pw_uid,account.pw_gid)
actual=subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(root)],text=True).strip()
if pathlib.Path(actual).resolve()!=dev.resolve() or os.stat(root).st_dev==os.stat('/srv/dl_binner').st_dev:raise ValueError('Task mount identity differs')
""".replace('@@ROOT@@',repr(str(root))).replace('@@NAME@@',repr(disk['name'])).replace('@@USER@@',repr(ident['user']))
 subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B','-'],input=script,text=True,check=True)
else:root.mkdir(parents=True,exist_ok=False)
usage=shutil.disk_usage(root);source=shutil.disk_usage('/srv/dl_binner')
if usage.free<37*1024**3 or source.free<25*1024**3:raise ValueError('Separate native reserves/growth headroom required')
cfg['initial_filesystem_used_bytes']=usage.used
for n in ['payload','logs','tmp']:(root/n).mkdir()
sys.path.insert(0,str(repo/'scripts'))
from e024_coverage import binding
from e021_control_json import publish
from e032_phase import validate_config
wheel=base64.b64decode(@@WHEEL@@,validate=True)
with pathlib.Path(cfg['wheel']).open('xb') as f:f.write(wheel)
if binding(cfg['wheel'])!=cfg['financial']['wheel_binding']:raise ValueError('Native wheel bytes differ')
plan=json.loads((repo/'experiments/E032-biological-candidate-selection/runtime-plan.json').read_text())
plan.update(work=str(root/'work'),restored=str(root/'restored'),python=cfg['python'])
publish(plan,root/'science-plan.json');publish(cfg['financial'],root/'payload/financial-gate.json')
validate_config(cfg)
publish(dict(user=ident['user'],boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
    filesystem=usage._asdict(),source_filesystem=source._asdict(),post_mount_before_payload_used_bytes=usage.used,
    disk=disk,epoch=time.time()),root/'host.json');publish(cfg,root/'config.json')
p=subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B',str(repo/'scripts/e032_arm.py'),'--config',str(root/'config.json')],capture_output=True,text=True,timeout=150)
(root/'logs/arming.log').write_text(p.stdout+p.stderr);print(p.stdout+p.stderr,flush=True);p.check_returncode()
print('E032_HELD',json.dumps(dict(root=str(root),config=binding(root/'config.json'),plan=binding(root/'science-plan.json'),service_name=ident['service_name'])),flush=True)
'''
    code=code.replace('@@IDENT@@',repr(ident)).replace('@@DISK@@',repr(disk)).replace('@@CONFIG@@',repr(cfg))
    code=code.replace('@@WHEEL@@',repr(base64.b64encode(wheel.read_bytes()).decode()))
    compile(code,'actual E032 host','exec');return code


def render_release(ident,held,provider):
    """Bind the live current-boot parent/watchdog and independent provider fallback."""
    code=r'''import json,pathlib,subprocess,sys,time
ident=@@IDENT@@;held=@@HELD@@;provider=@@PROVIDER@@
root=pathlib.Path(ident['root']);sys.path.insert(0,str(pathlib.Path(ident['repo'])/'scripts'))
from e009_exit_watchdog import identity
from e021_control_json import publish
from e024_coverage import binding
from e032_phase import validate_config
cfg=json.loads((root/'config.json').read_text());validate_config(cfg)
watch=json.loads((pathlib.Path('/var/lib')/(cfg['service_name']+'-exit')/'status.json').read_text());started=json.loads((root/'started.json').read_text())
if watch['decision']!='workflow alive' or watch['expected_process']!=identity(started['pid']) or watch['observed_process']!=watch['expected_process'] or watch['boot_id']!=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Fresh held-process watcher differs')
if subprocess.check_output(['systemctl','is-active',cfg['service_name']+'-exit.timer'],text=True).strip()!='active':raise ValueError('Exit timer is not active')
if provider['status']!='RUNNING' or str(provider['scheduling']['maxRunDuration']['seconds'])!=str(cfg['limits']['provider_STOP_seconds']) or provider['scheduling']['instanceTerminationAction']!='STOP':raise ValueError('Independent provider fallback differs')
publish(provider,root/'logs/provider-before-release.json')
publish(dict(config=binding(root/'config.json'),plan=binding(root/'science-plan.json'),provider_STOP_verified=True,watchdog=watch,epoch=time.time()),root/'release.json')
print('E032_RELEASED',str(root),flush=True)
'''
    code=code.replace('@@IDENT@@',repr(ident)).replace('@@HELD@@',repr(held)).replace('@@PROVIDER@@',repr(provider))
    compile(code,'actual E032 release','exec');return code


def render_inventory(phase):
    """Compile the actual cleanup/inventory producer before a paid allocation."""
    code="""import pathlib,subprocess,json
folder=pathlib.Path('/srv/dl_binner/experiments/e032/inventory');folder.mkdir(parents=True,exist_ok=True)
p=subprocess.run(['/usr/bin/python3','-I','-B','/srv/dl_binner/repo/scripts/e032_cleanup.py','--output',str(folder/OUTPUT)],capture_output=True,text=True,timeout=180)
print(p.stdout+p.stderr,flush=True);p.check_returncode()
p=subprocess.run(['du','-x','-B1','--max-depth=1','/srv/dl_binner/experiments'],capture_output=True,text=True,timeout=120);print(p.stdout);print(p.stderr)
""".replace('OUTPUT',repr(phase+'.json'))
    compile(code,'actual E032 inventory','exec');return code


def start(out):
    """Admit all source/cost/schema gates before any cost-bearing operation."""
    out=Path(out).absolute()
    if (out/'identity.json').exists():raise ValueError('Attempt exists; no implicit clock reset or retry')
    f=json.loads((out/'financial-gate.json').read_text());freeze()
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Exact clean source required')
    if f['source_transport']['source']!=source:raise ValueError('Private exact source differs')
    phase='selection-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+source[:7]
    ident=dict(source=source,repo='/srv/dl_binner/repo',phase=phase,
        root='/srv/dl_binner/experiments/e032/'+phase,user='rasmus_allesoee_gmail_com',
        service_name='e032-'+phase,archive_prefix='gs://dl-binner-archive-167650584170/e032/'+phase+'/',vm_start_epoch=time.time())
    validate_config(config_value(ident,f,0));render_host(ident,f);render_release(ident,{}, {});render_inventory(phase)
    compile(source_sync(ident,f['source_transport']),'source consumer','exec')
    c=Cloud(out/'control');before=c.state();c.put('provider-before.json',before)
    if before['status']!='TERMINATED' or not before['machineType'].endswith('/e2-standard-8') or sorted(int(d['diskSizeGb']) for d in before['disks'])!=[30,300] or before.get('guestAccelerators'):
        raise ValueError('Existing stopped E2/original disks required')
    seconds=config_value(ident,f,0)['limits']['provider_STOP_seconds']
    try:
        c.call(['compute','instances','set-scheduling',CPU,'--no-restart-on-failure','--max-run-duration='+str(seconds)+'s','--instance-termination-action=STOP'],CPU_ZONE)
        c.call(['compute','instances','start',CPU],CPU_ZONE);live=c.state();c.put('provider-start.json',live)
        if live['status']!='RUNNING' or live['lastStartTimestamp']==before['lastStartTimestamp']:raise ValueError('Fresh boot absent')
        ident['vm_start_epoch']=datetime.datetime.fromisoformat(live['lastStartTimestamp']).timestamp();save(out/'identity.json',ident)
        for at in range(12):
            p=subprocess.run(SSH+['true'],capture_output=True,text=True,timeout=25)
            (out/('ssh-ready-'+str(at)+'.log')).write_text(p.stdout+p.stderr)
            if p.returncode==0:break
            time.sleep(2)
        else:raise RuntimeError('Pinned existing SSH unavailable')
        remote(out,'source-sync',source_sync(ident,f['source_transport']))
        inventory=remote(out,'headroom-inventory',render_inventory(phase),330)
        usage=json.loads(next(v.removeprefix('E032_HEADROOM ') for v in inventory.splitlines() if v.startswith('E032_HEADROOM ')))
        if usage['free']<25*1024**3:raise ValueError('Original source reserve requires verified cleanup before continuation')
        disk=None
        if usage['free']<37*1024**3:
            # The admitted source transports are protected; no arbitrary removal
            # of old scientific inputs/runtime evidence is a cleanup fallback.
            name='e032-task-'+str(int(ident['vm_start_epoch']))
            c.put('task-disk-decision.json',dict(measured=usage,needed_free_bytes=37*1024**3,
                verified_old_task_already_released=True,unbacked_required_E021_transports_preserved=True,
                no_verified_disposable_candidate_meets_gap=True,approved_single_40_GiB=True))
            c.call(['compute','disks','create',name,'--size=40GB','--type=pd-balanced','--labels=experiment=e032'],CPU_ZONE)
            disk=c.call(['compute','disks','describe',name],CPU_ZONE);c.put('new-task-disk.json',disk)
            if int(disk['sizeGb'])!=40 or disk.get('users') or not disk['type'].endswith('/pd-balanced'):raise ValueError('New task identity differs')
            c.call(['compute','instances','attach-disk',CPU,'--disk='+name,'--device-name='+name],CPU_ZONE)
        text=remote(out,'held-host',render_host(ident,f,disk),300)
        held=json.loads(next(v.removeprefix('E032_HELD ') for v in text.splitlines() if v.startswith('E032_HELD ')))
        save(out/'held.json',held);provider=c.state();c.put('provider-before-release.json',provider)
        remote(out,'release',render_release(ident,held,provider),90);save(out/'released.json',dict(epoch=time.time(),held=held))
    except BaseException as e:
        save(out/'failure.json',dict(error=repr(e),epoch=time.time()));c.stop();raise
    return ident


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True)
    a=p.parse_args();print(json.dumps(start(a.root)),flush=True)
