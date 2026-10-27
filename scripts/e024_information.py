#!/usr/bin/env python3
"""E024 restore-only depth rebind and observed-modality retrieval control.

No training, marker search, GLM, truth, acquisition or cloud API is reachable.
Old native vectors keep their original feature binding. A separate receipt
admits only changed measured parent depth, never rewritten old cache metadata.
The no-depth path delegates exactly to E023. With depth, retrieval unions its
sequence pool, a depth-only pool and the retained native graph, then uses the
unchanged E023 distance/hierarchy/physical-marker policy. This is an information
and retrieval bundle, not a new depth-trained encoder or a pure edge reweighting.
"""
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import numpy as np
from e024_coverage import binding, write, SAMPLES
from dl_binner.io import digest, save_arrays, validate_features, emit
from dl_binner.multiview.arrays import load_arrays
from dl_binner.information.grouping import load_inputs, ordered_sample, CoreIndex, require
from dl_binner.density import grouping as old
from dl_binner.candidate.grouping import canonical_partition


def rebind(features, views, embeddings, matrix, fasta, output):
    """Create a fresh depth-only feature artifact with exact invariant proof.

    Retained crop bytes/metadata and original native vectors are bound read-only;
    they are not copied, regenerated, rewritten or re-inferred. This artifact is
    only admitted by this explicit grouping consumer, not by the old trainer.
    """
    data, vectors, valid, meta = load_inputs(features, embeddings)
    if meta['samples'] or data['depth'].shape[1] != 0:
        raise ValueError('Original oral sequence-only cache required')
    vm = json.loads(Path(views).with_suffix('.json').read_text())
    if (vm['kind'] != 'multiview_views' or vm['parent_features_sha256'] != digest(features)
            or vm['sha256'] != digest(views) or vm['fasta_sha256'] != digest(fasta)
            or meta['fasta_sha256'] != digest(fasta)):
        raise ValueError('Retained DNA/view/source binding differs')
    mr = json.loads(Path(str(matrix)+'.receipt.json').read_text())
    samples = [f'oral_sample_{s}' for s in SAMPLES]
    if (mr['status'] != 'PASS' or mr['reference'] != binding(fasta)
            or mr['matrix'] != binding(matrix) or mr['samples'] != samples
            or mr['rows'] != len(data['ids']) or not mr['all_cells_measured'] or mr['missing_cells'] != 0):
        raise ValueError('Complete measured matrix admission differs')
    depth = np.empty((len(data['ids']), 10), np.float32)
    with Path(matrix).open() as f:
        if f.readline().rstrip('\n').split('\t') != ['contig_id']+samples:
            raise ValueError('Ordered measured sample columns differ')
        for i, ident in enumerate(data['ids']):
            row = f.readline().rstrip('\n').split('\t')
            if len(row) != 11 or row[0] != ident:
                raise ValueError('Missing/reordered measured contig row')
            depth[i] = list(map(float, row[1:]))
        if f.read(1) or not np.isfinite(depth).all() or (depth < 0).any():
            raise ValueError('Extra/nonfinite/negative coverage cell')
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    new = dict(data, depth=depth, zero_depth=depth == 0, depth_evidence=(depth > 0).any(1))
    nm = dict(meta, samples=samples, depth_sha256=digest(matrix),
              mode='E024_grouping_only_depth_rebind',
              depth_semantics='Measured full-parent aligned read-base means; all cells observed, zeros measured; no measured window/per-base variance')
    validate_features(new, nm)
    save_arrays(out/'features.npz', new, nm)
    restored, restored_meta = load_arrays(out/'features.npz', 'features')
    validate_features(restored, restored_meta)
    invariants = [k for k in data if k not in ['depth', 'zero_depth', 'depth_evidence']]
    for key in invariants:
        require(np.array_equal(data[key], restored[key]), 'Depth rebind changed ' + key)
    paths = dict(original_features=features, original_metadata=Path(features).with_suffix('.json'),
                 original_views=views, original_view_metadata=Path(views).with_suffix('.json'),
                 original_embeddings=embeddings, original_embedding_metadata=Path(embeddings).with_suffix('.json'),
                 matrix=matrix, matrix_receipt=str(matrix)+'.receipt.json', fasta=fasta,
                 rebound_features=out/'features.npz', rebound_metadata=out/'features.json')
    result = dict(kind='E024 explicit measured-depth-only grouping rebind', status='PASS',
                  paths={k:str(Path(p).absolute()) for k,p in paths.items()},
                  files={k:binding(p) for k,p in paths.items()}, invariant_arrays=invariants,
                  samples=samples, rows=len(data['ids']), native_vector_bytes_unchanged=True,
                  original_view_coordinates_hashes_TNF_DNA_ID_unchanged=True,
                  all_cells_observed=True, all_zero_rows=int((depth == 0).all(1).sum()),
                  training_cache_rewritten=False, inference_performed=False)
    write(out/'rebind.json', result)
    return result


