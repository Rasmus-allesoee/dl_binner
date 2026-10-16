"""Modality-specific CPU encoder with real-window and composition auxiliary loss.

All training/inference/grouping vectors inhabit the same unit sphere. Saved
statistics and sample order are applied without refitting during reload.
"""
import json
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from ..io import digest, emit, save_arrays, write_json, load_arrays
from ..model import configure_torch, batches, nt_xent
from .views import load


class Encoder(nn.Module):
    """Encode composition/depth separately, fuse them, and expose a sequence head."""
    def __init__(self, samples, cfg):
        super().__init__()
        self.sequence = nn.Sequential(nn.Linear(136, cfg['sequence_hidden']),
            nn.LayerNorm(cfg['sequence_hidden']), nn.ReLU(),
            nn.Linear(cfg['sequence_hidden'], cfg['sequence_output']), nn.ReLU())
        self.sequence_head = nn.Linear(cfg['sequence_output'], cfg['output'])
        self.depth = (nn.Sequential(nn.Linear(samples, cfg['depth_hidden']),
            nn.LayerNorm(cfg['depth_hidden']), nn.ReLU(),
            nn.Linear(cfg['depth_hidden'], cfg['depth_hidden']), nn.ReLU()) if samples else None)
        width = cfg['sequence_output']+(cfg['depth_hidden'] if samples else 0)
        self.fusion = nn.Sequential(nn.Linear(width, cfg['fusion_hidden']),
            nn.LayerNorm(cfg['fusion_hidden']), nn.ReLU(), nn.Linear(cfg['fusion_hidden'], cfg['output']))

    def forward(self, composition, depth, depth_evidence):
        """Return fused/sequence unit vectors; all-zero depth has no branch bias."""
        s = self.sequence(composition)
        parts = [F.normalize(s, dim=1)]
        if self.depth is not None:
            d = F.normalize(self.depth(depth), dim=1)*depth_evidence[:, None]
            parts.append(d)
        return F.normalize(self.fusion(torch.cat(parts, 1)), dim=1), F.normalize(self.sequence_head(s), dim=1)


def fit_transform(data):
    """Fit label-free full-parent transforms; retain explicit depth zeros/magnitude."""
    state = {}
    for key, values in (('tnf', np.sqrt(data['tnf'])), ('depth', np.log1p(data['depth']))):
        x = values[data['eligible']].astype(np.float64)
        if len(x) < 2:
            raise ValueError('Candidate requires at least two eligible parents')
        state[key] = dict(mean=x.mean(0).tolist(), std=x.std(0).tolist())
    state['policy'] = 'sqrt TNF fitted parent z-score and row L2; log1p measured parent depth z-score / sqrt(S), all-zero depth block zero'
    return state


def transform(tnf, depth, depth_evidence, state):
    """Apply saved transforms to either parent or real-window TNF with parent depth."""
    result = []
    for key, values in (('tnf', np.sqrt(tnf)), ('depth', np.log1p(depth))):
        x = np.asarray(values, dtype=np.float64)
        mean, std = (np.array(state[key][v], dtype=np.float64) for v in ('mean', 'std'))
        if (x.ndim != 2 or x.shape[1:] != mean.shape or std.shape != mean.shape
                or not np.isfinite(x).all() or not np.isfinite(mean).all()
                or not np.isfinite(std).all() or (std < 0).any()):
            raise ValueError('Invalid candidate transform axes/statistics')
        z = np.zeros_like(x)
        usable = std > 1e-8
        z[:, usable] = (x[:, usable]-mean[usable])/std[usable]
        if key == 'tnf':
            z /= np.maximum(np.linalg.norm(z, axis=1, keepdims=True), 1e-12)
        else:
            z[~depth_evidence] = 0
            z /= np.sqrt(max(x.shape[1], 1))
        result.append(z.astype(np.float32))
    return result


def infer(model, data, state, cfg):
    """Infer all eligible parents with no output-space rescaling or stochastic views."""
    s, d = transform(data['tnf'], data['depth'], data['depth_evidence'], state)
    valid = data['eligible'] & ((np.linalg.norm(s, axis=1) > 1e-12) | data['depth_evidence'])
    output = np.zeros((len(s), cfg['output']), np.float32)
    model.eval()
    with torch.inference_mode():
        for selected in batches(np.flatnonzero(valid), cfg['inference_batch_size']):
            if len(selected):
                output[selected] = model(torch.from_numpy(s[selected]), torch.from_numpy(d[selected]),
                    torch.from_numpy(data['depth_evidence'][selected]))[0].numpy()
    if not np.isfinite(output).all():
        raise ValueError('Nonfinite candidate inference')
    return output, valid & (np.linalg.norm(output, axis=1) > 1e-12)


