"""A bounded taxonomy residual around immutable E031 multiview learning.

Taxonomic conditional reconstruction can share coarse biological context while a
fixed-vector anchor retains within-taxon distinctions. Parents without usable
classifier evidence have an exact intrinsic fallback. Benchmark-unknown origin is
a separate evaluation state. This is reference-assisted learning, not a truth
classifier.
"""
from pathlib import Path
import time

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from ..context.tokens import binding
from ..io import emit, save_arrays, write_json
from ..model import configure_torch
from ..bootstrap.model import state_digest
from ..candidate.model import transform
from ..multiview.positive import geometry
from .cache import read

DEFAULT = dict(version=1, seed=11, epochs=20, batch_size=256, hidden=64, taxonomy_width=16,
    learning_rate=.001, weight_decay=.0001, taxonomy_dropout=.25, residual_cap=.25,
    hierarchy_weight=1., anchor_weight=1., view_weight=.25,
    composition_weight=.1, parent_depth_weight=.05,
    intrinsic='frozen_E031_online_actual_parent_and_crop_heads', unknown='exact_intrinsic_fallback',
    taxonomy='partial_parent_context_not_crop_measurement', confidence='uncalibrated_ORF_support_proxy',
    objective='conditional_sibling_CE_available_views_anchor_and_modality_reconstruction',
    negative_policy='no_taxon_must_links_or_cannot_links', teacher_proposals='unchanged_E031_mode_ancestry')


def policy(value=None):
    """Refuse unannounced tuning, type coercion or per-community taxonomy policies."""
    value = DEFAULT if value is None else value
    if value != DEFAULT or any(type(value[k]) is not type(x) for k, x in DEFAULT.items()):
        raise ValueError('Unfrozen taxonomy adapter policy')
    return dict(value)


class Encoder(nn.Module):
    """Fuse four explicit branches and return unit vectors or exact fallback."""

    def __init__(self, dimensions, samples, tree):
        super().__init__(); h = DEFAULT['hidden']; w = DEFAULT['taxonomy_width']
        branch = lambda n: nn.Sequential(nn.Linear(n, h), nn.LayerNorm(h), nn.GELU())
        self.intrinsic = branch(2*dimensions); self.composition = branch(136)
        self.depth = branch(samples+1); self.taxa = nn.Embedding(len(tree.nodes), w, padding_idx=0)
        self.taxonomy = branch(w+7)
        self.residual = nn.Linear(4*h, dimensions, bias=False); nn.init.zeros_(self.residual.weight)
        self.composition_decoder = nn.Linear(dimensions, 136)
        self.depth_decoder = nn.Linear(dimensions, samples) if samples else None
        self.rank_projection = nn.ModuleList([nn.Linear(dimensions, w, bias=False) for _ in range(7)])
        self.label_vectors = nn.Embedding(len(tree.nodes), w, padding_idx=0)
        self.label_bias = nn.Embedding(len(tree.nodes), 1, padding_idx=0)

    def forward(self, fused, sequence, composition, depth, depth_signal, paths, confidence, keep):
        """Use the inherited positive-depth gate; unknown taxonomy returns exact base.

        `depth_signal` means a positive parent profile, not measurement presence.
        Measured all-zero rows remain in the original depth/zero-depth arrays.
        """
        if (paths.shape != (len(fused), 7) or confidence.shape != (len(fused),)
                or depth_signal.dtype != torch.bool or keep.dtype != torch.bool):
            raise ValueError('Malformed taxonomy encoder axes/masks')
        known = paths != 0
        tax = (self.taxa(paths)*known[..., None]).sum(1)/known.sum(1).clamp_min(1)[:, None]
        # A dropped/missing annotation contributes neither labels nor rank flags.
        tax = tax*keep[:, None]; flags = known.to(fused.dtype)*keep[:, None]
        dep = torch.cat([depth*depth_signal[:, None], depth_signal[:, None].to(depth.dtype)], 1)
        hidden = torch.cat([self.intrinsic(torch.cat([fused, sequence], 1)),
                            self.composition(composition), self.depth(dep),
                            self.taxonomy(torch.cat([tax, flags], 1))], 1)
        raw = torch.tanh(self.residual(hidden))
        delta = DEFAULT['residual_cap']*raw/raw.norm(dim=1, keepdim=True).clamp_min(1)
        gate = confidence*keep*known.any(1)
        updated = F.normalize(fused+gate[:, None]*delta, dim=1)
        return torch.where((gate > 0)[:, None], updated, fused)


