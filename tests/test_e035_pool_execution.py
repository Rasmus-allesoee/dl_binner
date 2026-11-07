"""Actual audit producer/schema/atomic release and exact restore contracts.

Only temporary local files are used. Cloud and systemd are never invoked; real
native source transport/watcher tests are separately required before release.
"""
import copy
import hashlib
import io
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock
import dl_binner as _owned_product

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import e035_pool_launch as launch
import e035_pool_phase as phase
from e021_control_json import publish


class AuditExecution(unittest.TestCase):
    def fixture(self,root):
        """Build the actual host configuration with source/clock/credit fields."""
        # A fixed before-boundary test clock cannot admit real cloud work.
        now=1794013200.;packet=Path(root)/'source.bundle';packet.write_bytes(b'local transport fixture')
        wheel=Path(root)/'candidate.whl';wheel.write_bytes(b'local wheel fixture')
        ident=dict(source='a'*40,repo='/srv/dl_binner/repo',phase='pooled-fixture',root='/srv/dl_binner/experiments/e035/pooled-fixture',user='rasmus_allesoee_gmail_com',service_name='e035-pooled-fixture',setup_timer='e035-setup-fixture',archive_prefix='gs://dl-binner-archive-167650584170/e035/pooled-fixture/',vm_start_epoch=now)
        f=dict(real_money_authorized=False,coverage_status='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY',ceiling_USD=4,estimated_complete_gross_USD=3.99,
            credit_checked_epoch=now,checked_epoch=now,storage_valid_until_epoch=1794351600,credit_valid_until_epoch=1799712000,
            native_pysam_path='/retained/native/pysam.whl',wheel_path=str(wheel),wheel_binding=launch.binding(wheel),pysam_binding={'bytes':1,'sha256':'b'*64},
            source_transport=dict(kind='private_exact_Git_bundle',path=str(packet),bundle=launch.binding(packet),base='b'*40,source='a'*40))
        return now,ident,f

    def test_complete_actual_host_producer_and_held_schema(self):
        with tempfile.TemporaryDirectory()as folder:
            now,ident,f=self.fixture(folder);c=launch.config_value(ident,f)
            self.assertTrue(phase.validate_config(c,now))
            for code in [launch.render_host(ident,f),launch.render_release(ident,{}),launch.render_inventory(ident),launch.source_sync(ident,f['source_transport'])]:compile(code,'actual audit producer','exec')
            self.assertNotIn('scripts/e034_phase.py',launch.render_host(ident,f))
            self.assertIn('scripts/e035_pool_arm.py',launch.render_host(ident,f))
            self.assertEqual(c['limits']['seconds'],28800);self.assertEqual(c['limits']['provider_STOP_seconds'],29700)
            for key in list(c):
                missing=dict(c);missing.pop(key)
                with self.assertRaises((KeyError,ValueError)):phase.validate_config(missing,now)

    def test_clock_stale_credit_resource_and_generation_refusal(self):
        with tempfile.TemporaryDirectory()as folder:
            now,ident,f=self.fixture(folder);c=launch.config_value(ident,f)
            for kind in ['clock','credit','resource','source']:
                bad=copy.deepcopy(c)
                if kind=='clock':bad['provider_deadline_epoch']+=1000
                elif kind=='credit':bad['financial']['credit_checked_epoch']-=7201
                elif kind=='resource':bad['limits']['RSS_bytes']+=1
                else:bad['operations_source']='c'*40
                with self.assertRaises(ValueError):phase.validate_config(bad,now)
            p=json.loads((ROOT/'experiments/E035-confidence-taxonomy/pooled-audit-plan.json').read_text())
            p['work']='/new/task/support';p['BAMs']['oral'][0]['local']='/new/source.bam'
            self.assertTrue(phase.validate_plan(p))
            p['BAMs']['oral'][0]['sha256']='0'*64
            with self.assertRaisesRegex(ValueError,'generation'):phase.validate_plan(p)

    def test_atomic_release_published_once_survives_controller_exit(self):
        with tempfile.TemporaryDirectory()as folder:
            path=Path(folder)/'release.json';value=dict(plan={'sha256':'a'*64,'bytes':3},watchdog_verified=True,provider_STOP_verified=True)
            publish(value,path)
            self.assertEqual(json.loads(path.read_text()),value)
            with self.assertRaises((FileExistsError,ValueError)):publish({'changed':True},path)
            self.assertEqual(json.loads(path.read_text()),value)
            bad=Path(folder)/'malformed-ready.json';bad.write_text('{')
            with self.assertRaises(json.JSONDecodeError):json.loads(bad.read_text())

    def test_complete_remainder_uses_both_readers_not_utility(self):
        samples={c:dict(status='PASS',wall_seconds=500.,observations=5000,utility='insufficient')for c in ['E009','oral']}
        result=phase.schedule(samples,20000)
        self.assertFalse(result['utility_used']);self.assertEqual(result['forecast_seconds'],15300)
        with self.assertRaises(ValueError):phase.schedule(samples,15000)
        samples['oral']['observations']=5_000_000
        with self.assertRaises(ValueError):phase.schedule(samples,20000)

    def test_actual_compact_collection_retains_logs_and_all_ledger_bytes(self):
        """Exercise real pack/alias/readback with mocked private object upload."""
        from e035_collect import verify,restore
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);task=root/'task';support=task/'support';support.mkdir(parents=True)
            (root/'logs').mkdir();(root/'gates').mkdir()
            for name in ['config.json','science-plan.json','host.json','release.json','started.json']:(root/name).write_text('{}\n')
            repo=root/'repo';repo.mkdir();experiment=repo/'experiments/E035-confidence-taxonomy';experiment.mkdir(parents=True)
            for label,name in [('source-lock.json','one.py'),('pooled-native-launch-lock.json','two.py')]:
                (repo/name).write_text('fixture source\n');(experiment/label).write_text(json.dumps(dict(files={name:launch.binding(repo/name)})))
            transports=root/'experiments/e035/source-transports';transports.mkdir(parents=True);packet=transports/('source-'+'a'*40+'.bundle');packet.write_bytes(b'exact fixture packet')
            (root/'config.json').write_text(json.dumps(dict(repo=str(repo),source_commit='a'*40,financial=dict(source_transport=dict(bundle=launch.binding(packet))))))
            (root/'logs/worker.stderr').write_text('real fixture worker error retained\n')
            sample=support/'E009/sample-00';sample.mkdir(parents=True);(sample/'ledger.npz').write_bytes(b'fixture retained bytes')
            os.link(sample/'ledger.npz',sample/'same-byte-alias')
            (sample/'coordinates.bin').write_bytes(b'failed raw compact coordinates')
            (sample/'collate.0000.bam').write_bytes(b'regenerable input-order temporary')
            restores=task/'restores/oral/00';restores.mkdir(parents=True);(restores/'source-restore.json').write_text('{}\n');(restores/'source.part').write_bytes(b'preserved partial source')
            c=dict(root=str(root),task_filesystem=str(task),plan=str(root/'science-plan.json'),archive_prefix='gs://fixture/',limits=dict(compressed_export_bytes=2*1024**3))
            result={};uploads=[]
            def upload(path,uri):
                uploads.append(uri);return dict(uri=uri,binding=launch.binding(path),readback_verified=True)
            with mock.patch.object(phase,'storage_upload',side_effect=upload):phase.collect(c,result)
            proof=verify(task/'return');staged=restore(task/'return',root/'restored')
            self.assertTrue(result['collection_readback_verified']);self.assertGreater(proof['members'],3)
            self.assertEqual((staged/'work/E009/sample-00/coordinates.bin').read_bytes(),b'failed raw compact coordinates')
            self.assertFalse((staged/'work/E009/sample-00/collate.0000.bam').exists());self.assertTrue((sample/'collate.0000.bam').is_file())
            self.assertEqual((staged/'evidence/logs/worker.stderr').read_text(),'real fixture worker error retained\n')
            self.assertEqual((staged/'evidence/source.bundle').read_bytes(),b'exact fixture packet')
            self.assertEqual((staged/'evidence/source-repository/two.py').read_text(),'fixture source\n')
            self.assertTrue(uploads);self.assertTrue((restores/'source.part').exists())


