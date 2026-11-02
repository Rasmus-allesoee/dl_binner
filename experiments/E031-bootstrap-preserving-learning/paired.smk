"""Serial bounded E031 research DAG; no automatic retry or hidden science."""
import json
from pathlib import Path
import shlex
P=json.loads(Path(config['plan']).read_text())
ENG=str(config.get('engineering','false')).lower()=='true'
FLAG=' --engineering' if ENG else ''
q=lambda x:shlex.quote(str(x))
BASE=q(P['python'])+' -I -B '+q(P['worker'])+' --plan '+q(config['plan'])+FLAG
rule all:
    input: [u+'/paired/done.json' for u in ['E009-noGLM','E009-GLM','oral-noGLM']]

rule barrier:
    input: []
    output: 'barrier/done.json'
    log: 'logs/barrier.log'
    benchmark: 'benchmarks/barrier.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage barrier > {log} 2>&1'

rule E009_noGLM_confidence:
    input: ['barrier/done.json']
    output: 'E009-noGLM/confidence/done.json'
    log: 'logs/E009_noGLM_confidence.log'
    benchmark: 'benchmarks/E009_noGLM_confidence.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage confidence --unit E009-noGLM > {log} 2>&1'

rule E009_noGLM_train:
    input: ['E009-noGLM/confidence/done.json']
    output: 'E009-noGLM/train/done.json'
    log: 'logs/E009_noGLM_train.log'
    benchmark: 'benchmarks/E009_noGLM_train.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage train --unit E009-noGLM > {log} 2>&1'

rule E009_noGLM_embed:
    input: ['E009-noGLM/train/done.json']
    output: 'E009-noGLM/embed/done.json'
    log: 'logs/E009_noGLM_embed.log'
    benchmark: 'benchmarks/E009_noGLM_embed.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage embed --unit E009-noGLM > {log} 2>&1'

rule E009_noGLM_graph:
    input: ['E009-noGLM/embed/done.json']
    output: 'E009-noGLM/graph/done.json'
    log: 'logs/E009_noGLM_graph.log'
    benchmark: 'benchmarks/E009_noGLM_graph.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage graph --unit E009-noGLM > {log} 2>&1'

rule E009_noGLM_retrieve:
    input: ['E009-noGLM/e023/done.json']
    output: 'E009-noGLM/retrieve/done.json'
    log: 'logs/E009_noGLM_retrieve.log'
    benchmark: 'benchmarks/E009_noGLM_retrieve.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage retrieve --unit E009-noGLM > {log} 2>&1'

rule E009_noGLM_forest:
    input: ['E009-noGLM/retrieve/done.json']
    output: 'E009-noGLM/forest/done.json'
    log: 'logs/E009_noGLM_forest.log'
    benchmark: 'benchmarks/E009_noGLM_forest.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage forest --unit E009-noGLM > {log} 2>&1'

rule E009_noGLM_construct:
    input: ['E009-noGLM/forest/done.json']
    output: 'E009-noGLM/construct/done.json'
    log: 'logs/E009_noGLM_construct.log'
    benchmark: 'benchmarks/E009_noGLM_construct.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage construct --unit E009-noGLM > {log} 2>&1'

rule E009_noGLM_export:
    input: ['E009-noGLM/construct/done.json']
    output: 'E009-noGLM/export/done.json'
    log: 'logs/E009_noGLM_export.log'
    benchmark: 'benchmarks/E009_noGLM_export.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage export --unit E009-noGLM > {log} 2>&1'

rule E009_noGLM_audit:
    input: ['E009-noGLM/export/done.json']
    output: 'E009-noGLM/audit/done.json'
    log: 'logs/E009_noGLM_audit.log'
    benchmark: 'benchmarks/E009_noGLM_audit.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage audit --unit E009-noGLM > {log} 2>&1'

rule E009_GLM_confidence:
    input: ['E009-noGLM/paired/done.json']
    output: 'E009-GLM/confidence/done.json'
    log: 'logs/E009_GLM_confidence.log'
    benchmark: 'benchmarks/E009_GLM_confidence.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage confidence --unit E009-GLM > {log} 2>&1'

rule E009_GLM_train:
    input: ['E009-GLM/confidence/done.json']
    output: 'E009-GLM/train/done.json'
    log: 'logs/E009_GLM_train.log'
    benchmark: 'benchmarks/E009_GLM_train.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage train --unit E009-GLM > {log} 2>&1'

rule E009_GLM_embed:
    input: ['E009-GLM/train/done.json']
    output: 'E009-GLM/embed/done.json'
    log: 'logs/E009_GLM_embed.log'
    benchmark: 'benchmarks/E009_GLM_embed.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage embed --unit E009-GLM > {log} 2>&1'

rule E009_GLM_graph:
    input: ['E009-GLM/embed/done.json']
    output: 'E009-GLM/graph/done.json'
    log: 'logs/E009_GLM_graph.log'
    benchmark: 'benchmarks/E009_GLM_graph.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage graph --unit E009-GLM > {log} 2>&1'

rule E009_GLM_retrieve:
    input: ['E009-GLM/e023/done.json']
    output: 'E009-GLM/retrieve/done.json'
    log: 'logs/E009_GLM_retrieve.log'
    benchmark: 'benchmarks/E009_GLM_retrieve.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage retrieve --unit E009-GLM > {log} 2>&1'

rule E009_GLM_forest:
    input: ['E009-GLM/retrieve/done.json']
    output: 'E009-GLM/forest/done.json'
    log: 'logs/E009_GLM_forest.log'
    benchmark: 'benchmarks/E009_GLM_forest.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage forest --unit E009-GLM > {log} 2>&1'

