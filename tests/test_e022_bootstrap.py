"""Pure operational scope/path contracts; no VM, install or scientific invocation."""
from datetime import datetime,timezone
from pathlib import Path
import sys,time,unittest
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e022_bootstrap import plan_for,admit

class Bootstrap(unittest.TestCase):
    def fixture(self):
        now=time.time();i=dict(root='/srv/dl_binner/experiments/e022/test',repo='/repo',source='a'*40,archive_prefix='gs://dl-binner-archive-167650584170/e022/test',ceiling_USD=2,provider_STOP_seconds=8100,storage_retention_extended=False,vm_start_epoch=now-10)
        f=dict(UTC=datetime.fromtimestamp(now-20,timezone.utc).isoformat(),coverage_status='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY',real_money_authorized=False,new_incremental_gross_ceiling_USD=2,credit_valid_until_epoch=now+10000,storage_valid_until_epoch=now+10000)
        return i,f,now
    def test_exact_native_inputs_and_only_new_output_paths(self):
        i,_,_=self.fixture();p,r=plan_for(i,Path(__file__).absolute().parents[1]);self.assertEqual(p['unit'],r['units']['E009-relational']);self.assertEqual(p['threads'],4);self.assertEqual(p['work'],i['root']+'/work');self.assertNotIn('truth',str(p))
    def test_live_finance_original_clock_and_scope_refusals(self):
        i,f,now=self.fixture();admit(i,f,now)
        for field,v in [('ceiling_USD',3),('provider_STOP_seconds',9000),('storage_retention_extended',True),('vm_start_epoch',now-1801),('archive_prefix','gs://another-bucket/test')]:
            bad=dict(i);bad[field]=v
            with self.assertRaises((ValueError,TimeoutError)):admit(bad,f,now)
        with self.assertRaises(TimeoutError):admit(i,dict(f,UTC=datetime.fromtimestamp(now-7201,timezone.utc).isoformat()),now)
        with self.assertRaises(ValueError):admit(i,dict(f,real_money_authorized=True),now)

if __name__=='__main__':unittest.main()
