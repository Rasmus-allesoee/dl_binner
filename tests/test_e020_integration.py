"""Read real retained E019 context bytes and reject metadata drift; no model call.

This file is also the native gate entrypoint. Ordinary unit use has its own tiny
synthetic feature fixture; retained native mode verifies both actual E019 modes.
Sparse/opaque/export mathematics remain covered by original E017 contracts and
the actual E020 cached worker fixture, rather than mocked downstream functions.
"""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).absolute().parents[1]/'scripts'))
sys.path.insert(0, str(Path(__file__).absolute().parent))
from e020_bootstrap import context_input
from e014_collect import binding


def retained(root, output):
    """Validate both retained learned-context modes without inference or mutation."""
    root = Path(root); result = {}
    for mode in ['depth', 'sequence']:
        features = root/'fixture'/mode/'features.npz'
        if not features.exists():
            features = root/mode/'features.npz'
        embeddings = root/(mode+'-embeddings.npz')
        before = {str(p): binding(p) for p in [features, features.with_suffix('.json'),
                  embeddings, embeddings.with_suffix('.json')]}
        data, vectors, valid, meta, em = context_input(features, embeddings)
        if vectors.shape != (len(data['ids']), 64):
            raise ValueError('Native context geometry differs')
        if before != {p: binding(p) for p in before}:
            raise ValueError('Read-only context gate mutated accepted bytes')
        result[mode] = dict(rows=len(data['ids']), eligible=int(valid.sum()),
            samples=meta['samples'], metadata=em, files=before)
    from dl_binner.io import write_json
    write_json(output, dict(status='PASS', modes=result, no_inference=True, no_fit=True))


class ContextReader(unittest.TestCase):
    def test_actual_context_metadata_and_refusal(self):
        from test_e017_grouping import fixture
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); f, e, _, _ = fixture(root)
            with self.assertRaisesRegex(ValueError, 'context metadata'):
                context_input(f, e)
            side = e.with_suffix('.json'); meta = json.loads(side.read_text())
            meta.update(mode='context_online_unit_sphere', reload_exact=True,
                samples=['2', '0', 'constant'], checkpoint_sha256='a'*64,
                tokens_manifest_sha256='b'*64,
                metric='unit-sphere cosine/equivalent Euclidean; no post-learning transform')
            side.write_text(json.dumps(meta)); context_input(f, e)
            for change in [dict(reload_exact=False), dict(samples=['0', '2', 'constant']),
                           dict(mode='positive_online_unit_sphere'), dict(checkpoint_sha256='x')]:
                side.write_text(json.dumps(meta|change))
                with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'context metadata'):
                    context_input(f, e)


if __name__ == '__main__':
    if '--context-root' in sys.argv:
        p = argparse.ArgumentParser(description=__doc__)
        p.add_argument('--context-root', type=Path, required=True)
        p.add_argument('--output', type=Path, required=True)
        a = p.parse_args(); retained(a.context_root, a.output)
    else:
        unittest.main()
