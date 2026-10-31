"""Bounded cross-view extraction with unchanged DNA/strand/chunk/pooling exposure.

This is a new execution recipe, not a repair/replacement of an accepted bank.
Actual GPU numerical equivalence, throughput and complete-cost admission remain
required before any community extraction. No model or data is downloaded here.
"""
from pathlib import Path
import hashlib
import json

import numpy as np

from .extract import Extractor, reverse_complement
from .bank import Bank, policy, model_pin, binding
from ..multiview.views import load, fasta_rows
from ..io import digest, write_json, emit


def execution_policy():
    """Freeze a bounded schedule; biological reference policy remains separate."""
    return dict(version=1, max_batch_sequences=8, token_bucket=128,
        max_queued_views=64, max_queued_bp=2000000,
        order='token bucket, token length, original chunk/strand index; scatter to original view',
        dtype='float32', reference_attention='pinned author Torch fallback',
        chunk_tokenization='once per recursive candidate/strand; reused for inference and QC',
        no_truncation_substitution_or_view_cutoff=True)


def planned_chunks(dna, tokenizer, max_bp=4000, max_tokens=1024):
    """Match original canonical recursive boundaries while retaining tokenized strands."""
    dna = min(dna, reverse_complement(dna)); parts=[]
    def split(a,b):
        seq=dna[a:b]; tokens=[tokenizer(s,truncation=False) for s in (seq,reverse_complement(seq))]
        if max(len(t['input_ids']) for t in tokens)<=max_tokens:
            parts.append((a,b,tokens))
        elif b-a>1:
            mid=(a+b)//2;split(a,mid);split(mid,b)
        else:raise ValueError('Single base exceeds frozen token budget')
    if max_bp<1 or max_tokens<3:raise ValueError('Invalid chunk limits')
    for a in range(0,len(dna),max_bp):split(a,min(a+max_bp,len(dna)))
    if sum(b-a for a,b,_ in parts)!=len(dna):raise ValueError('Chunk exposure differs')
    return parts


