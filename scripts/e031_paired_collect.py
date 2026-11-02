#!/usr/bin/env python3
"""Collect the prospectively enlarged, complete paired E031 learner return.

Three fits now retain both constructor families. The explicit 3 GiB compressed /
6 GiB logical envelope is frozen before execution, with the same strict member,
alias, closed-control and malformed-input checks. It is not a failure fallback.
The original collector's 2/4 GiB defaults are restored after each serial call.
"""
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).absolute().parent))
import e031_collect as original

CAP=3*1024**3
LOGICAL_CAP=6*1024**3


@contextmanager
def bounds():
    """Scope only the explicit operational byte bounds in this serial process."""
    old=original.CAP,original.LOGICAL_CAP
    original.CAP,original.LOGICAL_CAP=CAP,LOGICAL_CAP
    try:yield
    finally:original.CAP,original.LOGICAL_CAP=old


def pack(work,evidence,output):
    """Run the actual unchanged strict collector with pre-admitted complete bounds."""
    with bounds():return original.pack(work,evidence,output,ceiling=CAP)


def verify(archive,expected_archive=None):
    """Verify every physical member and exact alias under the paired byte caps."""
    with bounds():return original.verify(archive,expected_archive)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['work','evidence','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--allow-incomplete',action='store_true');a=p.parse_args()
    with bounds():
        result=original.pack(a.work,a.evidence,a.output,ceiling=CAP,allow_incomplete=a.allow_incomplete)
    print(json.dumps(result),flush=True)
