#!/usr/bin/env python3
"""Read one admitted retained BAM into a new verified physical-template cache.

Oral bytes are restored serially from an exact private generation, never acquired
again from the publisher or remapped. Passed caches are reused only by byte/axis/
source/policy contracts; corrupt or partial copies refuse without a fallback.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def token():
    """Read an ephemeral existing VM service token without writing/logging it."""
    q=urllib.request.Request('http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token',headers={'Metadata-Flavor':'Google'})
    with urllib.request.urlopen(q,timeout=8) as f:return json.load(f)['access_token']


def object_metadata(uri,generation):
    """Read the pinned object's metadata; MD5 may be absent for composite BAMs."""
    u=urllib.parse.urlsplit(uri)
    if u.scheme!='gs' or u.netloc!='dl-binner-archive-167650584170':raise ValueError('Existing private source only')
    url='https://storage.googleapis.com/storage/v1/b/'+u.netloc+'/o/'+urllib.parse.quote(u.path.lstrip('/'),safe='')
    request=urllib.request.Request(url+'?generation='+str(generation),headers={'Authorization':'Bearer '+token()})
    with urllib.request.urlopen(request,timeout=30) as f:meta=json.load(f)
    if meta['generation']!=str(generation):raise ValueError('Source generation differs')
    return meta,url


def source(record,root):
    """Verify a native original or restore one exact temporary private BAM copy."""
    root=Path(root);expected={k:record[k] for k in ['bytes','sha256']}
    if not record['source'].startswith('gs://'):
        p=Path(record['source'])
        if binding(p)!=expected:raise ValueError('Original native BAM differs')
        return p,dict(kind='original_readonly_native_BAM',binding=expected,source=record['source']),False
    uri,generation=record['source'].rsplit('#',1);meta,url=object_metadata(uri,generation)
    if int(meta['size'])!=record['bytes'] or meta['crc32c']!=record['crc32c']:raise ValueError('Private source size/CRC metadata differs')
    p=root/'source.bam';receipt=root/'source-restore.json'
    if p.exists() or receipt.exists():
        if not(p.is_file() and receipt.is_file()) or binding(p)!=expected:raise ValueError('Existing restored BAM missing/corrupt; no fallback')
        proof=json.loads(receipt.read_text())
        if proof['source']!=record:raise ValueError('Restored source record differs')
        return p,proof,True
    partial=root/'source.part'
    if partial.exists():raise ValueError('Partial source retained; fresh recorded attempt required')
    h=hashlib.sha256();size=0;started=time.monotonic()
    request=urllib.request.Request(url+'?alt=media&generation='+generation,headers={'Authorization':'Bearer '+token()})
    with urllib.request.urlopen(request,timeout=180) as stream,partial.open('xb') as out:
        while True:
            block=stream.read(1024**2)
            if not block:break
            if size+len(block)>expected['bytes'] or shutil.disk_usage(root).free-len(block)<25*1024**3:raise ValueError('Source restore bytes/free reserve exceeded')
            out.write(block);h.update(block);size+=len(block)
            if size%(256*1024**2)<len(block):print('E034_SOURCE_BYTES',record['sample'],size,flush=True)
        out.flush();os.fsync(out.fileno())
    if dict(bytes=size,sha256=h.hexdigest())!=expected:raise ValueError('Retained BAM whole SHA differs')
    # The SDK's compiled local CRC32C implementation is reused, without auth
    # or an added numerical dependency. It does not transfer the local file.
    hash_env=dict(os.environ,CLOUDSDK_CONFIG=os.environ['E034_HASH_CONFIG'],CLOUDSDK_COMPONENT_MANAGER_DISABLE_UPDATE_CHECK='true')
    command=['/snap/bin/gcloud','storage','hash',str(partial),'--format=json']
    checked=subprocess.run(command,capture_output=True,text=True,env=hash_env,timeout=180)
    (root/'CRC32C.stdout').write_text(checked.stdout);(root/'CRC32C.stderr').write_text(checked.stderr);checked.check_returncode()
    hashes=json.loads(checked.stdout)
    if len(hashes)!=1 or hashes[0]['crc32c_hash']!=meta['crc32c']:raise ValueError('Local/server retained BAM CRC32C differs')
    os.link(partial,p);partial.unlink();p.chmod(0o400)
    proof=dict(status='PASS',source=record,binding=expected,generation=generation,server_crc32c=meta['crc32c'],whole_sha256_verified=True,local_server_CRC32C_verified=True,CRC32C_command=command,wall_seconds=time.monotonic()-started,temporary_exact_copy=True)
    write(receipt,proof);return p,proof,True


def run(community,index,output,features):
    """Execute one new physical reader or return a strictly verified closed cache."""
    from e034_control import product_scope
    product_scope();from dl_binner.genomegraph.links import extract,read,DEFAULT
    from dl_binner.multiview.views import load
    records=json.loads((ROOT/'experiments/E033-multiscale-bam/BAM-manifest.json').read_text())['records'];record=[r for r in records if r['community']==community][index]
    output=Path(output)
    if (output/'completed.json').exists():
        r=json.loads((output/'completed.json').read_text());a,m=read(output/'links')
        if r['source']!=record or r['graph_completed']!=binding(output/'links/completed.json') or m['policy']!=DEFAULT or r['features']!=binding(features):raise ValueError('Passed link cache drift; no replay')
        return r
    output.mkdir(parents=True,exist_ok=False);data,meta=load(features)
    if meta['samples'][index]!=record['sample']:raise ValueError('Ordered BAM/feature sample differs')
    bam,restore,temporary=source(record,output)
    result=extract(bam,data['ids'].tolist(),data['lengths'],data['eligible'],record['sample'],output/'links',threads=4)
    arrays,closed=read(output/'links')
    proof=dict(status='PASS',community=community,index=index,source=record,features=binding(features),restore=restore,physical_edges=len(arrays['edges']),
        graph_completed=binding(output/'links/completed.json'),utility=result['utility'],reader_wall_seconds=result['wall_seconds'],alignment_records=result['counters']['alignment_records'],temporary_BAM_removed=False)
    if temporary:
        # Verified exact disposable copy only. The original private generation
        # and its full native decode/provenance remain unchanged and protected.
        if binding(bam)!={k:record[k] for k in ['bytes','sha256']}:raise ValueError('Temporary original-copy bytes drift before release')
        bam.unlink();proof['temporary_BAM_removed']=True
    write(output/'completed.json',proof);print('E034_TEMPLATE_SAMPLE_CLOSED',json.dumps(proof),flush=True);return proof


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--community',choices=['E009','oral'],required=True);p.add_argument('--index',type=int,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--features',type=Path,required=True);a=p.parse_args()
    if not 0<=a.index<10:p.error('One retained sample index 0..9 required')
    run(a.community,a.index,a.output,a.features)
