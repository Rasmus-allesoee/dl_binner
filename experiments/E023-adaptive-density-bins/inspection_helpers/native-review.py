"""Independently admit stopped E023 exits, source, full axes and returned contracts.

No optimizer, index/MST reconstruction, feature extraction, training or scorer.
All retained files have already passed archive/member verification.
"""
from pathlib import Path
import json,sys,re,csv
repo=Path.cwd();sys.path[:0]=[str(repo/'scripts'),str(repo/'src')]
from e014_collect import binding
from e023_control import verify_source
r=Path(Path('artifacts/e023-inspection/current-root.txt').read_text().strip());v=r/'verified';e=v/'evidence'
def read(p):return json.loads(Path(p).read_text())
def require(c,m):
 if not c:raise ValueError(m)
c=read(r/'completion.json');cfg=read(e/'config.json');rel=read(e/'release.json');plan=read(e/'science-plan.json');lock=read(repo/'experiments/E023-adaptive-density-bins/reuse-lock.json');policy=read(repo/'experiments/E023-adaptive-density-bins/config.json');inv=read(v/'inventory.json');watch=read(r/'watchdog-exit.json');sup=read(e/'logs/supervision.json')
require(read(r/'provider-current.json')['status']=='TERMINATED'and read(r/'archive-verification.json')['every_member_verified'],'Stopped/all-member verification required')
require(c['status']=='SUCCESS'and c['science_completed']and c['scientific_fits_completed']==0 and c['grouping_communities_completed']==2 and c['private_readback_verified'],'Incomplete native phase')
require(c['source']==cfg['source_commit']=='f13e5a1ea1933fa78c56773d739daa7faef24181'and rel['config']==binding(e/'config.json'),'Changed source/release')
require(watch['shutdown']and watch['decision']=='workflow exited'and watch['expected_process']==sup['process']and watch['boot_id']==sup['boot_id']==read(e/'host.json')['boot_id'],'Watchdog identity differs')
require(rel['provider_actual_STOP_epoch']<=cfg['vm_start_epoch']+8100 and c['elapsed_since_VM_start_seconds']<7200,'Original clock/STOP exceeded')
verify_source();source=read(e/'source/source-lock.json')
require(binding(e/'source/source-lock.json')==binding(repo/'experiments/E023-adaptive-density-bins/source-lock.json'),'Freeze differs')
for p in sorted((e/'source').glob('e023_*.py')):
 require(binding(p)==source['files']['scripts/'+p.name],'Native script differs: '+p.name)
for p in (e/'source/density').glob('*.py'):require(binding(p)==source['files']['src/dl_binner/density/'+p.name],'Native scientific module differs')
for name in ['config.json','reuse-lock.json','protocol.json','Snakefile']:
 require(binding(e/'source'/name)==binding(repo/'experiments/E023-adaptive-density-bins'/name),'Native frozen file differs: '+name)
require(plan['units']==lock['units']and plan['python']==lock['numerical_python']and plan['threads']==4,'Science units/runtime differ')
g=read(e/'gates/completion.json');require(g['status']=='SUCCESS'and g['config']==binding(e/'config.json'),'Native gate completion differs')
expected=['workflow-version','accepted-runtime','full-readers','tiny-readers-selection-export','tiny-DAG-collection'];require([s['name']for s in g['stages']]==expected,'Native gate sequence differs')
for s in g['stages']:
 require(s['resources']['exit_code']==0 and s['resources']['stop_reason']is None,'Failed native gate')
 exit_=read(e/'gates'/(s['name']+'.exit.json'));require(exit_['exit_code']==0 and exit_['command']==s['resources']['command'],'Native gate command/exit differs')
names=['science','used-inputs-after','collection','upload-e023-evidence.tar.gz','readback-e023-evidence.tar.gz','upload-e023-evidence.tar.gz.sha256','readback-e023-evidence.tar.gz.sha256','upload-collection.json','readback-collection.json'];require([x['name']for x in c['stages']]==names,'Incomplete native stage sequence')
for s in c['stages']:
 require(s['resources']['exit_code']==0 and s['resources']['stop_reason']is None,'Failed phase command')
 p=e/'logs'/(s['name']+'.exit.json')
 if p.exists():require(read(p)['exit_code']==0 and read(p)['command']==s['resources']['command'],'Native retained terminal exit differs')
