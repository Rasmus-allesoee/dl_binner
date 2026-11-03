"""Actual E032 stream/alias, collection, schema and rendered-consumer contracts."""
import base64
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import time
import unittest

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e032_restore import stream_restore,COMPRESSED,LOGICAL
from e032_collect import pack,verify
from e032_phase import validate_config
from e032_launch import config_value,render_host,render_release,render_inventory


def fixture(corrupt=False):
    """Write an actual inventory-first archive with two consumed exact aliases."""
    value=b'closed numerical fixture';b=dict(bytes=len(value),sha256=hashlib.sha256(value).hexdigest())
    name='work/E009-noGLM/forest/result/forest.npz';alias='work/E009-GLM/forest/result/forest.npz'
    inv=dict(members={name:b},all_work_members={name[5:]:b,alias[5:]:b},
        aliases={alias:dict(b,canonical=name)},omitted_retained_on_disk={})
    raw=io.BytesIO()
    with tarfile.open(fileobj=raw,mode='w:gz') as archive:
        for key,data in [('inventory.json',json.dumps(inv).encode()),(name,value+(b'x' if corrupt else b''))]:
            member=tarfile.TarInfo(key);member.size=len(data);archive.addfile(member,io.BytesIO(data))
    data=raw.getvalue();meta=dict(size=len(data),generation='123',md5_hash=base64.b64encode(hashlib.md5(data).digest()).decode())
    return data,meta,dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


class Operations(unittest.TestCase):
    def test_single_T4_uses_the_other_pool_without_fallback(self):
        from e032_gpu import gate,ZONE,SOURCE
        from e029_gpu_launch import commands
        now=time.time();f=dict(coverage_status='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY',
            real_money_authorized=False,ceiling_USD=3,estimated_complete_gross_USD=2.9,
            checked_epoch=now,credit_checked_epoch=now,storage_valid_until_epoch=1794351600,
            credit_valid_until_epoch=1800000000,T4_complete_current_pricing_passed=True)
        gate(f,now);self.assertEqual(ZONE,'us-central1-f')
        with self.assertRaises(ValueError):gate(dict(f,T4_complete_current_pricing_passed=False),now)
        baseline=dict(serviceAccounts=[dict(email='fixture',scopes=['fixture'])],networkInterfaces=[dict(subnetwork='fixture')])
        argv=commands('e029-batching-fixture',ZONE,baseline,'fixture','T4')
        self.assertTrue(all('--type=pd-standard' in c for c in argv[:2]))
        self.assertIn('--machine-type=n1-standard-8',argv[-1]);self.assertIn('--max-run-duration=6300s',argv[-1])
    def test_actual_full_stream_exact_alias_and_corruption_refusal(self):
        for bad in [False,True]:
            data,meta,wanted=fixture(bad)
            with tempfile.TemporaryDirectory() as t:
                root=Path(t)/'restored'
                if bad:
                    with self.assertRaisesRegex(ValueError,'member differs'):stream_restore(io.BytesIO(data),meta,wanted,root,reserve=0)
                    self.assertFalse((root/'work/restore-admission.json').exists())
                else:
                    result=stream_restore(io.BytesIO(data),meta,wanted,root,reserve=0)
                    self.assertTrue(result['every_member_verified']);self.assertEqual(result['aliases'],1)
                    a=root/'work/E009-noGLM/forest/result/forest.npz';b=root/'work/E009-GLM/forest/result/forest.npz'
                    self.assertEqual(a.stat().st_ino,b.stat().st_ino)
    def test_matched_3_6_GiB_bounds_and_reserve_refusal(self):
        self.assertEqual(COMPRESSED,3*1024**3);self.assertEqual(LOGICAL,6*1024**3)
        data,meta,wanted=fixture()
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(ValueError,'reserve refused'):
                stream_restore(io.BytesIO(data),meta,wanted,Path(t)/'out',reserve=10**20)
            with self.assertRaisesRegex(ValueError,'size/generation'):
                stream_restore(io.BytesIO(data),dict(meta,size=COMPRESSED+1),dict(wanted,bytes=COMPRESSED+1),Path(t)/'oversized',reserve=0)
    def test_real_collection_alias_and_byte_verifier(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);work=root/'work';evidence=root/'evidence';work.mkdir();evidence.mkdir()
            for n in ['a.npz','b.npz']:(work/n).write_bytes(b'identical native fixture')
            (evidence/'config.json').write_text('{}\n')
            result=pack(work,evidence,root/'return');self.assertEqual(len(result['aliases']),1)
            path=root/'return/e032-evidence.tar.gz';self.assertTrue(verify(path,result['archive'])['every_member_verified'])
            path.write_bytes(b'corrupt')
            with self.assertRaises(ValueError):verify(path,result['archive'])
    def test_full_schema_and_actual_host_release_rendering(self):
        with tempfile.TemporaryDirectory() as t:
            wheel=Path(t)/'tiny.whl';wheel.write_bytes(b'wheel-shaped rendering fixture')
            now=time.time();f=dict(credit_checked_epoch=now,checked_epoch=now,real_money_authorized=False,
                coverage_status='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY',estimated_complete_gross_USD=5.8,
                ceiling_USD=6,storage_valid_until_epoch=1794351600,credit_valid_until_epoch=1800000000,
                wheel_path=str(wheel),wheel_binding=dict(bytes=wheel.stat().st_size,sha256=hashlib.sha256(wheel.read_bytes()).hexdigest()))
            ident=dict(vm_start_epoch=now,root='/srv/dl_binner/experiments/e032/tiny',repo='/srv/dl_binner/repo',
                source='a'*40,service_name='e032-tiny',user='rasmus_allesoee_gmail_com',archive_prefix='gs://dl-binner-archive-167650584170/e032/tiny/')
            cfg=config_value(ident,f,0);validate_config(cfg,now)
            for key in cfg:
                bad=dict(cfg);bad.pop(key)
                with self.assertRaisesRegex(ValueError,'configuration'):validate_config(bad,now)
            with self.assertRaises(ValueError):validate_config(dict(cfg,provider_deadline_epoch=1794351601),now)
            with self.assertRaises(ValueError):validate_config(dict(cfg,financial=dict(f,real_money_authorized=True)),now)
            for code in [render_host(ident,f),render_host(ident,f,dict(name='e032-task-fixture')),render_release(ident,{}, {}),render_inventory('fixture')]:
                compile(code,'actual rendered E032 consumer','exec')
            armer=(ROOT/'scripts/e032_arm.py').read_text()
            self.assertIn("repo/'scripts/e032_phase.py'",armer)
            self.assertIn('try-restart',armer)


if __name__=='__main__':unittest.main()
