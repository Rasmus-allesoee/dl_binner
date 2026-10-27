"""Evaluate only admitted new E023 partitions with the frozen sequence readers."""
from pathlib import Path
import json,sys
repo=Path.cwd();sys.path[:0]=[str(repo/'scripts'),str(repo/'src')]
from e014_collect import binding
from e023_review import review
r=Path(Path('artifacts/e023-inspection/current-root.txt').read_text().strip());v=r/'verified'
if json.loads((r/'native-contract-review.json').read_text())['status']!='PASS_STOPPED_NATIVE_EXIT_SOURCE_REUSE_SUPERVISION_CONTRACTS':raise ValueError('Native inspection required')
ad=dict(provider_status='TERMINATED',archive_and_every_member_verified=True,cost_and_retention_admitted=True,workflow_completed=True,native=binding(r/'native-contract-review.json'),archive=binding(r/'e023-evidence.tar.gz'),finance=binding(r/'export-cost-admission.json'));(r/'review-admission.json').write_text(json.dumps(ad,indent=2)+'\n')
lock=json.loads((repo/'experiments/E023-adaptive-density-bins/reuse-lock.json').read_text())
def read(p):return json.loads(Path(p).read_text())
for unit,dataset,features,clean,truth in [
 ('E009-E022','E009',repo/'artifacts/e011-cached-grouping-reference/restore-local/candidate/features/features.npz',repo/'artifacts/e011-cached-grouping-reference/restore-local/candidate/markers/evidence.json',repo/'artifacts/e009-truth-v2/20261015/attempt-local-v2/truth-v2'),
 ('oral-E019','oral',repo/'artifacts/e014-multiview-reconstruction/inspection-20261019/verified/work/units/oral-dev5/features/features.npz',repo/'artifacts/e014-multiview-reconstruction/inspection-20261019/oral-marker-review.json',repo/'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1')]:
 native=lock['units'][unit]
 for p,n in [(features,native['features']),(features.with_suffix('.json'),str(Path(native['features']).with_suffix('.json')))]:
  if binding(p)!=lock['files'][n]:raise ValueError('Accepted full feature bytes differ')
 if dataset=='E009':
  accepted=read(repo/'experiments/E022-marker-informed-learning/reuse-lock.json');old=accepted['units']['E009-relational'];expected=accepted['files'][old['marker_cache']+'/evidence.json']
 else:expected=read(repo/'experiments/E014-multiview-reconstruction/comparison-review.json')['evidence'][str(clean.relative_to(repo))]
 if binding(clean)!=expected:raise ValueError('Marker-clean diagnostic axis differs')
 print('E023_FROZEN_DIAGNOSTICS_START',unit,flush=True)
 result=review(v/'work/units'/unit,features,v/'inventory.json',r/'review-admission.json',r/('diagnostics-'+unit),dataset,clean,truth)
 print('E023_FROZEN_DIAGNOSTICS_PASS',unit,flush=True)
 del result
