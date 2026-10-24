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
