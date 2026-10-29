"""Label-free rank calibration with explicit measured-zero/availability semantics.

Ranks refer to a reproducible local/random pair population, not to biological
probabilities. Immutable native vectors, TNF and parent means are read only.
No truth, model inference, marker detector or cloud dependency is reachable.
"""
from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
from numba import njit

from ..information.grouping import ordered_sample, require


DEFAULTS = dict(version=1, seed=11, core_min_bp=2500, length_scale_bp=2500,
    calibration_parents=8192, calibration_knots=129, neighbors=30,
    discovery_neighbors=61, max_candidates=60, index_iterations=15,
    index_delta=.001, query_epsilon=.2, batch_rows=512, exact_threshold=2048,
    audit_queries=32, audit_stratum_queries=16, min_neighbor_recall=.9,
    tie_tolerance=1e-10, core_degree=10, agreement_rank=.2,
    min_bin_contigs=2, min_bin_bp=10000, min_samples=10,
    distance_floor=.000001, marker_excess_penalty=5.,
    child_improvement_fraction=.05, neutral_rank=.5,
    recruit_min_support=2, recruit_vote_fraction=2/3,
    recruit_margin_ratio=1.5, recruit_new_excess_fraction=.05,
    reliable_marker_weight=.8)


def policy(path=None):
    """Return the single prospective policy; reject extra or changed defaults."""
    value = DEFAULTS.copy() if path is None else json.loads(Path(path).read_text())
    require(value == DEFAULTS and all(type(value[k]) is type(v) for k, v in DEFAULTS.items()),
            'Unfrozen E026 evidence-fusion policy')
    return value


@njit(cache=True)
def rank_value(value, x, y, count):
    """Interpolate validated monotone knots without a scalar-array allocation.

    Equivalent to NumPy interpolation on these unique finite knots. The explicit
    binary search avoids constructing a scalar result array in every native
    pair comparison; it changes neither calibration nor final-score precision.
    """
    if count == 0:
        return .5
    if value <= x[0]:
        return y[0]
    if value >= x[count-1]:
        return y[count-1]
    lo, hi = 0, count-1
    while hi-lo > 1:
        mid = (lo+hi)//2
        if x[mid] <= value:
            lo = mid
        else:
            hi = mid
    return y[lo]+(value-x[lo])*(y[hi]-y[lo])/(x[hi]-x[lo])


@njit(cache=True, fastmath={'reassoc', 'contract'})
def fused_metric(a, b, native_dim, composition_dim, knot_x, knot_y, counts,
                 active, length_scale, floor):
    """Compiled symmetric score; missing/co-absent channels keep a fixed denominator.

    Packed tails are exact integer length, native/TNF/measurement masks, positive
    depth flag. Accumulate in float64; native index distances alone use float32.
    The same expression is independently vectorized for final rerank/audit.
    """
    ends = (0, native_dim, native_dim+composition_dim, len(a)-5)
    reliability = np.sqrt((np.float64(a[-5])/(a[-5]+length_scale))
                          *(np.float64(b[-5])/(b[-5]+length_scale)))
    score = 0.; weight = 0.
    for c in range(3):
        if not active[c]:
            continue
        observed = a[-4+c] == 1 and b[-4+c] == 1
        if c == 2:
            observed = observed and (a[-1] == 1 or b[-1] == 1)
        q = .5
        if observed:
            d = 0.
            for j in range(ends[c], ends[c+1]):
                z = np.float64(a[j])-np.float64(b[j]); d += z*z
            q = rank_value(d, knot_x[c], knot_y[c], counts[c])
            if c > 0:
                q = .5+reliability*(q-.5)
        score += q; weight += 1.
    return max(score/weight if weight else .5, floor)


@njit(cache=True)
def index_metric(a, b, native_dim, composition_dim, knot_x, knot_y, counts,
                 active, length_scale, floor):
    """Use the native search heap's float32 dtype; final scoring stays float64.

    PyNNDescent 0.5.13's parallel query heap requires the callable's return dtype
    to match its float32 distance storage. This explicit adapter changes neither
    vectors nor final rerank/audit precision and avoids modifying dependencies.
    """
    return np.float32(fused_metric(a, b, native_dim, composition_dim, knot_x, knot_y,
                                  counts, active, length_scale, floor))


