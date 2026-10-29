"""One newly admitted custom-score core index with persisted exact recall gates.

The old native graph is an immutable initializer, never rebuilt. A changed score
and target-core population need new retrieval. Arrays are numeric; full opaque
axes are external byte-bound features, not duplicated giant Unicode matrices.
"""
import time
from pathlib import Path

import numpy as np

from ..information.grouping import ordered_sample, require
from ..io import emit, write_json
from .arrays import save
from .fusion import index_metric


class CoreIndex:
    """Actual compiled NNDescent or bounded exact crossover for the same score."""
    def __init__(self, model, data, valid, original, threads=4, force_native=False):
        require(type(threads) is int and 1 <= threads <= 4, 'Four numerical thread contract')
        self.model = model; self.cfg = model.cfg
        self.cores = np.array(sorted(np.flatnonzero(valid & (data['lengths'] >= self.cfg['core_min_bp'])),
                                    key=lambda i: str(data['ids'][i])), np.int64)
        self.native = None
        self.x = model.packed(self.cores)
        if len(self.cores) > self.cfg['exact_threshold'] or (force_native and len(self.cores) >= 3):
            import numba
            from pynndescent import NNDescent
            numba.set_num_threads(threads)
            n = len(self.cores); width = min(n, self.cfg['discovery_neighbors'])
            inverse = np.full(len(valid), -1, np.int64); inverse[self.cores] = np.arange(n)
            init = np.full((n, width), -1, np.int32)
            for local, i in enumerate(self.cores):
                old = original['neighbors'][i]; old = old[old >= 0]
                values = inverse[old]; values = values[(values >= 0) & (values != local)]
                values = np.r_[local, values][:width]
                require(len(np.unique(values)) == len(values), 'Duplicate retained initial neighbour')
                init[local, :len(values)] = values
            emit('calibrated_index_start', rows=n, dimensions=self.x.shape[1], threads=threads)
            self.native = NNDescent(self.x, metric=index_metric, metric_kwds=model.metric_args(),
                n_neighbors=width, init_graph=init, tree_init=False, random_state=self.cfg['seed'],
                n_jobs=threads, low_memory=True, max_candidates=self.cfg['max_candidates'],
                n_iters=self.cfg['index_iterations'], delta=self.cfg['index_delta'],
                # 0.5.13 parallel query seeds mix int32/int64 heap indices on
                # this pinned runtime. Its actual serial query path is tested;
                # construction still uses four workers. Do not patch libraries.
                parallel_batch_queries=False, verbose=True)

    def query(self, rows):
        """Return core-local candidates; public query/pickle is tested on real fixtures."""
        width = min(len(self.cores), self.cfg['discovery_neighbors'])
        if self.native is None:
            return np.tile(np.arange(len(self.cores)), (len(rows), 1))
        return self.native.query(self.model.packed(rows), k=width,
                                 epsilon=self.cfg['query_epsilon'])[0]


def query_strata(data, valid, cores, model):
    """Freeze hash samples before discovery, without source/length outcome routing."""
    ids = data['ids'].tolist(); cfg = model.cfg
    is_core = np.zeros(len(valid), bool); is_core[cores] = True
    result = dict(all=ordered_sample(ids, np.flatnonzero(valid), cfg['audit_queries']).tolist())
    for c in [True, False]:
        for p in [True, False]:
            mask = valid & (is_core == c) & (model.positive == p)
            key = ('core' if c else 'noncore')+'_'+('positive' if p else 'zero')
            result[key] = ordered_sample(ids, np.flatnonzero(mask), cfg['audit_stratum_queries']).tolist()
    return result


