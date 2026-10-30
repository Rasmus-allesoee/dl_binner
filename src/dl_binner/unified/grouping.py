"""Graded multi-information sparse density grouping with physical-marker selection.

One all-eligible training-neighbor index replaces universal per-channel vetoes.
Its custom symmetric distance is not promised to satisfy the triangle inequality.
Final float64 reranking and source-blind exhaustive recall gates precede any bin.
The sparse forest, whole/child alternatives and complete-DNA partitions survive.
"""
import json
from pathlib import Path
import time

import numpy as np
from numba import njit

from ..calibrated.arrays import save, load as load_numeric
from ..candidate.grouping import canonical_partition
from ..density import grouping as density
from ..information.grouping import load_inputs, ordered_sample, require
from ..information.export import validate_partition
from ..io import digest, emit, write_json


DEFAULT = dict(version=1, seed=11, neighbors=30, discovery_neighbors=61,
    max_candidates=60, index_iterations=15, index_delta=.001, exact_threshold=2048,
    audit_queries=32, audit_stratum_queries=16, min_neighbor_recall=.9,
    calibration_pairs=8192, batch_rows=512, length_scale_bp=2500,
    neutral_squared_distance=1., min_samples=10, min_bin_contigs=1,
    min_bin_bp=10000, marker_excess_penalty=5., distance_floor=.000001,
    singleton_min_bp=200000, singleton_min_reliable_families=2,
    reliable_marker_weight=.8)


def policy(path=None):
    """Refuse an unrecorded policy/grid; this block has one prospective rule."""
    cfg = json.loads(Path(path).read_text()) if path else dict(DEFAULT)
    require(cfg == DEFAULT and all(type(cfg[k]) is type(v) for k, v in DEFAULT.items()),
            'Unfrozen common grouping policy')
    return cfg


def validate_evidence(evidence, ids):
    """Refuse unknown rows or malformed physical calls, including excluded parents."""
    require(isinstance(evidence, dict) and type(evidence.get('panel_size')) is int and
            evidence['panel_size'] > 0 and isinstance(evidence.get('calls'), dict) and
            set(evidence['calls']) <= set(ids), 'Unknown/malformed cached physical marker axis')
    for values in evidence['calls'].values():
        require(isinstance(values, dict) and all(isinstance(f, str) and isinstance(v, list) and v and
                all(type(w) in (int, float) and np.isfinite(w) and 0 <= w <= 1 for w in v)
                for f, v in values.items()), 'Malformed full-axis physical marker weight')


def channels(data, vectors, valid, cfg):
    """Fit label-free numerical units; retain positive/zero/missing depth meanings.

    Means are measured at the parent level. Tanh bounds extreme log-depth
    coordinates after between-parent std scaling; no window variance is inferred.
    Co-absence/missing contributes a fixed random-pair neutral squared distance,
    rather than agreement. A positive/zero pair uses its measured contrast.
    """
    comp = np.sqrt(data['tnf'].astype(np.float32))
    raw = np.log1p(data['depth'].astype(np.float64))
    # All cells of the two admitted inputs were measured. Optional future absent
    # modalities use no columns; they cannot be fabricated by this interface.
    scale = raw[valid].std(0) if valid.any() else np.zeros(raw.shape[1])
    use = scale > 1e-8
    depth = np.tanh(raw[:, use]/scale[use]).astype(np.float32)
    positive = (data['depth'] > 0).any(1) & bool(use.any())
    selected = np.array(sorted(np.flatnonzero(valid), key=lambda i: str(data['ids'][i])), np.int64)
    sample = ordered_sample(data['ids'].tolist(), selected, cfg['calibration_pairs'])
    pairs = np.column_stack((sample, np.roll(sample, -1))) if len(sample) > 1 else np.empty((0, 2), np.int64)
    scales = []; constants = []
    for k, x in enumerate([vectors, comp, depth]):
        cohort = pairs if k < 2 else pairs[positive[pairs].any(1)]
        squared = np.square(x[cohort[:, 0]].astype(np.float64)-x[cohort[:, 1]]).sum(1)
        nonzero = squared[squared > 1e-12]
        scales.append(float(np.median(nonzero)) if len(nonzero) else 1.)
        constants.append(not len(nonzero))
    require(all(np.isfinite(scales)) and min(scales) > 0, 'Degenerate channel calibration')
    record = dict(samples=len(pairs), pair_rows=pairs.tolist(), squared_pair_medians=scales,
        constant_channels=constants, depth_column_std=scale.tolist(), usable_depth_columns=use.tolist(),
        actual_missing_cells=0, measured_all_zero_rows=int((data['depth'] == 0).all(1).sum()),
        depth_semantics='tanh(log1p(measured parent mean)/between-parent std); no window coverage/variance',
        neutral='fixed squared distance 1 for absent/co-zero depth and unreliable composition fraction',
        information='correlated evidence channels; numerical scale, not same-genome probability')
    return (vectors, comp, depth), positive, np.asarray(scales), selected, record


