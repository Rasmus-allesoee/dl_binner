#!/usr/bin/env python3
"""Verify sealed E019 inputs, native vectors and runtime in place; never restore anew."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).absolute().parent))
from e019_reuse import verify as verify_bytes


def verify(lock, output):
    """Refuse a foreign lock or any missing/corrupt retained member without fallback."""
    record = json.loads(Path(lock).read_text())
    if record['kind'] != 'E020 in-place sealed E019 reuse':
        raise ValueError('Unexpected E020 reuse schema')
    return verify_bytes(lock, output)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lock', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    verify(a.lock, a.output)
