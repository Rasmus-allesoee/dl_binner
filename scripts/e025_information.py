#!/usr/bin/env python3
"""E025 cached joint-distance retrieval; immutable E024 data and E023 selection.

Only candidate discovery changes. No truth, training, acquisition, marker search,
old-neighbor reconstruction or cloud operation is reachable from this consumer.
Approximate discovery uses raw float32 channels and exactly representable integer
lengths; final distances and sampled exhaustive answers use the original float64
E024 expression. Numeric evidence is sealed before the unchanged recall refusal.
"""
import json
from pathlib import Path
import pickle
import sys
import time

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
import numpy as np
from numba import njit
from e024_coverage import binding, write
from e024_information import load_rebound, audit as inherited_audit
from dl_binner.density import grouping as old
from dl_binner.information.grouping import ordered_sample, require
from dl_binner.candidate.grouping import canonical_partition
from dl_binner.io import digest, emit, save_arrays
from dl_binner.multiview.arrays import load_arrays


POLICY = dict(version=1, candidates=60, max_candidates=60, n_iters=10,
              delta=.001, seed=11, exact_threshold=2048,
              initialization='retained-native-neighbors-plus-self-and-random-fill',
              consumer='training-neighbor-graph-then-exact-rerank',
              metric='E024-pair-dependent-composite', threads=4)


@njit(cache=True, fastmath={'reassoc', 'contract'})
def joint_metric(a, b, native_dim, composition_dim, s0, s1, s2,
                 length_scale, distance_floor):
    """Compiled original composite expression, with positive-depth pair omission.

    Packed rows contain original float32 channels, integer length and a 0/1
    informative-depth flag. Native NNDescent stores distances as float32; this
    function accumulates in float64, allowing vectorized reassociation/FMA only
    during approximate discovery. Exact NumPy reranking is unchanged. It is
    symmetric but need not be a metric
    satisfying the triangle inequality. No fake zero-depth contrast is used.
    """
    d0 = 0.
    d1 = 0.
    d2 = 0.
    for j in range(native_dim):
        z = np.float64(a[j])-np.float64(b[j]); d0 += z*z
    end = native_dim+composition_dim
    for j in range(native_dim, end):
        z = np.float64(a[j])-np.float64(b[j]); d1 += z*z
    r = np.sqrt((np.float64(a[-2])/(a[-2]+length_scale))
                *(np.float64(b[-2])/(b[-2]+length_scale)))
    value = d0/s0+r*d1/s1
    weight = 1.+r
    if a[-1] == 1. and b[-1] == 1.:
        for j in range(end, len(a)-2):
            z = np.float64(a[j])-np.float64(b[j]); d2 += z*z
        value += d2/s2
        weight += 1.
    return max(np.sqrt(max(value/weight, 0.)), distance_floor)


def exact_distances(data, channels, available, scales, cfg, i, pool):
    """Evaluate the unchanged E024 float64 score and tie floor, without an index."""
    d0 = ((channels[0][pool].astype(np.float64)-channels[0][i])**2).sum(1)/scales[0]
    d1 = ((channels[1][pool].astype(np.float64)-channels[1][i])**2).sum(1)/scales[1]
    r = np.sqrt((float(data['lengths'][i])/(data['lengths'][i]+cfg['length_scale_bp']))
                *(data['lengths'][pool]/(data['lengths'][pool]+cfg['length_scale_bp'])))
    value, weight = d0+r*d1, 1+r
    measured = available[pool] & available[i]
    value[measured] += ((channels[2][pool[measured]].astype(np.float64)-channels[2][i])**2).sum(1)/scales[2]
    weight[measured] += 1
    return np.maximum(np.sqrt(np.maximum(value/weight, 0)), cfg['distance_floor'])


