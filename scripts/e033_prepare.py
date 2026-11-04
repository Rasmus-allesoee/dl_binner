#!/usr/bin/env python3
"""Freeze E033 source/protocol/runtime/BAM locators from retained metadata only.

No community arrays, truth, cloud account or VM is opened. Prospective records
may be regenerated before first changed community outcomes, preserving Git and
local failure journals. Original experiment locks are never modified.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).absolute().parents[1];EXP=ROOT/'experiments/E033-multiscale-bam'
UNITS=['E009-noGLM','E009-GLM','oral-noGLM']


def binding(path):
    """Bind compact source/metadata bytes without loading scientific arrays."""
    p=Path(path);h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return dict(bytes=p.stat().st_size,sha256=h.hexdigest())


def read(path):
    """Read a retained JSON metadata record without invoking its old launcher."""
    return json.loads((ROOT/path).read_text())


def write(name,value):
    """Write only prospective E033-owned records."""
    (EXP/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def plans():
    """Bind all twenty original BAMs, exact E031 states and original DNA/view caches."""
    prior=read('experiments/E031-bootstrap-preserving-learning/paired-plan.json')
    original=read('experiments/E027-common-information-binner/runtime-plan.json')
    reuse=read('experiments/E031-bootstrap-preserving-learning/reuse-lock.json')
    archive=read('experiments/E032-biological-candidate-selection/restore-lock.json')
    inventory=read('artifacts/e031-bootstrap-preserving-learning/learning-inspection-20261103/inventory.json')
    storage=read('artifacts/e032-biological-candidate-selection/admission/storage-inventory.json')
    objects={x['name']:x for x in storage['objects']}
    units={};files={};states={}
    for u in UNITS:
        e=prior['units'][u];o=original['units'][u];member='work/'+u+'/train/result/checkpoint.pt'
        # Exact aliases are resolved to a declared physical archive member.
        b=inventory['all_work_members'][member.removeprefix('work/')]
        states[u]=dict(member=member,checkpoint=b,metadata=inventory['all_work_members'][u+'/train/result/checkpoint.json'])
        units[u]={k:e[k] for k in ['features','views','fasta','tokens','frozen','marker_evidence']}
        units[u].update(original='/srv/dl_binner/experiments/e033/NEW_PHASE/restored/'+member,
            marker_cache=o['marker_cache'],hmm=o['hmm'],community='oral' if u.startswith('oral') else 'E009')
    for e in units.values():
        exact={e['features'],str(Path(e['features']).with_suffix('.json')),e['views'],str(Path(e['views']).with_suffix('.json')),e['fasta'],e['marker_evidence']}
        prefixes=[e['tokens']+'/']+([e['frozen']+'/'] if e['frozen'] else [])
        for n,b in reuse['learning_files'].items():
            if n in exact or any(n.startswith(prefix) for prefix in prefixes):files[n]=b
    # Bind additional physical marker/HMM members already admitted by E027/E022.
    priorfiles=read('experiments/E027-common-information-binner/reuse-lock.json')['files']
    for e in units.values():
        for n,b in priorfiles.items():
            if n.startswith(e['marker_cache']+'/') or n==e['hmm']:files[n]=b
    records=[];bams=read('experiments/E032-biological-candidate-selection/depth-audit-reviewed.json')['E009_existing_BAMs']
    samples=reuse['axes']['E009-noGLM']['samples']
    for sample,row in zip(samples,bams):
        native=row['path'];folder=Path(native).parents[1].name
        journal=read('artifacts/e009-gcp-review/20261015/returned/data-stage-v1/parts/'+folder+'/done.json')
        b=journal['files']['mapping/'+Path(native).name]
        if b['bytes']!=row['bytes']:raise ValueError('Retained E009 BAM byte records disagree')
        records.append(dict(community='E009',sample=sample,source=native,sorted=True,**b))
    for number,sample in zip([6,7,8,13,14,15,16,17,18,19],reuse['axes']['oral-noGLM']['samples']):
        record=read('artifacts/e024-inspection/20261028T193107Z/verified/work/samples/'+str(number)+'/mapped/alignment-retained.json')
        name=record['uri'].split('167650584170/',1)[1];obj=objects[name]
        if int(obj['size'])!=record['bytes'] or not record['full_readback_verified']:raise ValueError('Retained Oral object metadata differs')
        records.append(dict(community='oral',sample=sample,source=record['uri']+'#'+obj['generation'],sorted=False,
            bytes=record['bytes'],sha256=record['sha256'],records=record['native_full_decode_records'],generation=obj['generation'],crc32c=obj['crc32c']))
    if len(records)!=20 or sum(x['bytes'] for x in records)!=94_850_086_599:raise ValueError('Frozen twenty-BAM payload total differs')
    write('BAM-manifest.json',dict(kind='retained complete-reference placements, no remapping',records=records,
        total_bytes=sum(r['bytes'] for r in records),native_original_bam_count=10,private_unsorted_bam_count=10,
        pilot_samples=[records[0]['sample'],max([r for r in records if r['community']=='oral'],key=lambda r:r['bytes'])['sample']],
        all_old_tables_preserved=True,new_live_metadata_and_bytes_required=True))
    write('reuse-lock.json',dict(kind='E033 exact old-state/DNA/view/marker reuse',axes=reuse['axes'],external_files=files,
        E031_states=states,accepted_archive=archive,native_dependency_base=reuse['native_dependency_base'],
        native_runtime_reference=reuse['native_runtime_reference'],source_freezes_preserved=True))
    limits=dict(seconds=36*3600,provider_STOP_seconds=int(36.25*3600),ceiling_USD=20,
        threads=4,RSS_bytes=26_000_000_000,reserve_bytes=25*1024**3,extra_bytes=60*1024**3,
        slice_compressed_bytes=3*1024**3,slice_logical_bytes=8*1024**3,aggregate_compressed_bytes=12*1024**3,
        local_staged_bytes=3*1024**3,local_free_reserve_bytes=8*1024**3,
        retention_end='2026-11-11T00:00:00+01:00',automatic_tail_end='2026-11-18T00:00:00+01:00')
    write('runtime-plan.json',dict(kind='E033 common multiscale BAM information',engineering=False,
        work='/srv/dl_binner/experiments/e033/NEW_PHASE/work',units=units,
        measurements={c:dict(bank='/srv/dl_binner/experiments/e033/NEW_PHASE/measurements/'+c,
            new_features='/srv/dl_binner/experiments/e033/NEW_PHASE/measurements/'+c+'/features.npz') for c in ['E009','oral']},
        python='/srv/dl_binner/experiments/e033/NEW_PHASE/env/bin/python',workflow_python=prior['workflow_python'],
        worker='/srv/dl_binner/repo/scripts/e033_control.py',snakefile='/srv/dl_binner/repo/experiments/E033-multiscale-bam/Snakefile',limits=limits))
    write('protocol.json',dict(status='PROSPECTIVE_LOCAL_PREPARATION_NO_COMMUNITY_OUTCOMES',same_version_all_modes=True,
        units=UNITS,teacher_epochs=20,student_epochs=20,seed=11,batch_size=256,
        old_reconstruction=dict(composition=1.,depth=.1),parent_depth='shared newly measured',crop_depth='genuine exact retained interval plus explicit parent context',
        GLM_policy='on/off propagated through retained initialization, adapted teacher, proposals, student; no hidden GLM in no-GLM modes',
        grouping='unchanged E023/E030 candidate producers and common E032 selection/joint acceptance; no dataset routing',
        primary='frozen full-reference weighted R95 / T90',full_reference_targets=dict(E009=156,oral=799),E009_N_quarantine_fraction=.033034,
        oral_truth='provided-origin oracle with known-shared sensitivity, not unique-identifiability proof',
        KEEP='No R95/T90 loss against E032 in any mode, >=0.5 percentage point E009 gain, no best-bin multi-contig R95-contribution loss',
        MODIFY='Useful gain with trade-off or smaller effect',
        ABANDON='No R95 gain in any mode, or E009 loses >=1 point without >=0.5 point gain elsewhere',
        integrity_failure='NOT_ASSESSED',selection_optimality_not_established=True,
        baselines_rescored=False,skin_acquired_this_task=False,skin_previously_local_and_unscored=True,optional_parent_mean_only_control_included=False,
        bundle_not_pure_information_causal_test=True,historical_depth_filter_priors_retained_in_E031_initialization=True))


def freeze(wheel):
    """Match exact package/wheel/sdist bytes and freeze actual new consumer sources."""
    old=read('experiments/E032-biological-candidate-selection/candidate-lock.json')['package_files']
    package={str(p.relative_to(ROOT/'src/dl_binner')):binding(p) for p in (ROOT/'src/dl_binner').rglob('*')
        if p.is_file() and p.suffix in ['.py','.json'] and '__pycache__' not in p.parts}
    if any(package.get(n)!=b for n,b in old.items()):raise ValueError('Immutable accepted product member changed')
    for p in (ROOT/'src/dl_binner').rglob('*.py'):compile(p.read_text(),str(p),'exec')
    with zipfile.ZipFile(wheel) as z:
        actual={n.removeprefix('dl_binner/'):dict(bytes=len(z.read(n)),sha256=hashlib.sha256(z.read(n)).hexdigest()) for n in z.namelist() if n.startswith('dl_binner/') and not n.endswith('/')}
    if actual!=package:raise ValueError('Installed candidate wheel/source mismatch')
    import ast
    node=next(n for n in ast.parse((ROOT/'src/dl_binner/multiscale/model.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='POLICY' for t in n.targets))
    learning_policy={v.arg:ast.literal_eval(v.value) for v in node.value.keywords}
    bam_wheel=next((ROOT/'artifacts/e033-multiscale-bam/preparation/Linux-wheels').glob('pysam-*.whl'))
    write('candidate-lock.json',dict(kind='E033 additive measured-information candidate',wheel=binding(wheel),package_files=package,learning_policy=learning_policy,pysam_wheel=binding(bam_wheel),pysam_wheel_filename=bam_wheel.name,
        unchanged_E032_members=len(old),new_members=sorted(set(package)-set(old)),pysam='0.23.3',community_executed=False))
    paths=list((ROOT/'src/dl_binner').rglob('*.py'))+list((ROOT/'src/dl_binner/resources').glob('*.json'))
    paths+=list((ROOT/'scripts').glob('e033*.py'))+list((ROOT/'tests/product').glob('test_multiscale*.py'))+[ROOT/'tests/test_e033_operations.py']
    paths+=[EXP/n for n in ['design.md','protocol.json','runtime-plan.json','BAM-manifest.json','reuse-lock.json','candidate-lock.json',
        'source-audit.json','oral-GLM-milestone.json','resources.json','Snakefile']]
    paths+=[ROOT/'pyproject.toml',ROOT/'experiments/E023-adaptive-density-bins/config.json',ROOT/'experiments/E023-adaptive-density-bins/source-lock.json']
    paths+=[ROOT/n for n in ['requirements/candidate-cpu.txt','requirements/build.txt','scripts/build_candidate.py',
        'scripts/check_distribution.py','scripts/check_runtime.py','scripts/test_product.py',
        '.github/workflows/product.yml','docs/INSTALLATION.md']]
    write('source-lock.json',dict(kind='E033 prospective exact scientific/operations source',parent='ba7f9b5d50a0aab55c018f56f512a1605c98bad7',
        files={str(p.relative_to(ROOT)):binding(p) for p in sorted(set(paths))},community_outcomes_seen=False,cloud_authorized=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plans',action='store_true');p.add_argument('--wheel',type=Path);a=p.parse_args()
    if a.plans:plans()
    elif a.wheel:freeze(a.wheel)
    else:p.error('Choose metadata-only plans or candidate freeze')
