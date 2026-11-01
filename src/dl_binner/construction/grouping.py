"""Root-safe antichains and supported recruitment on immutable native caches.

This module cannot train, detect markers, retrieve neighbors or build a forest.
Profiles describe between-parent variation of measured means, not measured window
coverage or per-base variance. All decisions are label-free heuristics.
"""
import json
from pathlib import Path
import time

import numpy as np
from numba import njit

from ..calibrated.arrays import save, load
from ..candidate.grouping import canonical_partition
from ..context.tokens import binding
from ..density import grouping as density
from ..discovery import exact
from ..information.grouping import load_inputs, ordered_sample, require
from ..information.export import validate_partition
from ..io import digest, emit, write_json
from ..unified import grouping as original


DEFAULT = dict(version=1, seed=11, min_bin_contigs=1, min_bin_bp=10000,
    length_scale_bp=2500, calibration_rows=8192, calibration_neighbors=10,
    calibration_quantile=.9, radius_floor=1e-8, neutral_support=.5,
    merge_score=2/3, recruit_min_support=2, recruit_vote_fraction=2/3,
    recruit_margin_ratio=1.5, recruit_score=.6, marker_change_weight=.1,
    marker_excess_penalty=5., reliable_marker_weight=.8,
    root_policy='exclude_internal_forest_roots', profile_batch_rows=4096,
    singleton_min_bp=200000)


def policy(path=None):
    """Return exactly one prospective policy; refuse implicit grids or overrides."""
    cfg = dict(DEFAULT) if path is None else json.loads(Path(path).read_text())
    require(cfg == DEFAULT and all(type(cfg[k]) is type(v) for k,v in DEFAULT.items()),
            'Unfrozen biological bin-construction policy')
    return cfg


@njit(cache=True)
def reduce_moments(children, weights, values):
    """Accumulate weighted sums and scalar squared norms once per forest edge."""
    n, dim = values.shape; size = len(children)
    mass = np.zeros(size, np.float64); total = np.zeros((size, dim), np.float64)
    square = np.zeros(size, np.float64)
    for i in range(n):
        mass[i] = weights[i]
        for j in range(dim):
            total[i,j] = weights[i]*values[i,j]
            square[i] += weights[i]*values[i,j]*values[i,j]
    for node in range(n,size):
        a,b = children[node]
        mass[node] = mass[a]+mass[b]; square[node] = square[a]+square[b]
        for j in range(dim): total[node,j] = total[a,j]+total[b,j]
    return mass,total,square


def forest_contract(tree, data, selected, nn, dd):
    """Validate actual retained tree axes/core/MST support without rebuilding it."""
    n=len(selected); size=len(tree['mass']); seen=np.zeros(size,np.int32)
    require(n<=size<=max(n,2*n-1) and tree['children'].shape==(size,2)
        and tree['children'].dtype.kind in 'iu' and np.all(tree['children'][:n]==-1)
        and np.array_equal(tree['mass'][:n],data['lengths'][selected])
        and np.all(tree['count'][:n]==1) and np.all(tree['level'][:n]==0)
        and tree['level'].shape==(size,) and np.isfinite(tree['level']).all(),
        'Retained forest leaves/schema differ')
    for node in range(n,size):
        a,b=map(int,tree['children'][node])
        require(0<=a<b<node and tree['mass'][node]==tree['mass'][a]+tree['mass'][b]
            and tree['count'][node]==tree['count'][a]+tree['count'][b]
            and tree['level'][node]>0 and tree['level'][node]>=max(tree['level'][a],tree['level'][b]),
            'Retained forest parent/mass/level differs')
        seen[a]+=1;seen[b]+=1
    require(np.all(seen<=1) and np.array_equal(tree['roots'],np.flatnonzero(seen==0)),
        'Retained forest roots differ')
    k=nn.shape[1];core=dd[:,min(10,k)-1] if k else np.ones(n)
    require(np.array_equal(core,tree['core']) and tree['mst_edges'].shape==(size-n,2)
        and tree['mst_distances'].shape==(size-n,)
        and np.array_equal(np.sort(tree['mst_distances']),tree['level'][n:]),
        'Retained forest core/MST counters differ')
    # Vectorized membership in the existing n-by-k cache avoids Python work for
    # each of half a million MST edges. No new neighbor or MST is computed.
    edge=tree['mst_edges'];require(np.all((edge>=0)&(edge<n)) and np.all(edge[:,0]!=edge[:,1]),
        'Retained MST escaped eligible axis')
    for start in range(0,len(edge),8192):
        rows=edge[start:start+8192];a,b=rows.T
        da=np.min(np.where(nn[a]==b[:,None],dd[a],np.inf),axis=1)
        db=np.min(np.where(nn[b]==a[:,None],dd[b],np.inf),axis=1)
        expected=np.maximum(np.maximum(core[a],core[b]),np.minimum(da,db))
        require(np.array_equal(expected,tree['mst_distances'][start:start+len(rows)]),
            'Retained MST escaped actual sparse mutual-reachability support')


