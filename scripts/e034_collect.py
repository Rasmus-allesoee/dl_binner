#!/usr/bin/env python3
"""Use accepted complete member/alias collection under E034's 2 GiB slice cap."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).absolute().parent))
import e033_collect as closed


def pack(work,evidence,output):
    """Retain every regular work byte, verifying all aliases; refuse any oversize."""
    old=closed.CAP,closed.LOGICAL
    closed.CAP,closed.LOGICAL=2*1024**3,8*1024**3
    try:return closed.pack(work,evidence,output)
    finally:closed.CAP,closed.LOGICAL=old
