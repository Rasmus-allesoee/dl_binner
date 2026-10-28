#!/usr/bin/env python3
"""E025 native gates reuse existing independent environments without installation.

All commands are charged to the same new twelve-hour VM clock. Gates admit source,
runtime, actual retained data and the changed compiled retrieval/launcher paths;
they do not rebuild old science or claim full-scale biological performance.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
from e024_coverage import binding,write
from e024_gates import freeze as inherited_freeze
from e023_gates import workflow_probe
from e009_owner import supervisor


def freeze():
    """Verify new consumer locks and every immutable inherited science file."""
    inherited=inherited_freeze()
    lock=json.loads((ROOT/'experiments/E025-joint-distance-retrieval/source-lock.json').read_text())
    for name,wanted in lock['files'].items():
        if binding(ROOT/name)!=wanted:raise ValueError('Frozen E025 source differs: '+name)
    return dict(status='PASS',inherited=inherited,
                new=binding(ROOT/'experiments/E025-joint-distance-retrieval/source-lock.json'))


def unit_command(repo):
    """Compile the exact isolated Linux consumer rather than testing an in-process import."""
    code=('import sys,unittest;from pathlib import Path;r=Path('+repr(str(repo))+');'
          'sys.path[:0]=[str(r/"scripts"),str(r/"src"),str(r/"tests")];'
          'v=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames('
          '["test_e025_retrieval","test_e025_operations"]));sys.exit(not v.wasSuccessful())')
    compile(code,'E025-native-contracts','exec')
    return code


def run(config):
    """Run fresh changed native contracts, preserving any failed logs and clocks."""
    cfg=json.loads(Path(config).read_text());p=json.loads(Path(cfg['plan']).read_text())
    root=Path(cfg['root']);out=root/'gates';out.mkdir(exist_ok=False)
    write(out/'source.json',freeze())
    deadline=cfg['vm_start_epoch']+2700
    sup=supervisor();env=sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'gate-native-cache'),TMPDIR=str(root/'tmp'))
    stages=[]
    def command(label,argv):
        left=deadline-time.time()
        if left<60:raise TimeoutError('Original new 45-minute setup clock exhausted')
        value=sup.supervise(argv,out/(label+'.log'),left,26_000_000_000,env,sample_root=os.getpid())
        stages.append(dict(stage=label,resources=value))
    command('workflow-origin',[p['workflow_python'],'-I','-B','-c',workflow_probe('3.12.10','9.16.3')])
    old=json.loads((ROOT/'experiments/E023-adaptive-density-bins/reuse-lock.json').read_text())
    command('accepted-numerical',[p['python'],'-I','-B',str(ROOT/'scripts/e023_runtime.py'),
        '--reference',old['runtime_reference'],'--output',str(out/'runtime.json')])
    command('actual-compiled-consumer',[p['python'],'-I','-B','-c',unit_command(ROOT)])
    command('serial-tiny-DAG',[p['python'],'-I','-B',str(ROOT/'scripts/e025_tiny.py'),
        '--root',str(out/'tiny-DAG'),'--workflow-python',p['workflow_python']])
    command('synthetic-width-runtime',[p['python'],'-I','-B',str(ROOT/'scripts/e025_probe.py'),
        '--output',str(out/'schedule.json')])
    # Actual prior archive verification/readers are new stage verify, released
    # only after the byte-bound prelaunch data/expected axes contract is admitted.
    command('retained-data',[p['python'],'-I','-B',str(ROOT/'scripts/e025_gates.py'),
        '--inputs',cfg['plan'],'--output',str(out/'data.json')])
    write(out/'completion.json',dict(status='PASS',config=binding(config),stages=stages,
        original_start_epoch=cfg['vm_start_epoch'],finished_epoch=time.time(),source=freeze(),
        full_science_started=False,no_install_or_recopy=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path)
    p.add_argument('--inputs',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.config:run(a.config)
    elif a.inputs:
        from e025_control import verify_inputs
        write(a.output,dict(status='PASS',**verify_inputs(json.loads(a.inputs.read_text()))))
    else:p.error('Select native gates or read-only retained-input admission')