def distances(data, values, positive, scales, cfg, i, other):
    """Exact float64 score under the same fixed denominator in every stratum."""
    a, b, d = values
    native = np.square(a[other].astype(np.float64)-a[i]).sum(1)/scales[0]
    composition = np.square(b[other].astype(np.float64)-b[i]).sum(1)/scales[1]
    r = np.sqrt(data['lengths'][i]/(data['lengths'][i]+cfg['length_scale_bp']) *
                data['lengths'][other]/(data['lengths'][other]+cfg['length_scale_bp']))
    observed = positive[other] | positive[i]
    depth = np.full(len(other), cfg['neutral_squared_distance'], np.float64)
    depth[observed] = np.square(d[other[observed]].astype(np.float64)-d[i]).sum(1)/scales[2]
    return np.maximum(np.sqrt(np.maximum((native+r*composition+(1-r)+depth)/3, 0)), cfg['distance_floor'])


@njit(cache=True, fastmath={'reassoc', 'contract'})
def metric(a, b, native_dim, composition_dim, s0, s1, s2, length_scale, floor):
    """Compiled discovery expression; exact rerank retains unrounded source values."""
    native = 0.; composition = 0.; depth = 1.
    end = native_dim+composition_dim
    for j in range(native_dim):
        z = np.float64(a[j])-np.float64(b[j]); native += z*z
    for j in range(native_dim, end):
        z = np.float64(a[j])-np.float64(b[j]); composition += z*z
    if a[-1] == 1. or b[-1] == 1.:
        depth = 0.
        for j in range(end, len(a)-2):
            z = np.float64(a[j])-np.float64(b[j]); depth += z*z
        depth /= s2
    r = np.sqrt(np.float64(a[-2])/(a[-2]+length_scale)*np.float64(b[-2])/(b[-2]+length_scale))
    return max(np.sqrt(max((native/s0+r*composition/s1+1-r+depth)/3, 0.)), floor)


