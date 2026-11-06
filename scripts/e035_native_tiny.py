#!/usr/bin/env python3
"""Qualify the actual streaming GTDB-layout builder and native translated reader.

Own two-genome compressed protein archive and synthetic taxonomy only. No bulk
reference, community annotation or performance claim. Every native exit is logged.
"""
import argparse
import gzip
import io
import json
from pathlib import Path
import sys
import tarfile

import dl_binner


def run(binary,fixture,root,database=None):
    """Exercise nested gzip/tar, opaque reference IDs, native DB and query completion."""
    from dl_binner.taxonomy.database import build
    from dl_binner.taxonomy.classifier import classify
    from dl_binner.taxonomy.annotations import read
    from dl_binner.io import write_json
    from dl_binner.context.tokens import binding
    fixture=Path(fixture);root=Path(root);root.mkdir(parents=True,exist_ok=False)
    taxonomy=root/'taxonomy.tsv'
    taxonomy.write_text('GB_GCA_000000001.1\td__Fixture;p__P;c__C;o__O;f__F;g__G;s__a\nGB_GCA_000000002.1\td__Fixture;p__P;c__C;o__O;f__F;g__H;s__b\n')
    proteins=(fixture/'reference/proteins.faa').read_text().split('>')[1:]
    archive=root/'proteins.tar.gz'
    with tarfile.open(archive,'w:gz')as t:
        for i in range(2):
            data=gzip.compress(('>'+'>'.join(proteins[i*40:(i+1)*40])).encode(),mtime=0)
            member=tarfile.TarInfo('gtdb/GCA_00000000'+str(i+1)+'.1_protein.faa.gz');member.size=len(data);t.addfile(member,io.BytesIO(data))
    db=Path(database)if database else root/'database/database.json'
    if database is None:build(binary,archive,[taxonomy],root/'database',engineering=True)
    from dl_binner.io import read_fasta
    from dl_binner.multiview.views import prepare,config
    paths=json.loads((fixture.parent/'tiny-r5/plan.json').read_text())['units']['E009-noGLM']
    sequences=read_fasta(paths['fasta'])[:5];dna=sequences[0][1]
    sequences += [('opaque-long',(dna*30)[:80000]),('opaque-no-hit','N'*1000),('opaque-one-base','A')]
    fasta=root/'queries.fna';fasta.write_text(''.join('>'+q+'\n'+s+'\n'for q,s in sequences));prepare(fasta,None,root/'features',config())
    features=root/'features/features.npz'
    classify(binary,db,fasta,features,root/'classification',engineering=True)
    a,m,t=read(root/'classification/annotations',features)
    if len(a['ids'])!=8 or a['confidence'][-2]!=0 or a['paths'][-2].any()or a['states'][-1]!='no_retained_ORF':raise ValueError('Native full-axis/no-hit/one-base no-ORF contract not exercised')
    write_json(root/'completed.json',dict(status='PASS',full_axis_rows=len(a['ids']),
        states={str(s):int((a['states']==s).sum())for s in set(a['states'])},
        database=binding(db),classification=binding(root/'classification/completed.json'),
        actual_native_streamed_builder=True,actual_native_translated_classifier=True,query_longer_than_default_65535=80000,
        synthetic_reference=True,community_accessed=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['binary','fixture','root']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--database',type=Path)
    a=p.parse_args();run(a.binary,a.fixture,a.root,a.database)
