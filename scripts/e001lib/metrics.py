"""E001's conservative fixed-population endpoint and neighborhood probe."""

from collections import Counter, defaultdict
from fractions import Fraction

import numpy as np

from .records import config, require


def score(population, assignments):
    cfg = config()
    lengths, unique, genomes = (population[k] for k in ("lengths", "unique_origins", "genomes"))
    require(set(assignments) <= set(lengths), "Unknown predicted IDs")
    require(set(unique) <= set(lengths), "Unknown conservative truth IDs")
    require(len(genomes) == len(set(genomes)) and genomes, "Empty/duplicate genome population")
    totals, bin_bp, overlap = Counter(), Counter(), Counter()
    genome_ids = defaultdict(list)
    for seq, genome in unique.items():
        totals[genome] += lengths[seq]
        genome_ids[genome].append(seq)
    require(all(totals[g] >= cfg["min_genome_bp"] for g in genomes), "Invalid fixed genome population")
    for seq, bin_id in assignments.items():
        bin_bp[bin_id] += lengths[seq]
        if seq in unique:
            overlap[(bin_id, unique[seq])] += lengths[seq]
    candidates = defaultdict(list)
    threshold = Fraction(str(cfg["min_purity"]))
    for (bin_id, genome), bp in overlap.items():
        if bin_bp[bin_id] >= cfg["min_bin_bp"] and bp * threshold.denominator >= bin_bp[bin_id] * threshold.numerator:
            candidates[genome].append((bp, bin_id))
    values = {}
    for genome in genomes:
        best = sorted(candidates[genome], key=lambda pair: (-pair[0], pair[1]))
        tp, bin_id = best[0] if best else (0, None)
        strata = []
        boundaries = cfg["length_boundaries_bp"]
        for i, lower in enumerate(boundaries):
            upper = boundaries[i + 1] if i + 1 < len(boundaries) else None
            ids = [s for s in genome_ids[genome] if lower <= lengths[s] and (upper is None or lengths[s] < upper)]
            denominator = sum(lengths[s] for s in ids)
            recovered = sum(lengths[s] for s in ids if bin_id is not None and assignments.get(s) == bin_id)
            strata.append({"lower_bp": lower, "upper_bp": upper, "total_bp": denominator, "recovered_bp": recovered,
                           "recovery": recovered / denominator if denominator else None})
        values[genome] = {"total_bp": totals[genome], "recovered_bp": tp, "r95": tp / totals[genome],
                          "bin": bin_id, "bin_bp": bin_bp[bin_id] if bin_id is not None else None,
                          "confirmed_purity": tp / bin_bp[bin_id] if bin_id is not None else None,
                          "length_strata": strata}
    return {"r95": sum(r["r95"] for r in values.values()) / len(genomes),
            "r95_base_weighted": sum(r["recovered_bp"] for r in values.values()) / sum(totals[g] for g in genomes),
            "inclusive_recovered_counts": {str(t): sum(Fraction(r["recovered_bp"], r["total_bp"]) >= Fraction(str(t)) for r in values.values()) for t in cfg["recovery_thresholds"]},
            "assigned_bp": sum(bin_bp.values()), "unassigned_bp": sum(lengths.values()) - sum(bin_bp.values()),
            "ambiguous_or_unscored_assigned_bp": sum(lengths[s] for s in assignments if s not in unique),
            "per_genome": values}


def neighbor_purity(ids, features, population, k=None, batch_size=64):
    """Exact cosine neighbors; lexicographic ID tie break, labels used only for scoring."""
    k = config()["probe_k"] if k is None else k
    require(len(ids) == len(set(ids)), "Duplicate feature IDs")
    require(set(ids) <= set(population["lengths"]), "Unknown feature IDs")
    x = np.asarray(features, dtype=np.float64)
    require(x.ndim == 2 and len(x) == len(ids) and x.shape[1] > 0 and np.isfinite(x).all(), "Invalid feature matrix")
    require(k >= 1 and batch_size >= 1, "Invalid probe settings")
    index = {s: i for i, s in enumerate(ids)}
    norms = np.linalg.norm(x, axis=1)
    pool = sorted(s for s in population["probe_pool"] if s in index and norms[index[s]] > 0)
    reference = x[[index[s] for s in pool]]
    if pool:
        reference /= norms[[index[s] for s in pool], None]
    queries = population["probe_queries"]
    results = {}
    eligible_queries = []
    for s in queries:
        if s not in index:
            results[s] = {"status": "filtered", "purity": None}
        elif norms[index[s]] == 0:
            results[s] = {"status": "zero_row", "purity": None}
        elif len(pool) - (s in pool) < k:
            results[s] = {"status": "insufficient_neighbors", "purity": None}
        else:
            eligible_queries.append(s)
    pool_index = {s: i for i, s in enumerate(pool)}
    for start in range(0, len(eligible_queries), batch_size):
        query_ids = eligible_queries[start:start + batch_size]
        q = x[[index[s] for s in query_ids]] / norms[[index[s] for s in query_ids], None]
        similarities = q @ reference.T
        for seq, similarities_row in zip(query_ids, similarities):
            if seq in pool_index:
                similarities_row[pool_index[seq]] = -np.inf
            # Stable sorting over the ID-sorted pool gives a reproducible tie rule.
            neighbors = [pool[i] for i in np.argsort(-similarities_row, kind="stable")[:k]]
            purity = sum(population["unique_origins"][s] == population["unique_origins"][seq] for s in neighbors) / k
            results[seq] = {"status": "scored", "purity": purity, "neighbors": neighbors}
    return results
