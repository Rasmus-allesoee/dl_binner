#!/usr/bin/env python3
"""Bound a synthetic hierarchy/membership scale check without community science."""
import argparse
import json
from pathlib import Path
import time


def run(output,n=32768):
    """Exercise real additive profiles and shared occupancy on two balanced forests."""
    import numpy as np
    from dl_binner.selection import grouping as s
    begin=time.monotonic();rng=np.random.default_rng(11)
    ids=np.array([f'opaque-{i:08}' for i in range(n)])
    tnf=rng.random((n,136),dtype=np.float32);tnf/=tnf.sum(1)[:,None]
    depth=rng.random((n,10),dtype=np.float32);depth[::3]=0
    lengths=np.full(n,2500,np.int64);children=np.full((2*n-1,2),-1,np.int64)
    mass=np.empty(2*n-1,np.int64);mass[:n]=lengths;current=list(range(n));at=n
    while len(current)>1:
        next_rows=[]
        for a,b in zip(current[::2],current[1::2]):
            children[at]=[a,b];mass[at]=mass[a]+mass[b];next_rows.append(at);at+=1
        if len(current)%2:next_rows.append(current[-1])
        current=next_rows
    tree=dict(children=children,mass=mass,roots=np.array(current),core=np.ones(n))
    alternatives=[dict(node=i) for i in range(n,2*n-1)]
    nn=(np.arange(n)[:,None]+np.arange(1,31)[None,:])%n
    data=dict(ids=ids,lengths=lengths,tnf=tnf,depth=depth)
    evidence=dict(panel_size=40,calls={str(ids[i]):{'family-'+str(i%40):[.9]} for i in range(0,n,7)})
    a=dict(selected=np.arange(n),neighbors=nn);valid=np.ones(n,bool)
    pool,views,context,calibration=s.candidate_pool(data,valid,a,
        [('a',tree,alternatives,np.arange(n)),('b',tree,alternatives,np.arange(n))],[],evidence,s.policy())
    selected,choices=s.select(pool,views,context,s.policy())
    if len(selected)!=n or sum(len(v.order) for v in views)!=2*n or len(choices)!=len(pool):
        raise ValueError('Synthetic complete membership contract differs')
    elapsed=time.monotonic()-begin
    if elapsed>180:raise ValueError('Synthetic scale clock refused')
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(dict(status='PASS',rows=n,candidates=len(pool),
        wall_seconds=elapsed,shared_membership_entries=2*n,
        shared_membership_bytes=sum(v.order.nbytes+v.inverse.nbytes+v.bit.nbytes for v in views),
        no_ancestor_leaf_lists=True,synthetic_only=True,community_forecast_not_measured=True),f,indent=2);f.write('\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.output)
