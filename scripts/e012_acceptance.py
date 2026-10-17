#!/usr/bin/env python3
"""Restore-only selection between sealed parents and their retained marker children.

No truth, new partition optimizer, marker detector, inference or cloud interface
is accepted here. Only the cached graph supplies the acceptance test. Outputs
are fresh, complete partitions and native product exports; inputs are read-only.
"""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import sys
import tarfile
import time

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e010_review import require, refinement_membership
from e011_cached import cached_graph, verify_restored
from e011_review import verify_refinement_inputs

REPO = Path(__file__).absolute().parents[1]
EXP = REPO/'experiments/E012-marker-acceptance'


def verify_inputs(lock, base=REPO):
    """Verify sealed restores, archive identities and each consumed CPM member.

    Missing or corrupt payloads fail explicitly. This consumer never extracts,
    recopies, reinstalls or creates replacement scientific evidence.
    """
    base = Path(base)
    for name, item in lock['files'].items():
        require(binding(base/name) == item, 'Locked input bytes differ: '+name)
    root = base/lock['cache']
    restored = verify_restored(root, lock['restore_manifest'], lock['e010_archive'])
    native = base/lock['native_return']
    require(binding(native/'collection-inventory.json') == lock['e011_inventory'],
            'Native inventory differs')
    inventory = json.loads((native/'collection-inventory.json').read_text())['files']
    for name in lock['native_members']:
        require(name in inventory and binding(native/name) == inventory[name],
                'Sealed native member differs: '+name)
    # Bind the original archive as well, without restoring or reading tool source.
    require(binding(base/lock['e011_archive_path']) == lock['e011_archive'],
            'Original native archive differs; no recopy')
    with tarfile.open(base/lock['e011_archive_path']) as archive:
        data = archive.extractfile('collection-inventory.json').read()
    import hashlib
    require(dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest()) == lock['e011_inventory'],
            'Archive inventory differs')
    return dict(restore=restored, native_consumers=len(lock['native_members']),
                original_archive_verified=True, no_restore_or_fallback=True)


def validate_proposals(pre, post, lengths, clean, cfg):
    """Read the actual frozen schema; refuse cross-parent, unrecorded or stale splits."""
    refinement_membership(pre, post)
    n = len(pre['ids'])
    require(len(set(pre['ids'])) == n and len(pre['reason']) == len(post['reason']) == n,
            'Duplicate ID or truncated reason axis')
    parents = defaultdict(list)
    for i, p in enumerate(pre['assignment']):
        if p >= 0:
            parents[p].append(i)
        else:
            require(pre['reason'][i] == post['reason'][i], 'Old noise/excluded reason changed')
    attempts = {}
    from dl_binner.candidate.grouping import conflicts
    for attempt in post['attempts']:
        p = attempt['pre_bin']
        require(type(p) is int and p in parents and p not in attempts,
                'Unknown/duplicate recorded parent')
        require(type(attempt['adopted']) is bool
                and attempt['before'] == conflicts(parents[p], clean, pre['ids']),
                'Retained marker conflict evidence differs')
        attempts[p] = attempt
    proposals = {}
    for p, members in parents.items():
        children = defaultdict(list)
        for i in members:
            children[post['assignment'][i]].append(i)
        adopted = attempts.get(p, {}).get('adopted', False)
        if not adopted:
            require(len(children) == 1 and next(iter(children)) >= 0,
                    'Unrecorded split or unassignment')
            require(all(pre['reason'][i] == post['reason'][i] for i in members),
                    'Unadopted parent reason changed')
            continue
        a = attempts[p]
        groups = [v for k, v in sorted(children.items()) if k >= 0]
        noise = children.get(-1, [])
        require(len(groups) == a['k'] >= 2 and len(noise) == a['unassigned_proposal']
                and len(a['seed_ids']) == a['k'] and len(set(a['seed_ids'])) == a['k'],
                'Retained proposal child/seed/noise counts differ')
        require(sorted(sum(int(lengths[i]) for i in c) for c in groups) == sorted(a['proposed_bp'])
                and all(len(c) >= cfg['min_bin_contigs'] and sum(int(lengths[i]) for i in c) >= cfg['min_bin_bp']
                        and not conflicts(c, clean, pre['ids']) for c in groups),
                'Retained child support/conflicts differ')
        for seed in a['seed_ids']:
            require(seed in {pre['ids'][i] for i in members}
                    and a['seed_family'] in clean.get(seed, []), 'Seed cache identity differs')
        proposals[p] = dict(members=members, groups=groups, noise=noise, attempt=a)
    return parents, proposals