def hierarchy_loss_reference(model, vectors, paths, tree, chunk=2048):
    """Retain the clear slow expression for independent numerical contracts.

    Each observed rank contributes equally within a row. Unknown ranks contribute
    zero. No leaf or lineage is fabricated for a partial annotation. Chunked exact
    logsumexp avoids batch-by-all-taxa logits, with gradients through every sibling.
    """
    result = vectors.sum(1)*0; count = (paths != 0).sum(1).clamp_min(1)
    for rank in range(7):
        use = paths[:, rank] != 0
        if not use.any(): continue
        positions = torch.nonzero(use).ravel(); nodes = paths[use, rank]
        parents = np.array([tree.nodes[int(n)]['parent'] for n in nodes.detach().cpu().tolist()])
        for parent in np.unique(parents):
            select = positions[torch.from_numpy(parents == parent).to(positions.device)]
            projected = model.rank_projection[rank](vectors[select])
            wanted = paths[select, rank]
            chosen = (projected*model.label_vectors(wanted)).sum(1)+model.label_bias(wanted).ravel()
            candidates = tree.children[int(parent)]; normalizer = None
            for at in range(0, len(candidates), chunk):
                ids = torch.tensor(candidates[at:at+chunk], dtype=torch.long, device=vectors.device)
                logits = projected@model.label_vectors(ids).T+model.label_bias(ids).ravel()
                part = torch.logsumexp(logits, 1)
                normalizer = part if normalizer is None else torch.logaddexp(normalizer, part)
            result = result.index_add(0, select, (normalizer-chosen)/count[select])
    return result


def hierarchy_loss(model, vectors, paths, tree, chunk=2048):
    """Evaluate the same conditional CE with one global label-table lookup.

    Repeated dense EmbeddingBackward calls allocate the entire reference table
    once per parent group. Gather the union of required sibling nodes once,
    then index that small differentiable matrix. Every sibling remains in the
    exact denominator; there is no sampled-negative or hierarchy approximation.
    Per-group projection/reduction order matches the reference expression.
    """
    result=vectors.sum(1)*0;count=(paths!=0).sum(1).clamp_min(1);groups=[];candidates=[]
    for rank in range(7):
        use=paths[:,rank]!=0
        if not use.any():continue
        positions=torch.nonzero(use).ravel();nodes=paths[use,rank]
        parents=np.array([tree.nodes[int(n)]['parent']for n in nodes.detach().cpu().tolist()])
        for parent in np.unique(parents):
            select=positions[torch.from_numpy(parents==parent).to(positions.device)]
            siblings=np.asarray(tree.children[int(parent)],np.int64)
            groups.append((rank,select,siblings));candidates.append(siblings)
    if not groups:return result
    unique=np.unique(np.concatenate(candidates));ids=torch.from_numpy(unique).to(vectors.device)
    weights=model.label_vectors(ids);bias=model.label_bias(ids).ravel()
    for rank,select,siblings in groups:
        projected=model.rank_projection[rank](vectors[select]);wanted=paths[select,rank]
        positions=torch.from_numpy(np.searchsorted(unique,wanted.detach().cpu().numpy())).to(vectors.device)
        chosen=(projected*weights[positions]).sum(1)+bias[positions];normalizer=None
        for at in range(0,len(siblings),chunk):
            indices=torch.from_numpy(np.searchsorted(unique,siblings[at:at+chunk])).to(vectors.device)
            logits=projected@weights[indices].T+bias[indices]
            part=torch.logsumexp(logits,1)
            normalizer=part if normalizer is None else torch.logaddexp(normalizer,part)
        result=result.index_add(0,select,(normalizer-chosen)/count[select])
    return result


def infer(model, d, a, ix, base, values, state, enabled=True):
    """Infer parents in unchanged unit geometry; preserve every inactive DNA row."""
    s, dep = transform(d['tnf'], d['depth'], d['depth_evidence'], state)
    out = base['features'].copy(); rows = ix['rows']; model.eval()
    with torch.inference_mode():
        for at in range(0, len(rows), 256):
            pos = np.arange(at, min(at+256, len(rows))); selected = rows[pos]
            args = [values[pos, 0, 0].copy(), values[pos, 0, 1].copy(), s[selected], dep[selected],
                    d['depth_evidence'][selected], a['paths'][selected].astype(np.int64),
                    a['confidence'][selected], np.full(len(selected), enabled, bool)]
            out[selected] = model(*[torch.from_numpy(x) for x in args]).numpy()
    inactive = np.ones(len(d['ids']), bool); inactive[rows] = False
    if not np.array_equal(out[inactive], base['features'][inactive]): raise ValueError('Unknown/excluded fallback changed')
    if not enabled and not np.array_equal(out, base['features']): raise ValueError('Disabled taxonomy is not exact fallback')
    if not np.isfinite(out).all() or not np.allclose(np.linalg.norm(out[base['evidence']], axis=1), 1, rtol=0, atol=1e-6):
        raise ValueError('Taxonomy inference unit geometry differs')
    return out


