#!/usr/bin/env python3
"""Equivalent future cache validator with one hoisted opaque-ID membership set.

The active E025 phase at cea5f9e still executes its original inherited validator;
this separate read-only adapter does not modify that source, outputs or journals.
All hierarchy, provenance, marker-selection and full-DNA checks are preserved.
Only construction of an identical set moves outside a repeated marker lookup.
No index construction, learning, marker detection, truth or cloud action exists.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
from e024_information import (load_rebound,np,json,require,digest,load_arrays,old,canonical_partition)


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
    local_axis = set(local_ids)
    physical = dict(evidence, calls={q:v for q,v in evidence['calls'].items() if q in local_axis})
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


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['receipt','graph','evidence','cache','policy']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();print(json.dumps(audit(a.receipt,a.graph,a.evidence,a.cache,old.policy(a.policy))))
