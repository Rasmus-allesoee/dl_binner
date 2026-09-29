"""Close E001 seed-11 using retained bytes only: candidates, markers and probes.

Requires the verified diagnostic collection, frozen local population and prior
compact MetaBAT/VAMB/COMEBin returns. Writes compact summaries plus full probe
records to an ignored output directory; never fits, clusters or changes inputs.
"""
import argparse
import ast
from collections import Counter,defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import time
import numpy as np
from e001_features import EXP,read,sha,write
from e001lib.records import require,partition
from e001lib.metrics import score,neighbor_purity
from e001_review_comebin import candidate_names


def marker_sets(path):
    """Read pinned CheckM taxon sets as literals, without evaluating source code."""
    rows=path.read_text().splitlines(); text=rows[1].split('\t')[5]
    return [set(x) for x in ast.literal_eval(re.sub(r'set\((\[[^)]*\])\)',r'\1',text))]


def marker_hits(path,ids):
    """Mirror native adjacent-gene handling; retain marker multiplicity per contig."""
    hits=defaultdict(Counter)
    with path.open() as f:
        next(f)
        for line in f:
            _,marker,gene=line.rstrip().split('\t'); gene=gene.split('&&')[0];contig=gene.rsplit('_',1)[0]
            require(contig in ids,'Unknown marker contig');hits[contig][marker]+=1
    return hits


def marker_quality(counts,groups):
    """Independent CheckM grouped completeness/contamination and domain score."""
    all_markers=set.union(*groups)
    individual=100*sum(counts[m] for m in all_markers)/sum(map(len,groups))
    comp=100*sum(sum(counts[m]>0 for m in group)/len(group) for group in groups)/len(groups)
    cont=100*sum(sum(max(0,counts[m]-1) for m in group)/len(group) for group in groups)/len(groups)
    return individual,comp,cont


def marker_counts(ids,labels,hits,sets):
    """Recompute six strict marker quality counts for one retained partition."""
    bins={domain:defaultdict(Counter) for domain in hits}
    for seq,label in zip(ids,labels):
        for domain in hits:
            if seq in hits[domain]: bins[domain][int(label)].update(hits[domain][seq])
    result={f'num_{c}{t}':0 for c in (50,70,90) for t in (10,5)}
    for label in set(labels.tolist()):
        bac=marker_quality(bins['bac'][label],sets['bac']); ar=marker_quality(bins['ar'][label],sets['ar'])
        _,comp,cont=bac if bac[0]>ar[0] else ar
        for c in (50,70,90):
            for t in (10,5):result[f'num_{c}{t}']+=int(comp>c and cont<t)
    result['sum']=sum(result.values());result['sum_cont5']=sum(result[f'num_{c}5'] for c in (50,70,90))
    return result


def unit(x):
    """L2-normalize each nonzero row; leave exact zero rows explicit."""
    x=np.asarray(x,dtype=np.float64);n=np.linalg.norm(x,axis=1,keepdims=True)
    return np.divide(x,n,out=np.zeros_like(x),where=n!=0)


def scale_controls(collection):
    """Inspect retained CS arrays/tables; distinguish omitted VAMB CS bytes."""
    base=collection/'features/comebin'
    for name,factor in [('coverage_mean.npy',.1),('coverage_var.npy',.1**2)]:
        a=np.load(base/'C0'/name,allow_pickle=False)
        b=np.load(base/'CS'/name,allow_pickle=False)
        require(np.array_equal(a*factor,b),'COMEBin CS scaling differs')
    for name in ['contig_ids.txt','contig_lengths.npy','augmentation_intervals.npy']:
        require(sha(base/'C0'/name)==sha(base/'CS'/name),'CS axis/interval differs')
    a=np.load(base/'C0/normalized-views.npy',allow_pickle=False)
    b=np.load(base/'CS/normalized-views.npy',allow_pickle=False)
    require(np.array_equal(a[:,:,20:],b[:,:,20:]),'CS composition differs')
    tables=[]
    for c in ['C0','CS']:
        with (collection/'features/metabat'/c/'depth.tsv').open() as f:
            tables.append(list(csv.reader(f,delimiter='\t')))
    require(tables[0][0]==tables[1][0] and len(tables[0])==len(tables[1]),'MetaBAT CS header/row mismatch')
    for left,right in zip(tables[0][1:],tables[1][1:]):
        require(left[:2]==right[:2],'MetaBAT CS ID/length mismatch')
        values=np.array(left[2:],dtype=float);values[0]*=.1;values[1::2]*=.1;values[2::2]*=.1**2
        require(np.array_equal(values,np.array(right[2:],dtype=float)),'MetaBAT CS scaling differs')
    return dict(comebin_raw_scaling='exact',metabat_raw_scaling='exact',
        comebin_normalized_max_abs_difference_per_view=np.max(np.abs(a-b),axis=(1,2)).tolist(),
        vamb='Accepted native scale-invariance receipts reused; normalized-CS.npz was not in the collection. No new direct CS array claim.')


