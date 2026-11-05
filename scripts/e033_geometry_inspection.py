#!/usr/bin/env python3
"""Read admitted E033 tensors and cached geometry; never infer, fit or build an index.

Reuses the frozen all-row sparse/unit-neighbor contracts and label-blind 128-query
raw-parent comparison. Truth diagnoses geometry/pairs only after independent byte,
exit and cost admission. It cannot select a bin, feature, threshold or model.
"""
import argparse
from collections import Counter,defaultdict
import gc
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def tensor_digest(state):
    """Hash actual serialized tensors/buffers with the native named-state contract."""
    h=hashlib.sha256()
    for name,value in state.items():
        x=value.detach().cpu().contiguous()
        h.update(json.dumps([name,str(x.dtype),list(x.shape)]).encode());h.update(x.numpy().tobytes())
    return h.hexdigest()


def inspect(base,unit,features,truth_root,output):
    """Independently check two checkpoints/graphs and diagnose fixed populations."""
    import numpy as np
    import torch
    from threadpoolctl import threadpool_limits
    from dl_binner.multiview.views import load
    from dl_binner.io import load_arrays
    from dl_binner.multiscale.model import read_candidate
    from dl_binner.multiscale.pairs import read as read_pairs
    from e010_review import unit_neighbors,sparse_graph_contract
    from e014_review import parent_geometry,oral_labels,BOUNDS
    from e012_marker_audit import verify_truth
    from e022_review import pair_label_audit
    threadpool_limits(4);torch.set_num_threads(4);torch.set_num_interop_threads(1)
    base=Path(base);features=Path(features);root=base/('verified-'+unit)/'work'
    admit=json.loads((base/'native-admission.json').read_text())
    if admit['status']!='PASS_COMPLETED_SCIENCE_AND_DELIVERY_BEFORE_DIAGNOSTICS':raise ValueError('Independent completed science/bytes/cost admission missing')
    data,meta=load(features);ids=data['ids'].tolist();lineages={}
    if unit.startswith('E009'):
        lock=json.loads((ROOT/'experiments/E013-marker-quality/review-lock.json').read_text());truth_path=verify_truth(lock)
        truth=json.loads((truth_path/'truth.json').read_text());pop=json.loads((ROOT/lock['population_path']).read_text())
        labels={q:truth['contigs'][q]['AMBER_label'] for q in ids}
        lineages={g:r['lineage_class'] for g,r in pop['genomes'].items()};truth_semantics='Conservative v2 dominant origin; unknown remains in neighbor denominator'
        del truth,pop
    else:
        lab,quarantine,shared,genomes,truth=oral_labels(truth_root,ids,data['lengths'])
        labels={q:(genomes[int(lab[i])] if lab[i]>=0 else None) for i,q in enumerate(ids)}
        lineages={g:('provided_bacterial_target' if g in truth['targets'] else 'non_target_source') for g in genomes}
        truth_semantics='Provided-origin oracle, not unique-sequence identifiability; known-shared sensitivity remains separate in the primary review'
        del lab,quarantine,shared,truth
    names=sorted({x for x in labels.values() if x is not None});codes={g:i for i,g in enumerate(names)}
    encoded=np.array([codes.get(labels[q],-1) for q in ids],np.int32)
    result=dict(unit=unit,truth_semantics=truth_semantics,roles={},no_fit_inference_or_index=True,
        original_Mac_portability_tolerance_unchanged=True,query_policy='First 128 SHA256(contig ID), label blind; same eligible references')
    teacher_final=None
    for role in ['teacher','student']:
        saved,receipt=read_candidate(root/role/'result/checkpoint.pt')
        actual={label:tensor_digest(saved[key]) for label,key in [('online','model_state'),('target','target_state'),('predictor','predictor_state'),('anchor','anchor_state')]}
        if actual!=receipt['final_state'] or actual['anchor']!=receipt['initial_state']['anchor']:
            raise ValueError('Actual serialized tensor/buffer state differs')
        if role=='student' and receipt['initial_state']!=teacher_final:raise ValueError('Student initialization differs from its actual own teacher')
        teacher_final=actual if role=='teacher' else teacher_final
        steps=Counter(float(v['step']) for v in saved['optimizer_state']['state'].values() if 'step' in v)
        for slot in saved['optimizer_state']['state'].values():
            if any(torch.is_tensor(v) and not torch.isfinite(v).all() for v in slot.values()):raise ValueError('Nonfinite serialized Adam state')
        if any(g['lr']!=.0002 for g in saved['optimizer_state']['param_groups']):raise ValueError('Serialized learning rate differs')
        state=saved['transform'];del saved;gc.collect()
        emb,em=load_arrays(root/(role+'-embed')/'embeddings.npz','embeddings')
        graph,gm=load_arrays(root/(role+'-graph/result/graph.npz'),'candidate_sparse_graph')
        if emb['ids'].tolist()!=ids or graph['ids'].tolist()!=ids or not np.array_equal(emb['evidence'],data['eligible']):
            raise ValueError('Full cached vector/graph/eligibility axis differs')
        if not np.allclose(np.linalg.norm(emb['features'][emb['evidence']],axis=1),1,rtol=0,atol=1e-6):
            raise ValueError('Original strict E033 unit-vector tolerance failed')
        valid=emb['evidence'];matrix=graph['neighbors'];k=matrix.shape[1]
        sparse=sparse_graph_contract(graph['edges'],graph['weights'],ids,valid)
        neighbors=[[ids[j] for j in row[:5]] if ok else [] for row,ok in zip(matrix,valid)]
        numeric=unit_neighbors(emb['features'],ids,valid,neighbors,matrix,k)
        queries=np.flatnonzero(valid & (encoded>=0));same=(encoded[matrix[queries,:5]]==encoded[queries,None]).sum(1)
        census={}
        for low in BOUNDS:
            rows=(data['lengths'][queries]>=low)
            higher=[x for x in BOUNDS if x>low]
            if higher:rows&=data['lengths'][queries]<min(higher)
            bp=data['lengths'][queries][rows]
            census[str(low)]=dict(attributable_queries=int(rows.sum()),query_bp=int(bp.sum()),
                same_fraction=float(same[rows].mean()/5) if rows.any() else None,
                bp_weighted_same=float(np.dot(bp.astype(float),same[rows]/5)/bp.sum()) if bp.sum() else None)
        raw=parent_geometry(data,state,dict(ids=ids,neighbors=neighbors),labels)
        bylineage=defaultdict(list)
        for q in raw['queries']:bylineage[lineages.get(q['origin_label'],'unknown')].append(q)
        raw['by_lineage']={g:dict(queries=len(rows),raw_mean=sum(q['raw_same'] for q in rows)/len(rows),
            learned_mean=sum(q['learned_same'] for q in rows)/len(rows)) for g,rows in bylineage.items()}
        lineage=np.array([lineages.get(names[int(g)],'unknown') for g in encoded[queries]],dtype=object)
        native_lineage={}
        for group in sorted(set(lineage)):
            chosen=lineage==group;bp=data['lengths'][queries][chosen]
            native_lineage[group]=dict(attributable_queries=int(chosen.sum()),query_bp=int(bp.sum()),
                same_fraction=float(same[chosen].mean()/5),bp_weighted_same=float(np.dot(bp.astype(float),same[chosen]/5)/bp.sum()) if bp.sum() else None)
        result['roles'][role]=dict(actual_serialized_state=actual,Adam_step_histogram=dict(steps),
            inherited_state_contract='Byte-bound original E031 source plus passed native full-state/Adam restoration; no Mac forward/reload inference',
            sparse=sparse,unit_and_neighbor_contract=numeric,raw_learned_geometry=raw,
            attributable_native_5NN_queries=len(queries),unknown_valid_queries=int((valid & (encoded<0)).sum()),
            all_attributable_native_5NN_same=float(same.mean()/5),native_length_census=census,
            native_lineage_census=native_lineage,
            final_epoch_geometry=receipt['history'][-1]['geometry'])
        write(Path(str(output)+'.through-'+role+'.json'),result)
        del emb,graph,matrix,neighbors,queries,same;gc.collect()
    pairs,pairreceipt=read_pairs(root/'pairs/result/cache',features)
    pairs['ids']=np.asarray(ids)
    result['pair_label_consistency']=pair_label_audit(pairs,labels)
    result['source_pair_count']=pairreceipt['source_pair_count'];result['retained_pair_count']=len(pairs['left'])
    write(output,result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['base','features','truth-root','output']:p.add_argument('--'+n,required=True,type=Path)
    p.add_argument('--unit',required=True,choices=['E009-noGLM','E009-GLM','oral-noGLM']);a=p.parse_args()
    v=inspect(a.base,a.unit,a.features,a.truth_root,a.output);print('E033_TENSOR_GEOMETRY_PASS',v['unit'])
