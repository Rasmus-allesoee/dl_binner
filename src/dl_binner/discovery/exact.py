"""Blocked float64 retrieval for the unchanged E027 biological dissimilarity.

Candidate norms turn the score into an asymmetric inner product. A conservative
roundoff envelope retains every possible top-k boundary candidate. The original
subtraction-based function supplies final values and lexical ties. Native unit
vectors, views, measured depth and biological selection are never changed.
"""
import json
import os
from pathlib import Path
import sys
import time
import uuid

import numpy as np

from . import grouping as inherited
from ..unified import grouping as frozen
from ..unified.graph import runtime_scope
from ..information.grouping import load_inputs, ordered_sample, require
from ..calibrated.arrays import save, load
from ..io import digest, emit, write_json
from ..context.tokens import binding


def policy():
    """Return one exact backend policy, independent of truth or recovery outcomes."""
    return dict(version=1,backend='blocked_fp64_original_score_boundary_rerank',query_rows=64,
        floating_operation_margin=64,neighbors=30,seed=11,
        biological_policy=frozen.policy(),audit='unchanged E027 cohort; exact backend also requires recall 1.0',
        source_vectors_changed=False)


def publish(value,path):
    """Publish fresh complete JSON through a private sibling and exclusive link."""
    path=Path(path);tmp=path.parent.parent/('.'+path.name+'-'+uuid.uuid4().hex)
    data=(json.dumps(value,sort_keys=True,allow_nan=False)+'\n').encode()
    with tmp.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    try:os.link(tmp,path)
    finally:tmp.unlink()


def terms(values,lengths,positive,scales):
    """Return query/candidate maps and row constants without a unit-norm assumption."""
    u,c,d=[np.asarray(x,np.float64)for x in values];s0,s1,s2=scales
    rho=np.sqrt(lengths.astype(np.float64)/(lengths+2500))[:,None]
    un=np.einsum('ij,ij->i',u,u)[:,None]/s0
    cn=np.einsum('ij,ij->i',c,c)[:,None]/s1
    dn=np.einsum('ij,ij->i',d,d)[:,None]/s2
    one=np.ones((len(u),1));zero=(~positive).astype(np.float64)[:,None]
    candidates=np.column_stack([u,un,rho*c,rho*cn,rho,d,dn,zero])
    queries=np.column_stack([-2*u/s0,one,-2*rho*c/s1,rho,rho*(cn-1),-2*d/s2,one,zero])
    return queries,candidates,(un+dn+1)[:,0]


