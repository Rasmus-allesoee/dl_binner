"""Installed restore-only pair construction and explicit learning/reload stages."""
from pathlib import Path


def run(args):
    """Validate required paths, refuse existing outputs, and run only one stage."""
    required = dict(pairs=['features', 'embeddings', 'graph', 'marker_cache', 'marker_hmm'],
                    train=['features', 'views', 'tokens', 'pairs'],
                    embed=['features', 'views', 'tokens', 'pairs', 'checkpoint'])
    for name in required[args.stage]:
        if getattr(args, name) is None:
            raise ValueError('Relation stage requires --'+name.replace('_', '-'))
    if Path(args.output).exists():
        raise FileExistsError('Fresh relation output required; no overwrite or automatic retry')
    if args.stage != 'train' and args.config is not None:
        raise ValueError('--config applies only to training; other stages consume frozen metadata')
    if args.stage == 'pairs':
        from .pairs import prepare
        prepare(args.features, args.embeddings, args.graph, args.marker_cache, args.marker_hmm, args.output)
    else:
        from .model import config, train, embed
        if args.stage == 'train':
            train(args.features, args.views, args.tokens, args.frozen, args.pairs, args.output,
                  config(args.config, frozen=args.frozen is not None), args.threads)
        else:
            embed(args.features, args.views, args.tokens, args.frozen, args.pairs, args.checkpoint, args.output, args.threads)