def train(features, views, cache, annotations, output, threads=4, engineering_epochs=None):
    """Fit only new adapter/decoder parameters, keeping all E031 state immutable.

    Every eligible parent occupies an original batch slot. Annotated parents expose
    all available real views. Losses retain the original parent-length denominator;
    low annotation yield cannot silently amplify weak evidence. Empty annotation
    batches do not create Adam moments or decay otherwise unused parameters.
    """
    from ..multiview.views import load
    configure_torch(threads); cfg = policy(); d, a, tree, ix, base, values, m = read(cache, features, annotations)
    _, _, v, vm = load(features, views)
    if m['inputs']['views'] != binding(views): raise ValueError('Adapter actual DNA views differ')
    epochs = cfg['epochs'] if engineering_epochs is None else engineering_epochs
    if engineering_epochs is not None and (len(d['ids']) > 128 or not 1 <= epochs <= 20):
        raise ValueError('Taxonomy engineering override exceeds tiny scope')
    torch.manual_seed(cfg['seed']); rng = np.random.default_rng(cfg['seed'])
    model = Encoder(base['features'].shape[1], d['depth'].shape[1], tree)
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg['learning_rate'], weight_decay=cfg['weight_decay'])
    out = Path(output); out.mkdir(parents=True, exist_ok=False); start = time.monotonic()
    initial = state_digest(model); rows = ix['rows']; lookup = np.full(len(d['ids']), -1, np.int64); lookup[rows] = np.arange(len(rows))
    all_rows = np.flatnonzero(d['eligible'] & base['evidence']); state = m['transform']
    s, dep = transform(d['tnf'], d['depth'], d['depth_evidence'], state)
    weights = np.log1p(np.minimum(d['lengths'], 10000)/500).astype(np.float32)
    history = []; updates = 0
    for epoch in range(epochs):
        model.train(); totals = np.zeros(6); denominator = 0.; seen = exposed = dropped = 0
        for at in range(0, len(all_rows), cfg['batch_size']):
            # One epoch order is generated once, not once per batch.
            if at == 0: order = rng.permutation(all_rows)
            batch = order[at:at+cfg['batch_size']]; seen += len(batch); mass = float(weights[batch].sum()); denominator += mass
            selected = batch[lookup[batch] >= 0]
            if not len(selected): continue
            positions = lookup[selected]; mask = ix['usable'][positions]; owner_np, view_np = np.nonzero(mask)
            selected_views = selected[owner_np]; pos = positions[owner_np]; exposed += len(owner_np)
            sequence = np.empty((len(selected_views), 136), np.float32)
            for k in range(5):
                choose = view_np == k; parents = selected_views[choose]
                if choose.any():
                    sequence[choose] = s[parents] if k == 0 else transform(v['tnf'][parents, k-1], d['depth'][parents], d['depth_evidence'][parents], state)[0]
            keep = rng.random(len(owner_np)) >= cfg['taxonomy_dropout']; dropped += int((~keep).sum())
            args = [values[pos, view_np, 0].copy(), values[pos, view_np, 1].copy(), sequence,
                    dep[selected_views], d['depth_evidence'][selected_views], a['paths'][selected_views].astype(np.int64),
                    a['confidence'][selected_views], keep]
            fused = model(*[torch.from_numpy(x) for x in args])
            labels = torch.from_numpy(a['paths'][selected_views].astype(np.int64))
            h = hierarchy_loss(model, fused, labels, tree)*torch.from_numpy(a['confidence'][selected_views])
            anchor = (fused-torch.from_numpy(values[pos, view_np, 0].copy())).square().sum(1)
            # Parent context target is stopped at this update; no cross-parent
            # taxon positives or marker/taxonomy-selected negative pairs exist.
            with torch.no_grad():
                pargs = [values[positions, 0, 0].copy(), values[positions, 0, 1].copy(), s[selected], dep[selected],
                         d['depth_evidence'][selected], a['paths'][selected].astype(np.int64),
                         a['confidence'][selected], np.ones(len(selected), bool)]
                parent_z = model(*[torch.from_numpy(x) for x in pargs])
            consistency = (fused-parent_z[torch.from_numpy(owner_np)]).square().sum(1)
            target_s = torch.from_numpy(s[selected_views]); comp = (model.composition_decoder(fused)-target_s).square().mean(1)
            depth_loss = fused.sum(1)*0
            usable = np.asarray(state['depth']['std']) > 1e-8
            measured = torch.from_numpy(d['depth_evidence'][selected_views])
            if model.depth_decoder is not None and usable.any() and measured.any():
                diff = F.smooth_l1_loss(model.depth_decoder(fused)[:, usable], torch.from_numpy(dep[selected_views][:, usable]), reduction='none').mean(1)
                depth_loss = diff*measured
            owner = torch.from_numpy(owner_np); counts = torch.bincount(owner, minlength=len(selected)).clamp_min(1)
            parent_weights = torch.from_numpy(weights[selected])/mass
            def reduce(x):
                """Average available views per parent on the original batch mass."""
                return ((torch.zeros(len(selected)).index_add(0, owner, x)/counts)*parent_weights).sum()
            components = [reduce(x) for x in (h, anchor, consistency, comp, depth_loss)]
            total = sum(w*x for w, x in zip([cfg['hierarchy_weight'], cfg['anchor_weight'], cfg['view_weight'], cfg['composition_weight'], cfg['parent_depth_weight']], components))
            if not torch.isfinite(total): raise ValueError('Nonfinite taxonomy loss')
            optimizer.zero_grad(set_to_none=True); total.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in model.parameters()): raise ValueError('Nonfinite taxonomy gradient')
            optimizer.step(); updates += 1; totals += np.array([total.item()]+[x.item() for x in components])*mass
        result = infer(model, d, a, ix, base, values, state)
        sample = all_rows[np.linspace(0, len(all_rows)-1, min(8192, len(all_rows)), dtype=int)] if len(all_rows) else all_rows
        g = geometry(result[sample], dict(collapse_min_std=.001, collapse_min_rank=2), enforce=False) if len(sample) > 1 else None
        row = dict(epoch=epoch+1, original_parent_slots=seen, available_annotated_views=exposed,
                   annotation_dropped_views=dropped, adapter_updates=updates, geometry=g,
                   losses=dict(zip(['total','hierarchy','anchor','view','composition','parent_depth'], (totals/max(denominator, 1)).tolist())))
        write_json(out/('epoch-%02d.json' % (epoch+1)), row); history.append(row); emit('taxonomy_adapter_epoch', **row)
        if g and g['catastrophic_collapse']: raise ValueError('Taxonomy collapse; retained history refuses fit')
    result = infer(model, d, a, ix, base, values, state)
    infer(model, d, a, ix, base, values, state, False)
    saved = dict(kind='taxonomy_adapter_checkpoint', version=1, policy=cfg, state=model.state_dict(), optimizer=optimizer.state_dict(),
                 initial_state=initial, tree=binding(Path(annotations)/'tree.json'), cache=binding(Path(cache)/'cache.json'),
                 annotations=binding(Path(annotations)/'completed.json'), features=binding(features), views=binding(views),
                 dimensions=base['features'].shape[1], samples=d['depth'].shape[1], updates=updates,
                 torch_rng=torch.get_rng_state(), numpy_rng=rng.bit_generator.state)
    with (out/'checkpoint.pt').open('xb') as stream: torch.save(saved, stream)
    clone = Encoder(saved['dimensions'], saved['samples'], tree)
    reload = torch.load(out/'checkpoint.pt', map_location='cpu', weights_only=True)
    clone.load_state_dict(reload['state'], strict=True)
    copied_optimizer = torch.optim.AdamW(clone.parameters(), lr=cfg['learning_rate'], weight_decay=cfg['weight_decay'])
    copied_optimizer.load_state_dict(reload['optimizer'])
    if state_digest(model) != state_digest(clone) or not np.array_equal(infer(clone, d, a, ix, base, values, state), result):
        raise ValueError('Taxonomy same-runtime reload differs')
    if len(optimizer.state)!=len(copied_optimizer.state):raise ValueError('Taxonomy Adam state population differs')
    for before, after in zip(optimizer.state.values(), copied_optimizer.state.values()):
        if set(before) != set(after) or any(not torch.equal(before[k], after[k]) for k in before): raise ValueError('Taxonomy Adam reload differs')
    save_arrays(out/'embeddings.npz', dict(ids=d['ids'], features=result, evidence=base['evidence']),
        dict(kind='embeddings', mode='hierarchical_taxonomy_adapter_unit_sphere', features_sha256=binding(features)['sha256'],
             checkpoint_sha256=binding(out/'checkpoint.pt')['sha256'], reload_exact=True,
             metric='unit-sphere cosine/equivalent Euclidean; no post-learning transform'))
    receipt = dict(status='PASS', policy=cfg, checkpoint=binding(out/'checkpoint.pt'), cache=binding(Path(cache)/'cache.json'),
        annotations=binding(Path(annotations)/'completed.json'), history=history, engineering_epochs=engineering_epochs,
        wall_seconds=time.monotonic()-start, initial_state=initial, final_state=state_digest(model),
        exact_reload=True, exact_reference_free_fallback=True, old_encoder_refit=False, new_teacher_or_pairs=False, truth_accessed=False)
    write_json(out/'completed.json', receipt); return receipt
