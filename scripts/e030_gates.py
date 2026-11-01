#!/usr/bin/env python3
"""Fresh installed/native candidate gates within the original held E030 clock."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e030_control import freeze,verify_inputs,product_scope
from e024_coverage import binding,write
from e021_control_json import publish
from e009_owner import supervisor
from e023_gates import workflow_probe
from e029_gates import unit_command


def run(config):
    """Reuse dependencies read-only; install only new product and test real paths."""
    cfg=json.loads(Path(config).read_text());p=json.loads(Path(cfg['plan']).read_text());root=Path(cfg['root']);out=root/'gates';out.mkdir(exist_ok=False)
    write(out/'source.json',freeze());reuse=json.loads((ROOT/'experiments/E030-supported-biological-bins/reuse-lock.json').read_text())
    base=reuse['native_dependency_base'];deadline=cfg['vm_start_epoch']+2700
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),TMPDIR=str(root/'tmp'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    stages=[]
    def command(label,argv):
        remaining=deadline-time.time()
        if remaining<30:raise TimeoutError('Original native setup clock exhausted')
        try:result=sup.supervise(list(map(str,argv)),out/(label+'.log'),remaining,26000000000,env,sample_root=os.getpid())
        except BaseException:
            receipt=out/(label+'.exit.json')
            stages.append(dict(stage=label,resources=json.loads(receipt.read_text()) if receipt.exists() else dict(exit_code=None)))
            write(out/'failed-stages.json',stages);raise
        stages.append(dict(stage=label,resources=result))
    command('workflow-origin',[p['workflow_python'],'-I','-B','-c',workflow_probe('3.12.10','9.16.3')])
    candidate=ROOT/'experiments/E030-supported-biological-bins/candidate-lock.json'
    if binding(p['wheel'])!=json.loads(candidate.read_text())['wheel']:raise ValueError('Native wheel differs')
    command('package-install',[base+'/bin/python','-I','-B',ROOT/'scripts/e019_runtime.py','create','--base',base,'--destination',root/'env','--wheel',p['wheel'],'--output',out/'package-install.json'])
    command('owned-complete-runtime',[p['python'],'-I','-B',ROOT/'scripts/e027_runtime.py','--base',base,'--reference',reuse['native_runtime_reference'],'--candidate-lock',candidate,'--output',out/'runtime.json'])
    command('installed-construction',[p['python'],'-I','-B','-c',unit_command(ROOT,'test_supported_construction')])
    write(out/'construction-contracts.json',dict(status='PASS',resources=stages[-1]['resources'],actual_sparse_profile_marker_selection_reload_export=True))
    command('serial-cached-tiny-DAG',[p['python'],'-I','-B',ROOT/'scripts/e030_tiny.py','--root',out/'tiny-DAG','--workflow-python',p['workflow_python']])
    command('restore-complete-inputs',[p['python'],'-I','-B',ROOT/'scripts/e030_gates.py','--inputs',cfg['plan'],'--output',out/'data.json'])
    command('synthetic-shape-runtime',[p['python'],'-I','-B',ROOT/'scripts/e030_probe.py','--output',out/'schedule.json'])
    if not all(x['resources']['exit_code']==0 for x in stages):raise ValueError('Native gate failed')
    publish(dict(status='PASS',config=binding(config),stages=stages,finished_epoch=time.time(),source=freeze(),
        accepted_setup_reused=True,no_dependency_install_or_science_recopy=True,owned_package_install_explicit=True),out/'completion.json')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path);p.add_argument('--inputs',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.config:run(a.config)
    elif a.inputs:product_scope();verify_inputs(json.loads(a.inputs.read_text()),a.output)
    else:p.error('Select gates or restore-only input inventory')
