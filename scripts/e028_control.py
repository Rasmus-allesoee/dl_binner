#!/usr/bin/env python3
"""Restore-only E028 DAG: six retrieval proofs before unchanged E027 bin biology.

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

EXP=ROOT/'experiments/E028-global-discovery-repair'
UNITS=['E009-noGLM','E009-GLM','oral-noGLM']
COMPONENTS=[(u,r) for u in UNITS for r in ['teacher','student']]


def product_scope():
    """Pin actual workers to the owned installed package despite legacy helper overlays."""
    sys.path[:]=[p for p in sys.path if Path(p).absolute()!=ROOT/'src']
    import dl_binner
    package=Path(dl_binner.__file__).resolve()
    if not package.is_relative_to(Path(sys.prefix).resolve()):
        raise ValueError('Actual consumer imported checkout/foreign product instead of owned wheel')
    print('E028_OWNED_PRODUCT',str(package),flush=True)
    return str(package)


def freeze():
    """Bind new source while preserving the complete inherited scientific freeze."""
    from e027_control import freeze as old
    previous=old();lock=json.loads((EXP/'source-lock.json').read_text())
    for name,wanted in lock['files'].items():
        if binding(ROOT/name)!=wanted:raise ValueError('Frozen E028 source differs: '+name)
    return dict(status='PASS',inherited=previous,new=binding(EXP/'source-lock.json'))


def read_plan(path,engineering=False):
    """Refuse hidden modalities, unbounded clocks or an unheld native consumer."""
    p=json.loads(Path(path).read_text())
    schema=json.loads((EXP/'runtime-plan.json').read_text())
    if set(p)!=set(schema):raise ValueError('Unknown/missing E028 plan fields')
    if (p['kind']!='E028 cached complete-global discovery' or p['engineering'] is not engineering
        or set(p['units'])!=set(UNITS)):raise ValueError('Unexpected E028 plan/scope')
    if not engineering:
        expected=json.loads((EXP/'runtime-plan.json').read_text())
        if any(p[k]!=v for k,v in expected.items() if k not in ['work','python','wheel']):raise ValueError('Unfrozen E028 policy/input/runtime')
        if not Path(p['work']).is_relative_to('/srv/dl_binner/experiments/e028'):raise ValueError('Fresh E028 native work required')
        release=os.environ.get('E028_RELEASE_FILE')
        if not release or json.loads(Path(release).read_text()).get('plan')!=binding(path):raise ValueError('Externally supervised release required')
        freeze()
    return p


def inputs(p,u,role):
    """Locate only sealed original learning; never copy or regenerate science."""
    unit=p['units'][u];root=Path(p['source_work'])/'units'/u
    return [unit['features'],root/(role+'-embed/embeddings.npz'),root/(role+'-graph/graph.npz'),unit['marker_evidence']]


def verify_inputs(p,output):
    """Rebind complete learning seals/used bytes, original full axes and information paths.

    Unused admitted view/token arrays receive a size/existence + original-seal
    check, not another multi-GB hash. They cannot be consumed by this grouping DAG.
    This is scoped cache verification, not whole-VM nonmutation.
    """
    actual_product=product_scope()
    from dl_binner.multiview.views import load
    from dl_binner.information.grouping import load_inputs
    from e027_learning_review import frozen_manifest_contract
    lock=json.loads((EXP/'reuse-lock.json').read_text());base=Path(p['source_work'])
    if str(base)!=lock['source_work']:raise ValueError('Original E027 work differs')
    cache={};hashed={};stat_only={}
    def check(path,wanted,hash_bytes=True):
        path=Path(path)
        if path.is_symlink() or not path.is_file() or path.stat().st_size!=wanted['bytes']:raise ValueError('Missing/changed reused member: '+str(path))
        if hash_bytes:
            st=path.stat();key=(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)
            if key not in cache:cache[key]=binding(path)
            if cache[key]!=wanted:raise ValueError('Corrupt reused member: '+str(path))
            hashed[str(path)]=wanted
        else:stat_only[str(path)]=wanted
    for i,(name,wanted) in enumerate(lock['all_closed_stage_members'].items()):
        unused='/admit/' in name and (name.endswith('.npy') or name.endswith('views.npz'))
        check(base/name,wanted,not unused)
        if i%30==0:print('E028_REUSE_PROGRESS',i,len(lock['all_closed_stage_members']),flush=True)
    for name,wanted in lock['external_files'].items():check(name,wanted)
    protocol=json.loads((EXP/'protocol.json').read_text());axes={}
    for u in UNITS:
        unit=p['units'][u];data,meta=load(unit['features']);axis=protocol['axes'][u]
        if (len(data['ids'])!=axis['rows'] or int(data['lengths'].sum())!=axis['bp'] or
            int(data['eligible'].sum())!=axis['eligible'] or meta['samples']!=axis['samples']):raise ValueError('Full contig/ordered depth axis differs')
        root=base/'units'/u
        for name in ['admit','teacher','teacher-embed','teacher-graph','pairs','student','student-embed','student-graph']:
            done=json.loads((root/name/'done.json').read_text())
            expected={k.removeprefix('units/'+u+'/'+name+'/'):v for k,v in lock['all_closed_stage_members'].items() if k.startswith('units/'+u+'/'+name+'/') and not k.endswith('/done.json')}
            if done['status']!='PASS' or done['files']!=expected:raise ValueError('Completed learning seal differs')
        bank=binding(Path(unit['frozen'])/'bank.json')['sha256'] if unit['frozen'] else None
        pair=json.loads((root/'pairs/cache/cache.json').read_text())
        if pair['inputs']['embeddings']!=binding(root/'teacher-embed/embeddings.npz') or pair['inputs']['graph']!=binding(root/'teacher-graph/graph.npz'):raise ValueError('Own-teacher pair availability differs')
        for role in ['teacher','student']:
            model=json.loads((root/role/'checkpoint.json').read_text());emb=json.loads((root/(role+'-embed/embeddings.json')).read_text())
            frozen_manifest_contract(model,bank)
            if len(model['history'])!=20 or model['config']['seed']!=11 or model['samples']!=axis['samples'] or emb['reload_exact'] is not True or emb['checkpoint_sha256']!=binding(root/role/'checkpoint.pt')['sha256']:raise ValueError('Native frozen schedule/reload differs')
            if binding(root/role/'reference.npz')!=binding(root/(role+'-embed/embeddings.npz')):raise ValueError('Original reload vector bytes differ')
            load_inputs(unit['features'],root/(role+'-embed/embeddings.npz'))
        axes[u]=dict(axis,GLM_in_teacher_proposals_student=bool(unit['frozen']))
    result=dict(status='PASS',actual_installed_product=actual_product,hashed=hashed,unused_admitted_arrays_stat_only=stat_only,axes=axes,
        source_work=str(base),scientific_fits_run=0,learning_graphs_rebuilt=0,markers_redetected=0)
    write(output,result);return result


def stage(path,name,u=None,role=None,engineering=False):
    """Execute one recorded stage with an explicit six-cache barrier and strict resume."""
    product_scope()
    p=read_plan(path,engineering);work=Path(p['work'])
    target=work/(('retrieval/'+u+'/'+role) if name=='retrieve' else ('groups/'+u+'/'+role) if name=='group' else u+'/'+name if u else name)
    if (target/'done.json').exists():verify_seal(target);return
    target=fresh(target.parent,target.name)
    if name=='retrieve':
        from dl_binner.discovery.grouping import prepare
        a=inputs(p,u,role);prepare(*a[:3],target/'cache')
    elif name=='barrier':
        records={}
        for unit,r in COMPONENTS:
            cache=work/'retrieval'/unit/r;verify_seal(cache)
            from dl_binner.discovery.grouping import restore
            a=inputs(p,unit,r);records[unit+'-'+r]=restore(*a[:3],cache/'cache')[1]
        write(target/'proof.json',dict(status='PASS',all_six_retrievals_passed=True,caches=records,biological_selection_started=False))
    elif name=='group':
        verify_seal(work/'barrier')
        from dl_binner.discovery.grouping import run
        run(*inputs(p,u,role),work/'retrieval'/u/role/'cache',target/'result')
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
        from dl_binner.discovery.grouping import audit
        verify_seal(work/u/'export')
        proof={r:audit(*inputs(p,u,r),work/'groups'/u/r/'result') for r in ['teacher','student']}
        write(target/'proof.json',dict(status='PASS',learners=proof,learning_unchanged=True))
    else:raise ValueError('No training or unknown E028 stage supported')
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
