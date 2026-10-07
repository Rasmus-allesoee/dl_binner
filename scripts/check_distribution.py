#!/usr/bin/env python3
"""Inspect actual wheel/sdist bytes and package provenance without installing them.

Checks archive paths, wheel RECORD hashes, metadata/CLI, packaged defaults,
the accepted unchanged code, and absence of research payloads. An optional wheel
rebuilt from the sdist must contain equivalent package/metadata bytes. Writes an
exclusive JSON receipt; does not publish, import the binner or run science.
"""
import argparse
import base64
import csv
from email.parser import BytesParser
import hashlib
import io
import json
from pathlib import Path
import tarfile
import zipfile


def record(path):
    """Incrementally hash a regular retained build artifact."""
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda:stream.read(1024*1024),b''):h.update(part)
    return dict(bytes=Path(path).stat().st_size,sha256=h.hexdigest())


def inspect_wheel(path,accepted):
    """Validate the installed payload and every wheel RECORD entry independently."""
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)):raise ValueError('Duplicate wheel member')
        files={name:archive.read(name) for name in names}
    if any(Path(n).is_absolute() or '..' in Path(n).parts for n in files):raise ValueError('Unsafe wheel path')
    if any(not n.startswith(('dl_binner/','dl_binner-0.1.0.dev3.dist-info/')) for n in files):raise ValueError('Unexpected wheel payload')
    metadata_name='dl_binner-0.1.0.dev3.dist-info/METADATA'
    metadata=BytesParser().parsebytes(files[metadata_name])
    if metadata['Name']!='dl-binner' or metadata['Version']!='0.1.0.dev3':raise ValueError('Wheel version/name mismatch')
    if set(metadata['Requires-Python'].split(','))!={'<3.13','>=3.10'}:raise ValueError('Unsupported Python metadata')
    if set(metadata.get_all('Requires-Dist',[]))!={'numpy==1.26.4','torch==2.2.2','networkx==3.4.2','threadpoolctl==3.5.0'}:
        # Older pinned setuptools may insert whitespace before the version clause.
        if {v.replace(' ','') for v in metadata.get_all('Requires-Dist',[])}!={'numpy==1.26.4','torch==2.2.2','networkx==3.4.2','threadpoolctl==3.5.0'}:
            raise ValueError('Scientific dependency metadata changed')
    if 'dl-binner = dl_binner.cli:main' not in files['dl_binner-0.1.0.dev3.dist-info/entry_points.txt'].decode():raise ValueError('Missing installed CLI')
    rows=list(csv.reader(io.StringIO(files['dl_binner-0.1.0.dev3.dist-info/RECORD'].decode())))
    if len(rows)!=len(files) or {r[0] for r in rows}!=set(files):raise ValueError('Wheel RECORD set mismatch')
    for name,digest,size in rows:
        if name.endswith('/RECORD'):
            if digest or size:raise ValueError('RECORD self entry must have no digest')
        elif digest!='sha256='+base64.urlsafe_b64encode(hashlib.sha256(files[name]).digest()).decode().rstrip('=') or int(size)!=len(files[name]):
            raise ValueError('Wheel RECORD bytes changed: '+name)
    package={n.removeprefix('dl_binner/'):v for n,v in files.items() if n.startswith('dl_binner/')}
    root=Path(__file__).absolute().parents[1]/'src/dl_binner'
    expected={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file() and p.suffix in ('.py','.json')}
    if package!=expected:raise ValueError('Wheel payload differs from this committed build source')
    for name,expected in accepted.items():
        value=package[name]
        if dict(bytes=len(value),sha256=hashlib.sha256(value).hexdigest())!=expected:raise ValueError('Accepted package bytes changed: '+name)
    if package['__init__.py']!=b'"""Own experimental contrastive binner; no pretrained GLM or baseline executable."""\n__version__ = \'0.1.0.dev3\'\n':
        raise ValueError('Unexpected initializer change beyond version')
    return files


def inspect_sdist(path,wheel):
    """Require a clean rebuildable package/test recipe, with no external datasets."""
    with tarfile.open(path) as archive:
        members=archive.getmembers();names=[m.name for m in members]
        if len(names)!=len(set(names)):raise ValueError('Duplicate sdist member')
        if any(not (m.isfile() or m.isdir()) or Path(m.name).is_absolute() or '..' in Path(m.name).parts for m in members):raise ValueError('Unsafe sdist path/link')
        roots={Path(m.name).parts[0] for m in members}
        if len(roots)!=1:raise ValueError('sdist has multiple roots')
        root=next(iter(roots))
        files={str(Path(m.name).relative_to(root)):archive.extractfile(m).read() for m in members if m.isfile()}
    allowed=('src/dl_binner/','src/dl_binner.egg-info/','tests/product/','requirements/')
    top={'README.md','pyproject.toml','MANIFEST.in','PKG-INFO','setup.cfg','docs/INSTALLATION.md','docs/PROTOTYPE.md',
         'scripts/test_product.py','scripts/check_distribution.py','scripts/check_runtime.py'}
    if any(n not in top and not n.startswith(allowed) for n in files):raise ValueError('Unexpected sdist research payload')
    required={'README.md','pyproject.toml','requirements/binner-cpu.txt','requirements/workflow.txt','requirements/build.txt',
              'tests/product/accepted-package.json','tests/product/test_core.py','tests/product/test_run.py',
              'tests/product/fixtures.py','scripts/test_product.py','scripts/check_distribution.py','scripts/check_runtime.py','docs/INSTALLATION.md'}
    if not required.issubset(files):raise ValueError('sdist missing reproducibility files')
    for name,value in wheel.items():
        if name.startswith('dl_binner/') and files['src/'+name]!=value:raise ValueError('sdist/wheel package differs: '+name)
    if files['README.md'] not in wheel['dl_binner-0.1.0.dev3.dist-info/METADATA']:raise ValueError('Product README not in wheel metadata')
    return files


def main():
    """Write a compact exclusive build-inspection receipt after all checks pass."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('wheel','sdist','output'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--rebuilt-wheel',type=Path)
    args=parser.parse_args()
    root=Path(__file__).absolute().parents[1]
    accepted=json.loads((root/'tests/product/accepted-package.json').read_text())
    wheel=inspect_wheel(args.wheel,accepted);sdist=inspect_sdist(args.sdist,wheel)
    if args.rebuilt_wheel:
        rebuilt=inspect_wheel(args.rebuilt_wheel,accepted)
        if wheel!=rebuilt:raise ValueError('sdist rebuilt wheel content differs (archive timestamps may differ)')
    result=dict(status='passed',scope='Package contents and byte provenance, not runtime/science',
        wheel=dict(path=str(args.wheel),**record(args.wheel)),sdist=dict(path=str(args.sdist),**record(args.sdist)),
        wheel_members=sorted(wheel),sdist_members=sorted(sdist),accepted_scientific_bytes_unchanged=True,
        initializer_change='Versioned product execution change; scientific files unchanged',rebuilt_wheel=dict(path=str(args.rebuilt_wheel),**record(args.rebuilt_wheel)) if args.rebuilt_wheel else None)
    with args.output.open('x') as stream:json.dump(result,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':main()
