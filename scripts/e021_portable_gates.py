#!/usr/bin/env python3
"""Native engineering gates for portable E021; never score or fit communities.

Checks exact owned runtime/source in isolated native families, CPU/GPU float32
parity, real synthetic training and source-blind extraction cost. Truth is absent.
A separate release must admit all gates and the complete execution envelope.
"""
import argparse,hashlib,importlib.metadata as metadata,json,os,platform,re,site,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding,write_json


def inventory(config,recipe,output):
    """Check complete actual distributions, 43 installed sources and native libraries."""
    c=json.loads(Path(config).read_text());r=json.loads(Path(recipe).read_text());prefix=Path(sys.prefix).absolute();repo=Path(c['repo'])
    if platform.system()!='Linux'or platform.python_version()!='3.10.15'or site.ENABLE_USER_SITE or not sys.flags.isolated or not sys.dont_write_bytecode:raise ValueError('Owned isolated Linux Python 3.10.15 required')
    norm=lambda x:re.sub('[-_.]+','-',x.lower());expected={norm(n):v['version']for n,v in r['wheels'].items()};expected['dl-binner']='0.1.0.dev8';actual={};locations={}
    for d in metadata.distributions():
        n=norm(d.metadata['Name']);loc=Path(d._path).resolve()
        if n in actual or not loc.is_relative_to(prefix.resolve()):raise ValueError('Duplicate/foreign distribution '+n)
        actual[n]=d.version;locations[n]=str(loc)
    if actual!=expected:raise ValueError('Complete native inventory differs: '+str({n:(expected.get(n),actual.get(n))for n in expected.keys()|actual.keys()if expected.get(n)!=actual.get(n)}))
    import dl_binner
    package=Path(dl_binner.__file__).parent;source={str(p.relative_to(package)):binding(p)for p in package.rglob('*')if p.is_file()and p.suffix in ['.py','.json']};lock=json.loads((repo/'experiments/E021-frozen-sequence-hybrid/candidate-lock.json').read_text())
    if source!=lock['package_files']:raise ValueError('Installed 43 source/default members differ')
    groups={};libraries={}
    for label,mods in dict(tensor=['dl_binner','torch','numpy','transformers','tokenizers','einops'],graph=['scipy','sklearn','numba','pynndescent','igraph','leidenalg'],markers=['pyrodigal','pyhmmer','archspec']).items():
        code='''import importlib,json,sys
from pathlib import Path
origins={n:str(Path(importlib.import_module(n).__file__).resolve())for n in sys.argv[1].split(',')}
if any(not Path(p).is_relative_to(Path(sys.prefix).resolve())for p in origins.values()):raise ValueError('Foreign import')
if 'torch'in sys.modules:
 t=sys.modules['torch'];t.set_num_threads(4);t.set_num_interop_threads(1)
 if (t.version.cuda is None)!=(sys.argv[2]=='cpu'):raise ValueError('Wrong CPU/CUDA runtime')
 if sys.argv[2]=='gpu'and(not t.cuda.is_available()or t.cuda.device_count()!=1):raise ValueError('One native CUDA GPU required')
if 'numba'in sys.modules:sys.modules['numba'].set_num_threads(4)
from threadpoolctl import threadpool_info
pools=threadpool_info()
if any(p['num_threads']>4 for p in pools):raise ValueError('Native numerical pool exceeds four')
if any(p['prefix']=='libiomp'for p in pools)and any(p['prefix']=='libomp'for p in pools):raise ValueError('Conflicting OpenMP families')
print(json.dumps(dict(origins=origins,pools=pools)))'''
        p=subprocess.run([sys.executable,'-I','-B','-c',code,','.join(mods),c['role']],check=True,text=True,capture_output=True,timeout=240);g=json.loads(p.stdout.splitlines()[-1]);groups[label]=g
        for pool in g['pools']:
            alias=Path(pool['filepath']);target=alias.resolve(strict=True);libraries[str(alias)]=dict(resolved=str(target),binding=binding(target))
        print('NATIVE_OWNED_IMPORT_GROUP_PASS',label,flush=True)
    subprocess.run([str(prefix/'bin/dl-binner'),'--help'],check=True,cwd=Path(c['root'])/'tmp')
    write_json(output,dict(status='PASS',role=c['role'],python=sys.executable,prefix=str(prefix),python_version=platform.python_version(),distributions=actual,locations=locations,source=source,groups=groups,loaded_library_aliases=libraries,recipe=binding(recipe),complete_independent_owned=True))


