"""Preserved CPM-density and E013 refinement interfaces for new representations.

The graph construction is dev4's audited positive symmetric kNN weighting;
Leiden runs CPM directly, with gamma=median(weight)/neighbors. No RB partition
is computed. E013's pure selector is copied byte-for-byte as owned project code;
its policy is not tuned here. Truth cannot enter either interface.
"""
from collections import defaultdict
import json
from pathlib import Path

import numpy as np

from ..io import digest,load_arrays,save_arrays,write_json,emit
from ..candidate.grouping import canonical_partition,neighbor_graph,refine_partition
from ..candidate.markers import load_cache
from .views import load


REFINEMENT_CONFIG=dict(context_epsilon=1.4210854715202004e-14,excess_penalty=5.,lloyd_iterations=10,
                       min_seed_families=2,physical_overlap_fraction=.5,seed=11,seed_reliability=.5)


def group(embeddings,features,output,cfg,threads):
    """Build one sparse graph and one frozen-rule CPM parent, preserving every row."""
    import igraph as ig
    import leidenalg
    data,meta=load(features);a,em=load_arrays(embeddings,'embeddings')
    ids=data['ids'].tolist();valid=data['eligible']&a['evidence']
    if (a['ids'].tolist()!=ids or em['features_sha256']!=digest(features)
            or a['features'].shape!=(len(ids),cfg['output']) or not np.isfinite(a['features']).all()
            or not np.allclose(np.linalg.norm(a['features'][valid],axis=1),1,atol=1e-5)
            or np.any(a['features'][~valid])):raise ValueError('Multiview unit embedding/feature axes differ')
    selected=np.array(sorted(np.flatnonzero(valid),key=lambda i:ids[i]),np.int64);x=a['features'][selected]
    nn,scores,audit=neighbor_graph(x,[ids[i] for i in selected],cfg,threads)
    sigma=np.maximum(2-2*scores[:,-1],1e-6) if nn.shape[1] else np.ones(len(x));edges={}
    for i,candidates in enumerate(nn):
        for at,j in enumerate(candidates):
            if scores[i,at]<=0:continue
            pair=min(i,int(j)),max(i,int(j));distance=max(0,2-2*scores[i,at])
            edges[pair]=float(np.exp(-distance/np.sqrt(sigma[i]*sigma[j])))
    ordered=sorted(edges);weights=np.array([edges[e] for e in ordered],np.float64)
    gamma=float(np.median(weights))/cfg['neighbors'] if len(weights) else None
    if ordered:
        native=ig.Graph(n=len(selected),edges=ordered,directed=False)
        partition=leidenalg.find_partition(native,leidenalg.CPMVertexPartition,weights=weights.tolist(),
            node_sizes=[1]*len(selected),resolution_parameter=gamma,seed=cfg['seed'],n_iterations=cfg['leiden_iterations'])
        groups=[[int(selected[j]) for j in c] for c in partition]
    else:groups=[]
    result=canonical_partition(ids,valid,groups,data['lengths'],cfg)
    neighbors=[[] for _ in ids];full=np.full((len(ids),nn.shape[1]),-1,np.int64)
    for i,index in enumerate(selected):neighbors[index]=[ids[selected[j]] for j in nn[i,:5]];full[index]=selected[nn[i]]
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    save_arrays(out/'graph.npz',dict(ids=data['ids'],neighbors=full,
        edges=np.array([(selected[i],selected[j]) for i,j in ordered],np.int64).reshape(-1,2),weights=weights),
        dict(kind='candidate_sparse_graph',metric=em['metric'],embedding_sha256=digest(embeddings),audit=audit))
    result.update(neighbors=neighbors,parent_features_sha256=digest(features),embedding_sha256=digest(embeddings),
        graph_sha256=digest(out/'graph.npz'),algorithm='positive weighted symmetric kNN / sole Leiden CPM',audit=audit,config=cfg,
        objective=dict(gamma=gamma,rule='median_positive_retained_edge_weight / frozen_neighbor_count',node_sizes=1,
                       seed=cfg['seed'],n_iterations=cfg['leiden_iterations']),transform='none; learned unit sphere preserved')
    write_json(out/'partition.json',result);emit('multiview_CPM_complete',rows=len(ids),edges=len(ordered),clusters=result['clusters'])


