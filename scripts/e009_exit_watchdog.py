#!/usr/bin/env python3
"""Stop the current E009 VM after its explicitly pinned workflow process exits.

Run as a root systemd oneshot every 30 seconds. This observes /proc only while
the workflow lives: no experiment modification, retries, extra analysis or cloud
credentials. A boot ID, PID birth tick and command hash distinguish this run from
a reused PID or later VM boot. After 60 seconds of confirmed absence, retain a
small persistent exit snapshot, sync files and request a clean guest shutdown.
The existing provider STOP remains the independent absolute backstop.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def identity(pid, proc=Path('/proc')):
    """Read a Linux process identity; exited/zombie processes are not live work."""
    try:
        folder=Path(proc)/str(pid)
        # comm can contain spaces or parentheses; fields after its final ')' are fixed.
        fields=(folder/'stat').read_text().rsplit(')',1)[1].split()
        if fields[0] in ('Z','X','x'):return None
        command=(folder/'cmdline').read_bytes()
        if not command:return None
        return {'pid':pid,'start_ticks':int(fields[19]),
                'command_sha256':hashlib.sha256(command).hexdigest()}
    except (FileNotFoundError,ProcessLookupError):return None


def decide(config, state, observed, boot, now):
    """Return one deterministic decision without performing any shutdown or I/O."""
    if boot!=config['boot_id']:
        return {'decision':'different boot; disarmed','shutdown':False}
    if observed==config['process']:
        return {'decision':'workflow alive','shutdown':False}
    first=state.get('first_missing_monotonic',now)
    elapsed=max(0,now-first)
    return {'decision':'workflow exited' if elapsed>=config['exit_grace_seconds'] else 'exit grace',
            'shutdown':elapsed>=config['exit_grace_seconds'],
            'first_missing_monotonic':first,'missing_seconds':elapsed}


def write_atomic(path, value):
    """Replace a small watcher record atomically and flush it before returning."""
    path=Path(path);temporary=path.with_suffix(path.suffix+'.tmp')
    with temporary.open('w')as stream:
        json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
        stream.flush();os.fsync(stream.fileno())
    temporary.replace(path)


def snapshot(root):
    """Read only small journals and log tails; never scan/hash bulk scientific DNA."""
    root=Path(root);value={'attempts':{},'stages':{},'log_tails':{}}
    for path in sorted(root.glob('attempt-*.json')):
        try:value['attempts'][path.name]=json.loads(path.read_text())
        except (OSError,ValueError)as exc:value['attempts'][path.name]={'read_error':str(exc)}
    for folder in sorted((root/'parts').glob('*')):
        done=folder/'done.json'
        value['stages'][folder.name]={'sealed':done.is_file()}
        if done.is_file():
            data=done.read_bytes()
            value['stages'][folder.name]['manifest']={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    for pattern in ('terminal-*.log','dag-*.log','disk-*.jsonl','*.log'):
        paths=sorted((root/'logs').glob(pattern))
        for path in paths[-2:]:
            with path.open('rb')as stream:
                stream.seek(max(0,path.stat().st_size-8000))
                value['log_tails'][path.name]=stream.read().decode(errors='replace')
    return value


def clean_shutdown():
    """Request documented clean GCE guest shutdown, without deletion or an API role."""
    os.sync()
    subprocess.run(['/usr/sbin/shutdown','-h','now'],check=True,timeout=15)


def tick(config, state_dir, evidence, *, proc=Path('/proc'), now=None,
         boot=None, shutdown=clean_shutdown):
    """Check one pinned run and persist status; inject only OS boundaries in tests.

    Evidence collection is best effort: unavailable logs must not leave an exited
    VM billing indefinitely. A shutdown command failure propagates to systemd;
    its timer retries the stop, while retaining the first exit observation.
    """
    state_dir=Path(state_dir);evidence=Path(evidence)
    state_dir.mkdir(parents=True,exist_ok=True)
    path=state_dir/'status.json'
    previous=json.loads(path.read_text())if path.exists()else {}
    boot=boot if boot is not None else (Path(proc)/'sys/kernel/random/boot_id').read_text().strip()
    observed=identity(config['process']['pid'],proc)
    decision=decide(config,previous,observed,boot,time.monotonic()if now is None else now)
    status={**decision,'checked_utc':datetime.now(timezone.utc).isoformat(),
            'expected_process':config['process'],'observed_process':observed,
            'boot_id':boot,'workflow_root':config['workflow_root']}
    write_atomic(path,status)
    if decision['shutdown']:
        try:details=snapshot(config['workflow_root'])
        except Exception as exc:details={'snapshot_error':repr(exc)}
        record={**status,'snapshot':details,'action':'clean guest shutdown requested; no retry or deletion'}
        write_atomic(state_dir/'exit-snapshot.json',record)
        try:
            evidence.mkdir(parents=True,exist_ok=True)
            write_atomic(evidence/'exit-snapshot.json',record)
        except OSError as exc:print('Evidence mirror unavailable: '+str(exc),flush=True)
        print(json.dumps(status,sort_keys=True),flush=True)
        shutdown()
    else:print(json.dumps(status,sort_keys=True),flush=True)
    return status


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=Path('/etc/e009-exit-watchdog/current.json'))
    parser.add_argument('--state',type=Path,default=Path('/var/lib/e009-exit-watchdog'))
    parser.add_argument('--evidence',type=Path,required=True)
    args=parser.parse_args()
    tick(json.loads(args.config.read_text()),args.state,args.evidence)