def gains(edges, weights, pre, post, proposals, gamma):
    """Compute CPM half-quality deltas with all noise vertices as separate singletons.

    Delta = gamma * newly separated node pairs - cut weight. Both endpoints of
    each undirected edge occur once; all positive edges lost to noise count.
    Near-zero ties retain the parent using eight ULPs of the larger term.
    """
    require(math.isfinite(gamma) and gamma > 0, 'Invalid frozen density')
    cut = defaultdict(list)
    for (i, j), weight in zip(edges, weights):
        p = pre['assignment'][int(i)]
        if p in proposals and p == pre['assignment'][int(j)]:
            a, b = post['assignment'][int(i)], post['assignment'][int(j)]
            if a < 0 or b < 0 or a != b:
                cut[p].append(float(weight))
    result = {}
    choose = lambda n: n*(n-1)//2
    for p, proposal in proposals.items():
        pairs = choose(len(proposal['members']))-sum(choose(len(c)) for c in proposal['groups'])
        penalty_saved = gamma*pairs
        cut_weight = math.fsum(cut[p])
        delta = math.fsum([penalty_saved, -cut_weight])
        tolerance = 8*math.ulp(max(1., abs(penalty_saved), abs(cut_weight)))
        result[p] = dict(separated_pairs=pairs, penalty_saved=penalty_saved,
                         cut_weight=cut_weight, delta_half_quality=delta, tolerance=tolerance,
                         accepted=delta > tolerance,
                         parent_contigs=len(proposal['members']),
                         child_contigs=[len(c) for c in proposal['groups']],
                         unassigned_contigs=len(proposal['noise']))
    return result


def select(data, graph, pre, post, clean, cfg, gamma):
    """Select whole retained alternatives, canonicalizing labels without new grouping."""
    import numpy as np
    from dl_binner.candidate.grouping import canonical_partition
    ids = data['ids'].tolist()
    require(pre['ids'] == ids and pre['valid'] == post['valid'], 'Selection axis differs')
    require(not np.any(np.asarray(pre['valid']) & ~data['eligible']), 'Ineligible geometry became valid')
    cached_graph(graph, ids, np.array(pre['valid'], bool))
    parents, proposals = validate_proposals(pre, post, data['lengths'], clean, cfg)
    ledger = gains(graph['edges'], graph['weights'], pre, post, proposals, gamma)
    groups, reasons = [], list(pre['reason'])
    for p, members in sorted(parents.items()):
        if p in ledger and ledger[p]['accepted']:
            groups.extend(proposals[p]['groups'])
            for i in proposals[p]['noise']:
                reasons[i] = post['reason'][i]
        else:
            groups.append(members)
    result = canonical_partition(ids, pre['valid'], groups, data['lengths'], cfg, reasons)
    result.update(neighbors=pre['neighbors'], parent_features_sha256=pre['parent_features_sha256'],
                  graph_sha256=pre['graph_sha256'], embedding_sha256=pre['embedding_sha256'],
                  algorithm='restore-only parent/retained-child CPM-gain gate',
                  config=cfg, scientific_quality_assessed=False)
    refinement_membership(pre, result)
    result['selection'] = dict(gamma=gamma, node_sizes=1, noise_scoring='one singleton per unassigned vertex',
                              rule='delta_half_quality > 8 ULP of max(1, penalty_saved, cut_weight)')
    return result, [dict(pre_bin=p, seed_family=proposals[p]['attempt']['seed_family'], **v)
                    for p, v in sorted(ledger.items())]


