#!/usr/bin/env python3
"""New-output E035 reader with unchanged sequence-truth and E032 export contracts.

Require independent shutdown, actual exits, complete returns and cost admission.
No inference, refit, tuning, database download or baseline scoring is performed.
"""
import argparse
import json
from pathlib import Path
import sys

import dl_binner as _owned_product

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding


def contract(base,staged,unit,role,features,comparison,engineering=False):
    """Use the unchanged full-DNA selector reader under the new owned-package gate."""
    import e032_review as exports
    from e035_control import product_scope
    original=exports.product_scope
    try:
        exports.product_scope=product_scope
        result=exports.contract(base,staged,unit,role,features,comparison,engineering)
    finally:exports.product_scope=original
    from dl_binner.taxonomy.annotations import read
    from dl_binner.multiview.arrays import load_arrays
    import numpy as np
    base,staged=Path(base),Path(staged);inv=json.loads((base/'inventory.json').read_text())['all_work_members'];root=staged/'work'/unit
    r=json.loads((root/'student/result/completed.json').read_text());m=json.loads((root/'view-cache/result/cache.json').read_text())
    expected_policy=json.loads((ROOT/'experiments/E035-confidence-taxonomy/protocol.json').read_text())['adapter_policy']
    if (r['status']!='PASS' or r['policy']!=expected_policy or len(r['history'])!=20 or r['exact_reload']is not True
            or r['exact_reference_free_fallback']is not True or r['old_encoder_refit']is not False or r['new_teacher_or_pairs']is not False
            or r['truth_accessed']is not False or m['actual_crop_inference']is not True or m['exact_native_parent_reproduction']is not True
            or m['inputs']['features']!=binding(features) or r['checkpoint']!=inv[unit+'/student/result/checkpoint.pt']
            or r['cache']!=inv[unit+'/view-cache/result/cache.json']):raise ValueError('New taxonomy source/view/learning/reload contract differs')
    base_vectors,_=load_arrays(root/'view-cache/result/base.npz','embeddings')
    expected_parents=int(np.count_nonzero(result[0]['eligible']&base_vectors['evidence']))
    if any(h['original_parent_slots']!=expected_parents or (h['geometry']and h['geometry']['catastrophic_collapse'])for h in r['history']):
        raise ValueError('Taxonomy exposure/collapse history differs')
    community='oral'if unit.startswith('oral')else'E009';annotations=staged/'work/classifications'/community/'annotations'
    a,am,t=read(annotations,features)
    if r['annotations']!=binding(annotations/'completed.json') or am['provenance']['synthetic_reference']is not engineering:
        raise ValueError('Independent classifier annotation contract differs')
    for name in ['student/result/completed.json','view-cache/result/cache.json']:
        if binding(root/name)!=inv[unit+'/'+name]:raise ValueError('Restored taxonomy receipt differs')
    if not engineering:
        admission=json.loads((base/'admission.json').read_text())
        if admission.get('candidate_lock')!=binding(ROOT/'experiments/E035-confidence-taxonomy/candidate-lock.json')or admission.get('native_source_runtime_information_policy_verified')is not True:
            raise ValueError('Native taxonomy source/runtime information admission missing')
    result[-1].update(learning='frozen E031 actual view vectors plus new E035 hierarchy adapter; not unchanged geometry',
        constructor='unchanged common E032',independent_parent_classification=True,
        no_new_teacher_proposals=True,truth_or_baseline_rescore=False)
    return result


def review(base,staged,unit,features,marker_clean,truth_root,output):
    """Evaluate only admitted new pre/post partitions with the frozen evaluator."""
    import e031_review as accepted
    original=accepted.contract
    try:
        accepted.contract=contract
        return accepted.review(base,staged,unit,'student',features,'learning',marker_clean,truth_root,output)
    finally:accepted.contract=original


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['base','staged','features','marker-clean','truth-root','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--unit',choices=['E009-noGLM','E009-GLM','oral-noGLM'],required=True);a=p.parse_args()
    review(a.base,a.staged,a.unit,a.features,a.marker_clean,a.truth_root,a.output)
