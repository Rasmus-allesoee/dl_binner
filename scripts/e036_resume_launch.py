#!/usr/bin/env python3
"""One verified-reuse E036 restart on the existing VM/disk and original deadline."""
import argparse,datetime,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e021_portable_cloud import Cloud,CPU,CPU_ZONE
from e031_launch import save
from e033_launch import remote,SSH
from e036_launch import source_sync
from e024_coverage import binding
from e036_phase import validate_config


def host(i,c):
    """Mount only the existing identified E036 disk, without formatting/copy/install."""
    code='''import json,os,pathlib,shutil,subprocess,sys,time
ident=IDENT;cfg=CFG;repo=pathlib.Path(ident['repo']);root=pathlib.Path(cfg['root']);task=pathlib.Path(cfg['task_filesystem'])
if not os.path.ismount('/srv/dl_binner')or os.cpu_count()!=8:raise ValueError('Original E2/source mount required')
name=cfg['financial']['recovery']['task_disk_name'];dev=pathlib.Path('/dev/disk/by-id/google-'+name)
if not name.startswith('e036-task-')or not dev.exists():raise ValueError('Exact original task disk missing')
if not os.path.ismount(task):subprocess.run(['sudo','-n','mount','-o','nodev,nosuid',str(dev),str(task)],check=True)
actual=pathlib.Path(subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(task)],text=True).strip())
if actual.resolve()!=dev.resolve():raise ValueError('Retained task mount differs')
for n in [cfg['python'],cfg['wheel'],cfg['pysam_wheel'],cfg['plan']]:
 if not pathlib.Path(n).is_file():raise ValueError('Retained consumer missing; no install/recopy fallback: '+n)
sys.path.insert(0,str(repo/'scripts'));from e021_control_json import publish
from e036_resume import prepare_layout
prepare_layout(cfg)
from e036_phase import validate_config
from e036_repair import admit
admit();cfg['initial_filesystem_device']=os.stat(task).st_dev;validate_config(cfg)
usage=shutil.disk_usage(task);source=shutil.disk_usage('/srv/dl_binner')
if min(usage.free,source.free)<25*1024**3:raise ValueError('Original source/task reserve violated')
publish(cfg,root/'config.json');publish(dict(user=ident['user'],boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),filesystem=usage._asdict(),source_filesystem=source._asdict(),old_baseline_retained=cfg['initial_filesystem_used_bytes'],device=cfg['initial_filesystem_device'],no_format=True,epoch=time.time()),root/'host.json')
p=subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B',str(repo/'scripts/e036_resume_arm.py'),'--config',str(root/'config.json')],capture_output=True,text=True,timeout=180)
(root/'logs/arming.log').write_text(p.stdout+p.stderr);print(p.stdout+p.stderr,flush=True);p.check_returncode()
print('E036_REUSE_HELD',str(root),flush=True)
'''.replace('IDENT',repr(i)).replace('CFG',repr(c));compile(code,'E036 reuse host','exec');return code


def release(i,c,provider):
    """Verify current-boot watcher and remaining provider duration before atomic release."""
    code='''import json,pathlib,subprocess,sys,time,datetime
cfg=CFG;provider=PROVIDER;root=pathlib.Path(cfg['root']);sys.path.insert(0,str(pathlib.Path(cfg['repo'])/'scripts'))
from e009_exit_watchdog import identity
from e021_control_json import publish
from e024_coverage import binding
s=json.loads((root/'started.json').read_text());w=json.loads((pathlib.Path('/var/lib')/(cfg['service_name']+'-exit')/'status.json').read_text())
if w['decision']!='workflow alive'or w['expected_process']!=identity(s['pid'])or w['observed_process']!=w['expected_process']or w['boot_id']!=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Fresh recovery process/boot watcher differs')
if subprocess.check_output(['systemctl','is-active',cfg['service_name']+'-exit.timer'],text=True).strip()!='active':raise ValueError('Fresh recovery watcher timer inactive')
r=cfg['financial']['recovery']
if provider['status']!='RUNNING'or provider['scheduling']['instanceTerminationAction']!='STOP'or datetime.datetime.fromisoformat(provider['lastStartTimestamp']).timestamp()!=r['current_vm_start_epoch']or int(provider['scheduling']['maxRunDuration']['seconds'])!=r['provider_seconds']:raise ValueError('Recovery provider original-clock fallback differs')
publish(provider,root/'logs/provider-before-release.json');subprocess.run(['sudo','-n','systemctl','stop',SETUP+'.timer'],check=True)
publish(dict(config=binding(root/'config.json'),plan=binding(cfg['plan']),watchdog_verified=True,provider_STOP_verified=True,epoch=time.time()),root/'release.json');print('E036_REUSE_RELEASED',str(root),flush=True)
'''.replace('CFG',repr(c)).replace('PROVIDER',repr(provider)).replace('SETUP',repr(i['setup_timer']));compile(code,'E036 reuse release','exec');return code


