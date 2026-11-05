"""Bootstrap-preserving multiscale coverage fusion with exact parent/crop views.

The retained composition/context/optional-GLM encoder and optimizer are restored.
All new parent-depth inputs use one new measurement; genuine window moments enter
an explicit reliability-weighted residual. No truth is accepted by this API.
"""
import copy
import json
import math
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from ..bootstrap import model as preserved
from ..candidate.model import transform
from ..context.tokens import binding
from ..io import digest, emit, save_arrays, write_json
from ..model import batches, configure_torch
from ..multiview.arrays import load_arrays
from ..multiview.model import parent_average
from ..multiview.positive import pair_loss, update_target, geometry
from ..multiview.views import load
from ..relational import model as inherited
from ..relational.evidence import require
from ..relational.pairs import policy as side_policy
from .cache import Bank

POLICY=dict(version=1,seed=11,epochs=20,batch_size=256,learning_rate=.0002,
    anchor_weight=.1,cell_hidden=16,coverage_hidden=64,cell_dimensions=12,
    initialization='restore_E031_online_EMA_predictor_Adam_append_new_slots',
    parent_transform='refit_only_depth_on_new_eligible_parents',
    residual='zero_output_unit_sphere',reconstruction='retain_composition_1_depth_point1_actual_window_means',
    positive_views='full_parent_and_every_available_real_crop',original_pair_slot_denominator=True)


def policy(value=None):
    """Require exact candidate defaults; engineering epoch override is separate."""
    value=POLICY if value is None else value
    require(value==POLICY and all(type(value[k]) is type(v) for k,v in POLICY.items()),'Unfrozen multiscale learning policy')
    return dict(value)


class Encoder(nn.Module):
    """Preserve base modules and add small ordered-sample reliability-aware fusion."""
    def __init__(self,base,samples,cfg):
        super().__init__();self.base=base;self.samples=samples
        self.cell=nn.Sequential(nn.Linear(12,16),nn.GELU(),nn.Linear(16,16),nn.GELU())
        self.coverage=nn.Sequential(nn.Linear(samples*16,64),nn.LayerNorm(64),nn.GELU())
        self.residual=nn.Linear(64,cfg['output'],bias=False);nn.init.zeros_(self.residual.weight)
        self.coverage_decoder=nn.Linear(cfg['output'],samples)

    def forward(self,*args):
        """Return fused and sequence unit vectors, with cleared missing/dropout cells."""
        base_args=args[:-2];cells,weight=args[-2:]
        require(cells.shape==(len(cells),self.samples,12) and weight.shape==cells.shape[:2]
            and torch.isfinite(cells).all() and torch.isfinite(weight).all()
            and bool(((weight>=0)&(weight<=1)).all()),'Invalid measured coverage axes/weights')
        fused,seq=self.base(*base_args)
        hidden=self.cell(cells)*weight[:,:,None]
        value=self.coverage(hidden.flatten(1))
        # A missing/all-zero branch cannot leak LayerNorm/MLP bias. Positive vs
        # zero patterns remain explicit where another sample supplies support.
        row=weight.max(1).values[:,None]
        return F.normalize(fused+row*self.residual(value),dim=1),seq


def read_original(path,features,views,tokens,frozen):
    """Bind exact retained E031 state and original DNA/token/GLM provenance."""
    path=Path(path);receipt=json.loads(path.with_suffix('.json').read_text())
    require(receipt['sha256']==digest(path),'Retained E031 checkpoint bytes differ')
    saved=torch.load(path,map_location='cpu',weights_only=True)
    require(saved.get('kind')=='bootstrap_continuation_checkpoint' and saved.get('version')==1,
            'Expected admitted E031 continuation checkpoint')
    for key in ['config','transform','samples','inputs','inherited_updates','added_updates']:
        require(saved[key]==receipt[key],'Retained E031 checkpoint receipt differs')
    source=saved['inputs']
    require(source['features']==binding(features) and source['views']==binding(views)
        and source['tokens']==binding(Path(tokens)/'tokens.json')
        and source['frozen']==(binding(Path(frozen)/'bank.json') if frozen else None),
        'Retained bootstrap DNA/view/token/GLM input differs')
    require(saved['config']['seed']==11 and saved['config']['epochs']==20
        and saved['config']['batch_size']==256 and saved['config']['composition_reconstruction_weight']==1.
        and saved['config']['depth_reconstruction_weight']==.1 and len(receipt['history'])==20,
        'Unadmitted retained E031 schedule/reconstruction')
    require(('hybrid' in saved['config'])==(frozen is not None),'GLM information path differs')
    saved['ema_updates']=saved['inherited_updates']+saved['added_updates']
    return saved,receipt


