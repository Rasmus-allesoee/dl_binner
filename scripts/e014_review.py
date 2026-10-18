#!/usr/bin/env python3
"""Review verified E014 outputs locally; never fit, infer, regroup or select bins.

Requires independently verified shutdown/archive bytes. E009 conservative-v2 and
oral provided-origin recovery remain different truth modes. Native export DNA
was checked contig-by-contig before collection; this reader independently checks
its manifests, complete axes/status/base counts and unchanged label alternatives.
The all-member native recovery also binds omitted bulk DNA and graph bytes.
"""
import argparse
from collections import Counter,defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding,write_json
from e010_review import require,refinement_membership
from e013_review import verify_choices
from e009_controls_review import diagnostics,BOUNDS
from e011_review import grouping_diagnostics
from e012_review import population_cells

REPO=Path(__file__).absolute().parents[1]


def read(path):
    """Read one regular retained JSON member; no missing/member/schema fallback."""
    p=Path(path)
    require(p.is_file()and not p.is_symlink(),'Missing/linked retained JSON: '+str(p))
    return json.loads(p.read_text())


def manifest_bindings(manifest,prefix,original):
    """Compare every exported file, including omitted FASTAs, with original verified bytes."""
    for name,expected in manifest['files'].items():
        require(original[prefix+'/'+name]==expected,'Original export/member binding differs: '+name)


def export_accounting(part,data,table,accounting,manifest):
    """Independently read all native assignment rows and count every DNA/status/bin."""
    ids=part['ids'];lengths=data['lengths'];eligible=data['eligible'];totals=defaultdict(Counter);bins=Counter();seen=0
    with Path(table).open()as f:
        reader=csv.DictReader(f,delimiter='\t')
        require(reader.fieldnames==['contig_id','length','bin_id','status','reason'],'Native export schema differs')
        for i,row in enumerate(reader):
            require(i<len(ids)and row['contig_id']==ids[i]and int(row['length'])==int(lengths[i]),'Export complete ID/length axes differ')
            b=part['assignment'][i];status='excluded'if not eligible[i]else'assigned'if b>=0 else'unassigned'
            label=f'bin_{b+1:06d}'if b>=0 else''
            require(row['status']==status and row['bin_id']==label and row['reason']==part['reason'][i], 'Export labels/status/reasons differ')
            totals[status]['contigs']+=1;totals[status]['bp']+=int(lengths[i]);seen+=1
            if b>=0:bins[label]+=int(lengths[i])
    require(seen==len(ids)and accounting['contigs']==seen and accounting['bp']==int(lengths.sum()),'Export lost whole DNA')
    require(dict(totals)=={k:v for k,v in accounting['statuses'].items()if v['contigs']},'Independent native status accounting differs')
    require(len(bins)==accounting['bin_count']==manifest['bins']and all(bins[b]==v['bp']for b,v in accounting['bins'].items()),'Independent bin DNA accounting differs')
    return dict(contigs=seen,bp=int(lengths.sum()),statuses=dict(totals),bins=len(bins),all_bins_and_unassigned_DNA_counted=True)


def synthetic_rows(part,data):
    """Represent the retained old refinement labels without generating any DNA/export."""
    rows=[]
    for i,q in enumerate(part['ids']):
        b=part['assignment'][i];status='excluded'if not data['eligible'][i]else'assigned'if b>=0 else'unassigned'
        rows.append(dict(contig_id=q,length=str(int(data['lengths'][i])),bin_id=f'bin_{b+1:06d}'if b>=0 else'',status=status,reason=part['reason'][i]))
    return rows


