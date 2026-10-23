"""Frozen sequence/context/composition/depth hybrid with the preserved objective.

View-matched frozen-sequence residual fusion is the declared treatment. E016's predictor,
stopped EMA target, available-positive reduction, parent exposure, reconstruction
and measured-parent depth/dropout remain the learning anchors. No labels enter.
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

from ..candidate.model import fit_transform, transform
from ..io import digest, emit, save_arrays, write_json
from ..model import batches, configure_torch
from ..multiview.arrays import load_arrays
from ..multiview.model import Encoder as ParentEncoder, parent_average
from ..multiview.positive import predictor, pair_loss, update_target, geometry, validate_policy
from ..multiview.views import load, config as base_config
from ..context.tokens import Bank as ContextBank, policy
from ..context.model import config as context_config, Encoder as ContextEncoder
from .bank import Bank as FrozenBank, policy as hybrid_policy


def config(path=None):
    """Read one strict hybrid policy and inherited context/learning defaults."""
    default=dict(context_config(),hybrid=hybrid_policy())
    cfg=json.loads(Path(path).read_text())if path else default
    if set(cfg)!=set(default)or cfg['hybrid']!=hybrid_policy():raise ValueError('Unfrozen hybrid configuration')
    # Reuse E019's exact validators without rewriting retained cache metadata.
    from tempfile import TemporaryDirectory
    with TemporaryDirectory()as tmp:
        p=Path(tmp)/'context.json';p.write_text(json.dumps({k:v for k,v in cfg.items()if k!='hybrid'}));context_config(p)
    return cfg


class Encoder(ContextEncoder):
    """Add gated frozen sequence evidence to <=9-token context and explicit depth."""

    def __init__(self, samples, cfg):
        super().__init__(samples, cfg)
        c=cfg['hybrid']
        self.frozen_branch=nn.Sequential(nn.Linear(768,c['hidden']),nn.LayerNorm(c['hidden']),nn.GELU(),nn.Linear(c['hidden'],c['output']),nn.GELU())
        self.frozen_gate=nn.Linear(2,1)
        nn.init.zeros_(self.frozen_gate.weight);nn.init.zeros_(self.frozen_gate.bias)
        self.frozen_residual=nn.Linear(c['output'],cfg['sequence_output'],bias=False)
        nn.init.zeros_(self.frozen_residual.weight)

    def forward(self, composition, depth, depth_evidence, local, position, mask, frozen, quality):
        """Return unit fused/sequence vectors; padding and absent depth cannot leak."""
        if (composition.ndim != 2 or composition.shape[1] != 136
                or local.ndim != 3 or local.shape != (len(composition), self.tokens, 136)
                or position.shape != local.shape[:2]+(3,) or mask.shape != local.shape[:2]
                or mask.dtype != torch.bool or depth_evidence.dtype != torch.bool):
            raise ValueError('Invalid context encoder axes/masks')
        if not all(torch.isfinite(x).all() for x in (composition, depth, local, position)):
            raise ValueError('Nonfinite context encoder input')
        if frozen.shape!=(len(composition),768)or quality.shape!=(len(composition),2)or not torch.isfinite(frozen).all()or not torch.isfinite(quality).all():raise ValueError('Invalid frozen sequence axes/quality')
        # Both key masking and explicit value clearing protect padded tokens.
        local = local.masked_fill(~mask[..., None], 0)
        position = position.masked_fill(~mask[..., None], 0)
        tokens = self.token_projection(local)+self.position_projection(position)
        global_token = self.token_projection(composition)[:, None, :]+self.global_type
        tokens = torch.cat([global_token, tokens], dim=1)
        keep = torch.cat([torch.ones((len(mask), 1), dtype=torch.bool, device=mask.device), mask], dim=1)
        normalized = self.norm1(tokens)
        attended = self.attention(normalized, normalized, normalized, key_padding_mask=~keep, need_weights=False)[0]
        tokens = tokens+attended
        tokens = tokens+self.ff(self.norm2(tokens))
        pooled = tokens.masked_fill(~keep[..., None], 0).sum(1)/keep.sum(1)[:, None]
        sequence = self.sequence(composition)+self.context_projection(self.context_output_norm(pooled))
        sequence=sequence+torch.sigmoid(self.frozen_gate(quality))*self.frozen_residual(self.frozen_branch(frozen))
        parts = [F.normalize(sequence, dim=1)]
        if self.depth is not None:
            parts.append(F.normalize(self.depth(depth), dim=1)*depth_evidence[:, None])
        return (F.normalize(self.fusion(torch.cat(parts, dim=1)), dim=1),
            F.normalize(self.sequence_head(sequence), dim=1))


def initialize(samples, cfg):
    """Initialize online once, copy stopped teacher without RNG draws, then predictors."""
    model = Encoder(samples, cfg)
    before = torch.get_rng_state().clone()
    target = copy.deepcopy(model).requires_grad_(False).eval()
    if not torch.equal(before, torch.get_rng_state()):
        raise RuntimeError('Context target copying changed RNG')
    # Reuse the original predictor RNG point, without undoing or changing the
    # newly initialized context parameters. No new seed or stochastic forward.
    with torch.random.fork_rng(devices=[]):
        torch.set_rng_state(model._predictor_rng)
        predictors = nn.ModuleList([predictor(cfg['output'], cfg['predictor_hidden']) for _ in range(2)])
    return model, target, predictors


def forward_args(s, d, mask, bank, selected, view_numbers, state):
    """Create one bounded model batch using read-only cached context, without labels."""
    token, position, keep = bank[0].batch(selected, view_numbers, state)
    frozen,quality=bank[1].batch(selected,view_numbers,state['hybrid'])
    return [torch.from_numpy(x) for x in (s, d, mask, token, position, keep, frozen, quality)]


def parent_evidence(composition,depth_mask,local_valid,frozen):
    """Keep eligible parents with any actual input evidence, including GLM-only."""
    return ((np.linalg.norm(composition,axis=1)>1e-12)|depth_mask|local_valid|
        (np.linalg.norm(frozen,axis=1)>1e-12))


def infer(model, data, state, cfg, bank, transformed=None):
    """Infer full-parent contexts in the same unit geometry as learning/grouping."""
    s, d = transformed if transformed is not None else transform(data['tnf'], data['depth'], data['depth_evidence'], state)
    # Local information can distinguish parents whose full TNF becomes zero after
    # the parent-fitted transform. Do not inherit the old global-only veto.
    valid = np.zeros(len(s), bool)
    for selected in batches(np.flatnonzero(data['eligible']), cfg['context']['context_inference_batch_size']):
        local_valid = bank[0].counts[bank[0].lookup[selected], 0].sum((1, 2)) > 0
        frozen,_=bank[1].batch(selected,np.zeros(len(selected),np.int64),state['hybrid'])
        valid[selected] = parent_evidence(s[selected],data['depth_evidence'][selected],local_valid,frozen)
    values = np.zeros((len(s), cfg['output']), np.float32)
    model.eval()
    with torch.inference_mode():
        for selected in batches(np.flatnonzero(valid), cfg['context']['context_inference_batch_size']):
            args = forward_args(s[selected], d[selected], data['depth_evidence'][selected], bank,
                selected, np.zeros(len(selected), np.int64), state)
            values[selected] = model(*args)[0].numpy()
    if not np.isfinite(values).all():
        raise ValueError('Nonfinite context inference')
    return values, valid & (np.linalg.norm(values, axis=1) > 1e-12)


def monitor(model, target, data, transformed, state, cfg, bank, enforce=False):
    """Measure fixed, evenly spaced parent-only geometry without random draws."""
    indices = np.flatnonzero(data['eligible'])
    selected = indices[np.linspace(0, len(indices)-1, min(len(indices), cfg['collapse_rows']), dtype=int)]
    result = {}
    for name, module in [('online', model), ('target', target)]:
        module.eval()
        values = [[], []]
        with torch.inference_mode():
            for b in batches(selected, cfg['context']['context_inference_batch_size']):
                args = forward_args(transformed[0][b], transformed[1][b], data['depth_evidence'][b],
                    bank, b, np.zeros(len(b), np.int64), state)
                for i, value in enumerate(module(*args)):
                    values[i].append(value.numpy())
        result[name] = {label: geometry(np.concatenate(values[i]), cfg, enforce)
            for i, label in enumerate(['fused', 'sequence'])}
    return result


def train(features, views, tokens, frozen, output, cfg, threads):
    """Run one explicit fresh context fit; preserve exact exposure and every history."""
    configure_torch(threads)
    data, meta, v, vm = load(features, views)
    validate_policy({k: value for k, value in cfg.items() if k not in ('context','hybrid')}, vm['policy'])
    if cfg['context'] != policy():
        raise ValueError('Context training policy differs')
    bank = (ContextBank(tokens, features, views, data, meta, v),FrozenBank(frozen,features,views,data,meta,v))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    indices = np.flatnonzero(data['eligible'])
    state = fit_transform(data)
    state['hybrid']=bank[1].fit()
    parent, depth = transform(data['tnf'], data['depth'], data['depth_evidence'], state)
    weights_np = np.log1p(np.minimum(data['lengths'], 10000)/500).astype(np.float32)
    torch.manual_seed(cfg['seed'])
    rng = np.random.default_rng(cfg['seed'])
    model, target, predictors = initialize(len(meta['samples']), cfg)
    optimizer = torch.optim.AdamW(list(model.parameters())+list(predictors.parameters()),
        lr=cfg['learning_rate'], weight_decay=cfg['weight_decay'])
    usable_depth = np.asarray(state['depth']['std']) > 1e-8
    steps = cfg['epochs']*math.ceil(len(indices)/cfg['batch_size'])
    updates = 0
    start, cpu = time.monotonic(), time.process_time()
    history = []
    initial = monitor(model, target, data, (parent, depth), state, cfg, bank)
    write_json(out/'initial-geometry.json', initial)
    for epoch in range(cfg['epochs']):
        model.train()
        predictors.train()
        seen = anchors = dropped = 0
        totals = np.zeros(5)
        for selected in batches(rng.permutation(indices), cfg['batch_size']):
            n = len(selected)
            s0, d0, m0 = parent[selected], depth[selected], data['depth_evidence'][selected]
            global_views = [s0]+[transform(v['tnf'][selected, j], data['depth'][selected], m0, state)[0] for j in range(4)]
            available = np.concatenate([np.ones(n, bool)]+[v['usable'][selected, j] for j in range(4)])
            owners_np = np.tile(np.arange(n), 5)[available]
            view_numbers = np.repeat(np.arange(5), n)[available]
            selected_views = np.tile(selected, 5)[available]
            sequence = np.concatenate(global_views)[available]
            original_mask = np.tile(m0, 5)[available]
            observed_depth = np.tile(d0, (5, 1))[available]
            mask = original_mask & (rng.random(len(owners_np)) >= cfg['depth_dropout'])
            dropped += int((original_mask & ~mask).sum())
            owners, weights = torch.from_numpy(owners_np), torch.from_numpy(weights_np[selected])
            args = forward_args(sequence, observed_depth, mask, bank, selected_views, view_numbers, state)
            fused, seq = model(*args)
            with torch.no_grad():
                tf, ts = target(*args)
            pf = pair_loss(fused, tf, owners, weights, predictors[0])
            ps = pair_loss(seq, ts, owners, weights, predictors[1])
            wanted = torch.from_numpy(s0)[owners]
            rf = (F.normalize(model.composition_decoder(fused), dim=1)-wanted).square().sum(1)
            rs = (F.normalize(model.composition_decoder(seq), dim=1)-wanted).square().sum(1)
            rc = parent_average((rf+rs)*.5, owners, weights)
            rd = fused.sum()*0
            has = torch.from_numpy(original_mask)
            if model.depth_decoder is not None and usable_depth.any() and has.any():
                predicted = model.depth_decoder(fused)[has][:, usable_depth]
                desired = torch.from_numpy(observed_depth)[has][:, usable_depth]
                dl = F.smooth_l1_loss(predicted, desired, reduction='none').mean(1)
                rd = parent_average(dl, owners[has], weights)
            loss = pf+cfg['sequence_loss_weight']*ps+cfg['composition_reconstruction_weight']*rc+cfg['depth_reconstruction_weight']*rd
            if not torch.isfinite(loss):
                raise ValueError('Nonfinite context loss')
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for group in optimizer.param_groups for p in group['params']):
                raise ValueError('Nonfinite context gradient')
            if any(p.grad is not None for p in target.parameters()):
                raise RuntimeError('Context target received gradients')
            optimizer.step()
            tau = 1-(1-cfg['ema_base'])*(1+math.cos(math.pi*updates/steps))/2
            update_target(model, target, tau)
            updates += 1
            seen += n
            anchors += len(owners)
            totals += np.array([float(x.detach()) for x in (loss, pf, ps, rc, rd)])*n
        if seen != len(indices):
            raise RuntimeError('Context full-parent exposure differs')
        observed = monitor(model, target, data, (parent, depth), state, cfg, bank)
        write_json(out/f'geometry-{epoch+1:02d}.json', observed)
        if any(g['catastrophic_collapse'] for m in observed.values() for g in m.values()):
            raise ValueError('Catastrophic context collapse; epoch evidence retained')
        h = dict(epoch=epoch+1, parents_seen=seen, available_views=anchors, depth_dropped_views=dropped,
            **dict(zip(['loss', 'fused_positive', 'sequence_positive', 'composition_reconstruction', 'depth_reconstruction'], (totals/seen).tolist())),
            ema_updates=updates, last_tau=tau, geometry=observed, wall_seconds=time.monotonic()-start)
        history.append(h)
        emit('context_epoch', **h)
    values, valid = infer(model, data, state, cfg, bank, (parent, depth))
    saved = dict(kind='hybrid_checkpoint', version=1, config=cfg, transform=state, samples=meta['samples'],
        model_state=model.state_dict(), target_state=target.state_dict(), predictor_state=predictors.state_dict(),
        optimizer_state=optimizer.state_dict(), ema_updates=updates,
        training_features_sha256=digest(features), training_views_sha256=digest(views),
        training_tokens_sha256=digest(Path(tokens)/'tokens.json'),training_frozen_sha256=digest(Path(frozen)/'bank.json'))
    with (out/'checkpoint.pt').open('xb') as stream:
        torch.save(saved, stream)
    write_json(out/'checkpoint.json', {k: saved[k] for k in ['kind', 'version', 'config', 'transform', 'samples',
        'ema_updates', 'training_features_sha256', 'training_views_sha256', 'training_tokens_sha256','training_frozen_sha256']} |
        dict(sha256=digest(out/'checkpoint.pt'), history=history, initial_geometry=initial,
        threads=threads, loader_workers=0, training_parents=len(indices),
        positive_parents=int((data['eligible'] & v['usable'].any(1)).sum()),
        parameter_count=sum(p.numel() for p in model.parameters()),
        predictor_parameter_count=sum(p.numel() for p in predictors.parameters()),
        teacher_parameter_count=sum(p.numel() for p in target.parameters()),
        wall_seconds=time.monotonic()-start, process_cpu_seconds=time.process_time()-cpu,
        assumptions='Bounded canonical DNA contexts; all E016 real views/exposure/objective; parent means only; online unit inference; exact frozen DNABERT-S real views; no labels/markers/taxonomy'))
    save_arrays(out/'reference.npz', dict(ids=data['ids'], features=values, evidence=valid),
        dict(kind='embeddings', mode='hybrid_pre_save_reference', samples=meta['samples'],
        features_sha256=digest(features), checkpoint_sha256=digest(out/'checkpoint.pt')))


def embed(features, views, tokens, frozen, checkpoint, output, threads):
    """Strictly reload all checkpoint modules and demand exact same-runtime vectors."""
    configure_torch(threads)
    data, meta, v, vm = load(features, views)
    path = Path(checkpoint)
    receipt = json.loads(path.with_suffix('.json').read_text())
    if receipt['sha256'] != digest(path):
        raise ValueError('Context checkpoint bytes differ')
    saved = torch.load(path, weights_only=True, map_location='cpu')
    if (saved['kind'] != 'hybrid_checkpoint' or saved['version'] != 1 or saved['samples'] != meta['samples']
            or saved['training_features_sha256'] != digest(features) or saved['training_views_sha256'] != digest(views)
            or saved['training_tokens_sha256'] != digest(Path(tokens)/'tokens.json')
            or saved['training_frozen_sha256'] != digest(Path(frozen)/'bank.json')
            or any(saved[k] != receipt[k] for k in ['kind', 'version', 'config', 'transform', 'samples',
                'ema_updates', 'training_features_sha256', 'training_views_sha256', 'training_tokens_sha256','training_frozen_sha256'])):
        raise ValueError('Context checkpoint/source/schema differs')
    validate_policy({k: value for k, value in saved['config'].items() if k not in ('context','hybrid')}, vm['policy'])
    if saved['config']['context'] != policy() or saved['config']['hybrid']!=hybrid_policy():
        raise ValueError('Context reload policy differs')
    bank = (ContextBank(tokens, features, views, data, meta, v),FrozenBank(frozen,features,views,data,meta,v))
    model, target, predictors = initialize(len(meta['samples']), saved['config'])
    for module, key in [(model, 'model_state'), (target, 'target_state'), (predictors, 'predictor_state')]:
        module.load_state_dict(saved[key], strict=True)
        if any(not torch.isfinite(value).all() for value in module.state_dict().values()):
            raise ValueError('Nonfinite context checkpoint state')
    values, valid = infer(model, data, saved['transform'], saved['config'], bank)
    reference, rm = load_arrays(path.parent/'reference.npz', 'embeddings')
    if (rm['checkpoint_sha256'] != digest(path) or any(not np.array_equal(reference[k], value)
            for k, value in [('ids', data['ids']), ('features', values), ('evidence', valid)])):
        raise ValueError('Context exact same-runtime reload differs')
    save_arrays(output, dict(ids=data['ids'], features=values, evidence=valid),
        dict(kind='embeddings', mode='hybrid_online_unit_sphere', samples=meta['samples'],
        features_sha256=digest(features), checkpoint_sha256=digest(path), reload_exact=True,
        tokens_manifest_sha256=saved['training_tokens_sha256'], metric='unit-sphere cosine/equivalent Euclidean; no post-learning transform'))
