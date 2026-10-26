#!/usr/bin/env python3
"""Verify in-place E023 inputs without recovery, copying, install or science."""
from pathlib import Path
import argparse
import sys
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e023_control import verify_reuse

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lock',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(verify_reuse(a.lock,a.output),flush=True)
