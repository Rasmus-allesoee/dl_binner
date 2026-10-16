#!/usr/bin/env python3
"""Test a supplied production SCG profile on its generated consensus positive.

This is a native software contract, not biological accuracy, a training input,
or a community fit. Trusted cutoffs/coverage are unchanged. The fresh output
retains DNA, genes, domains, cache and exact source/asset bindings.
"""
import argparse
from pathlib import Path


def main():
    """Generate one reverse-translated consensus and run the real installed adapter."""
    import pyhmmer
    from dl_binner.candidate.markers import cache,load_cache
    from dl_binner.contracts import file_record,write_json
    from dl_binner.io import read_fasta
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['profile','manifest','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--threads',type=int,choices=range(1,9),default=2)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    with pyhmmer.plan7.HMMFile(a.profile)as stream:model=next(iter(stream))
    table=dict(zip('ACDEFGHIKLMNPQRSTVWY',
        ['GCT','TGT','GAT','GAA','TTT','GGT','CAT','ATT','AAA','CTG','ATG','AAT','CCT','CAA','CGT','TCT','ACT','GTT','TGG','TAT']))
    sequence='TAATGATAA'*20+'AGGAGGAAAAAAATG'+''.join(table.get(x,'NNN')for x in model.consensus.upper())+'TAA'+'TAATGATAA'*20
    fasta=a.output/'hmm-consensus.fna'
    fasta.write_text('>generated_'+model.name.decode()+'_positive_software_fixture\n'+sequence+'\n')
    destination=a.output/'cache';destination.mkdir()
    cache(fasta,a.profile,a.manifest,destination,a.threads)
    evidence=load_cache(destination,fasta,[i for i,_ in read_fasta(fasta)])
    import json
    domains=json.loads((destination/'domains.json').read_text())
    if not any(d['marker']==model.name.decode()for d in domains):
        raise ValueError('Expected production-profile consensus positive was not detected; no threshold relaxation')
    write_json(a.output/'observed.json',dict(status='passed',kind='production_profile_positive_software_contract',
        DNA=file_record(fasta),profile=file_record(a.profile),manifest=file_record(a.manifest),
        genes=evidence['gene_count'],domains=len(domains),profile_count=evidence['profile_count'],
        canonical_families=evidence['canonical_families'],cache=file_record(destination/'cache.json'),
        scientific_quality_assessed=False,source=file_record(__file__),
        scope='Own-consensus generated software positive; unchanged trusted cutoffs/.5 coverage, no genome recovery claim'))


if __name__=='__main__':main()
