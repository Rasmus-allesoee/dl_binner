"""Own compact contrastive encoder, fitted transforms and restricted checkpoints."""
import json
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from threadpoolctl import threadpool_info

from .io import digest, emit, load_arrays, save_arrays, validate_features, write_json


class Encoder(nn.Module):
    """Map fitted composition/depth features through a hidden layer to unit vectors."""
    def __init__(self, width, hidden=128, output=64):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(width, hidden), nn.ReLU(), nn.Linear(hidden, output))

    def forward(self, values):
        """Return L2-normalized learned embeddings, keeping zero-output detection possible."""
        return F.normalize(self.layers(values), dim=1, eps=1e-12)


def configure_torch(threads):
    """Reconcile native CPU pools; use no data loader/child workers or GPU."""
    torch.set_num_threads(threads)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    if any(p['num_threads'] > threads for p in threadpool_info()):
        raise RuntimeError('Numerical library pool exceeds requested CPU budget')


def fit_transform(data):
    """Fit label-free population z-scores on eligible rows for each input modality."""
    mask = data['eligible']
    if mask.sum() < 2:
        raise ValueError('Contrastive training needs at least two eligible contigs')
    state = {}
    for name, values in (('tnf', data['tnf']), ('depth', np.log1p(data['depth']))):
        mean = values[mask].astype(np.float64).mean(0)
        std = values[mask].astype(np.float64).std(0)
        state[name] = dict(mean=mean.tolist(), std=std.tolist(), usable=(std > 1e-8).tolist())
    state['policy'] = 'eligible population z-score; TNF row L2; depth scaled by sqrt(sample count), preserving magnitude; all-zero depth block stays zero'
    return state


def transform(data, state):
    """Apply saved statistics without refitting; preserve no-evidence/zero-depth rows.

    Normalize TNF directions and scale depth by sqrt(sample count), preserving
    scalar/multisample magnitude. Whole-row zero depth is zeroed after centering; partial
    zero samples remain real observations, with their original masks retained.
    """
    blocks = []
    for name, raw in (('tnf', data['tnf']), ('depth', np.log1p(data['depth']))):
        raw = raw.astype(np.float64)
        fitted = state[name]
        mean, std, usable = np.array(fitted['mean']), np.array(fitted['std']), np.array(fitted['usable'], dtype=bool)
        if raw.shape[1] != len(mean) or len(std) != len(mean) or len(usable) != len(mean):
            raise ValueError('Transform input dimensions mismatch')
        if not np.isfinite(mean).all() or not np.isfinite(std).all() or (std < 0).any() or not np.array_equal(usable, std > 1e-8):
            raise ValueError('Invalid fitted transform statistics')
        z = np.zeros_like(raw)
        z[:, usable] = (raw[:, usable]-mean[usable])/std[usable]
        z[~data['eligible']] = 0
        if name == 'depth':
            z[~data['depth_evidence']] = 0
        if name == 'tnf':
            norms = np.linalg.norm(z, axis=1)
            nonzero = norms > 1e-12
            z[nonzero] /= norms[nonzero, None]
        elif z.shape[1]:
            z /= np.sqrt(z.shape[1])
        blocks.append(z)
    x = np.concatenate(blocks, axis=1).astype(np.float32)
    valid = data['eligible'] & (np.linalg.norm(x, axis=1) > 1e-12)
    return x, valid


def nt_xent(first, second, temperature):
    """Symmetric NT-Xent; same-ID views positive, other in-batch IDs negative.

    The diagonal is excluded. Different IDs can be co-genomic false negatives;
    truth does not resolve or select them in this implementation.
    """
    if first.shape != second.shape or len(first) < 2 or temperature <= 0:
        raise ValueError('Invalid contrastive batch or temperature')
    n = len(first)
    z = torch.cat((first, second))
    logits = z@z.T/temperature
    logits = logits.masked_fill(torch.eye(2*n, dtype=torch.bool), float('-inf'))
    target = (torch.arange(2*n)+n) % (2*n)
    return F.cross_entropy(logits, target)


def batches(order, size):
    """Cover every eligible ID once per epoch; merge a singleton tail, never drop it."""
    parts = [order[start:start+size] for start in range(0, len(order), size)]
    if len(parts) > 1 and len(parts[-1]) == 1:
        parts[-2] = np.concatenate((parts[-2], parts[-1]))
        parts.pop()
    return parts


