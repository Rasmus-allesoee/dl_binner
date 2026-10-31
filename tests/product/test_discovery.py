"""Actual restore/index/selection/export contracts, no community data or training."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from discovery_fixture import fixture
from dl_binner.discovery import grouping as new
from dl_binner.unified import grouping as old
from dl_binner.information.grouping import load_inputs
from dl_binner.density.grouping import sparse_input
from dl_binner.information.export import export
from dl_binner.context.tokens import binding


class Discovery(unittest.TestCase):
    """All new numerical work uses the real pinned sparse-index library."""
    def test_complete_disconnected_native_cache_refine_export_reload(self):
        with tempfile.TemporaryDirectory() as t:
            f=fixture(t);old_bytes={str(p):binding(p) for p in [f['features'],f['embeddings'],f['graph'],f['evidence']]}
            cache=f['root']/'cache';new.prepare(f['features'],f['embeddings'],f['graph'],cache,force_native=True)
            init=json.loads((cache/'initialization.json').read_text())
            self.assertEqual(init['missing_entries'],0)
            self.assertEqual(json.loads((cache/'proposal-audit.json').read_text())['invalid_rows'],0)
            args=[f['features'],f['embeddings'],f['graph'],f['evidence']]
            out=f['root']/'group';new.run(*args,cache,out);self.assertEqual(new.audit(*args,out)['status'],'PASS')
            for arm in ['parent','post']:
                value=export(f['features'],out/(arm+'-partition.json'),f['fasta'],f['root']/('export-'+arm),include_dna=True)
                self.assertEqual(value['contigs'],len(f['data']['ids']))
                self.assertEqual(value['bp'],int(f['data']['lengths'].sum()))
            self.assertEqual(old_bytes,{p:binding(p) for p in old_bytes})
            self.assertEqual(new.policy()['biological_policy'],old.policy())
            with self.assertRaises(FileExistsError):new.prepare(f['features'],f['embeddings'],f['graph'],cache)
            (cache/'neighbors.npz').write_bytes(b'corrupt')
            with self.assertRaises(ValueError):new.restore(f['features'],f['embeddings'],f['graph'],cache)

    def test_initializer_determinism_axis_mapping_and_tiny_ties(self):
        selected=np.array([5,1,3,0],np.int64);original={'neighbors':np.full((6,2),-1,np.int64)}
        for at,i in enumerate(selected):original['neighbors'][i]=selected[[j for j in range(4) if j!=at]][:2]
        a=new.complete_initialization(selected,original,6,4);b=new.complete_initialization(selected,original,6,4)
        np.testing.assert_array_equal(a,b)
        for i,row in enumerate(a):self.assertEqual(set(row),set(range(4)));self.assertEqual(row[0],i)
        bad=np.full((4,4),-1,np.int32)
        d=new.proposal_diagnostic(bad,selected,np.array(['a','b','c','d','e','f']),4)
        self.assertEqual(d['invalid_rows'],4);self.assertEqual(d['missing_or_out_of_range_entries'],16)
        data=dict(ids=np.array(['d','a','c','b']),tnf=np.full((4,136),1/136,np.float32),depth=np.zeros((4,10),np.float32),lengths=np.full(4,800,np.int64))
        values=np.zeros((4,64),np.float32);values[:,0]=1
        orig={'neighbors':np.array([[1,2,3],[0,2,3],[0,1,3],[0,1,2]])}
        with tempfile.TemporaryDirectory() as t:
            _,nn,dd,audit=new.retrieve(data,values,np.ones(4,bool),orig,old.policy(),4,Path(t)/'ties',force_native=True)
            self.assertEqual(audit['overall'],1.)
            self.assertTrue((dd>0).all());self.assertEqual(nn.shape,(4,3))

    def test_unknown_marker_and_failed_cache_refuse_without_fallback(self):
        with tempfile.TemporaryDirectory() as t:
            f=fixture(t);p=f['root']/'partial';p.mkdir()
            with self.assertRaises(FileNotFoundError):new.restore(f['features'],f['embeddings'],f['graph'],p)
            with self.assertRaises(ValueError):old.validate_evidence({'panel_size':4,'calls':{'unknown':{'x':[1.]}}},f['data']['ids'].tolist())

    def test_injected_native_failure_is_journaled_before_refusal(self):
        """Fault injection tests refusal/publication; the passing native test stays real."""
        class InvalidIndex:
            def __init__(self,data,**kwargs):
                self.neighbor_graph=(np.full((len(data),kwargs['n_neighbors']),-1,np.int32),None)
        with tempfile.TemporaryDirectory() as t:
            f=fixture(t);out=f['root']/'failed'
            with patch('pynndescent.NNDescent',InvalidIndex):
                with self.assertRaisesRegex(ValueError,'Incomplete native proposals'):
                    new.prepare(f['features'],f['embeddings'],f['graph'],out,force_native=True)
            d=json.loads((out/'proposal-audit.json').read_text())
            self.assertEqual(d['invalid_rows'],256);self.assertEqual(len(d['examples']),32)
            self.assertFalse((out/'completed.json').exists())
            with self.assertRaises(FileNotFoundError):new.restore(f['features'],f['embeddings'],f['graph'],out)


if __name__=='__main__':unittest.main()
