"""Installed explicit context-stage entry point for a bounded research DAG."""
from pathlib import Path


def run(args):
    """Refuse absent inputs/existing outputs, then execute one declared native stage."""
    required = dict(tokens=['fasta', 'features', 'views'], train=['features', 'views', 'tokens'],
        embed=['features', 'views', 'tokens', 'checkpoint'])
    for name in required[args.stage]:
        if getattr(args, name) is None:
            raise ValueError(args.stage+' requires --'+name)
    if Path(args.output).exists():
        raise FileExistsError('Fresh context output required')
    from ..io import emit
    emit('context_stage_enter', stage_name=args.stage, threads=args.threads, loader_workers=0)
    if args.stage == 'tokens':
        from .tokens import prepare
        prepare(args.fasta, args.features, args.views, args.output)
    else:
        from .model import config, train, embed
        if args.stage == 'train':
            train(args.features, args.views, args.tokens, args.output, config(args.config), args.threads)
        else:
            embed(args.features, args.views, args.tokens, args.checkpoint, args.output, args.threads)
    emit('context_stage_complete', stage_name=args.stage)
