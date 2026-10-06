#!/usr/bin/env python3
"""Probe E006 prefix before site/imports; compare complete inventory and origins.

Use -I -B -S. Numerical dependencies may reside only in the explicitly reviewed
base prefix; the new dl_binner code must be in its own versioned venv. The caller
enforces wall/RSS bounds; this performs no scientific inference or installation.
"""
import faulthandler
import json
from pathlib import Path
import sys
print('before_site '+sys.executable+' '+sys.prefix, flush=True)
faulthandler.enable(); faulthandler.dump_traceback_later(20, repeat=True)
cfg = json.loads(Path(sys.argv[1]).read_text())
import site
site.main()
print('after_site '+sys.prefix, flush=True)
prefix, dependencies = Path(cfg['prefix']).absolute(), Path(cfg['dependency_prefix']).absolute()
if Path(sys.prefix).absolute() != prefix or site.ENABLE_USER_SITE:
    raise RuntimeError('Lexical prefix/user-site contract failed')
if not cfg['local'] and not sys.platform.startswith('linux'):
    raise RuntimeError('Native Linux required')
import importlib
import importlib.metadata as metadata
import re
def normalize(name): return re.sub(r'[-_.]+','-',name).lower()
distributions = {}
for dist in metadata.distributions():
    name = normalize(dist.metadata['Name'])
    if name in distributions: raise RuntimeError('Duplicate distribution: '+name)
    origin = Path(dist.locate_file('')).resolve()
    if not any(origin.is_relative_to(v.resolve()) for v in (prefix, dependencies)):
        raise RuntimeError('Distribution outside reviewed prefixes: '+str(origin))
    distributions[name] = dist.version
if distributions != {normalize(k):v for k,v in cfg['expected_distributions'].items()}:
    raise RuntimeError('Complete runtime inventory mismatch: '+json.dumps(distributions, sort_keys=True))
if sys.version.split()[0] != cfg['expected_python']:
    raise RuntimeError('Python version mismatch')
origins = {}
packages = ('dl_binner','numpy','torch','networkx','threadpoolctl') if cfg['role']=='binner' else ('snakemake',)
packages = sorted(set(packages) | set(cfg.get('expected_origins',{})))
for name in packages:
    print('before_import '+name, flush=True)
    module = importlib.import_module(name); path = Path(module.__file__).resolve()
    expected = prefix if cfg.get('own_package') and name=='dl_binner' else dependencies
    if not path.is_relative_to(expected.resolve()): raise RuntimeError('Unexpected import origin: '+str(path))
    if name in cfg.get('expected_origins',{}) and path != Path(cfg['expected_origins'][name]).resolve():
        raise RuntimeError('Accepted native import origin changed: '+name)
    origins[name] = str(path)
if cfg.get('own_package'):
    import hashlib
    code = Path(origins['dl_binner']).parent
    actual = {str(p.relative_to(code)):dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
              for p in code.rglob('*') if p.is_file() and p.suffix in ('.py','.json','.smk')}
    if actual != cfg['package_files']: raise RuntimeError('Installed wheel code/defaults/DAG mismatch')
import sysconfig
result = dict(executable=sys.executable, prefix=sys.prefix, base_prefix=sys.base_prefix,
              python_version=sys.version.split()[0], site_directory=sysconfig.get_path('purelib'),
              distributions=distributions, origins=origins, native_linux=sys.platform.startswith('linux'))
if cfg['role']=='binner':
    import torch
    from threadpoolctl import threadpool_info, threadpool_limits
    torch.set_num_threads(4); torch.set_num_interop_threads(1)
    with threadpool_limits(limits=4):
        pools = threadpool_info()
        if any(p['num_threads']>4 for p in pools): raise RuntimeError('Numerical threads exceed four')
        if torch.version.cuda is not None or (not cfg['local'] and '+cpu' not in torch.__version__):
            raise RuntimeError('CPU-only PyTorch required')
        result.update(torch_threads=torch.get_num_threads(), interop=torch.get_num_interop_threads(),
                      loader_workers=0, torch_version=torch.__version__, torch_cuda=torch.version.cuda, pools=pools)
else:
    if distributions.get('snakemake') != '9.16.3': raise RuntimeError('Pinned Snakemake version required')
faulthandler.cancel_dump_traceback_later()
print('INVENTORY_JSON='+json.dumps(result, sort_keys=True), flush=True)
