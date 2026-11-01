#!/usr/bin/env python3
"""Derive prospective E031 plans/byte locks from accepted small receipts only.

No community array, label, model, cloud account or VM is opened. Generated plans
are preparation records, not execution admission. Re-freezing is allowed only
before the candidate's first community outcome; retain Git history and journals.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).absolute().parents[1]
EXP=ROOT/'experiments/E031-bootstrap-preserving-learning'
UNITS=['E009-noGLM','E009-GLM','oral-noGLM']


def read(path):
    """Read one existing small metadata record relative to the repository."""
    return json.loads((ROOT/path).read_text())


def binding(path):
    """Bind file bytes without importing tensor or source-checkout product code."""
    p=Path(path);h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return dict(bytes=p.stat().st_size,sha256=h.hexdigest())


def write(path,value):
    """Write a prospective small record; never used to mutate accepted E009–E030 files."""
    path=Path(path)
    if not path.is_relative_to(EXP):raise ValueError('Only E031 preparation records may be generated')
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def plans():
    """Bind native original locators, explicit reuse and three common feature modes."""
    current=read('experiments/E030-supported-biological-bins/runtime-plan.json')
    accepted=read('experiments/E028-global-discovery-repair/reuse-lock.json')
    original=read('experiments/E027-common-information-binner/runtime-plan.json')
    old=read('experiments/E023-adaptive-density-bins/reuse-lock.json')
    inv=read('artifacts/e023-inspection/20261027T000221Z/verified/inventory.json')
    source=current['source_work'];native=read('experiments/E023-adaptive-density-bins/native-observed.json')['identity']['root']
    members={k.split('/group/',1)[1]:v for k,v in inv['all_work_members'].items() if k.startswith('units/E009-E022/group/')}
    bridge_units={};learning_units={};bridge_files={};learning_files={}
    external=accepted['external_files']
    def external_binding(path):
        if path in external:return external[path]
        if path in old['files']:return old['files'][path]
        values=read('experiments/E027-common-information-binner/reuse-lock.json')['files']
        if path in values:return values[path]
        raise KeyError('No accepted binding for '+path)
    for u in UNITS:
        unit=current['units'][u];bridge_units[u]={k:unit[k] for k in ['features','fasta','marker_evidence']}
        for name in ['features','fasta','marker_evidence']:
            path=unit[name];bridge_files[path]=external_binding(path);learning_files[path]=external_binding(path)
            if name=='features':
                p=str(Path(path).with_suffix('.json'));bridge_files[p]=external_binding(p);learning_files[p]=external_binding(p)
        for role in ['teacher','student']:
            root=source+'/units/'+u
            e=dict(embeddings=root+'/'+role+'-embed/embeddings.npz',graph=root+'/'+role+'-graph/graph.npz',accepted=None,members=None)
            for path in [e['embeddings'],e['graph']]:
                for p in [path,str(Path(path).with_suffix('.json'))]:
                    bridge_files[p]=accepted['all_closed_stage_members'][p.removeprefix(source+'/')]
            if u=='E009-GLM' and role=='student':
                e.update(accepted=native+'/work/units/E009-E022/group',members=members)
                for n,b in members.items():bridge_files[e['accepted']+'/'+n]=b
            bridge_units[u][role]=e
        root=source+'/units/'+u;orig=original['units'][u]
        learning_units[u]=dict(features=unit['features'],fasta=unit['fasta'],marker_evidence=unit['marker_evidence'],
            views=root+'/admit/views.npz',tokens=root+'/admit/tokens',frozen=unit['frozen'],
            bootstrap=root+'/teacher/checkpoint.pt',source_pairs=root+'/pairs/cache',
            embeddings=root+'/teacher-embed/embeddings.npz',graph=root+'/teacher-graph/graph.npz')
        for name,b in accepted['all_closed_stage_members'].items():
            if any(name.startswith('units/'+u+'/'+k+'/') for k in ['admit','teacher','teacher-embed','teacher-graph','pairs']):
                learning_files[source+'/'+name]=b
        if unit['frozen']:
            for path,b in external.items():
                if path.startswith(unit['frozen']+'/'):learning_files[path]=b
    axes={u:{k:v for k,v in a.items() if k in ['rows','bp','eligible','samples']}
          for u,a in read('experiments/E028-global-discovery-repair/protocol.json')['axes'].items()}
    reused=read('experiments/E030-supported-biological-bins/reuse-lock.json')
    lock=dict(kind='E031 scoped restore-only source/learning/result inputs',axes=axes,
        bridge_files=bridge_files,learning_files=learning_files,
        native_dependency_base=reused['native_dependency_base'],native_runtime_reference=reused['native_runtime_reference'],
        accepted_E023=read('experiments/E023-adaptive-density-bins/inspection-observed.json')['archive'],
        accepted_E030=read('experiments/E030-supported-biological-bins/inspection-observed.json').get('archive'),
        all_E023_product_source={k:v for k,v in read('experiments/E023-adaptive-density-bins/source-lock.json')['files'].items() if k.startswith('src/dl_binner/')},
        no_retraining_or_rescore_in_bridge=True,original_source='ca7b142aec1d15762fbc46d9f136d2af616dc1af')
    write(EXP/'reuse-lock.json',lock)
    queries={}
    for u in UNITS:
        queries[u]={}
        for role in ['teacher','student']:
            p=ROOT/'artifacts/e029-certifiable-joint-retrieval/inspection/controls/work/groups'/u/role/'result/retrieval/audit.json'
            record=json.loads(p.read_text())
            expected=reused['accepted_members']['groups/'+u+'/'+role+'/result/retrieval/audit.json']
            if binding(p)!=expected:raise ValueError('Frozen source-blind query receipt differs')
            queries[u][role]=dict(source_binding=expected,queries=[dict(id=q['id'],strata=q['strata']) for q in record['queries']],
                                 source='Accepted E029 technical recall query population; no truth selection')
    write(EXP/'query-axes.json',queries)
    for comparison,units,seconds,ceiling,extra in [('bridge',bridge_units,21600,4,7*1024**3),('learning',learning_units,43200,6,8*1024**3)]:
        limits=dict(seconds=seconds,provider_STOP_seconds=seconds+900,ceiling_USD=ceiling,numerical_threads=4,
            tree_RSS_bytes=26_000_000_000,free_reserve_bytes=25*1024**3,extra_bytes=extra,
            compressed_export_bytes=2*1024**3,logical_export_bytes=4*1024**3,
            retention_end='2026-11-04T00:00:00+01:00',allocated_vCPUs=8,WAN_review_bytes=2*1024**3)
        p=dict(kind='E031 frozen bootstrap/construction decision',comparison=comparison,
            work='/srv/dl_binner/experiments/e031/NEW_PHASE/work',units=units,
            python='/srv/dl_binner/experiments/e031/NEW_PHASE/env/bin/python',workflow_python=current['workflow_python'],
            worker='/srv/dl_binner/repo/scripts/e031_control.py',snakefile='/srv/dl_binner/repo/experiments/E031-bootstrap-preserving-learning/'+comparison+'.smk',
            limits=limits,reuse_lock='/srv/dl_binner/repo/experiments/E031-bootstrap-preserving-learning/reuse-lock.json',
            wheel='/srv/dl_binner/experiments/e031/NEW_PHASE/payload/dl_binner-0.1.0.dev9-py3-none-any.whl',engineering=False)
        write(EXP/(comparison+'-plan.json'),p)


def freeze(wheel):
    """Freeze installed package/defaults, protocols and actual preparation/ops adapters."""
    with zipfile.ZipFile(wheel) as z:
        files={n.removeprefix('dl_binner/'):dict(bytes=len(z.read(n)),sha256=hashlib.sha256(z.read(n)).hexdigest())
               for n in z.namelist() if n.startswith('dl_binner/') and not n.endswith('/')}
    actual={str(p.relative_to(ROOT/'src/dl_binner')):binding(p) for p in (ROOT/'src/dl_binner').rglob('*')
            if p.is_file() and p.suffix in ['.py','.json'] and '__pycache__' not in p.parts}
    if files!=actual:raise ValueError('Wheel/source identity differs; build fresh before freezing')
    old=read('experiments/E030-supported-biological-bins/candidate-lock.json')['package_files']
    if any(files[n]!=b for n,b in old.items()):raise ValueError('Accepted product member changed')
    write(EXP/'candidate-lock.json',dict(kind='E031 installed research candidate',wheel=binding(wheel),
        version='0.1.0.dev9',package_files=files,unchanged_E030_members=len(old),new_package_members=sorted(set(files)-set(old))))
    tree=ast.parse((ROOT/'scripts/e031_control.py').read_text())
    stage=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='stage')
    # Operational limits/phase/collector changes must not invalidate completed
    # science when product math, dispatch and consumed inputs are unchanged.
    science=dict(kind='E031 scientific stage identity independent of operational envelope',
        package_files=files,stage_dispatch_sha256=hashlib.sha256(ast.dump(stage,include_attributes=False).encode()).hexdigest(),
        protocol=binding(EXP/'protocol.json'),query_axes=binding(EXP/'query-axes.json'),
        E023_policy=binding(ROOT/'experiments/E023-adaptive-density-bins/config.json'),
        units={c:read('experiments/E031-bootstrap-preserving-learning/'+c+'-plan.json')['units'] for c in ['bridge','learning']})
    # Canonical object-key order is not a biological axis. Ordered lists remain
    # ordered, including every sample/contig contract carried by the inputs.
    write(EXP/'science-lock.json',json.loads(json.dumps(science,sort_keys=True)))
    paths=list((ROOT/'src/dl_binner').rglob('*.py'))+list((ROOT/'src/dl_binner/resources').glob('*.json'))
    paths+=list((ROOT/'scripts').glob('*.py'))+list((ROOT/'tests/product').glob('*.py'))
    paths+=[ROOT/'tests/test_e009_exit_watchdog.py']
    paths+=list(EXP.glob('*.smk'))+[EXP/n for n in ['design.md','protocol.json','science-lock.json','reuse-lock.json','review-lock.json','resources.json','query-axes.json','bridge-plan.json','learning-plan.json','candidate-lock.json']]
    paths+=[ROOT/'experiments/E023-adaptive-density-bins/source-lock.json',ROOT/'experiments/E023-adaptive-density-bins/config.json']
    paths+=list((ROOT/'tests').glob('test_e031*.py'))
    write(EXP/'source-lock.json',dict(kind='E031 prospective local scientific and operations source',parent_source='ca7b142',
        files={str(p.relative_to(ROOT)):binding(p) for p in sorted(set(paths))},
        community_executed=False,cloud_authorized=False))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--plans',action='store_true');a.add_argument('--wheel',type=Path);v=a.parse_args()
    if v.plans:plans()
    elif v.wheel:freeze(v.wheel)
    else:a.error('Choose metadata-only plans or prospective source freeze')
