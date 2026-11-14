"""Current optional-link configuration, rendering and restore-selection contracts.

No cloud/browser/scientific community actions run here. Operational transport is
fixture data; actual tensor/graph/fallback/export paths belong to e036_tiny.py.
"""
import copy,json,sys,tempfile,time,unittest
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import e036_phase as phase
import e036_launch as launch
from e036_restore import needed
from e024_coverage import binding


class OptionalExecution(unittest.TestCase):
    def values(self,folder):
        """Use the real producer and current complete envelope, not an abbreviated schema."""
        f=dict(real_money_authorized=False,coverage_status='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY',ceiling_USD=20,
               estimated_complete_gross_USD=17.,credit_checked_epoch=time.time(),checked_epoch=time.time(),
               storage_valid_until_epoch=1795215600,credit_valid_until_epoch=1799708400,
               Welcome_credit_remaining_DKK=1571.83,DKK_per_USD=6.71225,reserve_USD=35.,
               native_pysam_path='/fixed/pysam.whl',pysam_binding=dict(bytes=1,sha256='b'*64))
        ident=dict(root='/srv/dl_binner/experiments/e036/optional-fixture',repo='/srv/dl_binner/repo',source='a'*40,
                   vm_start_epoch=time.time(),service_name='e036-optional-fixture',user='fixture',archive_prefix='gs://dl-binner-archive-167650584170/e036/fixture/',phase='optional-fixture',setup_timer='e036-setup-fixture')
        wheel=ROOT/'artifacts/e035-confidence-taxonomy/preparation/qualified-package/dist/dl_binner-0.1.0.dev11-py3-none-any.whl'
        if not wheel.is_file():self.skipTest('Historical owned wheel unavailable; this is a research-adapter contract')
        f.update(wheel_path=str(wheel),wheel_binding=binding(wheel))
        packet=Path(folder)/'fixture.bundle';packet.write_bytes(b'fixture exact bytes, not a runnable Git source')
        f['source_transport']=dict(kind='private_exact_Git_bundle',path=str(packet),bundle=binding(packet),source='a'*40,base='b'*40)
        return ident,f

    def test_complete_producer_and_all_nested_programs_compile(self):
        with tempfile.TemporaryDirectory()as folder:
            i,f=self.values(folder);launch.preflight(i,f,check_source=False)
            c=launch.config_value(i,f);self.assertTrue(phase.validate_config(c))
            self.assertIn('64*1024**3',launch.render_host(i,f,dict(name='e036-task-fixture')))
            self.assertIn('e036_phase.py', (ROOT/'scripts/e036_arm.py').read_text())

    def test_missing_unknown_expired_and_uncovered_inputs_refuse(self):
        with tempfile.TemporaryDirectory()as folder:
            i,f=self.values(folder);c=launch.config_value(i,f)
            bad=copy.deepcopy(c);bad.pop('initial_filesystem_device')
            with self.assertRaises(ValueError):phase.validate_config(bad)
            bad=copy.deepcopy(c);bad['unexpected']=True
            with self.assertRaises(ValueError):phase.validate_config(bad)
            bad=copy.deepcopy(c);bad['financial']['credit_checked_epoch']-=7201
            with self.assertRaises(ValueError):phase.validate_config(bad)
            bad=copy.deepcopy(c);bad['financial']['Welcome_credit_remaining_DKK']=1.
            with self.assertRaises(ValueError):phase.validate_config(bad)
            bad=copy.deepcopy(c);bad['financial']['storage_valid_until_epoch']=time.time()-1
            with self.assertRaises(ValueError):phase.validate_config(bad)
            bad=copy.deepcopy(c);bad['financial']['real_money_authorized']=True
            with self.assertRaises(ValueError):phase.validate_config(bad)

    def test_actual_compact_consumer_companions_and_no_BAM(self):
        for c in ['E009','oral']:
            for name in ['graph.npz','graph.json','decisions.json','completed.json']:
                self.assertTrue(needed('work/'+c+'/pooled/'+name,'pooled'))
        self.assertFalse(needed('work/oral/sample-00/ledger.npz','pooled'))
        self.assertTrue(needed('work/oral-noGLM/select/result/post-partition.json','baseline'))
        self.assertFalse(needed('work/E009-GLM/select/result/post-partition.json','baseline'))
        self.assertFalse(needed('work/oral/bank.json','measurements'))
        self.assertTrue(needed('work/E009/intervals.npz','measurements'))

if __name__=='__main__':unittest.main()
