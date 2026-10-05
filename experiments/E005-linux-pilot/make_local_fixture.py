#!/usr/bin/env python3
"""Create a small real-DNA data fixture for the unchanged production pilot DAG.

Use retained E005 DNA, tiny deterministic perfectly matching paired reads and
synthetic sampling sizes. Truth labels serve adapter contracts only; no scores
from this partial fixture are scientific pilot results or design criteria.
"""
import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from e005_smoke import sha, write
from dl_binner.io import read_fasta


def prepare(root):
    """Retain every selected DNA/label, all length strata and real two-sample inputs."""
    root = Path(root).absolute(); root.mkdir(exist_ok=False)
    with (ROOT/'experiments/E005-linux-pilot/pilot-contigs.tsv').open() as stream:
        records = list(csv.DictReader(stream, delimiter='\t'))
    dna = dict(read_fasta(ROOT/'artifacts/e005-linux-pilot/input/pilot/assembly.fna'))
    selected = {}
    for genome in ('OTU_97.20215.0', 'OTU_97.43909.0'):
        group = [r for r in records if r['genome_id'] == genome]
        total = 0
        for row in sorted(group, key=lambda r: (-int(r['bp']), r['contig_id'])):
            if total >= 250000:
                break
            selected[row['contig_id']] = row
            total += int(row['bp'])
        for low, high in ((1,500), (500,768), (768,1000), (1000,2500), (2500,10000)):
            eligible = [r for r in group if low <= int(r['bp']) < high]
            if eligible:
                row = min(eligible, key=lambda r: (int(r['bp']), r['contig_id']))
                selected[row['contig_id']] = row
    rows = [r for r in records if r['contig_id'] in selected]
    fasta, table = root/'assembly.fna', root/'contigs.tsv'
    with fasta.open('x') as stream:
        for row in rows:
            ident = row['contig_id']; stream.write('>'+ident+'\n'+dna[ident]+'\n')
    with table.open('x') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    complement = str.maketrans('ACGT', 'TGCA')
    longs = [r['contig_id'] for r in rows if int(r['bp']) >= 10000]
    samples = []
    for sample in (1, 4):
        path = root/f'sample_{sample}.fq'
        with path.open('x') as stream:
            for index in range(1, 101):
                seq = dna[longs[(index+sample) % len(longs)]]
                offset = (31*index+sample) % (len(seq)-300)
                a, b = seq[offset:offset+150], seq[offset+150:offset+300].translate(complement)[::-1]
                for mate, value in ((1,a), (2,b)):
                    stream.write(f'@S{sample}R{index}/{mate}\n{value}\n+\n'+150*'I'+'\n')
        samples.append(dict(sample=sample, column='GI_sample_'+str(sample), reads=str(path), sha256=sha(path)))
    write(root/'local-fixture.json', dict(fasta=str(fasta), contigs=str(table), samples=samples, sampled_pairs=32,
        max_source_pairs=200, preprocess_first=True, role='tiny partial real-DNA software fixture; no scientific utility or pilot score',
        binner_python=str(ROOT/'artifacts/e005-linux-pilot/env-local/bin/python'),
        workflow_python=str(ROOT/'artifacts/e005-linux-pilot/env-workflow-local/bin/python'),
        mapping_prefix=str(ROOT/'artifacts/e005-linux-pilot/env-mapping-local'),
        amber_python=str(ROOT/'artifacts/e005-linux-pilot/env-amber-local/bin/python'),
        amber_source=str(ROOT/'agent_context/tools_repo/AMBER_evaluation'),
        skipped=['Linux ABI/affinity', 'large original UCloud FASTQs and E001 installed-lock comparison',
                 'production 10-GB provisioning; fixture requires 1 GB'], native_workers_mocked=[]))
    print(dict(contigs=len(rows), bp=sum(int(r['bp']) for r in rows), fixture=str(root/'local-fixture.json')))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, required=True)
    prepare(p.parse_args().root)
