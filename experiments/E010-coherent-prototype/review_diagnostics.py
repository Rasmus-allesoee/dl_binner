"""Read-only decomposition of frozen E010 bins and paired refinement losses.

Uses all bin DNA for source purity and exact retained sequence-truth interval
unions. Best-source bins ignoring purity/size are diagnostics, never replacements
for the frozen >=200kb/95% R95 endpoint. No new partition, fitting or marker scan.
"""
from collections import Counter,defaultdict
from pathlib import Path
import csv
import json
import sys
import time
import signal
sys.path.insert(0,str(Path(__file__).absolute().parents[2]/'scripts'))
from e009_common import binding,write_json
from e009_truth import union


def bin_sources(rows,truth,population,targets):
    """Describe mixing/fragmentation with unknown/non-target DNA in each bin total."""
    bins=defaultdict(lambda:dict(bp=0,support=Counter(),loci=defaultdict(list)))
    for row in rows:
        if not row['bin_id']:continue
        item=truth['contigs'][row['contig_id']];v=bins[row['bin_id']];v['bp']+=item['length'];v['support'].update(item['confirmed_query_bp'])
        for reference,intervals in item['source_intervals'].items():v['loci'][reference].extend(intervals)
    table=[]
    for label,v in bins.items():
        genome,n=v['support'].most_common(1)[0]if v['support']else(None,0)
        table.append(dict(bin_id=label,bp=v['bp'],dominant_genome=genome,dominant_confirmed_bp=n,
            confirmed_purity=n/v['bp'],dominant_lineage=population['genomes'][genome]['lineage_class']if genome else None,
            supported_genomes=len(v['support']),unconfirmed_bp=v['bp']-sum(v['support'].values())))
    by_target=[]
    for genome in targets:
        candidates=[]
        for label,v in bins.items():
            if not v['support'].get(genome):continue
            supported=sum(sum(b-a for a,b in union(intervals))for ref,intervals in v['loci'].items()if truth['reference_axis'][ref]['genome']==genome)
            candidates.append((supported,label,v['support'][genome]/v['bp'],v['bp']))
        best=sorted(candidates,key=lambda x:(-x[0],x[1]))[0]if candidates else(0,None,None,0)
        by_target.append(dict(genome=genome,best_source_union_bp=best[0],bin_id=best[1],confirmed_purity=best[2],bin_bp=best[3]))
    return dict(bins=table,targets=by_target,large_bins_at_least_200kb=sum(x['bp']>=200000 for x in table),
        large_bins_below_95pct_purity=sum(x['bp']>=200000 and x['confirmed_purity']<.95 for x in table),
        targets_best_source_bin_below_95pct=sum(x['confirmed_purity']is not None and x['confirmed_purity']<.95 for x in by_target),
        semantics='all bin DNA denominator; best-source bin ignores size/purity for diagnosis only')


def run(folder,repo):
    """Retain target deltas and complete composition of newly unassigned DNA."""
    p=Path(folder);native=p/'candidate/candidate';truth_dir=repo/'artifacts/e009-truth-v2/20261015/attempt-local-v2/truth-v2'
    truth=json.loads((truth_dir/'truth.json').read_text());population=json.loads((repo/'experiments/E009-competitive-benchmark/truth-population-review.json').read_text())
    target=json.loads((truth_dir/'targets.json').read_text());review=json.loads((p/'local-review-v3/review.json').read_text())
    baseline=json.loads((repo/'experiments/E009-competitive-benchmark/controls-review.json').read_text())
    marker=json.loads((native/'markers/evidence.json').read_text());parts={};tables={};assignment={}
    for arm in ['pre','post']:
        rows=list(csv.DictReader((native/'export'/arm/'assignments.tsv').open(),delimiter='\t'));parts[arm]=rows
        assignment[arm]={r['contig_id']:r for r in rows};tables[arm]=bin_sources(rows,truth,population,target['targets'])
    dropped=Counter();origins=defaultdict(Counter);by_length=defaultdict(Counter)
    for row in parts['post']:
        q=row['contig_id'];before=assignment['pre'][q]
        if before['status']!='assigned'or row['status']=='assigned':continue
        item=truth['contigs'][q];bp=item['length'];clean=q in marker['clean'];label=item['AMBER_label']
        lineage=population['genomes'][label]['lineage_class']if label else'not_attributable'
        length=max(b for b in [1,500,768,1000,2500,10000]if bp>=b)
        for counter in [dropped,origins[lineage],by_length[str(length)]]:
            counter['contigs']+=1;counter['bp']+=bp;counter['clean_marker_contigs']+=clean;counter['clean_marker_bp']+=bp if clean else 0
            for key in ['ambiguous_query_bp','nn_quarantined_query_bp','unsupported_query_bp']:counter[key]+=item[key]
        for genome,bases in item['confirmed_query_bp'].items():dropped[population['genomes'][genome]['lineage_class']+'_confirmed_bp']+=bases
    r95={arm:{x['genome']:x for x in v['diagnostics']['recovery']}for arm,v in review['arms'].items()}
    dev3={x['genome']:x for x in json.loads((repo/'artifacts/e009-controls/20261016-review/local-review-v2/review.json').read_text())['arms']['ten-depth-learned']['diagnostics']['recovery']}
    deltas=[]
    for g in target['targets']:
        a,b,c=[row[g] for row in [r95['pre'],r95['post'],dev3]]
        deltas.append(dict(genome=g,reference_bp=b['reference_bp'],pre_recovered_bp=a['recovered_bp'],post_recovered_bp=b['recovered_bp'],
            dev3_learned_ten_depth_recovered_bp=c['recovered_bp'],post_minus_pre_bp=b['recovered_bp']-a['recovered_bp'],post_minus_dev3_bp=b['recovered_bp']-c['recovered_bp'],
            assembly_confirmed_bp=b['assembly_confirmed_bp']))
    value=dict(bin_diagnostics=tables,newly_unassigned=dict(total=dict(dropped),by_lineage=dict(origins),by_length=dict(by_length)),
        target_deltas=deltas,source=binding(__file__),truth=binding(truth_dir/'manifest.json'),baseline=binding(repo/'experiments/E009-competitive-benchmark/controls-review.json'))
    write_json(p/'grouping-diagnostics.json',value)
    return value


if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in()).throw(TimeoutError('10 minute diagnostic bound')));signal.alarm(600)
    run(Path(sys.argv[1]),Path(__file__).absolute().parents[2])
