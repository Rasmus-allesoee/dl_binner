"""E016 positive-only parent-balanced learning, preserving dev5 inference geometry.

No community labels, markers, source joins or cross-parent pseudo-links enter this
module. The online model predicts stopped same-parent target views. An averaged
target is an algebraic pair-loss reduction, never a renormalized pseudo-positive.
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

from .model import (Encoder, parent_average, configure_torch, load, fit_transform,
                    transform, infer, batches, digest, write_json, emit, save_arrays)
from .arrays import load_arrays


def validate_policy(cfg, bank_policy):
    """Admit only declared training additions to an unchanged retained view bank."""
    extra = {'positive_only', 'predictor_hidden', 'ema_base', 'collapse_rows',
             'collapse_min_std', 'collapse_min_rank'}
    if set(cfg) != set(bank_policy) | extra or any(cfg[k] != v for k, v in bank_policy.items()):
        raise ValueError('Retained bank or positive-only training policy differs')
    if (cfg['positive_only'] is not True or cfg['predictor_hidden'] != 128 or
            cfg['ema_base'] != .996 or cfg['collapse_rows'] != 8192 or
            cfg['collapse_min_std'] != .001 or cfg['collapse_min_rank'] != 2):
        raise ValueError('Unfrozen positive-only defaults')


def predictor(width, hidden):
    """Construct a training-only predictor; call only on >=2 positive anchors."""
    return nn.Sequential(nn.Linear(width, hidden), nn.BatchNorm1d(hidden),
                         nn.ReLU(), nn.Linear(hidden, width))


def initialize(samples, cfg):
    """Build online first, copy frozen target without RNG draws, then predictors."""
    online = Encoder(samples, cfg)
    rng = torch.get_rng_state().clone()
    target = copy.deepcopy(online).requires_grad_(False).eval()
    if not torch.equal(rng, torch.get_rng_state()):
        raise RuntimeError('Target copying consumed RNG')
    predictors = nn.ModuleList([predictor(cfg['output'], cfg['predictor_hidden']) for _ in range(2)])
    return online, target, predictors


@torch.no_grad()
def update_target(online, target, tau):
    """EMA every named floating parameter/buffer, copying nonfloating buffers."""
    if not 0 <= tau <= 1:
        raise ValueError('Invalid EMA rate')
    a, b = online.state_dict(), target.state_dict()
    if a.keys() != b.keys():
        raise ValueError('Target state axes differ')
    for key, value in b.items():
        if value.shape != a[key].shape or value.dtype != a[key].dtype:
            raise ValueError('Target state shape/dtype differs')
        if value.is_floating_point():
            value.mul_(tau).add_(a[key], alpha=1-tau)
        else:
            value.copy_(a[key])


def pair_loss(z, target, parents, weights, head):
    """Average all ordered nonself same-parent squared unit prediction distances.

    This linear-memory reduction equals the explicit ragged ordered-pair oracle.
    A singleton supplies no alignment gradient; no other parent's target is used.
    Target is detached here too, so callers cannot accidentally train the teacher.
    """
    if z.ndim != 2 or z.shape != target.shape or len(z) != len(parents):
        raise ValueError('Positive loss axes differ')
    if (parents.dtype != torch.int64 or len(weights) == 0 or len(parents) == 0 or
            parents.min() < 0 or parents.max() >= len(weights) or
            not torch.isfinite(z).all() or not torch.isfinite(target).all() or
            not torch.isfinite(weights).all() or (weights <= 0).any()):
        raise ValueError('Invalid positive-only inputs')
    counts = torch.bincount(parents, minlength=len(weights))
    valid = counts[parents] > 1
    if not valid.any():
        return z.sum()*0
    t = F.normalize(target.detach(), dim=1)
    sums = torch.zeros((len(weights), t.shape[1]), dtype=t.dtype, device=t.device)
    sums.index_add_(0, parents, t)
    wanted = (sums[parents[valid]]-t[valid])/(counts[parents[valid]]-1)[:, None]
    q = F.normalize(head(z[valid]), dim=1)
    losses = 2-2*(q*wanted).sum(1)
    return parent_average(losses, parents[valid], weights)


def geometry(values, cfg, enforce=True):
    """Return label-free centered rank/variance and refuse catastrophic collapse."""
    x = np.asarray(values, dtype=np.float64)
    if (x.ndim != 2 or len(x) < 2 or not np.isfinite(x).all() or
            not np.allclose(np.linalg.norm(x, axis=1), 1, rtol=0, atol=1e-6)):
        raise ValueError('Invalid collapse-monitor unit vectors')
    centered = x-x.mean(0)
    eig = np.maximum(np.linalg.eigvalsh(centered.T@centered/len(x)), 0)
    p = eig[eig > 0]/max(eig.sum(), 1e-300)
    rank = float(np.exp(-(p*np.log(p)).sum())) if len(p) else 0.
    std = float(centered.std(0).mean())
    collapsed = len(x) >= 128 and (std < cfg['collapse_min_std'] or rank < cfg['collapse_min_rank'])
    result = dict(rows=len(x), effective_rank=rank, mean_dimension_std=std,
                  mean_other_cosine=float((np.square(x.sum(0)).sum()-len(x))/(len(x)*(len(x)-1))),
                  catastrophic_collapse=collapsed)
    if enforce and collapsed:
        raise ValueError('Catastrophic positive-only collapse: '+json.dumps(result))
    return result


def monitor(online, target, composition, depth, evidence, indices, cfg, enforce=True):
    """Measure both heads/teachers on evenly spaced eligible parents, without RNG."""
    selected = indices[np.linspace(0, len(indices)-1, min(len(indices), cfg['collapse_rows']), dtype=int)]
    result = {}
    for name, model in [('online', online), ('target', target)]:
        model.eval(); values = [[], []]
        with torch.inference_mode():
            for b in batches(selected, cfg['inference_batch_size']):
                heads = model(torch.from_numpy(composition[b]), torch.from_numpy(depth[b]),
                              torch.from_numpy(evidence[b]))
                for i, h in enumerate(heads):
                    values[i].append(h.numpy())
        result[name] = {label: geometry(np.concatenate(values[i]), cfg, enforce)
                        for i, label in enumerate(['fused', 'sequence'])}
    return result


def train(features, views, output, cfg, threads):
    """Fit the frozen two-head positive-only schedule on retained parent/crop bytes."""
    configure_torch(threads); data, meta, v, vm = load(features, views)
    validate_policy(cfg, vm['policy'])
    indices = np.flatnonzero(data['eligible'])
    if len(indices) < 2:
        raise ValueError('Need at least two eligible parents')
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    state = fit_transform(data)
    parent, depth = transform(data['tnf'], data['depth'], data['depth_evidence'], state)
    weights_np = np.log1p(np.minimum(data['lengths'], 10000)/500).astype(np.float32)
    torch.manual_seed(cfg['seed']); rng = np.random.default_rng(cfg['seed'])
    model, target, predictors = initialize(len(meta['samples']), cfg)
    optimizer = torch.optim.AdamW(list(model.parameters())+list(predictors.parameters()),
                                 lr=cfg['learning_rate'], weight_decay=cfg['weight_decay'])
    usable_depth = np.asarray(state['depth']['std']) > 1e-8
    steps = cfg['epochs']*math.ceil(len(indices)/cfg['batch_size']); updates = 0
    start, cpu = time.monotonic(), time.process_time(); history = []
    initial = monitor(model, target, parent, depth, data['depth_evidence'], indices, cfg, False)
    write_json(out/'initial-geometry.json', initial)
    for epoch in range(cfg['epochs']):
        model.train(); predictors.train(); seen = anchors = dropped = 0; totals = np.zeros(5)
        for selected in batches(rng.permutation(indices), cfg['batch_size']):
            n = len(selected); s0 = parent[selected]; d0 = depth[selected]; m0 = data['depth_evidence'][selected]
            bank = [s0]+[transform(v['tnf'][selected, j], data['depth'][selected], m0, state)[0] for j in range(4)]
            available = np.concatenate([np.ones(n, bool)]+[v['usable'][selected, j] for j in range(4)])
            owners = np.tile(np.arange(n), 5)[available]; composition = np.concatenate(bank)[available]
            original_mask = np.tile(m0, 5)[available]; observed_depth = np.tile(d0, (5, 1))[available]
            mask = original_mask & (rng.random(len(owners)) >= cfg['depth_dropout'])
            dropped += int((original_mask & ~mask).sum())
            owners = torch.from_numpy(owners); w = torch.from_numpy(weights_np[selected])
            args = [torch.from_numpy(x) for x in [composition, observed_depth, mask]]
            fused, seq = model(*args)
            with torch.no_grad():
                tf, ts = target(*args)
            pf = pair_loss(fused, tf, owners, w, predictors[0])
            ps = pair_loss(seq, ts, owners, w, predictors[1])
            wanted = torch.from_numpy(s0)[owners]
            rf = (F.normalize(model.composition_decoder(fused), dim=1)-wanted).square().sum(1)
            rs = (F.normalize(model.composition_decoder(seq), dim=1)-wanted).square().sum(1)
            rc = parent_average((rf+rs)*.5, owners, w); rd = fused.sum()*0
            has = torch.from_numpy(original_mask)
            if model.depth_decoder is not None and usable_depth.any() and has.any():
                predicted = model.depth_decoder(fused)[has][:, usable_depth]
                wanted_depth = torch.from_numpy(observed_depth)[has][:, usable_depth]
                dl = F.smooth_l1_loss(predicted, wanted_depth, reduction='none').mean(1)
                rd = parent_average(dl, owners[has], w)
            loss = pf+cfg['sequence_loss_weight']*ps+cfg['composition_reconstruction_weight']*rc+cfg['depth_reconstruction_weight']*rd
            if not torch.isfinite(loss):
                raise ValueError('Nonfinite positive-only loss')
            optimizer.zero_grad(set_to_none=True); loss.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for group in optimizer.param_groups for p in group['params']):
                raise ValueError('Nonfinite positive-only gradient')
            if any(p.grad is not None for p in target.parameters()):
                raise RuntimeError('Stopped target received gradients')
            optimizer.step()
            tau = 1-(1-cfg['ema_base'])*(1+math.cos(math.pi*updates/steps))/2
            update_target(model, target, tau); updates += 1
            seen += n; anchors += len(owners)
            totals += np.array([float(x.detach()) for x in (loss, pf, ps, rc, rd)])*n
        if seen != len(indices):
            raise RuntimeError('Positive-only parent exposure changed')
        # Retain diagnostics before any prospective catastrophic-collapse refusal.
        observed = monitor(model, target, parent, depth, data['depth_evidence'], indices, cfg, False)
        write_json(out/f'geometry-{epoch+1:02d}.json', observed)
        if any(g['catastrophic_collapse'] for m in observed.values() for g in m.values()):
            raise ValueError('Catastrophic positive-only collapse; retained epoch geometry')
        h = dict(epoch=epoch+1, parents_seen=seen, available_views=anchors, depth_dropped_views=dropped,
                 **dict(zip(['loss', 'fused_positive', 'sequence_positive', 'composition_reconstruction', 'depth_reconstruction'], (totals/seen).tolist())),
                 ema_updates=updates, last_tau=tau, geometry=observed, wall_seconds=time.monotonic()-start)
        history.append(h); emit('positive_only_epoch', **h)
    positive_parents = int((data['eligible'] & v['usable'].any(1)).sum()); del v
    values, valid = infer(model, data, state, cfg)
    saved = dict(kind='positive_only_checkpoint', version=1, config=cfg, transform=state, samples=meta['samples'],
                 model_state=model.state_dict(), target_state=target.state_dict(), predictor_state=predictors.state_dict(),
                 optimizer_state=optimizer.state_dict(), ema_updates=updates,
                 training_features_sha256=digest(features), training_views_sha256=digest(views))
    with (out/'checkpoint.pt').open('xb') as f:
        torch.save(saved, f)
    write_json(out/'checkpoint.json', dict(kind=saved['kind'], version=1, sha256=digest(out/'checkpoint.pt'),
        config=cfg, transform=state, samples=meta['samples'], training_features_sha256=digest(features), training_views_sha256=digest(views),
        history=history, initial_geometry=initial, threads=threads, loader_workers=0, training_parents=len(indices),
        positive_parents=positive_parents, reconstruction_only_parents=len(indices)-positive_parents,
        parameter_count=sum(p.numel() for p in model.parameters()), predictor_parameter_count=sum(p.numel() for p in predictors.parameters()),
        teacher_parameter_count=sum(p.numel() for p in target.parameters()), ema_updates=updates,
        wall_seconds=time.monotonic()-start, process_cpu_seconds=time.process_time()-cpu,
        assumptions='Within-parent real views; no cross-parent negative or pseudo-positive labels; measured-parent depth/dropout; original reconstruction; online inference only.'))
    save_arrays(out/'reference.npz', dict(ids=data['ids'], features=values, evidence=valid), dict(kind='embeddings',
                mode='positive_only_pre_save_reference', samples=meta['samples'], features_sha256=digest(features), checkpoint_sha256=digest(out/'checkpoint.pt')))


def embed(features, checkpoint, output, threads):
    """Reload every saved module strictly and require exact online native inference."""
    configure_torch(threads); data, meta = load(features); path = Path(checkpoint)
    receipt = json.loads(path.with_suffix('.json').read_text())
    if receipt['sha256'] != digest(path) or receipt['training_features_sha256'] != digest(features):
        raise ValueError('Positive-only checkpoint/input bytes differ')
    saved = torch.load(path, weights_only=True, map_location='cpu')
    if (saved['kind'] != 'positive_only_checkpoint' or saved['version'] != 1 or saved['samples'] != meta['samples'] or
            any(saved[k] != receipt[k] for k in ['config', 'transform', 'training_features_sha256', 'training_views_sha256', 'ema_updates'])):
        raise ValueError('Positive-only checkpoint schema differs')
    model, target, predictors = initialize(len(meta['samples']), saved['config'])
    for module, key in [(model, 'model_state'), (target, 'target_state'), (predictors, 'predictor_state')]:
        module.load_state_dict(saved[key], strict=True)
        if any(not torch.isfinite(v).all() for v in module.state_dict().values()):
            raise ValueError('Nonfinite positive-only checkpoint state')
    values, valid = infer(model, data, saved['transform'], saved['config'])
    reference, rm = load_arrays(path.parent/'reference.npz', 'embeddings')
    if (rm['checkpoint_sha256'] != digest(path) or any(not np.array_equal(reference[k], v) for k, v in
            [('ids', data['ids']), ('features', values), ('evidence', valid)])):
        raise ValueError('Positive-only exact same-runtime reload differs')
    save_arrays(output, dict(ids=data['ids'], features=values, evidence=valid), dict(kind='embeddings',
        mode='positive_only_online_unit_sphere', samples=meta['samples'], features_sha256=digest(features),
        checkpoint_sha256=digest(path), reload_exact=True, metric='unit-sphere cosine/equivalent Euclidean; no post-learning transform'))
