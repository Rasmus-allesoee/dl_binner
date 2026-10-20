"""Read back sparse decisions independently of an index or optimizer invocation."""
import json
from pathlib import Path

import numpy as np

from ..io import digest, write_json
from ..multiview.arrays import load_arrays
from .export import validate_partition
from .grouping import contexts, distances, load_inputs, recruit, require


def review(features, embeddings, root, output):
    """Verify all axes, sparse edges, frozen profiles, recruitment and byte bindings.

    Recomputes mathematical affinities and fixed-profile selection from retained
    candidates, never builds/query an index, invokes Leiden, reruns E013 or trains.
    Native approximate recall remains the separately retained sampled proof.
    """
    root = Path(root)
    data, vectors, valid, meta = load_inputs(features, embeddings)
    graph, gm = load_arrays(root/'graph.npz', 'information_core_graph')
    cache, cm = load_arrays(root/'recruitment.npz', 'information_recruitment')
    core = validate_partition(data, root/'core-partition.json', features)
    parent = validate_partition(data, root/'partition.json', features)
    cfg = gm['information_config']
    ids = data['ids'].tolist()
    require(graph['ids'].tolist() == cache['ids'].tolist() == ids
            and gm['features_sha256'] == cm['features_sha256'] == digest(features)
            and gm['embedding_sha256'] == cm['embedding_sha256'] == digest(embeddings)
            and cm['graph_sha256'] == digest(root/'graph.npz'), 'Cached identity differs')
    cores = graph['core_indices']
    expected = sorted(np.flatnonzero(valid & (data['lengths'] >= cfg['core_min_bp'])), key=lambda i: ids[i])
    require(cores.tolist() == expected, 'Core eligibility/opaque-ID map differs')
    edges, weights = graph['edges'], graph['weights']
    require(edges.ndim == 2 and edges.shape[1] == 2 and len(edges) == len(weights)
            and np.isfinite(weights).all() and np.all(weights > 0)
            and np.all((edges >= 0) & (edges < len(ids)))
            and np.all(edges[:, 0] < edges[:, 1])
            and len({tuple(e) for e in edges}) == len(edges)
            and np.isin(edges, cores).all(), 'Malformed sparse core graph')
    channels, available, scales, transforms = contexts(data, vectors, cores, cfg)
    require(transforms == gm['transform'], 'Frozen channel transforms differ')
    candidates = graph['candidates']
    require(candidates.ndim == 2 and candidates.shape[0] == len(cores)
            and np.isin(candidates, cores).all()
            and all(len(set(row)) == len(row) and i not in row for i, row in zip(cores, candidates)),
            'Malformed core candidate indices')
    expected_edges = {}
    for start in range(0, len(cores), cfg['batch_rows']):
        sl = slice(start, start+cfg['batch_rows'])
        d, mask, affinity = distances(channels, available, cores[sl], candidates[sl], scales,
                                       data['valid_fourmers'], cfg)
        require(np.allclose(d, graph['channel_distances'][sl], atol=1e-6, rtol=1e-6)
                and np.array_equal(mask, graph['channel_available'][sl])
                and np.array_equal(affinity, graph['candidate_affinities'][sl]),
                'Cached multi-evidence affinity differs')
        for i, near, values in zip(cores[sl], candidates[sl], affinity):
            order = sorted(range(len(near)), key=lambda j: (-values[j], ids[near[j]]))[:cfg['neighbors']]
            for j in order:
                if values[j] > 0:
                    pair = min(int(i), int(near[j])), max(int(i), int(near[j]))
                    expected_edges[pair] = max(expected_edges.get(pair, 0.), values[j])
    require([tuple(e) for e in edges] == sorted(expected_edges)
            and np.array_equal(weights, [expected_edges[e] for e in sorted(expected_edges)]),
            'Sparse symmetrization/top-neighbor edge rule differs')
    gamma = float(np.median(weights))/30 if len(weights) else None
    require(gm['objective'] == dict(gamma=gamma, rule='median_positive_edge_weight / 30', node_sizes=1),
            'Sole CPM density rule differs')
    queries = cache['query_indices']
    require(queries.tolist() == sorted(np.flatnonzero(valid & (np.array(core['assignment']) < 0)), key=lambda i: ids[i])
            and np.isin(cache['candidate_indices'], cores).all(), 'Recruitment axes differ')
    qaff = np.zeros(cache['candidate_affinities'].shape)
    for start in range(0, len(queries), cfg['batch_rows']):
        sl = slice(start, start+cfg['batch_rows'])
        _, _, qaff[sl] = distances(channels, available, queries[sl], cache['candidate_indices'][sl],
                                  scales, data['valid_fourmers'], cfg)
    require(np.array_equal(qaff, cache['candidate_affinities']), 'Cached recruitment affinities differ')
    selected, evidence = recruit(data, valid, channels, available, scales, core, queries,
                                 cache['candidate_indices'], qaff, cfg)
    require(selected['assignment'] == parent['assignment'] and selected['reason'] == parent['reason'],
            'Non-propagating profile selection differs')
    require(all(np.array_equal(v, cache[k]) for k, v in evidence.items()), 'Retained profiles/offers/votes differ')
    require(gm['audit']['mean_tie_aware_recall'] >= cfg['min_neighbor_recall']
            and cm['audit']['mean_tie_aware_recall'] >= cfg['min_neighbor_recall'], 'Missing native sampled recall pass')
    record = dict(status='PASS', rows=len(ids), bp=int(data['lengths'].sum()), samples=meta['samples'],
                  graph_sha256=digest(root/'graph.npz'), recruitment_sha256=digest(root/'recruitment.npz'),
                  original_embeddings_sha256=digest(embeddings), complete_DNA_axes=True,
                  index_rebuilt=False, optimizer_replayed=False, marker_detection=False, truth_used=False,
                  scope='All cached affinities/edges/profile offers and selection; native sampled approximate recall bound by graph metadata. Float32 channel cache uses 1e-6 round-trip tolerance; original vectors are unchanged.')
    write_json(output, record)
    return record
