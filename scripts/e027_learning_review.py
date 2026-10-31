#!/usr/bin/env python3
"""Read completed E027 learning components; never promote missing group outputs.

Checks native seals/source/schedule, exact reload bytes, full contig/sample axes,
original proposal provenance and cached graph geometry. Biological diagnostics
are restricted to the three genuinely new fits; reused learning summaries are
not rescored. There is no model inference, new neighbor index, bin selection or
recovery score here. The failed outer workflow remains failed.
"""
import argparse
import gc
import json
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e027_inspection import read, require, seal_from_inventory
from e024_coverage import binding, write


def frozen_manifest_contract(metadata, expected):
    """Respect the pinned context writer's omission; other writers require a hash key."""
    kind = metadata['kind']
    require(('hybrid' in metadata['config']) == (expected is not None), 'GLM constructor availability differs')
    if kind == 'context_checkpoint':
        require(expected is None and 'training_frozen_sha256' not in metadata,
                'Context writer has an unexpected frozen-bank field')
    else:
        require(kind in ['hybrid_checkpoint', 'relational_checkpoint'] and
                'training_frozen_sha256' in metadata and metadata['training_frozen_sha256'] == expected,
                'Hybrid/relational frozen-bank provenance is missing or differs')


def neighborhood_census(data, neighbors, labels, targets, clean):
    """Count five-neighbor origin support with full unknown/length/depth strata."""
    import numpy as np
    from e009_controls_review import BOUNDS
    cells = {}; ids = data['ids'].tolist(); eligible = data['eligible']
    for i in range(len(ids)):
        n = int(data['lengths'][i]); q = ids[i]; origin = labels.get(q)
        category = 'positive_cellular_target' if origin in targets else 'known_non_target' if origin is not None else 'unattributed'
        key = '|'.join([str(max(b for b in BOUNDS if n >= b)), category,
            'eligible' if eligible[i] else 'excluded', 'clean_marker' if q in clean else 'marker_negative_or_uncertain',
            'measured_positive_depth' if data['depth_evidence'][i] else 'measured_all_zero'])
        cell = cells.setdefault(key, dict(contigs=0, bp=0, queries=0, query_bp=0,
            same_origin_neighbors=0, same_origin_bp_weighted=0., unknown_neighbors=0))
        cell['contigs'] += 1; cell['bp'] += n
        if not eligible[i]: continue
        near = neighbors[i, :5]
        require(len(near) == 5 and np.all(near >= 0), 'Native display neighbors incomplete')
        sources = [labels.get(ids[int(j)]) for j in near]
        cell['queries'] += 1; cell['query_bp'] += n; cell['unknown_neighbors'] += sources.count(None)
        same = sources.count(origin) if origin is not None else 0
        cell['same_origin_neighbors'] += same; cell['same_origin_bp_weighted'] += n*same/5
    summary = {}
    for category in ['positive_cellular_target', 'known_non_target', 'unattributed']:
        selected = [c for k, c in cells.items() if k.split('|')[1] == category]
        q = sum(c['queries'] for c in selected); bp = sum(c['query_bp'] for c in selected)
        summary[category] = dict(queries=q, query_bp=bp,
            same_origin_fraction=sum(c['same_origin_neighbors'] for c in selected)/(5*q) if q and category != 'unattributed' else None,
            bp_weighted_same_origin=sum(c['same_origin_bp_weighted'] for c in selected)/bp if bp and category != 'unattributed' else None,
            unknown_endpoints=sum(c['unknown_neighbors'] for c in selected))
    return dict(summary=summary, cells=cells, full_rows=len(ids), full_bp=int(data['lengths'].sum()),
        scope='Full cached native five-neighbor population, dominant conservative/provided-origin labels; not unique-source proof. Unknown endpoints stay in five-neighbor denominator.')


class NeighborIDs:
    """Expose only requested display rows without copying millions of ID lists."""
    def __init__(self, ids, graph): self.ids, self.graph = ids, graph
    def __getitem__(self, i): return [self.ids[int(j)] for j in self.graph[i, :5]]