def parity(model,pin,output):
    """Compare real unchanged author-reference float32 extraction on CPU and CUDA."""
    import numpy as np,torch
    from dl_binner.hybrid.extract import Extractor
    from dl_binner.model import configure_torch
    configure_torch(4);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.cuda.set_per_process_memory_fraction(13*1024**3/torch.cuda.get_device_properties(0).total_memory)
    rng=np.random.default_rng(718);rows=[('own-parity-'+str(i),''.join(rng.choice(list('ACGT'),n)))for i,n in enumerate([503,1001,4001])];rows.append(('own-parity-IUPAC','ACGTRYSWKMBDHVN'*41));x=Extractor(model,pin,'cpu');a,ad=x.extract(rows);del x;x=Extractor(model,pin,'cuda');b,bd=x.extract(rows);cos=(a*b).sum(1)/(np.linalg.norm(a,axis=1)*np.linalg.norm(b,axis=1));ok=np.allclose(a,b,rtol=1e-4,atol=1e-5)and float(cos.min())>=.99999
    result=dict(status='PASS'if ok else'FAIL',raw_rtol=1e-4,raw_atol=1e-5,minimum_required_cosine=.99999,observed_cosine=cos.tolist(),maximum_absolute_difference=float(abs(a-b).max()),CPU_GPU_details_identical=ad==bd,attention=x.attention_backend,precision='float32; TF32/autocast disabled',original_Mac_tolerance_unchanged=True)
    write_json(output,result)
    if not ok or ad!=bd:raise ValueError('Prospective CPU/GPU numerical parity failed; no tolerance change')


def tiny_plan(config,output):
    """Bind generated own DNA/HMM to the actual frozen stage interface in both modes."""
    c=json.loads(Path(config).read_text());repo=Path(c['repo']);root=Path(c['root']);fixture=root/'gates/own-DNA';p=json.loads((repo/'experiments/E021-frozen-sequence-hybrid/native-plan-template.json').read_text().replace('@REPO@',str(repo)).replace('@RUN_ROOT@',str(root)))
    py=sys.executable;p.update(work=str(root/'gates/tiny-work'),python=py,model_directory=str(root/'payload/model'),extract_device='cuda',config=str(fixture/'config.json'),base_config=str(fixture/'base-config.json'),hmm=str(fixture/'synthetic.hmm'))
    for unit,mode in [('E009-hybrid','depth'),('oral-hybrid','sequence')]:p['units'][unit]=dict(fasta=str(fixture/'assembly.fna'),features=str(fixture/mode/'features.npz'),views=str(fixture/mode/'views.npz'),tokens=str(fixture/mode/'tokens'),marker_cache=str(fixture/'markers'),bank_reuse_from=None if mode=='depth'else'E009-hybrid')
    # Fixture asset's exact generated name is bound without another detector run.
    hmm=list(fixture.glob('*.hmm'))
    if len(hmm)!=1:raise ValueError('One real synthetic HMM required')
    p['hmm']=str(hmm[0]);write_json(output,p)


