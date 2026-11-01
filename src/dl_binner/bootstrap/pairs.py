"""Abstaining confidence filter over a verified own-bootstrap pair cache.

No new neighbor search, marker detection, truth join or transitive label closure
is performed. Shared neighbors attenuate evidence; they are not independent
measurements or calibrated common-genome probabilities.
"""
import json
from pathlib import Path

import numpy as np

from ..context.tokens import binding
from ..density.grouping import sparse_input
from ..information.grouping import load_inputs
from ..io import digest, save_arrays, write_json
from ..multiview.arrays import load_arrays
from ..multiview.views import load
from ..relational.evidence import require
from ..relational.pairs import load_pairs as original_pairs


def policy(value=None):
    """Require the one prospective rule, including exact field types."""
    default = dict(version=1, reciprocal_top_k=10, shared_top_k=30,
                   min_shared_neighbors=2, positive_marker_endpoints=2)
    cfg = default if value is None else value
    require(isinstance(cfg, dict) and cfg == default and
            all(type(cfg[k]) is type(v) for k, v in default.items()),
            'Unfrozen bootstrap pair confidence policy')
    return dict(cfg)


def choose(arrays, quality, neighbors, cfg=None):
    """Filter accepted signed proposals; return source rows, weights and decisions.

    Negatives retain the original physical-locus/protein/context safeguards.
    Positive weights are multiplied by shared-neighbor overlap divided by the
    smaller actual top-k neighborhood size. Empty valid support abstains.
    """
    cfg = policy(cfg)
    ids = arrays['ids'].tolist()
    require(isinstance(quality.get('calls'), dict) and set(quality['calls']) <= set(ids),
            'Malformed retained physical-call quality axis')
    adjacency = [set(map(int, row[row >= 0][:cfg['shared_top_k']])) for row in neighbors]
    reciprocal = [set(map(int, row[row >= 0][:cfg['reciprocal_top_k']])) for row in neighbors]
    kept, weights, decisions = [], [], []
    for at, (i, j, sign, weight) in enumerate(zip(arrays['left'], arrays['right'],
                                               arrays['sign'], arrays['weight'])):
        i, j = int(i), int(j)
        reason, confidence, shared = 'retained_guarded_negative', float(weight), None
        if sign == 1:
            common = (adjacency[i]-{j}) & (adjacency[j]-{i})
            shared = len(common)
            if not quality['calls'].get(ids[i]) or not quality['calls'].get(ids[j]):
                reason = 'abstain_positive_requires_two_reliable_marker_endpoints'
            elif j not in reciprocal[i] or i not in reciprocal[j]:
                reason = 'abstain_not_reciprocal_top10'
            elif shared < cfg['min_shared_neighbors']:
                reason = 'abstain_insufficient_shared_neighbors'
            else:
                denominator = min(len(adjacency[i]-{j}), len(adjacency[j]-{i}))
                require(denominator > 0, 'Invalid shared-neighbor confidence denominator')
                confidence *= shared/denominator
                reason = 'retained_soft_positive'
        accepted = reason.startswith('retained_')
        if accepted:
            require(np.isfinite(confidence) and 0 < confidence <= 1, 'Invalid attenuated pair confidence')
            kept.append(at); weights.append(confidence)
        decisions.append(dict(source_pair=at, left=ids[i], right=ids[j], sign=int(sign),
                              accepted=accepted, reason=reason, shared_neighbors=shared,
                              original_weight=float(weight), weight=confidence if accepted else 0.))
    return np.asarray(kept, np.int64), np.asarray(weights, np.float32), decisions


