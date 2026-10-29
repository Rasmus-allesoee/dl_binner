#!/usr/bin/env python3
"""Synthetic full-width index/query planning probe; no community or truth input.

The forecast extrapolates measured construction/query separately with conservative
headroom. It is not full-scale affordability or biological/retrieval admission.
Native execution repeats this small changed-runtime gate, not accepted science.
"""
import argparse
import json
import math
from pathlib import Path
import sys
import tempfile
import time

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import numpy as np
from dl_binner.calibrated.fusion import calibrate, policy
from dl_binner.calibrated.retrieval import CoreIndex
from e024_coverage import write


def probe(output):
    """Measure 4,096 synthetic parents, actual compiled construction and public queries."""
    cfg = policy(); n = 4096; rng = np.random.default_rng(11)
    x = rng.normal(size=(n, 64)).astype(np.float32); x /= np.linalg.norm(x, axis=1)[:, None]
    depth = rng.uniform(0, 30, (n, 10)).astype(np.float32); depth[::3] = 0
    data = dict(ids=np.array([f'opaque-{i:06}' for i in range(n)]), lengths=rng.integers(500, 18000, n),
        tnf=rng.dirichlet(np.ones(136), n).astype(np.float32), valid_fourmers=np.ones(n, np.int64),
        depth=depth, eligible=np.ones(n, bool))
    original = dict(neighbors=np.array([[(i+j)%n for j in range(1, 31)] for i in range(n)], np.int64))
    start = time.monotonic(); model = calibrate(data, x, data['eligible'], original, cfg)
    cal = time.monotonic()-start
    start = time.monotonic(); index = CoreIndex(model, data, data['eligible'], original, 4, True)
    build = time.monotonic()-start
    # First query includes lazy compile/search-graph setup, priced separately.
    start = time.monotonic(); index.query(np.arange(32)); setup = time.monotonic()-start
    start = time.monotonic()
    for i in range(0, n, cfg['batch_rows']): index.query(np.arange(i, min(i+cfg['batch_rows'], n)))
    query = time.monotonic()-start
    # Counts are sums over every origin/status stratum in old accepted reports,
    # not a new outcome/score or a selected subset. Native full axes verify them.
    axes = json.loads((ROOT/'experiments/E026-calibrated-evidence-fusion/protocol.json').read_text())['axes']
    build_upper = sum(build*(v['core_rows']/len(index.cores))*math.log2(v['core_rows'])/math.log2(len(index.cores))*3 for v in axes.values())
    query_upper = sum(query*(v['eligible']/n)*math.log2(v['core_rows'])/math.log2(len(index.cores))*3 for v in axes.values())
    remaining = build_upper+query_upper+cal*(sum(v['rows'] for v in axes.values())/n)*3+7200+setup
    result = dict(status='PASS', synthetic=True, parents=n, core_rows=len(index.cores), dimensions=index.x.shape[1],
        calibration_seconds=cal, index_build_seconds=build, lazy_query_setup_seconds=setup,
        full_probe_query_seconds=query, construction_threads=4, search_threads=1, full_axes=axes,
        build_upper_seconds=build_upper, query_upper_seconds=query_upper,
        planning_remaining_science_seconds=remaining,
        forecast='Threefold scale/log-size headroom plus two hours rerank/forest/export/audit/collection; not measured community time',
        required_future_actual_headroom_credit_and_complete_schedule_gate=True)
    write(output, result); return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); print(json.dumps(probe(a.output)), flush=True)
