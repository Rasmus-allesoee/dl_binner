#!/usr/bin/env python3
"""Recover sealed E014 outputs without fitting, rewriting or regenerating science.

The failed first collector already inventoried every work member. Verify that
inventory against retained bytes, omit only full graph binaries from this smaller
return, and include separately verified graph-reader receipts. Full graph/view/
DNA files remain untouched on the existing disk. This helper cannot start a VM.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import time


def binding(path):
    """Stream a regular file into its exact byte count and SHA256."""
    path=Path(path)
    if path.is_symlink() or not path.is_file():raise ValueError('Regular evidence file required: '+str(path))
    h=hashlib.sha256();n=0
    with path.open('rb')as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b);n+=len(b)
    return dict(bytes=n,sha256=h.hexdigest())


def member_path(root,key):
    """Refuse traversal and any scientific parent/file link in a retained locator."""
    rel=Path(key)
    if rel.is_absolute()or '..'in rel.parts or not rel.parts:raise ValueError('Unsafe retained member')
    p=Path(root)
    for part in rel.parts:
        p=p/part
        if p.is_symlink():raise ValueError('Retained scientific link refused')
    return p


def verify_work(work,inventory):
    """Independently verify every original work member, including omitted bulk DNA."""
    expected=json.loads(Path(inventory).read_text())['all_result_members'];checked=0;total=0;last=time.monotonic()
    for key,value in expected.items():
        p=member_path(work,key)
        if binding(p)!=value:raise ValueError('Original retained bytes differ: '+key)
        checked+=1;total+=value['bytes']
        if time.monotonic()-last>=5:
            print('RETAINED_MEMBER_BYTES_VERIFIED',checked,total,flush=True);last=time.monotonic()
    actual={str(p.relative_to(work))for p in Path(work).rglob('*')if p.is_file()}
    if actual!=set(expected):raise ValueError('Original work inventory member set differs')
    return dict(members=checked,bytes=total,every_original_work_member_verified=True)


def selection(work,inventory):
    """Keep the original retained set except full graph NPZs, never alter their bytes."""
    record=json.loads(Path(inventory).read_text());files={};omitted=[]
    for key in record['retained']:
        if key in {'units/'+u+'/group/graph.npz'for u in ['E009-dev5','oral-dev4','oral-dev5']}:
            omitted.append(dict(path=key,**record['all_result_members'][key]));continue
        files['work/'+key]=member_path(work,key)
    return files,omitted


def pack(work,inventory,phase,proofs,output,ceiling=2*1024**3):
    """Seal the reduced return and independently read back every member under its cap."""
    work,inventory,phase,proofs,output=map(Path,[work,inventory,phase,proofs,output])
    output.mkdir(exist_ok=False);checked=verify_work(work,inventory);files,omitted=selection(work,inventory)
    graph_proofs=sorted(proofs.glob('graph-*.json'))
    if omitted and len(graph_proofs)!=3:raise ValueError('Three native retained-graph proof receipts required')
    proof_units=set()
    for p in graph_proofs:
        r=json.loads(p.read_text())
        expected=next((x for x in omitted if x['path']=='units/'+r['unit']+'/group/graph.npz'),None)
        if r['status']!='PASS' or expected is None or r['graph']!={k:expected[k]for k in ['bytes','sha256']}:
            raise ValueError('Native graph receipt does not bind an omitted original')
        proof_units.add(r['unit'])
    if omitted and proof_units!={'E009-dev5','oral-dev4','oral-dev5'}:raise ValueError('Distinct native graph proof units required')
    for p in sorted(proofs.rglob('*')):
        if p.is_symlink():raise ValueError('Recovery proof link refused')
        if p.is_file():files['proofs/'+str(p.relative_to(proofs))]=p
    for name in ['phase-config.json','science-plan.json','host.json','started.json','release.json','bootstrap-result.json','completion.json']:
        p=phase/name
        if p.is_file():files['phase/'+name]=p
    for p in sorted((phase/'logs').iterdir()):
        if p.is_file():files['phase/logs/'+p.name]=p
    files['original-inventory.json']=inventory
    expected={key:binding(p)for key,p in files.items()}
    record=dict(source='Retained E014 science source858b7cc; collection only',all_original_work=checked,
                omitted_graphs_retained_on_disk=omitted,full_science_inventory=binding(inventory),members=expected)
    manifest=output/'inventory.json';manifest.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    archive=output/'e014-review.tar.gz'
    with tarfile.open(archive,'x:gz')as a:
        a.add(manifest,arcname='inventory.json',recursive=False)
        for key,p in sorted(files.items()):
            a.add(p,arcname=key,recursive=False)
            if archive.stat().st_size>ceiling:raise ValueError('Reduced compressed export cap exceeded')
    if archive.stat().st_size>ceiling:raise ValueError('Reduced compressed export cap exceeded')
    seen=set()
    with tarfile.open(archive,'r:gz')as a:
        for m in a:
            if not m.isfile()or m.name in seen:raise ValueError('Nonregular/duplicate return member')
            seen.add(m.name)
            if m.name=='inventory.json':continue
            f=a.extractfile(m);h=hashlib.sha256();n=0
            for b in iter(lambda:f.read(1024**2),b''):h.update(b);n+=len(b)
            if dict(bytes=n,sha256=h.hexdigest())!=expected[m.name]:raise ValueError('Reduced archive member differs')
    if seen!=set(expected)|{'inventory.json'}:raise ValueError('Reduced archive incomplete')
    receipt=dict(status='SUCCESS',archive=binding(archive),regular_members=len(seen),
                 logical_member_bytes=sum(v['bytes']for v in expected.values())+manifest.stat().st_size,
                 all_original_work=checked,every_return_member_verified=True,omitted_graphs=omitted,
                 science_repeated=False,original_files_modified=False)
    (output/'collection.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (output/'e014-review.tar.gz.sha256').write_text(receipt['archive']['sha256']+'  e014-review.tar.gz\n')
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['work','inventory','phase','proofs','output']:p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();print(json.dumps(pack(a.work,a.inventory,a.phase,a.proofs,a.output)),flush=True)
