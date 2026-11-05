#!/usr/bin/env python3
"""Prospective serial measurement/learning/construction worker; no cloud starts.

Native consumption requires an externally supervised, exact-source released plan.
Engineering mode admits only <=128 rows / 1 MB DNA and local tiny BAMs. Sealed
stages are verified before resume; an unsealed directory is retained and refused.
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
EXP=ROOT/'experiments/E033-multiscale-bam'
UNITS=['E009-noGLM','E009-GLM','oral-noGLM']
STAGES=['teacher','teacher-embed','teacher-graph','pairs','student','student-embed','student-graph',
        'retrieve','forest','construct','e023','select','audit']


def product_scope():
    """Require the owned installed candidate, never a checkout src overlay."""
    sys.path[:]=[p for p in sys.path if Path(p).absolute()!=ROOT/'src']
    import dl_binner
    if not Path(dl_binner.__file__).is_relative_to(Path(sys.prefix)):
        raise ValueError('Owned installed E033 package required')


def read_plan(path,engineering=False):
    """Refuse hidden inputs, source drift, incomplete measurement or loose release."""
    p=json.loads(Path(path).read_text())
    fields={'kind','engineering','work','units','measurements','python','workflow_python','worker','snakefile','limits'}
    if 'recovery' in p:fields.add('recovery')
    if set(p)!=fields or p['kind']!='E033 common multiscale BAM information' or p['engineering'] is not engineering or list(p['units'])!=UNITS:
        raise ValueError('Unknown E033 plan/schema/ordered modes')
    expected={'features','views','fasta','tokens','frozen','original','marker_cache','hmm','marker_evidence','community'}
    if any(set(e)!=expected for e in p['units'].values()) or set(p['measurements'])!={'E009','oral'}:
        raise ValueError('Unknown scientific input or hidden truth field')
    if not engineering:
        relative=Path(p['work']).relative_to('/srv/dl_binner/experiments/e033').parent
        if len(relative.parts) not in [1,2] or (len(relative.parts)==2 and relative.parts[-1]!='task') or not all(c.isalnum() or c=='-' for c in relative.parts[0]):
            raise ValueError('Fresh phase-owned E033 work required')
        schema=json.loads((EXP/'runtime-plan.json').read_text().replace('NEW_PHASE',str(relative)))
        repaired=None
        if 'recovery' in p:
            from e033_recovery import sources
            repaired=sources(p)
            schema['limits']=repaired[0]['limits']
        for key in ['kind','units','measurements','limits','workflow_python','worker','snakefile']:
            if p[key]!=schema[key]:raise ValueError('Unfrozen E033 '+key)
        effective=repaired[1] if repaired else json.loads((EXP/'source-lock.json').read_text())['files']
        for n,b in effective.items():
            if binding(ROOT/n)!=b:raise ValueError('Frozen E033 source drift: '+n)
        release=os.environ.get('E033_RELEASE_FILE')
        if not release or json.loads(Path(release).read_text()).get('plan')!=binding(path):
            raise ValueError('Externally verified current boot/process/provider/credit release required')
    return p


def inputs(p,u):
    """Bind the actual immutable manifests consumed by each independent unit."""
    e=p['units'][u];m=p['measurements'][e['community']]
    values={n:binding(e[n]) for n in ['features','views','fasta','original','marker_evidence','hmm']}
    values['tokens']=binding(Path(e['tokens'])/'tokens.json')
    values['marker_cache']=binding(Path(e['marker_cache'])/'cache.json')
    values['frozen']=binding(Path(e['frozen'])/'bank.json') if e['frozen'] else None
    values['measurement_bank']=binding(Path(m['bank'])/'bank.json');values['new_features']=binding(m['new_features'])
    return dict(unit=e,files=values)


def verify_inputs(p):
    """Verify exact old state/full axes and common newly measured DNA inputs."""
    from dl_binner.multiview.views import load
    from dl_binner.multiscale.cache import Bank
    results={}
    for u,e in p['units'].items():
        data,meta,v,_=load(e['features'],e['views']);m=p['measurements'][e['community']]
        bank=Bank(m['bank'],e['features'],e['views'],data,v)
        if not bank.meta['all_samples_measured']:raise ValueError('All ordered samples must be measured before fitting')
        if p['engineering']:
            if len(data['ids'])>128 or int(data['lengths'].sum())>1_000_000:raise ValueError('Engineering scope exceeds tiny DNA')
        else:
            axes=json.loads((EXP/'reuse-lock.json').read_text())['axes'][u]
            if dict(rows=len(data['ids']),bp=int(data['lengths'].sum()),eligible=int(data['eligible'].sum()),samples=meta['samples'])!=axes:
                raise ValueError('Full contig and ordered sample axis differs')
        results[u]=dict(rows=len(data['ids']),bp=int(data['lengths'].sum()),samples=meta['samples'],inputs=inputs(p,u))
    return dict(status='PASS',units=results,truth_accessed=False)


def constructor_cache(root,destination):
    """Bind freshly completed forests in E032's verified-cache reader layout.

    These are exact regular hardlinks to this E033 unit, not claimed E031 reuse.
    Original stage seals and every linked byte are verified before publishing the
    legacy reader's admission fields. No scientific result is recomputed here.
    """
    root=Path(root);destination=Path(destination);destination.mkdir(parents=True,exist_ok=False)
    parents=destination/'work';unit=parents/root.name;unit.mkdir(parents=True)
    members={};source_members={}
    for name in ['forest','construct','e023']:
        verify_seal(root/name)
        source=root/name/('science/result' if name=='e023' else 'result')
        for p in sorted(source.rglob('*')):
            if p.is_symlink():raise ValueError('Constructor source artifact links refused')
            if not p.is_file():continue
            n=str(p.relative_to(root));target=unit/n;target.parent.mkdir(parents=True,exist_ok=True)
            os.link(p,target);actual=binding(target)
            if actual!=binding(p):raise ValueError('Constructor hardlink bytes differ')
            members[n]=actual;source_members[str(p.absolute())]=actual
    write(parents/'restore-admission.json',dict(status='PASS',every_member_verified=True,omitted_work_members=0,
        kind='E033 freshly computed closed constructor-input cache, NOT historical E031 reuse',
        unit=root.name,members=members,original_source_members=source_members,no_scientific_stage_repeated=True))
    return unit


def verify_constructor_cache(root,unit):
    """Verify the legacy-layout adapter against its real new stage sources."""
    unit=Path(unit);r=json.loads((unit.parent/'restore-admission.json').read_text())
    if r['unit']!=Path(root).name or r['status']!='PASS':raise ValueError('Constructor cache unit differs')
    if any(binding(unit/n)!=b for n,b in r['members'].items()) or any(binding(n)!=b for n,b in r['original_source_members'].items()):
        raise ValueError('New constructor cache bytes changed')
    if {str(p.relative_to(unit)) for p in unit.rglob('*') if p.is_file()}!=set(r['members']):
        raise ValueError('Constructor cache member inventory differs')
    return r


def stage(path,name,u=None,engineering=False):
    """Execute one fresh stage or verify exact sealed no-op, without scientific retry."""
    product_scope();p=read_plan(path,engineering);work=Path(p['work'])
    if name=='barrier':u=UNITS[0];target=work/'barrier'
    elif u in UNITS and name in STAGES:target=work/u/name
    else:raise ValueError('Unknown E033 unit/stage')
    expected=inputs(p,u)
    if (target/'done.json').is_file():
        r=verify_seal(target)
        if r.get('inputs')!=expected:raise ValueError('Sealed stage input drift; no replay')
        return r
    target=fresh(target.parent,target.name)
    if name=='barrier':write(target/'proof.json',verify_inputs(p))
    else:
        verify_seal(work/'barrier');at=STAGES.index(name);root=work/u;e=p['units'][u]
        if at:verify_seal(root/STAGES[at-1])
        m=p['measurements'][e['community']];features=m['new_features']
        args=(e['features'],features,e['views'],e['tokens'],e['frozen'],m['bank'],e['original'])
        emb=root/'student-embed/embeddings.npz';graph=root/'student-graph/result/graph.npz'
        if name in ['teacher','student','teacher-embed','student-embed']:
            from dl_binner.multiscale import model
            if name=='teacher':model.train(*args,target/'result')
            elif name=='student':model.train(*args,target/'result',teacher=root/'teacher/result/checkpoint.pt',pairs=root/'pairs/result/cache')
            else:
                role=name.split('-')[0]
                model.embed(*args,root/role/'result/checkpoint.pt',target/'embeddings.npz',pairs=root/'pairs/result/cache' if role=='student' else None)
        elif name in ['teacher-graph','student-graph']:
            from dl_binner.unified.graph import prepare
            from dl_binner.unified.training import configuration
            role=name.split('-')[0];prepare(features,root/(role+'-embed/embeddings.npz'),target/'result',configuration(e['frozen'] is not None))
        elif name=='pairs':
            from dl_binner.multiscale.pairs import prepare
            prepare(features,e['features'],e['views'],m['bank'],root/'teacher-embed/embeddings.npz',root/'teacher-graph/result/graph.npz',e['marker_cache'],e['hmm'],target/'result')
        elif name in ['retrieve','forest']:
            from dl_binner.discovery import exact
            if name=='retrieve':exact.prepare(features,emb,graph,target/'result')
            else:exact.run(features,emb,graph,e['marker_evidence'],root/'retrieve/result',target/'result')
        elif name=='construct':
            from dl_binner.construction.grouping import run
            run(features,emb,graph,e['marker_evidence'],root/'forest/result',target/'result')
        elif name=='e023':
            from dl_binner.bootstrap.bridge import run
            run(features,emb,graph,e['marker_evidence'],e['fasta'],ROOT/'experiments/E023-adaptive-density-bins/config.json',ROOT/'experiments/E023-adaptive-density-bins/source-lock.json',target/'science',engineering=engineering)
        elif name=='select':
            from dl_binner.selection.grouping import run
            cached=constructor_cache(root,target/'input-cache')
            run(features,emb,graph,e['marker_evidence'],cached,e['fasta'],target/'result')
        else:
            from dl_binner.selection.grouping import audit
            cached=root/'select/input-cache/work'/u
            verify_constructor_cache(root,cached)
            write(target/'proof.json',audit(features,emb,graph,e['marker_evidence'],cached,root/'select/result'))
    return seal(target,dict(inputs=expected))


def workflow(path,engineering=False,dry=False):
    """Use the serial DAG with separate numerical workers and verified resume."""
    product_scope();p=read_plan(path,engineering);work=Path(p['work']);work.mkdir(exist_ok=True,parents=True)
    for d in work.rglob('done.json'):
        r=verify_seal(d.parent);u=next((x for x in UNITS if x in d.parts),UNITS[0])
        if r.get('inputs')!=inputs(p,u):raise ValueError('Resume source/input drift')
    argv=[p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],'--directory',str(work),
        '--cores','4','--resources','mem_mb=26000','--benchmark-extended','--runtime-source-cache-path',str(work.parent/('workflow-cache-'+work.name) if 'recovery' in p else work.parent/'workflow-cache'),
        '--rerun-triggers','mtime','--config','plan='+str(Path(path).absolute()),'engineering='+str(engineering).lower()]
    if dry:argv.append('--dry-run')
    subprocess.run(argv,check=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True,type=Path);p.add_argument('--engineering',action='store_true')
    p.add_argument('--workflow',action='store_true');p.add_argument('--dry-run',action='store_true');p.add_argument('--check-plan',action='store_true')
    p.add_argument('--stage',choices=['barrier']+STAGES);p.add_argument('--unit',choices=UNITS);a=p.parse_args()
    if a.check_plan:
        read_plan(a.plan,a.engineering);print('E033_PLAN_CONTRACT_PASS')
    elif a.workflow:workflow(a.plan,a.engineering,a.dry_run)
    elif a.stage:stage(a.plan,a.stage,a.unit,a.engineering)
    else:p.error('Choose stage/workflow')
