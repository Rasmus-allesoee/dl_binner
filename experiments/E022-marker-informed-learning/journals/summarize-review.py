#!/usr/bin/env python3
"""Summarize the admitted E022 review and retained E021 results without rescoring.

Input is the already verified inspection directory, including the frozen evaluator
output, native receipts and current financial admission. Output is a new compact
comparison JSON, all-target TSV, inspection receipt and allocation/storage ledger
in this experiment. Existing reports are refused. This script performs no fit,
inference, truth derivation, new genome scoring, cloud call or resource mutation.
"""
import argparse
import csv
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

REPO = Path(__file__).absolute().parents[3]
EXPERIMENT = REPO / 'experiments/E022-marker-informed-learning'


def read(path):
    """Read an explicit retained JSON artifact without modifying it."""
    return json.loads(Path(path).read_text())


def binding(path):
    """Bind a regular local artifact for the compact reproducibility record."""
    path = Path(path)
    return dict(bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def write(path, value):
    """Create a new report; refuse overwriting an existing reviewed record."""
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def summarize(root):
    """Join fixed target axes, describe trade-offs and price actual VM intervals."""
    root = Path(root).absolute()
    review_path = root / 'local-review-attempt1/diagnostics-E009-relational/review.json'
    review = read(review_path)
    resources = read(root / 'local-review-attempt1/diagnostics.resources.json')
    native = read(root / 'native-contract-review.json')
    completion = read(root / 'return/completion.json')
    provider = read(root / 'cloud/instance.json')
    finance = read(root / 'financial-export-admission.json')
    verification = read(root / 'archive-verification.json')
    original_inventory = read(root / 'inventory.json')
    baseline_path = REPO / 'experiments/E021-frozen-sequence-hybrid/comparison-review.json'
    baseline = read(baseline_path)
    baseline_targets_path = baseline_path.with_name('comparison-targets.tsv')
    baseline_targets = {row['genome']: row for row in csv.DictReader(baseline_targets_path.open(), delimiter='\t')}
    assert provider['status'] == 'TERMINATED'
    assert native['native_source'] == 'e88dc8a513e0408cf96dcc9462aa8ba077d7321e'
    assert verification['archive']['sha256'] == 'd7d709969070ee0831e2a765eacf6e3588de725cf37e2ca914c58022423c4cd9'
    assert completion['status'] == 'SUCCESS' and resources['status'] == review['status'] == 'SUCCESS'
    assert native['status'] == 'PASS_NATIVE_EXIT_SOURCE_REUSE_AND_SUPERVISION'
    assert verification['every_member_verified'] and finance['original_phase_with_run_disk_export_and_reserves_USD'] < 2
    assert resources['seconds'] < 3600 and resources['peak_extra_bytes'] < 6 * 1024**3
    assert resources['resources']['peak_sampled_rss_bytes'] < 8_000_000_000
    arms = {}
    for arm in ['pre', 'old', 'post']:
        value = review['arms'][arm]
        arms[arm] = dict(recovery=value['diagnostics']['recovery_summary'],
                         diagnostics=value['diagnostics'], populations=value['populations'],
                         accounting=review['contracts'][arm], bins=len(value['grouping']['bins']),
                         clean_marker_by_status=value['grouping']['clean_marker_by_status'])
    targets = {arm: {row['genome']: row for row in arms[arm]['diagnostics']['recovery']} for arm in arms}
    assert all(set(rows) == set(baseline_targets) and len(rows) == 156 for rows in targets.values())
    table = []
    for genome in sorted(targets['post']):
        target = targets['post'][genome]
        old = baseline_targets[genome]
        assert target['reference_bp'] == int(old['reference_bp'])
        row = dict(dataset='E009_conservative_v2', genome=genome, reference_bp=target['reference_bp'],
                   assembly_confirmed_bp=target['assembly_confirmed_bp'])
        row.update({f'E021_{arm}_bp': int(old[f'E021_{arm}_bp']) for arm in arms})
        row.update({f'E022_{arm}_bp': targets[arm][genome]['recovered_bp'] for arm in arms})
        row['delta_vs_E021_post_bp'] = row['E022_post_bp'] - row['E021_post_bp']
        table.append(row)
    denominator = sum(row['reference_bp'] for row in table)
    assert denominator == 554661890
    delta_bp = sum(row['delta_vs_E021_post_bp'] for row in table)
    new = arms['post']['recovery']
    old = baseline['arms']['post']['recovery']
    delta = new['bp_weighted_R95'] - old['bp_weighted_R95']
    assert abs(delta - delta_bp / denominator) < 1e-14
    keep = delta >= .005 and new['at_least_90_percent'] >= old['at_least_90_percent']
    abandon = new['bp_weighted_R95'] <= old['bp_weighted_R95'] and new['at_least_90_percent'] <= old['at_least_90_percent']
    disposition = 'KEEP' if keep else 'ABANDON' if abandon else 'MODIFY'
    transitions = {}
    for threshold in [.5, .9]:
        transitions[str(threshold)] = {
            direction: [row['genome'] for row in table
                        if ((row['E021_post_bp'] / row['reference_bp'] < threshold <= row['E022_post_bp'] / row['reference_bp'])
                            if direction == 'gain' else
                            (row['E022_post_bp'] / row['reference_bp'] < threshold <= row['E021_post_bp'] / row['reference_bp']))]
            for direction in ['gain', 'loss']}
    population = read(REPO / 'experiments/E009-competitive-benchmark/truth-population-review.json')
    bins = review['arms']['post']['grouping']['bins']
    bacterial_bins = [row for row in bins if population['genomes'].get(row['dominant_genome'], {}).get('lineage_class') == 'bacterial']
    decisions = read(root / 'verified/work/units/E009-relational/refine/decisions.json')
    sources = []
    for tool, relative in [('vamb', 'vamb/cluster.py'), ('metabat', 'src/metabat2.cpp')]:
        checkout = REPO / 'agent_context/tools_repo' / tool
        assert Path(subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', '--show-toplevel'], text=True).strip()) == checkout
        commit = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        data = subprocess.check_output(['git', '-C', str(checkout), 'show', 'HEAD:' + relative])
        assert (checkout / relative).read_bytes() == data
        sources.append(dict(tool=tool, commit=commit, file=relative, binding=binding(checkout / relative),
                            scope='Read-only source check; no external tool execution or measured speed comparison'))
    result = dict(
        record='E022 frozen new-output-only independent review', status='REVIEWED',
        reviewed_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        phase='marker-20261026T012935Z-e88dc8a-r2', scientific_candidate='fdad862',
        operational_execution_source=native['native_source'],
        evidence=dict(local_review=str(review_path.relative_to(REPO)), local_review_binding=binding(review_path),
                      baseline=binding(baseline_path), baseline_targets=binding(baseline_targets_path),
                      archive=verification['archive'], native_contract=binding(root / 'native-contract-review.json')),
        scope='One seed / E009 development assembly only. New candidate scored once; E021 and every older summary reused without rescoring/refitting.',
        full_reference=dict(targets=156, bp=denominator, N_quarantine_percent=3.3034,
                            confirmed_assembly_union_bp=sum(row['assembly_confirmed_bp'] for row in table),
                            scope='Conservative support under current truth, not actual complete assembly content or a proof all support can form pure bins.'),
        arms=arms, paired_vs_E021=dict(delta_R95=delta, delta_percentage_points=100 * delta, delta_recovered_bp=delta_bp,
                                      gains=sum(row['delta_vs_E021_post_bp'] > 0 for row in table),
                                      losses=sum(row['delta_vs_E021_post_bp'] < 0 for row in table),
                                      unchanged=sum(row['delta_vs_E021_post_bp'] == 0 for row in table),
                                      target50_before=old['at_least_50_percent'], target50_after=new['at_least_50_percent'],
                                      target90_before=old['at_least_90_percent'], target90_after=new['at_least_90_percent']),
        target_gains=sorted([row for row in table if row['delta_vs_E021_post_bp'] > 0], key=lambda row: -row['delta_vs_E021_post_bp']),
        target_losses=sorted([row for row in table if row['delta_vs_E021_post_bp'] < 0], key=lambda row: row['delta_vs_E021_post_bp']),
        threshold_transitions=transitions,
        paired_refinement={arm: dict(delta_R95_vs_parent=arms[arm]['recovery']['bp_weighted_R95'] - arms['pre']['recovery']['bp_weighted_R95'],
                                     recovered_bp=sum(target['recovered_bp'] for target in targets[arm].values())) for arm in arms},
        constraint_label_consistency=review['constraint_label_consistency'], pair_contract=review['pair_contract'],
        training={key: value for key, value in review['checkpoint'].items() if key not in ['history', 'transform']},
        geometry_history=[dict(epoch=row['epoch'], geometry=row['geometry'], relation_pairs_exposed=row['relation_pairs_exposed'],
                               relation_weight=row['relation_weight'], relation_positive=row['relation_positive'],
                               relation_negative=row['relation_negative']) for row in review['checkpoint']['history']],
        raw_learned_geometry=review['raw_learned_geometry'], preserved_E021_raw_learned_geometry=baseline['raw_learned_geometry'],
        preserved_E021_post_geometry=baseline['arms']['post']['diagnostics']['geometry'],
        preserved_E021_post_lineage_geometry=baseline['arms']['post']['diagnostics']['geometry_by_lineage'],
        preserved_E021_post_B3=baseline['arms']['post']['diagnostics']['restricted_B3'],
        native_neighbor_proof=review['native_graph_review'], token_contract=review['token_contract'],
        choices=review['choices'], refinement=review['refinement'],
        refinement_selected_counts={key: sum(row['selected'] == key for row in decisions) for key in sorted({row['selected'] for row in decisions})},
        bin_size_diagnostic=dict(all_bins=len(bins), all_under200kb=sum(row['all_bp'] < 200000 for row in bins),
                                 all_bp_under200kb=sum(row['all_bp'] for row in bins if row['all_bp'] < 200000),
                                 bacterial_dominant_bins=len(bacterial_bins),
                                 bacterial_dominant_under200kb=sum(row['all_bp'] < 200000 for row in bacterial_bins),
                                 bacterial_dominant_bp_under200kb=sum(row['all_bp'] for row in bacterial_bins if row['all_bp'] < 200000),
                                 scope='Diagnostic dominant-origin stratification only; not a truth-selected merge or estimate that small bins should all merge.'),
        preserved_context=baseline['preserved_context'], portability=review['portability'],
        disposition=dict(result=disposition, KEEP_passed=keep, ABANDON_passed=abandon,
                         required_R95_gain=.005, observed_R95_gain=delta,
                         no_target90_loss=new['at_least_90_percent'] >= old['at_least_90_percent'],
                         semantics='Original prospective practical rule unchanged; no product promotion or marker-family rejection.'),
        interpretation='Small bacterial neighbor/grouping gains and two more >=90% targets coexist with slightly lower full-reference R95. ASV406.4 no longer has a passing bin; the largest retained dominant bin has conservative purity 0.762798. This is not collapse, proof of a critical implementation bug, or proof all impurity is biological contamination.',
        next_decision=dict(recommendation='Locally implement one adaptive-density, abundance/marker-informed bin-construction block using fixed retained representations; prepare a two-community cached comparison with explicit different frozen learning anchors.',
                           reason='The fixed global CPM plus split-only alternatives leave both mixed bins and fragmentation. Improve bin construction before another larger model or pair-weight grid; evaluate the hypothesis rather than claim grouping is proven the sole bottleneck.',
                           prospective_scope='E022 E009 vectors and existing E019 oral sequence-only vectors remain untouched, each compared with its preserved CPM/E013 output. The same new downstream policy must work with explicit absence of depth; this does not validate E022 learning without depth.',
                           sources=sources, implementation_or_execution_performed=False),
        limitations=['Full provided denominators and conservative N/competitive ambiguity remain; this is not whole-MAG quality.',
                     'Positive dominant-label agreements are not unique DNA identity; unresolved pairs remain unresolved.',
                     'No matched community zero-side-loss control: retain original construction/RNG/BN contracts but do not claim every ingredient isolated.',
                     'No oral/skin E022 learning or independent unseen-genome validation; pretrained/panel overlap uncertain.',
                     'Original failed Mac allclose tolerance remains failed; native reload is exact, omitted bulk is not reread locally.',
                     'E017/E018 oral regressions prohibit assuming another grouping change generalizes; require matched two-community no-regression gates.'],
        confirmation_limits='Skin stays unscored under original 610-target provided-origin protocol; source/genome/replicon/molecule/host/circular/taxonomy/overlap/pretraining/competitive ambiguity/unique-versus-origin/evaluator/real-depth/cost/retention admission remain explicit. Additional independent depth-enabled community requires a new prospective scope.')
    with (EXPERIMENT / 'comparison-targets.tsv').open('x') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(table[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(table)
    write(EXPERIMENT / 'comparison-review.json', result)
    first = read(REPO / 'artifacts/e022-native/20261026T010043Z-fdad862/stop-dl-binner-cpu-1792978036459895000.json')
    def interval(state, label):
        start, stop = [datetime.datetime.fromisoformat(state[key]) for key in ['lastStartTimestamp', 'lastStopTimestamp']]
        return dict(attempt=label, start_UTC=start.astimezone(datetime.timezone.utc).isoformat(),
                    stop_UTC=stop.astimezone(datetime.timezone.utc).isoformat(), seconds=(stop - start).total_seconds(),
                    scope='Provider reported successful allocation start to lastStopTimestamp, not sampled process CPU or exact invoice')
    intervals = [interval(first, 'First failed remote parse before setup/science'), interval(provider, 'Repaired native phase')]
    seconds = sum(row['seconds'] for row in intervals)
    export_bytes = sum(path.stat().st_size for path in (root / 'return').iterdir() if path.is_file())
    rate = finance['compute_IP_rate_USD_per_hour']
    compute = seconds / 3600 * rate
    disks = seconds / 3600 * 31.2 / 730
    export = export_bytes / 1024**3 * .12
    storage_bytes = read(root / 'cloud/objects-live.json')['bytes']
    created = datetime.datetime.strptime(read(root / 'cloud/e022-evidence-tar-gz-metadata.json')['creation_time'], '%Y-%m-%dT%H:%M:%S%z').timestamp()
    retention = datetime.datetime.fromisoformat('2026-10-28T00:00:00+01:00').timestamp()
    return_storage = export_bytes / 1024**3 * .02 * (retention - created) / 3600 / 730
    subtotal = compute + disks + export + return_storage
    cost = dict(record='Measured-allocation pricing, not invoice or credit-delta attribution',
                phase=result['phase'], resource='Existing e2-standard-8; 30 GiB pd-standard + 300 GiB pd-balanced unchanged',
                intervals=intervals, measured_allocation_seconds=seconds, allocated_vCPU_hours=seconds / 3600 * 8,
                compute_RAM_IP_USD=compute, combined_VM_IP_rate_USD_per_hour=rate,
                existing_disk_attribution_USD=disks, exported_bytes=export_bytes,
                conservative_paid_export_USD=export, new_return_storage_through_original_boundary_USD=return_storage,
                priced_subtotal_USD=subtotal, operations_reserve_USD=.10, contingency_USD=.50,
                gross_with_reserves_USD=subtotal + .60, original_new_ceiling_USD=2,
                fresh_financial_gate=finance, current_Catalog_binding=binding(root / 'cloud/current-prices.json'),
                GCS_inventory=binding(root / 'cloud/objects-live.json'),
                storage_current_approved_until='2026-10-28T00:00:00+01:00',
                existing_stopped_disks_conservative_USD_per_month=31.2,
                storage_proposal=dict(approved=False, new_storage_only_ceiling_USD=8,
                                      from_Copenhagen='2026-10-28T00:00:00+01:00', until_Copenhagen='2026-11-04T00:00:00+01:00',
                                      forecast_with_2GiB_extra_GCS_and_half_dollar_reserve_USD=31.2*168/730+(storage_bytes/1024**3+2)*.02*168/730+.5,
                                      eligibility='Same ordinary PD/GCS products appear credit-eligible; fresh credit/delayed-usage/inventory gate before approval is exercised.',
                                      action='Owner approval needed before current boundary. No automatic renewal or deletion.'),
                process_resources=native['stage_resources'],
                caveats=['VM/IP prices conservatively ignore free allowances; actual discounts/invoice may differ.',
                         'Existing disk and GCS attribution overlaps the separate original $8 storage interval; do not double-count.',
                         'No compute, new object upload, service/resource change or retention extension in this inspection.',
                         'Original first-start two-hour clock includes stopped time; charged allocation sums only two actual running intervals.',
                         'Completion upload occurs after the pre-upload receipt, and was independently received/hash-bound.'],
                price_sources=['https://cloud.google.com/storage/pricing', 'https://docs.cloud.google.com/free/docs/free-cloud-features'])
    assert cost['gross_with_reserves_USD'] < 2
    write(EXPERIMENT / 'cost-review.json', cost)
    archive_summary = {key: verification[key] for key in ['status', 'archive', 'regular_members', 'logical_member_bytes', 'every_member_verified', 'aliases']}
    archive_summary['full_verification_binding'] = binding(root / 'archive-verification.json')
    archive_summary['full_inventory_binding'] = binding(root / 'inventory.json')
    inspection = dict(status='COMPLETE_AND_INDEPENDENTLY_REVIEWED', phase=result['phase'],
                      reviewed_UTC=result['reviewed_UTC'], provider_status='TERMINATED', provider=binding(root / 'cloud/instance.json'),
                      guest=binding(root / 'cloud/guest.json'), completion=binding(root / 'return/completion.json'),
                      watchdog=binding(root / 'return/watchdog-exit.json'), archive=archive_summary,
                      native_contract=native, local_review_resources=resources['resources'],
                      original_local_review_seconds=resources['seconds'],
                      local_review_peak_extra_bytes=resources['peak_extra_bytes'],
                      local_root=str(root.relative_to(REPO)),
                      omitted_work_members=len(original_inventory['omitted_retained_on_disk']),
                      omitted_work_logical_bytes=sum(row['bytes'] for row in original_inventory['omitted_retained_on_disk'].values()),
                      complete_work_logical_members=len(original_inventory['all_work_members']),
                      complete_work_logical_bytes=sum(row['bytes'] for row in original_inventory['all_work_members'].values()),
                      omissions='1,367,669,888 B frozen vectors and 233,607,419 B emitted DNA remain native; original context/FASTA inputs are separate retained dependencies, not backed up by these hashes.',
                      review_scope='Every returned member and alias checked; omitted native bulk uses bound in-place receipts/inventories, not a local reread.',
                      historical_failures='Original first-start parse/release failures and Mac portability remain. Preliminary inspection probes failed before affected checks (download not yet complete; wrong gates/stages schema key; compact baseline omitted query rows); recorded separately. Frozen evaluator ran once successfully.',
                      prohibited_work_performed=False, comparison='comparison-review.json', costs='cost-review.json')
    write(EXPERIMENT / 'inspection-observed.json', inspection)
    print('E022_REVIEW_SUMMARY', disposition, dict(delta_bp=delta_bp, target90=new['at_least_90_percent'], gross_USD=cost['gross_with_reserves_USD']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    summarize(parser.parse_args().root)
