"""Sealed multiscale moments, chunked transforms and measured reliability masks.

The immutable original DNA/cache bindings are retained. Parent-depth replacement
is an explicit new feature artifact for proposals/grouping, not a mutation or a
claim that old parent means were measured window coverage.
"""
import json
from pathlib import Path

import numpy as np

from ..context.tokens import binding
from ..io import save_arrays, write_json
from ..multiview.views import load
from .measurement import intervals, policy


def read_sample(path,features,views,sample):
    """Verify one closed producer cache and mmap its finite, nonnegative moments."""
    path=Path(path);m=json.loads((path/'sample.json').read_text())
    if m.get('kind')!='multiscale_BAM_sample' or m.get('version')!=1:
        raise ValueError('Unsupported/incomplete BAM sample cache')
    policy(m['policy'])
    if m['features']!=binding(features) or m['views']!=binding(views) or m['sample']!=sample:
        raise ValueError('Sample/DNA/view measurement binding differs')
    if m['moments']!=binding(path/'moments.npy'):raise ValueError('Corrupt BAM moment member')
    a=np.load(path/'moments.npy',mmap_mode='r',allow_pickle=False)
    if a.dtype!=np.float64 or list(a.shape)!=m['shape'] or a.shape!=(m['rows'],5,4):
        raise ValueError('Malformed BAM moment shape/dtype')
    for at in range(0,len(a),8192):
        x=a[at:at+8192]
        if not np.isfinite(x).all() or (x<0).any() or (x>2**53).any() or np.any(x!=np.floor(x)):
            raise ValueError('Malformed/inexact BAM moment counts')
        if np.any(x[...,3]>x[...,0]) or np.any(x[...,1]<x[...,0]):
            raise ValueError('Impossible high-quality/second depth moments')
    return a,m


def validate_moments(a,coords):
    """Refuse impossible full-parent/subinterval moments even after valid hashing."""
    lengths=coords[:,:,1]-coords[:,:,0];good=coords[:,:,0]>=0
    for at in range(0,len(a),8192):
        x=a[at:at+8192];l=lengths[at:at+8192];g=good[at:at+8192]
        if (np.any(x[~g]!=0) or np.any(x[...,2]>np.where(g,l,0))
            or np.any(x[...,2]>x[...,0]) or np.any(x[...,0]**2>x[...,1]*np.where(g,l,0)+1e-6)
            or np.any(x[:,1:]>x[:,0:1])):
            raise ValueError('Moment/exposure/window subset accounting differs')


def seal(root,features,views,samples):
    """Seal ordered sample subdirectories already inside a new root; no recopy.

    A None entry is explicitly unavailable, never zero-filled as a measurement.
    Scientific release requires all ten; optional missing modes remain testable.
    """
    root=Path(root);root.mkdir(exist_ok=True,parents=True)
    if (root/'bank.json').exists():raise FileExistsError('Multiscale bank already sealed')
    data,meta,v,vm=load(features,views);coords=intervals(data,v)
    if not isinstance(samples,list) or len(samples)!=len(meta['samples']):
        raise ValueError('Ordered sample measurement axis differs')
    rows=[];dictionary=None
    for j,(p,sample) in enumerate(zip(samples,meta['samples'])):
        if p is None:rows.append(None);continue
        p=Path(p)
        if p.resolve()!= (root/('sample-%02d'%j)).resolve():raise ValueError('Expected phase-owned ordered sample directory')
        a,m=read_sample(p,features,views,sample)
        if m['rows']!=len(data['ids']) or m['ids_sha256']!=meta['ids_sha256']:
            raise ValueError('Sample full-contig axis differs')
        if dictionary is not None and dictionary!=m['dictionary_sha256']:
            raise ValueError('Sample BAM dictionary/order differs')
        dictionary=m['dictionary_sha256']
        validate_moments(a,coords)
        rows.append(dict(path=p.name,sample_receipt=binding(p/'sample.json')))
    write_json(root/'bank.json',dict(kind='multiscale_BAM_bank',version=1,policy=policy(),
        features=binding(features),views=binding(views),samples=meta['samples'],rows=len(data['ids']),
        bp=int(data['lengths'].sum()),sample_files=rows,all_samples_measured=all(r is not None for r in rows),
        semantics='Exact retained DNA intervals; aligned-read depth, no template independence or calibrated probability',truth_accessed=False))


