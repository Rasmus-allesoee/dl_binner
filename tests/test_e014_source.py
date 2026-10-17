"""Real tiny tar/SQLite source verification; no ignored research assets required."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import sys
import tarfile
import tempfile
import time
import unittest

SCRIPTS = Path(__file__).absolute().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
import e014_source_audit as source
from e014_acquire import hashes


class SourceContracts(unittest.TestCase):
    def fixture(self, root, wrong=False, unsafe=False):
        """Create actual source bytes, receipt and disk-indexed independent GSA join."""
        (root/'metadata').mkdir();(root/'admission-v1').mkdir()
        (root/'acquisition-clock.json').write_text(json.dumps(dict(started_epoch=time.time(),seconds=5400)))
        (root/'metadata/setup-genome_to_id.tsv').write_text('g1\t/original/GCA1.fa\n')
        review=dict(fixed_unmatched=0,fixed_rows=1,supplied_GSA=dict(bp=3))
        (root/'admission-v1/review.json').write_text(json.dumps(review))
        db=sqlite3.connect(root/'admission-v1/joins.sqlite')
        db.execute('CREATE TABLE fixed(anon TEXT,genome TEXT,record TEXT,start INTEGER,end INTEGER,sha TEXT)')
        db.execute('INSERT INTO fixed VALUES(?,?,?,?,?,?)',('PC0','g1','CP1',2,4,hashlib.sha256(b'CGT' if not wrong else b'AAA').hexdigest()))
        db.commit();db.close()
        archive=root/'setup.tar.gz'
        with tarfile.open(archive,'w:gz') as tar:
            for name,raw in [('source_genomes/GCA1.fa',b'>CP1 plasmid\nACGTAC\n>copy\nACGTAC\n')]:
                info=tarfile.TarInfo('../escape.fa' if unsafe else name);info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
        (root/'source-acquisition.json').write_text(json.dumps(dict(status='SUCCESS',files=[dict(path=str(archive),hashes=hashes(archive))])))
        catalog=root/'old.json';catalog.write_text('{"files": []}')
        return catalog

    def test_exact_loci_full_and_deduplicated_denominators(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);catalog=self.fixture(root);result=source.audit(root,catalog)
            self.assertEqual(result['verified_GSA_loci'],1)
            lengths=json.loads((root/'source-validation-v1/denominators.json').read_text())['g1']
            self.assertEqual(lengths['raw_bp'],12);self.assertEqual(lengths['exact_DNA_deduplicated_bp'],6)
            references=json.loads((root/'source-validation-v1/references.json').read_text())
            self.assertEqual(references[0]['canonical_sha256'],hashlib.sha256(min('ACGTAC','GTACGT').encode()).hexdigest())
            self.assertIn('PROVISIONAL',result['status'])
            self.assertTrue((root/'admission-v1/joins.sqlite').is_file())

    def test_source_mismatch_and_unsafe_archive_refused(self):
        for wrong,unsafe in [(True,False),(False,True)]:
            with tempfile.TemporaryDirectory() as t:
                root=Path(t);catalog=self.fixture(root,wrong,unsafe)
                with self.assertRaisesRegex(ValueError,'substring DNA differs|Unsafe'):
                    source.audit(root,catalog)

    def test_coordinates_not_clipped(self):
        for start,end in [(0,3),(1,7),(3,2)]:
            with self.assertRaisesRegex(ValueError,'coordinate'):
                source.verify_locus('ACGTAC',start,end,hashlib.sha256(b'ACG').hexdigest())


if __name__=='__main__':unittest.main()
