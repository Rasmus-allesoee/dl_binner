#!/usr/bin/env python3
"""Restore-only E013 consumer with cached-artifact reload and complete DNA export.

The installed dev4 package, encoder/vectors/graph and scientific inputs stay
immutable. New research refinement code is frozen separately by Git/hash. No
truth, detector, neighbor builder, graph optimizer or cloud API is used in this stage.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e010_review import require, refinement_membership
from e011_cached import probe, cached_graph
from e011_review import verify_refinement_inputs
from e012_acceptance import verify_inputs, validate_proposals, gains
from e012_marker_audit import profile_headers
from e013_refinement import marker_evidence, refine

REPO = Path(__file__).absolute().parents[1]
EXP = REPO/'experiments/E013-marker-quality'


def run(lock_path, protocol_path, output, base=REPO):
    """Verify sealed readers/axes, refine once, reload and independently export all DNA."""
    import numpy as np
    from dl_binner.io import load_arrays, read_depth, digest
    from dl_binner.candidate.views import load
    from dl_binner.candidate.markers import load_cache
    from dl_binner.clustering import export
    from dl_binner.accounting import summarize_arm
    started = time.monotonic(); output = Path(output); base = Path(base)
    output.mkdir(parents=True, exist_ok=False)
    lock, protocol = [json.loads(Path(p).read_text()) for p in [lock_path, protocol_path]]
    verification = verify_inputs(lock, base)
    root = base/lock['cache']/'candidate'; f = root/'features/features.npz'
    e, g = root/'embed/embeddings.npz', root/'group/graph.npz'
    probe(base/lock['cache'], output/'runtime.json', native=False)
    data, meta = load(f); vectors, em = load_arrays(e, 'embeddings'); graph, gm = load_arrays(g, 'candidate_sparse_graph')
    ids = data['ids'].tolist(); support = json.loads((root/'candidate.json').read_text())
    require(support == protocol['candidate_config'] and support['seed'] == protocol['refinement']['seed'],
            'Frozen seed/default/source differs')
    require(vectors['ids'].tolist() == ids and em['features_sha256'] == digest(f)
            and gm['embedding_sha256'] == digest(e), 'Feature/vector/graph bindings differ')
    valid = data['eligible'] & vectors['evidence']; cached_graph(graph, ids, valid)
    samples, measured = read_depth(base/lock['depth'], ids)
    require(samples == protocol['samples'] == meta['samples'] and np.array_equal(measured, data['depth']),
            'Complete ordered depth axes differ')
    pre_path, post_path = [base/p for p in lock['contexts']['CPM']]
    pre, post = [json.loads(p.read_text()) for p in [pre_path, post_path]]
    require(pre['valid'] == valid.tolist() and pre['config'] == support
            and pre['graph_sha256'] == digest(g) and pre['embedding_sha256'] == digest(e), 'CPM parent differs')
    for i, row in enumerate(graph['neighbors']):
        require(pre['neighbors'][i] == ([ids[j] for j in row[:5]] if valid[i] else []), 'Retained neighbor axis differs')
    verify_refinement_inputs(pre, post, digest(pre_path), digest(f), digest(root/'markers/cache.json'))
    old = load_cache(root/'markers', base/lock['fasta'], ids)
    _, old_proposals = validate_proposals(pre, post, data['lengths'], old['clean'], support)
    hmm = base/lock['hmm_path']; asset = json.loads((root/'markers/asset.json').read_text())
    require(binding(hmm) == asset['hmm'] == lock['files'][lock['hmm_path']], 'Pinned HMM bytes differ')
    genes = {}
    with (root/'markers/genes.jsonl').open() as stream:
        for raw in stream:
            item = json.loads(raw); name = item.pop('gene'); require(name not in genes, 'Duplicate gene'); genes[name] = item
    domains = json.loads((root/'markers/domains.json').read_text())
    evidence = marker_evidence(genes, domains, asset['families'], profile_headers(hmm), ids, data['lengths'], protocol['refinement'])
    write_json(output/'quality-evidence.json', dict(evidence, input_cache=binding(root/'markers/cache.json'),
        config=protocol['refinement'], ids=ids))
    reloaded = json.loads((output/'quality-evidence.json').read_text())
    require(all(reloaded[k] == v for k, v in evidence.items()), 'Cached quality-evidence reload differs')
    print('E013_REFINEMENT_START', len(ids), len(evidence['loci']), flush=True)
    partition, decisions, alternatives, transforms = refine(pre, post, data, vectors['features'],
        reloaded, old_proposals, protocol['refinement'], support)
    write_json(output/'partition.json', partition); write_json(output/'decisions.json', decisions)
    write_json(output/'alternatives.json', alternatives); write_json(output/'context-transforms.json', transforms)
    require(json.loads((output/'partition.json').read_text()) == partition, 'Partition reload differs')
    # Log graph changes after quality selection; graph gain never selects bins.
    parents = {}
    for d in decisions:
        if d['selected'] != 'parent':
            p = d['pre_bin']; members = [i for i, b in enumerate(pre['assignment']) if b == p]
            labels = {}
            for i in members:
                labels.setdefault(partition['assignment'][i], []).append(i)
            parents[p] = dict(members=members, groups=[c for b, c in labels.items() if b >= 0], noise=labels.get(-1, []))
    graph_audit = gains(graph['edges'], graph['weights'], pre, partition, parents, pre['objective']['gamma'])
    for record in graph_audit.values():
        record['graph_gain_positive'] = record.pop('accepted')
    write_json(output/'selected-graph-audit.json', graph_audit)
    membership = refinement_membership(pre, partition)
    export(f, output/'partition.json', base/lock['fasta'], output/'export')
    accounting = summarize_arm(f, output/'export')[0]
    require(verification == verify_inputs(lock, base), 'Input evidence changed during execution')
    require(binding(hmm) == lock['files'][lock['hmm_path']], 'Profile changed during execution')
    result = dict(status='SUCCESS', protocol=binding(protocol_path), input_lock=binding(lock_path), verification=verification,
        partition=binding(output/'partition.json'), decisions=binding(output/'decisions.json'),
        alternatives=binding(output/'alternatives.json'), quality_evidence=binding(output/'quality-evidence.json'),
        context_transforms=binding(output/'context-transforms.json'), graph_audit=binding(output/'selected-graph-audit.json'),
        selection=dict(Counter(d['selected'] for d in decisions)),
        new_proposals=sum(any(v['route'] == 'median_seeded' for v in a['alternatives']) for a in alternatives),
        parents=len(set(b for b in pre['assignment'] if b >= 0)), assessed_parents=len(decisions),
        samples=samples, contigs=len(ids), bp=int(data['lengths'].sum()), membership=membership,
        accounting=accounting, truth_accessed=False, encoder_graph_seed_unchanged=True,
        no_detector_inference_neighbor_build_or_graph_optimizer=True, wall_seconds=time.monotonic()-started)
    write_json(output/'completed.json', result); return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock', type=Path, default=EXP/'input-lock.json')
    p.add_argument('--protocol', type=Path, default=EXP/'protocol.json')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); run(a.lock, a.protocol, a.output)
