"""Supplement E011's admitted local review with paired losses and full population axes.

Consumes only verified existing partitions, marker cache and conservative truth.
No optimization, training, marker detection, acquisition, cloud API or source-truth
construction. Native eligibility is descriptive, never a reduced R95 denominator.
"""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import signal
import sys
import time
sys.path.insert(0,str(Path(__file__).absolute().parents[2]/'scripts'))
from e009_common import binding,write_json
from e009_evaluate import read_partition
from e010_review import require


def seed_audit(changed,truth,marker,cache):
    """Describe retained marker seeds for lost passing bins, without new alignment.

    Reference overlap is between whole-contig confirmed source intervals, not
    localized marker intervals; zero overlap supports distinct provided loci but
    does not validate SCG universality or an individual HMM call biologically.
    """
    from e009_truth import union
    selected=[];wanted=set()
    for row in changed:
        if row['post']['recovered_bp']>=row['pre']['recovered_bp']:continue
        for attempt in row['pre_bin_refinement_proposal']:
            ids=attempt['seed_ids'];family=attempt['seed_family']
            calls=[c for c in marker['calls']if c['contig']in ids and c['family']==family]
            wanted.update(c['gene']for c in calls)
            overlap=0
            for i,left in enumerate(ids):
                for right in ids[i+1:]:
                    l=truth['contigs'][left]['source_intervals'];r=truth['contigs'][right]['source_intervals']
                    for ref in set(l)&set(r):
                        overlap+=sum(max(0,min(b,d)-max(a,c))for a,b in union(l[ref])for c,d in union(r[ref]))
            selected.append(dict(genome=row['genome'],pre_bin=attempt['pre_bin'],seed_family=family,
                pre_bin_confirmed_purity=row['pre']['confirmed_purity'],whole_contig_reference_overlap_bp=overlap,
                seeds=[dict(contig=q,truth_label=truth['contigs'][q]['AMBER_label'],
                            confirmed_query_bp=truth['contigs'][q]['confirmed_query_bp'])for q in ids],calls=calls))
    genes={}
    with (cache/'genes.jsonl').open()as stream:
        for line in stream:
            g=json.loads(line)
            if g['gene']in wanted:genes[g['gene']]=g
    proteins={};key=None;parts=[]
    def finish():
        if key in wanted:proteins[key]=hashlib.sha256(''.join(parts).encode()).hexdigest()
    with (cache/'proteins.faa').open()as stream:
        for line in stream:
            if line.startswith('>'):
                finish();key=line[1:].strip();parts=[]
            elif key in wanted:parts.append(line.strip())
        finish()
    for record in selected:
        record['genes']={c['gene']:dict(metadata=genes[c['gene']],protein_sha256=proteins[c['gene']])for c in record['calls']}
        record['same_marker_protein_bytes']=len({proteins[c['gene']]for c in record['calls']})==1
    require(set(genes)==set(proteins)==wanted,'Retained seed gene/protein inventory differs')
    return dict(lost_passing_bins=selected,scope='Retained evidence/source unions only; no marker detection, aligner or truth change. Whole-contig interval overlaps do not localize marker loci.')


