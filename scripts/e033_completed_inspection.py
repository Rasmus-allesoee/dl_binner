#!/usr/bin/env python3
"""Admit the completed repaired E033 return before frozen local diagnostics.

This stdlib reader checks independently captured provider/credit evidence, every
generation/member proof, actual native exits, immutable stage seals and source/
runtime/learning metadata. It neither starts cloud work nor computes a score.
Tensor/vector checks and the unchanged evaluators run separately in the installed
candidate prefix. Original failed journals and source freezes are read-only.
"""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e027_inspection import seal_from_inventory
from e033_control import STAGES,UNITS

EXP=ROOT/'experiments/E033-multiscale-bam'
PHASE='resume-20261105T023814Z-941ede3'
SOURCE='941ede36d29b76c5f542e56295236d5100447ca1'


def read(path):
    """Read a closed regular JSON artifact, refusing symlink substitution."""
    p=Path(path)
    if p.is_symlink() or not p.is_file():raise ValueError('Missing regular inspection record: '+str(p))
    return json.loads(p.read_text())


def require(value,message):
    """Refuse an incomplete contract before exposing any diagnostic admission."""
    if not value:raise ValueError(message)


def exits(completion):
    """Require each actual setup, scientific, input-after and collection exit."""
    expected=['original-inputs-before','repaired-package-install','repaired-complete-runtime',
        'repaired-plan','actual-progress-64-and-learning','actual-repaired-serial-tiny',
        'serial-six-fit-three-mode','original-inputs-after']+['collect-'+u for u in UNITS]
    require([s['stage'] for s in completion['stages']]==expected,'Actual native stage sequence differs')
    require(all(s['resources']['exit_code']==0 and s['resources']['stop_reason'] is None
        for s in completion['stages']),'Actual native exit failed or missing')
    return {s['stage']:s['resources'] for s in completion['stages']}


def archive(base,unit,expected):
    """Bind the full stream proof to its exact delivery generation and inventory."""
    b=Path(base);p=read(b/(unit+'-verification.json'));inv=read(b/'receipts'/unit/'inventory.json')
    require(p['every_member_verified'] and p['independent_server_MD5_verified']
        and p['archive']==expected['binding'] and p['generation']==expected['generation']
        and p['physical_members']==len(inv['members'])+1 and p['aliases']==len(inv['aliases'])
        and not inv['omitted_retained_on_disk'] and p['no_complete_compressed_local_duplicate'],
        'Full archive/member/alias/generation contract differs: '+unit)
    return p,inv


