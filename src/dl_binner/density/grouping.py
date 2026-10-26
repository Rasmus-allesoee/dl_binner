"""Sparse mutual-reachability hierarchy and marker-informed antichain selection.

Consumes immutable native vectors/features/graph and cached physical marker
evidence. No truth, detector, encoder, reference identity or cloud API is used.
This bp-weighted sparse-forest heuristic is not standard exact HDBSCAN.
"""
from collections import defaultdict
import json
from pathlib import Path
import time

import numpy as np

from ..candidate.grouping import canonical_partition
from ..information.grouping import CoreIndex, load_inputs, ordered_sample, require
from ..io import digest, emit, save_arrays, write_json
from ..multiview.arrays import load_arrays


def policy(path):
    """Read the one frozen label-free rule and reject unknown or drifting defaults."""
    cfg = json.loads(Path(path).read_text())
    frozen = dict(version=1, seed=11, neighbors=30, candidates=60, min_samples=10,
                  min_bin_contigs=2, min_bin_bp=10000, exact_threshold=2048,
                  audit_queries=32, min_neighbor_recall=.9, calibration_pairs=8192,
                  batch_rows=512, length_scale_bp=2500, marker_excess_penalty=5.,
                  distance_floor=.000001)
    require(cfg == frozen and all(type(cfg[k]) is type(v) for k, v in frozen.items()),
            'Unfrozen adaptive-density policy')
    return cfg


def sparse_input(path, ids, valid, embedding):
    """Read actual retained kNN/edge arrays; reject malformed axes and provenance."""
    a, meta = load_arrays(path, 'candidate_sparse_graph')
    n = len(ids); nn, edges, w = a['neighbors'], a['edges'], a['weights']
    require(a['ids'].tolist() == ids and meta['embedding_sha256'] == digest(embedding)
            and nn.ndim == 2 and nn.shape[0] == n and nn.dtype.kind in 'iu'
            and edges.ndim == 2 and edges.shape[1] == 2 and edges.dtype.kind in 'iu'
            and w.shape == (len(edges),) and np.isfinite(w).all() and (w > 0).all()
            and np.all((edges >= 0) & (edges < n))
            and all(ids[int(a)] < ids[int(b)] for a, b in edges)
            and np.all(valid[edges]) and np.all(nn[~valid] == -1),
            'Malformed retained sparse graph')
    for i in np.flatnonzero(valid):
        row = nn[i]
        require(np.all((row >= 0) & (row < n)) and len(set(map(int, row))) == len(row)
                and i not in row and np.all(valid[row]), 'Malformed retained sparse neighbors')
    edge_order = np.lexsort((edges[:, 1], edges[:, 0]))
    ordered = edges[edge_order]
    require(len(ordered) < 2 or np.any(ordered[1:] != ordered[:-1], axis=1).all(),
            'Duplicate retained sparse edge')
    return a, meta


def context_channels(data, vectors, selected, cfg):
    """Scale available measured-parent contexts without treating missing rows as zero evidence.

    Column std is between observed eligible parent means, not per-base coverage
    variance. Pair medians set numerical units only. Length reliability is a
    declared overlapping-composition heuristic, not a calibrated probability.
    """
    comp=np.sqrt(data['tnf'].astype(np.float32));raw=np.log1p(data['depth'].astype(np.float64))
    observed=data['eligible']&data['depth_evidence']
    scale=raw[observed].std(0)if observed.any()else np.zeros(raw.shape[1])
    use=scale>1e-8;depth=(raw[:,use]/scale[use]).astype(np.float32)
    available=observed&bool(use.any());ids=data['ids'].tolist()
    sample=ordered_sample(ids,selected,cfg['calibration_pairs'])
    pairs=np.column_stack((sample,np.roll(sample,-1)))if len(sample)>1 else np.empty((0,2),np.int64)
    channels=(vectors,comp,depth);scales=[];constant=[]
    for at,x in enumerate(channels):
        chosen=pairs if at!=2 else pairs[available[pairs].all(1)]
        d=((x[chosen[:,0]].astype(np.float64)-x[chosen[:,1]])**2).sum(1)
        positive=d[d>1e-12];scales.append(float(np.median(positive))if len(positive)else 1.);constant.append(not len(positive))
    return channels,available,np.asarray(scales),dict(channel_order=['native_unit','sqrt_TNF','log1p_measured_parent_depth'],
        pair_ids=[[ids[i],ids[j]]for i,j in pairs],pair_scales=scales,constant_pair_channels=constant,
        depth_column_std=scale.tolist(),depth_usable_columns=use.tolist(),depth_missing_rows=int((~available).sum()),
        depth_semantics='std across observed eligible parent means only; pair evidence only when both observed; no measured window/per-base variance',
        reliability='sqrt[L_i/(L_i+2500)*L_j/(L_j+2500)]; contig-length heuristic, not independent fourmer count or confidence')


