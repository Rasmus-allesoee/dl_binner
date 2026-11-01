#!/usr/bin/env python3
"""Stage one admitted E029 community from its fixed private GCS generation.

Streams and rechecks the complete archive/member inventory on each pass. Restores
only the selected results and full assignment exports, with exact aliases. No
compressed local duplicate, native execution, scientific reconstruction or retry.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import urllib.parse
import urllib.request

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e026_stage_review import BoundReader,inventory_relations
from e014_collect import member_path
from e024_coverage import binding,write
from e022_review import admission_contract
from e021_portable_cloud import Cloud


def stage(base, community, output, role=None, verified_reuse=False):
    """Refuse stale admission, malformed members, low headroom or alias drift."""
    base=Path(base);out=Path(output);admission_contract(base/'admission.json')
    inv=json.loads((base/'inventory.json').read_text())
    if community not in ['E009','oral'] or inv['kind']!='E029 exact-byte discovery repair return':
        raise ValueError('Unexpected review scope/archive')
    units=['E009-noGLM','E009-GLM'] if community=='E009' else ['oral-noGLM']
    names=set(inv['members'])|set(inv['aliases'])
    if role not in [None,'teacher','student']:raise ValueError('Invalid explicit actor')
    chosen={n for n in names if any(n.startswith('work/groups/'+u+'/'+(role+'/'if role else''))
            or n.startswith('work/'+u+'/export/'+(role+'-'if role else''))for u in units)
            and not n.endswith('/alternatives.json')}
    aliases={n:inv['aliases'][n]for n in chosen if n in inv['aliases']}
    selected={n for n in chosen if n in inv['members']}|{a['canonical']for a in aliases.values()}
    count=sum(inv['members'][n]['bytes']for n in selected);reused={}
    if out.exists():
        if not verified_reuse:raise ValueError('Existing stage requires explicit verified reuse')
        for n in selected:
            p=member_path(out,n)
            if p.exists():
                if p.is_symlink()or binding(p)!=inv['members'][n]:raise ValueError('Existing selected member is corrupt: '+n)
                reused[n]=inv['members'][n]
    elif verified_reuse:raise ValueError('No failed staging exists to reuse')
    remaining=count-sum(v['bytes']for v in reused.values())
    if count>2*2**30 or remaining+6*2**30>shutil.disk_usage(base).free:
        raise ValueError('Exact selected footprint/free reserve does not fit')
    if not out.exists():out.mkdir()
    meta=json.loads((base/'e029-evidence.tar.gz.object.json').read_text())
    proof=json.loads((base/'archive-verified.json').read_text());expected=proof['archive']
    if meta['generation']!=proof['generation']:raise ValueError('Archive generation changed')
    c=Cloud(out/'transport');token=subprocess.check_output([str(c.sdk),'auth','print-access-token'],env=c.env,text=True).strip()
    url='https://storage.googleapis.com/storage/v1/b/'+meta['bucket']+'/o/'+urllib.parse.quote(meta['name'],safe='')+'?alt=media&generation='+meta['generation']
    seen=set();logical=0
    with urllib.request.urlopen(urllib.request.Request(url,headers={'Authorization':'Bearer '+token}),timeout=180)as raw:
        reader=BoundReader(raw,expected)
        with tarfile.open(fileobj=reader,mode='r|gz')as stream:
            for m in stream:
                member_path(out,m.name)
                if not m.isfile()or m.name in seen or logical+m.size>4*2**30:raise ValueError('Malformed archive member')
                if not seen and m.name!='inventory.json':raise ValueError('Missing first inventory')
                seen.add(m.name);f=stream.extractfile(m)
                if m.name=='inventory.json':
                    payload=f.read(64*2**20+1)
                    if len(payload)!=m.size or json.loads(payload)!=inv:raise ValueError('Inventory drift')
                    logical+=len(payload);continue
                h=hashlib.sha256();size=0;target=None
                if m.name in selected and m.name not in reused:
                    p=member_path(out,m.name);p.parent.mkdir(parents=True,exist_ok=True);target=p.open('xb')
                try:
                    for chunk in iter(lambda:f.read(2**20),b''):
                        size+=len(chunk);h.update(chunk)
                        if target:
                            if shutil.disk_usage(base).free<len(chunk)+6*2**30:raise ValueError('Free reserve changed')
                            target.write(chunk)
                finally:
                    if target:target.close()
                logical+=size
                if inv['members'].get(m.name)!=dict(bytes=size,sha256=h.hexdigest()):raise ValueError('Member checksum drift')
        reader.finish()
    inventory_relations(inv,seen)
    for name,wanted in aliases.items():
        p=member_path(out,name);p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists():os.link(member_path(out,wanted['canonical']),p)
        if binding(p)!={k:wanted[k]for k in ['bytes','sha256']}:raise ValueError('Alias differs')
    result=dict(status='PASS',community=community,role=role,archive=expected,generation=meta['generation'],
        all_members_reverified=True,materialized_bytes=count,physical_members=len(selected),aliases=len(aliases),
        verified_reused_members=reused,additional_bytes=remaining,
        omitted_alternatives='Original candidates remain fully verified in private archive and native audit; not materialized')
    receipt=out/('staging-'+role+'.json'if role else'staging.json')
    if receipt.exists():raise ValueError('Closed staging receipt already exists')
    write(receipt,result);print(json.dumps({k:v for k,v in result.items()if k!='verified_reused_members'}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base',type=Path,required=True);p.add_argument('--community',choices=['E009','oral'],required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--role',choices=['teacher','student'])
    p.add_argument('--verified-reuse',action='store_true');a=p.parse_args();stage(a.base,a.community,a.output,a.role,a.verified_reuse)
