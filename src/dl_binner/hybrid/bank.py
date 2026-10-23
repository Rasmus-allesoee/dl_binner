"""Verify and stream immutable view-matched frozen sequence features.

Extraction is explicitly separate from training. Missing/corrupt cache members
never trigger inference. At most one parent DNA and one model batch are live;
full cache arrays are memory mapped, with complete retained-view provenance.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from ..io import digest, emit, write_json
from ..multiview.views import load, fasta_rows


def policy():
    """Read the packaged single prospective extraction/fusion policy."""
    return json.loads((Path(__file__).parents[1]/'resources/hybrid.json').read_text())


def model_pin():
    """Return the shipped exact E002/E003 model/custom-code/tokenizer identity."""
    return json.loads((Path(__file__).parents[1]/'resources/hybrid-model-pin.json').read_text())


def binding(path):
    """Stream a regular immutable member's size and SHA256, refusing links."""
    p=Path(path)
    if p.is_symlink() or not p.is_file():raise ValueError('Hybrid regular cache member required')
    return dict(bytes=p.stat().st_size,sha256=digest(p))


def prepare(fasta, features, views, output, extractor, pin):
    """Extract exact original parent/crop DNA once using an admitted frozen adapter.

    Caller supplies a native extractor and already verified pinned model identity.
    The adapter's detail receipt records all chunks/token/unknown counts. No truth
    or inferred crop coverage enters this cache. A partial cache cannot be consumed.
    """
    cfg=policy();data,meta,v,vm=load(features,views)
    if digest(fasta)!=meta['fasta_sha256'] or pin!=model_pin():
        raise ValueError('Hybrid input/model bytes differ')
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    rows=np.flatnonzero(data['eligible']).astype(np.int64);n=len(rows)
    np.save(out/'rows.npy',rows,allow_pickle=False)
    np.save(out/'ids.npy',data['ids'][rows],allow_pickle=False)
    vectors=np.lib.format.open_memmap(out/'vectors.npy',mode='w+',dtype=np.float32,shape=(n,5,768))
    quality=np.lib.format.open_memmap(out/'quality.npy',mode='w+',dtype=np.float32,shape=(n,5,2))
    usable=np.zeros((n,5),bool);seen=at=bp=tokens=chunks=0
    with (out/'views.jsonl').open('x')as log:
        for i,(ident,dna)in enumerate(fasta_rows(fasta)):
            if i>=len(data['ids']) or ident!=data['ids'][i] or hashlib.sha256(dna.encode()).hexdigest()!=data['sequence_sha256'][i]:
                raise ValueError('Hybrid full ordered FASTA DNA differs')
            seen+=1
            if not data['eligible'][i]:continue
            for j in range(5):
                if j and not v['usable'][i,j-1]:continue
                a,b=(0,len(dna))if j==0 else map(int,v['coordinates'][i,j-1]);s=dna[a:b]
                h=hashlib.sha256(s.encode()).hexdigest()
                if j and h.encode()!=v['sequence_sha256'][i,j-1]:raise ValueError('Hybrid crop sequence differs')
                values,details=extractor.extract([(ident+':view:'+str(j),s)])
                if values.shape!=(1,768) or values.dtype!=np.float32 or not np.isfinite(values).all() or np.linalg.norm(values[0])<=1e-12:
                    raise ValueError('Invalid native frozen vector')
                vectors[at,j]=values[0];usable[at,j]=True
                quality[at,j]=np.log1p(len(s))/np.log1p(10000),sum(c not in 'ACGT'for c in s)/len(s)
                detail=details[0]
                if detail['bp']!=len(s) or sum(y-x for x,y in detail['intervals'])!=len(s):raise ValueError('Frozen chunk exposure differs')
                bp+=len(s);chunks+=detail['chunks'];tokens+=sum(detail['tokens'])
                log.write(json.dumps(dict(row=i,view=j,start=a,end=b,sha256=h,detail=detail))+'\n')
            at+=1
            if at%100==0:emit('hybrid_extract',eligible_done=at,eligible_total=n,exposed_bp=bp)
    if seen!=len(data['ids']) or at!=n or digest(fasta)!=meta['fasta_sha256']:raise ValueError('Hybrid FASTA truncated/changed')
    vectors.flush();quality.flush();del vectors,quality
    np.save(out/'usable.npy',usable,allow_pickle=False)
    members={p.name:binding(p)for p in sorted(out.iterdir())if p.is_file()}
    result=dict(kind='hybrid_bank',version=1,policy=cfg,model=pin,features_sha256=digest(features),views_sha256=digest(views),fasta_sha256=meta['fasta_sha256'],parents=len(data['ids']),eligible=n,samples=meta['samples'],members=members,views=int(usable.sum()),exposed_bp=bp,forward_tokens=tokens,chunks=chunks,depth='Measured parent means only; no window measurements',status='COMPLETE')
    write_json(out/'bank.json',result);return result