def profile_headers(path):
    """Read HMM trusted header fields only, without searching any new DNA."""
    result={};current={}
    with Path(path).open() as f:
        for line in f:
            key,_,value=line.strip().partition(' ')
            if key in ['NAME','ACC','DESC','LENG','TC']:current[key]=value.strip()
            if line.strip()=='//':
                if current.get('NAME') in result or not {'NAME','LENG','TC'}<=set(current):raise ValueError('Malformed HMM header')
                result[current['NAME']]=current;current={}
    if current or not result:raise ValueError('Truncated/empty HMM headers')
    return result


def refine(features,embeddings,parent,cache,fasta,hmm,output,cfg):
    """Retain whole/old-child/new-child alternatives under the unchanged E013 rule."""
    from .refinement import marker_evidence,refine as select
    data,_=load(features);a,em=load_arrays(embeddings,'embeddings');pre=json.loads(Path(parent).read_text())
    ids=data['ids'].tolist()
    if (a['ids'].tolist()!=ids or pre['ids']!=ids or em['features_sha256']!=digest(features)
            or pre['embedding_sha256']!=digest(embeddings) or pre['parent_features_sha256']!=digest(features)
            or cfg['seed']!=REFINEMENT_CONFIG['seed']):raise ValueError('Refinement frozen input/seed differs')
    clean=load_cache(cache,fasta,ids);cache=Path(cache);cache_hash=digest(cache/'cache.json')
    asset=json.loads((cache/'asset.json').read_text())
    if asset['hmm']['sha256']!=digest(hmm) or asset['hmm']['bytes']!=Path(hmm).stat().st_size:raise ValueError('Marker HMM/cache asset differs')
    genes={}
    with (cache/'genes.jsonl').open() as f:
        for raw in f:
            row=json.loads(raw);name=row.pop('gene')
            if name in genes:raise ValueError('Duplicate cached gene')
            genes[name]=row
    domains=json.loads((cache/'domains.json').read_text())
    evidence=marker_evidence(genes,domains,asset['families'],profile_headers(hmm),ids,data['lengths'],REFINEMENT_CONFIG)
    old=refine_partition(pre,data,a['features'],clean['clean'],cfg)
    parents=defaultdict(list)
    for i,b in enumerate(pre['assignment']):
        if b>=0:parents[b].append(i)
    proposals={}
    for attempt in old['attempts']:
        if not attempt['adopted']:continue
        members=parents[attempt['pre_bin']];groups=defaultdict(list)
        for i in members:groups[old['assignment'][i]].append(i)
        proposals[attempt['pre_bin']]=dict(groups=[c for b,c in sorted(groups.items()) if b>=0],noise=groups.get(-1,[]))
    selected,decisions,alternatives,transforms=select(pre,old,data,a['features'],evidence,proposals,REFINEMENT_CONFIG,cfg)
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    for name,obj in [('old-partition',old),('partition',selected),('decisions',decisions),('alternatives',alternatives),
                     ('context-transforms',transforms),('quality-evidence',evidence)]:write_json(out/(name+'.json'),obj)
    if json.loads((out/'partition.json').read_text())!=selected:raise ValueError('Selected cached reload differs')
    load_cache(cache,fasta,ids)
    if digest(cache/'cache.json')!=cache_hash:raise ValueError('Marker cache changed')
    write_json(out/'completed.json',dict(status='SUCCESS',policy='unchanged E013',marker_cache_sha256=cache_hash,
        parent_sha256=digest(parent),features_sha256=digest(features),embeddings_sha256=digest(embeddings),
        partition_sha256=digest(out/'partition.json'),truth_accessed=False))
