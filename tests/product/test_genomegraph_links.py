"""Real collated BAM contracts, coordinate evidence and malformed-input refusal."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pysam

from dl_binner.genomegraph import links as g


def fixture(root,changes=None,reverse_header=False):
    """Separate mates in actual BAM order; independently define expected links."""
    root=Path(root);ids=['opaque-A','opaque-B','opaque-C','short'];lengths=np.array([5000,5000,5000,200],np.int64);valid=np.array([True,True,True,False])
    sq=[dict(SN=i,LN=int(l)) for i,l in zip(ids,lengths)]
    if reverse_header:sq=sq[::-1]
    byname={r['SN']:i for i,r in enumerate(sq)}
    templates=[('cal-0',0,1000,0,1250),('cal-1',0,1100,0,1350)]+[(f'opaque-{k}',0,4800+k,1,k) for k in range(3)]
    templates.append(('duplicate-coordinate',0,4800,1,0))
    bam=root/'input.bam'
    with pysam.AlignmentFile(bam,'wb',header=dict(HD=dict(VN='1.6',SO='unsorted'),SQ=sq)) as stream:
        records=[]
        for name,i,at,j,bt in templates:
            pair=[]
            for role,ref,pos,mref,mpos in [(1,i,at,j,bt),(2,j,bt,i,at)]:
                r=pysam.AlignedSegment(stream.header);r.query_name=name;r.flag=1|(64|32 if role==1 else 128|16)
                r.reference_id=byname[ids[ref]];r.reference_start=pos;r.next_reference_id=byname[ids[mref]];r.next_reference_start=mpos
                r.mapping_quality=60;r.cigarstring='150M';r.query_sequence='A'*150;r.query_qualities=pysam.qualitystring_to_array('I'*150);r.set_tag('NM',0)
                if changes is not None:changes(name,role,r)
                pair.append(r)
            records.append(pair)
        # Real external full collation must join these distant mates.
        for role in range(2):
            for pair in records:stream.write(pair[role])
    return bam,ids,lengths,valid


def tiny_policy():
    """Only the minimum calibration count is reduced for this engineering fixture."""
    return dict(g.DEFAULT,min_calibration=2)


class PhysicalLinks(unittest.TestCase):
    def test_actual_collator_independent_mates_dedup_and_reordered_dictionary(self):
        for reverse in [False,True]:
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder);bam,ids,lengths,valid=fixture(root,reverse_header=reverse)
                receipt=g.extract(bam,ids,lengths,valid,'sample-X',root/'links',threads=2,cfg=tiny_policy());a,m=g.read(root/'links')
                self.assertEqual(receipt['collator_exit'],0);self.assertEqual(receipt['calibration']['insert_limit'],400)
                self.assertEqual(a['edges'].tolist(),[[0,1]]);self.assertEqual(a['support'].tolist(),[3]);self.assertEqual(a['orientations'].tolist(),[1])
                self.assertEqual(receipt['aggregation']['duplicate_coordinate_observations'],1)
                self.assertEqual(m['counters']['templates'],6);self.assertFalse(m['read_names_or_DNA_retained'])
                self.assertEqual(m['pipeline_workers'],2)

    def test_low_MAPQ_mate_excluded_and_no_single_mate_pointer_substitution(self):
        for field in ['mapq','pointer','role']:
            with tempfile.TemporaryDirectory() as folder:
                root=Path(folder)
                def change(name,role,r):
                    if name=='opaque-2' and role==2:
                        if field=='mapq':r.mapping_quality=0
                        elif field=='pointer':r.next_reference_start+=1
                        else:r.flag=(r.flag&~128)|64
                bam,ids,lengths,valid=fixture(root,change);g.extract(bam,ids,lengths,valid,'sample-X',root/'links',threads=2,cfg=tiny_policy())
                a,m=g.read(root/'links');self.assertEqual(len(a['edges']),0)
                self.assertEqual(m['aggregation']['edge_exclusions']['below_unique_support'],1)

    def test_missing_NM_refuses_and_preserves_unsealed_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            def change(name,role,r):
                if name=='opaque-0' and role==2:r.set_tag('NM',None)
            bam,ids,lengths,valid=fixture(root,change)
            with self.assertRaisesRegex(ValueError,'missing NM'):g.extract(bam,ids,lengths,valid,'sample-X',root/'links',threads=2,cfg=tiny_policy())
            self.assertTrue((root/'links/failure.json').exists());self.assertFalse((root/'links/completed.json').exists())
            with self.assertRaises(FileNotFoundError):g.read(root/'links')

    def test_axis_corruption_refused_and_no_existing_output_retry(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);bam,ids,lengths,valid=fixture(root);wrong=lengths.copy();wrong[0]-=1
            with self.assertRaisesRegex(ValueError,'lengths differ'):g.extract(bam,ids,wrong,valid,'sample-X',root/'bad',threads=2,cfg=tiny_policy())
            with self.assertRaises(FileExistsError):g.extract(bam,ids,lengths,valid,'sample-X',root/'bad',threads=2,cfg=tiny_policy())

    def test_orientation_conflict_and_repeat_hub_do_not_become_positive_links(self):
        cfg=dict(tiny_policy(),maximum_degree=2);rows=[]
        for j in [1,2,3]:
            for k in range(3):rows.append((0,j,100+k,k,100,1))
        a=np.array(rows,g.OBS);e,_,_,audit=g.aggregate(a,400,np.full(4,1000),np.ones(4,bool),cfg)
        self.assertEqual(len(e),0);self.assertEqual(audit['hub_nodes'],1)
        a=np.array([(0,1,k,k,100,k%2) for k in range(6)],g.OBS)
        e,_,_,audit=g.aggregate(a,400,np.full(4,1000),np.ones(4,bool),cfg)
        self.assertEqual(len(e),0);self.assertEqual(audit['edge_exclusions']['orientation_conflict'],1)

    def test_per_sample_opaque_names_pool_and_assembly_scoped_utility(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);folders=[]
            for sample in ['one','two']:
                r=root/sample;r.mkdir();bam,ids,lengths,valid=fixture(r)
                g.extract(bam,ids,lengths,valid,sample,r/'links',threads=2,cfg=tiny_policy());folders.append(r/'links')
            g.pool(folders,['one','two'],root/'pooled');a,m=g.read(root/'pooled')
            self.assertEqual(a['support'].tolist(),[6]);self.assertEqual(a['sample_support'].tolist(),[[3,3]])
            self.assertEqual(m['utility']['status'],'INSUFFICIENT_ASSEMBLY_LINK_SUPPORT')
            self.assertIn('not general',m['utility']['scope'])
            with self.assertRaisesRegex(ValueError,'unique'):g.pool(folders,['one','one'],root/'invalid')


if __name__=='__main__':unittest.main()