def restore(features, embeddings, graph, evidence_path, accepted):
    """Bind every accepted result member, inputs, cache and numeric forest."""
    root=Path(accepted);m=json.loads((root/'completed.json').read_text())
    require(m['status']=='SUCCESS' and m['config']==original.policy()
        and m['input_sha256']=={k:digest(p) for k,p in dict(features=features,
            embeddings=embeddings,graph=graph,evidence=evidence_path).items()},
        'Accepted E029 result/input policy differs')
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    require(actual==set(m['files'])|{'completed.json'} and
        not any(p.is_symlink() for p in root.rglob('*')) and
        all(binding(root/k)==v for k,v in m['files'].items()),
        'Missing/corrupt accepted E029 member; no regeneration fallback')
    (data,vectors,valid,meta,a),cache=exact.restore(features,embeddings,graph,root/'retrieval')
    tree,_=load(root/'forest.npz','unified_density_forest',data['ids'])
    forest_contract(tree,data,a['selected'],a['neighbors'],a['distances'])
    evidence=json.loads(Path(evidence_path).read_text());original.validate_evidence(evidence,data['ids'].tolist())
    alternatives=json.loads((root/'alternatives.json').read_text())
    ids=data['ids'][a['selected']].tolist();axis=set(ids)
    physical=dict(evidence,calls={k:v for k,v in evidence['calls'].items() if k in axis})
    require(alternatives==original.alternatives_for(tree,data['lengths'][a['selected']],ids,physical,original.policy()),
        'Retained alternative support differs')
    return data,vectors,valid,meta,a,tree,alternatives,evidence


def profiles(data, valid, selected, nn, cfg):
    """Calibrate source-blind composition/depth moments from retained local pairs.

    The depth measurement mask is explicit. A zero numerical mean is never
    classified as a failed/missing measurement. All admitted production columns
    were measured; zero-column tiny inputs represent an absent modality.
    """
    n=len(selected);lengths=data['lengths'][selected].astype(np.float64)
    comp=np.sqrt(data['tnf'][selected].astype(np.float64))
    raw=np.log1p(data['depth'][selected].astype(np.float64))
    measured=np.full(n,raw.shape[1]>0,bool)
    if 'depth_measured' in data:
        full=np.asarray(data['depth_measured'])
        require(full.dtype==bool and full.shape==valid.shape,'Malformed explicit depth measurement mask')
        measured=full[selected]
        require(raw.shape[1]>0 or not measured.any(),'Missing depth modality claims measurements')
    std=raw[measured].std(0) if measured.any() else np.zeros(raw.shape[1]);use=std>1e-8
    depth=raw[:,use]/std[use];positive=(raw>0).any(1)&measured
    coords=(comp,depth);weights=(lengths*lengths/(lengths+cfg['length_scale_bp']),lengths*measured)
    sampled=ordered_sample(data['ids'][selected].tolist(),np.arange(n),cfg['calibration_rows'])
    k=min(cfg['calibration_neighbors'],nn.shape[1]);pairs=np.column_stack((np.repeat(sampled,k),nn[sampled,:k].ravel()))
    radii=[];active=[];counts=[]
    for c,x in enumerate(coords):
        take=np.ones(len(pairs),bool) if c==0 else measured[pairs].all(1)&positive[pairs].any(1)
        delta=np.square(x[pairs[take,0]]-x[pairs[take,1]]).sum(1)
        nonzero=delta[delta>cfg['radius_floor']]
        active.append(bool(len(nonzero) and x.shape[1]))
        radii.append(max(cfg['radius_floor'],float(np.quantile(nonzero,cfg['calibration_quantile']))/2) if len(nonzero) else 1.)
        counts.append(len(nonzero))
    record=dict(channel_order=['sqrt_TNF','scaled_log1p_measured_parent_means'],
        calibration_pair_local_rows=pairs.tolist(),calibration_query_ids=data['ids'][selected[sampled]].tolist(),
        radii=radii,active=active,nonzero_local_pairs=counts,depth_column_std=std.tolist(),
        depth_usable_columns=use.tolist(),measured_rows=int(measured.sum()),positive_rows=int(positive.sum()),
        measured_zero_rows=int((measured&~positive).sum()),missing_rows=int((~measured).sum()),
        semantics='Between-parent profile scatter only; co-zero/missing neutral; no measured window/per-base variance')
    return coords,weights,measured,positive,np.asarray(radii),np.asarray(active),record


