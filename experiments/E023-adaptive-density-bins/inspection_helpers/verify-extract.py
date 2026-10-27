"""Verify E023 archive and extract only checksum-bound regular members."""
from pathlib import Path
import json,sys,tarfile,shutil
repo=Path.cwd();sys.path[:0]=[str(repo/'scripts'),str(repo/'src')]
from e023_collect import verify
from e014_collect import member_path,binding
r=Path('/Users/rasmusallesoeenielsen/Documents/dl_binner/artifacts/e023-inspection/20261027T000221Z');collection=json.loads((r/'collection.json').read_text());v=verify(r/'e023-evidence.tar.gz',collection['archive'])
for key in ['archive','regular_members','logical_member_bytes','aliases','omitted_retained_on_disk']:
 if v[key]!=collection[key]:raise ValueError('Private collection/readback differs: '+key)
(r/'archive-verification.json').write_text(json.dumps(v,indent=2)+'\n')
dest=r/'verified';dest.mkdir(exist_ok=False)
with tarfile.open(r/'e023-evidence.tar.gz','r:gz')as a:
 for m in a:
  if not m.isfile():raise ValueError('Nonregular retained member')
  p=member_path(dest,m.name);p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb')as f:shutil.copyfileobj(a.extractfile(m),f,1024**2)
inv=json.loads((dest/'inventory.json').read_text())
for n,b in inv['members'].items():
 if binding(member_path(dest,n))!=b:raise ValueError('Extracted member differs: '+n)
print('PASS_ARCHIVE_AND_EVERY_EXTRACTED_MEMBER',v['regular_members'],v['logical_member_bytes'],flush=True)
