"""Packaged generic local workflow; explicit barriers serialize every native stage."""
from pathlib import Path
from shlex import quote

ROOT = Path(config['root'])
CFG = str(ROOT/config['invocation']/'config.json')
CLI = quote(config['python'])+' -I -B -m dl_binner.runner --config '+quote(CFG)+' --stage '
STAGES = ('features', 'train', 'raw-embed', 'raw-cluster', 'raw-export', 'learned-embed', 'learned-cluster', 'learned-export')
TARGETS = [f'receipts/{i+1:02d}-{s}.json' for i,s in enumerate(STAGES)]

rule all:
    input: TARGETS[-1]

rule native_stage:
    input:
        manifest='run-manifest.json',
        previous=lambda w: [TARGETS[int(w.number)-2]] if int(w.number)>1 else []
    output: 'receipts/{number}-{stage}.json'
    wildcard_constraints: number='0[1-8]', stage='features|train|raw-embed|raw-cluster|raw-export|learned-embed|learned-cluster|learned-export'
    threads: config['threads']
    resources: mem_mb=config['memory_mb']
    log: str(ROOT/config['invocation']/'{number}-{stage}.adapter.log')
    benchmark: str(ROOT/config['invocation']/'{number}-{stage}.benchmark.tsv')
    shell: 'set +e; {CLI}{wildcards.stage:q} > {log:q} 2>&1; result=$?; cat {log:q}; exit $result'