def marker_tables(tree, ids, evidence, cfg):
    """Aggregate reliable physical-locus weights with soft breadth/excess factors."""
    original.validate_evidence(evidence,ids);n=len(ids);size=len(tree['mass']);panel=evidence['panel_size']
    values={};breadth=np.zeros(size);excess=np.zeros(size);factor=np.ones(size)
    for node in range(size):
        if node<n:
            values[node]={f:(float(sum(v)),float(max(v))) for f,v in evidence['calls'].get(ids[node],{}).items()}
        else:
            a,b=map(int,tree['children'][node]);x,y=values.pop(a),values.pop(b)
            if len(x)<len(y):x,y=y,x
            for f,(total,maximum) in y.items():
                old=x.get(f,(0.,0.));x[f]=(old[0]+total,max(old[1],maximum))
            values[node]=x
        v=values[node];breadth[node]=sum(x[1] for x in v.values())/panel
        excess[node]=sum(x[0]-x[1] for x in v.values())/panel
        factor[node]=(1+breadth[node])/(1+cfg['marker_excess_penalty']*excess[node])
    return breadth,excess,factor


def candidate_profiles(tree, alternatives, coords, weights, measured, positive, radii, active, cfg):
    """Compute O(n*d) additive moments; retain only candidate profile means/stats."""
    nodes=np.array([x['node'] for x in alternatives],np.int64);means=[];scatter=[];masses=[]
    for c,(x,w) in enumerate(zip(coords,weights)):
        mass,total,square=reduce_moments(tree['children'],w,x)
        mu=np.divide(total[nodes],mass[nodes,None],out=np.zeros((len(nodes),x.shape[1])),where=mass[nodes,None]>0)
        var=np.maximum(0,np.divide(square[nodes],mass[nodes],out=np.zeros(len(nodes)),where=mass[nodes]>0)-np.square(mu).sum(1))
        means.append(mu);scatter.append(var);masses.append(mass[nodes])
        del mass,total,square
    _,pos,_=reduce_moments(tree['children'],np.ones(len(measured)),positive[:,None].astype(np.float64))
    observed,_,_=reduce_moments(tree['children'],measured.astype(np.float64),np.zeros((len(measured),0)))
    supports=np.full((len(nodes),2),cfg['neutral_support'])
    for c in range(2):
        informative=(masses[c]>0)&active[c]
        if c==1: informative &= (pos[nodes,0]>0)&(observed[nodes]>0)
        supports[informative,c]=1/(1+scatter[c][informative]/radii[c])
    return dict(nodes=nodes,composition_mean=means[0],depth_mean=means[1],
        composition_scatter=scatter[0],depth_scatter=scatter[1],
        composition_mass=masses[0],depth_mass=masses[1],support=supports)


