#!/usr/bin/env python3
"""Frozen new-output review adapter for E033, with unchanged scientific evaluators.

The new three-mode learning bundle is evaluated only after actual shutdown and
source/exit/archive/member/cost admission. Each mode uses a losslessly namespaced
inventory view; original archives and their manifests remain untouched. No fit,
constructor, threshold selection or old score replay is supported.
"""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def layout(collection,staged,unit,output):
    """Validate a verified per-mode compact stage and create exact namespaced links."""
    from e033_control import UNITS
    if unit not in UNITS:raise ValueError('Unknown frozen review mode')
    collection,staged,out=map(Path,[collection,staged,output]);out.mkdir(parents=True,exist_ok=False)
    inv=json.loads((collection/'inventory.json').read_text());admit=json.loads((collection/'admission.json').read_text())
    from e022_review import admission_contract
    admission_contract(collection/'admission.json')
    if admit.get('exact_source_schedule_axes_verified') is not True or inv['omitted_retained_on_disk']:
        raise ValueError('Exact completed science and complete inventory required')
    namespaced={unit+'/'+n:b for n,b in inv['all_work_members'].items()}
    for p in (staged/'work').rglob('*'):
        if p.is_symlink():raise ValueError('Scientific staged links refused')
        if not p.is_file():continue
        n=str(p.relative_to(staged/'work'))
        if n not in inv['all_work_members'] or binding(p)!=inv['all_work_members'][n]:
            raise ValueError('Compact staging byte/member differs')
        target=out/'staged/work'/unit/n;target.parent.mkdir(parents=True,exist_ok=True);os.link(p,target)
    (out/'base').mkdir()
    write(out/'base/admission.json',admit)
    write(out/'base/inventory.json',dict(kind='Lossless namespaced E033 review view',all_work_members=namespaced,
        original_inventory=binding(collection/'inventory.json'),original_unchanged=True))
    return out/'base',out/'staged'


def contract(base,staged,unit,role,features,comparison,engineering=False):
    """Verify new learning/source/exposure before the unchanged full-DNA reader."""
    from e032_review import contract as accepted
    base,staged=Path(base),Path(staged)
    result=accepted(base,staged,unit,role,features,comparison,engineering)
    data,meta=result[:2];inv=json.loads((base/'inventory.json').read_text())['all_work_members']
    admission=json.loads((base/'admission.json').read_text())
    if not engineering:
        if (admission.get('candidate_lock')!=binding(ROOT/'experiments/E033-multiscale-bam/candidate-lock.json')
            or admission.get('native_source_runtime_information_policy_verified') is not True):
            raise ValueError('Native E033 runtime/source/information admission missing')
    lock=json.loads((ROOT/'experiments/E033-multiscale-bam/candidate-lock.json').read_text())
    records={}
    import math
    for stage in ['teacher','student']:
        prefix=unit+'/'+stage+'/result';path=staged/'work'/prefix/'checkpoint.json'
        r=json.loads(path.read_text())
        if (inv.get(prefix+'/checkpoint.json')!=binding(path) or r.get('kind')!='multiscale_checkpoint'
            or r['policy']!=lock['learning_policy'] or r['stage']!=stage or r['sha256']!=inv[prefix+'/checkpoint.pt']['sha256']
            or r['samples']!=meta['samples'] or r['inputs']['new_features']!=binding(features)
            or r['config']['seed']!=11 or r['config']['batch_size']!=256
            or r['config']['composition_reconstruction_weight']!=1. or r['config']['depth_reconstruction_weight']!=.1
            or len(r['history'])!=20 or r['added_updates']!=20*math.ceil(int(data['eligible'].sum())/256)
            or ('hybrid' in r['config'])!=(unit=='E009-GLM') or (r['inputs']['frozen'] is not None)!=(unit=='E009-GLM')
            or r['truth_accessed'] is not False or r['original_Adam_restored'] is not True
            or r['initial_state']['anchor']!=r['final_state']['anchor']
            or any(h['parents_seen']!=int(data['eligible'].sum()) or any(g['catastrophic_collapse'] for d in h['geometry'].values() for g in d.values()) for h in r['history'])):
            raise ValueError('New full learning/exposure/stopped-state contract differs')
        ep=staged/'work'/unit/(stage+'-embed')/'embeddings.json';em=json.loads(ep.read_text())
        if (inv.get(unit+'/'+stage+'-embed/embeddings.json')!=binding(ep) or em.get('reload_exact') is not True
            or em['checkpoint_sha256']!=r['sha256'] or em['features_sha256']!=binding(features)['sha256']):
            raise ValueError('Native exact reload/feature binding missing')
        records[stage]=r
    if records['student']['teacher_checkpoint']!={k:inv[unit+'/teacher/result/checkpoint.pt'][k] for k in ['bytes','sha256']}:
        raise ValueError('Student is not the own adapted teacher continuation')
    pairpath=staged/'work'/unit/'pairs/result/cache/cache.json';pair=json.loads(pairpath.read_text())
    if (inv.get(unit+'/pairs/result/cache/cache.json')!=binding(pairpath)
        or pair['own_teacher_checkpoint_sha256']!=records['teacher']['sha256'] or pair['own_teacher_reload_exact'] is not True
        or any(h['original_pair_slots']!=pair['source_pair_count'] for h in records['student']['history'])):
        raise ValueError('Own-teacher pair/denominator contract missing')
    result[-1].update(learning='new E033 measured multiscale bundle; NOT fixed historical E031 learning',
        scientific_evaluators_unchanged=True,native_learning_contract_verified=True,
        GLM_coverage_policy_complete=True)
    return result


def review(base,staged,unit,features,marker_clean,truth_root,output):
    """Run only the admitted E009-v2/Oral-origin primary and secondary diagnostics."""
    import e031_review as accepted
    previous=accepted.contract
    try:
        accepted.contract=contract
        return accepted.review(base,staged,unit,'student',features,'learning',marker_clean,truth_root,output)
    finally:accepted.contract=previous


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['base','staged','features','marker-clean','truth-root','output']:p.add_argument('--'+n,required=True,type=Path)
    p.add_argument('--unit',required=True,choices=['E009-noGLM','E009-GLM','oral-noGLM']);a=p.parse_args()
    review(a.base,a.staged,a.unit,a.features,a.marker_clean,a.truth_root,a.output)