def initialize(saved):
    """Copy every old state/buffer/Adam slot; append initially absent new slots."""
    base,target,predictors,anchor,optimizer=preserved.initialize(saved)
    before={n:preserved.state_digest(x) for n,x in [('online',base),('target',target),('predictor',predictors)]}
    # Independent module initialization does not change inherited RNG consumption.
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(11);model=Encoder(base,len(saved['samples']),saved['config'])
    stopped=copy.deepcopy(model);stopped.base=target;stopped.requires_grad_(False).eval()
    new=[p for name,p in model.named_parameters() if not name.startswith('base.')]
    optimizer.add_param_group(dict(params=new,lr=.0002,weight_decay=saved['config']['weight_decay']))
    require(before['online']==preserved.state_digest(model.base) and before['target']==preserved.state_digest(stopped.base)
        and before['predictor']==preserved.state_digest(predictors),'Inherited state changed during extension')
    require(all(p not in optimizer.state for p in new),'New Adam slots must begin absent')
    return model,stopped,predictors,anchor,optimizer


def args(sequence,depth,mask,bank,coverage,selected,view_numbers,state,cfg,coverage_state,drop=None):
    """Create one batch with new measured parent means and exact crop moments."""
    keep=mask.copy()
    if drop is not None:keep&=~drop
    values=inherited.forward_args(sequence,depth,keep,bank,selected,view_numbers,state,cfg)
    cells,weights=coverage.batch(selected,view_numbers,coverage_state,drop)
    return values+[torch.from_numpy(cells),torch.from_numpy(weights)]


def transformed(data,new_data,state):
    """Apply retained composition transform and prospectively fitted shared depth."""
    return transform(data['tnf'],new_data['depth'],new_data['depth_evidence'],state)


def infer(model,data,new_data,state,cfg,bank,coverage,coverage_state,sequence=None):
    """Infer all eligible parents in exactly the training/grouping unit geometry."""
    s,d=transformed(data,new_data,state) if sequence is None else sequence
    result=np.zeros((len(s),cfg['output']),np.float32);valid=np.zeros(len(s),bool)
    model.eval()
    with torch.inference_mode():
        for ix in batches(np.flatnonzero(data['eligible']),cfg['context']['context_inference_batch_size']):
            a=args(s[ix],d[ix],new_data['depth_evidence'][ix],bank,coverage,ix,np.zeros(len(ix),np.int64),state,cfg,coverage_state)
            z=model(*a)[0].numpy();result[ix]=z;valid[ix]=np.linalg.norm(z,axis=1)>1e-12
    require(np.isfinite(result).all() and np.allclose(np.linalg.norm(result[valid],axis=1),1,rtol=0,atol=1e-6),
        'Invalid multiscale inference unit geometry')
    return result,valid


def monitor(model,target,data,new_data,state,cfg,bank,coverage,coverage_state,sequence):
    """Keep unchanged fixed-parent collapse thresholds, separately for both heads."""
    rows=np.flatnonzero(data['eligible']);rows=rows[np.linspace(0,len(rows)-1,min(len(rows),cfg['collapse_rows']),dtype=int)]
    result={}
    for name,module in [('online',model),('target',target)]:
        module.eval();pieces=[[],[]]
        with torch.inference_mode():
            for ix in batches(rows,cfg['context']['context_inference_batch_size']):
                a=args(sequence[0][ix],sequence[1][ix],new_data['depth_evidence'][ix],bank,coverage,ix,np.zeros(len(ix),np.int64),state,cfg,coverage_state)
                for i,z in enumerate(module(*a)):pieces[i].append(z.numpy())
        result[name]={label:geometry(np.concatenate(pieces[i]),cfg,enforce=False) for i,label in enumerate(['fused','sequence'])}
    return result


