#!/usr/bin/env python3
"""Audit already verified E033 measurement receipts and parent features, without science replay.

The caller must first admit the stopped VM, complete immutable archive streams and
costs. This reader never opens a BAM, fits, maps, makes a partition or reads truth.
It verifies the new feature DNA axes and reports technical filter/zero populations.
Raw moment bytes are bound to the full verified archive; numeric moment checks
remain the separately recorded native bank/full-shape gates.
"""
import argparse
import json
from pathlib import Path


def read(path):
    """Load one closed JSON receipt."""
    return json.loads(Path(path).read_text())


def require(value, message):
    """Refuse an unmet technical contract without admitting quality."""
    if not value:
        raise ValueError(message)


def validate_counters(counters):
    """Close the exclusive read-filter ledger; supplementary counters stay separate."""
    require(all(type(v) is int and v >= 0 for v in counters.values()),
            'Malformed read/filter counter')
    excluded = sum(v for k, v in counters.items() if k.startswith('excluded_'))
    require(counters['records'] == counters['accepted_reads'] + excluded
            + counters.get('unplaced_unmapped', 0)
            and counters['high_MAPQ_aligned_bases'] <= counters['accepted_aligned_bases'],
            'Read/filter counter ledger does not close')


def audit(base, originals, output):
    """Verify both ordered banks and unchanged DNA; summarize new measured means.

    ``base`` owns complete stream proofs, selected work and the exact inventory.
    ``originals`` maps E009/oral to retained original feature NPZs. ``output`` must
    not exist. Large communities are loaded serially and released between modes.
    """
    import numpy as np
    from dl_binner.context.tokens import binding
    from dl_binner.multiview.views import load
    from dl_binner.multiscale.measurement import policy
    base = Path(base)
    proof = read(base / 'measurement-detail-stream-proof.json')
    first = read(base / 'measurements-stream-proof.json')
    inv = read(base / 'control/measurements/inventory.json')
    require(proof['every_member_verified'] and first['every_member_verified']
            and proof['archive'] == first['archive'] and proof['generation'] == first['generation'],
            'Complete same-generation measurement verification required')
    root = base / 'measurement-detail/work'
    results = {}
    for community in ['E009', 'oral']:
        at = root / community
        bank = read(at / 'bank.json')
        original = Path(originals[community])
        require(bank['kind'] == 'multiscale_BAM_bank' and bank['all_samples_measured']
                and not bank['truth_accessed'] and bank['policy'] == policy()
                and len(bank['samples']) == len(bank['sample_files']) == 10,
                'Complete shared policy/ten-sample bank required')
        require(binding(original) == bank['features'], 'Original feature bytes differ')
        old, old_meta = load(original)
        new, new_meta = load(at / 'features.npz')
        require(new_meta['samples'] == old_meta['samples'] == bank['samples']
                and new_meta['prior_features'] == binding(original)
                and new_meta['measured_bank'] == binding(at / 'bank.json'),
                'Feature sample/bank binding differs')
        require(set(new) == set(old) and all(np.array_equal(old[k], new[k]) for k in old
                if k not in ['depth', 'zero_depth', 'depth_evidence']),
                'DNA/eligibility/composition identity changed')
        require(len(new['ids']) == bank['rows'] and int(new['lengths'].sum()) == bank['bp']
                and new['depth'].shape == (bank['rows'], 10)
                and np.isfinite(new['depth']).all() and (new['depth'] >= 0).all()
                and np.array_equal(new['zero_depth'], new['depth'] == 0)
                and np.array_equal(new['depth_evidence'], (new['depth'] > 0).any(1)),
                'New parent means or measured-zero evidence contract differs')
        samples = []
        dictionary = None
        for i, (name, entry) in enumerate(zip(bank['samples'], bank['sample_files'])):
            require(entry['path'] == 'sample-%02d' % i, 'Ordered sample path differs')
            path = at / entry['path'] / 'sample.json'
            sample = read(path)
            require(binding(path) == entry['sample_receipt']
                    and sample['sample'] == name and sample['features'] == bank['features']
                    and sample['views'] == bank['views'] and sample['policy'] == bank['policy']
                    and sample['ids_sha256'] == new_meta['ids_sha256']
                    and sample['shape'] == [bank['rows'], 5, 4]
                    and sample['bp'] == bank['bp'] and not sample['truth_accessed'],
                    'Sample/view/DNA/filter binding differs')
            require(sample['moments'] == inv['all_work_members'][
                    community + '/' + entry['path'] + '/moments.npy'], 'Moment byte binding differs')
            require(dictionary is None or dictionary == sample['dictionary_sha256'],
                    'BAM dictionaries differ between samples')
            dictionary = sample['dictionary_sha256']
            c = sample['counters']
            validate_counters(c)
            samples.append(dict(sample=name, counters=c, wall_seconds=sample['wall_seconds'],
                                peak_active_events=sample['peak_active_events']))
        strata = {}
        for name, selected in [('all', np.ones(len(new['ids']), bool)), ('eligible', new['eligible']),
                               ('lt500', new['lengths'] < 500),
                               ('500_999', (new['lengths'] >= 500) & (new['lengths'] < 1000)),
                               ('1000_2499', (new['lengths'] >= 1000) & (new['lengths'] < 2500)),
                               ('ge2500', new['lengths'] >= 2500)]:
            before = (old['depth'][selected] == 0).all(1)
            after = (new['depth'][selected] == 0).all(1)
            strata[name] = dict(rows=int(selected.sum()), bp=int(new['lengths'][selected].sum()),
                                old_all_zero=int(before.sum()), new_measured_all_zero=int(after.sum()),
                                zero_to_positive=int((before & ~after).sum()),
                                positive_to_zero=int((~before & after).sum()))
        totals = {k: sum(s['counters'].get(k, 0) for s in samples)
                  for k in set().union(*(s['counters'] for s in samples))}
        results[community] = dict(bank=binding(at / 'bank.json'), new_features=binding(at / 'features.npz'),
                                 rows=bank['rows'], bp=bank['bp'], ordered_samples=bank['samples'],
                                 policy=bank['policy'], samples=samples, counters=totals, strata=strata,
                                 raw_moment_numeric_review='Native bank seals and all three full-shape Bank readers passed; no local BAM/moment recomputation',
                                 all_other_DNA_features_unchanged=True)
        del old, new
    value = dict(status='PASS_TECHNICAL_MEASUREMENT_REVIEW_ONLY', communities=results,
                 scientific_comparison_admitted=False, new_quality_scores=False,
                 truth_accessed=False, baseline_scores_replayed=False)
    output = Path(output)
    with output.open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')
    return value


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['base', 'E009', 'oral', 'output']:
        p.add_argument('--' + name, required=True, type=Path)
    a = p.parse_args()
    audit(a.base, dict(E009=a.E009, oral=a.oral), a.output)