def parent_geometry(data,state,part,labels):
    """Compare 128 fixed ID-hash queries in raw input and native learned geometry.

Raw = unit-normalized concatenation of saved parent sqrt-TNF/z-score/L2 and
log1p-depth/z-score/sqrt(S), with observed zero-depth masking. No statistics are
refit, no index is built. Full eligible parent references include unknowns;
unknown learned/raw neighbors stay in the five-neighbor denominator. This is a
bounded mechanism diagnostic, separate from the complete native-neighbor census.
"""
    import numpy as np
    eligible=np.flatnonzero(data['eligible']);ids=part['ids'];blocks=[]
    for key,source in [('tnf',np.sqrt(data['tnf'][eligible])),('depth',np.log1p(data['depth'][eligible]))]:
        mean=np.asarray(state[key]['mean']);std=np.asarray(state[key]['std']);x=source.astype(np.float64);use=std>1e-8
        z=np.zeros_like(x);z[:,use]=(x[:,use]-mean[use])/std[use]
        if key=='tnf':z/=np.maximum(np.linalg.norm(z,axis=1,keepdims=True),1e-12)
        else:z[~data['depth_evidence'][eligible]]=0;z/=np.sqrt(max(z.shape[1],1))
        blocks.append(z.astype(np.float32))
    raw=np.concatenate(blocks,axis=1).astype(np.float64);raw/=np.maximum(np.linalg.norm(raw,axis=1,keepdims=True),1e-12)
    present=np.linalg.norm(raw,axis=1)>1e-12;references=eligible[present];raw=raw[present]
    chosen=sorted(range(len(references)),key=lambda j:hashlib.sha256(ids[int(references[j])].encode()).digest())[:128]
    results=[]
    for j in chosen:
        i=int(references[j]);scores=raw@raw[j];scores[j]=-np.inf
        threshold=np.partition(scores,-5)[-5];candidates=np.flatnonzero(scores>=threshold)
        neighbors=sorted(candidates,key=lambda k:(-scores[k],ids[int(references[k])]))[:5]
        raw_ids=[ids[int(references[k])]for k in neighbors];learned=part['neighbors'][i];label=labels.get(ids[i])
        if label is None:continue
        results.append(dict(id=ids[i],length=int(data['lengths'][i]),origin_label=label,raw_same=sum(labels.get(q)==label for q in raw_ids)/5,
            learned_same=sum(labels.get(q)==label for q in learned)/5,raw_unknown=sum(labels.get(q)is None for q in raw_ids),
            learned_unknown=sum(labels.get(q)is None for q in learned),learned_neighbor_count=len(learned)))
    by_length={}
    for low in BOUNDS:
        rows=[r for r in results if max(b for b in BOUNDS if r['length']>=b)==low]
        by_length[str(low)]=dict(queries=len(rows),raw_mean=sum(x['raw_same']for x in rows)/len(rows)if rows else None,
            learned_mean=sum(x['learned_same']for x in rows)/len(rows)if rows else None)
    return dict(query_selection='First128 SHA256(eligible opaque/contig ID), label blind; attributable subset reported',
        reference_contigs=len(references),queries=results,length_strata=by_length,statistics_refitted=False,
        raw_mean=sum(r['raw_same']for r in results)/len(results)if results else None,
        learned_mean=sum(r['learned_same']for r in results)/len(results)if results else None,
        saved_transform_sha256=hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest())


def oral_labels(artifact,ids,lengths):
    """Stream admitted origins/masks into compact arrays and refuse any axis drift."""
    import numpy as np
    meta=read(Path(artifact)/'manifest.json');admit=read(Path(artifact)/'admission.json')
    require(admit['admitted']and admit['manifest']==dict(binding(Path(artifact)/'manifest.json'),md5=hashlib.md5((Path(artifact)/'manifest.json').read_bytes()).hexdigest()),'Oral admission differs')
    require(binding(Path(artifact)/'rows.jsonl.gz')=={k:meta['rows'][k]for k in ['bytes','sha256']},'Oral oracle bytes differ')
    genomes=sorted({r['genome']for r in meta['references'].values()});codes={g:i for i,g in enumerate(genomes)}
    labels=np.full(len(ids),-1,np.int32);quarantine=np.zeros(len(ids),np.int32);shared=np.zeros(len(ids),bool);n=0
    with gzip.open(Path(artifact)/'rows.jsonl.gz','rt')as f:
        for i,line in enumerate(f):
            row=json.loads(line);require(i<len(ids)and row['id']==ids[i]and row['length']==int(lengths[i]),'Oral full ordered source/length axis differs')
            labels[i]=codes[row['genome']]if row['genome']is not None else-1;quarantine[i]=row['quarantined_bp'];shared[i]=row['shared_forward_query']or row['shared_complete_reference'];n+=1
    require(n==len(ids)and int(quarantine.sum())==meta['counts']['quarantined_bp'],'Oral population/quarantine differs')
    return labels,quarantine,shared,genomes,meta


