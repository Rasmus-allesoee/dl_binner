"""Restore-only E031 view inference for a new taxonomy adapter.

Every crop uses its actual DNA/context/optional GLM bank. The old encoder is
frozen in eval mode. No optimizer, EMA state, pair proposals or markers are fit.
"""
import json
from pathlib import Path

import numpy as np
import torch

from ..context.tokens import binding
from ..io import digest, emit, save_arrays, write_json
from ..bootstrap.model import state_digest
from ..candidate.model import transform
from ..multiview.arrays import load_arrays
from ..multiview.views import load
from ..relational import model as inherited
from .annotations import read as read_annotations


def restore(checkpoint, features, views, tokens, frozen):
    """Admit complete continuation-state metadata and the full modality ancestry.

    The caller still admits original archive/source/runtime locks before invoking
    this reader. No missing file triggers a regeneration or a different encoder.
    """
    path = Path(checkpoint); receipt = json.loads(path.with_suffix('.json').read_text())
    if receipt['sha256'] != digest(path): raise ValueError('E031 checkpoint bytes differ')
    saved = torch.load(path, map_location='cpu', weights_only=True)
    keys = ['kind', 'version', 'config', 'continuation', 'transform', 'samples', 'inputs', 'inherited_updates', 'added_updates']
    if saved.get('kind') != 'bootstrap_continuation_checkpoint' or saved.get('version') != 1 or any(saved[k] != receipt[k] for k in keys):
        raise ValueError('Not a sealed E031 continuation checkpoint')
    expected = dict(features=binding(features), views=binding(views),
                    view_metadata=binding(Path(views).with_suffix('.json')),
                    tokens=binding(Path(tokens)/'tokens.json'), frozen=binding(Path(frozen)/'bank.json') if frozen else None)
    if any(saved['inputs'][k] != value for k, value in expected.items()):
        raise ValueError('E031 input/GLM ancestry differs')
    data, meta, v, vm = load(features, views); cfg = saved['config']
    if saved['samples'] != meta['samples'] or ('hybrid' in cfg) != (frozen is not None):
        raise ValueError('E031 sample axis or full GLM path differs')
    from ..bootstrap.model import policy
    if saved['continuation'] != policy() or cfg['epochs'] != 20 or cfg['seed'] != 11 or cfg['batch_size'] != 256:
        raise ValueError('E031 source/schedule policy differs')
    model, _, _ = inherited.initialize(len(meta['samples']), cfg)
    model.load_state_dict(saved['model_state'], strict=True); model.requires_grad_(False).eval()
    if state_digest(model) != receipt['final_state']['online']:
        raise ValueError('E031 complete parameter/buffer state differs')
    bank = inherited.make_bank(tokens, frozen, features, views, data, meta, v, cfg)
    return model, bank, saved, data, meta, v, vm