def forward_all(model, x, valid, batch_size):
    """Embed all rows in fixed CPU batches; invalid evidence remains an explicit zero."""
    result = np.zeros((len(x), model.layers[-1].out_features), dtype=np.float32)
    model.eval()
    with torch.inference_mode():
        indices = np.flatnonzero(valid)
        for start in range(0, len(indices), batch_size):
            selected = indices[start:start+batch_size]
            result[selected] = model(torch.from_numpy(x[selected])).numpy()
    if not np.isfinite(result).all():
        raise ValueError('Nonfinite learned embeddings')
    return result


def validate_config(config):
    """Reject unsupported or invalid initial training settings, without a tuning grid."""
    expected = {'hidden', 'output', 'mask_probability', 'temperature', 'learning_rate',
                'batch_size', 'epochs', 'seed', 'inference_batch_size', 'weight_decay'}
    if set(config) != expected:
        raise ValueError('Training configuration keys mismatch')
    for name in ('hidden', 'output', 'batch_size', 'epochs', 'inference_batch_size'):
        if not isinstance(config[name], int) or config[name] < (2 if name == 'batch_size' else 1):
            raise ValueError('Invalid positive integer training setting')
    if not 0 <= config['mask_probability'] < 1 or not np.isfinite(config['temperature']) or config['temperature'] <= 0:
        raise ValueError('Invalid masking/temperature setting')
    if not np.isfinite(config['learning_rate']) or config['learning_rate'] <= 0:
        raise ValueError('Invalid optimizer learning rate')
    if not np.isfinite(config['weight_decay']) or config['weight_decay'] < 0 or not isinstance(config['seed'], int) or config['seed'] < 0:
        raise ValueError('Invalid weight decay/seed')


def train(features_path, config_path, output, threads):
    """Train once, save checkpoint/transforms, and retain pre-save inference for parity.

    No truth is read. Publish complete per-epoch coverage/loss and process timing;
    operational correctness does not imply improved biological grouping.
    """
    output = Path(output)
    if any(p.exists() for p in (output, output.with_suffix('.json'), output.with_suffix('.reference.npz'), output.with_suffix('.reference.json'))):
        raise FileExistsError('Fresh checkpoint and reference paths required')
    configure_torch(threads)
    config = json.loads(Path(config_path).read_text())
    validate_config(config)
    data, meta = load_arrays(features_path, 'features')
    validate_features(data, meta)
    state = fit_transform(data)
    x, valid = transform(data, state)
    if valid.sum() < 2:
        raise ValueError('Insufficient nonconstant transformed evidence to train')
    torch.manual_seed(config['seed'])
    rng = np.random.default_rng(config['seed'])
    model = Encoder(x.shape[1], config['hidden'], config['output'])
    optimizer = torch.optim.AdamW(model.parameters(), lr=config['learning_rate'],
                                  weight_decay=config['weight_decay'], betas=(0.9, 0.999), eps=1e-8)
    tensor = torch.from_numpy(x)
    indices = np.flatnonzero(valid)
    wall_start, cpu_start = time.monotonic(), time.process_time()
    histories = []
    for epoch in range(config['epochs']):
        model.train()
        total_loss, seen = 0.0, 0
        for selected in batches(rng.permutation(indices), config['batch_size']):
            base = tensor[selected]
            probability = config['mask_probability']
            a = base*(torch.rand_like(base) >= probability)/(1-probability)
            b = base*(torch.rand_like(base) >= probability)/(1-probability)
            loss = nt_xent(model(a), model(b), config['temperature'])
            if not torch.isfinite(loss):
                raise ValueError('Nonfinite contrastive loss')
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in model.parameters()):
                raise ValueError('Nonfinite gradients')
            optimizer.step()
            total_loss += float(loss.detach())*len(selected)
            seen += len(selected)
        if seen != len(indices):
            raise RuntimeError('Epoch did not cover every training ID')
        record = dict(epoch=epoch+1, loss=total_loss/seen, contigs_seen=seen,
                      wall_seconds=time.monotonic()-wall_start)
        histories.append(record)
        emit('epoch_complete', **record)
    learning_seconds = time.monotonic()-wall_start
    learning_cpu = time.process_time()-cpu_start
    if any(not torch.isfinite(p).all() for p in model.parameters()):
        raise ValueError('Nonfinite trained parameters')
    reference = forward_all(model, x, valid, config['inference_batch_size'])
    output = Path(output)
    if output.exists() or output.with_suffix('.json').exists():
        raise FileExistsError('Fresh checkpoint path required')
    output.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = dict(version=1, kind='contrastive_checkpoint', config=config, transform=state,
                      samples=meta['samples'], input_width=x.shape[1], model_state=model.state_dict(),
                      optimizer_state=optimizer.state_dict(), rng_state=torch.get_rng_state(),
                      training_features_sha256=digest(features_path),
                      training_feature_manifest_sha256=digest(Path(features_path).with_suffix('.json')))
    with output.open('xb') as stream:
        torch.save(checkpoint, stream)
    save_arrays(output.with_suffix('.reference.npz'), dict(ids=data['ids'], features=reference,
                evidence=valid & (np.linalg.norm(reference, axis=1) > 1e-12)),
                dict(kind='embeddings', mode='pre_save_reference', checkpoint_sha256=digest(output)))
    write_json(output.with_suffix('.json'), dict(kind='checkpoint', version=1, sha256=digest(output),
        config=config, transform=state, samples=meta['samples'], epochs=histories,
        training_features_sha256=digest(features_path), eligible=int(valid.sum()),
        numerical_threads=threads, torch_interop=1, loader_workers=0,
        parameter_count=sum(p.numel() for p in model.parameters()),
        torch_version=str(torch.__version__), library_pools=threadpool_info(),
        training_wall_seconds=learning_seconds, training_process_cpu_seconds=learning_cpu,
        training_average_cpus=learning_cpu/learning_seconds,
        assumption='Different-ID negatives can be co-genomic; no truth-based correction',
        runtime_imports=dict(torch=torch.__file__, numpy=np.__file__),
        code_sha256=digest(__file__)))
    emit('checkpoint_saved', training_seconds=learning_seconds, features=len(x), trained=int(valid.sum()))


