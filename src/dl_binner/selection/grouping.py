"""Integrate cached biological candidates without training or new retrievals.

Inputs are source-blind contig axes, two retained forests/neighbor contexts,
physical-locus marker weights and measured parent-contig means. Shared membership
orders keep hierarchy storage linear. Truth has no interface in this module.
"""
from dataclasses import dataclass
import json
from pathlib import Path
import time

import numpy as np
from numba import njit

from ..candidate.grouping import canonical_partition
from ..construction import grouping as old
from ..context.tokens import binding
from ..information.grouping import require
from ..information.export import validate_partition, export
from ..io import digest, emit, write_json
from ..multiview.arrays import load_arrays
from ..unified import grouping as unified

DEFAULT = dict(version=1, seed=11, min_bin_contigs=1, min_bin_bp=10000,
    marker_negative_min_bp=200000, marker_excess_penalty=5., profile_weight=.25,
    size_scale_bp=200000, recruit_min_support=2, recruit_vote_fraction=2/3,
    recruit_margin_ratio=1.5, recruit_score=.6, update_tolerance=1e-12,
    root_policy='exclude_internal_forest_roots', residual_policy='fixed_order_once')


def policy(path=None):
    """Admit the sole prospectively frozen policy; refuse unknown/grid overrides."""
    value = dict(DEFAULT) if path is None else json.loads(Path(path).read_text())
    require(value == DEFAULT and all(type(value[k]) is type(v) for k,v in DEFAULT.items()),
            'Unfrozen biological candidate-selection policy')
    return value


def score(bp, breadth, excess, support, cfg):
    """Combine soft physical markers and measured-profile coherence, without truth."""
    if not (bp >= 0 and np.isfinite([breadth,excess,*support]).all()
            and breadth >= 0 and excess >= -1e-12 and len(support) == 2):
        raise ValueError('Malformed candidate quality evidence')
    return float(breadth-cfg['marker_excess_penalty']*max(0.,excess)
        +cfg['profile_weight']*(2*float(np.mean(support))-1)
        *np.sqrt(bp/(bp+cfg['size_scale_bp'])))


def admissible(stats, cfg):
    """Retain a marker-negative path while refusing unsupported tiny fragments."""
    return (stats['bp'] >= cfg['min_bin_bp'] and stats['score'] > 0
        and (stats['breadth'] > 0 or stats['bp'] >= cfg['marker_negative_min_bp']))


@njit(cache=True)
def occupancy_update(bit, indices, delta):
    """Update one shared Fenwick occupancy index in O(rows log n), in place."""
    for i in indices:
        at = i+1
        while at < len(bit):
            bit[at] += delta
            at += at & -at


@njit(cache=True)
def occupancy_count(bit, lo, hi):
    """Return remaining rows in a half-open membership interval."""
    value = 0
    for at0, sign in ((hi,1),(lo,-1)):
        at = at0
        while at:
            value += sign*bit[at]
            at -= at & -at
    return value


@dataclass
class Membership:
    """Share a row permutation, inverse positions and remaining-row index."""
    order: np.ndarray
    inverse: np.ndarray
    bit: np.ndarray

    @classmethod
    def create(cls, order, n):
        """Create one complete eligible-axis permutation, refusing duplicate IDs."""
        order = np.asarray(order,np.int64)
        require(len(order)==n and np.array_equal(np.sort(order),np.arange(n)),
                'Candidate membership is not a full eligible permutation')
        inverse=np.empty(n,np.int64);inverse[order]=np.arange(n)
        bit=np.zeros(n+1,np.int64)
        occupancy_update(bit,np.arange(n,dtype=np.int64),1)
        return cls(order,inverse,bit)


def forest_layout(tree):
    """Return linear DFS leaf order/ranges; reject malformed or shared branches."""
    children=np.asarray(tree['children']);size=len(children)
    n=len(tree['core']);roots=np.asarray(tree['roots'])
    require(children.shape==(size,2) and children.dtype.kind in 'iu'
        and n<=size<=max(n,2*n-1) and np.all(children[:n]==-1)
        and roots.ndim==1 and roots.dtype.kind in 'iu', 'Malformed cached forest shape')
    seen=np.zeros(size,np.int8);lo=np.empty(size,np.int64);hi=np.empty(size,np.int64)
    order=[]
    for root in roots:
        stack=[(int(root),False)]
        while stack:
            node,after=stack.pop()
            require(0<=node<size,'Cached forest node escaped')
            if after:
                hi[node]=len(order)
                continue
            require(seen[node]==0,'Cached forest cycle/shared child/root')
            seen[node]=1;lo[node]=len(order)
            if node<n:
                order.append(node);hi[node]=len(order)
            else:
                a,b=map(int,children[node])
                require(0<=a<b<node,'Cached forest children are not topological')
                stack.extend([(node,True),(b,False),(a,False)])
    require(np.all(seen==1) and sorted(order)==list(range(n)),
            'Cached forest misses rows/nodes')
    return np.asarray(order,np.int64),lo,hi


