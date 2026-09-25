"""First seed-11 pair; one tool/condition at a time with extended benchmarks."""
PYTHON=config['driver_python']
HELPER=config['helper']
CONFIG=config['runtime_config']
PAIRS=[(t,c) for t in config['tools'] for c in ('C0','CT')]

def predecessor(w):
    i=PAIRS.index((w.tool,w.condition))
    return ['verified.json'] if i==0 else ['%s/%s/retained.json' % PAIRS[i-1]]

rule all:
    input: 'paired-summary.json'

rule native_condition:
    input: predecessor
    output: '{tool}/{condition}/retained.json'
    wildcard_constraints: tool='metabat|vamb|comebin', condition='C0|CT'
    threads: config['threads']
    resources: mem_mb=config['worker_mem_mb'], tool_slots=1
    log: 'logs/{tool}-{condition}.log'
    benchmark: 'benchmarks/{tool}-{condition}.tsv'
    shell:
        '{PYTHON:q} -I {HELPER:q} --config {CONFIG:q} --worker --tool {wildcards.tool} --condition {wildcards.condition} > {log:q} 2>&1'

rule summarize:
    input: ['%s/%s/retained.json' % pair for pair in PAIRS]
    output: 'paired-summary.json'
    shell:
        '{PYTHON:q} -I {HELPER:q} --config {CONFIG:q} --aggregate'
