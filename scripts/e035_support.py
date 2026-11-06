#!/usr/bin/env python3
"""Offline-configured retained-BAM support audit, with no mapper/fit/cloud API.

The native controller must independently admit credits, clock, source/runtime,
all twenty BAM bytes and supervision before invoking this consumer. A passed
sample ledger is reused only by its seal, source and unchanged policy.
"""
import argparse
import json
import os
from pathlib import Path
import sys

import dl_binner

ROOT=Path(__file__).absolute().parents[1]


def plan(path):
    """Require complete original ordered sample axes and the new support policy."""
    p=json.loads(Path(path).read_text())
    if set(p)!={'kind','engineering','work','features','BAMs','limits'} or p['kind']!='E035 pooled-before-support audit' or p['engineering']is not False:
        raise ValueError('Unknown or incomplete pooled-audit plan')
    if set(p['features'])!={'E009','oral'}or set(p['BAMs'])!={'E009','oral'}:raise ValueError('Both assembly communities required')
    frozen=json.loads((ROOT/'experiments/E035-confidence-taxonomy/pooled-audit-plan.json').read_text())
    if p['features']!=frozen['features']or p['limits']!=frozen['limits']:
        raise ValueError('Frozen feature bindings or complete pooled envelope differ')
    for c in ['E009','oral']:
        records=p['BAMs'][c]
        if len(records)!=10 or len({r['sample']for r in records})!=10:raise ValueError('Full ten-sample support axis required')
        # Only the transport destination may change. Actual generation/bytes,
        # sample order and source identity must remain independently locked even
        # if a controller accidentally publishes a different valid JSON plan.
        for actual,expected in zip(records,frozen['BAMs'][c]):
            if set(actual)!=set(expected)or {k:v for k,v in actual.items()if k!='local'}!={k:v for k,v in expected.items()if k!='local'}:
                raise ValueError('Frozen ordered original BAM identity differs')
    return p


def run(path,community,stage,index=None):
    """Extract one verified BAM or pool all ten sealed raw-support ledgers once."""
    from dl_binner.genomegraph import pooled,links
    from dl_binner.multiview.views import load
    from dl_binner.context.tokens import binding
    from dl_binner.io import write_json
    if dl_binner.__version__!='0.1.0.dev11' or not Path(dl_binner.__file__).is_relative_to(Path(sys.prefix)):
        raise ValueError('Owned installed E035 required')
    p=plan(path);root=Path(p['work'])/community;root.mkdir(parents=True,exist_ok=True);d,m=load(p['features'][community])
    lock=json.loads((ROOT/'experiments/E035-confidence-taxonomy/source-lock.json').read_text())
    if any(binding(ROOT/n)!=b for n,b in lock['files'].items()):raise ValueError('Frozen pooled-audit source differs')
    release=os.environ.get('E035_SUPPORT_RELEASE_FILE')
    if not release or json.loads(Path(release).read_text()).get('plan')!=binding(path):raise ValueError('Fresh externally supervised pooled-audit release required')
    records=p['BAMs'][community]
    if [r['sample']for r in records]!=m['samples']:raise ValueError('BAM/feature ordered columns differ')
    if stage=='sample':
        if index is None or not 0<=index<10:raise ValueError('One explicit native sample index required')
        entry=records[index];source=Path(entry['local']);expected={k:entry[k]for k in ['bytes','sha256']};target=root/('sample-%02d'%index)
        if (target/'completed.json').exists():
            a,r=pooled.read(target)
            if r['source']!=expected or r['sample']!=entry['sample']or r['policy']!=links.policy():raise ValueError('Sealed ledger source/policy drift')
            return
        if binding(source)!=expected:raise ValueError('Original BAM missing/corrupt; no mapping or fallback')
        pooled.extract(source,d['ids'].tolist(),d['lengths'],d['eligible'],entry['sample'],target,4)
        if binding(source)!=expected:raise ValueError('Original BAM changed')
    elif stage=='pool':
        folders=[root/('sample-%02d'%i)for i in range(10)];out=root/'pooled'
        if out.exists():raise ValueError('Pooled policy result already exists; verify it instead of recomputing')
        result=pooled.pool(folders,[r['sample']for r in records],out);links.read(out)
        write_json(root/'information-result.json',dict(status='COMPLETED_POOLED_INFORMATION_AUDIT',result=result,
            recovery_assessed=False,community_models_fit=False,all_ten_samples_completed=True))
    else:raise ValueError('Unknown pooled-audit stage')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--community',choices=['E009','oral'],required=True);p.add_argument('--stage',choices=['sample','pool'],required=True);p.add_argument('--index',type=int)
    a=p.parse_args();run(a.plan,a.community,a.stage,a.index)
