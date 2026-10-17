"""Tiny real indexed source-admission and BGZF/header parsing contracts."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import time
import unittest
import zlib

sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import e014_oral_audit as audit
import e014_headers as headers
from e014_acquire import hashes


class AdmissionContracts(unittest.TestCase):
    def test_real_BGZF_text_binary_dictionary_and_mismatch_refusal(self):
        def block(reference):
            text=b'@HD\tVN:1.6\n@SQ\tSN:reference\tLN:20\n'
            payload=b'BAM\x01'+struct.pack('<i',len(text))+text+struct.pack('<ii',1,len(reference)+1)+reference+b'\0'+struct.pack('<i',20)
            c=zlib.compressobj(wbits=-15);raw=c.compress(payload)+c.flush()
            size=18+len(raw)+8
            return b'\x1f\x8b\x08\x04'+b'\0'*6+struct.pack('<H',6)+b'BC'+struct.pack('<HH',2,size-1)+raw+struct.pack('<II',zlib.crc32(payload),len(payload))
        result=headers.decode(block(b'reference'))
        self.assertEqual(result['references'],[dict(SN='reference',LN=20)])
        self.assertIsNone(headers.decode(block(b'reference')[:12]))
        with self.assertRaisesRegex(ValueError,'dictionary differs'):headers.decode(block(b'wrong'))

    def test_indexed_sequence_join_keeps_unknown_and_refuses_missing_full_denominators(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);m=root/'metadata';m.mkdir();oral=root/'oral';oral.mkdir()
            (root/'acquisition-clock.json').write_text(json.dumps(dict(started_epoch=time.time(),seconds=100)))
            (m/'setup-metadata.tsv').write_text('genome_ID\tOTU\tNCBI_ID\tnovelty_category\ngenome-A\tOTU\t42\tknown\n')
            (m/'setup-genome_to_id.tsv').write_text('genome-A\t/source/assembly.fa\n')
            for i in range(20):
                (m/f'setup-abundance{i}.tsv').write_text('genome-A\t1.0\n')
                if i in [6,7,8,13,14,15,16,17,18,19]:
                    (m/f'setup-taxonomic_profile_{i}.txt').write_text('42\tspecies\t2|42\tBacteria|A\t100\tgenome-A\n')
            header='#anonymous_contig_id genome_id tax_id contig_id number_reads start_position end_position\n'
            for name in ['gsa_pooled_mapping_fixed.tsv','gsa_pooled_mapping.tsv']:
                (oral/name).write_text(header+'PC0\tgenome-A\t42\treference\t1.0\t1\t8\n')
            with gzip.open(oral/'gsa.tsv.gz','wt') as f:f.write('>PC0\nACGTACGT\n')
            (oral/'gsa.fa').write_text('>reference_from_1_to_8_total_8\nACGTACGT\n>unknown_from_10_to_13_total_4\nAAAA\n')
            (root/'acquisition.json').write_text(json.dumps(dict(status='SUCCESS',files=[dict(path=str(p),hashes=hashes(p)) for p in oral.iterdir()])))
            nodes=root/'tiny-nodes.dmp';nodes.write_text('1\t|\t1\t|\n2\t|\t1\t|\n42\t|\t2\t|\n')
            result=audit.audit(root,taxonomy_path=nodes,taxonomy_expected=hashes(nodes))
            self.assertEqual(result['status'],'PROVISIONAL_NOT_ADMITTED')
            self.assertEqual(result['supplied_GSA']['bp'],12)
            self.assertEqual(result['supplied_GSA']['verified_publisher_sequence_join_bp'],8)
            self.assertEqual(result['supplied_GSA']['unresolved_source_join_bp'],4)
            self.assertEqual(result['fixed_unmatched'],0)
            self.assertFalse(result['full_reference_denominators_admitted'])
            self.assertEqual(result['population']['exact_simulator_genome_overlap_with_GI'],['genome-A'])

    def test_mapping_refuses_invalid_coordinates_instead_of_weakening_them(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x';p.write_text('#anonymous_contig_id genome_id tax_id contig_id number_reads start_position end_position\nPC0\tg\t1\tr\t1\t0\t4\n')
            with self.assertRaisesRegex(ValueError,'coordinate'):list(audit.mapping(p))