def select(tree, alternatives, lengths, ids, evidence, stats, cfg, root_only=False):
    """Compare supported whole/children; exclude internal roots without truth/K."""
    n=len(ids);roots=set(map(int,tree['roots']));breadth,excess,factors=marker_tables(tree,ids,evidence,cfg)
    # Reference lifetime is a bp-weighted inverse local core radius, not infinity.
    _,inv,_=reduce_moments(tree['children'],lengths.astype(np.float64),
        (1/np.maximum(tree['core'],1e-6))[:,None])
    mean_inverse=inv[:,0]/tree['mass'];best=np.zeros(len(alternatives));decisions=[];choose={}
    for cid in range(len(alternatives)-1,-1,-1):
        c=alternatives[cid];node=c['node'];root=node in roots and node>=n
        lifetime=c['stability']
        # A long isolated sequence has its own finite density radius. Markers
        # can inform quality but their absence alone cannot make its DNA noise.
        if not root_only and node<n and lengths[node]>=cfg['singleton_min_bp']:
            lifetime=max(lifetime,float(lengths[node])*max(0.,1/max(tree['core'][node],1e-6)-c['birth']))
        relative=lifetime/max(mean_inverse[node],1e-12)
        support=float(stats['support'][cid].mean())
        own=0. if root else c['stability']*factors[node] if root_only else relative*support*factors[node]
        child=sum(best[j] for j in c['children']);take=own>0 and (own>=child if root_only else own>child)
        choose[cid]=bool(take);best[cid]=own if take else child
        decisions.append(dict(candidate=cid,node=node,internal_root_excluded=root,own_utility=float(own),
            child_utility=float(child),whole_preferred=bool(take),relative_persistence_mass=float(relative),
            profile_support=stats['support'][cid].tolist(),marker_breadth=float(breadth[node]),
            marker_excess=float(excess[node]),marker_factor=float(factors[node]),
            reason='internal_root' if root else 'supported_whole' if take else 'children_or_abstention'))
    stack=[i for i,c in enumerate(alternatives) if c['parent']<0];kept=[]
    while stack:
        cid=stack.pop()
        if choose[cid]:kept.append(cid)
        else:stack.extend(alternatives[cid]['children'])
    return kept,sorted(decisions,key=lambda x:x['candidate'])


def bin_profiles(assign, coords, weights, positive, evidence, ids, cfg):
    """Aggregate fixed bin moments and physical calls for a synchronous pass."""
    labels=sorted(set(map(int,assign[assign>=0])));result={}
    for label in labels:
        rows=np.flatnonzero(assign==label);means=[];variance=[]
        for x,w in zip(coords,weights):
            mass=float(w[rows].sum());mu=(x[rows]*w[rows,None]).sum(0)/mass if mass else np.zeros(x.shape[1])
            means.append(mu);variance.append(max(0,float((np.square(x[rows]-mu).sum(1)*w[rows]).sum()/mass)) if mass else 0.)
        calls={}
        for i in rows:
            for f,v in evidence['calls'].get(ids[i],{}).items():calls.setdefault(f,[]).extend(v)
        result[label]=dict(rows=rows,mean=means,scatter=variance,positive=bool(positive[rows].any()),
            measured=bool(weights[1][rows].sum()>0),calls=calls)
    return result


def quality(calls, panel, cfg):
    """Return a soft physical-marker proxy; absent panel evidence remains neutral."""
    breadth=sum(max(v) for v in calls.values())/panel
    excess=sum(sum(v)-max(v) for v in calls.values())/panel
    return (1+breadth)/(1+cfg['marker_excess_penalty']*excess)


def marker_change(a, b, panel, cfg):
    """Bound a pooled-marker quality change; duplicates never trigger a hard veto."""
    pooled={k:list(v) for k,v in a.items()}
    for f,v in b.items():pooled.setdefault(f,[]).extend(v)
    before=min(quality(a,panel,cfg),quality(b,panel,cfg))
    return float(np.clip(quality(pooled,panel,cfg)/max(before,1e-12)-1,-1,1))


