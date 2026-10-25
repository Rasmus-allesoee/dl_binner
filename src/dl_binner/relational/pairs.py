"""Bounded label-free constraints from retained graph, marker and parent contexts.

Proposal work is O(n*k + marker occurrences*8 + calibration size); no new index,
all-pairs graph, transitive pseudo-labels, taxonomy, truth or DNA scan. Every input
row remains in the pair axis even when it supplies no reliable constraint.
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np

from ..context.tokens import binding
from ..io import digest, save_arrays, write_json
from ..multiview.arrays import load_arrays
from ..multiview.views import load
from .evidence import restore, require


def policy(path=None):
    """Read the prospective policy; permit only the declared zero-weight ablation."""
    default = json.loads((Path(__file__).parents[1]/'resources/relational.json').read_text())
    cfg = path if isinstance(path, dict) else json.loads(Path(path).read_text()) if path else default
    require(isinstance(cfg, dict), 'Relational policy must be a JSON object')
    require(all(type(cfg.get(k)) is type(v) for k, v in default.items() if type(v) in (int, list)),
            'Malformed relational policy field types')
    require(set(cfg) == set(default) and all(cfg[k] == v for k, v in default.items() if k != 'loss_weight')
            and type(cfg['loss_weight']) in (int, float) and cfg['loss_weight'] in (0, default['loss_weight']),
            'Unfrozen relation policy; only the predeclared zero-weight control is supported')
    return cfg


def contexts(data, cfg):
    """Build Hellinger TNF and scaled measured-parent depth; missing stays absent."""
    comp = np.sqrt(data['tnf'].astype(np.float64))
    values = np.log1p(data['depth'].astype(np.float64))
    scale = values[data['eligible']].std(0) if len(values[data['eligible']]) else np.zeros(values.shape[1])
    columns = scale > 1e-8
    depth = values[:, columns]/scale[columns]
    available = (data['eligible'] & (data['lengths'] >= cfg['constraint_min_bp']) &
                 (np.linalg.norm(comp, axis=1) > 1e-12) & data['depth_evidence'])
    if int(columns.sum()) < cfg['min_depth_columns']:
        available[:] = False
    return comp, depth, available, dict(depth_column_std=scale.tolist(),
        usable_columns=columns.tolist(), depth_semantics='log1p measured parent means / eligible-column std; no window variance',
        composition_semantics='Hellinger sqrt raw retained TNF')


def calibrate(comp, depth, available, cfg):
    """Select at most 65,536 unordered pairs with an independent fixed sampler."""
    indices = np.flatnonzero(available)
    if len(indices) < 2:
        return np.empty((0, 2), np.int64), np.empty((0, 2)), dict(status='ABSTAIN_MISSING_MEASURED_CONTEXT')
    count = min(cfg['calibration_pairs'], len(indices)*(len(indices)-1)//2)
    if len(indices) <= 256:
        a, b = np.triu_indices(len(indices), 1); pairs = np.stack([indices[a], indices[b]], axis=1)
    else:
        rng = np.random.default_rng(cfg['seed']); chosen = set()
        while len(chosen) < count:
            draws = rng.integers(len(indices), size=(min(count, 8192), 2))
            for a, b in draws:
                if a != b:
                    chosen.add((int(min(indices[a], indices[b])), int(max(indices[a], indices[b]))))
                if len(chosen) == count:
                    break
        pairs = np.array(sorted(chosen), np.int64)
    distances = np.column_stack([np.linalg.norm(x[pairs[:, 0]]-x[pairs[:, 1]], axis=1) for x in [comp, depth]])
    cuts = np.quantile(distances, [cfg['near_quantile'], cfg['far_quantile']], axis=0)
    informative = bool(np.all(np.isfinite(cuts)) and np.all(cuts[1]-cuts[0] > 1e-12))
    return pairs, distances, dict(status='PASS' if informative else 'ABSTAIN_DEGENERATE_CONTEXT',
        near=cuts[0].tolist(), far=cuts[1].tolist(), pairs=len(pairs), seed=cfg['seed'])


def protein_near(a, b, cfg):
    """Veto identical/high-overlap protein kmer sets, without a sequence aligner."""
    if a == b:
        return True
    k = cfg['protein_k']
    x = {a[i:i+k] for i in range(max(0, len(a)-k+1))}
    y = {b[i:i+k] for i in range(max(0, len(b)-k+1))}
    return not x or not y or len(x & y)/len(x | y) >= cfg['protein_near_jaccard']


def choose(data, neighbors, quality, sequences, cfg, audit):
    """Emit one capped static signed pair set and every proposal's decision."""
    ids = data['ids'].tolist(); lookup = {v: i for i, v in enumerate(ids)}
    comp, depth, available, transforms = contexts(data, cfg)
    calibration, distances, cuts = calibrate(comp, depth, available, cfg)
    if cuts['status'] != 'PASS':
        audit.append(dict(reason=cuts['status'], accepted=False))
        return [], calibration, distances, dict(calibration=cuts, transforms=transforms)
    calls = quality['calls']; credible = {k: set(v) for k, v in quality['credible'].items()}
    strong = {lookup[k]: v for k, v in calls.items() if available[lookup[k]]}
    proposals = {}; checked = set()
    def consider(i, j, kind):
        i, j = min(int(i), int(j)), max(int(i), int(j))
        if i == j or (i, j, kind) in checked:
            return
        checked.add((i, j, kind))
        trace = dict(left=ids[i], right=ids[j], sign=kind, accepted=False)
        def reject(reason):
            audit.append(dict(trace, reason=reason)); return
        if not available[i] or not available[j]: return reject('missing_length_or_two_context_evidence')
        ds = np.array([np.linalg.norm(x[i]-x[j]) for x in [comp, depth]])
        trace['distances'] = ds.tolist()
        if kind == 1:
            if not (i in strong or j in strong): return reject('no_strong_marker_endpoint')
            shared = credible.get(ids[i], set()) & credible.get(ids[j], set())
            if shared: return reject('credible_family_conflict_abstain_positive')
            if not np.all(ds <= np.asarray(cuts['near'])+1e-12): return reject('two_context_near_disagreement')
            reliability = max([v['reliability'] for k in [i, j] for v in strong.get(k, {}).values()])
            agreement = np.where(np.asarray(cuts['near']) <= 1e-12, 1.,
                                 np.maximum(0., 1-ds/np.maximum(cuts['near'], 1e-12)))
            weight = reliability*float(np.prod(agreement))
        else:
            shared = sorted(set(strong.get(i, {})) & set(strong.get(j, {})))
            if not shared: return reject('no_strong_shared_family')
            trace['families'] = shared
            if any(protein_near(sequences[strong[i][f]['gene']], sequences[strong[j][f]['gene']], cfg) for f in shared):
                return reject('identical_or_near_protein_abstention')
            if not np.all(ds >= cuts['far']): return reject('two_context_far_disagreement')
            weight = max(strong[i][f]['reliability']*strong[j][f]['reliability'] for f in shared)
        if not np.isfinite(weight) or weight <= 0: return reject('zero_confidence')
        require((i, j) not in proposals, 'Contradictory pair signs survived guards')
        proposals[i, j] = dict(i=i, j=j, sign=kind, weight=float(weight), trace=trace)
    # Only retained reciprocal neighbors; never rebuild or transitively close.
    adjacency = [set(map(int, row[row >= 0])) for row in neighbors]
    for i in sorted(strong):
        for j in sorted(adjacency[i]):
            if i in adjacency[j]: consider(i, j, 1)
    families = defaultdict(list)
    for i, values in strong.items():
        for family in values: families[family].append(i)
    for family, members in sorted(families.items()):
        members.sort(key=lambda i: hashlib.sha256(('family\0'+family+'\0'+ids[i]).encode()).digest())
        for at, i in enumerate(members):
            for offset in cfg['family_offsets']:
                for direction in [-1, 1]:
                    other = at+offset*direction
                    if 0 <= other < len(members): consider(i, members[other], -1)
    degree = np.zeros(len(ids), np.int64); retained = []
    order = sorted(proposals.values(), key=lambda x: (-x['weight'], min(ids[x['i']], ids[x['j']]), max(ids[x['i']], ids[x['j']])))
    # One epoch's original optimizer updates bounds pair work, even on small data.
    cap = int(np.ceil(int(data['eligible'].sum())/256))*cfg['pair_batch_size']
    for value in order:
        i, j = value['i'], value['j']
        if degree[i] >= cfg['max_degree'] or degree[j] >= cfg['max_degree'] or len(retained) >= cap:
            audit.append(dict(value['trace'], reason='degree_or_original_step_budget_abstention'))
        else:
            degree[[i, j]] += 1; retained.append(value)
            audit.append(dict(value['trace'], accepted=True, confidence=value['weight'], reason='retained_soft_constraint'))
    retained.sort(key=lambda x: (x['i'], x['j']))
    return retained, calibration, distances, dict(calibration=cuts, transforms=transforms,
        eligible_context_rows=int(available.sum()), strong_marker_rows=len(strong),
        proposals=len(checked), retained=len(retained), degree_max=int(degree.max(initial=0)),
        sign_counts=dict(Counter(x['sign'] for x in retained)),
        abstention_counts=dict(Counter(x['reason'] for x in audit if not x['accepted'])),
        pair_budget=cap, pair_budget_basis='ceil(all training parents / inherited batch256) * pair_batch_size')


