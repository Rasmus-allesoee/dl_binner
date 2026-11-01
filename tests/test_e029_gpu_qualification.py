"""Real inert-runtime/compact-return contracts; transport alone is mocked."""
import io,json,sys,tarfile,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding
from e029_gpu_launch import commands,render_bootstrap,render_release,unused_owned_disks
from e029_gpu_node import unpack_runtime,collect
from e029_gpu_arm import service_content


class Qualification(unittest.TestCase):
    def test_actual_bootstrap_release_and_held_service_compile(self):
        i=dict(name='e029-batching-fixture-b',state=dict(disks=[{},dict(deviceName='persistent-disk-1')]),source='a'*40,start_epoch=1,node_deadline_epoch=5401,provider_deadline_epoch=6301,source_asset={},assets={},archive_prefix='gs://dl-binner-archive-167650584170/e029/fixture',GPU='L4')
        for code in [render_bootstrap(i,{}),render_release(i,dict(root='/fresh',repo='/repo'),{})]:compile(code,'actual-qualification-consumer','exec')
        service=service_content('/repo','/phase','own-user','/config',5400)
        self.assertIn('e029_gpu_node.py',service);self.assertIn('RefuseManualStop=yes',service);self.assertIn('MemoryMax=26000000000',service)
        baseline=dict(serviceAccounts=[dict(email='same-service',scopes=['same-scope'])],networkInterfaces=[dict(subnetwork='same-subnet')])
        args=commands(i['name'],'us-central1-b',baseline,'frozen-image')
        self.assertEqual(len(args),3);self.assertIn('--max-run-duration=6300s',args[-1]);self.assertNotIn('--no-shielded-secure-boot',args[-1])

    def test_exact_capacity_cleanup_uses_real_inventory_fields(self):
        name='e029-batching-fixture-b';zone='us-central1-b'
        rows=[dict(name=name+'-boot',zone='/zones/'+zone,sizeGb='40',labels={'experiment':'e029'}),dict(name=name+'-work',zone='/zones/'+zone,sizeGb='64',labels={'experiment':'e029'}),dict(name='dl-binner-cpu-work',zone='/zones/'+zone,sizeGb='300',users=['accepted'])]
        self.assertEqual([x['name']for x in unused_owned_disks(rows,name,zone)],[name+'-boot',name+'-work'])
        with self.assertRaises(ValueError):unused_owned_disks([dict(rows[0],users=['live-instance'])],name,zone)
        self.assertFalse(unused_owned_disks(rows,name,'us-central1-c'))
        self.assertIn('--machine-type=g2-standard-8',commands('e029-batching-fixture-a','us-central1-a',dict(serviceAccounts=[dict(email='same',scopes=[])],networkInterfaces=[dict(subnetwork='same')]),'same-image')[-1])

    def test_real_archive_runtime_bytes_internal_alias_and_escape_refusal(self):
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);archive=root/'runtime.tar.gz';prefix=root/'restored';data=b'own inert engineering bytes'
            import hashlib
            members={'lib/payload':dict(kind='file',bytes=len(data),sha256=hashlib.sha256(data).hexdigest()),'lib/alias':dict(kind='symlink',target='payload')}
            with tarfile.open(archive,'w:gz')as a:
                x=tarfile.TarInfo('lib/payload');x.size=len(data);x.mode=0o644;a.addfile(x,io.BytesIO(data))
                x=tarfile.TarInfo('lib/alias');x.type=tarfile.SYMTYPE;x.linkname='payload';a.addfile(x)
            manifest=root/'manifest.json';manifest.write_text(json.dumps(dict(source_prefix=str(prefix),archive=binding(archive),members=members,logical_regular_bytes=len(data))))
            result=unpack_runtime(archive,manifest,engineering=True)
            self.assertEqual(result['members'],2);self.assertEqual((prefix/'lib/alias').read_bytes(),data)
            with self.assertRaises(ValueError):unpack_runtime(archive,manifest,engineering=True)
            escaped=root/'escaped';bad=root/'bad.tar.gz';bad_members={'lib/alias':dict(kind='symlink',target='../../outside')}
            with tarfile.open(bad,'w:gz')as a:
                x=tarfile.TarInfo('lib/alias');x.type=tarfile.SYMTYPE;x.linkname='../../outside';a.addfile(x)
            bad_manifest=root/'bad.json';bad_manifest.write_text(json.dumps(dict(source_prefix=str(escaped),archive=binding(bad),members=bad_members,logical_regular_bytes=0)))
            with self.assertRaisesRegex(ValueError,'escapes'):unpack_runtime(bad,bad_manifest,engineering=True)
            self.assertFalse((root/'outside').exists())
            archive.write_bytes(b'corrupt')
            with self.assertRaises(ValueError):unpack_runtime(archive,manifest,engineering=True)

    def test_real_compact_collection_members_with_mock_transport(self):
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);(root/'logs').mkdir();(root/'logs/own.log').write_text('closed native fixture log\n');(root/'config.json').write_text('{}')
            with patch('e029_gpu_node.storage_upload',lambda p,u:dict(uri=u,binding=binding(p),readback_verified=True,mocked_transport=True)):
                result=collect(root,dict(archive_prefix='gs://dl-binner-archive-167650584170/e029/fixture'),{})
            self.assertTrue(result['every_member_verified']);self.assertEqual(result['regular_members'],3)
            with tarfile.open(root/'e029-gpu-evidence.tar.gz')as a:
                inv=json.load(a.extractfile('inventory.json'));self.assertEqual(set(inv['members']),{'logs/own.log','config.json'})


if __name__=='__main__':unittest.main()
