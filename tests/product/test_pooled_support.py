"""Real BAM proof that pre-pool support filtering can discard cumulative links."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from test_genomegraph_links import fixture
from dl_binner.genomegraph import links, pooled


class PooledSupport(unittest.TestCase):
    def test_two_plus_two_survives_only_pool_before_support_with_real_collation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);folders=[];samples=['first','second']
            for i,sample in enumerate(samples):
                at=root/sample;at.mkdir()
                def change(name,role,r):
                    if name=='opaque-2'and role==2:r.mapping_quality=0
                    if i and (name.startswith('opaque-')or name=='duplicate-coordinate'):
                        r.reference_start+=10;r.next_reference_start+=10
                bam,ids,lengths,eligible=fixture(at,change)
                old=at/'old';links.extract(bam,ids,lengths,eligible,sample,old,2,dict(links.DEFAULT,min_calibration=2))
                a,_=links.read(old);self.assertEqual(len(a['edges']),0)
                new=at/'new';m=pooled.extract(bam,ids,lengths,eligible,sample,new,2,engineering=True)
                a,r=pooled.read(new);self.assertEqual(len(a['observations']),2);self.assertEqual(m['insert_limit'],400)
                self.assertGreater(m['counters']['qualified_read_length_150'],0)
                self.assertTrue((a['observations']['a_end']>a['observations']['a']).all());folders.append(new)
            m=pooled.pool(folders,samples,root/'pooled');self.assertEqual(m['threshold_order'],'pool_before_support')
            from dl_binner.multiview.arrays import load_arrays
            a,_=load_arrays(root/'pooled/graph.npz','physical_template_graph')
            self.assertEqual(a['edges'].tolist(),[[0,1]]);self.assertEqual(a['support'].tolist(),[4]);self.assertEqual(a['sample_support'].tolist(),[[2,2]])
            self.assertEqual(m['utility']['status'],'INSUFFICIENT_ASSEMBLY_LINK_SUPPORT')
            with self.assertRaisesRegex(ValueError,'unique'):pooled.pool(folders,['same','same'],root/'duplicate-samples')

    def test_missing_NM_preserves_failure_and_no_ledger_seal(self):
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder)
            def change(name,role,r):
                if name=='opaque-0'and role==2:r.set_tag('NM',None)
            bam,ids,lengths,eligible=fixture(root,change)
            with self.assertRaisesRegex(ValueError,'NM'):pooled.extract(bam,ids,lengths,eligible,'s',root/'bad',2,engineering=True)
            self.assertTrue((root/'bad/failure.json').exists());self.assertFalse((root/'bad/completed.json').exists())

    def test_duplicate_loci_do_not_create_three_molecules_within_a_library(self):
        a=np.zeros(4,pooled.LEDGER);a['j']=1;a['a']=10;a['b']=20;a['a_end']=160;a['b_end']=170;a['distance']=200;a['orientation']=1
        a['a_end'][2]=161
        b=pooled.unique(a,400);self.assertEqual(len(b),1);self.assertEqual(int(b['a_end'][0]),161)
        with self.assertRaisesRegex(ValueError,'Malformed'):pooled.unique(np.empty(0,links.OBS),400)


if __name__=='__main__':unittest.main()