def retrieve(model, data, valid, original, output, threads=4, force_native=False):
    """Persist proposals, per-channel evidence and numeric answers before refusal.

    Neighbours are core-local indices, queries are original full-axis rows. A
    query that is itself a core never returns itself. Small core sets use -1
    padding and an explicit row count, rather than fabricated self neighbours.
    """
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    cfg = model.cfg; ids = data['ids']
    index = CoreIndex(model, data, valid, original, threads, force_native)
    cores = index.cores; n = len(cores)
    queries = np.array(sorted(np.flatnonzero(valid), key=lambda i: str(ids[i])), np.int64)
    inverse = np.full(len(valid), -1, np.int64); inverse[cores] = np.arange(n)
    k = min(cfg['neighbors'], n)
    near = np.full((len(queries), k), -1, np.int32)
    dd = np.full((len(queries), k), -1., np.float64)
    ranks = np.full((len(queries), k, 3), .5, np.float32)
    masks = np.zeros((len(queries), k, 3), bool)
    counts = np.zeros(len(queries), np.int32)
    proposals = np.full((len(queries), min(n, cfg['discovery_neighbors'])), -1, np.int32)
    strata = query_strata(data, valid, cores, model)
    audit_rows = set(sum(strata.values(), [])); answers = {}; last = time.monotonic()
    for start in range(0, len(queries), cfg['batch_rows']):
        rows = queries[start:start+cfg['batch_rows']]
        proposed = index.query(rows)
        require(proposed.ndim == 2 and proposed.shape[0] == len(rows), 'Malformed core proposals')
        for off, i in enumerate(rows):
            at = start+off; values = proposed[off]
            require(((values >= 0) & (values < n)).all(), 'Missing/out-of-axis core proposal; no fallback')
            proposals[at, :len(values)] = values
            old = original['neighbors'][i]; old = old[old >= 0]
            old = inverse[old]; old = old[old >= 0]
            pool = np.unique(np.r_[values, old]); pool = pool[cores[pool] != i]
            wanted = min(cfg['neighbors'], n-int(inverse[i] >= 0))
            require(len(pool) >= wanted, 'Insufficient calibrated core candidates; no widening')
            distance, q, available = model.distances(i, cores[pool], True)
            order = np.lexsort((ids[cores[pool]], distance))[:wanted]
            counts[at] = wanted
            near[at, :wanted], dd[at, :wanted] = pool[order], distance[order]
            ranks[at, :wanted], masks[at, :wanted] = q[order], available[order]
            if int(i) in audit_rows:
                all_other = cores[cores != i]
                exact = model.distances(i, all_other)
                best = np.lexsort((ids[all_other], exact))[:wanted]
                threshold = float(exact[best[-1]]) if wanted else 0.
                recall = float(np.mean(distance[order] <= threshold+cfg['tie_tolerance'])) if wanted else 1.
                answers[int(i)] = dict(id=str(ids[i]), full_row=int(i), recall=recall,
                    exact_ids=ids[all_other[best]].tolist(), exact_distances=exact[best].tolist(),
                    returned_ids=ids[cores[pool[order]]].tolist(), returned_distances=distance[order].tolist(),
                    kth_exact_distance=threshold)
        if time.monotonic()-last >= 5 or start+len(rows) == len(queries):
            emit('calibrated_query_progress', rows=start+len(rows), total=len(queries)); last = time.monotonic()
    reports = {key: dict(rows=rows, queries=[answers[i] for i in rows],
                         mean_recall=float(np.mean([answers[i]['recall'] for i in rows])) if rows else None)
               for key, rows in strata.items()}
    passed = all(v['mean_recall'] is None or v['mean_recall'] >= cfg['min_neighbor_recall'] for v in reports.values())
    audit = dict(status='PASS' if passed else 'FAILED_RECALL_GATE', cfg=cfg, strata=reports,
        native_custom_index=index.native is not None, target_population='valid parents at least 2500 bp',
        old_native_index_rebuilt=False, new_score_and_target_index=True,
        guarantee='Tie-aware exact sampled core-population recall; not biological homogeneity or exhaustive recall',
        rank_trace_precision='float32 diagnostic ranks; final distance/audit float64',
        query_rows=len(queries), core_rows=n)
    arrays = dict(queries=queries, cores=cores, neighbors=near, distances=dd,
                  counts=counts, channel_ranks=ranks, channel_available=masks, proposals=proposals)
    save(output/'neighbors.npz', arrays, dict(kind='calibrated_core_neighbors', audit=audit), ids)
    write_json(output/'audit.json', audit)
    require(passed, 'Calibrated score recall below frozen 0.90; numeric evidence retained; no automatic widening')
    return arrays, audit