def exact_neighbors(data,values,positive,scales,selected,cfg,query_rows=64,engineering_query_count=None):
    """Compute complete neighbors with bounded score storage and original reranking.

The error envelope overcounts elementary float64 operations by 64*(dimension+16).
It bounds both expanded and subtraction-based arithmetic with absolute coordinate
maxima, not observed ranking margins. Inputs are bounded native-unit, TNF and
tanh-depth coordinates, and scales originate from the frozen nonzero-median rule.
Cancellation can increase the retained pool, never justify discarding a boundary.
No n-by-n persistent or in-memory score matrix is constructed.
"""
    require(query_rows==64 and np.isfinite(scales).all()and np.all(scales>=1e-12),
        'Exact policy/calibration differs')
    n=len(selected);count=n if engineering_query_count is None else engineering_query_count
    require(type(count)is int and 0<=count<=n,'Invalid engineering query count')
    k=min(30,max(0,n-1));nn=np.empty((count,k),np.int32);dd=np.empty((count,k),np.float64)
    require(n<2**31,'Selected axis cannot use int32 cache')
    if not k:return nn,dd,dict(status='PASS',rows=n,certified_rows=n,maximum_candidate_pool=0)
    lengths=data['lengths'];require(np.array_equal(lengths[selected].astype(np.float32).astype(np.int64),lengths[selected]),
        'Preserved integer length packing contract differs')
    dims=sum(x.shape[1]for x in values)+5
    candidates=np.empty((n,dims),np.float64);maxima=[np.zeros(x.shape[1])for x in values]
    for start in range(0,n,8192):
        at=selected[start:start+8192];v=[x[at]for x in values]
        _,c,_=terms(v,lengths[at],positive[at],scales);candidates[start:start+len(at)]=c
        for j,x in enumerate(v):maxima[j]=np.maximum(maxima[j],np.max(np.abs(x),axis=0))
    require(np.isfinite(candidates).all(),'Nonfinite candidate map')
    largest=np.max(np.abs(candidates),axis=0)
    operations=64*(dims+16);eps=np.finfo(np.float64).eps;gamma=operations*eps/(1-operations*eps)
    maximum_pool=0;total_pool=0;max_error=0.;minimum_gap=None;last=time.monotonic()
    for start in range(0,count,query_rows):
        at=selected[start:min(start+query_rows,count)];v=[x[at]for x in values]
        q,_,constant=terms(v,lengths[at],positive[at],scales)
        scores=q@candidates.T;scores+=constant[:,None]
        require(np.isfinite(scores).all(),'Expanded score over/underflow')
        for offset,i in enumerate(at):
            local=start+offset;row=scores[offset];row[local]=np.inf
            rough=np.argpartition(row,k-1)[:k]
            upper=float(frozen.distances(data,values,positive,scales,cfg,int(i),selected[rough]).max())
            direct=2.+sum(float(np.square(np.abs(x[int(i)].astype(np.float64))+m).sum()/s)
                for x,m,s in zip(values,maxima,scales))
            magnitude=1.+abs(float(constant[offset]))+float(np.abs(q[offset])@largest)+direct
            error=gamma*(magnitude+3*upper*upper+1.)
            require(np.isfinite(error)and error>=0,'Invalid floating-point envelope')
            threshold=3*upper*upper+error
            pool=np.flatnonzero(row<=threshold)
            require(len(pool)>=k and local not in pool,'Boundary pool lost a provisional candidate')
            # Batches bound temporary full-dimensional subtraction arrays even
            # when a large exact-tie population needs the complete candidate set.
            score=np.empty(len(pool),np.float64)
            for left in range(0,len(pool),8192):
                score[left:left+8192]=frozen.distances(data,values,positive,scales,cfg,int(i),selected[pool[left:left+8192]])
            order=np.lexsort((data['ids'][selected[pool]],score))[:k]
            nn[local]=pool[order];dd[local]=score[order]
            maximum_pool=max(maximum_pool,len(pool));total_pool+=len(pool);max_error=max(max_error,error)
            outside=row>threshold
            if outside.any():
                gap=float(np.min(row[outside])-threshold)
                if np.isfinite(gap):minimum_gap=gap if minimum_gap is None else min(minimum_gap,gap)
        if time.monotonic()-last>=5 or start+len(at)==n:
            emit('exact_joint_rows',rows=start+len(at),total=n,maximum_boundary_candidates=maximum_pool)
            last=time.monotonic()
    return nn,dd,dict(status='PASS'if count==n else 'ENGINEERING_PARTIAL',rows=n,certified_rows=count,dimensions=dims,query_rows=query_rows,
        floating_operation_count_margin=operations,gamma=gamma,maximum_squared_error_envelope=max_error,
        maximum_candidate_pool=maximum_pool,mean_candidate_pool=total_pool/count,
        minimum_excluded_expanded_gap=minimum_gap,all_possible_boundaries_reranked=True,
        numerical_model='finite normal float64 operations; frozen bounded coordinates and nonzero-median scales',
        no_quadratic_score_storage=True)


def prepare(features,embeddings,graph,output):
    """Create a fresh explicitly exact cache, refusing failures before its ready seal."""
    require('torch'not in sys.modules,'Exact graph worker must not load tensor backend')
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    data,vectors,valid,_=load_inputs(features,embeddings);cfg=frozen.policy()
    values,positive,scales,selected,transform=frozen.channels(data,vectors,valid,cfg)
    write_json(out/'backend.json',dict(policy=policy(),metric_source='unchanged E027 subtraction-based score'))
    nn,dd,cert=exact_neighbors(data,values,positive,scales,selected,cfg)
    sampled=set(map(int,ordered_sample(data['ids'][selected].tolist(),np.arange(len(selected)),cfg['audit_queries'])))
    strata={}
    for name,mask in [('positive_depth',positive[selected]),('measured_zero_depth',~positive[selected]),
        ('short',data['lengths'][selected]<2500),('long',data['lengths'][selected]>=2500)]:
        rows=ordered_sample(data['ids'][selected].tolist(),np.flatnonzero(mask),cfg['audit_stratum_queries'])
        strata[name]=set(map(int,rows));sampled.update(strata[name])
    queries=[];k=nn.shape[1]
    for local in sorted(sampled):
        i=selected[local];other=selected[selected!=i]
        exact=frozen.distances(data,values,positive,scales,cfg,int(i),other)
        cutoff=float(np.partition(exact,k-1)[k-1])if k else 0.
        queries.append(dict(id=str(data['ids'][i]),row=local,
            recall=float((dd[local]<=cutoff+1e-10).mean())if k else 1.,
            strata=[name for name,rows in strata.items()if local in rows],kth_exact=cutoff))
    overall=float(np.mean([q['recall']for q in queries]))if queries else 1.
    report={name:float(np.mean([q['recall']for q in queries if name in q['strata']]))for name,rows in strata.items()if rows}
    passed=min([overall]+list(report.values()))>=.9
    audit=dict(status='PASS'if passed else 'FAILED_RECALL_GATE',overall=overall,strata=report,queries=queries,
        calibration=transform,exact_float64_rerank=True,sampled_not_global_guarantee=True,
        native_index=False,training_neighbor_graph_only=True,runtime=runtime_scope(4),backend=policy())
    save(out/'neighbors.npz',dict(selected=selected,neighbors=nn,distances=dd),dict(kind='unified_graded_neighbors',audit=audit),data['ids'])
    write_json(out/'audit.json',audit);write_json(out/'certificate.json',cert)
    require(passed and overall==1. and all(x==1. for x in report.values()),'Exact backend failed independent original-score audit')
    files={p.name:binding(p)for p in out.iterdir()if p.is_file()}
    publish(dict(status='PASS',backend=policy(),inputs={k:binding(p)for k,p in dict(features=features,embeddings=embeddings,graph=graph).items()},
        files=files,rows=len(data['ids']),eligible=int(valid.sum()),bp=int(data['lengths'].sum()),
        no_learner_index_training_or_marker_detection=True),out/'completed.json')
    return restore(features,embeddings,graph,out)[1]


