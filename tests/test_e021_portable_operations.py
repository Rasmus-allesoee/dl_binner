"""Portable E021 operational contracts; no model, cloud mutation or native claims."""
import importlib.util,tempfile,unittest
from pathlib import Path
P=Path(__file__).absolute().parents[1]
spec=importlib.util.spec_from_file_location('inventory',P/'scripts/e021_portable_inventory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class PortableOperations(unittest.TestCase):
    def test_inventory_unit_is_short_and_cannot_outlive_provider_boundary(self):
        text=m.unit_text(Path('/srv/payload/scripts/e021_portable_inventory.py'),Path('/srv/run'),'researcher',1200)
        for key in ['RuntimeMaxSec=1200','MemoryMax=8000000000','CPUAffinity=0 1 2 3',' hold --root ']:self.assertIn(key,text)
        for n in [0,1501]:
            with self.assertRaises(ValueError):m.unit_text('/srv/code','/srv/run','u',n)
    def test_receipt_exclusive_and_finite(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'receipt.json';m.write(p,dict(status='PASS'))
            with self.assertRaises(FileExistsError):m.write(p,{})
            with self.assertRaises(ValueError):m.write(Path(d)/'bad.json',dict(value=float('nan')))

class TransportContracts(unittest.TestCase):
    def module(self):
        s=importlib.util.spec_from_file_location('transport',P/'scripts/e021_portable_transport.py');q=importlib.util.module_from_spec(s);s.loader.exec_module(q);return q
    def test_real_tar_pipe_roundtrip_pairing_and_existing_refusal(self):
        import io,json
        t=self.module()
        with tempfile.TemporaryDirectory()as d:
            r=Path(d);f=r/'opaque.dat';f.write_bytes(bytes(range(251))*317);manifest=dict(kind='E021 verified transport v1',files={'bank/vectors.npy':dict(source=str(f),**t.binding(f))})
            stream=io.BytesIO();sent=t.send(manifest,stream,1024**2);received=t.receive(manifest,io.BytesIO(stream.getvalue()),r/'fresh',1024**2)
            self.assertEqual(t.paired(sent,received,t.binding_bytes(stream.getvalue()))['status'],'PAIRED_STREAM_AND_MEMBERS_PASS')
            self.assertEqual((r/'fresh/bank/vectors.npy').read_bytes(),f.read_bytes())
            with self.assertRaises(FileExistsError):t.receive(manifest,io.BytesIO(stream.getvalue()),r/'fresh',1024**2)
            with self.assertRaisesRegex(ValueError,'digests differ'):t.paired(sent,received,dict(bytes=0,sha256='0'*64))
    def test_malformed_bound_members_and_truncation_refuse_without_fallback(self):
        import io
        t=self.module()
        with tempfile.TemporaryDirectory()as d:
            r=Path(d);f=r/'a';f.write_bytes(b'actual retained bytes');v=dict(source=str(f),**t.binding(f))
            for name in ['../outside','/absolute','a/../b','a\\b','inventory.json']:
                with self.assertRaises(ValueError):t.names(dict(kind='E021 verified transport v1',files={name:v}))
            manifest=dict(kind='E021 verified transport v1',files={'a':v});stream=io.BytesIO();t.send(manifest,stream,1024**2)
            with self.assertRaises((ValueError,EOFError,__import__('tarfile').ReadError)):
                t.receive(manifest,io.BytesIO(stream.getvalue()[:1024]),r/'truncated',1024**2)
            self.assertTrue((r/'truncated.incoming').exists());self.assertFalse((r/'truncated').exists())
            with self.assertRaisesRegex(ValueError,'cap exceeded'):t.send(manifest,io.BytesIO(),100)

class WorkerCommands(unittest.TestCase):
    def test_exact_new_worker_shapes_source_security_and_no_IAM(self):
        s=importlib.util.spec_from_file_location('cloud',P/'scripts/e021_portable_cloud.py');m2=importlib.util.module_from_spec(s);s.loader.exec_module(m2)
        base=dict(networkInterfaces=[dict(subnetwork='existing-subnet')],serviceAccounts=[dict(email='existing-SA',scopes=['existing-scope'])])
        for placement in m2.PLACEMENTS:
            commands=m2.worker_commands('e021-test',placement,base,'verified-image');text=__import__('json').dumps(commands)
            for required in ['40GB','64GB','137700s','--shielded-secure-boot','existing-SA','existing-scope','existing-subnet']:self.assertIn(required,text)
            for forbidden in ['set-iam','services','roles/','spot','vws','format','delete']:self.assertNotIn(forbidden,text.replace('auto-delete=no',''))
            self.assertEqual('--accelerator=count=1,type=nvidia-tesla-t4'in commands[-1],placement[2]=='T4')
        with self.assertRaises(ValueError):m2.worker_commands('e021-test',('us-central1-a','n1-standard-8','T4','pd-standard'),base,'x')

class TransferredCLI(unittest.TestCase):
    def test_exact_isolated_sender_and_receiver_outside_checkout(self):
        import hashlib,json,shutil,subprocess,sys
        with tempfile.TemporaryDirectory()as d:
            r=Path(d);script=r/'e021_portable_transport.py';shutil.copyfile(P/'scripts/e021_portable_transport.py',script)
            f=r/'a';f.write_bytes(b'retained\x00DNA'*31);b=f.read_bytes();manifest=dict(kind='E021 verified transport v1',files={'bank/opaque.bin':dict(source=str(f),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())});mp=r/'manifest.json';mp.write_text(json.dumps(manifest));archive=r/'stream.tar'
            with archive.open('wb')as out:subprocess.run([sys.executable,'-I','-B',str(script),'send','--manifest',str(mp),'--receipt',str(r/'sent.json'),'--cap','1048576'],cwd=r,check=True,stdout=out)
            with archive.open('rb')as inp:subprocess.run([sys.executable,'-I','-B',str(script),'receive','--manifest',str(mp),'--receipt',str(r/'received.json'),'--destination',str(r/'fresh'),'--cap','1048576'],cwd=r,check=True,stdin=inp)
            sent=json.loads((r/'sent.json').read_text());recv=json.loads((r/'received.json').read_text());self.assertEqual(sent['stream'],recv['stream']);self.assertEqual((r/'fresh/bank/opaque.bin').read_bytes(),b)

if __name__=='__main__':unittest.main()

class PortableNativeContracts(unittest.TestCase):
    def load(self,name):
        import sys
        sys.path.insert(0,str(P/'scripts'))
        s=importlib.util.spec_from_file_location(name,P/'scripts'/(name+'.py'));q=importlib.util.module_from_spec(s);s.loader.exec_module(q);return q
    def test_portable_actual_service_clock_threads_and_memory(self):
        m=self.load('e021_portable_arm');s=m.service_content('/repo','/work','user','/work/config.json',7100)
        for x in ['RuntimeMaxSec=7100','e021_portable_node.py --config','MemoryMax=26000000000','CPUAffinity=0 1 2 3','KillMode=control-group']:self.assertIn(x,s)
        with self.assertRaises(ValueError):m.service_content('/repo','/work','bad user','/c',60)
        with self.assertRaises(ValueError):m.service_content('/repo','/work','u','/c',172801)
    def test_real_runtime_stream_hash_reuse_and_corruption_refusal(self):
        import hashlib
        m=self.load('e021_portable_runtime')
        with tempfile.TemporaryDirectory()as d:
            r=Path(d);f=r/'publisher';f.write_bytes(b'actual pinned software fixture'*113);b=f.read_bytes();row=dict(url=f.as_uri(),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));out=r/'fresh'
            self.assertEqual(m.acquire(row,out)['sha256'],row['sha256']);self.assertEqual(m.acquire(row,out)['bytes'],len(b));out.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'Corrupt retained'):m.acquire(row,out)
            with self.assertRaisesRegex(ValueError,'bytes differ'):m.acquire(dict(row,sha256='0'*64),r/'bad')
    def test_actual_peer_and_aggregate_space_refusal(self):
        m=self.load('e021_portable_node');local=dict(growth_bytes=9*1024**3,work_free_bytes=30*1024**3,boot_free_bytes=5*1024**3)
        m.peer_check({},local,dict(live=False,epoch=0,growth_bytes=10*1024**3),1000)
        with self.assertRaisesRegex(TimeoutError,'stale'):m.peer_check({},local,dict(live=True,epoch=0,growth_bytes=0),1000)
        with self.assertRaisesRegex(MemoryError,'Aggregate'):m.peer_check({},local,dict(live=False,epoch=0,growth_bytes=24*1024**3),1000)
    def test_completion_refuses_unproven_controller_boolean(self):
        m=self.load('e021_portable_node')
        with self.assertRaisesRegex(ValueError,'incomplete'):m.completed(dict(role='gpu',root='/never-read'),dict(stages=[]))

