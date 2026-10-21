#!/usr/bin/env python3
"""One serial context candidate on immutable E016 inputs; no truth or cloud APIs.

Preparation may add a bounded token bank from exactly retained DNA/views. It
cannot regenerate old features/crops/markers or fit an old baseline. Research
resource/credit/supervision release belongs to the bounded parent launcher.
"""
import argparse
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).absolute().parent))
from e014_collect import binding

UNITS = ['E009-context', 'oral-context']
STAGES = ['tokens', 'train', 'embed', 'group', 'refine', 'export', 'graph-proof']


def validate_plan(p, engineering=False):
    """Freeze sole treatment, complete paths and serial two-community scope."""
    allowed = {'kind', 'work', 'units', 'threads', 'python', 'worker', 'workflow_python',
        'snakefile', 'config', 'base_config', 'hmm', 'reuse_lock', 'candidate_lock'}
    if set(p) != allowed or p['kind'] != 'E019 window-context candidate' or p['threads'] != 4 or list(p['units']) != UNITS:
        raise ValueError('Frozen E019 scope differs')
    fields = {'fasta', 'features', 'views', 'marker_cache'}
    if any(set(u) != fields for u in p['units'].values()):
        raise ValueError('Unexpected input/truth path in context plan')
    cfg = json.loads(Path(p['config']).read_text())
    base = json.loads(Path(p['base_config']).read_text())
    # Pure validation keeps tensor and graph OpenMP families in separate processes.
    from e016_policy import validate_policy
    packaged = Path(__file__).absolute().parents[1]/'src/dl_binner/resources/context.json'
    if cfg.get('context') != json.loads(packaged.read_text()):
        raise ValueError('Unfrozen context token/encoder policy')
    validate_policy({k: v for k, v in cfg.items() if k != 'context'}, base)
    if not engineering and (cfg['epochs'] != 20 or cfg['batch_size'] != 256 or cfg['seed'] != 11):
        raise ValueError('Frozen community seed/schedule differs')
    return cfg, base


def stage(plan, unit, name, engineering=False):
    """Execute exactly one fresh token/fit/reload/fixed downstream/export stage."""
    p = json.loads(Path(plan).read_text())
    cfg, base = validate_plan(p, engineering)
    if unit not in UNITS or name not in STAGES:
        raise ValueError('Unknown context stage/unit')
    u = p['units'][unit]
    root = Path(p['work'])/'units'/unit
    root.mkdir(parents=True, exist_ok=True)
    # Snakemake creates output parents before entering a shell rule. Remove only
    # that empty shell-created directory; never accept a partial scientific stage.
    if name in ['tokens', 'train', 'group', 'refine', 'export']:
        target = root/name
        if target.is_dir() and not any(target.iterdir()):
            target.rmdir()
    if name == 'tokens':
        from dl_binner.context.tokens import prepare
        prepare(u['fasta'], u['features'], u['views'], root/'tokens')
    elif name == 'train':
        from dl_binner.context.model import train
        train(u['features'], u['views'], root/'tokens', root/'train', cfg, 4)
    elif name == 'embed':
        from dl_binner.context.model import embed
        embed(u['features'], u['views'], root/'tokens', root/'train/checkpoint.pt', root/'embeddings.npz', 4)
    elif name == 'group':
        from dl_binner.multiview.downstream import group
        group(root/'embeddings.npz', u['features'], root/'group', base, 4)
    elif name == 'refine':
        from dl_binner.multiview.downstream import refine
        refine(u['features'], root/'embeddings.npz', root/'group/partition.json', u['marker_cache'],
            u['fasta'], p['hmm'], root/'refine', base)
    elif name == 'export':
        from dl_binner.information.export import export
        from dl_binner.io import write_json
        target = root/'export'
        target.mkdir(exist_ok=False)
        result = {}
        for label, part in [('pre', root/'group/partition.json'), ('old', root/'refine/old-partition.json'),
                ('post', root/'refine/partition.json')]:
            # DNA is physically emitted once; all three assignment/accounting axes survive.
            export(u['features'], part, u['fasta'], target/label, include_dna=label == 'post')
            result[label] = json.loads((target/label/'manifest.json').read_text())
        write_json(target/'accounting.json', result)
    else:
        from e014_graph_review import review
        review(root, root/'graph-proof.json')


def workflow(plan, dry_run=False, engineering=False):
    """Execute the pinned four-core Snakemake DAG with an explicit serial unit barrier."""
    p = json.loads(Path(plan).read_text())
    validate_plan(p, engineering)
    argv = [p['workflow_python'], '-I', '-B', '-m', 'snakemake', '--snakefile', p['snakefile'],
        '--directory', p['work'], '--cores', '4', '--runtime-source-cache-path',
        str(Path(p['work']).parent/'workflow-source-cache'), '--config', 'plan='+str(Path(plan).absolute()),
        'engineering='+str(engineering).lower(), '--printshellcmds', '--benchmark-extended']
    if dry_run:
        argv.append('--dry-run')
    os.execv(argv[0], argv)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--workflow', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--engineering', action='store_true', help='Tiny generated fixtures only; not admitted by native launcher')
    p.add_argument('--unit', choices=UNITS)
    p.add_argument('--stage', choices=STAGES)
    a = p.parse_args()
    if a.workflow:
        if a.unit or a.stage:
            p.error('Workflow cannot also select a stage')
        workflow(a.plan, a.dry_run, a.engineering)
    else:
        if a.dry_run or not a.unit or not a.stage:
            p.error('Individual stage requires unit and stage')
        stage(a.plan, a.unit, a.stage, a.engineering)
