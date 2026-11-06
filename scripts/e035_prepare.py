#!/usr/bin/env python3
"""Freeze E035 prospective source/default/reuse/pricing records, never execute.

Only already retained metadata and tiny local preparation receipts are read.
No community arrays, cloud account, database payload or evaluator is opened.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).absolute().parents[1];EXP=ROOT/'experiments/E035-confidence-taxonomy'
UNITS=['E009-noGLM','E009-GLM','oral-noGLM']


def binding(path):
    """Bind small reproducibility-critical files without path or credential contents."""
    p=Path(path);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return dict(bytes=p.stat().st_size,sha256=h.hexdigest())


def read(path):
    """Read existing metadata, keeping every old record untouched."""
    return json.loads((ROOT/path).read_text())


def write(name,value):
    """Publish prospective E035-only records before changed community outcomes."""
    (EXP/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def plans():
    """Prepare actual same-version modes and separately bounded information scopes."""
    prior=read('experiments/E031-bootstrap-preserving-learning/learning-plan.json')
    old=read('experiments/E034-genome-graph/runtime-plan.json');reuse=read('experiments/E033-multiscale-bam/reuse-lock.json')
    units={};task='/srv/dl_binner/experiments/e035/NEW_PHASE/task'
    for u in UNITS:
        e=old['units'][u];original=prior['units'][u];prefix=task+'/original-bootstrap/work/'+u
        units[u]=dict(e,tokens=original['tokens'],frozen=original['frozen'],
            checkpoint=prefix+'/train/result/checkpoint.pt',embeddings=prefix+'/embed/embeddings.npz',
            annotations=task+'/classification/'+e['community']+'/annotations')
    limits=dict(seconds=72*3600,provider_STOP_seconds=int(72.25*3600),ceiling_USD=50,
        proposed_temporary_machine='e2-highmem-8',allocated_vCPUs=8,allocated_RAM_GiB=64,
        threads=4,RSS_bytes=52_000_000_000,reserve_bytes=25*1024**3,task_disk_GiB=750,task_growth_bytes=675*1024**3,
        aggregate_compressed_bytes=12*1024**3,slice_compressed_bytes=2*1024**3,slice_logical_bytes=8*1024**3,
        local_staged_bytes=3*1024**3,local_free_reserve_bytes=8*1024**3,
        retention_end='2026-11-11T00:00:00+01:00',automatic_tail_end='2026-11-18T00:00:00+01:00')
    write('limits.json',limits)
    write('runtime-plan.json',dict(kind='E035 confidence taxonomy',engineering=False,work=task+'/science',units=units,
        python=task+'/env/bin/python',workflow_python=prior['workflow_python'],worker='/srv/dl_binner/repo/scripts/e035_control.py',
        snakefile='/srv/dl_binner/repo/experiments/E035-confidence-taxonomy/Snakefile',limits=limits))
    write('reuse-lock.json',dict(reuse,kind='E035 immutable E031 full information ancestry and original accepted inputs'))
    inv=read('artifacts/e031-bootstrap-preserving-learning/learning-inspection-20261103/inventory.json')
    if binding(ROOT/'artifacts/e031-bootstrap-preserving-learning/learning-inspection-20261103/inventory.json')!=reuse['accepted_archive']['inventory']:
        raise ValueError('Retained E031 inventory belongs to a different generation')
    members=inv['all_work_members']
    write('retained-output-lock.json',{u:{name:members[u+'/'+name]for name in ['embed/embeddings.npz','embed/embeddings.json','train/result/checkpoint.pt','train/result/checkpoint.json']}for u in UNITS})
    B=read('experiments/E033-multiscale-bam/BAM-manifest.json');records={c:[]for c in ['E009','oral']}
    for r in B['records']:
        e=dict(r);e['local']=r['source']if r['community']=='E009'else '/srv/dl_binner/experiments/e035/POOLED_PHASE/task/one-BAM.bam';records[r['community']].append(e)
    # The serial controller must bind the new sample before replacing one-BAM.bam.
    write('pooled-audit-plan.json',dict(kind='E035 pooled-before-support audit',engineering=False,
        work='/srv/dl_binner/experiments/e035/POOLED_PHASE/task/support',features={c:old['units']['oral-noGLM'if c=='oral'else'E009-noGLM']['features']for c in ['E009','oral']},
        BAMs=records,limits=dict(seconds=8*3600,provider_STOP_seconds=int(8.25*3600),ceiling_USD=4,threads=4,RSS_bytes=26_000_000_000,
            reserve_bytes=25*1024**3,task_disk_GiB=100,task_growth_bytes=60*1024**3,compressed_export_bytes=2*1024**3,
            retention_end=limits['retention_end'],automatic_tail_end=limits['automatic_tail_end'])))
    base=read('experiments/E032-biological-candidate-selection/comparison-review.json')
    strong=read('experiments/E031-bootstrap-preserving-learning/learning-review.json')
    assignment=next(n for n in ast.parse((ROOT/'src/dl_binner/taxonomy/model.py').read_text()).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='DEFAULT'for t in n.targets))
    adapter_policy={item.arg:ast.literal_eval(item.value)for item in assignment.value.keywords}
    write('protocol.json',dict(status='FROZEN_PRE_COMMUNITY_PREPARATION',same_version_all_modes=True,modes=UNITS,
        adapter_policy=adapter_policy,
        learning='frozen E031 online encoder; new 20-epoch bounded taxonomy adapter only',constructor='unchanged common E032 with all alternatives',
        new_teacher_or_pairs=False,E009_GLM='full admitted E031 teacher/proposal/student ancestry and actual crop bank',
        noGLM='no bank or hidden GLM-derived teacher/proposal inputs',taxonomy_off_community_fit=False,
        primary='full provided-reference weighted R95 / T90; unchanged evaluator',full_reference_targets=dict(E009=156,oral=799),
        E009_N_quarantine_fraction=.033034,oral_truth='provided-origin oracle plus known-shared sensitivity',
        baselines={u:base['modes'][u]['arms']['post']['primary']for u in UNITS},
        stronger_E009_anchors={u:strong['actors'][u]['arms']['E023/selected']['primary']for u in UNITS[:2]},
        KEEP='No E032 R95/T90 loss in any mode; both E009 modes also meet stronger E031/E023 R95/T90; >=0.5 percentage point R95 or >=3 multi-contig T90 gain in one mode',
        MODIFY='Useful recovery gain with smaller effect or cross-mode/unknown-stratum trade-off',
        ABANDON='No mode improves R95 or multi-contig T90 against E032',
        missing_contract='No quality claim; first diagnose the scientific or operational boundary',
        strata=['length','origin','annotation state/rank/confidence','eligibility','marker','unknown/non-target','unassigned','singleton/multi-contig'],
        independent_confirmation=False,skin_unscored=True,old_scores_rescored=False))


def freeze(build):
    """Bind a tested wheel/sdist plus all scientific sources and current defaults."""
    build=Path(build);receipt=json.loads((build/'completed.json').read_text())
    write('candidate-lock.json',dict(kind='E035 locally qualified candidate, native admission outstanding',version='0.1.0.dev11',
        wheel=receipt['wheel'],sdist=receipt['sdist'],package_sources=receipt['source_members'],
        classifier_source=read('experiments/E035-confidence-taxonomy/reference-lock.json'),
        community_execution_authorized=False,bulk_database_admitted=False))
    old=read('experiments/E034-genome-graph/source-lock.json');names=set(old['files'])
    names={n for n in names if not n.startswith('experiments/E034-genome-graph/')}
    names.update(str(p.relative_to(ROOT))for p in (ROOT/'src/dl_binner').rglob('*')if p.is_file()and p.suffix in ['.py','.json'])
    names.update(str(p.relative_to(ROOT))for p in (ROOT/'scripts').glob('e035*.py'))
    names.update('experiments/E035-confidence-taxonomy/'+n for n in ['design.md','protocol.json','limits.json','runtime-plan.json','reuse-lock.json','retained-output-lock.json','reference-lock.json','pooled-audit-plan.json','resource-plan.json','Snakefile'])
    missing=[n for n in names if not (ROOT/n).is_file()]
    if missing:raise ValueError('Required freeze members missing: '+str(missing))
    write('source-lock.json',dict(kind='E035 prospective exact scientific/default/operational sources',files={n:binding(ROOT/n)for n in sorted(names)}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plans',action='store_true');p.add_argument('--freeze',type=Path);a=p.parse_args()
    if a.plans:plans()
    if a.freeze:freeze(a.freeze)
