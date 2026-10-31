"""One complete global ANN warm start; learning and E027 biology stay frozen.

Retrieval and bin construction are separate operations so a DAG can require all
six recall proofs before any new forest/partition. Inputs are restore-only.
Unknown/short/zero-depth rows remain in the original full DNA/eligible axes.
"""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys
import time

import numpy as np

from ..unified import grouping as frozen
from ..unified.grouping import channels, distances, metric
from ..unified.graph import runtime_scope
from ..density import grouping as density
from ..information.grouping import load_inputs, ordered_sample, require
from ..calibrated.arrays import save, load as load_numeric
from ..io import digest, emit, write_json
from ..context.tokens import binding


def policy():
    """Return the sole label-free initialization rule, without new metric knobs."""
    return dict(version=1, seed=11, initialization='self_native30_unique_uniform_global_fill',
        order='eligible opaque IDs lexical; one PCG64 seed11 row-major stream',
        native_library='pynndescent==0.5.13', biological_policy=frozen.policy(),
        exact_rerank_and_recall='unchanged E027 query/stratum/float64/gate rule')


def complete_initialization(selected, original, full_rows, width, seed=11):
    """Fill every heap slot in O(n*width), preserving native seeds and full axes.

    Small universes use explicit sampling without replacement. Large universes
    use bounded uniform rejection excluding self/native/previous draws. No truth,
    clustering, new index or distance outcome enters this deterministic rule.
    """
    n = len(selected)
    require(0 < width <= n and seed == 11, 'Invalid frozen discovery initialization')
    inverse = np.full(full_rows, -1, np.int64); inverse[selected] = np.arange(n)
    init = np.full((n, width), -1, np.int32); rng = np.random.default_rng(seed)
    for local, i in enumerate(selected):
        near = original['neighbors'][i]; near = near[near >= 0]
        mapped = inverse[near]
        require(np.all(mapped >= 0) and local not in mapped and len(set(mapped)) == len(mapped),
                'Original native graph does not match selected axis')
        known = [local]+list(map(int, mapped))
        known = known[:width]; seen = set(known)
        if n <= 2*width:
            available = np.array([j for j in range(n) if j not in seen], np.int32)
            known.extend(map(int, rng.choice(available, width-len(known), replace=False)))
        else:
            draws = 0
            while len(known) < width:
                for j in rng.integers(0, n, size=2*width):
                    draws += 1; j = int(j)
                    if j not in seen: known.append(j); seen.add(j)
                    if len(known) == width: break
                require(draws <= 100*width, 'Bounded global initialization exhausted')
        init[local] = known
    require(np.all((init >= 0) & (init < n)), 'Complete initialization has missing candidates')
    return init


def proposal_diagnostic(proposals, selected, ids, width):
    """Retain bounded invalid-row evidence before refusing any native proposal."""
    n = len(selected)
    if proposals.shape != (n, width) or proposals.dtype.kind not in 'iu':
        return dict(status='FAILED_SHAPE', shape=list(proposals.shape), dtype=str(proposals.dtype))
    invalid = (proposals < 0) | (proposals >= n)
    rows = np.flatnonzero(invalid.any(1))
    return dict(status='FAILED_MISSING_CANDIDATES' if len(rows) else 'PASS',
        missing_or_out_of_range_entries=int(invalid.sum()), invalid_rows=len(rows),
        examples=[dict(local_row=int(i), id=str(ids[selected[i]]),
            candidates=proposals[i].tolist(), invalid_positions=np.flatnonzero(invalid[i]).tolist())
            for i in rows[:32]], examples_limit=32, full_census_retained=True)