def prepare(features, embeddings, graph, marker_cache, hmm, output, cfg=None):
    """Restore original readers, derive constraints once, and seal every new member."""
    cfg = cfg or policy(); data, metadata = load(features)
    vectors, em = load_arrays(embeddings, 'embeddings'); sparse, gm = load_arrays(graph, 'candidate_sparse_graph')
    ids = data['ids']; n = len(ids); valid = data['eligible'] & vectors['evidence']
    require(np.array_equal(ids, vectors['ids']) and np.array_equal(ids, sparse['ids'])
            and em['features_sha256'] == digest(features) and gm['embedding_sha256'] == digest(embeddings)
            and gm['metric'] == em['metric'],
            'Retained feature/vector/sparse graph binding or full axis differs')
    require(vectors['features'].ndim == 2 and len(vectors['features']) == n and
            np.isfinite(vectors['features']).all() and
            np.allclose(np.linalg.norm(vectors['features'][valid], axis=1), 1, atol=1e-5)
            and not np.any(vectors['features'][~valid]), 'Original unit vectors invalid; no normalization repair')
    neighbors = sparse['neighbors']
    require(neighbors.ndim == 2 and neighbors.shape[0] == n and neighbors.dtype.kind in 'iu'
            and np.all((neighbors >= -1) & (neighbors < n)), 'Malformed actual sparse neighbor rows')
    for i, row in enumerate(neighbors):
        targets = row[row >= 0]
        require(len(set(map(int, targets))) == len(targets) and i not in targets and
                not np.any(~valid[targets]) and (valid[i] or not len(targets)),
                'Sparse neighbor self/duplicate/excluded row')
    edges, weights = sparse['edges'], sparse['weights']
    require(edges.shape == (len(weights), 2) and edges.dtype.kind in 'iu' and
            np.all((edges >= 0) & (edges < n)) and np.isfinite(weights).all()
            and np.all(weights > 0) and np.all(valid[edges]) and np.all(edges[:,0] != edges[:,1])
            and len({tuple(sorted(map(int,e))) for e in edges}) == len(edges),
            'Malformed retained sparse edges/weights')
    quality, sequences = restore(marker_cache, hmm, data, metadata, cfg)
    audit = []; pairs, calibration, distances, summary = choose(data, neighbors, quality, sequences, cfg, audit)
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    arrays = dict(ids=ids, left=np.array([x['i'] for x in pairs], np.int64),
        right=np.array([x['j'] for x in pairs], np.int64), sign=np.array([x['sign'] for x in pairs], np.int8),
        weight=np.array([x['weight'] for x in pairs], np.float32))
    save_arrays(out/'pairs.npz', arrays, dict(kind='relational_pairs', features_sha256=digest(features)))
    np.savez_compressed(out/'calibration.npz', pairs=calibration, distances=distances)
    write_json(out/'quality.json', quality)
    with (out/'decisions.jsonl').open('x') as stream:
        for row in audit: stream.write(json.dumps(row, allow_nan=False, sort_keys=True)+'\n')
    write_json(out/'cache.json', dict(kind='relational_pair_cache', version=1, policy=cfg,
        inputs=dict(features=binding(features), embeddings=binding(embeddings), graph=binding(graph),
                    marker_cache=binding(Path(marker_cache)/'cache.json'), hmm=binding(hmm)),
        full_contigs=n, full_bp=int(data['lengths'].sum()), samples=metadata['samples'],
        summary=summary, files={p.name: binding(p) for p in out.iterdir()},
        truth_accessed=False, native_vectors_untouched=True, no_new_index_detection_or_original_DNA_read=True))
    return load_pairs(out, features)[1]


