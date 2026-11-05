#!/usr/bin/env python3
"""Generation-bound restore of accepted E031 vectors and E033 measured banks.

Hash every compressed byte/member/alias but stage only actual consumed cache
members. Transport proofs live outside work; no accepted science is regenerated.
"""
import argparse,json
from pathlib import Path
import sys,urllib.parse,urllib.request
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import e032_restore as reader
from e024_coverage import binding,write
from e034_pilot import object_metadata,token


def needed(name,kind):
    """Select complete original graph/embedding or measured interval companions."""
    if kind=='measurements':return name.startswith('work/')
    if kind!='bootstrap':raise ValueError('One explicit accepted cache kind required')
    return any(name.startswith('work/'+u+'/'+part) for u in ['E009-noGLM','E009-GLM','oral-noGLM'] for part in ['embed/','graph/result/'])


def restore(kind,output):
    """Restore once with full byte verification; existing partial copies refuse."""
    output=Path(output)
    if (output/'stream-admission.json').exists():
        proof=json.loads((output/'stream-admission.json').read_text())
        for n,b in proof['restored_members'].items():
            if binding(output/n)!=b:raise ValueError('Retained restored member drift; no recopy')
        return proof
    if output.exists():raise ValueError('Partial original restore retained; no fallback')
    if kind=='bootstrap':
        lock=json.loads((ROOT/'experiments/E033-multiscale-bam/reuse-lock.json').read_text())['accepted_archive']
        uri=lock['archive']['uri'];expected=lock['archive']['binding'];generation=lock['metadata']['generation'];inventory=lock['inventory']
    else:
        lock=json.loads((ROOT/'experiments/E033-multiscale-bam/inspection-observed.json').read_text())['archives']['measurements']
        uri=lock['uri'];expected=lock['binding'];generation=lock['generation'];inventory=lock['inventory']
    meta,url=object_metadata(uri,generation)
    if int(meta['size'])!=expected['bytes']:raise ValueError('Original archive size differs')
    config=dict(size=expected['bytes'],generation=generation,md5_hash=meta.get('md5Hash'))
    request=urllib.request.Request(url+'?alt=media&generation='+generation,headers={'Authorization':'Bearer '+token()})
    old=reader.needed,reader.LOGICAL;reader.needed=lambda n:needed(n,kind);reader.LOGICAL=8*1024**3
    try:
        with urllib.request.urlopen(request,timeout=180) as stream:proof=reader.stream_restore(stream,config,expected,output,inventory,25*1024**3)
    finally:reader.needed,reader.LOGICAL=old
    (output/'work/restore-admission.json').rename(output/'stream-admission.json')
    # The original proof's inventory entry remains relative to the original
    # archive; move only the receiver-generated proof outside scientific work.
    print('E034_ORIGINAL_CACHE_RESTORED',kind,len(proof['restored_members']),flush=True);return proof


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--kind',choices=['bootstrap','measurements'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();restore(a.kind,a.output)