def compatibility(x, positive, center, radii, active, reliability, cfg, measured=True):
    """Combine channels additively, shrinking unreliable/absent evidence to neutral."""
    scores=[]
    for c in range(2):
        if not active[c] or (c==1 and (not measured or not center['measured'] or not (positive or center['positive']))):
            scores.append(cfg['neutral_support']);continue
        d=float(np.square(x[c]-center['mean'][c]).sum())
        s=1/(1+d/max(radii[c],center['scatter'][c],cfg['radius_floor']))
        scores.append(cfg['neutral_support']+reliability*(s-cfg['neutral_support']))
    return float(np.mean(scores))


def supported_updates(assign, nn, dd, coords, weights, measured, positive, lengths, ids, evidence, radii, active, cfg):
    """Make disjoint mutual merges, then one non-chaining bounded recruitment pass."""
    assign=assign.copy();panel=evidence['panel_size'];centers=bin_profiles(assign,coords,weights,positive,evidence,ids,cfg)
    pre_map={str(b):at for at,b in enumerate(sorted(centers,key=lambda b:min(ids[i] for i in centers[b]['rows'])))}
    votes={};outgoing={};k=nn.shape[1]
    # Each row contributes total vote <=1; base weighting prevents short-row count
    # dominating reciprocal bin evidence. Existing neighbor edges are the only path.
    for start in range(0,len(assign),cfg['profile_batch_rows']):
        stop=min(len(assign),start+cfg['profile_batch_rows'])
        for i in range(start,stop):
            a=int(assign[i])
            if a<0 or not k:continue
            w=1/np.maximum(dd[i],1e-6);w=w/w.sum()*lengths[i]
            for b in set(map(int,assign[nn[i]])):
                if b<0 or b==a:continue
                value=float(w[assign[nn[i]]==b].sum());votes[a,b]=votes.get((a,b),0.)+value
                outgoing[a]=outgoing.get(a,0.)+value
        if time.monotonic()%15<1:emit('construction_merge_votes',rows=stop,total=len(assign))
    best={}
    for (a,b),v in sorted(votes.items()):
        if a not in best or (v,-b)>(best[a][1],-best[a][0]):best[a]=(b,v)
    changes=[];used=set();merge_map={}
    for a in sorted(best):
        b=best[a][0]
        if a>=b or a in used or b in used or b not in best or best[b][0]!=a:continue
        ca,cb=centers[a],centers[b]
        # Fractions use all assigned-bin bp, including internal and abstaining
        # neighbor votes; external-only normalization would make weak bridges 1.
        ma=float(lengths[ca['rows']].sum());mb=float(lengths[cb['rows']].sum())
        reciprocal=min(votes[a,b]/ma,votes.get((b,a),0.)/mb)
        p=(compatibility(ca['mean'],ca['positive'],cb,radii,active,1.,cfg,ca['measured'])+
           compatibility(cb['mean'],cb['positive'],ca,radii,active,1.,cfg,cb['measured']))/2
        mark=marker_change(ca['calls'],cb['calls'],panel,cfg)
        score=.5*reciprocal+.5*p+cfg['marker_change_weight']*mark
        take=score>=cfg['merge_score']
        changes.append(dict(a=a,b=b,reciprocal_vote=reciprocal,profile=p,marker_change=mark,score=score,accepted=take))
        if take:used.update([a,b]);merge_map[b]=a
    for b,a in merge_map.items():assign[assign==b]=a
    centers=bin_profiles(assign,coords,weights,positive,evidence,ids,cfg);base=assign.copy()
    fixed_profiles={str(b):dict(member_local_rows=c['rows'].tolist(),
        mean=[x.tolist() for x in c['mean']],between_parent_scatter=c['scatter'],
        depth_measured=c['measured'],positive_measured_depth=c['positive'],
        marker_quality_proxy=quality(c['calls'],panel,cfg)) for b,c in centers.items()}
    reasons=[];counts={};last=time.monotonic()
    for i in np.flatnonzero(base<0):
        row=nn[i];label=base[row];w=1/np.maximum(dd[i],1e-6);total=float(w.sum());rank=[]
        for b in set(map(int,label[label>=0])):
            mask=label==b;rank.append((float(w[mask].sum()/total),b,int(mask.sum())))
        rank.sort(key=lambda z:(-z[0],z[1]));reason='no_assigned_neighbor';trace=dict(local_row=int(i),id=ids[i],depth='missing' if not measured[i] else 'positive' if positive[i] else 'measured_zero')
        if rank:
            vote,b,support=rank[0];runner=rank[1][0] if len(rank)>1 else 0.
            reason='insufficient_support' if support<cfg['recruit_min_support'] else 'vote_abstention' if vote<cfg['recruit_vote_fraction'] else 'ambiguous_bin' if runner and vote/runner<cfg['recruit_margin_ratio'] else 'context_abstention'
            reliability=float(lengths[i]/(lengths[i]+cfg['length_scale_bp']))
            p=compatibility([x[i] for x in coords],bool(positive[i]),centers[b],radii,active,reliability,cfg,bool(measured[i]))
            mark=marker_change(centers[b]['calls'],evidence['calls'].get(ids[i],{}),panel,cfg)
            score=.5*vote+.5*p+cfg['marker_change_weight']*mark
            if reason=='context_abstention' and score>=cfg['recruit_score']:reason='recruited';assign[i]=b
            trace.update(bin=b,vote=vote,runner=runner,support=support,profile=p,marker_change=mark,score=score)
        trace['reason']=reason;reasons.append(trace);counts[reason]=counts.get(reason,0)+1
        if time.monotonic()-last>=5:emit('construction_recruitment',reviewed=len(reasons),total=int((base<0).sum()));last=time.monotonic()
    labels=sorted(set(map(int,assign[assign>=0])),key=lambda b:min(ids[i] for i in np.flatnonzero(assign==b)))
    post_map={str(b):at for at,b in enumerate(labels)}
    return assign,dict(merge_candidates=changes,merge_map={str(b):int(a) for b,a in merge_map.items()},recruitment=reasons,recruitment_counts=counts,
        fixed_post_merge_profiles=fixed_profiles,pre_internal_to_canonical=pre_map,post_internal_to_canonical=post_map,
        label_scope='Trace bin labels are internal pre-antichain IDs; explicit maps bind canonical pre/post exports. Local rows index retained selected opaque-ID order.',
        synchronous=True,recruited_rows_can_recruit=False,profiles_fixed_before_recruitment=True)


