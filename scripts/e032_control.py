#!/usr/bin/env python3
"""Serial restore-only E032 cached construction DAG with verified stage seals.

No training, retrieval, marker detection, truth or cloud provisioning interface.
Unknown plan fields and unverified native releases are refused before consumers.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e024_control import fresh,seal,verify_seal

EXP=ROOT/'experiments/E032-biological-candidate-selection'
UNITS=['E009-noGLM','E009-GLM','oral-noGLM']


def product_scope():
    """Require the actual installed owned wheel, not the checkout src overlay."""
    sys.path[:]=[v for v in sys.path if Path(v).absolute()!=ROOT/'src']
    import dl_binner
    if not Path(dl_binner.__file__).is_relative_to(Path(sys.prefix)):
        raise ValueError('Owned independently installed product required')


def freeze():
    """Check the scientific package, prospective rule and actual operational paths."""
    lock=json.loads((EXP/'source-lock.json').read_text())
    for name,value in lock['files'].items():
        if binding(ROOT/name)!=value:raise ValueError('Frozen E032 source drift: '+name)
    old=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/candidate-lock.json').read_text())
    for name,value in old['package_files'].items():
        if binding(ROOT/'src/dl_binner'/name)!=value:raise ValueError('Preserved E031 product changed: '+name)
    import ast,hashlib
    text=(ROOT/'scripts/e032_control.py').read_text()
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='stage')
    science=json.loads((EXP/'science-lock.json').read_text())
    if hashlib.sha256(ast.get_source_segment(text,node).encode()).hexdigest()!=science['stage_dispatch_source_sha256']:
        raise ValueError('Frozen E032 scientific dispatch source differs')
    return dict(status='PASS',source_lock=binding(EXP/'source-lock.json'),unchanged_E031_package=True)


def read_plan(path,engineering=False):
    """Admit only the frozen three input modes and phase-local output layout."""
    p=json.loads(Path(path).read_text());schema=json.loads((EXP/'runtime-plan.json').read_text())
    if set(p)!=set(schema) or p['engineering'] is not engineering or set(p['units'])!=set(UNITS):
        raise ValueError('Unknown E032 plan/schema')
    if any(set(v)!=set(schema['units'][u]) for u,v in p['units'].items()):raise ValueError('Unknown scientific input fields')
    if not engineering:
        freeze();release=os.environ.get('E032_RELEASE_FILE')
        if not release or json.loads(Path(release).read_text()).get('plan')!=binding(path):
            raise ValueError('Externally supervised plan release required')
        for k in ['kind','limits','units','workflow_python']:
            if p[k]!=schema[k]:raise ValueError('Unfrozen E032 '+k)
    return p


def verify_inputs(p,output=None):
    """Verify consumed original bytes/full axes and both original numeric contexts."""
    product_scope()
    from dl_binner.selection.grouping import restore
    proof={};lock=json.loads((EXP/'reuse-lock.json').read_text())
    if not p['engineering']:
        for name,wanted in lock['external_files'].items():
            if binding(name)!=wanted:raise ValueError('Missing/corrupt original input: '+name)
    for u,e in p['units'].items():
        work=Path(p['restored'])/'work'/u
        data,vectors,valid,meta,*_=restore(e['features'],work/'embed/embeddings.npz',work/'graph/result/graph.npz',e['marker_evidence'],work)
        axis=dict(rows=len(valid),eligible=int(valid.sum()),bp=int(data['lengths'].sum()),samples=meta['samples'])
        if p['engineering']:
            if axis['rows']>128:raise ValueError('Engineering axes exceed tiny scope')
        elif axis!=lock['axes'][u]:raise ValueError('Full contig/ordered ten-depth axes differ')
        proof[u]=axis
    result=dict(status='PASS',axes=proof,all_original_bytes=True,no_science_regenerated=True,truth_accessed=False)
    if output:write(output,result)
    return result


def source_inputs(p,u):
    """Bind actual source, strict restore admission and original consumed inputs."""
    return dict(unit=p['units'][u],source=binding(EXP/'science-lock.json'),
        restored=binding(Path(p['restored'])/'work/restore-admission.json'))


def stage(path,name,unit=None,engineering=False):
    """Execute one new consumer or verify its sealed no-op; never replay old stages."""
    product_scope();p=read_plan(path,engineering);work=Path(p['work'])
    if name=='barrier':target=work/'barrier';unit=UNITS[0]
    elif name in ['select','audit'] and unit in UNITS:target=work/unit/name
    else:raise ValueError('Unknown E032 stage/unit')
    expected=source_inputs(p,unit)
    if (target/'done.json').is_file():
        old=verify_seal(target)
        if old.get('inputs')!=expected:raise ValueError('Sealed E032 input drift')
        return old
    target=fresh(target.parent,target.name)
    if name=='barrier':write(target/'proof.json',verify_inputs(p))
    else:
        verify_seal(work/'barrier');e=p['units'][unit];original=Path(p['restored'])/'work'/unit
        args=(e['features'],original/'embed/embeddings.npz',original/'graph/result/graph.npz',e['marker_evidence'],original)
        from dl_binner.selection.grouping import run,audit
        if name=='select':run(*args,e['fasta'],target/'result')
        else:
            verify_seal(work/unit/'select')
            write(target/'proof.json',audit(*args,work/unit/'select/result'))
    return seal(target,dict(inputs=expected))


def workflow(path,engineering=False,dry=False):
    """Run the explicit serial four-thread DAG, without --jobs defeating --cores."""
    product_scope();p=read_plan(path,engineering);work=Path(p['work']);work.mkdir(parents=True,exist_ok=True)
    for done in work.rglob('done.json'):
        old=verify_seal(done.parent);unit=next((u for u in UNITS if u in done.parts),UNITS[0])
        if old.get('inputs')!=source_inputs(p,unit):raise ValueError('Resume input/source mismatch')
    argv=[p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],'--directory',str(work),
        '--cores','4','--resources','mem_mb=26000','--benchmark-extended','--runtime-source-cache-path',str(work.parent/'workflow-source-cache'),
        '--rerun-triggers','mtime','--config','plan='+str(Path(path).absolute()),'engineering='+str(engineering).lower()]
    if dry:argv.append('--dry-run')
    subprocess.run(argv,check=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--engineering',action='store_true');p.add_argument('--workflow',action='store_true');p.add_argument('--dry-run',action='store_true')
    p.add_argument('--verify-inputs',action='store_true');p.add_argument('--output',type=Path)
    p.add_argument('--stage',choices=['barrier','select','audit']);p.add_argument('--unit',choices=UNITS);a=p.parse_args()
    if a.workflow:workflow(a.plan,a.engineering,a.dry_run)
    elif a.verify_inputs:verify_inputs(read_plan(a.plan,a.engineering),a.output)
    elif a.stage:stage(a.plan,a.stage,a.unit,a.engineering)
    else:p.error('Choose a bounded E032 action')
