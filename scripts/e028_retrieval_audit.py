#!/usr/bin/env python3
"""Audit retained search refusal and an algebraic next-step feasibility example.

No index, community partition, fit, marker call or truth score is constructed.
The numerical audit reads only new returned caches and hash-matched existing
feature axes. The algebra example uses synthetic channels, never native vectors.
"""
import argparse
import gc
import json
from pathlib import Path
import platform
import shutil
import sys
import tarfile
import time

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e028_control import product_scope
from e024_coverage import binding, write
from e027_inspection import require


def numeric(base, output):
    """Read actual sparse formats and independently check full ordered feature axes."""
    product_scope()
    import numpy as np
    from dl_binner.calibrated.arrays import load
    from dl_binner.information.grouping import ordered_sample
    from dl_binner.unified.grouping import policy
    base=Path(base);inv=json.loads((base/'inventory.json').read_text())
    require(json.loads((base/'archive-verified.json').read_text())['every_member_verified'], 'Archive not verified')
    plan=json.loads((base/'controls/evidence/plan.json').read_text())
    cfg=policy();out={}
    paths={'E009':ROOT/'artifacts/e011-cached-grouping-reference/restore-local/candidate/features/features.npz',
           'oral':ROOT/'artifacts/e024-inspection/20261028T193107Z/verified/work/rebound/features.npz'}
    for community,features in paths.items():
        unit='oral-noGLM' if community=='oral' else 'E009-noGLM'
        wanted=json.loads((base/'controls/evidence/gates/data.json').read_text())['hashed'][plan['units'][unit]['features']]
        require(binding(features)==wanted,'Retained local feature bytes differ')
        with np.load(features,allow_pickle=False)as z:
            ids=z['ids'];lengths=z['lengths'];eligible=z['eligible'];depth=z['depth']
        selected=np.array(sorted(np.flatnonzero(eligible),key=lambda i:str(ids[i])),np.int64)
        positive=(depth>0).any(1)
        local_ids=ids[selected].tolist();full_ids=ids.tolist()
        expected=set(map(int,ordered_sample(local_ids,np.arange(len(selected)),cfg['audit_queries'])))
        for mask in [positive[selected],~positive[selected],lengths[selected]<2500,lengths[selected]>=2500]:
            expected.update(map(int,ordered_sample(local_ids,np.flatnonzero(mask),cfg['audit_stratum_queries'])))
        roles=[(u,r)for u in (['oral-noGLM']if community=='oral'else ['E009-noGLM','E009-GLM'])for r in ['teacher','student']]
        for unit,role in roles:
            prefix=f'work/retrieval/{unit}/{role}/cache/'
            if prefix+'neighbors.npz' not in inv['members']:
                continue
            stage=base/'numeric-staging'/unit/role;stage.mkdir(parents=True,exist_ok=False)
            with tarfile.open(base/'e028-evidence.tar.gz','r:gz')as a:
                for name in ['neighbors.npz','neighbors.json']:
                    with (stage/name).open('xb')as f:shutil.copyfileobj(a.extractfile(prefix+name),f,1024**2)
                    require(binding(stage/name)==inv['members'][prefix+name],'Staged numeric member differs')
            arrays,meta=load(stage/'neighbors.npz','unified_graded_neighbors',full_ids)
            near,dist=arrays['neighbors'],arrays['distances']
            require(np.array_equal(arrays['selected'],selected)and near.shape==dist.shape==(len(selected),30), 'Wrong selected/full axis or shape')
            require(near.dtype==np.int32 and dist.dtype==np.float64 and np.isfinite(dist).all()
                    and np.all(dist>=cfg['distance_floor']) and np.all(dist[:,1:]>=dist[:,:-1]),'Invalid numeric distances/order')
            require(np.all((near>=0)&(near<len(selected))) and not np.any(near==np.arange(len(selected))[:,None])
                    and not np.any(np.diff(np.sort(near,axis=1),axis=1)==0),'Invalid/self/duplicate neighbors')
            audit=meta['audit'];rows={q['row']for q in audit['queries']}
            require(rows==expected and all(q['id']==local_ids[q['row']] for q in audit['queries']), 'Frozen audit cohort/ID mapping differs')
            require(audit['calibration']['actual_missing_cells']==0
                    and len(audit['calibration']['usable_depth_columns'])==10
                    and all(audit['calibration']['usable_depth_columns']), 'Measured ten-depth semantics differ')
            out[unit+'/'+role]=dict(status='PASS_RETURNED_NUMERIC_AND_SOURCE_AXIS',full_rows=len(ids),full_bp=int(lengths.sum()),
                selected_rows=len(selected),selected_bp=int(lengths[selected].sum()),
                selected_measured_zero_rows=int((~positive[selected]).sum()),selected_measured_zero_bp=int(lengths[selected][~positive[selected]].sum()),
                all_zero_full_rows=int((~positive).sum()),full_axis_sha256=meta['full_ids_sha256'],
                features=wanted,numeric=binding(stage/'neighbors.npz'),recall_status=audit['status'],
                search_accuracy_is_not_biological_homogeneity=True,completed_cache=(base/'controls'/prefix/'completed.json').exists())
            del arrays,near,dist;gc.collect()
            print('NUMERIC_AXIS_PASS',unit,role,len(selected),flush=True)
        del ids,lengths,eligible,depth,selected,positive,full_ids,local_ids;gc.collect()
    write(output,dict(status='PASS_ACTUAL_READER_AND_AXES',caches=out,model_inference_or_original_graph_rebuild=False,
        raw_native_vectors_not_modified=True,no_new_truth_score=True))


