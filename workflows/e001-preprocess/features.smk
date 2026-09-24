"""Native paired features: shared integrity gate, independent tools, review gate."""
PYTHON = config['driver_python']
HELPER = config['helper']
CONFIG = config['runtime_config']
TOOLS = ['metabat', 'vamb', 'comebin']

wildcard_constraints:
    tool='metabat|vamb|comebin'

rule all:
    input: 'feature-summary.json'

rule verify_inputs:
    input: manifest=config['manifest'], reference=config['reference']
    output: 'inputs.json'
    threads: 1
    resources: mem_mb=2000, tool_slots=1
    log: 'logs/verify.log'
    benchmark: 'benchmarks/verify.tsv'
    shell:
        '{PYTHON:q} -I {HELPER:q} --worker verify --config {CONFIG:q} > {log:q} 2>&1'

rule native_paired_features:
    input: 'inputs.json'
    output: '{tool}/result.json'
    threads: config['worker_vcpus']
    resources: mem_mb=config['worker_mem_mb'], tool_slots=1
    log: 'logs/{tool}.log'
    benchmark: 'benchmarks/{tool}.tsv'
    shell:
        '{PYTHON:q} -I {HELPER:q} --worker {wildcards.tool} --config {CONFIG:q} > {log:q} 2>&1'

rule review_receipt:
    input: expand('{tool}/result.json',tool=TOOLS)
    output: 'feature-summary.json'
    threads: 1
    resources: mem_mb=512
    log: 'logs/aggregate.log'
    shell:
        '{PYTHON:q} -I {HELPER:q} --worker aggregate --config {CONFIG:q} > {log:q} 2>&1'