def load_rebound(receipt):
    """Verify every retained binding and invariant before applying depth to grouping."""
    r = json.loads(Path(receipt).read_text())
    if r.get('kind') != 'E024 explicit measured-depth-only grouping rebind' or r.get('status') != 'PASS':
        raise ValueError('Explicit fresh grouping rebind required')
    for k, p in r['paths'].items():
        if binding(p) != r['files'][k]:
            raise ValueError('Corrupt/missing rebind member; no fallback: ' + k)
    original, vectors, valid, _ = load_inputs(r['paths']['original_features'], r['paths']['original_embeddings'])
    data, meta = load_arrays(r['paths']['rebound_features'], 'features')
    validate_features(data, meta)
    if meta['samples'] != r['samples'] or r['samples'] != [f'oral_sample_{s}' for s in SAMPLES]:
        raise ValueError('Frozen sample axis differs')
    for k in r['invariant_arrays']:
        require(np.array_equal(original[k], data[k]), 'Rebound invariant changed: ' + k)
    return data, vectors, valid, meta, r


def candidates(data, vectors, valid, original, cfg, threads):
    """Union unchanged sequence retrieval with observed-depth retrieval, then rerank.

    Depth uses E023 log1p/std/median units, with no row normalization: both relative
    abundance pattern and amount remain. All-zero, constant and unavailable depth
    supplies no pair evidence and no zero-filled retrieval coordinate. The exact
    no-depth call is delegated to immutable E023. Each pool has <=60 candidates;
    the retained native 30 neighbors are always included. No truth K or grid.
    """
    selected = np.array(sorted(np.flatnonzero(valid), key=lambda i: str(data['ids'][i])), np.int64)
    channels, available, scales, transform = old.context_channels(data, vectors, selected, cfg)
    transform.update(actual_missing_measured_cells=0,
                     availability_semantics='All cells measured; E023 depth_evidence means at least one positive parent mean. All-zero rows are retained as measured zero but do not vote in depth distance/index. Historical depth_missing_rows counts uninformative rows, not absent observations.')
    if not available[selected].any():
        return old.candidates(data, vectors, valid, original, cfg, threads)
    ids = data['ids'].tolist()
    coords = np.concatenate([channels[0][selected]/np.sqrt(scales[0]),
                             channels[1][selected]/np.sqrt(scales[1])], axis=1).astype(np.float32)
    sequence_index = CoreIndex(coords, [ids[i] for i in selected], cfg, threads)
    observed = selected[available[selected]]
    depth_coords = (channels[2][observed]/np.sqrt(scales[2])).astype(np.float32)
    depth_index = CoreIndex(depth_coords, [ids[i] for i in observed], cfg, threads)
    inverse = np.full(len(ids), -1, np.int64)
    inverse[selected] = np.arange(len(selected))
    observed_inverse = np.full(len(ids), -1, np.int64)
    observed_inverse[observed] = np.arange(len(observed))
    k = min(cfg['neighbors'], max(0, len(selected)-1))
    nn, dd = np.empty((len(selected), k), np.int64), np.empty((len(selected), k), np.float64)
    audit_local = ordered_sample([ids[i] for i in selected], np.arange(len(selected)), cfg['audit_queries'])
    audit_depth = ordered_sample([ids[i] for i in observed], np.arange(len(observed)), cfg['audit_queries'])
    final_audits, last = [], time.monotonic()
    def distances(i, pool):
        d0 = ((channels[0][pool].astype(np.float64)-channels[0][i])**2).sum(1)/scales[0]
        d1 = ((channels[1][pool].astype(np.float64)-channels[1][i])**2).sum(1)/scales[1]
        reliability = np.sqrt((float(data['lengths'][i])/(data['lengths'][i]+cfg['length_scale_bp']))
                              *(data['lengths'][pool]/(data['lengths'][pool]+cfg['length_scale_bp'])))
        value, weight = d0+reliability*d1, 1+reliability
        measured = available[pool] & available[i]
        value[measured] += ((channels[2][pool[measured]].astype(np.float64)-channels[2][i])**2).sum(1)/scales[2]
        weight[measured] += 1
        return np.maximum(np.sqrt(np.maximum(value/weight, 0)), cfg['distance_floor'])
    for start in range(0, len(selected), cfg['batch_rows']):
        stop = min(len(selected), start+cfg['batch_rows'])
        near, _ = sequence_index.query(coords[start:stop], np.arange(start, stop))
        rows = selected[start:stop]
        obs = np.flatnonzero(available[rows])
        depth_near = {}
        if len(obs):
            found, _ = depth_index.query(channels[2][rows[obs]]/np.sqrt(scales[2]), observed_inverse[rows[obs]])
            depth_near = {int(off): observed[found[j]] for j,off in enumerate(obs)}
        for off, local in enumerate(range(start, stop)):
            i = int(selected[local])
            pool = np.unique(np.r_[selected[near[off]], original['neighbors'][i], depth_near.get(off, np.empty(0,np.int64))])
            pool = pool[(pool >= 0) & (pool != i)]
            require(len(pool) >= k, 'Insufficient union candidates')
            value = distances(i, pool)
            order = np.lexsort((data['ids'][pool], value))[:k]
            nn[local], dd[local] = inverse[pool[order]], value[order]
            if local in audit_local:
                all_other = selected[selected != i]
                exact = distances(i, all_other)
                threshold = np.sort(exact)[k-1] if k else 0
                recall = float((value[order] <= threshold+1e-10).mean()) if k else 1.
                final_audits.append(dict(id=ids[i], final_composite_recall=recall))
        if time.monotonic()-last >= 5 or stop == len(selected):
            emit('E024_modality_union', completed_rows=stop, total_rows=len(selected))
            last = time.monotonic()
    def index_audit(index, x, indices, axis_ids):
        n, d = index.query(x[indices], indices)
        return index.audit(x[indices], [axis_ids[i] for i in indices], n, d, indices)
    seq_audit = index_audit(sequence_index, coords, audit_local, [ids[i] for i in selected])
    dep_audit = index_audit(depth_index, depth_coords, audit_depth, [ids[i] for i in observed])
    # Unlike E023's index-coordinate recall, this checks the final composite pool.
    composite_recall = float(np.mean([q['final_composite_recall'] for q in final_audits]))
    require(composite_recall >= cfg['min_neighbor_recall'], 'Final composite candidate recall below frozen 0.90; no auto widening')
    return selected, nn, dd, dict(transform=transform, sequence_retrieval=seq_audit,
        depth_retrieval=dep_audit, final_composite_queries=final_audits,
        final_composite_recall=composite_recall,
        candidate_scope='native30 union sequence60 union observed-depth60; exact final rerank; no complete all-pairs guarantee')


