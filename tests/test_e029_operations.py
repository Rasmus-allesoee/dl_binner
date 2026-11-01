"""Actual consumer compilation, byte guards, clock/STOP and cache-return contracts."""
import hashlib,json
from pathlib import Path
import sys,tempfile,time,unittest
from unittest.mock import patch
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding
from e029_phase import admission,SECONDS,STOP_SECONDS,deliver_completion
from e029_launch import render_host,render_release
from e029_collect import pack,verify,collect_controls,CONTROLS


class Operations(unittest.TestCase):
    def test_unknown_plan_fields_refuse_even_for_engineering(self):
        from e029_control import read_plan
        p=json.loads((ROOT/'experiments/E029-certifiable-joint-retrieval/runtime-plan.json').read_text())
        p['engineering']=True
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'plan.json';path.write_text(json.dumps(p));read_plan(path,True)
            p['truth_lookup']='forbidden';path.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'Unknown/missing'):read_plan(path,True)

    def test_actual_host_release_consumers_compile_and_fixed_limits(self):
        self.assertEqual(SECONDS,216000);self.assertEqual(STOP_SECONDS,216900)
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'candidate.whl';p.write_bytes(b'fixture')
            f=dict(wheel_path=str(p),wheel_binding=binding(p));ident=dict(root='/srv/dl_binner/experiments/e029/tiny',source='a'*40,wheel_binding=binding(p))
            for code in [render_host(ident,f),render_release(ident,{})]:compile(code,'actual-e029-consumer','exec')
            self.assertIn('certifiable-joint-retrieval',render_host(ident,f));self.assertNotIn('metabat',render_host(ident,f).lower())
    def test_input_import_guard_precedes_product_and_inherited_helpers(self):
        import inspect
        from e029_control import verify_inputs
        source=inspect.getsource(verify_inputs)
        self.assertLess(source.index('product_scope()'),source.index('from dl_binner.discovery'))
        self.assertLess(source.index('product_scope()'),source.index('from e028_control'))

    def test_clock_finance_source_and_failed_completion_refusal(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'config.json';p.write_text('{}');g=Path(t)/'gate.json';g.write_text('{}');now=1793470000.
            cfg=dict(vm_start_epoch=now-60,_path=str(p))
            flags=['credit_gate_passed','pending_usage_accounted','native_gates_passed','watchdog_verified','provider_STOP_verified','existing_VM_only','full_axes_verified','headroom_measured','retention_passed']
            r=dict.fromkeys(flags,True);r.update(real_money_authorized=False,estimated_incremental_gross_USD=20.6,ceiling_USD=22,provider_STOP_seconds=STOP_SECONDS,storage_retention_extended=False,covered_costs=['compute','disk','storage','network','operations'],credit_valid_until_epoch=1800000000,storage_valid_until_epoch=1793746800,config=binding(p),gate_files={str(g):binding(g)})
            admission(cfg,r,now)
            for k,v in [('real_money_authorized',True),('estimated_incremental_gross_USD',float('nan')),('estimated_incremental_gross_USD',22.1),('provider_STOP_seconds',22500),('watchdog_verified',False),('storage_retention_extended',True)]:
                with self.assertRaises(ValueError):admission(cfg,dict(r,**{k:v}),now)
            with self.assertRaises(ValueError):admission(dict(cfg,vm_start_epoch=now-SECONDS),r,now)
            g.write_text('changed')
            with self.assertRaises(ValueError):admission(cfg,r,now)
    def test_actual_collection_alias_integrity_and_failure_controls(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);work=r/'work';work.mkdir();phase=r/'phase';phase.mkdir();evidence=r/'evidence';evidence.mkdir()
            for name in CONTROLS+['config.json','science-plan.json','started.json','release.json','science-result.json','science-disk.jsonl','external-data.json']:
                p=phase/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'data_copied':False} if name=='external-data.json' else {}))
            collect_controls(phase,evidence/'controls');(evidence/'external-data.json').write_text('{"data_copied":false}')
            for name in ['native.npz','alias.npz']:(work/name).write_bytes(b'new-frozen-numeric')
            result=pack(work,evidence,r/'return');self.assertEqual(len(result['aliases']),1)
            archive=r/'return/e029-evidence.tar.gz';self.assertTrue(verify(archive,result['archive'])['every_member_verified'])
            archive.write_bytes(b'corrupt')
            with self.assertRaises(ValueError):verify(archive,result['archive'])

    def test_completion_transport_failure_keeps_bytes_and_publishes_failed(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);observed=[];result=dict(status='SUCCESS',science_completed=True,stages=[])
            def fail(path):raise IOError('injected transport error')
            with patch('e029_phase.status',lambda value:observed.append(value)):
                deliver_completion(result,root,time.time()+60,fail)
            self.assertEqual(observed[-1]['status'],'FAILED')
            self.assertEqual(observed[-1]['completion'],binding(root/'completion.json'))
            self.assertEqual(json.loads((root/'completion.json').read_text())['status'],'SUCCESS')
            self.assertIn('completion_delivery_error',result)


if __name__=='__main__':unittest.main()
