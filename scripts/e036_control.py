#!/usr/bin/env python3
"""Serial graph-only E036 worker; old learning/moments and truth are read-only.

Every scientific stage is independently sealed and runs in an isolated process.
The operator releases one frozen plan only after the native template utility and
complete-schedule gates. There is no mapping, detector or old-encoder fit here.
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

EXP=ROOT/'experiments/E036-optional-pooled-links'
UNITS=['E009-noGLM','E009-GLM','oral-noGLM']
STAGES=['node-features','student','student-embed','student-graph','retrieve','forest','construct','e023','select','audit']


def product_scope():
    """Require the actual new owned wheel, never a checkout or borrowed old product."""
    sys.path[:]=[s for s in sys.path if Path(s).absolute()!=ROOT/'src']
    import dl_binner
    if dl_binner.__version__!='0.1.0.dev11' or not Path(dl_binner.__file__).is_relative_to(Path(sys.prefix)):
        raise ValueError('Owned installed E036 package required')


def freeze():
    """Admit exact scientific/source/default bytes before a native consumer."""
    from e036_repair import admit
    return admit()


def read_plan(path,engineering=False,held=False):
    """Require the actual producer/consumer schema, complete modes and held release."""
    p=json.loads(Path(path).read_text());fields={'kind','engineering','work','source_cache','measurement_cache','physical','units','python','workflow_python','worker','snakefile','limits','baseline_cache','optional_policy'}
    if set(p)!=fields or p['kind']!='E036 optional pooled graph' or p['engineering']is not engineering or set(p['units'])!=set(UNITS):
        raise ValueError('Unknown/incomplete E036 plan')
    if any(set(p['units'][u])!={'features','views','fasta','marker_evidence','community'} for u in UNITS):raise ValueError('Unknown E036 unit input schema')
    if set(p['measurement_cache'])!={'E009','oral'} or set(p['physical'])!={'E009','oral'}:raise ValueError('Missing community cache')
    if not engineering:
        if p['optional_policy']!=json.loads((EXP/'runtime-plan.json').read_text())['optional_policy']:raise ValueError('Unfrozen optional availability rule')
        phase=Path(p['work']).parent.parent
        if phase.parent!=Path('/srv/dl_binner/experiments/e036') or not phase.name.startswith('optional-'):raise ValueError('Phase-owned E036 work required')
        schema=json.loads((EXP/'runtime-plan.json').read_text().replace('NEW_PHASE',phase.name))
        if p!=schema:raise ValueError('Exact frozen complete native plan differs')
        freeze();release=os.environ.get('E036_RELEASE_FILE')
        if not held and (not release or json.loads(Path(release).read_text())['plan']!=binding(path)):raise ValueError('Externally supervised E036 release required')
        if p['limits']!=json.loads((EXP/'limits.json').read_text()):raise ValueError('Unfrozen E036 resource envelope')
    return p


def inputs(p,u):
    """Bind the complete new plan and every consumed accepted cache receipt."""
    e=p['units'][u];original=Path(p['source_cache'])/'work'/u
    return dict(unit=e,source=(binding(EXP/'source-lock.json') if not p['engineering'] else None),
        original_vectors=binding(original/'embed/embeddings.npz'),original_graph=binding(original/'graph/result/graph.npz'),
        physical=binding(Path(p['physical'][e['community']])/'completed.json'),
        measured=(binding(Path(p['measurement_cache'][e['community']])/'bank.json') if available(p,u) else None))


def verify_inputs(p):
    """Independently read source-bound full axes and assembly-specific pooled utility."""
    product_scope();from dl_binner.multiview.views import load
    from dl_binner.multiview.arrays import load_arrays
    from dl_binner.genomegraph.links import read
    reuse=json.loads((ROOT/'experiments/E033-multiscale-bam/reuse-lock.json').read_text());result={}
    for u in UNITS:
        e=p['units'][u];d,m=load(e['features']);original=Path(p['source_cache'])/'work'/u
        a,am=load_arrays(original/'embed/embeddings.npz','embeddings');g,gm=load_arrays(original/'graph/result/graph.npz','candidate_sparse_graph');links,lm=read(p['physical'][e['community']])
        axis=dict(rows=len(d['ids']),eligible=int(d['eligible'].sum()),bp=int(d['lengths'].sum()),samples=m['samples'])
        if not p['engineering'] and (axis!=reuse['axes'][u] or lm['samples']!=m['samples'] ):
            raise ValueError('Full frozen axes/complete physical utility admission missing')
        if p['engineering'] and axis['rows']>128:raise ValueError('Engineering population exceeds tiny scope')
        if am['features_sha256']!=binding(e['features'])['sha256'] or gm['embedding_sha256']!=binding(original/'embed/embeddings.npz')['sha256']:
            raise ValueError('Original E031 vector/graph/source feature binding differs')
        from dl_binner.genomegraph.links import utility
        if lm['utility']!=utility(links['edges'],links['ids'],links['lengths'],links['eligible'],pilot=lm['utility']['pilot']):raise ValueError('Pooled utility differs from actual graph')
        if not p['engineering'] and lm['utility']['pilot']:raise ValueError('Community graph requires complete pooled utility, not a pilot')
        if lm.get('decisions') is not None and binding(Path(p['physical'][e['community']])/'decisions.json')!=lm['decisions']:raise ValueError('Pooled decisions companion differs')
        result[u]=dict(axis=axis,available=available(p,u))
    return dict(status='PASS',axes=result,old_learning_refit=False,truth_accessed=False)


def available(p,u):
    """Apply one label-free availability rule, without changing the old utility gate."""
    from dl_binner.genomegraph.links import read
    a,m=read(p['physical'][p['units'][u]['community']])
    if p['engineering']:
        if len(a['ids'])>128:raise ValueError('Engineering availability override exceeds tiny scope')
        return bool(len(a['edges']) and (a['eligible'][a['edges']].all(1)).any())
    return m['utility']['status']=='PASS'


def fallback(p,u,name,target):
    """Reuse exact admitted no-link geometry and partitions; never refit/rescore them."""
    from dl_binner.multiview.views import load
    from dl_binner.information.export import validate_partition
    src=Path(p['source_cache'])/'work'/u;baseline=Path(p['baseline_cache'])/'work'/u
    def linktree(source,dest):
        for f in source.rglob('*'):
            if f.is_symlink():raise ValueError('Fallback source symlink refused')
            if f.is_file():
                q=dest/f.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);os.link(f,q)
    if name=='student-embed':
        for n in ['embeddings.npz','embeddings.json']:os.link(src/'embed'/n,target/n)
    elif name=='student-graph':linktree(src/'graph/result',target/'result')
    elif name=='select':
        d,m=load(p['units'][u]['features'])
        proof=json.loads((baseline/'audit/proof.json').read_text());meta=json.loads((baseline/'select/result/completed.json').read_text())
        if proof['status']!='PASS' or meta['status']!='SUCCESS' or meta['truth_accessed']is not False:raise ValueError('Accepted fallback output not complete')
        for v in [p['units'][u]['features'],str(src/'embed/embeddings.npz'),str(src/'graph/result/graph.npz')]:
            if binding(v) not in meta['inputs'].values():raise ValueError('Fallback original feature/vector/graph binding differs')
        for arm in ['pre','post']:validate_partition(d,baseline/'select/result'/(arm+'-partition.json'),p['units'][u]['features'])
        for n,b in meta['files'].items():
            if binding(baseline/'select/result'/n)!=b:raise ValueError('Fallback member bytes differ')
        linktree(baseline/'select/result',target/'result')
    elif name=='audit':
        original=baseline/'audit/proof.json';os.link(original,target/'proof.json')
        old=baseline/'select/result';new=target.parent/'select/result'
        for f in old.rglob('*'):
            if f.is_file() and binding(new/f.relative_to(old))!=binding(f):raise ValueError('Exact fallback construction changed')
    write(target/'fallback.json',dict(status='EXACT_ACCEPTED_FALLBACK',unit=u,stage=name,availability_rule=p['optional_policy'],old_science_replayed=False,truth_accessed=False,original_vectors=binding(src/'embed/embeddings.npz'),original_graph=binding(src/'graph/result/graph.npz')))


def stage(path,name,u=None,engineering=False):
    """Run a fresh scientific target or verify its sealed exact no-op resume."""
    product_scope();p=read_plan(path,engineering);work=Path(p['work'])
    if name=='barrier':u=UNITS[0];target=work/'barrier'
    elif name in STAGES and u in UNITS:target=work/u/name
    else:raise ValueError('Unknown E036 stage/mode')
    expected=inputs(p,u)
    if (target/'done.json').is_file():
        old=verify_seal(target)
        if old['inputs']!=expected:raise ValueError('E036 sealed input drift; no replay')
        return old
    target=fresh(target.parent,target.name)
    if name=='barrier':write(target/'proof.json',verify_inputs(p))
    else:
        verify_seal(work/'barrier');at=STAGES.index(name);root=work/u;e=p['units'][u];features=e['features']
        if at:verify_seal(root/STAGES[at-1])
        source=Path(p['source_cache'])/'work'/u;emb=root/'student-embed/embeddings.npz';graph=root/'student-graph/result/graph.npz'
        if not available(p,u):
            fallback(p,u,name,target)
        elif name=='node-features':
            from dl_binner.genomegraph.model import cache
            from dl_binner.multiscale.cache import Bank
            bank=Bank(p['measurement_cache'][e['community']],features,e['views'])
            cache(features,source/'embed/embeddings.npz',source/'graph/result/graph.npz',p['physical'][e['community']],bank,target/'result')
        elif name=='student':
            from dl_binner.genomegraph.model import train
            train(root/'node-features/result/features.npz',target/'result',4,engineering_epochs=20 if engineering else None)
        elif name=='student-embed':
            for suffix in ['.npz','.json']:os.link(root/'student/result'/('embeddings'+suffix),target/('embeddings'+suffix))
            write(target/'reload-proof.json',dict(source=binding(root/'student/result/completed.json'),no_new_inference=True))
        elif name=='student-graph':
            from dl_binner.unified.graph import prepare
            from dl_binner.unified.training import configuration
            prepare(features,emb,target/'result',configuration(u=='E009-GLM'))
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
            from e033_control import constructor_cache
            from dl_binner.selection.grouping import run
            cached=constructor_cache(root,target/'input-cache');run(features,emb,graph,e['marker_evidence'],cached,e['fasta'],target/'result')
        else:
            from e033_control import verify_constructor_cache
            from dl_binner.selection.grouping import audit
            cached=root/'select/input-cache/work'/u;verify_constructor_cache(root,cached)
            write(target/'proof.json',audit(features,emb,graph,e['marker_evidence'],cached,root/'select/result'))
    return seal(target,dict(inputs=expected))


def workflow(path,engineering=False,dry=False):
    """Execute one strictly serial four-thread DAG; no competing --jobs option."""
    product_scope();p=read_plan(path,engineering);work=Path(p['work']);work.mkdir(parents=True,exist_ok=True)
    for done in work.rglob('done.json'):verify_seal(done.parent)
    from e036_dispatch import verify_existing
    verify_existing(p)
    # Snakemake caches local source by URI. A mutable source URI can otherwise
    # reuse an old Snakefile after a recorded repair; retain each cache by bytes.
    cache=work.parent/('workflow-source-cache-'+binding(p['snakefile'])['sha256'][:16])
    argv=[p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],'--directory',str(work),'--cores','4','--resources','mem_mb=26000','--benchmark-extended','--runtime-source-cache-path',str(cache),'--rerun-triggers','mtime','--config','plan='+str(Path(path).absolute()),'engineering='+str(engineering).lower()]
    if dry:argv+=['--dry-run']
    subprocess.run(argv,check=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True,type=Path);p.add_argument('--engineering',action='store_true');p.add_argument('--workflow',action='store_true');p.add_argument('--dry-run',action='store_true');p.add_argument('--stage',choices=['barrier']+STAGES);p.add_argument('--unit',choices=UNITS);a=p.parse_args()
    if a.workflow:workflow(a.plan,a.engineering,a.dry_run)
    elif a.stage:stage(a.plan,a.stage,a.unit,a.engineering)
    else:p.error('Choose a serial workflow or one explicit stage')
