#!/usr/bin/env python3
"""Review/release only obsolete compiled Numba cache bytes before task storage.

Never removes scientific arrays, views, graphs, weights, BAMs, source, runtime
distributions or accepted logs. Exact removed identities are retained. No cloud
operation exists; a temporary 40 GiB decision follows measured remaining space.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def review(output):
    """Hash and remove only regular .nbc/.nbi in old explicit native-cache dirs."""
    source=Path('/srv/dl_binner');experiments=source/'experiments'
    if not os.path.ismount(source):raise ValueError('Original source mount required')
    before=shutil.disk_usage(source);directories=[];removed=[];refused=[]
    # Current cost-bearing start was from a stopped VM. Refuse cleanup if another
    # project numerical worker is unexpectedly present after boot.
    active=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name)==os.getpid():continue
        try:cmd=(p/'cmdline').read_bytes().replace(b'\0',b' ')
        except (OSError,PermissionError):continue
        if b'/srv/dl_binner/' in cmd and (b'python' in cmd or b'snakemake' in cmd):active.append(int(p.name))
    found=subprocess.check_output(['find',str(experiments),'-xdev','-type','d','-name','native-cache','-prune'],text=True)
    for name in found.splitlines():
        directory=Path(name)
        if directory.is_symlink() or not directory.is_relative_to(experiments):raise ValueError('Unexpected cache directory')
        entries=[p for p in directory.rglob('*') if p.is_file() and not p.is_symlink() and p.suffix in ['.nbc','.nbi']]
        directories.append(dict(path=name,compiled_files=len(entries),bytes=sum(p.stat().st_size for p in entries)))
        for p in entries:
            if active or shutil.disk_usage(source).free>=37*1024**3:continue
            wanted=binding(p)
            try:p.unlink()
            except OSError as e:refused.append(dict(path=str(p),error=repr(e)));continue
            removed.append(dict(path=str(p),binding=wanted,regenerable='Numba compilation from preserved pinned source/runtime',
                no_scientific_or_source_evidence_removed=True))
    after=shutil.disk_usage(source)
    value=dict(status='REVIEWED',before=before._asdict(),after=after._asdict(),directories=directories,
        removed=removed,refused=refused,unexpected_project_worker_PIDs=active,
        all_scientific_and_required_runtime_inputs_preserved=True)
    write(output,value);print('E032_HEADROOM',json.dumps(after._asdict()),flush=True)
    return value


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();review(a.output)
