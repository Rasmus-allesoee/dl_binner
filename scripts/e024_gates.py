#!/usr/bin/env python3
"""Future Linux source/runtime/readers and actual tiny E024 admission gates.

Reuse the E023 accepted complete numerical environment; no installer or fresh
scientific feature/marker generation is available. All commands are charged to
the first VM-start clock, inside a one-hour setup sublimit. This script does not
start a VM, publish science release or replace a failed runtime/cache.
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
from e023_gates import workflow_probe
from e009_owner import supervisor


def freeze():
    """Verify new preparation and immutable inherited E023 scientific source bytes."""
    for path in ['experiments/E024-oral-measured-coverage/source-lock.json',
                 'experiments/E023-adaptive-density-bins/source-lock.json']:
        lock=json.loads((ROOT/path).read_text())
        for name,wanted in lock['files'].items():
            if binding(ROOT/name)!=wanted:raise ValueError('Source/policy bytes differ: '+name)
    return dict(status='PASS',new=binding(ROOT/'experiments/E024-oral-measured-coverage/source-lock.json'),
                immutable=binding(ROOT/'experiments/E023-adaptive-density-bins/source-lock.json'))


def readers(plan,output):
    """Read complete retained oral axes/geometry/markers without any new inference."""
    from dl_binner.information.grouping import load_inputs
    from dl_binner.density.grouping import sparse_input
    p=json.loads(Path(plan).read_text());u=p['inputs']
    data,x,valid,meta=load_inputs(u['features'],u['embeddings'])
    sparse_input(u['graph'],data['ids'].tolist(),valid,u['embeddings'])
    evidence=json.loads(Path(u['marker_evidence']).read_text())
    if (meta['samples'] or len(data['ids'])!=1286547 or int(data['lengths'].sum())!=1669981123
            or int(valid.sum())!=508763 or not set(evidence['calls'])<=set(data['ids'].tolist())):
        raise ValueError('Full oral native axes/physical marker input differs')
    write(output,dict(status='PASS_FULL_READERS_NO_SCIENCE',contigs=len(data['ids']),bp=int(data['lengths'].sum()),
                      eligible=int(valid.sum()),samples=meta['samples'],vectors=x.shape))


def unit_command(repo):
    """Render/compile the exact isolated Linux unittest consumer before a paid start."""
    code=('import sys,unittest;from pathlib import Path;r=Path('+repr(str(repo))+');'
          'sys.path[:0]=[str(r/"scripts"),str(r/"src"),str(r/"tests")];'
          's=unittest.defaultTestLoader.loadTestsFromNames(["test_e024_coverage","test_e024_operations"]);'
          'v=unittest.TextTestRunner(verbosity=2).run(s);sys.exit(not v.wasSuccessful())')
    compile(code,'E024-native-unit-command','exec')
    return code


def run(config):
    """Run source, complete runtime, axes, native tiny and serial collection gates."""
    cfg=json.loads(Path(config).read_text());p=json.loads(Path(cfg['plan']).read_text())
    root=Path(cfg['root']);out=root/'gates';out.mkdir(exist_ok=False)
    write(out/'source.json',freeze())
    inherited=json.loads((ROOT/'experiments/E023-adaptive-density-bins/reuse-lock.json').read_text())
    deadline=cfg['vm_start_epoch']+3600
    s=supervisor();env=s.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'gate-native-cache'),TMPDIR=str(root/'tmp'),
               E024_MAPPER=p['mapper'],E024_SAMTOOLS=p['samtools'])
    stages=[]
    def command(label,argv):
        remaining=deadline-time.time()
        if remaining<30:raise TimeoutError('Original one-hour native setup gate exhausted')
        r=s.supervise(argv,out/(label+'.log'),remaining,26_000_000_000,env,sample_root=os.getpid())
        stages.append(dict(stage=label,resources=r))
    command('workflow-origin',[p['workflow_python'],'-I','-B','-c',workflow_probe('3.12.10','9.16.3')])
    command('accepted-numerical',[p['python'],'-I','-B',str(ROOT/'scripts/e023_runtime.py'),
        '--reference',inherited['runtime_reference'],'--output',str(out/'runtime.json')])
    command('full-retained-readers',[p['python'],'-I','-B',str(ROOT/'scripts/e024_gates.py'),
        '--readers',cfg['plan'],'--output',str(out/'readers.json')])
    command('actual-native-contracts',[p['python'],'-I','-B','-c',unit_command(ROOT)])
    command('serial-tiny-DAG',[p['python'],'-I','-B',str(ROOT/'scripts/e024_tiny.py'),
        '--root',str(out/'tiny-DAG'),'--workflow-python',p['workflow_python']])
    write(out/'completion.json',dict(status='PASS',config=binding(config),stages=stages,
                                    original_start_epoch=cfg['vm_start_epoch'],finished_epoch=time.time(),
                                    full_science_started=False,source=freeze()))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path);parser.add_argument('--readers',type=Path);parser.add_argument('--output',type=Path)
    a=parser.parse_args()
    if a.config:run(a.config)
    elif a.readers:readers(a.readers,a.output)
    else:parser.error('Select native gates or full retained readers')