class BatchedExtractor(Extractor):
    """Use the verified frozen model with bounded tokenized cross-view GPU batches."""
    def extract(self,rows):
        """Scatter native float32 pooled chunks back to original views, never truncate."""
        cfg=execution_policy()
        if (not rows or len({i for i,dna in rows})!=len(rows) or len(rows)>cfg['max_queued_views']
                or len(rows)>1 and sum(len(dna) for _,dna in rows)>cfg['max_queued_bp']):
            raise ValueError('Bounded unique full-view extraction queue required')
        plans=[planned_chunks(dna,self.tokenizer,self.cfg['chunk_bp'],self.cfg['max_tokens']) for _,dna in rows]
        jobs=[(i,j,strand,t) for i,parts in enumerate(plans) for j,(_,_,pair) in enumerate(parts) for strand,t in enumerate(pair)]
        order=sorted(range(len(jobs)),key=lambda k:(len(jobs[k][3]['input_ids'])//cfg['token_bucket'],len(jobs[k][3]['input_ids']),k))
        pooled=np.empty((len(jobs),768),np.float32);seen=np.zeros(len(jobs),bool)
        torch=self.torch
        for start in range(0,len(order),cfg['max_batch_sequences']):
            indices=order[start:start+cfg['max_batch_sequences']]
            tokens=self.tokenizer.pad([jobs[k][3] for k in indices],padding=True,return_tensors='pt')
            if tokens['input_ids'].shape[1]>self.cfg['max_tokens']:raise ValueError('Unchunked token overflow')
            tokens={k:v.to(self.device) for k,v in tokens.items()}
            with torch.inference_mode():
                h=self.model(**tokens)[0];mask=tokens['attention_mask'].unsqueeze(-1);values=(h*mask).sum(1)/mask.sum(1)
            if not torch.isfinite(values).all():raise ValueError('Nonfinite frozen vector')
            pooled[indices]=values.cpu().numpy();seen[indices]=True
        if not seen.all():raise ValueError('Dropped model inputs')
        values=[];details=[];at=0
        for (ident,dna),parts in zip(rows,plans):
            n=len(parts);x=pooled[at:at+2*n].reshape(n,2,768).mean(1);at+=2*n
            values.append(np.average(x,axis=0,weights=np.array([b-a for a,b,_ in parts],np.float64)).astype(np.float32))
            ids=[t['input_ids'] for a,b,pair in parts for t in pair]
            details.append(dict(id=ident,bp=len(dna),chunks=n,tokens=list(map(len,ids)),
                unknown_tokens=sum(z.count(self.tokenizer.unk_token_id) for z in ids),intervals=[[a,b] for a,b,_ in parts]))
        return np.stack(values),details


def prepare(fasta,features,views,output,extractor,pin):
    """Stream exact retained views through bounded cross-view batches into a new bank.

    All old banks remain immutable. The new explicit schema is deliberately
    rejected by the original Bank; fitting needs a separately admitted consumer.
    """
    cfg=execution_policy();data,meta,v,vm=load(features,views)
    if digest(fasta)!=meta['fasta_sha256'] or pin!=model_pin():raise ValueError('Model/DNA identity differs')
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    rows=np.flatnonzero(data['eligible']).astype(np.int64);n=len(rows)
    np.save(out/'rows.npy',rows,allow_pickle=False);np.save(out/'ids.npy',data['ids'][rows],allow_pickle=False)
    vectors=np.lib.format.open_memmap(out/'vectors.npy',mode='w+',dtype=np.float32,shape=(n,5,768))
    quality=np.lib.format.open_memmap(out/'quality.npy',mode='w+',dtype=np.float32,shape=(n,5,2))
    vectors[:]=0;quality[:]=0;usable=np.zeros((n,5),bool)
    queue=[];queued_bp=seen=at=bp=tokens=chunks=0
    with (out/'views.jsonl').open('x') as log:
        def flush():
            nonlocal bp,tokens,chunks,queued_bp
            if not queue:return
            result,details=extractor.extract([(z['id'],s) for z,s,pos in queue])
            if result.shape!=(len(queue),768) or result.dtype!=np.float32 or not np.isfinite(result).all():raise ValueError('Invalid extracted batch')
            for (z,dna,pos),vector,detail in zip(queue,result,details):
                i,j=z['row'],z['view'];vectors[pos,j]=vector;usable[pos,j]=True
                quality[pos,j]=np.log1p(len(dna))/np.log1p(10000),sum(c not in 'ACGT' for c in dna)/len(dna)
                if detail['id']!=z['id'] or detail['bp']!=len(dna) or sum(b-a for a,b in detail['intervals'])!=len(dna):raise ValueError('Detail/exposure mismatch')
                z.pop('id');log.write(json.dumps(dict(z,detail=detail))+'\n')
                bp+=len(dna);tokens+=sum(detail['tokens']);chunks+=detail['chunks']
            queue.clear();queued_bp=0
        for i,(ident,dna) in enumerate(fasta_rows(fasta)):
            if i>=len(data['ids']) or ident!=data['ids'][i] or hashlib.sha256(dna.encode()).hexdigest()!=data['sequence_sha256'][i]:raise ValueError('Full DNA axis differs')
            seen+=1
            if not data['eligible'][i]:continue
            for j in range(5):
                if j and not v['usable'][i,j-1]:continue
                a,b=(0,len(dna)) if j==0 else map(int,v['coordinates'][i,j-1]);s=dna[a:b];h=hashlib.sha256(s.encode()).hexdigest()
                if j and h.encode()!=v['sequence_sha256'][i,j-1]:raise ValueError('Retained crop DNA differs')
                if queue and (len(queue)>=cfg['max_queued_views'] or queued_bp+len(s)>cfg['max_queued_bp']):flush()
                queue.append((dict(id=ident+':view:'+str(j),row=i,view=j,start=a,end=b,sha256=h),s,at));queued_bp+=len(s)
            at+=1
            if at%100==0:emit('batched_frozen_extract',parents=at,total=n)
        flush()
    if seen!=len(data['ids']) or at!=n or digest(fasta)!=meta['fasta_sha256']:raise ValueError('Truncated/changed input')
    vectors.flush();quality.flush();del vectors,quality
    np.save(out/'usable.npy',usable,allow_pickle=False)
    m=dict(kind='hybrid_batched_bank',version=1,status='COMPLETE',reference_policy=policy(),execution_policy=cfg,
        model=pin,features_sha256=digest(features),views_sha256=digest(views),fasta_sha256=meta['fasta_sha256'],
        parents=len(data['ids']),eligible=n,samples=meta['samples'],views=int(usable.sum()),exposed_bp=bp,
        forward_tokens=tokens,chunks=chunks,members={p.name:binding(p) for p in out.iterdir() if p.is_file()},
        native_numerical_admission_required=True,not_admitted_as_old_bank=True)
    write_json(out/'bank.json',m);return m


class BatchedBank(Bank):
    """Restore the explicit new recipe; reuse unchanged parent statistics/batch math.

    Community consumption requires a separately produced native numerical and
    throughput admission. Small explicit engineering fixtures cannot certify it.
    The original Bank and every old bank manifest remain untouched.
    """
    def __init__(self,path,features,views,data,meta,v,admission=None,engineering=False):
        self.root=Path(path);self.meta=json.loads((self.root/'bank.json').read_text());m=self.meta
        if engineering:
            if len(data['ids'])>1024:raise ValueError('Engineering bank must be tiny')
        else:
            if admission is None:raise ValueError('Native batched-recipe admission required')
            a=json.loads(Path(admission).read_text())
            if (a.get('status')!='PASS_REFERENCE_EQUIVALENCE_AND_THROUGHPUT' or
                a.get('execution_policy')!=execution_policy() or a.get('model')!=model_pin()
                or a.get('extractor_source')!=binding(Path(__file__))):raise ValueError('Native batched admission differs')
        names={'rows.npy','ids.npy','vectors.npy','quality.npy','usable.npy','views.jsonl'}
        if (m.get('kind')!='hybrid_batched_bank' or m.get('version')!=1 or m.get('status')!='COMPLETE'
            or m['reference_policy']!=policy() or m['execution_policy']!=execution_policy()
            or m['model']!=model_pin() or m['features_sha256']!=digest(features) or m['views_sha256']!=digest(views)
            or m['fasta_sha256']!=meta['fasta_sha256'] or m['samples']!=meta['samples']
            or m['parents']!=len(data['ids']) or set(m['members'])!=names):raise ValueError('Batched bank source/policy differs')
        if any(binding(self.root/n)!=m['members'][n] for n in names):raise ValueError('Corrupt batched bank')
        arrays={n[:-4]:np.load(self.root/n,mmap_mode='r',allow_pickle=False) for n in names if n.endswith('.npy')}
        self.rows=arrays['rows'];self.values=arrays['vectors'];self.quality=arrays['quality'];self.usable=arrays['usable'];n=len(self.rows)
        if (self.rows.dtype!=np.int64 or not np.array_equal(self.rows,np.flatnonzero(data['eligible']))
            or not np.array_equal(arrays['ids'],data['ids'][self.rows]) or m['eligible']!=n
            or self.values.shape!=(n,5,768) or self.values.dtype!=np.float32
            or self.quality.shape!=(n,5,2) or self.quality.dtype!=np.float32 or self.usable.dtype!=bool
            or not np.array_equal(self.usable,np.c_[np.ones(n,bool),v['usable'][self.rows]])):raise ValueError('Batched bank axis differs')
        self.lookup=np.full(len(data['ids']),-1,np.int64);self.lookup[self.rows]=np.arange(n)
        for start in range(0,n,1024):
            x=np.asarray(self.values[start:start+1024]);q=np.asarray(self.quality[start:start+1024]);mask=self.usable[start:start+1024]
            if (not np.isfinite(x).all() or not np.isfinite(q).all() or (x[~mask]!=0).any() or (q[~mask]!=0).any()
                or (np.linalg.norm(x[mask],axis=1)<=1e-12).any() or (q<0).any() or (q[...,1]>1).any()):raise ValueError('Invalid batched numbers')
        seen=set()
        with (self.root/'views.jsonl').open() as f:
            for line in f:
                z=json.loads(line);i,j=z['row'],z['view'];a=self.lookup[i] if 0<=i<len(self.lookup) else -1
                if a<0 or not 0<=j<5 or not self.usable[a,j] or (i,j) in seen:raise ValueError('Invalid batched detail axis')
                start,end=(0,int(data['lengths'][i])) if j==0 else map(int,v['coordinates'][i,j-1])
                h=str(data['sequence_sha256'][i]) if j==0 else v['sequence_sha256'][i,j-1].decode()
                if (z['start'],z['end'],z['sha256'])!=(start,end,h) or z['detail']['bp']!=end-start:raise ValueError('Batched DNA/view detail differs')
                seen.add((i,j))
        if len(seen)!=int(self.usable.sum()) or m['views']!=len(seen):raise ValueError('Missing batched view detail')
