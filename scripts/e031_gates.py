#!/usr/bin/env python3
"""Fresh native E031 wheel/runtime/reader/serial-DAG gates under the held clock.

Accepted dependency setup is verified read-only, not reinstalled. No community
fit or grouping is released here. Tiny fits use only generated engineering DNA.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e031_control import freeze,verify_inputs,product_scope
from e024_coverage import binding,write
from e021_control_json import publish
from e009_owner import supervisor
from e023_gates import workflow_probe
from e029_gates import unit_command


def run(config):
    """Verify source, the complete accepted runtime and actual changed native paths."""
    cfg=json.loads(Path(config).read_text());p=json.loads(Path(cfg['plan']).read_text());root=Path(cfg['root'])
    out=root/'gates';out.mkdir(exist_ok=False);write(out/'source.json',freeze())
    reuse=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/reuse-lock.json').read_text())
    base=reuse['native_dependency_base'];deadline=cfg['vm_start_epoch']+2700
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),
        TMPDIR=str(root/'tmp'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    stages=[]
    def command(label,argv):
        remaining=deadline-time.time()
        if remaining<30:raise TimeoutError('Original native setup clock exhausted')
        try:result=sup.supervise(list(map(str,argv)),out/(label+'.log'),remaining,26_000_000_000,env,sample_root=os.getpid())
        except BaseException:
            receipt=out/(label+'.exit.json')
            stages.append(dict(stage=label,resources=json.loads(receipt.read_text()) if receipt.exists() else dict(exit_code=None)))
            write(out/'failed-stages.json',stages);raise
        stages.append(dict(stage=label,resources=result))
    command('workflow-origin',[p['workflow_python'],'-I','-B','-c',workflow_probe('3.12.10','9.16.3')])
    candidate=ROOT/'experiments/E031-bootstrap-preserving-learning/candidate-lock.json'
    if binding(p['wheel'])!=json.loads(candidate.read_text())['wheel']:raise ValueError('Native wheel differs')
    command('package-install',[base+'/bin/python','-I','-B',ROOT/'scripts/e019_runtime.py','create','--base',base,
        '--destination',root/'env','--wheel',p['wheel'],'--output',out/'package-install.json'])
    command('owned-complete-runtime',[p['python'],'-I','-B',ROOT/'scripts/e027_runtime.py','--base',base,
        '--reference',reuse['native_runtime_reference'],'--candidate-lock',candidate,'--output',out/'runtime.json'])
    command('installed-state-pair-reader-export',[p['python'],'-I','-B','-c',unit_command(ROOT,'test_bootstrap')])
    for comparison in ['bridge','learning']:
        command('serial-'+comparison+'-tiny-DAG',[p['python'],'-I','-B',ROOT/'scripts/e031_tiny.py','--root',out/('tiny-'+comparison),
            '--workflow-python',p['workflow_python'],'--comparison',comparison])
    if p['comparison']=='learning':
        command('synthetic-full-batch-kernels',[p['python'],'-I','-B',ROOT/'scripts/e031_probe.py','--output',out/'kernel-probe.json'])
        probe=json.loads((out/'kernel-probe.json').read_text())
        resources=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/resources.json').read_text())
        fit=max(sum(probe['projected_training_seconds_with_50_percent_IO_headroom'].values()),
                sum(resources['retained_training_seconds'].values())*1.5)
        forecast=fit+resources['learning_nontraining_seconds_upper']
        remaining=cfg['vm_start_epoch']+p['limits']['seconds']-time.time()-900
        write(out/'complete-schedule.json',dict(status='PASS' if forecast<=remaining else 'REFUSED',
            forecast_remaining_seconds=forecast,actual_remaining_seconds=remaining,
            scope='Synthetic native kernels + retained real-bank floor + complete downstream/collection allowance; not a guarantee'))
        if forecast>remaining:raise ValueError('Complete native learning schedule needs a prospective covered envelope revision')
    command('restore-complete-inputs',[p['python'],'-I','-B',ROOT/'scripts/e031_gates.py','--inputs',cfg['plan'],'--output',out/'data.json'])
    if not all(x['resources']['exit_code']==0 for x in stages):raise ValueError('Native gate failed')
    publish(dict(status='PASS',config=binding(config),stages=stages,finished_epoch=time.time(),source=freeze(),
        accepted_dependencies_reused=True,dependency_reinstall_or_science_recopy=False),out/'completion.json')


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--config',type=Path);a.add_argument('--inputs',type=Path);a.add_argument('--output',type=Path);v=a.parse_args()
    if v.config:run(v.config)
    elif v.inputs:product_scope();verify_inputs(json.loads(v.inputs.read_text()),v.output)
    else:a.error('Choose native gates or restore-only input admission')
