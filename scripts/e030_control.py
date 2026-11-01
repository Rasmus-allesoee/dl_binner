#!/usr/bin/env python3
"""Restore-only six-actor bin construction: no fit, detector, aligner or retrieval.

Every scientific stage has an exclusive directory and a content seal. Verified
resume keeps accepted stages; a stale/incomplete directory fails explicitly.
The production worker pins the installed product before legacy helper imports.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e024_control import fresh,seal,verify_seal

EXP=ROOT/'experiments/E030-supported-biological-bins'
UNITS=['E009-noGLM','E009-GLM','oral-noGLM']
COMPONENTS=[(u,r) for u in UNITS for r in ['teacher','student']]
ARMS=['root-only','pre','post']


def product_scope():
    """Refuse checkout/foreign product execution, including inherited import overlays."""
    sys.path[:]=[p for p in sys.path if Path(p).absolute()!=ROOT/'src']
    import dl_binner
    actual=Path(dl_binner.__file__).resolve()
    if not actual.is_relative_to(Path(sys.prefix).resolve()):raise ValueError('Actual worker did not import owned installed package')
    print('E030_OWNED_PRODUCT',actual,flush=True);return str(actual)


def freeze():
    """Bind all new scientific/operational source and retain inherited immutable locks."""
    from e029_control import freeze as old
    previous=old();lock=json.loads((EXP/'source-lock.json').read_text())
    for name,wanted in lock['files'].items():
        if binding(ROOT/name)!=wanted:raise ValueError('Frozen E030 source differs: '+name)
    return dict(status='PASS',inherited=previous,source=binding(EXP/'source-lock.json'))


def read_plan(path,engineering=False):
    """Require declared modes, frozen inputs/resources and external native release."""
    p=json.loads(Path(path).read_text());schema=json.loads((EXP/'runtime-plan.json').read_text())
    if set(p)!=set(schema) or p['engineering'] is not engineering or set(p['units'])!=set(UNITS):raise ValueError('Unknown E030 plan/scope')
    if not engineering:
        if any(p[k]!=v for k,v in schema.items() if k not in ['work','python','wheel']):raise ValueError('Unfrozen E030 input/policy/runtime')
        if not Path(p['work']).is_relative_to('/srv/dl_binner/experiments/e030'):raise ValueError('Fresh E030 native work required')
        release=os.environ.get('E030_RELEASE_FILE')
        if not release or json.loads(Path(release).read_text()).get('plan')!=binding(path):raise ValueError('Externally supervised native release required')
        freeze()
    return p


def inputs(p,u,r):
    """Locate only original sealed learning and measured-parent feature inputs."""
    unit=p['units'][u];root=Path(p['source_work'])/'units'/u
    return [unit['features'],root/(r+'-embed/embeddings.npz'),root/(r+'-graph/graph.npz'),unit['marker_evidence']]


def accepted(p,u,r):
    """Locate the exact independently admitted E029 forest and retrieval cache."""
    return Path(p['accepted_work'])/'groups'/u/r/'result'


def verify_inputs(p,output):
    """Verify scoped original used bytes, full modes/axes and every reused E029 member."""
    product_scope()
    from e028_control import verify_inputs as original
    record=original(p,Path(output).with_suffix('.learning.json'))
    lock=json.loads((EXP/'reuse-lock.json').read_text())
    for i,(name,wanted) in enumerate(lock['accepted_members'].items()):
        path=Path(p['accepted_work'])/name
        if not path.is_file() or path.is_symlink() or binding(path)!=wanted:raise ValueError('Missing/corrupt accepted result: '+name)
        if i%30==0:print('E030_ACCEPTED_MEMBER',i,len(lock['accepted_members']),flush=True)
    record.update(accepted_members=lock['accepted_members'],accepted_work=p['accepted_work'],accepted_source=lock['accepted_science_source'],
        neighbors_or_forests_rebuilt=0,inputs_relocated=False)
    write(output,record);return record


def stage(path,name,u=None,role=None,engineering=False):
    """Execute one bounded scientific rule; no implicit fallback or completed replay."""
    product_scope();p=read_plan(path,engineering);work=Path(p['work'])
    target=work/('groups/'+u+'/'+role if name=='group' else u+'/'+name if u else name)
    if (target/'done.json').exists():verify_seal(target);return
    target=fresh(target.parent,target.name)
    if name=='barrier':
        proofs={}
        for unit,r in COMPONENTS:
            root=accepted(p,unit,r);m=json.loads((root/'completed.json').read_text())
            if m['status']!='SUCCESS' or any(binding(root/n)!=v for n,v in m['files'].items()):raise ValueError('Accepted cache barrier failed')
            proofs[unit+'-'+r]=dict(root=str(root),completed=binding(root/'completed.json'))
        write(target/'proof.json',dict(status='PASS',all_six_accepted=True,proofs=proofs,no_retrieval=True))
    elif name=='group':
        verify_seal(work/'barrier')
        from dl_binner.construction.grouping import run
        run(*inputs(p,u,role),accepted(p,u,role),target/'result')
    elif name=='export':
        from dl_binner.information.export import export
        result={}
        for r in ['teacher','student']:
            verify_seal(work/'groups'/u/r)
            for arm in ARMS:
                result[r+'-'+arm]=export(p['units'][u]['features'],work/'groups'/u/r/'result'/(arm+'-partition.json'),p['units'][u]['fasta'],target/(r+'-'+arm),include_dna=False)
        write(target/'accounting.json',result)
        write(target/'DNA-reuse.json',dict(status='PASS',fasta=p['units'][u]['fasta'],binding=binding(p['units'][u]['fasta']),full_DNA_preserved=True,physical_DNA_emission=False))
    elif name=='audit':
        from dl_binner.construction.grouping import audit
        verify_seal(work/u/'export')
        result={r:audit(*inputs(p,u,r),accepted(p,u,r),work/'groups'/u/r/'result') for r in ['teacher','student']}
        write(target/'proof.json',dict(status='PASS',learners=result,learning_unchanged=True))
    else:raise ValueError('Unknown stage; fits and retrieval have no E030 entry point')
    return seal(target)


def workflow(path,engineering=False,dry=False):
    """Run the serial local Snakemake DAG with core/RAM caps and real benchmarks."""
    product_scope();p=read_plan(path,engineering);Path(p['work']).mkdir(parents=True,exist_ok=True)
    for d in Path(p['work']).rglob('done.json'):verify_seal(d.parent)
    argv=[p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],'--directory',p['work'],
        '--cores','4','--resources','mem_mb=26000','--keep-going','--benchmark-extended',
        '--runtime-source-cache-path',str(Path(p['work']).parent/'workflow-source-cache'),'--rerun-triggers','mtime',
        '--config','plan='+str(Path(path).absolute()),'engineering='+str(engineering).lower()]
    if dry:argv.append('--dry-run')
    return subprocess.run(argv,check=True).returncode


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--plan',type=Path,required=True)
    a.add_argument('--unit',choices=UNITS);a.add_argument('--role',choices=['teacher','student'])
    a.add_argument('--stage',choices=['barrier','group','export','audit']);a.add_argument('--workflow',action='store_true')
    a.add_argument('--verify-inputs',action='store_true');a.add_argument('--output',type=Path)
    a.add_argument('--engineering',action='store_true');a.add_argument('--dry-run',action='store_true');v=a.parse_args()
    if v.verify_inputs:verify_inputs(read_plan(v.plan,v.engineering),v.output)
    elif v.workflow:workflow(v.plan,v.engineering,v.dry_run)
    elif v.stage:stage(v.plan,v.stage,v.unit,v.role,v.engineering)
    else:a.error('Choose one restore-only action')
