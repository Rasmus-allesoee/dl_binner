"""Reliable-core forests, soft biological alternatives and one-pass recruitment.

All choices are label free. Marker breadth/excess and rank coherence are proxies,
not calibrated genome quality. Cached physical loci remain separate; no genome K,
taxonomy, truth, encoder, detector or accepted index construction is reachable.
"""
from collections import defaultdict
import math

import numpy as np

from ..candidate.grouping import canonical_partition
from ..density import grouping as density
from ..information.grouping import require


def reliable_forest(data, model, retrieval):
    """Build a sparse MST only from reciprocal links with distinct channel support.

    Missing/neutral evidence never votes. Isolated cores remain explicit forest
    roots. Mutual reachability uses the farthest available accepted top-10 edge
    when fewer than ten pass, without fabricated padded neighbours.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import minimum_spanning_tree
    cores = retrieval['cores']; n = len(cores); cfg = model.cfg
    lookup = np.full(len(data['ids']), -1, np.int64)
    lookup[retrieval['queries']] = np.arange(len(retrieval['queries']))
    left, right, distance = [], [], []
    for i, full in enumerate(cores):
        at = lookup[full]; count = min(cfg['core_degree'], int(retrieval['counts'][at]))
        near = retrieval['neighbors'][at, :count]
        good = model.agreement(full, cores[near])
        for j, d in zip(near[good], retrieval['distances'][at, :count][good]):
            left.append(i); right.append(int(j)); distance.append(float(d))
    left, right, distance = np.array(left, np.int64), np.array(right, np.int64), np.array(distance)
    key = left*n+right; order = np.argsort(key); sorted_key = key[order]
    reverse = np.searchsorted(sorted_key, right*n+left)
    reciprocal = np.zeros(len(left), bool)
    valid = reverse < len(key)
    reciprocal[valid] = sorted_key[reverse[valid]] == (right*n+left)[valid]
    keep = reciprocal & (left < right)
    left, right, distance = left[keep], right[keep], distance[keep]
    core = np.zeros(n)
    np.maximum.at(core, left, distance); np.maximum.at(core, right, distance)
    weights = np.maximum(np.maximum(core[left], core[right]), distance)
    graph = coo_matrix((np.r_[weights, weights], (np.r_[left, right], np.r_[right, left])), shape=(n, n)).tocsr()
    mst = minimum_spanning_tree(graph).tocoo()
    size = max(1, 2*n); parent = np.arange(size); top = np.arange(n)
    children = np.full((size, 2), -1, np.int64)
    mass = np.zeros(size, np.int64); count = np.zeros(size, np.int64); level = np.zeros(size)
    mass[:n] = data['lengths'][cores]; count[:n] = 1
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = int(parent[i])
        return i
    at = n
    for e in np.lexsort((mst.col, mst.row, mst.data)):
        a, b = find(int(mst.row[e])), find(int(mst.col[e]))
        if a == b:
            continue
        x, y = sorted((int(top[a]), int(top[b])))
        children[at] = x, y; mass[at] = mass[x]+mass[y]; count[at] = count[x]+count[y]
        level[at] = mst.data[e]; parent[b] = a; top[a] = at; at += 1
    roots = sorted({int(top[find(i)]) for i in range(n)})
    tree = dict(children=children[:at], mass=mass[:at], count=count[:at], level=level[:at],
        roots=np.array(roots, np.int64), core=core,
        mst_edges=np.column_stack((mst.row, mst.col)).astype(np.int64), mst_distances=mst.data)
    edge = dict(left=left, right=right, distances=distance, weights=weights)
    return tree, edge


def marker_maps(ids, evidence):
    """Validate cached physical weights without redetection or cross-contig collapse."""
    require(type(evidence.get('panel_size')) is int and evidence['panel_size'] > 0
            and isinstance(evidence.get('calls'), dict) and set(evidence['calls']) <= set(ids),
            'Malformed/unknown cached marker axis')
    result = []
    for q in ids:
        values = evidence['calls'].get(q, {})
        require(isinstance(values, dict) and all(isinstance(f, str) and isinstance(v, list) and v
            and all(type(x) in (int, float) and math.isfinite(x) and 0 <= x <= 1 for x in v)
            for f, v in values.items()), 'Malformed physical marker weights')
        result.append({f: (math.fsum(v), max(v)) for f, v in values.items()})
    return result


def biological_utilities(tree, cores, data, model, evidence):
    """Compute O(n*d) exact weighted pair moments and soft marker quality per node.

    Mean pair distance followed by rank calibration is a declared coherence proxy,
    not mean calibrated pair similarity. Ordered distinct-pair denominators remove
    self pairs and distinguish co-absence from measured positive contrasts.
    """
    n, size = len(cores), len(tree['mass']); cfg = model.cfg
    dims = [x.shape[1] for x in model.channels]; ends = np.r_[0, np.cumsum(dims)]
    total = np.zeros((size, int(ends[-1])), np.float64)
    norm2 = np.zeros((size, 3)); obs_w = np.zeros((size, 3)); obs_w2 = np.zeros((size, 3))
    squared_w = np.zeros(size); rel = np.zeros(size); rel2 = np.zeros(size)
    zero_w = np.zeros(size); zero_w2 = np.zeros(size)
    w = data['lengths'][cores].astype(np.float64)
    squared_w[:n] = w*w
    r = np.sqrt(w/(w+cfg['length_scale_bp']))
    rel[:n] = w*r; rel2[:n] = w*w*r*r
    for c, x in enumerate(model.channels):
        available = model.available[cores, c]
        value = x[cores].astype(np.float64)
        weight = w*available
        total[:n, ends[c]:ends[c+1]] = value*weight[:, None]
        norm2[:n, c] = (value*value).sum(1)*weight
        obs_w[:n, c] = weight; obs_w2[:n, c] = weight*weight
    z = model.available[cores, 2] & ~model.positive[cores]
    zero_w[:n] = w*z; zero_w2[:n] = w*w*z
    core_ids = data['ids'][cores].tolist(); core_axis = set(core_ids)
    physical = dict(evidence, calls={q: v for q, v in evidence['calls'].items() if q in core_axis})
    by_node = {i: v for i, v in enumerate(marker_maps(core_ids, physical))}
    coherence = np.zeros(size); breadth = np.zeros(size); excess = np.zeros(size)
    utility = np.zeros(size); panel = evidence['panel_size']
    for node in range(size):
        if node >= n:
            a, b = map(int, tree['children'][node])
            for array in [total, norm2, obs_w, obs_w2, squared_w, rel, rel2, zero_w, zero_w2]:
                array[node] = array[a]+array[b]
            x, y = by_node.pop(a), by_node.pop(b)
            if len(x) < len(y):
                x, y = y, x
            for f, (s, m) in y.items():
                previous = x.get(f, (0., 0.)); x[f] = previous[0]+s, max(previous[1], m)
            by_node[node] = x
        values = by_node[node]
        breadth[node] = math.fsum(v[1] for v in values.values())/panel
        excess[node] = max(0., math.fsum(v[0]-v[1] for v in values.values())/panel)
        mass = float(tree['mass'][node]); pair_w = mass*mass-squared_w[node]
        q = np.full(3, .5)
        if pair_w > 0:
            length_reliability = max(0., min(1., (rel[node]**2-rel2[node])/pair_w))
            for c in range(3):
                observed_pair_w = obs_w[node, c]**2-obs_w2[node, c]
                if c == 2:
                    observed_pair_w -= zero_w[node]**2-zero_w2[node]
                if not model.active[c] or observed_pair_w <= 0:
                    continue
                sums = total[node, ends[c]:ends[c+1]]
                value = max(0., 2*(obs_w[node, c]*norm2[node, c]-float(sums@sums))/observed_pair_w)
                rank = float(np.interp(value, model.knot_x[c, :model.counts[c]], model.knot_y[c, :model.counts[c]]))
                fraction = min(1., observed_pair_w/pair_w)
                if c > 0:
                    fraction *= length_reliability
                q[c] = .5+fraction*(rank-.5)
            coherence[node] = 1-float(q[model.active].mean()) if model.active.any() else .5
        utility[node] = mass*max(coherence[node]-.5, 0)*(1+breadth[node])/(1+cfg['marker_excess_penalty']*excess[node])
    return dict(coherence=coherence, breadth=breadth, excess=excess, utility=utility)


def select(tree, branches, quality, cfg):
    """Choose one disjoint biological antichain; protect whole-parent numerical ties."""
    best = np.zeros(len(branches)); decisions = [None]*len(branches)
    for cid in range(len(branches)-1, -1, -1):
        branch = branches[cid]; node = branch['node']
        own = float(quality['utility'][node]); child = float(sum(best[j] for j in branch['children']))
        choose = own > 0 and child <= own*(1+cfg['child_improvement_fraction'])
        best[cid] = own if choose else child
        decisions[cid] = dict(candidate=cid, node=node, parent_selected=choose,
            own_utility=own, child_utility=child, coherence=float(quality['coherence'][node]),
            marker_breadth=float(quality['breadth'][node]), marker_excess=float(quality['excess'][node]))
    kept = []; stack = [i for i, c in enumerate(branches) if c['parent'] < 0]
    while stack:
        cid = stack.pop()
        if decisions[cid]['parent_selected']:
            kept.append(branches[cid]['node'])
        else:
            stack.extend(branches[cid]['children'])
    return kept, decisions


def recruit(pre, retrieval, model, data, evidence):
    """One non-propagating pass with complete votes, reasons and accumulated marker cap.

    Unselected supporting cores contribute to the vote denominator as uncertainty.
    Recruits never become geometric anchors. Reliable-copy excess is a soft panel
    proxy and a conservative recruitment guard, not measured contamination.
    """
    ids, lengths, cfg = data['ids'].tolist(), data['lengths'], model.cfg
    labels = np.asarray(pre['assignment']); cores = retrieval['cores']
    groups = [[int(i) for i in np.flatnonzero(labels == b)] for b in range(pre['clusters'])]
    reliable = []
    for q in ids:
        reliable.append({f: (math.fsum(x for x in v if x >= cfg['reliable_marker_weight']),
                             max([x for x in v if x >= cfg['reliable_marker_weight']], default=0.))
                         for f, v in evidence['calls'].get(q, {}).items()})
    bins = [defaultdict(lambda: (0., 0.)) for _ in groups]
    for b, rows in enumerate(groups):
        for i in rows:
            for f, (s, m) in reliable[i].items():
                old = bins[b][f]; bins[b][f] = old[0]+s, max(old[1], m)
    new_excess = np.zeros(len(groups)); requests = []; trace = []; reasons = list(pre['reason'])
    for at, i in enumerate(retrieval['queries']):
        if labels[i] >= 0:
            continue
        count = int(retrieval['counts'][at]); local = retrieval['neighbors'][at, :count]
        full = cores[local]
        good = model.agreement(i, full)
        full = full[good]; distance = retrieval['distances'][at, :count][good]
        weight = 1-distance; denominator = float(weight.sum())
        votes = defaultdict(float); support = defaultdict(int)
        for j, w in zip(full, weight):
            if labels[j] >= 0:
                b = int(labels[j]); votes[b] += float(w); support[b] += 1
        order = sorted(votes, key=lambda b: (-votes[b], b))
        best = order[0] if order else -1
        fraction = votes[best]/denominator if denominator and best >= 0 else 0.
        runner = votes[order[1]] if len(order) > 1 else 0.
        margin = votes[best]/runner if runner else (1e300 if best >= 0 else 0.)
        reason = ('insufficient_distinct_core_support' if best < 0 or support[best] < cfg['recruit_min_support']
                  else 'ambiguous_core_votes' if fraction < cfg['recruit_vote_fraction'] or margin < cfg['recruit_margin_ratio']
                  else 'pending_marker_guard')
        record = dict(id=ids[i], full_row=int(i), best_core_bin=best, vote_fraction=fraction,
            margin_ratio=margin, votes={str(b): dict(weight=votes[b], support=support[b]) for b in order},
            accepted_core_neighbors=full.tolist(), reason=reason)
        if reason == 'pending_marker_guard':
            requests.append((-margin, -support[best], ids[i], int(i), best, record))
        else:
            reasons[i] = reason; trace.append(record)
    for _, _, _, i, b, record in sorted(requests):
        delta = 0.
        for f, (s, m) in reliable[i].items():
            old = bins[b].get(f, (0., 0.))
            delta += max(0., old[0]+s-max(old[1], m))-(old[0]-old[1])
        delta = max(0., delta)/evidence['panel_size']
        record['incremental_reliable_marker_excess'] = delta
        if new_excess[b]+delta <= cfg['recruit_new_excess_fraction']+1e-12:
            groups[b].append(i); reasons[i] = 'supported_fixed_core_recruitment'
            new_excess[b] += delta
            for f, (s, m) in reliable[i].items():
                old = bins[b].get(f, (0., 0.)); bins[b][f] = old[0]+s, max(old[1], m)
        else:
            reasons[i] = 'accumulated_reliable_marker_excess_guard'
        record['reason'] = reasons[i]; trace.append(record)
    result = canonical_partition(ids, pre['valid'], groups, lengths, cfg, reasons)
    for i, b in enumerate(result['assignment']):
        if b >= 0:
            result['reason'][i] = reasons[i]
    result['core_bin_to_final_bin'] = [int(result['assignment'][group[0]]) for group in groups]
    for row in trace:
        row['final_bin'] = int(result['assignment'][row['full_row']])
    return result, sorted(trace, key=lambda r: r['full_row'])


def construct(data, valid, model, retrieval, evidence):
    """Return all new cached alternatives and complete core/final DNA partitions."""
    marker_maps(data['ids'].tolist(), evidence)
    tree, edge = reliable_forest(data, model, retrieval)
    cores = retrieval['cores']; n = len(cores)
    branches = density.condense(tree, data['lengths'][cores], model.cfg)
    quality = biological_utilities(tree, cores, data, model, evidence)
    nodes, decisions = select(tree, branches, quality, model.cfg)
    groups = [[int(cores[i]) for i in density.leaves(tree, node, n)] for node in nodes]
    reasons = ['outside_learning_eligibility' if not v else 'no_supported_biological_core' for v in valid]
    core = canonical_partition(data['ids'].tolist(), valid, groups, data['lengths'], model.cfg, reasons)
    core['core_bin_to_final_bin'] = list(range(core['clusters']))
    for i, b in enumerate(core['assignment']):
        if b >= 0:
            core['reason'][i] = 'selected_reliable_biological_core'
    final, votes = recruit(core, retrieval, model, data, evidence)
    return dict(core=core, recruited=final), tree, edge, quality, branches, decisions, votes
