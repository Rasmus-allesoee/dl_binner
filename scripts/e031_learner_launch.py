#!/usr/bin/env python3
"""Launch only the authorized fixed E031 learner with prospectively paired constructors.

Reuse the existing E2 and its single admitted task disk, without formatting,
provisioning or cleanup. Use the tested exact-source, held-parent, watcher and
atomic-release consumers. Small explicit rendering amendments select the new
paired plan and native full-schedule gate; all rendered programs are compiled
before the VM starts. Failures stop compute and preserve science/journals.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e021_portable_cloud import Cloud, CPU, CPU_ZONE
from e024_coverage import binding
from e031_control import freeze
from e031_launch import SSH, save, remote, source_code, host_code, release_code

MOUNT = '/srv/dl_binner/experiments/e031/bridge-20261102T130813Z-31962f8'
DISK = 'e031-bridge-scratch-20261102131010'
DISK_ID = '5531031824224302423'


def replace_once(code, before, after):
    """Refuse an unexpected base adapter instead of silently missing an amendment."""
    if code.count(before) != 1:
        raise ValueError('Prepared adapter amendment does not match exactly')
    return code.replace(before, after, 1)


def mount_code():
    """Mount only the existing positively named ext4 task disk; never format it."""
    return r'''import json,os,pathlib,subprocess
root=pathlib.Path(MOUNT);device=pathlib.Path('/dev/disk/by-id/google-'+DISK)
subprocess.run(['sudo','-n','udevadm','settle','--timeout=15'],check=True)
if not os.path.ismount('/srv/dl_binner') or not device.exists():raise ValueError('Original/task device missing; no provisioning fallback')
row=subprocess.check_output(['lsblk','-b','-dn','-o','TYPE,SIZE,FSTYPE',str(device)],text=True).strip().split()
if row!=['disk',str(40*1024**3),'ext4']:raise ValueError('Existing task disk identity/type differs; no formatting')
if not os.path.ismount(root):
 subprocess.run(['sudo','-n','mount','-o','nodev,nosuid',str(device),str(root)],check=True)
actual=subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(root)],text=True).strip()
if pathlib.Path(actual).resolve()!=device.resolve() or os.stat(root).st_dev==os.stat('/srv/dl_binner').st_dev:raise ValueError('Task mount/device differs')
for member in ['completion.json','collection/collection.json','work/used-inputs-after.json']:
 if not(root/member).is_file():raise ValueError('Preserve original bridge evidence; expected mount not present')
print('E031_EXISTING_TASK_MOUNT',json.dumps(dict(root=str(root),device=str(device),formatted=False,original_bridge_preserved=True)),flush=True)
'''.replace('pathlib.Path(MOUNT)', 'pathlib.Path('+repr(MOUNT)+')').replace("+DISK)", '+'+repr(DISK)+')')


def learner_host(ident, financial):
    """Select paired orchestration while preserving the existing held setup consumer."""
    code = host_code(ident, financial)
    before = "if ident.get('scratch'):\n if not os.path.ismount(root):raise ValueError('Admitted scratch mount missing')\nelse:root.mkdir(parents=True,exist_ok=False)"
    after = ("if not os.path.ismount("+repr(MOUNT)+"):raise ValueError('Existing admitted task mount missing')\n"
             "if root.parent!=pathlib.Path("+repr(MOUNT)+"):raise ValueError('Fresh learner must use only the admitted task filesystem')\n"
             "root.mkdir(parents=True,exist_ok=False)")
    code = replace_once(code, before, after)
    code = replace_once(code, 'baseline.free<33*1024**3', 'baseline.free<34*1024**3')
    code = replace_once(code, "E031-bootstrap-preserving-learning/bridge-plan.json", "E031-bootstrap-preserving-learning/paired-plan.json")
    if financial.get('bridge_review_controls'):
        import base64, gzip
        files={}
        for name, entry in financial['bridge_review_controls'].items():
            path=Path(entry['path'])
            if binding(path)!=entry['binding']:
                raise ValueError('Bounded bridge review control differs')
            files[name]=base64.b64encode(path.read_bytes()).decode()
        packet=base64.b64encode(gzip.compress(json.dumps(files).encode(),mtime=0)).decode()
        insert=("\nimport gzip\n"
                "controls=json.loads(gzip.decompress(base64.b64decode("+repr(packet)+",validate=True)))\n"
                "for name,value in controls.items():\n"
                " if '/' in name or name.startswith('.'):raise ValueError('Unsafe bridge control name')\n"
                " raw=base64.b64decode(value,validate=True)\n"
                " if dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())!=financial['bridge_review_controls'][name]['binding']:raise ValueError('Bridge review control transport differs')\n"
                " with (root/'payload'/name).open('xb') as handle:handle.write(raw)\n")
        code=replace_once(code,"publish(cfg,root/'config.json')",
            "cfg['bridge_review']=True\n"+insert+"publish(cfg,root/'config.json')")
    return code


def learner_release(ident, provider):
    """Bind actual complete native throughput, both constructors and the original clock."""
    code = release_code(ident, provider)
    code = replace_once(code,
        "if time.time()+10800+900>ident['vm_start_epoch']+cfg['limits']['seconds']:raise TimeoutError('Complete bridge forecast no longer fits original clock')",
        "schedule=json.loads((root/'gates/complete-schedule.json').read_text())\n"
        "if schedule['status']!='PASS' or time.time()+schedule['forecast_remaining_seconds']+900>ident['vm_start_epoch']+cfg['limits']['seconds']:raise TimeoutError('Complete paired learning schedule cannot fit original clock')")
    code = replace_once(code, 'shutil.disk_usage(root).free<32*1024**3', 'shutil.disk_usage(root).free<34*1024**3')
    code = replace_once(code, "paths=[root/'gates/completion.json'", "paths=[root/'gates/complete-schedule.json',root/'gates/kernel-probe.json',root/'gates/completion.json'")
    return code


def start(out):
    """One existing-node start after complete local credit/source/byte admission."""
    out = Path(out).absolute(); out.mkdir(parents=True, exist_ok=True)
    if (out/'identity.json').exists():
        raise ValueError('Attempt exists; original clock cannot be reset')
    f = json.loads((out/'financial-gate.json').read_text()); freeze()
    schema = json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/paired-plan.json').read_text())
    limits = schema['limits']
    if (f['coverage_status'] != 'PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY'
            or f['real_money_authorized'] is not False or f['new_incremental_gross_ceiling_USD'] != limits['ceiling_USD']
            or not 0 <= f['estimated_complete_gross_USD'] <= limits['ceiling_USD']
            or time.time()-f['checked_epoch'] > 7200
            or time.time()+limits['provider_STOP_seconds'] >= f['storage_valid_until_epoch']):
        raise ValueError('Fresh complete credit-only/retention admission failed')
    for name, wanted in f['local_gate_files'].items():
        if binding(name) != wanted:
            raise ValueError('Local gate bytes changed: '+name)
    if subprocess.check_output(['git','status','--porcelain'], cwd=ROOT, text=True).strip():
        raise ValueError('Exact clean source required')
    source = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    if f['source_transport']['source'] != source:
        raise ValueError('Private exact source differs')
    c = Cloud(out/'control-plane'); before = c.state(); c.put('provider-before.json', before)
    if (before['status'] != 'TERMINATED' or not before['machineType'].endswith('/e2-standard-8')
            or before.get('guestAccelerators') or not before['shieldedInstanceConfig']['enableSecureBoot']
            or sorted(int(d['diskSizeGb']) for d in before['disks']) != [30,40,300]
            or any(d['autoDelete'] for d in before['disks'])):
        raise ValueError('Existing stopped CPU/disks/security differ')
    matches = [d for d in before['disks'] if d['deviceName'] == DISK]
    if len(matches) != 1 or matches[0]['boot']:
        raise ValueError('Single admitted task attachment differs')
    disk = c.call(['compute','disks','describe',DISK], CPU_ZONE); c.put('existing-task-disk.json', disk)
    if disk['id'] != DISK_ID or int(disk['sizeGb']) != 40 or not disk['type'].endswith('/pd-balanced'):
        raise ValueError('Approved task disk resource identity differs')
    phase = 'learning-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+source[:7]
    ident = dict(root=MOUNT+'/'+phase, repo='/srv/dl_binner/repo', source=source, phase=phase,
        user='rasmus_allesoee_gmail_com', service_name='e031-'+phase,
        archive_prefix='gs://dl-binner-archive-167650584170/e031/'+phase+'/', vm_start_epoch=0,
        provider_max_duration_seconds=limits['provider_STOP_seconds'],
        scratch=dict(name=DISK,id=DISK_ID,size_GiB=40,reused=True))
    for label, code in [('source',source_code(ident,f['source_transport'])),('mount',mount_code()),
                        ('host',learner_host(ident,f)),('release',learner_release(ident,before))]:
        compile(code, 'prepared-learner-'+label, 'exec')
    c.call(['compute','instances','set-scheduling',CPU,'--no-restart-on-failure',
            '--max-run-duration='+str(limits['provider_STOP_seconds'])+'s','--instance-termination-action=STOP'], CPU_ZONE)
    stopped = c.state(); c.put('provider-STOP-readback.json', stopped)
    if (str(stopped['scheduling']['maxRunDuration']['seconds']) != str(limits['provider_STOP_seconds'])
            or stopped['scheduling']['instanceTerminationAction'] != 'STOP' or stopped['scheduling']['automaticRestart']):
        raise ValueError('Independent provider STOP differs')
    try:
        c.call(['compute','instances','start',CPU], CPU_ZONE); live = c.state()
        if live['status'] != 'RUNNING' or live['lastStartTimestamp'] == before['lastStartTimestamp']:
            raise ValueError('Fresh original CPU boot absent')
        ident['vm_start_epoch'] = datetime.datetime.fromisoformat(live['lastStartTimestamp']).timestamp()
        ident['allocation_start_epoch'] = ident['vm_start_epoch']; save(out/'identity.json', ident)
        c.put('provider-start.json', live)
        for at in range(12):
            result = subprocess.run(SSH+['true'], capture_output=True, text=True, timeout=25)
            (out/('ssh-ready-'+str(at)+'.log')).write_text(result.stdout+result.stderr)
            if result.returncode == 0:
                break
            time.sleep(2)
        else:
            raise RuntimeError('Pinned SSH unavailable; no credential replacement')
        remote(out,'source',source_code(ident,f['source_transport']))
        remote(out,'existing-task-mount',mount_code())
        remote(out,'held-host-native-gates',learner_host(ident,f),300)
        save(out/'held-gates-dispatched.json',ident)
    except BaseException:
        c.stop(); raise
    return ident


def release(out):
    """Release once after live provider and actual Linux schedule/gate readbacks."""
    out = Path(out).absolute(); ident = json.loads((out/'identity.json').read_text())
    c = Cloud(out/'release-control'); state = c.state(); c.put('provider-before-release.json',state)
    if (state['status'] != 'RUNNING'
            or datetime.datetime.fromisoformat(state['lastStartTimestamp']).timestamp() != ident['allocation_start_epoch']
            or str(state['scheduling']['maxRunDuration']['seconds']) != str(ident['provider_max_duration_seconds'])
            or state['scheduling']['automaticRestart'] or state['scheduling']['instanceTerminationAction'] != 'STOP'):
        raise ValueError('Original running boot/provider STOP differs')
    remote(out,'release',learner_release(ident,state))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--artifact-root',type=Path,required=True)
    p.add_argument('--start',action='store_true');p.add_argument('--release',action='store_true');a=p.parse_args()
    if a.start and not a.release:start(a.artifact_root)
    elif a.release and not a.start:release(a.artifact_root)
    else:p.error('Choose start or release')