def group_layout(assign):
    """Store a complete partition once and return only its assigned-bin ranges."""
    assign=np.asarray(assign,np.int64);order=np.argsort(assign,kind='stable')
    values=assign[order];ranges=[]
    starts=np.r_[0,np.flatnonzero(values[1:]!=values[:-1])+1]
    ends=np.r_[starts[1:],len(values)]
    for a,b in zip(starts,ends):
        if values[a]>=0:ranges.append((int(values[a]),int(a),int(b)))
    return order,ranges


def measured_stats(rows,coords,weights,measured,positive,lengths,ids,evidence,radii,active,cfg):
    """Compute a bin proxy from actual parent rows and cached weighted loci.

    Scatter is between contig means. Missing depth and co-zero depth remain
    distinct observations, both neutral when they supply no informative contrast.
    """
    rows=np.asarray(rows,np.int64);means=[];scatters=[];supports=[];masses=[]
    for c,(x,w) in enumerate(zip(coords,weights)):
        mass=float(w[rows].sum());masses.append(mass)
        mean=(x[rows]*w[rows,None]).sum(0)/mass if mass else np.zeros(x.shape[1])
        scatter=max(0.,float((np.square(x[rows]-mean).sum(1)*w[rows]).sum()/mass)) if mass else 0.
        informative=bool(active[c] and mass>0 and (c==0 or positive[rows].any()))
        supports.append(float(1/(1+scatter/radii[c])) if informative else .5)
        means.append(mean);scatters.append(scatter)
    calls={}
    for i in rows:
        for family,values in evidence['calls'].get(ids[int(i)],{}).items():
            calls.setdefault(family,[]).extend(values)
    panel=evidence['panel_size']
    breadth=sum(max(v) for v in calls.values())/panel
    excess=sum(sum(v)-max(v) for v in calls.values())/panel
    bp=int(lengths[rows].sum())
    return dict(bp=bp,rows=len(rows),breadth=float(breadth),excess=float(max(0.,excess)),
        support=supports,score=score(bp,breadth,excess,supports,cfg),
        min_row=int(rows.min()) if len(rows) else -1),dict(rows=rows,mean=means,scatter=scatters,
        measured=bool(measured[rows].any()),positive=bool(positive[rows].any()),calls=calls)