def load_pairs(path, features):
    """Strict fresh-process cache reader; no partial cache, alias or copy fallback."""
    path = Path(path); receipt = json.loads((path/'cache.json').read_text())
    binding(path/'cache.json')
    require(receipt.get('kind') == 'relational_pair_cache' and receipt.get('version') == 1,
            'Unsupported relational cache')
    # Loss weight is a training-only override, never rewrite accepted pair metadata.
    expected = policy(); original = dict(receipt['policy']); original['loss_weight'] = expected['loss_weight']
    policy(receipt['policy'])
    require(original == expected and receipt['inputs']['features'] == binding(features),
            'Pair source policy/features differ')
    require(set(receipt['files']) == {'pairs.npz', 'pairs.json', 'calibration.npz', 'quality.json', 'decisions.jsonl'}
            and {p.name for p in path.iterdir()} == set(receipt['files']) | {'cache.json'},
            'Missing/unexpected pair cache members')
    for name, wanted in receipt['files'].items():
        require(binding(path/name) == wanted, 'Corrupt pair cache member: '+name)
    a, meta = load_arrays(path/'pairs.npz', 'relational_pairs'); data, fm = load(features)
    n = len(data['ids']); left, right = a['left'], a['right']
    require(set(a) == {'ids', 'left', 'right', 'sign', 'weight'} and np.array_equal(a['ids'], data['ids'])
            and meta['features_sha256'] == digest(features) and receipt['samples'] == fm['samples']
            and receipt['full_contigs'] == n and receipt['full_bp'] == int(data['lengths'].sum()),
            'Complete pair/feature axes/accounting differs')
    require(left.dtype == np.int64 and right.dtype == np.int64 and left.ndim == right.ndim == 1
            and all(a[k].shape == left.shape for k in ['right', 'sign', 'weight'])
            and np.all((left >= 0) & (left < right) & (right < n))
            and a['sign'].dtype == np.int8 and a['weight'].dtype == np.float32
            and np.all(np.isin(a['sign'], [-1, 1])) and np.isfinite(a['weight']).all()
            and np.all((a['weight'] > 0) & (a['weight'] <= 1))
            and len(set(zip(map(int, left), map(int, right)))) == len(left)
            and np.all(data['eligible'][left]) and np.all(data['eligible'][right])
            and np.all(data['lengths'][left] >= expected['constraint_min_bp'])
            and np.all(data['lengths'][right] >= expected['constraint_min_bp']), 'Malformed cached signed pairs')
    degree = np.bincount(np.concatenate([left, right]), minlength=n)
    require(degree.max(initial=0) <= expected['max_degree'], 'Cached pair degree exceeds cap')
    return a, receipt