def recovered(pop,predictions,result):
    """Return contigs recovered in each genome's single qualifying primary bin."""
    return {s for s,g in pop['unique_origins'].items() if g in result['per_genome']
            and result['per_genome'][g]['bin'] is not None and predictions.get(s)==result['per_genome'][g]['bin']}


def representation_triage(probes,short,lengths,lost):
    """Compare each prespecified raw space with learned neighbors on fixed bases."""
    total=sum(lengths[s] for s in short)
    lost_total=sum(lengths[s] for s in short if s in lost)
    result={}
    for name in ['composition','coverage','equal_blocks']:
        raw=probes[name];learn=probes['embedding']
        dropped={s for s in short if raw[s]['purity'] is not None and learn[s]['purity'] is not None and raw[s]['purity']-learn[s]['purity']>=.10-1e-12}
        overlap=sum(lengths[s] for s in dropped&lost)
        result[name]=dict(short_base_fraction=sum(lengths[s] for s in dropped)/total,
            lost_short_overlap_base_fraction_of_all_short=overlap/total,
            lost_short_overlap_base_fraction_of_lost=overlap/lost_total if lost_total else None)
    return result


def summary_probe(probe,queries,lengths):
    """Summarize only scored fixed queries, reporting zero/filtered rows separately."""
    scored=[s for s in queries if probe[s]['status']=='scored'];bp=sum(lengths[s] for s in scored)
    return dict(status_counts=dict(Counter(probe[s]['status'] for s in queries)),
        mean_purity=float(np.mean([probe[s]['purity'] for s in scored])) if scored else None,
        base_weighted_purity=sum(lengths[s]*probe[s]['purity'] for s in scored)/bp if bp else None,scored_bp=bp)


