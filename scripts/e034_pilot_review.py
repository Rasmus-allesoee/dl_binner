#!/usr/bin/env python3
"""Audit the closed E034 pilot without fitting, scoring or reopening cloud compute.

Requires independently downloaded exact generations, complete archive/member/alias
proofs, shutdown and financial admission. Reads original sealed physical caches,
full axes and conservative truth only to describe populations and edge reliability.
It cannot change links, utility gates, partitions, truth or accepted old results.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write

REJECTIONS=('template_record_count_not_two','excessive_template_records',
 'alternative_or_chimeric_template','invalid_or_missing_mate_role','duplicate_mate_role',
 'template_flag_exclusion','low_or_unknown_template_MAPQ','template_identity_exclusion',
 'partial_template_alignment','inconsistent_actual_mate_metadata')


def counter_contract(c):
    """Require one terminal group outcome and retain early-exit filter semantics."""
    if any(type(n) is not int or n<0 for n in c.values()) or c.get('templates',0)<=0:
        raise ValueError('Invalid template counter')
    if c['qualified_both_mates']<c.get('cross_contig_qualified_templates',0)+c['calibration_eligible_templates']:
        raise ValueError('Qualified calibration/cross populations overlap or exceed admission')
    if c['templates']!=c.get('qualified_both_mates',0)+sum(c.get(n,0) for n in REJECTIONS):
        raise ValueError('Template terminal outcomes do not close')
    return dict(templates=c['templates'],exactly_two_record_fraction=1-(c.get('template_record_count_not_two',0)+c.get('excessive_template_records',0))/c['templates'],
        terminal_rejection_fractions={n:c[n]/c['templates'] for n in REJECTIONS if n in c},
        qualified_both_mates=c['qualified_both_mates'],
        qualified_same_contig_other_orientation_or_over_insert=c['qualified_both_mates']-c.get('cross_contig_qualified_templates',0)-c['calibration_eligible_templates'],
        interpretation='First terminal rejection per template; accepted_reads/bases may include an earlier mate of a later-refused template, not a full both-mate coverage census')


def inspect(base,output):
    """Verify actual eight exits, native source/tiny, both graphs and all populations."""
    import numpy as np
    from threadpoolctl import threadpool_limits
    from dl_binner.genomegraph.links import read,utility
    from e014_review import oral_labels
    from e024_control import verify_seal
    threadpool_limits(4);base=Path(base);integrity=json.loads((base/'integrity.json').read_text())
    if integrity.get('status')!='PASS' or not integrity.get('every_physical_member_and_alias_verified'):
        raise ValueError('Independent complete delivery admission missing')
    state=json.loads((base/'control/provider.json').read_text());completion=json.loads((base/'downloads/completion.json').read_text())
    if state['status']!='TERMINATED' or completion['status']!='INSUFFICIENT_ASSEMBLY_LINK_SUPPORT' or completion['science_completed'] or completion['comparison_admitted'] or not completion['pilot_completed']:
        raise ValueError('Only the stopped, pilot-only E034 disposition is admitted')
    export=json.loads((base/'export-admission.json').read_text())
    if export['status']!='PASS_BEFORE_ARCHIVE_EXPORT':raise ValueError('Export/cost/retention admission missing')
    root=base/'restored/closed-delivery/work';links=base/'restored/links/work'
    source=json.loads((ROOT/'experiments/E034-genome-graph/source-lock.json').read_text())
    for name,wanted in source['files'].items():
        if binding(ROOT/name)!=wanted:raise ValueError('Frozen scientific source differs: '+name)
    release=json.loads((root/'release.json').read_text())
    if release['config']!=binding(root/'config.json') or release['plan']!=binding(root/'science-plan.json'):
        raise ValueError('Actual held release byte bindings differ')
    before=json.loads((root/'gates/inputs-before.json').read_text())
    if before!=json.loads((root/'gates/inputs-after.json').read_text()):raise ValueError('Original inputs changed')
    runtime=json.loads((root/'gates/runtime.json').read_text());candidate=json.loads((ROOT/'experiments/E034-genome-graph/candidate-lock.json').read_text())
    if runtime['status']!='PASS_COMPLETE_READONLY_BASE_AND_NEW_OWNED_PACKAGE' or runtime['package_files']!=candidate['package_files'] or runtime['distributions']['dl-binner']!='0.1.0.dev10':
        raise ValueError('Native installed source/runtime differs')
    stages=['workflow-origin','owned-package-install','complete-native-runtime','original-inputs-before','actual-native-tiny','pilot-E009','pilot-oral','original-inputs-after']
    got={r['stage']:r['resources'] for r in completion['stages']}
    if set(got)!=set(stages):raise ValueError('Actual phase stage population differs')
    for name in stages:
        receipt=json.loads((root/'logs'/(name+'.exit.json')).read_text())
        if receipt!=got[name] or receipt['exit_code']!=0 or receipt['stop_reason'] is not None:
            raise ValueError('Actual native stage exit differs: '+name)
    tiny=root/'gates/tiny';done=json.loads((tiny/'completed.json').read_text());seals=list((tiny/'work').rglob('done.json'))
    if len(seals)!=31 or done['serial_scientific_seals']!=31 or not done['verified_resume_noop'] or done['community_science']:
        raise ValueError('Native tiny workflow differs')
    for path in seals:verify_seal(path.parent)
    for name in ['first','resume']:
        if json.loads((tiny/(name+'.exit.json')).read_text())['exit_code']!=0:raise ValueError('Tiny actual exit failed')
    if 'Nothing to be done' not in (tiny/'resume.log').read_text():raise ValueError('Native no-op proof missing')
    watch=json.loads((base/'downloads/watchdog-exit.json').read_text());sup=json.loads((root/'logs/supervision.json').read_text())
    if not watch['shutdown'] or watch['decision']!='workflow exited' or watch['expected_process']!=sup['process'] or watch['boot_id']!=sup['boot_id']:
        raise ValueError('Current boot/process exit watcher differs')
    axes=json.loads((ROOT/'experiments/E033-multiscale-bam/reuse-lock.json').read_text())['axes']
    records=json.loads((ROOT/'experiments/E033-multiscale-bam/BAM-manifest.json').read_text())['records']
    result=dict(status='PASS_CLOSED_PILOT_ONLY',phase='graph-20261105T231027Z-b0d741c',disposition='NOT_ASSESSED',
        comparison_admitted=False,new_community_fits=0,new_partitions=0,new_MAG_scores=0,actual_stage_exits={n:got[n]['exit_code'] for n in stages},
        native_package_files=len(runtime['package_files']),native_distributions=len(runtime['distributions']),native_tiny_seals=31,
        native_tiny_noop=True,source_files=len(source['files']),original_inputs_before_after_equal=True,watchdog_exit_verified=True,
        parent_systemd_numeric_exit_not_returned=True,source_runtime_bound_to_original_freeze=True,pilots={})
    for community,index,unit in [('E009',0,'E009-noGLM'),('oral',8,'oral-noGLM')]:
        at=links/community/('sample-%02d'%index);a,m=read(at/'links');sample=json.loads((at/'completed.json').read_text());manifest=[r for r in records if r['community']==community][index]
        if sample['source']!=manifest or sample['graph_completed']!=binding(at/'links/completed.json') or sample['features']!=before[json.loads((root/'science-plan.json').read_text())['units'][unit]['features']]:
            raise ValueError('Pilot source/features differ')
        expected=axes[unit]
        if (len(a['ids']),int(a['lengths'].sum()),int(a['eligible'].sum()))!=(expected['rows'],expected['bp'],expected['eligible']) or m['sample']!=expected['samples'][index] or m['source']!={k:manifest[k] for k in ['bytes','sha256']}:
            raise ValueError('Full pilot axis/sample differs')
        u=utility(a['edges'],a['ids'].tolist(),a['lengths'],a['eligible'],pilot=True)
        if u!=m['utility'] or u!=completion['pilot_utilities'][community]:raise ValueError('Frozen utility recomputation differs')
        histogram=np.asarray(m['calibration']['histogram'],np.int64);total=int(histogram.sum())
        quantile=int(np.searchsorted(np.cumsum(histogram),int(np.ceil((total-1)*.995))+1))
        if quantile!=m['calibration']['insert_limit'] or total!=m['calibration']['observations'] or m['collator_exit']!=0:
            raise ValueError('Insert calibration/decoder differs')
        connected=np.zeros(len(a['ids']),bool);connected[a['edges'].ravel()]=True
        if community=='E009':
            lock=json.loads((ROOT/'experiments/E013-marker-quality/review-lock.json').read_text());truthroot=ROOT/lock['truth_root']
            if binding(truthroot/'manifest.json')!=lock['manifest']:raise ValueError('Conservative truth manifest differs')
            for n,w in lock['truth_files'].items():
                if binding(truthroot/n)!=w:raise ValueError('Conservative truth bytes differ')
            truth=json.loads((truthroot/'truth.json').read_text());targets=json.loads((truthroot/'targets.json').read_text());targetset=set(targets['targets'])
            if a['ids'].tolist()!=truth['ordered_contig_ids'] or len(targetset)!=156:raise ValueError('Conservative truth population differs')
            labels=[truth['contigs'][q]['AMBER_label'] for q in a['ids']];quarantine=np.array([truth['contigs'][q]['nn_quarantined_query_bp'] for q in a['ids']],np.int64)
            truth_binding=binding(truthroot/'manifest.json');del truth
        else:
            lab,quarantine,shared,genomes,manifest_truth=oral_labels(ROOT/'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1',a['ids'].tolist(),a['lengths'])
            labels=[genomes[x] if x>=0 else None for x in lab];targetset=set(manifest_truth['targets']);truth_binding=binding(ROOT/'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1/manifest.json')
            if len(targetset)!=799:raise ValueError('Oral provided-origin population differs')
        populations=defaultdict(Counter)
        for i,(q,length,eligible) in enumerate(zip(a['ids'],a['lengths'],a['eligible'])):
            low=max(x for x in [0,500,1000,1500,2500,10000] if length>=x)
            origin='unknown' if labels[i] is None else 'target' if labels[i] in targetset else 'non_target'
            key='|'.join([str(low),origin,'eligible' if eligible else 'excluded','linked' if connected[i] else 'unlinked'])
            populations[key]['contigs']+=1;populations[key]['bp']+=int(length);populations[key]['quarantined_bp']+=int(quarantine[i])
        relation=Counter();support=Counter();eligible_relation=Counter();edges=[]
        for edge,weight,templates in zip(a['edges'],a['weights'],a['support']):
            i,j=map(int,edge);g,h=labels[i],labels[j];relation_name='unresolved' if g is None or h is None else 'same_conservative_genome' if g==h else 'different_conservative_genomes'
            relation[relation_name]+=1;support[relation_name]+=int(templates)
            if a['eligible'][edge].all():eligible_relation[relation_name]+=1
            edges.append(dict(left=str(a['ids'][i]),right=str(a['ids'][j]),left_length=int(a['lengths'][i]),right_length=int(a['lengths'][j]),both_eligible=bool(a['eligible'][edge].all()),relation=relation_name,support=int(templates),weight=float(weight)))
        parent={i:i for i in np.flatnonzero(connected)}
        def find(i):
            while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
            return i
        for i,j in a['edges']:
            x,y=find(int(i)),find(int(j));parent[x]=y
        components=Counter(find(i) for i in parent)
        strata={str(low):dict(contigs=int(((a['lengths']>=low)&a['eligible']).sum()),bp=int(a['lengths'][(a['lengths']>=low)&a['eligible']].sum())) for low in [500,1000,1500,2500,10000]}
        if sum(v['contigs'] for v in populations.values())!=expected['rows'] or sum(v['bp'] for v in populations.values())!=expected['bp']:raise ValueError('Full DNA accounting differs')
        result['pilots'][community]=dict(source=manifest,features=sample['features'],graph=binding(at/'links/graph.npz'),full_axes=expected,
            utility=u,template_accounting=counter_contract(m['counters']),counters=m['counters'],calibration={k:v for k,v in m['calibration'].items() if k!='histogram'},aggregation=m['aggregation'],
            edges=len(a['edges']),components=len(components),largest_component_contigs=max(components.values(),default=0),
            degree_maximum=int(np.bincount(a['edges'].ravel(),minlength=len(a['ids'])).max()),all_population_cells=dict(populations),eligible_cumulative_lengths=strata,
            edge_truth=dict(semantics='Conservative E009 v2 dominant-genome labels; unresolved not counted as disagreement' if community=='E009' else 'Provided-origin oracle, not unique-sequence truth',counts=dict(relation),support_counts=dict(support),both_eligible_counts=dict(eligible_relation),no_edges_fraction_is_undefined=not len(a['edges']),truth_manifest=truth_binding),edges_diagnostic_only=edges,
            temporary_BAM_removed=sample['temporary_BAM_removed'],same_reader_and_policy=True)
    result.update(finished_epoch=time.time(),truth_used_only_after_frozen_links=True,thresholds_or_edges_changed=False,old_scores_replayed=False,
        frozen_full_denominators=dict(E009=dict(targets=156,provided_bp=554661890),oral=dict(targets=799,provided_bp=2083072211)),E009_N_quarantine_percent=3.3034,oral_known_shared_sensitivity_not_newly_scored=True,
        original_Mac_allclose_failure_and_tolerance_preserved=True,scientific_quality_keep_modify_abandon='NOT_ASSESSED; no community model/partition to evaluate')
    write(output,result);return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();r=inspect(args.base,args.output);print('E034_PILOT_REVIEW',r['status'])
