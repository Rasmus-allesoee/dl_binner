#!/usr/bin/env python3
"""Summarize admitted E016 diagnostics and reuse earlier, checksum-bound results.

This reader neither scores old partitions nor runs models, graphs or cloud work.
It writes a compact comparison and a complete target table from closed reviews.
The original E016 criteria remain fixed; population trade-offs are explicit.
"""
import argparse
import csv
import datetime
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).absolute().parents[1]


def read(path):
    """Read one retained JSON record without a missing-input fallback."""
    return json.loads(Path(path).read_text())


def binding(path):
    """Return regular file size and SHA256; refuse linked evidence."""
    path = Path(path)
    if path.is_symlink():
        raise ValueError('Evidence link refused: ' + str(path))
    data = path.read_bytes()
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def metrics(review, arm):
    """Keep conservative sequence truth separate from the oral origin oracle."""
    value = review['arms'][arm]
    return (value['diagnostics'] if review['dataset'] == 'E009'
            else value['evaluation']['origin'])


def paired(current, previous):
    """Compare existing per-target recoveries, preserving every full denominator."""
    a = {r['genome']: r for r in current}
    b = {r['genome']: r for r in previous}
    if len(a) != len(current) or len(b) != len(previous) or a.keys() != b.keys():
        raise ValueError('Complete target axes differ')
    rows = []
    for genome, row in a.items():
        old = b[genome]
        if row['reference_bp'] != old['reference_bp']:
            raise ValueError('Full target denominator differs')
        rows.append(dict(genome=genome, reference_bp=row['reference_bp'],
                         previous_bp=old['recovered_bp'], candidate_bp=row['recovered_bp'],
                         delta_bp=row['recovered_bp'] - old['recovered_bp']))
    return dict(gained=sum(r['delta_bp'] > 0 for r in rows),
                lost=sum(r['delta_bp'] < 0 for r in rows),
                unchanged=sum(r['delta_bp'] == 0 for r in rows),
                delta_bp=sum(r['delta_bp'] for r in rows)), rows


def numerical_keep(current, baseline):
    """Apply the original two-scope recovery/count rule without a score grid."""
    deltas = [a['bp_weighted_R95'] - b['bp_weighted_R95']
              for a, b in zip(current, baseline)]
    return (len(deltas) == 2 and all(x >= 0 for x in deltas)
            and any(x >= .005 for x in deltas)
            and all(a['at_least_90_percent'] >= b['at_least_90_percent']
                    for a, b in zip(current, baseline)))


