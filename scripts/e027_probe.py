#!/usr/bin/env python3
"""Full-width synthetic model/runtime forecast, never a community fit or score.

Measures both declared encoders on batch256/five real-view-shaped inputs, actual
positive/reconstruction/backward/EMA work and bounded optional side constraints.
The complete serial forecast includes six fits, geometry/reload/graph/selection,
the single external reference and collection; allocation is priced separately.
"""
import argparse
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]


def probe(output):
    """Measure actual CPU arithmetic with four numerical threads and record headroom."""
    import numpy as np
    import torch
    from torch.nn import functional as F
    from dl_binner.unified.training import configuration
    from dl_binner.relational.model import initialize, signed_loss
    from dl_binner.multiview.positive import pair_loss, update_target
    from dl_binner.model import configure_torch
    from dl_binner.io import write_json
    configure_torch(4)
    times = {}
    for glm in [False, True]:
        cfg = configuration(glm); torch.manual_seed(11)
        model, target, heads = initialize(10, cfg)
        optimizer = torch.optim.AdamW(list(model.parameters())+list(heads.parameters()), lr=.001)
        batch = 256; n = 5*batch
        args = [F.normalize(torch.randn(n, 136), dim=1), torch.rand(n, 10), torch.arange(n) % 2 == 0,
                torch.rand(n, 8, 136), torch.rand(n, 8, 3), torch.ones(n, 8, dtype=torch.bool)]
        if glm: args += [torch.randn(n, 768), torch.rand(n, 2)]
        owner = torch.arange(batch).repeat(5); weights = torch.ones(batch)
        samples = []
        for step in range(5):
            start = time.monotonic(); model.train(); heads.train()
            z, sequence = model(*args)
            with torch.no_grad(): a, b = target(*args)
            loss = pair_loss(z, a, owner, weights, heads[0])+.5*pair_loss(sequence, b, owner, weights, heads[1])
            loss = loss+(model.composition_decoder(z)-args[0]).square().mean()+.1*(model.depth_decoder(z)-args[1]).square().mean()
            # Worst retained pair_batch256: two extra parent forwards and side loss.
            side = [x[:512] for x in args]
            with torch.random.fork_rng(devices=[]):
                online = [x.reshape(256, 2, -1) for x in model(*side)]
                with torch.no_grad(): stopped = [x.reshape(256, 2, -1) for x in target(*side)]
                for head in heads: head.eval()
                rp, rn = signed_loss(online, stopped, heads, torch.tensor([1, -1]*128, dtype=torch.int8), torch.ones(256), .2)
                for head in heads: head.train()
            loss = loss+.1*(rp+rn)
            optimizer.zero_grad(set_to_none=True); loss.backward(); optimizer.step(); update_target(model, target, .996)
            samples.append(time.monotonic()-start)
        times['GLM' if glm else 'noGLM'] = dict(seconds_per_full_batch=samples,
            planning_batch_seconds=max(samples[1:]), parameter_count=sum(p.numel() for p in model.parameters()),
            synthetic=True, actual_backward_EMA_predictors=True, max_side_pairs=256)
    counts = {'E009-noGLM': 89041, 'E009-GLM': 89041, 'oral-noGLM': 508763}
    fits = {u: math.ceil(n/256)*20*times['GLM' if u == 'E009-GLM' else 'noGLM']['planning_batch_seconds']*2*1.5
            for u, n in counts.items()}
    # Two fits/arm; side overhead included in both, 50% native throughput headroom.
    # Other work deliberately reserves 3h (including six learned and six joint
    # indices), not the former slow external-query projection.
    remaining = sum(fits.values())+3*3600
    result = dict(status='PASS' if remaining < 23*3600 else 'FAILED_COMPLETE_SCHEDULE_FORECAST',
        observations=times, six_fit_upper_seconds=fits, other_science_collection_reserve_seconds=10800,
        planning_remaining_science_seconds=remaining,
        formula='2 fits * ceil(parents/256) * 20 epochs * slowest warm batch * 1.5; plus 3h other work',
        limitation='Synthetic cache-free batch timing is a forecast, not native full-community stability/affordability proof')
    write_json(output, result)
    if result['status'] != 'PASS': raise TimeoutError('Complete frozen scientific schedule forecast exceeds prospective envelope; record a justified revision before release')
    return result


def graph_probe(output):
    """Exercise approximate 4,096-parent graded discovery in a graph-only process."""
    import numpy as np
    from dl_binner.unified.grouping import retrieve, policy
    from dl_binner.candidate.grouping import neighbor_graph
    from dl_binner.io import write_json
    rng = np.random.default_rng(11); n = 4096; cfg = policy()
    vectors = rng.normal(size=(n, 64)).astype(np.float32)
    vectors /= np.linalg.norm(vectors, axis=1)[:, None]
    ids = np.array([f'opaque-{i:06d}' for i in range(n)])
    depth = rng.uniform(0, 40, (n, 10)).astype(np.float32); depth[::3] = 0
    data = dict(ids=ids, lengths=rng.integers(500, 20000, n, dtype=np.int64),
        tnf=rng.dirichlet(np.ones(136), n).astype(np.float32), depth=depth, eligible=np.ones(n, bool))
    start = time.monotonic()
    nn, _, native = neighbor_graph(vectors, ids.tolist(), dict(cfg, audit_queries=32), 4)
    target = Path(output)
    _, _, _, graded = retrieve(data, vectors, data['eligible'], dict(neighbors=nn), cfg, 4,
                               target.parent/'synthetic-graph-arrays', force_native=True)
    write_json(target, dict(status='PASS', synthetic_parents=n, full_width=212,
        wall_seconds=time.monotonic()-start, native_unit_audit=native, graded_audit=graded,
        tensor_backend_loaded='torch' in sys.modules, community_science=False,
        limitation='Native approximate implementation/recall on this synthetic shape; full community audits still required'))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--graph-probe', action='store_true')
    a = p.parse_args()
    if a.graph_probe: graph_probe(a.output)
    else: print(json.dumps(probe(a.output)), flush=True)
