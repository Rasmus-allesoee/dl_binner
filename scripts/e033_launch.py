#!/usr/bin/env python3
"""Connect the frozen E033 candidate to its approved existing CPU allocation.

This operations-only controller validates the real producer/consumer schema before
starting compute. It preserves E032's closed delivery before releasing that task
disk, evaluates source-disk headroom and conditionally creates only the approved
100 GiB task disk. Science stays in the frozen held phase; failures retain evidence
and stop the allocation without an implicit retry or a new clock.
"""
import argparse
import base64
import datetime
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from e021_portable_cloud import Cloud, CPU, CPU_ZONE
from e024_coverage import binding
from e031_launch import remote, SSH, save, source_code
from e033_phase import validate_config

BRANCH = 'multiscale-bam-representation'
OLD_DISK = 'e032-task-1793735314'
OLD_DISK_ID = '6444653960304755760'
OLD_ROOT = '/srv/dl_binner/experiments/e032/selection-20261103T194814Z-bc93453'


def frozen():
    """Verify the unchanged prepared science and separate operations source lock."""
    for name in ['source-lock.json', 'native-launch-lock.json']:
        value = json.loads((ROOT / 'experiments/E033-multiscale-bam' / name).read_text())
        for n, b in value['files'].items():
            if binding(ROOT / n) != b:
                raise ValueError('Frozen source differs: ' + n)


def source_sync(ident, transport):
    """Advertise this exact branch privately without modifying GitHub access."""
    return source_code(ident, transport).replace(
        'bootstrap-preserving-learning', BRANCH).replace(
        'experiments/e031/source-transports', 'experiments/e033/source-transports')


def config_value(ident, financial, used=0, device=0):
    """Produce every exact held-parent field, including actual device baselines."""
    plan = json.loads((ROOT / 'experiments/E033-multiscale-bam/runtime-plan.json').read_text())
    reuse = json.loads((ROOT / 'experiments/E033-multiscale-bam/reuse-lock.json').read_text())
    limits = plan['limits']; start = ident['vm_start_epoch']; root = ident['root']
    return dict(root=root, repo=ident['repo'], source_commit=ident['source'], operations_source=ident['source'],
        vm_start_epoch=start, review_deadline_epoch=start + limits['seconds'],
        provider_deadline_epoch=start + limits['provider_STOP_seconds'], setup_deadline_epoch=start + 5400,
        service_name=ident['service_name'], user=ident['user'], archive_prefix=ident['archive_prefix'],
        plan=root + '/science-plan.json', python=root + '/task/env/bin/python',
        workflow_python=plan['workflow_python'], base=reuse['native_dependency_base'],
        reference=reuse['native_runtime_reference'], wheel=root + '/payload/dl_binner-0.1.0.dev9-py3-none-any.whl',
        pysam_wheel=root + '/payload/' + financial['pysam_filename'], gcloud='/snap/bin/gcloud',
        samtools='/srv/dl_binner/experiments/e009/envs/data-cpu-v1-ae654b442315/bin/samtools',
        financial=financial, initial_filesystem_used_bytes=used, initial_filesystem_device=device,
        source_filesystem='/srv/dl_binner', task_filesystem=root + '/task', limits=limits)


