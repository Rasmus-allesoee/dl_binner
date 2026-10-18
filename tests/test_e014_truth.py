"""Actual origin-oracle quarantine, recovery, gzip/axis and refusal contracts."""
import copy
import gzip
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e014_oral_truth import acgt_intervals,validate_row,recovery,evaluate
from e014_acquire import hashes

REFS={'A|r':dict(genome='A',length=100),'B|s':dict(genome='B',length=20),'Z|z':dict(genome='Z',length=1000)}
TARGETS={'A':100,'Z':1000}


def row(ident,start=0,length=10,genome='A',shared=False):
    """A tiny literal provided-source query; no learned or marker labels."""
    return dict(id=ident,length=length,genome=genome,reference=genome+'|'+('r'if genome=='A'else's'),start=start,end=start+length,
                source_intervals=[[start,start+length]],quarantined_bp=0,shared_forward_query=shared,shared_complete_reference=False)


class OriginTruthContracts(unittest.TestCase):
    def test_localized_non_ACGT_and_invalid_coordinates(self):
        self.assertEqual(acgt_intervals('ACNNGTN',10),[[10,12],[14,16]])
        q=row('n',10,7);q.update(source_intervals=[[10,12],[14,16]],quarantined_bp=3)
        self.assertEqual(validate_row(q,REFS),4)
        for changed in [dict(source_intervals=[[10,13],[12,17]],quarantined_bp=0),dict(start=-1),dict(genome='B'),dict(quarantined_bp=-1)]:
            with self.assertRaises(ValueError):validate_row(q|changed,REFS)

    def test_source_unions_full_denominators_and_zero_origin(self):
        rows=[row('a'),row('b',5)];result=recovery(rows,{'a':0,'b':0},REFS,TARGETS,min_bin=1)
        self.assertEqual(result['recovery'][0]['recovered_bp'],15)
        self.assertEqual(result['recovery'][0]['whole_reference_R95'],.15)
        self.assertEqual(result['recovery'][1]['reference_bp'],1000);self.assertEqual(result['recovery'][1]['recovered_bp'],0)
        self.assertEqual(result['recovery_summary']['reference_bp'],1100)
        self.assertEqual(recovery(rows,{'a':0,'b':0},REFS,TARGETS)['recovery'][0]['recovered_bp'],0)

    def test_unknown_non_target_and_known_shared_keep_all_bin_DNA(self):
        rows=[row('a'),row('b',5,shared=True)]
        unknown=dict(id='u',length=2,genome=None,reference=None,start=0,end=2,source_intervals=[],quarantined_bp=2,shared_forward_query=False,shared_complete_reference=False)
        mixed=recovery(rows+[unknown],{'a':0,'b':0,'u':0},REFS,TARGETS,min_bin=1)
        self.assertEqual(mixed['bin_DNA_bp'][0],22);self.assertEqual(mixed['recovery'][0]['recovered_bp'],0)
        unassigned=recovery(rows+[unknown],{'a':0,'b':0,'u':None},REFS,TARGETS,min_bin=1)
        self.assertEqual(unassigned['accounting']['bp'],22);self.assertEqual(unassigned['accounting']['unassigned_bp'],2)
        self.assertEqual(unassigned['recovery'][0]['recovered_bp'],15)
        non_target=recovery(rows+[row('nt',0,2,'B')],{'a':0,'b':0,'nt':0},REFS,TARGETS,min_bin=1)
        self.assertEqual(non_target['recovery'][0]['recovered_bp'],0)
        masked=recovery(rows,{'a':0,'b':0},REFS,TARGETS,min_bin=1,mask_known_shared=True)
        self.assertEqual(masked['bin_DNA_bp'][0],20);self.assertEqual(masked['recovery'][0]['recovered_bp'],0)

    def test_actual_gzip_reader_ordered_axis_and_corrupt_bytes(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);artifact=root/'truth';artifact.mkdir();rows=[row('a'),row('b',5)]
            with gzip.open(artifact/'rows.jsonl.gz','wt')as f:
                for q in rows:f.write(json.dumps(q)+'\n')
            manifest=dict(kind='E014_provided_source_origin_oracle',rows=hashes(artifact/'rows.jsonl.gz'),references=REFS,targets=TARGETS)
            (artifact/'manifest.json').write_text(json.dumps(manifest))
            (artifact/'admission.json').write_text(json.dumps(dict(admitted=True,manifest=hashes(artifact/'manifest.json'))))
            partition=root/'partition.json';partition.write_text(json.dumps(dict(ids=['a','b'],assignment=[0,-1])))
            result=evaluate(artifact,partition,root/'ok');self.assertEqual(result['origin']['accounting']['bp'],20)
            partition.write_text(json.dumps(dict(ids=['b','a'],assignment=[0,0])))
            with self.assertRaisesRegex(ValueError,'ordered ID'):evaluate(artifact,partition,root/'wrong-order')
            partition.write_text(json.dumps(dict(ids=['a','b'],assignment=[0,0.5])))
            with self.assertRaisesRegex(ValueError,'partition labels'):evaluate(artifact,partition,root/'float')
            with (artifact/'rows.jsonl.gz').open('ab')as f:f.write(b'changed')
            with self.assertRaisesRegex(ValueError,'bytes differ'):evaluate(artifact,partition,root/'corrupt')

    def test_no_missing_duplicate_or_shrunken_denominator_fallback(self):
        for rows,assignments in [([row('a'),row('a')],{'a':0}),([row('a')],{'a':0,'extra':0}),([row('a')],{})]:
            with self.assertRaisesRegex(ValueError,'query'):recovery(rows,assignments,REFS,TARGETS,min_bin=1)
        with self.assertRaisesRegex(ValueError,'denominator'):recovery([row('a')],{'a':0},REFS,{'A':10},min_bin=1)


if __name__=='__main__':unittest.main()