def oral_population(part,data,labels,quarantine,shared,genomes,targets,clean):
    """Count all origin/length/eligibility/status/marker populations and grouping DNA."""
    cells=Counter();known=Counter();assigned=Counter();all_bins=Counter();support=Counter();population=defaultdict(Counter);query_bp=0;same_bp=0;queries=0;same=0
    ids=part['ids'];index={q:i for i,q in enumerate(ids)}
    for i,q in enumerate(ids):
        g=int(labels[i]);b=part['assignment'][i];bp=int(data['lengths'][i])
        if g>=0:
            known[g]+=bp
            if b>=0:cells[b,g]+=bp;assigned[b]+=bp;support[b,g]+=bp-int(quarantine[i])
        if b>=0:all_bins[b]+=bp
    p=r=0.;native_by_length=defaultdict(Counter)
    for i,q in enumerate(ids):
        g=int(labels[i]);b=part['assignment'][i];bp=int(data['lengths'][i]);status='excluded'if not data['eligible'][i]else'assigned'if b>=0 else'unassigned'
        origin='unknown'if g<0 else'positive_bacterial_source'if genomes[g]in targets else'non_target_source'
        low=max(x for x in BOUNDS if bp>=x);key='|'.join([str(low),origin,'eligible'if data['eligible'][i]else'excluded',status,'clean_marker'if q in clean else'no_clean_marker'])
        v=population[key];v['contigs']+=1;v['bp']+=bp;v['non_ACGT_quarantine_bp']+=int(quarantine[i]);v['known_shared_query_bp']+=bp if shared[i]else 0
        nn=part['neighbors'][i]
        if nn:require(len(nn)==5 and len(set(nn))==5 and q not in nn and all(n in index for n in nn),'Oral native neighbor axis malformed')
        if g>=0:
            if b>=0:p+=bp*cells[b,g]/assigned[b];r+=bp*cells[b,g]/known[g]
            if nn:
                count=sum(int(labels[index[n]])==g for n in nn);queries+=1;same+=count;query_bp+=bp;same_bp+=bp*count/5
                v=native_by_length[str(low)];v['queries']+=1;v['query_bp']+=bp;v['same']+=count;v['same_weighted_bp']+=bp*count/5
    total=sum(known.values());p=p/total if total else 0;r=r/total if total else 0
    dominant={}
    for (b,g),n in support.items():
        if b not in dominant or (n,g)>dominant[b]:dominant[b]=(n,g)
    bins=[]
    for b,bp in sorted(all_bins.items()):
        n,g=dominant.get(b,(0,None))
        bins.append(dict(bin=b,bp=bp,dominant_source=genomes[g]if g is not None else None,supported_purity=n/bp))
    return dict(population_cells={k:dict(v)for k,v in population.items()},all_bp=sum(v['bp']for v in population.values()),
        geometry=dict(queries=queries,nn_purity=same/(5*queries)if queries else None,nn_purity_bp_weighted=same_bp/query_bp if query_bp else None,length_strata={k:dict(v)for k,v in native_by_length.items()}),
        origin_B3=dict(bp=total,precision=p,recall=r,f1=2*p*r/(p+r)if p+r else 0,scope='Provided-origin contigs; short/noise/excluded count zero. Recovery uses full references separately.'),
        bins=bins,large_bins=sum(v['bp']>=200000 for v in bins),large_bins_below95=sum(v['bp']>=200000 and v['supported_purity']<.95 for v in bins))


