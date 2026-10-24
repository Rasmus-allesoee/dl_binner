#!/usr/bin/env python3
"""Close the owner-authorized E009-only E021 scope without claiming oral success.

These native targets consume exact retained bytes. They do not install software,
extract DNA, train a model or select thresholds. The GPU wait is bounded and closes
its parent even if the Mac disappears; CPU completion needs six actual exits.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import time
import sys
sys.path.insert(0,str(Path(__file__).absolute().parent))


def put(path,value):
    """Write a new immutable small receipt, refusing accidental recovery overwrite."""
    with Path(path).open('x')as f:json.dump(value,f,indent=2);f.write('\n')


def bound(path):
    """Hash one regular member without buffering its complete contents."""
    p=Path(path)
    if p.is_symlink()or not p.is_file():raise ValueError('Regular member required')
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return dict(bytes=p.stat().st_size,sha256=h.hexdigest())


def bank(plan,output,context=False):
    """Use the actual installed FrozenBank and optionally the complete ContextBank."""
    from dl_binner.multiview.views import load
    from dl_binner.hybrid.bank import Bank
    p=json.loads(Path(plan).read_text());u=p['units']['E009-hybrid']
    data,meta,v,vm=load(u['features'],u['views'])
    if len(data['ids'])!=145702 or int(data['eligible'].sum())!=89041:
        raise ValueError('Complete E009 axes differ')
    lock=json.loads(Path(p['candidate_lock']).read_text())
    if meta['samples']!=lock['ordered_depth_columns']:raise ValueError('Ten ordered depth samples differ')
    root=Path(p['work'])/'units/E009-hybrid';b=Bank(root/'frozen',u['features'],u['views'],data,meta,v)
    if b.meta['views']!=432664:raise ValueError('Complete retained exposure differs')
    if bound(root/'accepted-context.json')!=bound(Path(u['tokens'])/'tokens.json'):
        raise ValueError('Original context manifest differs')
    if context:
        from dl_binner.context.tokens import Bank as ContextBank
        c=ContextBank(u['tokens'],u['features'],u['views'],data,meta,v)
        del c
    files={str(x.relative_to(root)):dict(source=str(x),**bound(x))
        for x in sorted(root.rglob('*'))if x.is_file()}
    put(output,dict(status='PASS_ACTUAL_E009_BANK_READER',full_contigs=len(data['ids']),
        eligible=int(data['eligible'].sum()),views=b.meta['views'],samples=meta['samples'],
        context_arrays_read=context,files=files,no_inference=True))


def wait_handoff(root,seconds):
    """Wait once for verified cache relocation, then always close the GPU parent."""
    r=Path(root);cfg=json.loads((r/'config.json').read_text())
    end=min(time.time()+seconds,cfg['node_deadline_epoch']-600)
    while time.time()<end:
        if(r/'handoff-done.json').exists():
            proof=json.loads((r/'handoff-done.json').read_text())
            if proof.get('CPU_bank_reader')!='PASS_ACTUAL_E009_BANK_READER' or proof.get('paired_transport')is not True:
                raise ValueError('Native CPU handoff is not proved')
            put(r/'finish.json',dict(status='SUCCESS_E009_EXTRACTION_RELOCATED_PENDING_CPU',
                science_completed=False,E009_extraction_completed=True,oral_executed=False))
            return
        print('E009_HANDOFF_WAIT',time.time(),flush=True);time.sleep(15)
    put(r/'finish.json',dict(status='SUCCESS_E009_EXTRACTION_RETAINED_HANDOFF_PENDING',
        science_completed=False,E009_extraction_completed=True,oral_executed=False,
        reason='Bounded handoff window ended; preserve bank and stop, no automatic replay'))


def cpu_target(root,plan):
    """Require six actual E009 exits, reload, graph and all three DNA partitions."""
    r=Path(root);p=json.loads(Path(plan).read_text());records=[]
    for f in sorted((r/'tasks').glob('*.result.json')):
        x=json.loads(f.read_text())
        if x['kind']=='science':records.append(x)
    if len(records)!=6 or any(x['status']!='SUCCESS'for x in records)or {(x.get('unit'),x.get('stage'))for x in records}!={
            ('E009-hybrid',s)for s in ['train','embed','group','refine','export','graph-proof']}:
        raise ValueError('Six E009 scientific exits not proved')
    u=Path(p['work'])/'units/E009-hybrid'
    a=json.loads((u/'export/accounting.json').read_text())
    g=json.loads((u/'graph-proof.json').read_text())
    ck=json.loads((u/'train/checkpoint.json').read_text())
    if (set(a)!={'pre','old','post'}or g['status']!='PASS'or len(ck['history'])!=20
            or bound(u/'train/reference.npz')!=bound(u/'embeddings.npz')):
        raise ValueError('Frozen reload/schedule/graph/export target failed')
    put(r/'gates/E009-scoped-target.json',dict(status='PASS_E009_ONLY_COMPLETE',
        stages=records,accounting=a,original_joint_criterion_met=False,oral_executed=False,
        scope='One full development assembly; no two-community KEEP or generalization claim'))
    put(r/'finish.json',dict(status='SUCCESS_E009_ONLY_COMPLETE',science_completed=False,
        E009_scoped_science_completed=True,oral_executed=False,
        reason='Legacy science_completed covers both communities and remains false'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['bank','wait','cpu-target'])
    p.add_argument('--plan',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--root',type=Path);p.add_argument('--context',action='store_true')
    p.add_argument('--seconds',type=int,default=5400);a=p.parse_args()
    if a.operation=='bank':bank(a.plan,a.output,a.context)
    elif a.operation=='wait':wait_handoff(a.root,a.seconds)
    else:cpu_target(a.root,a.plan)
