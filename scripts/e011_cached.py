#!/usr/bin/env python3
"""Restore accepted E010 evidence and run one frozen cached objective/reference.

No encoder training, marker search, neighbor-index construction, truth or cloud
API is reachable here. Fresh directories and exact byte/axis contracts are
required. The external parent owns the cumulative clock, logs and shutdown.
"""
import argparse
from collections import Counter
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile
import time

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e010_review import require, sparse_graph_contract, refinement_membership

REPO = Path(__file__).absolute().parents[1]
PROTOCOL = REPO/'experiments/E011-cached-grouping-reference/protocol.json'


def restore(archive, destination, expected, inventory_expected=None):
    """Verify every sealed member; extract only cached consumers to a fresh root.

    Never read original tool source, recreate missing artifacts or extract links.
    The checksum-bound inventory itself is verified separately from its members.
    Original full exports remain protected in the original private archive.
    """
    require(binding(archive) == expected, 'Accepted archive bytes differ; no fallback')
    destination = Path(destination)
    require(not destination.exists(), 'Restore needs a fresh directory; no resume')
    with tarfile.open(archive) as tar:
        raw = tar.extractfile('collection-inventory.json').read()
    actual = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    require(inventory_expected is None or actual == inventory_expected, 'Inventory binding differs')
    inventory = json.loads(raw)['files']; destination.mkdir(parents=True)
    selected, seen = {}, set()
    prefixes = ('candidate/features/features.', 'candidate/embed/', 'candidate/group/',
                'candidate/refine/', 'candidate/markers/')
    names = {'candidate/candidate.json', 'candidate/run-manifest.json', 'runtime.json', 'installed.json'}
    with tarfile.open(archive, 'r|gz') as tar:
        for member in tar:
            name = member.name; pure = PurePosixPath(name)
            require(member.isfile() and not pure.is_absolute() and '..' not in pure.parts
                    and name not in seen, 'Unsafe/duplicate retained member')
            seen.add(name)
            wanted = name in names or name.startswith(prefixes)
            stream = tar.extractfile(member); digest = hashlib.sha256(); count = 0
            target = destination.joinpath(*pure.parts)
            if wanted:
                target.parent.mkdir(parents=True, exist_ok=True)
                writer = target.open('xb')
            else:
                writer = None
            try:
                for block in iter(lambda: stream.read(1024**2), b''):
                    count += len(block); digest.update(block)
                    if writer is not None: writer.write(block)
            finally:
                if writer is not None: writer.close()
            record = dict(bytes=count, sha256=digest.hexdigest())
            require(record == (actual if name == 'collection-inventory.json' else inventory.get(name)),
                    'Retained member checksum mismatch: '+name)
            if wanted: selected[name] = record
    require(seen == set(inventory) | {'collection-inventory.json'}, 'Retained member set differs')
    result = dict(archive=expected, inventory=actual, verified_members=len(seen),
                  restored_files=selected, restore_only=True)
    write_json(destination/'restore.json', result)
    return result


def cached_graph(graph, ids, valid):
    """Map retained full FASTA endpoints to the original opaque-ID vertex order."""
    import numpy as np
    require(graph['ids'].tolist() == ids, 'Graph/FASTA ordered IDs differ')
    sparse_graph_contract(graph['edges'], graph['weights'], ids, valid)
    selected = np.array(sorted(np.flatnonzero(valid), key=lambda i: ids[i]), np.int64)
    inverse = np.full(len(ids), -1, np.int64); inverse[selected] = np.arange(len(selected))
    edges = inverse[graph['edges']]
    require(np.all(edges >= 0) and np.all(edges[:, 0] < edges[:, 1]), 'Opaque-ID graph map differs')
    return selected, edges