def prepare(features, views, tokens, frozen, checkpoint, embeddings, annotations, output, threads=4):
    """Cache new actual view inferences and prove exact retained parent equality.

    Full unannotated/excluded DNA remains in base.npz. Only confidently annotated
    eligible parents need the new five-view matrix. Its disk-backed shape scales
    with annotated parents, not a dense taxon count. The old vectors never change.
    """
    from ..model import configure_torch
    configure_torch(threads)
    model, bank, saved, d, meta, v, vm = restore(checkpoint, features, views, tokens, frozen)
    base, bm = load_arrays(embeddings, 'embeddings'); a, am, tree = read_annotations(annotations, features)
    if bm['features_sha256'] != digest(features) or bm['checkpoint_sha256'] != digest(checkpoint) or not np.array_equal(base['ids'], d['ids']):
        raise ValueError('Retained E031 parent vector/source axes differ')
    state = saved['transform']; cfg = saved['config']; before = state_digest(model)
    parent, depth = transform(d['tnf'], d['depth'], d['depth_evidence'], state)
    rng = torch.get_rng_state().clone()
    reproduced, valid = inherited.infer(model, d, state, cfg, bank, (parent, depth))
    if not np.array_equal(base['features'], reproduced) or not np.array_equal(base['evidence'], valid):
        raise ValueError('E031 same-runtime parent reproduction differs; no tolerance relaxation')
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    rows = np.flatnonzero(d['eligible'] & valid & (a['confidence'] > 0))
    values = np.lib.format.open_memmap(out/'vectors.npy', mode='w+', dtype=np.float32,
                                     shape=(len(rows), 5, 2, cfg['output']))
    values[:] = 0
    usable = np.zeros((len(rows), 5), bool)
    with torch.inference_mode():
        for k in range(5):
            for at in range(0, len(rows), cfg['context']['context_inference_batch_size']):
                positions = np.arange(at, min(at+cfg['context']['context_inference_batch_size'], len(rows)))
                ix = rows[positions]; ok = np.ones(len(ix), bool) if k == 0 else v['usable'][ix, k-1]
                positions, ix = positions[ok], ix[ok]
                if not len(ix): continue
                sequence = parent[ix] if k == 0 else transform(v['tnf'][ix, k-1], d['depth'][ix], d['depth_evidence'][ix], state)[0]
                args = inherited.forward_args(sequence, depth[ix], d['depth_evidence'][ix], bank, ix, np.full(len(ix), k, np.int64), state, cfg)
                result = model(*args)
                good = (result[0].norm(dim=1) > 1e-12).numpy()
                values[positions, k] = np.stack([x.numpy() for x in result], 1)
                usable[positions, k] = good
            emit('taxonomy_actual_view_cache', view=k, annotated_parents=len(rows))
    values.flush()
    if state_digest(model) != before or not torch.equal(rng, torch.get_rng_state()):
        raise ValueError('Frozen E031 view reader changed state/RNG')
    # Parent equality can be affected by a different GEMM batch shape. Native
    # reproduction above uses the original full-parent batching and is exact.
    # Cache parent slots use those exact admitted fused vectors; the sequence
    # head and crops are actual new frozen forwards, never a crop fallback.
    values[:, 0, 0] = base['features'][rows]; values.flush()
    save_arrays(out/'index.npz', dict(ids=d['ids'], rows=rows, usable=usable), dict(kind='taxonomy_view_index'))
    save_arrays(out/'base.npz', base, bm)
    receipt = dict(kind='taxonomy_frozen_view_cache', version=1, samples=meta['samples'],
        inputs=dict(features=binding(features), views=binding(views), tokens=binding(Path(tokens)/'tokens.json'),
                    frozen=binding(Path(frozen)/'bank.json') if frozen else None,
                    checkpoint=binding(checkpoint), checkpoint_metadata=binding(Path(checkpoint).with_suffix('.json')),
                    retained=binding(embeddings), annotations=binding(Path(annotations)/'completed.json')),
        files={n: binding(out/n) for n in ['vectors.npy', 'index.npz', 'index.json', 'base.npz', 'base.json']},
        config=cfg, transform=state, encoder_state_sha256=before, exact_native_parent_reproduction=True,
        actual_crop_inference=True, parent_taxonomy_and_depth_context=True, old_encoder_refit=False, truth_accessed=False)
    write_json(out/'cache.json', receipt); return receipt


def read(folder, features, annotations):
    """Read mmap views under their exact source/annotation/axis contract."""
    root = Path(folder); m = json.loads((root/'cache.json').read_text())
    if m.get('kind') != 'taxonomy_frozen_view_cache' or m.get('version') != 1 or any(binding(root/n) != b for n, b in m['files'].items()):
        raise ValueError('Frozen taxonomy view cache bytes differ')
    if m['inputs']['features'] != binding(features) or m['inputs']['annotations'] != binding(Path(annotations)/'completed.json'):
        raise ValueError('Frozen view/annotation source differs')
    d, meta = load(features); a, am, tree = read_annotations(annotations, features)
    ix, _ = load_arrays(root/'index.npz', 'taxonomy_view_index'); base, bm = load_arrays(root/'base.npz', 'embeddings')
    values = np.load(root/'vectors.npy', mmap_mode='r', allow_pickle=False)
    if (bm.get('features_sha256')!=binding(features)['sha256'] or bm.get('checkpoint_sha256')!=m['inputs']['checkpoint']['sha256']
            or base['features'].shape!=(len(d['ids']),m['config']['output']) or base['features'].dtype!=np.float32
            or base['evidence'].shape!=(len(d['ids']),) or base['evidence'].dtype!=bool
            or (base['evidence']&~d['eligible']).any() or not np.isfinite(base['features']).all()
            or m.get('actual_crop_inference')is not True or m.get('exact_native_parent_reproduction')is not True):
        raise ValueError('Frozen intrinsic source/geometry contract differs')
    rows = np.flatnonzero(d['eligible'] & base['evidence'] & (a['confidence'] > 0))
    if (not np.array_equal(ix['ids'], d['ids']) or not np.array_equal(base['ids'], d['ids'])
            or not np.array_equal(ix['rows'], rows) or values.shape != (len(rows), 5, 2, base['features'].shape[1])
            or values.dtype != np.float32 or ix['usable'].shape != (len(rows), 5) or ix['usable'].dtype!=bool
            or not ix['usable'][:, 0].all() or m['samples'] != meta['samples']):
        raise ValueError('Frozen view full axes differ')
    for at in range(0, len(rows), 4096):
        z = values[at:at+4096]; good = ix['usable'][at:at+4096]
        if not np.isfinite(z).all() or not np.allclose(np.linalg.norm(z[good], axis=-1), 1, rtol=0, atol=1e-6):
            raise ValueError('Frozen view unit geometry differs')
        if np.any(z[~good]!=0):raise ValueError('Unavailable crop carries invented vectors')
    return d, a, tree, ix, base, values, m
