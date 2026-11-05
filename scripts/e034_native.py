#!/usr/bin/env python3
"""Native pooled-link admission and full-shape comparison forecast; no score.

The graph model's timed microprobe is fresh/discarded; source cache/old vectors
are unchanged and no probe state can enter a scientific fit. Three planned node
caches are new outputs and are sealed/reused, rather than regenerated later.
"""
import argparse,json,os
from pathlib import Path
import sys,time
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def original_inputs(plan,output):
    """Bind only actual consumed accepted DNA/views/features/markers, without mutation."""
    p=json.loads(Path(plan).read_text());names={v for u in p['units'].values() for k,v in u.items() if k in ['features','views','fasta','marker_evidence']}
    names|={str(Path(n).with_suffix('.json')) for n in list(names) if str(n).endswith('.npz')}
    value={n:binding(n) for n in sorted(names)};write(output,value);return value


def pool(plan):
    """Complete one fixed ordered physical graph per community and admit utility."""
    from e034_control import product_scope
    product_scope();from dl_binner.genomegraph.links import pool as produce
    from dl_binner.multiview.views import load
    p=json.loads(Path(plan).read_text());root=Path(p['work']).parent.parent;task=Path(p['work']).parent;result={}
    for community,unit in [('E009','E009-noGLM'),('oral','oral-noGLM')]:
        _,m=load(p['units'][unit]['features']);folders=[task/'links'/community/('sample-%02d'%i)/'links' for i in range(10)]
        r=produce(folders,m['samples'],p['physical'][community]);result[community]=r['utility']
    write(root/'gates/pooled.json',dict(status='PASS_CLOSED_GRAPHS',utility=result,truth_accessed=False))


def probe(plan):
    """Time fresh isolated full-shape steps and close reusable feature prerequisites."""
    from e034_control import product_scope,read_plan,stage,UNITS
    product_scope();p=read_plan(plan);root=Path(p['work']).parent.parent
    stage(plan,'barrier');rows={};forecast=0
    # Feature cache stage is accepted once. The subsequent serial DAG verifies
    # its seal and does not recreate it or replay older learning/science.
    for u in UNITS:
        stage(plan,'node-features',u)
        argv=[p['python'],'-I','-B',str(ROOT/'scripts/e034_native.py'),'--plan',str(plan),'--action','probe-one','--unit',u]
        import subprocess
        with (root/'logs'/('probe-'+u+'.log')).open('x') as f:res=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT)
        if res.returncode:raise RuntimeError('Full-shape graph probe failed; actual log retained')
        q=json.loads((root/'gates'/('probe-'+u+'.json')).read_text());rows[u]=q;forecast+=q['forecast_fit_seconds']
    backend=6*3600;collection=1800;forecast=forecast*2+backend+collection
    config=json.loads((root/'config.json').read_text());remaining=config['review_deadline_epoch']-time.time()
    # Worst compressed output exposure before new fits, using actual saved NPZ
    # sizes plus a declared bounded graph/partition/checkpoint/log allowance.
    cached=sum(q['cache_bytes'] for q in rows.values());return_upper=cached+int(1.25*1024**3)
    gate=dict(status='PASS' if forecast<remaining-1800 and return_upper<=4*1024**3 else 'REFUSED',forecast_seconds=forecast,remaining_seconds=remaining,
        fit_microprobes=rows,downstream_reserve_seconds=backend,collection_seconds=collection,
        return_upper_bytes=return_upper,aggregate_compressed_cap_bytes=4*1024**3,all_probe_states_discarded=True,truth_accessed=False)
    write(root/'gates/full-schedule.json',gate)
    if gate['status']!='PASS':raise ValueError('Full-shape time/return budget refused; do not fit')


def probe_one(plan,unit):
    """Use real full-shape cache and fresh graph modules without retaining updates."""
    import numpy as np,torch
    from threadpoolctl import threadpool_limits
    from dl_binner.genomegraph.model import Encoder,DEFAULT
    from dl_binner.multiview.arrays import load_arrays
    from dl_binner.model import configure_torch
    threadpool_limits(4);configure_torch(4);torch.manual_seed(11)
    from e034_control import product_scope,read_plan
    product_scope();p=read_plan(plan);root=Path(p['work']).parent.parent;path=Path(p['work'])/unit/'node-features/result/features.npz';before=binding(path);a,m=load_arrays(path,'genome_graph_features')
    model=Encoder(a['local'].shape[1],a['bootstrap'].shape[1],a['depth'].shape[1]);optimizer=torch.optim.AdamW(model.parameters(),lr=.001)
    edges=a['edges'][:256];ix=np.unique(edges);positions=np.searchsorted(ix,edges)
    if len(ix)<2:raise ValueError('No physical training population')
    tensors={k:torch.from_numpy(a[k][ix]) for k in ['bootstrap','local','physical_one','physical_two','similarity','active','composition','depth']}
    values=[tensors[k] for k in ['bootstrap','local','physical_one','physical_two','similarity','active']]
    weight=torch.from_numpy(a['edge_weights'][:len(edges)].astype(np.float32))
    from torch.nn import functional as F
    prototype=F.normalize((tensors['bootstrap'][positions[:,0]]+tensors['bootstrap'][positions[:,1]]).detach(),dim=1)
    times=[]
    for k in range(4):
        start=time.monotonic();z=model(*values)
        alignment=(((1-(z[positions[:,0]]*prototype).sum(1).clamp(-1,1))+(1-(z[positions[:,1]]*prototype).sum(1).clamp(-1,1)))*.5*weight).sum()/weight.sum()
        anchor=(1-(z*tensors['bootstrap']).sum(1).clamp(-1,1)).mean()
        comp=F.mse_loss(model.composition_decoder(z),tensors['composition'])
        dep=F.mse_loss(model.depth_decoder(z),tensors['depth']) if model.depth_decoder is not None else z.sum()*0
        loss=alignment+DEFAULT['anchor_weight']*anchor+DEFAULT['composition_reconstruction_weight']*comp+DEFAULT['depth_reconstruction_weight']*dep
        optimizer.zero_grad(set_to_none=True);loss.backward();optimizer.step();times.append(time.monotonic()-start)
    if binding(path)!=before:raise ValueError('Probe altered accepted feature bytes')
    seconds=max(times[1:])*int(np.ceil(len(a['edges'])/256))*DEFAULT['epochs']*2
    write(root/'gates'/('probe-'+unit+'.json'),dict(status='PASS',cache=before,cache_bytes=path.stat().st_size,rows=len(a['ids']),active=int(a['active'].sum()),edges=len(a['edges']),step_seconds=times,forecast_fit_seconds=seconds,temporary_updates_not_consumed=True,old_encoder_fit=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True,type=Path);p.add_argument('--action',choices=['pool','probe','probe-one','inputs'],required=True);p.add_argument('--unit',choices=['E009-noGLM','E009-GLM','oral-noGLM']);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.action=='inputs':original_inputs(a.plan,a.output)
    elif a.action=='pool':pool(a.plan)
    elif a.action=='probe':probe(a.plan)
    else:probe_one(a.plan,a.unit)
