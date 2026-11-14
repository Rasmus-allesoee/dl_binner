#!/usr/bin/env python3
"""Close one serial workflow milestone without replaying a verified science stage.

Probe-completed caches do not satisfy these independent ordering milestones.
Every child must exit zero and its exact existing/new stage seal must verify.
"""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e024_control import verify_seal


def order():
    """Return the barrier and all three-mode stages in one fixed order."""
    from e036_control import UNITS,STAGES
    return [(None,'barrier')]+[(u,s)for u in UNITS for s in STAGES]


def verify_existing(p):
    """Refuse a missing predecessor, changed seal or foreign dispatch milestone."""
    root=Path(p['work']);seen=set()
    for f in sorted((root/'dispatch').glob('*.json')):
        r=json.loads(f.read_text());j=int(f.stem)
        if not 0<=j<len(order())or j!=len(seen):raise ValueError('Dispatch milestones are not a contiguous serial prefix')
        u,s=order()[j];target=root/'barrier'if u is None else root/u/s
        verify_seal(target)
        if r!=dict(status='PASS',ordinal=j,unit=u,stage=s,science_seal=binding(target/'done.json'),child_exit=0):raise ValueError('Dispatch seal/source differs')
        seen.add(j)
    return len(seen)


def run(plan,ordinal,engineering=False):
    """Execute/verify one actual worker and publish a separate serial closure."""
    from e036_control import read_plan
    p=read_plan(plan,engineering);root=Path(p['work']);existing=verify_existing(p)
    if not 0<=ordinal<len(order())or ordinal!=existing:raise ValueError('Dispatch requires exactly the next serial milestone')
    u,s=order()[ordinal];argv=[p['python'],'-I','-B',p['worker'],'--plan',str(plan),'--stage',s]
    if u:argv+=['--unit',u]
    if engineering:argv+=['--engineering']
    subprocess.run(argv,check=True)
    target=root/'barrier'if u is None else root/u/s;verify_seal(target)
    out=root/'dispatch';out.mkdir(exist_ok=True)
    write(out/('%03d.json'%ordinal),dict(status='PASS',ordinal=ordinal,unit=u,stage=s,science_seal=binding(target/'done.json'),child_exit=0))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--ordinal',type=int,required=True);p.add_argument('--engineering',action='store_true');a=p.parse_args();run(a.plan,a.ordinal,a.engineering)
