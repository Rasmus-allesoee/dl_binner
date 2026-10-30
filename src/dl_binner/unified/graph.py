"""Native unit-neighbor graph for fresh bootstrap proposals and learned support."""
from pathlib import Path
import sys

import numpy as np

from ..candidate.grouping import neighbor_graph
from ..information.grouping import load_inputs
from ..io import digest, save_arrays, write_json


def runtime_scope(threads=4):
    """Bind actual graph math libraries; tensor backends belong in another process."""
    if 'torch' in sys.modules: raise RuntimeError('Graph worker must be isolated from tensor imports')
    from threadpoolctl import threadpool_info
    pools = threadpool_info()
    if (any(p['num_threads'] > threads for p in pools) or
            any(p['prefix'] == 'libiomp' for p in pools) and any(p['prefix'] == 'libomp' for p in pools)):
        raise RuntimeError('Incompatible or over-budget graph numerical runtime')
    libraries = {}
    for p in pools:
        target = Path(p['filepath']).resolve(strict=True)
        libraries[p['filepath']] = dict(resolved=str(target), bytes=target.stat().st_size, sha256=digest(target))
    return dict(tensor_backend_loaded=False, pools=pools, libraries=libraries, threads=threads)


def prepare(features, embeddings, output, cfg, threads=4):
    """Retain source-blind exact-reranked kNN and positive weights, without binning."""
    if 'torch' in sys.modules: raise RuntimeError('Graph worker must be isolated from tensor imports')
    data, vectors, valid, _ = load_inputs(features, embeddings)
    ids = data['ids'].tolist()
    selected = np.array(sorted(np.flatnonzero(valid), key=lambda i: ids[i]), np.int64)
    nn, cosine, audit = neighbor_graph(vectors[selected], [ids[i] for i in selected], cfg, threads)
    full = np.full((len(ids), nn.shape[1]), -1, np.int64)
    full[selected] = selected[nn]
    sigma = np.maximum(2-2*cosine[:, -1], 1e-6) if nn.shape[1] else np.ones(len(selected))
    edges = {}
    for i, row in enumerate(nn):
        for at, j in enumerate(row):
            if cosine[i, at] <= 0:
                continue
            a, b = int(selected[i]), int(selected[j])
            pair = (a, b) if ids[a] < ids[b] else (b, a)
            edges[pair] = float(np.exp(-max(0, 2-2*cosine[i, at])/np.sqrt(sigma[i]*sigma[j])))
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    ordered = sorted(edges)
    save_arrays(out/'graph.npz', dict(ids=data['ids'], neighbors=full,
        edges=np.array(ordered, np.int64).reshape(-1, 2),
        weights=np.array([edges[e] for e in ordered], np.float64)),
        dict(kind='candidate_sparse_graph', embedding_sha256=digest(embeddings),
             metric='unit-sphere cosine/equivalent Euclidean; no post-learning transform', audit=audit))
    write_json(out/'completed.json', dict(status='PASS', features_sha256=digest(features),
        embedding_sha256=digest(embeddings), graph_sha256=digest(out/'graph.npz'), audit=audit,
        old_graph_reused=False, bins_computed=False, truth_accessed=False, runtime=runtime_scope(threads)))
