#!/usr/bin/env python3
"""Freeze E032 source, byte reuse and one shared protocol before new outcomes.

Reads only previously admitted small metadata and the freshly built wheel.
It never opens community numerical arrays, truth or a cloud account.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).absolute().parents[1]
EXP=ROOT/'experiments/E032-biological-candidate-selection'


def binding(p):
    """Hash one ordinary source/control file without loading numerical libraries."""
    p=Path(p);h=hashlib.sha256()
    with p.open('rb') as f:
        for v in iter(lambda:f.read(1024**2),b''):h.update(v)
    return dict(bytes=p.stat().st_size,sha256=h.hexdigest())


def write(name,value):
    """Write only unfitted E032 prospective records; old locks are immutable."""
    (EXP/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def prepare(wheel):
    """Verify additive package changes, then freeze actual launch/consumer paths."""
    old=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/candidate-lock.json').read_text())
    package={str(p.relative_to(ROOT/'src/dl_binner')):binding(p) for p in (ROOT/'src/dl_binner').rglob('*')
             if p.is_file() and p.suffix in ['.py','.json'] and '__pycache__' not in p.parts}
    if any(package.get(k)!=v for k,v in old['package_files'].items()):raise ValueError('Immutable E031 source changed')
    with zipfile.ZipFile(wheel) as z:
        files={n.removeprefix('dl_binner/'):dict(bytes=len(z.read(n)),sha256=hashlib.sha256(z.read(n)).hexdigest())
            for n in z.namelist() if n.startswith('dl_binner/') and not n.endswith('/')}
    if files!=package:raise ValueError('Fresh wheel differs from exact candidate sources')
    write('candidate-lock.json',dict(kind='E032 additive fixed-learning constructor',wheel=binding(wheel),
        package_files=package,unchanged_E031_members=len(old['package_files']),new_members=sorted(set(package)-set(old['package_files']))))
    reuse=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/reuse-lock.json').read_text())
    prior=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/paired-plan.json').read_text())
    units={u:{k:v for k,v in e.items() if k in ['features','fasta','marker_evidence']} for u,e in prior['units'].items()}
    needed=set()
    for entry in units.values():
        needed.update(entry.values());needed.add(str(Path(entry['features']).with_suffix('.json')))
    external={n:reuse['learning_files'][n] for n in sorted(needed)}
    write('reuse-lock.json',dict(axes=reuse['axes'],external_files=external,
        native_dependency_base=reuse['native_dependency_base'],native_runtime_reference=reuse['native_runtime_reference'],
        immutable_scientific_source='ba659119c3ec86edc83e27bad95939326fbaa2b8',
        deleted_task_environment_not_reused=True))
    original=ROOT/'artifacts/e031-bootstrap-preserving-learning/learning-inspection-20261103'
    inv=json.loads((original/'inventory.json').read_text())
    meta=dict(size=2101954568,generation='1793668697775852',md5_hash='ErbtjjJrgXm14WLnciCA8w==')
    archive=dict(uri='gs://dl-binner-archive-167650584170/e031/learning-20261102T200852Z-ba65911-r2/e031-evidence.tar.gz',
                 binding=dict(bytes=2101954568,sha256='d4ce1d15ad8f7c2443863a6c42805ddd419a6034c861b22a586b7659b9db47ec'))
    write('restore-lock.json',dict(archive=archive,metadata=meta,inventory=binding(original/'inventory.json'),
        reserve_bytes=25*1024**3,original_physical_members=len(inv['members'])+1,
        omitted_work_members=len(inv['omitted_retained_on_disk']),all_original_members_must_pass=True))
    limits=dict(seconds=8*3600,provider_STOP_seconds=int(8.25*3600),ceiling_USD=6,
        threads=4,RSS_bytes=26000000000,reserve_bytes=25*1024**3,extra_bytes=12*1024**3,
        compressed_bytes=3*1024**3,logical_bytes=6*1024**3,retention_epoch=1794351600)
    p=dict(kind='E032 common cached biological candidate selection',engineering=False,
        units=units,work='/srv/dl_binner/experiments/e032/NEW_PHASE/work',
        restored='/srv/dl_binner/experiments/e032/NEW_PHASE/restored',
        python='/srv/dl_binner/experiments/e032/NEW_PHASE/env/bin/python',
        workflow_python=prior['workflow_python'],worker='/srv/dl_binner/repo/scripts/e032_control.py',
        snakefile='/srv/dl_binner/repo/experiments/E032-biological-candidate-selection/Snakefile',limits=limits)
    write('runtime-plan.json',p)
    reviewed=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/learning-review.json').read_text())
    anchors={}
    for u in units:
        arm='E030/post' if u=='oral-noGLM' else 'E023/selected'
        v=reviewed['actors'][u]['arms'][arm]['primary']
        anchors[u]=dict(R95=v['bp_weighted_R95'],T90=v['at_least_90_percent'])
    write('protocol.json',dict(status='PROSPECTIVE_NO_E032_OUTCOMES',same_policy_all_modes=True,
        learning='E031 fixed; no model/RNG/view/graph/marker/depth change',
        partitions=['pre','post'],primary='frozen full-reference weighted R95 and T90',
        denominators=dict(E009_targets=156,oral_targets=799,E009_N_quarantine_fraction=.033034),
        anchors=anchors,
        KEEP='No R95/T90 loss in any mode against stronger retained E031 constructor; >=0.5 percentage point gain in at least one',
        MODIFY='Useful gain with trade-off or smaller improvement',
        ABANDON='No mode improves R95, or >=1 point loss without >=0.5 point gain elsewhere',
        failure='NOT_ASSESSED when operational/integrity gates fail',truth_not_used_for_selection=True,
        skin_unscored=True,depth_harmonization_not_this_treatment=True))
    text=(ROOT/'scripts/e032_control.py').read_text()
    dispatch=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='stage')
    science=dict(kind='E032 scientific identity independent of operational recovery',package_files=package,
        stage_dispatch_source_sha256=hashlib.sha256(ast.get_source_segment(text,dispatch).encode()).hexdigest(),
        protocol=binding(EXP/'protocol.json'),design=binding(EXP/'design.md'),units=units,
        reused_archive=archive,external_files=external)
    write('science-lock.json',science)
    paths=list((ROOT/'src/dl_binner').rglob('*.py'))+list((ROOT/'src/dl_binner/resources').glob('*.json'))
    paths+=list((ROOT/'scripts').glob('e032*.py'))+[ROOT/'tests/product/test_selection.py',ROOT/'tests/test_e032_operations.py']
    paths+=[EXP/n for n in ['design.md','protocol.json','science-lock.json','candidate-lock.json','reuse-lock.json','restore-lock.json','runtime-plan.json','Snakefile']]
    write('source-lock.json',dict(kind='E032 prospective scientific/operational freeze',
        parent_source='1ea748a3cdbc13db7c36b2155f26b76f4bf4091a',
        files={str(p.relative_to(ROOT)):binding(p) for p in sorted(set(paths))},community_outcomes_seen=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--wheel',type=Path,required=True)
    a=p.parse_args();prepare(a.wheel)
