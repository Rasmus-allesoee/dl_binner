"""Strict input readers and byte-bound, ordered artifact contracts for the binner."""
import csv
import hashlib
import itertools
import json
from pathlib import Path
import time

import numpy as np

DNA = frozenset('ACGTRYSWKMBDHVN')
COMPLEMENT = str.maketrans('ACGT', 'TGCA')
KMERS = sorted({min(k, k.translate(COMPLEMENT)[::-1])
                for k in map(''.join, itertools.product('ACGT', repeat=4))})
LOOKUP = {k: i for i, k in enumerate(KMERS)}


def digest(path):
    """Return the SHA256 of file bytes without loading the whole file."""
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            value.update(chunk)
    return value.hexdigest()


def id_digest(ids):
    """Bind an ordered string-ID axis, independent of array storage format."""
    return hashlib.sha256(json.dumps(list(ids), separators=(',', ':')).encode()).hexdigest()


def write_json(path, value):
    """Write a new small record exclusively; never overwrite an accepted output."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')


def emit(stage, **values):
    """Print timestamped stage progress to the caller's terminal/captured log."""
    print(json.dumps(dict(stage=stage, utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                          **values)), flush=True)


def read_fasta(path):
    """Return unique IDs and uppercase IUPAC sequences in FASTA order.

    Header descriptions are ignored, but whitespace-free first tokens identify
    contigs. Empty records, duplicates and invalid DNA fail before any training.
    """
    rows, ident, chunks = [], None, []
    seen = set()

    def finish():
        if ident is None:
            return
        sequence = ''.join(chunks).upper()
        if not sequence or set(sequence)-DNA:
            raise ValueError(f'Empty/invalid IUPAC sequence: {ident}')
        rows.append((ident, sequence))

    with Path(path).open() as stream:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            if line.startswith('>'):
                finish()
                fields = line[1:].split()
                if not fields or fields[0] in seen:
                    raise ValueError('Missing or duplicate FASTA ID')
                ident, chunks = fields[0], []
                if any(ord(c) < 32 for c in ident):
                    raise ValueError('Control character in FASTA ID')
                seen.add(ident)
            else:
                if ident is None:
                    raise ValueError('Sequence before FASTA header')
                chunks.append(line)
    finish()
    if not rows:
        raise ValueError('Empty FASTA')
    return rows


def read_depth(path, ids):
    """Read explicit mean depths; align arbitrary row order to FASTA, keep columns.

    Require all and only assembly IDs, unique sample names, finite nonnegative
    values. Return an empty-column matrix when coverage is explicitly absent.
    """
    if path is None:
        return [], np.empty((len(ids), 0), dtype=np.float64)
    with Path(path).open() as stream:
        reader = csv.reader(stream, delimiter='\t')
        header = next(reader, [])
        if (len(header) < 2 or header[0] != 'contig_id' or
                len(set(header[1:])) != len(header)-1 or any(not s.strip() for s in header[1:])):
            raise ValueError('Depth header requires contig_id and unique sample names')
        values = {}
        for fields in reader:
            if len(fields) != len(header) or not fields[0] or fields[0] in values:
                raise ValueError('Invalid/duplicate depth row')
            array = np.array([float(v) for v in fields[1:]], dtype=np.float64)
            if not np.isfinite(array).all() or (array < 0).any():
                raise ValueError('Depth must be finite and nonnegative')
            values[fields[0]] = array
    if set(values) != set(ids):
        raise ValueError('Missing/extra depth IDs relative to assembly')
    return header[1:], np.array([values[i] for i in ids], dtype=np.float64)


def tnf(rows):
    """Extract own 136-dimensional strand-collapsed fourmer frequencies.

    Skip ambiguity-containing fourmers and preserve rows with zero usable counts.
    This reader is used on fresh inputs; accepted feature caches bypass extraction.
    """
    features = np.zeros((len(rows), 136), dtype=np.float32)
    counts = np.zeros(len(rows), dtype=np.int64)
    for index, (_, dna) in enumerate(rows):
        bins = np.zeros(136, dtype=np.int64)
        for start in range(max(0, len(dna)-3)):
            k = dna[start:start+4]
            if set(k) <= set('ACGT'):
                bins[LOOKUP[min(k, k.translate(COMPLEMENT)[::-1])]] += 1
        counts[index] = bins.sum()
        features[index] = bins/max(int(counts[index]), 1)
    return features, counts


def import_tnf(cache, receipt_path, panel_path, fasta_path, rows):
    """Validate the accepted E003 cache's complete DNA/ID/byte contract, then reuse.

    Consume only ID, length and DNA hashes from the panel; genome labels never
    enter the feature matrix. Require the original ordered full assembly axis.
    """
    receipt = json.loads(Path(receipt_path).read_text())
    panel = json.loads(Path(panel_path).read_text())
    if digest(cache) != receipt['sha256'] or digest(panel_path) != receipt['panel_manifest_sha256']:
        raise ValueError('Stale TNF cache/panel hash')
    if digest(fasta_path) != panel['fna_sha256']:
        raise ValueError('Cached DNA file hash mismatch')
    ids = [i for i, _ in rows]
    if ids != [r['id'] for r in panel['rows']]:
        raise ValueError('Cached panel ordered-ID mismatch')
    for (_, dna), r in zip(rows, panel['rows']):
        if len(dna) != r['bp'] or hashlib.sha256(dna.encode()).hexdigest() != r['sequence_sha256']:
            raise ValueError('Cached per-contig DNA mismatch')
    with np.load(cache, allow_pickle=False) as archive:
        if archive['ids'].tolist() != ids:
            raise ValueError('Cached array ordered-ID mismatch')
        values = archive['features'].copy()
    counts = np.array(receipt['detail']['valid_fourmers'], dtype=np.int64)
    if (values.shape != (len(rows), 136) or counts.shape != (len(rows),) or
            not np.isfinite(values).all() or (values < 0).any() or (counts < 0).any()):
        raise ValueError('Invalid cached TNF shape/values/counts')
    expected = (counts > 0).astype(float)
    if not np.allclose(values.sum(1), expected, atol=1e-6):
        raise ValueError('Invalid TNF evidence mask/frequency sum')
    return values.astype(np.float32), counts