@dataclass
class Fusion:
    """Read-only channel coordinates and calibration sufficient for exact reload."""
    channels: tuple
    available: np.ndarray
    positive: np.ndarray
    lengths: np.ndarray
    knot_x: np.ndarray
    knot_y: np.ndarray
    counts: np.ndarray
    active: np.ndarray
    cfg: dict
    record: dict

    def distances(self, i, rows, trace=False):
        """Exact float64 rerank; optionally return raw ranks and evidence masks."""
        rows = np.asarray(rows, np.int64)
        q = np.full((len(rows), 3), .5, np.float64)
        observed = self.available[rows] & self.available[i] & self.active
        observed[:, 2] &= self.positive[rows] | self.positive[i]
        for c, x in enumerate(self.channels):
            take = observed[:, c]
            if not take.any():
                continue
            d = ((x[rows[take]].astype(np.float64)-x[i])**2).sum(1)
            q[take, c] = np.interp(d, self.knot_x[c, :self.counts[c]],
                                  self.knot_y[c, :self.counts[c]])
        r = np.sqrt((float(self.lengths[i])/(self.lengths[i]+self.cfg['length_scale_bp']))
                    *(self.lengths[rows]/(self.lengths[rows]+self.cfg['length_scale_bp'])))
        shrunk = q.copy(); shrunk[:, 1:] = .5+r[:, None]*(q[:, 1:]-.5)
        value = (shrunk[:, self.active].mean(1) if self.active.any()
                 else np.full(len(rows), .5))
        value = np.maximum(value, self.cfg['distance_floor'])
        return (value, q, observed) if trace else value

    def agreement(self, i, rows):
        """Require two distinct informative channels; statistical independence is not assumed."""
        _, ranks, observed = self.distances(i, rows, True)
        good = ((~observed) | (ranks <= self.cfg['agreement_rank'])).all(1)
        return good & (observed.sum(1) >= 2)

    def packed(self, rows):
        """Pack new index inputs without changing original vectors or integer lengths."""
        lengths = self.lengths[rows]
        require(np.array_equal(lengths.astype(np.float32).astype(np.int64), lengths),
                'Length packing would change calibrated score')
        return np.ascontiguousarray(np.column_stack(
            [x[rows] for x in self.channels]+[lengths, self.available[rows], self.positive[rows]]),
            dtype=np.float32)

    def metric_args(self):
        """Preserve documented ordered custom-metric kwargs for native NNDescent."""
        return dict(native_dim=self.channels[0].shape[1], composition_dim=self.channels[1].shape[1],
            knot_x=self.knot_x, knot_y=self.knot_y, counts=self.counts, active=self.active,
            length_scale=self.cfg['length_scale_bp'], floor=self.cfg['distance_floor'])


def quantile_knots(values, count):
    """Build monotone bounded quantile interpolation, retaining duplicate mid-ranks."""
    if len(values) < 2 or np.ptp(values) <= 1e-12:
        return np.empty(0), np.empty(0)
    p = np.linspace(0., 1., count)
    raw = np.quantile(values, p)
    x, first, size = np.unique(raw, return_index=True, return_counts=True)
    y = np.array([p[a:a+n].mean() for a, n in zip(first, size)])
    if x[0] > 0:
        x, y = np.r_[0., x], np.r_[0., y]
    else:
        # Identical informative coordinates are the strongest observed agreement,
        # even when many reference pairs tie at zero. Co-absence is separately
        # neutralized by the availability mask, never by this numerical anchor.
        y[0] = 0.
    return x, y


