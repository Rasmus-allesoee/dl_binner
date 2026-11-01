#!/usr/bin/env python3
"""Freeze a source-blind 128-view qualification payload from unchanged Oral caches.

Selection uses length, parent/crop, valid-fourmer interruption and opaque-ID hash.
It reads exact cached coordinates; no DNA view, model feature or truth is generated.
"""
import argparse,hashlib,heapq,json,sys,os
from pathlib import Path
ROOT=Path(os.environ.get('E029_SOURCE_REPO',Path(__file__).absolute().parents[1]))
sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def run(features,views,fasta,output,model_dir,count=128,engineering=False):
    """Stream-check all source DNA and retain only prospectively selected original views."""
    from e029_control import product_scope
    product_scope()
    import numpy as np
    from dl_binner.multiview.views import load,fasta_rows
    from dl_binner.hybrid.batched import planned_chunks
    from dl_binner.hybrid.extract import reverse_complement
    from dl_binner.hybrid.bank import model_pin
    from transformers import AutoTokenizer
    if count!=128 and not engineering:raise ValueError('Native cohort must contain exactly 128 original views')
    data,meta,v,vm=load(features,views)
    if binding(fasta)['sha256']!=meta['fasta_sha256']:raise ValueError('Original FASTA differs')
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    tokenizer=AutoTokenizer.from_pretrained(str(model_dir),local_files_only=True,trust_remote_code=False)
    pin=model_pin()
    for n in ['tokenizer.json','tokenizer_config.json','special_tokens_map.json']:
        if binding(Path(model_dir)/n)!={k:pin['files'][n][k]for k in ['bytes','sha256']}:raise ValueError('Pinned tokenizer differs')
    buckets={};global_heap=[];longest={};totals={};chosen={}
    def offer(heap,key,item,cap):
        z=(-key,item)
        if len(heap)<cap:heapq.heappush(heap,z)
        elif z>heap[0]:heapq.heapreplace(heap,z)
    for i in np.flatnonzero(data['eligible']):
        ident=str(data['ids'][i])
        for j in range(5):
            if j and not v['usable'][i,j-1]:continue
            a,b=(0,int(data['lengths'][i]))if j==0 else map(int,v['coordinates'][i,j-1]);length=b-a
            four=int(data['valid_fourmers'][i]if not j else v['valid_fourmers'][i,j-1])
            band=0 if length<1000 else 1 if length<2500 else 2 if length<10000 else 3
            category=f'{"parent"if not j else"crop"}:{band}:{"interrupted"if four<length-3 else"complete"}'
            h=int.from_bytes(hashlib.sha256(('E029:'+ident+':'+str(j)).encode()).digest()[:8],'big');item=(int(i),j,a,b,category)
            offer(buckets.setdefault(category,[]),h,item,8);offer(global_heap,h,item,128)
            totals[category]=totals.get(category,0)+1
            if category not in longest or length>longest[category][0]:longest[category]=(length,h,item)
    selected={item[:2]:item for heap in buckets.values()for h,item in heap}
    for length,h,item in longest.values():selected[item[:2]]=item
    ranked=sorted(selected.values(),key=lambda z:hashlib.sha256(('E029:'+str(data['ids'][z[0]])+':'+str(z[1])).encode()).digest())
    # Keep one longest member per populated category, then hash-balanced members.
    keep={item[:2]:item for length,h,item in longest.values()}
    for item in ranked+[item for h,item in sorted(global_heap,reverse=True)]:
        if len(keep)>=count:break
        keep[item[:2]]=item
    if len(keep)!=count:raise ValueError('Insufficient distinct original views for fixed qualification count')
    for item in keep.values():chosen.setdefault(item[0],[]).append(item)
    rows=[];seen=0
    for i,(ident,dna)in enumerate(fasta_rows(fasta)):
        if i>=len(data['ids'])or ident!=data['ids'][i]or hashlib.sha256(dna.encode()).hexdigest()!=data['sequence_sha256'][i]:raise ValueError('Original DNA axis/hash differs')
        seen+=1
        for _,j,a,b,category in chosen.get(i,[]):
            seq=dna[a:b];sha=hashlib.sha256(seq.encode()).hexdigest()
            if j and sha.encode()!=v['sequence_sha256'][i,j-1]:raise ValueError('Original crop hash differs')
            parts=planned_chunks(seq,tokenizer);tokens=[t['input_ids']for x,y,pair in parts for t in pair]
            rows.append(dict(id=ident+':view:'+str(j),parent=ident,row=i,view=j,start=a,end=b,bp=b-a,sha256=sha,selection_stratum=category,
                actual_ambiguous_bp=sum(c not in 'ACGT'for c in seq),tokens=list(map(len,tokens)),chunks=[[x,y]for x,y,_ in parts],
                unknown_tokens=sum(t.count(tokenizer.unk_token_id)for t in tokens),dna=seq))
    if seen!=len(data['ids'])or binding(fasta)['sha256']!=meta['fasta_sha256']:raise ValueError('Full source DNA incomplete/changed')
    rows.sort(key=lambda z:z['id']);write(out/'cohort.json',dict(kind='E029 original source-blind view qualification',count=count,rows=rows,truth_accessed=False))
    result=dict(status='FROZEN_BEFORE_GPU_OUTPUTS',source={k:binding(p)for k,p in dict(features=features,views=views,views_meta=Path(views).with_suffix('.json'),fasta=fasta).items()},
        count=count,cohort=binding(out/'cohort.json'),selection='8 lowest E029 opaque-ID hashes per length/type/fourmer-interruption stratum; include each longest; deterministic hash fill to 128',
        strata_full_counts=totals,original_full_contigs=seen,exposed_bp=sum(z['bp']for z in rows),forward_tokens=sum(sum(z['tokens'])for z in rows),
        all_original_coordinates=True,features_or_scientific_vectors_generated=False,model_outputs_observed=False,
        rows=[{k:v for k,v in z.items()if k!='dna'}for z in rows])
    write(out/'manifest.json',result);print(json.dumps(dict(status=result['status'],count=count,bp=result['exposed_bp'])),flush=True);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['features','views','fasta','output','model-dir']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();run(a.features,a.views,a.fasta,a.output,a.model_dir)
