#!/usr/bin/env python3
"""Check the actual owned installed wheel with isolated sequential backends."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import write


def run(root):
    """Capture every argv/exit; no acquisition, community data, training or cloud action."""
    root=Path(root).absolute();root.mkdir(exist_ok=False);records=[]
    def call(name,args):
        argv=[sys.executable,'-I','-B',*args]
        with (root/(name+'.log')).open('x') as out:v=subprocess.run(argv,stdout=out,stderr=subprocess.STDOUT,cwd=ROOT)
        record=dict(stage=name,argv=argv,exit_code=v.returncode);write(root/(name+'.exit.json'),record);records.append(record)
        if v.returncode:raise RuntimeError('Installed check failed: '+str(root/(name+'.log')))
    call('complete-runtime',['scripts/e027_runtime.py','--base','artifacts/e021-frozen-sequence-hybrid/envs/hybrid-owned-v2','--reference','experiments/E021-frozen-sequence-hybrid/local-runtime.json','--candidate-lock','experiments/E028-global-discovery-repair/candidate-lock.json','--output',str(root/'runtime.json')])
    for module in ['test_discovery','test_batched_frozen']:
        code='import sys,unittest;from pathlib import Path;r=Path.cwd();sys.path.insert(0,str(r/"tests/product"));v=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('+repr(module)+'));sys.exit(not v.wasSuccessful())'
        call(module,['-c',code])
    call('operations',['-m','unittest','discover','-s','tests','-p','test_e028_operations.py','-v'])
    call('tiny-DAG',['scripts/e028_tiny.py','--root',str(root/'tiny-DAG'),'--workflow-python','artifacts/e005-linux-pilot/env-workflow-local/bin/python'])
    write(root/'completed.json',dict(status='PASS',records=records,actual_installed_distribution=True,backend_processes_isolated=True,community_science=False))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--root',type=Path,required=True);run(a.parse_args().root)