def linear_terms(values,lengths,positive,scales,length_scale):
    """Algebra-only query/candidate terms for the unchanged squared dissimilarity.

Returns Q, C, row constants with 3*d(i,j)^2 = Q[i] @ C[j] + constant[i]
before the original floor. No unit-norm assumption or modality normalization is
added. This is a feasibility formula, not an admitted production search engine.
"""
    import numpy as np
    u,c,d=[np.asarray(x,np.float64)for x in values];s0,s1,s2=scales
    rho=np.sqrt(lengths.astype(np.float64)/(lengths+length_scale))[:,None]
    un=(u*u).sum(1)[:,None]/s0;cn=(c*c).sum(1)[:,None]/s1;dn=(d*d).sum(1)[:,None]/s2
    one=np.ones((len(u),1));zero=(~positive).astype(np.float64)[:,None]
    candidates=np.column_stack([u,un,rho*c,rho*cn,rho,d,dn,zero])
    queries=np.column_stack([-2*u/s0,one,-2*rho*c/s1,rho,rho*(cn-1),-2*d/s2,one,zero])
    return queries,candidates,(un+dn+1)[:,0]


def algebra(output):
    """Check exact formula/compiled metric on synthetic mixed-availability channels."""
    product_scope()
    import numpy as np
    from dl_binner.unified.grouping import channels,distances,metric,policy
    cfg=policy();rng=np.random.default_rng(11);n=256
    ids=np.array([f'opaque-{i:04d}'for i in range(n)]);lengths=rng.integers(500,100001,n,dtype=np.int64)
    vectors=rng.normal(size=(n,64)).astype(np.float32);vectors/=np.linalg.norm(vectors,axis=1)[:,None]
    depth=rng.uniform(0,30,(n,10)).astype(np.float32);depth[:90]=0;depth[90:106]=1e-6
    data=dict(ids=ids,lengths=lengths,tnf=rng.dirichlet(np.ones(136),n).astype(np.float32),depth=depth)
    values,positive,scales,selected,transform=channels(data,vectors,np.ones(n,bool),cfg)
    q,c,constant=linear_terms(values,lengths,positive,scales,cfg['length_scale_bp'])
    expanded=np.maximum(np.sqrt(np.maximum((q@c.T+constant[:,None])/3,0)),cfg['distance_floor'])
    exact=np.array([distances(data,values,positive,scales,cfg,i,np.arange(n))for i in range(n)])
    packed=np.ascontiguousarray(np.column_stack([*values,lengths,positive]),dtype=np.float32)
    args=dict(native_dim=64,composition_dim=136,s0=float(scales[0]),s1=float(scales[1]),s2=float(scales[2]),length_scale=cfg['length_scale_bp'],floor=cfg['distance_floor'])
    compiled=np.array([[metric(packed[i],packed[j],**args)for j in range(n)]for i in range(n)])
    error=float(np.max(np.abs(expanded-exact)));native_error=float(np.max(np.abs(compiled-exact)))
    require(error<1e-12 and native_error<1e-12,'Algebra/compiled score differs; do not widen or deploy')
    # A valid channel-level counterexample, not an explanation fitted to native IDs.
    v=np.tile(vectors[0],(3,1));composition=np.tile(values[1][0],(3,1));d=np.zeros((3,10),np.float32);d[2]=.001
    small=dict(lengths=np.full(3,100000,np.int64));p=np.array([False,False,True])
    counter=np.array([distances(small,(v,composition,d),p,scales,cfg,i,np.arange(3))for i in range(3)])
    require(counter[0,1]>counter[0,2]+counter[2,1] and counter[0,0]>0,'Expected nonmetric counterexample absent')
    write(output,dict(status='PASS_SYNTHETIC_EQUIVALENCE_AND_NONMETRIC_COUNTEREXAMPLE',rows=n,
        dimensions=c.shape[1],max_abs_expansion_error=error,max_abs_compiled_metric_error=native_error,
        triangle_counterexample=counter.tolist(),actual_frozen_metric_source=binding(ROOT/'src/dl_binner/unified/grouping.py'),
        native_vectors_or_index_or_community_score_consumed=False,
        limits=['Tiny synthetic numerical equivalence is not a full native backend admission or throughput result.',
                'Production needs conservative floating-point boundary handling and original subtraction-based rerank, including extreme calibration and ties.',
                'No proof that nonmetric geometry is the sole cause of the retained native misses.']))
    print('ALGEBRA_EQUIVALENCE_PASS',error,native_error,'dimensions',c.shape[1],flush=True)


