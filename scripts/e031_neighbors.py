#!/usr/bin/env python3
"""Describe the frozen matched E031 query views without search or model inference.

The same source-blind queries and k=5 denominator compare contextual E023 and
unchanged learned candidates. Unknown neighbors remain in the denominator;
unknown queries remain in explicit population accounting. These samples are not
whole-community biological quality or exact composite retrieval-recall proofs.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def evaluate_queries(queries, labels, lineage, targets):
    """Account all queries and compare the same known-origin neighbors by strata."""
    cells=defaultdict(lambda:dict(queries=0,bp=0,known_queries=0,known_bp=0,
        E023_same_weighted_sum=0.,native_same_weighted_sum=0.,E023_unknown=0,native_unknown=0))
    rows=[]
    for q in queries:
        g=labels[q['id']];n=q['length']
        low=max(x for x in [0,500,768,1000,2500,10000] if n>=x)
        origin='unknown' if g is None else 'target' if g in targets else 'non_target'
        key='|'.join([str(low),origin,lineage.get(g,'unresolved'),
                      'depth_positive' if q['depth_positive'] else 'measured_all_zero'])
        cell=cells[key];cell['queries']+=1;cell['bp']+=n
        result=dict(id=q['id'],length=n,origin=origin,lineage=lineage.get(g,'unresolved'),
                    frozen_query_strata=q['strata'],known_query=g is not None)
        if g is not None:cell['known_queries']+=1;cell['known_bp']+=n
        for mode,field in [('E023','E023_neighbors'),('native','native_neighbors')]:
            near=q[field][:5]
            if len(near)!=5 or len(set(near))!=5 or q['id'] in near or any(i not in labels for i in near):
                raise ValueError('Matched cached five-neighbor ID contract differs')
            unknown=sum(labels[i] is None for i in near)
            same=sum(labels[i]==g for i in near) if g is not None else None
            result[mode]=dict(same=same,unknown=unknown,k=5)
            if g is not None:
                cell[mode+'_same_weighted_sum']+=n*same/5
                cell[mode+'_unknown']+=unknown
        rows.append(result)
    for cell in cells.values():
        for mode in ['E023','native']:
            cell[mode+'_same_origin_bp_weighted']=(cell[mode+'_same_weighted_sum']/cell['known_bp'] if cell['known_bp'] else None)
    known_bp=sum(c['known_bp'] for c in cells.values())
    aggregate={m:sum(c[m+'_same_weighted_sum'] for c in cells.values())/known_bp if known_bp else None for m in ['E023','native']}
    return dict(all_queries=len(rows),all_query_bp=sum(q['length']for q in queries),known_query_bp=known_bp,
        same_origin_bp_weighted=aggregate,cells=dict(cells),queries=rows,
        scope='Same frozen query IDs; k=5 including unknown neighbors; known-query label semantics only')


def review(bridge, plan, truth_root, output):
    """Evaluate compact new query caches and add complete E009 measured-zero strata."""
    import numpy as np
    from dl_binner.multiview.views import load
    from e014_review import oral_labels
    from e025_review import coverage_populations
    bridge=Path(bridge);plan=json.loads(Path(plan).read_text());actors={};coverage={}
    lock=json.loads((ROOT/'experiments/E013-marker-quality/review-lock.json').read_text())
    truth=json.loads((ROOT/lock['truth_root']/'truth.json').read_text())
    targets=json.loads((ROOT/lock['truth_root']/'targets.json').read_text())
    pop=json.loads((ROOT/lock['population_path']).read_text())
    labels={q:c['AMBER_label']for q,c in truth['contigs'].items()}
    lineages={g:v['lineage_class']for g,v in pop['genomes'].items()}
    genomes=sorted({g for g in labels.values()if g is not None});index={g:i for i,g in enumerate(genomes)}
    clean=set(json.loads((ROOT/'artifacts/e011-cached-grouping-reference/restore-local/candidate/markers/evidence.json').read_text())['clean'])
    data,_=load(plan['units']['E009-noGLM']['features']);lab=np.asarray([index.get(labels[q],-1)for q in data['ids']],np.int64)
    for unit in ['E009-noGLM','E009-GLM']:
        for role in ['teacher','student']:
            if (unit,role)==('E009-GLM','student'):continue
            at=bridge/'work/actors'/unit/role
            actors[unit+'/'+role]=evaluate_queries(json.loads((at/'query-neighbors.json').read_text())['queries'],labels,lineages,targets['targets'])
            coverage[unit+'/'+role]={arm:coverage_populations(data,json.loads((at/'science/result'/(arm+'-partition.json')).read_text()),
                lab,genomes,targets['targets'],clean)for arm in ['density','selected']}
    del data,lab,truth,labels
    data,_=load(plan['units']['oral-noGLM']['features'])
    lab,_,_,genomes,truth=oral_labels(truth_root,data['ids'].tolist(),data['lengths'])
    labels={q:genomes[int(g)]if g>=0 else None for q,g in zip(data['ids'].tolist(),lab)}
    for role in ['teacher','student']:
        at=bridge/'work/actors/oral-noGLM'/role
        actors['oral-noGLM/'+role]=evaluate_queries(json.loads((at/'query-neighbors.json').read_text())['queries'],labels,{},truth['targets'])
    write(output,dict(status='PASS',actors=actors,E009_full_population_measured_depth=coverage,
        original_query_axes=binding(ROOT/'experiments/E031-bootstrap-preserving-learning/query-axes.json'),
        old_baselines_rescored=False,search_or_inference_performed=False,original_Mac_tolerance_unchanged=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['bridge','plan','truth-root','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();review(a.bridge,a.plan,a.truth_root,a.output)