def marker_review(cache,features,original_inventory,output):
    """Validate all new oral gene rows and independently reduce cached hit loci.

Only domain-bearing genes need be retained in RAM; every other row still receives
the same ID, coordinate, partial flag and protein-length validation. Proteins.faa
stays on the VM, bound by the independently verified original work inventory.
No gene caller or HMM search is invoked, and no marker threshold is changed.
"""
    import numpy as np
    from dl_binner.candidate.markers import POLICY,runtime,reduce_hits
    from dl_binner.io import id_digest
    cache=Path(cache);original=read(original_inventory)['all_result_members'];receipt=read(cache/'cache.json')
    require(receipt['policy']==POLICY and receipt['runtime']==runtime(),'Cached marker policy/source/runtime differs')
    for name,expected in receipt['files'].items():
        require(original['shared/oral-markers/'+name]==expected,'Cached marker original member differs')
        if (cache/name).is_file():require(binding(cache/name)==expected,'Local cached marker member differs')
    with np.load(features,allow_pickle=False)as a:ids=a['ids'].tolist();lengths=a['lengths']
    axis=dict(zip(ids,map(int,lengths)));domains=read(cache/'domains.json');evidence=read(cache/'evidence.json');asset=read(cache/'asset.json')
    require(evidence['ids']==ids and evidence['ids_sha256']==id_digest(ids),'New marker full contig axis differs')
    required={r['gene']for r in domains};genes={};seen=set();partials=0
    with (cache/'genes.jsonl').open()as f:
        for raw in f:
            g=json.loads(raw);name=g.pop('gene');q=g['contig']
            require(type(name)is str and name not in seen and q in axis and all(type(g[k])is int for k in ['start','end','strand','protein_length'])
                and g['strand']in(-1,1)and 0<=g['start']<g['end']<=axis[q]
                and type(g['partial_begin'])is bool and type(g['partial_end'])is bool and g['protein_length']>=1
                and 3*g['protein_length']<=g['end']-g['start'],'Malformed cached gene row, including non-hit genes')
            seen.add(name);partials+=g['partial_begin']or g['partial_end']
            if name in required:genes[name]=g
    require(len(seen)==receipt['genes']and len(domains)==receipt['domains']and set(genes)==required,'Complete cached gene/domain count differs')
    reduced=reduce_hits(genes,domains,asset['families'])
    require(all(evidence[k]==v for k,v in reduced.items()),'Independent retained marker reduction differs')
    result=dict(status='SUCCESS',clean=list(reduced['clean']),genes=len(seen),partial_genes=int(partials),
        hit_genes=len(genes),domains=len(domains),canonical_families=len(set(asset['families'].values())),
        clean_marker_contigs=len(reduced['clean']),ambiguous_genes=len(reduced['ambiguous']),multicopy_rows=len(reduced['multicopy']),
        implementation=receipt['runtime'],cache=binding(cache/'cache.json'),all_gene_rows_validated=True,
        protein_bytes='Reverified in-place against original manifest; not exported/read locally',new_detector_or_HMM_search=False)
    write_json(output,result);print('E014_ORAL_MARKER_CACHE_REVIEWED',len(seen),len(domains),flush=True);return result