def construct(data, vectors, valid, a, tree, alternatives, evidence, cfg):
    """Construct root-only, profile-pre and supported-post full-DNA partitions."""
    selected=a['selected'];ids=data['ids'][selected].tolist();axis=set(ids);n=len(ids)
    physical=dict(evidence,calls={k:v for k,v in evidence['calls'].items() if k in axis})
    coords,weights,measured,positive,radii,active,calibration=profiles(data,valid,selected,a['neighbors'],cfg)
    stats=candidate_profiles(tree,alternatives,coords,weights,measured,positive,radii,active,cfg)
    parts={};choices={};pre=None
    for arm,control in [('root-only',True),('pre',False)]:
        chosen,decision=select(tree,alternatives,data['lengths'][selected],ids,physical,stats,cfg,control)
        assignment=np.full(n,-1,np.int64)
        for label,cid in enumerate(chosen):
            rows=list(density.leaves(tree,alternatives[cid]['node'],n));require(np.all(assignment[rows]<0),'Overlapping antichain')
            assignment[rows]=label
        if not control:pre=assignment
        groups=[selected[np.flatnonzero(assignment==label)].tolist() for label in sorted(set(assignment[assignment>=0]))]
        parts[arm]=canonical_partition(data['ids'].tolist(),valid,groups,data['lengths'],cfg,
            ['supported_construction_abstention' if v else 'method_excluded_no_geometry' for v in valid])
        choices[arm]=decision
    final,updates=supported_updates(pre,a['neighbors'],a['distances'],coords,weights,measured,positive,
        data['lengths'][selected],ids,physical,radii,active,cfg)
    groups=[selected[np.flatnonzero(final==label)].tolist() for label in sorted(set(final[final>=0]))]
    parts['post']=canonical_partition(data['ids'].tolist(),valid,groups,data['lengths'],cfg,
        ['supported_construction_abstention' if v else 'method_excluded_no_geometry' for v in valid])
    return parts,choices,stats,calibration,updates


