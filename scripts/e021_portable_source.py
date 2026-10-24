#!/usr/bin/env python3
"""Pack a clean shallow source checkout without macOS AppleDouble metadata.

Uses Python's regular GNU tar writer instead of a platform tar utility. Rejects
links, AppleDouble files and an unclean source; no credentials or Git history
outside the supplied shallow clone can enter the native source packet.
"""
import argparse,hashlib,json,subprocess,tarfile
from pathlib import Path


def pack(source,output):
    """Write one new archive and inventory from actual clean shallow source bytes."""
    source=Path(source);out=Path(output)
    if out.exists()or subprocess.check_output(['git','status','--porcelain'],cwd=source,text=True).strip():raise ValueError('Fresh packet and clean source required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()
    if subprocess.check_output(['git','rev-parse','--is-shallow-repository'],cwd=source,text=True).strip()!='true':raise ValueError('Shallow source required')
    files={}
    with tarfile.open(out,'w:gz',format=tarfile.GNU_FORMAT)as a:
        for p in sorted(source.rglob('*')):
            rel=str(p.relative_to(source))
            if p.is_symlink()or any(x.startswith('._')for x in Path(rel).parts):raise ValueError('Link/AppleDouble source member refused')
            if p.is_dir():continue
            if not p.is_file():raise ValueError('Regular source members only')
            data=p.read_bytes();files[rel]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest());a.add(p,arcname=rel,recursive=False)
    return dict(source=head,archive=dict(bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest()),members=files)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();a.receipt.write_text(json.dumps(pack(a.source,a.output),indent=2)+'\n')
