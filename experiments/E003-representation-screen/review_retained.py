#!/usr/bin/env python3
"""Independently check accepted E003 artifacts and publish compact result records.

Read source DNA, pinned manifests, retained arrays, partitions and resource logs.
Recompute fourmer counts, cosine neighbors and fragment metrics without importing
the producer's scoring/geometry code. Never load the GLM, fit new communities or
alter a scientific output. Write observed.json, metrics.tsv and retained-files.json
only after checks pass; these summarize development grouping, not MAG recovery.
"""
import csv
import hashlib
import itertools
import json
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUN = ROOT / 'artifacts/e003-representation-screen/run-001'
TRANSLATE = str.maketrans('ACGTRYSWKMBDHVN', 'TGCAYRSWMKVHDBN')


def sha(path):
    """Hash file bytes in bounded chunks, including large read-only model files."""
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def load(path):
    """Read a retained JSON record without modifying it."""
    return json.loads(path.read_text())


def fasta(path):
    """Parse complete FASTA sequences in order and reject duplicate identifiers."""
    records, ident, sequence = {}, None, []
    for line in path.read_text().splitlines():
        if line.startswith('>'):
            if ident is not None:
                assert ident not in records
                records[ident] = ''.join(sequence).upper()
            ident, sequence = line[1:].split()[0], []
        else:
            assert ident is not None
            sequence.append(line.strip())
    assert ident is not None and ident not in records
    records[ident] = ''.join(sequence).upper()
    return records


def aggregate(values, lengths, indices, weighted=False):
    """Calculate full-denominator means; unassigned rows are already zero P/R."""
    weights = lengths[indices] if weighted else np.ones(len(indices))
    means = np.average(values[indices], axis=0, weights=weights)
    neighbor, precision, recall, assigned = map(float, means)
    return dict(fragments=len(indices), bp=int(lengths[indices].sum()),
                neighbor_purity=neighbor, b3_precision=precision, b3_recall=recall,
                b3_f1=2*precision*recall/(precision+recall) if precision+recall else 0,
                assigned_fraction=assigned)


