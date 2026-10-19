"""One bounded synthetic full-width learning/reload fixture, never community scoring.

Use the installed candidate. Generated parent-depth values are explicit engineering
fixtures, not observations or invented crop variance. Retain timing/loss/exposure
and hashes to inform a rough schedule estimate, not a biological design choice.
"""
import argparse
import json
from pathlib import Path

import numpy as np


def run(output,threads=4):
    """Generate 1,024 diverse DNA records, fit two epochs and independently reload."""
    from dl_binner.multiview.views import config,prepare
    from dl_binner.multiview.positive import train,embed
    from dl_binner.io import write_json
    root=Path(output);root.mkdir(parents=True,exist_ok=False);rng=np.random.default_rng(718)
    cfg=config();cfg['epochs']=2
    fasta=root/'synthetic.fa';depth=root/'synthetic-depth.tsv'
    with fasta.open('x') as f,depth.open('x') as d:
        d.write('contig_id\t'+'\t'.join('synthetic-'+str(i) for i in range(10))+'\n')
        for i in range(1024):
            n=500+(i*37)%11000;dna=''.join(rng.choice(list('ACGT'),n))
            f.write(f'>engineering-{i}\n{dna}\n')
            d.write(f'engineering-{i}\t'+'\t'.join(str(v) for v in (np.zeros(10) if i%11==0 else rng.integers(0,80,10)))+'\n')
    prepare(fasta,depth,root/'features',cfg)
    cfg.update(positive_only=True,predictor_hidden=128,ema_base=.996,collapse_rows=8192,collapse_min_std=.001,collapse_min_rank=2)
    train(root/'features/features.npz',root/'features/views.npz',root/'train',cfg,threads)
    embed(root/'features/features.npz',root/'train/checkpoint.pt',root/'embeddings.npz',threads)
    receipt=json.loads((root/'train/checkpoint.json').read_text())
    write_json(root/'fixture.json',dict(kind='synthetic engineering only',parents=1024,epochs=2,
        actual_inner_model_seconds=receipt['wall_seconds'],process_CPU_seconds=receipt['process_cpu_seconds'],
        parameter_count=receipt['parameter_count'],configuration=cfg,
        extrapolation='Rough kernel/parent-epoch scaling only; full data, graph, markers, export and Linux setup are separate.'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--threads',type=int,default=4)
    a=p.parse_args();run(a.output,a.threads)