class JointIndex:
    """One seed-11 compiled NNDescent, initialized from retained native neighbors.

    Community discovery consumes its training-neighbor graph directly, avoiding
    a redundant approximate query of the same parents. Actual external query and
    pickle/reload are exercised on tiny native fixtures, not claimed for a saved
    community search object. Only sparse discovery/final arrays are retained.
    """
    def __init__(self, data, channels, available, scales, selected, original, cfg,
                 threads=4, force_native=False):
        require(type(threads) is int and 1 <= threads <= 4, 'Four-thread index limit')
        self.selected, self.ids = selected, data['ids'][selected]
        self.native = None
        self.discovery = None
        self.args = dict(native_dim=channels[0].shape[1], composition_dim=channels[1].shape[1],
                         s0=float(scales[0]), s1=float(scales[1]), s2=float(scales[2]),
                         length_scale=cfg['length_scale_bp'], distance_floor=cfg['distance_floor'])
        lengths = data['lengths'][selected]
        require(np.array_equal(lengths.astype(np.float32).astype(np.int64), lengths),
                'Length packing would change the joint index distance')
        self.x = np.ascontiguousarray(np.column_stack(
            [x[selected] for x in channels]+[lengths, available[selected]]), dtype=np.float32)
        require(np.isfinite(self.x).all() and len(set(self.ids.tolist())) == len(selected),
                'Malformed packed index/opaque axis')
        if len(selected) > POLICY['exact_threshold'] or force_native:
            import numba
            from pynndescent import NNDescent
            numba.set_num_threads(threads)
            n = len(selected); count = min(n, POLICY['candidates']+1)
            require(n >= 3, 'Native fixture/index requires at least three rows')
            inv = np.full(len(data['ids']), -1, np.int64); inv[selected] = np.arange(n)
            init = np.full((n, count), -1, np.int32)
            for local, row in enumerate(selected):
                support = original['neighbors'][row]
                support = support[(support >= 0) & (support != row)]
                mapped = inv[support]
                require((mapped >= 0).all(), 'Retained neighbor outside eligible axis')
                values = np.r_[local, mapped][:count]
                require(len(set(map(int, values))) == len(values), 'Duplicate initialization neighbor')
                init[local, :len(values)] = values
            emit('E025_joint_index_start', rows=n, dimensions=self.x.shape[1],
                 threads=threads, initialization=POLICY['initialization'])
            self.native = NNDescent(self.x, metric=joint_metric, metric_kwds=self.args,
                n_neighbors=count, init_graph=init, tree_init=False,
                random_state=POLICY['seed'], n_jobs=threads, low_memory=True,
                max_candidates=POLICY['max_candidates'], n_iters=POLICY['n_iters'],
                delta=POLICY['delta'], verbose=True)
            # The public property copies the complete graph. Read it once, not
            # once per parent (which would turn sparse discovery into O(n^2) IO).
            self.discovery = self.native.neighbor_graph[0]

    def proposals(self, row):
        """Return original local-row proposals; no query rebuild or widening."""
        if self.native is None:
            return np.arange(len(self.selected), dtype=np.int64)
        return self.discovery[row].astype(np.int64)


def candidates(data, vectors, valid, original, cfg, threads, output,
               force_native=False):
    """Persist discovery, exact top-k and all numeric audits before gate refusal."""
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    selected = np.array(sorted(np.flatnonzero(valid), key=lambda i: str(data['ids'][i])), np.int64)
    channels, available, scales, transform = old.context_channels(data, vectors, selected, cfg)
    transform.update(actual_missing_measured_cells=0,
        availability_semantics='All ten cells measured; all-zero/constant rows do not supply a depth contrast')
    n = len(selected); k = min(cfg['neighbors'], max(0, n-1)); ids = data['ids']
    index = JointIndex(data, channels, available, scales, selected, original, cfg, threads, force_native)
    inverse = np.full(len(ids), -1, np.int64); inverse[selected] = np.arange(n)
    nn = np.empty((n, k), np.int64); dd = np.empty((n, k), np.float64)
    proposal_width = min(n, POLICY['candidates']+1)
    proposals = np.full((n, proposal_width), -1, np.int32)
    sample = ordered_sample(ids[selected].tolist(), np.arange(n), cfg['audit_queries'])
    queries = []; sampled = set(map(int, sample)); last = time.monotonic()
    for local, i in enumerate(selected):
        proposed = index.proposals(local)
        require(((proposed >= 0) & (proposed < n)).all(), 'Missing/out-of-axis NNDescent proposal; no fallback')
        proposals[local, :min(len(proposed), proposal_width)] = proposed[:proposal_width]
        pool = np.unique(np.r_[selected[proposed], original['neighbors'][i]])
        pool = pool[(pool >= 0) & (pool != i)]
        require(len(pool) >= k, 'Insufficient composite candidate pool; no widening')
        values = exact_distances(data, channels, available, scales, cfg, i, pool)
        order = np.lexsort((ids[pool], values))[:k]
        nn[local], dd[local] = inverse[pool[order]], values[order]
        if local in sampled:
            others = selected[selected != i]
            answer = exact_distances(data, channels, available, scales, cfg, i, others)
            exact_order = np.lexsort((ids[others], answer))[:k]
            threshold = float(answer[exact_order[-1]]) if k else 0.
            recall = float(np.mean(values[order] <= threshold+1e-10)) if k else 1.
            queries.append(dict(id=str(ids[i]), full_row=int(i), local_row=local,
                final_composite_recall=recall, kth_exact_distance=threshold,
                exact_ids=ids[others[exact_order]].tolist(), returned_ids=ids[pool[order]].tolist(),
                exact_distances=answer[exact_order].tolist(), returned_distances=values[order].tolist()))
        if time.monotonic()-last >= 5 or local+1 == n:
            emit('E025_joint_rerank', completed_rows=local+1, total_rows=n); last = time.monotonic()
    mean = float(np.mean([q['final_composite_recall'] for q in queries])) if queries else 1.
    audit = dict(status='PASS' if mean >= cfg['min_neighbor_recall'] else 'FAILED_RECALL_GATE',
        transform=transform, index_policy=POLICY, config=cfg, queries=queries,
        final_composite_recall=mean, min_neighbor_recall=cfg['min_neighbor_recall'],
        exact_native_metric=index.native is not None, candidate_scope=POLICY['consumer'],
        native_distance_rounding='NNDescent stores float32 distances; raw channels/integer lengths preserve original score inputs; final rerank/audit float64',
        native_query_scope='Real compiled external query/pickle in tiny contracts only; community uses training-neighbor graph')
    # Never lose these bounded arrays/values merely because acceptance fails.
    save_arrays(output/'neighbors.npz', dict(ids=ids, selected=selected, neighbors=nn,
        distances=dd, proposals=proposals), dict(kind='E025_joint_candidates', audit=audit))
    write(output/'audit.json', audit)
    require(mean >= cfg['min_neighbor_recall'], 'Final composite recall below frozen 0.90; numeric evidence retained; no widening')
    return selected, nn, dd, audit