def train(features, views, output, cfg, threads):
    """Train one fixed schedule, retain reference inference and restricted checkpoint."""
    configure_torch(threads)
    data, meta, v, vm = load(features, views)
    indices = np.flatnonzero(v['trainable'])
    if len(indices) < 2:
        raise ValueError('Need at least two parents with four usable real windows')
    state = fit_transform(data)
    transformed = []
    for j in range(4):
        transformed.append(transform(v['tnf'][:, j], data['depth'], data['depth_evidence'], state)[0])
    sequence = np.stack(transformed, 1)
    depth = transform(data['tnf'], data['depth'], data['depth_evidence'], state)[1]
    torch.manual_seed(cfg['seed'])
    rng = np.random.default_rng(cfg['seed'])
    model = Encoder(len(meta['samples']), cfg)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg['learning_rate'], weight_decay=cfg['weight_decay'])
    start, cpu = time.monotonic(), time.process_time()
    history = []
    for epoch in range(cfg['epochs']):
        model.train()
        seen, total, seq_total = 0, 0., 0.
        for selected in batches(rng.permutation(indices), cfg['batch_size']):
            pairs = rng.integers(0, 2, size=len(selected))*2
            a = torch.from_numpy(sequence[selected, pairs])
            b = torch.from_numpy(sequence[selected, pairs+1])
            d = torch.from_numpy(depth[selected])
            mask = torch.from_numpy(data['depth_evidence'][selected])
            first, sa = model(a, d, mask)
            second, sb = model(b, d, mask)
            sequence_loss = nt_xent(sa, sb, cfg['temperature'])
            loss = nt_xent(first, second, cfg['temperature'])+cfg['sequence_loss_weight']*sequence_loss
            if not torch.isfinite(loss):
                raise ValueError('Nonfinite candidate loss')
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in model.parameters()):
                raise ValueError('Nonfinite candidate gradient')
            optimizer.step()
            seen += len(selected)
            total += float(loss.detach())*len(selected)
            seq_total += float(sequence_loss.detach())*len(selected)
        if seen != len(indices):
            raise RuntimeError('Training parent coverage changed')
        h = dict(epoch=epoch+1, parents_seen=seen, loss=total/seen,
                 sequence_loss=seq_total/seen, wall_seconds=time.monotonic()-start)
        history.append(h)
        emit('candidate_epoch', **h)
    values, valid = infer(model, data, state, cfg)
    out = Path(output)
    checkpoint = dict(kind='candidate_checkpoint', version=1, config=cfg, transform=state,
        samples=meta['samples'], model_state=model.state_dict(), optimizer_state=optimizer.state_dict(),
        training_features_sha256=digest(features), training_views_sha256=digest(views))
    with (out/'checkpoint.pt').open('xb') as stream:
        torch.save(checkpoint, stream)
    write_json(out/'checkpoint.json', dict(kind='candidate_checkpoint', version=1,
        sha256=digest(out/'checkpoint.pt'), config=cfg, transform=state, samples=meta['samples'],
        training_features_sha256=digest(features), training_views_sha256=digest(views),
        training_parents=len(indices), history=history, threads=threads, loader_workers=0,
        parameter_count=sum(p.numel() for p in model.parameters()),
        wall_seconds=time.monotonic()-start, process_cpu_seconds=time.process_time()-cpu,
        assumption='Co-genomic negatives/chimeric positives unresolved; windows share measured parent depth; no labels/markers used'))
    save_arrays(out/'reference.npz', dict(ids=data['ids'], features=values, evidence=valid),
        dict(kind='embeddings', mode='candidate_pre_save_reference', samples=meta['samples'],
             features_sha256=digest(features), checkpoint_sha256=digest(out/'checkpoint.pt')))


def embed(features, checkpoint, output, threads):
    """Independently reload tensor-only CPU checkpoint; demand exact reference parity."""
    configure_torch(threads)
    data, meta = load(features)
    path = Path(checkpoint)
    receipt = json.loads(path.with_suffix('.json').read_text())
    if receipt['sha256'] != digest(path) or receipt['training_features_sha256'] != digest(features):
        raise ValueError('Candidate checkpoint/source bytes mismatch')
    saved = torch.load(path, weights_only=True, map_location='cpu')
    if (saved['kind'] != 'candidate_checkpoint' or saved['version'] != 1
            or saved['samples'] != meta['samples'] or saved['config'] != receipt['config']
            or saved['transform'] != receipt['transform']
            or saved['training_features_sha256'] != digest(features)
            or saved['training_views_sha256'] != receipt['training_views_sha256']):
        raise ValueError('Candidate checkpoint schema/sample/transform mismatch')
    model = Encoder(len(meta['samples']), saved['config'])
    model.load_state_dict(saved['model_state'], strict=True)
    if any(not torch.isfinite(p).all() for p in model.parameters()):
        raise ValueError('Nonfinite candidate checkpoint')
    values, valid = infer(model, data, saved['transform'], saved['config'])
    reference, rm = load_arrays(path.parent/'reference.npz', 'embeddings')
    if (rm['checkpoint_sha256'] != digest(path) or
            any(not np.array_equal(reference[k], v) for k, v in
                (('ids', data['ids']), ('features', values), ('evidence', valid)))):
        raise ValueError('Candidate reload differs from pre-save inference')
    save_arrays(output, dict(ids=data['ids'], features=values, evidence=valid),
        dict(kind='embeddings', mode='candidate_learned_unit_sphere', samples=meta['samples'],
            features_sha256=digest(features), checkpoint_sha256=digest(path), reload_exact=True,
            metric='unit-sphere cosine/equivalent Euclidean; no post-learning transform'))
