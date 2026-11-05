"""Compact residual graph learning on frozen, source-bound contig evidence.

Physical one/two-hop messages are cached sparsely before the MLP, avoiding dense
adjacency reconstruction and neighbor sampling explosion. Similarity context is
separate. An unlinked row retains its exact bootstrap vector, including exclusion.
"""
import json
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from ..context.tokens import binding
from ..io import emit, id_digest, load_arrays, save_arrays, write_json
from .links import read as read_links

DEFAULT=dict(version=1,seed=11,epochs=20,batch_size=256,hidden=64,learning_rate=.001,
    weight_decay=.0001,anchor_weight=.1,composition_reconstruction_weight=1.,depth_reconstruction_weight=.1,
    objective='stopped_physical_endpoint_prototypes_plus_bootstrap_and_modality_reconstruction',negative_policy='no_unlabeled_random_negatives',
    physical_hops=2,similarity_context=5,unlinked='exact_bootstrap',initializer='zero_residual')


def policy(value=None):
    """Require the prospectively frozen graph learner; tiny epochs are explicit."""
    v=DEFAULT if value is None else value
    if v!=DEFAULT or any(type(v[k]) is not type(x) for k,x in DEFAULT.items()):raise ValueError('Unfrozen graph learner policy')
    return dict(v)


def standardize(values,eligible):
    """Fit a saved label-free per-channel scale; constant channels stay explicit."""
    x=np.asarray(values,np.float32)
    if x.ndim!=2 or not np.isfinite(x).all() or not np.any(eligible):raise ValueError('Invalid graph feature matrix')
    mean=x[eligible].mean(0,dtype=np.float64);std=x[eligible].std(0,dtype=np.float64)
    return ((x-mean)/np.where(std>0,std,1)).clip(-8,8).astype(np.float32),dict(mean=mean.tolist(),std=std.tolist(),constant=(std==0).tolist())


def messages(values,edges,weights):
    """Compute degree-normalized sparse messages, retaining zero-degree rows."""
    from scipy.sparse import coo_matrix
    n=len(values);i=np.r_[edges[:,0],edges[:,1]];j=np.r_[edges[:,1],edges[:,0]];w=np.r_[weights,weights]
    graph=coo_matrix((w,(i,j)),shape=(n,n)).tocsr();mass=np.asarray(graph.sum(1)).ravel()
    graph.data*=np.repeat(np.divide(1,mass,out=np.zeros_like(mass),where=mass>0),np.diff(graph.indptr))
    return (graph@values).astype(np.float32),graph


def cache(features,bootstrap,neighbors,physical,coverage,output):
    """Bind original vectors and actual parent/crop moments, never infer/re-extract.

    `coverage` is the verified E033 Bank instance. Numerical parent/window fields
    remain separately named. This creates a new graph-only feature treatment and
    cannot erase historical priors encoded in the frozen bootstrap.
    """
    from ..multiview.views import load
    data,meta=load(features);b,bm=load_arrays(bootstrap,'embeddings');g,gm=load_arrays(neighbors,'candidate_sparse_graph');a,am=read_links(physical)
    if gm.get('embedding_sha256')!=binding(bootstrap)['sha256'] or bm.get('features_sha256')!=binding(features)['sha256']:
        raise ValueError('Frozen source graph/vector/feature binding differs')
    ids=data['ids'];eligible=data['eligible'];n=len(ids)
    if any(not np.array_equal(x,ids) for x in [b['ids'],g['ids'],a['ids']]) or not np.array_equal(a['eligible'],eligible) or not np.array_equal(a['lengths'],data['lengths']):raise ValueError('Graph cache full opaque axes differ')
    if not np.array_equal(b['evidence'],eligible) or not np.allclose(np.linalg.norm(b['features'][eligible],axis=1),1,rtol=0,atol=1e-6):raise ValueError('Frozen bootstrap unit geometry differs')
    if coverage.samples!=meta['samples'] or not np.array_equal(coverage.data['ids'],ids):raise ValueError('Measured parent/window sample axes differ')
    parts=[]
    for at in range(0,n,8192):
        ix=np.arange(at,min(at+8192,n));parent,pv=coverage.statistics(ix,np.zeros(len(ix),np.int64));windows=[];valid=[]
        for k in range(1,5):
            z,v=coverage.statistics(ix,np.full(len(ix),k,np.int64));windows.append(z);valid.append(v)
        w=np.stack(windows,1);v=np.stack(valid,1);den=np.maximum(v.sum(1),1)
        # Statistics are measured; across-crop dispersion is named separately
        # from the actual per-base population variance in each original interval.
        crop_mean=(w[...,:4]*v[...,None]).sum(1)/den[...,None]
        crop_disp=(((w[...,0]-crop_mean[:,None,:,0])**2)*v).sum(1)/den
        value=np.concatenate([np.log1p(parent[...,0]),parent[...,1],np.log1p(parent[...,2]),parent[...,3],pv.astype(float),
            np.log1p(crop_mean[...,0]),crop_mean[...,1],np.log1p(crop_mean[...,2]),crop_mean[...,3],np.log1p(crop_disp),v.mean(1)],1)
        parts.append(value.astype(np.float32))
    measured=np.concatenate(parts);raw=np.concatenate([data['tnf'],measured],1);x,transform=standardize(raw,eligible)
    e=a['edges'][eligible[a['edges']].all(1)];w=a['weights'][eligible[a['edges']].all(1)]
    one,graph=messages(x,e,w);two=(graph@one).astype(np.float32);active=np.asarray(graph.sum(1)).ravel()>0
    similarity=np.zeros_like(b['features']);nn=g['neighbors'];k=min(DEFAULT['similarity_context'],nn.shape[1])
    if k:
        for at in range(0,n,8192):
            ix=np.arange(at,min(at+8192,n));ok=eligible[ix];refs=nn[ix[ok],:k]
            if (refs<0).any() or (refs>=n).any():raise ValueError('Frozen similarity neighbor index differs')
            similarity[ix[ok]]=b['features'][refs].mean(1)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    receipt=dict(kind='genome_graph_features',version=1,ids_sha256=id_digest(ids.tolist()),samples=meta['samples'],transform=transform,
        tnf_dimensions=data['tnf'].shape[1],depth_dimensions=data['depth'].shape[1],inputs=dict(features=binding(features),bootstrap=binding(bootstrap),neighbors=binding(neighbors),physical=binding(Path(physical)/'completed.json'),coverage=binding(coverage.root/'bank.json')),
        measured_fields=['log_parent_mean','parent_breadth','log_parent_perbase_variance','parent_HQ_fraction','parent_measured_valid',
          'log_available_crop_mean','available_crop_breadth','log_available_crop_perbase_variance','available_crop_HQ_fraction','log_across_crop_mean_dispersion','available_crop_fraction'],
        parent_is_not_window=True,truth_accessed=False,frozen_bootstrap_priors_retained=True)
    arrays=dict(ids=ids,eligible=eligible,bootstrap=b['features'],local=x,physical_one=one,physical_two=two,similarity=similarity,active=active,edges=e,edge_weights=w,
        composition=data['tnf'].astype(np.float32),depth=measured[:,:len(meta['samples'])].copy())
    # The first measured block is exactly log1p(parent mean), for every row.
    save_arrays(output/'features.npz',arrays,receipt);return receipt


