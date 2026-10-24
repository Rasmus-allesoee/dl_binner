#!/usr/bin/env python3
"""Exercise unchanged head/reload/group/refine/export on real relocated tiny banks.

Only the predeclared own-DNA engineering plan is accepted. Extraction and marker
redetection are unavailable here. Every subprocess uses its actual installed
runtime outside the checkout, with separate numerical/native library families.
"""
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path


def run(plan,repo,output):
    """Execute twelve real cached engineering stages and check their complete targets."""
    p=json.loads(Path(plan).read_text());repo=Path(repo);cfg=json.loads(Path(p['config']).read_text());base=Path(p['work']);records=[]
    if not cfg['epochs']==20 or cfg['seed']!=11 or cfg['batch_size']!=256 or cfg['min_bin_bp']!=1:raise ValueError('Predeclared own-DNA engineering scope required')
    def binding(path):
        path=Path(path);h=hashlib.sha256()
        with path.open('rb')as f:
            for b in iter(lambda:f.read(1048576),b''):h.update(b)
        return dict(bytes=path.stat().st_size,sha256=h.hexdigest())
    for unit in ['E009-hybrid','oral-hybrid']:
        for stage in ['train','embed','group','refine','export','graph-proof']:
            log=Path(output).parent/('tiny-'+unit+'-'+stage+'.log');argv=[p['python'],'-I','-B',str(repo/'scripts/e021_control.py'),'--plan',str(plan),'--unit',unit,'--stage',stage,'--engineering'];start=time.time();print('REAL_CACHED_TINY_STAGE',unit,stage,flush=True)
            with log.open('x')as f:q=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT,cwd=Path(plan).parent,env=os.environ.copy())
            records.append(dict(unit=unit,stage=stage,exit=q.returncode,seconds=time.time()-start,log=binding(log)));q.check_returncode()
        r=base/'units'/unit;checkpoint=json.loads((r/'train/checkpoint.json').read_text());bank=json.loads((r/'frozen/bank.json').read_text());graph=json.loads((r/'graph-proof.json').read_text());account=json.loads((r/'export/accounting.json').read_text())
        if len(checkpoint['history'])!=20 or checkpoint['training_parents']!=bank['eligible']or bank['status']!='COMPLETE'or graph['status']!='PASS'or set(account)!={'pre','old','post'}or binding(r/'train/reference.npz')!=binding(r/'embeddings.npz'):raise ValueError('Native engineering reload/cache/graph/export target failed')
    with Path(output).open('x')as f:json.dump(dict(status='PASS_REAL_NATIVE_CACHED_TINY_BOTH_MODES',records=records,extraction_repeated=False,markers_redetected=False,scope='Own synthetic DNA only, actual GPU-extracted exact-view banks, real cached CPU 20-epoch fits/native reload/graph/marker/refiner/full export; no community recovery score'),f,indent=2);f.write('\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--repo',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.plan,a.repo,a.output)