def cpm_partition(data, embeddings, graph, pre, cfg, features_path, graph_path):
    """Run the sole predeclared CPM rule on unchanged weights and unit vectors."""
    import numpy as np
    import igraph as ig
    import leidenalg
    from dl_binner.candidate.grouping import canonical_partition
    ids = data['ids'].tolist(); valid = data['eligible'] & embeddings['evidence']
    require(pre['ids'] == ids and pre['valid'] == valid.tolist(), 'Native prepopulation differs')
    require(np.isfinite(embeddings['features']).all()
            and np.allclose(np.linalg.norm(embeddings['features'][valid], axis=1), 1, atol=1e-5)
            and not np.any(embeddings['features'][~valid]), 'Original unit geometry required')
    selected, edges = cached_graph(graph, ids, valid)
    weights = graph['weights']; require(len(weights) > 0, 'Missing positive cached graph')
    require(graph['neighbors'].shape == (len(ids), min(cfg['neighbors'],int(valid.sum())-1)), 'Frozen neighbor count differs')
    for i, row in enumerate(graph['neighbors']):
        require(pre['neighbors'][i] == ([ids[j] for j in row[:5]] if valid[i] else []),
                'Retained top-five axis differs')
    gamma = float(np.median(weights))/cfg['neighbors']
    native = ig.Graph(n=len(selected), edges=edges.tolist(), directed=False)
    groups = leidenalg.find_partition(native, leidenalg.CPMVertexPartition,
        weights=weights.tolist(), node_sizes=[1]*len(selected), resolution_parameter=gamma,
        seed=cfg['seed'], n_iterations=cfg['leiden_iterations'])
    result = canonical_partition(ids, valid, [[int(selected[j]) for j in c] for c in groups], data['lengths'], cfg)
    result.update(neighbors=pre['neighbors'], parent_features_sha256=binding(features_path)['sha256'],
        embedding_sha256=pre['embedding_sha256'], graph_sha256=binding(graph_path)['sha256'],
        algorithm='cached weighted graph / Leiden CPM', config=cfg,
        objective=dict(gamma=gamma, rule='median_positive_retained_edge_weight / frozen_neighbor_count',
                       node_sizes=1, seed=cfg['seed'], n_iterations=cfg['leiden_iterations'],
                       native_quality=float(groups.quality()), vertices=len(selected), edges=len(edges)),
        audit=pre['audit'], transform='none; learned unit sphere preserved')
    return result


def probe(root, output, native=True):
    """Verify the reused complete inventory/source, isolated origins and lexical prefix."""
    import dl_binner
    import numpy
    import igraph
    import leidenalg
    from dl_binner.runner import source_records
    lock = json.loads((REPO/'experiments/E010-coherent-prototype/candidate-lock.json').read_text())
    expected = json.loads((Path(root)/'runtime.json').read_text())
    normal = lambda s: re.sub('[-_.]+', '-', s).lower()
    actual = {normal(d.metadata['Name']): d.version for d in importlib.metadata.distributions()}
    if native:
        require(actual == expected['distributions'] and sys.prefix == expected['prefix']
                and sys.version_info[:2] == (3, 12), 'Reused complete native runtime differs')
    require(source_records() == lock['package_files'], 'Frozen installed package/default source differs')
    origins = {m.__name__: str(Path(m.__file__).absolute()) for m in [dl_binner,numpy,igraph,leidenalg]}
    require(all(Path(p).is_relative_to(Path(sys.prefix)) for p in origins.values()), 'External import origin')
    require(sys.dont_write_bytecode and sys.flags.isolated, 'Isolated -I -B Python required')
    write_json(output, dict(distributions=actual, origins=origins, prefix=sys.prefix,
                           base_prefix=sys.base_prefix, source=source_records(), native=native))


def control(root, fasta, depth, output, protocol):
    """Consume accepted parents/cache and export one CPM partition before/after refinement."""
    import numpy as np
    from dl_binner.io import load_arrays, read_depth, digest
    from dl_binner.candidate.views import load
    from dl_binner.candidate.markers import load_cache
    from dl_binner.candidate.grouping import refine_partition
    from dl_binner.clustering import export
    from dl_binner.accounting import summarize_arm
    root, output = Path(root)/'candidate', Path(output); output.mkdir(parents=True, exist_ok=False)
    f = root/'features/features.npz'; g = root/'group/graph.npz'; e = root/'embed/embeddings.npz'
    data, meta = load(f); vectors, em = load_arrays(e, 'embeddings'); graph, gm = load_arrays(g, 'candidate_sparse_graph')
    pre = json.loads((root/'group/partition.json').read_text()); cfg = protocol['config']
    require(json.loads((root/'candidate.json').read_text()) == cfg and pre['config'] == cfg,
            'Frozen candidate config differs')
    require(binding(fasta) == protocol['inputs']['fasta'] and binding(depth) == protocol['inputs']['depth'],
            'Accepted full assembly/depth bytes differ')
    require(vectors['ids'].tolist() == data['ids'].tolist() and em['features_sha256'] == digest(f)
            and gm['embedding_sha256'] == digest(e) and pre['graph_sha256'] == digest(g), 'Cached input binding differs')
    samples, measured = read_depth(depth, data['ids'].tolist())
    require(samples == meta['samples'] and np.array_equal(measured, data['depth']), 'Full ten-depth axes differ')
    evidence = load_cache(root/'markers', fasta, data['ids'].tolist())
    started = time.monotonic(); result = cpm_partition(data, vectors, graph, pre, cfg, f, g)
    write_json(output/'pre.json', result)
    post = refine_partition(result, data, vectors['features'], evidence['clean'], cfg)
    post.update(pre_partition_sha256=digest(output/'pre.json'), marker_cache_sha256=digest(root/'markers/cache.json'))
    write_json(output/'post.json', post)
    refinement = refinement_membership(result, post)
    accounting = {}
    for arm in ['pre','post']:
        export(f, output/(arm+'.json'), fasta, output/arm)
        accounting[arm] = summarize_arm(f, output/arm)[0]
    write_json(output/'completed.json', dict(status='SUCCESS', objective=result['objective'],
        protocol=binding(PROTOCOL), original_graph=binding(g), original_embeddings=binding(e),
        original_marker_cache=binding(root/'markers/cache.json'), refinement=refinement,
        accounting=accounting, wall_seconds=time.monotonic()-started, no_training_or_detection_or_index=True))