def inputs(features,new_features,views,tokens,frozen,measurements,original,pairs):
    """Bind every consumed manifest, excluding all truth/source-origin joins."""
    return dict(original_features=binding(features),new_features=binding(new_features),views=binding(views),
        tokens=binding(Path(tokens)/'tokens.json'),frozen=binding(Path(frozen)/'bank.json') if frozen else None,
        measurements=binding(Path(measurements)/'bank.json'),original=binding(original),
        original_metadata=binding(Path(original).with_suffix('.json')),
        pairs=binding(Path(pairs)/'cache.json') if pairs else None)


def train(features,new_features,views,tokens,frozen,measurements,original,output,
          teacher=None,pairs=None,threads=4,engineering_epochs=None):
    """Adapt one own teacher, or continue it with fresh measured signed proposals.

    Both stages preserve full available-positive exposure and strict native reload.
    Engineering schedules are <=20 epochs and tiny axes only; no fallback to a new
    fit or generated cache exists when an original byte contract fails.
    """
    configure_torch(threads);policy();source,_=read_original(original,features,views,tokens,frozen)
    data,meta,v,vm=load(features,views);new_data,new_meta=load(new_features)
    require(np.array_equal(data['ids'],new_data['ids']) and meta['samples']==new_meta['samples']
        and np.array_equal(data['sequence_sha256'],new_data['sequence_sha256'])
        and all(np.array_equal(data[k],new_data[k]) for k in data if k not in ['depth','zero_depth','depth_evidence']),
        'Original/new measured DNA or sample axis differs')
    cfg=source['config'];coverage=Bank(measurements,features,views,data,v)
    require(coverage.meta['all_samples_measured'],'Learning requires complete measured samples')
    require(new_meta.get('measured_bank')==binding(Path(measurements)/'bank.json')
        and new_meta.get('prior_features')==binding(features),'Unadmitted parent-depth replacement')
    bank=inherited.make_bank(tokens,frozen,features,views,data,meta,v,cfg)
    epochs=20 if engineering_epochs is None else engineering_epochs
    require(type(epochs) is int and 1<=epochs<=20 and (engineering_epochs is None or len(data['ids'])<=128),
        'Engineering exposure exceeds tiny scope')
    model,target,predictors,anchor,optimizer=initialize(source)
    state=copy.deepcopy(source['transform']);x=np.log1p(new_data['depth'][data['eligible']].astype(np.float64))
    state['depth']=dict(mean=x.mean(0).tolist(),std=x.std(0).tolist())
    coverage_state=coverage.fit();links=None;link_receipt=None;past_updates=source['ema_updates']
    if (teacher is None)!=(pairs is None):raise ValueError('Student needs its exact teacher and fresh pairs together')
    if teacher is not None:
        saved,receipt=read_candidate(teacher)
        expected=inputs(features,new_features,views,tokens,frozen,measurements,original,None)
        require(saved['inputs']==expected and saved['stage']=='teacher','Student does not own this exact teacher')
        for module,key in [(model,'model_state'),(target,'target_state'),(predictors,'predictor_state'),(anchor,'anchor_state')]:
            module.load_state_dict(saved[key],strict=True)
        optimizer.load_state_dict(saved['optimizer_state']);state=saved['transform'];coverage_state=saved['coverage_transform']
        past_updates=saved['total_updates']
        from .pairs import read
        links,link_receipt=read(pairs,new_features)
        require(link_receipt['own_teacher_checkpoint_sha256']==digest(teacher)
            and link_receipt['own_teacher_reload_exact'],'Fresh proposals do not own the adapted teacher')
    bound=inputs(features,new_features,views,tokens,frozen,measurements,original,pairs)
    sequence=transformed(data,new_data,state);parent,depth=sequence
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    initial={n:preserved.state_digest(m) for n,m in [('online',model),('target',target),('predictor',predictors),('anchor',anchor)]}
    write_json(out/'initial-state.json',dict(state=initial,inputs=bound,policy=policy(),stage='student' if teacher else 'teacher'))
    indices=np.flatnonzero(data['eligible']);require(len(indices)>=2,'At least two training parents required')
    weights_np=np.log1p(np.minimum(data['lengths'],10000)/500).astype(np.float32)
    torch.manual_seed(11);rng=np.random.default_rng(11);steps=epochs*math.ceil(len(indices)/256)
    updates=0;history=[];start=time.monotonic();cpu=time.process_time()
    slot_to_kept=None
    if links is not None:
        slot_to_kept=np.full(link_receipt['source_pair_count'],-1,np.int64)
        slot_to_kept[links['source_index']]=np.arange(len(links['left']))
    for epoch in range(epochs):
        model.train();predictors.train();seen=anchors=dropped=exposed=proposed=0;totals=np.zeros(8)
        pieces=inherited.pair_epoch(link_receipt['source_pair_count'],math.ceil(len(indices)/256),side_policy(),epoch) if links is not None else None
        for at,ix in enumerate(batches(rng.permutation(indices),256)):
            n=len(ix);real=[parent[ix]]+[transform(v['tnf'][ix,j],new_data['depth'][ix],new_data['depth_evidence'][ix],state)[0] for j in range(4)]
            available=np.concatenate([np.ones(n,bool)]+[v['usable'][ix,j] for j in range(4)])
            owners_np=np.tile(np.arange(n),5)[available];owners=torch.from_numpy(owners_np)
            view_numbers=np.repeat(np.arange(5),n)[available];rows=np.tile(ix,5)[available]
            s=np.concatenate(real)[available];d=depth[rows];mask=new_data['depth_evidence'][rows]
            drop=rng.random(len(rows))<cfg['depth_dropout'];dropped+=int((mask&drop).sum())
            a=args(s,d,mask,bank,coverage,rows,view_numbers,state,cfg,coverage_state,drop)
            fused,seq=model(*a)
            with torch.no_grad():tf,ts=target(*a)
            weights=torch.from_numpy(weights_np[ix]);pf=pair_loss(fused,tf,owners,weights,predictors[0]);ps=pair_loss(seq,ts,owners,weights,predictors[1])
            wanted=torch.from_numpy(parent[ix])[owners]
            rc=parent_average(((F.normalize(model.base.composition_decoder(fused),dim=1)-wanted).square().sum(1)
                +(F.normalize(model.base.composition_decoder(seq),dim=1)-wanted).square().sum(1))*.5,owners,weights)
            stats,valid=coverage.statistics(rows,view_numbers)
            desired=torch.from_numpy((np.log1p(stats[:,:,0])/np.asarray(coverage_state['parent_log_median_scale'])).astype(np.float32))
            keep=torch.from_numpy(valid);pred=model.coverage_decoder(fused)
            dl=F.smooth_l1_loss(pred,desired,reduction='none')*keep
            # Fully observed zeros are reconstruction targets. Missing channels
            # cannot supply a target, nor change the count of a parent's views.
            per_view=dl.sum(1)/keep.sum(1).clamp_min(1)
            rd=parent_average(per_view,owners,weights)
            parent_args=args(parent[ix],depth[ix],new_data['depth_evidence'][ix],bank,coverage,ix,np.zeros(n,np.int64),state,cfg,coverage_state)
            online=preserved.preserved_forward(model,parent_args)
            fixed=preserved.preserved_forward(anchor,parent_args[:-2],True)
            preservation=sum(scale*(((u-z.detach()).square().sum(1)*weights).sum()/weights.sum()) for scale,u,z in zip((1/1.5,.5/1.5),online,fixed))
            rp=rn=fused.sum()*0;coefficient=0.
            if links is not None:
                source_rows=pieces[at];chosen=slot_to_kept[source_rows];chosen=chosen[chosen>=0]
                coefficient=inherited.coefficient(side_policy(),epoch);proposed+=len(source_rows);exposed+=len(chosen)
                if len(chosen):
                    endpoints=np.column_stack([links['left'][chosen],links['right'][chosen]]).ravel()
                    side=args(parent[endpoints],depth[endpoints],new_data['depth_evidence'][endpoints],bank,coverage,endpoints,np.zeros(len(endpoints),np.int64),state,cfg,coverage_state)
                    online=[x.reshape(len(chosen),2,-1) for x in preserved.preserved_forward(model,side)]
                    stopped=[x.reshape(len(chosen),2,-1) for x in preserved.preserved_forward(target,side,True)]
                    modes=[(m,m.training) for m in predictors.modules()]
                    try:
                        predictors.eval()
                        with torch.random.fork_rng(devices=[]):
                            raw=inherited.signed_loss(online,stopped,predictors,torch.from_numpy(links['sign'][chosen]),torch.from_numpy(links['weight'][chosen]),side_policy()['negative_cosine_margin'])
                    finally:
                        for m,mode in modes:m.training=mode
                    rp,rn=preserved.attenuate(raw,len(chosen),len(source_rows))
            loss=pf+cfg['sequence_loss_weight']*ps+cfg['composition_reconstruction_weight']*rc+cfg['depth_reconstruction_weight']*rd+preserved.weighted_relation(rp,rn,coefficient)+.1*preservation
            require(torch.isfinite(loss),'Nonfinite multiscale loss');optimizer.zero_grad(set_to_none=True);loss.backward()
            require(all(p.grad is None or torch.isfinite(p.grad).all() for g in optimizer.param_groups for p in g['params']),'Nonfinite multiscale gradient')
            require(all(p.grad is None for m in (target,anchor) for p in m.parameters()),'Stopped target/anchor received gradients')
            optimizer.step();tau=1-(1-cfg['ema_base'])*(1+math.cos(math.pi*updates/steps))/2;update_target(model,target,tau);updates+=1
            seen+=n;anchors+=len(rows);totals+=np.array([float(z.detach()) for z in [loss,pf,ps,rc,rd,rp,rn,preservation]])*n
            if (at+1)%64==0:emit('multiscale_training_progress',role='student' if teacher else 'teacher',epoch=epoch+1,optimizer_updates=updates,parents_seen_this_epoch=seen,total_parents=len(indices))
        require(seen==len(indices) and (links is None or (exposed==len(links['left']) and proposed==link_receipt['source_pair_count'])),'Incomplete parent/pair-slot exposure')
        g=monitor(model,target,data,new_data,state,cfg,bank,coverage,coverage_state,sequence)
        write_json(out/('geometry-%02d.json'%(epoch+1)),g)
        require(not any(x['catastrophic_collapse'] for heads in g.values() for x in heads.values()),'Catastrophic multiscale collapse; geometry retained')
        h=dict(epoch=epoch+1,parents_seen=seen,available_views=anchors,depth_dropped_views=dropped,
            accepted_pairs=exposed,original_pair_slots=proposed,ema_updates=updates,last_tau=tau,
            geometry=g,**dict(zip(['loss','fused_positive','sequence_positive','composition_reconstruction','measured_depth_reconstruction','relation_positive','relation_negative','anchor_preservation'],(totals/seen).tolist())))
        history.append(h);emit('multiscale_epoch',**h)
    require(preserved.state_digest(anchor)==initial['anchor'],'Fixed bootstrap anchor changed')
    require(bound==inputs(features,new_features,views,tokens,frozen,measurements,original,pairs),'Multiscale input manifests changed')
    values,valid=infer(model,data,new_data,state,cfg,bank,coverage,coverage_state,sequence)
    saved=dict(kind='multiscale_checkpoint',version=1,policy=policy(),stage='student' if teacher else 'teacher',
        config=cfg,transform=state,coverage_transform=coverage_state,samples=meta['samples'],inputs=bound,
        model_state=model.state_dict(),target_state=target.state_dict(),predictor_state=predictors.state_dict(),
        anchor_state=anchor.state_dict(),optimizer_state=optimizer.state_dict(),total_updates=past_updates+updates,
        added_updates=updates,teacher_checkpoint=binding(teacher) if teacher else None,
        torch_rng_state=torch.get_rng_state(),numpy_rng_state=rng.bit_generator.state)
    with (out/'checkpoint.pt').open('xb') as f:torch.save(saved,f)
    write_json(out/'checkpoint.json',{k:saved[k] for k in ['kind','version','policy','stage','config','transform','coverage_transform','samples','inputs','total_updates','added_updates','teacher_checkpoint']}|
        dict(sha256=digest(out/'checkpoint.pt'),history=history,initial_state=initial,
            final_state={n:preserved.state_digest(m) for n,m in [('online',model),('target',target),('predictor',predictors),('anchor',anchor)]},
            wall_seconds=time.monotonic()-start,process_cpu_seconds=time.process_time()-cpu,threads=threads,loader_workers=0,
            original_Adam_restored=True,truth_accessed=False,engineering_epochs=engineering_epochs))
    save_arrays(out/'reference.npz',dict(ids=data['ids'],features=values,evidence=valid),
        dict(kind='embeddings',mode='multiscale_reference',samples=meta['samples'],features_sha256=digest(new_features),checkpoint_sha256=digest(out/'checkpoint.pt')))


