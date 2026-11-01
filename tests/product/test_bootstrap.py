"""Real tiny bootstrap-state, conservative-pair, reload and full-DNA contracts.

Uses generated DNA and actual HMM/cache readers. Frozen-GLM inference is mocked;
its coordinate/cache reader and hybrid trainer are real. A deliberate bad-distance
report exercises the real legacy recall refusal and bounded failure capture.
"""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch
from torch import nn

from relational_fixture import fixture, NumericExtractor
from dl_binner.bootstrap import model, pairs, bridge
from dl_binner.context.tokens import binding
from dl_binner.io import digest, write_json
from dl_binner.model import configure_torch


class Bootstrap(unittest.TestCase):
    def setUp(self): configure_torch(4)

    def test_frozen_defaults_and_truth_not_an_installed_stage_argument(self):
        for fn in (model.policy,pairs.policy):
            cfg = fn(); cfg['version'] = True
            with self.assertRaisesRegex(ValueError,'Unfrozen'): fn(cfg)
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable,'-I','-B','-m','dl_binner.bootstrap.stage','--help'],
                                    cwd=folder,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr); self.assertIn('--bootstrap',result.stdout)
            result = subprocess.run([sys.executable,'-I','-B','-m','dl_binner.bootstrap.stage','--stage','train',
                '--features','unused','--output','unused','--truth','forbidden'],cwd=folder,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0); self.assertIn('unrecognized arguments: --truth',result.stderr)

    def test_positive_abstention_absolute_confidence_and_negative_retention(self):
        ids = np.array(['a','b','c','d','e'])
        a = dict(ids=ids,left=np.array([0,0,1]),right=np.array([1,2,2]),
                 sign=np.array([1,1,-1],np.int8),weight=np.array([.8,.5,.9],np.float32))
        nn_ = np.array([[1,2,3,4],[0,2,3,4],[0,1,3,4],[0,1,2,4],[0,1,2,3]])
        q = dict(calls={'a':{'m':{}},'b':{'n':{}}})
        kept,w,trace = pairs.choose(a,q,nn_)
        self.assertEqual(kept.tolist(),[0,2]); self.assertAlmostEqual(float(w[0]),.8,6)
        self.assertAlmostEqual(float(w[1]),.9,6)
        self.assertEqual(trace[1]['reason'],'abstain_positive_requires_two_reliable_marker_endpoints')
        narrower = np.array([[1,2,3],[0,2,4],[0,1,3],[0,1,2],[0,1,2]])
        kept,w,trace = pairs.choose(a,q,narrower)
        self.assertEqual(kept.tolist(),[2]); self.assertIn('insufficient_shared',trace[0]['reason'])

    def test_eval_forwards_preserve_all_modes_BatchNorm_RNG_and_stopped_gradients(self):
        class Toy(nn.Module):
            """Expose real stochastic and non-parameter state in a tiny two-head model."""
            def __init__(self):
                super().__init__(); self.net=nn.Sequential(nn.Linear(4,4),nn.BatchNorm1d(4),nn.Dropout(.5))
            def forward(self,x):
                z=torch.nn.functional.normalize(self.net(x),dim=1); return z,z
        torch.manual_seed(11); online=Toy().train(); anchor=copy.deepcopy(online).requires_grad_(False).eval()
        online.net[1].eval()  # mixed child modes must also be restored
        modes=[m.training for m in online.modules()]; before=model.state_digest(online)
        rng=torch.get_rng_state().clone(); args=[torch.randn(8,4)]; rng=torch.get_rng_state().clone()
        loss=model.anchor_loss(online,anchor,args,torch.ones(8))
        self.assertEqual(float(loss),0.); (loss*0).backward()
        self.assertTrue(torch.equal(rng,torch.get_rng_state()))
        self.assertEqual(before,model.state_digest(online)); self.assertEqual(modes,[m.training for m in online.modules()])
        self.assertTrue(all(p.grad is None for p in anchor.parameters()))
        with torch.no_grad(): online.net[0].weight.add_(.1)
        online.zero_grad(); loss=model.anchor_loss(online,anchor,args,torch.ones(8));loss.backward()
        self.assertGreater(float(loss),0.); self.assertTrue(any(p.grad is not None and p.grad.abs().sum()>0 for p in online.parameters()))

    def test_optimizer_lazy_state_and_unequal_step_counters_are_preserved(self):
        from dl_binner.unified.training import configuration
        from dl_binner.relational.model import initialize
        cfg=configuration(False);torch.manual_seed(11)
        online,target,predictors=initialize(10,cfg)
        parameters=list(online.parameters())+list(predictors.parameters())
        optimizer=torch.optim.AdamW(parameters,lr=cfg['learning_rate'],weight_decay=cfg['weight_decay'])
        # Legitimate partial exposure: one parameter twice, another once; all
        # unexercised heads/decoders keep absent Adam state.
        parameters[0].sum().backward();optimizer.step();optimizer.zero_grad(set_to_none=True)
        (parameters[0].sum()+parameters[1].sum()).backward();optimizer.step()
        saved=dict(config=cfg,samples=[str(i) for i in range(10)],ema_updates=2,
            model_state=online.state_dict(),target_state=target.state_dict(),
            predictor_state=predictors.state_dict(),optimizer_state=optimizer.state_dict())
        restored=model.initialize(saved)[-1]
        self.assertEqual(len(restored.state),2)
        self.assertEqual([float(s['step']) for s in restored.state.values()],[2.,1.])
        for before,after in zip(optimizer.state.values(),restored.state.values()):
            self.assertTrue(all(torch.equal(before[k],after[k]) for k in before))

    def test_positive_abstention_does_not_increase_negative_force(self):
        from dl_binner.relational.model import signed_loss
        torch.manual_seed(11)
        raw=torch.randn(2,2,8);raw[1,1]=raw[1,0]+.01*torch.randn(8)
        x=torch.nn.functional.normalize(raw,dim=-1).requires_grad_()
        signs=torch.tensor([1,-1],dtype=torch.int8);weights=torch.tensor([.5,.8])
        before=signed_loss([x,x],[x.detach(),x.detach()],[nn.Identity(),nn.Identity()],signs,weights,.2)
        self.assertGreater(float(before[1]),0.)
        retained=signed_loss([x[1:],x[1:]],[x[1:].detach(),x[1:].detach()],[nn.Identity(),nn.Identity()],signs[1:],weights[1:],.2)
        after=model.attenuate(retained,1,2)
        self.assertEqual(float(after[0]),0.);self.assertTrue(torch.equal(after[1],before[1]))
        with self.assertRaises(ValueError):model.attenuate(retained,2,1)

    def test_zero_warmup_does_not_create_moments_or_weight_decay_for_an_unused_head(self):
        main=nn.Parameter(torch.tensor([1.]));side=nn.Parameter(torch.tensor([2.]))
        optimizer=torch.optim.AdamW([main,side],lr=.001,weight_decay=.1)
        loss=main.square().sum()+model.weighted_relation(side.square().sum(),side.sum()*0,0.)
        loss.backward();self.assertIsNone(side.grad);before=side.detach().clone();optimizer.step()
        self.assertTrue(torch.equal(side,before));self.assertNotIn(side,optimizer.state)
        optimizer.zero_grad(set_to_none=True)
        model.weighted_relation(side.square().sum(),side.sum()*0,.1).backward()
        self.assertIsNotNone(side.grad);self.assertGreater(float(side.grad.abs().sum()),0.)

    def test_original_E023_bridge_real_sparse_reload_export_and_no_fallback(self):
        from discovery_fixture import fixture as sparse_fixture
        from dl_binner.information.export import validate_partition
        with tempfile.TemporaryDirectory() as folder:
            f=sparse_fixture(folder,64)
            cfg=dict(version=1,seed=11,neighbors=30,candidates=60,min_samples=10,
                min_bin_contigs=2,min_bin_bp=10000,exact_threshold=2048,audit_queries=32,
                min_neighbor_recall=.9,calibration_pairs=8192,batch_rows=512,length_scale_bp=2500,
                marker_excess_penalty=5.,distance_floor=.000001)
            p=Path(folder); write_json(p/'config.json',cfg)
            write_json(p/'lock.json',dict(files={'src/dl_binner/density/grouping.py':binding(bridge.original.__file__)},
                                        policy=binding(p/'config.json')))
            args=(f['features'],f['embeddings'],f['graph'],f['evidence'],f['fasta'],p/'config.json',p/'lock.json')
            before={str(x):digest(x) for x in p.iterdir() if x.is_file()}
            bridge.run(*args,p/'new',engineering=True)
            view=bridge.query_view(p/'new/result',f['features'],f['graph'],
                [dict(id='opaque-0001',strata=['long']),dict(id='opaque-0000',strata=['observed_zero'])],p/'queries.json')
            self.assertEqual([r['id'] for r in view['queries']],['opaque-0001','opaque-0000'])
            self.assertEqual(len(view['queries'][0]['E023_neighbors']),30)
            self.assertNotIn('opaque-0001',view['queries'][0]['E023_neighbors'])
            with self.assertRaisesRegex(ValueError,'absent'):
                bridge.query_view(p/'new/result',f['features'],f['graph'],[dict(id='short-kept-in-accounting')],p/'bad-query.json')
            members={n:binding(p/'new/result'/n) for n in bridge.MEMBERS}
            bridge.run(*args,p/'reused',accepted=p/'new/result',members=members,engineering=True)
            for name in bridge.MEMBERS:
                self.assertEqual(binding(p/'new/result'/name),members[name])
            self.assertFalse((p/'reused/result').exists())
            self.assertFalse(json.loads((p/'reused/reuse/verified-reuse.json').read_text())['accepted_members_copied'])
            for arm in ['density','selected']:
                validate_partition(f['data'],p/'new/result'/(arm+'-partition.json'),f['features'])
                account=json.loads((p/'new/export'/arm/'manifest.json').read_text())
                self.assertEqual(account['contigs'],len(f['data']['ids']))
            self.assertTrue(all(digest(x)==d for x,d in before.items()))
            broken=copy.deepcopy(members);broken['hierarchy.npz']['sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'no rebuild'):bridge.run(*args,p/'bad-reuse',accepted=p/'new/result',members=broken,engineering=True)
            self.assertFalse((p/'bad-reuse/result').exists())
            real_query=bridge.original.CoreIndex.query
            def corrupt_report(index,*args,**kwargs):
                """Inject bad retrieval distances only; run the real legacy recall refusal."""
                near,dist=real_query(index,*args,**kwargs);return near,dist+1000000
            with patch.object(bridge.original.CoreIndex,'query',corrupt_report):
                with self.assertRaisesRegex(ValueError,'below frozen gate'):bridge.run(*args,p/'failed-recall',engineering=True)
            refused=json.loads((p/'failed-recall/failed-recall.json').read_text())
            self.assertEqual(refused['status'],'FAILED_RECALL_GATE_UNCHANGED');self.assertEqual(refused['measured_recall'],0.)
            self.assertEqual(refused['threshold'],.9);self.assertGreater(len(refused['query_ids']),0)
            with np.load(p/'failed-recall/failed-neighbors.npz') as saved:
                self.assertEqual(saved['neighbors'].shape,(64,30));self.assertTrue(np.isfinite(saved['distances']).all())

    def test_actual_twenty_epoch_bootstrap_continuation_both_modalities_and_export(self):
        from dl_binner.unified.training import configuration,bootstrap,reload_bootstrap
        from dl_binner.hybrid.bank import prepare as frozen_bank,model_pin
        from dl_binner.multiview.downstream import group
        from dl_binner.relational.pairs import prepare as original_pairs
        from dl_binner.multiview.arrays import load_arrays
        for glm in (False,True):
            with self.subTest(glm=glm), tempfile.TemporaryDirectory() as folder:
                f=fixture(folder); p=Path(folder); frozen=None
                if glm:
                    frozen=p/'frozen';frozen_bank(f['fasta'],f['features'],f['views'],frozen,NumericExtractor(),model_pin())
                cfg=configuration(glm);cfg.update(min_bin_bp=1,min_bin_contigs=1)
                bootstrap(f['features'],f['views'],f['tokens'],frozen,p/'bootstrap',cfg)
                reload_bootstrap(f['features'],f['views'],f['tokens'],frozen,p/'bootstrap/checkpoint.pt',p/'teacher.npz')
                group(p/'teacher.npz',f['features'],p/'teacher-graph',f['cfg'],4)
                original_pairs(f['features'],p/'teacher.npz',p/'teacher-graph/graph.npz',f['markers'],f['hmm'],p/'original-pairs')
                pairs.prepare(p/'original-pairs',f['features'],p/'teacher.npz',p/'teacher-graph/graph.npz',p/'pairs')
                actual_links,_=pairs.read(p/'pairs',f['features'])
                self.assertGreater(int((actual_links['sign']==1).sum()),0)
                self.assertGreater(int((actual_links['sign']==-1).sum()),0)
                saved,*_=model.read_bootstrap(p/'bootstrap/checkpoint.pt',f['features'],f['views'],f['tokens'],frozen)
                modules=model.initialize(saved)
                for module,key in zip(modules[:3],['model_state','target_state','predictor_state']):
                    self.assertTrue(all(torch.equal(x,module.state_dict()[k]) for k,x in saved[key].items()))
                self.assertEqual(model.state_digest(modules[0]),model.state_digest(modules[3]))
                self.assertEqual(modules[4].param_groups[0]['lr'],.0002)
                self.assertTrue(all(float(s['step'])==20 for s in modules[4].state.values()))
                bound={str(x):digest(x) for x in (p/'bootstrap').iterdir() if x.is_file()}
                args=(f['features'],f['views'],f['tokens'],frozen,p/'pairs',p/'bootstrap/checkpoint.pt')
                model.train(*args,p/'continued')
                model.embed(*args,p/'continued/checkpoint.pt',p/'candidate.npz')
                values,meta=load_arrays(p/'candidate.npz','embeddings')
                self.assertTrue(meta['reload_exact']);self.assertTrue(np.array_equal(values['ids'],f['data']['ids']))
                self.assertTrue(np.allclose(np.linalg.norm(values['features'][values['evidence']],axis=1),1,rtol=0,atol=1e-6))
                receipt=json.loads((p/'continued/checkpoint.json').read_text())
                self.assertEqual(receipt['inherited_updates'],20);self.assertEqual(receipt['added_updates'],20)
                self.assertEqual(receipt['initial_state']['anchor'],receipt['final_state']['anchor'])
                self.assertTrue(all(h['parents_seen']==int(f['data']['eligible'].sum()) for h in receipt['history']))
                self.assertTrue(all(h['available_views']==receipt['history'][0]['available_views'] for h in receipt['history']))
                self.assertFalse(receipt['exact_interrupted_resume']);self.assertFalse(receipt['truth_accessed'])
                self.assertTrue(all(digest(x)==d for x,d in bound.items()))
                with self.assertRaises(FileExistsError):model.train(*args,p/'continued')
                # Actual fixed E030 downstream path; fixture markers are explicit,
                # not a new detector, and no community quality is evaluated.
                group(p/'candidate.npz',f['features'],p/'candidate-graph',f['cfg'],4)
                # Marker detector's raw evidence is not the E013 quality schema.
                # Convert only this own fixture to physical weighted calls.
                quality=json.loads((p/'original-pairs/quality.json').read_text())
                physical=dict(panel_size=4,calls={q:{fam:[v['reliability']] for fam,v in fs.items()} for q,fs in quality['calls'].items()})
                write_json(p/'physical.json',physical)
                code = '''from pathlib import Path
import json,sys
from dl_binner.discovery import exact
from dl_binner.construction import grouping
from dl_binner.information.export import export
p=Path(sys.argv[1]); features=p/'data/features.npz'; emb=p/'candidate.npz'; graph=p/'candidate-graph/graph.npz'; physical=p/'physical.json'
exact.prepare(features,emb,graph,p/'search')
exact.run(features,emb,graph,physical,p/'search',p/'forest')
grouping.run(features,emb,graph,physical,p/'forest',p/'construction')
proof=grouping.audit(features,emb,graph,physical,p/'forest',p/'construction')
if proof['status']!='PASS': raise ValueError('Real construction audit failed')
for arm in ['root-only','pre','post']:
    export(features,p/'construction'/(arm+'-partition.json'),p/'assembly.fna',p/('export-'+arm),include_dna=True)
'''
                result=subprocess.run([sys.executable,'-I','-B','-c',code,str(p)],cwd=p,capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr+'\n'+result.stdout[-2000:])
                for arm in ['root-only','pre','post']:
                    account=json.loads((p/('export-'+arm)/'manifest.json').read_text())
                    self.assertEqual(account['contigs'],len(f['data']['ids']))
                    self.assertEqual(sum(x['bp'] for x in account['populations'].values()),int(f['data']['lengths'].sum()))


if __name__=='__main__':unittest.main()
