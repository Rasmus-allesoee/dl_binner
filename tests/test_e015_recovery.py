"""Actual tiny retained-output/proof and fresh-approval contracts; no VM or science."""
import ast
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

REPO=Path(__file__).absolute().parents[1];sys.path.insert(0,str(REPO/'scripts'))
from e014_collect import binding
from e015_recover import SOURCE,retained,admission


class RecoveryContracts(unittest.TestCase):
    def fixture(self,root):
        """Write actual small journals and binary payloads at the retained path contract."""
        phase=root/'original';(phase/'gates').mkdir(parents=True);(phase/'sealed-evidence/source').mkdir(parents=True)
        def write(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value));return path
        failed=write(phase/'completion.json',dict(status='FAILED',source=SOURCE,science_completed=True,
            collection_error="ModuleNotFoundError: No module named 'e014_collect'",stages=[dict(name=s,resources=dict(exit_code=0,stop_reason=None))for s in ['science','reuse-after']]))
        config=write(phase/'config.json',dict(source_commit=SOURCE,bindings={}))
        write(phase/'gates/completion.json',dict(status='SUCCESS',config=binding(config),stages=[dict(resources=dict(exit_code=0,stop_reason=None))for _ in range(7)]))
        for name in ['sealed-evidence/source/reuse-lock.json','gates/reuse-before.json','reuse-after.json']:
            write(phase/name,dict(status='PASS',files={}))
        for u in ['E009-zero','oral-zero']:
            p=phase/'work/units'/u
            for name in ['group/graph.npz','embeddings.npz','group/partition.json','train/checkpoint.pt','train/reference.npz','refine/partition.json']:
                f=p/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b'opaque exact retained fixture bytes')
            write(p/'graph-proof.json',dict(status='PASS',unit=u,graph=binding(p/'group/graph.npz'),embedding=binding(p/'embeddings.npz'),partition=binding(p/'group/partition.json')))
            write(p/'train/checkpoint.json',dict(config=dict(composition_reconstruction_weight=0.,depth_reconstruction_weight=0.),history=[{}for _ in range(20)],sha256=binding(p/'train/checkpoint.pt')['sha256']))
            write(p/'embeddings.json',dict(reload_exact=True,checkpoint_sha256=binding(p/'train/checkpoint.pt')['sha256']))
            write(p/'refine/completed.json',dict(status='SUCCESS',policy='unchanged E013',truth_accessed=False,partition_sha256=binding(p/'refine/partition.json')['sha256']))
            write(p/'export/accounting.json',dict(pre={},post={}))
        return phase,binding(failed),binding(config)

    def test_retains_passed_bytes_and_refuses_corrupt_outputs_or_failure_drift(self):
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);phase,done,cfg=self.fixture(root);before=binding(phase/'completion.json')
            result=retained(phase,done,cfg,root/'proof.json')
            self.assertEqual(result['status'],'PASS');self.assertFalse(result['science_reader_fit_or_score_replayed'])
            self.assertEqual(before,binding(phase/'completion.json'))
            (phase/'work/units/oral-zero/group/graph.npz').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'scientific bytes differ'):retained(phase,done,cfg,root/'bad.json')
            with self.assertRaisesRegex(ValueError,'journal differs'):retained(phase,dict(bytes=0,sha256='bad'),cfg,root/'bad2.json')

    def test_no_model_budget_retention_or_old_clock_fallback(self):
        with tempfile.TemporaryDirectory()as t:
            p=Path(t)/'config.json';p.write_text('{}');now=time.time();cfg=dict(_path=str(p),vm_start_epoch=now)
            r={k:True for k in ['collection_only_approved','new_clock_authorized','credit_gate_passed',
                              'pending_usage_accounted','watchdog_verified','existing_VM_only','no_scientific_replay']}
            r.update(config=binding(p),provider_STOP_seconds=2700,additional_gross_USD_upper=.64,combined_E015_gross_USD_upper=1.1,
                storage_retention_extended=False,storage_valid_until_epoch=now+5000,credit_valid_until_epoch=now+5000,
                covered_costs=['compute','disk','storage','network','operations'])
            admission(cfg,r,now)
            for delta in [dict(collection_only_approved=False),dict(new_clock_authorized=False),
                          dict(covered_costs=['compute']),dict(no_scientific_replay=False),dict(provider_STOP_seconds=8100),
                          dict(additional_gross_USD_upper=.7),dict(combined_E015_gross_USD_upper=2.1),
                          dict(storage_retention_extended=True),dict(storage_valid_until_epoch=now+2700)]:
                with self.assertRaises(ValueError):admission(cfg,r|delta,now)
            with self.assertRaises(TimeoutError):admission(cfg,r,now+601)

    def test_transferred_isolated_recovery_and_arming_entrypoints(self):
        """Check actual help-entry imports; Linux root/collection execution remains gated."""
        with tempfile.TemporaryDirectory()as t:
            root=Path(t);helpers=root/'helpers';helpers.mkdir();outside=root/'outside';outside.mkdir()
            for n in ['e015_recover.py','e015_collect.py','e014_collect.py','e015_recovery_arm.py']:
                shutil.copyfile(REPO/'scripts'/n,helpers/n)
            for n in ['e015_recover.py','e015_recovery_arm.py']:
                p=subprocess.run([sys.executable,'-I','-B',str(helpers/n),'--help'],cwd=outside,
                    capture_output=True,text=True,timeout=30)
                self.assertEqual(p.returncode,0,p.stdout+p.stderr)
                self.assertIn('--config',p.stdout)

    def test_arming_keeps_native_detector_and_changes_only_entry_clock_and_labels(self):
        original=(REPO/'scripts/e015_arm.py').read_text()
        expected=original.replace('Arm a fresh current-boot E015 held-parent exit watcher on the existing VM.',
            'Arm a fresh30-minute E015 collection-only held-parent exit watcher.')
        expected=expected.replace("cfg['vm_start_epoch']+1800","cfg['vm_start_epoch']+600").replace("cfg['vm_start_epoch']+7200","cfg['vm_start_epoch']+1800").replace("cfg['vm_start_epoch']+8100","cfg['vm_start_epoch']+2700")
        expected=expected.replace("str(repo/'scripts/e015_phase.py')","str(root/'helpers/e015_recover.py')").replace('E015 held control parent','E015 held collection-only parent')
        self.assertEqual(ast.dump(ast.parse(expected)),ast.dump(ast.parse((REPO/'scripts/e015_recovery_arm.py').read_text())))


if __name__=='__main__':unittest.main()
