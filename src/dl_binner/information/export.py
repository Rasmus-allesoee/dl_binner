"""Stream full-DNA exports and compact alternatives without a whole FASTA copy."""
from collections import OrderedDict
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from ..io import digest, emit, write_json
from ..multiview.views import fasta_rows, load
from .grouping import require


def validate_partition(data, path, features):
    """Refuse malformed labels, masks, reasons or lost opaque-ID axes."""
    value = json.loads(Path(path).read_text())
    ids = data['ids'].tolist()
    labels = np.asarray(value['assignment'])
    valid = np.asarray(value['valid'])
    require(value['ids'] == ids and value['parent_features_sha256'] == digest(features)
            and labels.shape == valid.shape == (len(ids),) and valid.dtype == bool
            and labels.dtype.kind in 'iu' and np.all(labels >= -1)
            and len(value['reason']) == len(ids) and all(isinstance(r, str) for r in value['reason'])
            and not np.any((labels >= 0) & (~valid | ~data['eligible']))
            and sorted(set(int(v) for v in labels if v >= 0)) == list(range(value['clusters']))
            and value['unassigned'] == int((labels < 0).sum()), 'Incomplete/malformed partition DNA accounting')
    return value


def export(features, partition, fasta, output, include_dna=True):
    """Write every row once, optionally streaming its DNA through <=32 open bins.

    Compact core/pre/old alternatives retain full assignments and denominators;
    final selected output additionally writes all assigned, unassigned and
    excluded DNA. Nothing is deleted. Output must be fresh and exclusive.
    """
    data, meta = load(features)
    value = validate_partition(data, partition, features)
    require(digest(fasta) == meta['fasta_sha256'], 'FASTA source bytes differ')
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    handles = OrderedDict()
    totals = {k: dict(contigs=0, bp=0) for k in ['assigned', 'unassigned', 'excluded']}
    seen = 0
    try:
        with (out/'assignments.tsv').open('x') as stream:
            writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
            writer.writerow(['contig_id', 'length', 'bin_id', 'status', 'reason'])
            for i, (q, dna) in enumerate(fasta_rows(fasta)):
                require(i < len(data['ids']) and q == data['ids'][i] and len(dna) == data['lengths'][i]
                        and hashlib.sha256(dna.encode()).hexdigest() == data['sequence_sha256'][i],
                        'FASTA opaque index/length/sequence checksum differs')
                label = value['assignment'][i]
                status = 'excluded' if not data['eligible'][i] else 'unassigned' if label < 0 else 'assigned'
                bucket = f'bin_{label+1:06d}' if status == 'assigned' else status
                reason = str(data['exclusion_reason'][i]) if status == 'excluded' else value['reason'][i] if label < 0 else ''
                writer.writerow([q, len(dna), bucket if label >= 0 else '', status, reason])
                totals[status]['contigs'] += 1
                totals[status]['bp'] += len(dna)
                seen += 1
                if include_dna:
                    if bucket in handles:
                        handle = handles.pop(bucket)
                    else:
                        if len(handles) >= 32:
                            handles.popitem(last=False)[1].close()
                        handle = (out/(bucket+'.fna')).open('a')
                    handles[bucket] = handle
                    handle.write('>'+q+'\n'+dna+'\n')
                if seen % 10000 == 0:
                    emit('information_export_progress', contigs=seen, include_dna=include_dna)
    finally:
        for handle in handles.values():
            handle.close()
    require(seen == len(data['ids']) and digest(fasta) == meta['fasta_sha256'], 'FASTA missing rows/changed during export')
    files = {str(p.relative_to(out)): dict(bytes=p.stat().st_size, sha256=digest(p)) for p in sorted(out.iterdir())}
    record = dict(status='SUCCESS', contigs=seen, bp=int(data['lengths'].sum()), populations=totals,
                  features_sha256=digest(features), partition_sha256=digest(partition),
                  fasta_sha256=meta['fasta_sha256'], includes_full_DNA=include_dna, files=files)
    write_json(out/'manifest.json', record)
    emit('information_export_complete', contigs=seen, bp=record['bp'], include_dna=include_dna)
    return record
