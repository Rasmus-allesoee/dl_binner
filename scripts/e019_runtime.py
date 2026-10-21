#!/usr/bin/env python3
"""Own only E019 package bytes; borrow accepted dependencies explicitly read-only.

This job-local prefix is not portable. Dependency directory links exclude the old
project and path-injecting overlays. Every child uses lexical Python -I -B. Full
inventory, origins and actual native library targets are independently checked;
an existing or corrupt prefix fails instead of reinstalling or copying a fallback.
"""
import argparse
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import platform
import re
import site
import subprocess
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e014_collect import binding
from e009_common import write_json


def create(base, destination, wheel, output):
    """Create a fresh lexical venv, link reviewed dependencies, install locked wheel."""
    base, destination, wheel = map(lambda p: Path(p).absolute(), [base, destination, wheel])
    if Path(sys.prefix).absolute() != base or destination.exists():
        raise ValueError('Exact accepted base and new prefix required')
    version = f'python{sys.version_info.major}.{sys.version_info.minor}'
    source = base/'lib'/version/'site-packages'
    subprocess.run([sys.executable, '-I', '-B', '-m', 'venv', '--without-pip', destination], check=True)
    target = destination/'lib'/version/'site-packages'; linked = {}; excluded = []
    for p in sorted(source.iterdir()):
        if p.name in ['dl_binner', '__pycache__'] or p.name.startswith('dl_binner-') or p.suffix in ['.pth', '.pyc']:
            excluded.append(p.name); continue
        if p.is_symlink() or not (p.is_dir() or p.is_file()):
            raise ValueError('Unreviewed base-site link/member')
        (target/p.name).symlink_to(p, target_is_directory=p.is_dir()); linked[p.name] = str(p)
    # Install own project only. No dependency resolver/network/copy fallback.
    with zipfile.ZipFile(wheel) as z:
        if any('/../' in '/'+n or n.startswith('/') or n.endswith('.pth') or '.data/' in n for n in z.namelist()):
            raise ValueError('Unsafe/unexpected candidate wheel member')
        if any((target/n).exists() for n in z.namelist() if not n.endswith('/')):
            raise ValueError('Candidate would overwrite borrowed member')
    subprocess.run([str(destination/'bin/python'), '-I', '-B', '-m', 'pip', '--isolated',
                    'install', '--no-deps', '--no-index', '--no-compile', str(wheel)], check=True,
                   env={**os.environ, 'PIP_DISABLE_PIP_VERSION_CHECK':'1'})
    write_json(output, dict(status='CREATED', base=str(base), prefix=str(destination), wheel=binding(wheel),
        linked_dependencies=linked, excluded=excluded, portable=False, read_only_reuse=True,
        scope='New owned package plus explicit complete dependency links; base stdlib retained; no old product or overlays.'))


def probe(base, lock, output, borrowed=True):
    """Check full distribution/import/source/library identity in isolated processes."""
    base = Path(base).absolute(); lock = json.loads(Path(lock).read_text()); prefix = Path(sys.prefix).absolute()
    if not sys.flags.isolated or not sys.dont_write_bytecode or site.ENABLE_USER_SITE:
        raise ValueError('Isolated bytecode-free runtime required')
    if (platform.python_version()!=lock['runtime']['python_version'] or
            platform.system()!=lock['runtime']['system'] or sys.base_prefix!=lock['runtime']['base_prefix']):
        raise ValueError('Native interpreter/platform/base identity differs')
    expected = lock['runtime']['distributions'].copy(); expected['dl-binner'] = '0.1.0.dev7'
    normalize = lambda n: re.sub(r'[-_.]+', '-', n.lower())
    inventory = {}; locations = {}
    for d in metadata.distributions():
        name = normalize(d.metadata['Name']); loc = Path(d._path).resolve()
        if name in inventory: raise ValueError('Duplicate runtime distribution')
        allowed = prefix if name == 'dl-binner' or not borrowed else base
        if not loc.is_relative_to(allowed.resolve()): raise ValueError('Foreign distribution '+str(loc))
        inventory[name] = d.version; locations[name] = str(loc)
    if inventory != expected: raise ValueError('Complete E019 distribution inventory differs')
    import dl_binner
    package = Path(dl_binner.__file__).parent
    if not package.is_relative_to(prefix): raise ValueError('New project import is not owned')
    source = {str(p.relative_to(package)): binding(p) for p in package.rglob('*') if p.is_file() and p.suffix in ['.py', '.json']}
    if source != lock['candidate_source']: raise ValueError('Installed candidate source/defaults differ')
    groups = {}; libraries = {}
    for label, names in {'tensor': ['dl_binner', 'torch', 'numpy'],
                         'graph': ['scipy', 'sklearn', 'numba', 'pynndescent', 'igraph', 'leidenalg'],
                         'markers': ['pyrodigal', 'pyhmmer', 'archspec']}.items():
        code = '''import importlib,json,sys
from pathlib import Path
origins={n:str(Path(importlib.import_module(n).__file__).resolve()) for n in sys.argv[1].split(',')}
if 'torch' in sys.modules:
 t=sys.modules['torch'];t.set_num_threads(4);t.set_num_interop_threads(1)
 if t.version.cuda is not None:raise ValueError('CPU runtime required')
if 'numba' in sys.modules:sys.modules['numba'].set_num_threads(4)
from threadpoolctl import threadpool_info
pools=threadpool_info()
if any(p['num_threads']>4 for p in pools):raise ValueError('CPU pool exceeds four')
if any(p['prefix']=='libiomp'for p in pools)and any(p['prefix']=='libomp'for p in pools):raise ValueError('Incompatible OpenMP families')
print(json.dumps(dict(origins=origins,pools=pools)))'''
        r = subprocess.run([sys.executable, '-I', '-B', '-c', code, ','.join(names)], capture_output=True, text=True, check=True, timeout=180)
        group = json.loads(r.stdout.splitlines()[-1]); groups[label] = group
        for name, origin in group['origins'].items():
            allowed = prefix if name == 'dl_binner' or not borrowed else base
            if not Path(origin).is_relative_to(allowed.resolve()): raise ValueError('Foreign module origin '+origin)
        for pool in group['pools']:
            alias = Path(pool['filepath']); real = alias.resolve(strict=True)
            libraries[str(real)] = binding(real)
    # Native aliases may traverse the new lexical prefix; resolved regular targets
    # must match accepted library contents, never randomized loader addresses.
    accepted = {r['resolved_regular']: r['content'] for r in lock['installed']['loaded_math_libraries']}
    if libraries != accepted: raise ValueError('Actual native library targets differ')
    write_json(output, dict(status='PASS', python=sys.executable, prefix=str(prefix), base_prefix=sys.base_prefix,
        dependency_base=str(base), python_version=platform.python_version(), distributions=inventory,
        distribution_locations=locations, source=source, isolated_native_groups=groups,
        native_library_targets=libraries, borrowed_read_only=borrowed, portable=False))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('operation', choices=['create', 'probe'])
    for name in ['base', 'destination', 'wheel', 'lock', 'output']: p.add_argument('--'+name, type=Path)
    a = p.parse_args()
    if a.operation == 'create': create(a.base, a.destination, a.wheel, a.output)
    else: probe(a.base, a.lock, a.output)
