#!/usr/bin/env python3
"""Restore identical accepted learning without retraining or native-vector changes.

Only an explicitly locked common-version match is admissible. Source/module,
configuration, original input/bank/pair, full axes, history and native reload
receipts remain intact. Missing/corrupt bytes never trigger a fresh fit fallback.
This module has no tensor import, inference, neighbor search, truth or cloud API.
"""
import json
import os
from pathlib import Path

from e024_coverage import binding, write


def verify(entry, unit, cfg, views, tokens):
    """Require an exact existing model-information contract, not a similar version."""
    from dl_binner.unified.training import configuration
    from dl_binner.relational.pairs import policy, load_pairs
    from dl_binner.information.grouping import load_inputs, require
    from dl_binner.density.grouping import sparse_input
    for path, wanted in entry['files'].items():
        require(binding(path) == wanted, 'Corrupt/missing identical learning input; no fallback: '+path)
    receipt = json.loads(Path(entry['checkpoint_metadata']).read_text())
    expected = dict(cfg, relational=policy()) if entry['role'] == 'student' else cfg
    require(receipt['config'] == expected and receipt['threads'] == 4 and receipt['loader_workers'] == 0
            and len(receipt['history']) == expected['epochs'] == 20, 'Accepted learning configuration/schedule differs')
    require(receipt['sha256'] == binding(entry['checkpoint'])['sha256']
            and receipt['training_features_sha256'] == binding(unit['features'])['sha256']
            and receipt['training_views_sha256'] == binding(views)['sha256']
            and receipt['training_tokens_sha256'] == binding(Path(tokens)/'tokens.json')['sha256'],
            'Accepted learning DNA/view/token admission differs')
    frozen = binding(Path(unit['frozen'])/'bank.json')['sha256'] if unit['frozen'] else None
    require(receipt.get('training_frozen_sha256') == frozen and ('hybrid' in receipt['config']) == bool(unit['frozen']),
            'Accepted teacher/student GLM availability differs')
    if entry['role'] == 'student':
        _, pair = load_pairs(entry['pairs'], unit['features'])
        require(receipt['training_pairs_sha256'] == binding(Path(entry['pairs'])/'cache.json')['sha256'],
                'Accepted student proposal/pair bytes differ')
        require(pair['inputs']['embeddings'] == entry['teacher_embedding'] and
                pair['inputs']['graph'] == entry['teacher_graph'], 'Declared GLM proposal teacher differs')
    data, vectors, valid, meta = load_inputs(unit['features'], entry['embeddings'])
    em = json.loads(Path(entry['embedding_metadata']).read_text())
    require(em.get('reload_exact') is True and em['checkpoint_sha256'] == receipt['sha256']
            and receipt['samples'] == meta['samples'] and receipt['training_parents'] == int(data['eligible'].sum()),
            'Accepted native exact reload/full learning axis differs')
    sparse_input(entry['graph'], data['ids'].tolist(), valid, entry['embeddings'])
    require(all(h['parents_seen'] == receipt['training_parents'] and
                all(not g['catastrophic_collapse'] for m in h['geometry'].values() for g in m.values())
                for h in receipt['history']), 'Accepted exposure/collapse history differs')
    return dict(status='PASS_IDENTICAL_ACCEPTED_LEARNING', producer=entry['producer'], role=entry['role'],
        checkpoint=binding(entry['checkpoint']), original_native_reload=True,
        no_new_reload_or_portability_claim=True, full_rows=len(valid), samples=meta['samples'],
        GLM=unit['frozen'] is not None, same_frozen_implementation_defaults_and_inputs=True,
        truth_accessed=False, trained_or_inferred=False)


def restore(entry, unit, cfg, views, tokens, target, kind):
    """Expose only exact same-filesystem links in a fresh stage with a reuse receipt."""
    proof = verify(entry, unit, cfg, views, tokens)
    target = Path(target)
    if target.is_dir() and not any(target.iterdir()): target.rmdir()
    target.mkdir(parents=True, exist_ok=False)
    if kind == 'fit':
        members = {'checkpoint.pt': entry['checkpoint'], 'checkpoint.json': entry['checkpoint_metadata'],
                   'reference.npz': entry['reference'], 'reference.json': entry['reference_metadata']}
    elif kind == 'embed':
        members = {'embeddings.npz': entry['embeddings'], 'embeddings.json': entry['embedding_metadata']}
    elif kind == 'graph':
        members = {'graph.npz': entry['graph'], 'graph.json': entry['graph_metadata']}
    elif kind == 'pairs':
        (target/'cache').mkdir()
        members = {'cache/'+p.name: str(p) for p in Path(entry['pairs']).iterdir()}
    else: raise ValueError('Unknown identical learning reuse stage')
    for name, source in members.items():
        if source not in entry['files'] or binding(source) != entry['files'][source]:
            raise ValueError('Unbound learning member; no copy/fitting fallback')
        os.link(source, target/name)
    write(target/'verified-reuse.json', dict(proof, kind=kind,
        members={k: dict(source=v, **binding(v)) for k, v in members.items()}, original_files_untouched=True))
    return proof