def retrieve(data, vectors, valid, original, cfg, threads, output, force_native=False):
    """Run one globally seeded index and unchanged exact E027 rerank/recall.

    The output directory and immutable initialization/exception records precede
    any refusal. The caller seals only a successful cache. Failed caches cannot
    be consumed by bin construction and are never widened automatically.
    """
    require('torch' not in sys.modules and threads == 4 and cfg == frozen.policy(),
            'Isolated four-thread frozen E027 geometry required')
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    values, positive, scales, selected, transform = channels(data, vectors, valid, cfg)
    n = len(selected); k = min(cfg['neighbors'], max(0, n-1)); ids = data['ids']
    inverse = np.full(len(ids), -1, np.int64); inverse[selected] = np.arange(n)
    packed = np.ascontiguousarray(np.column_stack([x[selected] for x in values]+
        [data['lengths'][selected], positive[selected]]), dtype=np.float32)
    packing = bool(np.array_equal(packed[:, -2].astype(np.int64), data['lengths'][selected]))
    write_json(out/'packing.json', dict(status='PASS' if packing else 'FAILED_LENGTH_PACKING', rows=n))
    require(packing, 'Integer length packing differs')
    args = dict(native_dim=values[0].shape[1], composition_dim=values[1].shape[1],
        s0=float(scales[0]), s1=float(scales[1]), s2=float(scales[2]),
        length_scale=cfg['length_scale_bp'], floor=cfg['distance_floor'])
    width = min(n, cfg['discovery_neighbors']); proposals = None
    if n > cfg['exact_threshold'] or force_native:
        import numba
        import pynndescent
        from pynndescent import NNDescent
        require(importlib.metadata.version('pynndescent') == '0.5.13', 'Pinned discovery version differs')
        numba.set_num_threads(threads)
        init = complete_initialization(selected, original, len(ids), width, cfg['seed'])
        write_json(out/'initialization.json', dict(status='PASS_COMPLETE_GLOBAL_INITIALIZATION',
            policy=policy(), shape=list(init.shape), missing_entries=int((init < 0).sum()),
            initialization_sha256=hashlib.sha256(init.tobytes()).hexdigest(),
            library_source=binding(Path(pynndescent.__file__).parent/'pynndescent_.py'),
            seed_inputs='opaque selected axis and retained native neighbors only'))
        emit('complete_global_joint_index_start', rows=n, dimensions=packed.shape[1], threads=threads)
        try:
            index = NNDescent(packed, metric=metric, metric_kwds=args, n_neighbors=width,
                init_graph=init, tree_init=False, random_state=cfg['seed'], n_jobs=threads,
                low_memory=True, max_candidates=cfg['max_candidates'], n_iters=cfg['index_iterations'],
                delta=cfg['index_delta'], verbose=True)
            proposals = index.neighbor_graph[0]
        except BaseException as exc:
            write_json(out/'index-exception.json', dict(status='FAILED_NATIVE_INDEX', error=repr(exc)))
            raise
        diagnostic = proposal_diagnostic(proposals, selected, ids, width)
        write_json(out/'proposal-audit.json', diagnostic)
        require(diagnostic['status'] == 'PASS', 'Incomplete native proposals; compact evidence retained')
    else:
        write_json(out/'initialization.json', dict(status='EXACT_SMALL_UNIVERSE', policy=policy(), rows=n))
    # The following block is the frozen E027 rerank/query/stratum/gate expression.
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
    audit['runtime'] = runtime_scope(threads)
    save(out/'neighbors.npz', dict(selected=selected, neighbors=nn, distances=dd),
         dict(kind='unified_graded_neighbors', audit=audit), ids)
    write_json(out/'audit.json', audit)
    require(passed, 'Graded final recall below frozen 0.90; evidence retained, no auto widening')
    return selected, nn, dd, audit


def prepare(features, embeddings, graph, output, threads=4, force_native=False):
    """Create a new recall-admitted cache from unchanged features and learner graph."""
    data, vectors, valid, _ = load_inputs(features, embeddings)
    original, _ = density.sparse_input(graph, data['ids'].tolist(), valid, embeddings)
    out = Path(output)
    retrieve(data, vectors, valid, original, frozen.policy(), threads, out, force_native)
    files = {p.name: binding(p) for p in out.iterdir() if p.is_file()}
    write_json(out/'completed.json', dict(status='PASS', policy=policy(),
        inputs={k: binding(p) for k, p in dict(features=features, embeddings=embeddings, graph=graph).items()},
        files=files, rows=len(data['ids']), eligible=int(valid.sum()), bp=int(data['lengths'].sum()),
        no_learner_index_training_or_marker_detection=True))
    return restore(features, embeddings, graph, out)[1]