def candidate_pool(data,valid,a,trees,partitions,evidence,cfg):
    """Build shared-membership candidate descriptors and additive full scores."""
    selected=a['selected'];n=len(selected);ids=data['ids'][selected].tolist()
    require(ids==sorted(ids) and len(set(ids))==n,'Eligible opaque-ID axis must be sorted/unique')
    axis=set(ids)
    physical=dict(evidence,calls={k:v for k,v in evidence['calls'].items() if k in axis})
    unified.validate_evidence(physical,ids)
    coords,weights,measured,positive,radii,active,calibration=old.profiles(data,valid,selected,a['neighbors'],old.policy())
    lengths=data['lengths'][selected];views=[];candidates=[];internal_roots=[]
    inverse_global=np.full(len(valid),-1,np.int64);inverse_global[selected]=np.arange(n)
    for name,tree,alternatives,global_axis in trees:
        local=inverse_global[np.asarray(global_axis)]
        require(np.array_equal(np.sort(local),np.arange(n)),'Retained forest eligibility differs')
        order,lo,hi=forest_layout(tree)
        view=len(views);views.append(Membership.create(local[order],n))
        local_coords=tuple(x[local] for x in coords);local_weights=tuple(w[local] for w in weights)
        stats=old.candidate_profiles(tree,alternatives,local_coords,local_weights,
            measured[local],positive[local],radii,active,old.policy())
        b,x,_=old.marker_tables(tree,[ids[int(i)] for i in local],physical,old.policy())
        minimum=np.empty(len(tree['mass']),np.int64);minimum[:n]=local
        for node in range(n,len(minimum)):
            left,right=tree['children'][node];minimum[node]=min(minimum[left],minimum[right])
        roots=set(map(int,tree['roots']))
        for node in roots:
            if node>=n:internal_roots.append(np.sort(local[order[lo[node]:hi[node]]]))
        for at,alternative in enumerate(alternatives):
            node=int(alternative['node'])
            require(0<=node<len(lo),'Candidate node escaped retained forest')
            if node>=n and node in roots:continue
            bp=int(tree['mass'][node]);support=stats['support'][at].tolist()
            candidates.append(dict(key=name+':'+str(node),view=view,lo=int(lo[node]),hi=int(hi[node]),
                bp=bp,rows=int(hi[node]-lo[node]),breadth=float(b[node]),excess=float(x[node]),support=support,
                score=score(bp,b[node],x[node],support,cfg),min_row=int(minimum[node]),kind='hierarchy'))
        # Long singletons may be absent from the condensed alternatives.
        existing={int(v['node']) for v in alternatives}
        for node in np.flatnonzero(data['lengths'][global_axis]>=cfg['marker_negative_min_bp']):
            if int(node) in existing:continue
            rows=np.array([local[node]],np.int64)
            s,_=measured_stats(rows,coords,weights,measured,positive,lengths,ids,physical,radii,active,cfg)
            candidates.append(dict(s,key=name+':leaf:'+str(node),view=view,
                lo=int(lo[node]),hi=int(hi[node]),kind='long_singleton'))
    for name,part in partitions:
        require(part['ids']==data['ids'].tolist() and np.array_equal(part['valid'],valid),
                'Retained partition full axes differ')
        assign=np.array([-1 if v is None else v for v in part['assignment']],np.int64)[selected]
        order,ranges=group_layout(assign);view=len(views);views.append(Membership.create(order,n))
        for label,lo,hi in ranges:
            rows=order[lo:hi]
            if any(len(r)==len(rows) and np.array_equal(np.sort(rows),r) for r in internal_roots):
                continue
            s,_=measured_stats(rows,coords,weights,measured,positive,lengths,ids,physical,radii,active,cfg)
            candidates.append(dict(s,key=name+':bin:'+str(label),view=view,lo=lo,hi=hi,kind='partition'))
    return candidates,views,(coords,weights,measured,positive,lengths,ids,physical,radii,active),calibration


def select(candidates,views,context,cfg):
    """Select one disjoint partition in fixed priority order, rescoring residuals once."""
    coords,weights,measured,positive,lengths,ids,evidence,radii,active=context
    assign=np.full(len(ids),-1,np.int64);trace=[];bins=[];last=time.monotonic()
    order=sorted(range(len(candidates)),key=lambda j:(-candidates[j]['score'],-candidates[j]['bp'],
                    ids[candidates[j]['min_row']],candidates[j]['key']))
    for pos,index in enumerate(order):
        c=candidates[index];view=views[c['view']]
        left=int(occupancy_count(view.bit,c['lo'],c['hi']))
        record=dict(candidate=index,key=c['key'],original_score=c['score'],remaining_rows=left)
        reason='fully_claimed'
        if left==c['rows'] and not admissible(c,cfg):
            # No residual exists to improve the proxy. Avoid enumerating every
            # long unsupported ancestor in an unbalanced retained hierarchy.
            record.update(reason='proxy_abstention',residual=False,
                stats={k:c[k] for k in ['bp','rows','breadth','excess','support','score']})
            trace.append(record)
            continue
        if left:
            rows=view.order[c['lo']:c['hi']];rows=rows[assign[rows]<0]
            require(len(rows)==left,'Shared candidate occupancy differs')
            stats=c
            if left!=c['rows']:
                stats,_=measured_stats(rows,coords,weights,measured,positive,lengths,ids,evidence,radii,active,cfg)
            record.update(residual=left!=c['rows'],stats={k:stats[k] for k in ['bp','rows','breadth','excess','support','score']})
            reason='proxy_abstention'
            if admissible(stats,cfg):
                label=len(bins);assign[rows]=label;bins.append(rows)
                for other in views:occupancy_update(other.bit,other.inverse[rows],-1)
                record['selected_bin']=label;reason='selected_whole' if left==c['rows'] else 'selected_residual'
        record['reason']=reason;trace.append(record)
        if time.monotonic()-last>=5:
            emit('selection_candidates',processed=pos+1,total=len(order),bins=len(bins));last=time.monotonic()
    return assign,trace


