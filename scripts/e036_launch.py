#!/usr/bin/env python3
"""Start one source/credit-bound E036 CPU phase with conditional task scratch.

Only the existing E2 and authorized conditional 64 GiB disk are exposed. No automatic
retry/reinstall/retention extension is possible. All submitted programs and API
responses are retained; the held native parent owns science and shutdown.
"""
import argparse,base64,datetime,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e021_portable_cloud import Cloud,CPU,CPU_ZONE
from e024_coverage import binding
from e031_launch import source_code,save
from e033_launch import remote,SSH
from e036_phase import validate_config
EXP=ROOT/'experiments/E036-optional-pooled-links';BRANCH='optional-pooled-links'


def frozen():
    """Verify all prospective science and operations bytes before cost-bearing work."""
    for name in ['source-lock.json']:
        for n,b in json.loads((EXP/name).read_text())['files'].items():
            if binding(ROOT/n)!=b:raise ValueError('Frozen E036 source differs: '+n)


def source_sync(ident,transport):
    """Use the owner-approved private exact commit, preserving read-only GitHub."""
    return source_code(ident,transport).replace('bootstrap-preserving-learning',BRANCH).replace('experiments/e031/source-transports','experiments/e036/source-transports')


def config_value(ident,f,used=0,device=0):
    """Produce the held parent's complete exact clock/device/source schema."""
    p=json.loads((EXP/'runtime-plan.json').read_text());r=json.loads((ROOT/'experiments/E033-multiscale-bam/reuse-lock.json').read_text());l=p['limits'];root=ident['root'];start=ident['vm_start_epoch']
    return dict(root=root,repo=ident['repo'],source_commit=ident['source'],operations_source=ident['source'],vm_start_epoch=start,
        review_deadline_epoch=start+l['seconds'],provider_deadline_epoch=start+l['provider_STOP_seconds'],setup_deadline_epoch=start+3600,
        service_name=ident['service_name'],user=ident['user'],archive_prefix=ident['archive_prefix'],plan=root+'/science-plan.json',
        python=root+'/task/env/bin/python',workflow_python=p['workflow_python'],base=r['native_dependency_base'],reference=r['native_runtime_reference'],
        wheel=root+'/payload/dl_binner-0.1.0.dev11-py3-none-any.whl',pysam_wheel=f['native_pysam_path'],gcloud='/snap/bin/gcloud',
        samtools='/srv/dl_binner/experiments/e009/envs/data-cpu-v1-ae654b442315/bin/samtools',financial=f,
        initial_filesystem_used_bytes=used,initial_filesystem_device=device,source_filesystem='/srv/dl_binner',task_filesystem=root+'/task',limits=l)


def render_inventory(ident):
    """Measure source headroom and retain safe-cleanup evidence without deletions."""
    return '''import json,os,pathlib,shutil,subprocess
root=pathlib.Path('/srv/dl_binner');out=root/'experiments/e036/inventory';out.mkdir(parents=True,exist_ok=True)
usage=shutil.disk_usage(root)
p=subprocess.run(['du','-x','-B1','--max-depth=2',str(root/'experiments')],capture_output=True,text=True,timeout=180)
(out/(@@PHASE@@+'.du')).write_text(p.stdout+p.stderr);p.check_returncode()
print('E036_HEADROOM',json.dumps(dict(usage._asdict(),device=os.stat(root).st_dev,epoch=__import__('time').time(),required_peak_plus_reserve_bytes=45*1024**3,accepted_inputs_runtimes_and_failed_evidence_preserved=True)),flush=True)
'''.replace('@@PHASE@@',repr(ident['phase']))


