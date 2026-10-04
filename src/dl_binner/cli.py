"""Installed CLI with isolated imports, coherent CPU budgets and fail-fast stages."""
import argparse
import os
from pathlib import Path
import sys
import traceback


def main(argv=None):
    """Dispatch one explicit native stage, never train/infer/overwrite implicitly."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--threads', type=int, default=4, choices=range(1, 5))
    parser.add_argument('--version', action='version', version='dl-binner 0.1.0.dev0')
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare', help='Validate FASTA/depth and prepare raw composition')
    prep.add_argument('--fasta', type=Path, required=True)
    prep.add_argument('--depth', type=Path)
    prep.add_argument('--min-length', type=int, default=500)
    prep.add_argument('--tnf-cache', type=Path)
    prep.add_argument('--tnf-receipt', type=Path)
    prep.add_argument('--tnf-panel', type=Path)
    prep.add_argument('--output', type=Path, required=True)
    training = commands.add_parser('train', help='Train own contrastive encoder and save state')
    training.add_argument('--features', type=Path, required=True)
    training.add_argument('--config', type=Path, required=True)
    training.add_argument('--output', type=Path, required=True)
    embedding = commands.add_parser('embed', help='Infer from checkpoint or retain raw control')
    embedding.add_argument('--features', type=Path, required=True)
    group = embedding.add_mutually_exclusive_group(required=True)
    group.add_argument('--checkpoint', type=Path)
    group.add_argument('--raw', action='store_true')
    embedding.add_argument('--output', type=Path, required=True)
    clustering = commands.add_parser('cluster', help='Fixed label-blind mutual-neighbor clustering')
    clustering.add_argument('--embeddings', type=Path, required=True)
    clustering.add_argument('--output', type=Path, required=True)
    exporting = commands.add_parser('export', help='Account for and export every input contig')
    exporting.add_argument('--features', type=Path, required=True)
    exporting.add_argument('--partition', type=Path, required=True)
    exporting.add_argument('--fasta', type=Path, required=True)
    exporting.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    for name in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONUSERBASE'):
        os.environ.pop(name, None)
    os.environ['PYTHONNOUSERSITE'] = '1'
    for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        os.environ[name] = str(args.threads)
    try:
        if args.output.exists():
            raise FileExistsError('Fresh output path required')
        from .io import emit
        emit('stage_enter', command=args.command, threads=args.threads, loader_workers=0)
        if args.command == 'prepare':
            from .io import prepare
            prepare(args.fasta, args.output, args.depth, args.min_length,
                    args.tnf_cache, args.tnf_receipt, args.tnf_panel)
        elif args.command == 'train':
            from .model import train
            train(args.features, args.config, args.output, args.threads)
        elif args.command == 'embed':
            from .model import embed
            embed(args.features, args.output, args.checkpoint, args.threads)
        elif args.command == 'cluster':
            from .clustering import cluster
            cluster(args.embeddings, args.output)
        elif args.command == 'export':
            from .clustering import export
            export(args.features, args.partition, args.fasta, args.output)
        emit('stage_complete', command=args.command)
        return 0
    except BaseException:
        traceback.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(1)  # Fatal native failures must not hang during library teardown.
