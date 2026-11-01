#!/usr/bin/env python3
"""Admit restored CUDA bytes and the current owned product on the actual GPU.

Checks full distribution versions/origins and installed product bytes, separate
native import/library families, single CUDA device and the real console entry.
"""
import argparse,hashlib,importlib.metadata as metadata,json,platform,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def run(base,recipe,candidate_lock,runtime_manifest,output):
    """Reject missing, foreign or changed runtime members without reinstall fallback."""
    from e029_control import product_scope
    product_scope()
    base=Path(base);prefix=Path(sys.prefix);r=json.loads(Path(recipe).read_text());lock=json.loads(Path(candidate_lock).read_text());m=json.loads(Path(runtime_manifest).read_text())
    if not sys.flags.isolated or not sys.dont_write_bytecode or platform.system()!='Linux'or platform.python_version()!='3.10.15'or prefix==base:raise ValueError('Fresh owned isolated Linux CUDA consumer required')
    norm=lambda x:re.sub('[-_.]+','-',x.lower());expected={norm(n):v['version']for n,v in r['wheels'].items()};expected['dl-binner']='0.1.0.dev9';actual={};origins={}
    for dist in metadata.distributions():
        name=norm(dist.metadata['Name']);p=Path(dist._path).resolve();allowed=prefix if name=='dl-binner'else base
        if name in actual or not p.is_relative_to(allowed.resolve()):raise ValueError('Duplicate/foreign CUDA distribution')
        actual[name]=dist.version;origins[name]=str(p)
    if actual!=expected:raise ValueError('Complete retained CUDA inventory differs: '+repr({k:(expected.get(k),actual.get(k))for k in expected.keys()|actual.keys()if expected.get(k)!=actual.get(k)}))
    import dl_binner
    package=Path(dl_binner.__file__).parent;files={str(p.relative_to(package)):binding(p)for p in package.rglob('*')if p.is_file()and p.suffix in ['.py','.json']}
    if not package.is_relative_to(prefix)or files!=lock['package_files']:raise ValueError('Installed current candidate bytes differ')
    allowed_hash={v['sha256']for v in m['members'].values()if v['kind']=='file'};groups={}
    for group,mods in dict(tensor=['torch','numpy','transformers','tokenizers','einops'],graph=['scipy','sklearn','numba','pynndescent','igraph','leidenalg'],markers=['pyrodigal','pyhmmer','archspec']).items():
        code='''import sys,json,importlib,hashlib
from pathlib import Path
origins={n:str(Path(importlib.import_module(n).__file__).resolve())for n in sys.argv[1].split(',')}
if any(not Path(x).is_relative_to(Path(sys.argv[2]).resolve())for x in origins.values()):raise ValueError('Foreign native import')
if 'torch'in sys.modules:
 t=sys.modules['torch'];t.set_num_threads(4);t.set_num_interop_threads(1)
 if t.version.cuda is None or not t.cuda.is_available()or t.cuda.device_count()!=1:raise ValueError('Actual single CUDA GPU unavailable')
if 'numba'in sys.modules:sys.modules['numba'].set_num_threads(4)
from threadpoolctl import threadpool_info
pools=threadpool_info()
if any(x['num_threads']>4 for x in pools):raise ValueError('Native pool exceeds four')
if any(x['prefix']=='libiomp'for x in pools)and any(x['prefix']=='libomp'for x in pools):raise ValueError('Conflicting OpenMP families')
libs={str(Path(x['filepath']).resolve()):hashlib.sha256(Path(x['filepath']).read_bytes()).hexdigest()for x in pools}
print(json.dumps(dict(origins=origins,pools=pools,libraries=libs)))'''
        result=subprocess.run([sys.executable,'-I','-B','-c',code,','.join(mods),str(base)],check=True,text=True,capture_output=True,timeout=180);value=json.loads(result.stdout.splitlines()[-1])
        if not set(value['libraries'].values())<=allowed_hash:raise ValueError('Loaded library differs from retained CUDA bytes')
        groups[group]=value
    cli=subprocess.run([str(prefix/'bin/dl-binner'),'--help'],check=True,text=True,capture_output=True,timeout=30)
    if 'context-stage'not in cli.stdout:raise ValueError('Installed console differs')
    write(output,dict(status='PASS_COMPLETE_RESTORED_CUDA_BASE_AND_NEW_OWNED_PACKAGE',prefix=str(prefix),base=str(base),distributions=actual,distribution_origins=origins,package_files=files,groups=groups,real_installed_CLI=True,dependency_reinstallation=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['base','recipe','candidate-lock','runtime-manifest','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();run(a.base,a.recipe,a.candidate_lock,a.runtime_manifest,a.output)
