#!/usr/bin/env python3
"""Verify sealed cached E016 consumers in place; no restoration/copy/install fallback."""
import argparse
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_collect import binding,member_path


def verify(lock,output):
    """Hash only contracted science/runtime members plus the accepted archive.

    The lock derives from already admitted member inventories. Native paths are
    preserved, not inferred from directory names or copied on missing data.
    """
    path=Path(lock);record=json.loads(path.read_text());result={};total=0;last=time.monotonic()
    if record['kind']!='E017 in-place sealed E016 reuse':raise ValueError('Unexpected reuse schema')
    for key,expected in record['files'].items():
        p=member_path(Path('/'),key.removeprefix('/'))
        if binding(p)!=expected:raise ValueError('Missing/corrupt retained payload; no recopy/reinstall fallback: '+key)
        result[key]=expected;total+=expected['bytes']
        if time.monotonic()-last>5:
            print('E017_RETAINED_VERIFIED',len(result),total,flush=True);last=time.monotonic()
    out=dict(status='PASS',lock=binding(path),files=result,bytes=total,read_only=True,
             copy_fallback=False,encoder_inference=False,scope='Sealed E016 archive, contracted feature/FASTA/native vector/marker inputs, runtime identity members; unused prefix files not rehashed')
    with Path(output).open('x') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lock',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(verify(a.lock,a.output)),flush=True)
