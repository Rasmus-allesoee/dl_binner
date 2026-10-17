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
        if p.is_symlink():
            # Normal venv interpreter aliases are an explicitly retained runtime
            # dependency, not downloaded scientific payloads or new file bytes.
            if p.relative_to(root).parts[0]=='envs':continue
            raise ValueError('E014 scientific output link refused: '+str(p))
        if p.is_file(): total += p.stat().st_size
    if total > 10*1024**3: raise RuntimeError('E014 10-GiB extra-space cap exceeded')
    if shutil.disk_usage(root).free < 5*1024**3: raise RuntimeError('E014 5-GiB free local reserve reached')
    return total


def acquire(root=ROOT, plan=None, resume_partial=False):
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
            if not resume_partial: raise ValueError('Partial exists; explicit repair/resume required')
            with partial.open('rb') as f:
                for b in iter(lambda:f.read(1024**2),b''):sha.update(b);md5.update(b);size+=len(b)
        if size>item['bytes']: raise ValueError('Oversized partial transfer refused')
        then=time.monotonic()
        url=plan['base_url']+item['path']
        # Bounded independent range requests avoid a server's long-transfer
        # disconnect; this is transport, with one final whole-file checksum.
        while size<item['bytes']:
            ranged=url.startswith(('http://','https://'))
            end=min(item['bytes'],size+16*1024**2)-1 if ranged else item['bytes']-1
            headers={'Range':f'bytes={size}-{end}'} if ranged else {}
            req=urllib.request.Request(url,headers=headers);begin=size
            with urllib.request.urlopen(req,timeout=45) as response, partial.open('ab' if partial.exists() else 'xb') as stream:
                if ranged and (response.status!=206 or not response.headers.get('Content-Range','').startswith(f'bytes {size}-{end}/')):
                    raise ValueError('Server did not honor bounded transfer range')
                if int(response.headers['Content-Length']) != end-size+1:raise ValueError('Publisher range length differs')
                for block in iter(lambda:response.read(1024**2),b''):
                    size+=len(block)
                    if size>item['bytes']:raise ValueError('Oversized response refused')
                    stream.write(block);sha.update(block);md5.update(block)
                    if time.monotonic()-then>=5:
                        stream.flush();peak=max(peak,guard(root,clock));then=time.monotonic()
                        print(json.dumps(dict(stage='download',file=target.name,bytes=size,total=item['bytes'],epoch=time.time())),flush=True)
            if size!=end+1:raise ValueError(f'Short transport range: {begin}-{end}, received through {size-1}')
        actual=dict(bytes=size,sha256=sha.hexdigest(),md5=md5.hexdigest())
        if actual['md5']!=item['md5'] or size!=item['bytes']:raise ValueError('Publisher checksum/size mismatch: '+target.name)
        partial.rename(target)
        if hashes(target)!=actual:raise ValueError('Independent acquisition readback mismatch')
        rec=dict(path=str(target),url=url,hashes=actual,completed_epoch=time.time())
        receipt.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n');receipts.append(rec)
        peak=max(peak,guard(root,clock));print('ACQUIRED',target.name,actual,flush=True)
    result=dict(status='SUCCESS',files=receipts,seconds=time.monotonic()-start,clock=clock,
                peak_sampled_working_bytes=peak,body_bytes=sum(r['hashes']['bytes'] for r in receipts))
    (root/'acquisition.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--resume-partial',action='store_true',help='Explicit verified-prefix transport recovery; original clock stays')
    a=p.parse_args()
    try:acquire(a.root,resume_partial=a.resume_partial)
    except BaseException as exc:
        fail=a.root/('acquisition-failure-'+str(time.time_ns())+'.json')
        fail.write_text(json.dumps(dict(error=repr(exc),epoch=time.time()),indent=2)+'\n')
        raise
