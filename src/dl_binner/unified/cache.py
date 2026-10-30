"""Admit measured parent depth to unchanged DNA views without rewriting a cache.

Creates only fresh manifests and same-filesystem hardlinks to verified original
arrays. The original feature/view/token evidence remains immutable. A new receipt
records the training admission, which is distinct from E024's grouping rebind.
"""
import json
import os
from pathlib import Path

import numpy as np

from ..context.tokens import Bank, binding
from ..io import digest, write_json
from ..multiview.views import load
from ..relational.evidence import require


def admit(original_features, features, views, tokens, output, measured_receipt=None):
    """Verify invariant parent/crop DNA, then expose fresh training-bound manifests.

    `features` can differ from `original_features` only in measured depth arrays
    and the corresponding metadata. All-zero observations remain measured zeros;
    the inherited encoder's positive-evidence mask does not mean missing cells.
    A changed depth axis requires an independent complete measurement receipt.
    """
    old, om, v, vm = load(original_features, views)
    data, meta = load(features)
    invariants = set(old)-{'depth', 'zero_depth', 'depth_evidence'}
    require(set(data) == set(old) and all(np.array_equal(old[k], data[k]) for k in invariants),
            'Training depth admission changed DNA, views, IDs or eligibility')
    require(meta['fasta_sha256'] == om['fasta_sha256'] and
            len(meta['samples']) == data['depth'].shape[1] and
            len(set(meta['samples'])) == len(meta['samples']), 'Depth/sample/assembly axis differs')
    changed = digest(features) != digest(original_features)
    if changed:
        require(measured_receipt is not None, 'Changed depth requires a complete measured receipt')
        r = json.loads(Path(measured_receipt).read_text())
        require(r['status'] == 'PASS' and r['all_cells_measured'] is True and
                r['missing_cells'] == 0 and r['samples'] == meta['samples'] and
                r['rows'] == len(data['ids']) and r['reference']['sha256'] == meta['fasta_sha256'] and
                r['matrix']['sha256'] == meta['depth_sha256'], 'Measured depth admission differs')
    original = Bank(tokens, original_features, views, old, om, v)
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    # Hardlinks avoid a second multi-GB bank. Never fall back to a copy or rebuild.
    os.link(views, out/'views.npz')
    new_view = dict(vm, parent_features_sha256=digest(features))
    write_json(out/'views.json', new_view)
    target = out/'tokens'; target.mkdir()
    token_meta = json.loads((Path(tokens)/'tokens.json').read_text())
    for name, wanted in token_meta['members'].items():
        require(Path(name).name == name and binding(Path(tokens)/name) == wanted,
                'Token member missing/corrupt; no fallback')
        os.link(Path(tokens)/name, target/name)
    write_json(target/'tokens.json', dict(token_meta, features_sha256=digest(features),
        views_sha256=digest(out/'views.npz'), samples=meta['samples']))
    restored, _, crops, _ = load(features, out/'views.npz')
    Bank(target, features, out/'views.npz', restored, meta, crops)
    result = dict(status='PASS', kind='explicit unchanged-DNA depth training admission',
        original_features=binding(original_features), features=binding(features),
        original_views=binding(views), original_tokens=binding(Path(tokens)/'tokens.json'),
        measured_receipt=binding(measured_receipt) if measured_receipt else None,
        views=binding(out/'views.npz'), view_metadata=binding(out/'views.json'),
        tokens=binding(target/'tokens.json'), invariant_arrays=sorted(invariants),
        samples=meta['samples'], rows=len(data['ids']), bp=int(data['lengths'].sum()),
        actual_missing_cells=0, measured_all_zero_rows=int((data['depth'] == 0).all(1).sum()),
        training_depth_semantics='Measured full-parent means condition every real crop; not window coverage/variance',
        original_cache_untouched=True, generated_DNA_features=False, hardlinks_only=True)
    write_json(out/'admission.json', result)
    return result
