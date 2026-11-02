#!/usr/bin/env python3
"""Freeze only the prospective paired orchestration; preserve original E031 locks.

No fit, evaluation or cloud action. Product bytes, original scientific dispatch,
loss/defaults, admitted input units and both construction policies must remain
unchanged. Re-freezing after the first new community learner outcome is forbidden.
"""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).absolute().parents[1]
EXP=ROOT/'experiments/E031-bootstrap-preserving-learning'
AMENDED=['scripts/e031_control.py','scripts/e031_phase.py','scripts/e031_gates.py','scripts/e031_review.py']
NEW=['scripts/e031_paired.py','scripts/e031_paired_tiny.py','scripts/e031_paired_collect.py',
     'scripts/e031_learner_launch.py','scripts/e031_native_review.py','scripts/e031_neighbors.py',
     'scripts/e031_stream_return.py','scripts/e031_inspection.py','scripts/e031_summary.py',
     'scripts/e031_freeze_paired.py','tests/test_e031_followthrough.py',
     'experiments/E031-bootstrap-preserving-learning/paired-plan.json',
     'experiments/E031-bootstrap-preserving-learning/paired.smk',
     'experiments/E031-bootstrap-preserving-learning/paired-execution-policy.json']


def binding(path):
    """Bind the exact regular source bytes before a separately admitted execution."""
    p=Path(path)
    return dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def freeze():
    """Refuse product, scientific dispatch, default, or original unit changes."""
    old=json.loads((EXP/'source-lock.json').read_text())
    for name,wanted in old['files'].items():
        if name not in AMENDED and binding(ROOT/name)!=wanted:
            raise ValueError('Original frozen scientific source changed: '+name)
    text=(ROOT/'scripts/e031_control.py').read_text()
    original=subprocess.check_output(['git','show','58d7d59e892304ad20efcf784e61288e8a7d4967:scripts/e031_control.py'],cwd=ROOT,text=True)
    def stage_source(value):
        node=next(n for n in ast.parse(value).body if isinstance(n,ast.FunctionDef)and n.name=='stage')
        return ast.get_source_segment(value,node)
    if stage_source(text)!=stage_source(original):
        raise ValueError('Original scientific stage source bytes changed')
    original_stage_source_sha256=hashlib.sha256(stage_source(original).encode()).hexdigest()
    science=json.loads((EXP/'science-lock.json').read_text())
    p=json.loads((EXP/'paired-plan.json').read_text())
    if p['units']!=science['units']['learning'] or p['comparison']!='learning':
        raise ValueError('Original learner inputs changed')
    result=dict(kind='Prospective paired learner source supplement; original locks preserved',
        original_source='58d7d59e892304ad20efcf784e61288e8a7d4967',
        amended_operational_files=AMENDED,files={n:binding(ROOT/n)for n in AMENDED+NEW},
        original_frozen_source=binding(EXP/'source-lock.json'),
        original_science=binding(EXP/'science-lock.json'),product_bytes_changed=False,
        original_stage_dispatch_changed=False,original_stage_source_sha256=original_stage_source_sha256,
        legacy_AST_fingerprint_preserved=True,portable_guard='Exact original source text; AST dumps differ across Python versions',
        truth_or_loss_or_default_changed=False,
        owner_authorization='November 2: both constructors across all three modes after operational/data gates, regardless of bridge score')
    (EXP/'paired-source-lock.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    result=freeze();print('Paired source frozen:',len(result['files']),'files; original science unchanged')
