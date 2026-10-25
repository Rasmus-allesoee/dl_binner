"""Fixed E019/E021 encoders with a bounded reliable cross-contig side loss.

No new encoder modules or random initialization: reuse the exact inherited
constructor and keep self-view RNG, full exposure and optimizer/EMA step count.
Only predeclared cache pairs enter; truth and bin identities have no interface.
"""
import json
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F

from ..context import model as context
from ..hybrid import model as hybrid
from .pairs import load_pairs, policy
from .evidence import require


def config(path=None, frozen=True):
    """Admit a declared training-only side policy against unchanged view metadata."""
    base = hybrid if frozen else context
    if path is None:
        return dict(base.config(), relational=policy())
    cfg = json.loads(Path(path).read_text())
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as folder:
        p = Path(folder)/'base.json'; p.write_text(json.dumps({k:v for k,v in cfg.items() if k != 'relational'}))
        base.config(p)
        p.write_text(json.dumps(cfg.get('relational'))); policy(p)
    require(('hybrid' in cfg) == frozen, 'Explicit frozen-bank modality/config differs')
    return cfg


def api(cfg):
    """Resolve the declared existing encoder; no missing-bank substitution."""
    return hybrid if 'hybrid' in cfg else context


def initialize(samples, cfg):
    """Use identical module construction, parameter initialization and predictors."""
    return api(cfg).initialize(samples, cfg)


def forward_args(s, d, mask, bank, selected, view_numbers, state, cfg):
    """Read the exact parent/crop bank through its original installed adapter."""
    return api(cfg).forward_args(s, d, mask, bank, selected, view_numbers, state)


def monitor(model, target, data, transformed, state, cfg, bank):
    """Preserve original native collapse population, statistics and thresholds."""
    return api(cfg).monitor(model, target, data, transformed, state, cfg, bank)


def infer(model, data, state, cfg, bank, transformed=None):
    """Preserve actual full-parent unit inference and evidence/length accounting."""
    return api(cfg).infer(model, data, state, cfg, bank, transformed)


def pair_epoch(count, steps, cfg, epoch):
    """Partition one pair exposure across existing updates without base RNG draws."""
    require(count <= steps*cfg['pair_batch_size'], 'Pair work exceeds original optimizer-step budget')
    order = np.random.default_rng(np.random.SeedSequence([cfg['seed'], epoch])).permutation(count)
    return np.array_split(order, steps)


def coefficient(cfg, epoch):
    """Return the frozen two-epoch warmup/three-epoch linear ramp."""
    return cfg['loss_weight']*min(1., max(0., (epoch+1-cfg['warmup_epochs'])/cfg['ramp_epochs']))


def signed_loss(online, target, predictors, sign, weights, margin):
    """Compute symmetric stopped positive distance and online negative hinge.

    Inputs are two heads with shape [pairs,2,dimension]. Confidence weights are
    averaged over pair count, retaining their absolute attenuation. Both empty
    signs give differentiable zero. No target gradient is permitted.
    """
    require(len(online) == len(target) == len(predictors) == 2, 'Two inherited heads required')
    require(sign.ndim == weights.ndim == 1 and sign.shape == weights.shape
            and torch.isfinite(weights).all() and bool(((weights > 0) & (weights <= 1)).all())
            and bool(((sign == 1) | (sign == -1)).all()), 'Malformed signed-loss weights/signs')
    positive = online[0].sum()*0; negative = positive
    count = len(sign)
    if not count:
        return positive, negative
    for scale, x, y, predictor in zip([1/1.5, .5/1.5], online, target, predictors):
        require(x.ndim == 3 and x.shape[:2] == (count, 2) and y.shape == x.shape
                and torch.isfinite(x).all() and torch.isfinite(y).all(), 'Malformed pair-head axes')
        stopped = y.detach()
        prediction = F.normalize(predictor(x.flatten(0, 1)), dim=1).reshape(x.shape)
        distance = ((2-2*(prediction[:, 0]*stopped[:, 1]).sum(1))+
                    (2-2*(prediction[:, 1]*stopped[:, 0]).sum(1)))*.5
        repulsion = F.relu((x[:, 0]*x[:, 1]).sum(1)-margin).square()
        positive = positive+scale*(weights*distance*(sign == 1)).sum()/count
        negative = negative+scale*(weights*repulsion*(sign == -1)).sum()/count
    return positive, negative