class Bank:
    """Restore only complete, byte-bound NPY views; transform with parent statistics."""
    def __init__(self,path,features,views,data,meta,v):
        self.root=Path(path);self.meta=json.loads((self.root/'bank.json').read_text());m=self.meta
        names={'rows.npy','ids.npy','vectors.npy','quality.npy','usable.npy','views.jsonl'}
        if (m.get('kind')!='hybrid_bank' or m.get('version')!=1 or m.get('status')!='COMPLETE' or m['policy']!=policy()
            or m['features_sha256']!=digest(features) or m['views_sha256']!=digest(views) or m['fasta_sha256']!=meta['fasta_sha256']
            or m['model']!=model_pin() or m['samples']!=meta['samples'] or m['parents']!=len(data['ids']) or set(m['members'])!=names):
            raise ValueError('Hybrid cache axes/policy/source differs')
        for name in names:
            if binding(self.root/name)!=m['members'][name]:raise ValueError('Hybrid corrupt member: '+name)
        arrays={name[:-4]:np.load(self.root/name,mmap_mode='r',allow_pickle=False)for name in names if name.endswith('.npy')}
        self.rows=arrays['rows'];self.values=arrays['vectors'];self.quality=arrays['quality'];self.usable=arrays['usable'];n=len(self.rows)
        if self.rows.dtype!=np.int64 or self.rows.ndim!=1 or (self.rows<0).any()or(self.rows>=len(data['ids'])).any():raise ValueError('Invalid hybrid row index')
        expected=np.concatenate([np.ones((n,1),bool),v['usable'][self.rows]],1)
        if (not np.array_equal(self.rows,np.flatnonzero(data['eligible'])) or not np.array_equal(arrays['ids'],data['ids'][self.rows])
            or self.values.shape!=(n,5,768) or self.values.dtype!=np.float32 or self.quality.shape!=(n,5,2)
            or self.quality.dtype!=np.float32 or self.usable.dtype!=bool or not np.array_equal(self.usable,expected)):
            raise ValueError('Hybrid member shape/ID/availability differs')
        self.lookup=np.full(len(data['ids']),-1,np.int64);self.lookup[self.rows]=np.arange(n)
        # Bounded chunks avoid a second full cache-sized RAM allocation.
        for a in range(0,n,1024):
            x=np.asarray(self.values[a:a+1024]);q=np.asarray(self.quality[a:a+1024]);mask=self.usable[a:a+1024]
            if not np.isfinite(x).all() or not np.isfinite(q).all() or (x[~mask]!=0).any() or (q[~mask]!=0).any():raise ValueError('Invalid hybrid cache numbers/masks')
            if (np.linalg.norm(x[mask],axis=1)<=1e-12).any()or(q[...,0]<0).any()or(q[...,1]<0).any()or(q[...,1]>1).any():raise ValueError('Invalid hybrid quality/evidence')
        # Reread exact retained-view coordinates/hash and detail inventory, without DNA inference.
        seen=set()
        with(self.root/'views.jsonl').open()as f:
            for line in f:
                z=json.loads(line);i,j=z['row'],z['view'];a=self.lookup[i]if 0<=i<len(self.lookup)else -1
                if a<0 or not 0<=j<5 or not self.usable[a,j]or(i,j)in seen:raise ValueError('Hybrid detail axis duplicate/invalid')
                start,end=(0,int(data['lengths'][i]))if j==0 else map(int,v['coordinates'][i,j-1])
                h=str(data['sequence_sha256'][i])if j==0 else v['sequence_sha256'][i,j-1].decode()
                if (z['start'],z['end'],z['sha256'])!=(start,end,h)or z['detail']['bp']!=end-start:raise ValueError('Hybrid view detail binding differs')
                seen.add((i,j))
        if len(seen)!=int(self.usable.sum())or m['views']!=len(seen):raise ValueError('Hybrid missing view details')

    def fit(self):
        """Compute stable float64 full-parent population statistics with bounded batches."""
        total=np.zeros(768);squares=np.zeros(768);n=len(self.rows)
        if n<2:raise ValueError('Hybrid statistics need two eligible parents')
        for a in range(0,n,1024):
            x=np.asarray(self.values[a:a+1024,0],dtype=np.float64);total+=x.sum(0);squares+=(x*x).sum(0)
        mean=total/n;std=np.sqrt(np.maximum(0,squares/n-mean*mean))
        return dict(mean=mean.tolist(),std=std.tolist(),policy='Eligible full-parent column population z-score then row L2; same saved transform on exact crops')

    def batch(self,selected,views,state):
        """Fetch only actual available views; no fallback or parent substitution."""
        rows=self.lookup[selected]
        if(rows<0).any()or not self.usable[rows,views].all():raise ValueError('Unavailable hybrid view requested')
        x=np.asarray(self.values[rows,views],dtype=np.float64);mean=np.asarray(state['mean']);std=np.asarray(state['std'])
        if mean.shape!=(768,)or std.shape!=(768,)or not np.isfinite(mean).all()or not np.isfinite(std).all()or(std<0).any():raise ValueError('Invalid saved hybrid transform')
        z=np.zeros_like(x);keep=std>1e-8;z[:,keep]=(x[:,keep]-mean[keep])/std[keep];z/=np.maximum(np.linalg.norm(z,axis=1,keepdims=True),1e-12)
        return z.astype(np.float32),np.asarray(self.quality[rows,views],dtype=np.float32)


