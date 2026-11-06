"""Pinned MMseqs2 translated parent-DNA classification, with captured exits.

This module never downloads a database, calls cloud APIs or supplies benchmark
labels. A separately admitted database manifest must bind every consumed member.
Synthetic reference databases are allowed only for explicitly tiny engineering.
"""
import json
from pathlib import Path
import subprocess
import time

from ..context.tokens import binding
from ..io import write_json
from .annotations import query_fasta, prepare

VERSION = '8cc5ce367b5638c4306c2d7cfc652dd099a4643f'
OPTIONS = ['--lca-mode','3','--orf-filter','1','--tax-lineage','0','--tax-output-mode','0',
           '--majority','0.5','--vote-mode','1','--translation-table','11',
           '-s','2','-e','1','--max-seqs','300','--max-accept','30','--max-rejected','5',
           '--min-length','30','--split-mode','0','--split-memory-limit','16G',
           '--db-load-mode','2','--threads','4']


def command(binary, args, folder, name):
    """Capture a real native command, stderr and exact exit without retry/fallback."""
    folder = Path(folder); start = time.monotonic(); argv = [str(binary)]+list(map(str,args))
    with (folder/(name+'.log')).open('x') as log:
        result = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT)
    receipt = dict(argv=argv, exit_code=result.returncode, wall_seconds=time.monotonic()-start)
    write_json(folder/(name+'.exit.json'), receipt)
    if result.returncode: raise RuntimeError('MMseqs2 '+name+' failed; inspect '+str(folder/(name+'.log')))
    return receipt


def classify(binary, database, fasta, features, output, engineering=False):
    """Run one admitted query, preserving raw annotations and classifier evidence."""
    binary = Path(binary).absolute(); manifest = Path(database).absolute(); db = json.loads(manifest.read_text())
    if (set(db) != {'kind','version','binary','release','synthetic_reference','target','tree','files'}
            or db['kind'] != 'independent_taxonomy_database' or db['version'] != 1
            or db['binary'] != binding(binary) or db['synthetic_reference'] is not engineering):
        raise ValueError('Classifier/database provenance is not admitted for this scope')
    for name in list(db['files'])+[db['target'],db['tree']]:
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or not (manifest.parent/path).resolve().is_relative_to(manifest.parent):
            raise ValueError('Classifier database path escapes admitted members')
    if not db['files'] or db['target']+'.dbtype'not in db['files'] or any(binding(manifest.parent/name) != b for name,b in db['files'].items()):
        raise ValueError('Classifier database member bytes differ')
    if db['tree'] not in db['files']: raise ValueError('Classifier hierarchy not bound')
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    command(binary, ['version'], out, 'version')
    if (out/'version.log').read_text().strip() != VERSION: raise ValueError('Unsupported native classifier version')
    query = query_fasta(fasta, features, out/'query')
    if engineering and len(query['rows']) > 128: raise ValueError('Classifier tiny scope exceeded')
    command(binary, ['createdb',out/'query/queries.fna',out/'queryDB','--dbtype','2','--shuffle','0','--threads','4'], out, 'createdb')
    command(binary, ['taxonomy',out/'queryDB',manifest.parent/db['target'],out/'taxa',out/'tmp']+OPTIONS, out, 'taxonomy')
    command(binary, ['createtsv',out/'queryDB',out/'taxa',out/'taxonomy.tsv','--threads','4'], out, 'createtsv')
    from .normalization import complete
    reducers=sorted({p.resolve() for p in (out/'tmp').glob('*/orfs_h_swapped.index')})
    if len(reducers)!=1:raise ValueError('Exact native ORF reducer is missing/ambiguous')
    if not reducers[0].is_relative_to((out/'tmp').resolve()):raise ValueError('Native ORF reducer escaped this query attempt')
    complete(out/'taxonomy.tsv',out/'query/index.json',out/'queryDB.lookup',reducers[0],out/'complete.tsv')
    provenance = dict(classifier_version=VERSION, binary=binding(binary), database=binding(manifest),
                      query_sha256=query['query']['sha256'], synthetic_reference=engineering, truth_accessed=False,
                      zero_ORF_completion=binding(out/'complete.completion.json'))
    write_json(out/'provenance.json', provenance)
    result = prepare(out/'complete.tsv',out/'query/index.json',manifest.parent/db['tree'],features,out/'provenance.json',out/'annotations',out/'complete.completion.json')
    write_json(out/'completed.json', dict(status='PASS', annotations=binding(out/'annotations/completed.json'),
        options=OPTIONS, database=binding(manifest), binary=binding(binary), query_index=binding(out/'query/index.json'),
        native_exit_files={n:binding(out/(n+'.exit.json')) for n in ['version','createdb','taxonomy','createtsv']},
        raw=binding(out/'taxonomy.tsv'), engineering=engineering, truth_accessed=False))
    return result
