#!/usr/bin/env python3
"""Bound one local engineering/admission worker by the original E021 clock.

Commands are explicit argv, never shell text. Complete logs, actual failure cause,
RSS/CPU and total local storage remain. Read-only dependency links are inventoried
separately and not counted as newly copied bytes. No cloud interface is provided.
"""
import argparse,json,os,signal,sys,threading,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_owner import supervisor
from e021_acquire import guard

def main():
    """Run one fresh numbered attempt with four threads / 8 GB and no clock reset."""
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--label',required=True);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    if not a.command or Path(a.label).name!=a.label:raise ValueError('Explicit safe command/label required')
    command=a.command[1:]if a.command[0]=='--'else a.command;clock=json.loads((a.root/'acquisition-clock.json').read_text());guard(a.root,clock)
    attempt=1
    while(a.root/(a.label+'-'+str(attempt)+'.resources.json')).exists():attempt+=1
    out=a.root/(a.label+'-'+str(attempt));stop=threading.Event();reasons=[]
    def check():
        while not stop.wait(1):
            try:guard(a.root,clock)
            except BaseException as exc:reasons.append(repr(exc));os.kill(os.getpid(),signal.SIGALRM);return
    def alarm(signum,frame):raise TimeoutError(reasons[0]if reasons else'Original E021 clock expired')
    signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,max(.001,clock['started_epoch']+clock['seconds']-time.time()))
    worker=threading.Thread(target=check,daemon=True);worker.start();s=supervisor();env=s.isolated_env(4)
    env.update(HF_MODULES_CACHE=str(a.root.absolute()/'model-module-cache'),HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false',NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(a.root.absolute()/'numba-cache'))
    result=dict(status='FAILED',label=a.label,attempt=attempt)
    try:
        result['resources']=s.supervise(command,out.with_suffix('.log'),clock['started_epoch']+clock['seconds']-time.time(),8_000_000_000,env,sample_root=os.getpid());result['status']='SUCCESS'
    except BaseException as exc:result['error']=repr(exc);raise
    finally:
        stop.set();worker.join(2);signal.setitimer(signal.ITIMER_REAL,0)
        result['elapsed_original_seconds']=time.time()-clock['started_epoch'];result['extra_local_bytes']=guard(a.root,clock)
        out.with_suffix('.resources.json').write_text(json.dumps(result,indent=2)+'\n')
        print('E021_LOCAL_ATTEMPT',a.label,attempt,result['status'],flush=True)

if __name__=='__main__':main()
