#!/usr/bin/env python3
"""Bound local E026 tiny contracts with four threads, sampled 8 GB RSS and logs.

Only explicitly named engineering tests run. No accepted community, acquisition,
cloud API or truth evaluation is selected by this harness. Failed logs survive
in exclusive attempt directories; this is not an automatic retry controller.
"""
import argparse
import json
import hashlib
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e009_owner import supervisor


def run(output, python, modules, task='contracts', workflow_python=None):
    """Record exact isolated test argv and sampled child-tree usage in a fresh attempt."""
    output = Path(output).absolute(); output.mkdir(parents=True, exist_ok=False)
    allowed = {'test_e026_fusion', 'test_e026_operations', 'test_e025_cache_audit'}
    if not modules or any(name.split('.')[0] not in allowed for name in modules):
        raise ValueError('Only named tiny engineering contracts permitted')
    code = ('import sys,unittest;from pathlib import Path;r=Path('+repr(str(ROOT))+');'
            'sys.path[:0]=[str(r/"src"),str(r/"scripts"),str(r/"tests")];'
            'v=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames('
            +repr(modules)+'));sys.exit(not v.wasSuccessful())')
    compile(code, 'actual-isolated-E026-tests', 'exec')
    sup = supervisor(); env = sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4', NUMBA_CACHE_DIR=str(output/'jit'), TMPDIR=str(output/'tmp'))
    (output/'tmp').mkdir()
    started = time.time()
    common = ROOT/'artifacts/e026-calibrated-evidence-fusion/preparation/engineering-clock.json'
    clock = json.loads(common.read_text())
    remaining = clock['deadline_epoch']-started
    if remaining <= 10: raise TimeoutError('Common local engineering clock exhausted; record any justified revision first')
    before = shutil.disk_usage(ROOT)
    if before.free < 6*1024**3: raise ValueError('Measured local 6 GiB reserve unavailable; no cleanup inferred')
    sources = {}
    for path in [*ROOT.glob('src/dl_binner/calibrated/*.py'), *ROOT.glob('scripts/e026*.py'),
                 *ROOT.glob('tests/test_e026*.py')]:
        payload = path.read_bytes(); sources[str(path.relative_to(ROOT))] = dict(bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
    argv = [str(Path(python).absolute()), '-I', '-B', '-c', code]
    if task == 'tiny':
        if not workflow_python: raise ValueError('Explicit workflow runtime required')
        argv = [str(Path(python).absolute()), '-I', '-B', str(ROOT/'scripts/e026_tiny.py'),
                '--root', str(output/'tiny'), '--workflow-python', str(Path(workflow_python).absolute())]
    elif task == 'probe':
        argv = [str(Path(python).absolute()), '-I', '-B', str(ROOT/'scripts/e026_probe.py'),
                '--output', str(output/'probe.json')]
    (output/'command.json').write_text(json.dumps(dict(argv=argv, started_epoch=started,
        threads=4, RSS_bytes=8000000000, seconds=remaining, common_clock=clock, source_files=sources,
        disk_before=before._asdict(), scope='Tiny local engineering only'), indent=2)+'\n')
    try:
        value = sup.supervise(argv, output/'contracts.log', remaining, 8000000000, env)
    finally:
        after = shutil.disk_usage(ROOT)
        (output/'disk-after.json').write_text(json.dumps(dict(before=before._asdict(), after=after._asdict(),
            scope='Filesystem snapshots, not attributable peak disk usage'), indent=2)+'\n')
    (output/'completed.json').write_text(json.dumps(dict(status='PASS', resources=value), indent=2)+'\n')
    return value


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--python', required=True); p.add_argument('--modules', nargs='+', default=['test_e026_fusion'])
    p.add_argument('--task', choices=['contracts', 'tiny', 'probe'], default='contracts')
    p.add_argument('--workflow-python')
    a = p.parse_args(); print(json.dumps(run(a.output, a.python, a.modules, a.task, a.workflow_python)), flush=True)
