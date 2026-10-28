#!/usr/bin/env python3
"""Bounded synthetic full-width runtime probe, never a community neighbor run.

One fixed 4,096-row shape exercises the compiled joint index. A conservative
size/log-size extrapolation is a planning estimate, not a measured full-Oral
speed claim. The independent whole-phase guard remains authoritative.
"""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
import numpy as np
from e025_information import JointIndex
from e024_coverage import write
from dl_binner.density.grouping import policy,context_channels


def probe(output):
    """Time one frozen 4,096 x 212 synthetic index with mixed measured zeros."""
    n=4096;rng=np.random.default_rng(11)
    x=rng.normal(size=(n,64)).astype(np.float32);x/=np.linalg.norm(x,axis=1)[:,None]
    d=dict(ids=np.array([f'fixture-{j:06}' for j in range(n)]),eligible=np.ones(n,bool),
        lengths=rng.integers(500,20000,n),tnf=rng.dirichlet(np.ones(136),n).astype(np.float32),
        depth=rng.uniform(0,20,(n,10)).astype(np.float32),depth_evidence=np.ones(n,bool))
    d['depth'][::3]=0;d['depth_evidence'][::3]=False
    cfg=policy(ROOT/'experiments/E023-adaptive-density-bins/config.json')
    c,a,s,_=context_channels(d,x,np.arange(n),cfg)
    original=dict(neighbors=np.array([[(j+k)%n for k in range(1,31)] for j in range(n)],np.int64))
    # Compilation is fixed per new process/signature, not per community row.
    # Numba's nested TimingListener counts enclosing intervals once, avoiding
    # double-counting the many nested compiler passes. Preserve the earlier
    # total-wall extrapolation refusal; this is an explicit measurement repair.
    from numba.core.event import install_timer
    from pynndescent import NNDescent
    compilation=[]
    started=time.monotonic()
    with install_timer('numba:compile',compilation.append):
        index=JointIndex(d,c,a,s,np.arange(n),original,cfg,4)
    elapsed=time.monotonic()-started
    compiled=sum(compilation)
    if not 0 <= compiled <= elapsed:raise ValueError('Compiler timing outside measured index wall')
    variable=elapsed-compiled
    forecast=2*compiled+2*variable*(508763/n)*(np.log2(508763)/np.log2(n))+1500
    maximum=json.loads((ROOT/'experiments/E025-joint-distance-retrieval/runtime-plan.json').read_text())['limits']['seconds']-1200
    result=dict(status='PASS' if forecast<=maximum else 'REFUSE_FORECAST',synthetic=True,
        rows=n,dimensions=index.x.shape[1],seconds_including_this_process_compile=elapsed,
        measured_compilation_seconds=compiled,remaining_index_seconds=variable,
        planning_remaining_science_seconds=float(forecast),planning_maximum=maximum,
        formula='2 x measured fixed compilation + 2 x remaining index wall x N/4096 x log2(N)/log2(4096) +1500s for rerank/hierarchy/export/audit/collection',
        limits='Single synthetic shape; biological distribution/nonmetric recall/full-scale cost remain unproved',
        native_index=True,threads=4,community_science=False)
    write(output,result)
    if result['status']!='PASS':raise TimeoutError('Synthetic complete-schedule forecast exceeds fixed envelope')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();probe(a.output)
