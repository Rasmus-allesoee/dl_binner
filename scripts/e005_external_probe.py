#!/usr/bin/env python3
"""Probe the retained AMBER runtime before site initialization and native evaluation.

Read-only verification of prefix, dependency/import origins and hash-bound source.
No installation, relocation, scoring or bypass of a failed native probe occurs.
"""
import faulthandler
import hashlib
import json
from pathlib import Path
import re
import sys

print(json.dumps(dict(stage='before_site', executable=sys.executable, prefix=sys.prefix)), flush=True)
faulthandler.enable()
faulthandler.dump_traceback_later(20, repeat=True)
prefix, source, spec_path, mode = map(str, sys.argv[1:5])
import site
site.main()
print(json.dumps(dict(stage='after_site', prefix=sys.prefix, sys_path=sys.path)), flush=True)
if Path(sys.prefix).resolve() != Path(prefix).resolve() or site.ENABLE_USER_SITE:
    raise RuntimeError('AMBER prefix/user-site mismatch')
if mode != 'local' and (not sys.platform.startswith('linux') or sys.version.split()[0] != '3.12.10'):
    raise RuntimeError('Retained native Linux/Python version differs')
spec = json.loads(Path(spec_path).read_text())
source = Path(source).resolve()
for name, expected in spec['source_files'].items():
    path = source/name
    if not path.resolve().is_relative_to(source) or not path.is_file():
        raise RuntimeError('Missing/outside AMBER source file')
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise RuntimeError('AMBER source byte mismatch: '+name)
unknown = {str(p.relative_to(source)) for p in (source/'cami_amber').rglob('*.py')}-set(spec['source_files'])
if unknown:
    raise RuntimeError('Unreviewed AMBER Python source: '+str(unknown))
import importlib
import importlib.metadata as metadata
normalize = lambda n: re.sub(r'[-_.]+', '-', n).lower()
inventory, origins = {}, {}
for d in metadata.distributions():
    if not Path(d.locate_file('')).resolve().is_relative_to(Path(prefix).resolve()):
        raise RuntimeError('AMBER distribution outside prefix: '+d.metadata['Name'])
    inventory[normalize(d.metadata['Name'])] = d.version
for package, version in spec['amber']['required_versions'].items():
    if inventory.get(normalize(package)) != version:
        raise RuntimeError('AMBER dependency version mismatch: '+package)
for name in ('numpy', 'pandas', 'matplotlib', 'bokeh', 'seaborn', 'jinja2', 'pyarrow', 'Bio'):
    print(json.dumps(dict(stage='before_import', package=name)), flush=True)
    module = importlib.import_module(name)
    origins[name] = str(Path(module.__file__).resolve())
    if not Path(origins[name]).is_relative_to(Path(prefix).resolve()):
        raise RuntimeError('AMBER dependency origin contamination')
sys.path.insert(0, str(source))
print(json.dumps(dict(stage='before_import', package='cami_amber.binning_classes')), flush=True)
from cami_amber.binning_classes import GenomeQuery, Options
from cami_amber.utils.load_data import read_metadata
import cami_amber.binning_classes as classes
if not Path(classes.__file__).resolve().is_relative_to(source):
    raise RuntimeError('AMBER source import contamination')
faulthandler.cancel_dump_traceback_later()
print('INVENTORY_JSON='+json.dumps(dict(prefix=sys.prefix, python=sys.version, source=str(source),
      source_commit=spec['source_commit'], source_files=spec['source_files'], distributions=inventory,
      origins=origins, native_linux=sys.platform.startswith('linux')), sort_keys=True), flush=True)
