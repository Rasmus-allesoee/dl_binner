"""Own-teacher signed proposals with cached markers and measured reliability.

The original physical-locus, context, reciprocal and shared-neighbor safeguards
remain. Confidence is an attenuation, not a calibrated same-genome probability.
Coabsence never supplies agreement; positive-versus-zero can support a contrast.
"""
import json
from pathlib import Path

import numpy as np

from ..bootstrap import pairs as confidence
from ..context.tokens import binding
from ..io import save_arrays,write_json
from ..multiview.arrays import load_arrays
from ..multiview.views import load
from ..relational import pairs as original
from .cache import Bank


def attenuation(left,right,sign):
    """Return informative-sample counts and absolute signed confidence weights.

    Positive coabsence is neutral; a measured positive-versus-zero profile can
    support a negative contrast. Inputs are declared heuristic reliabilities.
    """
    if (left.ndim!=2 or right.shape!=left.shape or sign.shape!=(len(left),)
        or not np.isfinite(left).all() or not np.isfinite(right).all()
        or np.any((left<0)|(left>1)|(right<0)|(right>1)) or not np.isin(sign,[-1,1]).all()):
        raise ValueError('Malformed measured pair reliabilities/signs')
    positive=sign>0
    shared=(left>0)&(right>0);union=(left>0)|(right>0)
    count=np.where(positive,shared.sum(1),union.sum(1))
    weight=np.where(positive,np.sqrt(left*right).mean(1),np.maximum(left,right).mean(1))
    return count,weight


def prepare(features,original_features,views,measurements,embeddings,graph,markers,hmm,output):
    """Build fresh proposals from this adapted teacher, then seal one attenuation."""
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    original.prepare(features,embeddings,graph,markers,hmm,out/'proposals')
    confidence.prepare(out/'proposals',features,embeddings,graph,out/'confidence')
    a,r=confidence.read(out/'confidence',features)
    data,meta,v,_=load(original_features,views);coverage=Bank(measurements,original_features,views,data,v)
    state=coverage.fit();kept=[];weights=[];decisions=[]
    for start in range(0,len(a['left']),8192):
        ix=np.arange(start,min(start+8192,len(a['left'])),dtype=np.int64)
        left,right=a['left'][ix],a['right'][ix]
        _,x=coverage.batch(left,np.zeros(len(ix),np.int64),state)
        _,y=coverage.batch(right,np.zeros(len(ix),np.int64),state)
        support,attenuated=attenuation(x,y,a['sign'][ix])
        for at,n,c in zip(ix,support,attenuated):
            accepted=bool(n>=2 and c>0)
            if accepted:kept.append(int(at));weights.append(float(a['weight'][at]*c))
            decisions.append(dict(source_pair=int(a['source_index'][at]),accepted=accepted,
                sign=int(a['sign'][at]),informative_samples=int(n),attenuation=float(c),
                reason='retained_measured_reliability' if accepted else 'abstain_insufficient_measured_support'))
    kept=np.asarray(kept,np.int64);final=out/'cache';final.mkdir()
    arrays={k:(a[k][kept] if k!='ids' else a[k]) for k in ['ids','left','right','sign','source_index']}
    arrays['weight']=np.asarray(weights,np.float32)
    save_arrays(final/'pairs.npz',arrays,dict(kind='multiscale_confidence_pairs',features_sha256=binding(features)['sha256']))
    (final/'decisions.jsonl').write_text(''.join(json.dumps(d,sort_keys=True,allow_nan=False)+'\n' for d in decisions))
    write_json(final/'cache.json',dict(kind='multiscale_confidence_cache',version=1,
        features=binding(features),original_features=binding(original_features),measurements=binding(Path(measurements)/'bank.json'),
        source_confidence=binding(out/'confidence/cache.json'),source_pair_count=r['source_pair_count'],
        own_teacher_checkpoint_sha256=r['own_teacher_checkpoint_sha256'],own_teacher_reload_exact=r['own_teacher_reload_exact'],
        samples=meta['samples'],normalization='original proposal slots; rejected pairs never amplify survivors',
        policy='positive >=2 shared positive-reliability samples: mean sqrt(r_i*r_j); negative >=2 union samples: mean max(r_i,r_j); coabsence 0',
        files={p.name:binding(p) for p in final.iterdir()},truth_accessed=False))
    return read(final,features)[1]


def read(path,features):
    """Refuse corrupt pairs, lost source slots, altered axes or changed policy."""
    path=Path(path);r=json.loads((path/'cache.json').read_text())
    if r.get('kind')!='multiscale_confidence_cache' or r.get('version')!=1 or r['features']!=binding(features):
        raise ValueError('Unsupported/unbound measured-pair cache')
    expected={'pairs.npz','pairs.json','decisions.jsonl'}
    if set(r['files'])!=expected or {p.name for p in path.iterdir()}!=expected|{'cache.json'}:
        raise ValueError('Unexpected/missing measured-pair members')
    for n,b in r['files'].items():
        if binding(path/n)!=b:raise ValueError('Corrupt measured-pair member')
    a,m=load_arrays(path/'pairs.npz','multiscale_confidence_pairs');data,meta=load(features)
    if (set(a)!={'ids','left','right','sign','weight','source_index'} or not np.array_equal(a['ids'],data['ids'])
            or r['samples']!=meta['samples'] or m['features_sha256']!=binding(features)['sha256']):
        raise ValueError('Measured-pair full axes differ')
    i,j,s,w,source=(a[k] for k in ['left','right','sign','weight','source_index'])
    n=r['source_pair_count']
    if (type(n) is not int or not 0<=n<=math_cap(data) or i.dtype!=np.int64 or j.dtype!=np.int64 or source.dtype!=np.int64
        or i.ndim!=1 or j.shape!=i.shape or s.shape!=i.shape or w.shape!=i.shape or source.shape!=i.shape
        or s.dtype!=np.int8 or w.dtype!=np.float32 or not np.isin(s,[-1,1]).all()
        or not np.all((i>=0)&(i<j)&(j<len(data['ids']))) or not np.isfinite(w).all() or not np.all((w>0)&(w<=1))
        or not np.all((source>=0)&(source<n)) or not np.all(np.diff(source)>0)
        or len(set(zip(i.tolist(),j.tolist())))!=len(i) or not np.all(data['eligible'][i]&data['eligible'][j])):
        raise ValueError('Malformed measured signed pairs/source slots')
    return a,r


def math_cap(data):
    """Keep the inherited one-epoch pair-slot budget, independent of acceptance."""
    return int(np.ceil(int(data['eligible'].sum())/256))*256
