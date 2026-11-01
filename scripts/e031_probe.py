#!/usr/bin/env python3
"""Measure actual full-batch E031 kernels on generated numerical inputs only.

This is a setup/resource probe, not community training or a quality result. The
complete schedule forecast adds retained bank/I/O/collapse-monitor overhead and
all downstream/collection costs. Mac throughput never grants Linux admission.
"""
import argparse
import json
import math
from pathlib import Path
import sys
import time

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import write
from e031_control import product_scope


def run(output,steps=3):
    """Exercise fused/sequence, reconstruction, signed, anchor, EMA and optimizer math."""
    product_scope()
    import numpy as np
    import torch
    from torch.nn import functional as F
    from dl_binner.bootstrap import model
    from dl_binner.relational import model as original
    from dl_binner.unified.training import configuration
    from dl_binner.model import configure_torch
    from dl_binner.multiview.positive import pair_loss,update_target
    from dl_binner.multiview.model import parent_average
    configure_torch(4)
    if type(steps) is not int or not 1<=steps<=10:raise ValueError('Bounded synthetic probe steps required')
    cases={};n=256;count=n*5
    for glm in [False,True]:
        cfg=configuration(glm);torch.manual_seed(11)
        online,target,predictors=original.initialize(10,cfg)
        optimizer=torch.optim.AdamW(list(online.parameters())+list(predictors.parameters()),lr=.001,weight_decay=.00001)
        sum(p.square().sum() for p in online.parameters()).backward()
        sum(p.square().sum() for p in predictors.parameters()).backward();optimizer.step()
        state=dict(config=cfg,samples=[str(i) for i in range(10)],ema_updates=1,
            model_state=online.state_dict(),target_state=target.state_dict(),predictor_state=predictors.state_dict(),optimizer_state=optimizer.state_dict())
        online,target,predictors,anchor,optimizer=model.initialize(state)
        s=F.normalize(torch.randn(count,136),dim=1);depth=torch.randn(count,10);mask=torch.rand(count)>=.5
        local=torch.randn(count,8,136);position=torch.rand(count,8,3);keep=torch.ones(count,8,dtype=torch.bool)
        args=[s,depth,mask,local,position,keep]
        if glm:args += [torch.randn(count,768),torch.rand(count,2)]
        parents=torch.arange(n).repeat(5);weights=torch.ones(n);times=[]
        for at in range(steps+1):
            start=time.monotonic();online.train();predictors.train();fused,seq=online(*args)
            with torch.no_grad():tf,ts=target(*args)
            positive=pair_loss(fused,tf,parents,weights,predictors[0])+.5*pair_loss(seq,ts,parents,weights,predictors[1])
            wanted=s[:n][parents]
            reconstruct=parent_average(((F.normalize(online.composition_decoder(fused),dim=1)-wanted).square().sum(1)+
                (F.normalize(online.composition_decoder(seq),dim=1)-wanted).square().sum(1))*.5,parents,weights)
            rd=F.smooth_l1_loss(online.depth_decoder(fused),depth)
            parent_args=[x[:n] for x in args];parent_args[2]=torch.ones(n,dtype=torch.bool)
            preserve=model.anchor_loss(online,anchor,parent_args,weights)
            pair_args=[x[:512] for x in args]
            pair_args[2]=torch.zeros(512,dtype=torch.bool)
            x=[z.reshape(256,2,-1) for z in model.preserved_forward(online,pair_args)]
            y=[z.reshape(256,2,-1) for z in model.preserved_forward(target,pair_args,True)]
            predictors.eval();p,q=original.signed_loss(x,y,predictors,torch.tensor([1,-1]*128,dtype=torch.int8),torch.full((256,),.5),.2)
            loss=positive+reconstruct+.1*rd+.1*(p+q)+.1*preserve
            if not torch.isfinite(loss):raise ValueError('Nonfinite synthetic probe loss')
            optimizer.zero_grad(set_to_none=True);loss.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for g in optimizer.param_groups for p in g['params']):
                raise ValueError('Nonfinite synthetic probe gradient')
            if any(p.grad is not None for m in [target,anchor] for p in m.parameters()):raise ValueError('Stopped probe target gradient')
            optimizer.step();update_target(online,target,.996)
            elapsed=time.monotonic()-start
            if at:times.append(elapsed)
        cases['GLM' if glm else 'noGLM']=dict(batch_parents=n,available_views=count,signed_pairs=256,
            measured_step_seconds=times,median_step_seconds=float(np.median(times)),
            finite_loss=bool(torch.isfinite(loss)),parameter_count=sum(p.numel() for p in online.parameters()),threads=torch.get_num_threads())
    axes=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/reuse-lock.json').read_text())['axes']
    estimates={u:20*math.ceil(a['eligible']/256)*cases['GLM' if u=='E009-GLM' else 'noGLM']['median_step_seconds']*1.5 for u,a in axes.items()}
    write(output,dict(status='PASS',cases=cases,generated_inputs_only=True,community_fit=False,
        science_seed_unchanged=11,projected_training_seconds_with_50_percent_IO_headroom=estimates,
        native_admission=False,scope='Full-shape kernels; retained real-bank timing and full complete schedule must also pass on the actual Linux VM'))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--output',required=True,type=Path);a.add_argument('--steps',type=int,default=3)
    v=a.parse_args();run(v.output,v.steps)
