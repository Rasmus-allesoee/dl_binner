#!/usr/bin/env python3
"""Restore-only E029 DAG: six retrieval proofs before unchanged E027 bin biology.

No training, original-neighbor construction, marker detection or external binner
entry point exists. Every used member is rebound before and after consumption.
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

EXP=ROOT/'experiments/E029-certifiable-joint-retrieval'
UNITS=['E009-noGLM','E009-GLM','oral-noGLM']
COMPONENTS=[(u,r) for u in UNITS for r in ['teacher','student']]


def product_scope():
    """Pin actual workers to the owned installed package despite legacy helper overlays."""
    sys.path[:]=[p for p in sys.path if Path(p).absolute()!=ROOT/'src']
    import dl_binner
    package=Path(dl_binner.__file__).resolve()
    if not package.is_relative_to(Path(sys.prefix).resolve()):
        raise ValueError('Actual consumer imported checkout/foreign product instead of owned wheel')
    print('E029_OWNED_PRODUCT',str(package),flush=True)
    return str(package)


def freeze():
    """Bind new source while preserving the complete inherited scientific freeze."""
    from e028_control import freeze as old
    previous=old();lock=json.loads((EXP/'source-lock.json').read_text())
    for name,wanted in lock['files'].items():
        if binding(ROOT/name)!=wanted:raise ValueError('Frozen E029 source differs: '+name)
    return dict(status='PASS',inherited=previous,new=binding(EXP/'source-lock.json'))


def read_plan(path,engineering=False):
    """Refuse hidden modalities, unbounded clocks or an unheld native consumer."""
    p=json.loads(Path(path).read_text())
    schema=json.loads((EXP/'runtime-plan.json').read_text())
    if set(p)!=set(schema):raise ValueError('Unknown/missing E029 plan fields')
    if (p['kind']!='E029 cached complete-global discovery' or p['engineering'] is not engineering
        or set(p['units'])!=set(UNITS)):raise ValueError('Unexpected E029 plan/scope')
    if not engineering:
        expected=json.loads((EXP/'runtime-plan.json').read_text())
        if any(p[k]!=v for k,v in expected.items() if k not in ['work','python','wheel']):raise ValueError('Unfrozen E029 policy/input/runtime')
        if not Path(p['work']).is_relative_to('/srv/dl_binner/experiments/e029'):raise ValueError('Fresh E029 native work required')
        release=os.environ.get('E029_RELEASE_FILE')
        if not release or json.loads(Path(release).read_text()).get('plan')!=binding(path):raise ValueError('Externally supervised release required')
        freeze()
    return p


def inputs(p,u,role):
    """Locate only sealed original learning; never copy or regenerate science."""
    unit=p['units'][u];root=Path(p['source_work'])/'units'/u
    return [unit['features'],root/(role+'-embed/embeddings.npz'),root/(role+'-graph/graph.npz'),unit['marker_evidence']]


def cache_for(p,u,role):
    """Resolve original passed E009 caches and fresh Oral exact caches explicitly."""
    return Path(p['retained_cache_work'] if u.startswith('E009') else p['work'])/'retrieval'/u/role/'cache'


def verify_inputs(p,output):
    """Rebind accepted learning and all four independently admitted old cache seals."""
    from e028_control import verify_inputs as original
    from dl_binner.discovery import exact
    result=original(p,Path(output).with_suffix('.learning.json'))
    lock=json.loads((EXP/'reuse-lock.json').read_text())
    for name,wanted in lock['retained_retrieval_members'].items():
        if binding(Path(p['retained_cache_work'])/name)!=wanted:
            raise ValueError('Retained completed E009 retrieval changed: '+name)
    proofs={}
    for u,r in COMPONENTS[:4]:
        a=inputs(p,u,r);proofs[u+'-'+r]=exact.restore(*a[:3],cache_for(p,u,r))[1]
    result['retained_four_retrievals']=proofs
    write(output,result);return result


def stage(path,name,u=None,role=None,engineering=False):
    """Execute one recorded stage with an explicit six-cache barrier and strict resume."""
    product_scope()
    p=read_plan(path,engineering);work=Path(p['work'])
    target=work/(('retrieval/'+u+'/'+role) if name=='retrieve' else ('groups/'+u+'/'+role) if name=='group' else u+'/'+name if u else name)
    if (target/'done.json').exists():verify_seal(target);return
    target=fresh(target.parent,target.name)
    if name=='retrieve':
        from dl_binner.discovery import exact
        a=inputs(p,u,role)
        if u.startswith('E009'):
            proof=exact.restore(*a[:3],cache_for(p,u,role))[1]
            write(target/'reuse.json',dict(status='PASS',original_cache=str(cache_for(p,u,role)),seal=proof,science_repeated=False))
        else:exact.prepare(*a[:3],target/'cache')
    elif name=='barrier':
        records={}
        for unit,r in COMPONENTS:
            cache=work/'retrieval'/unit/r;verify_seal(cache)
            from dl_binner.discovery.exact import restore
            a=inputs(p,unit,r);records[unit+'-'+r]=restore(*a[:3],cache_for(p,unit,r))[1]
        write(target/'proof.json',dict(status='PASS',all_six_retrievals_passed=True,caches=records,biological_selection_started=False))
    elif name=='group':
        verify_seal(work/'barrier')
        from dl_binner.discovery.exact import run
        run(*inputs(p,u,role),cache_for(p,u,role),target/'result')
    elif name=='export':
        from dl_binner.information.export import export
        accounting={}
        for r in ['teacher','student']:
            verify_seal(work/'groups'/u/r)
            for arm in ['parent','post']:
                key=r+'-'+arm
                accounting[key]=export(p['units'][u]['features'],work/'groups'/u/r/'result'/(arm+'-partition.json'),p['units'][u]['fasta'],target/key,include_dna=False)
        write(target/'accounting.json',accounting)
        write(target/'DNA-reuse.json',dict(status='PASS',fasta=p['units'][u]['fasta'],binding=binding(p['units'][u]['fasta']),full_DNA_assignment_accounting=True,physical_DNA_emission=False))
    elif name=='audit':
        from dl_binner.discovery.exact import audit
        verify_seal(work/u/'export')
        proof={r:audit(*inputs(p,u,r),work/'groups'/u/r/'result') for r in ['teacher','student']}
        write(target/'proof.json',dict(status='PASS',learners=proof,learning_unchanged=True))
    else:raise ValueError('No training or unknown E029 stage supported')
    return seal(target)


def workflow(path,engineering=False,dry=False):
    """Run independent ready rules serially; explicit barrier prevents premature bins."""
    product_scope()
    p=read_plan(path,engineering);Path(p['work']).mkdir(parents=True,exist_ok=True)
    for d in Path(p['work']).rglob('done.json'):verify_seal(d.parent)
    argv=[p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],'--directory',p['work'],'--cores','4','--resources','mem_mb=26000','--keep-going','--benchmark-extended','--runtime-source-cache-path',str(Path(p['work']).parent/'workflow-source-cache'),'--rerun-triggers','mtime','--config','plan='+str(Path(path).absolute()),'engineering='+str(engineering).lower()]
    if dry:argv.append('--dry-run')
    return subprocess.run(argv,check=True).returncode


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--plan',type=Path,required=True);a.add_argument('--unit',choices=UNITS);a.add_argument('--role',choices=['teacher','student']);a.add_argument('--stage',choices=['retrieve','barrier','group','export','audit']);a.add_argument('--workflow',action='store_true');a.add_argument('--verify-inputs',action='store_true');a.add_argument('--output',type=Path);a.add_argument('--engineering',action='store_true');a.add_argument('--dry-run',action='store_true');v=a.parse_args()
    if v.verify_inputs:verify_inputs(read_plan(v.plan,v.engineering),v.output)
    elif v.workflow:workflow(v.plan,v.engineering,v.dry_run)
    elif v.stage:stage(v.plan,v.stage,v.unit,v.role,v.engineering)
    else:a.error('Select one restore-only action')
