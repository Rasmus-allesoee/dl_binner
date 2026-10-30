#!/usr/bin/env python3
"""One native Oral MetaBAT2 cvExt reference and streaming complete-DNA accounting.

Means are supported external abundance inputs. Native cvExt assumes variance
equals mean; this is not BAM-derived variance or a matched-cutoff comparison.
No aligner, reference source label, tool campaign or quality selector is used.
"""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
from dl_binner.multiview.views import fasta_rows
from dl_binner.io import digest, write_json
from e024_coverage import binding


def export(fasta, native, output):
    """Verify native bin FASTAs, retain them once, and account for all original DNA.

    A compact original ID/length/SHA index avoids holding the 1.67 Gb assembly as
    Python sequence strings. Native files remain intact; unassigned DNA remains
    in the immutable complete input. Inventories are not full-DNA backups.
    """
    import re
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    original = {}
    for q, dna in fasta_rows(fasta):
        if q in original: raise ValueError('Duplicate original FASTA identifier')
        original[q] = len(dna), hashlib.sha256(dna.encode()).hexdigest()
    assigned = {}; bins = {}
    for p in sorted(Path(native).glob('bin.*.fa')):
        if not re.fullmatch(r'bin\.\d+\.fa', p.name): continue
        if p.is_symlink(): raise ValueError('Native bin link refused')
        label = 'bin_'+p.name.split('.')[1]
        for q, dna in fasta_rows(p):
            if q in assigned or original.get(q) != (len(dna), hashlib.sha256(dna.encode()).hexdigest()):
                raise ValueError('Native bin duplicated, unknown or changed DNA')
            if len(dna) < 1000: raise ValueError('Unexpected native short-contig assignment')
            assigned[q] = label
        bins[label] = dict(path=str(p.absolute()), **binding(p))
    totals = {k: dict(contigs=0, bp=0) for k in ['assigned', 'unassigned', 'excluded']}; strata = {}
    with (out/'assignments.tsv').open('x') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(['contig_id', 'length', 'bin_id', 'status', 'reason'])
        for q, (length, _) in original.items():
            label = assigned.get(q, '')
            status = 'assigned' if label else 'excluded' if length < 1000 else 'unassigned'
            reason = '' if label else 'native_below_small_contig_minimum' if length < 1000 else 'native_not_assigned'
            writer.writerow([q, length, label, status, reason])
            totals[status]['contigs'] += 1; totals[status]['bp'] += length
            low = max(n for n in [0, 500, 768, 1000, 1500, 2000, 2500, 10000] if length >= n)
            cell = strata.setdefault(str(low), {k: dict(contigs=0, bp=0) for k in totals})
            cell[status]['contigs'] += 1; cell[status]['bp'] += length
    result = dict(status='PASS', contigs=len(original), bp=sum(v[0] for v in original.values()),
        bins=len(bins), statuses=totals, length_strata=strata, native_bin_fastas=bins,
        source_fasta=binding(fasta), assignments=binding(out/'assignments.tsv'),
        seed_minimum_bp=2500, small_contig_minimum_bp=1000, min_bin_bp=200000,
        abundance='native cvExt measured means; variance=mean is a native assumption',
        unique_native_DNA_verified=True, full_DNA_accounted=True, native_bins_retained_once=True,
        unassigned_DNA_locator=str(Path(fasta).absolute()), inventory_is_not_DNA_backup=True)
    write_json(out/'manifest.json', result); return result


def validate_means(matrix, receipt, fasta):
    """Verify exact supported cvExt table axes/reference and finite measured cells."""
    import math
    r = json.loads(Path(receipt).read_text())
    if (r['status'] != 'PASS' or r['matrix'] != binding(matrix) or r['reference'] != binding(fasta)
            or r['missing_cells'] != 0 or not r['all_cells_measured'] or len(r['samples']) != 10):
        raise ValueError('Complete original ten-sample matrix contract differs')
    count = 0
    with Path(matrix).open() as f:
        if f.readline().rstrip('\n').split('\t') != ['contig_id']+r['samples']:
            raise ValueError('Ordered ten-sample columns differ')
        for q, _ in fasta_rows(fasta):
            row = f.readline().rstrip('\n').split('\t'); count += 1
            if len(row) != 11 or row[0] != q or any(not math.isfinite(float(x)) or float(x) < 0 for x in row[1:]):
                raise ValueError('Missing/reordered/nonfinite native abundance row')
        if f.read(1) or count != r['rows']: raise ValueError('Extra/missing native abundance row')
    return dict(status='PASS', samples=r['samples'], rows=count, mean_only=True)
