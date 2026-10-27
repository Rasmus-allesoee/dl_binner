"""Summarize only admitted E023 diagnostics and immutable baseline summaries.

Keeps full reference axes, fixed primary criteria, both new partitions and all
population tables. No optimizer, truth-selected partition or baseline rescore.
"""
from pathlib import Path
from collections import Counter
import json,csv,sys,shutil,datetime
repo=Path.cwd();sys.path.insert(0,str(repo/'scripts'))
from e014_collect import binding
r=Path(Path('artifacts/e023-inspection/current-root.txt').read_text().strip());out=repo/'experiments/E023-adaptive-density-bins'
def read(p):return json.loads(Path(p).read_text())
protocol=read(out/'protocol.json');b9=repo/'experiments/E022-marker-informed-learning/comparison-review.json';bo=repo/'experiments/E019-window-context/comparison-review.json'
assert binding(b9)==protocol['baseline_summaries']['E022_E009']and binding(bo)==protocol['baseline_summaries']['E019_oral']
bases={'E009':read(b9)['arms']['post']['diagnostics']['recovery_summary'],'oral':read(bo)['units']['oral-context']['arms']['post']['recovery']}
bt9={z['genome']:z for z in csv.DictReader((repo/'experiments/E022-marker-informed-learning/comparison-targets.tsv').open(),delimiter='\t')};bto={z['genome']:z for z in csv.DictReader((repo/'experiments/E019-window-context/comparison-targets.tsv').open(),delimiter='\t')if z['dataset'].startswith('oral')};meta={z['genome']:z for z in csv.DictReader((out/'metabat-target-context.tsv').open(),delimiter='\t')}
result=dict(record='E023',status='COMPLETED_VERIFIED_AND_FROZEN_DIAGNOSTICS_REVIEWED',reviewed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase='density-20261026T213652Z-f13e5a1-r2',scientific_source='546763dc27ad3e038f4054c8a183a8ceaf11b03d',execution_source='f13e5a1ea1933fa78c56773d739daa7faef24181',protocol=binding(out/'protocol.json'),source_lock=binding(out/'source-lock.json'),baselines_reused_without_rescore={'E022':binding(b9),'E019':binding(bo),'MetaBAT_secondary':binding(out/'metabat-secondary-review.json')},datasets={},evidence=dict(native_contract=binding(r/'native-contract-review.json'),archive_verification=binding(r/'archive-verification.json'),diagnostics_resources=binding(r/'frozen-diagnostics.resources.json'),residual_gaps=binding(r/'residual-gap-audit.json'),cached_neighbors=binding(r/'cached-neighbor-diagnostic.json')),limits=['Two development communities; different E022 E009 / E019 oral learning anchors','Native vectors/seed fixed; no causal isolation of encoder, individual context channels, markers or depth','Full 156/799 provided-reference denominators; conservative E009 v2 / 3.3034% N quarantine unchanged','Oral provided-origin oracle, not unique support; known-shared sensitivity unchanged','MetaBAT2 native eligibility differs; no matched-cutoff or general SOTA claim','Threshold-based HQ/MQ/LQ only, no RNA/tRNA screening or formal MIMAG HQ','Original failed Mac allclose tolerance preserved; no local neural inference','Omitted emitted FASTA remains native; collector hashes/manifest are not a bulk backup'])
rows=[]
for dataset,unit in [('E009','E009-E022'),('oral','oral-E019')]:
 raw=read(r/('diagnostics-'+unit)/'review.json');dest=out/('bin-quality-'+dataset);dest.mkdir(exist_ok=True)
 for p in (r/('diagnostics-'+unit)).glob('*.tsv'):shutil.copyfile(p,dest/p.name)
 arms={};maps={}
 for arm,a in raw['arms'].items():
  if dataset=='E009':rec=a['diagnostics']['recovery'];summary=a['diagnostics']['recovery_summary'];quality={'conservative_sequence':a['secondary']};pop=a['populations'];B3=a['grouping']['restricted_B3'];geometry=a['diagnostics']['geometry']
  else:rec=a['evaluation']['origin']['recovery'];summary=a['evaluation']['origin']['recovery_summary'];quality=a['secondary'];pop=a['grouping']['population_cells'];B3=a['grouping']['origin_B3'];geometry=a['grouping']['geometry']
  sq={}
  for mode,z in quality.items():
   sq[mode]={k:v for k,v in z.items()if k!='bins'};sq[mode]['target_at_least_200kb_counts']=dict(Counter(b['tier']for b in z['bins']if b['target']and b['bp']>=200000));sq[mode]['non_target_dominant_counts']=dict(Counter(b['tier']for b in z['bins']if not b['target']));sq[mode]['bin_count']=len(z['bins'])
  arms[arm]=dict(recovery=summary,grouping=B3,preserved_native_5NN=geometry,secondary=sq,complete_export=a['export_contract'],populations=pop)
  if dataset=='oral':arms[arm]['known_shared_sensitivity']=a['evaluation']['known_shared_mask']['recovery_summary']
  maps[arm]={z['genome']:z for z in rec}
 base=bases[dataset];s=arms['selected']['recovery'];d=arms['density']['recovery'];paired=[]
 for g,z in sorted(maps['selected'].items()):
  bt=bt9[g]if dataset=='E009'else bto[g];prior=int(bt['E022_post_bp'if dataset=='E009'else'E019_post_bp']);assert int(bt['reference_bp'])==z['reference_bp'];density=maps['density'][g]['recovered_bp']
  row=dict(dataset=dataset,genome=g,reference_bp=z['reference_bp'],assembly_confirmed_bp=z['assembly_confirmed_bp'],baseline_bp=prior,density_bp=density,selected_bp=z['recovered_bp'],delta_vs_baseline_bp=z['recovered_bp']-prior,marker_weight_effect_bp=z['recovered_bp']-density,retained_MetaBAT_bp=int(meta[g]['retained_MetaBAT_bp'])if dataset=='E009'else'');rows.append(row);paired.append(row)
  if dataset=='E009':assert prior==int(meta[g]['retained_E022_bp'])
 assert len(paired)==(156 if dataset=='E009'else 799)and sum(z['reference_bp']for z in paired)==(554661890 if dataset=='E009'else 2083072211)
 assert abs(sum(z['selected_bp']for z in paired)/sum(z['reference_bp']for z in paired)-s['bp_weighted_R95'])<1e-14
 result['datasets'][dataset]=dict(anchor='E022_E009_post'if dataset=='E009'else'E019_oral_post',baseline=base,arms=arms,paired=dict(R95_delta=s['bp_weighted_R95']-base['bp_weighted_R95'],R95_delta_percentage_points=100*(s['bp_weighted_R95']-base['bp_weighted_R95']),recovered_bp_delta=sum(z['delta_vs_baseline_bp']for z in paired),marker_weight_delta_bp=sum(z['marker_weight_effect_bp']for z in paired),target50_delta=s['at_least_50_percent']-base['at_least_50_percent'],target90_delta=s['at_least_90_percent']-base['at_least_90_percent'],gaining_targets=sum(z['delta_vs_baseline_bp']>0 for z in paired),losing_targets=sum(z['delta_vs_baseline_bp']<0 for z in paired),marker_gaining_targets=sum(z['marker_weight_effect_bp']>0 for z in paired),marker_losing_targets=sum(z['marker_weight_effect_bp']<0 for z in paired)),largest_gains=sorted(paired,key=lambda z:-z['delta_vs_baseline_bp'])[:8],largest_losses=sorted(paired,key=lambda z:z['delta_vs_baseline_bp'])[:8],raw_review=binding(r/('diagnostics-'+unit)/'review.json'))