def render_host(ident,f,disk=None):
    """Format only positively identified empty new scratch, then arm a held parent."""
    cfg=config_value(ident,f);wheel=Path(f['wheel_path'])
    if binding(wheel)!=f['wheel_binding']:raise ValueError('Local payload changed')
    code=r'''import base64,json,os,pathlib,pwd,shutil,subprocess,sys,time
ident=@@IDENT@@;disk=@@DISK@@;cfg=@@CONFIG@@
repo=pathlib.Path(ident['repo']);root=pathlib.Path(ident['root']);task=root/'task'
if not os.path.ismount('/srv/dl_binner')or os.cpu_count()!=8:raise ValueError('Original CPU/source mount required')
root.mkdir(parents=True,exist_ok=False)
if disk:
 script=r"""import os,pathlib,subprocess,json,pwd
task=pathlib.Path(@@TASK@@);name=@@NAME@@;dev=pathlib.Path('/dev/disk/by-id/google-'+name)
if not name.startswith('e036-task-')or task.exists():raise ValueError('Fresh approved task required')
subprocess.run(['udevadm','settle','--timeout=15'],check=True)
rows=json.loads(subprocess.check_output(['lsblk','-J','-b','-o','NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT',str(dev)],text=True))['blockdevices']
if len(rows)!=1 or rows[0]['size']!=64*1024**3 or rows[0]['type']!='disk'or rows[0].get('fstype')or rows[0].get('mountpoint')or rows[0].get('children'):raise ValueError('Only exact new empty 64 GiB disk may be formatted')
if subprocess.run(['blkid',str(dev)],capture_output=True).returncode!=2:raise ValueError('Existing disk signature refused')
subprocess.run(['mkfs.ext4','-m','0','-L','e036-task',str(dev)],check=True,capture_output=True)
task.mkdir();subprocess.run(['mount','-o','nodev,nosuid',str(dev),str(task)],check=True)
account=pwd.getpwnam(@@USER@@);os.chown(task,account.pw_uid,account.pw_gid)
actual=pathlib.Path(subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(task)],text=True).strip())
if actual.resolve()!=dev.resolve()or os.stat(task).st_dev==os.stat('/srv/dl_binner').st_dev:raise ValueError('Task device differs')
""".replace('@@TASK@@',repr(str(task))).replace('@@NAME@@',repr(disk['name'])).replace('@@USER@@',repr(ident['user']))
 subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B','-'],input=script,text=True,check=True)
else:task.mkdir()
usage=shutil.disk_usage(task);source=shutil.disk_usage('/srv/dl_binner')
if usage.free<45*1024**3 or source.free<25*1024**3:raise ValueError('Measured full peak plus separate reserves required')
cfg['initial_filesystem_used_bytes']=usage.used;cfg['initial_filesystem_device']=os.stat(task).st_dev
for n in ['payload','logs','tmp','gates']:(root/n).mkdir()
sys.path.insert(0,str(repo/'scripts'))
from e024_coverage import binding
from e021_control_json import publish
from e036_phase import validate_config
from e036_control import freeze
freeze()
wheel=root/'payload/dl_binner-0.1.0.dev11-py3-none-any.whl'
with wheel.open('xb')as f:f.write(base64.b64decode(@@WHEEL@@,validate=True))
if binding(wheel)!=cfg['financial']['wheel_binding']or binding(cfg['pysam_wheel'])!=cfg['financial']['pysam_binding']:raise ValueError('Exact new/retained dependency payload differs; no fallback')
plan=json.loads((repo/'experiments/E036-optional-pooled-links/runtime-plan.json').read_text().replace('NEW_PHASE',ident['phase']))
if plan['python']!=cfg['python']:raise ValueError('Produced native plan interpreter differs')
publish(plan,root/'science-plan.json');publish(cfg['financial'],root/'payload/financial-gate.json');validate_config(cfg)
publish(dict(user=ident['user'],boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),filesystem=usage._asdict(),source_filesystem=source._asdict(),post_mount_before_payload_used_bytes=usage.used,device=cfg['initial_filesystem_device'],disk=disk,epoch=time.time()),root/'host.json');publish(cfg,root/'config.json')
p=subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B',str(repo/'scripts/e036_arm.py'),'--config',str(root/'config.json')],capture_output=True,text=True,timeout=180)
(root/'logs/arming.log').write_text(p.stdout+p.stderr);print(p.stdout+p.stderr,flush=True);p.check_returncode()
print('E036_HELD',json.dumps(dict(root=str(root),config=binding(root/'config.json'),plan=binding(root/'science-plan.json'),service_name=ident['service_name'])),flush=True)
'''
    code=code.replace('@@IDENT@@',repr(ident)).replace('@@DISK@@',repr(disk)).replace('@@CONFIG@@',repr(cfg)).replace('@@WHEEL@@',repr(base64.b64encode(wheel.read_bytes()).decode()))
    compile(code,'Actual E036 host/schema producer','exec');return code


