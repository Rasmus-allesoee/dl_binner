"""Actual tiny origin derivation/reload with full zero-origin/shared denominators."""
import gzip,hashlib,json,sqlite3,sys,tempfile,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e021_skin_origin import derive,review


class Origin(unittest.TestCase):
    def fixture(self,root,duplicate=False):
        """Create synthetic pre-reviewed source inputs, not mock parser/evaluator calls."""
        src=root/'admission-v2';src.mkdir();m=root/'metadata';m.mkdir();(root/'skin').mkdir()
        dna='ACGT'*100+'NNNN'+'ACGT'*149;sha=hashlib.sha256(dna.encode()).hexdigest();ch=hashlib.sha256((dna+'ACGT'*50).encode()).hexdigest()
        samples=[1,13,14,15,16,17,18,19,20,28]
        for i in samples:(m/f'abundance{i}.tsv').write_text('g1\t1\ng2\t.5\n')
        pop=dict(domains={'g1':'2','g2':'2'},skin_positive_genomes=['g1','g2'],skin_sample_indices=samples,samples={str(i):dict(positive=['g1','g2'])for i in samples})
        den={g:dict(raw_bp=1200,exact_DNA_deduplicated_bp=1200,origin_queries=int(g=='g1'))for g in pop['domains']}
        if duplicate:den['g1']['exact_DNA_deduplicated_bp']=600
        refs=[dict(genomes=[g],record='r',bp=1200,molecule_header_evidence='unannotated',canonical_sha256=ch)for g in pop['domains']]
        audit=dict(status='EXACT_SOURCE_REVIEWED_TRUTH_PROVISIONAL',fixed_unmatched_or_unverified=0,observed_non_skin_positive=[],fixed_rows=1,anonymous=dict(bp=1000),GSA={})
        for name,d in [('population.json',pop),('denominators.json',den),('references.json',refs),('review.json',audit)]: (src/name).write_text(json.dumps(d))
        c=sqlite3.connect(src/'joins.sqlite');c.execute('CREATE TABLE fixed(anon,genome,record,start,end,sha,matched,verified)');c.execute('INSERT INTO fixed VALUES(?,?,?,?,?,?,?,?)',('PC0','g1','r',1,1000,sha,1,1));c.commit();c.close()
        with gzip.open(root/'skin/gsa.tsv.gz','wt')as f:f.write('>PC0\n'+dna+'\n')
        (root/'acquisition-clock.json').write_text(json.dumps(dict(started_epoch=time.time(),seconds=14400)))

    def test_complete_original_DNA_shared_reference_and_zero_origin_target(self):
        with tempfile.TemporaryDirectory()as tmp:
            r=Path(tmp);self.fixture(r);d=derive(r);a=review(r)
            self.assertEqual(a['status'],'ADMITTED_PROVIDED_ORIGIN_ORACLE_ONLY');self.assertEqual(a['targets'],2);self.assertEqual(a['full_target_bp'],2400);self.assertEqual(a['zero_origin_targets'],['g2']);self.assertEqual(a['counts']['quarantined_bp'],4);self.assertEqual(a['counts']['known_shared_queries'],1)
            self.assertNotIn('g1',(r/'model-input-v1/skin.fna').read_text());self.assertEqual(d['counts']['bp'],1000)
            # Current artifact reload refuses byte changes; it cannot silently admit a repair.
            with(r/'truth-origin-v1/queries.jsonl.gz').open('ab')as f:f.write(b'bad')
            with self.assertRaisesRegex(ValueError,'member changed'):review(r)

    def test_within_genome_duplicate_policy_is_not_silently_weakened(self):
        with tempfile.TemporaryDirectory()as tmp:
            r=Path(tmp);self.fixture(r,duplicate=True)
            with self.assertRaisesRegex(ValueError,'separate denominator'):derive(r)

if __name__=='__main__':unittest.main()
