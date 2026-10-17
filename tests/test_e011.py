"""Real tiny cached graph/export and refusal contracts; no community partitions."""
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e011_cached import restore,verify_restored,cached_graph,cpm_partition,external_export
from e009_common import binding,write_json


class CachedControlTests(unittest.TestCase):
    def test_retained_native_installation_reuse_refuses_inventory_or_binary_drift(self):
        from e011_metabat import verify_install
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory);(p/'bin').mkdir();(p/'conda-meta').mkdir();binary=p/'bin/metabat2';binary.write_bytes(b'bound native executable')
            item=dict(name='metabat2',version='2.18',build='fixed');(p/'conda-meta/metabat2.json').write_text(json.dumps(item))
            receipt=p/'installed.json';receipt.write_text(json.dumps(dict(binary=binding(binary),inventory={'metabat2':dict(version='2.18',build='fixed')})))
            expected=binding(receipt);self.assertTrue(verify_install(p,receipt,expected)['installation_reused'])
            binary.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'changed'):verify_install(p,receipt,expected)
            binary.write_bytes(b'bound native executable');(p/'conda-meta/extra.json').write_text(json.dumps(dict(name='extra',version='1',build='bad')))
            with self.assertRaisesRegex(ValueError,'changed'):verify_install(p,receipt,expected)

    def test_runtime_library_aliases_bind_target_bytes_without_relaxing_artifact_links(self):
        import hashlib
        from e011_metabat import runtime_member
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory);(p/'bin').mkdir();(p/'lib').mkdir()
            target=p/'lib/libz.so.1.3.2';target.write_bytes(b'real dependency bytes')
            alias=p/'lib/libz.so.1';alias.symlink_to(target.name)
            lexical=p/'bin/../lib/libz.so.1';before=runtime_member(lexical)
            self.assertTrue(before['direct_symlink']);self.assertEqual(before['resolved_path'],str(target.resolve()))
            self.assertEqual(before['link_target'],target.name)
            self.assertEqual(before['content']['sha256'],hashlib.sha256(target.read_bytes()).hexdigest())
            with self.assertRaisesRegex(ValueError,'linked'):binding(alias)
            target.write_bytes(b'changed actual dependency');self.assertNotEqual(before,runtime_member(lexical))
            (p/'broken').symlink_to('missing')
            with self.assertRaisesRegex(ValueError,'Unresolvable'):runtime_member(p/'broken')
            (p/'cycle-a').symlink_to('cycle-b');(p/'cycle-b').symlink_to('cycle-a')
            with self.assertRaisesRegex(ValueError,'Unresolvable'):runtime_member(p/'cycle-a')
            with self.assertRaisesRegex(ValueError,'regular'):runtime_member(p/'lib')

    def test_snapshot_upload_failure_cannot_prevent_shutdown(self):
        from e011_exit_watchdog import finish
        calls=[]
        def fail(*args):raise RuntimeError('inert transport failure')
        finish('inert','gs://private/inert',lambda:calls.append('stop'),upload=fail)
        self.assertEqual(calls,['stop'])
        finish('inert','gs://private/inert',lambda:calls.append('stop'),upload=lambda *_:calls.append('upload'))
        self.assertEqual(calls,['stop','upload','stop'])

    def test_fresh_budget_credit_retention_watchdog_and_original_clock_gates(self):
        from e011_phase import verify_admission
        now=time.time();cfg={'vm_start_epoch':now-10}
        release=dict(credit_gate_passed=True,pending_usage_accounted=True,watchdog_release_verified=True,
            provider_stop_seconds=2700,incremental_gross_ceiling_usd=1,no_resource_change=True,
            storage_retention_extended=False,credit_valid_until_epoch=now+9000,
            storage_valid_until_epoch=now+9000,covered_costs=['compute','disk','storage','network','operations'])
        verify_admission(cfg,release,now)
        for key,value in [('watchdog_release_verified',False),('provider_stop_seconds',15300),
            ('incremental_gross_ceiling_usd',2),('credit_gate_passed',False),('covered_costs',['compute']),
            ('storage_valid_until_epoch',now+100)]:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):verify_admission(cfg,dict(release,**{key:value}),now)
        with self.assertRaises(TimeoutError):verify_admission(dict(vm_start_epoch=now-1800),release,now)

    def test_restore_verifies_all_members_and_refuses_corruption_links_and_reuse(self):
        import hashlib
        with tempfile.TemporaryDirectory()as folder:
            p=Path(folder);payload={'candidate/group/file':b'retained','unused':b'also verified'}
            records={k:dict(bytes=len(v),sha256=hashlib.sha256(v).hexdigest())for k,v in payload.items()}
            payload['collection-inventory.json']=json.dumps(dict(files=records)).encode()
            def seal(path,link=False):
                with tarfile.open(path,'w:gz')as t:
                    for name,data in payload.items():
                        m=tarfile.TarInfo(name);m.size=len(data);t.addfile(m,io.BytesIO(data))
                    if link:
                        m=tarfile.TarInfo('unsafe');m.type=tarfile.SYMTYPE;m.linkname='/tmp/escape';t.addfile(m)
            archive=p/'fixture.tar.gz';seal(archive)
            result=restore(archive,p/'restored',binding(archive))
            self.assertEqual(result['verified_members'],3)
            self.assertFalse((p/'restored/unused').exists())
            self.assertEqual((p/'restored/candidate/group/file').read_bytes(),b'retained')
            self.assertFalse(verify_restored(p/'restored',binding(p/'restored/restore.json'),binding(archive))['original_recopied'])
            (p/'restored/candidate/group/file').write_bytes(b'corrupt retained bytes')
            with self.assertRaisesRegex(ValueError,'bytes differ'):
                verify_restored(p/'restored',binding(p/'restored/restore.json'),binding(archive))
            with self.assertRaisesRegex(ValueError,'fresh'):restore(archive,p/'restored',binding(archive))
            with self.assertRaisesRegex(ValueError,'archive bytes'):restore(archive,p/'bad',{'bytes':1,'sha256':'bad'})
            payload['unused']=b'changed unselected member';other=p/'corrupt.tar.gz';seal(other)
            with self.assertRaisesRegex(ValueError,'checksum'):restore(other,p/'corrupt',binding(other))
            payload['unused']=b'also verified';linked=p/'link.tar.gz';seal(linked,True)
            with self.assertRaisesRegex(ValueError,'Unsafe'):restore(linked,p/'linked',binding(linked))

    def test_real_native_graph_objective_mapping_refinement_and_complete_export(self):
        import numpy as np
        from dl_binner.candidate.views import prepare,config,load
        from dl_binner.candidate.grouping import group,refine_partition
        from dl_binner.io import save_arrays,load_arrays,digest
        from dl_binner.clustering import export
        from dl_binner.accounting import summarize_arm
        from e010_review import refinement_membership
        with tempfile.TemporaryDirectory()as folder:
            p=Path(folder);fasta=p/'dna.fa';depth=p/'depth.tsv'
            ids=['z','a','y','b','x','c','w','d','v','e','u','f','short']
            fasta.write_text(''.join('>'+q+'\n'+('ACGT'*800 if q!='short' else 'ACGT')+'\n'for q in ids))
            depth.write_text('contig_id\tZ\tA\n'+''.join(q+'\t5\t9\n'for q in ids))
            cfg=config();cfg.update(output=2,neighbors=5,min_bin_bp=1,exact_threshold=2048)
            features=p/'features';features.mkdir();prepare(fasta,depth,features,cfg)
            data,meta=load(features/'features.npz');x=np.zeros((len(ids),2),np.float32)
            for i in range(12):
                angle=(0 if i<6 else 1.2)+(i%6)*.01;x[i]=[np.cos(angle),np.sin(angle)]
            emb=p/'embeddings.npz';save_arrays(emb,dict(ids=data['ids'],features=x,evidence=data['eligible']),
                dict(kind='embeddings',features_sha256=digest(features/'features.npz'),metric='unit cosine'))
            old=p/'old';old.mkdir();group(emb,features/'features.npz',old,cfg,1)
            graph,_=load_arrays(old/'graph.npz','candidate_sparse_graph');vectors,_=load_arrays(emb,'embeddings')
            pre=json.loads((old/'partition.json').read_text())
            selected,edges=cached_graph(graph,ids,data['eligible'])
            self.assertEqual([ids[i]for i in selected],sorted(ids[:-1]));self.assertTrue(np.all(edges[:,0]<edges[:,1]))
            result=cpm_partition(data,vectors,graph,pre,cfg,features/'features.npz',old/'graph.npz')
            gamma=float(np.median(graph['weights']))/5;self.assertEqual(result['objective']['gamma'],gamma)
            labels=np.array(result['assignment']);counts=np.bincount(labels[labels>=0])
            internal=labels[graph['edges'][:,0]]==labels[graph['edges'][:,1]]
            oracle=2*(graph['weights'][internal].sum()-gamma*sum(n*(n-1)/2 for n in counts))
            self.assertAlmostEqual(oracle,result['objective']['native_quality'])
            self.assertEqual(result['clusters'],2);self.assertEqual(result['assignment'][-1],-1)
            after=refine_partition(result,data,x,{},cfg);refinement_membership(result,after)
            for name,part in [('pre',result),('post',after)]:
                write_json(p/(name+'.json'),part);export(features/'features.npz',p/(name+'.json'),fasta,p/name)
                accounting,_=summarize_arm(features/'features.npz',p/name)
                self.assertEqual(accounting['contigs'],13);self.assertEqual(accounting['bp'],38404)

    def test_unequal_marker_counts_preserve_actual_second_count_policy(self):
        import numpy as np
        from dl_binner.candidate.grouping import refine_partition
        from dl_binner.candidate.views import config
        ids=['a','b','c','d','e','f'];cfg=config();cfg.update(output=2,min_bin_bp=1)
        features=dict(ids=np.array(ids),lengths=np.full(6,5000))
        vectors=np.array([[1,0],[0,1],[1,0],[0,1],[1,0],[0,1]],np.float32)
        pre=dict(ids=ids,assignment=[0]*6,valid=[True]*6,reason=['']*6,neighbors=[[]for _ in ids],parent_features_sha256='fixture')
        clean={'a':['largest','second'],'b':['largest','second'],'c':['largest'],'d':['largest'],'e':['largest']}
        result=refine_partition(pre,features,vectors,clean,cfg)
        self.assertEqual(result['attempts'][0]['before'],{'largest':5,'second':2})
        self.assertEqual(result['attempts'][0]['k'],2)
        self.assertEqual(result['attempts'][0]['seed_family'],'second')
        self.assertEqual(result['attempts'][0]['seed_ids'],['a','b'])

    def test_external_export_keeps_native_eligibility_and_refuses_changed_DNA(self):
        with tempfile.TemporaryDirectory()as folder:
            p=Path(folder);fasta=p/'all.fa';native=p/'native';native.mkdir()
            rows={'big':'ACGT'*800,'recruited':'A'*1500,'unassigned':'G'*1200,'tiny':'T'*499}
            fasta.write_text(''.join('>'+q+'\n'+s+'\n'for q,s in rows.items()))
            (native/'bin.1.fa').write_text('>big\n'+rows['big']+'\n>recruited\n'+rows['recruited']+'\n')
            r=external_export(fasta,native,p/'complete')
            self.assertEqual(r['contigs'],4);self.assertEqual(r['bp'],6399)
            self.assertEqual(r['statuses']['assigned']['contigs'],2)
            self.assertEqual(r['statuses']['unassigned']['contigs'],1)
            self.assertEqual(r['statuses']['excluded']['contigs'],1)
            (native/'bin.2.fa').write_text('>big\n'+rows['big']+'\n')
            with self.assertRaisesRegex(ValueError,'duplicate'):external_export(fasta,native,p/'duplicate')
            (native/'bin.2.fa').write_text('>big\nAAAA\n')
            with self.assertRaisesRegex(ValueError,'changed'):external_export(fasta,native,p/'changed')

    def test_contrastive_positive_index_and_zero_depth_branch_in_separate_tensor_process(self):
        code='''import torch,numpy as np
from dl_binner.model import nt_xent
from dl_binner.candidate.model import Encoder
from dl_binner.candidate.views import config
x=torch.tensor([[1.,0.],[0.,1.]])
loss=nt_xent(x,x,.2)
expected=torch.log(torch.exp(torch.tensor(5.))+2)-5
assert torch.allclose(loss,expected)
cfg=config();model=Encoder(2,cfg)
c=torch.randn(3,136);mask=torch.zeros(3,dtype=torch.bool)
with torch.no_grad():
 a=model(c,torch.zeros(3,2),mask)[0];b=model(c,torch.ones(3,2)*50,mask)[0]
assert torch.equal(a,b) and torch.isfinite(a).all()
'''
        subprocess.run([sys.executable,'-I','-B','-c',code],check=True,timeout=30)


if __name__=='__main__':unittest.main()