class ExactRestoration(unittest.TestCase):
    def test_actual_stream_SHA_and_local_CRC_with_mocked_cloud_transport(self):
        """Exercise the accepted restorer and real SDK CRC, without cloud requests.

        HTTP/token/space are fixtures; SHA256, publication, local compiled CRC32C
        and verified-reuse/refusal paths are real. The standard CRC32C check
        vector has a known independent expected value, not one computed by us.
        """
        import e034_pilot as transport
        import shutil
        import subprocess
        payload=b'123456789';expected_crc='4waSgw=='
        sdk=Path('/snap/bin/gcloud')
        if not sdk.is_file():sdk=ROOT/'artifacts/gcp-workspace/tools/google-cloud-sdk/bin/gcloud'
        if not sdk.is_file():self.fail('Existing SDK required for the actual CRC contract')
        original_run=subprocess.run
        def local_hash(argv,**kw):
            if argv[:3]!=['/snap/bin/gcloud','storage','hash']:raise AssertionError('Unexpected native command')
            return original_run([str(sdk),*argv[1:]],**kw)
        def media(request,timeout):
            if 'alt=media&generation=123'not in request.full_url:raise AssertionError('Unpinned generation')
            return io.BytesIO(payload)
        record=dict(source='gs://dl-binner-archive-167650584170/fixture.bam#123',sample='fixture',bytes=len(payload),
            sha256=hashlib.sha256(payload).hexdigest(),crc32c=expected_crc,generation='123')
        with tempfile.TemporaryDirectory()as folder:
            at=Path(folder);metadata=dict(generation='123',size=str(len(payload)),crc32c=expected_crc)
            with mock.patch.object(transport,'object_metadata',return_value=(metadata,'https://storage.googleapis.com/fixture')),mock.patch.object(transport,'token',return_value='fixture-not-a-credential'),mock.patch.object(transport.urllib.request,'urlopen',side_effect=media),mock.patch.object(transport.subprocess,'run',side_effect=local_hash),mock.patch.object(transport.shutil,'disk_usage',return_value=shutil._ntuple_diskusage(100*1024**3,0,100*1024**3)),mock.patch.dict(os.environ,E034_HASH_CONFIG=str(at/'hash-config')):
                path,proof,_=transport.source(record,at)
                self.assertEqual(path.read_bytes(),payload);self.assertTrue(proof['local_server_CRC32C_verified'])
                self.assertTrue(proof['whole_sha256_verified'])
                with mock.patch.object(transport.urllib.request,'urlopen',side_effect=AssertionError('Verified source was redownloaded')):
                    reused,_,_=transport.source(record,at);self.assertEqual(reused,path)
                path.chmod(0o600);path.write_bytes(b'bad')
                with self.assertRaisesRegex(ValueError,'missing/corrupt'):transport.source(record,at)


if __name__=='__main__':unittest.main()