rule E009_GLM_construct:
    input: ['E009-GLM/forest/done.json']
    output: 'E009-GLM/construct/done.json'
    log: 'logs/E009_GLM_construct.log'
    benchmark: 'benchmarks/E009_GLM_construct.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage construct --unit E009-GLM > {log} 2>&1'

rule E009_GLM_export:
    input: ['E009-GLM/construct/done.json']
    output: 'E009-GLM/export/done.json'
    log: 'logs/E009_GLM_export.log'
    benchmark: 'benchmarks/E009_GLM_export.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage export --unit E009-GLM > {log} 2>&1'

rule E009_GLM_audit:
    input: ['E009-GLM/export/done.json']
    output: 'E009-GLM/audit/done.json'
    log: 'logs/E009_GLM_audit.log'
    benchmark: 'benchmarks/E009_GLM_audit.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage audit --unit E009-GLM > {log} 2>&1'

rule oral_noGLM_confidence:
    input: ['E009-GLM/paired/done.json']
    output: 'oral-noGLM/confidence/done.json'
    log: 'logs/oral_noGLM_confidence.log'
    benchmark: 'benchmarks/oral_noGLM_confidence.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage confidence --unit oral-noGLM > {log} 2>&1'

rule oral_noGLM_train:
    input: ['oral-noGLM/confidence/done.json']
    output: 'oral-noGLM/train/done.json'
    log: 'logs/oral_noGLM_train.log'
    benchmark: 'benchmarks/oral_noGLM_train.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage train --unit oral-noGLM > {log} 2>&1'

rule oral_noGLM_embed:
    input: ['oral-noGLM/train/done.json']
    output: 'oral-noGLM/embed/done.json'
    log: 'logs/oral_noGLM_embed.log'
    benchmark: 'benchmarks/oral_noGLM_embed.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage embed --unit oral-noGLM > {log} 2>&1'

rule oral_noGLM_graph:
    input: ['oral-noGLM/embed/done.json']
    output: 'oral-noGLM/graph/done.json'
    log: 'logs/oral_noGLM_graph.log'
    benchmark: 'benchmarks/oral_noGLM_graph.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage graph --unit oral-noGLM > {log} 2>&1'

rule oral_noGLM_retrieve:
    input: ['oral-noGLM/e023/done.json']
    output: 'oral-noGLM/retrieve/done.json'
    log: 'logs/oral_noGLM_retrieve.log'
    benchmark: 'benchmarks/oral_noGLM_retrieve.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage retrieve --unit oral-noGLM > {log} 2>&1'

rule oral_noGLM_forest:
    input: ['oral-noGLM/retrieve/done.json']
    output: 'oral-noGLM/forest/done.json'
    log: 'logs/oral_noGLM_forest.log'
    benchmark: 'benchmarks/oral_noGLM_forest.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage forest --unit oral-noGLM > {log} 2>&1'

rule oral_noGLM_construct:
    input: ['oral-noGLM/forest/done.json']
    output: 'oral-noGLM/construct/done.json'
    log: 'logs/oral_noGLM_construct.log'
    benchmark: 'benchmarks/oral_noGLM_construct.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage construct --unit oral-noGLM > {log} 2>&1'

rule oral_noGLM_export:
    input: ['oral-noGLM/construct/done.json']
    output: 'oral-noGLM/export/done.json'
    log: 'logs/oral_noGLM_export.log'
    benchmark: 'benchmarks/oral_noGLM_export.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage export --unit oral-noGLM > {log} 2>&1'

rule oral_noGLM_audit:
    input: ['oral-noGLM/export/done.json']
    output: 'oral-noGLM/audit/done.json'
    log: 'logs/oral_noGLM_audit.log'
    benchmark: 'benchmarks/oral_noGLM_audit.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage audit --unit oral-noGLM > {log} 2>&1'

rule E009_noGLM_e023:
    input: ['E009-noGLM/graph/done.json']
    output: 'E009-noGLM/e023/done.json'
    log: 'logs/E009_noGLM_e023.log'
    benchmark: 'benchmarks/E009_noGLM_e023.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage e023 --unit E009-noGLM > {log} 2>&1'

rule E009_noGLM_paired:
    input: ['E009-noGLM/e023/done.json', 'E009-noGLM/audit/done.json']
    output: 'E009-noGLM/paired/done.json'
    log: 'logs/E009_noGLM_paired.log'
    benchmark: 'benchmarks/E009_noGLM_paired.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage paired --unit E009-noGLM > {log} 2>&1'


rule E009_GLM_e023:
    input: ['E009-GLM/graph/done.json']
    output: 'E009-GLM/e023/done.json'
    log: 'logs/E009_GLM_e023.log'
    benchmark: 'benchmarks/E009_GLM_e023.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage e023 --unit E009-GLM > {log} 2>&1'

rule E009_GLM_paired:
    input: ['E009-GLM/e023/done.json', 'E009-GLM/audit/done.json']
    output: 'E009-GLM/paired/done.json'
    log: 'logs/E009_GLM_paired.log'
    benchmark: 'benchmarks/E009_GLM_paired.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage paired --unit E009-GLM > {log} 2>&1'


rule oral_noGLM_e023:
    input: ['oral-noGLM/graph/done.json']
    output: 'oral-noGLM/e023/done.json'
    log: 'logs/oral_noGLM_e023.log'
    benchmark: 'benchmarks/oral_noGLM_e023.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage e023 --unit oral-noGLM > {log} 2>&1'

rule oral_noGLM_paired:
    input: ['oral-noGLM/e023/done.json', 'oral-noGLM/audit/done.json']
    output: 'oral-noGLM/paired/done.json'
    log: 'logs/oral_noGLM_paired.log'
    benchmark: 'benchmarks/oral_noGLM_paired.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage paired --unit oral-noGLM > {log} 2>&1'
