"""Installed CLI with isolated imports, coherent CPU budgets and fail-fast stages."""
import argparse
import os
from pathlib import Path
import sys
import traceback

from . import __version__


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """Keep examples readable and show operational defaults in command help."""


def main(argv=None):
    """Dispatch a full bounded workflow or one native stage with actionable errors."""
    parser = argparse.ArgumentParser(prog='dl-binner', description='Experimental CPU metagenomic binner: composition + contrastive learning.',
        formatter_class=HelpFormatter,
        epilog='Start with dl-binner run --help. Every contig remains assigned, unassigned or excluded.\nBin sizes and assignment are not genome-quality estimates. Prototype interfaces may evolve.')
    parser.add_argument('--threads', type=int, default=4, choices=range(1, 5), help='Numerical CPU threads; loader workers remain zero')
    parser.add_argument('--version', action='version', version='dl-binner '+__version__)
    commands = parser.add_subparsers(dest='command', required=True)
    running = commands.add_parser('run', help='Run the complete learned binner and matched raw control',
        description='Validate FASTA/depth, train, reload, cluster and export both arms in serial.\nCompleted stages can be explicitly resumed; changed or corrupted bytes are refused.',
        formatter_class=HelpFormatter,
        epilog='Examples:\n  dl-binner run --fasta assembly.fna --output bins --workflow-python /path/workflow/bin/python\n  dl-binner run --fasta assembly.fna --depth mean-depth.tsv --output bins --workflow-python /path/workflow/bin/python\n  # Continue a matching partial run: repeat its command and add --resume.\n\nOutputs: learned/bins/ and raw/bins/ contain assignments.tsv, bin_*.fna,\nunassigned.fna and excluded.fna. run-summary.json/tsv retain all length strata.\nDetailed logs, resource samples and invocation status live under logs/.\nDepth header: contig_id followed by ordered unique sample names; every FASTA ID needs one row.\nSupply an existing, separate Snakemake 9.16.3 Python. This command installs nothing.')
    running.add_argument('--fasta', type=Path, required=True, help='Assembly FASTA with unique IDs and IUPAC DNA')
    running.add_argument('--depth', type=Path, help='Explicit finite nonnegative mean-depth TSV mapped to this exact assembly')
    running.add_argument('--output', type=Path, required=True, help='Fresh output directory; reused only with --resume')
    running.add_argument('--workflow-python', type=Path, default=os.environ.get('DL_BINNER_WORKFLOW_PYTHON'),
                         help='Lexical interpreter path of separate Snakemake 9.16.3 environment (or DL_BINNER_WORKFLOW_PYTHON)')
    running.add_argument('--min-length', type=int, default=500, help='Eligibility cutoff; shorter IDs are retained as exclusions')
    running.add_argument('--training-config', type=Path, help='Explicit training JSON; default is the packaged accepted seed-11 schedule')
    running.add_argument('--memory-gb', type=float, default=8, help='Working process-tree RSS ceiling, GB; maximum 8')
    running.add_argument('--timeout', type=float, default=7200, help='Overall invocation wall-time ceiling, seconds; maximum 7200')
    running.add_argument('--resume', action='store_true', help='Verify matching inputs/source/config/runtime and reuse completed stages')
    running.add_argument('--stop-after', choices=('features','train','raw-embed','raw-cluster','raw-export','learned-embed','learned-cluster','learned-export'),
                         help='Stop at a stage boundary for an inspectable partial run; omit when continuing')
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
    for command in commands.choices.values():
        command.add_argument('--threads', type=int, choices=range(1, 5), default=argparse.SUPPRESS,
                             help='CPU threads (1–4); may also appear before the command')
    args = parser.parse_args(argv)
    if args.command == 'run':
        import math
        if args.workflow_python is None:
            parser.error('run requires --workflow-python /path/to/workflow/bin/python (Snakemake 9.16.3), or DL_BINNER_WORKFLOW_PYTHON')
        if not math.isfinite(args.memory_gb) or not 0 < args.memory_gb <= 8:
            parser.error('--memory-gb must be greater than zero and at most 8')
        if not math.isfinite(args.timeout) or not 0 < args.timeout <= 7200:
            parser.error('--timeout must be greater than zero and at most 7200 seconds')
        if args.min_length < 4:
            parser.error('--min-length must be at least 4; shorter contigs still appear as exclusions')
    for name in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONUSERBASE'):
        os.environ.pop(name, None)
    os.environ['PYTHONNOUSERSITE'] = '1'
    for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        os.environ[name] = str(args.threads)
    try:
        if args.command == 'run':
            from .runner import run_pipeline
            return run_pipeline(args)
        if args.output.exists():
            raise FileExistsError(f'Fresh output path required: {args.output}. Choose a new path; no files were overwritten')
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
    except BaseException as error:
        print(f'error: {error}', file=sys.stderr, flush=True)
        if args.command == 'run':
            return 130 if isinstance(error, KeyboardInterrupt) else 1
        traceback.print_exc()
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(1)  # Fatal native failures must not hang during library teardown.
