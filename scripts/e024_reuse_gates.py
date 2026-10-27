#!/usr/bin/env python3
"""Admit a transport-only E024 recovery using byte-verified passed contracts.

Preserve the failed phase/archive and its accepted input-verification directory.
This helper never starts compute or acquisition. It verifies the old archive,
exact unchanged plan/input bytes, fresh source/runtime and the changed segment
reader, and exercises a completed tiny DAG as a no-op. Full-community alignments,
new features and scores are absent from this admission. The caller must arm a
new current-boot/process watcher and externally publish a fresh release.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import time

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'src')]
from e024_coverage import binding,write
from e024_gates import freeze
from e024_control import verify_seal
from e023_collect import verify
from e023_gates import workflow_probe
from e009_owner import supervisor


def run(config, previous):
    """Verify and explicitly reuse immutable gates; test only the changed transport."""
    cfg=json.loads(Path(config).read_text());root=Path(cfg['root']);old=Path(previous)
    p=json.loads(Path(cfg['plan']).read_text());prior=json.loads((old/'config.json').read_text())
    if not old.is_relative_to('/srv/dl_binner/experiments/e024') or old==root:
        raise ValueError('Distinct retained E024 attempt required')
    if binding(cfg['plan'])!=binding(prior['plan']) or p['work']!=prior['work']:
        raise ValueError('Original accepted plan/work cannot change for transport recovery')
    inv=verify(old/'collection/e024-evidence.tar.gz')
    completion=json.loads((old/'gates/completion.json').read_text())
    if completion['status']!='PASS' or completion['config']!=binding(old/'config.json'):
        raise ValueError('Old complete native admission missing')
    for name in ['completion.json','readers.json','runtime.json','source.json']:
        if binding(old/'gates'/name)!=inv['members']['evidence/gates/'+name]:
            raise ValueError('Retained gate differs from verified failure archive')
    old_done=json.loads((old/'completion.json').read_text())
    if old_done['science_completed'] or not old_done['collection_readback_verified']:
        raise ValueError('This recovery is only for the admitted pre-data transport failure')
    sealed=verify_seal(Path(p['work'])/'verified')
    if sealed['plan']!=binding(cfg['plan']):raise ValueError('Accepted input plan changed')
    for key,path in dict(p['inputs'],reference=p['reference'],mapper=p['mapper'],samtools=p['samtools']).items():
        if binding(path)!=sealed['inputs'][key]:raise ValueError('Retained input drift')
    out=root/'gates';out.mkdir(exist_ok=False)
    write(out/'source.json',freeze())
    for name in ['readers.json']:
        shutil.copyfile(old/'gates'/name,out/name)
    transport=old/'gates/private-BAM-smoke';(out/'private-BAM-smoke').mkdir()
    shutil.copyfile(transport/'receipt.json',out/'private-BAM-smoke/receipt.json')
    for name in ['e009-bam-integrity.json','cleanup-review.json']:
        shutil.copyfile(old/'logs'/name,root/'logs'/name)
    reused=dict(previous=str(old),archive=binding(old/'collection/e024-evidence.tar.gz'),
                prior_config=binding(old/'config.json'),prior_gates=binding(old/'gates/completion.json'),
                prior_science_failed=True,accepted_input_verification_repeated=False,
                prior_full_readers=binding(old/'gates/readers.json'),
                prior_24_native_contracts='PASS, unchanged code paths except new explicitly tested segment transport',
                original_E009_BAM_full_hash_audit='Retained prior-boot byte proof, no repeat',
                private_BAM_transport='Retained passed real GCS byte/readback/decode; sidecar code unchanged')
    write(out/'verified-reuse.json',reused)
    sup=supervisor();env=sup.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'gate-native-cache'))
    stages=[]
    def command(label,argv):
        remaining=cfg['vm_start_epoch']+3600-time.time()
        if remaining<60:raise TimeoutError('Original setup clock exhausted')
        result=sup.supervise(argv,out/(label+'.log'),remaining,26_000_000_000,env,sample_root=os.getpid())
        stages.append(dict(stage=label,resources=result))
    command('workflow-origin',[p['workflow_python'],'-I','-B','-c',workflow_probe('3.12.10','9.16.3')])
    lock=json.loads((ROOT/'experiments/E023-adaptive-density-bins/reuse-lock.json').read_text())
    command('accepted-numerical',[p['python'],'-I','-B',str(ROOT/'scripts/e023_runtime.py'),
        '--reference',lock['runtime_reference'],'--output',str(out/'runtime.json')])
    stages.append(dict(stage='full-retained-readers',resources=dict(exit_code=0,stop_reason=None,
        scope='VERIFIED_REUSE, not repeated',reference=binding(old/'gates/readers.json'))))
    code=('import sys,unittest;sys.path[:0]='+repr([str(ROOT/'scripts'),str(ROOT/'src'),str(ROOT/'tests')])+';'
          'r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('
          '"test_e024_coverage.Coverage.test_actual_public_segment_transport_without_aggregate_GET"));sys.exit(not r.wasSuccessful())')
    compile(code,'exact-current-segment-test','exec')
    command('actual-native-contracts',[p['python'],'-I','-B','-c',code])
    command('serial-tiny-DAG',[p['python'],'-I','-B',str(ROOT/'scripts/e024_control.py'),
        '--plan',str(old/'gates/tiny-DAG/plan.json'),'--engineering','--workflow'])
    if 'Nothing to be done' not in (out/'serial-tiny-DAG.log').read_text():
        raise ValueError('Completed tiny science was scheduled instead of verified no-op')
    write(out/'completion.json',dict(status='PASS',config=binding(config),stages=stages,
        original_start_epoch=cfg['vm_start_epoch'],finished_epoch=time.time(),full_science_started=False,
        source=freeze(),verified_reuse=reused,changed_native_segment_contract_passed=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True);parser.add_argument('--previous',type=Path,required=True)
    args=parser.parse_args();run(args.config,args.previous)
