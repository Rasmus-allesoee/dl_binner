#!/usr/bin/env python3
"""Connect the frozen E031 phase to the existing VM and optional task disk.

This controller is operational glue. It cannot alter product science, fit a
learner during the bridge, publish private history or extend retention. Every
rendered SSH consumer is retained and compiled before use. Failures stop the VM;
accepted stages and any attached disk remain for explicit verified recovery.
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
from e024_coverage import binding
from e031_control import freeze

BRANCH='bootstrap-preserving-learning'
SSH=['ssh','-o','ControlMaster=no','-o','ControlPath=none','-o','ConnectTimeout=12','dl-binner-gcp']


def save(path,value):
    """Keep a new local controller receipt without overwriting an earlier attempt."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def remote(out,label,code,seconds=240):
    """Compile and retain exactly the program submitted through pinned SSH."""
    compile(code,'E031-'+label,'exec');tag=label+'-'+str(time.time_ns())
    (out/(tag+'.py')).write_text(code)
    p=subprocess.run(SSH+['/usr/bin/python3 -I -B -'],input=code,capture_output=True,text=True,timeout=seconds)
    (out/(tag+'.log')).write_text(p.stdout+p.stderr)
    print(p.stdout+p.stderr,flush=True);p.check_returncode()
    return p.stdout


def source_code(ident,transport):
    """Render private exact-commit import; never publish financial/account history."""
    packet=Path(transport['path'])
    if transport['kind']!='private_exact_Git_bundle' or binding(packet)!=transport['bundle']:
        raise ValueError('Exact source transport differs')
    code=r'''import base64,hashlib,json,os,pathlib,subprocess,time
ident=IDENTITY;transport=TRANSPORT
repo=pathlib.Path(ident['repo'])
if not os.path.ismount('/srv/dl_binner'):
 subprocess.run(['sudo','-n','mount','-U','f76283ed-60c4-4060-bd22-84c95f38d3fb','/srv/dl_binner'],check=True)
if not os.path.ismount('/srv/dl_binner') or os.cpu_count()!=8:raise ValueError('Existing allocation/mount differs')
def call(argv):return subprocess.check_output(argv,cwd=repo,text=True).strip()
if call(['git','status','--porcelain']):raise ValueError('Preserve dirty native checkout')
folder=repo.parent/'experiments/e031/source-transports';folder.mkdir(parents=True,exist_ok=True)
packet=folder/('source-'+ident['source']+'.bundle');private=folder/('.source-'+str(time.time_ns()))
value=base64.b64decode(PAYLOAD,validate=True)
if dict(bytes=len(value),sha256=hashlib.sha256(value).hexdigest())!=transport['bundle']:raise ValueError('Transport bytes differ')
with private.open('xb')as f:f.write(value);f.flush();os.fsync(f.fileno())
try:os.link(private,packet)
finally:private.unlink()
if call(['git','rev-parse',transport['base']+'^{commit}'])!=transport['base']:raise ValueError('Existing private source base missing; no fallback fetch')
call(['git','bundle','verify',str(packet)])
if call(['git','bundle','list-heads',str(packet)]).split()!=[ident['source'],'refs/heads/bootstrap-preserving-learning']:raise ValueError('Advertised private head differs')
call(['git','fetch',str(packet),'refs/heads/bootstrap-preserving-learning'])
if call(['git','rev-parse','FETCH_HEAD'])!=ident['source']:raise ValueError('Private fetched head differs')
call(['git','checkout','--detach',ident['source']])
if call(['git','status','--porcelain']):raise ValueError('Exact checkout dirty')
print('E031_SOURCE_SYNC',json.dumps(dict(status='PASS',source=ident['source'],base=transport['base'],bundle=transport['bundle'],path=str(packet),GitHub_access_read_only=True,public_push=False)),flush=True)
'''
    return code.replace('IDENTITY',repr(ident)).replace('TRANSPORT',repr(transport)).replace('PAYLOAD',repr(base64.b64encode(packet.read_bytes()).decode()))


