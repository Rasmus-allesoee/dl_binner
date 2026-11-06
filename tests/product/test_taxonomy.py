"""Portable taxonomy/tree/loss/fallback contracts using only owned tiny fixtures."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import torch

from dl_binner.taxonomy.tree import Tree, from_gtdb
from dl_binner.taxonomy import annotations
from dl_binner.taxonomy import model
from dl_binner.io import id_digest


def fixture_tree():
    """Use skipped ranks deliberately to test actual partial-rank masks."""
    return Tree([dict(id=0,parent=0,rank='no rank',name='unclassified'),dict(id=1,parent=1,rank='no rank',name='root'),
        dict(id=2,parent=1,rank='superkingdom',name='Bacteria'),dict(id=3,parent=2,rank='genus',name='A'),
        dict(id=4,parent=3,rank='species',name='a'),dict(id=5,parent=3,rank='species',name='b'),
        dict(id=6,parent=2,rank='genus',name='B')])


class Taxonomy(unittest.TestCase):
    def test_tree_refuses_cycles_rank_reversals_and_foreign_labels(self):
        t=fixture_tree();self.assertEqual(t.path(4).tolist(),[2,0,0,0,0,3,4])
        bad=copy.deepcopy(t.nodes);bad[3]['parent']=4
        with self.assertRaisesRegex(ValueError,'acyclic'):Tree(bad)
        bad=copy.deepcopy(t.nodes);bad[4]['rank']='superkingdom'
        with self.assertRaisesRegex(ValueError,'rank'):Tree(bad)
        with self.assertRaisesRegex(ValueError,'Unknown'):t.path(7)

    def test_deterministic_gtdb_prefixes_and_empty_rank_refusal(self):
        with tempfile.TemporaryDirectory()as folder:
            p=Path(folder)/'tax.tsv';p.write_text('ref1\td__B;p__P;c__C;o__O;f__F;g__G;s__a\nref2\td__B;p__P;c__C;o__O;f__F;g__G;s__b\n')
            t,a=from_gtdb([p]);self.assertNotEqual(a['ref1'],a['ref2'])
            p.write_text('ref1\td__B;p__;c__C;o__O;f__F;g__G;s__a\n')
            with self.assertRaisesRegex(ValueError,'gap'):from_gtdb([p])

    def test_native_schema_partial_conflict_missing_duplicate_and_counter_refusals(self):
        with tempfile.TemporaryDirectory()as folder:
            p=Path(folder);ids=['opaqueA','opaqueB','opaqueC','zero'];rows=[dict(query='q'+str(i),id=q,queried=i<3)for i,q in enumerate(ids)]
            index=p/'index.json';index.write_text(json.dumps(dict(kind='taxonomy_query_index',version=1,ids_sha256=id_digest(ids),rows=rows)))
            tsv=p/'taxonomy.tsv';text='q0\t4\tspecies\ta\t4\t4\t4\t1\nq1\t3\tgenus\tA\t10\t5\t4\t.8\nq2\t0\tno rank\tunclassified\t3\t0\t0\t0\n'
            tsv.write_text(text);a,_=annotations.parse(tsv,index,fixture_tree())
            self.assertEqual(a['states'].tolist(),['classified','partial','no_hit','zero_length'])
            self.assertAlmostEqual(float(a['confidence'][1]),.4,6)
            self.assertEqual(a['paths'][1,-1],0)
            for bad in [text+text.splitlines()[0]+'\n',text.replace('4\t4\t4\t1','3\t4\t4\t1'),text.replace('\t.8','\tnan'),text.replace('q2\t0','qX\t0'),text.rsplit('q2',1)[0]]:
                tsv.write_text(bad)
                with self.assertRaises(ValueError):annotations.parse(tsv,index,fixture_tree())
            tsv.write_text(text.replace('5\t4\t.8','5\t2\t.4'));a,_=annotations.parse(tsv,index,fixture_tree());self.assertEqual(a['states'][1],'conflict');self.assertEqual(a['confidence'][1],0)

    def test_exact_sibling_loss_chunk_gradient_and_partial_mask(self):
        torch.manual_seed(11);t=fixture_tree();m=model.Encoder(8,2,t)
        z=torch.nn.functional.normalize(torch.randn(3,8),dim=1).requires_grad_()
        paths=torch.from_numpy(np.stack([t.path(4),t.path(3),t.path(0)])).long()
        small=model.hierarchy_loss(m,z,paths,t,chunk=1);full=model.hierarchy_loss_reference(m,z,paths,t,chunk=999)
        self.assertTrue(torch.allclose(small,full,rtol=0,atol=1e-6));self.assertEqual(float(small[-1]),0.)
        small.sum().backward();self.assertTrue(torch.isfinite(z.grad).all());self.assertGreater(float(z.grad[:2].abs().sum()),0.);self.assertEqual(float(z.grad[-1].abs().sum()),0.)
        # A genus observation has no species target and must not update a
        # species conditional head on that row.
        m.zero_grad();model.hierarchy_loss(m,z[1:2],paths[1:2],t).sum().backward();self.assertIsNone(m.rank_projection[6].weight.grad)

    def test_unknown_disabled_and_inactive_depth_gate_exact_fallback_and_bounded_delta(self):
        torch.manual_seed(11);t=fixture_tree();m=model.Encoder(8,2,t)
        base=torch.nn.functional.normalize(torch.randn(3,8),dim=1);seq=base.clone();comp=torch.randn(3,136);dep=torch.randn(3,2)
        paths=torch.from_numpy(np.stack([t.path(4),t.path(0),t.path(3)])).long();conf=torch.tensor([1.,0.,.4]);keep=torch.tensor([True,True,False]);measured=torch.zeros(3,dtype=torch.bool)
        with torch.no_grad():m.residual.weight.fill_(.2)
        out=m(base,seq,comp,dep,measured,paths,conf,keep)
        self.assertTrue(torch.equal(out[1:],base[1:]));self.assertLessEqual(float((out-base).norm(dim=1).max()),.5)
        again=m(base,seq,comp,dep*1000,measured,paths,conf,keep);self.assertTrue(torch.equal(out,again))
        off=m(base,seq,comp,dep,measured,paths,conf,torch.zeros(3,dtype=torch.bool));self.assertTrue(torch.equal(off,base))
        with self.assertRaisesRegex(ValueError,'Unfrozen'):model.policy(dict(model.policy(),seed=True))

    def test_optimized_conditional_loss_preserves_all_parameter_and_input_gradients(self):
        torch.manual_seed(11);t=fixture_tree();a=model.Encoder(8,2,t);b=copy.deepcopy(a)
        x=torch.nn.functional.normalize(torch.randn(9,8),dim=1).requires_grad_();y=x.detach().clone().requires_grad_()
        paths=torch.from_numpy(np.stack([t.path(i)for i in [4,5,3,6,0,4,5,3,6]])).long()
        left=model.hierarchy_loss_reference(a,x,paths,t);right=model.hierarchy_loss(b,y,paths,t)
        self.assertTrue(torch.allclose(left,right,rtol=0,atol=1e-6));left.sum().backward();right.sum().backward()
        self.assertTrue(torch.allclose(x.grad,y.grad,rtol=1e-5,atol=1e-6))
        for (_,p),(_,q)in zip(a.named_parameters(),b.named_parameters()):
            self.assertEqual(p.grad is None,q.grad is None)
            if p.grad is not None:self.assertTrue(torch.allclose(p.grad,q.grad,rtol=1e-5,atol=1e-6))

    def test_only_native_proven_zero_ORFs_can_complete_missing_rows(self):
        from dl_binner.taxonomy.normalization import complete
        with tempfile.TemporaryDirectory()as folder:
            p=Path(folder);rows=[dict(query='q0',id='a',queried=True),dict(query='q1',id='b',queried=True)]
            (p/'index.json').write_text(json.dumps(dict(rows=rows)))
            (p/'lookup').write_text('0\tq0\t0\n1\tq1\t0\n');(p/'orf.index').write_text('0\t0\t4\n')
            (p/'raw.tsv').write_text('q0\t4\tspecies\ta\t2\t2\t2\t1\n')
            proof=complete(p/'raw.tsv',p/'index.json',p/'lookup',p/'orf.index',p/'complete.tsv')
            self.assertEqual(proof['zero_ORF_queries'],['q1']);self.assertIn('q1\t0\tno rank', (p/'complete.tsv').read_text())
            (p/'orf.index').write_text('0\t0\t4\n1\t4\t4\n')
            with self.assertRaisesRegex(ValueError,'retained-ORF'):complete(p/'raw.tsv',p/'index.json',p/'lookup',p/'orf.index',p/'bad.tsv')


if __name__=='__main__':unittest.main()
