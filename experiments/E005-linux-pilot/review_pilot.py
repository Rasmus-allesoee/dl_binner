#!/usr/bin/env python3
"""Inspect a retained native GI pilot without executing its scientific stages.

Bind the owner archive/log to the immutable local transfer and source commit;
check returned bytes, read-selection receipts, depth/masks, partitions, all DNA,
native AMBER tables and an independent integer-count R95 calculation. Heavy
reads/SAM/BAM are receipt-bound only: they were deliberately not returned. No
mapping, extraction, training, inference or clustering is repeated.
"""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
from dl_binner.io import digest, load_arrays, read_fasta, validate_features


def read(path):
    """Read one retained small JSON record without modifying it."""
    return json.loads(Path(path).read_text())


def table(path):
    """Return a complete TSV table in its retained row order."""
    with Path(path).open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def check(condition, message):
    """Raise a review failure even when Python optimization disables assertions."""
    if not condition:
        raise ValueError(message)


def close(actual, expected):
    """Compare only serialized numerical metrics, never relax artifact identity."""
    np.testing.assert_allclose(float(actual), float(expected), atol=1e-12, rtol=1e-12)


def inventory(attempt):
    """Verify every returned inventory entry; list omitted heavy-file limitations."""
    record = read(attempt/'retained-files.json')
    entries = record['files']
    check(len({e['path'] for e in entries}) == len(entries), 'Duplicate inventory paths')
    omitted = []
    for entry in entries:
        path = attempt/entry['path']
        check(path.resolve().is_relative_to(attempt.resolve()), 'Inventory escapes attempt')
        if entry['in_return']:
            check(path.is_file() and path.stat().st_size == entry['bytes']
                  and digest(path) == entry['sha256'], 'Retained bytes mismatch: '+entry['path'])
        else:
            check(path.suffix in ('.fq', '.sam', '.bam') and not path.exists(),
                  'Unexpected omitted/present artifact: '+entry['path'])
            omitted.append(entry)
    expected = {e['path'] for e in entries if e['in_return']} | {'retained-files.json', 'terminal.log'}
    observed = {str(p.relative_to(attempt)) for p in attempt.rglob('*') if p.is_file()}
    check(expected == observed, 'Uninventoried/missing returned files')
    return dict(retained_files=len(entries), verified_returned_files=len(entries)-len(omitted),
                retained_logical_bytes=sum(e['bytes'] for e in entries),
                returned_logical_bytes=sum((attempt/p).stat().st_size for p in observed),
                omitted_heavy_files=omitted,
                limitation='Heavy file hashes/bytes are native receipts, not independently rehashed locally')


def count_quality(records, assignments):
    """Independently derive confirmed R95 from integer bin/genome overlaps.

    Short/noise/excluded rows stay in full confirmed denominators; ambiguous
    sequence stays in bin denominators only. Require both 200-kb minima, inclusive
    95% purity, one best bin per genome and lexicographic bin ties. Also retain
    the number of qualifying bins as a fragmentation diagnostic, not a tuning rule.
    """
    ids = {r['contig_id'] for r in records}
    check(len(ids) == len(records) and set(assignments) <= ids, 'Duplicate/unknown evaluation IDs')
    total, bins, overlap = Counter(), Counter(), Counter()
    genomes = sorted({r['genome_id'] for r in records})
    for row in records:
        ident, genome, bp = row['contig_id'], row['genome_id'], int(row['bp'])
        if row['confirmed_origin'] == '1':
            total[genome] += bp
        if ident in assignments:
            group = assignments[ident]
            bins[group] += bp
            if row['confirmed_origin'] == '1':
                overlap[genome, group] += bp
    per_genome = {}
    for genome in genomes:
        check(total[genome] >= 200_000, 'Genome below frozen confirmed denominator minimum')
        candidates = [(bp, group) for (g, group), bp in overlap.items()
                      if g == genome and bins[group] >= 200_000 and bp*100 >= bins[group]*95]
        bp, group = min(candidates, key=lambda v: (-v[0], v[1])) if candidates else (0, None)
        per_genome[genome] = dict(total_bp=total[genome], recovered_bp=bp, bin=group,
                                 r95=bp/total[genome],
                                 bin_bp=bins[group] if group is not None else None,
                                 confirmed_purity=bp/bins[group] if group is not None else None,
                                 qualifying_bins=len(candidates))
    return dict(r95=sum(v['r95'] for v in per_genome.values())/len(genomes),
                r95_base_weighted=sum(v['recovered_bp'] for v in per_genome.values())/sum(total.values()),
                inclusive_recovered_counts={str(t): sum(v['recovered_bp']*100 >= int(t*100)*v['total_bp']
                      for v in per_genome.values()) for t in (0.5, 0.9)},
                assigned_bp=sum(bins.values()),
                unassigned_bp=sum(int(r['bp']) for r in records)-sum(bins.values()),
                ambiguous_or_unscored_assigned_bp=sum(int(r['bp']) for r in records
                      if r['contig_id'] in assignments and r['confirmed_origin'] != '1'),
                per_genome=per_genome)


