#!/usr/bin/env python3
"""Stress full retained input shapes plus synthetic full-shape GLM maps on CPU.

Uses actual retained feature/view/context readers and unchanged head operations.
Synthetic GLM values and discarded engineering updates are NOT community fits,
real frozen features, stability/quality evidence or a replacement bank. Full actual
Bank validation remains required after extraction and before any scientific fit.
"""
import argparse,json,math,os,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import write_json


def probe(plan,output,scratch):
    """Measure full input coexistence and worst available-view training-batch resources."""
    import numpy as np,torch
    from torch.nn import functional as F
    from dl_binner.hybrid.model import initialize,forward_args
    from dl_binner.hybrid.bank import Bank as FrozenBank
    from dl_binner.context.tokens import Bank as ContextBank
    from dl_binner.multiview.views import load
    from dl_binner.candidate.model import fit_transform,transform
    from dl_binner.multiview.model import parent_average
    from dl_binner.multiview.positive import pair_loss,update_target
    from dl_binner.model import configure_torch
    configure_torch(4);p=json.loads(Path(plan).read_text());cfg=json.loads(Path(p['config']).read_text());scratch=Path(scratch);scratch.mkdir(exist_ok=False);results={}
    class Synthetic:
        """Call actual bounded FrozenBank methods on declared disposable NPY arrays."""
        fit=FrozenBank.fit;batch=FrozenBank.batch
    for unit,u in p['units'].items():
        start=time.time();data,meta,v,vm=load(u['features'],u['views']);context=ContextBank(u['tokens'],u['features'],u['views'],data,meta,v);ix=np.flatnonzero(data['eligible']);n=len(ix);path=scratch/(unit+'.npy');b=Synthetic();b.rows=ix;b.lookup=np.full(len(data['ids']),-1,np.int64);b.lookup[ix]=np.arange(n);b.usable=np.concatenate([np.ones((n,1),bool),v['usable'][ix]],1);b.quality=np.zeros((n,5,2),np.float32);b.quality[...,0]=b.usable*.5;b.values=np.lib.format.open_memmap(path,mode='w+',dtype=np.float32,shape=(n,5,768))
        base=np.linspace(-1,1,768,dtype=np.float32)
        for a in range(0,n,1024):
            k=min(n,a+1024);block=base[None,None,:]+((np.arange(a,k)%101).astype(np.float32)/101)[:,None,None];b.values[a:k]=block;b.values[a:k][~b.usable[a:k]]=0
        b.values.flush();metadata_proxy=bytearray(int(b.usable.sum())*224)
        # Touch proxy pages: it upper-budgets Python seen-set/tuple metadata, not labels.
        for a in range(0,len(metadata_proxy),4096):metadata_proxy[a]=1
        state=fit_transform(data);state['hybrid']=b.fit();parent,depth=transform(data['tnf'],data['depth'],data['depth_evidence'],state);torch.manual_seed(11);model,target,predictors=initialize(len(meta['samples']),cfg);opt=torch.optim.AdamW(list(model.parameters())+list(predictors.parameters()),lr=cfg['learning_rate'],weight_decay=cfg['weight_decay']);rng=np.random.default_rng(11);pool=ix[v['usable'][ix].all(1)];pool=pool if len(pool)>=256 else ix;times=[]
        for step in range(16):
            selected=rng.choice(pool,min(256,len(pool)),replace=False);n_batch=len(selected);t=time.perf_counter();s0,d0,m0=parent[selected],depth[selected],data['depth_evidence'][selected];global_views=[s0]+[transform(v['tnf'][selected,j],data['depth'][selected],m0,state)[0]for j in range(4)];available=np.concatenate([np.ones(n_batch,bool)]+[v['usable'][selected,j]for j in range(4)]);owners_np=np.tile(np.arange(n_batch),5)[available];vn=np.repeat(np.arange(5),n_batch)[available];sv=np.tile(selected,5)[available];sequence=np.concatenate(global_views)[available];observed_depth=np.tile(d0,(5,1))[available];original_mask=np.tile(m0,5)[available];mask=original_mask&(rng.random(len(owners_np))>=cfg['depth_dropout']);owners=torch.from_numpy(owners_np);weights=torch.ones(n_batch);args=forward_args(sequence,observed_depth,mask,(context,b),sv,vn,state);f,s=model(*args)
            with torch.no_grad():tf,ts=target(*args)
            pf=pair_loss(f,tf,owners,weights,predictors[0]);ps=pair_loss(s,ts,owners,weights,predictors[1]);wanted=torch.from_numpy(s0)[owners];rc=parent_average(((F.normalize(model.composition_decoder(f),dim=1)-wanted).square().sum(1)+(F.normalize(model.composition_decoder(s),dim=1)-wanted).square().sum(1))*.5,owners,weights);rd=f.sum()*0;valid=torch.from_numpy(original_mask);usable=np.asarray(state['depth']['std'])>1e-8
            if model.depth_decoder is not None and usable.any()and valid.any():rd=parent_average(F.smooth_l1_loss(model.depth_decoder(f)[valid][:,usable],torch.from_numpy(observed_depth)[valid][:,usable],reduction='none').mean(1),owners[valid],weights)
            loss=pf+cfg['sequence_loss_weight']*ps+cfg['composition_reconstruction_weight']*rc+cfg['depth_reconstruction_weight']*rd;opt.zero_grad(set_to_none=True);loss.backward()
            if not torch.isfinite(loss)or any(x.grad is not None and not torch.isfinite(x.grad).all()for x in model.parameters()):raise ValueError('Engineering stress numerical failure')
            opt.step();update_target(model,target,cfg['ema_base']);times.append(time.perf_counter()-t);print('FULL_SHAPE_RESOURCE_PROBE',unit,step+1,round(times[-1],4),flush=True)
        result=dict(full_contigs=len(data['ids']),eligible=len(ix),samples=meta['samples'],synthetic_GLM_shape=list(b.values.shape),synthetic_GLM_file_bytes=path.stat().st_size,metadata_proxy_bytes=len(metadata_proxy),batch_parents=n_batch,batch_seconds=times,full_20_epoch_training_upper_seconds=1.5*max(times[2:])*20*math.ceil(len(ix)/256),setup_reader_seconds=time.time()-start,actual_retained_context_reader=True,actual_FrozenBank_fit_batch_methods=True,actual_complete_new_FrozenBank_reader=False,discarded_engineering_updates=16);results[unit]=result
        del model,target,predictors,opt,args,context,b,parent,depth,state,metadata_proxy,data,v;path.unlink();print('DISPOSABLE_SYNTHETIC_MAP_REMOVED',unit,flush=True)
    write_json(output,dict(status='PASS_ENGINEERING_FULL_SHAPE_ONLY',units=results,total_training_upper_seconds=sum(x['full_20_epoch_training_upper_seconds']for x in results.values()),real_community_fit=False,actual_bank_validation_still_required=True,scope='Actual retained inputs/contexts plus synthetic mapped GLM and 224 bytes/view metadata proxy; no checkpoint or scientific embedding is produced'))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--scratch',type=Path,required=True);a=p.parse_args();probe(a.plan,a.output,a.scratch)