def run(features,embeddings,graph,evidence_path,accepted,output,cfg=None):
    """Restore accepted science and publish fresh candidate artifacts, no refitting."""
    cfg=cfg or policy();out=Path(output);out.mkdir(parents=True,exist_ok=False)
    data,vectors,valid,meta,a,tree,alternatives,evidence=restore(features,embeddings,graph,evidence_path,accepted)
    emit('construction_start',rows=len(data['ids']),eligible=int(valid.sum()),candidates=len(alternatives))
    parts,choices,stats,calibration,updates=construct(data,vectors,valid,a,tree,alternatives,evidence,cfg)
    for name,part in parts.items():
        part.update(parent_features_sha256=digest(features),embedding_sha256=digest(embeddings),graph_sha256=digest(graph),
            config=cfg,algorithm='root-safe relative persistence / biological profiles / soft physical markers / synchronous supported updates',scientific_quality_assessed=False)
        write_json(out/(name+'-partition.json'),part)
    for name,value in choices.items():write_json(out/(name+'-choices.json'),value)
    save(out/'candidate-profiles.npz',stats,dict(kind='supported_candidate_profiles',calibration=calibration),data['ids'])
    write_json(out/'profile-calibration.json',calibration);write_json(out/'updates.json',updates)
    write_json(out/'accepted-reuse.json',dict(accepted_root=str(accepted),completed=binding(Path(accepted)/'completed.json'),
        files=json.loads((Path(accepted)/'completed.json').read_text())['files'],no_retrieval_MST_training_detection=True))
    files={p.name:binding(p) for p in out.iterdir() if p.is_file()}
    record=dict(status='SUCCESS',config=cfg,rows=len(valid),eligible=int(valid.sum()),bp=int(data['lengths'].sum()),samples=meta['samples'],
        input_sha256={k:digest(p) for k,p in dict(features=features,embeddings=embeddings,graph=graph,evidence=evidence_path).items()},
        accepted=binding(Path(accepted)/'completed.json'),files=files,full_DNA_preserved=True,truth_accessed=False)
    write_json(out/'completed.json',record);return record


def audit(features,embeddings,graph,evidence_path,accepted,output,cfg=None):
    """Reproduce only new cached choices/updates and validate full partitions."""
    cfg=cfg or policy();out=Path(output);record=json.loads((out/'completed.json').read_text())
    require(record['status']=='SUCCESS' and record['config']==cfg and all(binding(out/n)==v for n,v in record['files'].items()),
        'New construction result member/policy differs')
    data,vectors,valid,meta,a,tree,alternatives,evidence=restore(features,embeddings,graph,evidence_path,accepted)
    require(record['accepted']==binding(Path(accepted)/'completed.json') and record['input_sha256']==
        {k:digest(p) for k,p in dict(features=features,embeddings=embeddings,graph=graph,evidence=evidence_path).items()},'New result input binding differs')
    parts,choices,stats,calibration,updates=construct(data,vectors,valid,a,tree,alternatives,evidence,cfg)
    arrays,am=load(out/'candidate-profiles.npz','supported_candidate_profiles',data['ids'])
    require(am['calibration']==calibration and all(np.array_equal(arrays[k],v) for k,v in stats.items()),'Cached profile moments/reload differ')
    require(calibration==json.loads((out/'profile-calibration.json').read_text()) and updates==json.loads((out/'updates.json').read_text()),
        'Cached profile/update provenance differs')
    for arm,expected in parts.items():
        part=validate_partition(data,out/(arm+'-partition.json'),features)
        require(all(part[k]==expected[k] for k in ['ids','assignment','valid','clusters','unassigned','reason']),
            'Full-DNA construction partition reload differs')
    for arm,value in choices.items():require(value==json.loads((out/(arm+'-choices.json')).read_text()),'Cached whole/child choices differ')
    return dict(status='PASS',full_contig_axis=True,ordered_samples=meta['samples'],complete_DNA=True,
        retained_neighbors_forest_vectors_unchanged=True,no_MST_neighbors_or_model_rebuilt=True,
        root_only_pre_post_verified=True,truth_accessed=False)
