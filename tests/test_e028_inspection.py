"""Failure-aware stopped-return contracts, independent of ignored research data."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e028_inspection import recall_contract, shutdown_contract, summarize_stages, matched_queries, feature_metadata_contract, SOURCE
from e024_coverage import binding


def failure():
    """Construct distinct failed-science/successful-delivery evidence."""
    proc=dict(pid=12,start_ticks=50,command_sha256='command')
    provider=dict(status='TERMINATED',machineType='/e2-standard-8',disks=[dict(diskSizeGb='30'),dict(diskSizeGb='300')],
        lastStartTimestamp='2026-10-31T20:00:00+00:00',lastStopTimestamp='2026-10-31T20:10:00+00:00')
    names=['workflow','collect']+[p+n for n in ['e028-evidence.tar.gz','e028-evidence.tar.gz.sha256','collection.json','collection-disk.jsonl','terminal-disk.json'] for p in ['upload-','readback-']]
    completion=dict(status='FAILED',science_completed=False,collection_readback_verified=True,source_commit=SOURCE,
        scientific_fits_completed=99,stages=[dict(name=n,resources=dict(exit_code=int(n=='workflow')))for n in names])
    bound=dict(bytes=10,sha256='completion')
    guest=[dict(namespace='e028-candidate',key='status',value=json.dumps(dict(status='FAILED',science_completed=False,completion=bound)))]
    watchdog=dict(shutdown=True,decision='workflow exited',boot_id='boot',expected_process=proc)
    started=dict(identity=proc);live=dict(shutdown=False,decision='workflow alive',boot_id='boot',expected_process=proc,observed_process=proc)
    return [provider,guest,completion,bound,watchdog,started,live,dict(measured_allocation_seconds=600,cost_and_retention_admitted=True)]


class StoppedReturn(unittest.TestCase):
    def test_shutdown_and_fit_counter_cannot_promote_failure(self):
        result=shutdown_contract(*failure())
        self.assertFalse(result['science_completed']);self.assertEqual(result['science_status'],'FAILED')

    def test_claimed_success_with_failed_workflow_is_refused(self):
        args=failure();args[2]['status']='SUCCESS'
        with self.assertRaises(ValueError):shutdown_contract(*args)

    def test_stale_completion_or_wrong_process_is_refused(self):
        for which in ['completion','watchdog']:
            args=failure()
            if which=='completion':args[3]=dict(bytes=11,sha256='other')
            else:args[4]=dict(args[4],boot_id='other')
            with self.assertRaises(ValueError):shutdown_contract(*args)

    def test_populated_stratum_retains_its_failed_gate(self):
        audit=dict(status='FAILED_RECALL_GATE',overall=.75,strata=dict(short=1.,measured_zero_depth=.5),
            queries=[dict(id='a',recall=1.,strata=['short']),dict(id='b',recall=.5,strata=['measured_zero_depth'])])
        self.assertEqual(recall_contract(audit)['status'],'FAILED_RECALL_GATE')
        audit['status']='PASS'
        with self.assertRaises(ValueError):recall_contract(audit)

    def test_unsealed_extra_member_is_refused(self):
        with tempfile.TemporaryDirectory()as d:
            prefix='groups/E009-noGLM/teacher';p=Path(d)/'work'/prefix;p.mkdir(parents=True)
            b=dict(bytes=2,sha256='content');(p/'done.json').write_text(json.dumps(dict(status='PASS',files={'result.json':b})))
            inventory=dict(all_work_members={prefix+'/result.json':b,prefix+'/done.json':dict(bytes=1,sha256='seal')})
            self.assertEqual(summarize_stages(d,inventory)[prefix]['status'],'PASS')
            inventory['all_work_members'][prefix+'/unexpected.json']=b
            with self.assertRaises(ValueError):summarize_stages(d,inventory)

    def test_search_comparison_refuses_changed_cohort_and_reports_exact_drift(self):
        a=dict(status='PASS',overall=1.,strata={},calibration={'fixed':1},queries=[dict(id='a',row=0,recall=1.,strata=[],kth_exact=.5)])
        b=json.loads(json.dumps(a));b['queries'][0]['kth_exact']=.6
        self.assertFalse(matched_queries(a,b)['exact_kth_identical'])
        b['queries'][0]['id']='changed'
        with self.assertRaises(ValueError):matched_queries(a,b)

    def test_reordered_depth_columns_are_refused(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'features.npz';p.write_bytes(b'bound array bytes')
            wanted=binding(p);samples=['sample-'+str(i)for i in range(10)]
            p.with_suffix('.json').write_text(json.dumps(dict(kind='features',version=1,sha256=wanted['sha256'],ids_sha256='ids',samples=samples)))
            self.assertEqual(feature_metadata_contract(p,wanted,'ids',samples)['status'],'PASS_INDEPENDENT_LOCAL_SAMPLE_AND_ID_AXIS')
            with self.assertRaises(ValueError):feature_metadata_contract(p,wanted,'ids',samples[::-1])


if __name__=='__main__':unittest.main()
