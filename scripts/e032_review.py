#!/usr/bin/env python3
"""Adapt E032's new result layout to the unchanged frozen sequence evaluators.

Independent shutdown, actual exits, archive/member bytes and cost admission are
mandatory before this read-only adapter. It changes no truth, denominator, tier,
threshold or old result. Geometry is retained E031 evidence, not recomputed here.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding
from e032_control import product_scope,UNITS


def contract(base,staged,unit,role,features,comparison,engineering=False):
    """Read actual complete E032 pre/post exports under independent admission."""
    product_scope()
    from e022_review import admission_contract
    from e014_review import manifest_bindings
    from dl_binner.multiview.views import load
    from dl_binner.information.export import validate_partition
    from dl_binner.selection.grouping import policy
    if unit not in UNITS or role!='student' or comparison!='learning':raise ValueError('Only new fixed-learning E032 outputs may be scored')
    base,staged=Path(base),Path(staged);admission=admission_contract(base/'admission.json')
    if admission.get('exact_source_schedule_axes_verified') is not True:raise ValueError('Independent source/axes admission required')
    inv=json.loads((base/'inventory.json').read_text())['all_work_members'];data,meta=load(features)
    axis=dict(rows=len(data['ids']),bp=int(data['lengths'].sum()),eligible=int(data['eligible'].sum()),samples=meta['samples'])
    if engineering:
        if axis['rows']>128:raise ValueError('Tiny review exceeded')
    elif axis!=json.loads((ROOT/'experiments/E032-biological-candidate-selection/reuse-lock.json').read_text())['axes'][unit]:
        raise ValueError('Full contig/ordered ten-depth axes differ')
    group=staged/'work'/unit/'select/result';prefix=unit+'/select/result'
    m=json.loads((group/'completed.json').read_text());proof=staged/'work'/unit/'audit/proof.json'
    if (m['status']!='SUCCESS' or m['config']!=policy() or m['truth_accessed'] is not False
        or m['unchanged_learning'] is not True or not any(v==binding(features) for v in m['inputs'].values())
        or json.loads(proof.read_text())['status']!='PASS'):
        raise ValueError('Complete fixed-learning/native cached audit missing')
    for path in [group/'completed.json',proof]:
        if binding(path)!=inv[str(path.relative_to(staged/'work'))]:raise ValueError('Native result/audit bytes differ')
    for name,wanted in m['files'].items():
        if inv.get(prefix+'/'+name)!=wanted:raise ValueError('New full member inventory differs')
        if (group/name).is_file() and binding(group/name)!=wanted:raise ValueError('New staged member differs')
    for arm in ['pre','post']:
        validate_partition(data,group/(arm+'-partition.json'),features)
        manifest_bindings(json.loads((group/'export'/arm/'manifest.json').read_text()),prefix+'/export/'+arm,inv)
    return data,meta,group,group/'export',['pre','post'],dict(status='PASS',unit=unit,axis=axis,
        features=binding(features),native_numeric_audit_verified=True,independent_archive_admission=admission,
        original_Mac_portability_tolerance_unchanged=True,local_model_inference=False)


def review(base,staged,unit,features,marker_clean,truth_root,output):
    """Reuse the exact accepted evaluation function; adapt only its new file layout."""
    product_scope()
    import e031_review as accepted
    original=accepted.contract
    try:
        accepted.contract=contract
        return accepted.review(base,staged,unit,'student',features,'learning',marker_clean,truth_root,output)
    finally:accepted.contract=original


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['base','staged','features','marker-clean','truth-root','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--unit',choices=UNITS,required=True);a=p.parse_args()
    review(a.base,a.staged,a.unit,a.features,a.marker_clean,a.truth_root,a.output)