def prepare(source, features, embeddings, graph, output):
    """Verify original readers and teacher identity, then seal a fresh filtered cache."""
    pairs, receipt = original_pairs(source, features)
    data, vectors, valid, meta = load_inputs(features, embeddings)
    embedding_meta = json.loads(Path(embeddings).with_suffix('.json').read_text())
    sparse, _ = sparse_input(graph, data['ids'].tolist(), valid, embeddings)
    require(receipt['inputs']['embeddings'] == binding(embeddings) and
            receipt['inputs']['graph'] == binding(graph), 'Pair proposals use a different bootstrap teacher')
    quality = json.loads((Path(source)/'quality.json').read_text())
    selected, weights, decisions = choose(pairs, quality, sparse['neighbors'])
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    arrays = dict(ids=pairs['ids'], **{k:pairs[k][selected] for k in ('left','right','sign')}, weight=weights,source_index=selected)
    save_arrays(out/'pairs.npz', arrays, dict(kind='bootstrap_confidence_pairs', features_sha256=digest(features)))
    with (out/'decisions.jsonl').open('x') as stream:
        for value in decisions: stream.write(json.dumps(value, allow_nan=False, sort_keys=True)+'\n')
    write_json(out/'cache.json', dict(kind='bootstrap_confidence_cache', version=1, policy=policy(),
        features=binding(features), own_teacher=binding(embeddings), teacher_graph=binding(graph),
        own_teacher_checkpoint_sha256=embedding_meta.get('checkpoint_sha256'),
        own_teacher_reload_exact=embedding_meta.get('reload_exact') is True,
        source_cache=binding(Path(source)/'cache.json'), source_cache_path=str(Path(source).absolute()),
        source_pair_count=len(pairs['left']),normalization='original proposal slots; abstention does not renormalize retained constraints',
        samples=meta['samples'], full_contigs=len(data['ids']), full_bp=int(data['lengths'].sum()),
        sign_counts={str(s):int((arrays['sign']==s).sum()) for s in (-1,1)},
        files={p.name:binding(p) for p in out.iterdir()},
        truth_accessed=False, redetected_markers=False, rebuilt_neighbors=False))
    return read(out, features)[1]


def read(path, features):
    """Refuse malformed/corrupt filtered artifacts, preserving the complete ID axis."""
    path = Path(path); receipt = json.loads((path/'cache.json').read_text())
    require(receipt.get('kind') == 'bootstrap_confidence_cache' and receipt.get('version') == 1,
            'Unsupported bootstrap pair cache')
    policy(receipt['policy'])
    require(set(receipt['files']) == {'pairs.npz','pairs.json','decisions.jsonl'} and
            {p.name for p in path.iterdir()} == set(receipt['files']) | {'cache.json'},
            'Missing/unexpected bootstrap pair members')
    for name, wanted in receipt['files'].items():
        require(binding(path/name) == wanted, 'Corrupt bootstrap pair member: '+name)
    require(receipt['features'] == binding(features), 'Bootstrap pair features differ')
    data, meta = load(features); a, m = load_arrays(path/'pairs.npz', 'bootstrap_confidence_pairs')
    left, right, sign, weight = (a[k] for k in ('left','right','sign','weight'))
    require(set(a) == {'ids','left','right','sign','weight','source_index'} and np.array_equal(a['ids'],data['ids'])
            and m['features_sha256'] == digest(features) and meta['samples'] == receipt['samples']
            and len(data['ids']) == receipt['full_contigs'] and int(data['lengths'].sum()) == receipt['full_bp'],
            'Bootstrap pair full ID/sample/DNA axes differ')
    source=a['source_index'];count=receipt['source_pair_count']
    require(type(count) is int and 0<=count<=int(np.ceil(int(data['eligible'].sum())/256))*256 and
            source.dtype==np.int64 and source.shape==left.shape and np.all((0<=source)&(source<count)) and
            np.all(np.diff(source)>0), 'Malformed original pair-slot accounting')
    require(left.ndim == 1 and left.dtype == right.dtype == np.int64 and
            right.shape == sign.shape == weight.shape == left.shape and
            sign.dtype == np.int8 and weight.dtype == np.float32 and
            np.all((0 <= left) & (left < right) & (right < len(data['ids']))) and
            np.isin(sign,[-1,1]).all() and np.isfinite(weight).all() and np.all((0 < weight) & (weight <= 1)) and
            len(set(zip(left.tolist(),right.tolist()))) == len(left) and
            np.all(data['eligible'][left]) and np.all(data['eligible'][right]) and
            all(receipt['sign_counts'][str(s)] == int((sign==s).sum()) for s in (-1,1)),
            'Malformed bootstrap signed pairs')
    return a, receipt