def summarize(root, output):
    """Write the reviewed bundle and paired full-target table from admitted inputs."""
    root, output = Path(root), Path(output)
    output.mkdir(exist_ok=True)
    if any((output / n).exists() for n in ['comparison-review.json', 'comparison-targets.tsv']):
        raise ValueError('Preserve prior summaries; use an explicit new reviewed attempt')
    exp = REPO / 'experiments/E016-positive-only-multiview'
    old = REPO / 'artifacts/e014-multiview-reconstruction/inspection-20261019'
    zero = REPO / 'artifacts/e015-zero-reconstruction/review-20261019'
    e014_path = REPO / 'experiments/E014-multiview-reconstruction/comparison-review.json'
    e015_path = REPO / 'experiments/E015-zero-reconstruction/comparison-review.json'
    e014, e015 = read(e014_path), read(e015_path)
    observed = read(exp / 'native-observed.json')
    assert read(root / 'verified/verification.json')['status'] == 'SUCCESS'
    assert read(root / 'native-receipts-review.json')['status'] == 'SUCCESS'
    assert read(root / 'learning-receipts-review.json')['status'] == 'PASS'
    units, targets, currents, priors, evidence = {}, [], [], [], {}
    for unit, prior_name, zero_name in [('E009-positive', 'E009-dev5-attempt2', 'E009-zero'),
                                         ('oral-positive', 'oral-dev5', 'oral-zero')]:
        new_path = root / ('diagnostics-' + unit) / 'review.json'
        prior_path = old / ('diagnostics-' + prior_name) / 'review.json'
        zero_path = zero / ('diagnostics-' + zero_name) / 'review.json'
        assert binding(prior_path) == e014['evidence'][str(prior_path.relative_to(REPO))]
        assert binding(zero_path) == e015['evidence'][str(zero_path.relative_to(REPO))]
        r, b, z = read(new_path), read(prior_path), read(zero_path)
        assert r['status'] == b['status'] == z['status'] == 'SUCCESS'
        current = metrics(r, 'post'); prior = metrics(b, 'post'); control = metrics(z, 'post')
        expected_count = 156 if r['dataset'] == 'E009' else 799
        expected_bp = 554661890 if r['dataset'] == 'E009' else 2083072211
        assert len(current['recovery']) == expected_count
        assert sum(row['reference_bp'] for row in current['recovery']) == expected_bp
        pair, rows = paired(current['recovery'], prior['recovery'])
        zero_pair, _ = paired(current['recovery'], control['recovery'])
        parent, _ = paired(current['recovery'], metrics(r, 'pre')['recovery'])
        old_refinement, _ = paired(current['recovery'], metrics(r, 'old')['recovery'])
        by_arm = {a: {row['genome']: row for row in metrics(r, a)['recovery']}
                  for a in ['pre', 'old', 'post']}
        zero_rows = {row['genome']: row for row in control['recovery']}
        for row in rows:
            genome = row['genome']
            targets.append(dict(dataset='E009_conservative_v2' if r['dataset'] == 'E009'
                                else 'oral_provided_origin_oracle', genome=genome,
                                reference_bp=row['reference_bp'], E014_post_bp=row['previous_bp'],
                                E015_post_bp=zero_rows[genome]['recovered_bp'],
                                E016_parent_bp=by_arm['pre'][genome]['recovered_bp'],
                                E016_old_refiner_bp=by_arm['old'][genome]['recovered_bp'],
                                E016_post_bp=row['candidate_bp'], delta_vs_E014_bp=row['delta_bp']))
        arms = {}
        for arm, value in r['arms'].items():
            g = value['grouping']
            arms[arm] = dict(recovery=metrics(r, arm)['recovery_summary'],
                             grouping=g['restricted_B3'] if r['dataset'] == 'E009' else g['origin_B3'],
                             geometry=value['diagnostics']['geometry'] if r['dataset'] == 'E009' else g['geometry'],
                             length_strata=g['length_strata'] if r['dataset'] == 'E009' else g['geometry']['length_strata'],
                             populations=value['populations'] if r['dataset'] == 'E009' else g['population_cells'])
            if r['dataset'] == 'E009':
                arms[arm]['geometry_by_lineage'] = value['diagnostics']['geometry_by_lineage']
            else:
                masked = value['evaluation']['known_shared_mask']
                same = (metrics(r, arm)['recovery_summary'] == masked['recovery_summary']
                        and [(x['genome'], x['recovered_bp'], x['whole_reference_R95'])
                             for x in metrics(r, arm)['recovery']]
                        == [(x['genome'], x['recovered_bp'], x['whole_reference_R95'])
                            for x in masked['recovery']])
                arms[arm]['known_shared_mask'] = dict(summary=masked['recovery_summary'],
                                                     all_target_recovery_identical=same)
        decisions = read(root / 'verified/work/units' / unit / 'refine/decisions.json')
        selection = {}
        for row in decisions:
            selection[row['selected']] = selection.get(row['selected'], 0) + 1
        history = r['checkpoint']['history']
        units[unit] = dict(arms=arms, baseline_E014_post=prior['recovery_summary'],
                           baseline_E015_post=control['recovery_summary'],
                           paired_vs_E014=pair, paired_vs_E015=zero_pair,
                           paired_E013_vs_parent=parent, paired_E013_vs_old=old_refinement,
                           accounting=r['contracts'], decisions=selection,
                           raw_learned_geometry={k: v for k, v in r['raw_learned_geometry'].items() if k != 'queries'},
                           native_graph={k: v for k, v in r['native_graph_review'].items() if k != 'geometry'},
                           native_neighbor_audit={k: v for k, v in r['native_graph_review']['geometry'].items() if k != 'queries'},
                           training={k: r['checkpoint'][k] for k in ['config', 'parameter_count', 'teacher_parameter_count',
                                      'predictor_parameter_count', 'samples', 'training_parents', 'positive_parents',
                                      'reconstruction_only_parents', 'ema_updates', 'threads', 'loader_workers',
                                      'wall_seconds', 'process_cpu_seconds']},
                           geometry_history=dict(initial=r['checkpoint']['initial_geometry'],
                                                 epochs=[dict(epoch=h['epoch'], ema_updates=h['ema_updates'],
                                                              last_tau=h['last_tau'], geometry=h['geometry']) for h in history]),
                           first_last_history=[history[0], history[-1]])
        currents.append(current['recovery_summary']); priors.append(prior['recovery_summary'])
        evidence.update({str(p.relative_to(REPO)): binding(p) for p in [new_path, prior_path, zero_path]})
    fields = ['dataset', 'genome', 'reference_bp', 'E014_post_bp', 'E015_post_bp',
              'E016_parent_bp', 'E016_old_refiner_bp', 'E016_post_bp', 'delta_vs_E014_bp']
    table = output / 'comparison-targets.tsv'
    with table.open('x') as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(targets)
    core_keep = numerical_keep(currents, priors)
    assert core_keep, 'Do not silently assign a different prospective disposition'
    resources = [read(p) | dict(path=str(p.relative_to(REPO)), binding=binding(p))
                 for p in root.glob('*.resources.json')]
    for item in resources:
        item.pop('samples', None)
    e009_gain = currents[0]['bp_weighted_R95'] - priors[0]['bp_weighted_R95']
    gap = .085493 - priors[0]['bp_weighted_R95']
    result = dict(record='E016 frozen positive-only multiview completed development comparison',
                  reviewed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  status='ACCEPTED_NATIVE_OUTPUTS_AND_FROZEN_LOCAL_DIAGNOSTICS; KEEP_SCOPED_CANDIDATE',
                  science_source=observed['source_commit'], phase=observed['phase'],
                  protocol=binding(exp / 'protocol.json'), candidate_lock=binding(exp / 'candidate-lock.json'),
                  reuse_lock=binding(exp / 'reuse-lock.json'), archive=read(root / 'verified/verification.json'),
                  native_ledger=binding(root / 'native-receipts-review.json'),
                  learning_audit=binding(root / 'learning-receipts-review.json'),
                  units=units, full_target_table=binding(table),
                  preserved_context=dict(E014=binding(e014_path), E015=binding(e015_path),
                      E009_dev3_R95=.053911, E009_dev4_E013_R95=e014['preserved_baseline']['weighted_R95'],
                      E009_MetaBAT2_R95=.085493, E009_gap_closed_vs_E014=e009_gain / gap,
                      scope='Rounded dev3/MetaBAT context from accepted summaries; no old rescore or refit'),
                  decision=dict(disposition='KEEP as a provisional recovery-focused research candidate',
                      original_numerical_keep=True, integrity_noncollapse_and_all_population_contracts_pass=True,
                      reason='Both separately scoped post-R95 endpoints improve, oral exceeds +0.5pp, and neither >=90% target count falls. No population is removed or hidden; losses in short/neighborhood precision, unassignment and oral parent recovery are explicitly retained.',
                      limitation='This is a bundle result with a large fixed-refiner interaction, not proof that removing false negatives caused a gain, uniform improvement or a product/default promotion. All tested communities are development.'),
                  local_review=dict(clock=read(root / 'local-clock.json'), stages=resources,
                      peak_sampled_RSS_bytes=max(x['resources']['peak_sampled_rss_bytes'] for x in resources if x.get('resources')),
                      peak_extra_review_bytes=max(x['extra_local_peak_bytes'] for x in resources),
                      core_review_cumulative_seconds=max(x['elapsed_cumulative_seconds'] for x in resources),
                      scope='Only new E016 partitions evaluated; accepted local features/truth/marker evidence reused read-only. No local neural inference, refit, regrouping, old rescore or cloud execution.'),
                  limitations=['E009: full156targets/554661890bp, 3.3034% N-quarantine retained; incomplete unique-origin assembly support constrains absolute recovery.',
                               'Oral: separately named origin oracle, full799targets/2083072211bp including2zeroGSA targets;1734nonACGTbp and49knownsharedqueries/12063bp; unique support and exhaustive near-overlap unadmitted.',
                               'All145702E009contigs/231678157bp and1286547nonemptyoralcontigs/1669981123bp are accounted, including short/excluded/unknown/non-target/marker-negative/unassigned DNA and two original zero-bp oral rows in input accounting.',
                               'Original Mac allclose remains failed. Native exact reload and original native vectors are admitted; no tolerance widening or local neural inference.',
                               'No historical gradient trajectory or full-community initial tensor snapshot exists. Source checks, saved states and actual native construction/gradient/EMA/reload contracts establish the stated implementation scope.',
                               'Compact archive contains new graphs/checkpoints/embeddings/partitions/assignments. Omitted native FASTAs, shared views/features/data/runtime are not backed up merely by hashes.'],
                  evidence=evidence)
    (output / 'comparison-review.json').write_text(json.dumps(result, indent=2) + '\n')
    print('E016_COMPARISON_WRITTEN', {u: dict(pair=x['paired_vs_E014'], parent=x['paired_E013_vs_parent'], old=x['paired_E013_vs_old']) for u, x in units.items()}, flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    summarize(args.root, args.output)
