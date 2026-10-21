#!/usr/bin/env python3
"""Restore-only E018 vote-led selection from the immutable E017 numeric caches.

No feature preparation, encoder, index, graph optimizer, profile calculation,
marker detector or truth reader is reachable here. All DNA rows remain present.
Stored float32 scores/votes are consumed as written; tolerances below validate
float32 normalization only and do not enlarge scientific acceptance thresholds.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).absolute().parent))


def read_inputs(features, retained):
    """Validate actual sparse/opaque-ID caches and frozen parent/core bindings."""
    import numpy as np
    from dl_binner.io import digest
    from dl_binner.multiview.arrays import load_arrays
    from dl_binner.information.export import validate_partition
    from dl_binner.information.grouping import require, policy
    retained=Path(retained);data,meta=load_arrays(features,'features')
    from dl_binner.io import validate_features
    validate_features(data,meta)
    graph,gm=load_arrays(retained/'graph.npz','information_core_graph')
    cache,cm=load_arrays(retained/'recruitment.npz','information_recruitment')
    core=validate_partition(data,retained/'core-partition.json',features)
    old=validate_partition(data,retained/'partition.json',features)
    done=json.loads((retained/'completed.json').read_text())
    require(done['status']=='SUCCESS' and done['truth_used'] is False and done['encoder_inference'] is False,
            'Retained native success contract missing')
    for filename,key in [('graph.npz','graph_sha256'),('recruitment.npz','recruitment_sha256'),
                         ('core-partition.json','core_partition_sha256'),('partition.json','parent_sha256')]:
        require(digest(retained/filename)==done[key],'Retained completion member differs')
    require(data['ids'].tolist()==graph['ids'].tolist()==cache['ids'].tolist()
            and gm['features_sha256']==cm['features_sha256']==digest(features)
            and cm['graph_sha256']==digest(retained/'graph.npz')
            and gm['embedding_sha256']==cm['embedding_sha256']==old['embedding_sha256'],
            'Retained complete ID/feature/vector/cache bindings differ')
    require(cm['config']==gm['information_config']==old['information_config'], 'Retained policy drift')
    # Invoke the strict packaged policy reader on the frozen adjacent original config.
    require(cm['config']==policy(Path(__file__).absolute().parents[1]/
            'experiments/E017-information-aware-grouping/config.json'), 'Unfrozen original policy')
    n=len(data['ids']);cores=graph['core_indices'];edges=graph['edges'];weights=graph['weights']
    require(cores.ndim==1 and np.issubdtype(cores.dtype,np.integer) and len(set(cores.tolist()))==len(cores)
            and np.all((cores>=0)&(cores<n)) and np.all(data['eligible'][cores])
            and np.all(data['lengths'][cores]>=2500), 'Malformed core indices')
    require(edges.ndim==2 and edges.shape[1]==2 and len(edges)==len(weights)
            and np.isfinite(weights).all() and np.all(weights>0)
            and np.isin(edges,cores).all() and np.all(edges[:,0]<edges[:,1])
            and len(set(map(tuple,edges)))==len(edges), 'Malformed retained sparse graph')
    q=cache['query_indices'];labels=np.asarray(core['assignment']);valid=np.asarray(core['valid'],bool)
    expected=sorted(np.flatnonzero(valid&(labels<0)),key=lambda i:str(data['ids'][i]))
    require(q.tolist()==expected and np.issubdtype(q.dtype,np.integer), 'Full original query axis differs')
    candidates=cache['candidate_indices'];aff=cache['candidate_affinities']
    require(candidates.ndim==2 and candidates.shape==aff.shape and len(candidates)==len(q)
            and np.issubdtype(candidates.dtype,np.integer) and np.isin(candidates,cores).all()
            and np.isfinite(aff).all() and np.all(aff>=0)
            and all(len(set(row.tolist()))==len(row)for row in candidates), 'Malformed candidate/support cache')
    offers=cache['offered_bins'];scores=cache['normalized_scores'];votes=cache['vote_fractions'];support=cache['distinct_support']
    require(offers.shape==scores.shape==votes.shape==support.shape==candidates.shape
            and np.issubdtype(offers.dtype,np.integer) and np.issubdtype(support.dtype,np.integer)
            and scores.dtype==votes.dtype==np.float32 and np.isfinite(scores).all()
            and np.isfinite(votes).all() and np.all((votes>=0)&(votes<=1))
            and np.all(support>=0), 'Malformed offered score/vote/support evidence')
    require(cache['channel_scores'].shape==cache['channel_available'].shape==(*offers.shape,3)
            and cache['channel_available'].dtype==bool and np.isfinite(cache['channel_scores']).all(),
            'Malformed channel evidence')
    require(cache['accepted_bins'].shape==(len(q),) and cache['reasons'].shape==(len(q),), 'Truncated original decisions')
    # Independently verify saved votes/support from distinct positive candidate IDs.
    for row in range(len(q)):
        near=labels[candidates[row]];bins=sorted(set(int(b)for b in near if b>=0))
        require(offers[row,:len(bins)].tolist()==bins and np.all(offers[row,len(bins):]==-1), 'Offered bins differ')
        require(np.all(scores[row,len(bins):]==-1) and not votes[row,len(bins):].any()
                and not support[row,len(bins):].any(), 'Nonempty unused offer')
        total=float(aff[row,near>=0].sum())
        for col,b in enumerate(bins):
            mask=(near==b)&(aff[row]>0);v=np.float32(float(aff[row,mask].sum())/total if total else 0.)
            require(support[row,col]==int(mask.sum()) and votes[row,col]==v,
                    'Distinct supporters/normalized vote differs from retained affinities')
            require(scores[row,col]>=0, 'Negative offered profile score')
    return data,meta,core,old,cache,gm


def choose(cache):
    """Apply the sole rule to saved offers; refuse ambiguous or malformed majorities."""
    import numpy as np
    from dl_binner.information.grouping import require
    offers=cache['offered_bins'];scores=cache['normalized_scores'];votes=cache['vote_fractions'];support=cache['distinct_support']
    require(offers.ndim==2 and offers.shape==scores.shape==votes.shape==support.shape,
            'Offered selection axes differ')
    require(np.isfinite(scores).all()and np.isfinite(votes).all()and np.all(votes>=0)
            and np.all(votes<=1)and np.all(support>=0), 'Nonfinite/negative decision evidence')
    offered=offers>=0
    require(np.all(votes.sum(axis=1,dtype=np.float64)<=1+1e-6),'Malformed vote normalization')
    require(np.all(((votes>=2/3)&offered).sum(axis=1)<=1),'Multiple vote majorities refused')
    admit=offered&(scores<=1.)&(scores>=0)&(votes>=2/3)&(support>=2)
    require(np.all(admit.sum(axis=1)<=1), 'Ambiguous admissible candidates')
    selected=np.full(len(offers),-1,np.int32);cols=np.full(len(offers),-1,np.int32)
    rows=np.flatnonzero(admit.any(axis=1))
    if len(rows):
        cols[rows]=admit[rows].argmax(axis=1)
        selected[rows]=offers[rows,cols[rows]]
    original=cache['accepted_bins']
    require(original.shape==selected.shape and np.all(selected[original>=0]==original[original>=0]),
            'Previously accepted recruitment was lost or redirected')
    return selected,cols


def partition_from_selection(data,core,old,cache,selected):
    """Preserve core group identity while canonical opaque-ID labels may permute."""
    from dl_binner.candidate.grouping import canonical_partition
    from dl_binner.information.grouping import require
    groups=[[]for _ in range(core['clusters'])]
    for i,b in enumerate(core['assignment']):
        if b>=0:groups[b].append(i)
    reasons=list(core['reason'])
    for row,i in enumerate(cache['query_indices']):
        b=int(selected[row])
        if b>=0:groups[b].append(int(i))
        reasons[i]=''if b>=0 else'no_jointly_admissible_core_candidate'
    parent=canonical_partition(data['ids'].tolist(),data['eligible'],groups,data['lengths'],old['config'],reasons)
    # Canonical labels can permute when a new member has the smallest opaque ID.
    # Verify biological group identity through original core members, not label equality.
    core_to_new={}
    for i,b in enumerate(core['assignment']):
        if b>=0:
            new=parent['assignment'][i]
            require(core_to_new.setdefault(b,new)==new, 'Core group split during canonicalization')
    require(len(set(core_to_new.values()))==len(core_to_new), 'Core groups merged')
    for row,i in enumerate(cache['query_indices']):
        require(parent['assignment'][i]==(core_to_new[int(selected[row])]if selected[row]>=0 else-1),
                'Opaque-ID canonical assignment differs')
    for key in ['config','neighbors','parent_features_sha256','embedding_sha256','graph_sha256','information_config','neighbor_storage']:
        parent[key]=old[key]
    parent.update(algorithm='E018 fixed E017 cores; vote-led/profile-admissibility recruitment',
                  scientific_quality_assessed=False,
                  acceptance_rule='unique existing core candidate: vote >=2/3, distinct positive supporters >=2, saved profile score <=1; otherwise unassigned; no profile ranking or runner margin')
    return parent,core_to_new


def consume(features,retained,output):
    """Write one fresh complete parent plus compact decisions; preserve all inputs."""
    import numpy as np
    from dl_binner.candidate.grouping import canonical_partition
    from dl_binner.io import digest,save_arrays,write_json,emit
    from dl_binner.information.grouping import require
    data,meta,core,old,cache,gm=read_inputs(features,retained)
    selected,cols=choose(cache)
    parent,core_to_new=partition_from_selection(data,core,old,cache,selected)
    parent['retained_group_root']=str(Path(retained))
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    write_json(out/'partition.json',parent)
    save_arrays(out/'selection.npz',dict(ids=data['ids'],query_indices=cache['query_indices'],
                accepted_bins=selected,chosen_offer=cols),dict(kind='E018_cached_selection',
                source_recruitment_sha256=digest(Path(retained)/'recruitment.npz'),
                parent_sha256=digest(out/'partition.json'),core_to_new={str(k):v for k,v in core_to_new.items()},
                rule=parent['acceptance_rule']))
    result=dict(status='SUCCESS',rows=len(data['ids']),bp=int(data['lengths'].sum()),samples=meta['samples'],
                features_sha256=digest(features),embeddings_sha256=old['embedding_sha256'],
                graph_sha256=old['graph_sha256'],retained_group_root=str(Path(retained)),
                original_parent_sha256=digest(Path(retained)/'partition.json'),
                original_core_sha256=digest(Path(retained)/'core-partition.json'),
                recruitment_sha256=digest(Path(retained)/'recruitment.npz'),parent_sha256=digest(out/'partition.json'),
                selection_sha256=digest(out/'selection.npz'),original_recruited=int((cache['accepted_bins']>=0).sum()),
                recruited=int((selected>=0).sum()),newly_recruited=int(((selected>=0)&(cache['accepted_bins']<0)).sum()),
                added_bp=int(data['lengths'][cache['query_indices'][(selected>=0)&(cache['accepted_bins']<0)]].sum()),
                truth_used=False,encoder_inference=False,index_rebuilt=False,profiles_recomputed=False,cores_regrouped=False)
    write_json(out/'completed.json',result);emit('E018_cached_acceptance_complete',**result)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['features','retained','output']:p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();consume(a.features,a.retained,a.output)
