#!/usr/bin/env python3
"""Run a logged tiny local engineering command under one recorded task clock.

Four numerical threads, 8 GB sampled process-tree RSS, 4 GiB total owned preparation files and
6 GiB filesystem reserve. This helper has no VM/cloud or community-data selector.
Fresh labels preserve failures; it never resets the common engineering clock.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import sys
import threading
import time

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e009_owner import supervisor
from e024_coverage import write


def owned_bytes(root):
    """Count regular owned files, ignoring borrowed dependency links."""
    total = 0
    for base, folders, files in os.walk(root, followlinks=False):
        folders[:] = [n for n in folders if not (Path(base)/n).is_symlink()]
        for name in files:
            p = Path(base)/name
            try:
                if not p.is_symlink(): total += p.stat().st_size
            except FileNotFoundError:
                pass  # A private temporary fixture can close while sampled.
    return total


def run(root, label, argv):
    """Supervise one explicit engineering argv and retain exact resource receipts."""
    root = Path(root).absolute(); clock = json.loads((root/'engineering-clock.json').read_text())
    if Path(label).name != label or not argv: raise ValueError('Explicit fresh label/argv required')
    out = root/label; out.mkdir(exist_ok=False); (out/'tmp').mkdir()
    remaining = clock['deadline_epoch']-time.time()
    if remaining <= 10 or shutil.disk_usage(root).free < 6*1024**3:
        raise ValueError('Common engineering clock/free-space reserve unavailable')
    sup = supervisor(); env = sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4', NUMBA_CACHE_DIR=str(out/'jit'), TMPDIR=str(out/'tmp'),
               HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    write(out/'command.json', dict(argv=argv, common_clock=clock, started_epoch=time.time(),
        threads=4, sampled_tree_RSS_bytes=8_000_000_000, filesystem_before=shutil.disk_usage(root)._asdict()))
    stop = threading.Event(); observations = []; failures = []
    def guard():
        value = dict(epoch=time.time(), owned_bytes=owned_bytes(root), free_bytes=shutil.disk_usage(root).free)
        observations.append(value)
        if value['owned_bytes'] > 4*1024**3 or value['free_bytes'] < 6*1024**3:
            raise RuntimeError('Local total-owned-byte/free-space guard exceeded')
    def watch():
        while not stop.wait(2):
            try: guard()
            except BaseException as exc:
                failures.append(repr(exc)); os.kill(os.getpid(), signal.SIGALRM); return
    def alarm(signum, frame): raise RuntimeError(failures[-1] if failures else 'Local engineering guard interrupted')
    signal.signal(signal.SIGALRM, alarm); thread = threading.Thread(target=watch, daemon=True)
    try:
        guard(); thread.start()
        result = sup.supervise(argv, out/'terminal.log', remaining, 8_000_000_000, env)
        guard()
        write(out/'completed.json', dict(status='PASS', resources=result))
        return result
    finally:
        stop.set()
        if thread.is_alive(): thread.join(3)
        write(out/'byte-observations.json', dict(samples=observations, failures=failures,
            baseline=0, scope='Conservative total owned preparation bytes including old attempts, not only new-command growth'))
        write(out/'filesystem-after.json', dict(epoch=time.time(), filesystem=shutil.disk_usage(root)._asdict(),
            scope='Filesystem snapshot, not attributable peak storage'))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, required=True)
    p.add_argument('--label', required=True); p.add_argument('command', nargs=argparse.REMAINDER); a = p.parse_args()
    command = a.command[1:] if a.command[:1] == ['--'] else a.command
    print(json.dumps(run(a.root, a.label, command)), flush=True)
