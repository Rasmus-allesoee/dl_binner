#!/usr/bin/env python3
"""Fresh isolated native restore/discovery gates under the same held VM clock."""
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e029_control import freeze,verify_inputs
from e024_coverage import binding,write
from e021_control_json import publish
from e009_owner import supervisor
from e023_gates import workflow_probe


def unit_command(repo,module):
    """Run installed product fixtures without checkout product imports or mixed backends."""
    code='import sys,unittest;from pathlib import Path;r=Path('+repr(str(repo))+');sys.path.insert(0,str(r/"tests/product"));v=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('+repr(module)+'));sys.exit(not v.wasSuccessful())'
    compile(code,'native-E029-unit','exec');return code


def run(config):
    """Reuse passed complete dependencies, own only new wheel, and admit actual Linux readers."""
    cfg=json.loads(Path(config).read_text());p=json.loads(Path(cfg['plan']).read_text());root=Path(cfg['root']);out=root/'gates';out.mkdir(exist_ok=False)
    write(out/'source.json',freeze());reuse=json.loads((ROOT/'experiments/E029-certifiable-joint-retrieval/reuse-lock.json').read_text())
    base=reuse['native_dependency_base'];deadline=cfg['vm_start_epoch']+2700
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),TMPDIR=str(root/'tmp'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    stages=[]
    def command(label,argv):
        reusable=cfg.get('reuse_passed_setup',{}).get(label)
        if reusable:
            if label not in ['workflow-origin','accepted-numerical','package-install','owned-complete-runtime','actual-ANN-source','installed-discovery','installed-batched-engineering','serial-cached-tiny-DAG']:raise ValueError('Input/science gates cannot be reused through setup')
            for member,wanted in reusable['files'].items():
                if binding(member)!=wanted:raise ValueError('Passed setup member changed: '+member)
            previous=json.loads(Path(reusable['exit_receipt']).read_text())
            if previous['exit_code']!=0 or previous.get('stop_reason') is not None:raise ValueError('Only completed setup gates can be reused')
            stages.append(dict(stage=label,resources=previous,reused_from=reusable['exit_receipt'],verified_files=reusable['files']))
            # Retain portable proof bytes; the original environment itself stays in place.
            if reusable.get('proof'):
                import shutil
                shutil.copyfile(reusable['proof'],out/Path(reusable['proof']).name)
            return
        remaining=deadline-time.time()
        if remaining<30:raise TimeoutError('Setup clock exhausted')
        result=sup.supervise(argv,out/(label+'.log'),remaining,26000000000,env,sample_root=__import__('os').getpid());stages.append(dict(stage=label,resources=result))
    command('workflow-origin',[p['workflow_python'],'-I','-B','-c',workflow_probe('3.12.10','9.16.3')])
    accepted=json.loads((ROOT/'experiments/E023-adaptive-density-bins/reuse-lock.json').read_text())
    command('accepted-numerical',[accepted['numerical_python'],'-I','-B',str(ROOT/'scripts/e023_runtime.py'),'--reference',accepted['runtime_reference'],'--output',str(out/'base-runtime.json')])
    candidate=ROOT/'experiments/E029-certifiable-joint-retrieval/candidate-lock.json'
    if binding(p['wheel'])!=json.loads(candidate.read_text())['wheel']:raise ValueError('Native wheel differs')
    command('package-install',[base+'/bin/python','-I','-B',str(ROOT/'scripts/e019_runtime.py'),'create','--base',base,'--destination',str(root/'env'),'--wheel',p['wheel'],'--output',str(out/'package-install.json')])
    command('owned-complete-runtime',[p['python'],'-I','-B',str(ROOT/'scripts/e027_runtime.py'),'--base',base,'--reference',reuse['native_runtime_reference'],'--candidate-lock',str(candidate),'--output',str(out/'runtime.json')])
    ann=json.loads((ROOT/'experiments/E029-certifiable-joint-retrieval/ann-source-lock.json').read_text())
    code=('import importlib.metadata,json;from pathlib import Path;import pynndescent;'
        'import sys;sys.path.insert(0,'+repr(str(ROOT/'scripts'))+');from e024_coverage import binding,write;'
        'p=Path(pynndescent.__file__).parent/"pynndescent_.py";'
        'assert importlib.metadata.version("pynndescent")=="0.5.13";'
        'assert binding(p)=='+repr(ann['binding'])+';'
        'write('+repr(str(out/'ann-source.json'))+',dict(status="PASS_ACTUAL_LINUX_DISCOVERY_SOURCE",source=binding(p),path=str(p)))')
    command('actual-ANN-source',[p['python'],'-I','-B','-c',code])
    command('installed-discovery',[p['python'],'-I','-B','-c',unit_command(ROOT,'test_exact_discovery')])
    write(out/'discovery-contracts.json',dict(status='PASS',resources=stages[-1]['resources'],actual_sparse_index_reader_refine_export=True))
    command('installed-batched-engineering',[p['python'],'-I','-B','-c',unit_command(ROOT,'test_batched_frozen')])
    command('serial-cached-tiny-DAG',[p['python'],'-I','-B',str(ROOT/'scripts/e029_tiny.py'),'--root',str(out/'tiny-DAG'),'--workflow-python',p['workflow_python']])
    command('restore-complete-inputs',[p['python'],'-I','-B',str(ROOT/'scripts/e029_gates.py'),'--inputs',cfg['plan'],'--output',str(out/'data.json')])
    command('synthetic-width-runtime',[p['python'],'-I','-B',str(ROOT/'scripts/e029_probe.py'),'--output',str(out/'schedule.json')])
    if not all(x['resources']['exit_code']==0 for x in stages):raise ValueError('Native gate failed')
    publish(dict(status='PASS',config=binding(config),stages=stages,finished_epoch=time.time(),source=freeze(),full_science_started=False,no_dependency_install_or_science_recopy=True,owned_package_install_explicit=True),out/'completion.json')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path);p.add_argument('--inputs',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.config:run(a.config)
    elif a.inputs:verify_inputs(json.loads(a.inputs.read_text()),a.output)
    else:p.error('Select gates or exact restore-only inventory')