def run(receipt, graph, evidence_path, output, cfg, threads=4):
    """Construct one new depth-informed hierarchy and both complete-DNA alternatives."""
    data, vectors, valid, meta, r = load_rebound(receipt)
    embedding = r['paths']['original_embeddings']
    features = r['paths']['rebound_features']
    ids = data['ids'].tolist()
    original, _ = old.sparse_input(graph, ids, valid, embedding)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    evidence = json.loads(Path(evidence_path).read_text())
    require(set(evidence.get('calls', {})) <= set(ids), 'Unknown retained marker ID')
    selected, nn, dd, audit = candidates(data, vectors, valid, original, cfg, threads)
    tree = old.hierarchy(nn, dd, data['lengths'][selected], cfg)
    branches = old.condense(tree, data['lengths'][selected], cfg)
    local_ids = [ids[i] for i in selected]
    local_axis = set(local_ids)
    physical = dict(evidence, calls={q:v for q,v in evidence['calls'].items() if q in local_axis})
    arms = {}
    for arm, markers in [('density', False), ('selected', True)]:
        nodes, choices = old.select(tree, branches, data['lengths'][selected], local_ids, physical, cfg, markers)
        groups = [[int(selected[i]) for i in old.leaves(tree, node, len(selected))] for node in nodes]
        part = canonical_partition(ids, valid, groups, data['lengths'], cfg,
                 ['density_abstention' if v else 'zero_geometry_evidence' for v in valid])
        part.update(parent_features_sha256=digest(features), embedding_sha256=digest(embedding),
                    graph_sha256=digest(graph), rebind_sha256=digest(receipt), config=cfg,
                    neighbors=[[ids[j] for j in original['neighbors'][i,:5]] if valid[i] else [] for i in range(len(ids))],
                    algorithm='E024 observed-depth retrieval union / unchanged E023 hierarchy and physical-marker selection',
                    scientific_quality_assessed=False)
        write(out/(arm+'-partition.json'), part)
        write(out/(arm+'-choices.json'), choices)
        arms[arm] = dict(partition=binding(out/(arm+'-partition.json')), selected_nodes=nodes, bins=part['clusters'])
    save_arrays(out/'hierarchy.npz', dict(ids=data['ids'], selected=selected, neighbors=nn, distances=dd,
        **{k:v for k,v in tree.items() if isinstance(v,np.ndarray)}),
        dict(kind='E024_depth_hierarchy', rebind_sha256=digest(receipt), embedding_sha256=digest(embedding),
             original_graph_sha256=digest(graph), audit=audit))
    write(out/'alternatives.json', branches)
    result = dict(status='SUCCESS', rebind=binding(receipt), graph=binding(graph),
                  evidence=binding(evidence_path), cfg=cfg, samples=meta['samples'], arms=arms,
                  rows=len(ids), bp=int(data['lengths'].sum()), truth_accessed=False, encoder_changed=False,
                  audit=audit)
    write(out/'completed.json', result)
    return result


