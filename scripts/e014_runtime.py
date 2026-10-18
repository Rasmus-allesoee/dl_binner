#!/usr/bin/env python3
"""Own a fresh dev5 CPU site from an accepted complete native recipe, then verify it.

No scientific output is consumed or fit here. Dependency copies are regular owned
bytes, never site-package links/overlays. The lexical Python base/stdlib remains
explicit. Actual isolated native imports, installed source and loaded math-library
bytes are gated separately before community science.
"""
import argparse
import gzip
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding,write_json


def copy_dependencies(source,destination):
    """Copy complete dependency members; exclude the old product and path injectors."""
    source,destination=Path(source),Path(destination);destination.mkdir(exist_ok=True)
    if any(destination.iterdir()):raise ValueError('Fresh empty dependency site required')
    copied=[];skipped=[]
    for p in sorted(source.iterdir()):
        if p.name in ['dl_binner','__pycache__']or p.name.startswith('dl_binner-')or p.suffix in ['.pth','.pyc']:
            skipped.append(p.name);continue
        target=destination/p.name
        if p.is_dir():shutil.copytree(p,target,symlinks=False,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        elif p.is_file():shutil.copyfile(p,target)
        else:raise ValueError('Unsupported dependency member: '+str(p))
        copied.append(p.name);print('OWNED_DEPENDENCY',p.name,flush=True)
    return dict(copied=copied,excluded=skipped,site_links=False,unused_prefix_recursively_hashed=False)


def create(base,destination,receipt):
    """Create one fresh native lexical venv using only the validated existing recipe."""
    base,destination=Path(base).absolute(),Path(destination).absolute()
    if sys.version_info[:2]!=(3,12)or Path(sys.prefix).absolute()!=base or sys.platform!='linux':
        raise ValueError('Accepted native Linux Python3.12 lexical source prefix required')
    if destination.exists():raise ValueError('Existing environment refused')
    inventory={d.metadata['Name']:d.version for d in importlib.metadata.distributions()}
    subprocess.run([sys.executable,'-I','-B','-m','venv','--without-pip',destination],check=True)
    source=base/'lib/python3.12/site-packages';target=destination/'lib/python3.12/site-packages'
    copied=copy_dependencies(source,target)
    write_json(receipt,dict(base_prefix=str(base),source_inventory=inventory,destination=str(destination),
        copy=copied,scope='Own numerical distribution files; Python base/stdlib retained explicitly; no old project or path-injecting overlay.'))


def probe(lock,inventory,output):
    """Verify every installed scientific/default member and loaded-library aliases."""
    import dl_binner
    lock_path,inventory_path=Path(lock),Path(inventory)
    lock=json.loads(lock_path.read_text());inventory=json.loads(inventory_path.read_text());root=Path(dl_binner.__file__).parent
    if Path(sys.prefix).absolute()!=Path(inventory['prefix']).absolute()or not sys.dont_write_bytecode or not sys.flags.isolated:
        raise ValueError('Isolated lexical runtime differs')
    actual={str(p.relative_to(root)):binding(p)for p in root.rglob('*')if p.is_file()and p.suffix in ['.py','.json']}
    if actual!=lock['source']:raise ValueError('Installed complete dev5 source/defaults differ')
    libraries=[];seen=set()
    for group in inventory['isolated_native_groups'].values():
        for pool in group['pools']:
            alias=Path(pool['filepath']);target=alias.resolve(strict=True)
            if str(alias)in seen:continue
            seen.add(str(alias))
            if not target.is_file():raise ValueError('Loaded math library has no regular target')
            libraries.append(dict(loader_alias=str(alias),resolved_regular=str(target),content=binding(target),
                                  direct_link=os.readlink(alias)if alias.is_symlink()else None))
    write_json(output,dict(status='PASS',version=dl_binner.__version__,source=actual,source_lock=binding(lock_path),
        inventory=binding(inventory_path),complete_distributions=inventory['distributions'],
        loaded_math_libraries=libraries,scope='Actual isolated execution libraries only, with normal OS aliases resolved; no unused prefix recursion.'))


def scheduler(workflow_python,output):
    """Exercise two independently ready four-core rules on the actual local executor."""
    output=Path(output).absolute();output.mkdir(exist_ok=False)
    worker=output/'timestamp.py'
    worker.write_text('"""Tiny scheduler timing fixture; no scientific or numerical work."""\nimport json,sys,time\nfrom pathlib import Path\na=time.time();time.sleep(.3);Path(sys.argv[1]).write_text(json.dumps(dict(start=a,end=time.time())))\n')
    snake=output/'Snakefile'
    command=' '.join(shlex.quote(str(x))for x in [workflow_python,'-I','-B',worker])+' {output:q}'
    snake.write_text('rule all:\n    input: "a.json", "b.json"\n\nrule independent:\n    output: "{name}.json"\n    threads: 4\n    shell: '+repr(command)+'\n')
    argv=[str(workflow_python),'-I','-B','-m','snakemake','--snakefile',str(snake),'--directory',str(output),'--cores','4','--printshellcmds','--benchmark-extended']
    subprocess.run(argv,check=True)
    rows=sorted([json.loads((output/(name+'.json')).read_text())for name in ['a','b']],key=lambda x:x['start'])
    if rows[0]['end']>rows[1]['start']:raise ValueError('Actual local core cap allowed ready-rule overlap')
    write_json(output/'verified.json',dict(status='PASS',argv=argv,observations=rows,
        independent_ready_rules=2,rule_threads=4,cores=4,jobs_argument=False,actual_overlap=False,scientific_work=False))


def restore_input(compressed,manifest,destination):
    """Restore lossless opaque DNA transport bytes once; no source regeneration."""
    compressed,manifest,destination=Path(compressed),Path(manifest),Path(destination)
    expected=json.loads(manifest.read_text())
    if binding(compressed)!={k:expected['compressed'][k]for k in ['bytes','sha256']}:
        raise ValueError('Compressed model-input bytes differ')
    partial=destination.with_suffix(destination.suffix+'.partial')
    if destination.exists()or partial.exists():raise ValueError('Fresh input destination required; no silent restore retry')
    digest=hashlib.sha256();count=0
    with gzip.open(compressed,'rb')as source,partial.open('xb')as out:
        for block in iter(lambda:source.read(1024**2),b''):
            out.write(block);digest.update(block);count+=len(block)
            if count%(64*1024**2)==0:print('OPAQUE_INPUT_RESTORED_BYTES',count,flush=True)
    actual=dict(bytes=count,sha256=digest.hexdigest())
    if actual!={k:expected['restored'][k]for k in ['bytes','sha256']}:raise ValueError('Lossless restored model DNA differs')
    partial.rename(destination)
    write_json(destination.with_suffix(destination.suffix+'.restored.json'),dict(status='PASS',compressed=binding(compressed),restored=actual,
        lossless=True,source_or_truth_join_transferred=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['create','probe','scheduler','restore-input'])
    p.add_argument('--base',type=Path);p.add_argument('--destination',type=Path);p.add_argument('--receipt',type=Path)
    p.add_argument('--lock',type=Path);p.add_argument('--inventory',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--compressed',type=Path);p.add_argument('--manifest',type=Path)
    p.add_argument('--workflow-python',type=Path);a=p.parse_args()
    if a.operation=='create':create(a.base,a.destination,a.receipt)
    elif a.operation=='probe':probe(a.lock,a.inventory,a.output)
    elif a.operation=='scheduler':scheduler(a.workflow_python,a.output)
    else:restore_input(a.compressed,a.manifest,a.destination)
