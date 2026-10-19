"""E015 training-only adapter over the byte-frozen dev5 loop.

Only view-policy admission changes: retained banks keep the original configuration,
while precisely the two reconstruction coefficients are zero for training. The
loop, native model/decoders, optimizer, random draws and saved artifacts otherwise
match the accepted dev5 function. AST equality is an executable release contract.
No package source or accepted bank is edited.
"""
import time
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from dl_binner.multiview.model import (Encoder,parent_average,multiview_loss,
    configure_torch,load,fit_transform,transform,infer,batches,digest,
    write_json,emit,save_arrays)

from e015_policy import validate_control


def train(features,views,output,cfg,threads):
    """Fit the one declared schedule on every eligible parent and save exact reload inputs."""
    configure_torch(threads);data,meta,v,vm=load(features,views)
    validate_control(cfg,vm['policy'])
    indices=np.flatnonzero(data['eligible'])
    if len(indices)<2:raise ValueError('Need at least two eligible parents')
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    state=fit_transform(data);parent,depth=transform(data['tnf'],data['depth'],data['depth_evidence'],state)
    # Transform each selected batch, avoiding a second whole-bank allocation.
    weights_np=np.log1p(np.minimum(data['lengths'],10000)/500).astype(np.float32)
    torch.manual_seed(cfg['seed']);rng=np.random.default_rng(cfg['seed'])
    model=Encoder(len(meta['samples']),cfg);optimizer=torch.optim.AdamW(model.parameters(),lr=cfg['learning_rate'],weight_decay=cfg['weight_decay'])
    usable_depth=np.asarray(state['depth']['std'])>1e-8
    start,cpu=time.monotonic(),time.process_time();history=[]
    for epoch in range(cfg['epochs']):
        model.train();seen=0;anchors=0;dropped=0;totals=np.zeros(5)
        for selected in batches(rng.permutation(indices),cfg['batch_size']):
            n=len(selected);s0=parent[selected];d0=depth[selected];m0=data['depth_evidence'][selected]
            bank=[s0]+[transform(v['tnf'][selected,j],data['depth'][selected],m0,state)[0] for j in range(4)]
            available=np.concatenate([np.ones(n,bool)]+[v['usable'][selected,j] for j in range(4)])
            owners=np.tile(np.arange(n),5)[available];composition=np.concatenate(bank)[available]
            original_mask=np.tile(m0,5)[available];observed_depth=np.tile(d0,(5,1))[available]
            mask=original_mask&(rng.random(len(owners))>=cfg['depth_dropout']);dropped+=int((original_mask&~mask).sum())
            owners=torch.from_numpy(owners);w=torch.from_numpy(weights_np[selected])
            fused,seq=model(torch.from_numpy(composition),torch.from_numpy(observed_depth),torch.from_numpy(mask))
            cf=multiview_loss(fused,owners,cfg['temperature'],w)
            cs=multiview_loss(seq,owners,cfg['temperature'],w)
            target=torch.from_numpy(s0)[owners]
            rf=(F.normalize(model.composition_decoder(fused),dim=1)-target).square().sum(1)
            rs=(F.normalize(model.composition_decoder(seq),dim=1)-target).square().sum(1)
            rc=parent_average((rf+rs)*.5,owners,w)
            rd=fused.sum()*0
            has=torch.from_numpy(original_mask)
            if model.depth_decoder is not None and usable_depth.any() and has.any():
                predicted=model.depth_decoder(fused)[has][:,usable_depth]
                wanted=torch.from_numpy(observed_depth)[has][:,usable_depth]
                dl=F.smooth_l1_loss(predicted,wanted,reduction='none').mean(1)
                rd=parent_average(dl,owners[has],w)
            loss=cf+cfg['sequence_loss_weight']*cs+cfg['composition_reconstruction_weight']*rc+cfg['depth_reconstruction_weight']*rd
            if not torch.isfinite(loss):raise ValueError('Nonfinite multiview loss')
            optimizer.zero_grad(set_to_none=True);loss.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in model.parameters()):raise ValueError('Nonfinite multiview gradient')
            optimizer.step();seen+=n;anchors+=len(owners)
            totals+=np.array([float(x.detach()) for x in (loss,cf,cs,rc,rd)])*n
        if seen!=len(indices):raise RuntimeError('Multiview parent exposure changed')
        h=dict(epoch=epoch+1,parents_seen=seen,available_views=anchors,depth_dropped_views=dropped,
               **dict(zip(['loss','fused_contrastive','sequence_contrastive','composition_reconstruction','depth_reconstruction'],(totals/seen).tolist())),
               wall_seconds=time.monotonic()-start)
        history.append(h);emit('multiview_epoch',**h)
    contrastive_parents=int((data['eligible']&v['usable'].any(1)).sum())
    # The fixed bank is no longer needed. Do not retain gigabytes of crop views
    # while allocating the full parent inference transforms/reference output.
    del v
    values,valid=infer(model,data,state,cfg)
    saved=dict(kind='multiview_checkpoint',version=1,config=cfg,transform=state,samples=meta['samples'],
               model_state=model.state_dict(),optimizer_state=optimizer.state_dict(),training_features_sha256=digest(features),training_views_sha256=digest(views))
    with (out/'checkpoint.pt').open('xb') as f:torch.save(saved,f)
    write_json(out/'checkpoint.json',dict(kind='multiview_checkpoint',version=1,sha256=digest(out/'checkpoint.pt'),
        config=cfg,transform=state,samples=meta['samples'],training_features_sha256=digest(features),training_views_sha256=digest(views),
        history=history,threads=threads,loader_workers=0,training_parents=len(indices),
        contrastive_parents=contrastive_parents,parameter_count=sum(p.numel() for p in model.parameters()),
        wall_seconds=time.monotonic()-start,process_cpu_seconds=time.process_time()-cpu,
        assumptions='Fixed real-crop bank; parent mean depth with independent branch dropout; co-genomic negatives/chimeric positives unresolved; no truth/markers/taxonomy.'))
    save_arrays(out/'reference.npz',dict(ids=data['ids'],features=values,evidence=valid),dict(kind='embeddings',
                mode='multiview_pre_save_reference',samples=meta['samples'],features_sha256=digest(features),checkpoint_sha256=digest(out/'checkpoint.pt')))