def render_release(ident,provider):
    """Bind actual boot/PID/STOP, cancel setup fallback, publish atomic release."""
    code=r'''import json,pathlib,subprocess,sys,time,datetime
ident=@@IDENT@@;provider=@@PROVIDER@@;root=pathlib.Path(ident['root']);sys.path.insert(0,str(pathlib.Path(ident['repo'])/'scripts'))
from e009_exit_watchdog import identity
from e021_control_json import publish
from e024_coverage import binding
from e036_phase import validate_config
c=json.loads((root/'config.json').read_text());validate_config(c);started=json.loads((root/'started.json').read_text());watch=json.loads((pathlib.Path('/var/lib')/(c['service_name']+'-exit')/'status.json').read_text())
if watch['decision']!='workflow alive'or watch['expected_process']!=identity(started['pid'])or watch['observed_process']!=watch['expected_process']or watch['boot_id']!=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Fresh held process/boot watcher differs')
if subprocess.check_output(['systemctl','is-active',c['service_name']+'-exit.timer'],text=True).strip()!='active':raise ValueError('Exit timer inactive')
if provider['status']!='RUNNING'or provider['scheduling']['instanceTerminationAction']!='STOP'or datetime.datetime.fromisoformat(provider['lastStartTimestamp']).timestamp()!=c['vm_start_epoch']or int(provider['scheduling']['maxRunDuration']['seconds'])!=c['limits']['provider_STOP_seconds']:raise ValueError('Independent provider STOP differs')
publish(provider,root/'logs/provider-before-release.json')
subprocess.run(['sudo','-n','systemctl','stop',ident['setup_timer']+'.timer'],check=True)
publish(dict(config=binding(root/'config.json'),plan=binding(root/'science-plan.json'),watchdog_verified=True,provider_STOP_verified=True,epoch=time.time()),root/'release.json')
print('E036_RELEASED',str(root),flush=True)
'''
    code=code.replace('@@IDENT@@',repr(ident)).replace('@@PROVIDER@@',repr(provider));compile(code,'E036 atomic release','exec');return code


def preflight(ident,f,check_source=True):
    """Validate actual complete producer schema and compile submitted programs."""
    if check_source:frozen()
    validate_config(config_value(ident,f));render_host(ident,f);render_release(ident,{})
    compile(render_inventory(ident),'inventory','exec');compile(source_sync(ident,f['source_transport']),'private exact source','exec')


