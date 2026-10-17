#!/usr/bin/env python3
"""Audit only public oral BAM reference headers, not alignment bodies or coverage.

At most four concurrent bounded header requests use <=128 KiB per file. Failed
or incomplete headers remain explicit; source filenames alone never establish a
genome identity. The original acquisition/validation clock and disk guard apply.
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import shlex
import struct
import time
import urllib.request
import zlib
import sys

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_acquire import ROOT,guard


def decode(raw):
    """Decode complete BGZF members through a complete text and binary dictionary."""
    data=b'';at=0
    while at+18<=len(raw):
        size=struct.unpack_from('<H',raw,at+16)[0]+1
        if size<18 or at+size>len(raw):break
        data+=zlib.decompress(raw[at:at+size],31);at+=size
        if len(data)<12 or data[:4]!=b'BAM\x01':continue
        textsize=struct.unpack_from('<i',data,4)[0]
        if textsize<0:raise ValueError('Negative BAM text size')
        if len(data)<12+textsize:continue
        text=data[8:8+textsize].decode();nref=struct.unpack_from('<i',data,8+textsize)[0];pos=12+textsize;refs=[]
        for _ in range(nref):
            if pos+4>len(data):break
            n=struct.unpack_from('<i',data,pos)[0];pos+=4
            if n<1:raise ValueError('Invalid BAM dictionary name')
            if pos+n+4>len(data):break
            name=data[pos:pos+n-1].decode();pos+=n;length=struct.unpack_from('<i',data,pos)[0];pos+=4
            refs.append(dict(SN=name,LN=length))
        if len(refs)!=nref:continue
        sam=[];sources=[]
        for line in text.splitlines():
            fields=dict(f.split(':',1) for f in line.split('\t')[1:] if ':' in f)
            if line.startswith('@SQ'):sam.append(dict(SN=fields['SN'],LN=int(fields['LN'])))
            if line.startswith('@PG') and 'CL' in fields:
                args=shlex.split(fields['CL'])
                if '-i' in args:sources.append(args[args.index('-i')+1])
        if sam!=refs or len({r['SN'] for r in refs})!=len(refs):raise ValueError('SAM/binary reference dictionary differs')
        return dict(sam_header=text,references=refs,source_paths=sources)
    return None


def header(name):
    """Read the smallest complete reference dictionary, bounded to 128 KiB."""
    url='https://frl.publisso.de/data/frl%3A6425518/per_bodysite/oral_bam/'+name
    try:
        for limit in [4096,16384,131072]:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'Range':f'bytes=0-{limit-1}'}),timeout=30) as f:
                if f.status!=206 or not f.headers.get('Content-Range','').startswith(f'bytes 0-{limit-1}/'):raise ValueError('Header range refused')
                raw=f.read(limit+1)
            if len(raw)!=limit:raise ValueError('Incomplete header response')
            decoded=decode(raw)
            if decoded is not None:return dict(name=name,url=url,probe_bytes=limit,range_sha256=hashlib.sha256(raw).hexdigest(),**decoded)
        raise ValueError('Header exceeds bounded prefix')
    except Exception as exc:return dict(name=name,url=url,error=repr(exc))


def main():
    """Audit all listed BAMs once and retain missing/foreign-source identities."""
    m=ROOT/'metadata';clock=json.loads((ROOT/'acquisition-clock.json').read_text());guard(ROOT,clock)
    names=sorted(set(re.findall(r'href="(OTU_[^/"?]+\.bam)"',(m/'per_bodysite_oral_bam-index.html').read_text())))
    expected=dict(line.rstrip().split('\t',1) for line in (m/'setup-genome_to_id.tsv').read_text().splitlines())
    records=[];start=time.monotonic()
    with ThreadPoolExecutor(max_workers=4) as pool:
        for record in pool.map(header,names):
            ident=record['name'][:-4];record['filename_genome_ID']=ident
            source=Path(expected[ident]).name if ident in expected else None
            record['expected_source_basename']=source
            record['source_matches_setup']=bool(record.get('source_paths')) and all(Path(p).name==source for p in record['source_paths'])
            records.append(record)
            if len(records)%40==0:guard(ROOT,clock);print('BAM_HEADERS',len(records),len(names),flush=True)
    result=dict(records=records,seconds=time.monotonic()-start,total_headers=len(records),complete_headers=sum('error' not in r for r in records),
                foreign_or_unjoined_sources=sum(not r['source_matches_setup'] for r in records),
                scope='Complete SAM/binary reference headers only; not whole-BAM publisher checksum or alignment/coverage validation.')
    (m/'all-oral-bam-headers.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('BAM_HEADER_SUMMARY',{k:v for k,v in result.items() if k!='records'},flush=True)


if __name__=='__main__':main()
