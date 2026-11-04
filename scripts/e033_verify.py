#!/usr/bin/env python3
"""Verify only original E033-consumed input/state members, without science."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def verify(plan,output):
    """Retain actual before/after byte measurements; no fallback recopy is possible."""
    p=json.loads(Path(plan).read_text());r=json.loads((ROOT/'experiments/E033-multiscale-bam/reuse-lock.json').read_text())
    actual={}
    for n,b in r['external_files'].items():
        actual[n]=binding(n)
        if actual[n]!=b:raise ValueError('Original consumed member changed: '+n)
    for u,e in p['units'].items():
        for suffix,key in [('.pt','checkpoint'),('.json','metadata')]:
            n=str(Path(e['original']).with_suffix(suffix));actual[n]=binding(n)
            if actual[n]!=r['E031_states'][u][key]:raise ValueError('Restored accepted state changed: '+n)
    write(output,dict(status='PASS',files=actual,files_verified=len(actual),bytes_verified=sum(v['bytes'] for v in actual.values()),
        no_science_replayed=True,scope='Exact original DNA/view/token/GLM/marker/state consumers; not unused whole numerical prefix'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();verify(a.plan,a.output)
