#!/usr/bin/env python3
"""Restore only E032's cached E031 consumers from one verified private stream.

Every compressed byte, physical member and exact-byte alias is checked. No model,
neighbor, marker, view or depth regeneration exists. Partial staging is retained
without an admission on refusal. Limits match the declared 3/6 GiB producer.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path,PurePosixPath
import os
import shutil
import subprocess
import sys
import tarfile

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e031_stream_return import BoundReader
from e024_coverage import binding

COMPRESSED=3*1024**3
LOGICAL=6*1024**3
UNITS=['E009-noGLM','E009-GLM','oral-noGLM']


def safe(name):
    """Refuse absolute, escaping, duplicate-spelling or nonportable member names."""
    path=PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or str(path)!=name:
        raise ValueError('Unsafe archive member')


def needed(name):
    """Select the actual cached numeric and partition paths consumed by E032."""
    for unit in UNITS:
        pre='work/'+unit+'/'
        if not name.startswith(pre):continue
        tail=name[len(pre):]
        if tail.startswith(('forest/result/','e023/science/result/')):return True
        if tail in ['embed/embeddings.npz','embed/embeddings.json','graph/result/graph.npz','graph/result/graph.json']:
            return True
        if tail.startswith('construct/result/') and tail.rsplit('/',1)[-1] in [
                'root-only-partition.json','pre-partition.json','post-partition.json','completed.json']:
            return True
    return False


def stream_restore(stream,metadata,expected,root,inventory_binding=None,reserve=25*1024**3):
    """Verify the complete stream and close exact aliases before admitting consumers."""
    root=Path(root);root.mkdir(parents=True,exist_ok=False)
    if (int(metadata['size'])!=expected['bytes'] or not 0<expected['bytes']<=COMPRESSED
            or not str(metadata['generation']).isdigit()):
        raise ValueError('Archive size/generation exceeds admitted scope')
    raw=BoundReader(stream,expected['bytes']);seen=set();got={};inv=None;count=0;wanted=set()
    with tarfile.open(fileobj=raw,mode='r|gz') as archive:
        for member in archive:
            safe(member.name)
            if (not member.isfile() or member.name in seen or member.size<0
                or len(seen)>=10000 or count+member.size>LOGICAL
                or not seen and member.name!='inventory.json'):
                raise ValueError('Malformed/oversized physical inventory')
            if member.name=='inventory.json' and member.size>64*1024**2:
                raise ValueError('Oversized inventory')
            seen.add(member.name);source=archive.extractfile(member);h=hashlib.sha256();n=0
            keep=member.name=='inventory.json' or member.name in wanted;target=root/member.name
            handle=None;chunks=[]
            if keep:
                if shutil.disk_usage(root).free-member.size<reserve:raise ValueError('Restore reserve refused')
                target.parent.mkdir(parents=True,exist_ok=True);handle=target.open('xb')
            try:
                for value in iter(lambda:source.read(1024**2),b''):
                    n+=len(value);h.update(value)
                    if handle:handle.write(value)
                    if member.name=='inventory.json':chunks.append(value)
            finally:
                if handle:handle.close()
            count+=n;value=dict(bytes=n,sha256=h.hexdigest());got[member.name]=value
            if n!=member.size:raise ValueError('Truncated member')
            if member.name=='inventory.json':
                if inventory_binding is not None and value!=inventory_binding:raise ValueError('Frozen inventory differs')
                inv=json.loads(b''.join(chunks))
                wanted={n for n in inv['members'] if needed(n)}
                for name,item in inv['aliases'].items():
                    if needed(name):wanted.add(item['canonical'])
            elif inv['members'].get(member.name)!=value:raise ValueError('Archive member differs: '+member.name)
    for _ in iter(lambda:raw.read(1024**2),b''):pass
    if dict(bytes=raw.count,sha256=raw.sha.hexdigest())!=expected:
        raise ValueError('Whole archive SHA256 differs')
    if metadata.get('md5_hash') and base64.b64encode(raw.md5.digest()).decode()!=metadata['md5_hash']:
        raise ValueError('Object MD5 differs')
    if seen!=set(inv['members'])|{'inventory.json'}:raise ValueError('Incomplete physical members')
    if inv['omitted_retained_on_disk']:raise ValueError('Accepted E031 archive must have no omitted work')
    all_work=inv['all_work_members'];physical={n.removeprefix('work/'):v for n,v in inv['members'].items() if n.startswith('work/')}
    aliases=inv['aliases']
    if set(physical)&set(n.removeprefix('work/') for n in aliases) or set(all_work)!=set(physical)|set(n.removeprefix('work/') for n in aliases):
        raise ValueError('Work inventory does not close')
    if any(all_work[n]!=v for n,v in physical.items()):raise ValueError('Work bindings differ')
    for name,item in aliases.items():
        safe(name);safe(item['canonical']);value={k:item[k] for k in ['bytes','sha256']}
        if (name in inv['members'] or inv['members'].get(item['canonical'])!=value
            or all_work.get(name.removeprefix('work/'))!=value):raise ValueError('Exact alias differs')
        if needed(name):
            target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
            os.link(root/item['canonical'],target)
    restored={str(p.relative_to(root)):binding(p)
              for p in root.rglob('*') if p.is_file()}
    proof=dict(status='PASS',archive=expected,generation=str(metadata['generation']),
        every_member_verified=True,physical_members=len(seen),aliases=len(aliases),
        logical_bytes=count,restored_bytes=sum(v['bytes'] for v in restored.values()),
        restored_members=restored,omitted_work_members=0,no_science_replayed=True,
        stream_not_retained_as_duplicate_archive=True)
    (root/'work').mkdir(exist_ok=True)
    with(root/'work/restore-admission.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
    return proof


def verify_restored(root,output):
    """Verify all restored source bytes again without touching original data DAGs."""
    root=Path(root);proof=json.loads((root/'work/restore-admission.json').read_text())
    for n,wanted in proof['restored_members'].items():
        if binding(root/n)!=wanted:raise ValueError('Restored retained input mutated: '+n)
    with Path(output).open('x') as f:json.dump(dict(status='PASS',files=len(proof['restored_members']),
        original_archive=proof['archive'],all_restored_members_unchanged=True),f,indent=2);f.write('\n')


def download(lock,root,gcloud):
    """Consume exactly the immutable admitted generation, without formatted cat output."""
    value=json.loads(Path(lock).read_text());archive=value['archive'];metadata=value['metadata']
    stderr=Path(str(root)+'.download.stderr')
    with stderr.open('xb') as log:
        p=subprocess.Popen([str(gcloud),'storage','cat',archive['uri']+'#'+metadata['generation']],stdout=subprocess.PIPE,stderr=log)
        try:
            proof=stream_restore(p.stdout,metadata,archive['binding'],root,value['inventory'],reserve=value['reserve_bytes'])
            if p.wait(timeout=30):raise RuntimeError('Raw generation stream failed')
        except BaseException:
            p.terminate();p.wait(timeout=30);raise
    return proof


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock',type=Path);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--gcloud',type=Path);p.add_argument('--verify-after',type=Path)
    a=p.parse_args()
    if a.verify_after:verify_restored(a.root,a.verify_after)
    else:download(a.lock,a.root,a.gcloud)