def rebind(source,source_features,source_views,features,views,output):
    """Reuse exact DNA-only vectors for explicitly changed parent-depth metadata.

    A fresh destination copies identical member bytes only after every ID, parent
    sequence hash, eligibility and crop coordinate/hash/evidence axis agrees. The
    original cache/manifest stays immutable. This is not a missing-cache fallback.
    """
    import shutil
    old,om,ov,ovm=load(source_features,source_views);new,nm,nv,nvm=load(features,views)
    bank=Bank(source,source_features,source_views,old,om,ov)
    for key in ['ids','lengths','sequence_sha256','eligible','tnf','valid_fourmers']:
        if not np.array_equal(old[key],new[key]):raise ValueError('Hybrid rebind DNA/ID/features differ')
    if om['fasta_sha256']!=nm['fasta_sha256']:raise ValueError('Hybrid rebind FASTA differs')
    for key in ['ids','tnf','coordinates','sequence_sha256','usable','valid_fourmers']:
        if not np.array_equal(ov[key],nv[key]):raise ValueError('Hybrid rebind retained views differ')
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    for name,b in bank.meta['members'].items():
        shutil.copyfile(Path(source)/name,out/name)
        if binding(out/name)!=b:raise ValueError('Exact rebind copy differs')
    m=dict(bank.meta,features_sha256=digest(features),views_sha256=digest(views),samples=nm['samples'],reused_source_bank=binding(Path(source)/'bank.json'),rebind_proof='All parent DNA/ID/eligibility/TNF and retained crop DNA/coordinates/masks agree; only parent-depth metadata may differ')
    write_json(out/'bank.json',m);Bank(out,features,views,new,nm,nv);return m
