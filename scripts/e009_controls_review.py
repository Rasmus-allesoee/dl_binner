#!/usr/bin/env python3
"""Review retained E009 control outputs only, with no training or reclustering.

Read immutable exported DNA, journals, features, checkpoints and native neighbor
lists. Independently check sampled exact geometry, complete exports and reload
inference. Compute length/origin diagnostics and conservative recovery using the
separately admitted truth. Native AMBER runs separately in its own tested runtime.
The caller must first verify archive/member checksums and provider shutdown.
"""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import resource
import signal
import sys
import time
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e009_evaluate import read_partition
from e009_truth import recovery

BOUNDS=[1,500,768,1000,2500,10000]


def stratum(bp):
    """Use the existing six length strata, with all short DNA retained."""
    return max(i for i,b in enumerate(BOUNDS)if bp>=b)


def diagnostics(truth, rows, partition, population, targets):
    """Summarize complete native neighbors and bins; unknown neighbors stay in k=5.

    Geometry uses queries with a >=95% attributable truth label and a nonempty
    native neighbor list. Unknown neighbors count as unconfirmed, never disappear
    from the denominator. B-cubed is bp weighted on the restricted attributable
    population; unassigned/excluded queries have zero precision/recall. All-bin
    conservative recovery separately includes every assigned base in purity.
    """
    contigs=truth['contigs'];ids=truth['ordered_contig_ids']
    if partition['ids']!=ids:raise ValueError('Native partition axis differs')
    if len(partition['neighbors'])!=len(ids):raise ValueError('Neighbor axis differs')
    labels={q:contigs[q]['AMBER_label']for q in ids};known_total=Counter()
    cells=Counter();bins=Counter();per=defaultdict(lambda:defaultdict(float));lineages=defaultdict(Counter)
    lineage_lengths=defaultdict(lambda:defaultdict(Counter))
    for r in rows:
        q=r['contig_id'];g=labels[q];bp=int(r['length'])
        if g is not None:
            known_total[g]+=bp
            if r['bin_id']:cells[r['bin_id'],g]+=bp;bins[r['bin_id']]+=bp
    strata=[{'lower_bp':low,'upper_bp':BOUNDS[i+1]if i+1<len(BOUNDS)else None,
             'contigs':0,'bp':0,'attributable_bp':0,'nn_queries':0,'nn_query_bp':0,
             'nn_same':0,'nn_unknown':0,'nn_weighted_sum':0.,'b3_precision_sum':0.,'b3_recall_sum':0.}
            for i,low in enumerate(BOUNDS)]
    for i,r in enumerate(rows):
        q=r['contig_id'];item=contigs[q];bp=item['length'];s=strata[stratum(bp)]
        s['contigs']+=1;s['bp']+=bp;g=labels[q];nn=partition['neighbors'][i]
        if len(nn)not in(0,5)or len(set(nn))!=len(nn)or q in nn or any(n not in contigs for n in nn):
            raise ValueError('Invalid native neighbor contract')
        if g is not None:
            s['attributable_bp']+=bp
            lg=lineages[population['genomes'][g]['lineage_class']]
            ll=lineage_lengths[population['genomes'][g]['lineage_class']][BOUNDS[stratum(bp)]]
            lg['attributable_bp']+=bp;ll['attributable_bp']+=bp
            if nn:
                same=sum(labels[n]==g for n in nn);s['nn_queries']+=1;s['nn_query_bp']+=bp
                s['nn_same']+=same;s['nn_unknown']+=sum(labels[n]is None for n in nn)
                s['nn_weighted_sum']+=bp*same/5
                lg['queries']+=1;lg['query_bp']+=bp;lg['same']+=same;lg['same_weighted_sum']+=bp*same/5
                ll['queries']+=1;ll['same']+=same
            b=r['bin_id']
            if b:
                s['b3_precision_sum']+=bp*cells[b,g]/bins[b]
                s['b3_recall_sum']+=bp*cells[b,g]/known_total[g]
                lg['b3_precision_sum']+=bp*cells[b,g]/bins[b]
                lg['b3_recall_sum']+=bp*cells[b,g]/known_total[g]
        status=r['status'];per[status]['all_bp']+=bp
        for genome,n in item['confirmed_query_bp'].items():
            lineage=population['genomes'][genome]['lineage_class'];per[status][lineage+'_confirmed_bp']+=n
        for field in ['ambiguous_query_bp','nn_quarantined_query_bp','unsupported_query_bp']:
            per[status][field]+=item[field]
    for s in strata:
        s['nn_purity']=s['nn_same']/(5*s['nn_queries'])if s['nn_queries']else None
        s['nn_purity_bp_weighted']=s['nn_weighted_sum']/s['nn_query_bp']if s['nn_query_bp']else None
        s['unknown_neighbor_fraction']=s['nn_unknown']/(5*s['nn_queries'])if s['nn_queries']else None
        for metric in ['precision','recall']:
            s['b3_'+metric]=s['b3_'+metric+'_sum']/s['attributable_bp']if s['attributable_bp']else None
    attribution_bp=sum(s['attributable_bp']for s in strata)
    nn_count=sum(s['nn_queries']for s in strata)
    precision=sum(s['b3_precision_sum']for s in strata)/attribution_bp
    recall=sum(s['b3_recall_sum']for s in strata)/attribution_bp
    for lg in lineages.values():
        lg['nn_purity']=lg['same']/(5*lg['queries'])if lg['queries']else None
        lg['nn_purity_bp_weighted']=lg['same_weighted_sum']/lg['query_bp']if lg['query_bp']else None
        for metric in ['precision','recall']:lg['b3_'+metric]=lg['b3_'+metric+'_sum']/lg['attributable_bp']
    for lengths in lineage_lengths.values():
        for ll in lengths.values():ll['nn_purity']=ll['same']/(5*ll['queries'])if ll['queries']else None
    metrics=recovery(contigs,{r['contig_id']:r['bin_id']or None for r in rows},truth['reference_axis'],targets['genome_lengths'],targets['targets'])
    return {'geometry':{'attributable_eligible_queries':nn_count,'nn_purity':sum(s['nn_same']for s in strata)/(5*nn_count),
                'nn_purity_bp_weighted':sum(s['nn_weighted_sum']for s in strata)/sum(s['nn_query_bp']for s in strata),
                'scope':'all emitted native 5-NN, attributable queries; unknown neighbors unconfirmed; no new neighbor search for scores'},
            'restricted_B3':{'attributable_bp':attribution_bp,'precision':precision,'recall':recall,'f1':2*precision*recall/(precision+recall)if precision+recall else 0,
                'scope':'bp-weighted attributable contigs only; noise/excluded zero, unknown bin DNA not in this restricted denominator'},
            'length_strata':strata,'origin_by_status':dict(per),'geometry_by_lineage':dict(lineages),
            'length_geometry_by_lineage':dict(lineage_lengths),'recovery':metrics,
            'recovery_summary':{'targets':len(metrics),'macro_R95':sum(r['whole_reference_R95']for r in metrics)/len(metrics),
                'bp_weighted_R95':sum(r['recovered_bp']for r in metrics)/sum(r['reference_bp']for r in metrics),
                'at_least_50_percent':sum(r['whole_reference_R95']>=.5 for r in metrics),
                'at_least_90_percent':sum(r['whole_reference_R95']>=.9 for r in metrics),
                'targets_with_any_passing_bin':sum(r['best_bin']is not None for r in metrics)},
            'semantics':'All-bin R95: >=200kb bin, >=95% confirmed source support; full supplied bacterial denominators; duplicate-safe locus unions; not MAG quality'}


