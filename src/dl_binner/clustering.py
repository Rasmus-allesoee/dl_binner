"""Fixed truth-free neighbor clustering and complete contig/bin accounting."""
import csv
import json
from pathlib import Path

import networkx as nx
import numpy as np

from .io import digest, emit, load_arrays, read_fasta, validate_features, write_json


def geometry(features, ids, evidence=None, query_block=128):
    """Apply E003's fixed geometry/clusterer, with memory-bounded exact query blocks.

    Population z-score and row L2, exact cosine 5-NN with opaque-ID ties, positive
    mutual edges, greedy weighted modularity resolution 1, minimum group size 3.
    No labels or expected cluster count are accepted. Keep invalid/noise rows.
    """
    x = np.asarray(features, dtype=np.float64)
    n = len(ids)
    if x.ndim != 2 or len(x) != n or len(set(ids)) != n or not np.isfinite(x).all() or query_block < 1:
        raise ValueError('Invalid clustering feature axes/values/block size')
    raw_evidence = np.linalg.norm(x, axis=1) > 0
    if evidence is not None:
        evidence = np.asarray(evidence, dtype=bool)
        if evidence.shape != (n,):
            raise ValueError('Invalid embedding evidence mask')
        raw_evidence &= evidence
    mean = x[raw_evidence].mean(0) if raw_evidence.any() else np.zeros(x.shape[1])
    std = x[raw_evidence].std(0) if raw_evidence.any() else np.zeros(x.shape[1])
    usable = std > 1e-8
    z = np.zeros_like(x)
    z[:, usable] = (x[:, usable]-mean[usable])/std[usable]
    z[~raw_evidence] = 0
    norms = np.linalg.norm(z, axis=1)
    valid = raw_evidence & (norms > 1e-12)
    z[valid] /= norms[valid, None]
    candidates = np.array(sorted(np.flatnonzero(valid), key=lambda i: ids[i]), dtype=np.int64)
    neighbors, similarities = [[] for _ in ids], [{} for _ in ids]
    for start in range(0, n, query_block):
        similarity = np.clip(z[start:start+query_block]@z.T, -1, 1)
        for local, i in enumerate(range(start, min(start+query_block, n))):
            if not valid[i]:
                continue
            eligible = candidates[candidates != i]
            selected = eligible[np.argsort(-similarity[local, eligible], kind='stable')[:5]]
            neighbors[i] = selected.tolist()
            similarities[i] = {int(j): float(similarity[local, j]) for j in selected}
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    for i, nn in enumerate(neighbors):
        for j in nn:
            if i < j and i in neighbors[j] and similarities[i][j] > 0:
                graph.add_edge(i, j, weight=similarities[i][j])
    communities = nx.community.greedy_modularity_communities(graph, weight='weight', resolution=1.0) if graph.number_of_edges() else []
    accepted = sorted((sorted(c) for c in communities if len(c) >= 3), key=lambda c: min(ids[i] for i in c))
    assignment = np.full(n, -1, dtype=np.int64)
    reasons = ['zero_geometry_evidence' if not valid[i] else
               'isolated_graph' if graph.degree(i) == 0 else 'community_below_min_size' for i in range(n)]
    for label, community in enumerate(accepted):
        assignment[community] = label
        for i in community:
            reasons[i] = ''
    return dict(ids=list(ids), neighbors=[[ids[j] for j in nn] for nn in neighbors],
                assignment=assignment.tolist(), valid=valid.tolist(), reason=reasons,
                clusters=len(accepted), unassigned=int(sum(assignment < 0)), edges=graph.number_of_edges(),
                clustering=dict(k=5, mutual=True, positive_weights=True, resolution=1.0,
                                min_size=3, expected_cluster_count=None, query_block=query_block),
                transform=dict(mean=mean.tolist(), std=std.tolist(), usable=usable.tolist()))


