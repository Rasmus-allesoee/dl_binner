#!/usr/bin/env python3
"""Refresh small oral HEAD/Swift segment-MD5 metadata, never read payload bodies.

The trailing slash on the Swift container listing is intentional: the no-slash
endpoint was observed to ignore prefix/format and return an unrelated listing.
Every size/prefix/index/aggregate relation is checked before a new manifest is
published. Output locations must be fresh; review changes before replacing any
prospectively frozen input manifest. No cloud credential or scientific input is used.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import urllib.parse
import urllib.request

ROOT=Path(__file__).absolute().parents[1]


def refresh(output,manifest):
    """Save bounded public source records and exact ordered ten-sample metadata."""
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    old=json.loads((ROOT/'artifacts/e014-multiview-reconstruction/metadata/swift-read-HEADs.json').read_text())
    base='https://openstack.cebitec.uni-bielefeld.de:8080/swift/v1/'
    records=[]
    for previous in old:
        url=base+'CAMI_Oral/'+previous['path']
        with urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=30) as response:
            if response.status!=200:raise ValueError('Full publisher HEAD required')
            headers={k.lower():v for k,v in response.headers.items()}
        container,prefix=headers['x-object-manifest'].split('/',1)
        query=urllib.parse.urlencode(dict(format='json',prefix=prefix,limit=100))
        request=urllib.request.Request(base+container+'/?'+query,headers={'Accept':'application/json'})
        with urllib.request.urlopen(request,timeout=30) as response:raw=response.read(100001)
        if len(raw)>100000:raise ValueError('Small segment manifest cap exceeded')
        segments=json.loads(raw)
        if (not 0<len(segments)<100 or any(not s['name'].startswith(prefix) or s['bytes']<=0
                                         or len(s['hash'])!=32 for s in segments)
                or [s['name'].rsplit('/',1)[-1] for s in segments]!=[f'{i:08d}' for i in range(len(segments))]
                or sum(s['bytes'] for s in segments)!=int(headers['content-length'])):
            raise ValueError('Publisher segment prefix/order/length differs')
        aggregate=hashlib.md5(''.join(s['hash'] for s in segments).encode()).hexdigest()
        if aggregate!=headers['etag'].strip('"'):raise ValueError('DLO aggregate ETag differs')
        record=dict(sample=previous['sample'],column=f'oral_sample_{previous["sample"]}',url=url,
                    bytes=int(headers['content-length']),headers=headers,
                    segments=[dict(url=base+container+'/'+s['name'],bytes=s['bytes'],md5=s['hash']) for s in segments],
                    etag_semantics='DLO MD5 of concatenated segment MD5 hex strings; NOT whole FASTQ MD5',
                    DLO_aggregate_md5=aggregate)
        records.append(record)
        (output/f'sample-{previous["sample"]}.json').write_text(json.dumps(record,indent=2)+'\n')
        print('E024_HEAD_SEGMENTS_VERIFIED',previous['sample'],record['bytes'],flush=True)
    publisher='https://frl.publisso.de/data/frl%3A6425518/'
    for name,cap in [('README.md',10000),('md5sums.tsv',1000000)]:
        with urllib.request.urlopen(publisher+name,timeout=30) as response:raw=response.read(cap+1)
        if len(raw)>cap:raise ValueError('Small public metadata cap exceeded')
        (output/name).write_bytes(raw)
    result=dict(kind='E024 publisher segment-MD5 acquisition manifest',observed_epoch=time.time(),
                ordered_samples=[r['sample'] for r in records],total_read_bytes=sum(r['bytes'] for r in records),reads=records,
                checksum_policy='Every publisher segment MD5 plus total bytes and newly calculated whole-object MD5/SHA256; DLO aggregate is separately checked',
                bulk_downloaded=False)
    with Path(manifest).open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--manifest',type=Path,required=True)
    a=parser.parse_args();print(json.dumps(refresh(a.output,a.manifest)),flush=True)
