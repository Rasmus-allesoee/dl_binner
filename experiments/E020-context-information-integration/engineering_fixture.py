"""Consume retained tiny inputs through the actual cached grouping launcher.

Local E019 fixtures have real learned context metadata and cached marker calls.
Linux reuses an E017 tiny marker fixture plus separately reads the accepted E019
native full-width context vectors. Neither route fits, infers, extracts features
or redetects markers. The fixture type is explicit, never a community bypass.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).absolute().parents[2]/'scripts'))
from e014_collect import binding
from e020_control import stage


def run(cached, output, layout):
    """Run all four real stages for both tiny depth modes, retaining every output."""
    from dl_binner.io import write_json
    from dl_binner.multiview.views import config
    root, cached = Path(output).absolute(), Path(cached).absolute()
    root.mkdir(parents=True, exist_ok=False)
    repo = Path(__file__).absolute().parents[2]
    units = {}
    for unit, mode in [('E009-context', 'depth'), ('oral-context', 'sequence')]:
        sub = cached if layout == 'context' else cached/mode
        units[unit] = dict(fasta=str(cached/'synthetic.fa' if layout == 'context' else cached/'tiny.fa'),
            features=str(sub/mode/'features.npz' if layout == 'context' else sub/'features/features.npz'),
            embeddings=str(cached/(mode+'-embeddings.npz') if layout == 'context' else sub/'embeddings.npz'),
            marker_cache=str(cached/'markers'))
    # The old E017 fixture names the FASTA via its original fixture generator.
    if layout == 'marker':
        names = [p for p in cached.glob('*') if p.suffix in ['.fa', '.fna', '.fasta']]
        if len(names) != 1:
            raise ValueError('Retained tiny FASTA locator is ambiguous')
        for u in units.values():
            u['fasta'] = str(names[0])
    hmms = list(cached.glob('*.hmm'))
    if len(hmms) != 1:
        raise ValueError('Retained tiny marker asset locator is ambiguous')
    inputs = {str(p): binding(p) for p in cached.rglob('*') if p.is_file() and not p.is_symlink()}
    reuse = root/'reuse.json'
    write_json(reuse, dict(units=units, hmm=str(hmms[0])))
    write_json(root/'base.json', config())
    plan = dict(kind='E020 cached E019 learning original E017 grouping', work=str(root/'work'),
        units=units, threads=4, python=sys.executable, workflow_python=sys.executable,
        worker=str(repo/'scripts/e020_control.py'), snakefile=str(Path(__file__).parent/'Snakefile'),
        config=str(Path(__file__).parent/'config.json'), base_config=str(root/'base.json'),
        hmm=str(hmms[0]), reuse_lock=str(reuse))
    write_json(root/'plan.json', plan)
    for unit in units:
        for name in ['group', 'refine', 'export', 'audit']:
            stage(root/'plan.json', unit, name)
        accounting = json.loads((root/'work/units'/unit/'export/accounting.json').read_text())
        if set(accounting) != {'cores', 'pre', 'old', 'post'}:
            raise ValueError('Tiny export lost an alternative')
        totals = {(a['contigs'], a['bp']) for a in accounting.values()}
        if len(totals) != 1:
            raise ValueError('Tiny alternatives lost DNA')
    if inputs != {str(p): binding(p) for p in cached.rglob('*') if p.is_file() and not p.is_symlink()}:
        raise ValueError('Retained tiny science was mutated')
    write_json(root/'fixture.json', dict(status='PASS', layout=layout, inputs=inputs,
        encoder_fit=False, inference=False, marker_detection=False,
        actual_worker_graph_refiner_exports=True, truth_used=False))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cached', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--layout', choices=['context', 'marker'], required=True)
    a = p.parse_args()
    run(a.cached, a.output, a.layout)
