#!/usr/bin/env python3
"""Seal only new E017 results with a full inventory and exact-byte aliases.

Shared accepted inputs are reused in place and named in byte-bound reuse receipts,
not duplicated into each return. New core/recruitment graphs and decisions,
pre/old/post partitions, decision alternatives and complete assignment tables are
retained. Full final exported FASTAs remain on disk with all-member hashes. This is not
a backup of omitted DNA/view banks. Every physical return member is read back.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tarfile
import time

# Isolated Python removes the script directory from sys.path. Admit only the
# adjacent, source-bound helper directory; never inherit PYTHONPATH/user site.
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_collect import binding,member_path

CAP=3*1024**3


def select(work):
    """Inventory every new work member; exclude only full DNA and exact duplicates."""
    work=Path(work);all_files={};files={};aliases={};omitted={}
    for p in sorted(work.rglob('*')):
        if p.is_symlink():raise ValueError('Scientific result link refused')
        if not p.is_file():continue
        k=str(p.relative_to(work));b=binding(p);all_files[k]=b
        if k.startswith('.snakemake/') or p.suffix in ['.json','.tsv','.log','.jsonl'] or p.suffix == '.npz':
            files['work/'+k]=p
        elif p.suffix in ['.fa','.fna','.fasta']:
            omitted[k]=b
        else:raise ValueError('Unexpected unaccounted result member: '+k)
    for k in list(files):
        if k.endswith('/train/reference.npz'):
            canonical=k.removesuffix('/train/reference.npz')+'/embeddings.npz'
            if canonical not in files or binding(files[k])!=binding(files[canonical]):
                raise ValueError('Reference/embedding alias is not exact bytes')
            aliases[k]=dict(canonical=canonical,**binding(files[k]));del files[k]
    return files,all_files,aliases,omitted


def verify(archive,expected_archive=None,output=None):
    """Stream every regular member and alias; optionally retain verified small inventory."""
    archive=Path(archive)
    if archive.stat().st_size>CAP or (expected_archive and binding(archive)!=expected_archive):raise ValueError('Return archive bytes/cap differ')
    seen=set();inventory=None;logical=0
    with tarfile.open(archive,'r:gz') as a:
        for m in a:
            member_path(Path('/verification-only'),m.name)
            if not m.isfile() or m.name in seen:raise ValueError('Duplicate/nonregular archive member')
            if not seen and m.name!='inventory.json':raise ValueError('Manifest must be first')
            seen.add(m.name);f=a.extractfile(m);sha=hashlib.sha256();n=0;chunks=[]
            for b in iter(lambda:f.read(1024**2),b''):
                sha.update(b);n+=len(b)
                if m.name=='inventory.json':chunks.append(b)
            logical+=n
            if m.name=='inventory.json':inventory=json.loads(b''.join(chunks))
            elif inventory['members'].get(m.name)!=dict(bytes=n,sha256=sha.hexdigest()):raise ValueError('Return member bytes differ')
    if seen!=set(inventory['members'])|{'inventory.json'}:raise ValueError('Return member inventory incomplete')
    for k,r in inventory['aliases'].items():
        b={x:r[x] for x in ['bytes','sha256']}
        if k in inventory['members'] or inventory['members'].get(r['canonical'])!=b or inventory['all_work_members'].get(k.removeprefix('work/'))!=b:
            raise ValueError('Invalid byte-identical alias')
    retained={k.removeprefix('work/') for k in inventory['members'] if k.startswith('work/')}
    aliases={k.removeprefix('work/') for k in inventory['aliases']}
    if set(inventory['all_work_members'])!=retained|aliases|set(inventory['omitted_DNA_retained_on_disk']):raise ValueError('Full work accounting differs')
    for k in retained:
        if inventory['members']['work/'+k]!=inventory['all_work_members'][k]:raise ValueError('Work inventory binding differs')
    result=dict(status='SUCCESS',archive=binding(archive),regular_members=len(seen),logical_member_bytes=logical,every_member_verified=True)
    if output:
        output=Path(output);output.mkdir(exist_ok=False)
        (output/'inventory.json').write_text(json.dumps(inventory,indent=2,sort_keys=True)+'\n')
        (output/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def pack(work,evidence,output,ceiling=CAP):
    """Write a fresh return, preflight logical bytes and enforce its compressed cap."""
    work,evidence,output=map(Path,[work,evidence,output]);output.mkdir(exist_ok=False)
    files,all_files,aliases,omitted=select(work)
    for p in sorted(evidence.rglob('*')):
        if p.is_symlink():raise ValueError('Evidence link refused')
        if p.is_file():files['evidence/'+str(p.relative_to(evidence))]=p
    members={k:binding(p) for k,p in files.items()}
    logical=sum(r['bytes'] for r in members.values())
    # gzip DEFLATE's pessimistic expansion plus tar headers: reject an impossible
    # return before writing any large archive. No estimated compression rescue.
    upper=logical+logical//1000+2048*len(members)+1024**2
    if upper>ceiling:raise ValueError('Prospective logical return bound exceeds compressed cap')
    inv=dict(kind='E017 exact-byte new-result return',members=members,all_work_members=all_files,
             aliases=aliases,omitted_DNA_retained_on_disk=omitted,
             shared_inputs='Original retained E014/E011 files; locked locators in evidence, not backed up by this archive',
             prospective_worst_case_archive_bytes=upper)
    manifest_size=len(json.dumps(inv,sort_keys=True,indent=2).encode())+128
    upper+=manifest_size+manifest_size//1000+2048
    if upper>ceiling:raise ValueError('Prospective manifest-inclusive return bound exceeds compressed cap')
    inv['prospective_worst_case_archive_bytes']=upper
    manifest=output/'inventory.json';manifest.write_text(json.dumps(inv,sort_keys=True,indent=2)+'\n')
    archive=output/'e017-evidence.tar.gz'
    with tarfile.open(archive,'x:gz') as a:
        a.add(manifest,arcname='inventory.json',recursive=False)
        for k,p in sorted(files.items()):
            a.add(p,arcname=k,recursive=False)
            if archive.stat().st_size>ceiling:raise ValueError('Compressed return cap exceeded')
    if archive.stat().st_size>ceiling:raise ValueError('Compressed return cap exceeded')
    r=verify(archive);r.update(aliases=aliases,prospective_worst_case_archive_bytes=upper,planned_science_fits=0)
    (output/'collection.json').write_text(json.dumps(r,indent=2)+'\n')
    (output/'e017-evidence.tar.gz.sha256').write_text(r['archive']['sha256']+'  e017-evidence.tar.gz\n')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--work',type=Path);p.add_argument('--evidence',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--verify',type=Path);a=p.parse_args()
    print(json.dumps(verify(a.verify,output=a.output) if a.verify else pack(a.work,a.evidence,a.output)),flush=True)