def run(lock_path, protocol_path, output, base=REPO):
    """Verify retained bytes/axes; serially select and fully export both contexts."""
    import numpy as np
    from dl_binner.io import load_arrays, read_depth, digest
    from dl_binner.candidate.views import load
    from dl_binner.candidate.markers import load_cache
    from dl_binner.clustering import export
    from dl_binner.accounting import summarize_arm
    from e011_cached import probe
    base, output = Path(base), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    lock, protocol = json.loads(Path(lock_path).read_text()), json.loads(Path(protocol_path).read_text())
    verification = verify_inputs(lock, base)
    root = base/lock['cache']/'candidate'
    probe(base/lock['cache'], output/'runtime.json', native=False)
    f, e, g = root/'features/features.npz', root/'embed/embeddings.npz', root/'group/graph.npz'
    data, fm = load(f); vectors, em = load_arrays(e, 'embeddings'); graph, gm = load_arrays(g, 'candidate_sparse_graph')
    ids = data['ids'].tolist(); cfg = json.loads((root/'candidate.json').read_text())
    require(cfg == protocol['config'], 'Frozen config differs')
    require(vectors['ids'].tolist() == ids and em['features_sha256'] == digest(f)
            and gm['embedding_sha256'] == digest(e), 'Feature/embedding/graph binding differs')
    valid = data['eligible'] & vectors['evidence']
    require(vectors['features'].shape == (len(ids), cfg['output'])
            and np.isfinite(vectors['features']).all() and not np.any(vectors['features'][~valid])
            and np.allclose(np.linalg.norm(vectors['features'][valid], axis=1), 1, atol=1e-5),
            'Original unit geometry differs; no inference fallback')
    fasta, depth = base/lock['fasta'], base/lock['depth']
    samples, matrix = read_depth(depth, ids)
    require(samples == protocol['samples'] == fm['samples'] and np.array_equal(matrix, data['depth']),
            'Full ordered ten-depth axes differ')
    evidence = load_cache(root/'markers', fasta, ids)
    gamma = float(np.median(graph['weights']))/cfg['neighbors']
    require(gamma == protocol['rule']['gamma'], 'Original label-free density differs')
    contexts = {}
    for context, files in lock['contexts'].items():
        print('E012_CONTEXT_START '+context, flush=True)
        pre_path, post_path = [base/p for p in files]
        pre, post = [json.loads(p.read_text()) for p in [pre_path, post_path]]
        require(pre['valid'] == valid.tolist(), 'Context complete valid axis differs')
        require(pre['config'] == cfg and pre['graph_sha256'] == digest(g)
                and pre['embedding_sha256'] == digest(e), 'Context source/geometry differs')
        verify_refinement_inputs(pre, post, digest(pre_path), digest(f), digest(root/'markers/cache.json'))
        selected, mapped_edges = cached_graph(graph, ids, valid)
        require(graph['neighbors'].shape == (len(ids), cfg['neighbors']), 'Retained neighbor shape differs')
        for i, row in enumerate(graph['neighbors']):
            require(pre['neighbors'][i] == ([ids[j] for j in row[:5]] if valid[i] else []),
                    'Retained neighbor IDs differ')
        result, decisions = select(data, graph, pre, post, evidence['clean'], cfg, gamma)
        destination = output/context; destination.mkdir()
        write_json(destination/'partition.json', result)
        write_json(destination/'decisions.json', decisions)
        export(f, destination/'partition.json', fasta, destination/'export')
        accounting = summarize_arm(f, destination/'export')[0]
        write_json(destination/'accounting.json', accounting)
        contexts[context] = dict(proposals=len(decisions), accepted=sum(x['accepted'] for x in decisions),
                                 accounting=accounting, partition=binding(destination/'partition.json'),
                                 decisions=binding(destination/'decisions.json'))
        print('E012_CONTEXT_COMPLETE '+context, flush=True)
    require(verification == verify_inputs(lock, base), 'Consumed evidence changed during execution')
    result = dict(status='SUCCESS', input_lock=binding(lock_path), protocol=binding(protocol_path),
                  verification=verification, contexts=contexts, samples=samples,
                  contigs=len(ids), bp=int(data['lengths'].sum()), valid=int(valid.sum()),
                  edges=len(graph['edges']), dimensions=cfg['output'], gamma=gamma,
                  wall_seconds=time.monotonic()-started, truth_accessed=False,
                  no_new_splits_training_detection_index_or_optimizer=True)
    write_json(output/'completed.json', result)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock', type=Path, default=EXP/'input-lock.json')
    p.add_argument('--protocol', type=Path, default=EXP/'protocol.json')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    run(a.lock, a.protocol, a.output)
