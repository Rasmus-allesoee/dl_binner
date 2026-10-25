#!/usr/bin/env python3
"""Publish complete E021 control JSON atomically, without overwriting a journal.

The queue reader must never observe a newly opened empty file. Serialize first,
fsync a private sibling, and atomically link it into its exclusive ready name.
Pending files are not commands. This utility performs no scientific work.
"""
import argparse
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
import tempfile

MAX_BYTES=1024**2


def publish(value,path):
    """Expose one immutable complete JSON value or refuse an existing target."""
    path=Path(path)
    data=(json.dumps(value,allow_nan=False,separators=(',',':'))+'\n').encode()
    if len(data)>MAX_BYTES:raise ValueError('Control JSON exceeds bounded size')
    fd,temp=tempfile.mkstemp(prefix='.'+path.name+'.',suffix='.pending',dir=path.parent)
    try:
        with os.fdopen(fd,'wb')as f:
            f.write(data);f.flush();os.fsync(f.fileno())
        os.link(temp,path,follow_symlinks=False)
        directory=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:os.unlink(temp)
    return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def remote_program(path):
    """Use this exact writer in isolated SSH Python without a remote module import."""
    return ('import hashlib,json,os,sys,tempfile\nfrom pathlib import Path\nMAX_BYTES=1048576\n'
        +inspect.getsource(publish)
        +'\nraw=sys.stdin.buffer.read(MAX_BYTES+1)\n'
        +'if len(raw)>MAX_BYTES:raise ValueError("Control JSON exceeds bounded size")\n'
        +'publish(json.loads(raw),Path('+repr(str(path))+'))\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--path',type=Path,required=True);a=p.parse_args()
    raw=sys.stdin.buffer.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError('Control JSON exceeds bounded size')
    publish(json.loads(raw),a.path)