def unit_review(unit,features,original_inventory,output,dataset,marker_clean,truth_root,graph_proof):
    """Review one complete retained unit and its parent/old/selected alternatives."""
    import numpy as np
    from threadpoolctl import threadpool_limits
    from dl_binner.multiview.views import load
    from dl_binner.multiview.arrays import load_arrays
    from e012_marker_audit import verify_truth
    from e014_oral_truth import evaluate
    started=time.monotonic();unit,features,output=Path(unit),Path(features),Path(output);output.mkdir(exist_ok=False);threadpool_limits(4)
    original=read(original_inventory)['all_result_members'];data,meta=load(features);ids=data['ids'].tolist();checkpoint=read(unit/'train/checkpoint.json')
    cfg=read(REPO/'src/dl_binner/resources'/('candidate.json'if unit.name=='oral-dev4'else'multiview.json'))
    require(checkpoint['config']==cfg and checkpoint['threads']==4 and checkpoint['loader_workers']==0
        and len(checkpoint['history'])==20 and [h['epoch']for h in checkpoint['history']]==list(range(1,21))
        and all(h['parents_seen']==checkpoint['training_parents']and np.isfinite(h['loss'])for h in checkpoint['history']),'Frozen schedule/exposure differs')
    require(checkpoint['training_features_sha256']==binding(features)['sha256']and checkpoint['sha256']==binding(unit/'train/checkpoint.pt')['sha256'],'Training feature/checkpoint bindings differ')
    require(checkpoint['training_views_sha256']==original['units/'+unit.name+'/features/views.npz']['sha256'],'Training view bank differs')
    if unit.name!='oral-dev4':require(checkpoint['training_parents']==int(data['eligible'].sum()),'Not every eligible parent trained')
    em=read(unit/'embeddings.json');require(em['reload_exact']and em['checkpoint_sha256']==checkpoint['sha256']and em['features_sha256']==binding(features)['sha256'],'Native exact reload receipt differs')
    require(original['units/'+unit.name+'/embeddings.npz']==original['units/'+unit.name+'/train/reference.npz'],'Native before/after reload arrays differ')
    pre,old,post=[read(unit/p)for p in ['group/partition.json','refine/old-partition.json','refine/partition.json']]
    require(pre['ids']==old['ids']==post['ids']==ids and pre['config']==read(REPO/'src/dl_binner/resources/multiview.json'),'Full axes/downstream freeze differs')
    proof=read(graph_proof);audit=pre['audit'];sample=proof['geometry']['queries'][:pre['config']['audit_queries']]
    require(proof['status']=='PASS'and proof['partition']==binding(unit/'group/partition.json')
        and proof['graph']==original['units/'+unit.name+'/group/graph.npz']
        and proof['embedding']==original['units/'+unit.name+'/embeddings.npz']
        and proof['embedding_metadata']==em and proof['objective']==pre['objective']
        and pre['parent_features_sha256']==binding(features)['sha256']
        and pre['transform']=='none; learned unit sphere preserved','Native geometry/source bindings differ')
    require([r['id']for r in sample]==audit['query_ids']
        and np.mean([r['recall_k']for r in sample])==audit['mean_tie_aware_recall']
        and min(r['recall_k']for r in sample)==audit['min_query_recall']
        and audit['mean_tie_aware_recall']>=pre['config']['min_neighbor_recall'],'Independent native neighbor audit differs')
    refinement_membership(pre,old)
    choices=verify_choices(pre,old,post,read(unit/'refine/decisions.json'),read(unit/'refine/alternatives.json'))
    completed=read(unit/'refine/completed.json');require(completed['status']=='SUCCESS'and not completed['truth_accessed']and completed['policy']=='unchanged E013','Native refinement gate differs')
    require(completed['parent_sha256']==binding(unit/'group/partition.json')['sha256']
        and completed['features_sha256']==binding(features)['sha256']
        and completed['embeddings_sha256']==proof['embedding']['sha256']
        and completed['partition_sha256']==binding(unit/'refine/partition.json')['sha256'],'Refinement retained input/output bindings differ')
    account=read(unit/'export/accounting.json');clean=set(read(marker_clean)['clean']);checks={}
    for arm,part in [('pre',pre),('post',post)]:
        manifest=read(unit/'export'/arm/'manifest.json');manifest_bindings(manifest,'units/'+unit.name+'/export/'+arm,original)
        require(manifest['features_sha256']==binding(features)['sha256']and manifest['fasta_sha256']==meta['fasta_sha256'],'Export input hashes differ')
        checks[arm]=export_accounting(part,data,unit/'export'/arm/'assignments.tsv',account[arm],manifest)
    result=dict(status='SUCCESS',unit=unit.name,dataset=dataset,source='858b7cc',contracts=checks,choices=choices,
        checkpoint=checkpoint,features_metadata=meta,embedding_metadata=em,refinement=completed,native_graph_review=proof,arms={},
        portability='Original E010 Mac allclose remains failed. Use unchanged original native vectors and passing native exact reload; no local model inference.')
    if dataset=='E009':
        lock=read(REPO/'experiments/E013-marker-quality/review-lock.json');truth_path=verify_truth(lock);truth=read(truth_path/'truth.json');targets=read(truth_path/'targets.json');pop=read(REPO/lock['population_path'])
        require(ids==truth['ordered_contig_ids']and meta['samples']==read(REPO/'experiments/E010-coherent-prototype/candidate-lock.json')['ordered_depth_columns'],'E009 full truth/depth axes differ')
        for arm,part in [('pre',pre),('old',old),('post',post)]:
            rows=synthetic_rows(part,data);metrics=diagnostics(truth,rows,part,pop,targets)
            grouped=grouping_diagnostics(truth,rows,pop,targets,clean);require(grouped['recovery']==metrics['recovery'],'Independent E009 recovery contracts disagree')
            result['arms'][arm]=dict(diagnostics=metrics,populations=population_cells(rows,truth,pop,clean),grouping=grouped)
        labels={q:truth['contigs'][q]['AMBER_label']for q in ids}
    else:
        lab,quarantine,shared,genomes,truth=oral_labels(truth_root,ids,data['lengths']);require(not meta['samples'],'Oral depth is not admitted')
        require(meta['fasta_sha256']==truth['model_input']['sha256'],'Oral source-blind DNA differs')
        for arm,part,path in [('pre',pre,unit/'group/partition.json'),('old',old,unit/'refine/old-partition.json'),('post',post,unit/'refine/partition.json')]:
            evaluated=evaluate(truth_root,path,output/('truth-'+arm))
            result['arms'][arm]=dict(evaluation=evaluated,grouping=oral_population(part,data,lab,quarantine,shared,genomes,truth['targets'],clean))
        labels={q:(genomes[int(lab[i])]if lab[i]>=0 else None)for i,q in enumerate(ids)}
    # Saved alternatives are fully checked/evaluated; retain only the parent
    # during the bounded raw-matrix diagnostic, rather than three million-row
    # Python partition objects alongside its numerical temporaries.
    del old,post,part
    result['raw_learned_geometry']=parent_geometry(data,checkpoint['transform'],pre,labels)
    query_groups=defaultdict(list)
    for row in result['raw_learned_geometry']['queries']:
        lineage=pop['genomes'][row['origin_label']]['lineage_class']if dataset=='E009'else'provided_bacterial_source'
        query_groups[lineage].append(row)
    result['raw_learned_geometry']['by_lineage']={g:dict(queries=len(rows),raw_mean=sum(x['raw_same']for x in rows)/len(rows),
        learned_mean=sum(x['learned_same']for x in rows)/len(rows))for g,rows in query_groups.items()}
    result['local_wall_seconds']=time.monotonic()-started;write_json(output/'review.json',result)
    print('E014_UNIT_REVIEWED',unit.name,{a:(v['diagnostics']['recovery_summary']if dataset=='E009'else v['evaluation']['origin']['recovery_summary'])for a,v in result['arms'].items()},flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['unit','features','original-inventory','output','marker-clean','truth-root','marker-cache','graph-proof']:p.add_argument('--'+key,type=Path)
    p.add_argument('--dataset',choices=['E009','oral']);a=p.parse_args()
    if a.marker_cache:marker_review(a.marker_cache,a.features,a.original_inventory,a.output)
    else:unit_review(a.unit,a.features,a.original_inventory,a.output,a.dataset,a.marker_clean,a.truth_root,a.graph_proof)
