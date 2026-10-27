"""Describe residual E023 E009 error mechanisms; never select or change bins.

Uses frozen per-bin purity/size gates only to categorize confirmed query support.
Counts are query bp, not deduplicated reference recovery or counterfactual scores.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,sys
repo=Path.cwd();sys.path[:0]=[str(repo/'scripts'),str(repo/'src')]
from e014_collect import binding
from e009_evaluate import read_partition
r=Path(Path('artifacts/e023-inspection/current-root.txt').read_text().strip());review=json.loads((r/'diagnostics-E009-E022/review.json').read_text())['arms']['selected'];truthroot=repo/'artifacts/e009-truth-v2/20261015/attempt-local-v2/truth-v2';truth=json.loads((truthroot/'truth.json').read_text());targets=json.loads((truthroot/'targets.json').read_text());pop=json.loads((repo/'experiments/E009-competitive-benchmark/truth-population-review.json').read_text());part=json.loads((r/'verified/work/units/E009-E022/group/selected-partition.json').read_text());rows,assign=read_partition(r/'verified/work/units/E009-E022/export/selected/assignments.tsv',truth)
secondary={int(b['bin_id']):b for b in review['secondary']['bins']};by_target=defaultdict(Counter);total=Counter();by_length=defaultdict(Counter);by_lineage=defaultdict(Counter);by_marker=defaultdict(Counter)
clean=set(json.loads((repo/'artifacts/e011-cached-grouping-reference/restore-local/candidate/markers/evidence.json').read_text())['clean']);unknown=Counter()
for i,q in enumerate(truth['ordered_contig_ids']):
 item=truth['contigs'][q];status=rows[i]['status'];b=int(part['assignment'][i]);length=item['length'];band=str(max(v for v in [1,500,768,1000,2500,10000]if v<=length));marker='clean_marker'if q in clean else'no_clean_marker'
 if status=='assigned'and b<0:raise ValueError('Assignment/status differs')
 for g,bp in item['confirmed_query_bp'].items():
  if g not in targets['targets']:continue
  if status!='assigned':category=status
  else:
   bin_=secondary[b]
   if bin_['dominant_origin']!=g:category='minor_origin_in_mixed_bin'
   elif bin_['confirmed_purity']<.95:category='dominant_but_below_95_purity'
   elif bin_['bp']<200000:category='pure_dominant_but_below_200kb'
   else:category='passing_bin_confirmed_query_support'
  by_target[g][category]+=bp;total[category]+=bp;by_length[band][category]+=bp;by_marker[marker][category]+=bp
  by_lineage[pop['genomes'][g]['lineage_class']][category]+=bp
 for k in ['nn_quarantined_query_bp','ambiguous_query_bp','unsupported_query_bp']:unknown[status+'|'+k]+=item[k]
counts=defaultdict(Counter)
for b in review['secondary']['bins']:
 g=b['dominant_origin'];lineage=pop['genomes'][g]['lineage_class']if g else'unknown';counts[lineage]['bins']+=1;counts[lineage]['all_bin_bp']+=b['bp'];counts[lineage]['unresolved_bp']+=b['unconfirmed_bp'];counts[lineage]['confirmed_foreign_bp']+=b['confirmed_other_origin_bp'];counts[lineage]['under200kb']+=b['bp']<200000
require_total=sum(sum(x.values())for x in by_target.values());assert require_total==sum(total.values())==sum(sum(x.values())for x in by_length.values())==sum(sum(x.values())for x in by_lineage.values())==sum(sum(x.values())for x in by_marker.values())
value=dict(status='PASS_DIAGNOSTIC_ONLY_NO_BIN_CHANGES',source=binding(__file__),review=binding(r/'diagnostics-E009-E022/review.json'),primary_confirmed_query_bp_by_outcome=dict(total),by_target={g:dict(by_target[g])for g in targets['targets']},by_length=dict(by_length),by_lineage=dict(by_lineage),by_marker=dict(by_marker),unresolved_all_DNA_by_status=dict(unknown),dominant_lineage_bin_accounting=dict(counts),scope='Full population; confirmed query bp can duplicate provided loci. Not a new recovery score, oracle selector or permission to tune. Passing means existing frozen >=200 kb and >=95% all-DNA support only.')
(r/'residual-gap-audit.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({k:value[k]for k in ['primary_confirmed_query_bp_by_outcome','by_length','dominant_lineage_bin_accounting']},indent=2),flush=True)
