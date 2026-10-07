#!/usr/bin/env python3
"""Run bounded installed-wheel product regressions outside the source checkout.

Requires an installed binner interpreter and a fresh evidence
directory. Copies only committed self-contained tests, then runs actual native
readers/writers and synthetic software fixtures. No research assets or workers
are mocked; no accepted scientific demonstration runs. Retains logs and exit/RSS
receipts for failures too. Resource ceiling covers copying, probes and tests.
"""
import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import signal
import sys
import time


def main():
    """Copy the portable suite and supervise the installed Python with lexical paths."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python',type=Path,required=True,help='Installed binner interpreter; preserve its lexical path')
    parser.add_argument('--output',type=Path,required=True,help='Fresh evidence directory; never overwritten')
    parser.add_argument('--timeout',type=float,default=1800,help='Overall software-test seconds, maximum 7200')
    parser.add_argument('--threads',type=int,choices=range(1,5),default=4,help='Explicit test CPU budget, 1–4 (prepared Linux CI uses 2)')
    args=parser.parse_args()
    if not 0 < args.timeout <= 7200:parser.error('--timeout must be positive and at most 7200')
    root=Path(__file__).absolute().parents[1]
    python=args.python.absolute()
    out=args.output.absolute();out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    spec=importlib.util.spec_from_file_location('product_supervision',root/'src/dl_binner/supervision.py')
    # sdists omit source helpers only if the package content contract is broken.
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    env=module.isolated_env(args.threads)
    env.update(DL_BINNER_TEST_OUTPUT=str(out),DL_BINNER_TEST_THREADS=str(args.threads))
    def ceiling(signum,frame):raise TimeoutError('Product regression overall ceiling reached')
    old=signal.signal(signal.SIGALRM,ceiling);signal.setitimer(signal.ITIMER_REAL,args.timeout)
    try:
        tests=out/'tests';shutil.copytree(root/'tests/product',tests,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        os.chdir(out)
        module.progress(f'Installed product regressions: {args.threads} threads / loader zero / 8 GB; '+str(out))
        module.supervise([python,'-I','-B','-m','unittest','discover','-s',tests,'-p','test_*.py','-v'],
                         out/'product-tests.log',args.timeout-(time.monotonic()-started),8000000000,env,sample_root=os.getpid())
        print('PRODUCT_TEST_OUTPUT='+str(out),flush=True)
    except BaseException:
        print('PRODUCT_TEST_OUTPUT='+str(out),file=sys.stderr,flush=True)
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old)


if __name__=='__main__':main()