@njit(cache=True)
def propose(assign,near0,dist0,near1,dist1,minimum,fraction,margin):
    """Aggregate two normalized cached geometries and distinct support, in O(n*k²)."""
    n=len(assign);labels=np.full(n,-1,np.int64);votes=np.zeros(n);support=np.zeros(n,np.int64);runner=np.zeros(n)
    for i in range(n):
        if assign[i]>=0:continue
        size=near0.shape[1]+near1.shape[1]
        seen=np.empty(size,np.int64);bs=np.empty(size,np.int64);ws=np.zeros(size);counts=np.zeros(size,np.int64)
        used=0;visited=0
        for which in range(2):
            near=near0 if which==0 else near1;dist=dist0 if which==0 else dist1
            den=0.
            for j in range(near.shape[1]):den+=1/max(dist[i,j],1e-6)
            if den<=0:continue
            for j in range(near.shape[1]):
                q=near[i,j];b=assign[q]
                if b<0:continue
                at=0
                while at<used and bs[at]!=b:at+=1
                if at==used:bs[used]=b;used+=1
                ws[at]+=.5/max(dist[i,j],1e-6)/den
                known=False
                for z in range(visited):
                    if seen[z]==q:known=True;break
                if not known:seen[visited]=q;visited+=1;counts[at]+=1
        best=-1;value=-1.;second=0.
        for at in range(used):
            if ws[at]>value or (ws[at]==value and bs[at]<bs[best]):
                second=max(0.,value);best=at;value=ws[at]
            elif ws[at]>second:second=ws[at]
        if best>=0:
            votes[i]=value;support[i]=counts[best];runner[i]=second
            if counts[best]>=minimum and value>=fraction and (second==0 or value>=margin*second):labels[i]=bs[best]
    return labels,votes,support,runner


def joint_updates(assign,neighbors,context,cfg):
    """Freeze individual proposals, then accept/reject each entire bin update jointly."""
    coords,weights,measured,positive,lengths,ids,evidence,radii,active=context
    before=assign.copy();result=assign.copy();oldcfg=old.policy()
    # One stable grouping avoids rescanning all n rows for every bin.
    order,ranges=group_layout(before);centers={};stats={}
    for b,lo,hi in ranges:
        stats[b],centers[b]=measured_stats(order[lo:hi],coords,weights,measured,positive,lengths,ids,evidence,radii,active,cfg)
    numeric=[(np.ascontiguousarray(nn,dtype=np.int64),np.ascontiguousarray(dd,dtype=np.float64))
             for nn,dd in neighbors]
    proposal,votes,support,runner=propose(before,*numeric[0],*numeric[1],
        cfg['recruit_min_support'],cfg['recruit_vote_fraction'],cfg['recruit_margin_ratio'])
    trace=[]
    for i in np.flatnonzero(before<0):
        b=int(proposal[i]);why='vote_abstention';p=None
        if b>=0:
            reliability=float(lengths[i]/(lengths[i]+oldcfg['length_scale_bp']))
            p=old.compatibility([x[i] for x in coords],bool(positive[i]),centers[b],
                radii,active,reliability,oldcfg,bool(measured[i]))
            if .5*votes[i]+.5*p<cfg['recruit_score']:proposal[i]=-1;why='profile_abstention'
            else:why='proposed_pending_joint_check'
        trace.append(dict(local_row=int(i),id=ids[i],bin=b if b>=0 else None,vote=float(votes[i]),
            distinct_support=int(support[i]),runner=float(runner[i]),profile=p,reason=why,
            depth='unavailable' if not measured[i] else 'positive' if positive[i] else 'measured_zero'))
    group_order,groups=group_layout(proposal);changes=[]
    for b,lo,hi in groups:
        extra=group_order[lo:hi];rows=np.r_[centers[b]['rows'],extra]
        after,_=measured_stats(rows,coords,weights,measured,positive,lengths,ids,evidence,radii,active,cfg)
        take=admissible(after,cfg) and after['score']+cfg['update_tolerance']>=stats[b]['score']
        if take:result[extra]=b
        changes.append(dict(bin=b,before=stats[b],proposed_after=after,proposed_rows=extra.tolist(),
            accepted=bool(take),reason='joint_proxy_non_decrease' if take else 'unchanged_alternative_retained'))
    accepted={c['bin']:c['accepted'] for c in changes}
    for value in trace:
        if value['reason']=='proposed_pending_joint_check':
            value['reason']='recruited_joint' if accepted[value['bin']] else 'joint_update_abstention'
    return result,dict(groups=changes,proposals=trace,synchronous=True,chaining=False,
        within_contig_depth_variance_used=False,truth_accessed=False)


