#!/usr/bin/env python3
"""Verify the frozen retained E014 inputs/runtime without copying or fallback.

The lock is prepared from already verified native inventories and admission
receipts. Hash only contracted execution files and inputs, not an entire numerical
prefix or unused sources. No detector, feature/view preparation or installation.
"""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_collect import binding,member_path


def verify(lock,output):
    """Check every locked regular input/source/library byte before or after a run."""
    lock=Path(lock);record=json.loads(lock.read_text());checked={};last=time.monotonic();total=0
    for key,r in record['files'].items():
        path=member_path(Path('/'),key.removeprefix('/'))
        actual=binding(path)
        if actual!=r:raise ValueError('Missing/corrupt retained byte; no fallback: '+key)
        checked[key]=actual;total+=actual['bytes']
        if time.monotonic()-last>5:print('E019_RETAINED_VERIFIED',len(checked),total,flush=True);last=time.monotonic()
    out=dict(status='PASS',lock=binding(lock),files=checked,bytes=total,read_only=True,fallback=False,
             scope='Inputs, accepted receipts, installed project sources and loaded native library targets; not all unused prefix files')
    with Path(output).open('x') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    print('E019_REUSE_PASS',len(checked),total,flush=True);return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lock',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();verify(a.lock,a.output)
