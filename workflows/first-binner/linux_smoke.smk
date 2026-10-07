"""Installed binner Linux smoke, cached real DNA and explicit synthetic depths."""
from pathlib import Path
from shlex import quote
from snakemake.io import multiext

CLI = quote(config['python'])+' -I -m dl_binner --threads '+str(config['threads'])
CFG = config['resolved_config']
VERIFY = str(Path(workflow.snakefile).resolve().parents[2]/'scripts/e005_smoke.py')
FASTA, DEPTH, TRAIN = config['fasta'], config['depth'], config['training']
CACHE, RECEIPT, PANEL = (config[k] for k in ('tnf_cache', 'tnf_receipt', 'tnf_panel'))

rule all:
    input: 'verified.json'

rule features:
    input: FASTA, DEPTH, CACHE, RECEIPT, PANEL
    output: multiext('features', '.npz', '.json')
    threads: config['threads']
    resources: mem_mb=2000
    log: 'logs/features.log'
    benchmark: 'benchmarks/features.tsv'
    shell: '{CLI} prepare --fasta {FASTA:q} --depth {DEPTH:q} --min-length 500 --tnf-cache {CACHE:q} --tnf-receipt {RECEIPT:q} --tnf-panel {PANEL:q} --output {output[0]:q} > {log:q} 2>&1'

rule fresh_tiny_reader:
    input: config['fresh_fasta']
    output: multiext('fresh', '.npz', '.json')
    threads: config['threads']
    resources: mem_mb=2000
    log: 'logs/fresh.log'
    benchmark: 'benchmarks/fresh.tsv'
    shell: '{CLI} prepare --fasta {input:q} --min-length 500 --output {output[0]:q} > {log:q} 2>&1'

rule train:
    input: multiext('features', '.npz', '.json'), training=TRAIN
    output: 'checkpoint.pt', 'checkpoint.json', 'checkpoint.reference.npz', 'checkpoint.reference.json'
    threads: config['threads']
    resources: mem_mb=8000
    log: 'logs/train.log'
    benchmark: 'benchmarks/train.tsv'
    shell: '{CLI} train --features features.npz --config {TRAIN:q} --output checkpoint.pt > {log:q} 2>&1'

rule embed:
    input: lambda w: ['features.npz', 'features.json'] + (['checkpoint.pt', 'checkpoint.json'] if w.mode == 'learned' else [])
    output: multiext('{mode}.embeddings', '.npz', '.json')
    wildcard_constraints: mode='raw|learned'
    threads: config['threads']
    resources: mem_mb=8000
    log: 'logs/{mode}.embedding.log'
    benchmark: 'benchmarks/{mode}.embedding.tsv'
    params: branch=lambda w: '--checkpoint checkpoint.pt' if w.mode == 'learned' else '--raw'
    shell: '{CLI} embed --features features.npz {params.branch} --output {output[0]:q} > {log:q} 2>&1'

rule cluster:
    input: multiext('{mode}.embeddings', '.npz', '.json')
    output: '{mode}.partition.json'
    wildcard_constraints: mode='raw|learned'
    threads: config['threads']
    resources: mem_mb=2000
    log: 'logs/{mode}.cluster.log'
    benchmark: 'benchmarks/{mode}.cluster.tsv'
    shell: '{CLI} cluster --embeddings {input[0]:q} --output {output:q} > {log:q} 2>&1'

rule export:
    input: 'features.npz', 'features.json', '{mode}.partition.json', fasta=FASTA
    output: directory('{mode}.export')
    wildcard_constraints: mode='raw|learned'
    threads: config['threads']
    resources: mem_mb=2000
    log: 'logs/{mode}.export.log'
    benchmark: 'benchmarks/{mode}.export.tsv'
    shell: '{CLI} export --features features.npz --partition {input[2]:q} --fasta {FASTA:q} --output {output:q} > {log:q} 2>&1'

rule verify:
    input: 'features.npz', 'features.json', 'fresh.npz', 'fresh.json', 'raw.export', 'learned.export', 'learned.embeddings.npz', 'learned.embeddings.json', 'checkpoint.reference.npz', 'checkpoint.reference.json'
    output: 'verified.json', 'raw.accounting.json', 'learned.accounting.json'
    threads: config['threads']
    resources: mem_mb=2000
    log: 'logs/verify.log'
    benchmark: 'benchmarks/verify.tsv'
    shell: '{config[python]:q} -I -u {VERIFY:q} --config {CFG:q} --output verified.json > {log:q} 2>&1'
