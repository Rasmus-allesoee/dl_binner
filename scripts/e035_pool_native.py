#!/usr/bin/env python3
"""Installed E035 retained-BAM wrapper; no mapper, fit, classifier or truth API.

Reuse the accepted exact-generation transport and the frozen E035 scientific
consumer. Restore only the next Oral BAM, close its full ledger before deleting
that verified temporary copy, and preserve original source generations and logs.
"""
import argparse
import json
from pathlib import Path
import sys
import time

import dl_binner as _owned_product

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def inputs(path,output):
    """Verify full feature bytes/axes and bind only the actual accepted inputs."""
    from e035_support import plan
    from dl_binner.multiview.views import load
    p=plan(path);reuse=json.loads((ROOT/'experiments/E035-confidence-taxonomy/reuse-lock.json').read_text());result={}
    for community,feature in p['features'].items():
        d,m=load(feature)
        unit='E009-noGLM'if community=='E009'else'oral-noGLM'
        axis=dict(rows=len(d['ids']),bp=int(d['lengths'].sum()),eligible=int(d['eligible'].sum()),samples=m['samples'])
        if axis!=reuse['axes'][unit]or axis['samples']!=[b['sample']for b in p['BAMs'][community]]:
            raise ValueError('Complete original contig/ordered sample axis differs')
        for f in [str(feature),str(Path(feature).with_suffix('.json'))]:
            actual=binding(f)
            if actual!=reuse['external_files'][f]:raise ValueError('Accepted original feature bytes differ')
            result[f]=actual
        result[community]=axis
    write(output,result);return result


def sample(path,community,index):
    """Run one byte-bound sample or verify its existing ledger without restoration."""
    from e035_support import plan,run
    from e034_pilot import source
    from dl_binner.genomegraph import pooled
    p=plan(path);root=Path(p['work']);target=root/community/('sample-%02d'%index)
    record=p['BAMs'][community][index];restore=Path(record['local']).parent
    proof_path=root/community/('sample-%02d-transport.json'%index)
    if (target/'completed.json').exists():
        run(path,community,'sample',index)
        if not proof_path.is_file():raise ValueError('Sealed ledger lacks closed source transport; preserve and diagnose')
        proof=json.loads(proof_path.read_text())
        if proof['record']!=record or proof['ledger']!=binding(target/'completed.json'):
            raise ValueError('Closed sample transport differs')
        return proof
    started=time.monotonic()
    if record['source'].startswith('gs://'):restore.mkdir(parents=True,exist_ok=True)
    bam,transport,temporary=source(record,restore)
    if bam.absolute()!=Path(record['local']).absolute():raise ValueError('Restored path differs from exact consumer plan')
    run(path,community,'sample',index)
    a,m=pooled.read(target)
    if binding(bam)!={k:record[k]for k in ['bytes','sha256']}:raise ValueError('Input BAM changed during ledger extraction')
    proof=dict(status='PASS',record=record,transport=transport,ledger=binding(target/'completed.json'),
        observations=len(a['observations']),reader_wall_seconds=m['wall_seconds'],wall_seconds=time.monotonic()-started,
        temporary_verified_copy_removed=False,old_science_replayed=False)
    if temporary:
        # Only this exact disposable restore is removed. The immutable original
        # private generation and its restoration/native decode evidence remain.
        bam.unlink();proof['temporary_verified_copy_removed']=True
    write(proof_path,proof);print('E035_POOL_SAMPLE_CLOSED',json.dumps(proof),flush=True);return proof


def tiny(output):
    """Exercise actual native BAM reader/pooling/refusal tests, without any fit."""
    import subprocess
    for suffix in ['test_pooled_support.py','test_e035_support.py','test_e035_pool_execution.py']:
        folder='tests/product'if suffix=='test_pooled_support.py'else'tests'
        argv=[sys.executable,'-I','-B','-m','unittest','discover','-s',str(ROOT/folder),'-p',suffix,'-v']
        result=subprocess.run(argv,cwd=ROOT,check=False)
        if result.returncode:raise RuntimeError('Actual native tiny audit gate failed: '+suffix)
    write(output,dict(status='PASS_NATIVE_AUDIT_ONLY',actual_BAM_reader_and_pool=True,no_model_fit=True,truth_accessed=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--plan',type=Path);parser.add_argument('--output',type=Path)
    parser.add_argument('--action',choices=['inputs','sample','pool','tiny'],required=True)
    parser.add_argument('--community',choices=['E009','oral']);parser.add_argument('--index',type=int)
    a=parser.parse_args()
    if a.action=='inputs':inputs(a.plan,a.output)
    elif a.action=='sample':sample(a.plan,a.community,a.index)
    elif a.action=='tiny':tiny(a.output)
    else:
        from e035_support import run
        run(a.plan,a.community,'pool')