# Collector seals its own input snapshot before later uploads: their delivered
# completion stage receipts plus exact readback binding supply that later proof.
log=(e/'logs/science.log').read_text();rules=re.findall(r'^localrule (verify|group|export|audit|all):',log,re.M);require(rules==['verify','group','export','audit','verify','group','export','audit','all'],'Actual scientific scheduling/serial barriers differ');require(len(re.findall(r'Finished jobid:',log))==9 and '9 of 9 steps (100%) done'in log,'Incomplete scientific DAG exits')
readers=read(e/'gates/readers.json');report={}
for u,nn,bp in [('E009-E022',145702,231678157),('oral-E019',1286547,1669981123)]:
 p=v/'work/units'/u;done=read(p/'group/completed.json');audit=read(p/'audited.json');before=read(p/'verified.json');account=read(p/'export/accounting.json')
 require(done['status']=='SUCCESS'and done['config']==policy and done['truth_accessed']is False and audit['status']=='PASS'and audit['inputs_unchanged']and audit['original_vectors_unchanged'],'Changed or incomplete new-output contract')
 require(audit['contigs']==nn==readers['units'][u]['contigs']and readers['units'][u]['bp']==bp,'Full contig/bp axes differ')
 require(before['inputs']=={k:lock['files'][z]for k,z in plan['units'][u].items()},'Retained input binding differs')
 recall=done['audit']['audit'];require(len(recall['queries'])==policy['audit_queries']and recall['mean_tie_aware_recall']>=policy['min_neighbor_recall'],'Frozen sampled retrieval gate failed')
 require(set(account)=={'density','selected'},'Missing arm/DNA accounting')
 for arm in ['density','selected']:
  require(binding(p/'group'/(arm+'-partition.json'))['sha256']==done['arms'][arm]['partition_sha256']==audit['arms'][arm]['partition_sha256'],'Partition binding differs')
  require(binding(p/'group'/(arm+'-choices.json'))['sha256']==audit['arms'][arm]['choices_sha256'],'Choices binding differs')
  require(binding(p/'group/hierarchy.npz')['sha256']==audit['hierarchy_sha256'],'Hierarchy binding differs')
  require(account[arm]['contigs']==nn and account[arm]['bp']==bp,'Full export DNA lost')
 for name in ['verify','group','export','audit']:
  with (v/'work/benchmarks'/u/(name+'.tsv')).open()as f:rows=list(csv.DictReader(f,delimiter='\t'))
  require(len(rows)==1 and int(rows[0]['threads'])==4,'Native rule benchmark/thread accounting differs')
 report[u]=dict(contigs=nn,bp=bp,eligible=audit['eligible'],tree_nodes=audit['tree_nodes'],recall=recall['mean_tie_aware_recall'],bins={a:done['arms'][a]['bins']for a in ['density','selected']},audit=binding(p/'audited.json'),core_and_selection_proof='Native actual persisted sparse/tree/condensation/choice reader PASS, exact returned bytes; no local optimizer rerun',all_DNA_exports=account)
require('19' in (e/'logs/used-inputs-after.log').read_text()and "'status': 'PASS'" in (e/'logs/used-inputs-after.log').read_text(),'Input reuse-after proof missing')
runtime=read(e/'gates/runtime.json');require(runtime['prefix']==str(Path(plan['python']).parent.parent)and runtime['python'].startswith('3.10.15')and len(runtime['package_files'])==49 and len(runtime['distributions'])==41,'Runtime inventory differs')
result=dict(status='PASS_STOPPED_NATIVE_EXIT_SOURCE_REUSE_SUPERVISION_CONTRACTS',source=c['source'],prepared_science='546763dc27ad3e038f4054c8a183a8ceaf11b03d',gates=expected,serial_science_rules=rules,phase_exits=names,units=report,original_source_members=287,completion=binding(r/'completion.json'),archive=binding(r/'e023-evidence.tar.gz'),member_verification=binding(r/'archive-verification.json'),watchdog=binding(r/'watchdog-exit.json'),scope='Independent retained byte/source/receipt/scheduling/axis checks; native full reload/selection proofs accepted without repeating optimizer; frozen local scoring follows separately',final_completion_upload='Exact guest-bound GCS bytes prove delivery; its own terminal exit cannot appear in its pre-upload completion snapshot')
(r/'native-contract-review.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS_NATIVE_CONTRACTS',json.dumps({u:{k:z for k,z in x.items()if k in ['contigs','bp','eligible','bins','recall']}for u,x in report.items()}),flush=True)