def render_tail(ident):
    """Retain complete old logs/gates/tail and prove the already accepted work bytes.

    Mount only the positively identified old task filesystem read-only. Upload a
    bounded regular-member capsule with server readback, and leave it mounted;
    detach/deletion is a subsequent controller action after actual proof returns.
    """
    old = json.loads((ROOT / 'experiments/E032-biological-candidate-selection/native-observed.json').read_text())
    code = r'''import hashlib,json,os,pathlib,subprocess,sys,time
ident=@@IDENT@@;old=@@OLD@@;disk=@@DISK@@;oldroot=pathlib.Path(@@OLDROOT@@)
repo=pathlib.Path(ident['repo']);sys.path.insert(0,str(repo/'scripts'))
from e024_coverage import binding
from e033_collect import pack
from e021_portable_node import storage_upload
device=pathlib.Path('/dev/disk/by-id/google-'+disk)
if not os.path.ismount(oldroot):
 subprocess.run(['sudo','-n','mount','-o','ro,nodev,nosuid,noload',str(device),str(oldroot)],check=True)
actual=pathlib.Path(subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(oldroot)],text=True).strip())
if actual.resolve()!=device.resolve() or os.stat(oldroot).st_dev==os.stat('/srv/dl_binner').st_dev:raise ValueError('Old protected task device differs')
opts=subprocess.check_output(['findmnt','-n','-o','OPTIONS','--target',str(oldroot)],text=True).strip().split(',')
if 'ro'not in opts:raise ValueError('Old preservation mount must be read-only')
completion=json.loads((oldroot/'completion.json').read_text())
if binding(oldroot/'completion.json')!=old['raw_completion'] or not completion['science_completed'] or completion['status']!='SUCCESS':raise ValueError('Original completion differs')
tail=json.loads((oldroot/'closed-delivery-tail.json').read_text())
if tail['status']!='PASS':raise ValueError('Original delivery tail did not pass')
expected=old['archive']['binding'];matches=[p for p in oldroot.rglob('e032-evidence.tar.gz') if binding(p)==expected]
if len(matches)!=1:raise ValueError('Exact retained E032 return archive missing/ambiguous')
import tarfile
with tarfile.open(matches[0],'r:gz')as t:
 f=t.extractfile('inventory.json')
 if f is None:raise ValueError('Original return inventory missing')
 inventory=json.load(f)
allwork=inventory['all_work_members']
actualwork={str(p.relative_to(oldroot/'work')):binding(p)for p in (oldroot/'work').rglob('*')if p.is_file()}
if actualwork!=allwork:raise ValueError('Old work contains changed/unarchived members; retain disk')
new=pathlib.Path('/srv/dl_binner/experiments/e033/closed-E032-'+ident['phase']);new.mkdir(parents=True,exist_ok=False)
work=new/'tail';work.mkdir();evidence=new/'evidence';evidence.mkdir()
import shutil
for n in ['logs','gates']:
 shutil.copytree(oldroot/n,work/n)
for n in ['closed-delivery-tail.json','completion.json','science-result.json','config.json','host.json','release.json','started.json','terminal.log']:
 p=oldroot/n
 if not p.is_file()or p.is_symlink():raise ValueError('Required old closed journal missing: '+n)
 shutil.copyfile(p,work/n)
(evidence/'accepted-work.json').write_text(json.dumps(dict(status='PASS',old_archive=expected,work_members=len(allwork),all_old_work_bytes_verified=True,read_only_mount=True),indent=2)+'\n')
# This capsule is small. Refuse before packing if it is unexpectedly large.
if sum(p.stat().st_size for p in work.rglob('*')if p.is_file())>256*1024**2:raise ValueError('Old closed-tail capsule exceeds bounded scope')
proof=pack(work,evidence,new/'return')
if proof['archive']['bytes']>128*1024**2:raise ValueError('Old closed-tail compressed cap exceeded')
prefix=ident['archive_prefix']+'E032-closed-tail/'
delivered={n:storage_upload(new/'return'/n,prefix+n)for n in ['e033-evidence.tar.gz','inventory.json','collection.json','e033-evidence.tar.gz.sha256']}
result=dict(status='PASS_OLD_TASK_RELEASE_ADMITTED',old_disk=disk,old_root=str(oldroot),work_members=len(allwork),
 all_old_work_bytes_verified=True,complete_logs_gates_tail_collected=True,archive=proof['archive'],delivered=delivered,
 local_preservation_root=str(new),epoch=time.time())
(new/'release-admission.json').write_text(json.dumps(result,indent=2)+'\n')
print('E033_OLD_TAIL_VERIFIED',json.dumps(result),flush=True)
'''
    code = code.replace('@@IDENT@@', repr(ident)).replace('@@OLD@@', repr(old)).replace(
        '@@DISK@@', repr(OLD_DISK)).replace('@@OLDROOT@@', repr(OLD_ROOT))
    compile(code, 'E033 actual old-tail consumer', 'exec'); return code


