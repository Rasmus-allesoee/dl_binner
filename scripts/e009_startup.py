"""Observe E009 reused-runtime startup without skipping site or weakening checks.

Invoke lexical Python -I -B -S, then this file, trace interval, file/module,
target and target arguments. Flush a marker before site initialization, retain
normal site.main(), then run the unchanged inventory or pip module. Parent-side
observation retains Linux wait state before the accepted supervisor stops a hang.
No environment is installed, relocated or modified here.
"""
import sys


def probe():
    """Run a real target after normal site; parent-requested stacks use no timer thread."""
    print(f'DLBINNER PROBE Python entered interpreter={sys.executable}',file=sys.stderr,flush=True)
    import faulthandler
    import os
    import _signal
    seconds=float(sys.argv[1])
    if not 0<seconds<=10:raise ValueError('Trace interval must be positive and <=10 seconds')
    mode,target=sys.argv[2:4]
    if mode not in ('file','module'):raise ValueError('Expected file or module target')
    sys.argv=[target,*sys.argv[4:]]
    print(f'DLBINNER PROBE before site pid={os.getpid()} interpreter={sys.executable}',file=sys.stderr,flush=True)
    # Separate stacks from stdout/inventory JSON; keep the descriptor open for
    # the process lifetime. The parent requests dumps only while the probe runs.
    global _stack_file
    directory=os.environ.get('E009_STARTUP_STACK_DIR')
    _stack_file=open(os.path.join(directory,str(os.getpid())+'.log'),'x') if directory else sys.stderr
    faulthandler.enable(file=_stack_file)
    faulthandler.register(_signal.SIGUSR1,file=_stack_file,all_threads=True)
    print(f'DLBINNER PROBE trace ready pid={os.getpid()} seconds={seconds}',file=sys.stderr,flush=True)
    try:
        import site
        site.main()
        print(f'DLBINNER PROBE site ready prefix={sys.prefix} user_site={site.ENABLE_USER_SITE}',file=sys.stderr,flush=True)
        import runpy
        print(f'DLBINNER PROBE target begin {mode}={target}',file=sys.stderr,flush=True)
        if mode=='file':runpy.run_path(target,run_name='__main__')
        else:runpy.run_module(target,run_name='__main__',alter_sys=True)
        print('DLBINNER PROBE target ready',file=sys.stderr,flush=True)
    finally:print(f'DLBINNER PROBE finished pid={os.getpid()}',file=sys.stderr,flush=True)


def startup_argv(python,target,args=(),mode='file',trace_seconds=10):
    """Preserve the lexical venv interpreter and target argv; instrument before site."""
    from pathlib import Path
    return [str(python),'-I','-B','-S',str(Path(__file__).absolute()),str(trace_seconds),mode,str(target),*map(str,args)]


def wait_snapshot(pid,start,proc_root='/proc'):
    """Read bounded Linux state for an observed PID/start identity, never environs.

    Permission-denied kernel stacks/syscalls are explicit unavailable evidence.
    A synthetic proc_root tests decoding only; it does not establish Linux runtime
    validation. PID reuse or exit is rejected before inspecting further state.
    """
    from pathlib import Path
    root=Path(proc_root)/str(pid);result={'pid':pid,'start_identity':start}
    try:
        stat=(root/'stat').read_text();fields=stat[stat.rfind(')')+2:].split()
        if fields[19]!=start:return dict(result,observation_status='exited or PID reused')
    except (OSError,ValueError,IndexError) as error:return dict(result,observation_status='unavailable',error=repr(error))
    result['observation_status']='observed owned process'
    for name in ('stat','status','wchan','syscall','stack','cmdline','io'):
        try:
            with (root/name).open('rb') as stream:data=stream.read(8192)
            result[name]=data.decode(errors='replace').replace('\0',' ')
        except OSError as error:result[name]={'unavailable':repr(error)}
    import os
    try:result['fd_targets']={p.name:os.readlink(p) for p in list((root/'fd').iterdir())[:32]}
    except OSError as error:result['fd_targets']={'unavailable':repr(error)}
    return result


def supervise_startup(sup,command,log,seconds,ram_bytes,env,sample_root=None):
    """Add scoped wait-state observations to unchanged timeout/RSS/group cleanup.

    The accepted supervisor already identifies the launched process and its
    descendants. Observe only that owned tree, restoring its sampler afterward;
    normal sampling, elapsed ceilings and termination remain unchanged.
    """
    import json
    import os
    from pathlib import Path
    import time
    import re
    import signal
    original=sup.process_sample;last=0;path=Path(log).with_suffix('.process-wait.jsonl')
    native=Path('/proc/self/stat').is_file()
    stacks=Path(log).with_suffix('.startup-stacks');stacks.mkdir()
    env=dict(env,E009_STARTUP_STACK_DIR=str(stacks));requested={}
    with path.open('x') as output:
        if not native:
            output.write(json.dumps({'scope':'Linux /proc wait-state unavailable on this platform; no Linux validation credit'})+'\n');output.flush()
        def observed(root,known):
            nonlocal last
            value=original(root,known);now=time.monotonic()
            if root is not None and root!=os.getpid():
                text=Path(log).read_text()
                ready={int(pid):float(interval) for pid,interval in re.findall(r'DLBINNER PROBE trace ready pid=(\d+) seconds=([\d.]+)',text)}
                finished={int(pid) for pid in re.findall(r'DLBINNER PROBE finished pid=(\d+)',text)}
                for pid,start in list(known):
                    if pid not in ready or pid in finished:continue
                    key=(pid,start);previous=requested.setdefault(key,now)
                    if now-previous<ready[pid]:continue
                    check={};original(pid,check)
                    if key in check:
                        try:os.kill(pid,signal.SIGUSR1)
                        except ProcessLookupError:pass
                    requested[key]=now
            if native and root is not None and root!=os.getpid() and now-last>=5:
                rows=[wait_snapshot(pid,start) for pid,start in list(known)[:32]]
                output.write(json.dumps({'monotonic_seconds':now,'scope':'observed launched tree only; no process environment captured','processes':rows})+'\n');output.flush();last=now
            return value
        sup.process_sample=observed
        try:return sup.supervise(command,log,seconds,ram_bytes,env,sample_root=sample_root)
        finally:sup.process_sample=original


if __name__=='__main__':probe()