def close(collection,population_dir,prior_comebin,prior_other,source,out):
    """Verify every byte, recompute native selection and run fixed exact probes."""
    started=time.monotonic();out.mkdir(parents=True,exist_ok=False)
    require((collection/'manifest.json').read_bytes()==(EXP/'diagnostic-collection.json').read_bytes(),'Collection manifest differs')
    for item in read(collection/'manifest.json')['files']:
        p=collection/item['member'];require(p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],'Changed collected file '+str(p))
    frozen=read(EXP/'frozen-inputs.json')
    require(sha(population_dir/'population.json')==frozen['outputs']['population.json'],'Changed population')
    pop=read(population_dir/'population.json');lengths=pop['lengths'];queries=pop['probe_queries'];short=[s for s in queries if lengths[s]<10000]
    require(queries==sorted(pop['probe_pool'],key=lambda s:(hashlib.sha256(('E001-probe:'+s).encode()).hexdigest(),s))[:10000],'Query selection changed')
    sets={d:marker_sets(source/'COMEBin/scripts/checkm_ms'/n) for d,n in [('bac','bacteria.ms'),('ar','archaea.ms')]}
    controls=scale_controls(collection)
    results={};preds={};scores={};candidate_rows=[];probes={};binary={};coverage={}
    for tool in ['metabat','vamb','comebin']:
        preds[tool]={};scores[tool]={}
        for c in ['C0','CT']:
            d=(prior_comebin if tool=='comebin' else prior_other)/tool/c
            pred=partition(d/'predictions.tsv',lengths);preds[tool][c]=pred;scores[tool][c]=score(pop,pred)
            require(scores[tool][c]==read(d/'r95.json'),'Changed primary result')
    for c in ['C0','CT']:
        print('AUDIT candidates/markers',c,flush=True)
        d=collection/'comebin/comebin'/c;native=d/'native';ids=(native/'embedding_ids.txt').read_text().splitlines()
        require(len(ids)==len(set(ids))==len(lengths) and set(ids)==set(lengths),'Embedding ID axis')
        arr=np.load(native/'embedding_lengths.npy',allow_pickle=False);require(arr.tolist()==[lengths[s] for s in ids],'Embedding length axis')
        arrays={name:np.load(native/name,allow_pickle=False) for name in ['embeddings.npy','covembeddings.npy']}
        require(all(a.shape==(len(ids),128) and a.dtype==np.float32 and np.isfinite(a).all() for a in arrays.values()),'Invalid embedding matrix')
        fit=read(d/'fit.json'); require(set(fit['candidate_sha256'])==candidate_names(),'Wrong grid')
        hits={domain:marker_hits(next((native/'cluster_res').glob('**/checkm_'+domain+'/marker_gene_table.tsv')),set(ids)) for domain in ('bac','ar')}
        with (native/'cluster_res/estimate_res.txt').open() as f: expected={r['Binning_method']:r for r in csv.DictReader(f,delimiter='\t')}
        candidates=[]
        for name in sorted(candidate_names()):
            path=native/'cluster_res'/name; require(sha(path)==fit['candidate_sha256'][name],'Candidate hash differs')
            labels=np.load(path,allow_pickle=False)
            require(labels.ndim==1 and len(labels)==len(ids) and np.issubdtype(labels.dtype,np.integer) and (labels>=0).all(),'Invalid complete candidate')
            counts=marker_counts(ids,labels,hits,sets)
            require(all(counts[k]==int(expected[name][k]) for k in counts),'Marker recomputation mismatch '+name)
            assignments={s:str(int(v)) for s,v in zip(ids,labels)}; r=score(pop,assignments)
            if name==fit['winning_candidate']:require(assignments==preds['comebin'][c],'Native selected labels differ from primary export')
            row=dict(condition=c,candidate=name,r95=r['r95'],bins=len(set(labels.tolist())),selected=name==fit['winning_candidate'],**counts)
            candidate_rows.append(row);candidates.append(row)
        best=max(candidates,key=lambda r:r['r95']);winner=max(candidates,key=lambda r:(r['sum'],r['sum_cont5']))
        require(winner['candidate']==fit['winning_candidate'],'Native winner differs')
        binary[c]=dict(embedding_shape=list(arrays['embeddings.npy'].shape),ids_sha256=sha(native/'embedding_ids.txt'),candidates=120,marker_scores_recomputed=120,selected=winner['candidate'],selected_r95=winner['r95'],oracle_candidate=best['candidate'],oracle_r95=best['r95'],oracle_gap=best['r95']-winner['r95'],unique_candidate_hashes=len(set(fit['candidate_sha256'].values())))
    with (out/'candidate-scores.tsv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(candidate_rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(candidate_rows)
    quartiles={}
    for tool in ['comebin','vamb']:
        probes[tool]={};coverage[tool]={}
        for c in ['C0','CT']:
            d=collection/'features'/tool/c
            ids=(d/('contig_ids.txt' if tool=='comebin' else 'ids.txt')).read_text().splitlines()
            require(set(ids)==set(lengths) and len(ids)==len(lengths),'Feature ID axis')
            if tool=='comebin':
                views=np.load(d/'normalized-views.npy',allow_pickle=False);require(views.shape==(6,len(ids),156) and np.isfinite(views).all(),'Invalid normalized views')
                comp=views[0,:,20:];cov=views[0,:,:20]
                raw=np.load(d/'coverage_mean.npy',allow_pickle=False)[:,0,:].T
                emb=np.load(collection/'comebin/comebin'/c/'native/embeddings.npy',allow_pickle=False)
                require(ids==(collection/'comebin/comebin'/c/'native/embedding_ids.txt').read_text().splitlines(),'Embedding/features row order')
                if c=='CT':
                    require(np.array_equal(comp,np.load(collection/'features/comebin/C0/normalized-views.npy',mmap_mode='r')[0,:,20:]),'Composition changed under thinning')
                    require(sha(d/'augmentation_intervals.npy')==sha(collection/'features/comebin/C0/augmentation_intervals.npy'),'Fixed intervals changed')
            else:
                with np.load(d/'normalized-C0.npz',allow_pickle=False) as x:comp=x['composition'];cov=np.concatenate([x['coverage'],x['total_abundance']],axis=1)
                mask=np.load(d/'input-mask.npy',allow_pickle=False);require(mask.dtype==bool and mask.all() and mask.shape==(len(ids),),'Unexpected VAMB mask')
                with np.load(collection/'vamb/vamb'/c/'native/latent.npz',allow_pickle=False) as x:emb=x['arr_0']
                require(ids==read(collection/'vamb/vamb'/c/'native/embedding-ids.json'),'VAMB embedding order')
                raw=None
            require(emb.shape==(len(ids),128 if tool=='comebin' else 32) and np.isfinite(emb).all(),'Invalid learned embedding')
            coverage[tool][c]=dict(zero_normalized_coverage_rows=int((np.linalg.norm(cov,axis=1)==0).sum()),zero_embedding_rows=int((np.linalg.norm(emb,axis=1)==0).sum()))
            if raw is not None:
                coverage[tool][c].update(zero_raw_mean_rows=int((raw.sum(axis=1)==0).sum()),zero_raw_entries=int((raw==0).sum()))
                if c=='C0':
                    medians={g:float(np.median([float(raw[i].sum()) for i,s in enumerate(ids) if pop['unique_origins'].get(s)==g])) for g in pop['genomes']}
                    cuts=np.quantile(list(medians.values()),[.25,.5,.75]);quartiles={g:int(np.searchsorted(cuts,v,side='right'))+1 for g,v in medians.items()}
                    write(out/'coverage-strata.json',dict(definition='C0 COMEBin view-0 summed sample mean depth; genome median then quartiles; ties assigned upward',cutpoints=cuts.tolist(),genomes=quartiles,median_depth=medians))
            probes[tool][c]={}
            for name,x in [('composition',comp),('coverage',cov),('equal_blocks',np.concatenate([unit(comp),unit(cov)],axis=1)),('embedding',emb)]:
                print('PROBE',tool,c,name,flush=True)
                probe=neighbor_purity(ids,x,pop,batch_size=128);probes[tool][c][name]=probe
                write(out/f'neighbors-{tool}-{c}-{name}.json',probe)
    for tool in preds:
        r={}; rec={c:recovered(pop,preds[tool][c],scores[tool][c]) for c in ['C0','CT']};lost=rec['C0']-rec['CT']; gained=rec['CT']-rec['C0']
        for c in ['C0','CT']:
            s=scores[tool][c]
            r[c]=dict(r95=s['r95'],assigned_bp=s['assigned_bp'],unassigned_bp=s['unassigned_bp'],
                length_strata=[dict(lower_bp=low,total_bp=sum(v['length_strata'][i]['total_bp'] for v in s['per_genome'].values()),recovered_bp=sum(v['length_strata'][i]['recovered_bp'] for v in s['per_genome'].values())) for i,low in enumerate([2500,5000,10000,50000])],
                C0_coverage_quartile_r95={str(q):float(np.mean([v['r95'] for g,v in s['per_genome'].items() if quartiles[g]==q])) for q in range(1,5)})
        r['paired']=dict(lost_correct_contigs=len(lost),lost_correct_bp=sum(lengths[s] for s in lost),gained_correct_bp=sum(lengths[s] for s in gained),short_query_lost_bp=sum(lengths[s] for s in short if s in lost))
        if tool in probes:
            r['neighborhood']={c:{name:dict(all_queries=summary_probe(p,queries,lengths),short_queries=summary_probe(p,short,lengths),lost_short_queries=summary_probe(p,[s for s in short if s in lost],lengths)) for name,p in probes[tool][c].items()} for c in ['C0','CT']}
            r['raw_space_triage']={c:representation_triage(probes[tool][c],short,lengths,lost) for c in ['C0','CT']}
            r['representation_triage']={c:r['raw_space_triage'][c]['equal_blocks'] for c in ['C0','CT']}
        results[tool]=r
    with (out/'per-genome.tsv').open('w') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['tool','genome','C0_depth_quartile','C0_R95','CT_R95','delta_CT_minus_C0'])
        for t in scores:
            for g in pop['genomes']:
                a=scores[t]['C0']['per_genome'][g]['r95'];b=scores[t]['CT']['per_genome'][g]['r95'];w.writerow([t,g,quartiles[g],a,b,b-a])
    result=dict(status='closed at amended seed-11 scope',collection_manifest_sha256=sha(collection/'manifest.json'),population_sha256=sha(population_dir/'population.json'),probe_pool=len(pop['probe_pool']),fixed_queries=len(queries),short_queries=len(short),short_query_bp=sum(lengths[s] for s in short),excluded_reference_contigs=len(lengths)-len(pop['probe_pool']),
        binary_audit=binary,coverage=coverage,scale_controls=controls,results=results,diagnostic_scope='No new native runs; exact 10-neighbor cosine on frozen query/reference IDs; whole-contig view only; labels score neighbors and oracle gaps, never select deployed method. COMEBin mean depth defines fixed common quartiles descriptively.',
        marker_source_hashes={str(p.relative_to(source)):sha(p) for p in [source/'COMEBin/scripts/checkm_ms/bacteria.ms',source/'COMEBin/scripts/checkm_ms/archaea.ms',source/'COMEBin/scripts/unitem_markers.py',source/'COMEBin/get_final_result.py']},
        output_hashes={p.name:sha(p) for p in out.iterdir() if p.is_file()},elapsed_seconds=time.monotonic()-started)
    write(out/'summary.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('collection','population','prior_comebin','prior_other','comebin_source','output'):p.add_argument(n,type=Path)
    a=p.parse_args();close(a.collection,a.population,a.prior_comebin,a.prior_other,a.comebin_source,a.output)
