"""Parent-balanced multiview contrastive learning with denoising reconstruction.

Positives are the parent and its usable real crops, never genome/taxonomy labels.
Different contigs can be co-genomic false negatives. Fixed view banks, measured
parent depth and random branch dropout are declared assumptions, not measured
crop coverage. All training/inference/grouping use the same unit geometry.
"""
import json
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from ..candidate.model import Encoder as BaseEncoder,fit_transform,transform,infer
from ..io import digest,emit,save_arrays,load_arrays,write_json
from ..model import configure_torch,batches
from .views import load


class Encoder(BaseEncoder):
    """Retain dev4 branch dimensions; add small decoders on unit representations."""
    def __init__(self,samples,cfg):
        super().__init__(samples,cfg)
        self.composition_decoder=nn.Sequential(nn.Linear(cfg['output'],cfg['fusion_hidden']),nn.ReLU(),nn.Linear(cfg['fusion_hidden'],136))
        self.depth_decoder=(nn.Sequential(nn.Linear(cfg['output'],cfg['depth_hidden']),nn.ReLU(),nn.Linear(cfg['depth_hidden'],samples)) if samples else None)


def parent_average(loss,parents,weights):
    """Average available anchors within each parent, then apply fixed length weights."""
    unique,inverse=torch.unique(parents,return_inverse=True)
    sums=torch.zeros(len(unique),dtype=loss.dtype,device=loss.device).scatter_add_(0,inverse,loss)
    counts=torch.zeros_like(sums).scatter_add_(0,inverse,torch.ones_like(loss))
    w=weights[unique]
    return ((sums/counts)*w).sum()/w.sum()


def multiview_loss(z,parents,temperature,weights):
    """Average log-positive probabilities outside the log, without false self-negatives.

    Every other available view of the same parent is positive. Diagonal self
    comparisons are absent. Single-view parents supply negatives but no invalid
    positive anchor; with fewer than two distinct parents the loss is zero.
    """
    if len(z)!=len(parents) or not 0<temperature or not torch.isfinite(z).all():raise ValueError('Invalid multiview loss axes/values')
    if len(z)<2 or len(torch.unique(parents))<2:return z.sum()*0
    diagonal=torch.eye(len(z),dtype=torch.bool,device=z.device)
    positive=(parents[:,None]==parents[None,:])&~diagonal
    counts=positive.sum(1);valid=counts>0
    if not valid.any():return z.sum()*0
    logits=(z@z.T)/temperature
    denominator=torch.logsumexp(logits.masked_fill(diagonal,-torch.inf),dim=1)
    # Do not multiply masked -infinity by zero, which would create NaNs.
    logp=logits-denominator[:,None]
    losses=-logp.masked_fill(~positive,0).sum(1)/counts.clamp(min=1)
    return parent_average(losses[valid],parents[valid],weights)


def train(features,views,output,cfg,threads):
    """Fit the one declared schedule on every eligible parent and save exact reload inputs."""
    configure_torch(threads);data,meta,v,vm=load(features,views)
    if vm['policy']!=cfg:raise ValueError('Multiview bank/config differs')
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
    values,valid=infer(model,data,state,cfg)
    saved=dict(kind='multiview_checkpoint',version=1,config=cfg,transform=state,samples=meta['samples'],
               model_state=model.state_dict(),optimizer_state=optimizer.state_dict(),training_features_sha256=digest(features),training_views_sha256=digest(views))
    with (out/'checkpoint.pt').open('xb') as f:torch.save(saved,f)
    write_json(out/'checkpoint.json',dict(kind='multiview_checkpoint',version=1,sha256=digest(out/'checkpoint.pt'),
        config=cfg,transform=state,samples=meta['samples'],training_features_sha256=digest(features),training_views_sha256=digest(views),
        history=history,threads=threads,loader_workers=0,training_parents=len(indices),
        contrastive_parents=int((data['eligible']&v['usable'].any(1)).sum()),parameter_count=sum(p.numel() for p in model.parameters()),
        wall_seconds=time.monotonic()-start,process_cpu_seconds=time.process_time()-cpu,
        assumptions='Fixed real-crop bank; parent mean depth with independent branch dropout; co-genomic negatives/chimeric positives unresolved; no truth/markers/taxonomy.'))
    save_arrays(out/'reference.npz',dict(ids=data['ids'],features=values,evidence=valid),dict(kind='embeddings',
                mode='multiview_pre_save_reference',samples=meta['samples'],features_sha256=digest(features),checkpoint_sha256=digest(out/'checkpoint.pt')))


def embed(features,checkpoint,output,threads):
    """Reload in a separate process; require exact same-runtime parent inference."""
    configure_torch(threads);data,meta=load(features);path=Path(checkpoint);receipt=json.loads(path.with_suffix('.json').read_text())
    if receipt['sha256']!=digest(path) or receipt['training_features_sha256']!=digest(features):raise ValueError('Multiview checkpoint/input bytes differ')
    saved=torch.load(path,weights_only=True,map_location='cpu')
    if (saved['kind']!='multiview_checkpoint' or saved['version']!=1 or saved['samples']!=meta['samples']
            or saved['config']!=receipt['config'] or saved['transform']!=receipt['transform']
            or saved['training_features_sha256']!=digest(features) or saved['training_views_sha256']!=receipt['training_views_sha256']):
        raise ValueError('Multiview checkpoint schema/sample/transform differs')
    model=Encoder(len(meta['samples']),saved['config']);model.load_state_dict(saved['model_state'],strict=True)
    if any(not torch.isfinite(p).all() for p in model.parameters()):raise ValueError('Nonfinite multiview checkpoint')
    values,valid=infer(model,data,saved['transform'],saved['config']);reference,rm=load_arrays(path.parent/'reference.npz','embeddings')
    if (rm['checkpoint_sha256']!=digest(path) or any(not np.array_equal(reference[k],v) for k,v in [('ids',data['ids']),('features',values),('evidence',valid)])):
        raise ValueError('Multiview exact same-runtime reload differs')
    save_arrays(output,dict(ids=data['ids'],features=values,evidence=valid),dict(kind='embeddings',mode='multiview_learned_unit_sphere',
                samples=meta['samples'],features_sha256=digest(features),checkpoint_sha256=digest(path),reload_exact=True,
                metric='unit-sphere cosine/equivalent Euclidean; no post-learning transform'))
