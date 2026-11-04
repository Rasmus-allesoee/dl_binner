#!/usr/bin/env python3
"""Prospective complete split collections, strict exact aliases and byte caps.

Measurements are one collection; each learning mode is a separate complete
collection, avoiding repeated scientific payloads and oversized fallback returns.
Accepted inputs/environments and temporary sorted BAMs are external prerequisites.
"""
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sys
import tarfile

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e024_coverage import binding,write
from e023_collect import CappedWriter
import e031_collect as reader

CAP=3*1024**3;LOGICAL=8*1024**3


@contextmanager
def bounds():
    """Give the unchanged verifier this prospective collection's exact bounds."""
    old=reader.CAP,reader.LOGICAL_CAP;reader.CAP,reader.LOGICAL_CAP=CAP,LOGICAL
    try:yield
    finally:reader.CAP,reader.LOGICAL_CAP=old


def verify(archive,expected=None):
    """Require every physical byte and declared exact alias; no omission fallback."""
    with bounds():return reader.verify(archive,expected)


def pack(work,evidence,output):
    """Archive every new member in this closed slice, refusing links/unsafe overlap."""
    work,evidence,out=map(lambda x:Path(x).absolute(),[work,evidence,output])
    if out==work or work in out.parents or evidence in out.parents:
        raise ValueError('Collection must be outside source directories')
    out.mkdir(parents=True,exist_ok=False);physical={};members={};aliases={};seen={};all_work={}
    for root,prefix in [(work,'work'),(evidence,'evidence')]:
        for p in sorted(root.rglob('*')):
            if p.is_symlink():raise ValueError('Collection artifact symlink refused')
            if not p.is_file():continue
            name=prefix+'/'+str(p.relative_to(root));b=binding(p);key=(b['bytes'],b['sha256'])
            if prefix=='work':all_work[name.removeprefix('work/')]=b
            if prefix=='work' and key in seen:aliases[name]=dict(b,canonical=seen[key])
            else:physical[name]=p;members[name]=b;seen.setdefault(key,name)
    if len(members)>30000 or sum(v['bytes'] for v in members.values())>LOGICAL:
        raise ValueError('Collection member/logical cap exceeded; no fallback')
    inventory=dict(kind='E033 complete closed slice',members=members,aliases=aliases,
        all_work_members=all_work,omitted_retained_on_disk={},compressed_hard_ceiling_bytes=CAP,logical_cap_bytes=LOGICAL)
    write(out/'inventory.json',inventory)
    if (out/'inventory.json').stat().st_size>64*1024**2 or sum(v['bytes'] for v in members.values())+(out/'inventory.json').stat().st_size>LOGICAL:
        raise ValueError('Manifest-inclusive logical cap exceeded')
    archive=out/'e033-evidence.tar.gz'
    with archive.open('xb') as raw:
        # Each physical inventory member must stay regular even when the local
        # staging tree contains exact hardlinks. Aliases are explicit JSON only.
        with tarfile.open(fileobj=CappedWriter(raw,CAP),mode='w:gz',dereference=True) as target:
            target.add(out/'inventory.json',arcname='inventory.json',recursive=False)
            for n,p in physical.items():target.add(p,arcname=n,recursive=False)
    proof=verify(archive,binding(archive));write(out/'collection.json',proof)
    (out/'e033-evidence.tar.gz.sha256').write_text(proof['archive']['sha256']+'  e033-evidence.tar.gz\n')
    return proof


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['work','evidence','output']:p.add_argument('--'+n,required=True,type=Path)
    a=p.parse_args();pack(a.work,a.evidence,a.output)