def restore(features,embeddings,graph,evidence_path,work):
    """Read only already verified E031 members, exact native axes and retained forests."""
    root=Path(work)
    # Exact whole archive/member admission is a caller prerequisite, additionally
    # required by its immutable restore receipt; no acquisition/rebuild fallback.
    receipt=json.loads((root.parent/'restore-admission.json').read_text())
    require(receipt['status']=='PASS' and receipt['every_member_verified'] is True
        and receipt['omitted_work_members']==0,'Verified E031 restore admission required')
    unit=root.name
    paths=[Path(features),Path(features).with_suffix('.json'),Path(embeddings),
        Path(embeddings).with_suffix('.json'),Path(graph),Path(graph).with_suffix('.json'),Path(evidence_path)]
    for p in paths:
        require(not p.is_symlink(),'Scientific input links refused')
    from ..information.grouping import load_inputs
    data,vectors,valid,meta=load_inputs(features,embeddings)
    evidence=json.loads(Path(evidence_path).read_text());unified.validate_evidence(evidence,data['ids'].tolist())
    forest_root=root/'forest/result';e023_root=root/'e023/science/result'
    expected={k:digest(p) for k,p in dict(features=features,embeddings=embeddings,graph=graph,evidence=evidence_path).items()}
    closed=json.loads((forest_root/'completed.json').read_text())
    require(closed['status']=='SUCCESS' and closed['input_sha256']==expected,
            'Retained forest belongs to different feature/vector/marker bytes')
    from ..calibrated.arrays import load
    from ..discovery import exact
    (data,vectors,valid,meta,cache),cm=exact.restore(
        features,embeddings,graph,forest_root/'retrieval')
    tree,tm=load(forest_root/'forest.npz','unified_density_forest',data['ids'])
    alt=json.loads((forest_root/'alternatives.json').read_text())
    a=dict(selected=cache['selected'],neighbors=cache['neighbors'],distances=cache['distances'])
    old.forest_contract(tree,data,a['selected'],a['neighbors'],a['distances'])
    hierarchy,hm=load_arrays(e023_root/'hierarchy.npz','density_hierarchy')
    closed023=json.loads((e023_root/'completed.json').read_text())
    require(closed023['status']=='SUCCESS' and closed023['marker_evidence_sha256']==expected['evidence'],
            'Retained E023 physical marker provenance differs')
    require(np.array_equal(hierarchy['ids'],data['ids'])
        and hm['features_sha256']==digest(features) and hm['embedding_sha256']==digest(embeddings)
        and hm['original_graph_sha256']==digest(graph),'E023 retained hierarchy provenance differs')
    alt023=json.loads((e023_root/'alternatives.json').read_text())
    parts=[]
    for name,p in [('E023-density',e023_root/'density-partition.json'),
                   ('E023-selected',e023_root/'selected-partition.json')]:
        parts.append((name,validate_partition(data,p,features)))
    for name in ['root-only','pre','post']:
        parts.append(('E030-'+name,validate_partition(data,root/'construct/result'/(name+'-partition.json'),features)))
    inverse=np.full(len(valid),-1,np.int64);inverse[a['selected']]=np.arange(len(a['selected']))
    other=inverse[hierarchy['selected']];back=np.argsort(other)
    require(np.array_equal(np.sort(other),np.arange(len(other))),'Neighbor eligible axes differ')
    nn023=other[hierarchy['neighbors'][back]];dd023=hierarchy['distances'][back]
    trees=[('E030',tree,alt,a['selected']),('E023',hierarchy,alt023,hierarchy['selected'])]
    return data,vectors,valid,meta,a,trees,parts,evidence,[(a['neighbors'],a['distances']),(nn023,dd023)]