def cluster(embeddings_path, output):
    """Cluster one byte-bound native embedding artifact; truth is never opened."""
    arrays, meta = load_arrays(embeddings_path, 'embeddings')
    result = geometry(arrays['features'], arrays['ids'].tolist(), arrays['evidence'])
    result.update(embedding_sha256=digest(embeddings_path),
                  embedding_manifest_sha256=digest(Path(embeddings_path).with_suffix('.json')),
                  parent_features_sha256=meta['features_sha256'], mode=meta['mode'])
    write_json(output, result)
    emit('partition_ready', clusters=result['clusters'], unassigned=result['unassigned'])


def export(features_path, partition_path, fasta_path, output):
    """Export every input contig once to assigned bins, unassigned or excluded FASTA.

    Reject mismatched DNA/features/partition axes and invalid labels before writing.
    Assignment TSV retains every ID, status/reason and length. No truth/marker
    selection is performed. Write a fresh directory with all-file hashes.
    """
    data, meta = load_arrays(features_path, 'features')
    validate_features(data, meta)
    rows = read_fasta(fasta_path)
    partition = json.loads(Path(partition_path).read_text())
    ids = data['ids'].tolist()
    if digest(fasta_path) != meta['fasta_sha256'] or [i for i, _ in rows] != ids:
        raise ValueError('Export DNA/feature identity mismatch')
    if partition['ids'] != ids or partition['parent_features_sha256'] != digest(features_path):
        raise ValueError('Export partition/feature identity mismatch')
    labels = np.array(partition['assignment'])
    if labels.shape != (len(ids),) or labels.dtype.kind not in 'iu' or (labels < -1).any():
        raise ValueError('Invalid/incomplete assignment labels')
    if len(partition['valid']) != len(ids) or len(partition['reason']) != len(ids):
        raise ValueError('Invalid partition mask/reason axes')
    observed = sorted(set(int(v) for v in labels if v >= 0))
    if observed != list(range(partition['clusters'])) or int(sum(labels < 0)) != partition['unassigned']:
        raise ValueError('Partition group/noise count mismatch')
    if ((labels >= 0) & (~data['eligible'] | ~np.array(partition['valid'], dtype=bool))).any():
        raise ValueError('Ineligible/invalid contig assigned to a bin')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    buckets = dict(unassigned=[], excluded=[])
    records = []
    for i, (ident, dna) in enumerate(rows):
        if not data['eligible'][i]:
            status, reason, name = 'excluded', str(data['exclusion_reason'][i]), 'excluded'
        elif labels[i] < 0:
            status, reason, name = 'unassigned', partition['reason'][i], 'unassigned'
        else:
            status, reason, name = 'assigned', '', f'bin_{int(labels[i])+1:06d}'
        buckets.setdefault(name, []).append((ident, dna))
        records.append(dict(contig_id=ident, length=len(dna), bin_id=name if status == 'assigned' else '',
                            status=status, reason=reason))
    with (output/'assignments.tsv').open('x') as stream:
        writer = csv.DictWriter(stream, fieldnames=['contig_id', 'length', 'bin_id', 'status', 'reason'], delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(records)
    for name, contigs in buckets.items():
        with (output/(name+'.fna')).open('x') as stream:
            for ident, dna in contigs:
                stream.write(f'>{ident}\n{dna}\n')
    files = {p.name: dict(bytes=p.stat().st_size, sha256=digest(p)) for p in sorted(output.iterdir())}
    write_json(output/'manifest.json', dict(features_sha256=digest(features_path),
               partition_sha256=digest(partition_path), fasta_sha256=digest(fasta_path),
               contigs=len(rows), bp=sum(len(dna) for _, dna in rows),
               assigned=sum(r['status'] == 'assigned' for r in records),
               unassigned=sum(r['status'] == 'unassigned' for r in records),
               excluded=sum(r['status'] == 'excluded' for r in records),
               bins=partition['clusters'], files=files))
    emit('export_complete', contigs=len(rows), bins=partition['clusters'])
