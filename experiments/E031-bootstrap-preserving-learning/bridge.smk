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
    input: [u+'/audit/done.json' for u in ['E009-noGLM','E009-GLM','oral-noGLM']]

rule barrier:
    input: []
    output: 'barrier/done.json'
    log: 'logs/barrier.log'
    benchmark: 'benchmarks/barrier.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage barrier > {log} 2>&1'

rule E009_noGLM_teacher:
    input: ['barrier/done.json']
    output: 'actors/E009-noGLM/teacher/done.json'
    log: 'logs/E009_noGLM_teacher.log'
    benchmark: 'benchmarks/E009_noGLM_teacher.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage actor --unit E009-noGLM --role teacher > {log} 2>&1'

rule E009_noGLM_student:
    input: ['actors/E009-noGLM/teacher/done.json']
    output: 'actors/E009-noGLM/student/done.json'
    log: 'logs/E009_noGLM_student.log'
    benchmark: 'benchmarks/E009_noGLM_student.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage actor --unit E009-noGLM --role student > {log} 2>&1'

rule E009_GLM_teacher:
    input: ['actors/E009-noGLM/student/done.json']
    output: 'actors/E009-GLM/teacher/done.json'
    log: 'logs/E009_GLM_teacher.log'
    benchmark: 'benchmarks/E009_GLM_teacher.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage actor --unit E009-GLM --role teacher > {log} 2>&1'

rule E009_GLM_student:
    input: ['actors/E009-GLM/teacher/done.json']
    output: 'actors/E009-GLM/student/done.json'
    log: 'logs/E009_GLM_student.log'
    benchmark: 'benchmarks/E009_GLM_student.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage actor --unit E009-GLM --role student > {log} 2>&1'

rule oral_noGLM_teacher:
    input: ['actors/E009-GLM/student/done.json']
    output: 'actors/oral-noGLM/teacher/done.json'
    log: 'logs/oral_noGLM_teacher.log'
    benchmark: 'benchmarks/oral_noGLM_teacher.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage actor --unit oral-noGLM --role teacher > {log} 2>&1'

rule oral_noGLM_student:
    input: ['actors/oral-noGLM/teacher/done.json']
    output: 'actors/oral-noGLM/student/done.json'
    log: 'logs/oral_noGLM_student.log'
    benchmark: 'benchmarks/oral_noGLM_student.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage actor --unit oral-noGLM --role student > {log} 2>&1'

rule E009_noGLM_audit:
    input: ['actors/oral-noGLM/student/done.json']
    output: 'E009-noGLM/audit/done.json'
    log: 'logs/E009_noGLM_audit.log'
    benchmark: 'benchmarks/E009_noGLM_audit.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage audit --unit E009-noGLM > {log} 2>&1'

rule E009_GLM_audit:
    input: ['E009-noGLM/audit/done.json']
    output: 'E009-GLM/audit/done.json'
    log: 'logs/E009_GLM_audit.log'
    benchmark: 'benchmarks/E009_GLM_audit.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage audit --unit E009-GLM > {log} 2>&1'

rule oral_noGLM_audit:
    input: ['E009-GLM/audit/done.json']
    output: 'oral-noGLM/audit/done.json'
    log: 'logs/oral_noGLM_audit.log'
    benchmark: 'benchmarks/oral_noGLM_audit.tsv'
    threads: 4
    resources: mem_mb=26000
    shell: BASE+' --stage audit --unit oral-noGLM > {log} 2>&1'