def check_geometry(arrays, part):
    """Recompute exact cosine neighbors on 128 fixed ID-hash queries, without grouping.

    Use the retained fitted grouping statistics, validate them against every valid
    row, then compare opaque-ID stable ties with native neighbors. Score summaries
    use the complete native lists rather than this verification subset.
    """
    import numpy as np
    x=arrays['features'].astype(np.float64);evidence=arrays['evidence']&(np.linalg.norm(x,axis=1)>0)
    mean=x[evidence].mean(0);std=x[evidence].std(0);usable=std>1e-8
    if not np.array_equal(mean,np.array(part['transform']['mean']))or not np.array_equal(std,np.array(part['transform']['std'])):
        raise ValueError('Native grouping population statistics differ')
    z=np.zeros_like(x);z[:,usable]=(x[:,usable]-mean[usable])/std[usable];z[~evidence]=0
    norms=np.linalg.norm(z,axis=1);valid=evidence&(norms>1e-12);z[valid]/=norms[valid,None]
    if valid.tolist()!=part['valid']:raise ValueError('Native geometry valid axis differs')
    ids=arrays['ids'].tolist();candidates=np.array(sorted(np.flatnonzero(valid),key=lambda i:ids[i]))
    queries=sorted(candidates,key=lambda i:hashlib.sha256(ids[i].encode()).digest())[:128]
    for i in queries:
        sim=np.clip(z[i:i+1]@z.T,-1,1)[0];others=candidates[candidates!=i]
        actual=[ids[j]for j in others[np.argsort(-sim[others],kind='stable')[:5]]]
        if actual!=part['neighbors'][i]:raise ValueError('Independent sampled exact neighbors differ: '+ids[i])
    return {'verified_queries':len(queries),'selection':'first128 SHA256(contigID), label blind','whole_geometry_refit_or_recluster':False}


