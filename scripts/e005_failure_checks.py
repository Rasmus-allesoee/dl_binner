#!/usr/bin/env python3
"""Exercise fatal native CLI inputs and overwrite protection; never tune/train.

Called in the isolated binner runtime. Expected failures are checked for prompt
exit and absence of outputs; they cannot convert the actual smoke's failure into
success. Detailed stdout and elapsed time are retained for each contract.
"""
import json
from pathlib import Path
import subprocess
import sys
import time

fasta, depth, checkpoint, features, directory = map(Path, sys.argv[1:6])
threads = sys.argv[6]
directory.mkdir(exist_ok=False)
cli = [sys.executable, '-I', '-m', 'dl_binner', '--threads', threads]
table = depth.read_text().splitlines()
(directory/'missing-depth.tsv').write_text('\n'.join(table[:-1])+'\n')
(directory/'corrupt.pt').write_bytes(checkpoint.read_bytes()+b'corrupted')
(directory/'corrupt.json').write_bytes(checkpoint.with_suffix('.json').read_bytes())
cases = {
    'missing-depth': ['prepare', '--fasta', str(fasta), '--depth', str(directory/'missing-depth.tsv'), '--output', str(directory/'bad.npz')],
    'corrupt-checkpoint': ['embed', '--features', str(features), '--checkpoint', str(directory/'corrupt.pt'), '--output', str(directory/'bad-embedding.npz')],
    'refuse-overwrite': ['prepare', '--fasta', str(fasta), '--output', str(features)],
}
results = {}
before = features.read_bytes()
for name, arguments in cases.items():
    started = time.monotonic()
    result = subprocess.run(cli+arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=10)
    (directory/(name+'.log')).write_bytes(result.stdout)
    results[name] = dict(exit_code=result.returncode, seconds=time.monotonic()-started)
    if result.returncode == 0:
        raise RuntimeError('Expected fatal native failure: '+name)
if features.read_bytes() != before or (directory/'bad.npz').exists() or (directory/'bad-embedding.npz').exists():
    raise RuntimeError('Failed adapter overwrote/created output')
(directory/'verified.json').write_text(json.dumps(dict(status='passed', cases=results), indent=2)+'\n')
print(json.dumps(dict(status='passed', cases=results)), flush=True)
