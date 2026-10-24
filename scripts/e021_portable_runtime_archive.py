#!/usr/bin/env python3
"""Preserve one owned native prefix before retiring the temporary E021 worker.

The result is an inert provenance/runtime payload, not a portable or admitted
environment on its destination host. No dependency is installed or executed.
Every regular file and internal symlink is inventoried and independently reread
from the archive. Credentials and other directories are outside the selection.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tarfile


def binding(path):
    """Stream a regular file's exact byte identity without following aliases."""
    p=Path(path)
    if p.is_symlink() or not p.is_file():
        raise ValueError('Regular file required')
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return dict(bytes=p.stat().st_size,sha256=h.hexdigest())


def inventory(prefix):
    """Inventory all actual prefix bytes and only aliases resolving inside it."""
    prefix=Path(prefix).resolve(strict=True);members={};total=0
    for p in sorted(prefix.rglob('*')):
        rel=str(p.relative_to(prefix))
        if p.is_symlink():
            if not p.resolve(strict=True).is_relative_to(prefix):
                raise ValueError('Runtime alias escapes owned prefix: '+rel)
            members[rel]=dict(kind='symlink',target=os.readlink(p))
        elif p.is_file():
            b=binding(p);total+=b['bytes'];members[rel]=dict(kind='file',**b)
        elif not p.is_dir():
            raise ValueError('Unsupported runtime member: '+rel)
    if total>8*1024**3:raise ValueError('Runtime logical cap exceeded')
    return members,total


def verify(path,expected):
    """Check every physical archive member, with no extraction or alias execution."""
    seen=set()
    with tarfile.open(path,'r:gz') as a:
        for m in a:
            p=Path(m.name)
            if (p.is_absolute() or '..'in p.parts or m.name in seen
                    or m.name not in expected):raise ValueError('Unexpected runtime archive member')
            seen.add(m.name);b=expected[m.name]
            if b['kind']=='symlink':
                if not m.issym() or m.linkname!=b['target']:
                    raise ValueError('Runtime symlink identity differs')
            else:
                if not m.isfile() or m.size!=b['bytes']:
                    raise ValueError('Runtime regular member differs')
                h=hashlib.sha256()
                with a.extractfile(m) as f:
                    for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
                if h.hexdigest()!=b['sha256']:raise ValueError('Runtime member checksum differs')
    if seen!=set(expected):raise ValueError('Runtime archive is incomplete')
    return True


def pack(prefix,output):
    """Write a fresh capped archive, verify it and refuse changed original bytes."""
    prefix=Path(prefix).resolve(strict=True);out=Path(output);out.mkdir(exist_ok=False)
    members,total=inventory(prefix);archive=out/'native-runtime.tar.gz'
    # addfile avoids implicit tar hard-link deduplication; explicit aliases survive.
    class Capped:
        def __init__(self,raw):self.raw=raw;self.count=0
        def write(self,b):
            if self.count+len(b)>4*1024**3:raise ValueError('Runtime compressed cap exceeded')
            n=self.raw.write(b);self.count+=n;return n
        def __getattr__(self,key):return getattr(self.raw,key)
    with archive.open('xb')as raw:
        with tarfile.open(fileobj=Capped(raw),mode='w:gz',compresslevel=1) as a:
            for rel,b in members.items():
                a.inodes.clear()
                p=prefix/rel;t=a.gettarinfo(str(p),arcname=rel)
                if b['kind']=='file':
                    with p.open('rb') as f:a.addfile(t,f)
                else:a.addfile(t)
    verify(archive,members)
    if inventory(prefix)!=(members,total):raise ValueError('Original runtime changed during preservation')
    result=dict(status='PASS_EVERY_RUNTIME_MEMBER',source_prefix=str(prefix),
        archive=binding(archive),logical_regular_bytes=total,members=members,
        destination_execution_admitted=False,
        scope='Inert byte preservation; no promise of relocation or compatible destination GPU')
    (out/'runtime-preservation.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prefix',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=pack(a.prefix,a.output)
    print('RUNTIME_PRESERVATION_PASS',r['archive'],len(r['members']),flush=True)