def main():
    """Validate the sole completed attempt and bind small summaries to its bytes."""
    config = load(HERE/'config.json')
    panel = load(HERE/'panel.json')
    sources = load(HERE/'sources.json')
    assert sha(HERE/'panel.json') == config['panel_manifest_sha256']
    assert sha(HERE/'sources.json') == panel['source_manifest_sha256']
    assert sha(ROOT/config['panel_fasta']) == panel['fna_sha256']
    sequences = fasta(ROOT/config['panel_fasta'])
    rows = panel['rows']
    ids = [r['id'] for r in rows]
    lengths = np.array([r['bp'] for r in rows])
    truth = np.array([r['genome'] for r in rows])
    assert list(sequences) == ids == sorted(ids) and len(ids) == 320
    assert int(lengths.sum()) == panel['bp'] == 945152
    assert len(set(truth)) == 16 and all(sum(truth == g) == 20 for g in set(truth))
    assert all(sum(lengths == n) == 64 for n in (500, 768, 1000, 2500, 10000))
    ambiguity, invariant = 0, []
    for source in sources['sources']:
        path = ROOT/source['fasta_path']
        assert sha(path) == source['fasta_sha256']
        metadata = path.parent/(source['requested_accession']+'.xml')
        assert sha(metadata) == source['metadata_sha256']
        dna, = fasta(path).values()
        assert len(dna) == source['length']
        assert hashlib.sha256(dna.encode()).hexdigest() == source['sequence_sha256']
        accession = source['accession_version']
        chosen = [r for r in rows if r['genome'] == accession]
        intervals = sorted((r['start'], r['end']) for r in chosen)
        assert all(a[1] <= b[0] for a, b in zip(intervals, intervals[1:]))
        cells = sorted(range(len(dna)//20000), key=lambda cell: hashlib.sha256(
            f'E003-v1:{accession}:cell:{cell}'.encode()).hexdigest())[:20]
        expected = set()
        for index, cell in enumerate(cells):
            bp = (500, 768, 1000, 2500, 10000)[index//4]
            offset = int(hashlib.sha256(f'E003-v1:{accession}:offset:{index}'.encode()).hexdigest(), 16)
            start = cell*20000 + offset % (20000-bp+1)
            expected.add((start, start+bp))
        assert set(intervals) == expected
        for row in chosen:
            seq = sequences[row['id']]
            assert dna[row['start']:row['end']] == seq and len(seq) == row['bp']
            assert row['id'] == 'F'+hashlib.sha256(f'{accession}:{row["start"]}:{len(seq)}'.encode()).hexdigest()[:16]
            assert hashlib.sha256(seq.encode()).hexdigest() == row['sequence_sha256']
            canonical = min(seq, seq.translate(TRANSLATE)[::-1])
            canonical_hash = hashlib.sha256(canonical.encode()).hexdigest()
            assert canonical_hash == row['strand_invariant_sha256']
            invariant.append(canonical_hash)
            ambiguous = sum(base not in 'ACGT' for base in seq)
            assert ambiguous == row['ambiguity_bases']
            ambiguity += ambiguous
    assert ambiguity == 3 and len(set(invariant)) == 320
    pin = load(ROOT/config['model_pin'])
    for filename, receipt in pin['files'].items():
        assert sha(ROOT/config['model_directory']/filename) == receipt['sha256']
    retained_scores = load(RUN/'scores.json')
    commit = retained_scores['source_commit']
    assert retained_scores['config'] == config
    for name in ('scripts/e003_representation_screen.py', 'scripts/dnabert_s_cpu_spike.py',
                 'workflows/e003-screen/Snakefile', 'experiments/E003-representation-screen/config.json',
                 'experiments/E003-representation-screen/panel.json', 'experiments/E003-representation-screen/sources.json'):
        committed = subprocess.check_output(['git', 'show', f'{commit}:{name}'], cwd=ROOT)
        assert hashlib.sha256(committed).hexdigest() == sha(ROOT/name)
    summaries, details = {}, {}
    canonical_kmers = sorted({min(k, k.translate(TRANSLATE)[::-1])
                             for k in map(''.join, itertools.product('ACGT', repeat=4))})
    for method, width in (('tnf', 136), ('glm', 768)):
        receipt = load(RUN/f'{method}.features.json')
        path = RUN/f'{method}.features.npz'
        assert sha(path) == receipt['sha256'] and receipt['source_commit'] == commit
        assert receipt['panel_manifest_sha256'] == config['panel_manifest_sha256']
        assert receipt['config_sha256'] == hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
        with np.load(path, allow_pickle=False) as archive:
            assert archive['ids'].tolist() == ids
            features = archive['features'].astype(np.float64)
        assert features.shape == (320, width) and np.isfinite(features).all()
        assert (np.linalg.norm(features, axis=1) > 0).all()
        if method == 'tnf':
            for i, ident in enumerate(ids):
                seq = sequences[ident]
                counts = dict.fromkeys(canonical_kmers, 0)
                for start in range(len(seq)-3):
                    kmer = seq[start:start+4]
                    if set(kmer) <= set('ACGT'):
                        counts[min(kmer, kmer.translate(TRANSLATE)[::-1])] += 1
                total = sum(counts.values())
                assert total == receipt['detail']['valid_fourmers'][i]
                expected = np.array([counts[k]/total for k in canonical_kmers], dtype=np.float32)
                np.testing.assert_array_equal(features[i], expected)
        else:
            detail = receipt['detail']
            assert detail['frozen'] and detail['model_revision'] == pin['revision']
            assert detail['model_files'] == pin['files']
            assert detail['torch_intraop'] == 4 and detail['torch_interop'] == 1 and detail['loader_workers'] == 0
            assert all(p['num_threads'] <= 4 for p in detail['library_pools'])
            assert [r['id'] for r in detail['chunk_records']] == ids
            for row, chunks in zip(rows, detail['chunk_records']):
                intervals = chunks['intervals']
                assert chunks['bp'] == row['bp'] and chunks['chunks'] == len(intervals)
                assert intervals[0][0] == 0 and intervals[-1][1] == row['bp']
                assert all(a[1] == b[0] for a, b in zip(intervals, intervals[1:]))
                assert all(0 < b-a <= 4000 for a, b in intervals)
                assert len(chunks['tokens']) == 2*len(intervals) and max(chunks['tokens']) <= 1024
            assert sum(r['unknown_tokens'] for r in detail['chunk_records']) == detail['unknown_tokens'] == 6
        partition = load(RUN/f'{method}.partition.json')
        assert partition['ids'] == ids and all(partition['valid'])
        assert partition['clustering'] == dict(k=5, mutual=True, positive_weights=True,
                                              resolution=1.0, min_size=3,
                                              expected_cluster_count=None)
        mean, std = features.mean(0), features.std(0)
        np.testing.assert_allclose(partition['transform']['mean'], mean, rtol=0, atol=1e-12)
        np.testing.assert_allclose(partition['transform']['std'], std, rtol=0, atol=1e-12)
        usable = std > 1e-8
        assert partition['transform']['usable'] == usable.tolist()
        z = (features[:, usable]-mean[usable])/std[usable]
        z /= np.linalg.norm(z, axis=1, keepdims=True)
        similarity = np.clip(z@z.T, -1, 1)
        neighbor_indices = [sorted((j for j in range(320) if j != i),
                            key=lambda j: (-similarity[i, j], ids[j]))[:5] for i in range(320)]
        assert partition['neighbors'] == [[ids[j] for j in nn] for nn in neighbor_indices]
        edges = sum(i < j and i in neighbor_indices[j] and similarity[i, j] > 0
                    for i, nn in enumerate(neighbor_indices) for j in nn)
        assert edges == partition['edges']
        labels = np.array(partition['assignment'])
        groups = {label: np.flatnonzero(labels == label) for label in set(labels) if label >= 0}
        assert len(groups) == partition['clusters'] and sum(labels < 0) == partition['unassigned']
        assert all(len(group) >= 3 for group in groups.values())
        values = []
        for i in range(320):
            nn_purity = sum(truth[j] == truth[i] for j in neighbor_indices[i])/5
            if labels[i] < 0:
                precision = recall = 0
            else:
                group = groups[labels[i]]
                same = sum(truth[group] == truth[i])
                precision, recall = same/len(group), same/sum(truth == truth[i])
            values.append((nn_purity, precision, recall, labels[i] >= 0))
            reported = retained_scores['scores'][method]['per_fragment'][i]
            assert (reported['id'], reported['genome'], reported['bp']) == (ids[i], truth[i], int(lengths[i]))
            np.testing.assert_allclose([reported[k] for k in ('neighbor_purity', 'b3_precision', 'b3_recall', 'assigned')], values[-1], rtol=0, atol=1e-12)
        values = np.array(values)
        subsets = {'all': np.arange(320), 'base_weighted': np.arange(320),
                   'short': np.flatnonzero(lengths < 2500), 'long': np.flatnonzero(lengths >= 2500)}
        subsets.update({str(n): np.flatnonzero(lengths == n) for n in sorted(set(lengths))})
        summaries[method] = {}
        for subset, indices in subsets.items():
            metrics = aggregate(values, lengths, indices, subset == 'base_weighted')
            reported = retained_scores['scores'][method]
            reported = reported['by_length'][subset] if subset.isdigit() else reported[subset]
            for key, value in metrics.items():
                assert abs(value-reported[key]) < 1e-12
            summaries[method][subset] = metrics
        details[method] = dict(shape=list(features.shape), finite_nonzero_rows=320,
                               clusters=len(groups), unassigned=int(sum(labels < 0)), edges=int(edges),
                               cluster_sizes=sorted(map(len, groups.values())))
    operational = {}
    for label, name, ceiling in (('workflow', 'supervisor.json', 7200), ('glm', 'glm-monitor/supervisor.json', 3600)):
        record = load(RUN/name)
        assert record['exit_code'] == 0 and record['stop_reason'] is None
        assert record['wall_seconds'] < ceiling and record['peak_sampled_rss_bytes'] < 8000000000
        operational[label] = record
    gains = dict(short_neighbor_gain=summaries['glm']['short']['neighbor_purity']-summaries['tnf']['short']['neighbor_purity'],
                 long_neighbor_delta=summaries['glm']['long']['neighbor_purity']-summaries['tnf']['long']['neighbor_purity'],
                 base_weighted_b3_gain=summaries['glm']['base_weighted']['b3_f1']-summaries['tnf']['base_weighted']['b3_f1'])
    passed = {key: value+1e-12 >= config['decision'][key+'_min'] for key, value in gains.items()}
    assert passed == retained_scores['decision']['criteria_passed']
    assert all(passed.values()) == retained_scores['decision']['include_frozen_glm']
    assert 'Nothing to be done' in (RUN.parent/'acquisition/resume-dryrun.log').read_text()
    files = [{ 'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': sha(p)}
             for p in sorted(RUN.parent.rglob('*')) if p.is_file()]
    inventory = dict(owner='local project checkout; not a remote backup', files=files,
                     file_count=len(files), retained_bytes=sum(r['bytes'] for r in files))
    (HERE/'retained-files.json').write_text(json.dumps(inventory, indent=2)+'\n')
    observed = dict(record='E003', date='2026-10-03', attempt='run-001', execution='completed',
                    scientific_outcome='joint GLM inclusion criterion not met; grouping benefit retained',
                    source_commit=commit, source_implementation_unchanged=True,
                    config_sha256=sha(HERE/'config.json'), panel_manifest_sha256=sha(HERE/'panel.json'),
                    sources_manifest_sha256=sha(HERE/'sources.json'), model_pin_sha256=sha(ROOT/config['model_pin']),
                    hardware=load(ROOT/'experiments/E002-dnabert-s-feasibility/observed.json')['runtime']['hardware'],
                    runtime_reuse='accepted E002 environment and pinned model read-only; existing Snakemake 9.16.3 coordinator',
                    operational=operational, glm_extraction_seconds=load(RUN/'glm.features.json')['detail']['extraction_seconds'],
                    summaries=summaries, partition_checks=details,
                    decision=dict(include_frozen_glm=all(passed.values()), values=gains, criteria_passed=passed,
                                  first_prototype='136-dimensional composition input to our own compact contrastive encoder'),
                    review=dict(independent_tnf_counts=True, independent_cosine_neighbors=True,
                                independent_all_metrics=True, native_model_not_repeated=True,
                                no_new_partition_fit=True, source_sampling_hashes_axes_chunks_masks_checked=True,
                                completed_resume_schedules_nothing=True),
                    resource_limits='sampled process trees; 4-thread wall budget is not billing; acquisition/setup excluded',
                    benchmark_limit='local extended benchmark RAM/cpu_time fields are zero/unavailable; rely on independent supervisor samples',
                    retention=dict(locator='artifacts/e003-representation-screen/', file_count=len(files),
                                   bytes=inventory['retained_bytes'], inventory='retained-files.json',
                                   inventory_sha256=sha(HERE/'retained-files.json'), model_copy_added=False),
                    claims='development fragments only; no trained TNF comparison, whole-MAG, unseen-species or strain-resolution claim; pretraining overlap not excluded')
    (HERE/'observed.json').write_text(json.dumps(observed, indent=2)+'\n')
    with (HERE/'metrics.tsv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=['method', 'stratum', *next(iter(summaries['tnf'].values())).keys()], delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for method, subsets in summaries.items():
            for stratum, metrics in subsets.items():
                writer.writerow(dict(method=method, stratum=stratum, **metrics))
    print(json.dumps(dict(independent_review='passed', decision=observed['decision'],
                          retained_files=len(files), retained_bytes=inventory['retained_bytes'])))


if __name__ == '__main__':
    main()
