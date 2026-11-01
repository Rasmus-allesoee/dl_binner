"""Bootstrap-preserving continuation with an immutable anchor and cautious pairs.

The inherited self-view arithmetic and encoder topology are retained. Loading
bootstrap state, conservative cross-parent supervision and a soft fixed-teacher
penalty form one declared bundle, not a pure marker-loss ablation. This module
reads only feature/view/token/GLM/pair/checkpoint artifacts, never sequence truth.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
import torch
from torch.nn import functional as F

from ..candidate.model import transform
from ..context.tokens import binding
from ..io import digest, emit, save_arrays, write_json
from ..model import batches, configure_torch
from ..multiview.arrays import load_arrays
from ..multiview.model import parent_average
from ..multiview.positive import pair_loss, update_target, validate_policy
from ..multiview.views import load
from ..relational import model as inherited
from ..relational.evidence import require
from ..relational.pairs import policy as side_policy
from .pairs import read as read_pairs


def policy(value=None):
    """Freeze one continuation schedule; no truth-selected loss or learning rate."""
    default = dict(version=1, learning_rate=0.0002, anchor_weight=0.1,
                   epochs=20, seed=11, optimizer='restore_AdamW_moments_and_steps',
                   online='bootstrap_online', ema='bootstrap_stopped_target',
                   predictor='bootstrap_predictor', anchor='fixed_bootstrap_online_eval',
                   rng='fresh_seed11_continuation_not_interrupted_resume')
    cfg = default if value is None else value
    require(isinstance(cfg,dict) and cfg == default and
            all(type(cfg[k]) is type(v) for k,v in default.items()), 'Unfrozen bootstrap continuation policy')
    return dict(cfg)


def state_digest(module):
    """Hash named tensor dtype/shape/content, including non-parameter buffers."""
    result = hashlib.sha256()
    for name, value in module.state_dict().items():
        x = value.detach().cpu().contiguous()
        result.update(json.dumps([name,str(x.dtype),list(x.shape)]).encode())
        result.update(x.numpy().tobytes())
    return result.hexdigest()


def read_bootstrap(checkpoint, features, views, tokens, frozen):
    """Validate the exact producer schema, inputs, modality and stopped-state bytes."""
    path = Path(checkpoint); receipt = json.loads(path.with_suffix('.json').read_text())
    require(receipt['sha256'] == digest(path), 'Bootstrap checkpoint bytes differ')
    saved = torch.load(path, map_location='cpu', weights_only=True)
    require(saved.get('kind') == ('hybrid_checkpoint' if frozen is not None else 'context_checkpoint')
            and saved.get('version') == 1, 'Not an admitted bootstrap checkpoint')
    keys = ['kind','version','config','transform','samples','ema_updates',
            'training_features_sha256','training_views_sha256','training_tokens_sha256']
    if frozen is not None: keys.append('training_frozen_sha256')
    require(all(saved[k] == receipt[k] for k in keys), 'Bootstrap checkpoint/receipt schema differs')
    require(saved['training_features_sha256'] == digest(features) and
            saved['training_views_sha256'] == digest(views) and
            saved['training_tokens_sha256'] == digest(Path(tokens)/'tokens.json') and
            saved.get('training_frozen_sha256') == (digest(Path(frozen)/'bank.json') if frozen is not None else None),
            'Bootstrap feature/view/token/GLM input differs')
    data, meta, v, vm = load(features,views)
    cfg = saved['config']
    validate_policy({k:x for k,x in cfg.items() if k not in ('context','hybrid')},vm['policy'])
    from ..context.tokens import policy as context_policy
    from ..hybrid.bank import policy as hybrid_policy
    require(cfg['context'] == context_policy() and ('hybrid' in cfg) == (frozen is not None) and
            (frozen is None or cfg['hybrid'] == hybrid_policy()) and saved['samples'] == meta['samples'] and
            cfg['seed'] == 11 and cfg['batch_size'] == 256 and cfg['epochs'] == 20 and
            len(receipt['history']) == 20 and saved['ema_updates'] == 20*math.ceil(int(data['eligible'].sum())/256),
            'Bootstrap source/default/sample/exposure contract differs')
    require(all(h['parents_seen'] == int(data['eligible'].sum()) and
                all(not g['catastrophic_collapse'] for m in h['geometry'].values() for g in m.values())
                for h in receipt['history']), 'Bootstrap history/collapse contract differs')
    return saved, data, meta, v, vm


def initialize(saved):
    """Restore online/EMA/predictors, optimizer moments and a separate frozen anchor.

    Construction uses the unchanged seed-11 topology. Original RNG is unavailable,
    so the continuation deliberately starts a new documented stream after restore.
    No bootstrap weight, predictor buffer or Adam step is reinitialized silently.
    """
    cfg = saved['config']; torch.manual_seed(policy()['seed'])
    model, target, predictors = inherited.initialize(len(saved['samples']),cfg)
    for module,key in ((model,'model_state'),(target,'target_state'),(predictors,'predictor_state')):
        module.load_state_dict(saved[key],strict=True)
        require(all(torch.isfinite(x).all() for x in module.state_dict().values()), 'Nonfinite bootstrap state')
    optimizer = torch.optim.AdamW(list(model.parameters())+list(predictors.parameters()),
                                 lr=cfg['learning_rate'],weight_decay=cfg['weight_decay'])
    optimizer.load_state_dict(saved['optimizer_state'])
    require(len(optimizer.param_groups) == 1 and optimizer.state, 'Missing/incompatible bootstrap optimizer state')
    for group in optimizer.param_groups:
        require(group['weight_decay'] == cfg['weight_decay'], 'Bootstrap optimizer defaults differ')
        for parameter in group['params']:
            # Adam creates state lazily. An unexercised decoder can legitimately
            # have no moments; preserve that absence rather than manufacturing
            # zero state. Original bytes are independently admitted by the caller.
            s = optimizer.state.get(parameter)
            if not s: continue
            require(set(s) == {'step','exp_avg','exp_avg_sq'} and
                    s['exp_avg'].shape == s['exp_avg_sq'].shape == parameter.shape and
                    all(torch.isfinite(x).all() for x in s.values()) and
                    s['step'].ndim == 0 and 1 <= float(s['step']) <= saved['ema_updates'] and
                    float(s['step']).is_integer(),
                    'Bootstrap Adam moments/step contract differs')
        group['lr'] = policy()['learning_rate']
    anchor = copy.deepcopy(model).requires_grad_(False).eval()
    torch.manual_seed(policy()['seed'])
    return model, target, predictors, anchor, optimizer


def preserved_forward(module, args, stopped=False):
    """Evaluate without changing any module modes, buffers or the global RNG stream."""
    modes = [(m,m.training) for m in module.modules()]
    try:
        module.eval()
        with torch.random.fork_rng(devices=[]):
            if stopped:
                with torch.no_grad(): return module(*args)
            return module(*args)
    finally:
        for m, mode in modes: m.training = mode


def anchor_loss(model, anchor, args, weights):
    """Penalize unit-head drift on full parents, leaving bootstrap/EMA independent."""
    online = preserved_forward(model,args)
    fixed = preserved_forward(anchor,args,True)
    return sum(scale*(((x-y.detach()).square().sum(1)*weights).sum()/weights.sum())
               for scale,x,y in zip((1/1.5,.5/1.5),online,fixed))


def signed_forward(model, target, predictors, pairs, selected, transformed, data, state, cfg, bank):
    """Use guarded full-parent pairs with predictor buffers and RNG held fixed."""
    indices = np.column_stack([pairs['left'][selected],pairs['right'][selected]]).ravel()
    if not len(indices):
        zero = next(model.parameters()).sum()*0
        return zero,zero
    args = inherited.forward_args(transformed[0][indices],transformed[1][indices],np.zeros(len(indices),bool),
                                  bank,indices,np.zeros(len(indices),np.int64),state,cfg)
    online = [x.reshape(len(selected),2,-1) for x in preserved_forward(model,args)]
    stopped = [x.reshape(len(selected),2,-1) for x in preserved_forward(target,args,True)]
    modes = [(m,m.training) for m in predictors.modules()]
    try:
        predictors.eval()
        with torch.random.fork_rng(devices=[]):
            return inherited.signed_loss(online,stopped,predictors,torch.from_numpy(pairs['sign'][selected]),
                                         torch.from_numpy(pairs['weight'][selected]),side_policy()['negative_cosine_margin'])
    finally:
        for module, mode in modes: module.training = mode


def attenuate(losses,retained,proposed):
    """Keep original pair-slot denominators when weak constraints abstain."""
    require(type(retained) is int and type(proposed) is int and 0<=retained<=proposed,
            'Malformed retained/original proposal reduction')
    scale=retained/proposed if proposed else 0.
    return tuple(value*scale for value in losses)


def weighted_relation(positive,negative,coefficient):
    """A zero warmup coefficient must not create otherwise absent Adam gradients."""
    require(type(coefficient) in (int,float) and math.isfinite(coefficient) and 0<=coefficient<=.1,
            'Unfrozen signed coefficient')
    value=positive+negative
    return coefficient*value if coefficient else value.detach()*0


def inputs(features,views,tokens,frozen,pairs,bootstrap):
    """Bind every manifest consumed by a fit; bank readers verify underlying members."""
    return dict(features=binding(features),views=binding(views),view_metadata=binding(Path(views).with_suffix('.json')),
                tokens=binding(Path(tokens)/'tokens.json'),frozen=binding(Path(frozen)/'bank.json') if frozen else None,
                pairs=binding(Path(pairs)/'cache.json'),bootstrap=binding(bootstrap),
                bootstrap_metadata=binding(Path(bootstrap).with_suffix('.json')))


def train(features,views,tokens,frozen,pairs,bootstrap,output,threads=4):
    """Continue one admitted bootstrap for 20 epochs and save complete learning evidence."""
    configure_torch(threads); continuation = policy()
    saved,data,meta,v,vm = read_bootstrap(bootstrap,features,views,tokens,frozen)
    cfg = saved['config']; bank = inherited.make_bank(tokens,frozen,features,views,data,meta,v,cfg)
    links,link_receipt = read_pairs(pairs,features)
    require(link_receipt['own_teacher_checkpoint_sha256'] == digest(bootstrap) and
            link_receipt['own_teacher_reload_exact'],
            'Signed proposals are not from the admitted bootstrap online vectors')
    # Reference-array equality is also verified by native admission; embedding
    # container metadata may differ from reference.npz despite identical arrays.
    out = Path(output); out.mkdir(parents=True,exist_ok=False)
    bound = inputs(features,views,tokens,frozen,pairs,bootstrap)
    indices = np.flatnonzero(data['eligible']); state = copy.deepcopy(saved['transform'])
    parent,depth = transform(data['tnf'],data['depth'],data['depth_evidence'],state)
    model,target,predictors,anchor,optimizer = initialize(saved)
    initial_state = {n:state_digest(m) for n,m in [('online',model),('target',target),('predictor',predictors),('anchor',anchor)]}
    initial_rng = digest_bytes(torch.get_rng_state().numpy().tobytes())
    rng = np.random.default_rng(continuation['seed'])
    weights_np = np.log1p(np.minimum(data['lengths'],10000)/500).astype(np.float32)
    usable_depth = np.asarray(state['depth']['std']) > 1e-8
    epoch_steps = math.ceil(len(indices)/cfg['batch_size']); steps = cfg['epochs']*epoch_steps
    source_to_kept=np.full(link_receipt['source_pair_count'],-1,np.int64)
    source_to_kept[links['source_index']]=np.arange(len(links['left']))
    updates = 0; start,cpu = time.monotonic(),time.process_time(); history = []
    initial = inherited.monitor(model,target,data,(parent,depth),state,cfg,bank)
    write_json(out/'initial-state.json',dict(state=initial_state,rng_sha256=initial_rng,
        inherited_updates=saved['ema_updates'],continuation=continuation,inputs=bound,geometry=initial))
    for epoch in range(cfg['epochs']):
        model.train(); predictors.train(); seen = anchors = dropped = exposed = proposed_exposed = 0
        totals = np.zeros(8)
        pieces = inherited.pair_epoch(link_receipt['source_pair_count'],epoch_steps,side_policy(),epoch)
        coefficient = inherited.coefficient(side_policy(),epoch)
        for at,selected in enumerate(batches(rng.permutation(indices),cfg['batch_size'])):
            n = len(selected); s0,d0,m0 = parent[selected],depth[selected],data['depth_evidence'][selected]
            real = [s0]+[transform(v['tnf'][selected,j],data['depth'][selected],m0,state)[0] for j in range(4)]
            available = np.concatenate([np.ones(n,bool)]+[v['usable'][selected,j] for j in range(4)])
            owners_np = np.tile(np.arange(n),5)[available]
            view_numbers = np.repeat(np.arange(5),n)[available]; selected_views = np.tile(selected,5)[available]
            sequence = np.concatenate(real)[available]; original_mask = np.tile(m0,5)[available]
            observed_depth = np.tile(d0,(5,1))[available]
            mask = original_mask & (rng.random(len(owners_np)) >= cfg['depth_dropout'])
            dropped += int((original_mask & ~mask).sum())
            owners,weights = torch.from_numpy(owners_np),torch.from_numpy(weights_np[selected])
            args = inherited.forward_args(sequence,observed_depth,mask,bank,selected_views,view_numbers,state,cfg)
            fused,seq = model(*args)
            with torch.no_grad(): tf,ts = target(*args)
            pf = pair_loss(fused,tf,owners,weights,predictors[0]); ps = pair_loss(seq,ts,owners,weights,predictors[1])
            wanted = torch.from_numpy(s0)[owners]
            rf = (F.normalize(model.composition_decoder(fused),dim=1)-wanted).square().sum(1)
            rs = (F.normalize(model.composition_decoder(seq),dim=1)-wanted).square().sum(1)
            rc = parent_average((rf+rs)*.5,owners,weights); rd = fused.sum()*0
            has = torch.from_numpy(original_mask)
            if model.depth_decoder is not None and usable_depth.any() and has.any():
                predicted = model.depth_decoder(fused)[has][:,usable_depth]
                desired = torch.from_numpy(observed_depth)[has][:,usable_depth]
                rd = parent_average(F.smooth_l1_loss(predicted,desired,reduction='none').mean(1),owners[has],weights)
            chosen=source_to_kept[pieces[at]];chosen=chosen[chosen>=0]
            raw=signed_forward(model,target,predictors,links,chosen,(parent,depth),data,state,cfg,bank)
            rp,rn=attenuate(raw,len(chosen),len(pieces[at]))
            parent_args = inherited.forward_args(s0,d0,m0,bank,selected,np.zeros(n,np.int64),state,cfg)
            preservation = anchor_loss(model,anchor,parent_args,weights)
            loss = (pf+cfg['sequence_loss_weight']*ps+cfg['composition_reconstruction_weight']*rc+
                    cfg['depth_reconstruction_weight']*rd+weighted_relation(rp,rn,coefficient)+continuation['anchor_weight']*preservation)
            require(bool(torch.isfinite(loss)), 'Nonfinite bootstrap continuation loss')
            optimizer.zero_grad(set_to_none=True); loss.backward()
            require(all(p.grad is None or torch.isfinite(p.grad).all() for g in optimizer.param_groups for p in g['params']),
                    'Nonfinite bootstrap continuation gradient')
            require(all(p.grad is None for m in (target,anchor) for p in m.parameters()), 'Stopped bootstrap/EMA received gradients')
            optimizer.step()
            tau = 1-(1-cfg['ema_base'])*(1+math.cos(math.pi*updates/steps))/2
            update_target(model,target,tau); updates += 1
            seen += n; anchors += len(owners); exposed += len(chosen)
            proposed_exposed += len(pieces[at])
            totals += np.array([float(x.detach()) for x in (loss,pf,ps,rc,rd,rp,rn,preservation)])*n
        require(seen == len(indices) and exposed == len(links['left']) and proposed_exposed==link_receipt['source_pair_count'],
                'Continuation parent/pair exposure differs')
        observed = inherited.monitor(model,target,data,(parent,depth),state,cfg,bank)
        write_json(out/f'geometry-{epoch+1:02d}.json',observed)
        require(not any(g['catastrophic_collapse'] for m in observed.values() for g in m.values()),
                'Catastrophic continuation collapse; geometry retained')
        h = dict(epoch=epoch+1,parents_seen=seen,available_views=anchors,depth_dropped_views=dropped,
                 relation_pairs_exposed=exposed,relation_weight=coefficient,ema_updates=updates,
                 original_pair_slots=proposed_exposed,relation_normalizer='original proposal slots, not accepted count or weight sum',
                 inherited_ema_updates=saved['ema_updates'],last_tau=tau,geometry=observed,
                 **dict(zip(['loss','fused_positive','sequence_positive','composition_reconstruction',
                             'depth_reconstruction','relation_positive','relation_negative','anchor_preservation'],(totals/seen).tolist())),
                 wall_seconds=time.monotonic()-start)
        history.append(h); emit('bootstrap_continuation_epoch',**h)
    require(state_digest(anchor) == initial_state['anchor'], 'Fixed bootstrap anchor mutated')
    require(inputs(features,views,tokens,frozen,pairs,bootstrap) == bound, 'Continuation input manifests changed')
    values,valid = inherited.infer(model,data,state,cfg,bank,(parent,depth))
    result = dict(kind='bootstrap_continuation_checkpoint',version=1,config=cfg,continuation=continuation,
                  transform=state,samples=meta['samples'],inputs=bound,model_state=model.state_dict(),
                  target_state=target.state_dict(),predictor_state=predictors.state_dict(),
                  anchor_state=anchor.state_dict(),optimizer_state=optimizer.state_dict(),
                  torch_rng_state=torch.get_rng_state(),numpy_rng_state=rng.bit_generator.state,
                  inherited_updates=saved['ema_updates'],added_updates=updates)
    with (out/'checkpoint.pt').open('xb') as stream: torch.save(result,stream)
    write_json(out/'checkpoint.json',{k:result[k] for k in ['kind','version','config','continuation','transform','samples','inputs',
        'inherited_updates','added_updates']} | dict(sha256=digest(out/'checkpoint.pt'),initial_state=initial_state,
        final_state={n:state_digest(m) for n,m in [('online',model),('target',target),('predictor',predictors),('anchor',anchor)]},
        history=history,threads=threads,loader_workers=0,training_parents=len(indices),
        wall_seconds=time.monotonic()-start,process_cpu_seconds=time.process_time()-cpu,
        original_optimizer_steps_restored=True,exact_interrupted_resume=False,truth_accessed=False))
    save_arrays(out/'reference.npz',dict(ids=data['ids'],features=values,evidence=valid),
        dict(kind='embeddings',mode='bootstrap_continuation_reference',samples=meta['samples'],
             features_sha256=digest(features),checkpoint_sha256=digest(out/'checkpoint.pt')))


def digest_bytes(value):
    """Hash an RNG byte stream without writing another artifact."""
    return hashlib.sha256(value).hexdigest()


def embed(features,views,tokens,frozen,pairs,bootstrap,checkpoint,output,threads=4):
    """Reload every learned module strictly and require exact same-runtime outputs."""
    configure_torch(threads); path = Path(checkpoint)
    receipt = json.loads(path.with_suffix('.json').read_text())
    require(receipt['sha256'] == digest(path), 'Continuation checkpoint bytes differ')
    saved = torch.load(path,map_location='cpu',weights_only=True)
    require(saved.get('kind') == 'bootstrap_continuation_checkpoint' and saved.get('version') == 1 and
            all(saved[k] == receipt[k] for k in ['kind','version','config','continuation','transform','samples','inputs',
                                                'inherited_updates','added_updates']) and
            saved['inputs'] == inputs(features,views,tokens,frozen,pairs,bootstrap), 'Continuation reload source/schema differs')
    policy(saved['continuation']); read_pairs(pairs,features)
    _,data,meta,v,vm = read_bootstrap(bootstrap,features,views,tokens,frozen)
    require(saved['samples'] == meta['samples'], 'Continuation reload sample axis differs')
    cfg = saved['config']; bank = inherited.make_bank(tokens,frozen,features,views,data,meta,v,cfg)
    model,target,predictors = inherited.initialize(len(meta['samples']),cfg)
    for module,key,name in [(model,'model_state','online'),(target,'target_state','target'),(predictors,'predictor_state','predictor')]:
        module.load_state_dict(saved[key],strict=True)
        require(state_digest(module) == receipt['final_state'][name], 'Continuation module/buffer reload differs')
    fixed = copy.deepcopy(model).requires_grad_(False).eval(); fixed.load_state_dict(saved['anchor_state'],strict=True)
    require(state_digest(fixed) == receipt['initial_state']['anchor'] == receipt['final_state']['anchor'], 'Fixed anchor state differs')
    values,valid = inherited.infer(model,data,saved['transform'],cfg,bank)
    reference,rm = load_arrays(path.parent/'reference.npz','embeddings')
    require(rm['checkpoint_sha256'] == digest(path) and all(np.array_equal(reference[k],x) for k,x in
        [('ids',data['ids']),('features',values),('evidence',valid)]), 'Continuation exact same-runtime reload differs')
    save_arrays(output,dict(ids=data['ids'],features=values,evidence=valid),
        dict(kind='embeddings',mode='bootstrap_continuation_online_unit_sphere',samples=meta['samples'],
             features_sha256=digest(features),checkpoint_sha256=digest(path),reload_exact=True,
             metric='unit-sphere cosine/equivalent Euclidean; no post-learning transform'))
