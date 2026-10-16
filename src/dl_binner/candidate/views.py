"""Real DNA-window feature preparation; no truth, BAMs or synthetic coverage.

Every parent and ordered depth column is retained. Training windows use explicit
zero-based half-open parent coordinates; depth is the parent's observed mean,
never a claim to measured window coverage. Short DNA enters inference/export.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from ..io import (KMERS, digest, emit, read_depth, read_fasta, save_arrays,
                  load_arrays, validate_features)


def config(path=None):
    """Load the strict candidate schema; reject invalid settings before work starts."""
    default = Path(__file__).parents[1]/'resources/candidate.json'
    expected = json.loads(default.read_text())
    value = json.loads(Path(path or default).read_text())
    if set(value) != set(expected):
        raise ValueError('Candidate configuration keys mismatch')
    for key, initial in expected.items():
        v = value[key]
        if type(initial) is int:
            if type(v) is not int or v < (0 if key == 'seed' else 1):
                raise ValueError('Invalid integer configuration: '+key)
        elif type(v) not in (float, int) or not np.isfinite(v) or v < 0:
            raise ValueError('Invalid numeric configuration: '+key)
    if (value['batch_size'] < 2 or value['window_pairs'] != 2 or value['window_min'] < 4
            or value['window_max'] < value['window_min'] or value['min_length'] < 4
            or value['neighbors'] < 5 or value['exact_threshold'] < 2
            or not 0 < value['min_neighbor_recall'] <= 1
            or not 0 < value['temperature'] or not 0 < value['learning_rate']
            or not 0 < value['resolution'] or not 0 <= value['refinement_min_cosine'] <= 1
            or not 0 <= value['refinement_margin'] <= 2):
        raise ValueError('Invalid candidate view/training/grouping policy')
    return value


# A byte lookup implements exactly the historical 136 reverse-complement classes.
BASES = np.full(256, -100, dtype=np.int16)
for _i, _base in enumerate(b'ACGT'):
    BASES[_base] = _i
CLASSES = np.empty(256, dtype=np.int16)
for _code in range(256):
    _word = ''.join('ACGT'[(_code >> s) & 3] for s in (6, 4, 2, 0))
    _reverse = _word.translate(str.maketrans('ACGT', 'TGCA'))[::-1]
    CLASSES[_code] = KMERS.index(min(_word, _reverse))


def composition(dna):
    """Compute native vectorized TNF, skipping every IUPAC-containing fourmer."""
    b = BASES[np.frombuffer(dna.encode('ascii'), dtype=np.uint8)]
    if len(b) < 4:
        return np.zeros(136, np.float32), 0
    good = (b[:-3] >= 0) & (b[1:-2] >= 0) & (b[2:-1] >= 0) & (b[3:] >= 0)
    code = b[:-3]*64+b[1:-2]*16+b[2:-1]*4+b[3:]
    counts = np.bincount(CLASSES[code[good]], minlength=136)
    n = int(counts.sum())
    return (counts/max(n, 1)).astype(np.float32), n


def windows(ident, dna, cfg):
    """Draw two deterministic disjoint pairs, independently in the two parent halves."""
    if len(dna) < 2*cfg['window_min']:
        return []
    seed = int.from_bytes(hashlib.sha256((str(cfg['seed'])+'\0'+ident).encode()).digest()[:8], 'little')
    rng = np.random.default_rng(seed)
    half = len(dna)//2
    result = []
    for _ in range(cfg['window_pairs']):
        for left, right in ((0, half), (half, len(dna))):
            length = min(right-left, cfg['window_max'])
            start = int(rng.integers(left, right-length+1))
            end = start+length
            result.append((start, end, dna[start:end]))
    return result


def prepare(fasta, depth, output, cfg):
    """Create full parent features and four real-window features per trainable parent.

    The fresh output directory belongs to the caller. All DNA IDs survive; no
    source genome, taxonomy or truth file is accepted by this API.
    """
    out = Path(output)
    rows = read_fasta(fasta)
    ids = [i for i, _ in rows]
    samples, coverage = read_depth(depth, ids)
    n = len(rows)
    tnf = np.zeros((n, 136), np.float32)
    counts = np.zeros(n, np.int64)
    views = np.zeros((n, 4, 136), np.float32)
    view_counts = np.zeros((n, 4), np.int64)
    coords = np.full((n, 4, 2), -1, np.int64)
    hashes = np.full((n, 4), '', dtype='<U64')
    for i, (ident, dna) in enumerate(rows):
        tnf[i], counts[i] = composition(dna)
        for j, (start, end, sequence) in enumerate(windows(ident, dna, cfg)):
            views[i, j], view_counts[i, j] = composition(sequence)
            coords[i, j] = [start, end]
            hashes[i, j] = hashlib.sha256(sequence.encode()).hexdigest()
        if i % 2000 == 0:
            emit('candidate_features', completed_contigs=i, total_contigs=n)
    lengths = np.array([len(dna) for _, dna in rows], np.int64)
    reasons = np.where(lengths < cfg['min_length'], 'below_min_length',
                       np.where(counts == 0, 'no_valid_fourmers', ''))
    arrays = dict(ids=np.array(ids), tnf=tnf, valid_fourmers=counts, lengths=lengths,
        depth=coverage, zero_depth=coverage == 0, depth_evidence=(coverage > 0).any(1),
        eligible=reasons == '', exclusion_reason=reasons,
        sequence_sha256=np.array([hashlib.sha256(dna.encode()).hexdigest() for _, dna in rows]))
    meta = dict(kind='features', fasta_sha256=digest(fasta),
        depth_sha256=digest(depth) if depth else None, samples=samples,
        min_length=cfg['min_length'], sequence_dimensions=136, mode='candidate_measured_parent_depth',
        depth_semantics='Measured full-parent means; repeated conditioning for windows, not measured window depth. No variance available.')
    save_arrays(out/'features.npz', arrays, meta)
    trainable = arrays['eligible'] & (view_counts > 0).all(1)
    save_arrays(out/'views.npz', dict(ids=np.array(ids), tnf=views, valid_fourmers=view_counts,
        coordinates=coords, sequence_sha256=hashes, trainable=trainable),
        dict(kind='candidate_views', parent_features_sha256=digest(out/'features.npz'),
             fasta_sha256=digest(fasta), policy=cfg, coordinates='zero-based half-open',
             depth_semantics=meta['depth_semantics'], training_parents=int(trainable.sum())))
    emit('candidate_views_complete', parents=n, training_parents=int(trainable.sum()), samples=samples)


def load(features, views=None):
    """Verify complete parent/window axes, coordinate and frequency/mask contracts."""
    data, meta = load_arrays(features, 'features')
    validate_features(data, meta)
    if views is None:
        return data, meta
    v, vm = load_arrays(views, 'candidate_views')
    n = len(data['ids'])
    if (vm['parent_features_sha256'] != digest(features) or not np.array_equal(v['ids'], data['ids'])
            or v['tnf'].shape != (n, 4, 136) or v['coordinates'].shape != (n, 4, 2)
            or v['valid_fourmers'].shape != (n, 4) or v['sequence_sha256'].shape != (n, 4)
            or v['coordinates'].dtype.kind not in 'iu' or v['valid_fourmers'].dtype.kind not in 'iu'
            or v['trainable'].shape != (n,) or v['trainable'].dtype != bool
            or not np.isfinite(v['tnf']).all() or (v['tnf'] < 0).any()
            or (v['valid_fourmers'] < 0).any()
            or not np.allclose(v['tnf'].sum(2), v['valid_fourmers'] > 0, atol=1e-6)):
        raise ValueError('Invalid real-window axes/values/parent binding')
    cfg = vm['policy']
    present = data['lengths'] >= 2*cfg['window_min']
    for i in range(n):
        c = v['coordinates'][i]
        if not present[i]:
            if (c != -1).any() or (v['valid_fourmers'][i] != 0).any() or (v['sequence_sha256'][i] != '').any():
                raise ValueError('Short parent has fabricated windows')
            continue
        half = int(data['lengths'][i])//2
        for j, (start, end) in enumerate(c):
            lower, upper = (0, half) if j % 2 == 0 else (half, int(data['lengths'][i]))
            if not lower <= start < end <= upper or not cfg['window_min'] <= end-start <= cfg['window_max']:
                raise ValueError('Invalid/disjoint window coordinates')
            if v['valid_fourmers'][i, j] > end-start-3 or len(v['sequence_sha256'][i, j]) != 64:
                raise ValueError('Invalid window count/hash')
    if not np.array_equal(v['trainable'], data['eligible'] & (v['valid_fourmers'] > 0).all(1)):
        raise ValueError('Invalid window training mask')
    return data, meta, v, vm
