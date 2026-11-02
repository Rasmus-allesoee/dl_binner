#!/usr/bin/env python3
"""Prepared E031 serial cached bridge and separate bootstrap-continuation DAGs.

Native execution requires an external fresh release; engineering mode refuses
community-sized axes. There is no cloud mutation, acquisition, detector or truth
interface. Closed stages resume only through exact source/input/member seals.
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

EXP=ROOT/'experiments/E031-bootstrap-preserving-learning'
UNITS=['E009-noGLM','E009-GLM','oral-noGLM']
COMPONENTS=[(u,r) for u in UNITS for r in ['teacher','student']]
LEARNING=['confidence','train','embed','graph','retrieve','forest','construct','export','audit']


def product_scope():
    """Import the actual independently installed wheel before legacy helper overlays."""
    sys.path[:]=[p for p in sys.path if Path(p).absolute()!=ROOT/'src']
    import dl_binner
    path=Path(dl_binner.__file__).resolve()
    if not path.is_relative_to(Path(sys.prefix).resolve()):raise ValueError('Owned installed product required')
    return str(path)


def freeze(include_files=False):
    """Check source/defaults and all unchanged accepted product members."""
    lock=json.loads((EXP/'source-lock.json').read_text())
    effective = dict(lock['files'])
    supplement = EXP/'paired-source-lock.json'
    if supplement.is_file():
        import ast,hashlib
        extra=json.loads(supplement.read_text())
        allowed={'scripts/e031_control.py','scripts/e031_phase.py','scripts/e031_gates.py','scripts/e031_review.py'}
        if set(extra['amended_operational_files'])!=allowed:raise ValueError('Unadmitted scientific source amendment')
        for name,wanted in extra['files'].items():
            if name in effective and name not in allowed:raise ValueError('Prepared science may not change')
            if binding(ROOT/name)!=wanted:raise ValueError('Paired supplement differs: '+name)
        text=(ROOT/'scripts/e031_control.py').read_text()
        node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='stage')
        if hashlib.sha256(ast.get_source_segment(text,node).encode()).hexdigest()!=extra['original_stage_source_sha256']:
            raise ValueError('Frozen original scientific stage source bytes changed')
        effective.update(extra['files'])
        effective[str(supplement.relative_to(ROOT))]=binding(supplement)
    for name,wanted in effective.items():
        if binding(ROOT/name)!=wanted:raise ValueError('Frozen E031 source differs: '+name)
    old=json.loads((ROOT/'experiments/E023-adaptive-density-bins/source-lock.json').read_text())
    names=[n for n in old['files'] if n.startswith('src/dl_binner/')]
    for name in names:
        if binding(ROOT/name)!=old['files'][name]:raise ValueError('E023 transitive product source drift: '+name)
    proof=dict(status='PASS',unchanged_E023_product_members=len(names),
               old_lock=binding(ROOT/'experiments/E023-adaptive-density-bins/source-lock.json'))
    result=dict(status='PASS',source=binding(EXP/'source-lock.json'),E023=proof,
        paired_supplement=binding(supplement) if supplement.is_file() else None)
    if include_files:result['effective_files']=effective
    return result


def read_plan(path,engineering=False):
    """Refuse changed scope, native release drift and hidden GLM/truth routing."""
    p=json.loads(Path(path).read_text());comparison=p.get('comparison')
    if comparison not in ['bridge','learning']:raise ValueError('One frozen comparison required')
    paired=p.get('worker')=='/srv/dl_binner/repo/scripts/e031_paired.py' or (engineering and str(p.get('worker','')).endswith('/e031_paired.py'))
    schema=json.loads((EXP/('paired-plan.json' if paired else comparison+'-plan.json')).read_text())
    if set(p)!=set(schema) or p['engineering'] is not engineering or set(p['units'])!=set(UNITS):
        raise ValueError('Unknown E031 plan/schema')
    if any(set(p['units'][u])!=set(schema['units'][u]) for u in UNITS):raise ValueError('Unknown scientific/truth input field')
    if not engineering:
        if any(p[k]!=v for k,v in schema.items() if k not in ['work','python','wheel']):raise ValueError('Unfrozen E031 input/policy/runtime')
        if not Path(p['work']).is_relative_to('/srv/dl_binner/experiments/e031'):raise ValueError('Fresh E031 native work required')
        release=os.environ.get('E031_RELEASE_FILE')
        if not release or json.loads(Path(release).read_text()).get('plan')!=binding(path):raise ValueError('Externally supervised E031 release required')
        freeze()
    return p


def verify_inputs(p,output=None,engineering=False):
    """Verify only consumed original members, all axes and exact native vector identity."""
    product_scope()
    from dl_binner.information.grouping import load_inputs
    from dl_binner.density.grouping import sparse_input
    lock=json.loads((EXP/'reuse-lock.json').read_text())
    hashed=verify_file_bindings(lock[p['comparison']+'_files']) if not engineering else {}
    result={}
    for u,entry in p['units'].items():
        roles=['teacher','student'] if p['comparison']=='bridge' else ['teacher']
        for role in roles:
            e=entry[role] if p['comparison']=='bridge' else entry
            data,vectors,valid,meta=load_inputs(entry['features'],e['embeddings'])
            sparse_input(e['graph'],data['ids'].tolist(),valid,e['embeddings'])
            axis=dict(rows=len(data['ids']),bp=int(data['lengths'].sum()),eligible=int(data['eligible'].sum()),samples=meta['samples'])
            if engineering:
                if axis['rows']>128 or axis['bp']>1_000_000:raise ValueError('Engineering fixture exceeds tiny scope')
            elif axis!=lock['axes'][u]:raise ValueError('Complete contig/ordered ten-depth axes differ')
            result[u+'-'+role]=axis
    proof=dict(status='PASS',axes=result,comparison=p['comparison'],original_inputs_untouched=True,
               hashed_inputs=hashed,verified_original_files=len(hashed),verified_original_bytes=sum(b['bytes'] for b in hashed.values()),
               truth_accessed=False,engineering=engineering)
    if output:write(output,proof)
    return proof


def verify_file_bindings(expected):
    """Retain actual per-file measurements, not only a successful summary counter."""
    actual={}
    for at,(name,wanted) in enumerate(expected.items()):
        value=binding(name)
        if value!=wanted:raise ValueError('Missing/corrupt retained member; no fallback: '+name)
        actual[name]=value
        if at%30==0:print('E031_VERIFIED_ORIGINAL',at+1,len(expected),name,flush=True)
    return actual


def source_inputs(p,u):
    """Bind the exact stage policy, installed source lock and all consumed original files."""
    science=json.loads((EXP/'science-lock.json').read_text())
    if not p['engineering'] and p['units']!=science['units'][p['comparison']]:raise ValueError('Frozen scientific unit policy differs')
    result=dict(unit=p['units'][u],source=binding(EXP/'science-lock.json'),comparison=p['comparison'])
    if p['engineering']:
        paths=[]
        def walk(value):
            if isinstance(value,dict):
                for v in value.values():walk(v)
            elif isinstance(value,str) and Path(value).is_file():paths.append(value)
        walk(p['units'][u]);result['inputs']={n:binding(n) for n in paths}
    else:
        lock=json.loads((EXP/'reuse-lock.json').read_text())
        result['inputs']=lock[p['comparison']+'_files']
    return result


def stage(path,name,u=None,role=None,engineering=False):
    """Execute one stage, with verified completed-stage reuse and no implicit retry."""
    product_scope();p=read_plan(path,engineering);work=Path(p['work'])
    if engineering:verify_inputs(p,engineering=True)
    if name=='barrier':target=work/'barrier'
    elif u in UNITS:target=work/('actors/'+u+'/'+role if name=='actor' and role in ['teacher','student'] else u+'/'+name)
    else:raise ValueError('Unknown E031 actor')
    expected=source_inputs(p,u or UNITS[0])
    if (target/'done.json').is_file():
        record=verify_seal(target)
        if record.get('inputs')!=expected:raise ValueError('Completed E031 stage source/input drift')
        return record
    target=fresh(target.parent,target.name)
    if name=='barrier':
        write(target/'proof.json',verify_inputs(p,engineering=engineering))
    else:
        verify_seal(work/'barrier');entry=p['units'][u]
        if p['comparison']=='bridge':
            if name=='actor':
                from dl_binner.bootstrap.bridge import run,query_view
                e=entry[role]
                run(entry['features'],e['embeddings'],e['graph'],entry['marker_evidence'],entry['fasta'],
                    ROOT/'experiments/E023-adaptive-density-bins/config.json',
                    ROOT/'experiments/E023-adaptive-density-bins/source-lock.json',target/'science',
                    accepted=e['accepted'],members=e['members'],engineering=engineering)
                result_root=Path(e['accepted']) if e['accepted'] else target/'science/result'
                queries=(json.loads((EXP/'query-axes.json').read_text())[u][role]['queries'] if not engineering else
                         [{'id':q,'strata':[]} for q in json.loads((result_root/'selected-partition.json').read_text())['ids'][:4]])
                query_view(result_root,entry['features'],e['graph'],queries,target/'query-neighbors.json')
            elif name=='audit':
                for r in ['teacher','student']:verify_seal(work/'actors'/u/r)
                write(target/'proof.json',dict(status='PASS',both_roles=True,no_new_fit=True))
            else:raise ValueError('Bridge has no learning/retrieval/marker stage')
        else:
            if name not in LEARNING:raise ValueError('Unknown learning stage')
            root=work/u
            at=LEARNING.index(name)
            if at:verify_seal(root/LEARNING[at-1])
            features=entry['features'];emb=root/'embed/embeddings.npz';graph=root/'graph/result/graph.npz'
            if name=='confidence':
                from dl_binner.bootstrap.pairs import prepare
                prepare(entry['source_pairs'],features,entry['embeddings'],entry['graph'],target/'cache')
            elif name in ['train','embed']:
                from dl_binner.bootstrap import model
                args=(features,entry['views'],entry['tokens'],entry['frozen'],root/'confidence/cache',entry['bootstrap'])
                if name=='train':model.train(*args,target/'result')
                else:model.embed(*args,root/'train/result/checkpoint.pt',emb)
            elif name=='graph':
                from dl_binner.unified.graph import prepare
                from dl_binner.unified.training import configuration
                prepare(features,emb,target/'result',configuration(entry['frozen'] is not None))
            elif name in ['retrieve','forest']:
                from dl_binner.discovery import exact
                if name=='retrieve':exact.prepare(features,emb,graph,target/'result')
                else:exact.run(features,emb,graph,entry['marker_evidence'],root/'retrieve/result',target/'result')
            elif name=='construct':
                from dl_binner.construction.grouping import run
                run(features,emb,graph,entry['marker_evidence'],root/'forest/result',target/'result')
            elif name=='export':
                from dl_binner.information.export import export
                values={arm:export(features,root/'construct/result'/(arm+'-partition.json'),entry['fasta'],target/arm,include_dna=False)
                        for arm in ['root-only','pre','post']}
                write(target/'accounting.json',values)
            else:
                from dl_binner.construction.grouping import audit
                write(target/'proof.json',audit(features,emb,graph,entry['marker_evidence'],root/'forest/result',root/'construct/result'))
    return seal(target,dict(inputs=expected))


def workflow(path,engineering=False,dry=False):
    """Run serial Snakemake with explicit CPU/RAM bounds and per-rule benchmarks."""
    product_scope();p=read_plan(path,engineering);work=Path(p['work']);work.mkdir(parents=True,exist_ok=True)
    verify_inputs(p,engineering=engineering)
    for name in work.rglob('done.json'):
        record=verify_seal(name.parent)
        unit=next((u for u in UNITS if u in name.parts),UNITS[0])
        if record.get('inputs')!=source_inputs(p,unit):raise ValueError('Verified resume source/input drift')
    if any(not (d/'done.json').is_file() for d in work.glob('*/train') if d.is_dir()):
        raise ValueError('Incomplete fit is retained; explicit verified recovery required')
    argv=[p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],'--directory',str(work),
        '--cores','4','--resources','mem_mb=26000','--benchmark-extended',
        '--runtime-source-cache-path',str(work.parent/'workflow-source-cache'),'--rerun-triggers','mtime',
        '--config','plan='+str(Path(path).absolute()),'engineering='+str(engineering).lower()]
    if dry:argv.append('--dry-run')
    return subprocess.run(argv,check=True).returncode


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--plan',required=True,type=Path)
    a.add_argument('--engineering',action='store_true');a.add_argument('--workflow',action='store_true');a.add_argument('--dry-run',action='store_true')
    a.add_argument('--verify-inputs',action='store_true');a.add_argument('--output',type=Path)
    a.add_argument('--stage',choices=['barrier','actor']+LEARNING);a.add_argument('--unit',choices=UNITS);a.add_argument('--role',choices=['teacher','student'])
    v=a.parse_args()
    if v.verify_inputs:verify_inputs(read_plan(v.plan,v.engineering),v.output,v.engineering)
    elif v.workflow:workflow(v.plan,v.engineering,v.dry_run)
    elif v.stage:stage(v.plan,v.stage,v.unit,v.role,v.engineering)
    else:a.error('Choose one bounded E031 action')
