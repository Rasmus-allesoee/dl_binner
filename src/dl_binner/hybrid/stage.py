"""Explicit installed frozen extraction/training/reload stages with no downloads."""
from pathlib import Path


def run(args):
    """Refuse absent/final outputs then execute the one requested native stage."""
    required=dict(extract=['fasta','features','views','model_directory','model_pin'],train=['features','views','tokens','frozen'],embed=['features','views','tokens','frozen','checkpoint'])
    for name in required[args.stage]:
        if getattr(args,name) is None:raise ValueError('Hybrid stage requires --'+name.replace('_','-'))
    if Path(args.output).exists():raise FileExistsError('Fresh hybrid output required')
    from ..model import configure_torch
    configure_torch(args.threads)
    if args.stage=='extract':
        from .extract import Extractor
        from .bank import prepare
        extractor=Extractor(args.model_directory,args.model_pin,args.device)
        prepare(args.fasta,args.features,args.views,args.output,extractor,extractor.pin)
    else:
        from .model import config,train,embed
        if args.stage=='train':train(args.features,args.views,args.tokens,args.frozen,args.output,config(args.config),args.threads)
        else:embed(args.features,args.views,args.tokens,args.frozen,args.checkpoint,args.output,args.threads)
