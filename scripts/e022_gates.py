#!/usr/bin/env python3
"""Run remaining actual Linux E022 gates inside the original held-parent clock.

The controller creates the package-only prefix beforehand. This adapter installs
nothing and changes no cloud resource. A passed dependency inventory is reused;
full current input readers and the new tiny treatment/launcher paths are checked.
Synthetic tiny marker annotations and GLM values are explicitly engineering mocks.
"""
import argparse
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_owner import supervisor
from e014_collect import binding
from e021_control_json import publish
from e022_control import validate,verify_inputs,restore_pairs


def readers(plan, output):
    """Verify exact full bank/context/axes/pair readers, without training or detection."""
    from dl_binner.multiview.views import load
    from dl_binner.relational.model import make_bank
    from dl_binner.relational.pairs import load_pairs
    cfg,_=validate(plan);lock=verify_inputs(plan['input_lock']);u=plan['unit']
    data,meta,views,vm=load(u['features'],u['views'])
    expected=json.loads((Path(__file__).absolute().parents[1]/'experiments/E010-coherent-prototype/candidate-lock.json').read_text())
    if len(data['ids'])!=145702 or int(data['lengths'].sum())!=231678157 or meta['samples']!=expected['ordered_depth_columns']:
        raise ValueError('Complete accepted E009 axes differ')
    banks=make_bank(u['tokens'],u['frozen'],u['features'],u['views'],data,meta,views,cfg)
    target=Path(output).with_suffix('.pairs');restore_pairs(plan['pair_archive'],target,lock)
    pairs,m=load_pairs(target,u['features'])
    if m['summary']['sign_counts']!={'1':1963,'-1':365}:raise ValueError('Exact frozen pair counts differ')
    publish(dict(status='PASS_FULL_READERS',contigs=len(data['ids']),bp=int(data['lengths'].sum()),samples=meta['samples'],
        pairs=binding(target/'cache.json'),pair_counts=m['summary']['sign_counts'],no_training_or_extraction=True),Path(output))


def run(path):
    """Capture all new native gates and emit completion only after every exit is zero."""
    cfg=json.loads(Path(path).read_text());repo=Path(cfg['repo']);root=Path(cfg['root']);g=root/'gates'
    g.mkdir(exist_ok=False);plan=json.loads(Path(cfg['science_plan']).read_text());sup=supervisor();env=sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),TMPDIR=str(root/'tmp'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    deadline=min(cfg['vm_start_epoch']+1800,cfg['vm_start_epoch']+7200-600);results=[]
    def cmd(name,args):
        remaining=deadline-time.time()
        if remaining<5:raise TimeoutError('Original native-setup clock expired')
        r=sup.supervise(args,g/(name+'.log'),remaining,26_000_000_000,env,sample_root=__import__('os').getpid())
        results.append(dict(name=name,resources=r))
    ref=json.loads((repo/'experiments/E022-marker-informed-learning/reuse-lock.json').read_text())
    cmd('runtime',[plan['python'],'-I','-B',str(repo/'scripts/e022_runtime.py'),'--base',ref['native_dependency_base'],'--reference',ref['native_runtime_reference'],'--candidate-lock',str(repo/'experiments/E022-marker-informed-learning/candidate-lock.json'),'--output',str(g/'runtime.json')])
    cmd('full-readers',[plan['python'],'-I','-B',str(repo/'scripts/e022_gates.py'),'--readers',cfg['science_plan'],'--output',str(g/'readers.json')])
    cmd('tiny-product',[plan['python'],'-I','-B','-m','unittest','discover','-s',str(repo/'tests/product'),'-p','test_relational.py','-v'])
    cmd('operational',[plan['python'],'-I','-B','-m','unittest','discover','-s',str(repo/'tests'),'-p','test_e022_operational.py','-v'])
    cmd('tiny-DAG-collection',[plan['python'],'-I','-B',str(repo/'scripts/e022_tiny.py'),'--root',str(g/'tiny-DAG'),'--workflow-python',plan['workflow_python']])
    publish(dict(status='SUCCESS',config=binding(path),stages=results,elapsed_since_VM_start_seconds=time.time()-cfg['vm_start_epoch'],
        scope='Fresh Linux gates, no community science released; package-only install is separate inside same original clock'),g/'completion.json')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path);p.add_argument('--readers',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.config:run(a.config)
    elif a.readers and a.output:readers(json.loads(a.readers.read_text()),a.output)
    else:p.error('Select --config or --readers/--output')