class RuntimeMetadataContract(unittest.TestCase):
    def test_actual_zip_vendor_metadata_is_not_the_distributions_identity(self):
        import io,sys,zipfile
        sys.path.insert(0,str(P/'scripts'));from e021_portable_runtime import metadata_member
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w')as z:
            z.writestr('setuptools-78.1.1.dist-info/METADATA','Name: setuptools\nVersion: 78.1.1\n');z.writestr('setuptools/_vendor/packaging-24.2.dist-info/METADATA','Name: packaging\nVersion: 24.2\n')
        with zipfile.ZipFile(io.BytesIO(b.getvalue()))as z:self.assertEqual(metadata_member(z.namelist()),'setuptools-78.1.1.dist-info/METADATA')
        with self.assertRaises(ValueError):metadata_member(['a.dist-info/METADATA','b.dist-info/METADATA'])

class StrictTransportGuard(unittest.TestCase):
    def test_actual_receiver_checks_budget_before_writing_file_content(self):
        import io,json,sys
        sys.path.insert(0,str(P/'scripts'));from e021_portable_transport import send,receive,binding
        with tempfile.TemporaryDirectory()as d:
            r=Path(d);p=r/'a';p.write_bytes(b'actual tiny byte stream');m=dict(kind='E021 verified transport v1',files={'a':dict(source=str(p),**binding(p))});b=io.BytesIO();send(m,b,1048576)
            def refuse(n):raise MemoryError('intended before-write reserve failure')
            with self.assertRaisesRegex(MemoryError,'intended before-write'):receive(m,io.BytesIO(b.getvalue()),r/'destination',1048576,refuse)
            self.assertEqual((r/'destination.incoming/a').stat().st_size,0);self.assertFalse((r/'destination').exists())

