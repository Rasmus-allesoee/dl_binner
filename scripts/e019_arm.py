#!/usr/bin/env python3
"""Arm a fresh current-boot E019 held-parent exit watcher on the existing VM.

Requires root only to own transient systemd units and request eventual shutdown.
Copies accepted detector source byte-for-byte, pins boot/PID/start/command, tests
actual normal/crash observations with an injected stop callback, and retains a
live identity receipt before any science release. It cannot change VM resources.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import time


def arm(path):
    """Start the held parent, pin its identity and test the fresh watcher timer."""
    path=Path(path);cfg=json.loads(path.read_text());root=Path(cfg['root']);repo=Path(cfg['repo']);host=json.loads((root/'host.json').read_text())
    if os.geteuid()!=0 or time.time()>=cfg['vm_start_epoch']+1800:raise ValueError('Root/current setup clock required')
    if host['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Host boot identity differs')
    unit=cfg['service_name'];watch=unit+'-exit';user=host['user'];account=pwd.getpwnam(user)
    def run(argv):return subprocess.run(argv,check=True,text=True,capture_output=True)
    wd=root/'watchdog';wd.mkdir(exist_ok=False);bindings={}
    for name in ['e009_exit_watchdog.py','e011_exit_watchdog.py']:
        target=wd/name;shutil.copyfile(repo/'scripts'/name,target);b=target.read_bytes();bindings[name]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    remaining=int(cfg['vm_start_epoch']+28800-time.time())
    service='[Unit]\nDescription=Frozen E019 held control parent\nAfter=network-online.target\n[Service]\nType=simple\nUser='+user+'\nWorkingDirectory='+str(repo)+'\nEnvironment=PYTHONNOUSERSITE=1\nEnvironment=OMP_NUM_THREADS=4\nEnvironment=OPENBLAS_NUM_THREADS=4\nEnvironment=MKL_NUM_THREADS=4\nEnvironment=NUMBA_NUM_THREADS=4\nExecStart=/usr/bin/python3 -u -I -B '+str(repo/'scripts/e019_phase.py')+' --config '+str(path)+'\nRuntimeMaxSec='+str(remaining)+'\nKillMode=control-group\nTimeoutStopSec=30\nStandardOutput=append:'+str(root/'logs/systemd-parent.log')+'\nStandardError=append:'+str(root/'logs/systemd-parent.log')+'\n'
    Path('/run/systemd/system/'+unit+'.service').write_text(service)
    run(['systemctl','daemon-reload']);run(['systemctl','start',unit+'.service'])
    for _ in range(100):
        pid=int(run(['systemctl','show',unit+'.service','--property=MainPID','--value']).stdout)
        if pid and (root/'started.json').exists():break
        time.sleep(.1)
    else:raise RuntimeError('Held parent failed to start')
    spec=importlib.util.spec_from_file_location('detector',wd/'e009_exit_watchdog.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
    identity=base.identity(pid)
    if identity is None or identity['pid']!=json.loads((root/'started.json').read_text())['pid']:raise ValueError('Held process identity unavailable')
    configdir=Path('/run')/watch;configdir.mkdir(exist_ok=False)
    config=dict(boot_id=host['boot_id'],process=identity,workflow_root=str(root),exit_grace_seconds=60,exit_snapshot_uri=cfg['archive_prefix']+'/watchdog-exit.json')
    (configdir/'current.json').write_text(json.dumps(config,indent=2)+'\n')
    watcher='[Unit]\nDescription=Current-boot process-bound E019 exit shutdown\n[Service]\nType=oneshot\nExecStart=/usr/bin/python3 -I -B '+str(wd/'e011_exit_watchdog.py')+' --base '+str(wd/'e009_exit_watchdog.py')+' --config '+str(configdir/'current.json')+' --state /var/lib/'+watch+' --evidence '+str(root/'logs')+'\nTimeoutStartSec=60\n'
    timer='[Unit]\nDescription=Check held E019 parent every 30 seconds\n[Timer]\nOnActiveSec=1\nOnUnitActiveSec=30\nAccuracySec=1\nUnit='+watch+'.service\n[Install]\nWantedBy=timers.target\n'
    Path('/run/systemd/system/'+watch+'.service').write_text(watcher);Path('/run/systemd/system/'+watch+'.timer').write_text(timer)
    run(['systemctl','daemon-reload']);run(['systemctl','start',watch+'.timer']);run(['systemctl','start',watch+'.service'])
    status=json.loads((Path('/var/lib')/watch/'status.json').read_text())
    if status['decision']!='workflow alive' or status['expected_process']!=identity or status['observed_process']!=identity or status['boot_id']!=host['boot_id']:raise ValueError('Watcher live identity differs')
    proof=root/'logs/watchdog-live-before-release.json';proof.write_text(json.dumps(status,indent=2)+'\n');os.chown(proof,account.pw_uid,account.pw_gid)
    if run(['systemctl','is-active',unit+'.service']).stdout.strip()!='active' or run(['systemctl','is-active',watch+'.timer']).stdout.strip()!='active':raise ValueError('Parent/watcher timer not active')
    with (root/'logs/watchdog-native-tests.log').open('x') as f:
        result=subprocess.run(['/usr/bin/python3','-I','-B','-m','unittest','discover','-s',str(repo/'tests'),'-p','test_e009_exit_watchdog.py','-v'],cwd=repo,stdout=f,stderr=subprocess.STDOUT)
    if result.returncode:raise RuntimeError('Native exit/crash tests failed')
    receipt=dict(status='ARMED_AND_TESTED',parent_unit=unit+'.service',watchdog_timer=watch+'.timer',watchdog_service=watch+'.service',process=identity,boot_id=host['boot_id'],source_commit=cfg['source_commit'],detector_bindings=bindings,exit_grace_seconds=60,timer_seconds=30,original_vm_start_epoch=cfg['vm_start_epoch'],hard_deadline_epoch=cfg['vm_start_epoch']+28800,provider_stop_epoch=cfg['vm_start_epoch']+29700,native_normal_exit_and_crash_tests_passed=True)
    target=root/'logs/supervision.json';target.write_text(json.dumps(receipt,indent=2)+'\n');os.chown(target,account.pw_uid,account.pw_gid)
    print('E019_SUPERVISION_READY',json.dumps(receipt),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);a=p.parse_args();arm(a.config)
