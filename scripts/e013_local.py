#!/usr/bin/env python3
"""One clock/disk-bounded local E013 cached comparison with explicit verified reuse.

No cloud interface or dependency installation exists. The original clock persists
across operational repairs; logs and failed attempts are never overwritten.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tarfile
import threading
import time
import traceback

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e009_owner import supervisor
from e013_control import REPO, EXP


def tree_bytes(root):
    """Count attributed experiment files, refusing links instead of following inputs."""
    total = 0
    for p in Path(root).rglob('*'):
        if p.is_symlink(): raise ValueError('Linked working-space member refused')
        try:
            if p.is_file(): total += p.stat().st_size
        except FileNotFoundError:
            continue
    return total


class OutputGuard:
    """Enforce the original parent clock and actual experiment output-space cap."""
    def __init__(self, root, seconds, cap):
        self.root, self.seconds, self.cap = Path(root), seconds, cap
        self.done = threading.Event(); self.peak = 0; self.reason = None

    def __enter__(self):
        if self.seconds <= 0: raise TimeoutError('Original cumulative E013 clock exhausted')
        if tree_bytes(self.root) > self.cap: raise RuntimeError('E013 extra working-space cap already exceeded')
        self.previous = signal.getsignal(signal.SIGALRM); self.previous_timer = signal.getitimer(signal.ITIMER_REAL)
        def expired(*_): raise TimeoutError(self.reason or 'Original cumulative E013 clock exhausted')
        signal.signal(signal.SIGALRM, expired); signal.setitimer(signal.ITIMER_REAL, self.seconds)
        def watch():
            while not self.done.wait(.2):
                try:
                    size = tree_bytes(self.root); self.peak = max(self.peak, size)
                    if size > self.cap: self.reason = 'E013 extra working-space cap exceeded'
                except BaseException as exc:
                    self.reason = 'E013 disk monitor failed: '+str(exc)
                if self.reason:
                    os.kill(os.getpid(), signal.SIGALRM); return
        self.thread = threading.Thread(target=watch, daemon=True); self.thread.start(); return self

    def __exit__(self, *_):
        self.done.set(); self.thread.join(timeout=2)
        self.peak = max(self.peak, tree_bytes(self.root))
        signal.setitimer(signal.ITIMER_REAL, 0); signal.signal(signal.SIGALRM, self.previous)
        if self.previous_timer[0]: signal.setitimer(signal.ITIMER_REAL, *self.previous_timer)


def verify_reuse(root, protocol, lock):
    """Verify successful original rule/output bytes before skipping accepted refinement."""
    root = Path(root); done = json.loads((root/'completed.json').read_text())
    if done['status'] != 'SUCCESS' or done['protocol'] != protocol or done['input_lock'] != lock:
        raise ValueError('Only successful same-rule/input E013 output can be reused')
    for key, name in [('partition', 'partition.json'), ('decisions', 'decisions.json'), ('alternatives', 'alternatives.json'),
                      ('quality_evidence', 'quality-evidence.json'), ('context_transforms', 'context-transforms.json'),
                      ('graph_audit', 'selected-graph-audit.json')]:
        if binding(root/name) != done[key]: raise ValueError('Reused E013 member differs: '+name)
    return dict(root=str(root), completed=binding(root/'completed.json'), no_refinement_repeat=True)


def collect(root, archive):
    """Seal closed records, sources and assignment/manifest evidence; verify every byte.

    Full DNA FASTAs remain in local exports, bound by included export manifests.
    The live parent terminal/final postcollection receipt are not archived as if
    closed payloads. Source/config snapshots are byte-bound separately.
    """
    root, archive = Path(root), Path(archive)
    paths = {p.relative_to(root).as_posix(): p for p in root.rglob('*') if p.is_file() and p.suffix != '.fna'}
    records = {n: binding(p) for n, p in paths.items()}
    sources = {}
    for p in list((REPO/'scripts').glob('e013_*.py'))+list(EXP.glob('*')):
        if p.is_file() and p.suffix in ['.py', '.json', '.md']:
            sources['source/'+p.relative_to(REPO).as_posix()] = p.read_bytes()
    for n, raw in sources.items(): records[n] = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    raw = (json.dumps(dict(files=records, excludes=['full DNA FASTAs (retained with manifest hashes)',
        'live parent terminal and postcollection receipt']), sort_keys=True, indent=2)+'\n').encode()
    inventory = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    with tarfile.open(archive, 'x:gz', compresslevel=6) as tar:
        for name, p in sorted(paths.items()): tar.add(p, arcname=name, recursive=False)
        for name, data in sources.items():
            info = tarfile.TarInfo(name); info.size = len(data); tar.addfile(info, io.BytesIO(data))
        info = tarfile.TarInfo('collection-inventory.json'); info.size = len(raw); tar.addfile(info, io.BytesIO(raw))
    seen = set(); logical = 0
    with tarfile.open(archive, 'r|gz') as tar:
        for member in tar:
            if not member.isfile() or member.name in seen: raise ValueError('Unsafe/duplicate E013 member')
            seen.add(member.name); h = hashlib.sha256(); size = 0
            with tar.extractfile(member) as stream:
                for block in iter(lambda: stream.read(1024**2), b''): h.update(block); size += len(block)
            if dict(bytes=size, sha256=h.hexdigest()) != (inventory if member.name == 'collection-inventory.json' else records[member.name]):
                raise ValueError('E013 archive readback differs: '+member.name)
            logical += size
    if seen != set(records)|{'collection-inventory.json'}: raise ValueError('E013 member set differs')
    for name, p in paths.items():
        if binding(p) != records[name]: raise ValueError('E013 closed source changed during collection')
    (archive.with_suffix(archive.suffix+'.sha256')).write_text(binding(archive)['sha256']+'  '+archive.name+'\n')
    return dict(archive=binding(archive), local_path=str(archive), inventory=inventory, regular_members=len(seen),
                logical_member_bytes=logical, every_member_readback=True, cloud_upload=False, full_DNA_retained_locally=True)


def execute(output, reuse=None):
    """Run cached control/review/collection under one original 30-minute parent clock."""
    output = Path(output); output.mkdir(parents=True, exist_ok=False); started = time.monotonic()
    state = dict(status='FAILED', source_commit=None, stages=[], error=None, new_cloud_cost_usd=0)
    guard = None
    try:
        protocol = json.loads((EXP/'protocol.json').read_text()); budget = protocol['resources']
        top = REPO/'artifacts/e013-marker-quality'; clock_path = top/'clock.json'
        if not clock_path.exists(): write_json(clock_path, dict(started_epoch=time.time(), seconds=budget['cumulative_seconds']))
        clock = json.loads(clock_path.read_text())
        if clock['seconds'] != budget['cumulative_seconds']: raise ValueError('Original clock budget differs')
        deadline = clock['started_epoch']+clock['seconds']
        with OutputGuard(top, deadline-time.time(), budget['extra_working_bytes']) as guard:
            state['source_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, cwd=REPO).strip()
            if subprocess.check_output(['git', 'status', '--porcelain'], text=True, cwd=REPO).strip():
                raise ValueError('Exact source/protocol must be committed clean before E013 outcomes')
            write_json(output/'source.json', dict(commit=state['source_commit'], protocol=binding(EXP/'protocol.json'),
                scripts={p.name: binding(p) for p in (REPO/'scripts').glob('e013_*.py')},
                clock=binding(clock_path), numerical_threads=budget['threads'], system=os.uname().sysname,
                note='New research refiner uses immutable installed dev4 I/O/runtime; no product CLI mutation'))
            control = Path(reuse) if reuse else output/'control'; state['control'] = str(control)
            if reuse: write_json(output/'reused-control.json', verify_reuse(control, binding(EXP/'protocol.json'), binding(EXP/'input-lock.json')))
            stages = ([] if reuse else [('control', 'e013_control.py', ['--output', str(control)])])
            stages += [('review', 'e013_review.py', ['--root', str(control), '--output', str(output/'review')])]
            sup = supervisor(); env = sup.isolated_env(budget['threads'])
            python = REPO/'artifacts/e010-coherent-prototype/envs/candidate-dev4-v3/bin/python'
            for name, script, args in stages:
                print('E013_STAGE '+name, flush=True)
                receipt = sup.supervise([python, '-I', '-B', REPO/'scripts'/script, *args], output/(name+'.log'),
                    deadline-time.time(), budget['ram_bytes'], env, sample_root=os.getpid())
                state['stages'].append(dict(stage=name, receipt=receipt))
            write_json(output/'science-completed.json', dict(status='SUCCESS', stages=state['stages'],
                source_commit=state['source_commit'], control=str(control), clock=binding(clock_path)))
            state['collection'] = collect(output, top/('evidence-'+output.name+'.tar.gz'))
            write_json(output/'collection.json', state['collection'])
            state['status'] = 'SUCCESS'
    except BaseException as exc:
        state['error'] = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__)); raise
    finally:
        state['wall_seconds'] = time.monotonic()-started
        state['peak_sampled_working_bytes'] = guard.peak if guard else None
        write_json(output/'attempt.json', state)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--reuse-control', type=Path); a = p.parse_args(); execute(a.output, a.reuse_control)