def audit(receipt, graph, evidence_path, output, cfg):
    """Reload actual arrays/choices without building another index or science stage."""
    data, _, valid, _, r = load_rebound(receipt)
    out = Path(output)
    a, m = load_arrays(out/'hierarchy.npz', 'E024_depth_hierarchy')
    require(m['rebind_sha256'] == digest(receipt) and m['original_graph_sha256'] == digest(graph)
            and m['embedding_sha256'] == digest(r['paths']['original_embeddings']), 'Hierarchy provenance differs')
    selected, nn, dd = a['selected'], a['neighbors'], a['distances']
    require(np.array_equal(selected, np.array(sorted(np.flatnonzero(valid), key=lambda i:str(data['ids'][i]))))
            and a['ids'].tolist() == data['ids'].tolist(), 'Persisted full/local axes differ')
    n, k = len(selected), nn.shape[1]
    require(nn.shape == dd.shape == (n,min(cfg['neighbors'],max(0,n-1)))
            and nn.dtype.kind in 'iu' and np.isfinite(dd).all() and np.all(dd > 0)
            and np.all(np.diff(dd,axis=1) >= 0) and np.all((nn >= 0) & (nn < n)),
            'Malformed retained sparse neighbor/distance arrays')
    for i, row in enumerate(nn):
        require(i not in row and len(set(map(int,row))) == k, 'Duplicate/self retained neighbor')
    rebuilt = {key:a[key] for key in ['children','mass','count','level','roots','core','mst_edges','mst_distances']}
    size = len(rebuilt['mass'])
    require(n <= size <= max(n,2*n-1) and rebuilt['children'].shape == (size,2)
            and rebuilt['children'].dtype.kind in 'iu'
            and all(rebuilt[key].shape == (size,) for key in ['mass','count','level'])
            and np.array_equal(rebuilt['mass'][:n],data['lengths'][selected])
            and np.all(rebuilt['count'][:n] == 1) and np.all(rebuilt['children'][:n] == -1)
            and np.all(rebuilt['level'][:n] == 0) and np.isfinite(rebuilt['level']).all(),
            'Malformed retained forest axes/leaves')
    seen = np.zeros(size,np.int64)
    for node in range(n,size):
        x,y = map(int,rebuilt['children'][node])
        require(0 <= x < y < node and rebuilt['level'][node] > 0
                and rebuilt['level'][node] >= max(rebuilt['level'][x],rebuilt['level'][y])
                and rebuilt['mass'][node] == rebuilt['mass'][x]+rebuilt['mass'][y]
                and rebuilt['count'][node] == rebuilt['count'][x]+rebuilt['count'][y],
                'Retained parent/child accounting differs')
        seen[x] += 1
        seen[y] += 1
    require(np.all(seen <= 1) and np.array_equal(rebuilt['roots'],np.flatnonzero(seen == 0))
            and rebuilt['mst_edges'].shape == (size-n,2)
            and rebuilt['mst_distances'].shape == (size-n,)
            and np.all((rebuilt['mst_edges'] >= 0) & (rebuilt['mst_edges'] < n))
            and np.array_equal(np.sort(rebuilt['mst_distances']),rebuilt['level'][n:]),
            'Retained forest root/edge accounting differs')
    core = dd[:,min(cfg['min_samples'],k)-1] if k else np.ones(n)
    require(np.array_equal(core,rebuilt['core']), 'Retained core distances differ')
    for (i,j), weight in zip(rebuilt['mst_edges'],rebuilt['mst_distances']):
        found = np.r_[dd[i][nn[i] == j],dd[j][nn[j] == i]]
        require(i != j and len(found) > 0 and weight == max(core[i],core[j],float(found.min())),
                'Retained edge escaped declared mutual reachability')
    branches = old.condense(rebuilt, data['lengths'][selected], cfg)
    require(branches == json.loads((out/'alternatives.json').read_text()), 'Persisted branches differ')
    evidence = json.loads(Path(evidence_path).read_text())
    ids = data['ids'].tolist()
    local_ids = [ids[i] for i in selected]
    physical = dict(evidence, calls={q:v for q,v in evidence['calls'].items() if q in set(local_ids)})
    from dl_binner.information.export import validate_partition
    for arm, markers in [('density', False), ('selected', True)]:
        nodes, choices = old.select(rebuilt, branches, data['lengths'][selected], local_ids, physical, cfg, markers)
        require(choices == json.loads((out/(arm+'-choices.json')).read_text()), 'Cached marker choices differ')
        part = json.loads((out/(arm+'-partition.json')).read_text())
        expected = canonical_partition(ids, valid,
            [[int(selected[i]) for i in old.leaves(rebuilt,node,len(selected))] for node in nodes],
            data['lengths'],cfg,['density_abstention' if v else 'zero_geometry_evidence' for v in valid])
        require(all(part[k] == v for k,v in expected.items()), 'Partition/selected branch differs')
        validate_partition(data, out/(arm+'-partition.json'), r['paths']['rebound_features'])
    return dict(status='PASS', full_axis=len(ids), bp=int(data['lengths'].sum()),
                native_vectors_untouched=True, views_untouched=True,
                scope='Actual persisted sparse arrays/forest and recomputed cached marker selection; no index, MST, training or new candidates')
