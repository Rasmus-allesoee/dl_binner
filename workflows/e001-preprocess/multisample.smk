"""Bounded sample lanes on one allocation; accepted sample 0 is external."""

PYTHON = config["mapping_python"]
HELPER = config["helper"]
CONFIG = config["runtime_config"]
SAMPLES = config["samples"]
LANES = config.get("max_concurrent_samples", 1)
SAMPLE_CPUS = config.get("sample_vcpus", 4)
SAMPLE_MEM = int(config.get("sample_ram_gb", 10) * 1000)

wildcard_constraints:
    sample="|".join(str(s) for s in SAMPLES)

def previous_sample(wildcards):
    """Start a new sample only after the previous sample in its lane finishes."""
    index = SAMPLES.index(int(wildcards.sample))
    return [] if index < LANES else [f"sample_{SAMPLES[index - LANES]}/preprocessing-summary.json"]

rule all:
    input: expand("sample_{sample}/preprocessing-summary.json", sample=SAMPLES)

rule download:
    input: previous_sample
    output: archive="sample_{sample}/source.tar.gz", metadata="sample_{sample}/acquisition.json"
    threads: 1
    resources: mem_mb=512, download_slots=1
    log: "sample_{sample}/logs/download.log"
    benchmark: "sample_{sample}/benchmarks/download.tsv"
    shell:
        "{PYTHON:q} -I {HELPER:q} --worker download --config {CONFIG:q} --sample {wildcards.sample} > {log:q} 2>&1"

rule extract:
    input: archive="sample_{sample}/source.tar.gz", metadata="sample_{sample}/acquisition.json"
    output: reads="sample_{sample}/reads.fq", metadata="sample_{sample}/reads.json"
    threads: 1
    resources: mem_mb=1000
    log: "sample_{sample}/logs/extract.log"
    benchmark: "sample_{sample}/benchmarks/extract.tsv"
    shell:
        "{PYTHON:q} -I {HELPER:q} --worker extract --config {CONFIG:q} --sample {wildcards.sample} > {log:q} 2>&1"

rule map_full:
    input: reads="sample_{sample}/reads.fq", metadata="sample_{sample}/reads.json", reference=config["reference"]
    output: bam="sample_{sample}/C0/mapped.bam", index="sample_{sample}/C0/mapped.bam.bai", qc="sample_{sample}/C0/qc.json"
    threads: SAMPLE_CPUS
    resources: mem_mb=SAMPLE_MEM
    log: "sample_{sample}/logs/map.log"
    benchmark: "sample_{sample}/benchmarks/map.tsv"
    shell:
        "{PYTHON:q} -I {HELPER:q} --worker map --config {CONFIG:q} --sample {wildcards.sample} > {log:q} 2>&1"

rule thin_and_report:
    input: bam="sample_{sample}/C0/mapped.bam", qc="sample_{sample}/C0/qc.json", reads="sample_{sample}/reads.json"
    output: bam="sample_{sample}/CT/mapped.bam", index="sample_{sample}/CT/mapped.bam.bai", qc="sample_{sample}/CT/qc.json", summary="sample_{sample}/preprocessing-summary.json"
    threads: 1
    resources: mem_mb=SAMPLE_MEM
    log: "sample_{sample}/logs/thin.log"
    benchmark: "sample_{sample}/benchmarks/thin.tsv"
    shell:
        "{PYTHON:q} -I {HELPER:q} --worker thin --config {CONFIG:q} --sample {wildcards.sample} > {log:q} 2>&1"
