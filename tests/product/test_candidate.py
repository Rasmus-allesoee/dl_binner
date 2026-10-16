"""Native dev4 unit/integration contracts on generated DNA; no community scores."""
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np

from candidate_fixture import asset, fixture, tiny_config
from dl_binner import io
from dl_binner.candidate import views, grouping, markers
from fixtures import THREADS


class CandidateContracts(unittest.TestCase):
    """Own native fixtures and require real evidence, including intended refusals."""
    def setUp(self):
        if os.environ.get('DL_BINNER_TEST_OUTPUT'):
            self.root=Path(os.environ['DL_BINNER_TEST_OUTPUT'])/'candidate-contracts'/self._testMethodName
            self.root.mkdir(parents=True)
        else:
            self.temp = tempfile.TemporaryDirectory(prefix='dev4-contract-')
            self.addCleanup(self.temp.cleanup)
            self.root = Path(self.temp.name)

    def test_vectorized_TNF_strand_IUPAC_and_real_disjoint_window_contract(self):
        rng = np.random.default_rng(41)
        dna = ''.join(rng.choice(list('ACGTRYSWKMBDHVN'), 15001))
        for s in [dna, 'ACGT'*2000, 'NNNN', 'A', 'AAAACCCCGGGGTTTT']:
            a, counts = views.composition(s)
            original, old_counts = io.tnf([('opaque',s)])
            np.testing.assert_array_equal(a, original[0])
            self.assertEqual(counts, old_counts[0])
        cfg = views.config()
        windows = views.windows('opaque', dna, cfg)
        self.assertEqual(windows, views.windows('opaque', dna, cfg))
        self.assertEqual(len(windows),4)
        for a,b in [(0,1),(2,3)]:
            self.assertLessEqual(windows[a][1], windows[b][0])
        for start,end,s in windows:
            self.assertEqual(s, dna[start:end])
            self.assertGreaterEqual(end-start,cfg['window_min'])
        self.assertEqual(views.windows('short','A'*1999,cfg),[])

    def test_complete_parent_window_depth_axes_and_invalid_contract_refusal(self):
        fasta, depth, rows = fixture(self.root)
        out=self.root/'features';out.mkdir()
        cfg=views.config()
        views.prepare(fasta,depth,out,cfg)
        d,m,v,vm=views.load(out/'features.npz',out/'views.npz')
        self.assertEqual(d['ids'].tolist(),[i for i,_ in rows])
        self.assertEqual(m['samples'],['Z-last','A-first'])
        self.assertEqual(d['lengths'].sum(),sum(len(s) for _,s in rows))
        self.assertFalse(v['trainable'][7])  # 1,999-bp parent not split.
        self.assertTrue(d['eligible'][7])  # Still enters inference.
        self.assertFalse(d['eligible'][-2])  # N-only DNA is retained/excluded.
        self.assertIn('not measured window depth',m['depth_semantics'])
        bad=dict(d);bad['zero_depth']=~d['zero_depth']
        with self.assertRaisesRegex(ValueError,'depth masks'):io.validate_features(bad,m)
        for key,value in [('window_pairs',3),('temperature',0),('seed',True),('refinement_margin',3)]:
            altered=dict(cfg);altered[key]=value;p=self.root/(key+'.json');p.write_text(json.dumps(altered))
            with self.assertRaises(ValueError):views.config(p)
        depth.write_text(depth.read_text()+depth.read_text().splitlines()[1]+'\n')
        with self.assertRaisesRegex(ValueError,'duplicate depth'):io.read_depth(depth,[i for i,_ in rows])

    def test_marker_dedup_alias_ambiguity_multicopy_and_bad_coordinates(self):
        genes={f'g{i}':dict(contig='a' if i<2 else 'b',start=i*300,end=i*300+300,
                            strand=1,protein_length=100)for i in range(4)}
        def hit(g,f,start=1,end=80):
            return dict(gene=g,marker=f,score=100.,hmm_from=1,hmm_to=80,hmm_length=100,
                        protein_from=start,protein_to=end)
        result=markers.reduce_hits(genes,[hit('g0','m'),hit('g0','alias'),hit('g1','m'),
            hit('g2','m'),hit('g2','other'),hit('g3','alias')],dict(m='M',alias='M',other='O'))
        self.assertNotIn('a',result['clean'])
        self.assertEqual(result['clean']['b'],['M'])
        self.assertEqual(len(result['multicopy']),1)
        self.assertEqual(result['ambiguous'][0]['gene'],'g2')
        bad=hit('g0','m');bad['hmm_to']=101
        with self.assertRaisesRegex(ValueError,'coordinates'):markers.reduce_hits(genes,[bad],dict(m='M'))

    def test_sequence_only_one_depth_and_zero_depth_fusion_loss_contract(self):
        import torch
        from dl_binner.candidate.model import Encoder,transform
        from dl_binner.model import nt_xent,configure_torch
        configure_torch(THREADS)
        cfg=views.config();cfg.update(sequence_hidden=16,sequence_output=8,depth_hidden=4,fusion_hidden=8,output=4)
        for samples in [0,1,3]:
            torch.manual_seed(11)
            model=Encoder(samples,cfg)
            s=torch.rand(4,136);d=torch.rand(4,samples);mask=torch.tensor([False,True,False,True])
            a,sa=model(s,d,mask)
            changed=d.clone();changed[~mask]=99
            b,_=model(s,changed,mask)
            np.testing.assert_array_equal(a.detach().numpy(),b.detach().numpy())
            np.testing.assert_allclose(torch.linalg.vector_norm(a,dim=1).detach(),1,atol=1e-6)
            loss=nt_xent(a,b,.2)+.5*nt_xent(sa,sa,.2)
            self.assertTrue(torch.isfinite(loss));loss.backward()
            self.assertTrue(all(p.grad is None or torch.isfinite(p.grad).all() for p in model.parameters()))

    def test_native_gene_HMM_cache_hit_reuse_and_corruption_refusal(self):
        fasta,_,rows=fixture(self.root)
        hmm,manifest=asset(self.root,fasta)
        cache=self.root/'cache';cache.mkdir()
        markers.cache(fasta,hmm,manifest,cache,THREADS)
        before={p.name:io.digest(p) for p in cache.iterdir()}
        evidence=markers.load_cache(cache,fasta,[i for i,_ in rows])
        self.assertGreater(evidence['gene_count'],0)
        self.assertGreater(len(json.loads((cache/'domains.json').read_text())),0)
        self.assertEqual(before,{p.name:io.digest(p) for p in cache.iterdir()})
        self.assertEqual(evidence['ids'],[i for i,_ in rows])
        original_evidence=(cache/'evidence.json').read_bytes();original_receipt=(cache/'cache.json').read_bytes()
        evidence['clean'][rows[0][0]]=['fabricated_family']
        (cache/'evidence.json').write_text(json.dumps(evidence))
        receipt=json.loads(original_receipt)
        from dl_binner.contracts import file_record
        receipt['files']['evidence.json']=file_record(cache/'evidence.json')
        (cache/'cache.json').write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ValueError,'canonical marker'):markers.load_cache(cache,fasta)
        (cache/'evidence.json').write_bytes(original_evidence);(cache/'cache.json').write_bytes(original_receipt)
        (cache/'proteins.faa').write_text('corrupt\n')
        with self.assertRaisesRegex(ValueError,'bytes changed'):markers.load_cache(cache,fasta)
        manifest.write_text('{}')
        with self.assertRaisesRegex(ValueError,'marker asset'):markers.read_asset(hmm,manifest)

    def test_native_approximate_neighbors_unit_geometry_and_exact_audit(self):
        # sklearn's LLVM OpenMP and this Mac Torch wheel's Intel OpenMP must not
        # coexist. Production also isolates embedding from graph construction.
        code='''
import numpy as np
from dl_binner.candidate import views,grouping
        cfg=views.config();cfg.update(exact_threshold=64,audit_queries=24)
        rng=np.random.default_rng(37)
        x=rng.normal(size=(512,8)).astype(np.float32)
        x/=np.linalg.norm(x,axis=1,keepdims=True)
        ids=['opaque-'+str(i) for i in range(len(x))]
nn,scores,audit=grouping.neighbor_graph(x,ids,cfg,THREADS)
assert audit['mode']=='pynndescent_exact_rerank'
assert audit['mean_tie_aware_recall']>=.9
assert nn.shape==(512,30)
assert not any(i in row for i,row in enumerate(nn))
        np.testing.assert_allclose(scores,np.sum(x[nn].astype(float)*x[:,None,:],2),atol=1e-6)
        bad=np.tile(np.arange(3),(len(x),1))
try:grouping.rank_candidates(x,ids,bad,30)
except ValueError as e:assert 'missing/duplicate' in str(e)
else:raise AssertionError('invalid index accepted')
'''
        # Strip only fixture indentation, keeping production modules unchanged.
        code='\n'.join(line[8:] if line.startswith('        ') else line for line in code.splitlines())
        result=subprocess.run([sys.executable,'-I','-B','-c',code.replace('THREADS',str(THREADS))],
                              capture_output=True,text=True,timeout=180)
        (self.root/'neighbors.stdout.log').write_text(result.stdout)
        (self.root/'neighbors.stderr.log').write_text(result.stderr)
        self.assertEqual(result.returncode,0,result.stdout+'\n'+result.stderr)

    def test_refinement_two_family_support_marker_negative_and_ambiguous_DNA(self):
        cfg=views.config();cfg.update(output=2,min_bin_bp=1)
        ids=np.array(['a','b','c','d','e','f','ambiguous','excluded'])
        x=np.array([[1,0]]*3+[[0,1]]*3+[[2**-.5,2**-.5],[0,0]],np.float32)
        data=dict(ids=ids,lengths=np.full(8,10000,np.int64))
        pre=dict(ids=ids.tolist(),assignment=[0]*7+[-1],valid=[True]*7+[False],
            reason=['']*7+['zero_geometry_evidence'],neighbors=[[]]*8,parent_features_sha256='bound')
        clean={'a':['M','N'],'d':['M','N']}
        result=grouping.refine_partition(pre,data,x,clean,cfg)
        self.assertEqual(result['clusters'],2)
        self.assertNotEqual(result['assignment'][0],result['assignment'][3])
        self.assertTrue(all(result['assignment'][i]>=0 for i in [1,2,4,5]))
        self.assertEqual(result['assignment'][6:],[-1,-1])
        self.assertEqual(result['reason'][6],'refinement_ambiguous_affinity')
        self.assertFalse(result['unresolved_conflicts'])
        unchanged=grouping.refine_partition(pre,data,x,{'a':['M'],'d':['M']},cfg)
        self.assertEqual(unchanged['assignment'],pre['assignment'])
        self.assertFalse(unchanged['attempts'][0]['adopted'])

    def test_installed_pipeline_native_train_reload_export_resume_and_failure(self):
        fasta,depth,rows=fixture(self.root)
        hmm,manifest=asset(self.root,fasta)
        cfg_path=self.root/'tiny.json';cfg=tiny_config(cfg_path)
        out=self.root/'run'
        base=[sys.executable,'-I','-B','-m','dl_binner','candidate','--fasta',str(fasta),'--depth',str(depth),
              '--marker-hmm',str(hmm),'--marker-manifest',str(manifest),'--config',str(cfg_path),
              '--output',str(out),'--threads',str(THREADS),'--timeout','240','--memory-gb','6']
        def call(command,ok=True):
            p=subprocess.run(command,capture_output=True,text=True,timeout=300)
            if ok:self.assertEqual(p.returncode,0,p.stdout+'\n'+p.stderr)
            else:self.assertNotEqual(p.returncode,0,p.stdout+'\n'+p.stderr)
            return p
        call(base+['--stop-after','markers'])
        accepted=io.digest(out/'receipts/markers.json')
        self.assertFalse((out/'train').exists())
        call(base+['--resume'])
        self.assertEqual(io.digest(out/'receipts/markers.json'),accepted)
        done=json.loads((out/'completion.json').read_text())
        self.assertTrue(done['checkpoint_reload_exact'])
        stage_receipts=[json.loads((out/'receipts'/(s+'.json')).read_text()) for s in
                        ['features','markers','train','embed','group','refine','export']]
        self.assertTrue(all(a['end_monotonic_ns']<=b['start_monotonic_ns']for a,b in zip(stage_receipts,stage_receipts[1:])))
        trained=json.loads((out/'train/checkpoint.json').read_text())
        self.assertEqual(len(trained['history']),2)
        self.assertTrue(all(h['parents_seen']==trained['training_parents'] for h in trained['history']))
        for arm in ['pre','post']:
            folder=out/'export'/arm
            exported=[r for p in folder.glob('*.fna') if p.stat().st_size for r in io.read_fasta(p)]
            self.assertEqual(sorted(exported),sorted(rows))
            with (folder/'assignments.tsv').open() as stream:assignments=list(csv.DictReader(stream,delimiter='\t'))
            self.assertEqual([r['contig_id'] for r in assignments],[i for i,_ in rows])
            self.assertEqual(sum(int(r['length']) for r in assignments),sum(len(s) for _,s in rows))
        before=io.digest(out/'completion.json')
        call(base+['--resume'])
        self.assertEqual(io.digest(out/'completion.json'),before)
        # Preserve successful journals/artifacts before intentional corruption
        # tests mutate this disposable test run. Never mutate actual E009 data.
        shutil.copytree(out,self.root/'accepted-candidate')
        # Exercise the actual packaged network/window/20-epoch default schedule
        # on this same tiny software fixture, without any community input/score.
        defaults=list(base);at=defaults.index('--config');del defaults[at:at+2]
        default_out=self.root/'packaged-defaults';defaults[defaults.index('--output')+1]=str(default_out)
        call(defaults)
        default_training=json.loads((default_out/'train/checkpoint.json').read_text())
        self.assertEqual(len(default_training['history']),20)
        self.assertEqual(default_training['config'],views.config())
        cfg_path.write_text(cfg_path.read_text()+' ')
        # Configuration identity is semantic and retained exactly in the run;
        # changed config values, not JSON whitespace, must refuse recovery.
        cfg['seed']=12;cfg_path.write_text(json.dumps(cfg))
        failed=call(base+['--resume'],False)
        self.assertIn('identity changed',failed.stderr)
        (out/'group/partition.json').write_text('{}')
        cfg['seed']=11;cfg_path.write_text(json.dumps(cfg))
        failed=call(base+['--resume'],False)
        self.assertIn('bytes changed',failed.stderr)
        self.assertFalse((out/'.run-lock').exists())
        invalid=self.root/'invalid.fna';invalid.write_text('>bad\nACGZ\n')
        command=list(base);command[command.index('--fasta')+1]=str(invalid)
        invalid_out=self.root/'failed-native';command[command.index('--output')+1]=str(invalid_out)
        failed=call(command,False)
        self.assertIn('IUPAC',failed.stderr)
        self.assertFalse((invalid_out/'features').exists())
        self.assertFalse((invalid_out/'train').exists())
        status=json.loads(next((invalid_out/'logs').glob('*/status.json')).read_text())
        self.assertEqual(status['status'],'failed')
        self.assertFalse((invalid_out/'.run-lock').exists())


if __name__=='__main__':unittest.main()