def read_candidate(path):
    """Verify strict model receipt/source schema, preserving failures without fallback."""
    path=Path(path);r=json.loads(path.with_suffix('.json').read_text())
    require(r['sha256']==digest(path),'Multiscale checkpoint hash differs')
    saved=torch.load(path,map_location='cpu',weights_only=True)
    require(saved.get('kind')=='multiscale_checkpoint' and saved.get('version')==1,'Unsupported multiscale checkpoint')
    policy(saved['policy'])
    for key in ['policy','stage','config','transform','coverage_transform','samples','inputs','total_updates','added_updates','teacher_checkpoint']:
        require(saved[key]==r[key],'Multiscale checkpoint receipt differs')
    return saved,r


def embed(features,new_features,views,tokens,frozen,measurements,original,checkpoint,output,pairs=None,threads=4):
    """Reload every tensor/buffer and require exact same-runtime reference equality."""
    configure_torch(threads);saved,r=read_candidate(checkpoint)
    require(saved['inputs']==inputs(features,new_features,views,tokens,frozen,measurements,original,pairs),'Multiscale reload input differs')
    source,_=read_original(original,features,views,tokens,frozen);model,target,predictors,anchor,optimizer=initialize(source)
    for module,key,name in [(model,'model_state','online'),(target,'target_state','target'),(predictors,'predictor_state','predictor'),(anchor,'anchor_state','anchor')]:
        module.load_state_dict(saved[key],strict=True);require(preserved.state_digest(module)==r['final_state'][name],'Reload module/buffer differs')
    optimizer.load_state_dict(saved['optimizer_state'])
    data,meta,v,_=load(features,views);new_data,_=load(new_features)
    bank=inherited.make_bank(tokens,frozen,features,views,data,meta,v,saved['config']);coverage=Bank(measurements,features,views,data,v)
    z,valid=infer(model,data,new_data,saved['transform'],saved['config'],bank,coverage,saved['coverage_transform'])
    ref,_=load_arrays(Path(checkpoint).parent/'reference.npz','embeddings')
    require(np.array_equal(z,ref['features']) and np.array_equal(valid,ref['evidence']) and np.array_equal(data['ids'],ref['ids']),'Exact same-runtime multiscale reload differs')
    save_arrays(output,dict(ids=data['ids'],features=z,evidence=valid),dict(kind='embeddings',mode='multiscale_unit_sphere',
        features_sha256=digest(new_features),samples=meta['samples'],checkpoint_sha256=digest(checkpoint),reload_exact=True,
        metric='unit-sphere cosine/equivalent Euclidean; no post-learning transform'))
