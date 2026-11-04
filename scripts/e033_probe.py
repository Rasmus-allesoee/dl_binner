#!/usr/bin/env python3
"""Native full-shape three-update throughput gate; no retained community fit.

Restores the same fixed initialization and uses genuine cached DNA/coverage views.
Its temporary optimizer updates are engineering timing only and never consumed by
teacher, proposals, student or evaluation. No labels or new data are reachable.
"""
import argparse
import copy
import json
import math
from pathlib import Path
import time


def probe(features,new_features,views,tokens,frozen,measurements,original,output,threads=4):
    """Time three complete 256-parent self-view/anchor/reconstruction update steps."""
    import numpy as np
    import platform
    import torch
    from torch.nn import functional as F
    from dl_binner.multiscale import model
    from dl_binner.multiscale.cache import Bank
    from dl_binner.multiview.views import load
    from dl_binner.multiview.model import parent_average
    from dl_binner.multiview.positive import pair_loss,update_target
    from dl_binner.relational import model as inherited
    from dl_binner.bootstrap.model import preserved_forward
    from dl_binner.io import write_json
    model.configure_torch(threads);start=time.monotonic()
    saved,_=model.read_original(original,features,views,tokens,frozen)
    data,meta,v,_=load(features,views);new,_=load(new_features)
    bank=inherited.make_bank(tokens,frozen,features,views,data,meta,v,saved['config'])
    coverage=Bank(measurements,features,views,data,v);cs=coverage.fit()
    state=copy.deepcopy(saved['transform']);x=np.log1p(new['depth'][data['eligible']].astype(np.float64))
    state['depth']=dict(mean=x.mean(0).tolist(),std=x.std(0).tolist());s,d=model.transformed(data,new,state)
    online,target,predictors,anchor,optimizer=model.initialize(saved);online.train();predictors.train()
    rows=np.flatnonzero(data['eligible']);rows=rows[np.random.default_rng(11).permutation(len(rows))[:256]]
    if len(rows)<2:raise ValueError('Native probe has insufficient parents')
    ns=len(rows);timings=[];weights=torch.from_numpy(np.log1p(np.minimum(data['lengths'][rows],10000)/500).astype(np.float32))
    for step in range(3):
        begin=time.monotonic()
        sequences=[s[rows]]+[model.transform(v['tnf'][rows,j],new['depth'][rows],new['depth_evidence'][rows],state)[0] for j in range(4)]
        available=np.concatenate([np.ones(ns,bool)]+[v['usable'][rows,j] for j in range(4)])
        owners=np.tile(np.arange(ns),5)[available];indices=np.tile(rows,5)[available];numbers=np.repeat(np.arange(5),ns)[available]
        args=model.args(np.concatenate(sequences)[available],d[indices],new['depth_evidence'][indices],bank,coverage,indices,numbers,state,saved['config'],cs)
        fused,sequence=online(*args)
        with torch.no_grad():tf,ts=target(*args)
        own=torch.from_numpy(owners);loss=pair_loss(fused,tf,own,weights,predictors[0])+.5*pair_loss(sequence,ts,own,weights,predictors[1])
        wanted=torch.from_numpy(s[rows])[own]
        rc=parent_average(((F.normalize(online.base.composition_decoder(fused),dim=1)-wanted).square().sum(1)
            +(F.normalize(online.base.composition_decoder(sequence),dim=1)-wanted).square().sum(1))*.5,own,weights)
        stats,valid=coverage.statistics(indices,numbers)
        wanted_depth=torch.from_numpy((np.log1p(stats[:,:,0])/np.asarray(cs['parent_log_median_scale'])).astype(np.float32))
        valid=torch.from_numpy(valid);rd=parent_average((F.smooth_l1_loss(online.coverage_decoder(fused),wanted_depth,reduction='none')*valid).sum(1)/valid.sum(1).clamp_min(1),own,weights)
        pa=model.args(s[rows],d[rows],new['depth_evidence'][rows],bank,coverage,rows,np.zeros(ns,np.int64),state,saved['config'],cs)
        now=preserved_forward(online,pa);fixed=preserved_forward(anchor,pa[:-2],True)
        al=sum(k*(((a-b.detach()).square().sum(1)*weights).sum()/weights.sum()) for k,a,b in zip((1/1.5,.5/1.5),now,fixed))
        loss=loss+rc+.1*rd+.1*al
        if not torch.isfinite(loss):raise ValueError('Native probe loss nonfinite')
        optimizer.zero_grad(set_to_none=True);loss.backward()
        if any(p.grad is not None and not torch.isfinite(p.grad).all() for g in optimizer.param_groups for p in g['params']):raise ValueError('Native probe gradient nonfinite')
        optimizer.step();update_target(online,target,.996);timings.append(time.monotonic()-begin)
    # A signed student also evaluates extra full-parent endpoints; budget twice
    # the adapted-teacher estimate, then 1.5x throughput uncertainty. No speedup
    # from the Mac is assumed and no old learner output is replayed/consumed.
    teacher_seconds=max(timings[1:])*math.ceil(int(data['eligible'].sum())/256)*20
    write_json(output,dict(status='PASS_FULL_SHAPE_PROBE' if len(data['ids'])>128 else 'PASS_TINY_PROBE_PATH',system=platform.system(),community_workload_measured=len(data['ids'])>128,parents=int(data['eligible'].sum()),batch_parents=ns,
        step_seconds=timings,teacher_estimate_seconds=teacher_seconds,two_fit_estimate_with_student_and_uncertainty_seconds=teacher_seconds*3*1.5,
        setup_seconds=time.monotonic()-start-sum(timings),temporary_updates_not_consumed=True,truth_accessed=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['features','new-features','views','tokens','measurements','original','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--frozen',type=Path);a=p.parse_args()
    probe(a.features,a.new_features,a.views,a.tokens,a.frozen,a.measurements,a.original,a.output)
