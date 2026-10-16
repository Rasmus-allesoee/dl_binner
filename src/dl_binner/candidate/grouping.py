"""Sparse unit-sphere graph grouping with native audited approximate neighbors.

Only an O(n*k) graph is retained. A fixed bounded exact audit is a correctness
gate, not an index/quality parameter search. Marker refinement is separate.
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np

from ..io import digest, emit, load_arrays, save_arrays, write_json


def rank_candidates(x, ids, candidates, k):
    """Rerank supplied candidates by exact cosine and deterministic opaque-ID ties."""
    neighbors = np.full((len(x), k), -1, np.int64)
    scores = np.full((len(x), k), -1., np.float64)
    for i, row in enumerate(candidates):
        allowed = np.array(sorted(set(int(j) for j in row if 0 <= j < len(x) and j != i), key=lambda j: ids[j]), np.int64)
        if len(allowed) < k:
            raise ValueError('Approximate index has missing/duplicate neighbor candidates')
        values = np.clip(x[allowed].astype(np.float64)@x[i].astype(np.float64), -1, 1)
        order = np.argsort(-values, kind='stable')[:k]
        neighbors[i], scores[i] = allowed[order], values[order]
    return neighbors, scores


def neighbor_graph(x, ids, cfg, threads):
    """Build native NNDescent (exact on small data); verify sampled tie-aware recall."""
    n = len(x)
    k = min(cfg['neighbors'], n-1)
    if k < 1:
        return np.empty((n, 0), np.int64), np.empty((n, 0)), dict(mode='no_neighbors', audit_queries=0)
    if n <= cfg['exact_threshold']:
        # Exact threshold is a bounded implementation crossover, not a different
        # biological graph. No all-n square allocation outside small fixtures.
        candidates = np.tile(np.arange(n), (n, 1))
        mode = 'bounded_exact'
    else:
        import numba
        from pynndescent import NNDescent
        numba.set_num_threads(threads)
        emit('candidate_approximate_index_start', rows=n, dimensions=x.shape[1], neighbors=k, threads=threads)
        index = NNDescent(np.asarray(x, np.float32), metric='euclidean', n_neighbors=min(n, max(k+1, 2*k)),
            random_state=cfg['seed'], n_jobs=threads, low_memory=True, max_candidates=60, n_iters=10, verbose=True)
        candidates = index.neighbor_graph[0]
        mode = 'pynndescent_exact_rerank'
    nn, scores = rank_candidates(x, ids, candidates, k)
    selected = sorted(range(n), key=lambda i: hashlib.sha256(ids[i].encode()).digest())[:cfg['audit_queries']]
    recalls = []
    for i in selected:
        exact = np.clip(x.astype(np.float64)@x[i].astype(np.float64), -1, 1)
        exact[i] = -np.inf
        cutoff = np.partition(exact, -k)[-k]
        # Candidates at an equal kth score are all valid; do not create a false
        # index failure from arbitrary ties or call it an exact ID-list match.
        recalls.append(float(np.mean(scores[i] >= cutoff-1e-6)))
    audit = dict(mode=mode, audit_queries=len(selected), query_ids=[ids[i] for i in selected],
        mean_tie_aware_recall=float(np.mean(recalls)), min_query_recall=float(min(recalls)), k=k,
        threshold=cfg['min_neighbor_recall'], metric='Euclidean on unit vectors; exact cosine rerank',
        guarantee='fixed sampled queries only; no unqueried recall guarantee', threads=threads)
    if audit['mean_tie_aware_recall'] < cfg['min_neighbor_recall']:
        raise ValueError('Approximate neighbor recall below predeclared gate: '+json.dumps(audit))
    emit('candidate_neighbor_audit', mean_recall=audit['mean_tie_aware_recall'], queries=len(selected), mode=mode)
    return nn, scores, audit


def canonical_partition(ids, valid, groups, lengths, cfg, reasons=None):
    """Canonicalize accepted group IDs and retain every invalid/noise reason."""
    labels = np.full(len(ids), -1, np.int64)
    reason = list(reasons or ['zero_geometry_evidence' if not v else 'group_below_support' for v in valid])
    accepted = [sorted(c) for c in groups if len(c) >= cfg['min_bin_contigs']
                and sum(int(lengths[i]) for i in c) >= cfg['min_bin_bp']]
    for label, members in enumerate(sorted(accepted, key=lambda c: min(ids[i] for i in c))):
        for i in members:
            if not valid[i] or labels[i] != -1:
                raise ValueError('Invalid/duplicate member in grouping')
            labels[i], reason[i] = label, ''
    return dict(ids=list(ids), assignment=labels.tolist(), valid=list(map(bool, valid)),
                reason=reason, clusters=len(accepted), unassigned=int((labels < 0).sum()))


def group(embeddings, features, output, cfg, threads):
    """Create one Leiden partition and retain complete sparse edges/neighbor axes."""
    import igraph as ig
    import leidenalg
    from .views import load
    data, meta = load(features)
    a, em = load_arrays(embeddings, 'embeddings')
    if (not np.array_equal(a['ids'], data['ids']) or em['features_sha256'] != digest(features)
            or a['features'].shape != (len(data['ids']), cfg['output'])
            or a['evidence'].shape != data['eligible'].shape
            or not np.isfinite(a['features']).all()):
        raise ValueError('Grouping feature/embedding contract mismatch')
    ids = data['ids'].tolist()
    valid = data['eligible'] & a['evidence']
    selected = np.array(sorted(np.flatnonzero(valid), key=lambda i: ids[i]), np.int64)
    x = a['features'][selected]
    if len(x) and not np.allclose(np.linalg.norm(x, axis=1), 1, atol=1e-5):
        raise ValueError('Candidate grouping requires unchanged unit embeddings')
    nn, scores, audit = neighbor_graph(x, [ids[i] for i in selected], cfg, threads)
    edges = {}
    sigma = np.maximum(2-2*scores[:, -1], 1e-6) if nn.shape[1] else np.ones(len(x))
    for i, candidates in enumerate(nn):
        for at, j in enumerate(candidates):
            if scores[i, at] <= 0:
                continue
            pair = min(i, int(j)), max(i, int(j))
            distance = max(0, 2-2*scores[i, at])
            edges[pair] = float(np.exp(-distance/np.sqrt(sigma[i]*sigma[j])))
    ordered = sorted(edges)
    graph = ig.Graph(n=len(selected), edges=ordered, directed=False)
    if ordered:
        partition = leidenalg.find_partition(graph, leidenalg.RBConfigurationVertexPartition,
            weights=[edges[e] for e in ordered], resolution_parameter=cfg['resolution'],
            seed=cfg['seed'], n_iterations=cfg['leiden_iterations'])
        groups = [[int(selected[j]) for j in c] for c in partition]
    else:
        groups = []
    result = canonical_partition(ids, valid, groups, data['lengths'], cfg)
    neighbors = [[] for _ in ids]
    full = np.full((len(ids), nn.shape[1]), -1, np.int64)
    for i, index in enumerate(selected):
        neighbors[index] = [ids[selected[j]] for j in nn[i, :5]]
        full[index] = selected[nn[i]]
    out = Path(output)
    save_arrays(out/'graph.npz', dict(ids=data['ids'], neighbors=full,
        edges=np.array([(selected[i], selected[j]) for i, j in ordered], np.int64).reshape(-1, 2),
        weights=np.array([edges[e] for e in ordered], np.float64)),
        dict(kind='candidate_sparse_graph', metric=em['metric'], embedding_sha256=digest(embeddings), audit=audit))
    result.update(neighbors=neighbors, parent_features_sha256=digest(features),
        embedding_sha256=digest(embeddings), graph_sha256=digest(out/'graph.npz'),
        algorithm='single weighted symmetric positive kNN / Leiden RB', audit=audit, config=cfg,
        transform='none; learned unit sphere preserved')
    write_json(out/'partition.json', result)
    emit('candidate_grouping_complete', rows=len(ids), edges=len(ordered), clusters=result['clusters'])


def conflicts(members, clean, ids):
    """Count clean marker families repeated across distinct contigs within a group."""
    counts = Counter(f for i in members for f in clean.get(ids[i], []))
    return {f: c for f, c in counts.items() if c > 1}


def refine_partition(pre, features, vectors, clean, cfg):
    """Propose conservative conflict splits with constrained spherical refinement.

    Two independently repeated canonical families are required. No bin merging,
    marker-negative exclusion or inferred genome labels occur. A failed proposal
    leaves the pre-bin intact and explicitly unresolved; accepted splits can
    retain uncertain members as noise. At most one proposal per pre-bin.
    """
    ids, lengths = features['ids'].tolist(), features['lengths']
    if pre['ids'] != ids or vectors.shape != (len(ids), cfg['output']):
        raise ValueError('Refinement axes mismatch')
    groups = defaultdict(list)
    for i, b in enumerate(pre['assignment']):
        if b >= 0:
            groups[b].append(i)
    accepted, attempts = [], []
    reasons = list(pre['reason'])
    for label, members in sorted(groups.items()):
        before = conflicts(members, clean, ids)
        if len(before) < 2:
            accepted.append(members)
            if before:
                attempts.append(dict(pre_bin=label, adopted=False, reason='fewer_than_two_conflict_families', before=before))
            continue
        k = sorted(before.values(), reverse=True)[1]
        family = min((f for f, c in before.items() if c == k))
        seeds = sorted((i for i in members if family in clean.get(ids[i], [])), key=lambda i: (-int(lengths[i]), ids[i]))
        centers = vectors[seeds].astype(np.float64).copy()
        prior = None
        proposal = [[] for _ in seeds]
        unassigned = {}
        for iteration in range(cfg['refinement_iterations']):
            proposal = [[i] for i in seeds]
            used = [set(clean.get(ids[i], [])) for i in seeds]
            unassigned = {}
            for i in sorted(set(members)-set(seeds), key=lambda j: (-len(clean.get(ids[j], [])), -int(lengths[j]), ids[j])):
                own = set(clean.get(ids[i], []))
                similarity = centers@vectors[i].astype(np.float64)
                order = sorted(range(k), key=lambda b: (-similarity[b], b))
                allowed = [b for b in order if not own & used[b]]
                if not allowed:
                    unassigned[i] = 'marker_conflict_no_compatible_group'
                    continue
                best = allowed[0]
                # Confidence compares all centers, including a conflicting best
                # group; do not force an implausible alternate solely to satisfy SCG.
                if (best != order[0] or similarity[best] < cfg['refinement_min_cosine']
                        or (k > 1 and similarity[order[0]]-similarity[order[1]] < cfg['refinement_margin'])):
                    unassigned[i] = 'refinement_ambiguous_affinity'
                    continue
                proposal[best].append(i)
                used[best].update(own)
            membership = tuple(tuple(sorted(c)) for c in proposal)
            if membership == prior:
                break
            prior = membership
            for b, c in enumerate(proposal):
                center = (vectors[c].astype(np.float64)*np.sqrt(lengths[c, None])).sum(0)
                norm = np.linalg.norm(center)
                centers[b] = center/norm if norm > 1e-12 else vectors[seeds[b]]
        supported = all(len(c) >= cfg['min_bin_contigs'] and int(lengths[c].sum()) >= cfg['min_bin_bp'] for c in proposal)
        after = [conflicts(c, clean, ids) for c in proposal]
        adopt = supported and not any(after)
        attempts.append(dict(pre_bin=label, before=before, k=k, seed_family=family,
            seed_ids=[ids[i] for i in seeds], adopted=adopt, iterations=iteration+1,
            unassigned_proposal=len(unassigned), proposed_bp=[int(lengths[c].sum()) for c in proposal],
            reason='conflicts_removed_with_supported_groups' if adopt else 'unsupported_split_retained_original', after=after))
        if adopt:
            accepted.extend(proposal)
            for i, reason in unassigned.items():
                reasons[i] = reason
        else:
            accepted.append(members)
    result = canonical_partition(ids, pre['valid'], accepted, lengths, cfg, reasons)
    canonical = defaultdict(list)
    for i, label in enumerate(result['assignment']):
        if label >= 0:
            canonical[label].append(i)
    result.update(neighbors=pre['neighbors'], parent_features_sha256=pre['parent_features_sha256'],
        pre_partition_semantics='one proposal per pre-bin; no merging; uncertainty may remain unassigned',
        attempts=attempts, scientific_quality_assessed=False,
        unresolved_conflicts={str(b): conflicts(c, clean, ids) for b, c in canonical.items() if conflicts(c, clean, ids)})
    return result
