"""Explicit installed stages for a serial multiview research workflow.

Each call owns fresh outputs, never silently retries/reinstalls or accepts truth.
The research launcher owns the overall time/RSS/disk supervision and stage journal.
"""
from .views import config


def run(args):
    """Dispatch one actual native stage with required inputs and exclusive output."""
    required=dict(features=['fasta'],markers=['fasta','marker_hmm','marker_manifest'],train=['features','views'],
                  embed=['features','checkpoint'],group=['features','embeddings'],
                  refine=['features','embeddings','parent','marker_cache','fasta','marker_hmm'],export=['features','parent','fasta'])
    for key in required[args.stage]:
        if getattr(args,key) is None:raise ValueError(args.stage+' requires --'+key.replace('_','-'))
    if args.output.exists():raise FileExistsError('Fresh multiview stage output required')
    cfg=config(args.config)
    from ..io import emit
    emit('multiview_stage_enter',stage_name=args.stage,threads=args.threads,loader_workers=0)
    if args.stage=='features':
        from .views import prepare
        prepare(args.fasta,args.depth,args.output,cfg,args.parent_features)
    elif args.stage=='markers':
        from ..candidate.markers import cache
        args.output.mkdir(parents=True);cache(args.fasta,args.marker_hmm,args.marker_manifest,args.output,args.threads)
    elif args.stage=='train':
        from .model import train
        train(args.features,args.views,args.output,cfg,args.threads)
    elif args.stage=='embed':
        from .model import embed
        embed(args.features,args.checkpoint,args.output,args.threads)
    elif args.stage=='group':
        from .downstream import group
        group(args.embeddings,args.features,args.output,cfg,args.threads)
    elif args.stage=='refine':
        from .downstream import refine
        refine(args.features,args.embeddings,args.parent,args.marker_cache,args.fasta,args.marker_hmm,args.output,cfg)
    else:
        from ..clustering import export
        export(args.features,args.parent,args.fasta,args.output)
    emit('multiview_stage_complete',stage_name=args.stage)