def inspect_amber(folder, records, assignments):
    """Recount every AMBER purity/recall/count entry without invoking AMBER again."""
    sizes, counts, overlaps, overlap_counts = Counter(), Counter(), Counter(), Counter()
    genome_sizes, genome_counts = Counter(), Counter()
    for row in records:
        ident, genome, bp = row['contig_id'], row['genome_id'], int(row['bp'])
        genome_sizes[genome] += bp; genome_counts[genome] += 1
        if ident in assignments:
            group = assignments[ident]
            sizes[group] += bp; counts[group] += 1
            overlaps[group, genome] += bp; overlap_counts[group, genome] += 1
    bins = table(folder/'amber-per-bin.tsv')
    check({r['BINID'] for r in bins} == set(sizes) and len(bins) == len(sizes), 'AMBER bin axis')
    for row in bins:
        group, genome = row['BINID'], row['genome_id']
        check(int(row['tp_length']) == overlaps[group, genome]
              == max(v for (b, g), v in overlaps.items() if b == group), 'AMBER majority overlap')
        for key, expected in dict(total_length=sizes[group], total_seq_counts=counts[group],
                                  tp_seq_counts=overlap_counts[group, genome],
                                  length_gs=genome_sizes[genome], seq_counts_gs=genome_counts[genome]).items():
            check(int(row[key]) == expected, 'AMBER count '+key)
        close(row['precision_bp'], overlaps[group, genome]/sizes[group])
        close(row['precision_seq'], overlap_counts[group, genome]/counts[group])
        close(row['recall_bp'], overlaps[group, genome]/genome_sizes[genome])
        close(row['recall_seq'], overlap_counts[group, genome]/genome_counts[genome])
        close(row['seq_length_mean'], sizes[group]/counts[group])
    recalls = table(folder/'amber-per-genome.tsv')
    check({r['genome_id'] for r in recalls} == set(genome_sizes), 'AMBER full genome denominators')
    for row in recalls:
        group, genome = row['BINID'], row['genome_id']
        maximum = max((v for (b, g), v in overlaps.items() if g == genome), default=0)
        check(int(row['genome_length']) == overlaps[group, genome] == maximum, 'AMBER best overlap')
        check(int(row['genome_seq_counts']) == overlap_counts[group, genome], 'AMBER genome ID count')
        check(int(row['length_gs']) == genome_sizes[genome]
              and int(row['seq_counts_gs']) == genome_counts[genome], 'AMBER short denominator')
        check(int(row['total_length']) == sizes[group], 'AMBER winning bin size')
        close(row['recall_bp'], maximum/genome_sizes[genome])
        close(row['recall_seq'], overlap_counts[group, genome]/genome_counts[genome])
    return dict(bins=len(bins), genomes=len(recalls),
                mean_bin_purity_bp=float(np.mean([float(r['precision_bp']) for r in bins])),
                weighted_bin_purity_bp=sum(int(r['tp_length']) for r in bins)/sum(sizes.values()),
                mean_best_bin_completeness_bp=float(np.mean([float(r['recall_bp']) for r in recalls])))


