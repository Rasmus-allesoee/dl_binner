#!/usr/bin/env python3
"""Measure two real 1,024-parent context kernels in isolated owned processes.

Generated DNA and parent means are engineering fixtures, never community labels.
The bounded native parent owns this helper's clock/RSS/disk; no cloud APIs or
automatic retry exist here. Output paths are fresh and retained on failure.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def run(output, python, epochs=2):
    """Generate once, tokenize/train/reload both modes and retain actual timing."""
    root = Path(output)
    root.mkdir(parents=True, exist_ok=False)
    repo = Path(__file__).absolute().parents[1]
    commands = []

    def call(label, args):
        log = root/(label+'.log')
        with log.open('x') as stream:
            code = subprocess.run([str(python), '-I', '-B', *map(str, args)], stdout=stream, stderr=subprocess.STDOUT).returncode
        commands.append(dict(label=label, argv=[str(python), '-I', '-B', *map(str, args)], exit_code=code))
        (root/'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
        if code:
            raise RuntimeError('Actual context timing failed: '+str(log))

    fixture = root/'fixture'
    call('generate', [repo/'experiments/E019-window-context/engineering_fixture.py', '--output', fixture, '--parents', 1024, '--epochs', epochs])
    results = {}
    for mode in ['depth', 'sequence']:
        common = ['-m', 'dl_binner', 'context-stage', '--features', fixture/mode/'features.npz',
            '--views', fixture/mode/'views.npz', '--threads', 4]
        call(mode+'-tokens', common+['--stage', 'tokens', '--fasta', fixture/'synthetic.fa', '--output', root/(mode+'-tokens')])
        call(mode+'-train', common+['--stage', 'train', '--tokens', root/(mode+'-tokens'),
            '--config', fixture/'config.json', '--output', root/(mode+'-train')])
        call(mode+'-reload', common+['--stage', 'embed', '--tokens', root/(mode+'-tokens'),
            '--checkpoint', root/(mode+'-train/checkpoint.pt'), '--output', root/(mode+'-embeddings.npz')])
        checkpoint = json.loads((root/(mode+'-train/checkpoint.json')).read_text())
        # Inspect actual saved tensor states in a separate Torch process; this
        # helper/controller remains stdlib-only and never loads graph runtimes.
        probe = '''import json,sys,torch
from pathlib import Path
from dl_binner.context.model import initialize
torch.set_num_threads(4);torch.set_num_interop_threads(1)
s=torch.load(Path(sys.argv[1]),weights_only=True,map_location='cpu')
torch.manual_seed(s['config']['seed']);initial,_,_=initialize(len(s['samples']),s['config'])
key='context_projection.weight';attention='attention.in_proj_weight'
v=dict(online_projection_norm=float(s['model_state'][key].norm()),
       teacher_projection_norm=float(s['target_state'][key].norm()),
       attention_change_norm=float((s['model_state'][attention]-initial.state_dict()[attention]).norm()))
assert all(__import__('math').isfinite(x) and x>0 for x in v.values()),v
print(json.dumps(v))'''
        probed = subprocess.run([str(python), '-I', '-B', '-c', probe,
            str(root/(mode+'-train/checkpoint.pt'))], capture_output=True, text=True, check=True)
        residual_state = json.loads(probed.stdout.splitlines()[-1])
        durations = [b['wall_seconds']-a['wall_seconds'] for a, b in zip(checkpoint['history'], checkpoint['history'][1:])]
        import statistics
        results[mode] = dict(steady_epoch_seconds=statistics.median(durations[-5:]),
            checkpoint=checkpoint, epochs=epochs, dna_profile='oligomer', residual_state=residual_state,
            timing_scope='Actual generated engineering schedule with monitor; not community stability/performance proof')
    (root/'timing.json').write_text(json.dumps(results, indent=2)+'\n')
    return results


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--python', type=Path, required=True)
    p.add_argument('--epochs', type=int, choices=[2, 20], default=2)
    a = p.parse_args()
    run(a.output, a.python, a.epochs)