def inventory_code(ident):
    """Inspect original files and only the approved redundant transport candidates."""
    return r'''import json,os,pathlib,shutil,subprocess,time,sys
ident=IDENTITY;repo=pathlib.Path(ident['repo'])
plan=repo/'experiments/E031-bootstrap-preserving-learning/cleanup-plan.json'
folder=repo.parent/'experiments/e031/inventory';folder.mkdir(parents=True,exist_ok=True)
out=folder/(ident['phase']+'-cleanup.json')
before=shutil.disk_usage('/srv/dl_binner')
clean=subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B',str(repo/'scripts/e030_cleanup.py'),'--plan',str(plan),'--output',str(out)],capture_output=True,text=True,timeout=240)
(folder/(ident['phase']+'-cleanup-terminal.log')).write_text(clean.stdout+clean.stderr)
print(clean.stdout+clean.stderr,flush=True);clean.check_returncode()
after=shutil.disk_usage('/srv/dl_binner')
du=subprocess.run(['du','-x','-B1','--max-depth=2','/srv/dl_binner/experiments'],capture_output=True,text=True,timeout=120)
(folder/(ident['phase']+'-du.txt')).write_text(du.stdout+du.stderr)
print('E031_HEADROOM',json.dumps(dict(before=before._asdict(),after=after._asdict(),cleanup=json.loads(out.read_text()),source_device=os.stat('/srv/dl_binner').st_dev,source_used_baseline=before.used,epoch=time.time())),flush=True)
'''.replace('IDENTITY',repr(ident))


def scratch_mount_code(ident):
    """Format only the newly created, exactly sized and positively named empty disk."""
    return r'''import json,os,pathlib,subprocess
ident=IDENTITY;root=pathlib.Path(ident['root']);name=ident['scratch']['name']
subprocess.run(['sudo','-n','udevadm','settle','--timeout=15'],check=True)
device=pathlib.Path('/dev/disk/by-id/google-'+name)
if not name.startswith('e031-bridge-scratch-') or not device.exists():raise ValueError('New task disk identity missing')
row=subprocess.check_output(['lsblk','-b','-dn','-o','TYPE,SIZE',str(device)],text=True).strip().split()
if row!=['disk',str(40*1024**3)]:raise ValueError('New task device type/size differs')
if subprocess.run(['findmnt','-rn','-S',str(device)],capture_output=True).returncode==0:raise ValueError('New task disk already mounted')
signatures=subprocess.check_output(['sudo','-n','wipefs','--no-act','--noheadings',str(device)],text=True).strip()
if signatures:raise ValueError('Task disk is not empty; never format existing data')
if root.exists():raise ValueError('Fresh phase mountpoint required')
root.mkdir(parents=True)
subprocess.run(['sudo','-n','mkfs.ext4','-q','-m','0',str(device)],check=True)
subprocess.run(['sudo','-n','mount','-o','nodev,nosuid',str(device),str(root)],check=True)
subprocess.run(['sudo','-n','chown',str(os.getuid())+':'+str(os.getgid()),str(root)],check=True)
if not os.path.ismount(root) or os.stat(root).st_dev==os.stat('/srv/dl_binner').st_dev:raise ValueError('Task mount is not the new filesystem')
print('E031_NEW_TASK_MOUNT',json.dumps(dict(device=str(device),real_device=str(device.resolve()),root=str(root),original_disks_formatted=False)),flush=True)
'''.replace('IDENTITY',repr(ident))