def retrieve(data, vectors, valid, original, cfg, threads, output, force_native=False):
    """Build exactly one sparse index and seal audits before any refusal or binning."""
    import sys
    require('torch' not in sys.modules, 'Graded graph worker must be isolated from tensor imports')
    values, positive, scales, selected, transform = channels(data, vectors, valid, cfg)
    n = len(selected); k = min(cfg['neighbors'], max(0, n-1)); ids = data['ids']
    inverse = np.full(len(ids), -1, np.int64); inverse[selected] = np.arange(n)
    packed = np.ascontiguousarray(np.column_stack([x[selected] for x in values]+
        [data['lengths'][selected], positive[selected]]), dtype=np.float32)
    require(np.array_equal(packed[:, -2].astype(np.int64), data['lengths'][selected]), 'Integer length packing differs')
    args = dict(native_dim=values[0].shape[1], composition_dim=values[1].shape[1],
        s0=float(scales[0]), s1=float(scales[1]), s2=float(scales[2]),
        length_scale=cfg['length_scale_bp'], floor=cfg['distance_floor'])
    width = min(n, cfg['discovery_neighbors']); proposals = None
    if n > cfg['exact_threshold'] or force_native:
        import numba
        from pynndescent import NNDescent
        numba.set_num_threads(threads)
        init = np.full((n, width), -1, np.int32)
        for local, i in enumerate(selected):
            near = original['neighbors'][i]; near = near[near >= 0]
            mapped = inverse[near]
            require((mapped >= 0).all() and local not in mapped, 'Teacher/student graph axis differs')
            seed = np.r_[local, mapped][:width]; init[local, :len(seed)] = seed
        emit('unified_joint_index_start', rows=n, dimensions=packed.shape[1], threads=threads)
        index = NNDescent(packed, metric=metric, metric_kwds=args, n_neighbors=width,
            init_graph=init, tree_init=False, random_state=cfg['seed'], n_jobs=threads,
            low_memory=True, max_candidates=cfg['max_candidates'], n_iters=cfg['index_iterations'],
            delta=cfg['index_delta'], verbose=True)
        proposals = index.neighbor_graph[0]
    nn = np.empty((n, k), np.int32); dd = np.empty((n, k), np.float64)
    sampled = set(map(int, ordered_sample(ids[selected].tolist(), np.arange(n), cfg['audit_queries'])))
    strata = {}
    for name, mask in [('positive_depth', positive[selected]), ('measured_zero_depth', ~positive[selected]),
                       ('short', data['lengths'][selected] < 2500), ('long', data['lengths'][selected] >= 2500)]:
        rows = ordered_sample(ids[selected].tolist(), np.flatnonzero(mask), cfg['audit_stratum_queries'])
        strata[name] = set(map(int, rows)); sampled.update(strata[name])
    audits = []; last = time.monotonic()
    for local, i in enumerate(selected):
        proposal = np.arange(n) if proposals is None else proposals[local]
        require(np.all((proposal >= 0) & (proposal < n)), 'Missing native neighbor proposal; no widening/fallback')
        pool = np.unique(np.r_[selected[proposal], original['neighbors'][i]])
        pool = pool[(pool >= 0) & (pool != i)]
        require(len(pool) >= k, 'Insufficient graded candidates')
        score = distances(data, values, positive, scales, cfg, i, pool)
        order = np.lexsort((ids[pool], score))[:k]
        nn[local], dd[local] = inverse[pool[order]], score[order]
        if local in sampled:
            other = selected[selected != i]; exact = distances(data, values, positive, scales, cfg, i, other)
            cutoff = np.partition(exact, k-1)[k-1] if k else 0.
            audits.append(dict(id=str(ids[i]), row=local, recall=float((score[order] <= cutoff+1e-10).mean()) if k else 1.,
                strata=[name for name, rows in strata.items() if local in rows], kth_exact=float(cutoff)))
        if time.monotonic()-last >= 5 or local+1 == n:
            emit('unified_exact_rerank', rows=local+1, total=n); last = time.monotonic()
    reports = {name: float(np.mean([x['recall'] for x in audits if name in x['strata']]))
               for name, rows in strata.items() if rows}
    mean = float(np.mean([x['recall'] for x in audits])) if audits else 1.
    passed = min([mean]+list(reports.values())) >= cfg['min_neighbor_recall']
    audit = dict(status='PASS' if passed else 'FAILED_RECALL_GATE', overall=mean, strata=reports,
        queries=audits, calibration=transform, exact_float64_rerank=True, sampled_not_global_guarantee=True,
        native_index=proposals is not None, training_neighbor_graph_only=True)
    from .graph import runtime_scope
    audit['runtime'] = runtime_scope(threads)
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    save(out/'neighbors.npz', dict(selected=selected, neighbors=nn, distances=dd),
         dict(kind='unified_graded_neighbors', audit=audit), ids)
    write_json(out/'audit.json', audit)
    require(passed, 'Graded final recall below frozen 0.90; evidence retained, no auto widening')
    return selected, nn, dd, audit


def alternatives_for(tree, lengths, ids, physical, cfg):
    """Derive supported branches and bounded reliable leaves from a retained forest."""
    alternatives = density.condense(tree, lengths, cfg)
    for c in alternatives:
        node = c['node']
        if node < len(ids):
            reliable = sum(max(v) >= cfg['reliable_marker_weight'] for v in physical['calls'].get(ids[node], {}).values())
            if c['bp'] >= cfg['singleton_min_bp'] and reliable >= cfg['singleton_min_reliable_families']:
                c['stability'] = c['bp']*max(0., 1/max(tree['core'][node], cfg['distance_floor'])-c['birth'])
    return alternatives


