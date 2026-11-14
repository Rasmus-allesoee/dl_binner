#!/usr/bin/env python3
"""Admit new E036 pre/post outputs for the unchanged frozen sequence evaluators.

No launch, inference, threshold tuning or old score replay. Independent shutdown,
actual exits, financial admission and every archive/member/alias proof are caller
prerequisites. Geometry describes new graph learning over fixed E031 inputs.
"""
import argparse,json
from pathlib import Path
import sys
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding


def contract(base,staged,unit,role,features,comparison,engineering=False):
    """Require native graph-fit/cache/reload closure in addition to full E032 exports."""
    from e032_review import contract as complete_exports
    import e032_review
    from e036_control import product_scope
    e032_review.product_scope=product_scope
    result=complete_exports(base,staged,unit,role,features,comparison,engineering)
    base,staged=Path(base),Path(staged);root=staged/'work'/unit;inv=json.loads((base/'inventory.json').read_text())['all_work_members']
    fallback=root/'student/fallback.json'
    if fallback.is_file():
        if json.loads(fallback.read_text())['status']!='EXACT_ACCEPTED_FALLBACK':raise ValueError('Missing exact fallback closure')
        result[-1].update(exact_accepted_fallback=True,no_graph_fit=True,baseline_rescore=False)
        return result
    from dl_binner.genomegraph.model import policy
    saved=root/'student/result/completed.json';r=json.loads(saved.read_text());cache=root/'node-features/result/features.json';m=json.loads(cache.read_text())
    if (r['status']!='PASS' or r['policy']!=policy() or len(r['history'])!=20 or r['old_encoder_refit'] is not False
        or r['reload_exact'] is not True or r['truth_accessed'] is not False or m['parent_is_not_window'] is not True
        or m['inputs']['features']!=binding(features) or r['cache']!=inv[unit+'/node-features/result/features.npz']
        or r['checkpoint']!=inv[unit+'/student/result/checkpoint.pt']):
        raise ValueError('Complete E036 graph fit/cache/source/reload differs')
    for file in [saved,cache]:
        if inv[str(file.relative_to(staged/'work'))]!=binding(file):raise ValueError('Native graph receipt bytes differ')
    if any(x['geometry']['catastrophic_collapse'] for x in r['history']):raise ValueError('Graph collapse history failed')
    if not engineering:
        a=json.loads((base/'admission.json').read_text())
        if r['engineering_epochs'] is not None or a.get('candidate_lock')!=binding(ROOT/'experiments/E036-optional-pooled-links/candidate-lock.json') or a.get('native_source_runtime_information_policy_verified')is not True:
            raise ValueError('Independent E036 source/runtime admission missing')
    result[-1].update(learning='Frozen E031 source-bound vectors; new E036 physical graph representation, NOT unchanged E031 output geometry',
        constructor='unchanged E032 common selection/joint policy',scientific_evaluators_unchanged=True,
        historical_depth_priors_retained=True,new_measured_context=True,old_scores_replayed=False)
    return result


def review(base,staged,unit,features,marker_clean,truth_root,output):
    """Evaluate only independently admitted new outputs, preserving all denominators."""
    import e031_review as accepted
    old=accepted.contract
    try:
        accepted.contract=contract
        return accepted.review(base,staged,unit,'student',features,'learning',marker_clean,truth_root,output)
    finally:accepted.contract=old


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['base','staged','features','marker-clean','truth-root','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--unit',choices=['E009-noGLM','E009-GLM','oral-noGLM'],required=True);a=p.parse_args();review(a.base,a.staged,a.unit,a.features,a.marker_clean,a.truth_root,a.output)
