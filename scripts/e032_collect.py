#!/usr/bin/env python3
"""Package complete E032 outputs and closed controls with exact-byte aliases.

The 3 GiB compressed / 6 GiB logical producer and verifier agree. No science,
credentials, runtime or original data are copied into this result backup.
"""
import argparse
import json
from pathlib import Path
import sys
import tarfile

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e024_coverage import binding,write
from e023_collect import CappedWriter
from e031_paired_collect import verify

CAP=3*1024**3
LOGICAL=6*1024**3


def pack(work,evidence,output):
    """Refuse unclosed/incomplete inventories; verify all physical members/aliases."""
    work,evidence,out=map(Path,[work,evidence,output])
    if out==work or work in out.parents:raise ValueError('Separate bounded return required')
    out.mkdir(parents=True,exist_ok=False);files={};all_work={};aliases={};seen={}
    for root,prefix in [(work,'work'),(evidence,'evidence')]:
        for p in sorted(root.rglob('*')):
            if p.is_symlink():raise ValueError('Result artifact links refused')
            if not p.is_file():continue
            relative=str(p.relative_to(root));name=prefix+'/'+relative;value=binding(p)
            if prefix=='work':all_work[relative]=value
            key=(value['bytes'],value['sha256'])
            if prefix=='work' and key in seen:aliases[name]=dict(value,canonical=seen[key])
            else:files[name]=p;seen.setdefault(key,name)
    members={name:binding(p) for name,p in files.items()}
    if sum(v['bytes'] for v in members.values())>LOGICAL or len(members)>20000:
        raise ValueError('Logical/member cap refused, no fallback')
    inventory=dict(kind='E032 complete candidate-selection evidence',members=members,
        all_work_members=all_work,aliases=aliases,omitted_retained_on_disk={},
        compressed_hard_ceiling_bytes=CAP,logical_cap_bytes=LOGICAL,
        original_science_external_and_privately_archived=True)
    write(out/'inventory.json',inventory)
    if (out/'inventory.json').stat().st_size>64*1024**2 or sum(v['bytes'] for v in members.values())+(out/'inventory.json').stat().st_size>LOGICAL:
        raise ValueError('Manifest-inclusive cap refused')
    path=out/'e032-evidence.tar.gz'
    with path.open('xb') as raw:
        with tarfile.open(fileobj=CappedWriter(raw,CAP),mode='w:gz') as archive:
            archive.add(out/'inventory.json',arcname='inventory.json',recursive=False)
            for name,p in sorted(files.items()):archive.add(p,arcname=name,recursive=False)
    proof=verify(path,binding(path));write(out/'collection.json',proof)
    (out/'e032-evidence.tar.gz.sha256').write_text(proof['archive']['sha256']+'  e032-evidence.tar.gz\n')
    return proof


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['work','evidence','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();pack(a.work,a.evidence,a.output)
