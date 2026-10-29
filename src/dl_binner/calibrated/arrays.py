"""Numeric sparse caches bound to one external complete opaque-ID axis.

Do not duplicate hundreds of megabytes of Unicode IDs in every sparse artifact.
The explicit reader requires the full external axis and checks its canonical
hash as well as member bytes. This is a new research format, not a modification
of the historical ID-containing NPZ readers.
"""
import json
from pathlib import Path

import numpy as np

from ..io import digest, id_digest, write_json
from ..information.grouping import require


def save(path, arrays, metadata, ids):
    """Write fresh numeric arrays and byte/full-axis-bound sidecar, without pickle."""
    path = Path(path); sidecar = path.with_suffix('.json')
    require(not path.exists() and not sidecar.exists(), 'Fresh numeric artifact required')
    require(all(isinstance(x, np.ndarray) and x.dtype.kind in 'biuf' for x in arrays.values()),
            'Only explicit numeric arrays allowed')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        np.savez_compressed(f, **arrays)
    write_json(sidecar, dict(metadata, version=1, format='external_full_axis_numeric',
        sha256=digest(path), full_ids_sha256=id_digest(list(ids)), full_rows=len(ids)))


def load(path, kind, ids):
    """Refuse corrupt bytes, wrong/missing/reordered external axes and object members."""
    path = Path(path); meta = json.loads(path.with_suffix('.json').read_text())
    require(meta['kind'] == kind and meta['version'] == 1
            and meta['format'] == 'external_full_axis_numeric' and meta['sha256'] == digest(path)
            and meta['full_ids_sha256'] == id_digest(list(ids)) and meta['full_rows'] == len(ids),
            'Numeric cache bytes/external full axis differ')
    with np.load(path, allow_pickle=False) as a:
        arrays = {k: a[k] for k in a.files}
    require(all(x.dtype.kind in 'biuf' for x in arrays.values()), 'Non-numeric sparse member refused')
    return arrays, meta
