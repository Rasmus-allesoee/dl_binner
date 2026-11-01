#!/usr/bin/env python3
"""Native 128-original-view equivalence and timing, without community extraction.

Both recipes share one immutable float32 model. Exact token/chunk/strand/QC,
frozen raw-vector tolerance and cosine are required; failed arrays stay evidence.
"""
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def run(model,cohort,manifest,output):
    """Compare real original and batched DNABERT-S exposure on the frozen cohort."""
    from e029_control import product_scope
    product_scope()
    import numpy as np,torch
    from dl_binner.hybrid.extract import Extractor
    from dl_binner.hybrid.batched import BatchedExtractor,execution_policy,planned_chunks
    from dl_binner.hybrid.bank import model_pin
    from dl_binner.model import configure_torch
    out=Path(output);out.mkdir(exist_ok=False);m=json.loads(Path(manifest).read_text());c=json.loads(Path(cohort).read_text())
    if m['status']!='FROZEN_BEFORE_GPU_OUTPUTS'or m['cohort']!=binding(cohort)or len(c['rows'])!=128 or c['count']!=128:raise ValueError('Frozen 128-view source cohort differs')
    configure_torch(4);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    if not torch.cuda.is_available()or torch.cuda.device_count()!=1:raise ValueError('One native GPU required')
    torch.cuda.set_per_process_memory_fraction(13*1024**3/torch.cuda.get_device_properties(0).total_memory)
    pin=Path(model)/'pin.json';write(pin,model_pin())
    old=Extractor(model,pin,'cuda');new=object.__new__(BatchedExtractor);new.__dict__=old.__dict__.copy()
    rows=[(z['id'],z['dna'])for z in c['rows']]
    for z in c['rows']:
        import hashlib
        if hashlib.sha256(z['dna'].encode()).hexdigest()!=z['sha256']or z['bp']!=len(z['dna']):raise ValueError('Retained view DNA differs')
        parts=planned_chunks(z['dna'],old.tokenizer)
        if [[a,b]for a,b,pair in parts]!=z['chunks']or[len(t['input_ids'])for a,b,pair in parts for t in pair]!=z['tokens']:raise ValueError('Original tokenizer/chunk manifest differs')
    shortest=min(rows,key=lambda z:len(z[1]));start=time.perf_counter();old.extract([shortest]);new.extract([shortest]);torch.cuda.synchronize();warm=time.perf_counter()-start
    observations=[];phase=['unassigned']
    def hook(module,args,kwargs):
        ids=kwargs['input_ids'];mask=kwargs['attention_mask'];observations.append(dict(recipe=phase[0],shape=list(ids.shape),attended_tokens=int(mask.sum()),padded_tokens=int(ids.numel()-mask.sum())))
    handle=old.model.register_forward_pre_hook(hook,with_kwargs=True)
    phase[0]='original';torch.cuda.reset_peak_memory_stats();start=time.perf_counter();a,ad=old.extract(rows);torch.cuda.synchronize();old_seconds=time.perf_counter()-start;old_peak=torch.cuda.max_memory_allocated()
    phase[0]='batched';torch.cuda.reset_peak_memory_stats();start=time.perf_counter();values=[];details=[];queue=[];bp=0
    def flush():
        if queue:
            x,d=new.extract(queue);values.append(x);details.extend(d);queue.clear()
    for row in rows:
        if queue and(len(queue)==64 or bp+len(row[1])>2000000):flush();bp=0
        queue.append(row);bp+=len(row[1])
    flush();torch.cuda.synchronize();new_seconds=time.perf_counter()-start;new_peak=torch.cuda.max_memory_allocated();handle.remove();b=np.concatenate(values)
    np.savez(out/'vectors.npz',original=a,batched=b)
    cos=(a.astype(np.float64)*b).sum(1)/(np.linalg.norm(a.astype(np.float64),axis=1)*np.linalg.norm(b.astype(np.float64),axis=1));maximum=float(abs(a-b).max())
    ok=np.isfinite(a).all()and np.isfinite(b).all()and np.allclose(a,b,rtol=1e-5,atol=1e-6)and maximum<=1e-5 and float(cos.min())>=.999999 and ad==details
    result=dict(status='PASS_REFERENCE_EQUIVALENCE_AND_THROUGHPUT'if ok else'FAILED_FROZEN_NUMERICAL_ADMISSION',model=model_pin(),execution_policy=execution_policy(),extractor_source=binding(ROOT/'src/dl_binner/hybrid/batched.py'),cohort=binding(cohort),manifest=binding(manifest),
        warmup_seconds=warm,original_seconds=old_seconds,batched_seconds=new_seconds,speedup=old_seconds/new_seconds,original_peak_VRAM_bytes=old_peak,batched_peak_VRAM_bytes=new_peak,
        actual_gpu=torch.cuda.get_device_name(),torch=torch.__version__,CUDA=torch.version.cuda,maximum_absolute_error=maximum,minimum_cosine=float(cos.min()),allclose_rtol=1e-5,allclose_atol=1e-6,maximum_allowed_error=1e-5,minimum_required_cosine=.999999,
        details_identical=ad==details,reference_details=ad,batched_details=details,batches=observations,full_Oral_bank_extracted=False,community_fits=0,precision='float32; unchanged author reference attention; TF32/autocast disabled',old_Mac_failure_and_tolerance_unchanged=True)
    write(out/'admission.json',result);print(json.dumps({k:v for k,v in result.items()if k not in ['model','reference_details','batched_details','batches']}),flush=True)
    if not ok:raise ValueError('Frozen native batched equivalence failed; no tolerance/recipe change')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['model','cohort','manifest','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--gpu',choices=['L4','T4'],required=True);p.add_argument('--deadline',type=float,required=True)
    a=p.parse_args()
    from e021_gpu_guard import GPUPhaseGuard
    from e021_portable_node import sample_gpu
    monitor=a.output.parent/'gpu-monitor';monitor.mkdir()
    with GPUPhaseGuard(monitor,a.deadline-time.time(),reserve_bytes=10*1024**3,growth_bytes=20*1024**3,sampler=lambda:sample_gpu(a.gpu)):
        run(a.model,a.cohort,a.manifest,a.output)