def side_forward(model, target, predictors, pairs, selected, transformed, data, state, cfg, bank):
    """Use full cached parents without direct depth evidence or global RNG changes."""
    indices = np.column_stack([pairs['left'][selected], pairs['right'][selected]]).ravel()
    if not len(indices):
        zero = next(model.parameters()).sum()*0
        return zero, zero
    with torch.random.fork_rng(devices=[]):
        args = forward_args(transformed[0][indices], transformed[1][indices],
            np.zeros(len(indices), bool), bank, indices, np.zeros(len(indices), np.int64), state, cfg)
        online = [x.reshape(len(selected), 2, -1) for x in model(*args)]
        with torch.no_grad():
            stopped = [x.reshape(len(selected), 2, -1) for x in target(*args)]
        # Predictor BatchNorm belongs to inherited self-view updates. Side work
        # uses its existing running statistics, including the weight-zero control.
        modes = [head.training for head in predictors]
        try:
            for head in predictors: head.eval()
            return signed_loss(online, stopped, predictors, torch.from_numpy(pairs['sign'][selected]),
                torch.from_numpy(pairs['weight'][selected]), cfg['relational']['negative_cosine_margin'])
        finally:
            for head, mode in zip(predictors, modes): head.train(mode)


# The self-view loop below intentionally retains the frozen E021 arithmetic.
# Additional side work does not replace views, alter RNG or add optimizer steps.
import math
import time
from ..candidate.model import fit_transform, transform
from ..io import digest, emit, save_arrays, write_json
from ..model import batches, configure_torch
from ..multiview.arrays import load_arrays
from ..multiview.model import parent_average
from ..multiview.positive import pair_loss, update_target, validate_policy
from ..multiview.views import load
from ..context.tokens import Bank as ContextBank, policy as context_policy
from ..hybrid.bank import Bank as FrozenBank, policy as hybrid_policy


def make_bank(tokens, frozen, features, views, data, metadata, view_data, cfg):
    """Require the declared modality; missing GLM bytes never trigger a substitute."""
    local = ContextBank(tokens, features, views, data, metadata, view_data)
    if 'hybrid' in cfg:
        require(frozen is not None, 'Declared hybrid requires its exact frozen bank')
        return local, FrozenBank(frozen, features, views, data, metadata, view_data)
    require(frozen is None, 'Undeclared frozen bank would change the treatment')
    return local


def train(features, views, tokens, frozen, pairs_path, output, cfg, threads):
    """Run one explicit fresh context fit; preserve exact exposure and every history."""
    configure_torch(threads)
    policy(cfg['relational'])
    data, meta, v, vm = load(features, views)
    validate_policy({k: value for k, value in cfg.items() if k not in ('context','hybrid','relational')}, vm['policy'])
    if cfg['context'] != context_policy():
        raise ValueError('Context training policy differs')
    bank = make_bank(tokens, frozen, features, views, data, meta, v, cfg)
    pairs, pair_receipt = load_pairs(pairs_path, features)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    indices = np.flatnonzero(data['eligible'])
    state = fit_transform(data)
    if 'hybrid' in cfg:
        state['hybrid'] = bank[1].fit()
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
        totals = np.zeros(7)
        pieces = pair_epoch(len(pairs['left']), math.ceil(len(indices)/cfg['batch_size']), cfg['relational'], epoch)
        pair_exposure = 0
        side_weight = coefficient(cfg['relational'], epoch)
        for batch_number, selected in enumerate(batches(rng.permutation(indices), cfg['batch_size'])):
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
            args = forward_args(sequence, observed_depth, mask, bank, selected_views, view_numbers, state, cfg)
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
            rp, rn = side_forward(model, target, predictors, pairs, pieces[batch_number],
                (parent, depth), data, state, cfg, bank)
            pair_exposure += len(pieces[batch_number])
            loss = pf+cfg['sequence_loss_weight']*ps+cfg['composition_reconstruction_weight']*rc+cfg['depth_reconstruction_weight']*rd+side_weight*(rp+rn)
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
            totals += np.array([float(x.detach()) for x in (loss, pf, ps, rc, rd, rp, rn)])*n
        if pair_exposure != len(pairs['left']):
            raise RuntimeError('Relational pair exposure differs')
        if seen != len(indices):
            raise RuntimeError('Context full-parent exposure differs')
        observed = monitor(model, target, data, (parent, depth), state, cfg, bank)
        write_json(out/f'geometry-{epoch+1:02d}.json', observed)
        if any(g['catastrophic_collapse'] for m in observed.values() for g in m.values()):
            raise ValueError('Catastrophic context collapse; epoch evidence retained')
        h = dict(epoch=epoch+1, parents_seen=seen, available_views=anchors, depth_dropped_views=dropped,
            **dict(zip(['loss', 'fused_positive', 'sequence_positive', 'composition_reconstruction', 'depth_reconstruction', 'relation_positive', 'relation_negative'], (totals/seen).tolist())),
            relation_pairs_exposed=pair_exposure, relation_weight=side_weight,
            ema_updates=updates, last_tau=tau, geometry=observed, wall_seconds=time.monotonic()-start)
        history.append(h)
        emit('relational_epoch', **h)
    values, valid = infer(model, data, state, cfg, bank, (parent, depth))
    saved = dict(kind='relational_checkpoint', version=1, config=cfg, transform=state, samples=meta['samples'],
        model_state=model.state_dict(), target_state=target.state_dict(), predictor_state=predictors.state_dict(),
        optimizer_state=optimizer.state_dict(), ema_updates=updates,
        training_features_sha256=digest(features), training_views_sha256=digest(views),
        training_tokens_sha256=digest(Path(tokens)/'tokens.json'),
        training_frozen_sha256=digest(Path(frozen)/'bank.json') if 'hybrid' in cfg else None,
        training_pairs_sha256=digest(Path(pairs_path)/'cache.json'))
    with (out/'checkpoint.pt').open('xb') as stream:
        torch.save(saved, stream)
    write_json(out/'checkpoint.json', {k: saved[k] for k in ['kind', 'version', 'config', 'transform', 'samples',
        'ema_updates', 'training_features_sha256', 'training_views_sha256', 'training_tokens_sha256','training_frozen_sha256','training_pairs_sha256']} |
        dict(sha256=digest(out/'checkpoint.pt'), history=history, initial_geometry=initial,
        threads=threads, loader_workers=0, training_parents=len(indices),
        positive_parents=int((data['eligible'] & v['usable'].any(1)).sum()),
        parameter_count=sum(p.numel() for p in model.parameters()),
        predictor_parameter_count=sum(p.numel() for p in predictors.parameters()),
        teacher_parameter_count=sum(p.numel() for p in target.parameters()),
        wall_seconds=time.monotonic()-start, process_cpu_seconds=time.process_time()-cpu,
        assumptions='E021 or explicit E019 encoder/views/exposure; reliable static marker/context constraints; side forwards have no depth evidence; no truth/taxonomy; missing depth abstains'))
    save_arrays(out/'reference.npz', dict(ids=data['ids'], features=values, evidence=valid),
        dict(kind='embeddings', mode='relational_pre_save_reference', samples=meta['samples'],
        features_sha256=digest(features), checkpoint_sha256=digest(out/'checkpoint.pt')))