def candidates(data, vectors, valid, original, cfg, threads):
    """Build one all-eligible retrieval, then exact-rerank actual available contexts.

    Only n-by-k outputs and bounded query batches are retained. Raw native
    vectors are never transformed in place; depth is not part of retrieval.
    """
    selected = np.array(sorted(np.flatnonzero(valid), key=lambda i: str(data['ids'][i])), np.int64)
    ids = data['ids'].tolist(); n = len(selected); k = min(cfg['neighbors'], max(0, n-1))
    channels, available, scales, transform = context_channels(data, vectors, selected,cfg)
    coords = np.concatenate([channels[0][selected]/np.sqrt(scales[0]),
                             channels[1][selected]/np.sqrt(scales[1])], axis=1).astype(np.float32)
    index = CoreIndex(coords, [ids[i] for i in selected], cfg, threads)
    inverse = np.full(len(ids), -1, np.int64); inverse[selected] = np.arange(n)
    nn = np.empty((n, k), np.int64); dd = np.empty((n, k), np.float64)
    query_rows, query_nn, query_dd = [], [], []
    last_progress = time.monotonic()
    audit_indices = set(map(int, ordered_sample([ids[i] for i in selected], np.arange(n), cfg['audit_queries'])))
    for start in range(0, n, cfg['batch_rows']):
        stop = min(n, start+cfg['batch_rows'])
        near, distances = index.query(coords[start:stop], np.arange(start, stop))
        for off, local in enumerate(range(start, stop)):
            i = int(selected[local])
            pool = np.unique(np.concatenate([selected[near[off]], original['neighbors'][i]]))
            pool = pool[(pool >= 0) & (pool != i)]
            require(len(pool) >= k, 'Insufficient sparse candidates')
            d0 = ((channels[0][pool].astype(np.float64)-channels[0][i])**2).sum(1)/scales[0]
            d1 = ((channels[1][pool].astype(np.float64)-channels[1][i])**2).sum(1)/scales[1]
            reliability = np.sqrt((float(data['lengths'][i])/(data['lengths'][i]+cfg['length_scale_bp']))
                                  *(data['lengths'][pool]/(data['lengths'][pool]+cfg['length_scale_bp'])))
            value = d0+reliability*d1; weight = 1+reliability
            measured = available[pool] & available[i]
            if measured.any():
                value[measured] += ((channels[2][pool[measured]].astype(np.float64)-channels[2][i])**2).sum(1)/scales[2]
                weight[measured] += 1
            value = np.maximum(np.sqrt(np.maximum(value/weight, 0)), cfg['distance_floor'])
            order = np.lexsort((data['ids'][pool], value))[:k]
            nn[local], dd[local] = inverse[pool[order]], value[order]
            if local in audit_indices:
                query_rows.append(local); query_nn.append(near[off]); query_dd.append(distances[off])
        if time.monotonic()-last_progress >= 5 or stop == n:
            emit('density_candidates', completed_rows=stop, total_rows=n, retained_neighbors=k)
            last_progress = time.monotonic()
    if n > 1:
        order = np.argsort(query_rows); qi = np.asarray(query_rows)[order]
        audit = index.audit(coords[qi], [ids[selected[j]] for j in qi],
                            np.asarray(query_nn)[order], np.asarray(query_dd)[order], qi)
    else:
        audit = dict(mode='fewer_than_two_eligible_rows', mean_tie_aware_recall=None)
    return selected, nn, dd, dict(transform=transform, audit=audit,
        depth_used_pairs='both endpoints only; missing omitted',
        candidate_scope='native kNN union all-eligible learned/Hellinger retrieval; no exact composite-neighbor guarantee')