def save_arrays(path, arrays, metadata):
    """Write an exclusive NPZ and sidecar binding bytes, ordered IDs and parents."""
    path = Path(path)
    sidecar = path.with_suffix('.json')
    if path.exists() or sidecar.exists():
        raise FileExistsError(f'Fresh artifact path required: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        np.savez_compressed(stream, **arrays)
    write_json(sidecar, dict(metadata, version=1, sha256=digest(path),
                             ids_sha256=id_digest(arrays['ids'].tolist())))


def load_arrays(path, kind):
    """Reject stale bytes/IDs and unsafe object arrays before returning artifacts."""
    path = Path(path)
    metadata = json.loads(path.with_suffix('.json').read_text())
    if metadata.get('version') != 1 or metadata.get('kind') != kind or digest(path) != metadata['sha256']:
        raise ValueError('Artifact kind/version/byte hash mismatch')
    with np.load(path, allow_pickle=False) as archive:
        arrays = {k: archive[k].copy() for k in archive.files}
    ids = arrays['ids'].tolist()
    if len(set(ids)) != len(ids) or id_digest(ids) != metadata['ids_sha256']:
        raise ValueError('Artifact ordered-ID mismatch')
    return arrays, metadata


def prepare(fasta_path, output, depth=None, min_length=500, cache=None, receipt=None, panel=None):
    """Publish complete raw features, masks and exclusions, from fresh DNA or cache."""
    if Path(output).exists() or Path(output).with_suffix('.json').exists():
        raise FileExistsError('Fresh feature paths required')
    if min_length < 4:
        raise ValueError('Minimum eligible length must be at least four bases')
    rows = read_fasta(fasta_path)
    ids = [i for i, _ in rows]
    samples, coverage = read_depth(depth, ids)
    if cache is not None:
        if receipt is None or panel is None:
            raise ValueError('Cached TNF requires its receipt and frozen DNA panel')
        values, counts = import_tnf(cache, receipt, panel, fasta_path, rows)
    else:
        if receipt is not None or panel is not None:
            raise ValueError('Receipt/panel require a TNF cache')
        values, counts = tnf(rows)
    lengths = np.array([len(dna) for _, dna in rows], dtype=np.int64)
    reasons = np.where(lengths < min_length, 'below_min_length',
                       np.where(counts == 0, 'no_valid_fourmers', ''))
    eligible = reasons == ''
    arrays = dict(ids=np.array(ids), tnf=values, valid_fourmers=counts, lengths=lengths,
                  depth=coverage, zero_depth=coverage == 0, depth_evidence=(coverage > 0).any(1),
                  eligible=eligible, exclusion_reason=reasons,
                  sequence_sha256=np.array([hashlib.sha256(dna.encode()).hexdigest() for _, dna in rows]))
    save_arrays(output, arrays, dict(kind='features', fasta_sha256=digest(fasta_path),
                                    depth_sha256=digest(depth) if depth else None,
                                    samples=samples, min_length=min_length, sequence_dimensions=136,
                                    cached_tnf_sha256=digest(cache) if cache else None,
                                    cached_panel_sha256=digest(panel) if panel else None,
                                    mode='measured_depth' if depth else 'sequence_only'))
    emit('features_ready', contigs=len(ids), eligible=int(eligible.sum()),
         excluded=int((~eligible).sum()), samples=len(samples), reused_tnf=cache is not None)


def validate_features(data, meta):
    """Verify native feature axes, evidence masks and lengths before consumption."""
    n = len(data['ids'])
    if (data['tnf'].shape != (n, 136) or data['depth'].shape != (n, len(meta['samples'])) or
            not np.isfinite(data['tnf']).all() or not np.isfinite(data['depth']).all() or
            (data['tnf'] < 0).any() or (data['depth'] < 0).any()):
        raise ValueError('Invalid feature/depth axes or values')
    for key in ('lengths', 'eligible', 'valid_fourmers', 'exclusion_reason', 'sequence_sha256', 'depth_evidence'):
        if data[key].shape != (n,):
            raise ValueError('Invalid row metadata axis')
    if (data['lengths'].dtype.kind not in 'iu' or (data['lengths'] < 1).any() or
            data['valid_fourmers'].dtype.kind not in 'iu' or (data['valid_fourmers'] < 0).any() or
            (data['valid_fourmers'] > np.maximum(0, data['lengths']-3)).any() or
            not np.allclose(data['tnf'].sum(1), (data['valid_fourmers'] > 0).astype(float), atol=1e-6)):
        raise ValueError('Invalid length/fourmer evidence/frequency contract')
    if not np.array_equal(data['zero_depth'], data['depth'] == 0) or not np.array_equal(data['depth_evidence'], (data['depth'] > 0).any(1)):
        raise ValueError('Invalid original depth masks')
    reasons = np.where(data['lengths'] < meta['min_length'], 'below_min_length',
                       np.where(data['valid_fourmers'] == 0, 'no_valid_fourmers', ''))
    if not np.array_equal(data['exclusion_reason'], reasons) or not np.array_equal(data['eligible'], reasons == ''):
        raise ValueError('Invalid eligibility/exclusion mask')
