"""Actual exact-score/cache/group/export contracts on tiny real feature fixtures."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from discovery_fixture import fixture
from dl_binner.discovery import exact
from dl_binner.discovery import grouping as old
from dl_binner.unified import grouping as frozen
from dl_binner.information.export import export
from dl_binner.context.tokens import binding


class ExactDiscovery(unittest.TestCase):
    def test_real_cache_group_reload_export_and_inherited_reuse(self):
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);f=fixture(root/'fixture',64);cache=root/'exact'
            before={k:binding(f[k])for k in ['features','embeddings','graph','fasta','evidence']}
            proof=exact.prepare(f['features'],f['embeddings'],f['graph'],cache)
            self.assertEqual(proof['status'],'PASS')
            (data,vec,valid,meta,a),_=exact.restore(f['features'],f['embeddings'],f['graph'],cache)
            vals,pos,scales,selected,_=frozen.channels(data,vec,valid,frozen.policy())
            inverse=np.full(len(data['ids']),-1);inverse[selected]=np.arange(len(selected))
            for local,i in enumerate(selected):
                other=selected[selected!=i];dist=frozen.distances(data,vals,pos,scales,frozen.policy(),i,other)
                order=np.lexsort((data['ids'][other],dist))[:30]
                np.testing.assert_array_equal(a['neighbors'][local],inverse[other[order]])
                np.testing.assert_array_equal(a['distances'][local],dist[order])
            out=root/'result';exact.run(f['features'],f['embeddings'],f['graph'],f['evidence'],cache,out)
            self.assertEqual(exact.audit(f['features'],f['embeddings'],f['graph'],f['evidence'],out)['status'],'PASS')
            for arm in ['parent','post']:
                result=export(f['features'],out/(arm+'-partition.json'),f['fasta'],root/('export-'+arm),include_dna=False)
                self.assertEqual(result['bp'],int(f['data']['lengths'].sum()))
            old.prepare(f['features'],f['embeddings'],f['graph'],root/'inherited')
            _,m=exact.restore(f['features'],f['embeddings'],f['graph'],root/'inherited')
            self.assertNotIn('backend',m)
            self.assertEqual(before,{k:binding(f[k])for k in before})

    def test_cancellation_ties_and_zero_or_absent_depth_match_global_oracle(self):
        rng=np.random.default_rng(11);n=80;ids=np.array([f'opaque-{n-i:03d}'for i in range(n)])
        lengths=np.full(n,100000,np.int64);selected=np.argsort(ids).astype(np.int64)
        u=np.ones((n,64),np.float32);u/=8;u[20:,0]+=rng.normal(0,1e-7,n-20).astype(np.float32)
        c=np.full((n,136),np.sqrt(1/136),np.float32)
        data=dict(ids=ids,lengths=lengths)
        for width in [0,10]:
            depth=np.zeros((n,width),np.float32)
            if width:depth[40:]=.5
            pos=(depth>0).any(1);values=(u,c,depth);scales=np.array([1e-12,1e-12,1e-12])
            near,dist,certificate=exact.exact_neighbors(data,values,pos,scales,selected,frozen.policy())
            inverse=np.empty(n,np.int64);inverse[selected]=np.arange(n)
            for local,i in enumerate(selected):
                other=selected[selected!=i];score=frozen.distances(data,values,pos,scales,frozen.policy(),i,other)
                order=np.lexsort((ids[other],score))[:30]
                np.testing.assert_array_equal(near[local],inverse[other[order]])
                np.testing.assert_array_equal(dist[local],score[order])
            self.assertEqual(certificate['certified_rows'],n)
            self.assertGreater(certificate['maximum_candidate_pool'],30)

    def test_corrupt_or_unknown_cache_refused_without_repair(self):
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);f=fixture(root/'fixture',32);cache=root/'exact'
            exact.prepare(f['features'],f['embeddings'],f['graph'],cache)
            p=cache/'completed.json';value=json.loads(p.read_text());value['backend']['query_rows']=32;p.write_text(json.dumps(value))
            with self.assertRaises(ValueError):exact.restore(f['features'],f['embeddings'],f['graph'],cache)
            value['backend']['query_rows']=64;p.write_text(json.dumps(value))
            with(cache/'neighbors.npz').open('ab')as s:s.write(b'corrupt')
            with self.assertRaises(ValueError):exact.restore(f['features'],f['embeddings'],f['graph'],cache)


if __name__=='__main__':unittest.main()