def host_code(ident,financial):
    """Render mounted-device baseline, payload, held watcher and native-gate dispatch."""
    wheel=Path(financial['wheel_path'])
    if binding(wheel)!=financial['wheel_binding']:raise ValueError('Prepared wheel differs')
    code=r'''import base64,hashlib,json,os,pathlib,pwd,shutil,subprocess,sys,time
ident=IDENTITY;financial=FINANCIAL;root=pathlib.Path(ident['root']);repo=pathlib.Path(ident['repo'])
if ident.get('scratch'):
 if not os.path.ismount(root):raise ValueError('Admitted scratch mount missing')
else:root.mkdir(parents=True,exist_ok=False)
baseline=shutil.disk_usage(root);device=os.stat(root).st_dev
if baseline.free<33*1024**3 or shutil.disk_usage('/srv/dl_binner').free<25*1024**3:raise ValueError('Complete task/source headroom unavailable')
for name in ['logs','tmp','payload']:(root/name).mkdir(exist_ok=False)
sys.path.insert(0,str(repo/'scripts'))
from e021_control_json import publish
from e024_coverage import binding
from e031_control import freeze
freeze()
launch=json.loads((repo/'experiments/E031-bootstrap-preserving-learning/native-launch-lock.json').read_text())
launch_files={}
for name,wanted in launch['files'].items():
 if binding(repo/name)!=wanted:raise ValueError('Native launch source changed: '+name)
 target=root/'payload/launch-source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(repo/name,target)
 launch_files[str(target)]=binding(target)
launch_target=root/'payload/launch-source/native-launch-lock.json';shutil.copyfile(repo/'experiments/E031-bootstrap-preserving-learning/native-launch-lock.json',launch_target)
launch_files[str(launch_target)]=binding(launch_target)
publish(dict(status='PASS',retained=launch_files),root/'payload/native-launch-source.json')
wheel=root/'payload/dl_binner-0.1.0.dev9-py3-none-any.whl';value=base64.b64decode(WHEEL,validate=True)
if dict(bytes=len(value),sha256=hashlib.sha256(value).hexdigest())!=financial['wheel_binding']:raise ValueError('Wheel transfer differs')
with wheel.open('xb')as f:f.write(value)
h=dict(initial_filesystem_used_bytes=baseline.used,filesystem=baseline._asdict(),filesystem_device=device,baseline_epoch=time.time(),boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),user=pwd.getpwuid(os.getuid()).pw_name,logical_cpus=os.cpu_count(),gcloud=shutil.which('gcloud'),scratch=ident.get('scratch'),source_filesystem=shutil.disk_usage('/srv/dl_binner')._asdict())
if h['gcloud']!='/snap/bin/gcloud':raise ValueError('Existing CLI path differs; no reinstall')
publish(h,root/'host.json');publish(financial,root/'payload/financial-gate.json');publish(ident,root/'identity.json')
p=json.loads((repo/'experiments/E031-bootstrap-preserving-learning/bridge-plan.json').read_text())
p['work']=str(root/'work');p['python']=str(root/'env/bin/python');p['wheel']=str(wheel);publish(p,root/'science-plan.json')
cfg=dict(root=str(root),work=p['work'],repo=str(repo),plan=str(root/'science-plan.json'),source_commit=ident['source'],limits=p['limits'],vm_start_epoch=ident['vm_start_epoch'],initial_filesystem_used_bytes=baseline.used,filesystem_device=device,gcloud=h['gcloud'],archive_prefix=ident['archive_prefix'],watchdog_live=str(root/'logs/watchdog-live-before-release.json'),service_name=ident['service_name'])
publish(cfg,root/'config.json')
publish(dict(data_copied=False,reuse_lock=binding(p['reuse_lock']),units=p['units'],scope='Accepted original inputs and E023 result stay in place; new actors only'),root/'external-data.json')
(root/'logs/process-inventory.txt').write_text(subprocess.check_output(['ps','-eo','pid,ppid,etime,pcpu,rss,args'],text=True))
arm=subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B',str(repo/'scripts/e031_arm.py'),'--config',str(root/'config.json')],capture_output=True,text=True)
(root/'logs/arm-terminal.log').write_text(arm.stdout+arm.stderr);print(arm.stdout+arm.stderr,flush=True);arm.check_returncode()
remaining=int(ident['vm_start_epoch']+2700-time.time())
if remaining<300:raise TimeoutError('Original setup clock exhausted')
argv=['sudo','-n','systemd-run','--unit='+ident['service_name']+'-gates','--uid='+h['user'],'--working-directory='+str(repo),'--property=Restart=no','--property=MemoryMax=26000000000','--property=CPUAffinity=0 1 2 3','--property=RuntimeMaxSec='+str(remaining),'--property=KillMode=control-group','--property=TimeoutStopSec=30','--property=StandardOutput=append:'+str(root/'logs/gates-terminal.log'),'--property=StandardError=append:'+str(root/'logs/gates-terminal.log'),'--setenv=OMP_NUM_THREADS=4','--setenv=OPENBLAS_NUM_THREADS=4','--setenv=MKL_NUM_THREADS=4','--setenv=NUMBA_NUM_THREADS=4','--setenv=PYTHONDONTWRITEBYTECODE=1','/usr/bin/python3','-u','-I','-B',str(repo/'scripts/e031_gates.py'),'--config',str(root/'config.json')]
subprocess.run(argv,check=True)
print('E031_HELD_GATES',json.dumps(dict(root=str(root),config=binding(root/'config.json'),host=h)),flush=True)
'''
    return code.replace('IDENTITY',repr(ident)).replace('FINANCIAL',repr(financial)).replace('WHEEL',repr(base64.b64encode(wheel.read_bytes()).decode()))