def inspect_selection(work, sample, omitted):
    """Check one million unique selected ranks/order/offsets and native hash links.

    The original sources are remote; full-stream validity/global bottom-hash
    optimality are supported by the reviewed two-pass native code and receipts,
    not a local reread of those unreturned FASTQs.
    """
    number = sample['sample']; stem = work/'reads'/f'sample_{number}'
    receipt = read(stem.with_suffix('.sample.json'))
    selection = stem.with_suffix('.selection.tsv.gz')
    check(receipt['source_sha256'] == sample['sha256'] and receipt['source'] == sample['reads'], 'Source read identity')
    check(receipt['selection_sha256'] == digest(selection) and receipt['selected_pairs'] == 1_000_000
          and receipt['source_pairs'] <= 20_000_000, 'Selection digest/count/cap')
    check(receipt['salt'] == f'E005-S{number}-pairs-v1:', 'Selection salt')
    seen, last_ordinal, last_offset, maximum = set(), 0, -1, ('', '')
    with gzip.open(selection, 'rt') as stream:
        for row in csv.DictReader(stream, delimiter='\t'):
            ident, ordinal, offset = row['pair_id'], int(row['source_pair_ordinal']), int(row['source_byte_offset'])
            check(re.fullmatch(f'S{number}R[0-9]+', ident) and ident not in seen, 'Selection ID/sample/duplicate')
            check(last_ordinal < ordinal <= receipt['source_pairs'] and last_offset < offset < receipt['source_bytes'], 'Selection source order/offset')
            seen.add(ident); last_ordinal, last_offset = ordinal, offset
            maximum = max(maximum, (hashlib.sha256((receipt['salt']+ident).encode()).hexdigest(), ident))
    check(len(seen) == receipt['selected_pairs'] and list(maximum) == receipt['rank_threshold'], 'Selection size/threshold')
    selected = omitted[f'pilot/reads/sample_{number}.fq']
    check(selected['sha256'] == receipt['sampled_sha256'] and selected['bytes'] == receipt['sampled_bytes'], 'Sampled byte receipt')
    return receipt


