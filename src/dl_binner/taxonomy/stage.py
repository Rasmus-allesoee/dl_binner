"""Explicit installed taxonomy stages; no acquisition, truth, scoring or cloud API."""
import argparse
from pathlib import Path


def main():
    """Dispatch only a fresh, independently admitted classifier/cache/adapter step."""
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',required=True,choices=['classify','cache','train'])
    for name in ['features','views','fasta','binary','database','tokens','frozen','checkpoint','embeddings','annotations','cache','output']:
        p.add_argument('--'+name,type=Path,required=name in ['features','output'])
    p.add_argument('--engineering',action='store_true');p.add_argument('--threads',type=int,default=4);a=p.parse_args()
    if a.stage=='classify':
        if not all([a.binary,a.database,a.fasta]):p.error('classify needs binary/database/FASTA')
        from .classifier import classify
        classify(a.binary,a.database,a.fasta,a.features,a.output,a.engineering)
    elif a.stage=='cache':
        if not all([a.views,a.tokens,a.checkpoint,a.embeddings,a.annotations]):p.error('cache needs exact DNA views/tokens/state/vectors/annotations')
        from .cache import prepare
        prepare(a.features,a.views,a.tokens,a.frozen,a.checkpoint,a.embeddings,a.annotations,a.output,a.threads)
    else:
        if not all([a.views,a.cache,a.annotations]):p.error('train needs views/cache/annotations')
        from .model import train
        train(a.features,a.views,a.cache,a.annotations,a.output,a.threads)


if __name__=='__main__':main()
