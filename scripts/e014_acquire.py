#!/usr/bin/env python3
"""Acquire only the frozen oral-GSA quartet with publisher MD5 and SHA256 receipts.

Streaming transfers preserve partial files and closed failures. Existing completed
files require their receipts and complete byte verification; there is no fallback
download or implicit retry. A persistent 90-minute acquisition/validation clock,
10-GiB experiment-space cap and 5-GiB filesystem reserve bound this local block.
No read sets, BAMs, reference collection or cloud interface is included.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time
import urllib.request

REPO = Path(__file__).absolute().parents[1]
ROOT = REPO/'artifacts/e014-multiview-reconstruction'


def hashes(path):
    """Return streamed byte count, SHA256 and legacy publisher-check MD5."""
    sha, md5, size = hashlib.sha256(), hashlib.md5(), 0
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024**2), b''):
            sha.update(b); md5.update(b); size += len(b)
    return dict(bytes=size, sha256=sha.hexdigest(), md5=md5.hexdigest())


def guard(root, clock):
    """Refuse an expired original clock, unsafe links, excess output or low disk."""
    if time.time()-clock['started_epoch'] >= clock['seconds']:
        raise TimeoutError('Original E014 acquisition/validation clock exhausted')
    total = 0
    for p in Path(root).rglob('*'):
        if p.is_symlink(): raise ValueError('E014 output link refused')
        if p.is_file(): total += p.stat().st_size
    if total > 10*1024**3: raise RuntimeError('E014 10-GiB extra-space cap exceeded')
    if shutil.disk_usage(root).free < 5*1024**3: raise RuntimeError('E014 5-GiB free local reserve reached')
    return total


def acquire(root=ROOT, plan=None):
    """Download the fixed files once; seal receipts after exact size/hash readback."""
    root=Path(root); root.mkdir(parents=True, exist_ok=True)
    plan=plan or json.loads((REPO/'experiments/E014-multiview-reconstruction/acquisition-lock.json').read_text())
    clock_path=root/'acquisition-clock.json'
    if not clock_path.exists():
        clock_path.write_text(json.dumps(dict(started_epoch=time.time(), seconds=5400))+'\n')
    clock=json.loads(clock_path.read_text()); peak=guard(root,clock)
    receipts=[]; start=time.monotonic()
    for item in plan['files']:
        target=root/'oral'/Path(item['path']).name;target.parent.mkdir(exist_ok=True)
        receipt=target.with_suffix(target.suffix+'.receipt.json')
        if target.exists():
            if not receipt.exists(): raise ValueError('Unreceipted complete file refused: '+str(target))
            old=json.loads(receipt.read_text());actual=hashes(target)
            if old['hashes']!=actual or actual['md5']!=item['md5'] or actual['bytes']!=item['bytes']:
                raise ValueError('Completed acquisition bytes differ: '+str(target))
            receipts.append(old);print('VERIFIED_REUSE',target.name,flush=True);continue
        partial=target.with_suffix(target.suffix+'.partial')
        sha, md5, size=hashlib.sha256(),hashlib.md5(),0
        # Explicit repair can resume partial transport bytes, never accepted science.
        if partial.exists():
            if not plan.get('resume_partial',False): raise ValueError('Partial exists; explicit repair/resume required')
            with partial.open('rb') as f:
                for b in iter(lambda:f.read(1024**2),b''):sha.update(b);md5.update(b);size+=len(b)
        if size>item['bytes']: raise ValueError('Oversized partial transfer refused')
        headers={'Range':f'bytes={size}-'} if size else {}
        req=urllib.request.Request(plan['base_url']+item['path'],headers=headers)
        then=time.monotonic()
        with urllib.request.urlopen(req,timeout=45) as response:
            if size and (response.status!=206 or not response.headers.get('Content-Range','').startswith(f'bytes {size}-')):
                raise ValueError('Server did not honor explicit partial resume')
            if int(response.headers['Content-Length']) != item['bytes']-size:
                raise ValueError('Publisher length differs from frozen HEAD')
            with partial.open('ab' if size else 'xb') as stream:
                for block in iter(lambda:response.read(1024**2),b''):
                    size+=len(block)
                    if size>item['bytes']:raise ValueError('Oversized response refused')
                    stream.write(block);sha.update(block);md5.update(block)
                    if time.monotonic()-then>=5:
                        stream.flush();peak=max(peak,guard(root,clock));then=time.monotonic()
                        print(json.dumps(dict(stage='download',file=target.name,bytes=size,total=item['bytes'],epoch=time.time())),flush=True)
        actual=dict(bytes=size,sha256=sha.hexdigest(),md5=md5.hexdigest())
        if actual['md5']!=item['md5'] or size!=item['bytes']:raise ValueError('Publisher checksum/size mismatch: '+target.name)
        partial.rename(target)
        if hashes(target)!=actual:raise ValueError('Independent acquisition readback mismatch')
        rec=dict(path=str(target),url=req.full_url,hashes=actual,completed_epoch=time.time())
        receipt.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n');receipts.append(rec)
        peak=max(peak,guard(root,clock));print('ACQUIRED',target.name,actual,flush=True)
    result=dict(status='SUCCESS',files=receipts,seconds=time.monotonic()-start,clock=clock,
                peak_sampled_working_bytes=peak,body_bytes=sum(r['hashes']['bytes'] for r in receipts))
    (root/'acquisition.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args()
    try:acquire(a.root)
    except BaseException as exc:
        fail=a.root/('acquisition-failure-'+str(time.time_ns())+'.json')
        fail.write_text(json.dumps(dict(error=repr(exc),epoch=time.time()),indent=2)+'\n')
        raise
