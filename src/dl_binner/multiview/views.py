"""Stream real DNA into a bounded diverse crop bank and full-parent features.

All parent DNA is retained. Crops carry zero-based half-open coordinates and
sequence hashes; depth, when present, is measured on the parent, never a crop.
The fixed bank is honest cached augmentation, not fresh per-epoch sequencing.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from ..io import DNA, digest, emit, read_depth, save_arrays, load_arrays, validate_features
from ..candidate.views import composition


def config(path=None):
    """Read the packaged strict prospective schema; reject unsupported schedules."""
    default=Path(__file__).parents[1]/'resources/multiview.json'
    expected=json.loads(default.read_text());value=json.loads(Path(path or default).read_text())
    if set(value)!=set(expected):raise ValueError('Multiview configuration keys mismatch')
    for k,initial in expected.items():
        v=value[k]
        if type(initial) is int:
            if type(v) is not int or v<(0 if k=='seed' else 1):raise ValueError('Invalid integer configuration: '+k)
        elif type(v) not in (float,int) or not np.isfinite(v) or v<0:raise ValueError('Invalid numeric configuration: '+k)
    if (value['crop_pairs']!=2 or value['crop_min']<4 or value['crop_max']<value['crop_min']
            or not 0<value['crop_fraction']<1 or not 0<=value['depth_dropout']<1
            or value['min_length']<4 or value['batch_size']<2 or value['neighbors']<5
            or not 0<value['temperature'] or not 0<value['learning_rate']
            or not 0<value['min_neighbor_recall']<=1):
        raise ValueError('Invalid multiview policy')
    return value


def fasta_rows(path):
    """Yield one validated IUPAC contig at a time with duplicate opaque-ID refusal."""
    ident=None;chunks=[];seen=set()
    def sequence():
        dna=''.join(chunks).upper()
        if not dna or set(dna)-DNA:raise ValueError('Empty/invalid IUPAC DNA: '+str(ident))
        return ident,dna
    with Path(path).open() as stream:
        for raw in stream:
            line=raw.strip()
            if not line:continue
            if line.startswith('>'):
                if ident is not None:yield sequence()
                fields=line[1:].split()
                if not fields or fields[0] in seen or any(ord(c)<32 for c in fields[0]):raise ValueError('Missing/duplicate FASTA ID')
                ident=fields[0];seen.add(ident);chunks=[]
            else:
                if ident is None:raise ValueError('Sequence before FASTA header')
                chunks.append(line)
    if ident is None:raise ValueError('Empty FASTA')
    yield sequence()


def crops(ident,dna,cfg):
    """Draw four variable-length crops in paired disjoint halves, without labels."""
    if len(dna)<2*cfg['crop_min']:return []
    seed=int.from_bytes(hashlib.sha256((str(cfg['seed'])+'\0'+ident).encode()).digest()[:8],'little')
    rng=np.random.default_rng(seed);half=len(dna)//2;result=[]
    for _ in range(cfg['crop_pairs']):
        for left,right in [(0,half),(half,len(dna))]:
            upper=min(cfg['crop_max'],max(cfg['crop_min'],int((right-left)*cfg['crop_fraction'])))
            length=int(rng.integers(cfg['crop_min'],upper+1));start=int(rng.integers(left,right-length+1))
            result.append((start,start+length,dna[start:start+length]))
    return result


def prepare(fasta,depth,output,cfg,parent_features=None):
    """Prepare complete parent features and crop bank; optionally reuse sealed parents.

    Only one contig's DNA is live. Fresh output is exclusive. Reuse verifies exact
    FASTA/depth bytes, axes and eligibility instead of copying accepted features.
    """
    out=Path(output);out.mkdir(parents=True,exist_ok=False);fasta_hash=digest(fasta)
    ids=[];lengths=[];hashes=[]
    for ident,dna in fasta_rows(fasta):
        ids.append(ident);lengths.append(len(dna));hashes.append(hashlib.sha256(dna.encode()).hexdigest())
    samples,coverage=read_depth(depth,ids);n=len(ids)
    if parent_features:
        data,meta=load_arrays(parent_features,'features');validate_features(data,meta)
        if (meta['fasta_sha256']!=fasta_hash or meta['samples']!=samples
                or meta['min_length']!=cfg['min_length'] or data['ids'].tolist()!=ids
                or not np.array_equal(data['depth'],coverage)
                or not np.array_equal(data['lengths'],lengths) or data['sequence_sha256'].tolist()!=hashes):
            raise ValueError('Reused full parent features/input axes differ')
        features=Path(parent_features)
    else:
        data=dict(ids=np.array(ids),tnf=np.zeros((n,136),np.float32),valid_fourmers=np.zeros(n,np.int64),
                  lengths=np.array(lengths,np.int64),depth=coverage,zero_depth=coverage==0,
                  depth_evidence=(coverage>0).any(1),sequence_sha256=np.array(hashes))
        features=out/'features.npz'
    bank=np.zeros((n,4,136),np.float32);counts=np.zeros((n,4),np.int64)
    coords=np.full((n,4,2),-1,np.int64);shas=np.full((n,4),'',dtype='S64');usable=np.zeros((n,4),bool)
    for i,(ident,dna) in enumerate(fasta_rows(fasta)):
        if ident!=ids[i] or hashlib.sha256(dna.encode()).hexdigest()!=hashes[i]:raise ValueError('FASTA changed during preparation')
        if not parent_features:data['tnf'][i],data['valid_fourmers'][i]=composition(dna)
        seen=set()
        for j,(a,b,s) in enumerate(crops(ident,dna,cfg)):
            bank[i,j],counts[i,j]=composition(s);coords[i,j]=a,b;h=hashlib.sha256(s.encode()).hexdigest();shas[i,j]=h
            usable[i,j]=bool(counts[i,j] and h not in seen);seen.add(h)
        if i%2000==0:emit('multiview_features',completed_contigs=i,total_contigs=n)
    if digest(fasta)!=fasta_hash:raise ValueError('FASTA changed after preparation')
    if not parent_features:
        reasons=np.where(data['lengths']<cfg['min_length'],'below_min_length',np.where(data['valid_fourmers']==0,'no_valid_fourmers',''))
        data.update(eligible=reasons=='',exclusion_reason=reasons)
        meta=dict(kind='features',fasta_sha256=fasta_hash,depth_sha256=digest(depth) if depth else None,
                  samples=samples,min_length=cfg['min_length'],sequence_dimensions=136,mode='multiview_measured_parent_depth',
                  depth_semantics='Measured parent means condition crops, not measured window depth; no variance.')
        validate_features(data,meta);save_arrays(features,data,meta)
    save_arrays(out/'views.npz',dict(ids=data['ids'],tnf=bank,valid_fourmers=counts,coordinates=coords,
                sequence_sha256=shas,usable=usable),dict(kind='multiview_views',parent_features_sha256=digest(features),
                fasta_sha256=fasta_hash,policy=cfg,coordinates='zero-based half-open',
                semantics='Full parent plus every distinct valid cached crop are positives; no genome labels; measured parent depth only.'))
    write=dict(features=str(features.absolute()),features_sha256=digest(features),views_sha256=digest(out/'views.npz'),
               parents=n,eligible=int(data['eligible'].sum()),contrastive_parents=int((data['eligible']&usable.any(1)).sum()),
               crop_views=int((usable&data['eligible'][:,None]).sum()),samples=samples,bp=int(data['lengths'].sum()),parent_features_reused=bool(parent_features))
    from ..io import write_json
    write_json(out/'prepared.json',write);return write


def load(features,views=None):
    """Validate full bank axes, disjoint coordinates, evidence and duplicate masks."""
    data,meta=load_arrays(features,'features');validate_features(data,meta)
    if views is None:return data,meta
    v,vm=load_arrays(views,'multiview_views');n=len(data['ids']);cfg=vm['policy']
    if (vm['parent_features_sha256']!=digest(features) or not np.array_equal(v['ids'],data['ids'])
            or v['tnf'].shape!=(n,4,136) or v['coordinates'].shape!=(n,4,2)
            or v['valid_fourmers'].shape!=(n,4) or v['sequence_sha256'].shape!=(n,4) or v['usable'].shape!=(n,4)
            or v['usable'].dtype!=bool or v['coordinates'].dtype.kind not in 'iu'
            or v['valid_fourmers'].dtype.kind not in 'iu' or not np.isfinite(v['tnf']).all()
            or (v['tnf']<0).any() or (v['valid_fourmers']<0).any()
            or not np.allclose(v['tnf'].sum(2),v['valid_fourmers']>0,atol=1e-6)):
        raise ValueError('Invalid multiview axes/evidence')
    for i,length in enumerate(data['lengths']):
        if length<2*cfg['crop_min']:
            if (v['coordinates'][i]!=-1).any() or (v['valid_fourmers'][i]!=0).any() or v['usable'][i].any() or (v['sequence_sha256'][i]!=b'').any():
                raise ValueError('Short parent has fabricated crop')
            continue
        seen=set()
        for j,(a,b) in enumerate(v['coordinates'][i]):
            left,right=(0,length//2) if j%2==0 else (length//2,length)
            upper=min(cfg['crop_max'],max(cfg['crop_min'],int((right-left)*cfg['crop_fraction'])))
            h=v['sequence_sha256'][i,j];count=v['valid_fourmers'][i,j]
            if not left<=a<b<=right or not cfg['crop_min']<=b-a<=upper or count>b-a-3 or len(h)!=64:
                raise ValueError('Invalid real crop coordinates/count/hash')
            if v['usable'][i,j]!=bool(count and h not in seen):raise ValueError('Distinct crop mask differs')
            seen.add(h)
    return data,meta,v,vm
