"""Self-contained installed-product regressions; no research helpers or caches."""
import importlib.metadata
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
import torch
from threadpoolctl import threadpool_info

import dl_binner
from dl_binner import io, model, clustering
from dl_binner.accounting import summarize_arm
from dl_binner.contracts import check_files, file_record
from dl_binner.runner import PACKAGE, source_records
from dl_binner.supervision import local_scheduler_options
from fixtures import THREADS, write_fixture


class ProductContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dl-binner-product-')
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_installed_owned_origins_version_and_packaged_resources(self):
        self.assertEqual(dl_binner.__version__, importlib.metadata.version('dl-binner'))
        self.assertEqual(dl_binner.__version__, '0.1.0.dev2')
        for module in (dl_binner, np, torch):
            self.assertTrue(Path(module.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()), module.__file__)
        self.assertIsNone(torch.version.cuda)
        accepted = json.loads((Path(__file__).parent/'accepted-package.json').read_text())
        self.assertEqual({k:v for k,v in source_records().items() if k != '__init__.py'}, accepted)
        model.configure_torch(THREADS)
        self.assertEqual(torch.get_num_threads(),THREADS)
        self.assertEqual(torch.get_num_interop_threads(),1)
        self.assertTrue(all(p['num_threads'] <= THREADS for p in threadpool_info()))
        self.assertIn('previous=lambda', (PACKAGE/'resources/run.smk').read_text())

    def test_fasta_iupac_strand_counts_and_invalid_inputs(self):
        dna = 'AAAACGTACGTRYSWKMBDHVNAAAA'
        rc = dna.translate(str.maketrans('ACGTRYSWKMBDHVN','TGCAYRSWMKVHDBN'))[::-1]
        values, count = io.tnf([('a',dna),('b',rc),('n','NNNN'),('tiny','A')])
        np.testing.assert_array_equal(values[0],values[1])
        self.assertEqual(count[0],sum(set(dna[i:i+4]) <= set('ACGT') for i in range(len(dna)-3)))
        self.assertEqual(count[-2:].tolist(),[0,0])
        for content in ('>same\nACGT\n>same\nACGT\n','>x\nACGZ\n','>x\n','ACGT\n','>\nACGT\n'):
            path=self.root/'bad.fna';path.write_text(content)
            with self.assertRaises(ValueError):io.read_fasta(path)

    def test_depth_order_zeros_missing_duplicate_nonfinite_and_negative(self):
        depth=self.root/'depth.tsv'
        depth.write_text('contig_id\tS1\tS2\nc\t3\t0\na\t0\t0\nb\t0\t4\n')
        samples, values=io.read_depth(depth,['a','b','c'])
        self.assertEqual(samples,['S1','S2']);np.testing.assert_array_equal(values,[[0,0],[0,4],[3,0]])
        for content in ('contig_id\tS1\tS1\n','contig_id\tS1\na\t1\n',
                        'contig_id\tS1\na\t1\nb\t2\nc\t3\nd\t4\n',
                        'contig_id\tS1\na\t-1\n','contig_id\tS1\na\tnan\n',
                        'contig_id\tS1\na\tinf\n','contig_id\tS1\na\t1\na\t2\n'):
            depth.write_text(content)
            with self.assertRaises(ValueError):io.read_depth(depth,['a','b','c'])
        samples,values=io.read_depth(None,['a','b','c'])
        self.assertEqual(samples,[]);self.assertEqual(values.shape,(3,0))

    def test_fresh_features_all_strata_and_transform_preserves_original_masks(self):
        fasta,depth,rows=write_fixture(self.root)
        path=self.root/'features.npz';io.prepare(fasta,path,depth)
        data,meta=io.load_arrays(path,'features')
        self.assertEqual(data['ids'].tolist(),[i for i,_ in rows])
        self.assertEqual(meta['samples'],['software_S1','software_S2'])
        self.assertEqual(int(data['eligible'].sum()),10)
        self.assertEqual(data['exclusion_reason'].tolist()[:2],['below_min_length']*2)
        self.assertEqual(data['exclusion_reason'][-1],'no_valid_fourmers')
        np.testing.assert_array_equal(data['zero_depth'],data['depth']==0)
        self.assertEqual(int((~data['depth_evidence']).sum()),3)
        state=model.fit_transform(data);before=json.dumps(state,sort_keys=True)
        x,valid=model.transform(data,state)
        np.testing.assert_array_equal(x[~data['depth_evidence'],136:],0)
        self.assertEqual(json.dumps(state,sort_keys=True),before)
        self.assertTrue(np.isfinite(x).all());self.assertTrue(valid[data['eligible']].all())
        # Mean depth remains a magnitude-bearing block after the saved transform.
        changed={k:v.copy() for k,v in data.items()};changed['depth'][1:3]*=10
        transformed,_=model.transform(changed,state)
        self.assertFalse(np.array_equal(x[:,136:],transformed[:,136:]))
        broken=json.loads(json.dumps(state));broken['tnf']['std'][0]=-1
        with self.assertRaises(ValueError):model.transform(data,broken)

    def test_cached_bytes_order_and_mask_corruption_fail(self):
        fasta,_,_=write_fixture(self.root);path=self.root/'features.npz';io.prepare(fasta,path)
        data,meta=io.load_arrays(path,'features');data['ids']=data['ids'][::-1]
        with path.open('wb') as stream:np.savez(stream,**data)
        meta['sha256']=io.digest(path);path.with_suffix('.json').write_text(json.dumps(meta))
        with self.assertRaisesRegex(ValueError,'ordered-ID'):io.load_arrays(path,'features')
        with path.open('ab') as stream:stream.write(b'corrupt')
        with self.assertRaises(ValueError):io.load_arrays(path,'features')
        original=self.root/'new.npz';io.prepare(fasta,original)
        data,meta=io.load_arrays(original,'features');data['eligible'][0]=True
        with self.assertRaisesRegex(ValueError,'eligibility'):io.validate_features(data,meta)

    def test_training_checkpoint_exact_reload_order_schema_and_corruption(self):
        fasta,depth,_=write_fixture(self.root);features=self.root/'features.npz';io.prepare(fasta,features,depth)
        checkpoint=self.root/'checkpoint.pt';config=PACKAGE/'resources/training.json'
        model.train(features,config,checkpoint,THREADS)
        model.embed(features,self.root/'reloaded.npz',checkpoint,THREADS)
        ref,_=io.load_arrays(checkpoint.with_suffix('.reference.npz'),'embeddings')
        actual,_=io.load_arrays(self.root/'reloaded.npz','embeddings')
        for key in ref:np.testing.assert_array_equal(ref[key],actual[key])
        report=json.loads(checkpoint.with_suffix('.json').read_text())
        self.assertEqual(report['config'],json.loads(config.read_text()))
        self.assertEqual(len(report['epochs']),20);self.assertEqual(report['loader_workers'],0)
        self.assertTrue(all(e['contigs_seen']==10 for e in report['epochs']))
        state,_=model.load_checkpoint(checkpoint,['software_S1','software_S2'])
        self.assertEqual(state['transform'],report['transform'])
        with self.assertRaisesRegex(ValueError,'sample'):model.load_checkpoint(checkpoint,['software_S2','software_S1'])
        with self.assertRaises(FileExistsError):model.train(features,config,checkpoint,THREADS)
        with checkpoint.open('ab') as stream:stream.write(b'bad')
        with self.assertRaisesRegex(ValueError,'byte/receipt'):model.load_checkpoint(checkpoint,['software_S1','software_S2'])

    def test_insufficient_evidence_and_invalid_training_configuration(self):
        path=self.root/'none.fna';path.write_text('>short\nACGT\n>ambiguous\nNNNNNNNN\n')
        out=self.root/'features.npz';io.prepare(path,out,min_length=5)
        data,_=io.load_arrays(out,'features')
        with self.assertRaisesRegex(ValueError,'two eligible'):model.fit_transform(data)
        config=json.loads((PACKAGE/'resources/training.json').read_text())
        for field,value in [('epochs',0),('batch_size',1),('temperature',float('nan')),('mask_probability',1),('unknown',0)]:
            with self.subTest(field=field),self.assertRaises(ValueError):model.validate_config({**config,field:value})

    def test_fixed_geometry_ties_query_blocks_and_noise(self):
        ids=['b','a','c','d','e','f','z']
        values=np.array([[2,1]]*3+[[1,2]]*3+[[0,0]])
        first=clustering.geometry(values,ids,query_block=1)
        self.assertEqual(first['assignment'][-1],-1);self.assertEqual(first['clusters'],2)
        for block in (3,128):
            actual=clustering.geometry(values,ids,query_block=block)
            for key in ('assignment','neighbors','valid','edges','clusters','unassigned'):
                self.assertEqual(actual[key],first[key])
        self.assertEqual(first['clustering']['expected_cluster_count'],None)

    def test_export_all_dna_empty_bins_and_semantic_reason_corruption(self):
        fasta=self.root/'tiny.fna';fasta.write_text('>short\nACGT\n>ambiguous\nNNNNNNNN\n>eligible\nACGTACGT\n')
        features=self.root/'features.npz';io.prepare(fasta,features,min_length=5)
        partition=self.root/'partition.json'
        partition.write_text(json.dumps(dict(ids=['short','ambiguous','eligible'],parent_features_sha256=io.digest(features),
            assignment=[-1,-1,-1],valid=[False,False,True],reason=['zero_geometry_evidence','zero_geometry_evidence','isolated_graph'],clusters=0,unassigned=3)))
        clustering.export(features,partition,fasta,self.root/'bins')
        summary,_=summarize_arm(features,self.root/'bins')
        self.assertEqual(summary['bin_count'],0);self.assertIsNone(summary['bin_size_bp']['median'])
        self.assertEqual(summary['reasons']['excluded'],{'below_min_length':1,'no_valid_fourmers':1})
        self.assertEqual(len(summary['length_strata']),6)
        exported=[]
        for path in (self.root/'bins').glob('*.fna'):
            if path.stat().st_size:exported.extend(io.read_fasta(path))
        self.assertEqual(dict(exported),dict(io.read_fasta(fasta)))
        table=self.root/'bins/assignments.tsv';table.write_text(table.read_text().replace('no_valid_fourmers','false_reason'))
        manifest=self.root/'bins/manifest.json';value=json.loads(manifest.read_text())
        value['files']['assignments.tsv']=file_record(table);manifest.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError,'Exclusion reason'):summarize_arm(features,self.root/'bins')

    def test_byte_inventory_links_and_aggregate_scheduler_limits(self):
        path=self.root/'valid';path.write_text('one');entry=file_record(path)
        check_files(self.root,{'valid':entry});path.write_text('two')
        with self.assertRaises(ValueError):check_files(self.root,{'valid':entry})
        path.unlink();path.symlink_to(self.root/'absent')
        with self.assertRaises(ValueError):check_files(self.root,{'valid':entry})
        with self.assertRaises(ValueError):check_files(self.root,{'../outside':entry})
        options=local_scheduler_options(4,8000)
        self.assertNotIn('--jobs',options);self.assertIn('mem_mb=global',options)
        for threads,memory in ((0,8000),(5,8000),(4,0),(4,8001)):
            with self.assertRaises(ValueError):local_scheduler_options(threads,memory)


if __name__ == '__main__':unittest.main()
