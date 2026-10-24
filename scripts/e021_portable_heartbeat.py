#!/usr/bin/env python3
"""Relay small peer-space snapshots through Mac-owned pinned IAP SSH sessions.

No DNA/cache payload or credentials are retained/copied by this helper. A failed
relay ceases updates: the native stale-live-peer guard and independent watchdog
stop work. It does not start VMs, retry science or extend any admitted clock.
"""
import argparse,json,subprocess,time
from pathlib import Path


def remote(node,code,value=None):
    """Use explicit pinned SSH argv; stdin carries JSON rather than shell interpolation."""
    p=subprocess.run(node['ssh']+['/usr/bin/python3 -I -B -c '+__import__('shlex').quote(code)],input=None if value is None else json.dumps(value),text=True,capture_output=True,timeout=50)
    if p.returncode:raise RuntimeError(p.stderr[-3000:])
    return p.stdout


def run(path):
    """Maintain current aggregate accounting until the fixed common deadline."""
    path=Path(path);last={};root=path.parent
    while True:
        cfg=json.loads(path.read_text())
        if time.time()>=cfg['deadline_epoch']:break
        nodes=cfg['nodes'];active={k:n for k,n in nodes.items()if n['active']}
        if not active:break
        for key,node in active.items():
            code="import json,sys;from pathlib import Path;sys.path.insert(0,"+repr(node['repo']+'/scripts')+");from e021_portable_node import usage;c=json.loads(Path("+repr(node['root']+'/config.json')+").read_text());print(json.dumps(usage(c)))"
            v=json.loads(remote(node,code));v['live']=True
            if abs(time.time()-v['epoch'])>60 or v['growth_bytes']<0:raise ValueError('Fresh actual usage required')
            last[key]=v
        for key,node in active.items():
            other=next(k for k in nodes if k!=key);peer=dict(last.get(other,dict(growth_bytes=0,epoch=time.time())))
            peer['live']=nodes[other]['active']
            if peer['live']and other not in last:raise ValueError('Live peer lacks measured usage')
            code="import json,sys;from pathlib import Path;p=Path("+repr(node['root']+'/peer-usage.json')+");v=json.load(sys.stdin);q=p.with_name('peer-usage.pending');q.write_text(json.dumps(v)+'\\n');q.replace(p)"
            remote(node,code,peer)
        if sum(x['growth_bytes']for x in last.values())>32*1024**3:raise MemoryError('Aggregate 32 GiB extra work exceeded')
        snap=dict(epoch=time.time(),nodes=last,active=list(active));(root/'peer-snapshot.json').write_text(json.dumps(snap,indent=2)+'\n')
        with(root/'peer-heartbeats.jsonl').open('a')as f:f.write(json.dumps(snap)+'\n')
        time.sleep(20)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);a=p.parse_args();run(a.config)