gains=[v['paired']['R95_delta']for v in result['datasets'].values()];counts=[v['paired']['target90_delta']for v in result['datasets'].values()];keep=max(gains)>=.005 and min(gains)>=0 and min(counts)>=0;abandon=not any(x>0 for x in gains+counts)
result['disposition']=dict(value='KEEP'if keep else'ABANDON'if abandon else'MODIFY',original_rule_unchanged=True,keep_passed=keep,abandon_passed=abandon,reason='E009 materially gains, but oral R95 and target-90 regress; neither promotion nor a universal method-family rejection')
metabat=read(out/'metabat-secondary-review.json')['retained_primary_summary'];result['retained_MetaBAT_context']=dict(secondary=read(out/'metabat-secondary-review.json')['secondary'],primary=metabat,new_E009_R95_minus_MetaBAT_pp=100*(result['datasets']['E009']['arms']['selected']['recovery']['bp_weighted_R95']-metabat['bp_weighted_R95']),new_E009_recovered_bp_minus_MetaBAT=sum(z['selected_bp']-z['retained_MetaBAT_bp']for z in rows if z['dataset']=='E009'),native_input_eligibility_not_matched=True)
result['residual_gap_audit']=read(r/'residual-gap-audit.json');result['cached_neighbor_diagnostic']=read(r/'cached-neighbor-diagnostic.json')
with (out/'comparison-targets.tsv').open('x')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
(out/'comparison-review.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(dict(disposition=result['disposition'],summary={k:dict(baseline=v['baseline'],density=v['arms']['density']['recovery'],selected=v['arms']['selected']['recovery'],paired=v['paired'])for k,v in result['datasets'].items()},MetaBAT=result['retained_MetaBAT_context']),indent=2),flush=True)
