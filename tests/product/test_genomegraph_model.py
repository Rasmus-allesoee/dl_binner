"""Actual sparse messages, measured cache, graph fit/reload and DNA export contracts.

Bootstrap vectors and cached marker domains are synthetic engineering inputs;
BAM readers, per-window moments, tensor gradients and export writers are real.
No community or biological quality is evaluated by these tests.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import pysam
import torch

from dl_binner.genomegraph import model,links
from dl_binner.io import digest
from dl_binner.multiscale.cache import Bank
from dl_binner.multiview.arrays import load_arrays
from relational_fixture import fixture
from test_multiscale_learning import measured


def physical(root,f):
    """Encode independently placed true-mate fixture records for the full DNA axis."""
    root=Path(root);root.mkdir();d=f['data'];bam=root/'pairs.bam'
    with pysam.AlignmentFile(bam,'wb',header=dict(HD=dict(VN='1.6',SO='unsorted'),SQ=[dict(SN=str(i),LN=int(n)) for i,n in zip(d['ids'],d['lengths'])])) as out:
        records=[]
        pairs=[('cal0',0,1000,0,1250),('cal1',0,1100,0,1350)]
        for i in range(0,12,2):
            for k in range(3):pairs.append((f'opaque-{i}-{k}',i,3000+k,i+1,k))
        for name,i,p,j,q in pairs:
            for role,ref,pos,mate,other in [(1,i,p,j,q),(2,j,q,i,p)]:
                r=pysam.AlignedSegment(out.header);r.query_name=name;r.flag=1|(64|32 if role==1 else 128|16)
                r.reference_id=ref;r.reference_start=pos;r.next_reference_id=mate;r.next_reference_start=other
                r.mapping_quality=60;r.cigarstring='150M';r.query_sequence='A'*150;r.set_tag('NM',0);records.append(r)
        for r in records:out.write(r)
    links.extract(bam,d['ids'].tolist(),d['lengths'],d['eligible'],'Z9',root/'links',threads=2,cfg=dict(links.DEFAULT,min_calibration=2))
    return root/'links'


class GraphRepresentation(unittest.TestCase):
    def test_sparse_one_two_hop_messages_and_exact_unlinked_forward(self):
        x=np.arange(12,dtype=np.float32).reshape(4,3);edges=np.array([[0,1],[1,2]],np.int64)
        one,adj=model.messages(x,edges,np.ones(2));two=adj@one
        np.testing.assert_array_equal(one,np.array([x[1],(x[0]+x[2])/2,x[1],np.zeros(3)]))
        np.testing.assert_array_equal(two[3],np.zeros(3))
        torch.manual_seed(11);encoder=model.Encoder(3,64,2)
        base=torch.nn.functional.normalize(torch.randn(4,64),dim=1);active=torch.tensor([True,True,True,False])
        out=encoder(base,torch.from_numpy(x),torch.from_numpy(one),torch.from_numpy(two.astype(np.float32)),base,active)
        self.assertTrue(torch.equal(out[~active],base[~active]));self.assertTrue(torch.allclose(out[active],base[active],rtol=0,atol=1e-6))
        out[:3,0].sum().backward();self.assertGreater(float(encoder.residual.weight.grad.abs().sum()),0)

    def test_real_measured_cache_twenty_epoch_fit_reload_full_DNA_and_export(self):
        from dl_binner.information.export import export
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);f=fixture(root/'dna');measured(root/'coverage',f);bank=Bank(root/'coverage',f['features'],f['views'])
            p=physical(root/'physical',f);protected={str(x):digest(x) for x in [f['features'],f['views'],f['embeddings'],f['graph'],root/'coverage/bank.json']}
            model.cache(f['features'],f['embeddings'],f['graph'],p,bank,root/'cache')
            cache,meta=load_arrays(root/'cache/features.npz','genome_graph_features');self.assertTrue(meta['parent_is_not_window'])
            self.assertEqual(int(cache['active'].sum()),12);self.assertEqual(cache['depth'].shape,(len(f['data']['ids']),10))
            receipt=model.train(root/'cache/features.npz',root/'fit',4,engineering_epochs=20)
            self.assertTrue(receipt['reload_exact']);self.assertEqual(len(receipt['history']),20)
            emb,em=load_arrays(root/'fit/embeddings.npz','embeddings')
            np.testing.assert_array_equal(emb['features'][~cache['active']],cache['bootstrap'][~cache['active']])
            saved=torch.load(root/'fit/checkpoint.pt',map_location='cpu',weights_only=True)
            self.assertGreater(float(saved['state']['residual.weight'].abs().sum()),0.)
            e=cache['edges'];before=(cache['bootstrap'][e[:,0]]*cache['bootstrap'][e[:,1]]).sum(1).mean();after=(emb['features'][e[:,0]]*emb['features'][e[:,1]]).sum(1).mean()
            self.assertGreater(float(after),float(before)+.1)
            z=emb['features'][cache['active']];mean_other=((z.sum(0)**2).sum()-len(z))/(len(z)*(len(z)-1));self.assertLess(float(mean_other),.5)
            # Use the real cached marker/refiner and export through an isolated
            # graph worker, matching the native numerical-family separation.
            args=[sys.executable,'-I','-B','-c',
                'import json,sys;from pathlib import Path;from dl_binner.multiview.downstream import group,refine;from dl_binner.information.export import export;'
                'r=Path(sys.argv[1]);f=json.loads((r/"paths.json").read_text());cfg=f["cfg"];'
                'group(r/"fit/embeddings.npz",f["features"],r/"group",cfg,4);'
                'refine(f["features"],r/"fit/embeddings.npz",r/"group/partition.json",f["markers"],f["fasta"],f["hmm"],r/"refine",cfg);'
                'export(f["features"],r/"refine/partition.json",f["fasta"],r/"export");',str(root)]
            paths={k:str(f[k]) for k in ['features','markers','fasta','hmm']};paths['cfg']=f['cfg'];(root/'paths.json').write_text(json.dumps(paths))
            result=subprocess.run(args,capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            manifest=json.loads((root/'export/manifest.json').read_text());self.assertEqual(manifest['contigs'],len(f['data']['ids']));self.assertEqual(manifest['bp'],int(f['data']['lengths'].sum()))
            self.assertEqual(protected,{n:digest(n) for n in protected})


if __name__=='__main__':unittest.main()
