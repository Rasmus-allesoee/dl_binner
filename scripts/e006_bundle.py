#!/usr/bin/env python3
"""Build the small checksum-bound E006 packet from committed driver contracts.

Includes only the accepted platform-independent wheel, stdlib supervisor source,
small retained real-DNA software fixtures, runtime baseline and smoke scripts.
Never transfers a Mac venv, Linux dependency payload, large DNA or accepted runs.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zipfile

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e006_owner import record, write

ROOT=Path(__file__).absolute().parents[1]
EXP='experiments/E006-cli-usability'
SOURCES=['scripts/e006_owner.py','scripts/e006_runtime.py','scripts/e006_smoke.py','scripts/e006_bundle.py',
         EXP+'/linux-smoke.json',EXP+'/runtime-baseline.json']


def build(output):
    """Bind committed code, accepted wheel/input bytes, and emit exactly two uploads."""
    output=Path(output).absolute(); output.mkdir(parents=True,exist_ok=False)
    folder=output/'e006-linux-smoke'; folder.mkdir()
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name in SOURCES+['src/dl_binner/supervision.py']:
        data=(ROOT/name).read_bytes()
        if data!=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT):
            raise ValueError('Uncommitted transfer source: '+name)
        target=folder/(name if name!='src/dl_binner/supervision.py' else 'payload/supervision.py')
        target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
    spec=json.loads((folder/EXP/'linux-smoke.json').read_text())
    wheel=ROOT/'artifacts/e006-cli-usability/setup/dist-v7/dl_binner-0.1.0.dev1-py3-none-any.whl'
    if record(wheel)!=spec['wheel_record']: raise ValueError('Accepted E006 wheel bytes changed')
    target=folder/spec['wheel']; shutil.copyfile(wheel,target)
    package={}
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.startswith('dl_binner/') and Path(name).suffix in ('.py','.json','.smk'):
                relative=name[len('dl_binner/'):]; data=archive.read(name)
                if data!=(ROOT/'src/dl_binner'/relative).read_bytes():
                    raise ValueError('Current package differs from accepted wheel: '+relative)
                import hashlib
                package[relative]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    for name,expected in spec['input_files'].items():
        source=ROOT/'artifacts/e006-cli-usability/integration-002/input'/name
        if record(source)!=expected: raise ValueError('Retained E006 input bytes changed: '+name)
        target=folder/'input'/name; target.parent.mkdir(exist_ok=True); shutil.copyfile(source,target)
    shutil.copyfile(folder/EXP/'runtime-baseline.json',folder/'runtime-baseline.json')
    files={str(p.relative_to(folder)):record(p) for p in sorted(folder.rglob('*')) if p.is_file()}
    write(folder/'bundle-manifest.json',dict(record='E006',kind='generic Linux smoke v1',source_commit=commit,
          accepted_wheel_source='e30023c0a9e78c255da3b7abc43ed3025571dcef',files=files,package_files=package,
          scope='Tiny software job only; dependencies remain on UCloud; no E005 science'))
    archive=output/'e006-linux-smoke-v1.tar.gz'
    with archive.open('xb') as stream,tarfile.open(fileobj=stream,mode='w:gz') as tar:
        for path in sorted(folder.rglob('*')):
            if path.is_file(): tar.add(path,arcname='e006-linux-smoke/'+str(path.relative_to(folder)),recursive=False)
    checksum=archive.with_name(archive.name+'.sha256')
    checksum.write_text(record(archive)['sha256']+'  '+archive.name+'\n')
    result=dict(archive=str(archive),checksum=str(checksum),archive_record=record(archive),source_commit=commit,
                packet_files=len(files)+1,packet_logical_bytes=sum(v['bytes'] for v in files.values()),wheel=spec['wheel_record'])
    print(json.dumps(result,sort_keys=True)); return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    build(p.parse_args().output)