def construct(data,valid,a,trees,partitions,evidence,neighbors,cfg):
    """Return one selected and one jointly recruited partition, preserving all DNA."""
    pool,views,context,calibration=candidate_pool(data,valid,a,trees,partitions,evidence,cfg)
    selected,choices=select(pool,views,context,cfg)
    post,updates=joint_updates(selected,neighbors,context,cfg)
    parts={}
    for name,assign in [('pre',selected),('post',post)]:
        order,ranges=group_layout(assign)
        groups=[a['selected'][order[lo:hi]].tolist() for b,lo,hi in ranges]
        parts[name]=canonical_partition(data['ids'].tolist(),valid,groups,data['lengths'],cfg,
            ['candidate_selection_abstention' if v else 'method_excluded_no_geometry' for v in valid])
    return parts,pool,views,choices,calibration,updates


def run(features,embeddings,graph,evidence_path,work,fasta,output,cfg=None):
    """Publish new candidate evidence and full pre/post exports; no old science replay."""
    cfg=cfg or policy();out=Path(output);out.mkdir(parents=True,exist_ok=False)
    inputs={str(Path(p).absolute()):binding(p) for p in [features,embeddings,graph,evidence_path,fasta]}
    data,vectors,valid,meta,a,trees,partitions,evidence,neighbors=restore(features,embeddings,graph,evidence_path,work)
    parts,pool,views,choices,calibration,updates=construct(data,valid,a,trees,partitions,evidence,neighbors,cfg)
    write_json(out/'candidates.json',pool);write_json(out/'choices.json',choices)
    write_json(out/'updates.json',updates);write_json(out/'calibration.json',calibration)
    with (out/'membership.npz').open('xb') as stream:
        np.savez_compressed(stream,**{'order_'+str(i):v.order for i,v in enumerate(views)})
    accounts={}
    for name,part in parts.items():
        part.update(parent_features_sha256=digest(features),embedding_sha256=digest(embeddings),
            graph_sha256=digest(graph),config=cfg,algorithm='common biological candidate selection / joint recruitment',scientific_quality_assessed=False)
        write_json(out/(name+'-partition.json'),part)
        accounts[name]=export(features,out/(name+'-partition.json'),fasta,out/'export'/name,include_dna=False)
    require(all(binding(p)==v for p,v in inputs.items()),'Retained input mutated')
    files={str(p.relative_to(out)):binding(p) for p in out.rglob('*') if p.is_file()}
    record=dict(status='SUCCESS',config=cfg,inputs=inputs,files=files,rows=len(valid),eligible=int(valid.sum()),
        bp=int(data['lengths'].sum()),samples=meta['samples'],candidates=len(pool),accounts=accounts,
        unchanged_learning=True,unchanged_neighbors_forests=True,truth_accessed=False)
    write_json(out/'completed.json',record);return record


def audit(features,embeddings,graph,evidence_path,work,output,cfg=None):
    """Independently reproduce new cached decisions and require full export reload."""
    cfg=cfg or policy();out=Path(output);m=json.loads((out/'completed.json').read_text())
    require(m['status']=='SUCCESS' and m['config']==cfg and
        all(binding(out/n)==v for n,v in m['files'].items()),'New selection byte/policy drift')
    data,vectors,valid,meta,a,trees,partitions,evidence,neighbors=restore(features,embeddings,graph,evidence_path,work)
    parts,pool,views,choices,calibration,updates=construct(data,valid,a,trees,partitions,evidence,neighbors,cfg)
    for name,value in [('candidates',pool),('choices',choices),('calibration',calibration),('updates',updates)]:
        require(json.loads((out/(name+'.json')).read_text())==value,'Cached new decision reload differs: '+name)
    with np.load(out/'membership.npz',allow_pickle=False) as arrays:
        require(set(arrays.files)=={'order_'+str(i) for i in range(len(views))}
            and all(np.array_equal(arrays['order_'+str(i)],v.order) for i,v in enumerate(views)),
            'Shared membership reload differs')
    for name,part in parts.items():
        actual=validate_partition(data,out/(name+'-partition.json'),features)
        require(all(actual[k]==part[k] for k in ['ids','assignment','valid','clusters','unassigned','reason']),
                'New complete DNA partition differs')
        accounts=json.loads((out/'export'/name/'manifest.json').read_text())
        require(accounts['bp']==int(data['lengths'].sum()),'New complete DNA export differs')
    return dict(status='PASS',rows=len(valid),bp=int(data['lengths'].sum()),samples=meta['samples'],
        candidate_decisions_reproduced=True,complete_DNA=True,retained_geometry_unchanged=True,
        new_neighbors_or_fit=False,truth_accessed=False)