class CompleteInputManifest(unittest.TestCase):
    def test_native_reader_sidecars_are_explicit_original_members(self):
        import sys
        sys.path.insert(0,str(P/'scripts'))
        from e021_portable_inputs import compile_manifest
        units={u:dict(fasta='/original/'+u+'/assembly.fna',
            features='/original/'+u+'/features.npz',views='/original/'+u+'/views.npz',
            tokens='/original/'+u+'/tokens')for u in ['E009-hybrid','oral-hybrid']}
        files={}
        for u,v in units.items():
            for path in [v['fasta'],v['features'],v['views'],
                    v['features'].replace('.npz','.json'),v['views'].replace('.npz','.json'),
                    v['tokens']+'/tokens.json']:
                files[path]=dict(bytes=23,sha256='a'*64)
        out=compile_manifest(units,files)
        self.assertEqual(len(out['files']),12)
        self.assertEqual(sum(k.endswith('.json')for k in out['files']),6)
        del files[units['oral-hybrid']['views'].replace('.npz','.json')]
        with self.assertRaisesRegex(ValueError,'original input binding'):
            compile_manifest(units,files)

class RuntimeArchivePreservation(unittest.TestCase):
    def test_actual_bytes_internal_alias_and_no_overwrite(self):
        import sys
        sys.path.insert(0,str(P/'scripts'))
        from e021_portable_runtime_archive import pack,verify,inventory
        with tempfile.TemporaryDirectory()as d:
            r=Path(d);prefix=r/'prefix';prefix.mkdir();(prefix/'python').write_bytes(b'owned runtime bytes'*170)
            (prefix/'alias').symlink_to('python')
            __import__('os').link(prefix/'python',prefix/'second-regular')
            result=pack(prefix,r/'preserved')
            self.assertTrue(verify(r/'preserved/native-runtime.tar.gz',result['members']))
            self.assertFalse(result['destination_execution_admitted'])
            with self.assertRaises(FileExistsError):pack(prefix,r/'preserved')
            (prefix/'outside').symlink_to(r)
            with self.assertRaisesRegex(ValueError,'escapes'):inventory(prefix)

