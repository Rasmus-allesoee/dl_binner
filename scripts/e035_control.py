#!/usr/bin/env python3
"""Serial E035 taxonomy worker; old encoder, markers and truth are read-only.

Every scientific stage is independently sealed and runs in an isolated process.
The operator releases one frozen plan only after the independent annotation utility and
complete-schedule gates. There is no mapping, detector or old-encoder fit here.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

# Pin the installed product before legacy helpers can expose the checkout path.
import dl_binner as _owned_product

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e024_control import fresh,seal,verify_seal

EXP=ROOT/'experiments/E035-confidence-taxonomy'
UNITS=['E009-noGLM','E009-GLM','oral-noGLM']
STAGES=['view-cache','student','student-embed','student-graph','retrieve','forest','construct','e023','select','audit']


def product_scope():
    """Require the actual new owned wheel, never a checkout or borrowed old product."""
    sys.path[:]=[s for s in sys.path if Path(s).absolute()!=ROOT/'src']
    import dl_binner
    if dl_binner.__version__!='0.1.0.dev11' or not Path(dl_binner.__file__).is_relative_to(Path(sys.prefix)):
        raise ValueError('Owned installed E035 package required')


def freeze():
    """Admit exact scientific/source/default bytes before a native consumer."""
    lock=json.loads((EXP/'source-lock.json').read_text())
    for name,b in lock['files'].items():
        if binding(ROOT/name)!=b:raise ValueError('Frozen E035 source differs: '+name)
    return binding(EXP/'source-lock.json')


def read_plan(path,engineering=False):
    """Require the actual producer/consumer schema, complete modes and held release."""
    p=json.loads(Path(path).read_text());fields={'kind','engineering','work','units','python','workflow_python','worker','snakefile','limits'}
    if set(p)!=fields or p['kind']!='E035 confidence taxonomy' or p['engineering']is not engineering or set(p['units'])!=set(UNITS):
        raise ValueError('Unknown/incomplete E035 plan')
    if any(set(p['units'][u])!={'features','views','tokens','frozen','checkpoint','embeddings','annotations','fasta','marker_evidence','community'} for u in UNITS):raise ValueError('Unknown E035 unit input schema')
    if not engineering:
        freeze();release=os.environ.get('E035_RELEASE_FILE')
        if not release or json.loads(Path(release).read_text())['plan']!=binding(path):raise ValueError('Externally supervised E035 release required')
        if p['limits']!=json.loads((EXP/'limits.json').read_text()):raise ValueError('Unfrozen E035 resource envelope')
    return p


def inputs(p,u):
    """Bind all actual mode ancestry, new classifier annotations and frozen E031 state."""
    e=p['units'][u]
    files={k:binding(e[k]) for k in ['features','views','checkpoint','embeddings','fasta','marker_evidence']}
    files.update(annotations=binding(Path(e['annotations'])/'completed.json'),
                 tokens=binding(Path(e['tokens'])/'tokens.json'),
                 frozen=binding(Path(e['frozen'])/'bank.json') if e['frozen'] else None)
    return dict(unit=e,source=binding(EXP/'source-lock.json') if not p['engineering'] else None,files=files)


def verify_inputs(p):
    """Validate classifier/source/full axes and common declared availability modes."""
    product_scope()
    from dl_binner.multiview.views import load
    from dl_binner.taxonomy.annotations import read
    from dl_binner.multiview.arrays import load_arrays
    import numpy as np
    result={};trees=[]
    reuse=json.loads((ROOT/'experiments/E033-multiscale-bam/reuse-lock.json').read_text())
    for u in UNITS:
        e=p['units'][u];d,m=load(e['features']);a,am,t=read(e['annotations'],e['features']);b,bm=load_arrays(e['embeddings'],'embeddings')
        if bool(e['frozen']) != (u=='E009-GLM') or not np.array_equal(d['ids'],b['ids']):raise ValueError('Full GLM/mode/parent-vector contract differs')
        if am['provenance']['synthetic_reference'] is not p['engineering']:raise ValueError('Synthetic annotations cannot admit community fits')
        axis=dict(rows=len(d['ids']),eligible=int(d['eligible'].sum()),bp=int(d['lengths'].sum()),samples=m['samples'])
        if not p['engineering'] and axis!=reuse['axes'][u]:raise ValueError('Frozen complete contig/sample axes differ')
        if not p['engineering']:
            state=reuse['E031_states'][u]
            if binding(e['checkpoint'])!=state['checkpoint'] or binding(Path(e['checkpoint']).with_suffix('.json'))!=state['metadata']:
                raise ValueError('Accepted E031 teacher/proposal/student ancestry differs')
            retained=json.loads((EXP/'retained-output-lock.json').read_text())[u]
            if binding(e['embeddings'])!=retained['embed/embeddings.npz'] or binding(Path(e['embeddings']).with_suffix('.json'))!=retained['embed/embeddings.json']:
                raise ValueError('Accepted E031 vector/native output binding differs')
        if p['engineering'] and axis['rows']>128:raise ValueError('Engineering population exceeds tiny scope')
        if not p['engineering']:
            annotated=d['eligible'] & (a['confidence']>0)
            fraction=int(d['lengths'][annotated].sum())/int(d['lengths'][d['eligible']].sum())
            if not annotated.any():raise ValueError('NO_NEW_TAXONOMY_INFORMATION: close an exact reference-only null before any fit; retain all annotations')
            axis['annotation_yield']=dict(contigs=int(annotated.sum()),eligible_bp_fraction=fraction)
        trees.append(am['tree']);result[u]=axis
    if any(t!=trees[0] for t in trees):raise ValueError('Taxonomy tree/database policy differs across modes')
    return dict(status='PASS',axes=result,old_learning_refit=False,truth_accessed=False)


def stage(path,name,u=None,engineering=False):
    """Run a fresh scientific target or verify its sealed exact no-op resume."""
    product_scope();p=read_plan(path,engineering);work=Path(p['work'])
    if name=='barrier':u=UNITS[0];target=work/'barrier'
    elif name in STAGES and u in UNITS:target=work/u/name
    else:raise ValueError('Unknown E035 stage/mode')
    expected=inputs(p,u)
    if (target/'done.json').is_file():
        old=verify_seal(target)
        if old['inputs']!=expected:raise ValueError('E035 sealed input drift; no replay')
        return old
    target=fresh(target.parent,target.name)
    if name=='barrier':write(target/'proof.json',verify_inputs(p))
    else:
        verify_seal(work/'barrier');at=STAGES.index(name);root=work/u;e=p['units'][u];features=e['features']
        if at:verify_seal(root/STAGES[at-1])
        emb=root/'student-embed/embeddings.npz';graph=root/'student-graph/result/graph.npz'
        if name=='view-cache':
            from dl_binner.taxonomy.cache import prepare
            prepare(features,e['views'],e['tokens'],e['frozen'],e['checkpoint'],e['embeddings'],e['annotations'],target/'result',4)
        elif name=='student':
            from dl_binner.taxonomy.model import train
            train(features,e['views'],root/'view-cache/result',e['annotations'],target/'result',4)
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
    # Snakemake caches local source by URI. A mutable source URI can otherwise
    # reuse an old Snakefile after a recorded repair; retain each cache by bytes.
    cache=work.parent/('workflow-source-cache-'+binding(p['snakefile'])['sha256'][:16])
    memory=int(p['limits'].get('RSS_bytes',26_000_000_000)/1_000_000)
    argv=[p['workflow_python'],'-I','-B','-m','snakemake','--snakefile',p['snakefile'],'--directory',str(work),'--cores','4','--resources','mem_mb='+str(memory),'--benchmark-extended','--runtime-source-cache-path',str(cache),'--rerun-triggers','mtime','--config','plan='+str(Path(path).absolute()),'engineering='+str(engineering).lower()]
    if dry:argv+=['--dry-run']
    subprocess.run(argv,check=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True,type=Path);p.add_argument('--engineering',action='store_true');p.add_argument('--workflow',action='store_true');p.add_argument('--dry-run',action='store_true');p.add_argument('--stage',choices=['barrier']+STAGES);p.add_argument('--unit',choices=UNITS);a=p.parse_args()
    if a.workflow:workflow(a.plan,a.engineering,a.dry_run)
    elif a.stage:stage(a.plan,a.stage,a.unit,a.engineering)
    else:p.error('Choose a serial workflow or one explicit stage')