def embed(features, views, tokens, frozen, pairs_path, checkpoint, output, threads):
    """Strictly reload all checkpoint modules and demand exact same-runtime vectors."""
    configure_torch(threads)
    data, meta, v, vm = load(features, views)
    path = Path(checkpoint)
    receipt = json.loads(path.with_suffix('.json').read_text())
    if receipt['sha256'] != digest(path):
        raise ValueError('Context checkpoint bytes differ')
    saved = torch.load(path, weights_only=True, map_location='cpu')
    policy(saved['config']['relational'])
    if (saved['kind'] != 'relational_checkpoint' or saved['version'] != 1 or saved['samples'] != meta['samples']
            or saved['training_features_sha256'] != digest(features) or saved['training_views_sha256'] != digest(views)
            or saved['training_tokens_sha256'] != digest(Path(tokens)/'tokens.json')
            or saved['training_frozen_sha256'] != (digest(Path(frozen)/'bank.json') if 'hybrid' in saved['config'] else None)
            or saved['training_pairs_sha256'] != digest(Path(pairs_path)/'cache.json')
            or any(saved[k] != receipt[k] for k in ['kind', 'version', 'config', 'transform', 'samples',
                'ema_updates', 'training_features_sha256', 'training_views_sha256', 'training_tokens_sha256','training_frozen_sha256','training_pairs_sha256'])):
        raise ValueError('Context checkpoint/source/schema differs')
    validate_policy({k: value for k, value in saved['config'].items() if k not in ('context','hybrid','relational')}, vm['policy'])
    if saved['config']['context'] != context_policy() or ('hybrid' in saved['config'] and saved['config']['hybrid'] != hybrid_policy()):
        raise ValueError('Context reload policy differs')
    load_pairs(pairs_path, features)
    bank = make_bank(tokens, frozen, features, views, data, meta, v, saved['config'])
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
        dict(kind='embeddings', mode='relational_online_unit_sphere', samples=meta['samples'],
        features_sha256=digest(features), checkpoint_sha256=digest(path), reload_exact=True,
        tokens_manifest_sha256=saved['training_tokens_sha256'],
        frozen_manifest_sha256=saved['training_frozen_sha256'], pair_manifest_sha256=saved['training_pairs_sha256'],
        metric='unit-sphere cosine/equivalent Euclidean; no post-learning transform'))