def start(out):
    """Perform one authorized start, preserving journals and stopping on failure."""
    out=Path(out).absolute();f=json.loads((out/'financial-gate.json').read_text());source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if (out/'identity.json').exists()or subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Fresh attempt and exact clean source required')
    if f['source_transport']['source']!=source:raise ValueError('Private source differs')
    phase='optional-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+source[:7]
    ident=dict(source=source,repo='/srv/dl_binner/repo',phase=phase,root='/srv/dl_binner/experiments/e036/'+phase,user='rasmus_allesoee_gmail_com',service_name='e036-'+phase,setup_timer='e036-setup-'+str(int(time.time())),archive_prefix='gs://dl-binner-archive-167650584170/e036/'+phase+'/',vm_start_epoch=time.time())
    preflight(ident,f);c=Cloud(out/'control');before=c.state();c.put('provider-before.json',before)
    if before['status']!='TERMINATED'or not before['machineType'].endswith('/e2-standard-8')or sorted(int(d['diskSizeGb'])for d in before['disks'])!=[30,300]or before.get('guestAccelerators'):raise ValueError('Original stopped E2 and 30/300 GiB disks required')
    try:
        seconds=json.loads((EXP/'limits.json').read_text())['provider_STOP_seconds']
        c.call(['compute','instances','set-scheduling',CPU,'--no-restart-on-failure','--max-run-duration='+str(seconds)+'s','--instance-termination-action=STOP'],CPU_ZONE)
        checked=c.state();c.put('provider-STOP-before-start.json',checked)
        if checked['scheduling']['instanceTerminationAction']!='STOP'or int(checked['scheduling']['maxRunDuration']['seconds'])!=seconds:raise ValueError('Pre-start provider STOP differs')
        c.call(['compute','instances','start',CPU],CPU_ZONE);live=c.state();c.put('provider-start.json',live)
        if live['status']!='RUNNING'or live['lastStartTimestamp']==before['lastStartTimestamp']:raise ValueError('Fresh actual start missing')
        ident['vm_start_epoch']=datetime.datetime.fromisoformat(live['lastStartTimestamp']).timestamp();validate_config(config_value(ident,f));save(out/'identity.json',ident)
        # A short independent setup fallback precedes the full held watcher.
        for at in range(10):
            p=subprocess.run(SSH+['true'],capture_output=True,text=True,timeout=60);(out/('ssh-'+str(at)+'.log')).write_text(p.stdout+p.stderr)
            if p.returncode==0:break
            time.sleep(2)
        else:raise RuntimeError('Pinned SSH unavailable')
        setup="import subprocess\nsubprocess.run(['sudo','-n','systemd-run','--unit',"+repr(ident['setup_timer'])+",'--on-active=30m','/usr/sbin/shutdown','-h','now'],check=True)\n"
        remote(out,'setup-shutdown',setup)
        remote(out,'source-sync',source_sync(ident,f['source_transport']))
        value=remote(out,'headroom',render_inventory(ident),240)
        headroom=json.loads(next(x.removeprefix('E036_HEADROOM ')for x in value.splitlines()if x.startswith('E036_HEADROOM ')))
        save(out/'headroom.json',headroom)
        if headroom['free']<25*1024**3:raise ValueError('Source reserve violated; only verified safe cleanup may repair')
        disk=None
        if headroom['free']<45*1024**3:
            # Pause only for the agent's inspection of the actual retained du
            # journal. This is not a new owner approval or an execution clock.
            print('E036_AWAITING_HEADROOM_REVIEW',str(out/'headroom.json'),flush=True)
            until=time.time()+600;decision=out/'disk-decision.json'
            while not decision.exists():
                if time.time()>until:raise TimeoutError('Bounded live headroom review expired')
                time.sleep(1)
            reviewed=json.loads(decision.read_text())
            if reviewed.get('headroom')!=binding(out/'headroom.json')or reviewed.get('safe_cleanup_insufficient')is not True or not reviewed.get('reason'):raise ValueError('Actual headroom/cleanup review missing')
            quota=c.call(['compute','regions','describe','us-central1']);q={x['metric']:x for x in quota['quotas']}
            if q['SSD_TOTAL_GB']['limit']-q['SSD_TOTAL_GB']['usage']<64:raise ValueError('Existing quota cannot fit approved scratch')
            # No large disposable targets remain in the retained source. Accepted
            # runtime/data/failed journals are not cleanup candidates.
            c.put('task-disk-decision.json',dict(measured=headroom,source_cleanup_review=reviewed,safe_cleanup_cannot_supply_45GiB=True))
            name='e036-task-'+str(int(ident['vm_start_epoch']));c.call(['compute','disks','create',name,'--size=64GB','--type=pd-balanced','--labels=experiment=e036'],CPU_ZONE)
            disk=c.call(['compute','disks','describe',name],CPU_ZONE);c.put('new-task-disk.json',disk)
            if disk.get('users')or int(disk['sizeGb'])!=64 or not disk['type'].endswith('/pd-balanced'):raise ValueError('Fresh task identity differs')
            c.call(['compute','instances','attach-disk',CPU,'--disk='+name,'--device-name='+name],CPU_ZONE)
        value=remote(out,'held-host',render_host(ident,f,disk),360);save(out/'held.json',dict(raw=value,epoch=time.time()))
        provider=c.state();c.put('provider-before-release.json',provider);remote(out,'release',render_release(ident,provider),90);save(out/'released.json',dict(epoch=time.time()))
    except BaseException as error:
        save(out/('failure-'+str(time.time_ns())+'.json'),dict(error=repr(error),epoch=time.time()));c.stop();raise
    return ident


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True,type=Path);a=p.parse_args();print(json.dumps(start(a.root)),flush=True)
