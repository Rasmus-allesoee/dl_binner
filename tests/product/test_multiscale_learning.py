"""Actual tiny measured-view training, old-state preservation and export contracts.

GLM inference alone is an explicit numeric mock; token/bank/native PyTorch paths
are real. Cached HMM files and hand-authored domains do not test marker detection.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pysam
import torch

from relational_fixture import fixture,NumericExtractor
from dl_binner.bootstrap import model as old_model,pairs as old_pairs
from dl_binner.multiscale import model,measurement,cache,pairs
from dl_binner.io import digest
from dl_binner.model import configure_torch
from dl_binner.multiview.arrays import load_arrays


def measured(root,f):
    """Encode ten coordinate-sorted real BAMs, retaining true crop-local variation."""
    root=Path(root);root.mkdir();data=f['data'];header={'HD':{'VN':'1.6','SO':'coordinate'},
        'SQ':[dict(SN=str(q),LN=int(n)) for q,n in zip(data['ids'],data['lengths'])]}
    samples=[]
    for j,sample in enumerate(f['metadata']['samples']):
        bam=root/('tiny-%02d.bam'%j)
        with pysam.AlignmentFile(bam,'wb',header=header) as stream:
            for i,(ident,length) in enumerate(zip(data['ids'],data['lengths'])):
                if ident=='no-signal':continue
                for pos in range(0,max(1,int(length)-49),160):
                    n=min(100,int(length)-pos)
                    for rep in range(1+int(data['depth'][i,j]/10)):
                        read=pysam.AlignedSegment(stream.header);read.query_name=f'fixture-{i}-{pos}-{rep}'
                        read.flag=0;read.reference_id=i;read.reference_start=pos;read.mapping_quality=60
                        read.cigarstring=str(n)+'M';read.query_sequence='A'*n;read.query_qualities=pysam.qualitystring_to_array('I'*n)
                        read.set_tag('NM',0);stream.write(read)
        target=root/('sample-%02d'%j);measurement.summarize(bam,f['features'],f['views'],target,sample);samples.append(target)
    cache.seal(root,f['features'],f['views'],samples);cache.rebind(root,f['features'],f['views'],root/'new-features.npz')
    return root/'new-features.npz'


def source(root,f,glm=False):
    """Generate an actual twenty-epoch E031-format engineering source, not a stub."""
    from dl_binner.unified.training import configuration,bootstrap,reload_bootstrap
    from dl_binner.hybrid.bank import prepare,model_pin
    from dl_binner.multiview.downstream import group
    from dl_binner.relational.pairs import prepare as proposals
    root=Path(root);root.mkdir();frozen=None
    if glm:
        frozen=root/'frozen';prepare(f['fasta'],f['features'],f['views'],frozen,NumericExtractor(),model_pin())
    cfg=configuration(glm);cfg.update(min_bin_bp=1,min_bin_contigs=1)
    bootstrap(f['features'],f['views'],f['tokens'],frozen,root/'bootstrap',cfg)
    reload_bootstrap(f['features'],f['views'],f['tokens'],frozen,root/'bootstrap/checkpoint.pt',root/'teacher.npz')
    group(root/'teacher.npz',f['features'],root/'teacher-graph',cfg,4)
    proposals(f['features'],root/'teacher.npz',root/'teacher-graph/graph.npz',f['markers'],f['hmm'],root/'proposals')
    old_pairs.prepare(root/'proposals',f['features'],root/'teacher.npz',root/'teacher-graph/graph.npz',root/'pairs')
    old_model.train(f['features'],f['views'],f['tokens'],frozen,root/'pairs',root/'bootstrap/checkpoint.pt',root/'E031')
    return root/'E031/checkpoint.pt',frozen


class Learning(unittest.TestCase):
    def setUp(self):configure_torch(4)

    def test_real_teacher_student_reload_unit_geometry_gradients_and_full_export(self):
        from dl_binner.multiview.downstream import group
        from dl_binner.information.export import export
        from dl_binner.information.grouping import load_inputs
        from dl_binner.bootstrap import bridge
        for glm in (False,True):
            with self.subTest(glm=glm),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);f=fixture(root/'dna');new=measured(root/'measured',f)
                original,frozen=source(root/'source',f,glm)
                protected={str(p):digest(p) for p in [f['features'],f['views'],original,original.with_suffix('.json')]}
                saved,_=model.read_original(original,f['features'],f['views'],f['tokens'],frozen)
                modules=model.initialize(saved);online,target,predictors,anchor,optimizer=modules
                for base,key in [(online.base,'model_state'),(target.base,'target_state'),(predictors,'predictor_state')]:
                    self.assertTrue(all(torch.equal(x,base.state_dict()[k]) for k,x in saved[key].items()))
                self.assertTrue(all(p not in optimizer.state for n,p in online.named_parameters() if not n.startswith('base.')))
                self.assertTrue(all(p.grad is None for p in target.parameters()))
                args=(f['features'],new,f['views'],f['tokens'],frozen,root/'measured',original)
                # Full twenty-epoch engineering exposure in each new stage.
                model.train(*args,root/'teacher')
                model.embed(*args,root/'teacher/checkpoint.pt',root/'teacher.npz')
                cfg=saved['config'];group(root/'teacher.npz',new,root/'teacher-graph',cfg,4)
                r=pairs.prepare(new,f['features'],f['views'],root/'measured',root/'teacher.npz',root/'teacher-graph/graph.npz',f['markers'],f['hmm'],root/'pairs')
                links,_=pairs.read(root/'pairs/cache',new)
                self.assertLessEqual(len(links['left']),r['source_pair_count'])
                model.train(*args,root/'student',teacher=root/'teacher/checkpoint.pt',pairs=root/'pairs/cache')
                model.embed(*args,root/'student/checkpoint.pt',root/'student.npz',pairs=root/'pairs/cache')
                values,meta=load_arrays(root/'student.npz','embeddings');self.assertTrue(meta['reload_exact'])
                np.testing.assert_allclose(np.linalg.norm(values['features'][values['evidence']],axis=1),1,rtol=0,atol=1e-6)
                self.assertEqual(values['ids'].tolist(),f['data']['ids'].tolist())
                checkpoint,record=model.read_candidate(root/'student/checkpoint.pt')
                self.assertEqual(len(record['history']),20);self.assertEqual(checkpoint['total_updates'],80)
                self.assertTrue(all(h['parents_seen']==int(f['data']['eligible'].sum()) for h in record['history']))
                self.assertTrue(all(h['original_pair_slots']==r['source_pair_count'] and h['accepted_pairs']==len(links['left']) for h in record['history']))
                self.assertEqual(record['initial_state']['anchor'],record['final_state']['anchor'])
                teacher,_=model.read_candidate(root/'teacher/checkpoint.pt')
                self.assertGreater(float(checkpoint['model_state']['residual.weight'].abs().sum()),0.)
                self.assertTrue(all(torch.isfinite(t).all() for t in checkpoint['model_state'].values()))
                # Actual downstream graph and exact E023 native export readers.
                group(root/'student.npz',new,root/'student-graph',cfg,4)
                bridge_cfg=dict(version=1,seed=11,neighbors=30,candidates=60,min_samples=10,min_bin_contigs=2,min_bin_bp=10000,
                    exact_threshold=2048,audit_queries=32,min_neighbor_recall=.9,calibration_pairs=8192,batch_rows=512,length_scale_bp=2500,
                    marker_excess_penalty=5.,distance_floor=.000001)
                from dl_binner.io import write_json
                write_json(root/'policy.json',bridge_cfg)
                write_json(root/'bridge-lock.json',dict(files={'src/dl_binner/density/grouping.py':dict(bytes=Path(bridge.original.__file__).stat().st_size,sha256=digest(bridge.original.__file__))},policy=dict(bytes=(root/'policy.json').stat().st_size,sha256=digest(root/'policy.json'))))
                write_json(root/'quality.json',dict(panel_size=4,calls={str(q):{'family-0':[.95]} for q in f['data']['ids'][:8]}))
                bridge.run(new,root/'student.npz',root/'student-graph/graph.npz',root/'quality.json',f['fasta'],root/'policy.json',root/'bridge-lock.json',root/'group',engineering=True)
                account=json.loads((root/'group/export/selected/manifest.json').read_text())
                self.assertEqual(account['bp'],int(f['data']['lengths'].sum()));self.assertEqual(account['contigs'],len(values['ids']))
                self.assertTrue(all(digest(p)==h for p,h in protected.items()))
                with self.assertRaisesRegex(ValueError,'hash differs'):
                    (root/'student/checkpoint.pt').write_bytes((root/'student/checkpoint.pt').read_bytes()+b'bad');model.read_candidate(root/'student/checkpoint.pt')

    def test_pair_reliability_coabsence_versus_measured_contrast_and_guarded_negative_gradient(self):
        x=np.array([[.5,.5,0],[.5,.5,0],[0,0,0]],np.float32)
        y=np.array([[0,0,0],[.5,.5,0],[0,0,0]],np.float32)
        count,weight=pairs.attenuation(x,y,np.array([-1,1,-1]))
        np.testing.assert_array_equal(count,[2,2,0]);np.testing.assert_allclose(weight,[1/3,1/3,0])
        self.assertEqual(float(pairs.attenuation(x[:1],y[:1],np.array([1]))[1][0]),0.)
        from dl_binner.relational.model import signed_loss
        from torch import nn
        # Distinct nearby endpoints must receive an actual repulsive gradient;
        # identical unit endpoints can sit at the cosine maximum with zero slope.
        raw=torch.ones(1,2,64);raw[0,1,:32]=2.;raw.requires_grad_(True)
        unit=torch.nn.functional.normalize(raw,dim=2)
        positive,negative=signed_loss([unit,unit],[unit.detach(),unit.detach()],[nn.Identity(),nn.Identity()],torch.tensor([-1],dtype=torch.int8),torch.tensor([1/3]),.2)
        self.assertEqual(float(positive),0.);self.assertGreater(float(negative),0.)
        negative.backward();self.assertTrue(torch.isfinite(raw.grad).all())
        self.assertGreater(float(raw.grad.abs().sum()),0.)
        with self.assertRaisesRegex(ValueError,'Malformed'):pairs.attenuation(x*3,y,np.array([-1,1,-1]))

    def test_reliability_residual_zero_initialization_mask_and_gradient(self):
        from dl_binner.unified.training import configuration
        from dl_binner.relational.model import initialize
        cfg=configuration(False);torch.manual_seed(11);base,_,_=initialize(10,cfg)
        extended=model.Encoder(base,10,cfg).eval()
        s=torch.randn(8,136);d=torch.randn(8,10);e=torch.ones(8,dtype=torch.bool)
        local=torch.randn(8,8,136);pos=torch.randn(8,8,3);mask=torch.ones(8,8,dtype=torch.bool)
        base_args=[s,d,e,local,pos,mask];cells=torch.randn(8,10,12);weight=torch.ones(8,10)
        z=extended(*base_args,cells,weight)[0]
        self.assertTrue(torch.equal(z,torch.nn.functional.normalize(base(*base_args)[0],dim=1)))
        loss=(z*torch.randn_like(z)).sum();loss.backward();self.assertGreater(float(extended.residual.weight.grad.abs().sum()),0.)
        self.assertEqual(float(extended.cell[0].weight.grad.abs().sum()),0.)
        with torch.no_grad():extended.residual.weight.fill_(.1)
        zero=torch.zeros_like(weight)
        self.assertTrue(torch.equal(extended(*base_args,cells,zero)[0],torch.nn.functional.normalize(base(*base_args)[0],dim=1)))
        with self.assertRaisesRegex(ValueError,'axes/weights'):extended(*base_args,cells,weight*2)
        cfg=model.policy();cfg['epochs']=21
        with self.assertRaisesRegex(ValueError,'Unfrozen'):model.policy(cfg)


if __name__=='__main__':unittest.main()
