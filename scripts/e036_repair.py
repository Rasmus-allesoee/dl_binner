"""Admit only E036 journal-layout and serial-dispatch repairs, never science edits."""
import ast,json,subprocess
from pathlib import Path
import sys
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding
EXP=ROOT/'experiments/E036-optional-pooled-links'


def admit():
    """Verify preserved source plus an explicit operational overlay and stable stage identity."""
    original=EXP/'source-lock.json';old=json.loads(original.read_text());path=EXP/'repair-lock.json'
    if not path.exists():
        for n,b in old['files'].items():
            if binding(ROOT/n)!=b:raise ValueError('Original E036 source differs: '+n)
        return binding(original)
    r=json.loads(path.read_text())
    if r['parent_source_lock']!=binding(original):raise ValueError('Original E036 lock changed')
    if set(r['overrides'])!={'scripts/e036_control.py','scripts/e036_tiny.py','experiments/E036-optional-pooled-links/Snakefile'}:raise ValueError('Unknown operational repair scope')
    effective=dict(old['files'])
    for n,b in r['overrides'].items():
        if b['before']!=old['files'][n]:raise ValueError('Repair predecessor differs')
        effective[n]=b['after']
    for n,b in dict(effective,**r['extra_files']).items():
        if binding(ROOT/n)!=b:raise ValueError('Effective repair source differs: '+n)
    raw=subprocess.check_output(['git','show','7aa7bf7:scripts/e036_control.py'],cwd=ROOT,text=True)
    def functions(text):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    before,after=functions(raw),functions((ROOT/'scripts/e036_control.py').read_text())
    if set(before)!=set(after)or {n for n in before if before[n]!=after[n]}!={'freeze','fallback','workflow'}:raise ValueError('Repair changes more than journal copy/source/dispatch verification')
    # All product model/loss/defaults and stage/input/availability functions remain
    # exact. Return the original source-lock binding to verify accepted node seals.
    return binding(original)
