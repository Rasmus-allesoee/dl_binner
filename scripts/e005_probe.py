#!/usr/bin/env python3
"""Start before site initialization; verify E005 prefix, package origins and CPU.

Invoked with -I -S -u so an interpreter/site/import hang is distinguishable in the
retained child log. The external stage supervisor enforces its timeout. This is
runtime inventory, not an inference benchmark or biological feasibility test.
"""
import faulthandler
import json
import os
from pathlib import Path
import sys

print(json.dumps(dict(stage='before_site', executable=sys.executable,
                      prefix=sys.prefix, base_prefix=sys.base_prefix)), flush=True)
faulthandler.enable()
faulthandler.dump_traceback_later(20, repeat=True)
prefix, role, threads, allow_mac = Path(sys.argv[1]).absolute(), sys.argv[2], int(sys.argv[3]), sys.argv[4] == 'local'
import site
site.main()
print(json.dumps(dict(stage='after_site', prefix=sys.prefix, sys_path=sys.path)), flush=True)
if Path(sys.prefix).absolute() != prefix or site.ENABLE_USER_SITE:
    raise RuntimeError('Runtime prefix/user-site mismatch')
if not allow_mac and not sys.platform.startswith('linux'):
    raise RuntimeError('Native Linux required')
import importlib
import importlib.metadata as metadata
packages = ('dl_binner', 'numpy', 'torch', 'networkx', 'threadpoolctl', 'psutil') if role == 'binner' else ('snakemake',)
origins = {}
for name in packages:
    print(json.dumps(dict(stage='before_import', package=name)), flush=True)
    module = importlib.import_module(name)
    path = Path(module.__file__).resolve()
    if not path.is_relative_to(prefix.resolve()):
        raise RuntimeError('Package outside isolated prefix: '+str(path))
    origins[name] = str(path)
distributions = {}
for distribution in metadata.distributions():
    if not Path(distribution.locate_file('')).resolve().is_relative_to(prefix.resolve()):
        raise RuntimeError('Distribution outside prefix: '+distribution.metadata['Name'])
    distributions[distribution.metadata['Name']] = distribution.version
result = dict(executable=sys.executable, prefix=sys.prefix, base_prefix=sys.base_prefix,
              python=sys.version, origins=origins, distributions=distributions,
              platform=sys.platform, native_linux=sys.platform.startswith('linux'),
              allocation_threads=threads, affinity=sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None)
if role == 'binner':
    import torch
    torch.set_num_threads(threads)
    torch.set_num_interop_threads(1)
    from threadpoolctl import threadpool_info, threadpool_limits
    with threadpool_limits(limits=threads):
        pools = threadpool_info()
        if any(p['num_threads'] > threads for p in pools):
            raise RuntimeError('Effective numerical pool exceeds allocation')
        if not allow_mac and (torch.version.cuda is not None or '+cpu' not in torch.__version__):
            raise RuntimeError('CPU-only PyTorch build required')
        result.update(torch_version=torch.__version__, torch_cuda=torch.version.cuda,
                      torch_threads=torch.get_num_threads(), interop=torch.get_num_interop_threads(),
                      loader_workers=0, pools=pools)
faulthandler.cancel_dump_traceback_later()
print('INVENTORY_JSON='+json.dumps(result, sort_keys=True), flush=True)