def run(folder,repo):
    """Keep target deltas, all length/origin/eligibility cells and refinement losses."""
    p=Path(folder);start=time.perf_counter()
    reviewed=json.loads((p/'local-review-v3/review.json').read_text())
    truthroot=repo/'artifacts/e009-truth-v2/20261015/attempt-local-v2/truth-v2'
    truth=json.loads((truthroot/'truth.json').read_text());targets=json.loads((truthroot/'targets.json').read_text())
    population=json.loads((repo/'experiments/E009-competitive-benchmark/truth-population-review.json').read_text())
    marker=json.loads((repo/'artifacts/e011-cached-grouping-reference/restore-local/candidate/markers/evidence.json').read_text());clean=set(marker['clean'])
    old9=json.loads((repo/'experiments/E009-competitive-benchmark/controls-review.json').read_text())
    old10=json.loads((repo/'experiments/E010-coherent-prototype/review.json').read_text())
    previous={}
    for label,record,rawroot,name in [('dev3',old9,repo/'artifacts/e009-controls/20261016-review','local-review-v2/review.json'),
                                    ('dev4',old10,repo/'artifacts/e010-coherent-prototype/review-20261017','local-review-v3/review.json')]:
        require(binding(rawroot/name)==record['analysis_bindings'][name],'Accepted baseline review differs: '+label)
        previous[label]=json.loads((rawroot/name).read_text())
    recovery={k:v['diagnostics']['recovery']for k,v in reviewed['arms'].items()}
    recovery.update({'dev3-learned-ten':previous['dev3']['arms']['ten-depth-learned']['diagnostics']['recovery'],
                     'RB-pre':previous['dev4']['arms']['pre']['diagnostics']['recovery'],
                     'RB-post':previous['dev4']['arms']['post']['diagnostics']['recovery']})
    maps={k:{row['genome']:row for row in rows}for k,rows in recovery.items()}
    require(all(set(m)==set(targets['targets'])for m in maps.values()),'Paired target axes differ')
    deltas=[]
    for genome in sorted(targets['targets']):
        row=dict(genome=genome,reference_bp=targets['genome_lengths'][genome])
        row['recovered_bp']={k:m[genome]['recovered_bp']for k,m in maps.items()}
        row['CPM_post_minus_pre_bp']=row['recovered_bp']['cpm-post']-row['recovered_bp']['cpm-pre']
        row['CPM_post_minus_RB_post_bp']=row['recovered_bp']['cpm-post']-row['recovered_bp']['RB-post']
        row['MetaBAT_minus_dev3_bp']=row['recovered_bp']['metabat']-row['recovered_bp']['dev3-learned-ten']
        deltas.append(row)
    summary={}
    for name,rows in recovery.items():
        summary[name]=dict(bp_weighted_R95=sum(r['recovered_bp']for r in rows)/sum(r['reference_bp']for r in rows),
                           at_least_50_percent=sum(r['whole_reference_R95']>=.5 for r in rows),
                           at_least_90_percent=sum(r['whole_reference_R95']>=.9 for r in rows))
    parts={};axes={};rows_by={};lost=Counter();lost_length=defaultdict(Counter);lost_lineage=defaultdict(Counter)
    for arm,directory in [('cpm-pre',p/'members/cpm/pre'),('cpm-post',p/'members/cpm/post'),('metabat',p/'members/metabat-export')]:
        rows,_=read_partition(directory/'assignments.tsv',truth);rows_by[arm]={r['contig_id']:r for r in rows};table=defaultdict(Counter)
        for row in rows:
            q=row['contig_id'];item=truth['contigs'][q];bp=item['length'];g=item['AMBER_label']
            lineage=population['genomes'][g]['lineage_class']if g else'not_attributable'
            low=max(b for b in [1,500,768,1000,2500,10000]if bp>=b)
            eligibility=('native_seed'if bp>=2500 else'native_recruitment_only'if bp>=1000 else'native_excluded')if arm=='metabat'else('candidate_eligible'if bp>=500 else'candidate_excluded')
            key='|'.join([str(low),lineage,eligibility,row['status'],'clean_marker'if q in clean else'no_clean_marker'])
            cell=table[key];cell['contigs']+=1;cell['all_bp']+=bp
            cell['primary_confirmed_bp']+=sum(n for genome,n in item['confirmed_query_bp'].items()if genome in targets['targets'])
            for field in ['ambiguous_query_bp','nn_quarantined_query_bp','unsupported_query_bp']:cell[field]+=item[field]
        require(sum(v['contigs']for v in table.values())==reviewed['full_contigs']and sum(v['all_bp']for v in table.values())==reviewed['full_bp'],'Population cross-tab lost DNA')
        axes[arm]=dict(cells=dict(table),keys=['lower_length_bp','attributable_lineage_or_unknown','native_length_eligibility','status','clean_marker_support'])
    for q,before in rows_by['cpm-pre'].items():
        after=rows_by['cpm-post'][q]
        if before['status']!='assigned'or after['status']=='assigned':continue
        item=truth['contigs'][q];bp=item['length'];g=item['AMBER_label'];lineage=population['genomes'][g]['lineage_class']if g else'not_attributable'
        low=str(max(b for b in [1,500,768,1000,2500,10000]if bp>=b))
        for counter in [lost,lost_length[low],lost_lineage[lineage]]:
            counter['contigs']+=1;counter['bp']+=bp;counter['clean_marker_contigs']+=q in clean
            counter['primary_confirmed_bp']+=sum(n for genome,n in item['confirmed_query_bp'].items()if genome in targets['targets'])
    post=json.loads((p/'members/cpm/post.json').read_text());attempts=post['attempts']
    paired=[]
    for row in deltas:
        if row['CPM_post_minus_pre_bp']==0:continue
        g=row['genome'];pre=maps['cpm-pre'][g];after=maps['cpm-post'][g]
        old_bin=int(pre['best_bin'].split('_')[1])-1 if pre['best_bin']else None
        proposals=[a for a in attempts if a['pre_bin']==old_bin]if old_bin is not None else[]
        paired.append(dict(genome=g,pre=pre,post=after,pre_bin_refinement_proposal=proposals))
    assigned_old=previous['dev4']['arms']['post']['diagnostics']['origin_by_status']['assigned']['bacterial_confirmed_bp']
    assigned_new=reviewed['arms']['cpm-post']['diagnostics']['origin_by_status']['assigned']['bacterial_confirmed_bp']
    gain=100*(summary['cpm-post']['bp_weighted_R95']-summary['RB-post']['bp_weighted_R95'])
    criteria=dict(R95_gain_percentage_points=gain,required_gain=.5,target50_count=summary['cpm-post']['at_least_50_percent'],required_target50=6,
        assigned_bacterial_bp_ratio=assigned_new/assigned_old,required_assignment_ratio=.9,
        keep_passed=gain>=.5 and summary['cpm-post']['at_least_50_percent']>=6 and assigned_new/assigned_old>=.9,
        disposition='modify refinement hypothesis; frozen CPM setting fails keep threshold; no resolution search',
        external_gap_percentage_points=100*(summary['metabat']['bp_weighted_R95']-max(v['bp_weighted_R95']for k,v in summary.items()if k!='metabat')),
        external_material_gap_threshold=1)
    value=dict(summary=summary,predeclared_criteria=criteria,target_deltas=deltas,changed_CPM_targets=paired,
        populations=axes,newly_unassigned=dict(total=dict(lost),by_length=dict(lost_length),by_lineage=dict(lost_lineage)),
        refinement=dict(proposals=len(attempts),adopted=sum(a['adopted']for a in attempts),unresolved=len(post['unresolved_conflicts'])),
        marker_seed_audit=seed_audit(paired,truth,marker,repo/'artifacts/e011-cached-grouping-reference/restore-local/candidate/markers'),
        baseline_bindings=dict(E009=binding(repo/'experiments/E009-competitive-benchmark/controls-review.json'),E010=binding(repo/'experiments/E010-coherent-prototype/review.json')),
        source=binding(__file__),wall_seconds=time.perf_counter()-start,
        limits='Length eligibility is descriptive, not a recovery-denominator filter. Markers/source truth are evaluation-only here; no new scientific policy or score selection.')
    write_json(p/'grouping-diagnostics-v2.json',value);print(json.dumps(dict(summary=summary,criteria=criteria,newly_unassigned=value['newly_unassigned']['total']),indent=2),flush=True)
    return value


if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in()).throw(TimeoutError('10-minute local diagnostics bound')));signal.alarm(600)
    run(Path(sys.argv[1]),Path(__file__).absolute().parents[2])