def start(output):
    """Restart only after local repair tests; stop on an operational start failure."""
    out=Path(output).absolute();f=json.loads((out/'financial-gate.json').read_text());old=json.loads((out/'original-config.json').read_text());source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()or f['source_transport']['source']!=source:raise ValueError('Exact clean repaired source required')
    name='recover-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+source[:7]
    i=dict(source=source,repo=old['repo'],phase=name,root='/srv/dl_binner/experiments/e036/'+name,user=old['user'],service_name='e036-'+name,setup_timer='e036-recovery-setup-'+str(int(time.time())))
    c=dict(old,root=i['root'],source_commit=source,operations_source=source,service_name=i['service_name'],archive_prefix='gs://dl-binner-archive-167650584170/e036/'+name+'/',financial=f,setup_deadline_epoch=min(time.time()+3600,old['review_deadline_epoch']))
    validate_config(c);host(i,c);release(i,c,{})
    cloud=Cloud(out/'control');before=cloud.state()
    if before['status']!='TERMINATED'or not before['machineType'].endswith('/e2-standard-8')or sorted(int(d['diskSizeGb'])for d in before['disks'])!=[30,64,300]:raise ValueError('Stopped original E2/disks plus existing E036 scratch required')
    disk=cloud.call(['compute','disks','describe',f['recovery']['task_disk_name']],CPU_ZONE)
    if disk['id']!=f['recovery']['task_disk_id']or int(disk['sizeGb'])!=64 or not disk['type'].endswith('/pd-balanced'):raise ValueError('Retained E036 task disk identity differs')
    try:
        seconds=int(old['provider_deadline_epoch']-time.time()-120)
        if seconds<1800:raise TimeoutError('Insufficient original E036 clock for repair')
        cloud.call(['compute','instances','set-scheduling',CPU,'--no-restart-on-failure','--max-run-duration='+str(seconds)+'s','--instance-termination-action=STOP'],CPU_ZONE)
        cloud.call(['compute','instances','start',CPU],CPU_ZONE);live=cloud.state();cloud.put('provider-start.json',live);start_epoch=datetime.datetime.fromisoformat(live['lastStartTimestamp']).timestamp()
        c['financial']['recovery'].update(current_vm_start_epoch=start_epoch,provider_seconds=seconds);c['provider_deadline_epoch']=start_epoch+seconds;validate_config(c);save(out/'identity.json',i);save(out/'prospective-config.json',c)
        for n in range(10):
            q=subprocess.run(SSH+['true'],capture_output=True,text=True,timeout=45);(out/('ssh-'+str(n)+'.log')).write_text(q.stdout+q.stderr)
            if not q.returncode:break
            time.sleep(2)
        else:raise RuntimeError('Pinned SSH unavailable')
        remote(out,'setup-shutdown',"import subprocess\nsubprocess.run(['sudo','-n','systemd-run','--unit',"+repr(i['setup_timer'])+",'--on-active=30m','/usr/sbin/shutdown','-h','now'],check=True)\n",60)
        remote(out,'exact-repaired-source',source_sync(i,f['source_transport']),120)
        remote(out,'verified-reuse-held-host',host(i,c),240);provider=cloud.state();cloud.put('provider-before-release.json',provider);remote(out,'release',release(i,c,provider),90);save(out/'released.json',dict(epoch=time.time()))
    except BaseException as e:save(out/('failure-'+str(time.time_ns())+'.json'),dict(error=repr(e)));cloud.stop();raise
    return i

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);a=p.parse_args();print(json.dumps(start(a.root)),flush=True)
