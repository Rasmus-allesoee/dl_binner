"""Actual local E022 restore/collection/admission adapters; no VM or shell mocks."""
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import time
import unittest

S=Path(__file__).absolute().parents[1]/'scripts';sys.path.insert(0,str(S))
import e022_control as control
import e022_collect as collector
import e022_phase as phase
from e022_arm import service_content
from e014_collect import binding


class Operational(unittest.TestCase):
    def test_restore_exact_refuses_corrupt_extra_symlink_and_existing(self):
        with tempfile.TemporaryDirectory()as f:
            r=Path(f);src=r/'pairs';src.mkdir();(src/'cache.json').write_text('{}')
            arc=r/'pairs.tar.gz'
            with tarfile.open(arc,'w:gz')as a:a.add(src/'cache.json',arcname='cache.json')
            lock=dict(pair_archive=binding(arc),pair_members={'cache.json':binding(src/'cache.json')})
            control.restore_pairs(arc,r/'restored',lock);self.assertEqual((r/'restored/cache.json').read_text(),'{}')
            with self.assertRaises(FileExistsError):control.restore_pairs(arc,r/'restored',lock)
            bad=copy.deepcopy(lock);bad['pair_members']['cache.json']['bytes']=3
            with self.assertRaisesRegex(ValueError,'inventory'):control.restore_pairs(arc,r/'bad',bad)
            self.assertFalse((r/'bad').exists())
            link=r/'linked';link.symlink_to(arc)
            with self.assertRaises(ValueError):control.restore_pairs(link,r/'bad',lock)
            evil=r/'evil.tar.gz'
            with tarfile.open(evil,'w:gz')as a:
                m=tarfile.TarInfo('../escape');m.size=1;a.addfile(m,io.BytesIO(b'x'))
            with self.assertRaises(ValueError):control.restore_pairs(evil,r/'bad',dict(lock,pair_archive=binding(evil)))

    def test_actual_collector_exact_alias_incomplete_and_cap(self):
        with tempfile.TemporaryDirectory()as f:
            r=Path(f);w=r/'work';e=r/'evidence';e.mkdir();(e/'gate.json').write_text('{}')
            u=w/'units/E009-relational';(u/'train').mkdir(parents=True)
            (u/'embeddings.npz').write_bytes(b'abc');(u/'train/reference.npz').write_bytes(b'abc')
            (u/'pairs.npz').write_bytes(b'pair');(u/'calibration.npz').write_bytes(b'calibration')
            got=collector.pack(w,e,r/'return');self.assertTrue(got['every_member_verified']);self.assertEqual(len(got['aliases']),1)
            with self.assertRaisesRegex(ValueError,'Compressed'):collector.pack(w,e,r/'too-small',ceiling=10)
            (u/'train/reference.npz').write_bytes(b'bad')
            with self.assertRaisesRegex(ValueError,'alias'):collector.select(w)
            files,_,aliases,_=collector.select(w,allow_incomplete=True);self.assertEqual(aliases,{})
            self.assertIn('work/units/E009-relational/train/reference.npz',files)

    def test_controller_identity_translation_requires_complete_source(self):
        identity=dict(root='/phase',service_name='e022-owned',source='a'*40,input_lock='/lock.json',
            vm_start_epoch=123.,archive_prefix='gs://private/e022/attempt')
        value=phase.configuration(identity,Path('/repo'),42,{'/file':{'bytes':1,'sha256':'b'*64}})
        self.assertEqual(value['source_commit'],identity['source'])
        self.assertEqual(value['science_plan'],'/phase/science-plan.json')
        self.assertEqual(value['initial_filesystem_used_bytes'],42)
        bad=dict(identity,source='short')
        with self.assertRaises(ValueError):phase.configuration(bad,Path('/repo'),42,{})

    def test_fresh_credit_budget_and_original_clock(self):
        with tempfile.TemporaryDirectory()as f:
            p=Path(f)/'cfg';p.write_text('{}');now=time.time();cfg=dict(vm_start_epoch=now-20,_path=str(p))
            v=dict(config=binding(p),provider_STOP_seconds=8100,ceiling_USD=2,estimated_incremental_gross_USD=1.5,
                real_money_authorized=False,storage_retention_extended=False,covered_costs=['compute','disk','storage','network','operations'],
                credit_valid_until_epoch=now+10000,storage_valid_until_epoch=now+10000)
            for k in ['credit_gate_passed','pending_usage_accounted','native_gates_passed','watchdog_verified','existing_VM_only','full_axes_verified']:v[k]=True
            phase.admission(cfg,v,now)
            for key,value in [('credit_gate_passed',False),('estimated_incremental_gross_USD',float('nan')),('estimated_incremental_gross_USD',2.01),('real_money_authorized',True),('storage_valid_until_epoch',now+100),('storage_retention_extended',True)]:
                bad=dict(v);bad[key]=value
                with self.assertRaises((ValueError,TimeoutError)):phase.admission(cfg,bad,now)
            with self.assertRaises(TimeoutError):phase.admission(cfg,v,now+7200)

    def test_review_refuses_missing_admission_and_retains_unknown_labels(self):
        import e022_review
        with tempfile.TemporaryDirectory()as f:
            p=Path(f)/'admission.json';p.write_text('{}')
            with self.assertRaises(ValueError):e022_review.admission_contract(p)
        pairs={'ids':['a','b','c'],'left':[0,0,1],'right':[1,2,2],'sign':[1,-1,1]}
        a=e022_review.pair_label_audit(pairs,{'a':'known','b':'known','c':None})['counts']
        self.assertEqual(a['1']['same_admitted_label'],1);self.assertEqual(a['1']['unresolved'],1);self.assertEqual(a['-1']['unresolved'],1)

    def test_atomic_parent_ready_and_safe_nonrestarting_service(self):
        with tempfile.TemporaryDirectory()as f:
            p=Path(f)/'ready.json';phase.write_json(p,{'ready':True});self.assertEqual(json.loads(p.read_text()),{'ready':True})
            with self.assertRaises(FileExistsError):phase.write_json(p,{'ready':False})
        s=service_content(Path('/repo'),Path('/phase'),'owner',Path('/phase/config.json'),3600)
        self.assertIn('Restart=no',s);self.assertIn('RefuseManualStop=yes',s);self.assertIn('RuntimeMaxSec=3600',s)
        for n in [0,7201,True]:
            with self.assertRaises(ValueError):service_content(Path('/repo'),Path('/phase'),'owner',Path('/cfg'),n)
        with self.assertRaises(ValueError):service_content(Path('/bad path'),Path('/phase'),'owner',Path('/cfg'),1)


if __name__=='__main__':unittest.main()
