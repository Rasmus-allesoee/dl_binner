"""Fixed-learning, length-aware core graph and non-propagating recruitment.

This research module consumes sealed features and original native unit vectors.
It has no training, sequence extraction, marker search, truth or cloud interface.
Distances and reliability factors are label-free heuristics, not calibrated
probabilities or measured coverage variances. Every input row survives.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from ..candidate.grouping import canonical_partition
from ..io import digest, emit, save_arrays, validate_features, write_json
from ..multiview.arrays import load_arrays


def require(condition, message):
    """Refuse malformed evidence under optimized as well as ordinary Python."""
    if not condition:
        raise ValueError(message)


def policy(path):
    """Read the single frozen E017 policy; refuse extra keys and invalid bounds."""
    cfg = json.loads(Path(path).read_text())
    expected = dict(version=1, core_min_bp=2500, reliability_fourmers=2500,
                    neighbors=30, candidates=60, calibration_pairs=8192,
                    exact_threshold=2048, audit_queries=32, min_neighbor_recall=.9,
                    profile_quantile=.95, profile_floor_fraction=.01,
                    recruit_min_support=2, recruit_vote_fraction=2/3,
                    recruit_margin_ratio=1.5, recruit_max_normalized_distance=1.,
                    seed=11, leiden_iterations=2, batch_rows=1024)
    require(cfg == expected and all(type(cfg[k]) is type(v) for k, v in expected.items()),
            'Information-grouping policy is not the frozen single rule')
    return cfg


def load_inputs(features, embeddings):
    """Validate full opaque axes, measured-depth semantics and unchanged geometry."""
    data, meta = load_arrays(features, 'features')
    validate_features(data, meta)
    a, em = load_arrays(embeddings, 'embeddings')
    n = len(data['ids'])
    require(a['ids'].tolist() == data['ids'].tolist()
            and em['features_sha256'] == digest(features)
            and a['features'].shape == (n, 64)
            and a['evidence'].shape == (n,) and a['evidence'].dtype == bool
            and np.isfinite(a['features']).all(), 'Feature/embedding axes or bytes differ')
    valid = data['eligible'] & a['evidence']
    require(np.array_equal(valid, data['eligible'])
            and np.allclose(np.linalg.norm(a['features'][valid], axis=1), 1, atol=1e-5)
            and not np.any(a['features'][~valid]), 'Original native eligible unit geometry required')
    require(meta['depth_semantics'].lower().find('parent') >= 0,
            'Explicit measured-parent depth semantics required')
    return data, a['features'], valid, meta


def ordered_sample(ids, selected, limit):
    """Choose a fixed source-blind ID-hash sample, independent of truth and length."""
    return np.array(sorted(map(int, selected),
                           key=lambda i: (hashlib.sha256(ids[i].encode()).digest(), ids[i]))[:limit],
                    dtype=np.int64)


def contexts(data, vectors, cores, cfg):
    """Return retained channels and deterministic pair scales without DNA reads.

    Depth column spread is between observed parent means, not read-depth variance.
    All-zero rows and constant columns supply no depth evidence. Pair distances
    set comparable numerical units, not probabilities of common genome origin.
    """
    ids = data['ids'].tolist()
    comp = np.sqrt(data['tnf'].astype(np.float32))
    depth = np.log1p(data['depth'].astype(np.float64))
    scale = depth[cores].std(0) if len(cores) else np.zeros(depth.shape[1])
    use = scale > 1e-8
    depth = (depth[:, use]/scale[use]).astype(np.float32)
    available = data['depth_evidence'] & bool(use.any())
    selected = ordered_sample(ids, cores, cfg['calibration_pairs'])
    pairs = np.column_stack((selected, np.roll(selected, -1))) if len(selected) > 1 else np.empty((0, 2), np.int64)
    channels = (vectors, comp, depth)
    scales, constants = [], []
    for channel, x in enumerate(channels):
        chosen = pairs if channel != 2 else pairs[available[pairs].all(1)]
        d = ((x[chosen[:, 0]].astype(np.float64)-x[chosen[:, 1]])**2).sum(1)
        positive = d[d > 1e-12]
        constants.append(not bool(len(positive)))
        scales.append(float(np.median(positive)) if len(positive) else 1.)
    meta = dict(channel_order=['native_unit', 'sqrt_TNF', 'log1p_measured_parent_depth'],
                pair_ids=[[ids[i], ids[j]] for i, j in pairs], pair_scales=scales,
                constant_pair_channels=constants, depth_column_std=scale.tolist(),
                depth_usable_columns=use.tolist(), depth_missing_rows=int((~available).sum()),
                depth_semantics='between-parent means; no per-base/window coverage or variance',
                reliability='N_valid_fourmers/(N_valid_fourmers+2500), overlapping-count heuristic')
    return channels, available, np.array(scales), meta


class CoreIndex:
    """One reusable joint learned/composition index, with bounded exact tiny path.

    Native NNDescent is used beyond the frozen crossover. Query candidates are
    reranked by actual joint Euclidean distance and deterministic opaque-ID ties.
    The index is never rebuilt after observing recruitment or scientific scores.
    """
    def __init__(self, coordinates, ids, cfg, threads):
        self.x = np.asarray(coordinates, np.float32)
        self.ids, self.cfg = list(ids), cfg
        self.native = None
        require(self.x.ndim == 2 and len(self.x) == len(ids)
                and len(set(ids)) == len(ids) and np.isfinite(self.x).all()
                and type(threads) is int and 1 <= threads <= 4, 'Malformed core index')
        if len(ids) > cfg['exact_threshold']:
            import numba
            from pynndescent import NNDescent
            numba.set_num_threads(threads)
            emit('information_core_index_start', rows=len(ids), dimensions=self.x.shape[1], threads=threads)
            self.native = NNDescent(self.x, metric='euclidean', n_neighbors=min(len(ids), cfg['candidates']+1),
                                   random_state=cfg['seed'], n_jobs=threads, low_memory=True,
                                   max_candidates=60, n_iters=10, verbose=True)

    def query(self, x, self_indices=None):
        """Return up to 60 distinct exact-reranked core candidates per query."""
        x = np.asarray(x, np.float32)
        require(x.ndim == 2 and x.shape[1] == self.x.shape[1] and np.isfinite(x).all(),
                'Malformed index query coordinates')
        count = min(self.cfg['candidates'], max(0, len(self.x)-(self_indices is not None)))
        nn = np.full((len(x), count), -1, np.int64)
        dd = np.zeros((len(x), count), np.float64)
        if count == 0:
            return nn, dd
        if self.native is not None:
            proposed = self.native.query(x, k=min(len(self.x), count+1))[0]
        else:
            proposed = None
        for row, v in enumerate(x):
            exclude = int(self_indices[row]) if self_indices is not None else -1
            candidates = range(len(self.x)) if proposed is None else proposed[row]
            choices = np.array(sorted({int(i) for i in candidates if 0 <= i < len(self.x) and i != exclude},
                                      key=lambda i: self.ids[i]), np.int64)
            require(len(choices) >= count, 'Native core candidate index has missing/duplicate rows')
            d = ((self.x[choices].astype(np.float64)-v)**2).sum(1)
            order = np.argsort(d, kind='stable')[:count]
            nn[row], dd[row] = choices[order], d[order]
        return nn, dd

    def audit(self, x, ids, nn, distances, self_indices=None):
        """Refuse low recall on fixed sampled queries; ties count as valid hits."""
        k = min(self.cfg['neighbors'], nn.shape[1])
        selected = ordered_sample(ids, range(len(ids)), self.cfg['audit_queries'])
        recalls = []
        for row in selected:
            if not k:
                break
            d = ((self.x.astype(np.float64)-x[row])**2).sum(1)
            if self_indices is not None:
                d[self_indices[row]] = np.inf
            threshold = np.partition(d, k-1)[k-1]
            recalls.append(float(np.mean(distances[row, :k] <= threshold+1e-6)))
        mean = float(np.mean(recalls)) if recalls else 1.
        require(mean >= self.cfg['min_neighbor_recall'], 'Core/query sampled neighbor recall below frozen gate')
        return dict(mode='NNDescent_joint_exact_rerank' if self.native is not None else 'bounded_exact',
                    mean_tie_aware_recall=mean, k=k, queries=[ids[i] for i in selected],
                    threshold=self.cfg['min_neighbor_recall'], guarantee='sampled queries only')


def joint_coordinates(channels, scales):
    """Create one equally scaled learned/composition index; no missing-depth fill."""
    return np.concatenate([channels[j]/np.sqrt(scales[j]) for j in range(2)], axis=1).astype(np.float32)


def distances(channels, available, rows, candidates, scales, counts, cfg):
    """Calculate all available channel distances and finite-length affinities."""
    result = np.zeros((*candidates.shape, 3), np.float64)
    mask = np.ones_like(result, bool)
    for j, x in enumerate(channels):
        delta = x[candidates].astype(np.float64)-x[rows, None, :]
        result[:, :, j] = (delta*delta).sum(2)/scales[j]
    mask[:, :, 2] = available[rows, None] & available[candidates]
    result[:, :, 2] *= mask[:, :, 2]
    reliability = counts/(counts+cfg['reliability_fourmers'])
    r = np.sqrt(reliability[rows, None]*reliability[candidates])
    weights = np.stack([np.ones_like(r), r, mask[:, :, 2].astype(float)], axis=2)
    score = np.sum(result*weights, axis=2)/weights.sum(2)
    affinity = np.exp(-score)*r
    # A positive exponential alone gives every poor pair an edge, including
    # forced distant neighbors when the core population is smaller than k.
    # Require agreement better than the label-free background pair medians.
    # This is an explicit conservative graph gate, not a genome probability.
    agreement = ((result[:, :, :2] < 1.).all(2)
                 & (result[:, :, 0]*scales[0] < 2.)
                 & (~mask[:, :, 2] | (result[:, :, 2] < 1.)))
    affinity *= agreement
    require(np.isfinite(result).all() and np.isfinite(affinity).all(), 'Nonfinite multi-evidence affinity')
    return result, mask, affinity


def core_partition(data, valid, core_rows, directed, affinities, cfg, support):
    """Retain a symmetric sparse core graph and sole median-edge/30 CPM partition."""
    import igraph as ig
    import leidenalg
    pairs, weights = [], []
    for i, row in enumerate(directed):
        k = min(cfg['neighbors'], len(row))
        order = sorted(range(len(row)), key=lambda j: (-affinities[i, j], str(data['ids'][row[j]])))[:k]
        for j in order:
            if affinities[i, j] > 0:
                pairs.append((min(int(core_rows[i]), int(row[j])), max(int(core_rows[i]), int(row[j]))))
                weights.append(affinities[i, j])
    if pairs:
        edges = np.array(pairs, np.int64)
        order = np.lexsort((edges[:, 1], edges[:, 0]))
        edges, weights = edges[order], np.array(weights)[order]
        starts = np.r_[0, 1+np.flatnonzero(np.any(edges[1:] != edges[:-1], axis=1))]
        weights = np.maximum.reduceat(weights, starts)
        edges = edges[starts]
        lookup = np.full(len(valid), -1, np.int64)
        lookup[core_rows] = np.arange(len(core_rows))
        graph = ig.Graph(n=len(core_rows), edges=lookup[edges].tolist(), directed=False)
        gamma = float(np.median(weights))/cfg['neighbors']
        partition = leidenalg.find_partition(graph, leidenalg.CPMVertexPartition, weights=weights.tolist(),
                                             node_sizes=[1]*len(core_rows), resolution_parameter=gamma,
                                             seed=cfg['seed'], n_iterations=cfg['leiden_iterations'])
        groups = [[int(core_rows[i]) for i in c] for c in partition]
    else:
        edges, weights, gamma, groups = np.empty((0, 2), np.int64), np.empty(0), None, []
    reasons = np.where(valid, 'no_supported_core', data['exclusion_reason']).tolist()
    result = canonical_partition(data['ids'].tolist(), valid, groups, data['lengths'], support, reasons)
    return result, edges, weights, gamma


def core_profiles(data, channels, available, assignment, scales, cfg):
    """Freeze length-weighted core centers and leave-one-out empirical envelopes."""
    labels = np.array(assignment)
    bins = sorted(set(int(v) for v in labels if v >= 0))
    centers = [np.zeros((len(bins), x.shape[1]), np.float64) for x in channels]
    radii = np.full((len(bins), 3), cfg['profile_floor_fraction'], np.float64)
    present = np.zeros((len(bins), 3), bool)
    counts = np.zeros(len(bins), np.int64)
    order = np.argsort(labels, kind='stable')
    starts = np.searchsorted(labels[order], np.arange(len(bins)+1))
    for b in bins:
        members = order[starts[b]:starts[b+1]]
        counts[b] = len(members)
        for j, x in enumerate(channels):
            sel = members if j != 2 else members[available[members]]
            if len(sel) < 2:
                continue
            mass = data['lengths'][sel].astype(np.float64)
            values = x[sel].astype(np.float64)
            total = (values*mass[:, None]).sum(0)
            center = total/mass.sum()
            loo = (total-values*mass[:, None])/(mass.sum()-mass[:, None])
            if j == 0:
                norm = np.linalg.norm(center)
                norms = np.linalg.norm(loo, axis=1)
                if norm <= 1e-12 or np.any(norms <= 1e-12):
                    continue
                center, loo = center/norm, loo/norms[:, None]
            d = ((values-loo)**2).sum(1)/scales[j]
            centers[j][b], present[b, j] = center, True
            radii[b, j] = max(cfg['profile_floor_fraction'], float(np.quantile(d, cfg['profile_quantile'])))
    return centers, radii, present, counts


def recruit(data, valid, channels, available, scales, pre, query_rows, candidates,
            affinities, cfg):
    """Make one non-propagating assignment with complete offered-bin evidence.

    No newly recruited contig changes any profile or vote. Reliability affects
    composition/learned envelopes, never fabricates measured depth variance.
    Markers are deliberately absent here; the unchanged E013 policy follows.
    """
    centers, radii, present, counts = core_profiles(data, channels, available, pre['assignment'], scales, cfg)
    labels = np.array(pre['assignment'], np.int64)
    width = candidates.shape[1]
    offers = np.full((len(query_rows), width), -1, np.int64)
    scores = np.full((len(query_rows), width), -1., np.float32)
    channel_scores = np.zeros((len(query_rows), width, 3), np.float32)
    channel_masks = np.zeros_like(channel_scores, bool)
    votes = np.zeros_like(scores)
    supporters = np.zeros_like(offers)
    accepted = np.full(len(query_rows), -1, np.int64)
    reasons = []
    for row, i in enumerate(query_rows):
        near_labels = labels[candidates[row]]
        bins = sorted(set(int(b) for b in near_labels if b >= 0))
        reason = 'no_supported_core_candidate'
        if bins:
            total_vote = float(affinities[row, near_labels >= 0].sum())
            inflation = max(1., cfg['core_min_bp']/max(1, int(data['valid_fourmers'][i])))
            for at, b in enumerate(bins):
                offers[row, at] = b
                support = (near_labels == b) & (affinities[row] > 0)
                supporters[row, at] = int(support.sum())
                votes[row, at] = float(affinities[row, support].sum())/total_vote if total_vote else 0.
                available_channels = present[b].copy()
                available_channels[2] &= available[i]
                channel_masks[row, at] = available_channels
                if not available_channels[:2].all():
                    scores[row, at] = np.finfo(np.float32).max
                    continue
                d = np.zeros(3)
                for j, x in enumerate(channels):
                    if available_channels[j]:
                        d[j] = ((x[i]-centers[j][b])**2).sum()/scales[j]/radii[b, j]
                        if j < 2:
                            d[j] /= inflation
                channel_scores[row, at] = d
                scores[row, at] = float(d[available_channels].mean())
            order = sorted(range(len(bins)), key=lambda at: (float(scores[row, at]), bins[at]))
            best = order[0]
            within = scores[row, best] <= cfg['recruit_max_normalized_distance']
            margin = len(order) == 1 or scores[row, best]*cfg['recruit_margin_ratio'] < scores[row, order[1]]
            support = supporters[row, best] >= cfg['recruit_min_support']
            vote = votes[row, best] >= cfg['recruit_vote_fraction']
            if within and margin and support and vote:
                accepted[row] = bins[best]
                reason = 'accepted_fixed_core_profile'
            else:
                reason = ('profile_outside_envelope' if not within else 'ambiguous_core_margin' if not margin
                          else 'insufficient_distinct_core_support' if not support else 'discordant_core_votes')
        reasons.append(reason)
    groups = [[] for _ in range(pre['clusters'])]
    for i, b in enumerate(pre['assignment']):
        if b >= 0:
            groups[b].append(i)
    full_reasons = list(pre['reason'])
    for row, i in enumerate(query_rows):
        b = int(accepted[row])
        if b >= 0:
            groups[b].append(int(i))
        full_reasons[i] = '' if b >= 0 else reasons[row]
    out = canonical_partition(data['ids'].tolist(), valid, groups, data['lengths'], pre['config'], full_reasons)
    evidence = dict(query_indices=query_rows, candidate_indices=candidates, candidate_affinities=affinities,
                    offered_bins=offers, normalized_scores=scores, channel_scores=channel_scores,
                    channel_available=channel_masks, vote_fractions=votes, distinct_support=supporters,
                    accepted_bins=accepted, reasons=np.array(reasons, dtype='U48'),
                    profile_radii=radii, profile_available=present, profile_core_counts=counts,
                    profile_native=centers[0], profile_composition=centers[1], profile_depth=centers[2])
    return out, evidence


def group(features, embeddings, output, cfg, support, threads=4):
    """Write fresh core/recruit partitions and every sparse decision/cache byte.

    This is the only community grouping entry point; it must be called only by a
    separately authorized bounded launcher. Tiny real fixtures use the same code.
    """
    data, vectors, valid, meta = load_inputs(features, embeddings)
    require(support['seed'] == cfg['seed'] == 11 and support['neighbors'] == cfg['neighbors'] == 30,
            'Frozen downstream seed/neighbor count differs')
    ids = data['ids'].tolist()
    cores = np.array(sorted(np.flatnonzero(valid & (data['lengths'] >= cfg['core_min_bp'])),
                            key=lambda i: ids[i]), np.int64)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    channels, available, scales, transform = contexts(data, vectors, cores, cfg)
    coordinates = joint_coordinates(channels, scales)
    index = CoreIndex(coordinates[cores], [ids[i] for i in cores], cfg, threads)
    local, dd = index.query(coordinates[cores], np.arange(len(cores)))
    audit = index.audit(coordinates[cores], [ids[i] for i in cores], local, dd, np.arange(len(cores)))
    candidates = cores[local]
    d = np.empty((*candidates.shape, 3), np.float32)
    mask = np.zeros_like(d, bool)
    affinity = np.zeros(candidates.shape, np.float64)
    for start in range(0, len(cores), cfg['batch_rows']):
        sl = slice(start, start+cfg['batch_rows'])
        d[sl], mask[sl], affinity[sl] = distances(channels, available, cores[sl], candidates[sl],
                                                scales, data['valid_fourmers'], cfg)
        if start % (10*cfg['batch_rows']) == 0:
            emit('information_core_affinities', rows=min(start+cfg['batch_rows'], len(cores)), total=len(cores))
    core, edges, weights, gamma = core_partition(data, valid, cores, candidates, affinity, cfg, support)
    core['config'] = support
    queries = np.array(sorted(np.flatnonzero(valid & (np.array(core['assignment']) < 0)), key=lambda i: ids[i]), np.int64)
    qlocal = np.empty((len(queries), min(cfg['candidates'], len(cores))), np.int64)
    qdd = np.zeros(qlocal.shape)
    for start in range(0, len(queries), cfg['batch_rows']):
        sl = slice(start, start+cfg['batch_rows'])
        qlocal[sl], qdd[sl] = index.query(coordinates[queries[sl]])
        emit('information_recruit_candidates', rows=min(start+cfg['batch_rows'], len(queries)), total=len(queries))
    qaudit = index.audit(coordinates[queries], [ids[i] for i in queries], qlocal, qdd)
    qcandidate = cores[qlocal]
    qaffinity = np.zeros(qcandidate.shape)
    for start in range(0, len(queries), cfg['batch_rows']):
        sl = slice(start, start+cfg['batch_rows'])
        _, _, qaffinity[sl] = distances(channels, available, queries[sl], qcandidate[sl], scales, data['valid_fourmers'], cfg)
    parent, recruitment = recruit(data, valid, channels, available, scales, core, queries, qcandidate, qaffinity, cfg)
    save_arrays(out/'graph.npz', dict(ids=data['ids'], core_indices=cores, candidates=candidates,
                channel_distances=d, channel_available=mask, candidate_affinities=affinity,
                edges=edges, weights=weights), dict(kind='information_core_graph',
                features_sha256=digest(features), embedding_sha256=digest(embeddings),
                objective=dict(gamma=gamma, rule='median_positive_edge_weight / 30', node_sizes=1),
                audit=audit, transform=transform, information_config=cfg))
    # Index storage is lossless at this admitted population size. Scientific
    # affinities/radii retain their precision; native vectors are never rewritten.
    stored = {k: (v.astype(np.int32) if v.dtype == np.int64 and
                   (not v.size or (v.min() >= -1 and v.max() <= np.iinfo(np.int32).max)) else v)
              for k, v in recruitment.items()}
    save_arrays(out/'recruitment.npz', dict(ids=data['ids'], **stored),
                dict(kind='information_recruitment', features_sha256=digest(features),
                     embedding_sha256=digest(embeddings), graph_sha256=digest(out/'graph.npz'), audit=qaudit,
                     rule='fixed supported core profiles; one pass; no recruited-contig propagation', config=cfg))
    # E013 copies, but never reads, this legacy display field. The complete
    # numeric neighbor axes live once in the hash-bound sparse caches, avoiding
    # four repeated million-row ID-string lists. No neighbors are discarded.
    neighbors = []
    for name, value in [('core-partition.json', core), ('partition.json', parent)]:
        value.update(neighbors=neighbors, parent_features_sha256=digest(features),
                     embedding_sha256=digest(embeddings), graph_sha256=digest(out/'graph.npz'),
                     algorithm='E017 multi-evidence core CPM and fixed-profile recruitment', config=support,
                     information_config=cfg, scientific_quality_assessed=False,
                     neighbor_storage=dict(mode='complete_sparse_numeric_cache',
                         core='graph.npz:candidates', recruitment='recruitment.npz:candidate_indices',
                         query_axes='core_indices / query_indices; original full FASTA row indices'))
        write_json(out/name, value)
    for path, kind in [('graph.npz', 'information_core_graph'), ('recruitment.npz', 'information_recruitment')]:
        load_arrays(out/path, kind)
    write_json(out/'completed.json', dict(status='SUCCESS', rows=len(ids), bp=int(data['lengths'].sum()),
                cores=len(cores), recruited=int((recruitment['accepted_bins'] >= 0).sum()),
                clusters=parent['clusters'], samples=meta['samples'], depth_semantics=transform['depth_semantics'],
                graph_sha256=digest(out/'graph.npz'), recruitment_sha256=digest(out/'recruitment.npz'),
                features_sha256=digest(features), embeddings_sha256=digest(embeddings),
                core_partition_sha256=digest(out/'core-partition.json'), parent_sha256=digest(out/'partition.json'),
                native_audit=audit, recruitment_audit=qaudit, truth_used=False, encoder_inference=False))
    emit('information_grouping_complete', rows=len(ids), cores=len(cores), recruited=int((recruitment['accepted_bins'] >= 0).sum()))
