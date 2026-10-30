"""Scientific-boundary, native-consumer and complete export/return contracts."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e024_coverage import binding, write
from e027_phase import admission, SECONDS, STOP_SECONDS, phase_exit, service_content
from e027_launch import render_host, render_release
from e027_reference import export, validate_means
from e027_collect import pack, verify, collect_controls, CONTROLS


class Operations(unittest.TestCase):
    def test_actual_remote_consumers_compile_with_transferred_exact_wheel(self):
        with tempfile.TemporaryDirectory() as folder:
            wheel = Path(folder)/'candidate.whl'; wheel.write_bytes(b'own-wheel-fixture')
            finance = dict(wheel_path=str(wheel), wheel_binding=binding(wheel))
            ident = dict(root='/srv/dl_binner/experiments/e027/tiny', source='a'*40, wheel_binding=binding(wheel))
            for code in [render_host(ident, finance), render_release(ident, {})]:
                compile(code, 'actual-rendered-consumer', 'exec')
            self.assertIn('common-multiview-marker-binner', render_host(ident, finance))
            self.assertIn('validate=True', render_host(ident, finance))
            self.assertNotIn('instances',''.join([service_content('/r','/p','/s','/c','u')]))

    def test_credit_deadline_original_clock_and_bound_gates_refuse_drift(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/'config.json'; p.write_text('{}')
            g = Path(folder)/'gates.json'; g.write_text('{}')
            now = 1793400000.
            cfg = dict(vm_start_epoch=now-60, _path=str(p))
            flags = ['credit_gate_passed','pending_usage_accounted','native_gates_passed','watchdog_verified',
                     'provider_STOP_verified','existing_VM_only','full_axes_verified','headroom_measured','retention_passed']
            release = dict.fromkeys(flags, True)
            release.update(real_money_authorized=False, estimated_incremental_gross_USD=14., ceiling_USD=15,
                provider_STOP_seconds=STOP_SECONDS, storage_retention_extended=False, covered_costs=['compute','disk','storage','network','operations'],
                credit_valid_until_epoch=1800000000, storage_valid_until_epoch=1793746800,
                config=binding(p), gate_files={str(g):binding(g)})
            admission(cfg, release, now)
            for field, value in [('real_money_authorized',True),('estimated_incremental_gross_USD',float('nan')),
                ('estimated_incremental_gross_USD',15.1),('storage_retention_extended',True),
                ('storage_valid_until_epoch',1793746801),('watchdog_verified',False),('covered_costs',['compute'])]:
                with self.assertRaises(ValueError): admission(cfg, dict(release, **{field:value}), now)
            with self.assertRaises(ValueError): admission(dict(cfg,vm_start_epoch=now-SECONDS),release,now)
            g.write_text('{"drift":1}')
            with self.assertRaisesRegex(ValueError,'bytes'): admission(cfg,release,now)
            self.assertEqual(phase_exit(dict(status='SUCCESS',science_completed=True,collection_readback_verified=True)),0)
            self.assertEqual(phase_exit(dict(status='SUCCESS',science_completed=False)),1)

    def test_native_reference_complete_axis_and_duplicate_changed_DNA_refusal(self):
        with tempfile.TemporaryDirectory() as folder:
            r=Path(folder);f=r/'source.fa';f.write_text('>opaque-z\n'+'ACGT'*700+'\n>opaque-a\n'+'TGCA'*300+'\n>short\nACG\n')
            native=r/'native';native.mkdir();(native/'bin.1.fa').write_text('>opaque-z\n'+'ACGT'*700+'\n')
            out=export(f,native,r/'export')
            self.assertEqual(out['contigs'],3);self.assertEqual(out['bp'],4003)
            self.assertEqual(out['statuses']['assigned']['bp'],2800)
            self.assertEqual(out['statuses']['excluded']['bp'],3)
            self.assertTrue((native/'bin.1.fa').is_file())
            (native/'bin.2.fa').write_text('>opaque-z\n'+'ACGT'*700+'\n')
            with self.assertRaisesRegex(ValueError,'duplicated'): export(f,native,r/'bad')
            samples=['s'+str(i)for i in range(10)];m=r/'means.tsv'
            m.write_text('contig_id\t'+'\t'.join(samples)+'\n'+''.join(q+'\t'+'\t'.join(['0']*10)+'\n' for q in ['opaque-z','opaque-a','short']))
            receipt=r/'receipt.json';write(receipt,dict(status='PASS',matrix=binding(m),reference=binding(f),missing_cells=0,all_cells_measured=True,samples=samples,rows=3))
            self.assertEqual(validate_means(m,receipt,f)['rows'],3)
            m.write_text(m.read_text().replace('opaque-z','wrong'))
            write(r/'bad-receipt.json',dict(json.loads(receipt.read_text()),matrix=binding(m)))
            with self.assertRaisesRegex(ValueError,'reordered'): validate_means(m,r/'bad-receipt.json',f)

    def test_manifest_inclusive_alias_and_linked_input_omission_contract(self):
        with tempfile.TemporaryDirectory() as folder:
            r=Path(folder);work=r/'work';work.mkdir();phase=r/'phase';phase.mkdir();evidence=r/'evidence';evidence.mkdir()
            for name in CONTROLS+['config.json','science-plan.json','started.json','release.json','science-result.json','science-disk.jsonl','external-data.json']:
                p=phase/name;p.parent.mkdir(parents=True,exist_ok=True);write(p,dict(data_copied=False)if name=='external-data.json'else{})
            collect_controls(phase,evidence/'controls');write(evidence/'external-data.json',dict(data_copied=False))
            for name,data in [('units/x/admit/tokens/counts.npy',b'retained-array'),('units/x/new.npz',b'new-science'),('units/x/alias.npz',b'new-science'),('reference/native/bin.1.fa',b'>q\nACGT\n')]:
                p=work/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            result=pack(work,evidence,r/'return');inv=json.loads((r/'return/inventory.json').read_text())
            self.assertIn('units/x/admit/tokens/counts.npy',inv['omitted_retained_on_disk'])
            self.assertIn('work/reference/native/bin.1.fa',inv['members'])
            self.assertEqual(len(inv['aliases']),1);self.assertTrue(result['every_member_verified'])
            a=r/'return/e027-evidence.tar.gz';a.write_bytes(a.read_bytes()[:-5]+b'bad!!')
            with self.assertRaises((ValueError,EOFError,OSError)): verify(a,result['archive'])

    def test_common_mode_includes_teacher_proposals_and_frozen_references(self):
        p=json.loads((ROOT/'experiments/E027-common-information-binner/runtime-plan.json').read_text())
        self.assertEqual(list(p['units']),['E009-noGLM','E009-GLM','oral-noGLM'])
        self.assertIsNone(p['units']['E009-noGLM']['frozen']);self.assertIsNotNone(p['units']['E009-GLM']['frozen'])
        self.assertEqual(p['units']['E009-noGLM']['features'],p['units']['E009-GLM']['features'])
        self.assertNotIn('anchor_graph',p['units']['E009-GLM'])
        protocol=json.loads((ROOT/'experiments/E027-common-information-binner/protocol.json').read_text())
        self.assertAlmostEqual(protocol['anchors']['E009_E023']['R95'],.1041634228737078)
        self.assertEqual(protocol['full_reference_bp'],{'E009':554661890,'oral':2083072211})


if __name__=='__main__': unittest.main()
