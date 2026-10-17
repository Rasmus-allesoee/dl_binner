#!/usr/bin/env python3
"""Confidence/quality-aware marker refinement of a fixed CPM parent partition.

Pure label-free functions consume retained genes/domains, measured parent means
and original unit vectors. No truth, inference, marker search, graph optimizer or
reference taxonomy is reachable. Marker quality is a panel-dependent proxy,
never a calibrated completeness/contamination estimate or MAG quality claim.
"""
from collections import defaultdict
import math


def require(condition, message):
    """Refuse malformed retained evidence independently of assertion settings."""
    if not condition:
        raise ValueError(message)


def marker_evidence(genes, domains, families, profiles, ids, lengths, config):
    """Weight trusted family calls and consolidate overlapping physical loci.

    Weight is HMM coverage times 1-2**(-positive domain-score margin over TC).
    Partial gene calls receive another coverage factor. These are heuristic
    evidence weights, not probabilities. Ambiguous multi-family genes remain
    recorded but supply no constraint. Separate contigs never become a single
    locus merely because their proteins/families match.
    """
    by_gene = defaultdict(list); axis = dict(zip(ids, map(int, lengths)))
    for name, g in genes.items():
        require(g['contig'] in axis and g['strand'] in (-1, 1)
                and 0 <= g['start'] < g['end'] <= axis[g['contig']]
                and type(g['partial_begin']) is bool and type(g['partial_end']) is bool,
                'Malformed cached gene coordinates/partial flags')
    for d in domains:
        require(d['gene'] in genes and d['marker'] in families and d['marker'] in profiles,
                'Unknown domain/gene/profile')
        g, p = genes[d['gene']], profiles[d['marker']]
        require(d['hmm_length'] == int(p['LENG'])
                and 1 <= d['hmm_from'] <= d['hmm_to'] <= d['hmm_length']
                and 1 <= d['protein_from'] <= d['protein_to'] <= g['protein_length']
                and math.isfinite(d['score']), 'Malformed cached HMM domain')
        coverage = (d['hmm_to']-d['hmm_from']+1)/d['hmm_length']
        require(abs(coverage-d['hmm_coverage']) < 1e-12, 'Cached HMM coverage differs')
        tc = [float(v) for v in p['TC'].rstrip(';').split()]
        require(len(tc) == 2 and all(math.isfinite(v) for v in tc), 'Malformed trusted cutoff')
        margin = max(0., d['score']-tc[1])
        require(math.isfinite(margin), 'Nonfinite trusted-score margin')
        r = coverage*(-math.expm1(-math.log(2)*margin))
        if g['partial_begin'] or g['partial_end']:
            r *= coverage
        left, right = ((g['start']+3*(d['protein_from']-1), g['start']+3*d['protein_to'])
                       if g['strand'] == 1 else
                       (g['end']-3*d['protein_to'], g['end']-3*(d['protein_from']-1)))
        require(g['start'] <= left < right <= g['end'] and 0 <= r <= 1, 'Domain escaped gene')
        by_gene[d['gene']].append(dict(contig=g['contig'], gene=d['gene'], family=families[d['marker']],
            start=left, end=right, reliability=r, hmm_coverage=coverage, margin_bits=margin,
            partial=g['partial_begin'] or g['partial_end'], profile=d['marker']))
    loci = defaultdict(list); ambiguous = []
    for gene, values in sorted(by_gene.items()):
        if len({v['family'] for v in values}) != 1:
            ambiguous.append(gene)
        else:
            for v in values:
                loci[v['contig'], v['family']].append(v)
    retained, consolidated = [], []
    for key, values in sorted(loci.items()):
        physical = []
        for v in sorted(values, key=lambda v: (-v['reliability'], v['start'], v['end'], v['gene'], v['profile'])):
            overlap = [w for w in physical if max(0, min(v['end'], w['end'])-max(v['start'], w['start']))
                       >= config['physical_overlap_fraction']*min(v['end']-v['start'], w['end']-w['start'])]
            if overlap:
                consolidated.append(dict(call=v, representative=overlap[0]['gene']))
            else:
                physical.append(v)
        retained.extend(physical)
    calls = defaultdict(lambda: defaultdict(list))
    for v in retained:
        calls[v['contig']][v['family']].append(v['reliability'])
    return dict(version=1, calls={q: dict(v) for q, v in calls.items()}, loci=retained,
                ambiguous_genes=ambiguous, consolidated=consolidated,
                families=sorted(set(families.values())), panel_size=len(set(families.values())),
                semantics='heuristic weighted family breadth/repetition; no lineage calibration or cross-contig locus collapse')


