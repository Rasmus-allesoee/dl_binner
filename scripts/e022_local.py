#!/usr/bin/env python3
"""Run a fresh bounded local E022 engineering attempt with persistent evidence.

The first invocation starts one 90-minute wall clock for setup/checks/collection;
later attempts reuse it. Four numerical threads, 8 GB sampled tree RSS and 4 GiB
new files are enforced. This helper has no cloud or community-data operation.
"""
import argparse
import json
import os
from pathlib import Path
import signal
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_owner import supervisor
from e021_control_json import publish


def used(root):
    """Count owned regular bytes, excluding read-only borrowed dependency links."""
    total = 0
    for base, folders, names in os.walk(root, followlinks=False):
        folders[:] = [n for n in folders if not (Path(base)/n).is_symlink()]
        total += sum((Path(base)/n).stat().st_size for n in names if not (Path(base)/n).is_symlink())
    return total


def main():
    """Execute one argv and retain real native failures without resetting the clock."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True); p.add_argument('--label', required=True)
    p.add_argument('command', nargs=argparse.REMAINDER); a = p.parse_args()
    root = a.root.absolute(); root.mkdir(parents=True, exist_ok=True)
    if not a.command or Path(a.label).name != a.label: raise ValueError('Explicit safe label/argv required')
    command = a.command[1:] if a.command[0] == '--' else a.command
    clock_path = root/'engineering-clock.json'
    if not clock_path.exists(): publish(dict(start_epoch=time.time(),seconds=5400,baseline_bytes=used(root)),clock_path)
    clock = json.loads(clock_path.read_text()); deadline = clock['start_epoch']+clock['seconds']
    number = 1
    while (root/(a.label+'-'+str(number)+'.resources.json')).exists(): number += 1
    stem = root/(a.label+'-'+str(number)); result = dict(status='FAILED',command=command)
    stop = threading.Event(); reasons = []; samples = []
    def guard():
        from shutil import disk_usage
        extra = used(root)-clock['baseline_bytes']; free = disk_usage(root).free
        samples.append(dict(epoch=time.time(),extra_bytes=extra,free_bytes=free))
        if time.time() >= deadline or extra > 4*1024**3 or free < 6*1024**3:
            raise RuntimeError('Original E022 engineering clock/disk/reserve exceeded')
    def watch():
        while not stop.wait(2):
            try: guard()
            except BaseException as exc: reasons.append(repr(exc));os.kill(os.getpid(),signal.SIGALRM);return
    def alarm(signum,frame): raise TimeoutError(reasons[-1] if reasons else 'Original E022 engineering clock expired')
    signal.signal(signal.SIGALRM,alarm); signal.setitimer(signal.ITIMER_REAL,max(.001,deadline-time.time()))
    thread = threading.Thread(target=watch,daemon=True); thread.start()
    s = supervisor(); env = s.isolated_env(4)
    (root/'tmp').mkdir(exist_ok=True)
    env.update(NUMBA_NUM_THREADS='4', NUMBA_CACHE_DIR=str(root/'numba-cache'),
               TMPDIR=str(root/'tmp'),
               HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
    try:
        guard();result['resources']=s.supervise(command,stem.with_suffix('.log'),deadline-time.time(),8_000_000_000,env,sample_root=os.getpid())
        result['status']='SUCCESS'
    except BaseException as exc: result['error']=repr(exc);raise
    finally:
        stop.set();thread.join(3);signal.setitimer(signal.ITIMER_REAL,0)
        result.update(elapsed_original_seconds=time.time()-clock['start_epoch'],samples=samples,
                      extra_bytes=used(root)-clock['baseline_bytes'],clock=str(clock_path))
        publish(result,stem.with_suffix('.resources.json'));print('E022_ENGINEERING_ATTEMPT',stem.name,result['status'],flush=True)


if __name__=='__main__': main()
