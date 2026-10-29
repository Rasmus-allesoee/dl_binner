"""Descriptive decomposition of the already accepted new cached 5NN edges.

No search, fit, bin selection, threshold change or old-output rescore. These are
additive strata of the frozen global neighbor diagnostic, including measured
zero/positive endpoint combinations. Origin labels remain evaluation-only.
"""
from pathlib import Path
import json,sys,time
repo=Path.cwd();sys.path[:0]=[str(repo/'scripts'),str(repo/'src')]
import numpy as np
from dl_binner.multiview.arrays import load_arrays
from e014_review import oral_labels
out=repo/'artifacts/e025-inspection/20261028T232534Z'
data,_=load_arrays(repo/'artifacts/e024-inspection/20261028T193107Z/verified/work/rebound/features.npz','features')
h,_=load_arrays(out/'verified/work/group/hierarchy.npz','E024_depth_hierarchy')
lab,_,_,genomes,truth=oral_labels(repo/'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1',data['ids'].tolist(),data['lengths'])
s=h['selected'];near=s[h['neighbors'][:,:5]];same=(lab[s,None]==lab[near])&(lab[s,None]>=0);purity=same.mean(1);length=data['lengths'][s];positive=(data['depth']>0).any(1);qpos=positive[s];npos=positive[near];clean=set(json.loads((repo/'artifacts/e014-multiview-reconstruction/inspection-20261019/oral-marker-review.json').read_text())['clean'])
rows=[]
for lower,upper in [(500,768),(768,1000),(1000,2500),(2500,10000),(10000,2**63-1)]:
 for name,mask in [('all',np.ones(len(s),bool)),('positive',qpos),('measured_all_zero',~qpos)]:
  keep=mask&(length>=lower)&(length<upper)&(lab[s]>=0);bp=int(length[keep].sum())
  rows.append(dict(lower_bp=lower,upper_bp=upper,depth=name,queries=int(keep.sum()),bp=bp,mean=float(purity[keep].mean()) if keep.any() else None,bp_weighted=float(np.dot(purity[keep],length[keep])/bp) if bp else None,cross_availability_edge_fraction=float((qpos[keep,None]!=npos[keep]).mean()) if keep.any() else None))
edge=[]
for a in [False,True]:
 for b in [False,True]:
  keep=(qpos[:,None]==a)&(npos==b);w=np.broadcast_to(length[:,None],keep.shape);bp=int(w[keep].sum())
  edge.append(dict(query_positive=a,neighbor_positive=b,edges=int(keep.sum()),query_bp_repeated_per_edge=bp,edge_same_origin=float(same[keep].mean()) if keep.any() else None,bp_weighted_same_origin=float(w[keep&same].sum()/bp) if bp else None))
known=lab[s]>=0;bp=int(length[known].sum());global_value=float(np.dot(purity[known],length[known])/bp)
assert global_value==json.loads((out/'diagnostics/review.json').read_text())['new_composite_neighbors']['same_origin_bp_weighted'] or abs(global_value-json.loads((out/'diagnostics/review.json').read_text())['new_composite_neighbors']['same_origin_bp_weighted'])<1e-12
result=dict(scope='Descriptive cached new 5NN edges; provided origin, not uniqueness; no candidate policy or old scoring change',full_DNA_bp=int(data['lengths'].sum()),known_queries=int(known.sum()),query_bp=bp,global_bp_weighted=global_value,length_depth_strata=rows,availability_edges=edge,all_target_queries=int(sum(genomes[int(g)] in truth['targets'] for g in lab[s] if g>=0)),unknown_queries=int((lab[s]<0).sum()),numeric_tolerance='Global agreement1e-12; original Mac portability unchanged')
(out/'neighbor-strata.json').write_text(json.dumps(result,indent=2)+'\n');print('ADDITIVE_NEIGHBOR_STRATA_PASS',global_value)
