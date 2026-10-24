#!/usr/bin/env python3
"""Inspect original E021 disks under a tested current-boot exit shutdown watcher.

No data acquisition, package installation, science, cleanup or cloud mutation.
A fresh persistent directory owns logs and host/space receipts. The held process
ends after inventory or its short deadline; the copied accepted detector requests
shutdown independently of SSH. Provider STOP must already be set by the controller.
"""
import argparse,datetime,getpass,hashlib,importlib.util,json,os,pwd,shutil,subprocess,sys,time
from pathlib import Path


def write(path,value):
    """Exclusively retain finite JSON; no receipt is overwritten on retry."""
    with Path(path).open('x')as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def unit_text(source,root,user,remaining):
    """Return the actual short held-parent systemd unit without starting it."""
    if not 1<=remaining<=1500:raise ValueError('Short original inventory deadline required')
    if any('\n'in str(x)or'\r'in str(x)for x in [source,root,user]):raise ValueError('Invalid unit field')
    return ('[Unit]\nDescription=Bounded E021 original-space inventory\n[Service]\nType=simple\nUser='+user+'\n'
            'ExecStart=/usr/bin/python3 -u -I -B '+str(source)+' hold --root '+str(root)+'\n'
            'CPUAffinity=0 1 2 3\nMemoryMax=8000000000\nRuntimeMaxSec='+str(remaining)+'\nKillMode=control-group\n'
            'StandardOutput=append:'+str(root/'logs/held.log')+'\nStandardError=append:'+str(root/'logs/held.log')+'\n')