def kernel(output):
    """Measure one synthetic BLAS/top-k shape, without native/community claims."""
    product_scope()
    import numpy as np
    from threadpoolctl import threadpool_info
    rng=np.random.default_rng(11);q=rng.normal(size=(64,215));c=rng.normal(size=(65536,215));times=[]
    for repeat in range(4):
        start=time.monotonic();scores=q@c.T;indices=np.argpartition(scores,29,axis=1)[:,:30]
        seconds=time.monotonic()-start
        require(indices.shape==(64,30)and np.isfinite(scores).all(),'Invalid synthetic kernel')
        if repeat:times.append(seconds)
    pools=threadpool_info();require(all(p['num_threads']<=4 for p in pools),'Kernel thread budget differs')
    pairs=508763**2;one=max(times)*pairs/(64*65536)
    write(output,dict(status='PASS_SYNTHETIC_KERNEL_ONLY',platform=platform.platform(),pools=pools,
        query_rows=64,candidate_rows=65536,dimensions=215,dtype='float64',warmups=1,
        measured_seconds=times,one_Oral_pairing_count=pairs,one_Oral_linear_projection_seconds=one,
        native_slowdown_planning_factor=4,two_Oral_plus_setup_group_export_collection_seconds=8*one+7200,
        non_kernel_reserve_seconds=7200,no_community_vectors_truth_or_index=True,
        limits=['Synthetic kernel projection, not native full-shape/full-stage throughput.',
                'Numerical boundary certificates and original rerank are not implemented.',
                'Blocking bounds memory; pair arithmetic remains quadratic.']))
    print('SYNTHETIC_KERNEL_PASS',times,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path);p.add_argument('--numeric',action='store_true');p.add_argument('--algebra',action='store_true');p.add_argument('--kernel',action='store_true');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if sum([a.numeric,a.algebra,a.kernel])!=1:p.error('Select exactly one audit')
    if a.numeric:numeric(a.base,a.output)
    elif a.algebra:algebra(a.output)
    elif a.kernel:kernel(a.output)
    else:p.error('Select exactly numeric or synthetic algebra audit')
