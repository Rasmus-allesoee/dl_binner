#!/usr/bin/env python3
"""Summarize the admitted E031 bridge without rescoring historical baselines.

All target unions and secondary tiers come from frozen new-output reviewers or
the accepted E023 reuse. Integer denominators independently reconstruct the
primary decisions. No bin selection, fit, threshold tuning or dataset routing.
"""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e024_coverage import binding, write
from e029_summary import changed
from e031_decision import disposition, UNITS, REFERENCES


def read(path):
    """Read a closed retained JSON summary."""
    return json.loads(Path(path).read_text())


def table(path):
    """Read full-target integer TSV evidence without opening scientific partitions."""
    with Path(path).open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def summarize(base, output):
    """Retain every target, teacher/student and density/marker effect beside anchors."""
    base, output = Path(base).absolute(), Path(output).absolute()
    admission = read(base/'admission.json')
    if not admission['workflow_completed']:
        raise ValueError('Independent bridge admission missing')
    old = {(r['unit'], r['role'], r['genome']): r for r in table(ROOT/'experiments/E030-supported-biological-bins/comparison-targets.tsv')}
    e023 = {r['genome']: r for r in table(ROOT/'experiments/E023-adaptive-density-bins/comparison-targets.tsv') if r['dataset'] == 'E009'}
    oldsummary = read(ROOT/'experiments/E030-supported-biological-bins/comparison-review.json')
    frozen_e023 = read(ROOT/'experiments/E023-adaptive-density-bins/comparison-review.json')['datasets']['E009']['arms']
    arms, target_rows, metrics, oldmetrics, evidence = {}, [], {}, {}, {}
    for unit in UNITS:
        dataset = 'E009' if unit.startswith('E009') else 'oral'
        for role in ['teacher', 'student']:
            reuse = unit == 'E009-GLM' and role == 'student'
            key = unit+'/'+role; values, targets = {}, {}
            record = None
            if not reuse:
                path = base/('review-'+unit+'-'+role)/'review.json'; record = read(path)
                if record['contract']['status'] != 'PASS' or record['contract']['unit'] != unit or record['contract']['role'] != role:
                    raise ValueError('New review identity differs')
                evidence[str(path.relative_to(ROOT))] = binding(path)
            for arm in ['density', 'selected']:
                if reuse:
                    rows = [dict(genome=g, reference_bp=int(r['reference_bp']), recovered_bp=int(r[arm+'_bp']),
                                 assembly_confirmed_bp=int(r['assembly_confirmed_bp'])) for g, r in e023.items()]
                    summary = frozen_e023[arm]['recovery']
                    values[arm] = dict(primary=summary, accepted_summary_reused=True, old_output_rescored=False)
                else:
                    value = record['arms'][arm]
                    primary = value['grouping'] if dataset == 'E009' else value['evaluation']['origin']
                    rows, summary = primary['recovery'], primary['recovery_summary']
                    values[arm] = dict(primary=summary, export=value['export_contract'], partition=value['partition'],
                        secondary={mode: {k: v for k, v in quality.items() if k != 'bins'} for mode, quality in value['secondary'].items()},
                        secondary_not_formal_MIMAG_HQ=True)
                    if dataset == 'oral':
                        values[arm]['known_shared_sensitivity'] = value['evaluation']['known_shared_mask']['recovery_summary']
                axis = {r['genome']: r for r in rows}
                if (len(rows) != len(axis) or len(rows) != (156 if dataset == 'E009' else 799)
                        or sum(r['reference_bp'] for r in rows) != REFERENCES[unit]
                        or abs(sum(r['recovered_bp'] for r in rows)/REFERENCES[unit]-summary['bp_weighted_R95']) > 1e-15
                        or any(int(old[unit, role, g]['reference_bp']) != r['reference_bp'] for g, r in axis.items())):
                    raise ValueError('Full target/integer reconstruction differs')
                targets[arm] = axis
            prior = {g: int(old[unit, role, g]['post_bp']) for g in targets['selected']}
            density = {g: r['recovered_bp'] for g, r in targets['density'].items()}
            selected = {g: r['recovered_bp'] for g, r in targets['selected'].items()}
            arms[key] = dict(arms=values, density_to_marker=changed(density, selected),
                selected_vs_same_learning_E030=changed(prior, selected), accepted_E023_reuse=reuse,
                retained_E030=oldsummary['arms'][key]['arms']['post']['primary'])
            if role == 'student':
                metrics[unit] = dict(recovered_bp=sum(selected.values()), reference_bp=REFERENCES[unit],
                                     target_90=values['selected']['primary']['at_least_90_percent'])
                oldmetrics[unit] = dict(recovered_bp=sum(prior.values()), reference_bp=REFERENCES[unit],
                                        target_90=oldsummary['primary_student_metrics'][unit]['at_least_90_percent'])
            for g, row in sorted(targets['selected'].items()):
                target_rows.append(dict(dataset=dataset, unit=unit, role=role, genome=g,
                    reference_bp=row['reference_bp'], assembly_confirmed_bp=row['assembly_confirmed_bp'],
                    density_bp=density[g], selected_bp=selected[g], E030_same_learning_bp=prior[g],
                    selection_effect_bp=selected[g]-density[g], selected_vs_E030_bp=selected[g]-prior[g],
                    retained_MetaBAT2_bp=int(old[unit, role, g]['retained_MetaBAT2_bp']),
                    accepted_E023_reuse=reuse))
    output.mkdir(parents=True, exist_ok=True)
    path = output/'bridge-targets.tsv'
    with path.open('x') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(target_rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(target_rows)
    if len(target_rows) != 2222:
        raise ValueError('Full six-actor reference population differs')
    result = dict(status='COMPLETED_REVIEWED', phase=admission['phase'], checked_UTC=datetime.now(timezone.utc).isoformat(),
        source=admission['source'], frozen_decision=disposition('bridge', oldmetrics, metrics, {}),
        primary_integer_metrics=metrics, arms=arms, target_table=binding(path), target_rows=len(target_rows),
        raw_new_review_bindings=evidence, old_baselines_rescored=False, new_fits=0,
        learning_authorized_regardless_of_bridge_quality=True,
        denominator_bp=dict(E009=554661890, oral=2083072211), N_quarantine_percent=3.3034,
        oral_semantics='Provided-origin oracle plus retained known-shared sensitivity; not exhaustive unique-source truth',
        no_dataset_winner_router=True, no_causal_graph_vs_selection_or_learning_claim=True,
        original_Mac_portability_tolerance_unchanged=True, independent_confirmation=False)
    write(output/'bridge-review.json', result)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); result = summarize(a.base, a.output)
    print(json.dumps(dict(decision=result['frozen_decision'], primary=result['primary_integer_metrics'])))