def arm(root):
    """Pin a real parent PID/start/command to the boot and test live/exit/crash paths."""
    if os.geteuid()!=0:raise ValueError('Root required only for transient units/watcher')
    host=json.loads((root/'host.json').read_text());unit=host['unit'];watch=unit+'-exit';source=Path(__file__).absolute()
    def run(argv):return subprocess.run(list(map(str,argv)),check=True,text=True,capture_output=True)
    remaining=int(host['inventory_deadline']-time.time());Path('/run/systemd/system/'+unit+'.service').write_text(unit_text(source,root,host['user'],remaining))
    run(['systemctl','daemon-reload']);run(['systemctl','start',unit+'.service'])
    for _ in range(100):
        pid=int(run(['systemctl','show',unit+'.service','--property=MainPID','--value']).stdout)
        if pid and(root/'started.json').exists():break
        time.sleep(.1)
    else:raise RuntimeError('Inventory holder failed')
    spec=importlib.util.spec_from_file_location('detector',source.parent/'e009_exit_watchdog.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
    identity=base.identity(pid)
    if identity is None:raise ValueError('Holder identity missing')
    d=Path('/run')/watch;d.mkdir(exist_ok=False)
    cfg=dict(boot_id=host['boot_id'],process=identity,workflow_root=str(root),exit_grace_seconds=60,exit_snapshot_uri=host['archive_prefix']+'/inventory-watchdog-exit.json');write(d/'current.json',cfg)
    Path('/run/systemd/system/'+watch+'.service').write_text('[Unit]\nDescription=E021 inventory exit stop\n[Service]\nType=oneshot\nExecStart=/usr/bin/python3 -I -B '+str(source.parent/'e011_exit_watchdog.py')+' --base '+str(source.parent/'e009_exit_watchdog.py')+' --config '+str(d/'current.json')+' --state /var/lib/'+watch+' --evidence '+str(root/'logs')+'\nTimeoutStartSec=60\n')
    Path('/run/systemd/system/'+watch+'.timer').write_text('[Timer]\nOnActiveSec=1\nOnUnitActiveSec=30\nAccuracySec=1\nUnit='+watch+'.service\n')
    run(['systemctl','daemon-reload']);run(['systemctl','start',watch+'.timer']);run(['systemctl','start',watch+'.service'])
    status=json.loads((Path('/var/lib')/watch/'status.json').read_text())
    if status['decision']!='workflow alive'or status['observed_process']!=identity or status['expected_process']!=identity or status['boot_id']!=host['boot_id']:raise ValueError('Actual watcher identity differs')
    with(root/'logs/watchdog-tests.log').open('x')as f:
        p=subprocess.run(['/usr/bin/python3','-I','-B','-m','unittest','discover','-s',str(source.parent.parent/'tests'),'-p','test_e009_exit_watchdog.py','-v'],stdout=f,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError('Actual native exit/crash tests failed')
    proof=dict(status='ARMED_AND_TESTED',process=identity,boot_id=host['boot_id'],parent_unit=unit+'.service',watchdog_timer=watch+'.timer',live=status,normal_exit_crash_tests=True)
    write(root/'supervision.json',proof);os.chown(root/'supervision.json',host['uid'],host['gid'])
    print('INVENTORY_WATCHER_READY',json.dumps(proof),flush=True)


def inspect(root,clock):
    """Read original mount/df/du and Git state; stop safely after a bound receipt."""
    c=json.loads(Path(clock).read_text());root.mkdir(parents=True,exist_ok=False);(root/'logs').mkdir()
    start=c['first_VM_start_epoch'];deadline=min(start+1500,c['deadline_epoch'])
    work=shutil.disk_usage('/srv/dl_binner');boot=shutil.disk_usage('/')
    host=dict(user=getpass.getuser(),uid=os.getuid(),gid=os.getgid(),boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),unit='e021-inventory-'+str(int(start)),inventory_deadline=deadline,archive_prefix=c['archive_prefix'],source_script=str(Path(__file__).absolute()),first_VM_start_epoch=start,work_used_bytes=work.used,work_free_bytes=work.free,boot_used_bytes=boot.used,boot_free_bytes=boot.free)
    write(root/'host.json',host)
    def run(argv):
        p=subprocess.run(list(map(str,argv)),text=True,capture_output=True,timeout=max(1,min(180,int(deadline-time.time()))))
        with(root/'logs/inventory.log').open('a')as f:f.write(json.dumps(list(map(str,argv)))+'\n'+p.stdout+p.stderr)
        print(p.stdout+p.stderr,flush=True);p.check_returncode();return p.stdout
    run(['sudo','-n','/usr/bin/python3','-I','-B',Path(__file__).absolute(),'arm','--root',root])
    try:
        if sys.platform!='linux'or os.cpu_count()!=8 or not os.path.ismount('/srv/dl_binner'):raise ValueError('Original Linux eight-CPU mounted node required')
        mount=json.loads(run(['findmnt','-J','-T','/srv/dl_binner','-o','TARGET,SOURCE,FSTYPE,UUID,SIZE,OPTIONS']))
        if mount['filesystems'][0]['uuid']!='f76283ed-60c4-4060-bd22-84c95f38d3fb':raise ValueError('Original filesystem UUID differs')
        run(['df','-B1','/','/srv/dl_binner']);run(['du','-x','-k','--max-depth=2','/srv/dl_binner/experiments'])
        head=run(['git','-C','/srv/dl_binner/repo','rev-parse','HEAD']).strip();dirty=run(['git','-C','/srv/dl_binner/repo','status','--porcelain']).strip()
        if dirty:raise ValueError('Original Git checkout dirty; no reset allowed')
        if work.free<57*1024**3:raise ValueError('Actual headroom below 32 GiB extra plus 25 GiB reserve; cleanup review needed')
        result=dict(status='PASS',checked_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),host=host,mount=mount,primary_checkout=head,primary_unchanged=True,original_work_headroom_passed=True,cleanup=[],storage_increase_for_original_node=False,temporary_worker_disks='Necessary only for approved cross-zone/G2 compatibility; no original resize.',science=False)
        write(root/'inventory.json',result);write(root/'inventory-complete.json',dict(status='SUCCESS',epoch=time.time()));print('E021_INVENTORY_PASS',json.dumps(result),flush=True)
    except BaseException as exc:
        write(root/'inventory-complete.json',dict(status='FAILED',error=repr(exc),epoch=time.time()));raise


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['inspect','arm','hold']);p.add_argument('--root',type=Path,required=True);p.add_argument('--clock',type=Path);a=p.parse_args();root=a.root
    if a.action=='inspect':inspect(root,a.clock)
    elif a.action=='arm':arm(root)
    else:
        host=json.loads((root/'host.json').read_text());write(root/'started.json',dict(pid=os.getpid(),epoch=time.time()))
        while time.time()<host['inventory_deadline']and not(root/'inventory-complete.json').exists():time.sleep(.2)
        print('INVENTORY_HOLDER_EXIT',flush=True)

if __name__=='__main__':main()