def calibrate(data, vectors, valid, original, cfg, measured=None):
    """Fit one source-blind reference scale, with complete raw-pair provenance.

    Actual admitted matrices are complete. An explicit boolean measurement mask
    is supported for tiny partial-channel contracts; missing means are never
    guessed from their numerical value. `depth_evidence` is not a missing mask.
    """
    ids = data['ids']; n = len(ids)
    require(vectors.shape[0] == n and vectors.ndim == 2 and np.isfinite(vectors).all()
            and valid.shape == (n,) and valid.dtype == bool
            and data['depth'].shape[0] == n and np.isfinite(data['depth']).all()
            and (data['depth'] >= 0).all() and (data['lengths'] > 0).all()
            and len(set(ids.tolist())) == n, 'Malformed fusion axes/coordinates')
    has_depth = data['depth'].shape[1] > 0
    measured = np.full(n, has_depth, bool) if measured is None else np.asarray(measured)
    require(measured.shape == (n,) and measured.dtype == bool, 'Explicit measurement mask required')
    require(has_depth or not measured.any(), 'Absent depth modality cannot claim measured rows')
    raw = np.log1p(data['depth'].astype(np.float64))
    spread = raw[valid & measured].std(0) if (valid & measured).any() else np.zeros(raw.shape[1])
    use = spread > 1e-8
    depth = (raw[:, use]/spread[use]).astype(np.float32)
    channels = (vectors, np.sqrt(data['tnf'].astype(np.float32)), depth)
    require(all(np.isfinite(x).all() for x in channels), 'Malformed TNF/context channels')
    available = np.column_stack([valid, valid & (data['valid_fourmers'] > 0), measured & bool(use.any())])
    positive = (data['depth'] > 0).any(1)
    selected = ordered_sample(ids.tolist(), np.flatnonzero(valid), cfg['calibration_parents'])
    pairs = set()
    if len(selected) > 1:
        for i, j in zip(selected, np.roll(selected, -1)):
            pairs.add(tuple(sorted((int(i), int(j)))))
    for i in selected:
        row = original['neighbors'][i]
        row = row[(row >= 0) & (row != i)]
        if len(row):
            require(np.all(row < n) and np.all(valid[row]), 'Calibration neighbour escaped valid axis')
            pairs.add(tuple(sorted((int(i), int(row[0])))))
    pairs = np.array(sorted(pairs, key=lambda p: (str(ids[p[0]]), str(ids[p[1]]))), np.int64).reshape(-1, 2)
    width = cfg['calibration_knots']+1
    knot_x = np.zeros((3, width)); knot_y = np.zeros_like(knot_x)
    counts = np.zeros(3, np.int64); raw_pairs = np.full((len(pairs), 3), -1.)
    for c, x in enumerate(channels):
        observed = available[pairs].all(1)[:, c]
        if c == 2:
            observed &= positive[pairs].any(1)
        d = ((x[pairs[observed, 0]].astype(np.float64)-x[pairs[observed, 1]])**2).sum(1)
        raw_pairs[observed, c] = d
        a, b = quantile_knots(d, cfg['calibration_knots'])
        counts[c] = len(a); knot_x[c, :len(a)] = a; knot_y[c, :len(b)] = b
    record = dict(version=1, cfg=cfg, channel_order=['native_unit', 'sqrt_TNF', 'log1p_measured_parent_depth'],
        calibration_pairs=pairs.tolist(), pair_ids=ids[pairs].tolist(), raw_pair_distances=raw_pairs.tolist(),
        knot_x=[knot_x[i, :k].tolist() for i, k in enumerate(counts)],
        knot_y=[knot_y[i, :k].tolist() for i, k in enumerate(counts)],
        depth_column_std=spread.tolist(), depth_usable_columns=use.tolist(),
        active_channels=(counts > 0).tolist(), measured_rows=int(measured.sum()),
        incomplete_measurement_rows=int((~measured).sum()) if has_depth else 0,
        no_depth_modality_rows=0 if has_depth else n,
        all_zero_rows=int((~positive & measured).sum()),
        semantics='Empirical rank calibration, not biological probability; measured zero-positive contrast; neutral co-absence/missing on fixed active-channel denominator; no measured variance/window depth')
    return Fusion(channels, available, positive, data['lengths'], knot_x, knot_y,
                  counts, counts > 0, cfg, record)
