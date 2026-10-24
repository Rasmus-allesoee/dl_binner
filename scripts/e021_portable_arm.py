#!/usr/bin/env python3
"""Arm the approved portable node with an exact current-boot/process exit watcher.

The queue parent is held before any science. The accepted detector sources and
native normal/crash tests are reused unchanged. Provider STOP is independently
read back by the Mac controller; no cloud mutation occurs in this helper.
"""
import argparse,hashlib,importlib.util,json,os,pwd,shutil,subprocess,time
from pathlib import Path


def service_content(repo,root,user,config,remaining):
    """Return a bounded four-thread/26 GB service for the actual queue parent."""
    if type(remaining)is not int or not 1<=remaining<=172800:raise ValueError('Original common/node remainder required')
    for x in [repo,root,user,config]:
        if any(c in str(x)for c in ['\n','\r',' ','\t']):raise ValueError('Unsafe unit field')
    return ('[Unit]\nRefuseManualStop=yes\nDescription=Bounded portable E021 '+str(user)+' parent\nAfter=network-online.target\n[Service]\nType=simple\nUser='+str(user)+'\nWorkingDirectory='+str(repo)+'\nRestart=no\nEnvironment=PYTHONNOUSERSITE=1\nEnvironment=OMP_NUM_THREADS=4\nEnvironment=OPENBLAS_NUM_THREADS=4\nEnvironment=MKL_NUM_THREADS=4\nEnvironment=NUMBA_NUM_THREADS=4\nCPUAffinity=0 1 2 3\nMemoryMax=26000000000\nExecStart=/usr/bin/python3 -u -I -B '+str(Path(repo)/'scripts/e021_portable_node.py')+' --config '+str(config)+'\nRuntimeMaxSec='+str(remaining)+'\nKillMode=control-group\nTimeoutStopSec=30\nStandardOutput=append:'+str(Path(root)/'logs/systemd-parent.log')+'\nStandardError=append:'+str(Path(root)/'logs/systemd-parent.log')+'\n')


def arm(path):
    """Start held queue, pin its identity, and exercise a live tested shutdown timer."""
    cfg=json.loads(Path(path).read_text());root=Path(cfg['root']);repo=Path(cfg['repo']);host=json.loads((root/'host.json').read_text());unit=cfg['service_name'];watch=unit+'-exit'
    if os.geteuid()!=0 or time.time()>=cfg['node_deadline_epoch']-900 or host['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Root and current-boot remaining clock required')
    if not unit.startswith('e021-')or not all(c.isalnum()or c=='-'for c in unit):raise ValueError('Unsafe service name')
    account=pwd.getpwnam(host['user'])
    def run(argv):return subprocess.run(argv,check=True,text=True,capture_output=True,timeout=60)
    wd=root/'watchdog';wd.mkdir(exist_ok=False);bindings={}
    for n in ['e009_exit_watchdog.py','e011_exit_watchdog.py']:
        p=wd/n;shutil.copyfile(repo/'scripts'/n,p);b=p.read_bytes();bindings[n]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    Path('/run/systemd/system/'+unit+'.service').write_text(service_content(repo,root,host['user'],path,int(cfg['node_deadline_epoch']-time.time())))
    run(['systemctl','daemon-reload']);run(['systemctl','start',unit+'.service'])
    for _ in range(100):
        pid=int(run(['systemctl','show',unit+'.service','--property=MainPID','--value']).stdout)
        if pid and(root/'started.json').exists():break
        time.sleep(.1)
    else:raise RuntimeError('Held queue parent unavailable')
    spec=importlib.util.spec_from_file_location('detector',wd/'e009_exit_watchdog.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);identity=m.identity(pid)
    if identity is None or identity['pid']!=json.loads((root/'started.json').read_text())['pid']:raise ValueError('Actual held process differs')
    cd=Path('/run')/watch;cd.mkdir(exist_ok=False);c=dict(boot_id=host['boot_id'],process=identity,workflow_root=str(root),exit_grace_seconds=60,exit_snapshot_uri=cfg['archive_prefix']+'/watchdog-exit.json');(cd/'current.json').write_text(json.dumps(c,indent=2)+'\n')
    Path('/run/systemd/system/'+watch+'.service').write_text('[Unit]\nDescription=Portable E021 current-process exit shutdown\n[Service]\nType=oneshot\nExecStart=/usr/bin/python3 -I -B '+str(wd/'e011_exit_watchdog.py')+' --base '+str(wd/'e009_exit_watchdog.py')+' --config '+str(cd/'current.json')+' --state /var/lib/'+watch+' --evidence '+str(root/'logs')+'\nTimeoutStartSec=60\n')
    Path('/run/systemd/system/'+watch+'.timer').write_text('[Timer]\nOnActiveSec=1\nOnUnitActiveSec=30\nAccuracySec=1\nUnit='+watch+'.service\n[Install]\nWantedBy=timers.target\n')
    run(['systemctl','daemon-reload']);run(['systemctl','start',watch+'.timer']);run(['systemctl','start',watch+'.service'])
    status=json.loads((Path('/var/lib')/watch/'status.json').read_text())
    if status['decision']!='workflow alive'or status['expected_process']!=identity or status['observed_process']!=identity or status['boot_id']!=host['boot_id']:raise ValueError('Watcher live identity failed')
    restart=subprocess.run(['systemctl','try-restart',unit+'.service'],capture_output=True,text=True,timeout=15)
    actual=int(run(['systemctl','show',unit+'.service','--property=MainPID','--value']).stdout)
    if not restart.returncode or 'refus'not in(restart.stdout+restart.stderr).lower()or actual!=pid:raise ValueError('Held parent restart protection failed')
    (root/'logs/maintenance-restart-refused.json').write_text(json.dumps(dict(status='PASS',pid_before=pid,pid_after=actual,exit=restart.returncode,stderr=restart.stderr),indent=2)+'\n')
    for n,v in [('watchdog-live-before-release.json',status),('supervision.json',dict(status='ARMED_AND_TESTED',parent_unit=unit+'.service',watchdog_timer=watch+'.timer',process=identity,boot_id=host['boot_id'],source=cfg['source'],config_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),detector_bindings=bindings,node_deadline_epoch=cfg['node_deadline_epoch'],provider_deadline_epoch=cfg['provider_deadline_epoch'],native_normal_exit_and_crash_tests_passed=True))]:
        p=root/'logs'/n;p.write_text(json.dumps(v,indent=2)+'\n');os.chown(p,account.pw_uid,account.pw_gid)
    with(root/'logs/watchdog-native-tests.log').open('x')as f:
        p=subprocess.run(['/usr/bin/python3','-I','-B','-m','unittest','discover','-s',str(repo/'tests'),'-p','test_e009_exit_watchdog.py','-v'],stdout=f,stderr=subprocess.STDOUT,cwd=repo)
    if p.returncode:raise RuntimeError('Native normal-exit/crash tests failed')
    for name in [unit+'.service',watch+'.timer']:
        if run(['systemctl','is-active',name]).stdout.strip()!='active':raise ValueError('Parent/watcher inactive')
    print('E021_PORTABLE_SUPERVISION_ARMED',json.dumps(status),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);a=p.parse_args();arm(a.config)
