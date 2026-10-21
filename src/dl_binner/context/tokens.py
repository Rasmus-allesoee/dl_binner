"""Build bounded, strand-canonical DNA context from accepted parent/crop views.

Only one original contig is live during construction. Counts and coordinates are
indexed read-only NPY members, not an in-memory overlapping-window bank. Accepted
features/views are never rewritten; missing or corrupt banks have no fallback.
"""
import json
from pathlib import Path

import numpy as np

from ..candidate.views import BASES, CLASSES
from ..io import DNA, digest, emit, write_json
from ..multiview.views import fasta_rows, load

RC = str.maketrans('ACGTRYSWKMBDHVN', 'TGCAYRSWMKVHDBN')


def policy():
    """Return the packaged, prospective token/encoder defaults, never labels."""
    return json.loads((Path(__file__).parents[1] / 'resources/context.json').read_text())


def reverse_complement(dna):
    """Reverse-complement validated uppercase IUPAC sequence, including ambiguity."""
    return dna.translate(RC)[::-1]


def tokenize(dna, cfg=None):
    """Return eight bounded integer-count windows and canonical-view coordinates.

    The third result says whether coordinates refer to the reverse complement.
    Padded coordinates are -1; zero-count real windows remain explicit but masked.
    """
    cfg = cfg or policy()
    if not isinstance(dna, str) or not dna or set(dna)-DNA:
        raise ValueError('Context requires nonempty uppercase IUPAC DNA')
    other = reverse_complement(dna)
    flipped = other < dna
    canonical = other if flipped else dna
    length = len(dna)
    counts = np.zeros((cfg['tokens'], 136), np.uint16)
    coordinates = np.full((cfg['tokens'], 2), -1, np.int64)
    n = min(cfg['tokens'], max(1, length // cfg['token_min_interval']))
    for j in range(n):
        left, right = j * length // n, (j+1) * length // n
        width = min(cfg['token_max_bp'], right-left)
        start = left + (right-left-width)//2
        end = start+width
        coordinates[j] = start, end
        bases = BASES[np.frombuffer(canonical[start:end].encode('ascii'), np.uint8)]
        if len(bases) < 4:
            continue
        good = (bases[:-3] >= 0) & (bases[1:-2] >= 0) & (bases[2:-1] >= 0) & (bases[3:] >= 0)
        code = bases[:-3]*64 + bases[1:-2]*16 + bases[2:-1]*4 + bases[3:]
        value = np.bincount(CLASSES[code[good]], minlength=136)
        if value.max() > np.iinfo(np.uint16).max:
            raise ValueError('Context count overflow')
        counts[j] = value
    return counts, coordinates, bool(flipped)


def parent_coordinates(start, end, view_start, view_end, flipped):
    """Map canonical-view half-open coordinates to the original parent strand."""
    if not 0 <= start < end <= view_end-view_start:
        raise ValueError('Invalid context coordinate mapping')
    return (view_end-end, view_end-start) if flipped else (view_start+start, view_start+end)


def binding(path):
    """Hash a regular cache member without following scientific artifact symlinks."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Missing/nonregular context member: '+str(path))
    return dict(bytes=path.stat().st_size, sha256=digest(path))


def prepare(fasta, features, views, output):
    """Stream exact retained DNA views into a fresh bounded count bank.

    Original axes/hashes/eligibility/crop semantics are verified with their actual
    readers. The bank only stores eligible rows; the full parent axis is unchanged.
    """
    data, meta, v, vm = load(features, views)
    cfg = policy()
    if digest(fasta) != meta['fasta_sha256'] or vm['fasta_sha256'] != meta['fasta_sha256']:
        raise ValueError('Context FASTA/accepted features/views differ')
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    rows = np.flatnonzero(data['eligible']).astype(np.int64)
    if len(rows) < 2:
        raise ValueError('Context needs two eligible parents')
    np.save(out/'rows.npy', rows, allow_pickle=False)
    shape = (len(rows), 5, cfg['tokens'])
    counts = np.lib.format.open_memmap(out/'counts.npy', mode='w+', dtype=np.uint16, shape=shape+(136,))
    coords = np.lib.format.open_memmap(out/'coordinates.npy', mode='w+', dtype=np.int64, shape=shape+(2,))
    flips = np.lib.format.open_memmap(out/'flipped.npy', mode='w+', dtype=bool, shape=(len(rows), 5))
    coords[:] = -1
    eligible_row = 0
    seen = 0
    for i, (ident, dna) in enumerate(fasta_rows(fasta)):
        if i >= len(data['ids']) or ident != data['ids'][i]:
            raise ValueError('Context ordered FASTA ID differs')
        import hashlib
        if hashlib.sha256(dna.encode()).hexdigest() != data['sequence_sha256'][i]:
            raise ValueError('Context parent DNA changed')
        seen += 1
        if not data['eligible'][i]:
            continue
        for j in range(5):
            if j and not v['usable'][i, j-1]:
                continue
            a, b = (0, len(dna)) if j == 0 else v['coordinates'][i, j-1]
            sequence = dna[a:b]
            if j and hashlib.sha256(sequence.encode()).hexdigest().encode() != v['sequence_sha256'][i, j-1]:
                raise ValueError('Context retained crop DNA changed')
            c, xy, reverse = tokenize(sequence, cfg)
            counts[eligible_row, j] = c
            coords[eligible_row, j] = xy
            flips[eligible_row, j] = reverse
        eligible_row += 1
        if eligible_row % 2000 == 0:
            emit('context_tokens', eligible_done=eligible_row, eligible_total=len(rows))
    if seen != len(data['ids']) or eligible_row != len(rows) or digest(fasta) != meta['fasta_sha256']:
        raise ValueError('Context FASTA changed/truncated during construction')
    for array in (counts, coords, flips):
        array.flush()
    del counts, coords, flips
    manifest = dict(kind='context_tokens', version=1, policy=cfg,
        features_sha256=digest(features), views_sha256=digest(views), fasta_sha256=digest(fasta),
        parents=len(data['ids']), eligible=len(rows), samples=meta['samples'],
        members={p.name: binding(p) for p in sorted(out.glob('*.npy'))},
        coordinates='zero-based half-open in lexicographically canonical view; flipped maps to original parent',
        scope='At most eight bounded windows/view; complete parent TNF unchanged; no depth/labels in tokens')
    write_json(out/'tokens.json', manifest)
    return manifest


class Bank:
    """Verify and memory-map a complete immutable bank; fetch only selected batches."""

    def __init__(self, path, features, views, data, meta, v):
        self.root = Path(path)
        self.meta = json.loads((self.root/'tokens.json').read_text())
        m = self.meta
        names = {'rows.npy', 'counts.npy', 'coordinates.npy', 'flipped.npy'}
        if (m.get('kind') != 'context_tokens' or m.get('version') != 1 or m['policy'] != policy()
                or m['features_sha256'] != digest(features) or m['views_sha256'] != digest(views)
                or m['fasta_sha256'] != meta['fasta_sha256'] or m['samples'] != meta['samples']
                or m['parents'] != len(data['ids']) or set(m['members']) != names):
            raise ValueError('Context manifest/source/axes/policy differs')
        for name in sorted(names):
            if binding(self.root/name) != m['members'][name]:
                raise ValueError('Corrupt context member: '+name)
        arrays = {name[:-4]: np.load(self.root/name, mmap_mode='r', allow_pickle=False) for name in names}
        self.rows = arrays['rows']
        self.counts = arrays['counts']
        self.coordinates = arrays['coordinates']
        self.flipped = arrays['flipped']
        expected = np.flatnonzero(data['eligible'])
        n = len(expected)
        shape = (n, 5, policy()['tokens'])
        if (m['eligible'] != n or self.rows.dtype != np.int64 or not np.array_equal(self.rows, expected)
                or self.counts.dtype != np.uint16 or self.counts.shape != shape+(136,)
                or self.coordinates.dtype != np.int64 or self.coordinates.shape != shape+(2,)
                or self.flipped.dtype != bool or self.flipped.shape != (n, 5)):
            raise ValueError('Context bank array dtype/shape/eligible axis differs')
        self.lookup = np.full(len(data['ids']), -1, np.int64)
        self.lookup[self.rows] = np.arange(n)
        # Bounded semantic validation; never coerce/copy the full count bank.
        cfg = policy()
        for start in range(0, n, 1024):
            stop = min(start+1024, n)
            selected = expected[start:stop]
            available = np.column_stack([np.ones(stop-start, bool), v['usable'][selected]])
            lengths = np.column_stack([data['lengths'][selected],
                np.diff(v['coordinates'][selected], axis=2).squeeze(2)])
            for j in range(5):
                c = self.counts[start:stop, j]
                xy = self.coordinates[start:stop, j]
                missing = ~available[:, j]
                if c[missing].any() or (xy[missing] != -1).any() or self.flipped[start:stop, j][missing].any():
                    raise ValueError('Unavailable context has fabricated evidence')
                length = lengths[:, j]
                count = np.minimum(cfg['tokens'], np.maximum(1, length//cfg['token_min_interval']))
                for t in range(cfg['tokens']):
                    active = available[:, j] & (t < count)
                    padding = ~active
                    if (xy[padding, t] != -1).any() or c[padding, t].any():
                        raise ValueError('Invalid context padding')
                    left, right = t*length[active]//count[active], (t+1)*length[active]//count[active]
                    width = np.minimum(cfg['token_max_bp'], right-left)
                    a = left+(right-left-width)//2
                    if (not np.array_equal(xy[active, t], np.column_stack([a, a+width]))
                            or (c[active, t].sum(1) > np.maximum(width-3, 0)).any()):
                        raise ValueError('Invalid context coordinates/counts')
        self.lengths = data['lengths']
        self.view_coordinates = v['coordinates']

    def batch(self, selected, view_numbers, state):
        """Fetch transformed local TNF, center/span/reliability and mask in row order."""
        from ..candidate.model import transform
        selected, view_numbers = np.asarray(selected), np.asarray(view_numbers)
        if (selected.ndim != 1 or view_numbers.shape != selected.shape or selected.dtype.kind not in 'iu'
                or view_numbers.dtype.kind not in 'iu' or (selected < 0).any() or (selected >= len(self.lookup)).any()
                or (view_numbers < 0).any() or (view_numbers > 4).any() or (self.lookup[selected] < 0).any()):
            raise ValueError('Invalid context batch parent/view axes')
        ix = self.lookup[selected]
        counts = self.counts[ix, view_numbers].astype(np.float32)
        coordinates = self.coordinates[ix, view_numbers]
        totals = counts.sum(2)
        valid = totals > 0
        probabilities = counts/np.maximum(totals[..., None], 1)
        flat = probabilities.reshape(-1, 136)
        samples = len(state['depth']['mean'])
        values = transform(flat, np.zeros((len(flat), samples), np.float32), np.zeros(len(flat), bool), state)[0]
        values = values.reshape(counts.shape)
        values[~valid] = 0
        lengths = self.lengths[selected].copy()
        crop = view_numbers > 0
        lengths[crop] = np.diff(self.view_coordinates[selected[crop], view_numbers[crop]-1], axis=1).ravel()
        spans = coordinates[..., 1]-coordinates[..., 0]
        positions = np.stack([(coordinates[..., 0]+coordinates[..., 1])/(2*lengths[:, None]),
            spans/lengths[:, None], totals/np.maximum(spans-3, 1)], axis=2).astype(np.float32)
        positions[~valid] = 0
        return values, positions, valid
