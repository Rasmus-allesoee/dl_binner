#!/usr/bin/env python3
"""Prepared Mac controller for a separately authorized existing-VM E027 phase.

Start is explicitly selected after clean pushed source and fresh external finance
admission. It creates no resources and runs no installer. Native science remains
held until a separate machine-checkable release. Every SSH consumer is rendered
and compiled before the start; disconnect-safe guest services own the workflow.
"""
import argparse
import base64
import datetime
import json
import math
from pathlib import Path
import shlex
import subprocess
import sys
import time

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e021_portable_cloud import Cloud
from e024_coverage import binding
from e027_gates import freeze

BRANCH='common-multiview-marker-binner'
SSH=['ssh','-o','ControlMaster=no','-o','ControlPath=none','-o','ConnectTimeout=12','dl-binner-gcp']


def render_host(ident,financial):
    """Render the exact source-sync, mount/headroom and held-service admission."""
    code=r'''import os,subprocess,json,pathlib,shutil,pwd,time,sys
ident=IDENTITY
financial=FINANCIAL
root=pathlib.Path(ident['root']);repo=pathlib.Path(ident['repo'])
if not os.path.ismount('/srv/dl_binner'):
 subprocess.run(['sudo','-n','mount','-U','f76283ed-60c4-4060-bd22-84c95f38d3fb','/srv/dl_binner'],check=True)
if not os.path.ismount('/srv/dl_binner') or os.cpu_count()!=8:raise ValueError('Existing mount/allocation differs')
u=shutil.disk_usage('/srv/dl_binner')
if u.free<33*1024**3:raise ValueError('25 GiB reserve plus 8 GiB additional allowance unavailable')
def call(a):return subprocess.check_output(a,cwd=repo,text=True).strip()
if call(['git','status','--porcelain']):raise ValueError('Existing checkout dirty; preserve it')
call(['git','fetch','origin','common-multiview-marker-binner'])
if call(['git','rev-parse','FETCH_HEAD'])!=ident['source']:raise ValueError('Pushed commit differs')
call(['git','checkout','--detach',ident['source']])
if call(['git','status','--porcelain']):raise ValueError('Exact source not clean')
if root.exists():raise ValueError('Fresh E027 attempt required')
for name in ['logs','tmp','payload']:(root/name).mkdir(parents=True,exist_ok=False)
import base64,hashlib
wheel=root/'payload/dl_binner-0.1.0.dev9-py3-none-any.whl'
payload=base64.b64decode(WHEEL_PAYLOAD,validate=True)
if dict(bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest())!=ident['wheel_binding']:raise ValueError('Transferred wheel bytes differ')
with wheel.open('xb') as stream:stream.write(payload)
h=dict(initial_filesystem_used_bytes=u.used,filesystem=u._asdict(),boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),user=pwd.getpwuid(os.getuid()).pw_name,logical_cpus=os.cpu_count(),epoch=time.time(),gcloud=shutil.which('gcloud'))
if h['gcloud']!='/snap/bin/gcloud':raise ValueError('Existing CLI path differs; no reinstall')
sys.path.insert(0,str(repo/'scripts'))
from e021_control_json import publish
from e027_gates import freeze
from e024_coverage import binding
from e027_phase import service_content
freeze();publish(h,root/'host.json');publish(financial,root/'payload/financial-gate.json')
(root/'logs/process-inventory.txt').write_text(subprocess.check_output(['ps','-eo','pid,ppid,etime,pcpu,rss,args'],text=True))
p=json.loads((repo/'experiments/E027-common-information-binner/runtime-plan.json').read_text())
p['work']=str(root/'work');p['python']=str(root/'env/bin/python');p['wheel']=str(root/'payload/dl_binner-0.1.0.dev9-py3-none-any.whl');publish(p,root/'science-plan.json')
cfg=dict(root=str(root),work=p['work'],repo=str(repo),plan=str(root/'science-plan.json'),source_commit=ident['source'],limits=p['limits'],vm_start_epoch=ident['vm_start_epoch'],initial_filesystem_used_bytes=u.used,gcloud=h['gcloud'],archive_prefix=ident['archive_prefix'],watchdog_live=str(root/'logs/watchdog-live-before-release.json'),service_name=ident['service_name'])
publish(cfg,root/'config.json');publish(ident,root/'identity.json')
publish(dict(data_copied=False,reuse_lock=binding(p['reuse_lock']),units=p['units'],scope='Immutable accepted inputs in place; no data/runtime recopy'),root/'external-data.json')
service_content(root,'/usr/bin/python3',repo/'scripts/e027_phase.py',root/'config.json',h['user'])
arm=subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B',str(repo/'scripts/e027_arm.py'),'--config',str(root/'config.json')],capture_output=True,text=True)
(root/'logs/arm-terminal.log').write_text(arm.stdout+arm.stderr);print(arm.stdout+arm.stderr,flush=True);arm.check_returncode()
left=int(ident['vm_start_epoch']+2700-time.time())
if left<300:raise TimeoutError('Native setup clock unavailable')
argv=['sudo','-n','systemd-run','--unit='+ident['service_name']+'-gates','--uid='+h['user'],'--working-directory='+str(repo),'--property=Restart=no','--property=MemoryMax=26000000000','--property=CPUAffinity=0 1 2 3','--property=RuntimeMaxSec='+str(left),'--property=KillMode=control-group','--property=TimeoutStopSec=30','--property=StandardOutput=append:'+str(root/'logs/gates-terminal.log'),'--property=StandardError=append:'+str(root/'logs/gates-terminal.log'),'--setenv=OMP_NUM_THREADS=4','--setenv=OPENBLAS_NUM_THREADS=4','--setenv=MKL_NUM_THREADS=4','--setenv=NUMBA_NUM_THREADS=4','--setenv=PYTHONDONTWRITEBYTECODE=1','/usr/bin/python3','-u','-I','-B',str(repo/'scripts/e027_gates.py'),'--config',str(root/'config.json')]
subprocess.run(argv,check=True)
print('E027_HELD_GATES',json.dumps(dict(root=str(root),config=binding(root/'config.json'),plan=binding(root/'science-plan.json'),host=h)),flush=True)
'''
    wheel=Path(financial['wheel_path'])
    if binding(wheel)!=financial['wheel_binding']:raise ValueError('Local wheel changed')
    return code.replace('IDENTITY',repr(ident)).replace('FINANCIAL',repr(financial)).replace('WHEEL_PAYLOAD',repr(base64.b64encode(wheel.read_bytes()).decode()))