def release_code(ident,provider):
    """Render one atomic release against actual boot, gates, finance and task device."""
    return r'''import json,pathlib,subprocess,sys,time,shutil
ident=IDENTITY;provider=PROVIDER;root=pathlib.Path(ident['root']);repo=pathlib.Path(ident['repo']);sys.path.insert(0,str(repo/'scripts'))
from e021_control_json import publish
from e024_coverage import binding
from e031_phase import admission,filesystem_contract
from e031_control import freeze
from e009_exit_watchdog import identity
freeze();cfg=json.loads((root/'config.json').read_text());cfg['_path']=str(root/'config.json')
gate=json.loads((root/'gates/completion.json').read_text())
if gate['status']!='PASS' or gate['config']!=binding(root/'config.json'):raise ValueError('Actual native gates absent/differ')
if time.time()+10800+900>ident['vm_start_epoch']+cfg['limits']['seconds']:raise TimeoutError('Complete bridge forecast no longer fits original clock')
started=json.loads((root/'started.json').read_text());process=identity(started['pid'])
if process!=started['identity']:raise ValueError('Held parent identity changed')
w=json.loads((pathlib.Path('/var/lib')/(ident['service_name']+'-exit')/'status.json').read_text())
if w['decision']!='workflow alive' or w['expected_process']!=process or w['observed_process']!=process or w['boot_id']!=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Fresh held watcher mismatch')
if subprocess.check_output(['systemctl','is-active',ident['service_name']+'-exit.timer'],text=True).strip()!='active':raise ValueError('Watcher inactive')
f=json.loads((root/'payload/financial-gate.json').read_text());limits=cfg['limits']
if time.time()-f['checked_epoch']>7200 or f['new_incremental_gross_ceiling_USD']!=limits['ceiling_USD']:raise ValueError('Fresh complete financial gate expired/differs')
filesystem_contract(root,cfg)
if shutil.disk_usage(root).free<32*1024**3 or shutil.disk_usage('/srv/dl_binner').free<25*1024**3:raise ValueError('Release task/source reserve unavailable')
proof=root/'logs/provider-before-release.json';publish(provider,proof)
paths=[root/'gates/completion.json',root/'gates/source.json',root/'gates/runtime.json',root/'gates/data.json',root/'logs/supervision.json',root/'logs/watchdog-native-tests.log',root/'logs/maintenance-restart-refused.json',proof,root/'payload/financial-gate.json',root/'external-data.json',root/'host.json',root/'identity.json']
launch_source=root/'payload/native-launch-source.json';paths.append(launch_source)
for name,wanted in json.loads(launch_source.read_text())['retained'].items():
 if binding(name)!=wanted:raise ValueError('Retained launch supplement differs')
 paths.append(pathlib.Path(name))
release=dict(config=binding(root/'config.json'),plan=binding(cfg['plan']),vm_start_epoch=ident['vm_start_epoch'],credit_gate_passed=True,pending_usage_accounted=True,native_gates_passed=True,watchdog_verified=True,provider_STOP_verified=True,existing_VM_only=True,full_axes_verified=True,headroom_measured=True,retention_passed=True,resource_scope_verified=True,mount_baseline_verified=True,real_money_authorized=False,estimated_incremental_gross_USD=f['estimated_complete_gross_USD'],ceiling_USD=limits['ceiling_USD'],provider_STOP_seconds=limits['provider_STOP_seconds'],storage_retention_extended=False,credit_valid_until_epoch=f['credit_valid_until_epoch'],storage_valid_until_epoch=f['storage_valid_until_epoch'],covered_costs=['compute','disk','storage','network','operations'],gate_files={str(p):binding(p) for p in paths})
admission(cfg,release,time.time());publish(release,root/'release.json')
print('E031_RELEASED',json.dumps(dict(epoch=time.time(),release=binding(root/'release.json'),supervision=w)),flush=True)
'''.replace('IDENTITY',repr(ident)).replace('PROVIDER',repr(provider))


