#!/usr/bin/env python3
"""Own the new research package; reuse the accepted complete numerical base.

The E016 creator/probe are reused unchanged: they verify inventories, isolated
imports and regular native library targets. The new lock changes only the owned
package source inventory; no resolver, reinstall or source-copy fallback occurs.
"""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e016_runtime import create,probe

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['create','probe'])
    for n in ['base','destination','wheel','lock','output']:p.add_argument('--'+n,type=Path)
    a=p.parse_args()
    if a.operation=='create':create(a.base,a.destination,a.wheel,a.output)
    else:probe(a.base,a.lock,a.output)