def partitions(data, valid, selected, nn, dd, evidence, cfg):
    """Retain density parent and reliable-marker whole/child alternatives.

    A long isolated leaf needs >=200 kb and two reliable physical families; its
    persistence ends at its own measured kNN radius, not infinity. Marker-negative
    multi-contig candidates keep the density path. No truth chooses an alternative.
    """
    validate_evidence(evidence, data['ids'].tolist())
    tree = density.hierarchy(nn, dd, data['lengths'][selected], cfg)
    local_ids = data['ids'][selected].tolist(); keep = set(local_ids)
    physical = dict(evidence, calls={q: v for q, v in evidence['calls'].items() if q in keep})
    alternatives = alternatives_for(tree, data['lengths'][selected], local_ids, physical, cfg)
    arms = {}; choices = {}
    for name, markers in [('parent', False), ('post', True)]:
        nodes, decisions = density.select(tree, alternatives, data['lengths'][selected], local_ids, physical, cfg, markers)
        groups = [[int(selected[i]) for i in density.leaves(tree, node, len(selected))] for node in nodes]
        arms[name] = canonical_partition(data['ids'].tolist(), valid, groups, data['lengths'], cfg,
            ['graded_density_abstention' if v else 'method_excluded_no_geometry' for v in valid])
        choices[name] = decisions
    return arms, tree, alternatives, choices


def run(features, embeddings, graph, evidence_path, output, cfg=None, threads=4, force_native=False):
    """Compute one fresh supported grouping and retain all numeric/partition evidence."""
    cfg = cfg or policy(); out = Path(output); out.mkdir(parents=True, exist_ok=False)
    data, vectors, valid, meta = load_inputs(features, embeddings)
    original, _ = density.sparse_input(graph, data['ids'].tolist(), valid, embeddings)
    evidence = json.loads(Path(evidence_path).read_text())
    selected, nn, dd, audit = retrieve(data, vectors, valid, original, cfg, threads, out/'retrieval', force_native)
    arms, tree, alternatives, choices = partitions(data, valid, selected, nn, dd, evidence, cfg)
    for name, part in arms.items():
        part.update(parent_features_sha256=digest(features), embedding_sha256=digest(embeddings),
            graph_sha256=digest(graph), config=cfg, algorithm='graded joint distance / sparse mutual reachability / physical-marker antichain',
            scientific_quality_assessed=False)
        write_json(out/(name+'-partition.json'), part)
        write_json(out/(name+'-choices.json'), choices[name])
    save(out/'forest.npz', {k: v for k, v in tree.items() if isinstance(v, np.ndarray)},
         dict(kind='unified_density_forest'), data['ids'])
    write_json(out/'alternatives.json', alternatives)
    files = {str(p.relative_to(out)): dict(bytes=p.stat().st_size, sha256=digest(p)) for p in out.rglob('*') if p.is_file()}
    result = dict(status='SUCCESS', config=cfg, rows=len(valid), bp=int(data['lengths'].sum()),
        samples=meta['samples'], input_sha256={k: digest(v) for k, v in dict(features=features,
            embeddings=embeddings, graph=graph, evidence=evidence_path).items()}, files=files,
        full_DNA_preserved=True, truth_accessed=False, recall=audit)
    write_json(out/'completed.json', result); return result