def load_checkpoint(path, samples):
    """Load trusted tensor state with restricted deserialization and schema checks."""
    path = Path(path)
    receipt = json.loads(path.with_suffix('.json').read_text())
    if receipt['kind'] != 'checkpoint' or digest(path) != receipt['sha256']:
        raise ValueError('Checkpoint byte/receipt mismatch')
    checkpoint = torch.load(path, map_location='cpu', weights_only=True)
    if checkpoint.get('version') != 1 or checkpoint.get('kind') != 'contrastive_checkpoint':
        raise ValueError('Unsupported checkpoint contract')
    validate_config(checkpoint['config'])
    if checkpoint['samples'] != samples or checkpoint['input_width'] != 136+len(samples):
        raise ValueError('Checkpoint ordered sample/input schema mismatch')
    cfg = checkpoint['config']
    model = Encoder(checkpoint['input_width'], cfg['hidden'], cfg['output'])
    model.load_state_dict(checkpoint['model_state'], strict=True)
    if any(not torch.isfinite(p).all() for p in model.parameters()):
        raise ValueError('Nonfinite checkpoint parameters')
    return checkpoint, model


def embed(features_path, output, checkpoint_path=None, threads=4):
    """Publish learned checkpoint inference or the complete unlearned control space."""
    data, meta = load_arrays(features_path, 'features')
    validate_features(data, meta)
    if checkpoint_path is None:
        # Sequence-only raw control is exactly the accepted E003 TNF space.
        values = np.concatenate((data['tnf'], np.log1p(data['depth'])), axis=1).astype(np.float32)
        values[~data['eligible']] = 0
        valid = data['eligible'] & (np.linalg.norm(values, axis=1) > 1e-12)
        mode = 'raw_tnf_log1p_depth'
    else:
        configure_torch(threads)
        checkpoint, model = load_checkpoint(checkpoint_path, meta['samples'])
        x, valid = transform(data, checkpoint['transform'])
        values = forward_all(model, x, valid, checkpoint['config']['inference_batch_size'])
        valid &= np.linalg.norm(values, axis=1) > 1e-12
        mode = 'learned_checkpoint'
    save_arrays(output, dict(ids=data['ids'], features=values, evidence=valid),
                dict(kind='embeddings', mode=mode, features_sha256=digest(features_path),
                     feature_manifest_sha256=digest(Path(features_path).with_suffix('.json')),
                     samples=meta['samples'], shape=list(values.shape),
                     checkpoint_sha256=digest(checkpoint_path) if checkpoint_path else None))
    emit('embeddings_ready', mode=mode, contigs=len(values), nonzero_evidence=int(valid.sum()))