def render_release(ident,provider):
    """Render atomic release after actual native gates/forecast/watcher checks."""
    code=r'''import json,pathlib,subprocess,sys,time,shutil
ident=IDENTITY
provider=PROVIDER
root=pathlib.Path(ident['root']);repo=pathlib.Path(ident['repo']);sys.path.insert(0,str(repo/'scripts'))
from e021_control_json import publish
from e024_coverage import binding
from e027_phase import admission,SECONDS,STOP_SECONDS
from e027_gates import freeze
from e009_exit_watchdog import identity
freeze();cfg=json.loads((root/'config.json').read_text());cfg['_path']=str(root/'config.json')
gate=json.loads((root/'gates/completion.json').read_text())
if gate['status']!='PASS' or gate['config']!=binding(root/'config.json'):raise ValueError('Actual native gates absent or differ')
schedule=json.loads((root/'gates/schedule.json').read_text())
if schedule['status']!='PASS' or schedule['planning_remaining_science_seconds']>ident['vm_start_epoch']+SECONDS-time.time()-120:raise TimeoutError('Actual native complete schedule cannot fit original new clock')
started=json.loads((root/'started.json').read_text());process=identity(started['pid'])
if process!=started['identity']:raise ValueError('Held parent identity changed')
state=pathlib.Path('/var/lib')/(ident['service_name']+'-exit')/'status.json'
w=json.loads(state.read_text())
if w['decision']!='workflow alive' or w['expected_process']!=process or w['observed_process']!=process or w['boot_id']!=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Fresh held watcher mismatch')
if subprocess.check_output(['systemctl','is-active',ident['service_name']+'-exit.timer'],text=True).strip()!='active':raise ValueError('Watcher timer inactive')
f=json.loads((root/'payload/financial-gate.json').read_text())
if time.time()-f['checked_epoch']>7200 or f['new_incremental_gross_ceiling_USD']!=15:raise ValueError('Fresh finance expired')
if shutil.disk_usage(root).free<33*1024**3:raise ValueError('Native release headroom unavailable')
proof=root/'logs/provider-before-release.json';publish(provider,proof)
paths=[root/'gates/completion.json',root/'gates/source.json',root/'gates/runtime.json',root/'gates/data.json',root/'gates/schedule.json',root/'gates/tiny-DAG/completed.json',root/'logs/supervision.json',root/'logs/watchdog-native-tests.log',root/'logs/maintenance-restart-refused.json',proof,root/'payload/financial-gate.json',root/'external-data.json']
release=dict(config=binding(root/'config.json'),plan=binding(cfg['plan']),vm_start_epoch=ident['vm_start_epoch'],credit_gate_passed=True,pending_usage_accounted=True,native_gates_passed=True,watchdog_verified=True,provider_STOP_verified=True,existing_VM_only=True,full_axes_verified=True,headroom_measured=True,retention_passed=True,real_money_authorized=False,estimated_incremental_gross_USD=f['estimated_complete_gross_USD'],ceiling_USD=15,provider_STOP_seconds=STOP_SECONDS,storage_retention_extended=False,credit_valid_until_epoch=f['credit_valid_until_epoch'],storage_valid_until_epoch=f['storage_valid_until_epoch'],covered_costs=['compute','disk','storage','network','operations'],gate_files={str(p):binding(p) for p in paths})
admission(cfg,release,time.time());publish(release,root/'release.json')
print('E027_RELEASED',json.dumps(dict(epoch=time.time(),release=binding(root/'release.json'),schedule=schedule,supervision=w)),flush=True)
'''
    return code.replace('IDENTITY',repr(ident)).replace('PROVIDER',repr(provider))