class Bank:
    """Mmap verified per-sample moments and construct only requested view batches."""
    def __init__(self,root,features,views,data=None,view_data=None):
        self.root=Path(root);self.meta=json.loads((self.root/'bank.json').read_text())
        m=self.meta
        if m.get('kind')!='multiscale_BAM_bank' or m.get('version')!=1:raise ValueError('Incomplete multiscale bank')
        policy(m['policy'])
        if m['features']!=binding(features) or m['views']!=binding(views):raise ValueError('Multiscale bank DNA/view binding differs')
        if data is None or view_data is None:data,fm,view_data,_=load(features,views)
        else:
            from ..multiview.views import load as load_features
            _,fm=load_features(features)
        self.data=data;self.samples=fm['samples'];self.coordinates=intervals(data,view_data)
        if m['samples']!=self.samples or m['rows']!=len(data['ids']) or len(m['sample_files'])!=len(self.samples):
            raise ValueError('Multiscale bank complete sample/contig axes differ')
        self.arrays=[]
        for i,(r,sample) in enumerate(zip(m['sample_files'],self.samples)):
            if r is None:self.arrays.append(None);continue
            if r['path']!='sample-%02d'%i:raise ValueError('Unexpected sample member path')
            p=self.root/r['path']
            if binding(p/'sample.json')!=r['sample_receipt']:raise ValueError('Changed sample measurement receipt')
            a,_=read_sample(p,features,views,sample);validate_moments(a,self.coordinates);self.arrays.append(a)
        if m['all_samples_measured'] is not all(a is not None for a in self.arrays):
            raise ValueError('False complete-measurement claim')

    def statistics(self,selected,view_numbers):
        """Return mean/breadth/population variance/HQ fraction/exposure and validity.

        Measured zero is valid with mean/breadth/variance zero. Missing sample or
        absent DNA crop is invalid with cleared numeric storage; it stays masked.
        """
        selected=np.asarray(selected);view_numbers=np.asarray(view_numbers)
        if (selected.ndim!=1 or selected.dtype.kind not in 'iu' or selected.shape!=view_numbers.shape or
                view_numbers.dtype.kind not in 'iu' or np.any(selected>=len(self.data['ids'])) or
                np.any(selected<0) or np.any((view_numbers<0)|(view_numbers>=5))):
            raise ValueError('Invalid measured view indices')
        coords=self.coordinates[selected,view_numbers];exposure=coords[:,1]-coords[:,0]
        possible=coords[:,0]>=0
        stats=np.zeros((len(selected),len(self.samples),5),np.float64)
        valid=np.zeros(stats.shape[:2],bool)
        for j,a in enumerate(self.arrays):
            if a is None:continue
            x=a[selected,view_numbers];v=possible;length=np.maximum(exposure,1)
            mean=x[:,0]/length;var=x[:,1]/length-mean**2
            if np.any(var[v]<-1e-7):raise ValueError('Negative population depth variance')
            stats[:,j]=np.column_stack([mean,x[:,2]/length,np.maximum(var,0),
                                       np.divide(x[:,3],x[:,0],out=np.zeros(len(x)),where=x[:,0]>0),
                                       np.where(v,exposure,0)])
            stats[~v,j]=0;valid[:,j]=v
        return stats,valid

    def fit(self):
        """Fit one label-free parent scale per sample on eligible positive means."""
        indices=np.flatnonzero(self.data['eligible']);values=[[] for _ in self.samples]
        for at in range(0,len(indices),8192):
            ix=indices[at:at+8192];s,v=self.statistics(ix,np.zeros(len(ix),np.int64))
            for j in range(len(self.samples)):
                values[j].append(np.log1p(s[:,j,0][v[:,j]&(s[:,j,0]>0)]))
        scale=[]
        for pieces in values:
            x=np.concatenate(pieces) if pieces else np.empty(0)
            scale.append(float(max(np.median(x),1e-6)) if len(x) else 1.)
        return dict(version=1,parent_log_median_scale=scale,zero_semantics='measured zero != missing; coabsence not agreement',
                    reliability='length/(length+1000) * mean/(mean+1) * (.25+.75*HQfraction) / sqrt(1+variance/(mean+mean²+1e-8))')

    def batch(self,selected,view_numbers,state,drop=None):
        """Return measured parent/view cell features and bounded information weight."""
        s,v=self.statistics(selected,view_numbers)
        p,pv=self.statistics(selected,np.zeros(len(selected),np.int64))
        scales=np.asarray(state['parent_log_median_scale'],np.float64)
        if scales.shape!=(len(self.samples),) or not np.isfinite(scales).all() or (scales<=0).any():
            raise ValueError('Invalid frozen multiscale transform')
        def metrics(x):
            mean,breadth,var,hq,length=(x[:,:,i] for i in range(5))
            over=var/(mean+mean**2+1e-8)
            reliability=length/(length+1000)*mean/(mean+1)*(.25+.75*hq)/np.sqrt(1+over)
            return np.log1p(mean)/scales,breadth,np.log1p(over),hq,length/(length+1000),reliability
        pm,pb,pd,ph,pe,pr=metrics(p);wm,wb,wd,wh,we,wr=metrics(s)
        valid=v&pv
        # Explicit validity/zero indicators are retained even when the confidence
        # weight is zero. They cannot enter a missing channel through MLP biases.
        cells=np.stack([pm,wm,pb,wb,pd,wd,ph,wh,pe,we,(p[:,:,0]==0)&pv,(s[:,:,0]==0)&v],axis=2)
        weight=np.maximum(pr,wr)*valid
        if drop is not None:
            drop=np.asarray(drop)
            if drop.dtype!=bool or drop.shape!=(len(selected),):raise ValueError('Invalid whole-branch dropout mask')
            valid=valid&~drop[:,None];weight=weight*~drop[:,None]
        cells*=valid[:,:,None]
        if not np.isfinite(cells).all() or not np.isfinite(weight).all():raise ValueError('Nonfinite coverage features')
        return cells.astype(np.float32),weight.astype(np.float32)


def rebind(root,features,views,output):
    """Write new full-parent scalar features for unchanged downstream/proposal APIs.

    Original features/views/tokens/banks remain byte-bound and untouched. This
    new file deliberately changes depth only and records the measurement source.
    """
    bank=Bank(root,features,views);data,meta=load(features);new={k:v for k,v in data.items()}
    means=np.zeros_like(data['depth']);valid=np.zeros_like(means,bool)
    for at in range(0,len(means),8192):
        ix=np.arange(at,min(at+8192,len(means)),dtype=np.int64)
        s,v=bank.statistics(ix,np.zeros(len(ix),np.int64));means[ix]=s[:,:,0];valid[ix]=v
    if not valid.all():raise ValueError('Scientific scalar rebind requires all samples fully measured')
    new.update(depth=means,zero_depth=means==0,depth_evidence=(means>0).any(1))
    meta={k:v for k,v in meta.items() if k not in ['sha256','ids_sha256','version']}
    meta.update(mode='common_multiscale_parent_means',depth_semantics='New pinned full-parent mean; actual crop moments remain separately measured',
                prior_features=binding(features),measured_bank=binding(Path(root)/'bank.json'))
    save_arrays(output,new,meta)
