"""Real stream/member/alias, paired-source and rendered launch refusal contracts."""
import base64
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e031_stream_return import stream_restore
from e031_learner_launch import learner_host, learner_release, mount_code, MOUNT, remaining_provider_seconds


def fixture(bad_member=False, bad_alias=False):
    """Produce real gzip/tar bytes with a complete inventory and exact alias."""
    value=b'closed evidence\n'; b=dict(bytes=len(value),sha256=hashlib.sha256(value).hexdigest())
    name='work/barrier/proof.json'; alias='work/actors/tiny/query-neighbors.json'
    inv=dict(members={name:b},all_work_members={'barrier/proof.json':b,'actors/tiny/query-neighbors.json':b},
             aliases={alias:dict(b,canonical=name)},omitted_retained_on_disk={})
    if bad_alias:inv['aliases'][alias]['bytes']+=1
    output=io.BytesIO()
    with tarfile.open(fileobj=output,mode='w:gz')as out:
        for n,data in [('inventory.json',json.dumps(inv).encode()),(name,value+b'x' if bad_member else value)]:
            member=tarfile.TarInfo(n);member.size=len(data);out.addfile(member,io.BytesIO(data))
    raw=output.getvalue();expected=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    return raw,dict(size=len(raw),generation='actual-tiny-fixture',md5_hash=base64.b64encode(hashlib.md5(raw).digest()).decode()),expected


class Followthrough(unittest.TestCase):
    def test_recorded_setup_recovery_keeps_original_provider_horizon(self):
        remaining=remaining_provider_seconds(1000,1400)
        self.assertLessEqual(1400+remaining,1000+58500)
        self.assertLess(remaining,58500)
        with self.assertRaises(TimeoutError):remaining_provider_seconds(1000,1000+58000)

    def test_real_stream_and_exact_alias_reuse(self):
        raw,meta,expected=fixture()
        with tempfile.TemporaryDirectory()as folder:
            first=Path(folder)/'first';second=Path(folder)/'second'
            proof=stream_restore(io.BytesIO(raw),meta,expected,first,reserve=0)
            self.assertTrue(proof['every_member_verified']);self.assertEqual(proof['aliases'],1)
            alias=first/'work/actors/tiny/query-neighbors.json';self.assertEqual(alias.read_bytes(),b'closed evidence\n')
            stream_restore(io.BytesIO(raw),meta,expected,second,reserve=0,existing=first)
            self.assertEqual((first/'work/barrier/proof.json').stat().st_ino,(second/'work/barrier/proof.json').stat().st_ino)

    def test_corrupt_member_alias_and_transport_refuse(self):
        for member,alias,transport in [(True,False,False),(False,True,False),(False,False,True)]:
            raw,meta,expected=fixture(member,alias)
            if transport:expected['sha256']='0'*64
            with tempfile.TemporaryDirectory()as folder:
                with self.assertRaises(ValueError):stream_restore(io.BytesIO(raw),meta,expected,Path(folder)/'out',reserve=0)
                self.assertFalse((Path(folder)/'out/stream-verification.json').exists())

    def test_reserve_refusal_leaves_no_success(self):
        raw,meta,expected=fixture()
        with tempfile.TemporaryDirectory()as folder:
            with self.assertRaises(RuntimeError):stream_restore(io.BytesIO(raw),meta,expected,Path(folder)/'out',reserve=10**20)
            self.assertFalse((Path(folder)/'out/stream-verification.json').exists())

    def test_rendered_existing_disk_host_and_native_schedule_release(self):
        # Render against a real tiny wheel-shaped packet. No provider calls or
        # actual mount/format are mocked as successful native evidence here.
        with tempfile.TemporaryDirectory()as folder:
            packet=Path(folder)/'candidate.whl';packet.write_bytes(b'wheel-packet-fixture')
            f=dict(wheel_path=str(packet),wheel_binding=dict(bytes=packet.stat().st_size,sha256=hashlib.sha256(packet.read_bytes()).hexdigest()))
            ident=dict(root=MOUNT+'/learning-fixture',repo='/srv/dl_binner/repo',source='f'*40,scratch={'reused':True})
            host=learner_host(ident,f);release=learner_release(ident,{'status':'RUNNING'})
            for label,code in [('mount',mount_code()),('host',host),('release',release)]:compile(code,label,'exec')
            self.assertNotIn('mkfs',mount_code());self.assertIn('paired-plan.json',host)
            self.assertIn('forecast_remaining_seconds',release);self.assertNotIn('10800+900',release)

    def test_real_matched_query_unknown_denominators(self):
        from e031_neighbors import evaluate_queries
        labels=dict(a='g',b='g',c='g',d='h',e=None,f='h',u=None)
        rows=[dict(id='a',length=500,depth_positive=True,strata=['prospective'],
                   E023_neighbors=['b','c','d','e','f'],native_neighbors=['b','d','e','f','u']),
              dict(id='u',length=1000,depth_positive=False,strata=[],
                   E023_neighbors=['a','b','c','d','e'],native_neighbors=['a','b','c','d','e'])]
        value=evaluate_queries(rows,labels,{'g':'bacteria','h':'bacteria'},{'g'})
        self.assertEqual(value['all_queries'],2);self.assertEqual(value['known_query_bp'],500)
        self.assertEqual(value['same_origin_bp_weighted'],dict(E023=.4,native=.2))
        rows[0]['native_neighbors'][0]='a'
        with self.assertRaisesRegex(ValueError,'five-neighbor'):evaluate_queries(rows,labels,{},set())

    def test_native_review_view_reuses_actual_payload_bytes(self):
        from e031_native_review import prepare_view
        from e024_coverage import binding
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);prior=root/'prior';repo=root/'repo';(repo/'scripts').mkdir(parents=True);(repo/'experiments').mkdir()
            names=['artifacts/e009-truth-v2/20261015/attempt-local-v2/truth-v2/manifest.json',
                   'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1/manifest.json',
                   'artifacts/e014-multiview-reconstruction/inspection-20261019/oral-marker-review.json',
                   'artifacts/e011-cached-grouping-reference/restore-local/candidate/markers/evidence.json']
            for name in names:
                p=prior/'view'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{"fixture":true}\n')
            payload=dict(status='PASS_EXACT_EVIDENCE_PAYLOAD',files={n:binding(prior/'view'/n)for n in names})
            (prior/'inputs.json').write_text(json.dumps(dict(payload=payload)))
            proof=prepare_view(repo,root/'new-view',prior,payload)
            self.assertTrue(proof['truth_is_separate_from_training'])
            for name in names:self.assertEqual(binding(root/'new-view'/name),payload['files'][name])
            (prior/'view'/names[0]).write_text('corrupt')
            with self.assertRaisesRegex(ValueError,'payload bytes differ'):prepare_view(repo,root/'refused',prior,payload)

    def test_both_constructors_are_required_in_all_three_modes(self):
        text=(ROOT/'experiments/E031-bootstrap-preserving-learning/paired.smk').read_text()
        for prefix,unit in [('E009_noGLM','E009-noGLM'),('E009_GLM','E009-GLM'),('oral_noGLM','oral-noGLM')]:
            self.assertIn('rule '+prefix+'_e023:',text);self.assertIn('rule '+prefix+'_paired:',text)
            self.assertIn("input: ['"+unit+"/e023/done.json', '"+unit+"/audit/done.json']",text)


if __name__=='__main__':unittest.main()
