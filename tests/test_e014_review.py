"""Actual tiny retained readers and independent E014 diagnostic accounting contracts."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e014_review import export_accounting,parent_geometry,marker_review,oral_population
from e014_collect import binding


class ReviewContracts(unittest.TestCase):
    def test_full_export_accounting_and_actual_axis_refusal(self):
        import numpy as np
        with tempfile.TemporaryDirectory()as t:
            p=Path(t)/'assignments.tsv';part=dict(ids=['a','b','c'],assignment=[0,-1,-1],reason=['','noise','below_min_length'])
            data=dict(lengths=np.array([1000,800,499]),eligible=np.array([True,True,False]),exclusion_reason=np.array(['','','below_min_length']));rows=[['a',1000,'bin_000001','assigned',''],['b',800,'','unassigned','noise'],['c',499,'','excluded','below_min_length']]
            def write():
                with p.open('w')as f:
                    w=csv.writer(f,delimiter='\t');w.writerow(['contig_id','length','bin_id','status','reason']);w.writerows(rows)
            write();account=dict(contigs=3,bp=2299,statuses=dict(assigned=dict(contigs=1,bp=1000),unassigned=dict(contigs=1,bp=800),excluded=dict(contigs=1,bp=499)),bin_count=1,bins={'bin_000001':dict(bp=1000)})
            r=export_accounting(part,data,p,account,dict(bins=1));self.assertEqual(r['bp'],2299)
            rows[1][0]='a';write()
            with self.assertRaisesRegex(ValueError,'axes'):export_accounting(part,data,p,account,dict(bins=1))

    def test_actual_native_export_separates_exclusion_from_geometry_reason(self):
        from dl_binner.io import prepare,load_arrays,digest
        from dl_binner.clustering import export
        from dl_binner.accounting import summarize_arm
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);fasta=root/'input.fna';fasta.write_text('>long\n'+'ACGT'*250+'\n>noise\n'+'TGCA'*200+'\n>short\nACGT\n')
            features=root/'features';features.mkdir();f=features/'features.npz';prepare(fasta,f)
            data,_=load_arrays(f,'features');part=dict(ids=['long','noise','short'],assignment=[0,-1,-1],valid=[True,True,False],reason=['','density_noise','zero_geometry_evidence'],clusters=1,unassigned=2,parent_features_sha256=digest(f))
            partition=root/'partition.json';partition.write_text(json.dumps(part));out=root/'export';export(f,partition,fasta,out)
            r=export_accounting(part,data,out/'assignments.tsv',summarize_arm(f,out)[0],json.loads((out/'manifest.json').read_text()));self.assertEqual(r['statuses']['excluded']['bp'],4)
            table=out/'assignments.tsv';table.write_text(table.read_text().replace('below_min_length','zero_geometry_evidence'))
            with self.assertRaisesRegex(ValueError,'reasons differ'):export_accounting(part,data,table,dict(contigs=3,bp=1804),dict(bins=1))

    def test_raw_geometry_unknown_neighbors_and_mismatched_learned_structure(self):
        import numpy as np
        ids=['opaque_'+str(i)for i in range(12)];tnf=np.zeros((12,136),np.float32);tnf[:6,0]=1;tnf[6:,1]=1
        data=dict(tnf=tnf,depth=np.empty((12,0),np.float32),depth_evidence=np.zeros(12,bool),eligible=np.ones(12,bool),lengths=np.full(12,1000))
        state=dict(tnf=dict(mean=[.5,.5]+[0.]*134,std=[.5,.5]+[0.]*134),depth=dict(mean=[],std=[]))
        part=dict(ids=ids,neighbors=[ids[6:11]if i<6 else ids[:5]for i in range(12)])
        labels={q:('A'if i<5 else None if i==5 else'B')for i,q in enumerate(ids)}
        r=parent_geometry(data,state,part,labels)
        self.assertEqual(len(r['queries']),11);self.assertAlmostEqual(r['raw_mean'],10/11);self.assertEqual(r['learned_mean'],0)
        self.assertEqual(sum(x['raw_unknown']for x in r['queries']),5)

    def test_oral_population_keeps_short_unknown_nontarget_and_masked_DNA(self):
        import numpy as np
        data=dict(lengths=np.array([1000,800,499]),eligible=np.array([True,True,False]));part=dict(ids=['a','b','c'],assignment=[0,0,-1],neighbors=[[],[],[]])
        r=oral_population(part,data,np.array([0,1,-1]),np.array([3,0,1]),np.array([True,False,False]),['target','non-target'],{'target':2000},{'a'})
        self.assertEqual(r['all_bp'],2299);cells=r['population_cells'];self.assertEqual(sum(v['non_ACGT_quarantine_bp']for v in cells.values()),4)
        self.assertTrue(any('unknown' in k and v['bp']==499 for k,v in cells.items()))
        self.assertTrue(any('non_target_source' in k and v['bp']==800 for k,v in cells.items()))
        self.assertEqual(r['bins'][0]['supported_purity'],997/1800)

    def marker_fixture(self,root,malformed=False):
        """Use real JSON readers and marker reducer; no gene caller/search is substituted."""
        import numpy as np
        from dl_binner.candidate.markers import POLICY,runtime,reduce_hits
        from dl_binner.io import id_digest
        cache=root/'cache';cache.mkdir();features=root/'features.npz';np.savez(features,ids=np.array(['q']),lengths=np.array([1000]))
        genes={'g0':dict(contig='q',start=0,end=300,strand=1,protein_length=100,partial_begin=False,partial_end=False),
               'g1':dict(contig='q',start=500,end=800,strand=1,protein_length=100,partial_begin=True,partial_end=False)}
        domains=[dict(gene='g0',marker='m',hmm_from=1,hmm_to=90,hmm_length=100,protein_from=1,protein_to=90,score=20.)]
        families={'m':'F'};evidence=dict(ids=['q'],ids_sha256=id_digest(['q']),**reduce_hits(genes,domains,families))
        if malformed:genes['g1']['end']=799
        (cache/'genes.jsonl').write_text(''.join(json.dumps(dict(gene=k,**g))+'\n'for k,g in genes.items()))
        for n,v in [('domains.json',domains),('evidence.json',evidence),('asset.json',dict(families=families))]:(cache/n).write_text(json.dumps(v))
        receipt=dict(policy=POLICY,runtime=runtime(),genes=2,domains=1,files={p.name:binding(p)for p in cache.iterdir()})
        (cache/'cache.json').write_text(json.dumps(receipt));inventory=root/'original.json';inventory.write_text(json.dumps(dict(all_result_members={'shared/oral-markers/'+k:v for k,v in receipt['files'].items()})))
        return cache,features,inventory

    def test_actual_marker_reduction_and_nonhit_gene_refusal(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);cache,features,inventory=self.marker_fixture(root);r=marker_review(cache,features,inventory,root/'review.json')
            self.assertEqual(r['genes'],2);self.assertEqual(r['hit_genes'],1);self.assertEqual(r['clean'],['q'])
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);cache,features,inventory=self.marker_fixture(root,True)
            with self.assertRaisesRegex(ValueError,'Malformed cached gene row'):marker_review(cache,features,inventory,root/'refused.json')


if __name__=='__main__':unittest.main()
