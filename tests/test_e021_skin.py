"""Actual strict coordinate/sequence/source-stream helpers; no retained DNA required."""
import hashlib,io,json
from pathlib import Path
import sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e021_skin import HashReader,opaque,sketch,RC,population,raw_mapping
from e014_source_audit import records,verify_locus
from e014_oral_truth import acgt_intervals,validate_row


class Skin(unittest.TestCase):
    def test_exact_ambiguity_and_full_provided_coordinate_contract(self):
        dna='ACGTNNRYACGT';h=hashlib.sha256(dna[2:9].encode()).hexdigest();verify_locus(dna,3,9,h)
        for a,b in [(0,5),(1,13),(4,3)]:
            with self.assertRaises(ValueError):verify_locus(dna,a,b,h)
        with self.assertRaises(ValueError):verify_locus(dna,3,9,'a'*64)
        row=dict(id='Copaque',length=len(dna),quarantined_bp=4,shared_forward_query=False,shared_complete_reference=True,genome='g',reference='g|r',start=0,end=len(dna),source_intervals=acgt_intervals(dna,0))
        self.assertEqual(validate_row(row,{'g|r':dict(genome='g',length=12)}),8)
        with self.assertRaises(ValueError):validate_row(row|dict(quarantined_bp=0),{'g|r':dict(genome='g',length=12)})
        self.assertEqual(list(records(b'>r chromosome\nACGTNR\n')),[('r chromosome','ACGTNR')])
        with self.assertRaises(ValueError):list(records(b'ACGT\n>r\nACGT'))
        with self.assertRaises(ValueError):list(records(b'>r\nACG-'))

    def test_complete_compressed_stream_hashing_and_source_blind_ID(self):
        data=b'fixed compressed payload\x00\x01';reader=HashReader(io.BytesIO(data));self.assertEqual(reader.read(3)+reader.read(),data)
        self.assertEqual(reader.result(),dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),md5=hashlib.md5(data).hexdigest()))
        self.assertEqual(opaque('PC123'),opaque('PC123'));self.assertNotIn('PC123',opaque('PC123'));self.assertEqual(len(opaque('PC123')),65)
        with self.assertRaises(ValueError):opaque('unsafe id')

    def test_actual_29_sample_profile_headers_and_publisher_skin_join(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);m=root/'metadata';m.mkdir()
            (m/'genome_to_id.tsv').write_text('g\t/source/g.fa\n')
            (m/'metadata.tsv').write_text('genome_ID\tNCBI_ID\ng\t10\n')
            for j in range(29):
                (m/f'abundance{j}.tsv').write_text('g\t1.0\n')
                (m/f'taxonomic_profile_{j}.txt').write_text('@SampleID: '+str(j)+'\n@@TAXID\tRANK\tTAXPATH\tTAXPATHSN\tPERCENTAGE\t_CAMI_GENOMEID\n2\tsuperkingdom\t2\tBacteria\t100\n10\tspecies\t2|10\tBacteria|test\t100\tg\n')
            n=root/'artifacts/e001-taxonomy-reviewed/nodes.dmp';n.parent.mkdir(parents=True);n.write_text('1 | 1 |\n2 | 1 |\n10 | 2 |\n')
            policy=root/'experiments/E001-coverage-thinning/taxonomy-policy.json';policy.parent.mkdir(parents=True);policy.write_text(json.dumps(dict(members={'nodes.dmp':dict(size=n.stat().st_size,sha256=hashlib.sha256(n.read_bytes()).hexdigest())})))
            pub=root/'artifacts/e021-frozen-sequence-hybrid/metadata-public/README.md';pub.parent.mkdir(parents=True);pub.write_text('Skin samples: 1,13,14,15,16,17,18,19,20,28')
            result=population(m,root);self.assertEqual(result['skin_positive_genomes'],['g']);self.assertEqual(len(result['samples']),29);self.assertEqual(result['domains']['g'],'2')

    def test_pinned_headerless_raw_map_is_distinct_and_strict(self):
        with tempfile.TemporaryDirectory()as tmp:
            p=Path(tmp)/'raw.tsv';p.write_text('PC0\tg\t2\tr\t1.0\t1\t12\n')
            self.assertEqual(list(raw_mapping(p)),[('PC0','g','2','r',1,12,'1.0')])
            for bad in ['#anonymous_contig_id genome_id tax_id contig_id number_reads start_position end_position\n','PC0\tg\t2\tr\tNaN\t1\t12\n','PC0\tg\t2\tr\t1\t0\t12\n','PC0\tg\t2\tr\t1\t1\t12\textra\n']:
                p.write_text(bad)
                with self.assertRaises(ValueError):list(raw_mapping(p))

    def test_shared_sequence_screen_is_strand_stable_and_bounded(self):
        dna='AACCTG'*40+'ACGCGT'+'AGGCTA'*45
        a=sketch(dna);b=sketch(dna.translate(RC)[::-1]);self.assertEqual(a,b);self.assertGreater(len(a),0);self.assertLessEqual(len(a),128);self.assertEqual(sketch('N'*500),[])


if __name__=='__main__':unittest.main()
