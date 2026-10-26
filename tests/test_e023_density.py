"""Actual tiny sparse/cache/readers/selection/export contracts, never community scores."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from dl_binner.density.grouping import (audit_cache, condense, context_channels, hierarchy, leaves, policy, run, select, sparse_input)
from dl_binner.density.bin_quality import summarize, quality_tier
from dl_binner.io import digest, save_arrays

ROOT = Path(__file__).absolute().parents[1]
CFG = ROOT/'experiments/E023-adaptive-density-bins/config.json'


def fixture(root, depth):
    """Write real indexed DNA/features/graph, with synthetic frozen unit vectors."""
    from dl_binner.multiview.views import prepare, config
    from dl_binner.multiview.arrays import load_arrays
    from dl_binner.candidate.grouping import group
    fasta = root/'dna.fa'; ids = ['opaque-z', 'opaque-a', 'opaque-t', 'opaque-b', 'short', 'missing', 'excluded']
    dna = ['ACGT'*1500, 'ACGT'*1500, 'AAAACCCC'*750, 'AAAACCCC'*750, 'ACGT'*200, 'AAAACCCC'*125, 'ACGT'*20]
    fasta.write_text(''.join('>'+q+' description\n'+s+'\n' for q, s in zip(ids, dna)))
    cov = root/'depth.tsv'
    cov.write_text('contig_id\tS2\tS0\n'+''.join(q+'\t'+('0\t0' if q=='missing' else '10\t1' if j in (0,1,4) else '1\t10')+'\n' for j,q in reversed(list(enumerate(ids)))))
    base = config(); prepare(fasta, cov if depth else None, root/'features', base)
    f = root/'features/features.npz'; data, meta = load_arrays(f, 'features')
    x = np.zeros((len(ids),64), np.float32)
    for j in np.flatnonzero(data['eligible']): x[j,0 if j in (0,1,4) else 1] = 1
    emb = root/'embeddings.npz'
    save_arrays(emb, dict(ids=data['ids'], features=x, evidence=data['eligible']),
                dict(kind='embeddings',features_sha256=digest(f),metric='synthetic engineering unit vectors'))
    group(emb, f, root/'original', base, 4)
    evidence = root/'evidence.json'; evidence.write_text(json.dumps(dict(panel_size=40, calls={}, loci=[])))
    return f, emb, root/'original/graph.npz', evidence, fasta, data


class Density(unittest.TestCase):
    def test_physical_overlap_partial_and_cross_contig_loci(self):
        from dl_binner.multiview.refinement import marker_evidence
        genes={name:dict(contig=q,start=0,end=90,strand=1,protein_length=30,
                        partial_begin=partial,partial_end=False)
               for name,q,partial in [('g1','a',False),('alias','a',False),('g2','b',True)]}
        domains=[dict(gene=g,marker='F',score=40.,hmm_from=1,hmm_to=15,hmm_length=30,
                      protein_from=1,protein_to=15,hmm_coverage=.5)for g in genes]
        e=marker_evidence(genes,domains,{'F':'F'},{'F':{'TC':'20 20;','LENG':30}},['a','b'],[100,100],{'physical_overlap_fraction':.5})
        self.assertEqual(len(e['consolidated']),1);self.assertEqual(len(e['loci']),2)
        self.assertEqual(len(e['calls']['a']['F']),1)
        self.assertAlmostEqual(e['calls']['b']['F'][0],e['calls']['a']['F'][0]/2)

    def test_actual_approximate_joint_index(self):
        from dl_binner.information.grouping import CoreIndex
        # Same native index implementation; crossover lowered for engineering only.
        cfg=policy(CFG);cfg['exact_threshold']=32
        x=np.random.default_rng(11).normal(size=(96,12)).astype(np.float32)
        index=CoreIndex(x,[f'opaque-{j:03}' for j in range(96)],cfg,4)
        nn,dd=index.query(x,np.arange(96));audit=index.audit(x,index.ids,nn,dd,np.arange(96))
        self.assertIsNotNone(index.native);self.assertGreaterEqual(audit['mean_tie_aware_recall'],.9)

    def test_real_two_mode_readers_hierarchy_export_reload(self):
        from dl_binner.information.export import export
        from dl_binner.multiview.arrays import load_arrays
        for depth in (True, False):
            with self.subTest(depth=depth), tempfile.TemporaryDirectory() as d:
                p=Path(d); f,e,g,m,fa,data=fixture(p,depth); before=[digest(x) for x in (f,e,g,m)]
                record=run(f,e,g,m,p/'new',policy(CFG),4)
                self.assertEqual(record['contigs'],7); self.assertEqual(len(record['samples']),2 if depth else 0)
                from dl_binner.density.grouping import load_inputs
                loaded,vectors,valid,_=load_inputs(f,e)
                channels,available,scales,transforms=context_channels(loaded,vectors,np.flatnonzero(valid),policy(CFG))
                if depth:
                    self.assertFalse(available[5])
                    expected=np.log1p(loaded['depth'][loaded['eligible']&loaded['depth_evidence']]).std(0)
                    np.testing.assert_allclose(transforms['depth_column_std'],expected,atol=1e-12)
                else:
                    self.assertEqual(channels[2].shape[1],0);self.assertFalse(available.any())
                a,meta=load_arrays(p/'new/hierarchy.npz','density_hierarchy')
                self.assertEqual(a['ids'].tolist(),data['ids'].tolist())
                self.assertEqual(audit_cache(f,e,g,m,p/'new',policy(CFG))['status'],'PASS')
                for arm in ['density','selected']:
                    part=json.loads((p/'new'/(arm+'-partition.json')).read_text())
                    self.assertEqual(part['assignment'][-1],-1)
                    r=export(f,p/'new'/(arm+'-partition.json'),fa,p/('export-'+arm),True)
                    self.assertEqual(sum(v['contigs'] for v in r['populations'].values()),7)
                    self.assertEqual(sum(v['bp'] for v in r['populations'].values()),int(data['lengths'].sum()))
                self.assertEqual(before,[digest(x) for x in (f,e,g,m)])
                with self.assertRaises(FileExistsError):run(f,e,g,m,p/'new',policy(CFG),4)
                # Rebind the outer checksum so the real structural reader must refuse it.
                a['selected'][0]=a['selected'][-1]
                damaged=p/'damaged';damaged.mkdir()
                save_arrays(damaged/'hierarchy.npz',a,{k:v for k,v in meta.items()if k not in ['version','sha256','ids_sha256']})
                with self.assertRaisesRegex(ValueError,'index mapping'):
                    audit_cache(f,e,g,m,damaged,policy(CFG))
                with self.assertRaisesRegex(ValueError,'byte hash mismatch'):
                    g.write_bytes(g.read_bytes()+b'corrupt'); sparse_input(g,data['ids'].tolist(),data['eligible'],e)

    def test_unequal_density_bridge_and_supported_alternatives(self):
        cfg=policy(CFG)
        # Two dense islands with a sparse bridge; complete tiny sparse representation.
        x=np.r_[np.arange(12)*.001, 3+np.arange(12)*.02, [1.5]]
        dd=abs(x[:,None]-x[None,:]);np.fill_diagonal(dd,np.inf)
        nn=np.argsort(dd,axis=1)[:,:24]; ds=np.take_along_axis(dd,nn,axis=1)
        ds=np.maximum(ds,cfg['distance_floor']); lengths=np.array([6000]*24+[500])
        tree=hierarchy(nn,ds,lengths,cfg); branches=condense(tree,lengths,cfg)
        ids=[f'opaque-{j:02}'for j in range(len(x))]
        selected,trace=select(tree,branches,lengths,ids,dict(panel_size=40,calls={}),cfg)
        groups=[set(leaves(tree,n,len(x)))for n in selected]
        self.assertTrue(any(set(range(12))<=c for c in groups))
        self.assertTrue(any(set(range(12,24))<=c for c in groups))
        self.assertFalse(any(set(range(24))<=c for c in groups))
        self.assertTrue(any(b['children'] for b in branches))
        self.assertTrue(all(t['marker_factor']==1 for t in trace))

    def test_marker_reliability_is_soft_and_distinct_loci_remain(self):
        cfg=policy(CFG); nn=np.array([[1,2],[0,2],[3,1],[2,1]]); dd=np.array([[.1,1],[.1,1],[.1,1],[.1,1.]])
        tree=hierarchy(nn,dd,np.array([6000]*4),cfg)
        # A whole-parent alternative and children, independent of test truth.
        root=int(tree['roots'][0]); children=list(map(int,tree['children'][root]))
        branches=[dict(node=root,parent=-1,children=[1,2],stability=10.)]+[dict(node=c,parent=0,children=[],stability=4.)for c in children]
        ids=['a','b','c','d']; evidence=dict(panel_size=1,calls={'a':{'F':[1.]},'c':{'F':[1.]}})
        raw,_=select(tree,branches,np.array([6000]*4),ids,evidence,cfg,False)
        marked,trace=select(tree,branches,np.array([6000]*4),ids,evidence,cfg,True)
        self.assertEqual(raw,[root]); self.assertEqual(len(marked),2)
        self.assertGreater(trace[0]['excess_proxy'],0)
        self.assertGreater(trace[0]['own_utility'],0) # no cannot-link
        evidence['calls']['a']['F']=[float('nan')]
        with self.assertRaisesRegex(ValueError,'weights'):select(tree,branches,np.array([6000]*4),ids,evidence,cfg)

    def test_support_abstention_and_malformed_policy(self):
        cfg=policy(CFG); tree=hierarchy(np.array([[1],[0]]),np.array([[.1],[.1]]),np.array([800,800]),cfg)
        self.assertEqual(condense(tree,np.array([800,800]),cfg),[])
        empty=hierarchy(np.empty((0,0),np.int64),np.empty((0,0)),np.empty(0,np.int64),cfg)
        self.assertEqual(condense(empty,np.empty(0,np.int64),cfg),[])
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'config.json';p.write_text(json.dumps(dict(cfg,truth_K=2)))
            with self.assertRaisesRegex(ValueError,'Unfrozen'):policy(p)
        with self.assertRaisesRegex(ValueError,'Duplicate/self'):
            hierarchy(np.array([[0],[0]]),np.ones((2,1)),np.ones(2,dtype=np.int64),cfg)


class SecondaryQuality(unittest.TestCase):
    def test_full_union_unknown_and_non_target(self):
        refs={'r':dict(genome='G',length=100),'n':dict(genome='N',length=100)}
        rows=[dict(id='a',length=100,confirmed_query_bp={'G':95},source_intervals={'r':[[0,95]]}),
              dict(id='b',length=100,confirmed_query_bp={'G':95},source_intervals={'r':[[0,95]]}),
              dict(id='n',length=100,confirmed_query_bp={'N':100},source_intervals={'n':[[0,100]]}),
              dict(id='u',length=40,confirmed_query_bp={},source_intervals={})]
        r=summarize(rows,dict(a='B',b='B',n='N',u=None),refs,{'G':100,'N':100},{'G'})
        b=next(x for x in r['bins']if x['bin_id']=='B')
        self.assertEqual(b['completeness'],.95);self.assertEqual(b['unconfirmed_bp'],10)
        self.assertAlmostEqual(b['impurity_upper_bound'],.05)
        self.assertEqual(r['assigned_bp'],300);self.assertEqual(r['query_count'],4)
        self.assertFalse(r['primary_rule_changed']);self.assertFalse(r['rRNA_tRNA_screened'])
        self.assertEqual(sum(r['target_counts'].values()),1)
        rows[0]['source_intervals']['r']=[[0,101]]
        with self.assertRaisesRegex(ValueError,'escaped'):summarize(rows,dict(a='B',b='B',n='N',u=None),refs,{'G':100,'N':100},{'G'})

    def test_tier_edges_do_not_claim_mimag(self):
        self.assertEqual(quality_tier(.91,.049),'threshold_based_HQ')
        self.assertEqual(quality_tier(.90,.049),'threshold_based_MQ')
        self.assertEqual(quality_tier(.95,.05),'threshold_based_MQ')
        self.assertEqual(quality_tier(.50,.099),'threshold_based_MQ')
        self.assertEqual(quality_tier(.49,.099),'threshold_based_LQ')
        self.assertEqual(quality_tier(.99,.10),'high_impurity_or_unresolved')
        with self.assertRaisesRegex(ValueError,'quality fraction'):quality_tier(float('nan'),0)

    def test_oral_streamed_adapter_keeps_N_and_shared_ambiguity(self):
        import gzip
        from e023_review import oral_secondary_rows
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'rows.jsonl.gz';row=dict(id='opaque',length=10,genome='G',reference='r',start=0,end=10,
                source_intervals=[[0,4],[5,10]],quarantined_bp=1,shared_forward_query=True,shared_complete_reference=False)
            with gzip.open(p,'wt')as f:f.write(json.dumps(row)+'\n')
            refs={'r':dict(genome='G',length=100)}
            unmasked=list(oral_secondary_rows(p,refs))[0];masked=list(oral_secondary_rows(p,refs,True))[0]
            self.assertEqual(unmasked['confirmed_query_bp'],{'G':9})
            self.assertEqual(masked['confirmed_query_bp'],{});self.assertEqual(masked['length'],10)
            v=summarize([unmasked],{'opaque':'B'},refs,{'G':100},{'G'})
            self.assertAlmostEqual(v['bins'][0]['completeness'],.09)
            self.assertEqual(v['bins'][0]['unconfirmed_bp'],1)


if __name__=='__main__':unittest.main()
