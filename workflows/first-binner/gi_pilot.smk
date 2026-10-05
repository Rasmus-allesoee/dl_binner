"""One frozen serial GI pilot; truth-consuming evaluation follows both verified exports."""
from pathlib import Path
from shlex import quote
from snakemake.io import multiext

BASE = Path(workflow.snakefile).resolve().parents[2]
CFG, T = config['resolved_config'], config['threads']
FASTA, TRAIN = config['fasta'], config['training']
SAMPLES = [str(s['sample']) for s in config['samples']]
HELPER = str(BASE/'scripts/e005_pilot.py')
ADAPTER = quote(config['python'])+' -I -u '+quote(HELPER)+' --config '+quote(CFG)
EVAL = quote(config['amber_python'])+' -I -u '+quote(HELPER)+' --config '+quote(CFG)
CLI = quote(config['python'])+' -I -m dl_binner --threads '+str(T)
GUARD = quote(config['python'])+' -I -u '+quote(str(BASE/'scripts/e005_rule.py'))+' --config '+quote(CFG)

rule all:
    input: 'raw.evaluation', 'learned.evaluation'

rule sample_reads:
    input: lambda w: next(s['reads'] for s in config['samples'] if str(s['sample']) == w.sample)
    output: 'reads/sample_{sample}.fq', 'reads/sample_{sample}.sample.json', 'reads/sample_{sample}.selection.tsv.gz'
    wildcard_constraints: sample='|'.join(SAMPLES)
    threads: T
    resources: mem_mb=8000
    log: 'logs/sample-{sample}.log'
    benchmark: 'benchmarks/sample-{sample}.tsv'
    shell: '{GUARD} --name sample-{wildcards.sample} --seconds 1200 -- {ADAPTER} sample --sample {wildcards.sample} > {log:q} 2>&1'

rule map_reads:
    input: 'reads/sample_{sample}.fq', 'reads/sample_{sample}.sample.json', fasta=FASTA
    output: 'mapping/sample_{sample}.bam', 'mapping/sample_{sample}.bam.bai', 'mapping/sample_{sample}.mapped.json'
    threads: T
    resources: mem_mb=8000
    log: 'logs/map-{sample}.log'
    benchmark: 'benchmarks/map-{sample}.tsv'
    shell: '{GUARD} --name map-{wildcards.sample} --seconds 1800 -- {ADAPTER} map --sample {wildcards.sample} > {log:q} 2>&1'

rule mean_depth:
    input: 'mapping/sample_{sample}.bam', 'mapping/sample_{sample}.bam.bai', 'mapping/sample_{sample}.mapped.json', fasta=FASTA
    output: 'depth/sample_{sample}.tsv', 'depth/sample_{sample}.depth.json'
    threads: T
    resources: mem_mb=4000
    log: 'logs/depth-{sample}.log'
    benchmark: 'benchmarks/depth-{sample}.tsv'
    shell: '{GUARD} --name depth-{wildcards.sample} --seconds 900 -- {ADAPTER} depth --sample {wildcards.sample} > {log:q} 2>&1'

rule combine_depth:
    input: expand('depth/sample_{sample}.tsv', sample=SAMPLES), expand('depth/sample_{sample}.depth.json', sample=SAMPLES), fasta=FASTA
    output: 'mean-depth.tsv', 'mean-depth.depth.json'
    threads: T
    resources: mem_mb=2000
    log: 'logs/combine.log'
    benchmark: 'benchmarks/combine.tsv'
    shell: '{GUARD} --name combine --seconds 120 -- {ADAPTER} combine > {log:q} 2>&1'

rule features:
    input: FASTA, 'mean-depth.tsv', 'mean-depth.depth.json'
    output: multiext('features', '.npz', '.json')
    threads: T
    resources: mem_mb=8000
    log: 'logs/features.log'
    benchmark: 'benchmarks/features.tsv'
    shell: '{GUARD} --name features --seconds 1800 -- {CLI} prepare --fasta {FASTA:q} --depth mean-depth.tsv --min-length 500 --output features.npz > {log:q} 2>&1'

rule train:
    input: multiext('features', '.npz', '.json'), training=TRAIN
    output: 'checkpoint.pt', 'checkpoint.json', 'checkpoint.reference.npz', 'checkpoint.reference.json'
    threads: T
    resources: mem_mb=8000
    log: 'logs/train.log'
    benchmark: 'benchmarks/train.tsv'
    shell: '{GUARD} --name train --seconds 900 -- {CLI} train --features features.npz --config {TRAIN:q} --output checkpoint.pt > {log:q} 2>&1'

rule embed:
    input: lambda w: ['features.npz', 'features.json']+(['checkpoint.pt', 'checkpoint.json'] if w.mode == 'learned' else [])
    output: multiext('{mode}.embeddings', '.npz', '.json')
    wildcard_constraints: mode='raw|learned'
    threads: T
    resources: mem_mb=8000
    log: 'logs/{mode}-embed.log'
    benchmark: 'benchmarks/{mode}-embed.tsv'
    params: branch=lambda w: '--checkpoint checkpoint.pt' if w.mode == 'learned' else '--raw'
    shell: '{GUARD} --name {wildcards.mode}-embed --seconds 300 -- {CLI} embed --features features.npz {params.branch} --output {output[0]:q} > {log:q} 2>&1'

rule cluster:
    input: multiext('{mode}.embeddings', '.npz', '.json')
    output: '{mode}.partition.json'
    wildcard_constraints: mode='raw|learned'
    threads: T
    resources: mem_mb=8000
    log: 'logs/{mode}-cluster.log'
    benchmark: 'benchmarks/{mode}-cluster.tsv'
    shell: '{GUARD} --name {wildcards.mode}-cluster --seconds 900 -- {CLI} cluster --embeddings {input[0]:q} --output {output:q} > {log:q} 2>&1'

rule export:
    input: 'features.npz', 'features.json', '{mode}.partition.json', fasta=FASTA
    output: directory('{mode}.export')
    wildcard_constraints: mode='raw|learned'
    threads: T
    resources: mem_mb=8000
    log: 'logs/{mode}-export.log'
    benchmark: 'benchmarks/{mode}-export.tsv'
    shell: '{GUARD} --name {wildcards.mode}-export --seconds 300 -- {CLI} export --features features.npz --partition {input[2]:q} --fasta {FASTA:q} --output {output:q} > {log:q} 2>&1'

rule verify:
    input: 'raw.export', 'learned.export', 'features.npz', 'features.json', 'mean-depth.tsv', 'checkpoint.json', 'checkpoint.reference.npz', 'checkpoint.reference.json', 'learned.embeddings.npz', 'learned.embeddings.json'
    output: 'verified.json'
    threads: T
    resources: mem_mb=8000
    log: 'logs/verify.log'
    benchmark: 'benchmarks/verify.tsv'
    shell: '{GUARD} --name verify --seconds 300 -- {ADAPTER} verify > {log:q} 2>&1'

rule evaluate:
    input: 'verified.json', '{mode}.export', truth=config['contigs']
    output: directory('{mode}.evaluation')
    wildcard_constraints: mode='raw|learned'
    threads: T
    resources: mem_mb=8000
    log: 'logs/{mode}-evaluate.log'
    benchmark: 'benchmarks/{mode}-evaluate.tsv'
    shell: '{GUARD} --name {wildcards.mode}-evaluate --seconds 900 -- {EVAL} evaluate --mode {wildcards.mode} > {log:q} 2>&1'