def review(args):
    """Validate one complete learning chain, then describe only its new fits."""
    import numpy as np
    from threadpoolctl import threadpool_limits
    from dl_binner.multiview.views import load
    from dl_binner.information.grouping import load_inputs
    from dl_binner.density.grouping import sparse_input
    from dl_binner.unified.training import configuration
    from dl_binner.relational.pairs import policy as pair_policy, load_pairs
    from e014_review import parent_geometry, oral_labels
    from e022_review import pair_label_audit
    threadpool_limits(4)
    inv = read(Path(args.verified)/'inventory.json'); global_status = read(args.status)
    require(global_status['provider_status'] == 'TERMINATED' and
            read(Path(args.verified)/'archive-verified.json')['every_member_verified'] is True and
            read(args.finance)['cost_and_retention_admitted'] is True and
            read(args.source)['source']['status'] == 'PASS', 'Stopped byte/source/cost admission required')
    root = Path(args.staged)/'work/units'/args.unit
    for name in ['admit', 'teacher', 'teacher-embed', 'teacher-graph', 'pairs', 'student', 'student-embed', 'student-graph']:
        seal_from_inventory(read(root/name/'done.json'), 'units/'+args.unit+'/'+name, inv)
    plan = read(Path(args.controls)/'evidence/plan.json'); u = plan['units'][args.unit]
    lock = read(ROOT/'experiments/E027-common-information-binner/reuse-lock.json')
    require(binding(Path(args.features)) == lock['files'][u['features']], 'Accepted local feature bytes differ')
    data, meta = load(args.features); ids = data['ids'].tolist()
    axis = read(ROOT/'experiments/E027-common-information-binner/protocol.json')['axes'][args.unit]
    require(len(ids) == axis['rows'] and int(data['lengths'].sum()) == axis['bp'] and
            int(data['eligible'].sum()) == axis['eligible'] and meta['samples'] == axis['samples'], 'Full learning axes differ')
    views = inv['all_work_members']['units/'+args.unit+'/admit/views.npz']
    tokens = binding(root/'admit/tokens/tokens.json')
    frozen = lock['files'][u['frozen']+'/bank.json']['sha256'] if u['frozen'] else None
    proposal = read(root/'pairs/cache/cache.json')
    pair_arrays, pair_metadata = load_pairs(root/'pairs/cache', args.features)
    require(proposal['inputs']['embeddings'] == inv['all_work_members']['units/'+args.unit+'/teacher-embed/embeddings.npz'] and
            proposal['inputs']['graph'] == inv['all_work_members']['units/'+args.unit+'/teacher-graph/graph.npz'],
            'Own information-policy proposal teacher differs')
    records = {}; actual_new = ['teacher', 'student'] if args.unit == 'oral-noGLM' else ['student'] if args.unit == 'E009-noGLM' else []
    for role in ['teacher', 'student']:
        m = read(root/role/'checkpoint.json'); e = read(root/(role+'-embed/embeddings.json'))
        cfg = configuration(args.unit == 'E009-GLM')
        if role == 'student': cfg = dict(cfg, relational=pair_policy())
        frozen_manifest_contract(m, frozen)
        require(m['config'] == cfg and m['samples'] == meta['samples'] and m['threads'] == 4 and
                m['loader_workers'] == 0 and m['training_parents'] == axis['eligible'] and
                m['training_features_sha256'] == binding(Path(args.features))['sha256'] and
                m['training_views_sha256'] == views['sha256'] and m['training_tokens_sha256'] == tokens['sha256'],
                'Frozen model/view/modality/exposure source differs')
        require(m['sha256'] == binding(root/role/'checkpoint.pt')['sha256'] and e['reload_exact'] is True and
                e['checkpoint_sha256'] == m['sha256'] and e['features_sha256'] == m['training_features_sha256'] and
                inv['all_work_members']['units/'+args.unit+'/'+role+'/reference.npz'] ==
                inv['all_work_members']['units/'+args.unit+'/'+role+'-embed/embeddings.npz'], 'Native exact reload vector bytes differ')
        require(len(m['history']) == 20 and [h['epoch'] for h in m['history']] == list(range(1,21)) and
                all(h['parents_seen'] == axis['eligible'] and np.isfinite(h['loss']) and
                    all(not g['catastrophic_collapse'] for bymode in h['geometry'].values() for g in bymode.values())
                    for h in m['history']), 'Complete schedule/exposure/noncollapse differs')
        require(m['teacher_parameter_count'] == m['parameter_count'] and m['predictor_parameter_count'] > 0 and
                m['ema_updates'] == 20*((axis['eligible']+255)//256) and
                all(h['ema_updates'] == h['epoch']*((axis['eligible']+255)//256) and
                    0 < h['available_views'] <= axis['eligible']*5 for h in m['history']),
                'Stopped target/predictor/EMA/view exposure differs')
        if role == 'student':
            require(m['training_pairs_sha256'] == binding(root/'pairs/cache/cache.json')['sha256'], 'Student pair provenance differs')
            for h in m['history']:
                pp = pair_policy()
                expected = pp['loss_weight']*min(1., max(0., (h['epoch']-pp['warmup_epochs'])/pp['ramp_epochs']))
                require(h['relation_weight'] == expected and h['relation_pairs_exposed'] == len(pair_arrays['left']),
                        'Frozen marker warmup/ramp/full pair exposure differs')
        records[role] = dict(status='PASS_COMPLETED_NATIVE_LEARNING_COMPONENT', newly_fitted=role in actual_new,
            historical_learning_time_not_new_compute=role not in actual_new, checkpoint=binding(root/role/'checkpoint.pt'),
            original_native_reload=True, no_new_inference_or_Mac_portability_claim=True,
            available_views_per_epoch=[h['available_views'] for h in m['history']],
            complete_history=m['history'], initial_geometry=m['initial_geometry'], transform=m['transform'],
            training_pairs_sha256=m.get('training_pairs_sha256'), training_frozen_sha256=frozen)
    if not actual_new:
        result = dict(status='PASS_CLOSED_LEARNING_COMPONENTS_ONLY', unit=args.unit, roles=records,
            global_workflow_completed=False, new_recovery_score_available=False,
            group_export_audit_missing=True, old_learning_not_rescored=True, truth_opened=False,
            full_rows=len(ids), full_bp=int(data['lengths'].sum()), samples=meta['samples'])
        write(args.output, result)
        print('EXACT_ACCEPTED_LEARNING_REUSED_NO_LABEL_OR_SCORE_REPLAY', args.unit, flush=True)
        return result
    # Source/learning contracts have passed before any independent labels are opened.
    clean = set(read(args.marker_clean)['clean'])
    if args.unit.startswith('E009'):
        from e012_marker_audit import verify_truth
        truth_root = verify_truth(read(ROOT/'experiments/E013-marker-quality/review-lock.json'))
        truth = read(truth_root/'truth.json'); target = read(truth_root/'targets.json')
        require(truth['ordered_contig_ids'] == ids and len(target['targets']) == 156, 'Conservative v2 axis differs')
        labels = {q: truth['contigs'][q]['AMBER_label'] for q in ids}; targets = target['targets']
    else:
        lab, quarantine, shared, genomes, truth = oral_labels(args.truth_root, ids, data['lengths'])
        require(len(truth['targets']) == 799 and sum(truth['targets'].values()) == 2083072211, 'Full Oral reference contract differs')
        labels = {q: genomes[int(g)] if g >= 0 else None for q, g in zip(ids, lab)}; targets = truth['targets']
    for role in actual_new:
        data, vectors, valid, em = load_inputs(args.features, root/(role+'-embed/embeddings.npz'))
        gc.collect()
        graph, gm = sparse_input(root/(role+'-graph/graph.npz'), ids, valid, root/(role+'-embed/embeddings.npz'))
        require(gm['audit']['mean_tie_aware_recall'] >= .9, 'Native learning graph recall failed')
        records[role]['native_graph_audit'] = gm['audit']
        records[role]['native_neighborhoods'] = neighborhood_census(data, graph['neighbors'], labels, targets, clean)
        records[role]['bounded_raw_geometry'] = parent_geometry(data, records[role]['transform'],
            dict(ids=ids, neighbors=NeighborIDs(ids, graph['neighbors'])), labels)
        if role == 'student':
            pairs, _ = load_pairs(root/'pairs/cache', args.features)
            records[role]['pair_label_diagnostic'] = pair_label_audit(pairs, labels)
        del vectors, valid, graph; gc.collect()
    result = dict(status='PASS_CLOSED_LEARNING_COMPONENTS_ONLY', unit=args.unit, roles=records,
        global_workflow_completed=False, new_recovery_score_available=False,
        group_export_audit_missing=True, old_learning_not_rescored=True,
        full_rows=len(ids), full_bp=int(data['lengths'].sum()), samples=meta['samples'])
    write(args.output, result)
    print(json.dumps({role: dict(new=r['newly_fitted'], native_neighborhoods=r.get('native_neighborhoods',{}).get('summary'))
                      for role, r in records.items()}), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--unit', choices=['E009-noGLM','E009-GLM','oral-noGLM'], required=True)
    for name in ['staged','verified','controls','features','status','finance','source','truth-root','marker-clean','output']:
        p.add_argument('--'+name, type=Path, required=True)
    review(p.parse_args())