class ScopedHandoffContracts(unittest.TestCase):
    def load(self,name):
        import sys
        sys.path.insert(0,str(P/'scripts'))
        return __import__(name)
    def test_exact_subprocess_JSON_roundtrip_and_overwrite_refusal(self):
        m=self.load('e021_portable_E009_controller')
        with tempfile.TemporaryDirectory()as d:
            r=Path(d);node=dict(ssh=['/bin/sh','-c'],root=str(r))
            value=dict(opaque='quote \' and actual\nnewline',axes=[0,2,17])
            m.put(r,node,str(r/'actual.json'),value)
            self.assertEqual(m.read(r,node,str(r/'actual.json')),value)
            with self.assertRaises(RuntimeError):m.put(r,node,str(r/'actual.json'),{})
    def test_original_credit_and_common_clock_lease_cannot_expand(self):
        m=self.load('e021_portable_E009_controller')
        v=dict(gross_upper_USD=39.11,real_money=False,available_USD_after_pending_reserve=248,
            credit_expiry_epoch=30000,scope='SAME_PREAPPROVED_E009_PHASE_ONLY')
        clock=dict(provider_deadline_epoch=20000,deadline_epoch=19000)
        m.validate_lease(v,clock,1000)
        for bad in [dict(v,gross_upper_USD=46),dict(v,real_money=True),
                dict(v,available_USD_after_pending_reserve=44),dict(v,credit_expiry_epoch=19000)]:
            with self.assertRaises(ValueError):m.validate_lease(bad,clock,1000)
    def test_native_wait_closes_without_claiming_two_community_success(self):
        import json,time
        m=self.load('e021_portable_handoff')
        with tempfile.TemporaryDirectory()as d:
            r=Path(d);(r/'config.json').write_text(json.dumps(dict(node_deadline_epoch=time.time()+7200)))
            m.wait_handoff(r,0)
            v=json.loads((r/'finish.json').read_text())
            self.assertFalse(v['science_completed']);self.assertFalse(v['oral_executed'])
            self.assertEqual(v['status'],'SUCCESS_E009_EXTRACTION_RETAINED_HANDOFF_PENDING')
    def test_scoped_completion_requires_all_six_actual_exits(self):
        import json
        m=self.load('e021_portable_handoff')
        with tempfile.TemporaryDirectory()as d:
            r=Path(d);(r/'tasks').mkdir();(r/'gates').mkdir();u=r/'work/units/E009-hybrid'
            for n in ['train','export']:(u/n).mkdir(parents=True)
            (u/'train/checkpoint.json').write_text(json.dumps(dict(history=[{}]*20)))
            (u/'train/reference.npz').write_bytes(b'exact reload fixture')
            (u/'embeddings.npz').write_bytes(b'exact reload fixture')
            (u/'export/accounting.json').write_text(json.dumps({n:{}for n in ['pre','old','post']}))
            (u/'graph-proof.json').write_text(json.dumps(dict(status='PASS')))
            p=r/'plan.json';p.write_text(json.dumps(dict(work=str(r/'work'))))
            for i,s in enumerate(['train','embed','group','refine','export','graph-proof']):
                (r/'tasks'/(str(i)+'.result.json')).write_text(json.dumps(dict(kind='science',unit='E009-hybrid',stage=s,status='SUCCESS')))
            m.cpu_target(r,p)
            self.assertFalse(json.loads((r/'finish.json').read_text())['science_completed'])
            (r/'finish.json').unlink();(r/'gates/E009-scoped-target.json').unlink()
            (r/'tasks/extra.result.json').write_text(json.dumps(dict(kind='science',unit='oral-hybrid',stage='train',status='SUCCESS')))
            with self.assertRaisesRegex(ValueError,'Six E009'):m.cpu_target(r,p)
