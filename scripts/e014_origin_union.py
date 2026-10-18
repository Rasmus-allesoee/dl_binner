#!/usr/bin/env python3
"""Independently summarize provided-source locus unions without any binner output.

This is a data-availability audit, never community recovery/scoring. Overlapping
or repeated query intervals cannot double-count provided reference coordinates.
Full positive reference denominators include GSA-absent genomes. Molecular aliases,
cross-genome ambiguity and non-ACGT support remain truth-admission concerns.
"""
import argparse
import json
from pathlib import Path
import sqlite3
import sys
import time

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_acquire import ROOT,guard,hashes


def union_length(spans):
    """Count one-based inclusive coordinates once; refuse malformed intervals."""
    total=0;left=right=None
    for start,end in sorted(spans):
        if not 1<=start<=end:raise ValueError('Invalid source-union coordinates')
        if right is None:left,right=start,end
        elif start<=right+1:right=max(right,end)
        else:total+=right-left+1;left,right=start,end
    return total+(right-left+1 if right is not None else 0)


def review(root=ROOT,source_name='source-validation-v1',clock_path=None):
    """Read immutable source/SQLite receipts; retain all target/zero-availability rows."""
    root=Path(root);clock=json.loads(Path(clock_path or root/'acquisition-clock.json').read_text());guard(root,clock)
    if Path(source_name).name!=source_name:raise ValueError('Invalid source review basename')
    source=root/source_name;status=json.loads((source/'review.json').read_text())
    if status['status']!='SOURCE_VALIDATED_TRUTH_STILL_PROVISIONAL':raise ValueError('Complete source audit missing')
    first=json.loads((root/'admission-v1/review.json').read_text())
    references=json.loads((source/'references.json').read_text());lengths={}
    for row in references:
        for g in row['genomes']:
            key=(g,row['record'])
            if key in lengths:raise ValueError('Duplicate provided source record axis')
            lengths[key]=row['bp']
    positive=set(first['population']['historical_taxonomy']['joins'])
    denominators=json.loads((source/'denominators.json').read_text());totals={g:dict(reference_bp=denominators[g]['raw_bp'],union_bp=0,contigs=0,interval_bp=0)for g in sorted(positive)}
    db=sqlite3.connect((root/'admission-v1/joins.sqlite').absolute().as_uri()+'?mode=ro',uri=True)
    current=None;spans=[];n=0
    def finish():
        if current is not None:
            g,r=current
            if g not in totals:raise ValueError('Observed genome outside positive target population')
            totals[g]['union_bp']+=union_length(spans)
    for g,r,a,b in db.execute('SELECT genome,record,start,end FROM fixed ORDER BY genome,record,start,end'):
        if (g,r) not in lengths or not 1<=a<=b<=lengths[(g,r)]:raise ValueError('Source-union complete-reference bounds differ')
        if current!=(g,r):finish();current=(g,r);spans=[]
        spans.append((a,b));totals[g]['contigs']+=1;totals[g]['interval_bp']+=b-a+1;n+=1
        if n%100000==0:guard(root,clock)
    finish();db.close()
    if n!=first['fixed_rows'] or sum(v['interval_bp']for v in totals.values())!=first['supplied_GSA']['bp']:
        raise ValueError('Full provided DNA interval accounting differs')
    if any(v['union_bp']>v['reference_bp']for v in totals.values()):raise ValueError('Source union exceeds full reference denominator')
    result=dict(status='DATA_AVAILABILITY_ONLY_TRUTH_PROVISIONAL',provided_positive_genomes=len(totals),
        GSA_observed_genomes=sum(v['contigs']>0 for v in totals.values()),
        zero_GSA_positive_genomes=[g for g,v in totals.items()if not v['contigs']],
        full_positive_reference_bp=sum(v['reference_bp']for v in totals.values()),
        observed_interval_bp=sum(v['interval_bp']for v in totals.values()),
        duplicate_safe_provided_record_union_bp=sum(v['union_bp']for v in totals.values()),genomes=totals,
        source_references=hashes(source/'references.json'),source_review=hashes(source/'review.json'),
        coordinate_policy='One-based inclusive union per supplied genome/record; neither query sum nor maximum observed coordinate becomes full denominator.',
        limits='Raw supplied-record denominators, not admitted molecular alias/near-ambiguity truth. No binner output, quality metric or change to target definitions.',validation_clock=clock,
        original_acquisition_clock=json.loads((root/'acquisition-clock.json').read_text()))
    out=root/'origin-union-v1.json'
    if out.exists():raise ValueError('Existing source-union review refused')
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');guard(root,clock)
    print('SOURCE_UNIONS',result['provided_positive_genomes'],result['GSA_observed_genomes'],result['full_positive_reference_bp'],result['duplicate_safe_provided_record_union_bp'],flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-name',default='source-validation-v1')
    p.add_argument('--clock',type=Path);a=p.parse_args();review(source_name=a.source_name,clock_path=a.clock)