def render_inventory(ident):
    """Measure real source headroom without removing required science or runtimes."""
    return r'''import json,os,pathlib,shutil,subprocess
root=pathlib.Path('/srv/dl_binner');out=root/'experiments/e033/inventory';out.mkdir(parents=True,exist_ok=True)
usage=shutil.disk_usage(root)
p=subprocess.run(['du','-x','-B1','--max-depth=2',str(root/'experiments')],capture_output=True,text=True,timeout=180)
(out/(@@PHASE@@+'.du')).write_text(p.stdout+p.stderr);p.check_returncode()
# Existing source transports, extracted inputs, runtimes and science remain.
# The preceding local and E032 cache cleanup already removed disposable caches.
print('E033_HEADROOM',json.dumps(dict(usage._asdict(),device=os.stat(root).st_dev,
 safe_cleanup_insufficient_for_55GiB_peak_plus_25GiB_reserve=usage.free<80*1024**3,
 required_E021_transports_and_original_science_preserved=True)),flush=True)
'''.replace('@@PHASE@@', repr(ident['phase']))


def render_host(ident, financial, disk=None):
    """Render exact new-device checks, payload transport and real held admission."""
    cfg = config_value(ident, financial)
    code = r'''import base64,json,os,pathlib,pwd,shutil,subprocess,sys,time
ident=@@IDENT@@;disk=@@DISK@@;cfg=@@CONFIG@@
repo=pathlib.Path(ident['repo']);root=pathlib.Path(ident['root']);task=root/'task'
if not os.path.ismount('/srv/dl_binner') or os.cpu_count()!=8:raise ValueError('Original CPU/mount required')
root.mkdir(parents=True,exist_ok=False)
if disk:
 script=r"""import os,pathlib,subprocess,json,pwd
task=pathlib.Path(@@TASK@@);name=@@NAME@@;dev=pathlib.Path('/dev/disk/by-id/google-'+name)
if not name.startswith('e033-task-')or task.exists():raise ValueError('Fresh exact task scope required')
subprocess.run(['udevadm','settle','--timeout=15'],check=True)
rows=json.loads(subprocess.check_output(['lsblk','-J','-b','-o','NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT',str(dev)],text=True))['blockdevices']
if len(rows)!=1 or rows[0]['size']!=100*1024**3 or rows[0]['type']!='disk'or rows[0].get('fstype')or rows[0].get('mountpoint')or rows[0].get('children'):raise ValueError('Only new empty 100 GiB task disk may be formatted')
if subprocess.run(['blkid',str(dev)],capture_output=True).returncode!=2:raise ValueError('Existing device signature refused')
subprocess.run(['mkfs.ext4','-m','0','-L','e033-task',str(dev)],check=True,capture_output=True)
task.mkdir(exist_ok=False);subprocess.run(['mount','-o','nodev,nosuid',str(dev),str(task)],check=True)
account=pwd.getpwnam(@@USER@@);os.chown(task,account.pw_uid,account.pw_gid)
actual=subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(task)],text=True).strip()
if pathlib.Path(actual).resolve()!=dev.resolve() or os.stat(task).st_dev==os.stat('/srv/dl_binner').st_dev:raise ValueError('New task mount differs')
""".replace('@@TASK@@',repr(str(task))).replace('@@NAME@@',repr(disk['name'])).replace('@@USER@@',repr(ident['user']))
 subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B','-'],input=script,text=True,check=True)
else:task.mkdir(exist_ok=False)
usage=shutil.disk_usage(task);source=shutil.disk_usage('/srv/dl_binner')
if usage.free<80*1024**3 or source.free<25*1024**3:raise ValueError('Measured peak plus separate reserves required')
cfg['initial_filesystem_used_bytes']=usage.used;cfg['initial_filesystem_device']=os.stat(task).st_dev
for n in ['payload','logs','tmp']:(root/n).mkdir()
sys.path.insert(0,str(repo/'scripts'))
from e024_coverage import binding
from e021_control_json import publish
from e033_phase import validate_config
for name,encoded,expected in @@PAYLOADS@@:
 p=root/'payload'/name
 with p.open('xb')as f:f.write(base64.b64decode(encoded,validate=True))
 if binding(p)!=expected:raise ValueError('Native wheel transport differs: '+name)
relative=ident['phase']+'/task'
plan=json.loads((repo/'experiments/E033-multiscale-bam/runtime-plan.json').read_text().replace('NEW_PHASE',relative))
if plan['python']!=cfg['python']:raise ValueError('Task interpreter path differs')
publish(plan,root/'science-plan.json');publish(cfg['financial'],root/'payload/financial-gate.json')
validate_config(cfg)
publish(dict(user=ident['user'],boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 filesystem=usage._asdict(),source_filesystem=source._asdict(),post_mount_before_payload_used_bytes=usage.used,
 device=cfg['initial_filesystem_device'],disk=disk,epoch=time.time()),root/'host.json');publish(cfg,root/'config.json')
p=subprocess.run(['sudo','-n','/usr/bin/python3','-I','-B',str(repo/'scripts/e033_arm.py'),'--config',str(root/'config.json')],capture_output=True,text=True,timeout=180)
(root/'logs/arming.log').write_text(p.stdout+p.stderr);print(p.stdout+p.stderr,flush=True);p.check_returncode()
print('E033_HELD',json.dumps(dict(root=str(root),config=binding(root/'config.json'),plan=binding(root/'science-plan.json'),service_name=ident['service_name'])),flush=True)
'''
    payloads = []
    for path_key, expected_key in [('wheel_path', 'wheel_binding'), ('pysam_path', 'pysam_binding')]:
        p = Path(financial[path_key]); expected = financial[expected_key]
        if binding(p) != expected: raise ValueError('Frozen payload differs')
        payloads.append((p.name, base64.b64encode(p.read_bytes()).decode(), expected))
    code = code.replace('@@IDENT@@', repr(ident)).replace('@@DISK@@', repr(disk)).replace(
        '@@CONFIG@@', repr(cfg)).replace('@@PAYLOADS@@', repr(payloads))
    compile(code, 'E033 actual host producer', 'exec'); return code