def external_export(fasta, native, output):
    """Validate native bin DNA and export every original row exactly once, without features.

    MetaBAT's 2,500-bp seeds and enabled >=1,000-bp recruitment differ from dev4.
    Missing native bins after a successful native exit mean unassigned, never a
    substituted failed run. The caller must verify its native exit independently.
    """
    from dl_binner.io import read_fasta, digest
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    rows = read_fasta(fasta); originals = dict(rows); assignments = {}; buckets = {}
    for path in sorted(Path(native).glob('bin.*.fa')):
        if not re.fullmatch(r'bin\.\d+\.fa', path.name): continue
        label = 'bin_'+path.name.split('.')[1]
        for ident, dna in read_fasta(path):
            require(ident in originals and dna == originals[ident] and ident not in assignments,
                    'Native external bin has unknown/changed/duplicate DNA')
            assignments[ident] = label
    totals = {s: dict(contigs=0,bp=0) for s in ['assigned','unassigned','excluded']}
    strata = {}; records = []
    for ident, dna in rows:
        label = assignments.get(ident); bp = len(dna)
        status = 'assigned' if label else 'excluded' if bp < 1000 else 'unassigned'
        require(not label or bp >= 1000, 'MetaBAT assigned DNA below native small-contig minimum')
        reason = '' if label else 'native_below_small_contig_minimum' if bp < 1000 else 'native_not_assigned'
        buckets.setdefault(label or status, []).append((ident,dna))
        records.append(dict(contig_id=ident,length=bp,bin_id=label or '',status=status,reason=reason))
        totals[status]['contigs'] += 1; totals[status]['bp'] += bp
        low = max(n for n in [1,500,768,1000,2500,10000] if bp >= n)
        item = strata.setdefault(str(low),Counter()); item[status+'_contigs'] += 1; item[status+'_bp'] += bp
    with (output/'assignments.tsv').open('x') as stream:
        writer=csv.DictWriter(stream,fieldnames=['contig_id','length','bin_id','status','reason'],delimiter='\t',lineterminator='\n')
        writer.writeheader();writer.writerows(records)
    for name, values in buckets.items():
        with (output/(name+'.fna')).open('x') as stream:
            for ident,dna in values: stream.write('>'+ident+'\n'+dna+'\n')
    observed = {}
    for path in output.glob('*.fna'):
        for ident,dna in read_fasta(path):
            require(ident not in observed and dna == originals[ident], 'External export DNA differs')
            observed[ident] = len(dna)
    require(set(observed) == set(originals), 'External export lost original DNA')
    result = dict(contigs=len(rows), bp=sum(map(len, originals.values())), bins=len(set(assignments.values())),
        statuses=totals, length_strata={k:dict(v)for k,v in strata.items()},
        seed_minimum_bp=2500, small_contig_minimum_bp=1000,
        files={q.name:binding(q)for q in sorted(output.iterdir())})
    write_json(output/'manifest.json', result)
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['restore','probe','control','external-export'])
    for name in ['archive','root','fasta','depth','output','native','native-exit']:p.add_argument('--'+name,type=Path)
    p.add_argument('--local',action='store_true');a=p.parse_args();protocol=json.loads(PROTOCOL.read_text())
    if a.action == 'restore': restore(a.archive,a.output,protocol['archive']['archive'],protocol['archive'].get('inventory'))
    elif a.action == 'probe': probe(a.root,a.output,native=not a.local)
    elif a.action == 'control': control(a.root,a.fasta,a.depth,a.output,protocol)
    else:
        require(a.native_exit is not None, 'Native success receipt required; no empty failed partition')
        receipt=json.loads(a.native_exit.read_text())
        require(receipt['exit_code']==0 and receipt['stop_reason']is None, 'Native external run failed')
        require(binding(a.fasta)==protocol['inputs']['fasta'], 'Full accepted assembly differs')
        external_export(a.fasta,a.native,a.output)
