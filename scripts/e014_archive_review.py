#!/usr/bin/env python3
"""Stream-verify the compact E014 return and stage only bounded local review copies.

No source artifact is altered. All physical members and every lossless alias are
verified before any diagnostic consumes them. Omitted graph/bulk DNA evidence
remains explicitly native, bound by the independently checked original inventory.
"""
import hashlib
import json
from pathlib import Path
import tarfile
import time

from e014_collect import binding,member_path


def verify_archive(archive,collection,output,select=None):
    """Verify archive and each regular member; optionally stage selected exact bytes."""
    archive,output=Path(archive),Path(output);receipt=json.loads(Path(collection).read_text())
    if receipt['status']!='SUCCESS' or not receipt['every_return_member_verified'] or receipt['science_repeated']:
        raise ValueError('No successful evidence-only collection receipt')
    if archive.stat().st_size>2*1024**3 or binding(archive)!=receipt['archive']:raise ValueError('Archive bytes/cap differ')
    output.mkdir(exist_ok=False);seen=set();total=0;start=time.monotonic();inventory=None;original=None;last=time.monotonic()
    with tarfile.open(archive,'r:gz')as a:
        for m in a:
            member_path(output,m.name)
            if not m.isfile() or m.name in seen:raise ValueError('Duplicate/nonregular archive member')
            if inventory is None and m.name!='inventory.json':raise ValueError('Archive must start with manifest')
            seen.add(m.name);stream=a.extractfile(m);sha=hashlib.sha256();n=0
            keep=m.name in ['inventory.json','original-inventory.json']or m.name.startswith('proofs/')or bool(select and select(m.name,m.size))
            path=member_path(output,m.name)
            if keep:path.parent.mkdir(parents=True,exist_ok=True)
            target=path.open('xb')if keep else None
            try:
                for b in iter(lambda:stream.read(1024**2),b''):
                    sha.update(b);n+=len(b)
                    if target:target.write(b)
            finally:
                if target:target.close()
            value=dict(bytes=n,sha256=sha.hexdigest());total+=n
            if m.name=='inventory.json':inventory=json.loads(path.read_text())
            elif m.name not in inventory['members'] or inventory['members'][m.name]!=value:raise ValueError('Archive member bytes differ: '+m.name)
            if m.name=='original-inventory.json':original=json.loads(path.read_text())
            if time.monotonic()-last>10:
                print('E014_ARCHIVE_MEMBERS_VERIFIED',len(seen),total,flush=True);last=time.monotonic()
    if seen!=set(inventory['members'])|{'inventory.json'}or len(seen)!=receipt['regular_members']:raise ValueError('Incomplete archive member set')
    if binding(output/'original-inventory.json')!=inventory['full_science_inventory']:raise ValueError('Original science inventory differs')
    retained=set(original['retained']);work={k.removeprefix('work/')for k in inventory['members']if k.startswith('work/')}
    omitted={r['path']for r in inventory['omitted_graphs_retained_on_disk']};aliases=inventory.get('identical_duplicate_members',{})
    if retained!=work|omitted|{k.removeprefix('work/')for k in aliases}:raise ValueError('Original return selection not fully accounted')
    for key in work:
        if inventory['members']['work/'+key]!=original['all_result_members'][key]:raise ValueError('Work member differs from original inventory')
    for key,r in aliases.items():
        expected={k:r[k]for k in ['bytes','sha256']};canonical=r['canonical']
        if key in inventory['members']or canonical not in inventory['members']or inventory['members'][canonical]!=expected or original['all_result_members'][key.removeprefix('work/')]!=expected:
            raise ValueError('Nonidentical/unknown lossless alias')
    for row in inventory['omitted_graphs_retained_on_disk']:
        unit=row['path'].split('/')[1];proof=json.loads((output/'proofs'/('graph-'+unit+'.json')).read_text())
        if proof['status']!='PASS'or proof['graph']!={k:row[k]for k in ['bytes','sha256']}or proof['graph']!=original['all_result_members'][row['path']]:raise ValueError('Native omitted-graph proof differs')
    result=dict(status='SUCCESS',archive=receipt['archive'],members=len(seen),uncompressed_member_bytes=total,
        every_archive_member_verified=True,lossless_aliases=aliases,omitted_graphs=inventory['omitted_graphs_retained_on_disk'],
        original_work=inventory['all_original_work'],seconds=time.monotonic()-start,
        local_scope='All return members streamed; graphs and omitted bulk DNA were independently verified in place on native VM. No local reread of omitted DNA.')
    (output/'verification.json').write_text(json.dumps(result,indent=2)+'\n');return result


def extract_selected(archive,verified,output,select,ceiling=4*1024**3,budget_root=None):
    """Recreate scratch copies under the total review-footprint cap, rechecking bytes."""
    archive,verified,output=map(Path,[archive,verified,output]);inventory=json.loads((verified/'inventory.json').read_text())
    budget_root=Path(budget_root or archive.parent)
    proof=json.loads((verified/'verification.json').read_text())
    if proof['status']!='SUCCESS' or binding(archive)!=proof['archive']:raise ValueError('Verified archive changed')
    written=[]
    def used():return sum(p.stat().st_size for p in budget_root.rglob('*')if p.is_file())
    with tarfile.open(archive,'r:gz')as a:
        for m in a:
            if not select(m.name,m.size):continue
            if not m.isfile()or m.name not in inventory['members']:raise ValueError('Unknown/nonregular selected member')
            p=member_path(output,m.name);p.parent.mkdir(parents=True,exist_ok=True)
            if p.exists():
                if binding(p)!=inventory['members'][m.name]:raise ValueError('Existing review copy differs')
                continue
            if used()+m.size>ceiling:raise ValueError('Additional local review storage cap would be exceeded')
            stream=a.extractfile(m)
            with p.open('xb')as f:
                for b in iter(lambda:stream.read(1024**2),b''):
                    f.write(b)
            if binding(p)!=inventory['members'][m.name]:raise ValueError('Selected member bytes differ')
            written.append(m.name)
    return written
