#!/usr/bin/env python3
"""Build an immutable E009 owner preflight from committed code/config and tiny DNA.

The packet owns no Mac environment or linked dependency. Linux source/model
payloads are acquired by pinned receipts; only the small Linux bootstrap is
included. Build into a fresh destination, bind every member, then hash the archive.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
sys.path.insert(0,str(Path(__file__).absolute().parent))

from e009_common import binding,extract,write_json
from e009_owner import verify_bundle

ROOT=Path(__file__).absolute().parents[1]
EXP='experiments/E009-competitive-benchmark'


def build(destination,bootstrap=None,version='v12',recovery_only=False):
    """Require committed transfer inputs and return the exact two owner upload paths."""
    destination=Path(destination).absolute()
    if not version.isalnum():raise ValueError('Simple version name required')
    if destination.exists():raise ValueError('Use a fresh versioned transfer directory')
    scripts=sorted((ROOT/'scripts').glob('e009_*.py'))
    record_names=['preflight.json','runtime-baseline.json','comebin-base-freeze.txt'] if recovery_only else [
             'protocol.json','preflight.json','fixture.json','native-lock.json','development-overlap.json',
             'runtime-baseline.json','comebin-base-freeze.txt','utilities-linux-lock.json','linux-runtime-recovery-v8.json',
             'linux-preflight-v10.json','failed-paths-lock.json']
    records=[ROOT/EXP/name for name in record_names]
    if not recovery_only:
        if bootstrap is None:raise ValueError('Full preflight needs pinned Linux bootstrap')
        bootstrap=Path(bootstrap).absolute()
        fixture=json.loads((ROOT/EXP/'fixture.json').read_text());fixture_path=ROOT/fixture['fixture_archive']['path']
    inputs=scripts+records+[ROOT/'src/dl_binner/supervision.py']+([] if recovery_only else [fixture_path])
    names=[str(p.relative_to(ROOT)) for p in inputs]
    tracked=subprocess.check_output(['git','ls-files','--',*names],cwd=ROOT,text=True).splitlines()
    if set(tracked)!=set(names):raise ValueError('Commit all packet source/config/fixture inputs before building')
    subprocess.run(['git','diff','--exit-code','HEAD','--',*names],cwd=ROOT,check=True,capture_output=True)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if not recovery_only:
        lock=json.loads((ROOT/EXP/'native-lock.json').read_text());expected=lock['payloads']['micromamba']
        if binding(bootstrap)!={k:expected[k] for k in ('bytes','sha256')}:raise ValueError('Linux bootstrap bytes changed')
        if binding(fixture_path)!={k:fixture['fixture_archive'][k] for k in ('bytes','sha256')}:raise ValueError('Tiny fixture archive changed')
    destination.mkdir(parents=True);packet=destination/('e009-preflight-'+version);packet.mkdir()
    for path in scripts+records:
        target=packet/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
    (packet/'payload').mkdir();shutil.copyfile(ROOT/'src/dl_binner/supervision.py',packet/'payload/supervision.py')
    if not recovery_only:
        shutil.copyfile(bootstrap,packet/'payload/micromamba-linux.tar.bz2');extract(fixture_path,packet/'input')
        for name,expected in fixture['files'].items():
            if binding(packet/'input'/name)!=expected:raise ValueError('Expanded fixture bytes changed')
    files={str(p.relative_to(packet)):binding(p) for p in sorted(packet.rglob('*')) if p.is_file()}
    write_json(packet/'bundle-manifest.json',{'record':'E009','version':version,'source_commit':head,'files':files,
               'scope':'job-local runtime recovery only' if recovery_only else 'asset/native preflight only; no full-community fit, benchmark score or architecture comparison',
               'scientific_execution_authorized':False})
    verify_bundle(packet)
    archive=destination/(packet.name+'.tar.gz')
    with archive.open('xb') as stream,tarfile.open(fileobj=stream,mode='w:gz') as out:
        for path in sorted(packet.rglob('*')):
            if not path.is_file():continue
            member=out.gettarinfo(path,arcname=packet.name+'/'+str(path.relative_to(packet)))
            member.uid=member.gid=0;member.uname=member.gname='';member.mtime=0;member.mode=0o644
            with path.open('rb') as src:out.addfile(member,src)
    checksum=archive.with_name(archive.name+'.sha256')
    checksum.write_text(binding(archive)['sha256']+'  '+archive.name+'\n')
    receipt={'source_commit':head,'archive':str(archive),'file':binding(archive),'checksum':str(checksum),
             'manifest':binding(packet/'bundle-manifest.json'),'files':len(files),'recovery_only':recovery_only,'linux_validation':'not yet executed'}
    write_json(destination/'transfer-receipt.json',receipt);return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True)
    p.add_argument('--bootstrap',type=Path);p.add_argument('--version',default='v12')
    p.add_argument('--recovery-only',action='store_true')
    args=p.parse_args();print(json.dumps(build(args.destination,args.bootstrap,args.version,args.recovery_only),indent=2))
