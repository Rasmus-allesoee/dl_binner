"""Generate bounded engineering DNA and fit the actual full-width context candidate.

No public/community sequences, origin labels or genome-quality metrics are read.
The reusable marker fixture exercises native Pyrodigal/PyHMMER separately from
Torch; source/installed stages are subprocesses so incompatible libraries stay
isolated. The two-epoch throughput is a planning observation, not scale proof.
"""
import argparse
import json
from pathlib import Path
import sys


def generate(root, parents=192, epochs=2, dna_profile='oligomer'):
    """Write diverse real DNA views, ordered synthetic parent means and tiny HMM."""
    import numpy as np
    from dl_binner.multiview.views import prepare, config as base_config
    from dl_binner.context.model import config
    from dl_binner.io import write_json
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    rng = np.random.default_rng(718)
    fasta, depth = root/'synthetic.fa', root/'synthetic-depth.tsv'
    rows = []
    words = np.array([''.join('ACGT'[(i >> shift) & 3] for shift in (6, 4, 2, 0)) for i in range(256)])
    for i in range(parents):
        n = 500+(i*37)%11000
        if dna_profile == 'gc_iid':
            probs = np.array([1+(i % 5), 2+(i % 3), 2+(i % 4), 1+(i % 7)], float)
            probs /= probs.sum()
            dna = ''.join(rng.choice(list('ACGT'), n, p=probs))
        else:
            # Many independent oligomer-frequency directions, instead of mostly
            # a three-parameter base-frequency surface. This is an engineering
            # positive control, not a simulated ecological community or truth.
            probs = rng.dirichlet(np.full(256, .3))
            dna = ''.join(rng.choice(words, (n+3)//4, p=probs))[:n]
        if i % 17 == 0:
            dna = dna[:len(dna)//2]+'N'*17+dna[len(dna)//2+17:]
        rows.append((f'opaque-{i:06d}', dna))
    rows += [('short-kept', 'ACGT'*31), ('N-kept', 'N'*1200)]
    fasta.write_text(''.join(f'>{i}\n{s}\n' for i, s in rows))
    depth.write_text('contig_id\t'+'\t'.join(f'synthetic-{i}' for i in range(10))+'\n'+
        ''.join(i+'\t'+'\t'.join(map(str, np.zeros(10) if j % 11 == 0 else rng.integers(0, 80, 10)))+'\n'
            for j, (i, _) in enumerate(reversed(rows))))
    base = base_config()
    base['epochs'] = epochs
    for mode in ['depth', 'sequence']:
        prepare(fasta, depth if mode == 'depth' else None, root/mode, base)
    cfg = config()
    cfg['epochs'] = epochs
    write_json(root/'config.json', cfg)
    write_json(root/'base-config.json', base)
    write_json(root/'generated.json', dict(kind='Own generated engineering DNA only', parents=parents,
        dna_profile=dna_profile, epochs=epochs, all_records=len(rows), bp=sum(len(s) for _, s in rows),
        samples='Synthetic test values, not measured observations'))


def main():
    """Generate fixtures or invoke one actual installed stage; orchestration is external."""
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--parents', type=int, default=192)
    p.add_argument('--epochs', type=int, choices=[2, 20], default=2)
    p.add_argument('--dna-profile', choices=['oligomer', 'gc_iid'], default='oligomer')
    a = p.parse_args()
    if not 128 <= a.parents <= 1024:
        p.error('Engineering fixture requires 128..1024 parents')
    generate(a.output, a.parents, a.epochs, a.dna_profile)


if __name__ == '__main__':
    main()