class Encoder(nn.Module):
    """Fuse explicit local/physical/similarity branches into a bounded residual."""
    def __init__(self,dimensions,embedding,depth):
        super().__init__();h=DEFAULT['hidden']
        branch=lambda d:nn.Sequential(nn.Linear(d,h),nn.LayerNorm(h),nn.GELU())
        self.local=branch(dimensions);self.physical=branch(2*dimensions);self.similarity=branch(embedding)
        self.residual=nn.Linear(3*h,embedding,bias=False);nn.init.zeros_(self.residual.weight)
        self.composition_decoder=nn.Linear(embedding,136);self.depth_decoder=nn.Linear(embedding,depth) if depth else None

    def forward(self,base,local,one,two,similarity,active):
        """Preserve inactive vectors bit-for-bit; update only physical-link nodes."""
        hidden=torch.cat([self.local(local),self.physical(torch.cat([one,two],1)),self.similarity(similarity)],1)
        changed=F.normalize(base+torch.tanh(self.residual(hidden)),dim=1)
        return torch.where(active[:,None],changed,base)


def train(cache_path,output,threads=4,engineering_epochs=None):
    """Fit only the new small graph model; preserve old modules/vectors unchanged."""
    from ..model import configure_torch
    from ..multiview.positive import geometry
    cfg=policy();
    from threadpoolctl import threadpool_limits
    threadpool_limits(threads);configure_torch(threads);torch.manual_seed(cfg['seed']);a,m=load_arrays(cache_path,'genome_graph_features')
    n=len(a['ids']);epochs=cfg['epochs'] if engineering_epochs is None else engineering_epochs
    if engineering_epochs is not None and (n>128 or not 1<=epochs<=20):raise ValueError('Tiny graph epoch override exceeds engineering scope')
    ix=np.flatnonzero(a['active']&a['eligible'])
    if len(ix)<2 or len(a['edges'])<1:raise ValueError('Graph utility admission missing; do not fit empty links')
    if (np.linalg.norm(a['bootstrap'][a['edges'][:,0]]+a['bootstrap'][a['edges'][:,1]],axis=1)<1e-6).any():
        raise ValueError('Antipodal bootstrap endpoint prototype is numerically undefined')
    output=Path(output);output.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    model=Encoder(a['local'].shape[1],a['bootstrap'].shape[1],a['depth'].shape[1]);optimizer=torch.optim.AdamW(model.parameters(),lr=cfg['learning_rate'],weight_decay=cfg['weight_decay'])
    tensors={k:torch.from_numpy(a[k]) for k in ['bootstrap','local','physical_one','physical_two','similarity','active','composition','depth']}
    def forward(rows):return model(*(tensors[k][rows] for k in ['bootstrap','local','physical_one','physical_two','similarity','active']))
    rng=np.random.default_rng(cfg['seed']);history=[]
    for epoch in range(epochs):
        order=rng.permutation(len(a['edges']));sums=np.zeros(5);seen=0
        for at in range(0,len(order),cfg['batch_size']):
            selected=order[at:at+cfg['batch_size']];edges=a['edges'][selected];rows=np.unique(edges);positions=np.searchsorted(rows,edges)
            z=forward(rows);weight=torch.from_numpy(a['edge_weights'][selected].astype(np.float32));left=z[positions[:,0]];right=z[positions[:,1]]
            prototype=F.normalize((tensors['bootstrap'][edges[:,0]]+tensors['bootstrap'][edges[:,1]]).detach(),dim=1)
            alignment=(((1-(left*prototype).sum(1).clamp(-1,1))+(1-(right*prototype).sum(1).clamp(-1,1)))*.5*weight).sum()/weight.sum()
            anchor=(1-(z*tensors['bootstrap'][rows]).sum(1).clamp(-1,1)).mean()
            comp=F.mse_loss(model.composition_decoder(z),tensors['composition'][rows])
            dep=F.mse_loss(model.depth_decoder(z),tensors['depth'][rows]) if model.depth_decoder is not None else z.sum()*0
            loss=alignment+cfg['anchor_weight']*anchor+cfg['composition_reconstruction_weight']*comp+cfg['depth_reconstruction_weight']*dep
            if not torch.isfinite(loss):raise ValueError('Nonfinite graph learning loss')
            optimizer.zero_grad(set_to_none=True);loss.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in model.parameters()):raise ValueError('Nonfinite graph gradient')
            optimizer.step();sums+=np.array([loss.item(),alignment.item(),anchor.item(),comp.item(),dep.item()])*len(selected);seen+=len(selected)
        model.eval();values=[]
        with torch.no_grad():
            for at in range(0,min(len(ix),8192),1024):values.append(forward(ix[at:at+1024]).numpy())
        sample=np.concatenate(values);g=geometry(sample,dict(collapse_min_std=.001,collapse_min_rank=2),enforce=False)
        if g['catastrophic_collapse']:raise ValueError('Graph representation collapse; history preserved')
        row=dict(epoch=epoch+1,edges_seen=seen,active_rows=len(ix),loss=float(sums[0]/seen),link_loss=float(sums[1]/seen),anchor_loss=float(sums[2]/seen),composition_loss=float(sums[3]/seen),measured_parent_depth_loss=float(sums[4]/seen),geometry=g)
        history.append(row);write_json(output/('epoch-%02d.json'%(epoch+1)),row);emit('genome_graph_epoch',**row);model.train()
    model.eval();vectors=a['bootstrap'].copy()
    with torch.no_grad():
        for at in range(0,len(ix),1024):vectors[ix[at:at+1024]]=forward(ix[at:at+1024]).numpy()
    saved=dict(state=model.state_dict(),optimizer=optimizer.state_dict(),policy=cfg,cache=binding(cache_path),dimensions=a['local'].shape[1],embedding=a['bootstrap'].shape[1],depth=a['depth'].shape[1])
    torch.save(saved,output/'checkpoint.pt');copy_model=Encoder(saved['dimensions'],saved['embedding'],saved['depth']);copy_model.load_state_dict(torch.load(output/'checkpoint.pt',map_location='cpu',weights_only=True)['state']);copy_model.eval()
    with torch.no_grad():
        for at in range(0,len(ix),1024):
            rows=ix[at:at+1024];reloaded=copy_model(*(tensors[k][rows] for k in ['bootstrap','local','physical_one','physical_two','similarity','active'])).numpy()
            if not np.array_equal(reloaded,vectors[rows]):raise ValueError('Native graph reload is not exact')
    if not np.array_equal(vectors[~a['active']],a['bootstrap'][~a['active']]):raise ValueError('Unlinked bootstrap fallback changed')
    if not np.allclose(np.linalg.norm(vectors[a['eligible']],axis=1),1,rtol=0,atol=1e-6):raise ValueError('Graph inference unit geometry differs')
    save_arrays(output/'embeddings.npz',dict(ids=a['ids'],features=vectors,evidence=a['eligible']),dict(kind='embeddings',mode='physical_graph_unit_sphere',features_sha256=m['inputs']['features']['sha256'],metric='unit-sphere cosine/equivalent Euclidean; no post-learning transform',checkpoint_sha256=binding(output/'checkpoint.pt')['sha256'],reload_exact=True))
    receipt=dict(status='PASS',policy=cfg,cache=binding(cache_path),checkpoint=binding(output/'checkpoint.pt'),history=history,wall_seconds=time.monotonic()-start,engineering_epochs=engineering_epochs,
        old_encoder_refit=False,bootstrap_unchanged=True,truth_accessed=False,reload_exact=True)
    write_json(output/'completed.json',receipt);return receipt