def quality(members, evidence, ids, config):
    """Compute weighted family breadth minus five times excess-copy evidence."""
    families = defaultdict(list)
    for i in members:
        for family, weights in evidence['calls'].get(ids[i], {}).items():
            families[family].extend(weights)
    breadth = math.fsum(max(v) for v in families.values())
    excess = math.fsum(math.fsum(v)-max(v) for v in families.values())
    scale = 100/evidence['panel_size']
    return dict(breadth_proxy=scale*breadth, excess_copy_proxy=scale*excess,
                score=scale*(breadth-config['excess_penalty']*excess), observed_families=len(families))


def seed_proposal(members, evidence, ids, lengths, vectors, config, support):
    """Propose one deterministic median-marker seeded spherical Lloyd split.

    Median includes all observed reliable families, including single occurrences.
    Seeds initialize centers, without cannot-links, anchors or forced noise.
    Unsupported/collapsed groups are reported, never reseeded or retried.
    """
    import numpy as np
    by_family = defaultdict(list)
    for i in members:
        for family, values in evidence['calls'].get(ids[i], {}).items():
            # A same-contig multicopy family cannot seed separate genomes.
            if len(values) == 1 and values[0] >= config['seed_reliability']:
                by_family[family].append((i, values[0]))
    counts = sorted(len(v) for v in by_family.values())
    k = counts[len(counts)//2] if counts else 0
    trace = dict(k=k, observed_family_counts={f: len(v) for f, v in sorted(by_family.items())})
    if k < 2 or sum(len(v) >= k for v in by_family.values()) < config['min_seed_families']:
        return None, dict(trace, reason='insufficient_typical_multiplicity_or_independent_family_support')
    candidates = [f for f, v in by_family.items() if len(v) == k]
    family = min(candidates, key=lambda f: (-math.fsum(w for _, w in by_family[f])/k, f))
    seeds = sorted((i for i, _ in by_family[family]), key=lambda i: (-int(lengths[i]), ids[i]))
    centers = vectors[seeds].astype(np.float64).copy(); x = vectors[members].astype(np.float64)
    previous = None; groups = None
    for iteration in range(config['lloyd_iterations']):
        labels = np.argmax(x@centers.T, axis=1)
        groups = [[members[j] for j in np.flatnonzero(labels == b)] for b in range(k)]
        if any(not c for c in groups):
            return None, dict(trace, family=family, seed_ids=[ids[i] for i in seeds], reason='collapsed_child')
        if previous is not None and np.array_equal(labels, previous):
            break
        previous = labels.copy()
        for b, c in enumerate(groups):
            center = (vectors[c].astype(np.float64)*np.sqrt(lengths[c, None])).sum(0)
            norm = np.linalg.norm(center)
            if norm <= 1e-12:
                return None, dict(trace, family=family, reason='zero_child_center')
            centers[b] = center/norm
    supported = all(len(c) >= support['min_bin_contigs'] and int(lengths[c].sum()) >= support['min_bin_bp'] for c in groups)
    trace.update(family=family, seed_ids=[ids[i] for i in seeds], iterations=iteration+1,
                 child_bp=[int(lengths[c].sum()) for c in groups],
                 reason='supported' if supported else 'below_frozen_child_support')
    return (groups if supported else None), trace


def contexts(data):
    """Create raw diagnostic contexts; depth dispersion is between parent means only.

    Original native vectors are untouched. Composition uses Hellinger coordinates;
    depth uses log1p measured parent means divided by label-free column std.
    Zero-evidence depth rows and constant columns supply no depth support.
    """
    import numpy as np
    comp = np.sqrt(data['tnf'].astype(np.float64))
    depth = np.log1p(data['depth'].astype(np.float64)); eligible = data['eligible']
    scale = depth[eligible].std(0) if depth.shape[1] else np.empty(0)
    usable = scale > 1e-8
    depth = depth[:, usable]/scale[usable]
    return comp, depth, dict(depth_column_std=scale.tolist(), depth_usable_columns=usable.tolist(),
                            depth='log1p measured parent means / eligible-population column std; no window/per-base variance',
                            composition='sqrt retained TNF; Hellinger coordinates')


def centroid_context(members, groups, noise, x, lengths, mask=None, cosine=False):
    """Score length-weighted leave-one-out centroid silhouettes in O(n*k*d).

    Native unit vectors use cosine distance. Other contexts use squared Euclidean
    distance. Missing context contributes zero, unassigned DNA minus one, all with
    the full parent bp denominator. This is a geometric heuristic, not a test of
    measured coverage variance or a calibrated statistical silhouette.
    """
    import numpy as np
    require(x.ndim == 2 and np.isfinite(x).all(), 'Malformed context coordinates')
    if x.shape[1] == 0:
        return dict(score=0., available=False, informative_bp=0, noise_bp=int(lengths[noise].sum()))
    mask = np.ones(len(x), bool) if mask is None else np.asarray(mask, bool)
    centers, sums, masses = [], [], []
    for c in groups:
        selected = [i for i in c if mask[i]]; mass = float(lengths[selected].sum())
        value = (x[selected]*lengths[selected, None]).sum(0) if selected else np.zeros(x.shape[1])
        sums.append(value); masses.append(mass); centers.append(value/mass if mass else np.zeros(x.shape[1]))
    centers = np.array(centers); total = -float(lengths[noise].sum()); informative = 0
    for b, c in enumerate(groups):
        selected = [i for i in c if mask[i] and masses[b] > lengths[i]]
        if not selected or any(masses[j] <= 0 for j in range(len(groups)) if j != b):
            continue
        values = x[selected]; loo = (sums[b]-values*lengths[selected, None])/(masses[b]-lengths[selected, None])
        others = np.delete(centers, b, axis=0)
        if cosine:
            own_norm = np.linalg.norm(loo, axis=1); other_norm = np.linalg.norm(others, axis=1)
            a = 1-np.clip((values*loo).sum(1)/np.maximum(own_norm, 1e-12), -1, 1)
            d = 1-np.clip(values@others.T/np.maximum(other_norm, 1e-12), -1, 1)
        else:
            a = ((values-loo)**2).sum(1)
            d = ((values[:, None, :]-others[None, :, :])**2).sum(2)
        near = d.min(1); denominator = np.maximum(a, near)
        silhouette = np.divide(near-a, denominator, out=np.zeros_like(a), where=denominator > 1e-12)
        total += float(lengths[selected]@silhouette); informative += int(lengths[selected].sum())
    return dict(score=total/int(lengths[members].sum()), available=informative > 0,
                informative_bp=informative, noise_bp=int(lengths[noise].sum()))


def assess(members, groups, noise, evidence, ids, lengths, vectors, comp, depth, data, config):
    """Assess a whole alternative using marker quality and two supporting contexts."""
    flat = [i for c in groups for i in c]+noise
    require(len(groups) >= 2 and all(groups) and len(flat) == len(set(flat))
            and set(flat) == set(members), 'Malformed whole-parent alternative')
    parent = quality(members, evidence, ids, config)
    children = [quality(c, evidence, ids, config) for c in groups]
    mass = int(lengths[members].sum()); unassigned = int(lengths[noise].sum())
    # Noise retains its parent's score: dropping DNA alone provides no free gain.
    score = (math.fsum(int(lengths[c].sum())*q['score'] for c, q in zip(groups, children))
             + unassigned*parent['score'])/mass
    tolerance = 8*math.ulp(max(1., abs(parent['score']), abs(score)))
    context = dict(embedding=centroid_context(members, groups, noise, vectors, lengths, cosine=True),
                   composition=centroid_context(members, groups, noise, comp, lengths, data['valid_fourmers'] > 0),
                   depth=centroid_context(members, groups, noise, depth, lengths, data['depth_evidence']))
    eps = config['context_epsilon']
    eligible = (score-parent['score'] > tolerance and context['embedding']['score'] > eps
                and max(context['composition']['score'], context['depth']['score']) > eps)
    return dict(parent=parent, children=children, parent_bp=mass, assigned_bp=mass-unassigned,
                noise_bp=unassigned, weighted_quality=score, quality_gain=score-parent['score'],
                numerical_tolerance=tolerance, context=context, eligible=eligible)


def refine(pre, old_post, data, vectors, evidence, old_proposals, config, support):
    """Select parent, retained children or one new median-seeded proposal per parent.

    No merging, new assignment of prior noise or DNA deletion occurs. All
    alternatives and their quality/context evidence survive for cheap inspection.
    """
    import numpy as np
    from dl_binner.candidate.grouping import canonical_partition
    ids, lengths = data['ids'].tolist(), data['lengths']
    require(pre['ids'] == ids and pre['valid'] == old_post['valid']
            and vectors.shape == (len(ids), support['output']) and np.isfinite(vectors).all(), 'Refinement input axes differ')
    valid = np.array(pre['valid'], bool)
    require(np.allclose(np.linalg.norm(vectors[valid], axis=1), 1, atol=1e-5)
            and not np.any(vectors[~valid]), 'Original unit vectors required')
    comp, depth, transforms = contexts(data); parents = defaultdict(list)
    for i, b in enumerate(pre['assignment']):
        if b >= 0: parents[b].append(i)
    accepted, reasons, decisions, proposals = [], list(pre['reason']), [], []
    for p, members in sorted(parents.items()):
        candidates = []; generated, trace = seed_proposal(members, evidence, ids, lengths, vectors, config, support)
        if p in old_proposals:
            v = old_proposals[p]
            candidates.append(dict(route='retained', groups=v['groups'], noise=v['noise']))
        if generated is not None:
            candidates.append(dict(route='median_seeded', groups=generated, noise=[]))
        for v in candidates:
            flat = [i for c in v['groups'] for i in c]+v['noise']
            require(len(flat) == len(set(flat)) and set(flat) == set(members), 'Candidate lost/duplicated/cross-parent DNA')
            v['assessment'] = assess(members, v['groups'], v['noise'], evidence, ids, lengths, vectors, comp, depth, data, config)
        eligible = [v for v in candidates if v['assessment']['eligible']]
        winner = None
        for v in eligible:  # Retained route wins numerical ties unless retention/support improves.
            if winner is None:
                winner = v; continue
            a, b = v['assessment'], winner['assessment']
            tol = max(a['numerical_tolerance'], b['numerical_tolerance'])
            if a['weighted_quality'] > b['weighted_quality']+tol or (abs(a['weighted_quality']-b['weighted_quality']) <= tol
                and (a['assigned_bp'], -len(v['groups'])) > (b['assigned_bp'], -len(winner['groups']))):
                winner = v
        if winner:
            accepted.extend(winner['groups'])
            for i in winner['noise']:
                reasons[i] = old_post['reason'][i]
        else:
            accepted.append(members)
        if candidates or trace['k'] >= 2 or p in old_proposals:
            proposals.append(dict(pre_bin=p, seed_trace=trace, alternatives=candidates))
            decisions.append(dict(pre_bin=p, selected=winner['route'] if winner else 'parent',
                                  alternatives=[dict(route=v['route'], **v['assessment']) for v in candidates]))
    result = canonical_partition(ids, pre['valid'], accepted, lengths, support, reasons)
    result.update(neighbors=pre['neighbors'], parent_features_sha256=pre['parent_features_sha256'],
                  graph_sha256=pre['graph_sha256'], embedding_sha256=pre['embedding_sha256'],
                  algorithm='quality-aware marker refinement / frozen CPM parent', config=support,
                  refinement_config=config, scientific_quality_assessed=False)
    return result, decisions, proposals, transforms
