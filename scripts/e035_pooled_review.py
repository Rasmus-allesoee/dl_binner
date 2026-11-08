#!/usr/bin/env python3
"""Review admitted pooled-support ledgers without fits, edge changes or cloud work.

Require independent complete transport/shutdown admission. Reuse the frozen readers
and conservative PAF semantics to diagnose endpoint spans, not template error rates.
"""
import argparse,gzip,json,sys,time
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'src'))
from e024_coverage import binding


def counter_contract(c,histogram):
    """Close E035 template outcomes using its retained calibration histogram.

    E035 counts calibration directly in the histogram, unlike E034's separate
    calibration_eligible_templates counter. Do not invent that absent field.
    """
    from e034_pilot_review import REJECTIONS
    assert all(type(v)is int and v>=0 for v in c.values())
    assert c['templates']==c['qualified_both_mates']+sum(c.get(k,0)for k in REJECTIONS)
    assert sum(histogram)+c.get('cross_contig_qualified_templates',0)<=c['qualified_both_mates']
    assert sum(v for k,v in c.items()if k.startswith('qualified_read_length_'))==2*c['qualified_both_mates']


def endpoint(q,a,b,blocks,vetoes):
    """Count conservative confirmed/ambiguous/quarantined bp in one span envelope."""
    values=[v for v in blocks.get(q,[])if v['q0']<b and v['q1']>a]
    masks=[v for v in vetoes.get(q,[])if v[0]<b and v[1]>a]
    positions={a,b}
    for v in values:positions.update([max(a,v['q0']),min(b,v['q1'])])
    for x,y in masks:positions.update([max(a,x),min(b,y)])
    confirmed=Counter();other=Counter()
    s=sorted(positions)
    for x,y in zip(s,s[1:]):
        if any(lo<y and hi>x for lo,hi in masks):other['quarantined']+=y-x;continue
        g={v['genome']for v in values if v['q0']<y and v['q1']>x}
        if len(g)==1:confirmed[next(iter(g))]+=y-x
        else:other['ambiguous'if g else'unsupported']+=y-x
    assert sum(confirmed.values())+sum(other.values())==b-a
    label=next(iter(confirmed))if len(confirmed)==1 and sum(confirmed.values())==b-a else None
    return label,dict(confirmed),dict(other)


