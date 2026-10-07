#!/usr/bin/env python3
"""Build a checksum-bound offline Linux smoke transfer from committed sources.

Package only explicit E005 source/contracts, unchanged accepted binner wheel,
small smoke inputs and pinned binary payloads. Reference caches, raw pilot DNA,
old environments and unrelated files are never vendored. Metadata closure is
checked for Linux/Python 3.12 before emitting hashed install locks.
"""
import argparse
import email
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e005_smoke import sha, write


def wheel_lock(folder, output):
    """Bind all wheel bytes and independently validate target dependency closure."""
    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name
    from packaging.version import Version
    records = {}
    for path in sorted(Path(folder).glob('*.whl')):
        with zipfile.ZipFile(path) as archive:
            meta = email.message_from_bytes(archive.read(next(n for n in archive.namelist() if n.endswith('.dist-info/METADATA'))))
            wheel = archive.read(next(n for n in archive.namelist() if n.endswith('.dist-info/WHEEL'))).decode()
        name = canonicalize_name(meta['Name'])
        if name in records:
            raise ValueError('Duplicate wheel distribution: '+name)
        records[name] = dict(name=name, version=meta['Version'], filename=path.name,
                             sha256=sha(path), bytes=path.stat().st_size,
                             requires=meta.get_all('Requires-Dist', []), wheel=wheel,
                             requires_python=meta.get('Requires-Python'))
    target = dict(os_name='posix', sys_platform='linux', platform_machine='x86_64',
                  platform_python_implementation='CPython', python_version='3.12',
                  python_full_version='3.12.10', implementation_name='cpython',
                  implementation_version='3.12.10', platform_system='Linux',
                  platform_release='', platform_version='', extra='')
    from packaging.specifiers import SpecifierSet
    for name, record in records.items():
        if record['requires_python'] and Version('3.12.10') not in SpecifierSet(record['requires_python']):
            raise ValueError('Unsupported target Python: '+name)
        for raw in record['requires']:
            requirement = Requirement(raw)
            if requirement.marker and not requirement.marker.evaluate(target):
                continue
            needed = canonicalize_name(requirement.name)
            if needed not in records or Version(records[needed]['version']) not in requirement.specifier:
                raise ValueError(f'Incomplete Linux wheel closure: {name} needs {raw}')
    Path(output).write_text('# Offline exact-wheel lock; install with --no-index --no-deps --require-hashes.\n'+
                           ''.join(f"{r['name']}=={r['version']} --hash=sha256:{r['sha256']}\n" for r in records.values()))
    return records


def build(output):
    """Make one fresh reproducible archive with immutable source and payload receipts."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    folder = output/'e005-linux-smoke'
    folder.mkdir()
    sources = ['scripts/e005_owner.py', 'scripts/e005_smoke.py', 'scripts/e005_probe.py',
               'scripts/e005_failure_checks.py', 'workflows/first-binner/linux_smoke.smk',
               'experiments/E005-linux-pilot/smoke.json', 'experiments/E005-linux-pilot/binner-linux.lock',
               'experiments/E005-linux-pilot/workflow-linux.lock', 'experiments/E005-linux-pilot/runtime-payloads.json',
               'experiments/E005-linux-pilot/README.md', 'experiments/E005-linux-pilot/OPERATIONS.md',
               'experiments/E005-linux-pilot/pilot.json', 'experiments/E005-linux-pilot/pilot-inputs.json',
               'experiments/E005-linux-pilot/pilot-contigs.tsv', 'experiments/E004-first-binner/training.json']
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for name in sources:
        data = subprocess.check_output(['git', 'show', f'{commit}:{name}'], cwd=ROOT)
        if data != (ROOT/name).read_bytes():
            raise ValueError('Uncommitted transfer source: '+name)
        path = folder/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    payload = ROOT/'artifacts/e005-linux-pilot/payload'
    shutil.copytree(payload, folder/'payload')
    shutil.copytree(ROOT/'artifacts/e005-linux-pilot/input/smoke', folder/'input/smoke')
    pin = json.loads((ROOT/'experiments/E005-linux-pilot/runtime-payloads.json').read_text())
    for name, entry in pin['files'].items():
        if sha(folder/'payload'/name) != entry['sha256']:
            raise ValueError('Frozen runtime payload drift: '+name)
    smoke = json.loads((folder/'experiments/E005-linux-pilot/smoke.json').read_text())
    for name, expected in smoke['input_sha256'].items():
        if sha(folder/name) != expected:
            raise ValueError('Frozen smoke input drift: '+name)
    files = {str(p.relative_to(folder)): dict(sha256=sha(p), bytes=p.stat().st_size)
             for p in sorted(folder.rglob('*')) if p.is_file()}
    write(folder/'bundle-manifest.json', dict(schema=1, source_commit=commit,
          accepted_package_source_commit='7b24a6b9677d8d7625d392aa0fc0a189952767cb',
          scope='offline native CPU/Linux software smoke; no pilot execution', files=files))
    archive = output/'e005-linux-smoke-v2.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                tar.add(path, arcname='e005-linux-smoke/'+str(path.relative_to(folder)), recursive=False)
    checksum = archive.with_name(archive.name+'.sha256')
    checksum.write_text(sha(archive)+'  '+archive.name+'\n')
    print(json.dumps(dict(archive=str(archive), checksum=str(checksum), source_commit=commit,
                         sha256=sha(archive), bytes=archive.stat().st_size)), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.output)