def restore(features, embeddings, graph, cache):
    """Refuse partial/corrupt caches and validate full axes without rebuilding an index."""
    root = Path(cache); m = json.loads((root/'completed.json').read_text())
    require(m['status'] == 'PASS' and m['policy'] == policy() and
        m['inputs'] == {k: binding(p) for k, p in dict(features=features, embeddings=embeddings, graph=graph).items()},
        'Discovery cache input/policy differs')
    require({p.name for p in root.iterdir()} == set(m['files']) | {'completed.json'} and
        all(binding(root/n) == b for n, b in m['files'].items()), 'Partial/corrupt discovery members')
    data, vectors, valid, meta = load_inputs(features, embeddings)
    a, am = load_numeric(root/'neighbors.npz', 'unified_graded_neighbors', data['ids'])
    audit = json.loads((root/'audit.json').read_text())
    require(am['audit'] == audit and audit['status'] == 'PASS' and
        min([audit['overall']]+list(audit['strata'].values())) >= .9,
        'Discovery recall proof missing or failed')
    expected = np.array(sorted(np.flatnonzero(valid), key=lambda i: str(data['ids'][i])), np.int64)
    n = len(expected); k = min(30, max(0, n-1))
    require(m['rows'] == len(data['ids']) and m['eligible'] == n and m['bp'] == int(data['lengths'].sum())
        and np.array_equal(expected, a['selected']) and a['neighbors'].shape == a['distances'].shape == (n, k)
        and a['neighbors'].dtype.kind in 'iu' and np.all((a['neighbors'] >= 0) & (a['neighbors'] < n))
        and np.isfinite(a['distances']).all() and np.all(a['distances'] > 0)
        and not np.any(np.diff(a['distances'], axis=1) < 0), 'Discovery cache axes/numbers differ')
    require(not np.any(a['neighbors'] == np.arange(n)[:, None]) and
        not np.any(np.diff(np.sort(a['neighbors'], axis=1), axis=1) == 0),
        'Duplicate/self cached discovery neighbor')
    init = json.loads((root/'initialization.json').read_text())
    require(init['policy'] == policy() and init['status'] ==
        ('PASS_COMPLETE_GLOBAL_INITIALIZATION' if audit['native_index'] else 'EXACT_SMALL_UNIVERSE'),
        'Missing/wrong initialization provenance')
    if audit['native_index']:
        proposal = json.loads((root/'proposal-audit.json').read_text())
        require(init['missing_entries'] == 0 and proposal['status'] == 'PASS' and proposal['invalid_rows'] == 0,
                'Failed native proposal proof cannot be consumed')
    return (data, vectors, valid, meta, a), m


def run(features, embeddings, graph, evidence_path, cache, output):
    """Construct the unchanged E027 forest/marker alternatives from an admitted cache.

    Retrieval files are hardlinked into this fresh owned result for complete old
    audit compatibility. No index, model, marker detector or truth is invoked.
    """
    (data, vectors, valid, meta, a), cached = restore(features, embeddings, graph, cache)
    cfg = frozen.policy(); evidence = json.loads(Path(evidence_path).read_text())
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    dest = out/'retrieval'; dest.mkdir()
    import os
    for p in Path(cache).iterdir():
        require(p.is_file() and not p.is_symlink(), 'Unexpected discovery cache link/member')
        os.link(p, dest/p.name)
    arms, tree, alternatives, choices = frozen.partitions(data, valid, a['selected'],
        a['neighbors'], a['distances'], evidence, cfg)
    for name, part in arms.items():
        part.update(parent_features_sha256=digest(features), embedding_sha256=digest(embeddings),
            graph_sha256=digest(graph), config=cfg, discovery_policy=policy(),
            algorithm='E027 biology with complete-global discovery initialization', scientific_quality_assessed=False)
        write_json(out/(name+'-partition.json'), part); write_json(out/(name+'-choices.json'), choices[name])
    save(out/'forest.npz', {k: v for k, v in tree.items() if isinstance(v, np.ndarray)},
        dict(kind='unified_density_forest'), data['ids'])
    write_json(out/'alternatives.json', alternatives)
    files = {str(p.relative_to(out)): binding(p) for p in out.rglob('*') if p.is_file()}
    result = dict(status='SUCCESS', config=cfg, discovery_policy=policy(), rows=len(valid),
        bp=int(data['lengths'].sum()), samples=meta['samples'],
        input_sha256={k: digest(v) for k, v in dict(features=features, embeddings=embeddings,
            graph=graph, evidence=evidence_path).items()}, files=files,
        full_DNA_preserved=True, truth_accessed=False, recall=json.loads((dest/'audit.json').read_text()))
    write_json(out/'completed.json', result)
    return result


def audit(features, embeddings, graph, evidence_path, output):
    """Apply strict new discovery admission and the entire unchanged cached E027 audit."""
    restore(features, embeddings, graph, Path(output)/'retrieval')
    return frozen.audit(features, embeddings, graph, evidence_path, output)