def audit(features, embeddings, graph, evidence_path, output, cfg=None):
    """Reload bytes and reproduce cached choices, without another index or MST."""
    cfg = cfg or policy(); out = Path(output); record = json.loads((out/'completed.json').read_text())
    from ..context.tokens import binding
    require(record['config'] == cfg and all(binding(out/k) == v for k, v in record['files'].items()),
            'Grouping member/policy corruption')
    require(record['input_sha256'] == {k: digest(v) for k, v in dict(features=features,
        embeddings=embeddings, graph=graph, evidence=evidence_path).items()}, 'Grouping source binding differs')
    data, vectors, valid, meta = load_inputs(features, embeddings)
    a, am = load_numeric(out/'retrieval/neighbors.npz', 'unified_graded_neighbors', data['ids'])
    tree, _ = load_numeric(out/'forest.npz', 'unified_density_forest', data['ids'])
    values, positive, scales, selected, _ = channels(data, vectors, valid, cfg)
    require(np.array_equal(selected, a['selected']), 'Full/local grouping axes differ')
    n = len(selected); k = min(cfg['neighbors'], max(0, n-1))
    require(a['neighbors'].shape == a['distances'].shape == (n, k) and
            a['neighbors'].dtype.kind in 'iu' and np.all((a['neighbors'] >= 0) & (a['neighbors'] < n)) and
            np.isfinite(a['distances']).all() and np.all(a['distances'] > 0) and
            np.all(np.diff(a['distances'], axis=1) >= 0), 'Malformed graded neighbor/distance cache')
    for local, i in enumerate(selected):
        require(local not in a['neighbors'][local] and len(set(map(int, a['neighbors'][local]))) == k,
                'Duplicate/self retained graded neighbor')
        other = selected[a['neighbors'][local]]
        score = distances(data, values, positive, scales, cfg, i, other)
        require(np.allclose(score, a['distances'][local], rtol=1e-12, atol=1e-12), 'Cached exact distance differs')
    # Structural forest validation, deliberately without recomputing its MST.
    mass = tree['mass']; seen = np.zeros(len(mass), np.int8)
    require(n <= len(mass) <= max(n, 2*n-1) and tree['children'].shape == (len(mass), 2) and
            np.all(tree['children'][:n] == -1) and np.array_equal(mass[:n], data['lengths'][selected]) and
            np.all(tree['count'][:n] == 1) and np.all(tree['level'][:n] == 0) and
            np.isfinite(tree['level']).all(), 'Forest leaves/axes differ')
    for node in range(n, len(mass)):
        x, y = map(int, tree['children'][node]); require(0 <= x < y < node, 'Malformed forest child')
        require(mass[node] == mass[x]+mass[y] and tree['count'][node] == tree['count'][x]+tree['count'][y]
                and tree['level'][node] >= max(tree['level'][x], tree['level'][y]), 'Forest mass/level differs')
        seen[x] += 1; seen[y] += 1
    require(np.all(seen <= 1) and np.array_equal(tree['roots'], np.flatnonzero(seen == 0)), 'Forest roots differ')
    core = a['distances'][:, min(cfg['min_samples'], k)-1] if k else np.ones(n)
    require(np.array_equal(core, tree['core']) and tree['mst_edges'].shape == (len(mass)-n, 2) and
            tree['mst_distances'].shape == (len(mass)-n,) and
            np.array_equal(np.sort(tree['mst_distances']), tree['level'][n:]), 'Core/MST counters differ')
    for (i, j), weight in zip(tree['mst_edges'], tree['mst_distances']):
        require(0 <= i < n and 0 <= j < n and i != j, 'MST index escaped full eligible population')
        found = np.r_[a['distances'][i][a['neighbors'][i] == j], a['distances'][j][a['neighbors'][j] == i]]
        require(len(found) > 0 and weight == max(core[i], core[j], float(found.min())), 'MST escaped actual graded sparse support')
    alternatives = json.loads((out/'alternatives.json').read_text()); evidence = json.loads(Path(evidence_path).read_text())
    validate_evidence(evidence, data['ids'].tolist())
    local_ids = data['ids'][selected].tolist(); local_set = set(local_ids)
    physical = dict(evidence, calls={q: v for q, v in evidence['calls'].items() if q in local_set})
    require(alternatives == alternatives_for(tree, data['lengths'][selected], local_ids, physical, cfg),
            'Cached whole/child/singleton support alternatives differ')
    for name, markers in [('parent', False), ('post', True)]:
        nodes, choices = density.select(tree, alternatives, data['lengths'][selected], local_ids, physical, cfg, markers)
        require(choices == json.loads((out/(name+'-choices.json')).read_text()), 'Marker antichain reload differs')
        expected = canonical_partition(data['ids'].tolist(), valid,
            [[int(selected[i]) for i in density.leaves(tree, node, n)] for node in nodes], data['lengths'], cfg)
        part = validate_partition(data, out/(name+'-partition.json'), features)
        require(all(part[k] == expected[k] for k in ['ids', 'assignment', 'valid', 'clusters', 'unassigned']), 'Cached partition differs')
    return dict(status='PASS', full_axis=True, complete_DNA=True, no_index_or_MST_rebuilt=True,
                original_vectors_untouched=True, optimality_claim=False)