def start(out):
    """Start once after local admission; only measured need may create one task disk."""
    out=Path(out).absolute();out.mkdir(parents=True,exist_ok=True)
    if (out/'identity.json').exists():raise ValueError('Attempt exists; do not reset its original clock')
    f=json.loads((out/'financial-gate.json').read_text());freeze()
    if f['real_money_authorized'] is not False or f['coverage_status']!='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY':raise ValueError('Credit-only gate missing')
    if not 0<=f['estimated_complete_gross_USD']<=4 or f['new_incremental_gross_ceiling_USD']!=4:raise ValueError('Bridge complete envelope differs')
    if time.time()-f['checked_epoch']>7200 or time.time()+22500>=f['storage_valid_until_epoch']:raise ValueError('Fresh finance/retention gate failed')
    for p,wanted in f['local_gate_files'].items():
        if binding(p)!=wanted:raise ValueError('Local admission bytes changed: '+p)
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Exact clean source required')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();transport=f['source_transport']
    if transport['source']!=source or binding(transport['path'])!=transport['bundle']:raise ValueError('Exact private source differs')
    p=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/bridge-plan.json').read_text());limits=p['limits']
    c=Cloud(out/'control-plane');before=c.state();c.put('provider-before.json',before)
    if before['status']!='TERMINATED' or not before['machineType'].endswith('/e2-standard-8') or before.get('guestAccelerators'):raise ValueError('Original stopped E2 required')
    if [int(d['diskSizeGb'])for d in before['disks']]!=[30,300] or any(d['autoDelete']for d in before['disks']):raise ValueError('Original persistent disks differ')
    if not before['shieldedInstanceConfig']['enableSecureBoot']:raise ValueError('Secure Boot differs')
    phase='bridge-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+source[:7]
    ident=dict(root='/srv/dl_binner/experiments/e031/'+phase,repo='/srv/dl_binner/repo',source=source,phase=phase,user='rasmus_allesoee_gmail_com',service_name='e031-'+phase,archive_prefix='gs://dl-binner-archive-167650584170/e031/'+phase+'/',vm_start_epoch=0,provider_max_duration_seconds=limits['provider_STOP_seconds'],scratch=None)
    compile(source_code(ident,transport),'private-source','exec');compile(inventory_code(ident),'headroom','exec');compile(host_code(ident,f),'host','exec');compile(release_code(ident,before),'release','exec')
    c.call(['compute','instances','set-scheduling',CPU,'--no-restart-on-failure','--max-run-duration='+str(limits['provider_STOP_seconds'])+'s','--instance-termination-action=STOP'],CPU_ZONE)
    armed=c.state();c.put('provider-STOP-readback.json',armed)
    if str(armed['scheduling']['maxRunDuration']['seconds'])!=str(limits['provider_STOP_seconds']) or armed['scheduling']['instanceTerminationAction']!='STOP' or armed['scheduling']['automaticRestart']:raise ValueError('Provider STOP/restart differs')
    try:
        c.call(['compute','instances','start',CPU],CPU_ZONE);live=c.state()
        if live['status']!='RUNNING' or live['lastStartTimestamp']==before['lastStartTimestamp']:raise ValueError('Fresh original boot absent')
        ident['vm_start_epoch']=datetime.datetime.fromisoformat(live['lastStartTimestamp']).timestamp();ident['allocation_start_epoch']=ident['vm_start_epoch']
        save(out/'identity.json',ident);c.put('provider-start.json',live)
        for i in range(12):
            value=subprocess.run(SSH+['true'],capture_output=True,text=True,timeout=25)
            (out/('ssh-ready-'+str(i)+'.log')).write_text(value.stdout+value.stderr)
            if not value.returncode:break
            time.sleep(2)
        else:raise RuntimeError('Pinned SSH unavailable; no credential replacement')
        remote(out,'source',source_code(ident,transport))
        text=remote(out,'headroom',inventory_code(ident),240)
        head=json.loads(next(s.removeprefix('E031_HEADROOM ')for s in text.splitlines()if s.startswith('E031_HEADROOM ')));save(out/'native-headroom.json',head)
        if head['after']['free']<33*1024**3:
            if f.get('temporary_40_GiB_task_disk_owner_approved') is not True:raise ValueError('Separate task disk not admitted')
            if head['after']['free']<25*1024**3:raise ValueError('Original input reserve unavailable')
            q=c.call(['compute','regions','describe','us-central1']);quota=next(x for x in q['quotas']if x['metric']=='SSD_TOTAL_GB')
            if quota['limit']-quota['usage']<40:raise ValueError('Existing balanced quota insufficient; no request fallback')
            name='e031-bridge-scratch-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')
            if c.call(['compute','disks','list','--filter=name='+name]):raise ValueError('New task disk name already exists')
            c.call(['compute','disks','create',name,'--size=40GB','--type=pd-balanced','--labels=experiment=e031,scope=temporary-task'],CPU_ZONE)
            disk=c.call(['compute','disks','describe',name],CPU_ZONE)
            if disk.get('users') or int(disk['sizeGb'])!=40 or not disk['type'].endswith('/pd-balanced'):raise ValueError('New empty disk resource differs')
            ident['scratch']=dict(name=name,id=disk['id'],created=disk['creationTimestamp'],size_GiB=40,zone=CPU_ZONE)
            save(out/'scratch-created.json',disk);save(out/'identity-with-scratch.json',ident)
            c.call(['compute','instances','attach-disk',CPU,'--disk='+name,'--device-name='+name],CPU_ZONE)
            attached=c.state();matches=[d for d in attached['disks']if d['deviceName']==name]
            if len(matches)!=1 or matches[0]['autoDelete'] or matches[0]['boot'] or not matches[0]['source'].endswith('/'+name):
                raise ValueError('New task disk attachment/lifetime differs')
            save(out/'scratch-attached-provider.json',attached)
            remote(out,'scratch-mount',scratch_mount_code(ident))
        remote(out,'host-and-gates',host_code(ident,f),300)
        save(out/'held-gates-dispatched.json',ident)
    except BaseException:
        c.stop();raise
    return ident


def release(out):
    """Release once after independent provider readback and actual native gates."""
    out=Path(out).absolute();p=out/'identity-with-scratch.json'
    ident=json.loads((p if p.exists()else out/'identity.json').read_text());c=Cloud(out/'release-control');state=c.state();c.put('provider-before-release.json',state)
    if state['status']!='RUNNING' or datetime.datetime.fromisoformat(state['lastStartTimestamp']).timestamp()!=ident['allocation_start_epoch']:raise ValueError('Original boot no longer running')
    if str(state['scheduling']['maxRunDuration']['seconds'])!=str(ident['provider_max_duration_seconds']) or state['scheduling']['instanceTerminationAction']!='STOP' or state['scheduling']['automaticRestart']:raise ValueError('Provider STOP differs')
    remote(out,'release',release_code(ident,state))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--artifact-root',type=Path,required=True)
    a.add_argument('--start',action='store_true');a.add_argument('--release',action='store_true');v=a.parse_args()
    if v.start and not v.release:start(v.artifact_root)
    elif v.release and not v.start:release(v.artifact_root)
    else:a.error('Choose exactly start or release')