def render_release(ident, provider):
    """Publish one immutable release bound to live process, source and provider."""
    code = r'''import json,pathlib,subprocess,sys,time
ident=@@IDENT@@;provider=@@PROVIDER@@
root=pathlib.Path(ident['root']);sys.path.insert(0,str(pathlib.Path(ident['repo'])/'scripts'))
from e009_exit_watchdog import identity
from e021_control_json import publish
from e024_coverage import binding
from e033_phase import validate_config
cfg=json.loads((root/'config.json').read_text());validate_config(cfg)
watch=json.loads((pathlib.Path('/var/lib')/(cfg['service_name']+'-exit')/'status.json').read_text());started=json.loads((root/'started.json').read_text())
if watch['decision']!='workflow alive'or watch['expected_process']!=identity(started['pid'])or watch['observed_process']!=watch['expected_process']or watch['boot_id']!=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip():raise ValueError('Fresh held watcher identity differs')
if subprocess.check_output(['systemctl','is-active',cfg['service_name']+'-exit.timer'],text=True).strip()!='active':raise ValueError('Exit timer inactive')
if provider['status']!='RUNNING'or str(provider['scheduling']['maxRunDuration']['seconds'])!=str(cfg['limits']['provider_STOP_seconds'])or provider['scheduling']['instanceTerminationAction']!='STOP':raise ValueError('Provider fallback differs')
actual=__import__('datetime').datetime.fromisoformat(provider['lastStartTimestamp']).timestamp()
if actual!=cfg['vm_start_epoch']:raise ValueError('Provider original start differs')
publish(provider,root/'logs/provider-before-release.json')
publish(dict(config=binding(root/'config.json'),plan=binding(root/'science-plan.json'),provider_STOP_verified=True,watchdog=watch,epoch=time.time()),root/'release.json')
print('E033_RELEASED',str(root),flush=True)
'''
    code = code.replace('@@IDENT@@', repr(ident)).replace('@@PROVIDER@@', repr(provider))
    compile(code, 'E033 actual release', 'exec'); return code