def restore(features,embeddings,graph,cache):
    """Read one exact or explicit inherited admitted cache without regenerating it."""
    root=Path(cache);m=json.loads((root/'completed.json').read_text())
    if 'backend'not in m:return inherited.restore(features,embeddings,graph,cache)
    require(m['status']=='PASS'and m['backend']==policy()and m['inputs']==
        {k:binding(p)for k,p in dict(features=features,embeddings=embeddings,graph=graph).items()},'Exact cache input/policy differs')
    require({p.name for p in root.iterdir()}==set(m['files'])|{'completed.json'}and
        all(p.is_file()and not p.is_symlink()for p in root.iterdir())and
        all(binding(root/n)==b for n,b in m['files'].items()),'Partial/corrupt exact cache')
    data,vectors,valid,meta=load_inputs(features,embeddings)
    arrays,am=load(root/'neighbors.npz','unified_graded_neighbors',data['ids'])
    audit=json.loads((root/'audit.json').read_text());cert=json.loads((root/'certificate.json').read_text())
    expected=np.array(sorted(np.flatnonzero(valid),key=lambda i:str(data['ids'][i])),np.int64);n=len(expected);k=min(30,max(0,n-1))
    near,dist=arrays['neighbors'],arrays['distances']
    require(am['audit']==audit and audit['status']=='PASS'and audit['overall']==1. and all(v==1. for v in audit['strata'].values())
        and cert['status']=='PASS'and cert['certified_rows']==n,'Failed exact proof cannot be consumed')
    require(m['rows']==len(data['ids'])and m['eligible']==n and m['bp']==int(data['lengths'].sum())and
        np.array_equal(arrays['selected'],expected)and near.shape==dist.shape==(n,k)and near.dtype==np.int32
        and dist.dtype==np.float64 and np.all((near>=0)&(near<n))and np.isfinite(dist).all()
        and np.all(dist>0)and not np.any(np.diff(dist,axis=1)<0)and
        not np.any(near==np.arange(n)[:,None])and not np.any(np.diff(np.sort(near,axis=1),axis=1)==0),
        'Exact cache axes/numbers differ')
    return (data,vectors,valid,meta,arrays),m


def run(features,embeddings,graph,evidence_path,cache,output):
    """Run unchanged biological partitions from an admitted inherited/exact cache."""
    (data,vectors,valid,meta,a),m=restore(features,embeddings,graph,cache)
    out=Path(output);out.mkdir(parents=True,exist_ok=False);dest=out/'retrieval';dest.mkdir()
    for p in Path(cache).iterdir():os.link(p,dest/p.name)
    cfg=frozen.policy();evidence=json.loads(Path(evidence_path).read_text())
    arms,tree,alternatives,choices=frozen.partitions(data,valid,a['selected'],a['neighbors'],a['distances'],evidence,cfg)
    provenance=m.get('backend',m.get('policy'))
    for name,part in arms.items():
        part.update(parent_features_sha256=digest(features),embedding_sha256=digest(embeddings),graph_sha256=digest(graph),
            config=cfg,discovery_policy=provenance,algorithm='Unchanged E027 biology; admitted inherited/exact retrieval',scientific_quality_assessed=False)
        write_json(out/(name+'-partition.json'),part);write_json(out/(name+'-choices.json'),choices[name])
    save(out/'forest.npz',{k:v for k,v in tree.items()if isinstance(v,np.ndarray)},dict(kind='unified_density_forest'),data['ids'])
    write_json(out/'alternatives.json',alternatives)
    files={str(p.relative_to(out)):binding(p)for p in out.rglob('*')if p.is_file()}
    result=dict(status='SUCCESS',config=cfg,discovery_policy=provenance,rows=len(valid),bp=int(data['lengths'].sum()),samples=meta['samples'],
        input_sha256={k:digest(p)for k,p in dict(features=features,embeddings=embeddings,graph=graph,evidence=evidence_path).items()},files=files,
        full_DNA_preserved=True,truth_accessed=False,recall=json.loads((dest/'audit.json').read_text()))
    write_json(out/'completed.json',result);return result


def audit(features,embeddings,graph,evidence_path,output):
    """Apply strict cache admission and the entire original cached forest/DNA audit."""
    restore(features,embeddings,graph,Path(output)/'retrieval')
    return frozen.audit(features,embeddings,graph,evidence_path,output)
