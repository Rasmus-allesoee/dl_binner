#!/usr/bin/env python3
"""Restore only exact E031 online/EMA/predictor/Adam checkpoints, no old science.

The accepted full stream/member/alias verifier remains unchanged. This consumer
selects six state/metadata files rather than E032's old forests. No missing-byte
recopy or refit fallback exists, and the original archive is never rewritten.
"""
import argparse
from contextlib import contextmanager
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).absolute().parent))
import e032_restore as accepted


def needed(name):
    """Select only original admitted E031 checkpoints and their strict metadata."""
    return name in {'work/'+u+'/train/result/checkpoint'+suffix
                   for u in accepted.UNITS for suffix in ['.pt','.json']}


@contextmanager
def state_selection():
    """Scope only the restore predicate, preserving every verifier and cap."""
    old=accepted.needed;accepted.needed=needed
    try:yield
    finally:accepted.needed=old


def restore(stream,metadata,expected,root,inventory_binding=None,reserve=25*1024**3):
    """Verify the complete closed archive but retain only needed state bytes."""
    with state_selection():return accepted.stream_restore(stream,metadata,expected,root,inventory_binding,reserve)


def download(lock,root,gcloud):
    """Read the frozen existing generation directly, without a compressed copy."""
    with state_selection():return accepted.download(lock,root,gcloud)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lock',required=True,type=Path)
    p.add_argument('--root',required=True,type=Path);p.add_argument('--gcloud',required=True,type=Path);a=p.parse_args();download(a.lock,a.root,a.gcloud)
