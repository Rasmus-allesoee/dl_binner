#!/usr/bin/env python3
"""Verify/reuse the failed E036 allocation; preserve only its unsealed journal stage.

No install, copy fallback, old fit, extraction or new scientific rule is exposed.
The original deadline and all accepted cache/stage bytes remain authoritative.
"""
import argparse,json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e024_control import verify_seal


def prepare_layout(c):
    """Create the actual snapshot contract and link its immutable original plan."""
    root=Path(c['root']);plan=Path(c['plan'])
    if plan.is_symlink()or not plan.is_file():raise ValueError('Regular retained science plan required')
    root.mkdir(parents=True,exist_ok=False)
    for n in ['logs','gates','payload','tmp']:(root/n).mkdir()
    os.link(plan,root/'science-plan.json')
    if binding(root/'science-plan.json')!=binding(plan):raise ValueError('Snapshot science-plan companion differs')
    return root


def verify(config):
    """Require passed original gates/caches and move one failed partial aside once."""
    c=json.loads(Path(config).read_text());r=c['financial']['recovery'];old=Path(r['original_root']);root=Path(c['root'])
    before=json.loads((old/'config.json').read_text())
    if before['vm_start_epoch']!=c['vm_start_epoch']or before['source_commit']!=r['original_source']or before['plan']!=c['plan']or before['task_filesystem']!=c['task_filesystem']or before['initial_filesystem_used_bytes']!=c['initial_filesystem_used_bytes']:raise ValueError('Original common clock/task/cache identity differs')
    gates={}
    for n in ['owned-package-install','complete-native-runtime','original-inputs-before','actual-native-tiny','restore-pooled','restore-baseline','restore-bootstrap','restore-measurements','full-native-admission']:
        p=old/'logs'/(n+'.exit.json');q=json.loads(p.read_text())
        if q['exit_code']!=0 or q['stop_reason']is not None:raise ValueError('Original gate not passed: '+n)
        gates[n]=binding(p)
    if json.loads((old/'gates/inputs-before.json').read_text())!=json.loads((old/'gates/inputs-after.json').read_text()):raise ValueError('Original protected input after-proof differs')
    p=json.loads(Path(c['plan']).read_text());work=Path(p['work']);seals={}
    for f in work.rglob('done.json'):
        verify_seal(f.parent);seals[str(f.relative_to(work))]=binding(f)
    partial=work/'oral-noGLM/student-embed';preserved=Path(c['task_filesystem'])/('failed-stage-'+r['original_source'][:7])
    if partial.exists():
        if (partial/'done.json').exists():raise ValueError('Never move an accepted stage')
        if preserved.exists():raise ValueError('Original failed stage already preserved; inspect before reuse')
        files={str(f.relative_to(partial)):binding(f)for f in partial.rglob('*')if f.is_file()}
        partial.rename(preserved)
        if any(binding(preserved/n)!=b for n,b in files.items()):raise ValueError('Failed stage preservation differs')
    elif preserved.exists():files={str(f.relative_to(preserved)):binding(f)for f in preserved.rglob('*')if f.is_file()}
    else:raise ValueError('Expected failed-stage journal unavailable')
    q=dict(status='PASS_VERIFIED_REUSE',old_gate_exits=gates,existing_scientific_seals=seals,failed_stage_preserved=dict(path=str(preserved),files=files),old_science_replayed=False,deadline_unchanged=c['review_deadline_epoch'],epoch=time.time())
    write(root/'gates/reuse.json',q);return q

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);a=p.parse_args();verify(a.config)