def run(receipt, graph, evidence_path, output, cfg, threads=4):
    """Reuse admitted rebind, graph and marker cache; export both hierarchy choices."""
    data, vectors, valid, meta, r = load_rebound(receipt)
    ids = data['ids'].tolist(); embedding = r['paths']['original_embeddings']
    original, _ = old.sparse_input(graph, ids, valid, embedding)
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    evidence = json.loads(Path(evidence_path).read_text())
    require(set(evidence.get('calls', {})) <= set(ids), 'Unknown cached marker ID')
    selected, nn, dd, audit = candidates(data, vectors, valid, original, cfg, threads, out/'retrieval')
    tree = old.hierarchy(nn, dd, data['lengths'][selected], cfg)
    branches = old.condense(tree, data['lengths'][selected], cfg)
    local_ids = [ids[i] for i in selected]; local_axis = set(local_ids)
    physical = dict(evidence, calls={q:v for q,v in evidence['calls'].items() if q in local_axis})
    arms = {}
    for arm, markers in [('density', False), ('selected', True)]:
        nodes, choices = old.select(tree, branches, data['lengths'][selected], local_ids, physical, cfg, markers)
        groups = [[int(selected[i]) for i in old.leaves(tree, node, len(selected))] for node in nodes]
        part = canonical_partition(ids, valid, groups, data['lengths'], cfg,
            ['density_abstention' if v else 'zero_geometry_evidence' for v in valid])
        part.update(parent_features_sha256=digest(r['paths']['rebound_features']),
            embedding_sha256=digest(embedding), graph_sha256=digest(graph), rebind_sha256=digest(receipt),
            config=cfg, neighbors=[[ids[j] for j in original['neighbors'][i,:5]] if valid[i] else [] for i in range(len(ids))],
            algorithm='E025 direct joint-distance NNDescent / unchanged E023 hierarchy and physical-marker selection',
            scientific_quality_assessed=False)
        write(out/(arm+'-partition.json'), part); write(out/(arm+'-choices.json'), choices)
        arms[arm] = dict(partition=binding(out/(arm+'-partition.json')), selected_nodes=nodes, bins=part['clusters'])
    # Same inherited on-disk hierarchy schema, with an explicit new treatment.
    save_arrays(out/'hierarchy.npz', dict(ids=data['ids'], selected=selected, neighbors=nn, distances=dd,
        **{k:v for k,v in tree.items() if isinstance(v,np.ndarray)}),
        dict(kind='E024_depth_hierarchy', treatment='E025_joint_distance_retrieval',
            rebind_sha256=digest(receipt), embedding_sha256=digest(embedding),
            original_graph_sha256=digest(graph), audit=audit))
    write(out/'alternatives.json', branches)
    result = dict(status='SUCCESS', rebind=binding(receipt), graph=binding(graph),
        evidence=binding(evidence_path), cfg=cfg, samples=meta['samples'], arms=arms,
        rows=len(ids), bp=int(data['lengths'].sum()), truth_accessed=False,
        encoder_changed=False, audit=audit, retrieval_policy=POLICY)
    write(out/'completed.json', result)
    return result


def audit(receipt, graph, evidence, output, cfg):
    """Reload persisted candidates and inherited exact hierarchy/marker choices."""
    out = Path(output)
    proof = inherited_audit(receipt, graph, evidence, out, cfg)
    a, m = load_arrays(out/'retrieval/neighbors.npz', 'E025_joint_candidates')
    h, hm = load_arrays(out/'hierarchy.npz', 'E024_depth_hierarchy')
    require(hm['treatment'] == 'E025_joint_distance_retrieval' and m['audit'] == hm['audit']
            and all(np.array_equal(a[k], h[k]) for k in ['ids','selected','neighbors','distances']),
            'Persisted discovery/hierarchy bytes or full/local mapping differ')
    require(json.loads((out/'retrieval/audit.json').read_text()) == m['audit']
            and m['audit']['index_policy'] == POLICY and m['audit']['status'] == 'PASS',
            'Frozen numeric retrieval audit differs')
    return dict(proof, direct_joint_retrieval_reload=True)
