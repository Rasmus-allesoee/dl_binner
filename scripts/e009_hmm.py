#!/usr/bin/env python3
"""Translate tool HMM CPU budgets to HMMER's additional-worker convention.

An E009-owned PATH wrapper calls this helper, records actual argv and replaces
itself with the pinned utility binary. --cpu 0 uses serial HMMER: one main CPU.
Science/thresholds/databases are unchanged. Never overwrite a retained executable.
"""
import argparse
import json
import os
from pathlib import Path


def budget_args(argv):
    """Count HMMER's master within the requested per-process total CPU budget."""
    result=list(argv)
    if result in (['-h'],['--help'],['--version']):return result,None
    if result.count('--cpu')!=1:raise ValueError('Explicit single HMM --cpu budget required')
    index=result.index('--cpu')+1
    total=int(result[index])
    if total<1:raise ValueError('Tool HMM total CPU budget must be positive')
    result[index]=str(total-1)
    return result,total


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--native',type=Path,required=True)
    parser.add_argument('args',nargs=argparse.REMAINDER);a=parser.parse_args()
    native,total=budget_args(a.args[1:] if a.args[:1]==['--'] else a.args)
    audit={'requested_total_cpus':total,'hmmer_additional_workers':total-1 if total else None,'actual_argv':[str(a.native),*native]}
    if os.environ.get('E009_HMM_AUDIT'):
        descriptor=os.open(os.environ['E009_HMM_AUDIT'],os.O_APPEND|os.O_CREAT|os.O_WRONLY,0o644)
        try:os.write(descriptor,(json.dumps(audit)+'\n').encode())
        finally:os.close(descriptor)
    print('NATIVE_HMM_PLAN='+json.dumps(audit),flush=True)
    os.execv(str(a.native),[str(a.native),*native])
