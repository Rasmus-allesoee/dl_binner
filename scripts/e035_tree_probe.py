#!/usr/bin/env python3
"""Bounded full-release hierarchy/Adam shape probe on synthetic inputs only.

Uses the admitted *metadata tree*, never community DNA, labels or vectors. Local
throughput is a planning observation, not a Linux/GCP speed or quality guarantee.
"""
import argparse
from pathlib import Path
import time

import numpy as np
import torch


def run(tree_path,output):
    """Exercise large sibling groups, gradients, optimizer state and exact reload."""
    from dl_binner.taxonomy.tree import Tree
    from dl_binner.taxonomy.model import Encoder,hierarchy_loss,policy
    from dl_binner.model import configure_torch
    from dl_binner.bootstrap.model import state_digest
    from dl_binner.context.tokens import binding
    from dl_binner.io import write_json
    configure_torch(4);tree=Tree.load(tree_path);rng=np.random.default_rng(11);torch.manual_seed(11)
    parents=256;owners=np.repeat(np.arange(parents),5);maximum=int(np.argmax([len(x)for x in tree.children]))
    labels=rng.choice(np.arange(2,len(tree.nodes)),parents);labels[:128]=rng.choice(tree.children[maximum],128)
    paths=np.stack([tree.path(int(i))for i in labels])[owners]
    base=torch.nn.functional.normalize(torch.randn(len(owners),64),dim=1);sequence=base.clone();composition=torch.randn(len(owners),136);depth=torch.randn(len(owners),10)
    args=[base,sequence,composition,depth,torch.ones(len(owners),dtype=torch.bool),torch.from_numpy(paths).long(),torch.full((len(owners),),.8),torch.ones(len(owners),dtype=torch.bool)]
    model=Encoder(64,10,tree);optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
    start=time.monotonic();times=[]
    for step in range(16):
        t=time.monotonic();z=model(*args);loss=hierarchy_loss(model,z,args[5],tree).mean()+(z-base).square().sum(1).mean()
        optimizer.zero_grad(set_to_none=True);loss.backward()
        if not all(p.grad is None or torch.isfinite(p.grad).all()for p in model.parameters()):raise ValueError('Full-tree probe gradient nonfinite')
        optimizer.step();times.append(time.monotonic()-t)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    torch.save(dict(model=model.state_dict(),optimizer=optimizer.state_dict()),output/'state.pt')
    saved=torch.load(output/'state.pt',weights_only=True,map_location='cpu');copy=Encoder(64,10,tree);copy.load_state_dict(saved['model'],strict=True)
    if state_digest(copy)!=state_digest(model)or not torch.equal(copy(*args),model(*args)):raise ValueError('Full-tree exact reload failed')
    write_json(output/'completed.json',dict(status='PASS_FULL_TREE_SYNTHETIC_SHAPE_ONLY',tree=binding(tree_path),policy=policy(),
        nodes=len(tree.nodes),largest_sibling_group=len(tree.children[maximum]),parents=parents,views=len(owners),updates=16,
        mean_update_seconds=float(np.mean(times[2:])),first_update_seconds=times[0],wall_seconds=time.monotonic()-start,
        new_parameters=sum(p.numel()for p in model.parameters()),new_Adam_parameters_with_state=len(optimizer.state),
        threads=4,platform='local macOS Python 3.10 CPU; not native GCP admission',community_data_accessed=False,
        generated_labels_not_biological_predictions=True,model_reload_exact=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tree',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.tree,a.output)
