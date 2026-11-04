#!/usr/bin/env python3
"""Bound actual installed E033 checks with persisted CPU/RSS/exit evidence.

Run one named check per invocation, preserving failed attempts in distinct roots.
This executes synthetic engineering data only and has no cloud action interface.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1]


def run(action,output,python,workflow_python=None):
    """Use the preserved process-tree supervisor, four threads and an 8 GB ceiling."""
    out=Path(output).absolute();out.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('supervisor',ROOT/'src/dl_binner/supervision.py')
    sup=importlib.util.module_from_spec(spec);spec.loader.exec_module(sup)
    env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(out/'numba'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
    if action=='DAG':
        if not workflow_python:raise ValueError('Explicit existing workflow interpreter required')
        argv=[python,'-I','-B',ROOT/'scripts/e033_tiny.py','--root',out/'tiny','--workflow-python',workflow_python]
    elif action=='scale':
        argv=[python,'-I','-B',ROOT/'scripts/e033_scale.py','--root',out/'scale']
    elif action in ['product','operations']:
        modules=['test_multiscale_measurement','test_multiscale_learning'] if action=='product' else ['test_e033_operations']
        code="import sys,unittest;sys.path[:0]=sys.argv[1:3];s=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in sys.argv[3:]);r=unittest.TextTestRunner(verbosity=2).run(s);raise SystemExit(not r.wasSuccessful())"
        argv=[python,'-I','-B','-c',code,ROOT/'tests/product',ROOT/'tests',*modules]
    else:raise ValueError('Unknown engineering action')
    result=sup.supervise(list(map(str,argv)),out/'check.log',3600,8_000_000_000,env)
    (out/'completed.json').write_text(json.dumps(dict(status='PASS',action=action,resources=result,community=False,cloud=False),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action',choices=['product','operations','DAG','scale'],required=True)
    for n in ['output','python']:p.add_argument('--'+n,required=True,type=Path)
    p.add_argument('--workflow-python',type=Path);a=p.parse_args();run(a.action,a.output,a.python,a.workflow_python)
