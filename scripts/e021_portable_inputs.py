#!/usr/bin/env python3
"""Compile the complete restore-only E021 extraction-input transport manifest.

The native NPZ readers also require their original JSON sidecars. This compiler
uses only the original reuse lock, refuses incomplete bindings, and never reads
truth, regenerates features or changes the frozen cache. File verification and
actual native reader admission remain separate transport/execution gates.
"""
import argparse
import json
from pathlib import Path


def compile_manifest(units, locked_files):
    """Bind both communities' six required members, including native sidecars."""
    if list(units) != ['E009-hybrid', 'oral-hybrid']:
        raise ValueError('Exact ordered two-community axes required')
    files = {}
    for unit, u in units.items():
        paths = {
            'assembly.fna': Path(u['fasta']),
            'features.npz': Path(u['features']),
            'features.json': Path(u['features']).with_suffix('.json'),
            'views.npz': Path(u['views']),
            'views.json': Path(u['views']).with_suffix('.json'),
            'tokens/tokens.json': Path(u['tokens'])/'tokens.json',
        }
        for name, path in paths.items():
            b = locked_files.get(str(path))
            if (not path.is_absolute() or b is None or set(b) != {'bytes', 'sha256'}
                    or type(b['bytes']) is not int or b['bytes'] < 1
                    or len(b['sha256']) != 64
                    or any(c not in '0123456789abcdef' for c in b['sha256'])):
                raise ValueError('Missing/invalid original input binding: '+str(path))
            files[unit+'/'+name] = dict(source=str(path), **b)
    return dict(kind='E021 verified transport v1', files=files)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reuse-lock', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = compile_manifest(json.loads(a.plan.read_text())['units'],
        json.loads(a.reuse_lock.read_text())['files'])
    with a.output.open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