def review(args):
    """Validate frozen scientific contracts and write new local diagnostic records."""
    import numpy as np
    import torch
    from threadpoolctl import threadpool_limits
    start=time.perf_counter();cpu=time.process_time();out=args.output;out.mkdir(exist_ok=False)
    threadpool_limits(4);torch.set_num_threads(4)
    repo=Path(__file__).absolute().parents[1];exp=repo/'experiments/E009-competitive-benchmark'
    lock=json.loads((exp/'diagnostic-package-lock.json').read_text())
    for n,v in lock['package_files'].items():
        if binding(repo/'src/dl_binner'/n)!=v:raise ValueError('Immutable product source changed')
    sys.path.insert(0,str(repo/'src'))
    from dl_binner.io import load_arrays,validate_features,read_fasta,read_depth
    from dl_binner.model import load_checkpoint,transform,forward_all
    from dl_binner.accounting import summarize_arm
    from dl_binner.runner import validate_completed
    admission=json.loads((exp/'truth-v2-admission.json').read_text());manifest=args.truth/'manifest.json'
    if not admission['admitted']or binding(manifest)!=admission['artifact_manifest']:raise ValueError('Unadmitted truth')
    for n,v in json.loads(manifest.read_text())['files'].items():
        if binding(args.truth/n)!=v:raise ValueError('Truth member differs')
    truth=json.loads((args.truth/'truth.json').read_text());targets=json.loads((args.truth/'targets.json').read_text())
    population=json.loads((exp/'truth-population-review.json').read_text());inputs=json.loads((exp/'diagnostic-feature-inputs.json').read_text())
    if binding(args.fasta)!=inputs['fasta']or binding(args.depth)!=inputs['depth']:raise ValueError('Accepted feature input differs')
    dna=read_fasta(args.fasta);ids=[q for q,_ in dna]
    if ids!=truth['ordered_contig_ids']:raise ValueError('Truth/full FASTA order differs')
    dna_hash=np.array([hashlib.sha256(s.encode()).hexdigest()for q,s in dna]);del dna
    samples,coverage=read_depth(args.depth,ids);result={'arms':{},'verification':{},'truth_manifest':binding(manifest),'source_lock':binding(exp/'diagnostic-package-lock.json')}
    baseline_tnf=None
    for pair in ['ten-depth','tnf-only']:
        root=args.root/pair;f=root/'features/features.npz';data,meta=load_arrays(f,'features');validate_features(data,meta)
        if data['ids'].tolist()!=ids or not np.array_equal(data['sequence_sha256'],dna_hash):raise ValueError('Full DNA axis/hash differs')
        if meta['min_length']!=500 or not np.array_equal(data['eligible'],data['lengths']>=500):raise ValueError('Eligibility differs')
        if meta['samples']!=(samples if pair=='ten-depth'else[]):raise ValueError('Ordered depth columns differ')
        if pair=='ten-depth':
            if samples!=inputs['ordered_columns']or not np.array_equal(data['depth'],coverage):raise ValueError('Depth matrix differs')
            baseline_tnf=data['tnf'].copy()
        elif not np.array_equal(data['tnf'],baseline_tnf):raise ValueError('Pair sequence features differ')
        cfg=json.loads((root/'.run/training.json').read_text())
        if cfg!=json.loads((repo/'src/dl_binner/resources/training.json').read_text()):raise ValueError('Seed/schedule differs')
        summary=json.loads((root/'run-summary.json').read_text())
        if not summary['checkpoint_reload_exact']:raise ValueError('Native reload failed')
        stages={k:{f:v[f]for f in ['exit_code','stop_reason','wall_seconds','peak_sampled_rss_bytes','sampled_cpu_seconds','sampled_average_cpus']}for k,v in summary['stage_resources'].items()}
        if len(stages)!=8 or any(v['exit_code']!=0 or v['stop_reason']is not None for v in stages.values()):raise ValueError('Incomplete/failed stages')
        if len(validate_completed(root))!=8:raise ValueError('Incomplete native receipt chain')
        result['verification'][pair]={'stages':stages,'native_reload_exact':True,'all_DNA_axis_hashes_match':True,'all_depth_cells_match':pair=='ten-depth','config':cfg}
        checkpoint,model=load_checkpoint(root/'training/checkpoint.pt',meta['samples']);x,valid=transform(data,checkpoint['transform'])
        reloaded=forward_all(model,x,valid,cfg['inference_batch_size']) # inference only, no fit
        for mode in ['raw','learned']:
            name=pair+'-'+mode;print('REVIEW_ARM '+name,flush=True)
            arrays,emeta=load_arrays(root/mode/'embedding/embeddings.npz','embeddings');part=json.loads((root/mode/'clustering/partition.json').read_text())
            expected=np.concatenate((data['tnf'],np.log1p(data['depth'])),axis=1).astype(np.float32)if mode=='raw'else reloaded.copy()
            expected[~data['eligible']]=0
            delta=float(np.abs(expected-arrays['features']).max())
            if mode=='raw'and not np.array_equal(expected,arrays['features']):raise ValueError('Raw feature space differs')
            if mode=='learned'and not np.allclose(expected,arrays['features'],rtol=1e-5,atol=2e-6):raise ValueError('Cross-platform reload differs')
            accounting,_=summarize_arm(f,root/mode/'bins')
            if accounting!=summary['arms'][mode]:raise ValueError('Independent all-DNA accounting differs')
            rows,assignment=read_partition(root/mode/'bins/assignments.tsv',truth)
            if [r['bin_id']or None for r in rows]!=[f'bin_{i+1:06d}'if i>=0 else None for i in part['assignment']]:raise ValueError('Native partition/export differs')
            geom=check_geometry(arrays,part)
            result['arms'][name]={'accounting':{k:v for k,v in accounting.items()if k!='bins'},'geometry_check':geom,
                'reload_max_absolute_error':delta,'cross_platform_reload_tolerance':{'rtol':1e-5,'atol':2e-6},
                'partition':binding(root/mode/'clustering/partition.json'),'assignments':binding(root/mode/'bins/assignments.tsv'),
                'diagnostics':diagnostics(truth,rows,part,population,targets)}
    result['local_resources']={'wall_seconds':time.perf_counter()-start,'process_CPU_seconds':time.process_time()-cpu,'peak_own_RSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'threads':4,'inference_only_no_fit_or_recluster':True,'platform':sys.platform}
    result['limits']=['development assembly only','3.3034% N-quarantine retained','AMBER restricted evaluation runs separately','B3 uses restricted attributable population; R95 all-bin purity includes unknown and non-target DNA']
    write_json(out/'review.json',result);print('REVIEW_COMPLETE',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['root','truth','fasta','depth','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    def timeout(*_):raise TimeoutError('Bounded local review exceeded 15 minutes')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    review(a)
