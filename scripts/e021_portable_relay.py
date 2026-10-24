#!/usr/bin/env python3
"""Move one verified file stream through a bounded Mac buffer and pair all digests.

No bulk Mac retention, credentials on workers, automatic retry or cloud mutation.
Failed bytes count toward the same 20 GiB transport cap. A completed transfer is
not an admitted scientific cache until the actual installed consumer passes.
"""
import argparse,hashlib,json,os,shlex,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e021_portable_transport import paired,CAP,names


def remote(node,code,value=None):
    """Read/write only small explicit JSON over the pinned SSH entry point."""
    p=subprocess.run(node.get('bulk_ssh',node['ssh'])+['/usr/bin/python3 -I -B -c '+shlex.quote(code)],input=None if value is None else json.dumps(value),capture_output=True,text=True,timeout=60)
    if p.returncode:raise RuntimeError(p.stderr[-3000:])
    return p.stdout


def transfer(config,source,destination,manifest,directory,label,seconds=1800):
    """Enforce wire/time ceilings and independent sender/relay/receiver SHA256 equality."""
    config=Path(config);root=config.parent;cfg=json.loads(config.read_text());nodes=cfg['nodes'];m=json.loads(Path(manifest).read_text());names(m)
    if destination not in nodes or source not in ['mac',*nodes]or destination==source or not label or Path(label).name!=label:raise ValueError('Explicit safe transfer scope required')
    prior=list(root.glob('transport-*.json'));used=0
    for p in prior:
        x=json.loads(p.read_text())
        if x.get('kind')=='E021 actual transport ledger':used+=x['stream']['bytes']
    cap=CAP-used
    if cap<=0 or sum(x['bytes']for x in m['files'].values())+1024**2>cap:raise ValueError('Remaining aggregate 20 GiB transport cap insufficient')
    receipt=root/('transport-'+label+'.json')
    if receipt.exists():raise FileExistsError('Fresh recorded transport required; never repeat accepted copy')
    start=time.time();stop=min(start+seconds,cfg['deadline_epoch']-120);processes=[];h=hashlib.sha256();count=0;result=dict(kind='E021 actual transport ledger',label=label,source=source,destination=destination,started_epoch=start,status='FAILED',stream=dict(bytes=0,sha256=h.hexdigest()),remaining_before_bytes=cap)
    def alarm(*_):raise TimeoutError('Bounded transport/common clock exhausted')
    previous=signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,max(.001,stop-time.time()))
    def put(node,path,value):
        code='import json,sys;from pathlib import Path;p=Path('+repr(path)+');v=json.load(sys.stdin);f=p.open("x");json.dump(v,f);f.write("\\n");f.close()';remote(node,code,value)
    try:
        endpoints={};scripts={}
        for role in set([destination]+([]if source=='mac'else[source])):
            n=nodes[role];mp=n['root']+'/transport-'+label+'-manifest.json';put(n,mp,m);scripts[role]=n.get('transport_script',n['repo']+'/scripts/e021_portable_transport.py');endpoints[role]=dict(manifest=mp,receipt=n['root']+'/transport-'+label+('-sent.json'if role==source else'-received.json'))
        d=nodes[destination];e=endpoints[destination];argv=['/usr/bin/python3','-I','-B',scripts[destination],'receive','--manifest',e['manifest'],'--receipt',e['receipt'],'--destination',directory,'--cap',str(cap)]
        if d.get('transport_budget'):argv+=['--budget-config',d['root']+'/config.json']
        recvlog=(root/(label+'-receiver.stderr')).open('xb');recv=subprocess.Popen(d.get('bulk_ssh',d['ssh'])+[shlex.join(argv)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=recvlog,start_new_session=True);processes.append(recv)
        if source=='mac':
            sr=root/(label+'-sender.json');sargv=[sys.executable,'-I','-B',str(Path(__file__).with_name('e021_portable_transport.py')),'send','--manifest',str(Path(manifest).absolute()),'--receipt',str(sr),'--cap',str(cap)]
        else:
            n=nodes[source];e=endpoints[source];sargv=n.get('bulk_ssh',n['ssh'])+[shlex.join(['/usr/bin/python3','-I','-B',scripts[source],'send','--manifest',e['manifest'],'--receipt',e['receipt'],'--cap',str(cap)])]
        sendlog=(root/(label+'-sender.stderr')).open('xb');send=subprocess.Popen(sargv,stdout=subprocess.PIPE,stderr=sendlog,start_new_session=True);processes.append(send);last=time.time()
        while True:
            b=send.stdout.read(1024**2)
            if not b:break
            count+=len(b)
            if count>cap:raise ValueError('Aggregate transport byte ceiling exceeded')
            h.update(b);recv.stdin.write(b)
            if time.time()-last>15:
                (root/(label+'-progress.json')).write_text(json.dumps(dict(epoch=time.time(),bytes=count,elapsed=time.time()-start))+'\n');last=time.time()
        recv.stdin.close();send.wait(timeout=max(.1,stop-time.time()));recv.wait(timeout=max(.1,stop-time.time()))
        if send.returncode or recv.returncode:raise RuntimeError('Sender/receiver exit '+str((send.returncode,recv.returncode)))
        sender=json.loads(sr.read_text())if source=='mac'else json.loads(remote(nodes[source],'from pathlib import Path;print(Path('+repr(endpoints[source]['receipt'])+').read_text())'))
        receiver=json.loads(remote(d,'from pathlib import Path;print(Path('+repr(endpoints[destination]['receipt'])+').read_text())'));proof=paired(sender,receiver,dict(bytes=count,sha256=h.hexdigest()));result.update(status='PASS',pairing=proof,sender=sender,receiver=receiver)
    except BaseException as e:result['error']=repr(e);raise
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)
        for p in processes:
            if p.poll()is None:
                try:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=10)
                except ProcessLookupError:pass
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=10)
        result.update(stream=dict(bytes=count,sha256=h.hexdigest()),ended_epoch=time.time(),seconds=time.time()-start)
        with receipt.open('x')as f:json.dump(result,f,indent=2);f.write('\n')
    print('E021_TRANSPORT_PASS',label,count,round(time.time()-start,3),flush=True);return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);p.add_argument('--source',choices=['mac','cpu','gpu'],required=True);p.add_argument('--destination',choices=['cpu','gpu'],required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--directory',required=True);p.add_argument('--label',required=True);p.add_argument('--seconds',type=int,default=1800);a=p.parse_args();transfer(a.config,a.source,a.destination,a.manifest,a.directory,a.label,a.seconds)