def hierarchy(nn, distances, lengths, cfg):
    """Return an O(n) binary forest from a scipy sparse mutual-reachability MST.

    Missing edges remain missing. Sparse-graph distances approximate the full
    mutual-reachability hierarchy. Equal-weight binary branches have zero life.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import minimum_spanning_tree
    n = len(lengths); k = nn.shape[1]
    require(nn.shape == distances.shape and nn.dtype.kind in 'iu' and distances.ndim == 2
            and np.isfinite(distances).all() and np.all(distances > 0)
            and np.all((nn >= 0) & (nn < n)) and np.all(np.diff(distances, axis=1) >= 0),
            'Malformed candidate sparse arrays')
    for i, row in enumerate(nn):
        require(i not in row and len(set(map(int, row))) == k, 'Duplicate/self sparse candidate')
    core = distances[:, min(cfg['min_samples'], k)-1] if k else np.ones(n)
    rows = np.repeat(np.arange(n), k); cols = nn.ravel()
    weights = np.maximum(np.maximum(core[rows], core[cols]), distances.ravel())
    # Canonical unordered keys and minimum avoid CSR summation of duplicates.
    lo, hi = np.minimum(rows, cols), np.maximum(rows, cols)
    order = np.lexsort((weights, hi, lo)); lo, hi, weights = lo[order], hi[order], weights[order]
    keep = np.ones(len(lo), bool)
    if len(lo) > 1: keep[1:] = (lo[1:] != lo[:-1]) | (hi[1:] != hi[:-1])
    lo, hi, weights = lo[keep], hi[keep], weights[keep]
    graph = coo_matrix((np.r_[weights, weights], (np.r_[lo, hi], np.r_[hi, lo])), shape=(n, n)).tocsr()
    mst = minimum_spanning_tree(graph).tocoo()
    parent = np.arange(max(1, 2*n), dtype=np.int64); top = np.arange(n, dtype=np.int64)
    children = np.full((max(1, 2*n), 2), -1, np.int64)
    mass = np.zeros(max(1, 2*n), np.int64); count = np.zeros_like(mass)
    level = np.zeros(max(1, 2*n), np.float64); mass[:n] = lengths; count[:n] = 1
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = int(parent[i])
        return i
    at = n
    for e in np.lexsort((mst.col, mst.row, mst.data)):
        a, b = find(int(mst.row[e])), find(int(mst.col[e]))
        if a == b: continue
        x, y = int(top[a]), int(top[b]); children[at] = sorted((x, y))
        mass[at] = mass[x]+mass[y]; count[at] = count[x]+count[y]; level[at] = mst.data[e]
        parent[b] = a; top[a] = at; at += 1
    roots = sorted({int(top[find(i)]) for i in range(n)})
    return dict(children=children[:at], mass=mass[:at], count=count[:at], level=level[:at],
                roots=np.asarray(roots, np.int64), core=core, sparse_edges=len(lo),
                mst_edges=np.column_stack((mst.row, mst.col)).astype(np.int64), mst_distances=mst.data)


def leaves(tree, node, n):
    """Iterate original local row indices without materializing every subtree."""
    stack = [int(node)]
    while stack:
        item = stack.pop()
        if item < n: yield item
        else: stack.extend(map(int, tree['children'][item][::-1]))


def condense(tree, lengths, cfg):
    """Condense support-limited branches and integrate bp-weighted persistence."""
    n = len(lengths); result = []
    supported = lambda v: tree['count'][v] >= cfg['min_bin_contigs'] and tree['mass'][v] >= cfg['min_bin_bp']
    def add(node, birth, parent):
        cid = len(result)
        result.append(dict(node=int(node), parent=parent, children=[], birth=float(birth), stability=0., bp=int(tree['mass'][node])))
        if parent >= 0: result[parent]['children'].append(cid)
        return cid
    todo = [(int(r), add(int(r), 0., -1)) for r in tree['roots'] if supported(int(r))]
    while todo:
        node, cid = todo.pop(); r = result[cid]
        if node < n: continue
        a, b = map(int, tree['children'][node]); death = 1/max(float(tree['level'][node]), cfg['distance_floor'])
        sa, sb = supported(a), supported(b)
        if sa and sb:
            r['stability'] += float(tree['mass'][node])*(death-r['birth'])
            todo += [(a, add(a, death, cid)), (b, add(b, death, cid))]
        elif sa or sb:
            child, noise = (a, b) if sa else (b, a)
            r['stability'] += float(tree['mass'][noise])*(death-r['birth'])
            todo.append((child, cid))
        else:
            r['stability'] += float(tree['mass'][node])*(death-r['birth'])
    return result


def select(tree, candidates_, lengths, ids, evidence, cfg, markers=True):
    """Select a disjoint hierarchy antichain using density persistence and proxies.

    Physical-locus evidence is retained; copies on separate contigs are not
    collapsed into a locus or asserted to be contamination. Parent ties win.
    """
    require(isinstance(evidence, dict) and type(evidence.get('panel_size')) is int
            and evidence['panel_size'] > 0 and isinstance(evidence.get('calls'), dict)
            and set(evidence['calls']) <= set(ids), 'Malformed cached marker evidence')
    by_node = {}; n = len(lengths); panel = evidence['panel_size']
    for i, q in enumerate(ids):
        values = evidence['calls'].get(q, {})
        require(all(isinstance(v, list) and v and all(type(w) in (int, float) and np.isfinite(w) and 0 <= w <= 1 for w in v)
                    for v in values.values()), 'Malformed physical marker weights')
        by_node[i] = {f: (sum(v), max(v)) for f, v in values.items()}
    # Small-to-large maps avoid visiting every leaf once per ancestor.
    factors = np.ones(len(tree['mass'])); breadth = np.zeros(len(factors)); excess = np.zeros(len(factors))
    for node in range(len(tree['mass'])):
        if node >= n:
            a, b = map(int, tree['children'][node]); x, y = by_node.pop(a), by_node.pop(b)
            if len(x) < len(y): x, y = y, x
            for f, (total, maximum) in y.items():
                old = x.get(f, (0., 0.)); x[f] = (old[0]+total, max(old[1], maximum))
            by_node[node] = x
        v = by_node[node]; breadth[node] = sum(x[1] for x in v.values())/panel
        excess[node] = sum(x[0]-x[1] for x in v.values())/panel
        factors[node] = (1+breadth[node])/(1+cfg['marker_excess_penalty']*excess[node]) if markers else 1.
    best = np.zeros(len(candidates_)); decisions = []
    for cid in range(len(candidates_)-1, -1, -1):
        c = candidates_[cid]; own = c['stability']*factors[c['node']]
        child = sum(best[j] for j in c['children']); choose = own > 0 and own >= child
        best[cid] = own if choose else child
        decisions.append(dict(candidate=cid, node=c['node'], own_utility=float(own), child_utility=float(child),
                              parent_selected=bool(choose), breadth_proxy=float(100*breadth[c['node']]),
                              excess_proxy=float(100*excess[c['node']]), marker_factor=float(factors[c['node']])))
    choose = {d['candidate']: d['parent_selected'] for d in decisions}; kept = []
    stack = [j for j, c in enumerate(candidates_) if c['parent'] < 0]
    while stack:
        cid = stack.pop()
        if choose[cid]: kept.append(candidates_[cid]['node'])
        else: stack.extend(candidates_[cid]['children'])
    return kept, sorted(decisions, key=lambda d: d['candidate'])


def run(features, embeddings, graph, evidence_path, output, cfg, threads=4):
    """Consume immutable cached inputs; retain hierarchy, both choices and full axes."""
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    data, vectors, valid, meta = load_inputs(features, embeddings); ids = data['ids'].tolist()
    original, gm = sparse_input(graph, ids, valid, embeddings)
    evidence = json.loads(Path(evidence_path).read_text())
    selected, nn, dd, audit = candidates(data, vectors, valid, original, cfg, threads)
    emit('density_forest_start', eligible_rows=len(selected), neighbors=nn.shape[1])
    tree = hierarchy(nn, dd, data['lengths'][selected], cfg)
    branches = condense(tree, data['lengths'][selected], cfg)
    emit('density_forest_condensed', nodes=len(tree['mass']), candidates=len(branches), components=len(tree['roots']))
    local_ids = [ids[i] for i in selected]
    local_axis = set(local_ids)
    require(set(evidence.get('calls', {})) <= set(ids), 'Unknown cached marker contig')
    local_evidence = dict(evidence, calls={q: v for q, v in evidence['calls'].items() if q in local_axis})
    arms = {}
    for name, use_markers in [('density', False), ('selected', True)]:
        nodes, decisions = select(tree, branches, data['lengths'][selected], local_ids, local_evidence, cfg, use_markers)
        groups = [[int(selected[i]) for i in leaves(tree, node, len(selected))] for node in nodes]
        part = canonical_partition(ids, valid, groups, data['lengths'], cfg,
            ['density_abstention' if v else 'zero_geometry_evidence' for v in valid])
        part.update(parent_features_sha256=digest(features), embedding_sha256=digest(embeddings),
                    graph_sha256=digest(graph), neighbors=[[ids[j] for j in original['neighbors'][i, :5]] if valid[i] else [] for i in range(len(ids))],
                    config=cfg, algorithm='bp-weighted sparse mutual-reachability hierarchy / antichain', scientific_quality_assessed=False)
        write_json(out/(name+'-partition.json'), part); write_json(out/(name+'-choices.json'), decisions)
        arms[name] = dict(partition_sha256=digest(out/(name+'-partition.json')), bins=part['clusters'], selected_nodes=nodes)
        emit('density_partition', arm=name, bins=part['clusters'], unassigned=part['unassigned'])
    save_arrays(out/'hierarchy.npz', dict(ids=data['ids'], selected=selected, neighbors=nn, distances=dd,
                **{k: v for k, v in tree.items() if isinstance(v, np.ndarray)}),
                dict(kind='density_hierarchy', features_sha256=digest(features), embedding_sha256=digest(embeddings),
                     original_graph_sha256=digest(graph), audit=audit))
    write_json(out/'alternatives.json', branches)
    record = dict(status='SUCCESS', features_sha256=digest(features), embeddings_sha256=digest(embeddings),
                  original_graph_sha256=digest(graph), marker_evidence_sha256=digest(evidence_path),
                  config=cfg, samples=meta['samples'], contigs=len(ids), bp=int(data['lengths'].sum()),
                  candidate_count=len(branches), sparse_edges=tree['sparse_edges'], audit=audit, arms=arms,
                  truth_accessed=False, training_or_marker_detection=False)
    write_json(out/'completed.json', record)
    return record


def audit_cache(features, embeddings, graph, evidence_path, output, cfg):
    """Read persisted sparse/tree/choice axes and reproduce only cached decisions.

    No index, MST, encoder or new candidate is built. Structural identities,
    condensation and deterministic choices must match retained outputs exactly.
    This is a reload/selection contract, not a proof of approximate MST optimality.
    """
    out=Path(output);data,vectors,valid,meta=load_inputs(features,embeddings)
    original,_=sparse_input(graph,data['ids'].tolist(),valid,embeddings)
    a,m=load_arrays(out/'hierarchy.npz','density_hierarchy');ids=data['ids'].tolist()
    require(set(a)=={'ids','selected','neighbors','distances','children','mass','count','level','roots','core','mst_edges','mst_distances'},
            'Unexpected persisted hierarchy schema')
    selected=np.array(sorted(np.flatnonzero(valid),key=lambda i:ids[i]),np.int64);n=len(selected)
    require(a['ids'].tolist()==ids and np.array_equal(a['selected'],selected)
            and m['features_sha256']==digest(features) and m['embedding_sha256']==digest(embeddings)
            and m['original_graph_sha256']==digest(graph),'New hierarchy provenance/index mapping differs')
    nn,dd=a['neighbors'],a['distances'];k=min(cfg['neighbors'],max(0,n-1))
    require(nn.shape==dd.shape==(n,k) and nn.dtype.kind in 'iu' and np.isfinite(dd).all()
            and np.all(dd>0) and np.all(np.diff(dd,axis=1)>=0)
            and np.all((nn>=0)&(nn<n)),'Malformed persisted sparse distances/neighbors')
    for i,row in enumerate(nn):require(i not in row and len(set(map(int,row)))==k,'Malformed persisted sparse neighbor row')
    tree={key:a[key]for key in ['children','mass','count','level','roots','core','mst_edges','mst_distances']}
    size=len(tree['mass']);require(n<=size<=max(n,2*n-1) and tree['children'].shape==(size,2)
        and tree['children'].dtype.kind in 'iu' and all(tree[key].shape==(size,)for key in ['count','level'])
        and tree['mass'].dtype.kind in 'iu' and tree['count'].dtype.kind in 'iu'
        and np.array_equal(tree['mass'][:n],data['lengths'][selected])
        and np.all(tree['count'][:n]==1) and np.all(tree['children'][:n]==-1)
        and np.all(tree['level'][:n]==0) and np.isfinite(tree['level']).all(), 'Malformed persisted density tree')
    seen=np.zeros(size,np.int64)
    for node in range(n,size):
        x,y=map(int,tree['children'][node])
        require(0<=x<y<node and tree['level'][node]>0
                and tree['level'][node]>=max(tree['level'][x],tree['level'][y])
                and tree['mass'][node]==tree['mass'][x]+tree['mass'][y]
                and tree['count'][node]==tree['count'][x]+tree['count'][y], 'Persisted hierarchy parent/child contract differs')
        seen[x]+=1;seen[y]+=1
    require(np.all(seen<=1) and np.array_equal(tree['roots'],np.flatnonzero(seen==0))
            and len(tree['mst_edges'])==size-n and tree['mst_edges'].shape==(size-n,2)
            and tree['mst_edges'].dtype.kind in 'iu' and np.all((tree['mst_edges']>=0)&(tree['mst_edges']<n))
            and tree['mst_distances'].shape==(size-n,) and np.isfinite(tree['mst_distances']).all()
            and np.all(tree['mst_distances']>0)
            and np.array_equal(np.sort(tree['mst_distances']),tree['level'][n:]), 'Persisted forest accounting differs')
    core=dd[:,min(cfg['min_samples'],k)-1]if k else np.ones(n)
    require(np.array_equal(tree['core'],core),'Persisted local core distances differ')
    for (i,j),weight in zip(tree['mst_edges'],tree['mst_distances']):
        require(i!=j,'Persisted forest self edge')
        distances_=np.r_[dd[i][nn[i]==j],dd[j][nn[j]==i]]
        require(len(distances_)>0 and weight==max(core[i],core[j],float(distances_.min())),
                'Persisted forest edge escaped mutual-reachability candidates')
    branches=condense(tree,data['lengths'][selected],cfg)
    require(branches==json.loads((out/'alternatives.json').read_text()),'Persisted condensation differs')
    evidence=json.loads(Path(evidence_path).read_text());local_ids=[ids[i]for i in selected];axis=set(local_ids)
    evidence=dict(evidence,calls={q:v for q,v in evidence['calls'].items()if q in axis})
    records={}
    for arm,markers in [('density',False),('selected',True)]:
        nodes,choices=select(tree,branches,data['lengths'][selected],local_ids,evidence,cfg,markers)
        require(choices==json.loads((out/(arm+'-choices.json')).read_text()),'Persisted candidate selection differs')
        groups=[[int(selected[i])for i in leaves(tree,node,n)]for node in nodes]
        expected=canonical_partition(ids,valid,groups,data['lengths'],cfg,
            ['density_abstention'if v else'zero_geometry_evidence'for v in valid])
        part=json.loads((out/(arm+'-partition.json')).read_text())
        require(all(part[key]==value for key,value in expected.items())
                and part['neighbors']==[[ids[j]for j in original['neighbors'][i,:5]]if valid[i]else[]for i in range(len(ids))],
                'Persisted selected complete-DNA partition differs')
        records[arm]=dict(partition_sha256=digest(out/(arm+'-partition.json')),choices_sha256=digest(out/(arm+'-choices.json')))
    return dict(status='PASS',hierarchy_sha256=digest(out/'hierarchy.npz'),contigs=len(ids),eligible=n,
                tree_nodes=size,original_vectors_unchanged=True,arms=records,
                scope='Actual persisted sparse/tree/condensation/choice/full-axis reload; no index/MST rebuild or optimality claim')
