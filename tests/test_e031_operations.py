"""Bounded E031 release, source, return and prospective-decision contracts.

Financial/provider observations and metadata publication are fixtures. This suite
does not claim live billing, Linux systemd or an active shutdown watchdog.
"""
import copy
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
import zipfile
from unittest.mock import patch

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import e031_phase as phase
from e031_collect import pack,verify,CONTROLS,collect_controls
from e031_control import read_plan
import e031_control as control
from e031_decision import disposition,REFERENCES
from e024_coverage import binding,write
from e031_prepare import freeze


class Operations(unittest.TestCase):
    def test_actual_input_measurements_are_retained_and_corruption_refuses(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'source';path.write_bytes(b'own closed data')
            expected={str(path):binding(path)}
            self.assertEqual(control.verify_file_bindings(expected),expected)
            path.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'no fallback'):control.verify_file_bindings(expected)
    def test_operational_packet_or_clock_change_does_not_replay_unchanged_science(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);units={u:dict(features='same-'+u) for u in control.UNITS}
            write(root/'science-lock.json',dict(units=dict(bridge=units)))
            write(root/'reuse-lock.json',dict(bridge_files={}))
            write(root/'source-lock.json',dict(operational_revision=1))
            p=dict(comparison='bridge',units=units,engineering=False,limits=dict(seconds=1))
            with patch.object(control,'EXP',root):
                before=control.source_inputs(p,'E009-noGLM')
                (root/'source-lock.json').write_text(json.dumps(dict(operational_revision=2)))
                p['limits']['seconds']=99
                self.assertEqual(before,control.source_inputs(p,'E009-noGLM'))
                p['units']['E009-noGLM']['features']='different-science'
                with self.assertRaisesRegex(ValueError,'scientific unit'):control.source_inputs(p,'E009-noGLM')
    def test_prospective_freeze_refuses_a_stale_or_partial_wheel_before_record_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            wheel=Path(folder)/'partial.whl'
            with zipfile.ZipFile(wheel,'w') as z:z.writestr('dl_binner/__init__.py',b'wrong-source')
            with self.assertRaisesRegex(ValueError,'Wheel/source identity differs'):freeze(wheel)

    def release(self,p,comparison='bridge'):
        """Create explicit simulated source/financial/boot proofs, never live account state."""
        limits=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning'/(comparison+'-plan.json')).read_text())['limits']
        # Clock is fixed early enough to test both cases before the real boundary.
        now=phase.RETENTION_EPOCH-2*86400
        write(p/'config.json',dict(fixture=True));write(p/'plan.json',dict(fixture=True));write(p/'gate.json',dict(fixture=True))
        cfg=dict(limits=limits,vm_start_epoch=now-60,_path=str(p/'config.json'),plan=str(p/'plan.json'))
        r=dict(credit_gate_passed=True,pending_usage_accounted=True,native_gates_passed=True,
            watchdog_verified=True,provider_STOP_verified=True,existing_VM_only=True,full_axes_verified=True,
            headroom_measured=True,retention_passed=True,resource_scope_verified=True,mount_baseline_verified=True,real_money_authorized=False,
            estimated_incremental_gross_USD=limits['ceiling_USD']-.1,ceiling_USD=limits['ceiling_USD'],
            provider_STOP_seconds=limits['provider_STOP_seconds'],storage_retention_extended=False,
            covered_costs=['compute','disk','storage','network','operations'],credit_valid_until_epoch=phase.RETENTION_EPOCH+86400,
            storage_valid_until_epoch=phase.RETENTION_EPOCH,config=binding(p/'config.json'),plan=binding(p/'plan.json'),
            vm_start_epoch=cfg['vm_start_epoch'],gate_files={str(p/'gate.json'):binding(p/'gate.json')})
        return cfg,r,now

    def test_bridge_and_learning_release_complete_cost_original_clock_and_retention(self):
        for comparison in ['bridge','learning']:
            with self.subTest(comparison=comparison),tempfile.TemporaryDirectory() as folder:
                cfg,r,now=self.release(Path(folder),comparison);phase.admission(cfg,r,now)
                for key,value in [('real_money_authorized',True),('credit_gate_passed',False),
                                  ('estimated_incremental_gross_USD',float('nan')),
                                  ('covered_costs',['compute']),('storage_valid_until_epoch',phase.RETENTION_EPOCH+1)]:
                    bad=copy.deepcopy(r);bad[key]=value
                    with self.assertRaises(ValueError):phase.admission(cfg,bad,now)
                with self.assertRaises(ValueError):phase.admission(cfg,r,cfg['vm_start_epoch']+cfg['limits']['seconds'])
                badcfg=copy.deepcopy(cfg);badcfg['vm_start_epoch']=phase.RETENTION_EPOCH-60
                bad=copy.deepcopy(r);bad['vm_start_epoch']=badcfg['vm_start_epoch']
                with self.assertRaises(ValueError):phase.admission(badcfg,bad,badcfg['vm_start_epoch'])
                (Path(folder)/'gate.json').write_text('changed')
                with self.assertRaisesRegex(ValueError,'proof bytes'):phase.admission(cfg,r,now)

    def test_held_service_render_parse_and_no_silent_scientific_scope_expansion(self):
        service=phase.service_content('/srv/run','/usr/bin/python3','/repo/scripts/e031_phase.py','/srv/run/config.json','user')
        self.assertIn('Restart=no',service);self.assertIn(' -I -B ',service)
        with self.assertRaises(ValueError):phase.service_content('/srv/run\nevil','python','script','config','user')
        for source in (ROOT/'scripts').glob('e031_*.py'):compile(source.read_text(),str(source),'exec')
        with tempfile.TemporaryDirectory() as folder:
            p=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/bridge-plan.json').read_text())
            p['engineering']=True;p['units']['oral-noGLM']['truth']='forbidden'
            path=Path(folder)/'plan.json';write(path,p)
            with self.assertRaisesRegex(ValueError,'truth input'):read_plan(path,True)
            p=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/bridge-plan.json').read_text());write(Path(folder)/'native.json',p)
            with self.assertRaisesRegex(ValueError,'release required'):read_plan(Path(folder)/'native.json')

    def test_a_mounted_filesystem_cannot_inherit_another_disks_usage_baseline(self):
        with tempfile.TemporaryDirectory() as folder:
            cfg=dict(filesystem_device=-1,initial_filesystem_used_bytes=0,limits=dict(extra_bytes=7*1024**3))
            with self.assertRaisesRegex(ValueError,'filesystem changed'):phase.filesystem_contract(folder,cfg)

    def test_final_publication_stays_final_and_upload_failure_is_exposed(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);seen=[];result=dict(status='SUCCESS',science_completed=True,collection_readback_verified=True)
            with patch.object(phase,'status',side_effect=seen.append):
                phase.deliver_completion(result,p,time.time()+120,lambda f:None)
            self.assertEqual(seen[-1]['status'],'SUCCESS');self.assertEqual(json.loads((p/'completion.json').read_text())['status'],'SUCCESS')
        with tempfile.TemporaryDirectory() as folder:
            seen=[];result=dict(status='SUCCESS',science_completed=True)
            def failed(f):raise RuntimeError('fixture transport failed')
            with patch.object(phase,'status',side_effect=seen.append):phase.deliver_completion(result,Path(folder),time.time()+120,failed)
            self.assertEqual(seen[-1]['status'],'FAILED');self.assertIn('completion_delivery_error',result)

    def test_real_collector_exact_aliases_controls_corruption_and_small_cap(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);work=p/'work';work.mkdir();(work/'a.bin').write_bytes(b'own-fixture'*500);(work/'b.bin').write_bytes((work/'a.bin').read_bytes())
            phase_root=p/'phase';phase_root.mkdir();evidence=p/'evidence';evidence.mkdir()
            for name in CONTROLS+['config.json','science-plan.json','started.json','release.json','science-result.json','science-disk.jsonl','external-data.json']:
                dst=phase_root/name;dst.parent.mkdir(parents=True,exist_ok=True);write(dst,dict(data_copied=False) if name=='external-data.json' else dict(fixture=True))
            collect_controls(phase_root,evidence/'controls');write(evidence/'external-data.json',dict(data_copied=False))
            result=pack(work,evidence,p/'return');proof=verify(p/'return/e031-evidence.tar.gz',result['archive'])
            self.assertTrue(proof['every_member_verified']);self.assertEqual(len(proof['aliases']),1)
            with self.assertRaises(FileExistsError):pack(work,evidence,p/'return')
            with self.assertRaisesRegex(ValueError,'ceiling|cap|exceed|exceeding'):pack(work,evidence,p/'too-small',ceiling=16)
            with (p/'return/e031-evidence.tar.gz').open('r+b') as f:f.seek(-1,2);f.write(b'!')
            with self.assertRaisesRegex(ValueError,'bytes/cap'):verify(p/'return/e031-evidence.tar.gz',result['archive'])

    def test_integer_joint_decision_retains_a_failed_criterion_and_common_modes(self):
        old={u:dict(recovered_bp=10_000_000,reference_bp=REFERENCES[u],target_90=5) for u in REFERENCES}
        new=copy.deepcopy(old);new['oral-noGLM']['recovered_bp']+=11_000_000
        self.assertEqual(disposition('bridge',old,new,{})['disposition'],'KEEP')
        new['E009-noGLM']['target_90']=4
        self.assertEqual(disposition('bridge',old,new,{})['disposition'],'MODIFY')
        self.assertEqual(disposition('bridge',old,old,{})['disposition'],'ABANDON')
        anchors={u:dict(old[u],recovered_bp=20_000_000) for u in ['E009-GLM','oral-noGLM']}
        new=copy.deepcopy(old);new['E009-GLM']['recovered_bp']=20_000_000
        self.assertEqual(disposition('learning',old,new,anchors)['disposition'],'KEEP')
        bad=copy.deepcopy(new);bad['oral-noGLM']['reference_bp']=100
        with self.assertRaises(ValueError):disposition('learning',old,bad,anchors)
        del bad['oral-noGLM']
        with self.assertRaises(ValueError):disposition('bridge',old,bad,{})


if __name__=='__main__':unittest.main()
