#!/usr/bin/env python3
"""Bound all E012 local selection/audit/review work, preserving failed attempts.

Uses the existing process supervisor and independently owned frozen Mac runtime.
No cloud command is present. An operational repair needs a new attempt; successful
selection may be explicitly reused only with its completed byte-bound receipts.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e009_common import binding, write_json
from e009_owner import supervisor
from e012_acceptance import REPO, EXP


def verify_selection_reuse(selected):
    """Refuse missing/corrupt/failed selections before dispatching another consumer."""
    selected = Path(selected)
    done = json.loads((selected/'completed.json').read_text())
    if done['status'] != 'SUCCESS' or done['protocol'] != binding(EXP/'protocol.json'):
        raise ValueError('Only successful identical frozen selection can be reused')
    for context, record in done['contexts'].items():
        for name in ['partition', 'decisions']:
            if binding(selected/context/(name+'.json')) != record[name]:
                raise ValueError('Reused selection member differs')
    return dict(path=str(selected), receipt=binding(selected/'completed.json'), no_reselection=True)


def dispatch(output, reuse_selection, started, state):
    """Perform clock-bound prerequisites and actual serial children; update the journal state."""
    protocol = json.loads((EXP/'protocol.json').read_text()); limits = protocol['resources']
    python = REPO/'artifacts/e010-coherent-prototype/envs/candidate-dev4-v3/bin/python'
    sup = supervisor(); env = sup.isolated_env(limits['local_threads'])
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True, cwd=REPO).strip()
    state['source_commit'] = source
    if subprocess.check_output(['git', 'status', '--porcelain'], text=True, cwd=REPO).strip():
        raise ValueError('Commit exact clean source before community selection/diagnostics')
    write_json(output/'source.json', dict(commit=source, protocol=binding(EXP/'protocol.json'),
        scripts={p.name: binding(p) for p in (REPO/'scripts').glob('e012_*.py')},
        supervisor=binding(REPO/'src/dl_binner/supervision.py'), prefix=str(python.parent.parent),
        hostname=os.uname().nodename, system=os.uname().sysname, cpu_threads=limits['local_threads'], cloud_cost_usd=0))
    selected = Path(reuse_selection) if reuse_selection else output/'selection'
    state['selection'] = str(selected)
    if reuse_selection:
        # Selection receipt and every consumed partition are verified by reviewer;
        # refuse a failed/partial selection before scheduling any new diagnostics.
        write_json(output/'reused-selection.json', verify_selection_reuse(selected))
    stages = ([] if reuse_selection else [('selection', 'e012_acceptance.py', ['--output', str(selected)])])
    stages += [('marker-audit', 'e012_marker_audit.py', ['--output', str(output/'marker-audit')]),
               ('review', 'e012_review.py', ['--run', str(selected), '--output', str(output/'review')])]
    for name, script, args in stages:
        remaining = limits['total_control_seconds']-(time.monotonic()-started)
        if remaining <= 0:
            raise TimeoutError('Overall local clock expired')
        argv = [python, '-I', '-B', REPO/'scripts'/script, *args]
        print('E012_STAGE '+name, flush=True)
        receipt = sup.supervise(argv, output/(name+'.log'), min(limits['per_stage_seconds'], remaining),
                                limits['ram_bytes'], env, sample_root=os.getpid())
        state['stages'].append(dict(stage=name, receipt=receipt))


def execute(output, reuse_selection=None):
    """Journal even prerequisite failures, retaining each new attempt without overwriting."""
    started = time.monotonic(); output = Path(output); output.mkdir(parents=True, exist_ok=False)
    state = dict(status='FAILED', error=None, stages=[], source_commit=None, local_only=True,
                 cloud_cost_usd=0, selection=None)
    try:
        dispatch(output, reuse_selection, started, state)
        state['status'] = 'SUCCESS'
    except BaseException as exc:
        state['error'] = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        raise
    finally:
        state['wall_seconds'] = time.monotonic()-started
        write_json(output/'attempt.json', state)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--reuse-selection', type=Path)
    a = p.parse_args(); execute(a.output, a.reuse_selection)