def preflight(ident, financial):
    """Exercise real complete configuration and all generated producer programs."""
    frozen(); validate_config(config_value(ident, financial))
    render_host(ident, financial); render_release(ident, {})
    compile(render_tail(ident), 'tail', 'exec'); compile(render_inventory(ident), 'inventory', 'exec')
    compile(source_sync(ident, financial['source_transport']), 'private source', 'exec')


def start(out):
    """Start once after fresh financial/source gates; stop on controller failure."""
    out = Path(out).absolute()
    if (out / 'identity.json').exists(): raise ValueError('Original attempt exists; explicit verified recovery required')
    financial = json.loads((out / 'financial-gate.json').read_text())
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip(): raise ValueError('Exact clean source required')
    if financial['source_transport']['source'] != source: raise ValueError('Exact private source differs')
    phase = 'multiscale-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + source[:7]
    ident = dict(source=source, repo='/srv/dl_binner/repo', phase=phase, root='/srv/dl_binner/experiments/e033/' + phase,
        user='rasmus_allesoee_gmail_com', service_name='e033-' + phase,
        archive_prefix='gs://dl-binner-archive-167650584170/e033/' + phase + '/', vm_start_epoch=time.time())
    preflight(ident, financial)
    c = Cloud(out / 'control'); before = c.state(); c.put('provider-before.json', before)
    sizes = sorted(int(d['diskSizeGb']) for d in before['disks'])
    if before['status'] != 'TERMINATED' or not before['machineType'].endswith('/e2-standard-8') or sizes != [30, 40, 300] or before.get('guestAccelerators'):
        raise ValueError('Original stopped E2 and protected old task required')
    old_disk = c.call(['compute', 'disks', 'describe', OLD_DISK], CPU_ZONE)
    if old_disk['id'] != OLD_DISK_ID or int(old_disk['sizeGb']) != 40: raise ValueError('Protected old disk identity differs')
    seconds = config_value(ident, financial)['limits']['provider_STOP_seconds']
    try:
        c.call(['compute', 'instances', 'set-scheduling', CPU, '--no-restart-on-failure', '--max-run-duration=' + str(seconds) + 's', '--instance-termination-action=STOP'], CPU_ZONE)
        checked = c.state(); c.put('provider-STOP-before-start.json', checked)
        if str(checked['scheduling']['maxRunDuration']['seconds']) != str(seconds) or checked['scheduling']['instanceTerminationAction'] != 'STOP': raise ValueError('Pre-start provider STOP differs')
        c.call(['compute', 'instances', 'start', CPU], CPU_ZONE); live = c.state(); c.put('provider-start.json', live)
        if live['status'] != 'RUNNING' or live['lastStartTimestamp'] == before['lastStartTimestamp']: raise ValueError('Fresh actual start absent')
        ident['vm_start_epoch'] = datetime.datetime.fromisoformat(live['lastStartTimestamp']).timestamp(); save(out / 'identity.json', ident)
        for at in range(12):
            p = subprocess.run(SSH + ['true'], capture_output=True, text=True, timeout=25)
            (out / ('ssh-ready-' + str(at) + '.log')).write_text(p.stdout + p.stderr)
            if p.returncode == 0: break
            time.sleep(2)
        else: raise RuntimeError('Pinned original SSH unavailable')
        remote(out, 'source-sync', source_sync(ident, financial['source_transport']))
        text = remote(out, 'protected-old-tail', render_tail(ident), 600)
        tail = json.loads(next(v.removeprefix('E033_OLD_TAIL_VERIFIED ') for v in text.splitlines() if v.startswith('E033_OLD_TAIL_VERIFIED ')))
        save(out / 'old-task-release-admission.json', tail)
        if tail['status'] != 'PASS_OLD_TASK_RELEASE_ADMITTED' or not tail['all_old_work_bytes_verified']: raise ValueError('Old task release proof missing')
        remote(out, 'unmount-old-task', "import subprocess\nsubprocess.run(['sudo','-n','umount'," + repr(OLD_ROOT) + "],check=True)\n")
        c.call(['compute', 'instances', 'detach-disk', CPU, '--disk=' + OLD_DISK], CPU_ZONE)
        detached = c.call(['compute', 'disks', 'describe', OLD_DISK], CPU_ZONE)
        if detached['id'] != OLD_DISK_ID or detached.get('users'): raise ValueError('Old disk not safely detached')
        c.call(['compute', 'disks', 'delete', OLD_DISK], CPU_ZONE); c.put('old-task-released.json', dict(disk=detached,proof=tail,epoch=time.time()))
        text = remote(out, 'source-headroom', render_inventory(ident), 210)
        headroom = json.loads(next(v.removeprefix('E033_HEADROOM ') for v in text.splitlines() if v.startswith('E033_HEADROOM ')))
        if headroom['free'] < 25 * 1024**3: raise ValueError('Original source reserve requires verified cleanup')
        disk = None
        if headroom['free'] < 80 * 1024**3:
            quota = c.call(['compute', 'regions', 'describe', 'us-central1']); q = {x['metric']: x for x in quota['quotas']}
            if q['SSD_TOTAL_GB']['limit'] - q['SSD_TOTAL_GB']['usage'] < 100: raise ValueError('Approved task disk exceeds current quota')
            c.put('task-disk-decision.json', dict(measured=headroom,needed_free_bytes=80 * 1024**3,
                old_tail_verified_and_disk_released=True,safe_cleanup_cannot_supply_peak_and_reserve=True,approved_single_100_GiB=True))
            name = 'e033-task-' + str(int(ident['vm_start_epoch']))
            c.call(['compute', 'disks', 'create', name, '--size=100GB', '--type=pd-balanced', '--labels=experiment=e033'], CPU_ZONE)
            disk = c.call(['compute', 'disks', 'describe', name], CPU_ZONE); c.put('new-task-disk.json', disk)
            if int(disk['sizeGb']) != 100 or disk.get('users') or not disk['type'].endswith('/pd-balanced'): raise ValueError('New task identity differs')
            c.call(['compute', 'instances', 'attach-disk', CPU, '--disk=' + name, '--device-name=' + name], CPU_ZONE)
        text = remote(out, 'held-host', render_host(ident, financial, disk), 360)
        held = json.loads(next(v.removeprefix('E033_HELD ') for v in text.splitlines() if v.startswith('E033_HELD ')))
        save(out / 'held.json', held); provider = c.state(); c.put('provider-before-release.json', provider)
        remote(out, 'release', render_release(ident, provider), 90)
        save(out / 'released.json', dict(epoch=time.time(),held=held))
    except BaseException as e:
        save(out / ('failure-' + str(time.time_ns()) + '.json'), dict(error=repr(e),epoch=time.time()))
        c.stop(); raise
    return ident


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args(); print(json.dumps(start(args.root)), flush=True)
