#!/usr/bin/env python3
"""Restore-only E026 cached grouping consumer and no-search reload audit.

Read immutable E022 E009 or explicitly rebound E024 Oral features, unit vectors,
native sparse graph and physical marker calls. Only new calibrated retrieval,
biological cores and conservative recruitment are computed. Truth is absent.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
import numpy as np
from e024_coverage import binding, write
from e024_information import load_rebound
from dl_binner.calibrated.fusion import calibrate, policy
from dl_binner.calibrated.retrieval import retrieve
from dl_binner.calibrated.grouping import construct, select, recruit
from dl_binner.calibrated.arrays import save, load
from dl_binner.candidate.grouping import canonical_partition
from dl_binner.density import grouping as old
from dl_binner.information.grouping import load_inputs, require
from dl_binner.information.export import validate_partition
from dl_binner.io import digest, save_arrays
from dl_binner.multiview.arrays import load_arrays


def inputs(unit):
    """Admit exact native bindings and an explicit grouping-only Oral depth rebind."""
    if unit.get('receipt'):
        data, vectors, valid, meta, receipt = load_rebound(unit['receipt'])
        require(unit['features'] == receipt['paths']['rebound_features']
                and unit['embeddings'] == receipt['paths']['original_embeddings'],
                'Explicit Oral rebind path differs')
    else:
        data, vectors, valid, meta = load_inputs(unit['features'], unit['embeddings'])
    graph, _ = old.sparse_input(unit['graph'], data['ids'].tolist(), valid, unit['embeddings'])
    evidence = json.loads(Path(unit['marker_evidence']).read_text())
    require(data['depth'].shape[1] == len(meta['samples']) and np.isfinite(data['depth']).all()
            and len(set(meta['samples'])) == len(meta['samples']), 'Ordered complete measured sample axis differs')
    return data, vectors, valid, meta, graph, evidence


def source_bindings(unit):
    """Bind actual feature/metadata/vector/graph/marker/reference bytes, never copy them."""
    paths = {k: unit[k] for k in ['features', 'embeddings', 'graph', 'marker_evidence', 'fasta']}
    for k in ['features', 'embeddings', 'graph']:
        paths[k+'_metadata'] = str(Path(unit[k]).with_suffix('.json'))
    if unit.get('receipt'):
        paths['receipt'] = unit['receipt']
        for k, value in json.loads(Path(unit['receipt']).read_text())['paths'].items():
            paths['rebind_'+k] = value
    return {k: dict(path=str(v), **binding(v)) for k, v in paths.items()}


def run(unit, output, cfg, threads=4, force_native=False):
    """Compute exactly one new grouping bundle into an exclusive fresh directory."""
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    before = source_bindings(unit)
    data, vectors, valid, meta, original, evidence = inputs(unit)
    model = calibrate(data, vectors, valid, original, cfg)
    write(out/'calibration.json', model.record)
    retrieval, audit_record = retrieve(model, data, valid, original, out/'retrieval', threads, force_native)
    arms, tree, edges, quality, branches, choices, votes = construct(data, valid, model, retrieval, evidence)
    for name, part in arms.items():
        part.update(parent_features_sha256=digest(unit['features']), embedding_sha256=digest(unit['embeddings']),
            graph_sha256=digest(unit['graph']), algorithm='E026 calibrated biological cores / fixed-core recruitment',
            config=cfg, scientific_quality_assessed=False,
            neighbor_geometry='Original native and new target-core numeric arrays external; no fabricated display neighbors')
        write(out/(name+'-partition.json'), part)
    # Do not duplicate giant string axes or retrieval arrays in the forest cache.
    save(out/'forest.npz', dict(**tree, **{'quality_'+k: v for k, v in quality.items()},
        **{'edge_'+k: v for k, v in edges.items()}), dict(kind='calibrated_biological_forest',
        features=binding(unit['features']), retrieval=binding(out/'retrieval/neighbors.npz')), data['ids'])
    write(out/'alternatives.json', branches); write(out/'choices.json', choices)
    with (out/'recruitment.jsonl').open('x') as f:
        for row in votes:
            f.write(json.dumps(row, allow_nan=False, separators=(',', ':'))+'\n')
    require(source_bindings(unit) == before, 'Retained science inputs changed')
    record = dict(status='SUCCESS', policy=cfg, inputs=before, samples=meta['samples'],
        ordered_ids_sha256=hashlib.sha256('\n'.join(data['ids'].tolist()).encode()).hexdigest(),
        rows=len(data['ids']), bp=int(data['lengths'].sum()), eligible=int(valid.sum()),
        core_rows=len(retrieval['cores']), retrieval_audit=audit_record,
        truth_accessed=False, learning_changed=False, marker_detection=False,
        old_index_rebuilt=False, arms={k: dict(partition=binding(out/(k+'-partition.json')),
            bins=p['clusters'], unassigned=p['unassigned']) for k, p in arms.items()})
    record['files'] = {str(p.relative_to(out)): binding(p) for p in sorted(out.rglob('*')) if p.is_file()}
    write(out/'completed.json', record)
    return record


def audit(unit, output, cfg):
    """Reload exact channels/score/axes/forest/alternatives/recruitment without search.

    Recompute deterministic cached choices, not an approximate index or MST.
    This proves byte/structural/interface consistency, not global MST optimality
    or biological quality. The separate exact tiny moment test validates formulae.
    """
    out = Path(output); done = json.loads((out/'completed.json').read_text())
    require(done['policy'] == cfg and done['inputs'] == source_bindings(unit), 'Completed input/policy seal differs')
    require(all(binding(out/k) == v for k, v in done['files'].items()), 'Cached grouping member corrupted')
    data, vectors, valid, meta, original, evidence = inputs(unit)
    model = calibrate(data, vectors, valid, original, cfg)
    require(model.record == json.loads((out/'calibration.json').read_text()), 'Calibration reload differs')
    r, rm = load(out/'retrieval/neighbors.npz', 'calibrated_core_neighbors', data['ids'])
    queries = np.array(sorted(np.flatnonzero(valid), key=lambda i: str(data['ids'][i])), np.int64)
    cores = np.array(sorted(np.flatnonzero(valid & (data['lengths'] >= cfg['core_min_bp'])),
                            key=lambda i: str(data['ids'][i])), np.int64)
    require(np.array_equal(r['queries'], queries) and np.array_equal(r['cores'], cores)
            and rm['audit'] == done['retrieval_audit'] and rm['audit']['status'] == 'PASS',
            'Cached query/core/recall axes differ')
    is_core = np.zeros(len(valid), bool); is_core[cores] = True
    for at, i in enumerate(queries):
        count = int(r['counts'][at]); near = r['neighbors'][at, :count]
        require(count == min(cfg['neighbors'], len(cores)-int(is_core[i]))
                and len(set(map(int, near))) == count and np.all((near >= 0) & (near < len(cores)))
                and i not in cores[near] and np.all(r['neighbors'][at, count:] == -1),
                'Malformed calibrated query neighbours/padding')
        d, q, observed = model.distances(i, cores[near], True)
        require(np.allclose(d, r['distances'][at, :count], rtol=1e-12, atol=1e-12)
                and np.array_equal(q.astype(np.float32), r['channel_ranks'][at, :count])
                and np.array_equal(observed, r['channel_available'][at, :count])
                and np.all(np.diff(d) >= 0), 'Retained calibrated distances/contributions differ')
    arrays, fm = load(out/'forest.npz', 'calibrated_biological_forest', data['ids'])
    require(fm['features'] == binding(unit['features']) and fm['retrieval'] == binding(out/'retrieval/neighbors.npz'),
            'Forest binding differs')
    tree = {k: arrays[k] for k in ['children', 'mass', 'count', 'level', 'roots', 'core', 'mst_edges', 'mst_distances']}
    n, size = len(cores), len(tree['mass']); seen = np.zeros(size, np.int32)
    require(n <= size <= max(n, 2*n-1) and tree['children'].shape == (size, 2)
            and np.array_equal(tree['mass'][:n], data['lengths'][cores])
            and np.all(tree['count'][:n] == 1) and np.all(tree['children'][:n] == -1), 'Malformed core forest leaves')
    for node in range(n, size):
        a, b = map(int, tree['children'][node]); require(0 <= a < b < node, 'Malformed core forest child')
        require(tree['mass'][node] == tree['mass'][a]+tree['mass'][b]
                and tree['count'][node] == tree['count'][a]+tree['count'][b]
                and tree['level'][node] >= max(tree['level'][a], tree['level'][b]) > -1,
                'Core forest accounting differs')
        seen[a] += 1; seen[b] += 1
    require(np.all(seen <= 1) and np.array_equal(tree['roots'], np.flatnonzero(seen == 0)), 'Core forest root coverage differs')
    # Prove retained trusted edges are genuinely reciprocal and independently supported.
    lookup = np.full(len(valid), -1, np.int64); lookup[queries] = np.arange(len(queries))
    edge_keys = set()
    for i, j, weight in zip(arrays['edge_left'], arrays['edge_right'], arrays['edge_distances']):
        i, j = int(i), int(j); require(0 <= i < j < n, 'Malformed trusted core edge')
        require(model.agreement(cores[i], np.array([cores[j]]))[0], 'Unsupported retained core edge')
        for a, b in [(i, j), (j, i)]:
            at = lookup[cores[a]]
            require(b in r['neighbors'][at, :cfg['core_degree']], 'Core edge is not reciprocal top-10')
        require(abs(model.distances(cores[i], np.array([cores[j]]))[0]-weight) <= 1e-12, 'Core edge weight differs')
        edge_keys.add((i, j))
    require(len(edge_keys) == len(arrays['edge_left']), 'Duplicate trusted edge')
    for (i, j), weight in zip(tree['mst_edges'], tree['mst_distances']):
        require(tuple(sorted((int(i), int(j)))) in edge_keys
                and weight == max(tree['core'][i], tree['core'][j], model.distances(cores[i], np.array([cores[j]]))[0]),
                'MST escaped retained trusted edges')
    branches = old.condense(tree, data['lengths'][cores], cfg)
    require(branches == json.loads((out/'alternatives.json').read_text()), 'Core condensation differs')
    quality = {k: arrays['quality_'+k] for k in ['coherence', 'breadth', 'excess', 'utility']}
    require(all(x.shape == (size,) and np.isfinite(x).all() for x in quality.values())
            and np.all((quality['coherence'] >= 0) & (quality['coherence'] <= 1))
            and np.all(quality['breadth'] >= 0) and np.all(quality['excess'] >= 0)
            and np.allclose(quality['utility'], tree['mass']*np.maximum(quality['coherence']-.5, 0)
                            *(1+quality['breadth'])/(1+cfg['marker_excess_penalty']*quality['excess']),
                            rtol=1e-12, atol=1e-12), 'Biological utility accounting differs')
    nodes, choices = select(tree, branches, quality, cfg)
    require(choices == json.loads((out/'choices.json').read_text()), 'Biological choice reload differs')
    groups = [[int(cores[i]) for i in old.leaves(tree, node, n)] for node in nodes]
    pre = validate_partition(data, out/'core-partition.json', unit['features'])
    expected = canonical_partition(data['ids'].tolist(), valid, groups, data['lengths'], cfg)
    require(all(pre[k] == expected[k] for k in ['ids', 'assignment', 'valid', 'clusters', 'unassigned']), 'Core partition differs')
    require(pre['core_bin_to_final_bin'] == list(range(pre['clusters'])), 'Core identity map differs')
    post, votes = recruit(pre, r, model, data, evidence)
    actual = validate_partition(data, out/'recruited-partition.json', unit['features'])
    require(all(actual[k] == post[k] for k in ['ids', 'assignment', 'valid', 'reason', 'clusters', 'unassigned', 'core_bin_to_final_bin']), 'Fixed-core recruitment differs')
    retained_votes = [json.loads(line) for line in (out/'recruitment.jsonl').open()]
    require(votes == retained_votes, 'Retained recruitment reasons/marker cap differ')
    return dict(status='PASS', original_learning_vectors_unchanged=True, rows=len(valid), cores=n,
                no_index_or_MST_rebuilt=True, all_inputs_before_after=True,
                scope='Byte/score/axes/structural/choice/recruitment reload; no global optimality claim')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit', type=Path, required=True); parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--policy', type=Path, required=True); parser.add_argument('--audit', action='store_true')
    args = parser.parse_args()
    unit = json.loads(args.unit.read_text()); cfg = policy(args.policy)
    print(json.dumps(audit(unit, args.output, cfg) if args.audit else run(unit, args.output, cfg)), flush=True)
