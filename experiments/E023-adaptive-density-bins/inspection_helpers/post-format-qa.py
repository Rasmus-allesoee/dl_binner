"""Validate complete E023 population/target/quality/resource accounting after review."""
from pathlib import Path
import csv,json,sys,time
repo=Path.cwd();sys.path.insert(0,str(repo/'scripts'))
from e014_collect import binding
from e023_control import verify_source
r=Path(Path('artifacts/e023-inspection/current-root.txt').read_text().strip());exp=repo/'experiments/E023-adaptive-density-bins';v=json.loads((exp/'comparison-review.json').read_text());rows=list(csv.DictReader((exp/'comparison-targets.tsv').open(),delimiter='\t'));assert len(rows)==955
checked=[]
for d,n,bp in [('E009',145702,231678157),('oral',1286547,1669981123)]:
 z=v['datasets'][d];targetrows=[a for a in rows if a['dataset']==d];assert len(targetrows)==(156 if d=='E009'else 799)
 for arm,a in z['arms'].items():
  p=a['populations'];cells=p['cells']if 'cells'in p else p;assert sum(x['contigs']for x in cells.values())==n;assert sum(x['all_bp'if d=='E009'else'bp']for x in cells.values())==bp
  if d=='E009':assert sum(x['nn_quarantined_query_bp']for x in cells.values())==7653205
  for mode,sq in a['secondary'].items():
   assert sum(sq['counts'].values())==sq['bin_count'];assert sum(sq['target_counts'].values())+sum(sq['non_target_dominant_counts'].values())==sq['bin_count'];assert sum(sq['at_least_200kb_counts'].values())<=sq['bin_count'];assert not sq['rRNA_tRNA_screened']and not sq['primary_rule_changed']
  assert a['recovery']['at_least_90_percent']<=a['recovery']['at_least_50_percent'];checked.append(d+'/'+arm)
 assert abs(sum(int(a['selected_bp'])for a in targetrows)/sum(int(a['reference_bp'])for a in targetrows)-z['arms']['selected']['recovery']['bp_weighted_R95'])<1e-14
assert v['disposition']['value']=='MODIFY'and not v['disposition']['keep_passed']and v['disposition']['original_rule_unchanged']
source=verify_source();owned=sum(p.stat().st_size for p in r.rglob('*')if p.is_file());assert owned<6*1024**3
clock=json.loads((r/'review-clock.json').read_text());assert time.time()-clock['start_epoch']<3600
for label in ['verify-extract','native-contracts','frozen-diagnostics','residual-gap-audit','cached-neighbor-audit','summarize-r2']:
 s=json.loads((r/(label+'.resources.json')).read_text());assert s['status']=='SUCCESS'and s['resources']['peak_sampled_rss_bytes']<8_000_000_000
proof=dict(status='PASS_FULL_POPULATIONS_955_TARGETS_SECONDARY_AND_FROZEN_LIMITS',arms=checked,source=source,owned_bytes=owned,elapsed_original_seconds=time.time()-clock['start_epoch'],all_population_counts_and_bp_and_N_quarantine_match=True,secondary_counts_match_every_bin=True,original_criteria_unchanged=True,primary_evaluator_not_modified=True,comparison=binding(exp/'comparison-review.json'),targets=binding(exp/'comparison-targets.tsv'))
(r/'post-format-contracts.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