def inspect(base,output):
    """Validate the completed science and closed delivery without learning or truth."""
    b=Path(base);controls=read(b/'control-state.json');provider=controls['state']
    c=read(b/'receipts/completion.json');tail=read(b/'receipts/closed-delivery-tail.json')
    finance=read(b/'finance/download-admission.json');summary=read(b/'all-streams-verified.json')
    require(provider['status']=='TERMINATED' and provider['machineType'].endswith('/e2-standard-8')
        and not provider.get('guestAccelerators') and sorted(int(x['diskSizeGb']) for x in provider['disks'])==[30,100,300],
        'Independent stopped resources differ')
    guest=[json.loads(x['value']) for x in controls['guest'] if x['namespace']=='e033-candidate' and x['key']=='status']
    require(len(guest)==1 and guest[0]['root']==c['root'] and c['root'].endswith('/'+PHASE)
        and guest[0]['status']==c['status']=='SUCCESS' and guest[0]['science_completed']
        and guest[0]['completion_delivery_verified'] and c['science_completed'] and c['collection_readback_verified']
        and c['source']==SOURCE,'Actual completion/root/source differs')
    stage_exits=exits(c)
    require(finance['status']=='PASS' and finance['credit_only'] and finance['original_ceiling_USD']==20
        and finance['remaining_original_20_covers'] and not finance['new_compute']
        and summary['status']=='PASS' and summary['shared_physical_stage_bytes']<=3*1024**3,
        'Credit/export/staging admission missing')
    require(tail['status']=='PASS' and tail['science_completed']
        and tail['completion']['binding']==binding(b/'receipts/completion.json'),'Closed completion delivery differs')
    closeproof,closeinv=archive(b,'closed-delivery',c['closed_delivery_archive'])
    require(c['closed_delivery_inventory']['binding']==binding(b/'receipts/closed-delivery/inventory.json'),
        'Closed post-collector inventory differs')
    e=b/'verified-E009-noGLM/evidence';cfg=read(e/'config.json');plan=read(e/'science-plan.json')
    release=read(e/'release.json');live=read(e/'logs/watchdog-live-before-release.json')
    stopped=read(b/'receipts/watchdog-exit.json');started=read(e/'started.json');supervision=read(e/'logs/supervision.json')
    require(stopped['shutdown'] and stopped['decision']=='workflow exited' and stopped['observed_process'] is None
        and stopped['boot_id']==live['boot_id']==supervision['boot_id']
        and stopped['expected_process']==live['expected_process']==live['observed_process']==started['identity']==supervision['process']
        and live['decision']=='workflow alive' and supervision['native_normal_exit_and_crash_tests_passed'],
        'Matching current-boot/process exit evidence missing')
    require(cfg['source_commit']==cfg['operations_source']==SOURCE and cfg['vm_start_epoch']==1793843252.334
        and cfg['review_deadline_epoch']==1793951252.334 and cfg['provider_deadline_epoch']==1793951872.01
        and c['finished_epoch']<cfg['review_deadline_epoch']<cfg['provider_deadline_epoch']<1794351600
        and cfg['initial_filesystem_used_bytes']==24576 and cfg['limits']==read(EXP/'repair-lock.json')['limits']
        and release['config']==binding(e/'config.json') and release['plan']==binding(e/'science-plan.json')
        and release['provider_STOP_verified'] and release['watchdog_verified'],'Original clocks/limits/release differ')
    lock=read(EXP/'repair-lock.json');candidate=read(EXP/'repair-candidate-lock.json')
    require(c['repair_lock']==binding(EXP/'repair-lock.json') and c['candidate_lock']==binding(EXP/'repair-candidate-lock.json'),
        'Completion repair/source artifact differs')
    for name in ['source-lock.json','candidate-lock.json','repair-lock.json','repair-candidate-lock.json','protocol.json']:
        require(binding(e/'repair-source'/name)==binding(EXP/name),'Returned freeze differs: '+name)
    effective=dict(read(EXP/'source-lock.json')['files']);effective.update({n:v['after'] for n,v in lock['source_overrides'].items()});effective.update(lock['extra_files'])
    for name,wanted in effective.items():
        raw=subprocess.check_output(['git','show',SOURCE+':'+name],cwd=ROOT)
        require(dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())==wanted,'Executed source differs: '+name)
    runtime=read(e/'gates/runtime.json');reuse=read(e/'gates/reuse.json')
    require(runtime['status']=='PASS_COMPLETE_READONLY_BASE_AND_NEW_OWNED_PACKAGE'
        and runtime['package_files']==candidate['package_files'] and reuse['status']=='PASS_VERIFIED_REUSE'
        and len(reuse['measurements'])==46 and reuse['barrier_reused'] and not reuse['BAM_measurement_sort_state_restore_replayed'],
        'Native complete runtime or verified measurement/barrier reuse differs')
    require(read(e/'gates/inputs-before.json')==read(e/'gates/inputs-after.json'),'Original consumed inputs changed')
    require(read(e/'gates/tiny/completed.json')['status']=='PASS','Repaired native tiny workflow incomplete')
    closed=b/'verified-closed-delivery/work/logs'
    for stage,resources in stage_exits.items():
        require(read(closed/(stage+'.exit.json'))==resources,'Post-collector actual exit differs: '+stage)
    history=b/'receipts/filesystem.jsonl';require(binding(history)==c['filesystem']['history'],'Closed full filesystem history differs')
    count=0;minsource=mintask=None;maxused=0
    for line in history.open():
        row=json.loads(line);count+=1
        minsource=row['source_free'] if minsource is None else min(minsource,row['source_free'])
        mintask=row['task_free'] if mintask is None else min(mintask,row['task_free']);maxused=max(maxused,row['task_used'])
    fs=c['filesystem'];require(count==fs['samples'] and minsource==fs['minimum_source_free_bytes']
        and mintask==fs['minimum_task_free_bytes'] and maxused==fs['maximum_task_used_bytes']
        and min(minsource,mintask)>=25*1024**3 and maxused-24576==fs['maximum_original_baseline_growth_bytes']<=60*1024**3
        and fs['monitor_error'] is None,'Full resource history/old task baseline does not close')
    scheduled=(closed/'serial-six-fit-three-mode.log').read_text()
    jobs=re.findall(r'^Execute (\d+) jobs',scheduled,re.M)
    require(len(jobs)==40 and set(jobs)=={'1'} and '40 of 40 steps (100%) done' in scheduled,
        'Actual serial scientific/final scheduling incomplete')
    results={};axes=read(EXP/'reuse-lock.json')['axes']
    for u in UNITS:
        item=next(x for x in c['collections'] if x['label']==u);proof,inv=archive(b,u,item['delivered']['e033-evidence.tar.gz'])
        at=b/('verified-'+u)/'work';require(item['inventory']==binding(b/'receipts'/u/'inventory.json'),'Mode inventory differs')
        seals={n:seal_from_inventory(read(at/n/'done.json'),n,inv) for n in STAGES}
        checkpoints={}
        for role in ['teacher','student']:
            q=read(at/role/'result/checkpoint.json');init=read(at/role/'result/initial-state.json')
            require(q['policy']==candidate['learning_policy'] and q['stage']==role and q['config']['seed']==11
                and q['config']['batch_size']==256 and q['engineering_epochs'] is None and q['threads']==4 and q['loader_workers']==0
                and len(q['history'])==20 and [x['epoch'] for x in q['history']]==list(range(1,21))
                and q['samples']==axes[u]['samples'] and q['original_Adam_restored'] and not q['truth_accessed']
                and q['initial_state']==init['state'] and q['initial_state']['anchor']==q['final_state']['anchor']
                and q['sha256']==inv['all_work_members'][role+'/result/checkpoint.pt']['sha256']
                and q['added_updates']==20*((axes[u]['eligible']+255)//256)
                and all(h['parents_seen']==axes[u]['eligible'] and not any(z['catastrophic_collapse'] for x in h['geometry'].values() for z in x.values()) for h in q['history']),
                'Full frozen learning/restoration/exposure differs: '+u+'/'+role)
            if role=='student':require(q['initial_state']==checkpoints['teacher']['final_state']
                and q['teacher_checkpoint']==inv['all_work_members']['teacher/result/checkpoint.pt'], 'Student does not continue own teacher')
            emb=read(at/(role+'-embed')/'embeddings.json');graph=read(at/(role+'-graph/result/graph.json'))
            require(emb['reload_exact'] and emb['checkpoint_sha256']==q['sha256']
                and graph['embedding_sha256']==inv['all_work_members'][role+'-embed/embeddings.npz']['sha256']
                and graph['audit']['mean_tie_aware_recall']>=graph['audit']['threshold']
                and not read(at/(role+'-graph/result/completed.json'))['old_graph_reused'], 'Native reload/neighbor contract differs')
            checkpoints[role]=q
        result=read(at/'select/result/completed.json');audit=read(at/'audit/proof.json')
        require(result['status']=='SUCCESS' and result['rows']==audit['rows']==axes[u]['rows']
            and result['bp']==audit['bp']==axes[u]['bp'] and result['samples']==axes[u]['samples']
            and audit['status']=='PASS' and audit['complete_DNA'] and not audit['new_neighbors_or_fit']
            and not result['truth_accessed'],'Complete new selection/DNA audit differs')
        results[u]=dict(axis=axes[u],seals=seals,checkpoint_receipts={r:binding(at/r/'result/checkpoint.json') for r in checkpoints},
            teacher_seconds=checkpoints['teacher']['wall_seconds'],student_seconds=checkpoints['student']['wall_seconds'],archive=proof['archive'])
        admission=dict(provider_status='TERMINATED',archive_and_every_member_verified=True,cost_and_retention_admitted=True,
            workflow_completed=True,exact_source_schedule_axes_verified=True,native_source_runtime_information_policy_verified=True,
            candidate_lock=binding(EXP/'repair-candidate-lock.json'),repair_lock=binding(EXP/'repair-lock.json'),
            phase=PHASE,source=SOURCE,diagnostic_scores_not_yet_admitted=True)
        write(b/'receipts'/u/'admission.json',admission)
    value=dict(status='PASS_COMPLETED_SCIENCE_AND_DELIVERY_BEFORE_DIAGNOSTICS',phase=PHASE,source=SOURCE,
        scientific_fits=6,scientific_stage_seals=39,barrier_reused=True,all_twenty_measurements_reused=True,
        stage_exits=stage_exits,units=results,filesystem=fs,matching_watchdog_shutdown=True,
        source_policy_unchanged=True,original_Mac_portability_tolerance_unchanged=True,baselines_rescored=False,
        active_retention_end='2026-11-11T00:00:00+01:00',approved_tail_end='2026-11-18T00:00:00+01:00')
    write(output,value);return value


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();v=inspect(a.base,a.output);print(v['status'],v['scientific_fits'],v['scientific_stage_seals'])