def throughput(plan,output):
    """Time source-blind actual parent/crop strata and forecast all unchanged exposure."""
    import numpy as np,torch
    from dl_binner.hybrid.extract import Extractor
    from dl_binner.multiview.views import load,fasta_rows
    from dl_binner.model import configure_torch
    configure_torch(4);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False;torch.cuda.set_per_process_memory_fraction(13*1024**3/torch.cuda.get_device_properties(0).total_memory)
    p=json.loads(Path(plan).read_text());extractor=Extractor(p['model_directory'],p['model_pin'],'cuda');results={};bounds=[1,500,1000,2000,4000,8000,16000,64000,2**63-1];total_upper=0
    expected_axes={'E009-hybrid':(145702,89041),'oral-hybrid':(1286547,508763)}
    locked=json.loads(Path(p['candidate_lock']).read_text())
    for unit,u in p['units'].items():
        data,meta,v,vm=load(u['features'],u['views']);eligible=data['eligible'];strata=[];chosen={};n=len(data['ids'])
        if(n,int(eligible.sum()))!=expected_axes[unit]or meta['samples']!=(locked['ordered_depth_columns']if unit=='E009-hybrid'else[]):raise ValueError('Full contig/ordered sample axes differ')
        if binding(u['fasta'])['sha256']!=meta['fasta_sha256']:raise ValueError('Actual transported FASTA differs')
        for j in range(5):
            lengths=data['lengths']if not j else v['coordinates'][:,j-1,1]-v['coordinates'][:,j-1,0];valid=eligible if not j else eligible&v['usable'][:,j-1]
            for lo,hi in zip(bounds[:-1],bounds[1:]):
                ix=np.flatnonzero(valid&(lengths>=lo)&(lengths<hi))
                if not len(ix):continue
                selected=np.unique(np.concatenate([ix[np.linspace(0,len(ix)-1,min(3,len(ix)),dtype=int)],[ix[np.argmax(lengths[ix])]]])).tolist();z=dict(view=j,minimum_bp=lo,maximum_bp_exclusive=hi,views=len(ix),exposed_bp=int(lengths[ix].sum()),selected_rows=selected,observations=[]);strata.append(z)
                for i in selected:chosen.setdefault(i,[]).append((j,z))
        seen=0
        for i,(ident,dna)in enumerate(fasta_rows(u['fasta'])):
            if i>=n or ident!=data['ids'][i]or hashlib.sha256(dna.encode()).hexdigest()!=data['sequence_sha256'][i]:raise ValueError('Full transported DNA/order differs')
            seen+=1
            for j,z in chosen.get(i,[]):
                a,b=(0,len(dna))if not j else map(int,v['coordinates'][i,j-1]);s=dna[a:b];h=hashlib.sha256(s.encode()).hexdigest()
                if j and h.encode()!=v['sequence_sha256'][i,j-1]:raise ValueError('Retained crop differs')
                start=time.perf_counter();values,detail=extractor.extract([(ident+':view:'+str(j),s)]);elapsed=time.perf_counter()-start
                if values.shape!=(1,768)or not np.isfinite(values).all():raise ValueError('Native representative extraction invalid')
                z['observations'].append(dict(row=i,view=j,start=a,end=b,sha256=h,seconds=elapsed,chunks=detail[0]['chunks'],tokens=sum(detail[0]['tokens'])))
                print('NATIVE_STRATUM_TIMING',unit,i,j,len(s),round(elapsed,4),flush=True)
        if seen!=n:raise ValueError('Truncated full FASTA')
        upper=0
        for z in strata:
            obs=z['observations'];point=z['views']*sum(x['seconds']for x in obs)/len(obs);bp_upper=z['exposed_bp']*max(x['seconds']/(x['end']-x['start'])for x in obs);z['point_seconds']=point;z['planning_upper_seconds']=1.5*max(point,bp_upper);upper+=z['planning_upper_seconds']
        results[unit]=dict(full_contigs=n,eligible=int(eligible.sum()),ordered_samples=meta['samples'],available_views=sum(x['views']for x in strata),exposed_bp=sum(x['exposed_bp']for x in strata),strata=strata,planning_upper_seconds=upper);total_upper+=upper
        del data,v
    write_json(output,dict(status='MEASURED_NOT_AUTOMATIC_RELEASE',units=results,total_extraction_planning_upper_seconds=total_upper,scope='Label-free length/coordinate stratified native float32 timing, 1.5 multiplier; forecast is not a statistical upper guarantee; full live guards still apply'))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['inventory','parity','tiny-plan','throughput']);p.add_argument('--config',type=Path);p.add_argument('--recipe',type=Path);p.add_argument('--plan',type=Path);p.add_argument('--model',type=Path);p.add_argument('--pin',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.operation=='inventory':inventory(a.config,a.recipe,a.output)
    elif a.operation=='parity':parity(a.model,a.pin,a.output)
    elif a.operation=='tiny-plan':tiny_plan(a.config,a.output)
    else:throughput(a.plan,a.output)
