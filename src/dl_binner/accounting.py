"""Byte-bound, label-free bin accounting; no genome-quality or truth estimates."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from .io import load_arrays, read_fasta, validate_features
from .contracts import check_files, digest, file_record

BOUNDS = [1, 500, 768, 1000, 2500, 10000]


def summarize_arm(features_path, export_dir):
    """Verify native features, assignment table and complete exported DNA, then count.

Consumes retained outputs only. Retains every stratum, exclusion, original zero
and noise reason. Assigned sequence is not completeness/recovery or MAG quality.
Return both accounting and the hashes of every consumed source file.
"""
    features_path, export_dir = Path(features_path), Path(export_dir)
    data, meta = load_arrays(features_path, 'features')
    validate_features(data, meta)
    manifest_path = export_dir/'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    if (manifest['features_sha256'] != digest(features_path) or
            manifest['fasta_sha256'] != meta['fasta_sha256']):
        raise ValueError('Export/features/reference hash mismatch')
    check_files(export_dir, manifest['files'])
    actual = {p.name for p in export_dir.iterdir()}
    if actual != set(manifest['files']) | {'manifest.json', '.snakemake_timestamp'} and actual != set(manifest['files']) | {'manifest.json'}:
        raise ValueError('Unexpected or missing exported files')
    with (export_dir/'assignments.tsv').open() as stream:
        records = list(csv.DictReader(stream, delimiter='\t'))
    ids = data['ids'].tolist()
    if [r['contig_id'] for r in records] != ids:
        raise ValueError('Assignment ordered-ID axis mismatch')
    exported, buckets = {}, {}
    for name in manifest['files']:
        if not name.endswith('.fna'):
            continue
        for ident, dna in read_fasta(export_dir/name) if (export_dir/name).stat().st_size else []:
            if ident in exported:
                raise ValueError('Duplicate exported ID')
            exported[ident], buckets[ident] = dna, Path(name).stem
    if set(exported) != set(ids):
        raise ValueError('Export is not a complete contig partition')
    bins = {}
    totals = {s: dict(contigs=0, bp=0) for s in ('assigned', 'unassigned', 'excluded')}
    reasons = {s: Counter() for s in totals}
    strata = [dict(lower_bp=low, upper_bp=BOUNDS[i+1] if i+1 < len(BOUNDS) else None,
                   contigs=0, bp=0, statuses={s: dict(contigs=0, bp=0) for s in totals}, reasons={})
              for i, low in enumerate(BOUNDS)]
    for i, r in enumerate(records):
        ident, bp, status = r['contig_id'], int(r['length']), r['status']
        dna = exported[ident]
        if bp != int(data['lengths'][i]) or len(dna) != bp or hashlib.sha256(dna.encode()).hexdigest() != data['sequence_sha256'][i]:
            raise ValueError('Exported DNA/length hash mismatch')
        if status not in totals:
            raise ValueError('Unknown assignment status')
        expected = 'excluded' if not data['eligible'][i] else 'assigned' if r['bin_id'] else 'unassigned'
        bucket = r['bin_id'] if status == 'assigned' else status
        if status != expected or buckets[ident] != bucket or (status == 'assigned' and r['reason']):
            raise ValueError('Assignment status/bin/mask mismatch')
        if status == 'excluded' and r['reason'] != data['exclusion_reason'][i]:
            raise ValueError('Exclusion reason mismatch')
        if status != 'assigned' and not r['reason']:
            raise ValueError('Missing exclusion/noise reason')
        totals[status]['contigs'] += 1
        totals[status]['bp'] += bp
        if r['reason']:
            reasons[status][r['reason']] += 1
        if status == 'assigned':
            value = bins.setdefault(r['bin_id'], dict(contigs=0, bp=0))
            value['contigs'] += 1; value['bp'] += bp
        at = max(j for j, low in enumerate(BOUNDS) if bp >= low)
        s = strata[at]
        s['contigs'] += 1; s['bp'] += bp
        s['statuses'][status]['contigs'] += 1; s['statuses'][status]['bp'] += bp
        if r['reason']:
            s['reasons'][r['reason']] = s['reasons'].get(r['reason'], 0)+1
    for status in totals:
        if totals[status]['contigs'] != manifest[status]:
            raise ValueError('Export manifest status count mismatch')
    if len(bins) != manifest['bins'] or manifest['contigs'] != len(ids) or manifest['bp'] != int(data['lengths'].sum()):
        raise ValueError('Export manifest bin/total count mismatch')
    samples = meta['samples']
    value = dict(contigs=len(ids), bp=int(data['lengths'].sum()), mode=meta['mode'], samples=samples,
                 statuses=totals, reasons={s: dict(c) for s, c in reasons.items()}, bin_count=len(bins),
                 bins=bins, bin_size_bp=dict(min=min((b['bp'] for b in bins.values()), default=None),
                     median=float(np.median([b['bp'] for b in bins.values()])) if bins else None,
                     max=max((b['bp'] for b in bins.values()), default=None)), length_strata=strata,
                 masks=dict(eligible_contigs=int(data['eligible'].sum()),
                     no_valid_fourmers=int((data['valid_fourmers'] == 0).sum()),
                     zero_depth_by_sample={s: int(data['zero_depth'][:, j].sum()) for j, s in enumerate(samples)},
                     all_zero_depth_contigs=int((~data['depth_evidence']).sum()) if samples else None,
                     depth_observations_present=bool(samples)))
    sources = {str(features_path): file_record(features_path),
               str(features_path.with_suffix('.json')): file_record(features_path.with_suffix('.json')),
               str(manifest_path): file_record(manifest_path)}
    sources.update({str(export_dir/name): entry for name, entry in manifest['files'].items()})
    return value, sources


def write_summary_tsv(path, arms):
    """Write concise count/bp rows for totals and all six strata, including zeros."""
    with Path(path).open('x') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(['arm', 'length_range_bp', 'status', 'contigs', 'bp'])
        for arm, value in arms.items():
            for status, counts in value['statuses'].items():
                writer.writerow([arm, 'all', status, counts['contigs'], counts['bp']])
            for s in value['length_strata']:
                label = f'{s["lower_bp"]}-{s["upper_bp"]-1}' if s['upper_bp'] else f'{s["lower_bp"]}+'
                for status, counts in s['statuses'].items():
                    writer.writerow([arm, label, status, counts['contigs'], counts['bp']])