def remote(out,code,seconds=240):
    """Capture and compile the actual SSH consumer before invoking pinned SSH."""
    compile(code,'exact-E027-remote','exec');tag=str(time.time_ns())
    (out/(tag+'-remote.py')).write_text(code)
    value=subprocess.run(SSH+['/usr/bin/python3 -I -B -'],input=code,capture_output=True,text=True,timeout=seconds)
    (out/(tag+'-ssh.log')).write_text(value.stdout+value.stderr)
    print(value.stdout+value.stderr,flush=True);value.check_returncode()
    return value.stdout


def start(out):
    """Start the existing E2 once; any controller failure stops without recovery."""
    out=Path(out).absolute();out.mkdir(parents=True,exist_ok=True)
    if (out/'identity.json').exists():
        raise ValueError('Recorded attempt already exists; assess verified reuse and cumulative ledger, never reset by reissuing start')
    f=json.loads((out/'financial-gate.json').read_text());freeze()
    if (f['real_money_authorized'] is not False
            or not math.isfinite(f['estimated_complete_gross_USD'])
            or not 0 <= f['estimated_complete_gross_USD']<=15
            or f['new_incremental_gross_ceiling_USD']!=15
            or f.get('coverage_status')!='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'
            or f.get('complete_schedule_gate_passed') is not True):
        raise ValueError('Complete credit-only fifteen-dollar gate required')
    if time.time()-f['checked_epoch']>7200 or time.time()+87300>=f['storage_valid_until_epoch']:
        raise ValueError('Finance/retention freshness gate failed')
    for path,wanted in f['local_gate_files'].items():
        if binding(path)!=wanted:raise ValueError('Local gate/source changed')
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise ValueError('Clean source required')
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if subprocess.check_output(['git','ls-remote','origin','refs/heads/'+BRANCH],cwd=ROOT,text=True).split()[0]!=source:
        raise ValueError('Exact source not pushed')
    c=Cloud(out/'control-plane');before=c.state()
    if before['status']!='TERMINATED' or not before['machineType'].endswith('/e2-standard-8') or before.get('guestAccelerators'):
        raise ValueError('Original stopped E2 required')
    if [int(d['diskSizeGb']) for d in before['disks']]!=[30,300] or any(d['autoDelete'] for d in before['disks']):
        raise ValueError('Original persistent disks differ')
    if not before['shieldedInstanceConfig']['enableSecureBoot']:raise ValueError('Secure Boot differs')
    c.put('provider-before.json',before)
    phase='common-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+source[:7]
    ident=dict(root='/srv/dl_binner/experiments/e027/'+phase,repo='/srv/dl_binner/repo',source=source,phase=phase,
        user='rasmus_allesoee_gmail_com',service_name='e027-'+phase,
        archive_prefix='gs://dl-binner-archive-167650584170/e027/'+phase+'/',vm_start_epoch=0,
        wheel_binding=f['wheel_binding'])
    # Both actual consumers compile before changing any provider scheduling.
    for label,code in [('host',render_host(ident,f)),('release',render_release(ident,before))]:
        compile(code,'prestart-'+label,'exec');(out/(label+'-precompiled.py')).write_text(code)
    try:
        c.call(['compute','instances','set-scheduling','dl-binner-cpu','--no-restart-on-failure',
            '--clear-termination-time','--max-run-duration=87300s','--instance-termination-action=STOP'],'us-central1-a')
        policy=c.state()
        if str(policy['scheduling']['maxRunDuration']['seconds'])!='87300' or policy['scheduling'].get('terminationTime'):
            raise ValueError('New provider STOP readback differs')
        if any(policy[k]!=before[k] for k in ['machineType','disks','metadata','serviceAccounts','shieldedInstanceConfig']):
            raise ValueError('Protected resources changed')
        c.put('STOP-readback.json',policy)
        c.call(['compute','instances','start','dl-binner-cpu'],'us-central1-a');live=c.state()
        if live['status']!='RUNNING' or live['lastStartTimestamp']==before['lastStartTimestamp']:raise ValueError('No fresh allocation')
        ident['vm_start_epoch']=datetime.datetime.fromisoformat(live['lastStartTimestamp']).timestamp()
        c.put('provider-start.json',live);(out/'identity.json').write_text(json.dumps(ident,indent=2)+'\n')
        for i in range(12):
            value=subprocess.run(SSH+['true'],capture_output=True,text=True,timeout=20)
            (out/('ssh-ready-'+str(i)+'.log')).write_text(value.stdout+value.stderr)
            if value.returncode==0:break
            time.sleep(2)
        else:raise RuntimeError('Pinned SSH unavailable; no credential replacement')
        remote(out,render_host(ident,f))
        (out/'held-gates-dispatched.json').write_text(json.dumps(ident,indent=2)+'\n')
    except BaseException:
        c.stop();raise
    return ident


def release(out):
    """Release once, only when fresh independent provider/gate evidence passes."""
    out=Path(out).absolute();ident=json.loads((out/'identity.json').read_text());c=Cloud(out/'release-control')
    state=c.state();c.put('provider-before-release.json',state)
    if state['status']!='RUNNING' or datetime.datetime.fromisoformat(state['lastStartTimestamp']).timestamp()!=ident['vm_start_epoch']:
        raise ValueError('Original new boot no longer running')
    if str(state['scheduling']['maxRunDuration']['seconds'])!='87300' or state['scheduling']['instanceTerminationAction']!='STOP' or state['scheduling']['automaticRestart']:
        raise ValueError('Provider STOP/restart policy differs')
    remote(out,render_release(ident,state))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--artifact-root',type=Path,required=True)
    p.add_argument('--start',action='store_true');p.add_argument('--release',action='store_true');a=p.parse_args()
    if a.start and not a.release:start(a.artifact_root)
    elif a.release and not a.start:release(a.artifact_root)
    else:p.error('Choose exactly start or release')
