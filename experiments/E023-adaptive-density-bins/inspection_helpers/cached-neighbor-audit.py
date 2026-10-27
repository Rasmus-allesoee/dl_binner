"""Matched-population diagnostic of already retained composite-neighbor arrays.

No neighbor search, graph rebuild, partition or model change. All native eligible
queries are retained; unknown query labels are reported separately and unknown
neighbors never count as same source. Origin labels are evaluation-only.
"""
from pathlib import Path
import json,sys,numpy as np
repo=Path.cwd();sys.path[:0]=[str(repo/'scripts'),str(repo/'src')]
from e014_collect import binding
from e014_review import oral_labels
r=Path(Path('artifacts/e023-inspection/current-root.txt').read_text().strip());results={}
for unit in ['E009-E022','oral-E019']:
 p=r/'verified/work/units'/unit/'group/hierarchy.npz'
 with np.load(p,allow_pickle=False)as a:ids=a['ids'];selected=a['selected'];nn=a['neighbors'][:,:5]
 require=lambda c:None if c else(_ for _ in()).throw(ValueError('Cached neighbor diagnostic axis differs'))
 if unit=='E009-E022':
  t=json.loads((repo/'artifacts/e009-truth-v2/20261015/attempt-local-v2/truth-v2/truth.json').read_text());pop=json.loads((repo/'experiments/E009-competitive-benchmark/truth-population-review.json').read_text());names=sorted({x['AMBER_label']for x in t['contigs'].values()if x['AMBER_label']is not None});codes={q:i for i,q in enumerate(names)}
  labels=np.array([codes.get(t['contigs'][str(q)]['AMBER_label'],-1)for q in ids]);lengths=np.array([t['contigs'][str(q)]['length']for q in ids]);cohort=np.array([pop['genomes'][t['contigs'][str(q)]['AMBER_label']]['lineage_class']if t['contigs'][str(q)]['AMBER_label']else'unknown'for q in ids]);base=json.loads((repo/'experiments/E022-marker-informed-learning/comparison-review.json').read_text())['arms']['post']['diagnostics'];old=base['geometry'];expected=old['attributable_eligible_queries'];del t,pop
 else:
  f=repo/'artifacts/e014-multiview-reconstruction/inspection-20261019/verified/work/units/oral-dev5/features/features.npz'
  with np.load(f,allow_pickle=False)as a:lengths=a['lengths'];require(np.array_equal(a['ids'],ids))
  labels,quarantine,shared,names,_=oral_labels(repo/'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1',ids.tolist(),lengths);cohort=np.where(labels>=0,'provided_origin','unknown');old=json.loads((repo/'experiments/E019-window-context/comparison-review.json').read_text())['units']['oral-context']['arms']['post']['geometry'];expected=old['queries']
 qlabels=labels[selected];qlengths=lengths[selected];same=(labels[selected[nn]]==qlabels[:,None])&(qlabels[:,None]>=0);known=qlabels>=0;require(int(known.sum())==expected)
 def summary(mask):
  n=int(mask.sum());bp=int(qlengths[mask].sum());total=int(same[mask].sum());weighted=float((same[mask].sum(1)*qlengths[mask]).sum()/5)
  return dict(queries=n,query_bp=bp,nn_purity=total/(5*n)if n else None,nn_purity_bp_weighted=weighted/bp if bp else None)
 by_length={str(low):summary(known&(qlengths>=low)&(qlengths<hi))for low,hi in [(500,768),(768,1000),(1000,2500),(2500,10000),(10000,np.inf)]}
 result=dict(new_composite=summary(known),preserved_native_5NN=old,by_length=by_length,by_origin={str(c):summary(known&(cohort[selected]==c))for c in np.unique(cohort[selected])},unattributed_eligible_queries=int((~known).sum()),array=binding(p),same_query_population_verified=True,scope='First five cached composite-distance neighbors versus preserved native learned 5-NN summaries. No retrieval rebuild or score-selected rule; oral remains provided-origin, not unique identity.')
 if unit=='E009-E022':
  result['preserved_native_by_lineage']=base['geometry_by_lineage']
  for c,z in result['by_origin'].items():
   if c in base['geometry_by_lineage']:require(z['queries']==base['geometry_by_lineage'][c]['queries'])
 else:
  for low,z in by_length.items():require(z['queries']==old['length_strata'][low]['queries']and z['query_bp']==old['length_strata'][low]['query_bp'])
 results[unit]=result;print(unit,json.dumps(dict(new=result['new_composite'],old={k:z for k,z in old.items()if k!='length_strata'},by_length=by_length)),flush=True)
 del ids,selected,nn,labels,lengths,same,cohort
(r/'cached-neighbor-diagnostic.json').write_text(json.dumps(results,indent=2)+'\n')
