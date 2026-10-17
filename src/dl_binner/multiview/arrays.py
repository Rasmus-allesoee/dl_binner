"""Byte/axis-equivalent NPZ loading without a redundant whole-array copy.

NPZ member access already owns its array; copying a multi-GB crop bank again
needlessly doubles its transient RSS. This preserves historical receipts and
numeric bytes while streaming the canonical JSON ID hash. It is not a new format.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from ..io import digest


def load_arrays(path,kind):
    """Verify the original byte/ID contracts and return independently owned members."""
    path=Path(path);meta=json.loads(path.with_suffix('.json').read_text())
    if meta.get('version')!=1 or meta.get('kind')!=kind or digest(path)!=meta['sha256']:
        raise ValueError('Artifact kind/version/byte hash mismatch')
    with np.load(path,allow_pickle=False) as archive:
        arrays={k:archive[k] for k in archive.files}
    ids=arrays['ids']
    if ids.ndim!=1 or ids.dtype.kind!='U':raise ValueError('Invalid string ID axis')
    seen=set();h=hashlib.sha256();h.update(b'[')
    for i,v in enumerate(ids):
        ident=str(v)
        if ident in seen:raise ValueError('Artifact duplicate ID')
        seen.add(ident)
        if i:h.update(b',')
        h.update(json.dumps(ident,separators=(',',':')).encode())
    h.update(b']')
    if h.hexdigest()!=meta['ids_sha256']:raise ValueError('Artifact ordered-ID mismatch')
    return arrays,meta
