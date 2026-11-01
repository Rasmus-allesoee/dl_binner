"""Explicit installed continuation stages; no truth, marker detection or cloud API.

Each output is fresh and refuses overwrite. The experiment DAG supplies verified
resume and native release gates; this module is also usable on real tiny fixtures.
"""
import argparse
from pathlib import Path


def main():
    """Dispatch exactly one confidence-cache, continuation-fit or native-reload stage."""
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--stage',required=True,choices=['pairs','train','embed'])
    a.add_argument('--features',required=True,type=Path); a.add_argument('--output',required=True,type=Path)
    a.add_argument('--source-pairs',type=Path); a.add_argument('--teacher-embeddings',type=Path)
    a.add_argument('--teacher-graph',type=Path); a.add_argument('--views',type=Path)
    a.add_argument('--tokens',type=Path); a.add_argument('--frozen',type=Path)
    a.add_argument('--pairs',type=Path); a.add_argument('--bootstrap',type=Path)
    a.add_argument('--checkpoint',type=Path); a.add_argument('--threads',type=int,default=4)
    v = a.parse_args()
    if v.stage == 'pairs':
        if not all([v.source_pairs,v.teacher_embeddings,v.teacher_graph]): a.error('pairs needs source cache and exact own teacher/graph')
        from .pairs import prepare
        prepare(v.source_pairs,v.features,v.teacher_embeddings,v.teacher_graph,v.output)
    else:
        if not all([v.views,v.tokens,v.pairs,v.bootstrap]): a.error('learning needs views, tokens, pairs and admitted bootstrap')
        from . import model
        args = (v.features,v.views,v.tokens,v.frozen,v.pairs,v.bootstrap)
        if v.stage == 'train': model.train(*args,v.output,v.threads)
        else:
            if v.checkpoint is None: a.error('embed needs checkpoint')
            model.embed(*args,v.checkpoint,v.output,v.threads)


if __name__ == '__main__': main()