def inspect(base,output):
    """Verify actual stages/source, all axes/counters/graphs and localized diagnostics."""
    import numpy as np
    from dl_binner.genomegraph import pooled,links
    from e014_review import oral_labels
    from threadpoolctl import threadpool_limits
    threadpool_limits(4);base=Path(base);out=Path(output)
    integrity=json.loads((base/'integrity.json').read_text());assert integrity['status']=='PASS'
    assert json.loads((base/'control/provider.json').read_text())['status']=='TERMINATED'
    c=json.loads((base/'objects/completion.json').read_text());assert c['status']=='SUCCESS_INFORMATION_AUDIT'and c['audit_completed']and not c['community_models_fit']and not c['taxonomy_acquired']
    e=base/'restored/evidence';work=base/'restored/work'
    for lock in ['source-lock.json','pooled-native-launch-lock.json']:
        for n,b in json.loads((ROOT/'experiments/E035-confidence-taxonomy'/lock).read_text())['files'].items():
            assert binding(ROOT/n)==b and binding(e/'source-repository'/n)==b,n
    got={s['stage']:s['resources']for s in c['stages']}
    wanted={'owned-package-install','complete-native-runtime','original-inputs-before','actual-native-tiny','pool-E009','pool-oral','original-inputs-after'}|{'sample-'+v+'-%02d'%i for v in ['E009','oral']for i in range(10)}
    assert set(got)==wanted and len(c['stages'])==27
    for n,r in got.items():assert r==json.loads((e/'logs'/(n+'.exit.json')).read_text())and r['exit_code']==0 and r['stop_reason']is None,n
    before=json.loads((e/'gates/inputs-before.json').read_text());assert before==json.loads((e/'gates/inputs-after.json').read_text())
    runtime=json.loads((e/'gates/runtime.json').read_text());assert runtime['package_files']==json.loads((ROOT/'experiments/E035-confidence-taxonomy/pooled-native-package-lock.json').read_text())['package_files']
    sup=json.loads((e/'logs/supervision.json').read_text());watch=json.loads((base/'objects/watchdog-exit.json').read_text());assert watch['shutdown']and watch['decision']=='workflow exited'and watch['boot_id']==sup['boot_id']and watch['expected_process']==sup['process']
    plan=json.loads((e/'science-plan.json').read_text());frozen=json.loads((ROOT/'experiments/E035-confidence-taxonomy/pooled-audit-plan.json').read_text())
    axes=json.loads((ROOT/'experiments/E033-multiscale-bam/reuse-lock.json').read_text())['axes']
    data=json.loads((ROOT/'experiments/E009-competitive-benchmark/gcp-data-observed.json').read_text())
    def samplelist(v):
        if isinstance(v,dict):
            if isinstance(v.get('samples'),list)and v['samples']and isinstance(v['samples'][0],dict)and 'read_pairs'in v['samples'][0]:return v['samples']
            for x in v.values():
                z=samplelist(x)
                if z:return z
        return None
    totals={x['column']:x['read_pairs']*2 for x in samplelist(data)}
    result=dict(status='PASS_COMPLETED_INFORMATION_AUDIT',actual_stage_exits={n:r['exit_code']for n,r in got.items()},watchdog_exit_verified=True,original_inputs_unchanged=True,source_files=542,operational_source_files=11,native_distributions=len(runtime['distributions']),native_package_files=len(runtime['package_files']),parent_systemd_numeric_exit_unavailable=True,communities={})
    lock=json.loads((ROOT/'experiments/E013-marker-quality/review-lock.json').read_text());truthroot=ROOT/lock['truth_root']
    for n,b in lock['truth_files'].items():assert binding(truthroot/n)==b
    assert binding(ROOT/lock['paf_path'])==lock['paf']and binding(ROOT/lock['policy_path'])==lock['policy']
    truth=json.loads((truthroot/'truth.json').read_text());from e009_truth_v2 import parse_paf
    references=json.loads((truthroot/'reference-map.json').read_text())
    blocks,vetoes,pafcounts=parse_paf(ROOT/lock['paf_path'],{q:v['length']for q,v in truth['contigs'].items()},references['aliases'],json.loads((ROOT/lock['policy_path']).read_text()))
    assert pafcounts==truth['alignments']
    for community,unit in [('E009','E009-noGLM'),('oral','oral-noGLM')]:
        at=work/community;a,m=links.read(at/'pooled');expected=axes[unit];assert (len(a['ids']),int(a['lengths'].sum()),int(a['eligible'].sum()))==(expected['rows'],expected['bp'],expected['eligible'])
        # save_arrays writes a copy with its actual NPZ hash; pool() returns the
        # pre-serialization metadata. Require exactly that one writer-owned key.
        assert m==dict(c['information'][community]['result'],sha256=binding(at/'pooled/graph.npz')['sha256'])and m['samples']==expected['samples']and m['policy']==links.policy()
        assert links.utility(a['edges'],a['ids'].tolist(),a['lengths'],a['eligible'])==m['utility']
        samples=[];observations=[];counters=Counter()
        for i,record in enumerate(frozen['BAMs'][community]):
            r=at/('sample-%02d'%i);aa,mm=pooled.read(r);transport=json.loads((at/('sample-%02d-transport.json'%i)).read_text());assert mm['sample']==record['sample']and mm['source']=={k:record[k]for k in ['bytes','sha256']}
            assert transport['status']=='PASS'and transport['ledger']==binding(r/'completed.json')and transport['record']==plan['BAMs'][community][i]
            for k in ['ids','lengths','eligible']:assert np.array_equal(aa[k],a[k])
            if community=='oral':assert transport['transport']['generation']==record['generation']and transport['transport']['server_crc32c']==record['crc32c']and transport['temporary_verified_copy_removed']
            wanted_records=record['records']if community=='oral'else totals[record['sample']]
            assert mm['counters']['alignment_records']==wanted_records and mm['collator_exit']==0
            counter_contract(mm['counters'],mm['histogram']);h=np.asarray(mm['histogram']);assert int(np.searchsorted(np.cumsum(h),int(np.ceil((h.sum()-1)*.995))+1))==mm['insert_limit']
            counters.update(mm['counters']);observations.append(aa['observations']);samples.append(dict(sample=record['sample'],records=wanted_records,templates=mm['counters']['templates'],qualified=mm['counters']['qualified_both_mates'],calibrated=len(aa['observations']),raw=mm['pre_support_observations'],insert_limit=mm['insert_limit'],median_insert=int(np.searchsorted(np.cumsum(h),(h.sum()+1)//2)),calibration_pairs=int(h.sum()),overlap_templates=mm['counters'].get('calibration_reference_span_overlap_templates',0)))
        assert sum(len(o)for o in observations)==m['calibrated_unique_observations']
        degree=np.bincount(a['edges'].ravel(),minlength=len(a['ids']))
        assert degree.max()<=64 and m['hub_edges_removed']==0
        reference=np.log1p(a['support'])/np.sqrt(np.maximum(degree[a['edges'][:,0]],1)*np.maximum(degree[a['edges'][:,1]],1))
        # Linux and macOS libm can round log1p differently. Preserve the failed
        # bitwise comparison and native vectors; independently bound rounding
        # across log/sqrt/divide to four float64 ULPs. This is not the original
        # embedding-portability test, whose failed tolerance remains unchanged.
        delta=np.abs(a['weights']-reference);ulp=np.spacing(reference)
        weight_check=dict(bitwise_equal=bool(np.array_equal(a['weights'],reference)),
            unequal=int(np.count_nonzero(delta)),maximum_absolute_error=float(delta.max(initial=0)),
            maximum_ULPs=float((delta/ulp).max(initial=0)),rounding_bound_ULPs=4,
            native_weights_unchanged=True,original_embedding_portability_unchanged=True)
        assert np.isfinite(delta).all()and (delta<=4*ulp).all()
        # Recompute the single frozen pooling rule in memory, without emitting a new graph.
        groups=defaultdict(list)
        for i,obs in enumerate(observations):
            for o in obs:groups[int(o['i']),int(o['j'])].append((i,int(o['a']),int(o['b']),int(o['orientation'])))
        decisions=json.loads((at/'pooled/decisions.json').read_text());assert len(decisions)==len(groups)
        edge_index={tuple(map(int,pair)):i for i,pair in enumerate(a['edges'])};cross_library_new=0
        for row in decisions:
            x=np.asarray(groups[tuple(row['edge'])],np.int64);direction=int(np.bincount(x[:,3],minlength=4).argmax());kept=x[x[:,3]==direction];counts=np.bincount(kept[:,0],minlength=10)
            reason='below_pooled_unique_support'if len(kept)<3 else'pooled_orientation_conflict'if len(kept)/len(x)<.9 else'pooled_distinct_starts'if min(len(np.unique(kept[:,1])),len(np.unique(kept[:,2])))<2 else'supported'
            assert row['reason']==reason and row['counts']==counts.tolist()and row['orientation']==direction
            if reason=='supported':
                index=edge_index[tuple(row['edge'])];assert np.array_equal(a['sample_support'][index],counts)and int(a['support'][index])==len(kept)
                cross_library_new+=int(max(counts)<3)
        linked=np.zeros(len(a['ids']),bool);eligible_edges=a['edges'][a['eligible'][a['edges']].all(1)];linked[eligible_edges.ravel()]=True
        if community=='E009':
            assert a['ids'].tolist()==truth['ordered_contig_ids'];labels=[truth['contigs'][str(q)]['AMBER_label']for q in a['ids']];quarantine=np.asarray([truth['contigs'][str(q)]['nn_quarantined_query_bp']for q in a['ids']]);targets=set(json.loads((truthroot/'targets.json').read_text())['targets']);shared=np.zeros(len(labels),bool)
        else:
            labs,quarantine,shared,genomes,tm=oral_labels(ROOT/'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1',a['ids'].tolist(),a['lengths']);labels=[genomes[x]if x>=0 else None for x in labs];targets=set(tm['targets'])
        population=defaultdict(Counter)
        for i,(length,eligible)in enumerate(zip(a['lengths'],a['eligible'])):
            low=max(b for b in [0,500,1000,1500,2500,10000]if length>=b);origin='unknown'if labels[i]is None else'target'if labels[i]in targets else'non_target'
            v=population[f'{low}|{origin}|'+('eligible'if eligible else'excluded')+'|'+('linked'if linked[i]else'unlinked')];v['contigs']+=1;v['bp']+=int(length);v['quarantined_bp']+=int(quarantine[i]);v['known_shared_bp']+=int(length)if shared[i]else 0
        assert sum(v['contigs']for v in population.values())==len(a['ids'])and sum(v['bp']for v in population.values())==int(a['lengths'].sum())
        dominant=Counter();loci=Counter();locus_bp=Counter();cache={};eligible_loci=Counter()
        for pair in a['edges']:
            i,j=map(int,pair);g,h=labels[i],labels[j];dominant['unresolved'if g is None or h is None else'same'if g==h else'different']+=1
        for obs in observations:
            for o in obs:
                pair=(int(o['i']),int(o['j']));index=edge_index.get(pair)
                if index is None or o['orientation']!=a['orientations'][index]:continue
                resolved=[]
                for node,start,end in [(pair[0],int(o['a']),int(o['a_end'])),(pair[1],int(o['b']),int(o['b_end']))]:
                    key=(node,start,end)
                    if key not in cache:
                        if community=='E009':cache[key]=endpoint(str(a['ids'][node]),start,end,blocks,vetoes)
                        else:cache[key]=(labels[node]if not shared[node]and quarantine[node]==0 else None,{},dict(known_shared_or_quarantine=int(shared[node]or quarantine[node]>0)))
                    label,confirmed,other=cache[key];resolved.append(label)
                    for k,v in other.items():locus_bp[k]+=v
                name='unresolved'if None in resolved else'same'if resolved[0]==resolved[1]else'different'
                loci[name]+=1
                if a['eligible'][list(pair)].all():eligible_loci[name]+=1
        result['communities'][community]=dict(full_axes=expected,utility=m['utility'],all_edges=len(a['edges']),samples=samples,counters=dict(counters),decision_counts=m['decision_counts'],weight_formula_review=weight_check,new_edges_requiring_cross_library_support=cross_library_new,dominant_edge_relations=dict(dominant),accepted_orientation_observation_locus_relations=dict(loci),eligible_observation_locus_relations=dict(eligible_loci),supporting_locus_unresolved_bp=dict(locus_bp),locus_semantics='E009 complete span unanimous conservative genome after all competitor and ambiguity vetoes; not gap-free BAM CIGAR and not measured template-error rate'if community=='E009'else'Provided-source origin only; known-shared/quarantine contigs unresolved; exact mate-level sequence uniqueness unadmitted',population_cells={k:dict(v)for k,v in population.items()})
        print('REVIEW_COMMUNITY',community,m['utility']['status'],dict(loci),flush=True)
    result.update(full_denominators=dict(E009=156,oral=799),E009_N_quarantine_percent=3.3034,oral_known_shared_retained=True,new_binner_fits=0,new_R95_scores=0,thresholds_or_edges_changed=False,old_scores_replayed=False,finished_epoch=time.time())
    out.write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();inspect(a.base,a.output)