def inspect(attempt, archive, terminal, packet):
    """Perform independent retained-evidence review and return a compact receipt."""
    attempt, archive, terminal, packet = (p.resolve() for p in (attempt, archive, terminal, packet))
    check(digest(archive) == archive.with_name(archive.name+'.sha256').read_text().split()[0], 'Archive checksum')
    status, manifest = read(attempt/'status.json'), read(attempt/'bundle-manifest.json')
    check(status['status'] == 'passed' and status['native_linux'] and status['allocated_vcpus'] == 4
          and status['allocated_ram_gb'] == 12 and status['affinity'] == [0, 1, 2, 3], 'Native allocation/result')
    check(manifest == read(packet/'bundle-manifest.json') and manifest['source_commit'] == status['source_commit'], 'Returned transfer/source differs')
    for name, entry in manifest['files'].items():
        check(digest(packet/name) == entry['sha256'] and (packet/name).stat().st_size == entry['bytes'], 'Packet file '+name)
        if not name.startswith('input/'):
            committed = subprocess.check_output(['git', 'show', manifest['source_commit']+':'+name], cwd=ROOT)
            check(hashlib.sha256(committed).hexdigest() == entry['sha256'], 'Packet differs from source commit: '+name)
    stored = inventory(attempt); omitted = {e['path']: e for e in stored['omitted_heavy_files']}
    cfg, runtime = read(attempt/'resolved-config.json'), read(attempt/'runtime.json')
    spec = read(packet/'experiments/E005-linux-pilot/pilot.json')
    inputs = read(packet/'experiments/E005-linux-pilot/pilot-inputs.json')
    contigs = packet/'experiments/E005-linux-pilot/pilot-contigs.tsv'
    records = table(contigs); fasta = packet/'input/pilot/assembly.fna'
    check(digest(fasta) == inputs['fasta_sha256'] and digest(contigs) == inputs['contig_manifest_sha256'], 'Frozen reference/truth hash')
    source = dict(read_fasta(fasta)); ids = list(source); lengths = np.array([len(v) for v in source.values()])
    check(ids == [r['contig_id'] for r in records] and len(ids) == 5309 and lengths.sum() == 12924259, 'Full reference/manifest axis')
    check([int(r['bp']) for r in records] == lengths.tolist(), 'Truth/reference lengths')
    check(cfg['samples'] == spec['samples'] and cfg['columns'] == spec['mean_depth']['columns']
          and cfg['threads'] == 4 and cfg['loader_workers'] == 0 and cfg['rss_bytes'] == 8_000_000_000, 'Frozen resolved input/resources')
    for role in ('binner', 'workflow'):
        inv = runtime[role]['inventory']; accepted = read(packet/'experiments/E005-linux-pilot/linux-observed.json')['runtime'][role]['inventory']
        check(inv['distributions'] == accepted['distributions'] and inv['python'].split()[0] == '3.12.10', 'Runtime inventory '+role)
        check(all(Path(v).is_relative_to(Path(runtime[role]['python']).parents[1]) for v in inv['origins'].values()), 'Runtime origins '+role)
    check(read(attempt/'runtime-preflight-check.json')['status'] == 'passed', 'AMBER v5 gate')
    external_spec = read(packet/'experiments/E005-linux-pilot/external-runtime.json')
    check(runtime['amber']['inventory']['source_files'] == external_spec['source_files']
          and runtime['amber']['inventory']['source_commit'] == external_spec['source_commit'], 'AMBER source hashes')
    # Reapply the exact audited exception policy; this is a comparison, not a runtime probe.
    sys.path.insert(0, str(ROOT/'scripts'))
    from e005_pilot_owner import reconcile_amber_inventory
    amber_policy = read(packet/'experiments/E005-linux-pilot/external-runtime.json')['amber']['lock_reconciliation']
    lock = runtime['original_e001_locks']['amber']
    check(hashlib.sha256(lock['text'].encode()).hexdigest() == lock['sha256'], 'Retained original lock text/hash')
    check(reconcile_amber_inventory(lock['text'], lock['sha256'], runtime['amber']['inventory']['distributions'], amber_policy)
          == read(attempt/'runtime-preflight-check.json'), 'AMBER reconciliation differs')
    work = attempt/'pilot'; read_receipts = []
    tables = []
    for sample in spec['samples']:
        number = sample['sample']; selected = inspect_selection(work, sample, omitted); read_receipts.append(selected)
        mapped = read(work/f'mapping/sample_{number}.mapped.json')
        depth_path = work/f'depth/sample_{number}.tsv'; depth = read(depth_path.with_suffix('.depth.json'))
        check(mapped['sample_receipt_sha256'] == digest(work/f'reads/sample_{number}.sample.json')
              and mapped['reads_sha256'] == selected['sampled_sha256'], 'Map/read provenance')
        check(mapped['reference_sha256'] == depth['reference_sha256'] == digest(fasta)
              and depth['mapped_receipt_sha256'] == digest(work/f'mapping/sample_{number}.mapped.json'), 'Depth/map/reference provenance')
        for suffix in ('sam', 'bam'):
            heavy = omitted[f'pilot/mapping/sample_{number}.{suffix}']
            check(heavy['sha256'] == mapped[suffix+'_sha256'] and heavy['bytes'] == mapped[suffix+'_bytes'], 'Heavy map receipt')
        check(mapped['index_sha256'] == digest(work/f'mapping/sample_{number}.bam.bai')
              and depth['bam_sha256'] == mapped['bam_sha256'], 'BAM/index links')
        axis_rows = mapped['reference_axis']
        check(axis_rows == [[i, int(n)] for i, n in zip(ids, lengths)], 'Native BAM reference axis')
        check(mapped['mapper_threads'] == 4 and mapped['sort_extra_threads'] == 3
              and depth['native_extra_workers'] == 2 and depth['python_aggregator_workers'] == 1, 'Native process budget')
        check('Processing paired-end reads using 4 threads' in (work/f'mapping/sample_{number}.map.stderr').read_text(), 'Effective native mapper threads')
        check(depth['command'][1:] == ['depth','-aa','-q','0','-Q','0','-g','0x600','-G','0x800','-@','2',f'mapping/sample_{number}.bam'], 'Frozen native depth flags')
        check(depth['table_sha256'] == digest(depth_path) and depth['native_positions'] == int(lengths.sum()), 'Depth stream/table binding')
        rows = table(depth_path)
        check([r['contig_id'] for r in rows] == ids and list(rows[0]) == ['contig_id', sample['column']], 'Depth sample/contig axes')
        values = np.array([float(r[sample['column']]) for r in rows]); tables.append(values)
        sums = np.rint(values*lengths).astype(np.int64)
        np.testing.assert_allclose(values*lengths, sums, atol=1e-7, rtol=1e-12)
        check(int(sums.sum()) == depth['aligned_base_observations']
              and int((values == 0).sum()) == depth['zero_contigs'], 'Native depth integer sums/zeros')
    data, meta = load_arrays(work/'features.npz', 'features'); validate_features(data, meta)
    check(data['ids'].tolist() == ids and meta['samples'] == cfg['columns']
          and meta['fasta_sha256'] == digest(fasta) and meta['depth_sha256'] == digest(work/'mean-depth.tsv'), 'Feature hashes/axes')
    np.testing.assert_array_equal(data['lengths'], lengths)
    np.testing.assert_array_equal(data['sequence_sha256'], [hashlib.sha256(dna.encode()).hexdigest() for dna in source.values()])
    check(data['depth'].dtype == np.float64, 'Depth precision')
    np.testing.assert_array_equal(data['depth'], np.array(tables).T)
    merged = table(work/'mean-depth.tsv')
    check([r['contig_id'] for r in merged] == ids and list(merged[0]) == ['contig_id']+cfg['columns'], 'Merged ordered axis')
    np.testing.assert_array_equal(data['depth'], np.array([[float(r[c]) for c in cfg['columns']] for r in merged]))
    check(int(data['eligible'].sum()) == 4212 and int((lengths < 500).sum()) == 1097, 'Eligibility/full shorts')
    training = read(work/'checkpoint.json')
    check(training['config'] == read(packet/'experiments/E004-first-binner/training.json')
          and training['numerical_threads'] == 4 and training['torch_interop'] == 1
          and training['loader_workers'] == 0 and len(training['epochs']) == 20
          and all(e['contigs_seen'] == 4212 for e in training['epochs']), 'Native schedule/all rows')
    check(all(p['num_threads'] <= 4 for p in training['library_pools']), 'Actual numeric pools')
    check(training['sha256'] == digest(work/'checkpoint.pt') and training['training_features_sha256'] == digest(work/'features.npz')
          and training['code_sha256'] == digest(ROOT/'src/dl_binner/model.py'), 'Checkpoint/source parent')
    reference, _ = load_arrays(work/'checkpoint.reference.npz', 'embeddings')
    arms = {}
    for mode in ('raw', 'learned'):
        embedding, emb_meta = load_arrays(work/f'{mode}.embeddings.npz', 'embeddings')
        check(embedding['ids'].tolist() == ids and np.isfinite(embedding['features']).all()
              and emb_meta['features_sha256'] == digest(work/'features.npz'), 'Embedding axis/parent')
        if mode == 'raw':
            expected = np.c_[data['tnf'], np.log1p(data['depth'])].astype(np.float32); expected[~data['eligible']] = 0
            np.testing.assert_array_equal(embedding['features'], expected)
        else:
            for key in ('ids', 'evidence', 'features'):
                np.testing.assert_array_equal(embedding[key], reference[key])
            check(emb_meta['checkpoint_sha256'] == digest(work/'checkpoint.pt'), 'Reload checkpoint parent')
            norms = np.linalg.norm(embedding['features'][embedding['evidence']], axis=1)
            np.testing.assert_allclose(norms, 1, atol=1e-6)
        partition = read(work/f'{mode}.partition.json')
        check(partition['ids'] == ids and partition['embedding_sha256'] == digest(work/f'{mode}.embeddings.npz')
              and partition['parent_features_sha256'] == digest(work/'features.npz'), 'Partition parent/axis')
        check(partition['clustering'] == dict(expected_cluster_count=None, k=5, min_size=3, mutual=True,
              positive_weights=True, query_block=128, resolution=1.0), 'Label-blind clustering settings')
        folder = work/f'{mode}.export'; export = read(folder/'manifest.json'); rows = table(folder/'assignments.tsv')
        check([r['contig_id'] for r in rows] == ids and len(rows) == len(ids), 'Complete assignment axis')
        found = {}; assignments = {}; accounting = Counter(); bp_accounting = Counter(); reasons = Counter()
        for path in folder.glob('*.fna'):
            for ident, dna in read_fasta(path) if path.stat().st_size else []:
                check(ident not in found, 'Duplicate export DNA')
                found[ident] = dna
        check(found == source, 'Complete identical DNA exports')
        for name, entry in export['files'].items():
            check(digest(folder/name) == entry['sha256'] and (folder/name).stat().st_size == entry['bytes'], 'Export byte receipt')
        for i, row in enumerate(rows):
            check(int(row['length']) == lengths[i], 'Assignment length')
            label = partition['assignment'][i]
            expected_status = 'excluded' if not data['eligible'][i] else 'unassigned' if label < 0 else 'assigned'
            expected_reason = str(data['exclusion_reason'][i]) if not data['eligible'][i] else partition['reason'][i]
            check(row['status'] == expected_status and row['reason'] == expected_reason, 'Status/reason preservation')
            if row['status'] == 'assigned':
                check(row['bin_id'] == f'bin_{label+1:06d}' and partition['valid'][i] and data['eligible'][i], 'Assignment/bin validity')
                assignments[row['contig_id']] = row['bin_id']
            else:
                check(not row['bin_id'], 'Noise/exclusion assigned a bin')
                reasons[row['reason']] += 1
            accounting[row['status']] += 1; bp_accounting[row['status']] += int(row['length'])
        check(len(set(assignments.values())) == partition['clusters'] == export['bins'], 'Complete bin count')
        quality = count_quality(records, assignments); retained = read(work/f'{mode}.evaluation/r95.json')
        for key in ('r95','r95_base_weighted','assigned_bp','unassigned_bp','ambiguous_or_unscored_assigned_bp','inclusive_recovered_counts'):
            check(quality[key] == retained[key], 'Independent R95 differs: '+key)
        for genome, result in quality['per_genome'].items():
            for key, value in result.items():
                if key != 'qualifying_bins': check(value == retained['per_genome'][genome][key], 'R95 genome '+key)
        evaluation = read(work/f'{mode}.evaluation/evaluation.json')
        check(evaluation['assignment_sha256'] == digest(folder/'assignments.tsv')
              and evaluation['truth_manifest_sha256'] == digest(contigs), 'Evaluator input hashes')
        native_truth = (work/f'{mode}.evaluation/truth.tsv').read_text().splitlines()[3:]
        native_predictions = (work/f'{mode}.evaluation/predictions.tsv').read_text().splitlines()[3:]
        check(native_truth == [r['contig_id']+'\t'+r['genome_id']+'\t'+r['bp'] for r in records], 'AMBER truth IDs/origins/shorts')
        check(native_predictions == [i+'\t'+assignments[i] for i in ids if i in assignments], 'AMBER assigned-only predictions')
        for s in evaluation['strata']:
            subset = [(r, a) for r, a in zip(records, rows) if int(r['bp']) >= s['lower_bp']
                      and (s['upper_bp'] is None or int(r['bp']) < s['upper_bp'])]
            check(len(subset) == s['contigs'] and sum(int(r['bp']) for r, a in subset) == s['bp'], 'Length-stratum denominator')
            for kind in ('assigned','unassigned','excluded'):
                check(sum(a['status'] == kind for r, a in subset) == s[kind+'_contigs']
                      and sum(int(r['bp']) for r, a in subset if a['status'] == kind) == s[kind+'_bp'], 'Stratum status/bp')
            check(dict(Counter(a['reason'] for r,a in subset if a['status'] != 'assigned')) == s['reasons'], 'Stratum reasons')
            check(sum(int(r['bp']) for r,a in subset if r['confirmed_origin']=='1') == s['confirmed_total_bp'], 'Stratum confirmed denominator')
            check(sum(int(r['bp']) for r,a in subset if r['confirmed_origin']=='1'
                  and quality['per_genome'][r['genome_id']]['bin'] is not None
                  and assignments.get(r['contig_id']) == quality['per_genome'][r['genome_id']]['bin']) == s['confirmed_recovered_bp'], 'Stratum recovered bp')
        arms[mode] = dict(accounting=dict(accounting), bp_accounting=dict(bp_accounting), reasons=dict(reasons),
                          bins=export['bins'], r95=quality, strata=evaluation['strata'],
                          amber=inspect_amber(work/f'{mode}.evaluation', records, assignments))
    rules = {p.stem: read(p) for p in sorted((attempt/'rules').glob('*.json'))}
    check(all(r['exit_code'] == 0 and r['stop_reason'] is None and r['allocated_vcpus'] == 4 for r in rules.values()), 'Rule failure/resource allocation')
    # Inspect actual scheduler events rather than accepting the driver's serial label.
    dag_log = (attempt/'stages/gi-pilot.log').read_text()
    batches = [int(n) for n in re.findall(r'Execute (\d+) jobs', dag_log)]
    parallel_batches = sum(n > 1 for n in batches)
    check(parallel_batches == 2, 'Unexpected changed native scheduling evidence')
    scheduling = dict(declared_serial=status['serial'], actual_serial=False,
        parallel_batches=parallel_batches,
        observed_overlaps=[['train','raw-embed'],['train','raw-cluster'],['train','raw-export'],
                           ['raw-evaluate','learned-evaluate']],
        declared_rule_threads_per_parallel_batch=8, allocation_vcpus=4,
        disposition='accept valid scientific outputs; reject serial-budget claim; local launcher/DAG correction required before new work')
    scheduler_fix = ROOT/'artifacts/e005-linux-pilot/scheduler-review-005/observed.json'
    dag_fix = ROOT/'artifacts/e005-linux-pilot/scheduler-dag-001/observed.json'
    correction = read(scheduler_fix); plan = read(dag_fix)
    check(correction['status'] == plan['status'] == 'passed'
          and correction['production_helper_sha256'] == digest(ROOT/'scripts/e005_owner.py')
          and correction['check_source_sha256'] == digest(ROOT/'experiments/E005-linux-pilot/check_scheduler.py')
          and plan['source_sha256'] == digest(ROOT/'workflows/first-binner/gi_pilot.smk'), 'Local correction evidence/source mismatch')
    scheduling['local_correction'] = dict(scheduler=correction, dag=plan,
        receipt_sha256=digest(scheduler_fix), dag_receipt_sha256=digest(dag_fix),
        prior_harness_attempts=dict(incorrect_base_interpreter=['scheduler-review-001','scheduler-review-002','scheduler-review-003'],
                                   rejected_by_version_check=['scheduler-review-004']),
        native_Linux_corrected_launch=False)
    starts, ends = {}, {}
    for name in rules:
        events = [json.loads(l) for l in (work/'logs'/(name+'.log')).read_text().splitlines() if l.startswith('{')]
        starts[name] = next(e['utc'] for e in events if e['stage']=='stage_start')
        ends[name] = next(e['utc'] for e in events if e['stage']=='stage_end')
    check(max(ends['raw-export'],ends['learned-export']) <= starts['verify']
          and ends['verify'] <= min(starts['raw-evaluate'],starts['learned-evaluate']), 'Truth consumed before verified exports')
    check('Nothing to be done' in (attempt/'stages/completed-resume.log').read_text(), 'Completed work schedules again')
    external = terminal.read_text(); internal = (attempt/'terminal.log').read_text()
    external_events = [json.loads(l) for l in external.splitlines() if l.startswith('{')]
    internal_events = [json.loads(l) for l in internal.splitlines() if l.startswith('{')]
    check(all(e in external_events for e in internal_events), 'External terminal/result mismatch')
    # The historical Bash EXIT trap prints after tee, so its line is outside the
    # captured log. Native stage/result/return events independently establish success.
    check('EXIT_CODE=' not in external or 'EXIT_CODE=0' in external, 'Shell reported failure')
    cost = next(e for e in external_events if e['stage'] == 'cost_through_collection')
    close(cost['allocated_vcpu_hours'], cost['driver_seconds']*4/3600)
    check(status['driver_seconds_before_collection'] <= spec['resources']['total_driver_seconds_ceiling']
          and max(s['peak_sampled_rss_bytes'] for s in status['stages']) < cfg['rss_bytes'], 'Prospective ceilings')
    return dict(record='E005', date='2026-10-06', decision='v5 scientific outputs accepted; serial scheduling nonconformance corrected locally; prepare bounded usability milestone',
                source_commit=manifest['source_commit'],
                archive=dict(path=str(archive.relative_to(ROOT)), sha256=digest(archive), bytes=archive.stat().st_size),
                terminal=dict(path=str(terminal.relative_to(ROOT)), sha256=digest(terminal),
                              exit_trap_line_captured='EXIT_CODE=0' in external,
                              success_evidence='all native stage exit codes, driver_end=passed, return_ready, completed-resume'),
                retained_locator=str(attempt.relative_to(ROOT)), storage=stored,
                reference=dict(sha256=digest(fasta), contig_manifest_sha256=digest(contigs), contigs=len(ids),
                               bp=int(lengths.sum()), eligible=int(data['eligible'].sum()), excluded=int((~data['eligible']).sum()),
                               samples=meta['samples'], zero_depth_per_sample=(data['depth']==0).sum(0).tolist(),
                               zero_depth_rows=int((~data['depth_evidence']).sum())),
                reads=read_receipts, runtime_preflight=read(attempt/'runtime-preflight-check.json'),
                reload_max_abs=0, training={k:training[k] for k in ('config','parameter_count','numerical_threads','torch_interop','loader_workers',
                    'training_wall_seconds','training_process_cpu_seconds','training_average_cpus')},
                arms=arms, resources=dict(allocation_vcpus=4, allocation_ram_gb=12, cost_through_collection=cost,
                    scheduling=scheduling,
                    driver_seconds_before_collection=status['driver_seconds_before_collection'],
                    stage_resources=status['stages'], rule_resources=rules,
                    limitations='sampled descendant RSS/CPU; not exact peak/invoice; outer launch/upload/idle and environment storage excluded'),
                scope=dict(development=True, whole_MAG_quality=False, independent_generalization=False,
                    coverage_benefit_isolated=False, heavy_sources_locally_rehashed=False,
                    repeated_scientific_stages=[], architecture_comparison_run=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('attempt','archive','terminal','packet','output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.attempt, args.archive, args.terminal, args.packet)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(status='passed', receipt=str(args.output), returned_hashes=result['storage']['verified_returned_files'],
                          raw_r95=result['arms']['raw']['r95']['r95'], learned_r95=result['arms']['learned']['r95']['r95'])))
