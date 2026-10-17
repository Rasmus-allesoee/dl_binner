"""Actual anonymous-FASTA/SQLite derivative checks, including changed-DNA refusal."""
import gzip
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
import unittest

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
import e014_opaque_input as opaque
from e014_acquire import hashes


class OpaqueContracts(unittest.TestCase):
    def test_complete_DNA_kept_source_labels_outside_model_path(self):
        for mismatch in [False,True]:
            with tempfile.TemporaryDirectory()as t:
                root=Path(t);(root/'oral').mkdir();(root/'admission-v1').mkdir()
                (root/'acquisition-clock.json').write_text(json.dumps(dict(started_epoch=time.time(),seconds=100)))
                raw=root/'oral/gsa.tsv.gz'
                with gzip.open(raw,'wt')as f:f.write('>PC0\nACGTNN\n>PC1\nCGT\n')
                raw.with_suffix(raw.suffix+'.receipt.json').write_text(json.dumps(dict(hashes=hashes(raw))))
                db=sqlite3.connect(root/'admission-v1/joins.sqlite')
                db.execute('CREATE TABLE fixed(anon TEXT,genome TEXT,tax TEXT,record TEXT,start INTEGER,end INTEGER,sha TEXT)')
                for i,dna in enumerate(['ACGTNN','CGT']):
                    db.execute('INSERT INTO fixed VALUES(?,?,?,?,?,?,?)',(f'PC{i}','secret-genome','secret-taxon','secret-locus',1,len(dna),hashlib.sha256((dna if not mismatch else 'AAA').encode()).hexdigest()))
                db.commit();db.close()
                (root/'admission-v1/review.json').write_text(json.dumps(dict(fixed_unmatched=0,fixed_rows=2,anonymous_FASTA={},supplied_GSA=dict(bp=9),examples=[dict(id='empty-source',bp=0)])))
                if mismatch:
                    with self.assertRaisesRegex(ValueError,'join differs'):opaque.prepare(root)
                else:
                    result=opaque.prepare(root);text=(root/'model-input-v1/oral.fna').read_text()
                    self.assertNotIn('secret',text);self.assertNotIn('PC',text)
                    self.assertEqual(text,'>'+opaque.opaque('PC0')+'\nACGTNN\n>'+opaque.opaque('PC1')+'\nCGT\n')
                    self.assertEqual(result['bp'],9)
                    with gzip.open(root/'source-blind-join-v1.tsv.gz','rt')as f:self.assertIn('secret-genome',f.read())


if __name__=='__main__':unittest.main()
