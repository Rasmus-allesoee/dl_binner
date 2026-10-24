"""Actual GPU CSV/clock/disk contracts; sampler doubles are not native GPU proof."""
import json,sys,tempfile,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e014_collect import binding
from e021_gpu_guard import parse_gpu,GPUPhaseGuard,GPU_BYTES
from e021_gpu_phase import admission,SECONDS,STOP_SECONDS
from e021_gpu_arm import service_content
from e021_gpu_cloud import configuration_commands
from e021_gpu_initial import populate_plan

class GPUOperations(unittest.TestCase):
    def test_actual_csv_parser_hardware_and_counter_refusal(self):
        d=parse_gpu('GPU-known, Tesla T4, 15360, 12\n');self.assertEqual(d['used_bytes'],12*1024**2)
        for text in ['GPU-a, A100, 40960, 0','GPU-a, Tesla T4, N/A, 0','GPU-a, Tesla T4, 100, 0','GPU-a, Tesla T4, 15360, 16000','GPU-a, Tesla T4, 15360, 0\nGPU-b, Tesla T4, 15360, 0']:
            with self.assertRaises(ValueError):parse_gpu(text)
    def test_real_guard_clock_and_gpu_error_stop_parent(self):
        with tempfile.TemporaryDirectory()as tmp:
            d=parse_gpu('GPU-known, Tesla T4, 15360, 0');calls=[]
            def sampler():
                calls.append(1);return d if len(calls)==1 else d|dict(used_bytes=GPU_BYTES+1)
            with self.assertRaisesRegex(TimeoutError,'GPU resource guard failed.*14 GiB'):
                with GPUPhaseGuard(tmp,2,reserve_bytes=0,sampler=sampler,interval=.01):time.sleep(1)
            self.assertEqual(len(list((Path(tmp)/'logs').glob('gpu-memory-*.jsonl'))),1)
            with self.assertRaisesRegex(TimeoutError,'clock exhausted'):
                with GPUPhaseGuard(tmp,.03,reserve_bytes=0,sampler=lambda:d,interval=.01):time.sleep(.3)
    def test_driver_wait_does_not_claim_gpu_until_same_boot_readiness(self):
        with tempfile.TemporaryDirectory()as tmp:
            r=Path(tmp);value=parse_gpu('GPU-known, Tesla T4, 15360, 0');calls=[]
            def sampler():calls.append(1);return value
            with GPUPhaseGuard(tmp,2,reserve_bytes=0,sampler=sampler,interval=.01,wait_for_ready=True,boot_id='current-boot')as guard:
                time.sleep(.03);self.assertFalse(calls);self.assertFalse((r/'logs/gpu-guard-live.json').exists())
                (r/'gpu-ready.json').write_text(json.dumps(dict(boot_id='current-boot',gpu_uuid='GPU-known')))
                time.sleep(.04);self.assertTrue(calls);self.assertEqual(json.loads((r/'logs/gpu-guard-live.json').read_text())['status'],'LIVE_NATIVE_TELEMETRY')
            with self.assertRaisesRegex(ValueError,'boot/identity'):
                with GPUPhaseGuard(tmp,2,reserve_bytes=0,sampler=sampler,wait_for_ready=True,boot_id='old-boot'):pass

    def test_actual_plan_preserves_input_axes_and_changes_only_runtime_worker_device(self):
        p=Path(__file__).absolute().parents[1]/'experiments/E021-frozen-sequence-hybrid/native-plan-template.json'
        plan=populate_plan(p,Path('/srv/research'),Path('/srv/job'))
        self.assertEqual(plan['extract_device'],'cuda');self.assertEqual(plan['worker'],'/srv/research/scripts/e021_gpu_worker.py')
        self.assertEqual(list(plan['units']),['E009-hybrid','oral-hybrid']);self.assertEqual(plan['threads'],4)
        self.assertTrue(all(u['bank_reuse_from']is None for u in plan['units'].values()))

    def test_exact_cloud_commands_never_provision_or_weaken_security(self):
        commands=configuration_commands();text=json.dumps(commands)
        self.assertIn('173700s',text);self.assertIn('n1-standard-8',text);self.assertIn('--accelerator-count=1',text)
        for forbidden in ['create','disks','services','iam','shielded','billing','reserve']:
            self.assertNotIn(forbidden,text)

    def test_actual_parent_unit_has_fixed_cpu_ram_and_original_clock(self):
        text=service_content(Path('/srv/repo'),Path('/srv/job'),'researcher',Path('/srv/job/config.json'),172000)
        for value in ['e021_gpu_phase.py','RuntimeMaxSec=172000','CPUAffinity=0 1 2 3','MemoryMax=26000000000','KillMode=control-group']:
            self.assertIn(value,text)
        with self.assertRaises(ValueError):service_content('/srv/repo','/srv/job','researcher','/srv/config',172801)

    def test_exact_45_dollar_48_hour_gpu_release_and_original_retention(self):
        self.assertEqual((SECONDS,STOP_SECONDS),(48*3600,48*3600+900))
        with tempfile.TemporaryDirectory()as tmp:
            p=Path(tmp)/'config.json';p.write_text('{}');start=1792846800
            cfg=dict(vm_start_epoch=start,_path=str(p),storage_authorization_sha256='storage')
            gates=['credit_gate_passed','pending_usage_accounted','native_gates_passed','watchdog_verified','existing_VM_only','full_axes_verified','frozen_extraction_runtime_passed','full_scale_RAM_passed','native_throughput_and_return_admitted','local_review_headroom_passed','GPU_credit_coverage_passed','GPU_runtime_and_numerics_passed','storage_cleanup_review_passed','GPU_guard_verified']
            release={k:True for k in gates};release.update(config=binding(p),provider_STOP_seconds=STOP_SECONDS,ceiling_USD=45,estimated_incremental_gross_USD=39.23,storage_authorization_sha256='storage',compressed_export_GiB=2,storage_retention_extended=False,covered_costs=['compute','gpu','disk','storage','network','operations'],credit_valid_until_epoch=1800000000,storage_valid_until_epoch=1793142000)
            admission(cfg,release,start+10)
            for key in gates:
                with self.assertRaises(ValueError):admission(cfg,release|{key:False},start+10)
            for change in [dict(estimated_incremental_gross_USD=46),dict(storage_valid_until_epoch=1793142001),dict(storage_retention_extended=True)]:
                with self.assertRaises(ValueError):admission(cfg,release|change,start+10)
            with self.assertRaises(ValueError):admission(cfg|dict(vm_start_epoch=1793142000-STOP_SECONDS),release,1793142000-STOP_SECONDS+1)

if __name__=='__main__':unittest.main()
