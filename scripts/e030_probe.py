#!/usr/bin/env python3
"""Measure actual candidate operations at a synthetic large sparse/forest shape.

No community partitions, truth, detector, index or model are run. Forecast both
construction and its independent cached audit, setup/collection and hashing I/O.
Native admission remains a forecast rather than a scientific result.
"""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import write


def run(output,rows=32768):
    """Exercise full channel widths, many alternatives and all sparse update rows."""
    from e030_control import product_scope
    product_scope()
    import numpy as np
    from dl_binner.construction import grouping as g
    from dl_binner.unified import grouping as original
    n=rows;rng=np.random.default_rng(11);size=2*n-1
    children=np.full((size,2),-1,np.int64);mass=np.zeros(size,np.int64);count=np.zeros(size,np.int64);level=np.zeros(size)
    lengths=rng.integers(500,20000,n,dtype=np.int64);mass[:n]=lengths;count[:n]=1;queue=list(range(n));at=n
    while len(queue)>1:
        next_=[]
        for j in range(0,len(queue)-1,2):
            a,b=sorted(queue[j:j+2]);children[at]=[a,b];mass[at]=mass[a]+mass[b];count[at]=count[a]+count[b];level[at]=max(level[a],level[b])+1.;next_.append(at);at+=1
        if len(queue)%2:next_.append(queue[-1])
        queue=next_
    tree=dict(children=children,mass=mass,count=count,level=level,roots=np.array(queue),core=np.full(n,.1))
    tnf=rng.dirichlet(np.ones(136),n).astype(np.float32);depth=rng.uniform(0,30,(n,10)).astype(np.float32);depth[::3]=0
    vectors=rng.normal(size=(n,64)).astype(np.float32);vectors/=np.linalg.norm(vectors,axis=1)[:,None]
    data=dict(ids=np.array([f'opaque-{i:08d}' for i in range(n)]),lengths=lengths,tnf=tnf,depth=depth)
    valid=np.ones(n,bool);nn=(np.arange(n)[:,None]+np.arange(1,31))%n;dd=np.broadcast_to(np.linspace(.1,1.,30),(n,30)).copy()
    a=dict(selected=np.arange(n),neighbors=nn,distances=dd);evidence=dict(panel_size=107,calls={})
    alternatives=original.alternatives_for(tree,lengths,data['ids'].tolist(),evidence,original.policy())
    started=time.monotonic();parts,choices,stats,calibration,updates=g.construct(data,vectors,valid,a,tree,alternatives,evidence,g.policy());elapsed=time.monotonic()-started
    # Actual full eligible axes, not a projection from the number of genomes.
    axis=json.loads((ROOT/'experiments/E028-global-discovery-repair/protocol.json').read_text())['axes']
    total=2*sum(v['eligible'] for v in axis.values());scale=total/n
    forecast=elapsed*scale*2*1.75+3600 # construction+audit, headroom, setup/hash/export/upload reserve
    # The synthetic balanced tree deliberately has far more supported alternatives
    # per row than the admitted forests. Bound their actual count using immutable
    # JSON byte sizes and the minimum serialized required record schema; no
    # biological outcomes or regenerated candidates enter this storage forecast.
    reuse=json.loads((ROOT/'experiments/E030-supported-biological-bins/reuse-lock.json').read_text())
    minimum_record_bytes=len(json.dumps(dict(node=0,parent=0,children=[],birth=0.,stability=0.,bp=0),separators=(',',':')).encode())
    sizes=[v['bytes'] for k,v in reuse['accepted_members'].items() if k.endswith('/alternatives.json')]
    if len(sizes)!=6:raise ValueError('Six bound retained candidate inventories required')
    candidate_bound=sum(v//minimum_record_bytes for v in sizes)
    per_candidate_bytes=sum(v.nbytes for v in stats.values())//len(alternatives)
    profile_bytes=candidate_bound*per_candidate_bytes
    work_upper=profile_bytes+total*1200+128*1024**2
    peak_upper=work_upper+2*1024**3
    record=dict(status='PASS' if forecast<18000 and peak_upper<4*1024**3 else 'REFUSED_COMPLETE_FORECAST',
        synthetic_rows=n,synthetic_candidates=len(alternatives),elapsed_seconds=elapsed,total_actor_rows=total,
        construction_and_audit_factor=2,headroom_factor=1.75,setup_hash_collection_reserve_seconds=3600,
        planning_remaining_science_seconds=forecast,projected_unique_work_bytes=work_upper,
        projected_with_closed_copy_and_compressed_return_bytes=peak_upper,
        collector_scope='Work is packed in place; no second work copy. Full 2 GiB compressed cap coexists.',
        retained_alternative_count_upper=candidate_bound,minimum_serialized_record_bytes=minimum_record_bytes,
        numeric_profile_bytes_per_candidate=per_candidate_bytes,
        native_measurement=sys.platform.startswith('linux'),measured_platform=sys.platform,
        community_outputs=False,policy=g.policy())
    write(output,record);print(json.dumps(record),flush=True)
    if record['status']!='PASS':raise ValueError('Complete candidate forecast requires prospective resource reassessment')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--rows',type=int,default=32768);a=p.parse_args();run(a.output,a.rows)
