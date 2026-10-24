#!/usr/bin/env python3
"""Bound one ordinary T4's sampled memory alongside E021's clock and disk guard.

Only nvidia-smi is queried; this module never loads a tensor/OpenMP runtime,
changes a device, retries science or mutates cloud resources. Unit samplers are
explicit test doubles and are not accepted as native hardware evidence.
"""
import csv,json,os,signal,subprocess,threading,time
from pathlib import Path
from e009_controls import PhaseGuard

GPU_BYTES=14*1024**3


def parse_gpu(text):
    """Require one identified T4 and finite integer MiB counters from native CSV."""
    rows=list(csv.reader(text.strip().splitlines()))
    if len(rows)!=1 or len(rows[0])!=4:raise ValueError('Exactly one ordinary T4 GPU required')
    uuid,name,total,used=[x.strip()for x in rows[0]]
    if not uuid.startswith('GPU-')or not name.endswith('T4')or not total.isdigit()or not used.isdigit():raise ValueError('GPU identity/counters differ')
    total,used=int(total)*1024**2,int(used)*1024**2
    if total<GPU_BYTES or used>total:raise ValueError('Insufficient/invalid T4 memory inventory')
    return dict(uuid=uuid,name=name,total_bytes=total,used_bytes=used)


def sample_gpu():
    """Read the distro-installed NVIDIA CLI with a bounded, non-shell subprocess."""
    p=subprocess.run(['/usr/bin/nvidia-smi','--query-gpu=uuid,name,memory.total,memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=8)
    if p.returncode:raise RuntimeError('Native nvidia-smi query failed: '+p.stderr[-2000:])
    return parse_gpu(p.stdout)


class GPUPhaseGuard:
    """Sample a fixed GPU identity and stop its supervised parent on any limit loss.

    Disk/free/clock enforcement is delegated to the retained guard with explicit
    32 GiB growth. VRAM errors use its main-thread alarm so native supervision
    reaps its owned child process group; the exit watcher then stops the VM.
    """
    def __init__(self,root,seconds,reserve_bytes=25*1024**3,growth_bytes=32*1024**3,sampler=None,interval=2,wait_for_ready=False,boot_id=None):
        self.root=Path(root);self.cpu=PhaseGuard(root,seconds,reserve_bytes,growth_bytes);self.sampler=sampler or sample_gpu;self.interval=interval;self.done=threading.Event();self.thread=None;self.wait_for_ready=wait_for_ready;self.boot_id=boot_id;self.uuid=None
    @property
    def observations(self):return self.cpu.observations
    def __enter__(self):
        self.cpu.__enter__()
        try:
            self.log=self.root/'logs'/('gpu-memory-'+str(time.time_ns())+'.jsonl');self.log.parent.mkdir(exist_ok=True)
            self._observe()
            def watch():
                while not self.done.wait(self.interval):
                    try:self._observe()
                    except BaseException as exc:
                        self.cpu.reason='GPU resource guard failed: '+str(exc);os.kill(os.getpid(),signal.SIGALRM);return
            self.thread=threading.Thread(target=watch,daemon=True);self.thread.start();return self
        except BaseException:
            self.cpu.__exit__(None,None,None);raise
    def _observe(self):
        """Hold safely before driver install; activate only on same-boot real telemetry."""
        ready=self.root/'gpu-ready.json'
        if self.uuid is None:
            if self.wait_for_ready and not ready.exists():
                if (self.root/'release.json').exists():raise ValueError('GPU driver readiness missing before release')
                return
            value=self.sampler()
            if self.wait_for_ready:
                if ready.is_symlink():raise ValueError('GPU driver receipt link refused')
                proof=json.loads(ready.read_text());current=self.boot_id or Path('/proc/sys/kernel/random/boot_id').read_text().strip()
                if set(proof)!={'boot_id','gpu_uuid'}or proof!={'boot_id':current,'gpu_uuid':value['uuid']}:raise ValueError('GPU driver receipt boot/identity differs')
            self.uuid=value['uuid'];self._record(value)
            (self.root/'logs/gpu-guard-live.json').write_text(json.dumps(dict(status='LIVE_NATIVE_TELEMETRY',gpu_uuid=self.uuid,guard_pid=os.getpid(),epoch=time.time()))+'\n')
        else:self._record(self.sampler())

    def _record(self,value):
        if value['uuid']!=self.uuid:raise ValueError('Current-boot GPU identity changed')
        if value['used_bytes']>GPU_BYTES:raise MemoryError('14 GiB GPU memory ceiling exceeded')
        with self.log.open('a')as f:f.write(json.dumps(dict(epoch=time.time(),**value))+'\n')
    def __exit__(self,*exc):
        self.done.set()
        if self.thread:self.thread.join(timeout=10)
        self.cpu.__exit__(*exc)
