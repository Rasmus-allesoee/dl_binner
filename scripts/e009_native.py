"""Pinned native E009 configuration and isolated operational adaptations.

Only CompleteBin's max-50 schedule changes science. Loader/resource adaptations
are explicit and byte-bound. These command plans do not themselves authorize a
fit; scientific launch requires reviewed inputs, Linux contracts and affordability.
"""
import argparse
import ast
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import runpy
import multiprocessing
import sys
sys.path.insert(0, str(Path(__file__).absolute().parent))

from e009_common import binding, fasta, write_json


def patch_completebin(source, expected_sha):
    """Change just the upstream 200-epoch maximum to 50 in a fresh E009 copy.

    This preserves the native data-dependent schedule and subsequent lower safety
    valve. The cap affects the automatic pretraining overfitting score too; record
    that consequence. Refuse drift/already-patched bytes, never edit a cache.
    """
    path=Path(source)/'CompleteBin/Binning_steps.py'
    if binding(path)['sha256']!=expected_sha:raise ValueError('CompleteBin source anchor changed')
    text=path.read_text();old='        if train_epoch > 200:\n            train_epoch = 200\n'
    new='        if train_epoch > 50:\n            train_epoch = 50\n'
    if text.count(old)!=1:raise ValueError('CompleteBin epoch anchor not unique')
    path.write_text(text.replace(old,new))
    return {'before_sha256':expected_sha,'after':binding(path),'change':'200 maximum -> 50; modified E009 configuration, not native parity',
            'automatic_pretraining_score_uses_capped_epochs':True,'early_stopping':'no validation-loss early stop in contrastive training; lower native safety valve retained'}


def patch_scgbinner(source, expected_sha):
    """Replace two removed NumPy aliases with the equivalent integer dtype in E009 only."""
    path=Path(source)/'SCGBinner/utils.py'
    if binding(path)['sha256']!=expected_sha:raise ValueError('SCGBinner source anchor changed')
    text=path.read_text()
    if text.count('dtype=np.int)')!=2:raise ValueError('SCGBinner NumPy alias anchor changed')
    path.write_text(text.replace('dtype=np.int)','dtype=int)'))
    return {'before_sha256':expected_sha,'after':binding(path),'change':'two np.int dtype aliases -> int; same native integer dtype, no scientific settings change'}


def resolved_epochs(source, n50, num_contigs, base_epoch=35):
    """Execute the actual isolated upstream scheduler AST, without a community fit.

    Tests changed production epoch assignments at small/large sizes. Does not mock
    a trainer and claim training validation; automatic safety/pretraining remains
    separately recorded and is tested through its real source module.
    """
    if num_contigs<=0:raise ValueError('No effective training contigs')
    text=(Path(source)/'CompleteBin/Binning_steps.py').read_text()
    start=text.index('        if N50 >= 1536:');end=text.index('        # ---- Automatic pretrained model decision ----',start)
    block=text[start:end]
    lines=[line[8:] for line in block.splitlines() if 'sampler =' not in line and 'num_contigs =' not in line]
    nodes=ast.parse(text)
    threshold=next(n.value.value for n in ast.walk(nodes) if isinstance(n,ast.Assign)
                   and any(isinstance(t,ast.Name) and t.id=='large_data_size_thre' for t in n.targets)
                   and isinstance(n.value,ast.Constant))
    node=ast.parse('\n'.join(lines));namespace={'N50':n50,'num_contigs':num_contigs,
                                               'base_epoch':base_epoch,'large_data_size_thre':threshold}
    exec(compile(node,'actual-CompleteBin-epoch-block','exec'),namespace)
    return namespace['train_epoch']


def cpu_plan(tool, threads):
    """Declare active process/thread budgets, including loaders and native extra workers."""
    if threads<4:raise ValueError('E009 native adapters require >=4 CPUs; owner preflight is eight')
    if tool=='comebin':return {'torch_threads':threads,'loader_workers':0,'pool_workers':threads-1,'blas_threads':1,
            'phase_note':'HNSW numerical phase N; Leiden N-1 workers plus coordinator; HMM master included'}
    if tool=='scgbinner':return {'torch_threads':threads,'loader_workers':0,'pool_workers':threads-1,'blas_threads':1}
    if tool=='completebin':return {'torch_threads':threads,'loader_workers':0,'pool_workers':threads-2,'blas_threads':1,
            'phase_note':'two BAMs use one coverage process, BGZF N-2 + its main + coordinator; HMM N-2 workers + master/coordinator'}
    if tool=='metacat':return {'torch_threads':0,'loader_workers':0,'pool_workers':threads-1,'blas_threads':1,
            'phase_note':'affinity completes before LP tasks; scoring waits LP.join; five score workers; waiting pools not concurrent CPU phases'}
    if tool=='semibin':return {'torch_threads':threads,'loader_workers':0,'pool_workers':threads-1,'blas_threads':1,
            'phase_note':'two BAM coverage workers are single-thread numerical; native torch phase uses N; self-supervised only'}
    raise ValueError('Unknown selected tool')


def command_plan(tool, source, reference, bams, output, threads, db=None):
    """Return argv/config for selected native stages; truth is never an argument.

    Preserve upstream seeds/defaults except named CompleteBin maximum. Shell
    convenience wrappers are avoided where their unquoted paths/default workers
    fail the declared contract. Inputs still use native readers/extractors.
    """
    source,output=Path(source),Path(output);plan=cpu_plan(tool,threads)
    if len(bams)!=2 or len(set(map(str,bams)))!=2:raise ValueError('Two distinct ordered BAM samples required')
    if any(any(c.isspace() for c in str(p)) for p in bams):
        raise ValueError('COMEBin/SCGBinner native BAM-list parser requires paths without whitespace')
    shared={'tool':tool,'source':str(source),'reference':str(reference),'ordered_bams':list(map(str,bams)),
            'output':str(output),'resource_plan':plan,'truth_inputs':[],'scientific_execution_authorized':False}
    if tool=='semibin':
        shared['stages']=[['single_easy_bin','-i',str(reference),'-b',*map(str,bams),'-o',str(output),
                           '-p',str(threads),'--engine','cpu','--self-supervised','--sequencing-type','short_read']]
    elif tool=='metacat':
        t=plan['pool_workers'];shared['stages']=[
            ['coverage','--bam',*map(str,bams),'--output',str(output/'coverage'),'-ti',str(t),'-tc',str(t)],
            ['seed','--fasta',str(reference),'--output',str(output/'seed'),'-t',str(t),
             '--hmmsearch','hmmsearch','--fraggenescan','FragGeneScan'],
            ['cluster','--fasta',str(reference),'--coverage',str(output/'coverage'),'--seed',str(output/'seed'),
             '--output',str(output/'metacat'),'-t',str(t),'--swdpgmm-engine','cpu']]
    elif tool=='scgbinner':
        lengths=sorted((len(seq) for _,seq in fasta(reference)),reverse=True);half=sum(lengths)/2;running=0
        for n50 in lengths:
            running+=n50
            if running>=half:break
        batch=min(1024,len(lengths));aug=output/'data_augmentation';res=output/'scgbinner_res'
        shared['stages']=[
            ['generate_aug_data','--contig_file',str(reference),'--out_augdata_path',str(aug),'--n_views','6',
             '--bam_file_path',' '.join(map(str,bams)),'--num_threads',str(plan['pool_workers'])],
            ['train','--data',str(aug),'--contig_file',str(reference),'--temperature',str(.07 if n50>10000 else .15),
             '--emb_szs_forcov','2048','--emb_szs','2048','--batch_size',str(batch),'--n_views','6',
             '--add_model_for_coverage','--remove_single_copy','128','--scg_batch_size','0','--output_path',str(res),
             '--earlystop','--addvars','--vars_sqrt','--num_threads',str(threads),'--workers','0','--epochs','200'],
            ['bin','--contig_file',str(reference),'--emb_file',str(res/'embeddings.tsv'),'--output_path',str(res),'--num_threads',str(plan['pool_workers'])],
            ['get_result','--contig_file',str(reference),'--output_path',str(res),'--num_threads',str(plan['pool_workers'])]]
    elif tool=='comebin':
        aug=output/'augmentation';res=output/'native'
        shared['bam_directory']=str(output/'bam-input')
        shared['stages']=[
            ['generate_aug_data','--contig_file',str(reference),'--out_augdata_path',str(aug),'--n_views','6',
             '--bam_file_path',shared['bam_directory'],'--num_threads',str(plan['pool_workers'])],
            ['train','--data',str(aug),'--output_path',str(res),'--epochs','200','--batch_size','1024',
             '--n_views','6','--addvars','--vars_sqrt','--earlystop','--device','cpu','--num_threads',str(threads)],
            ['bin','--contig_file',str(reference),'--emb_file',str(res/'embeddings.npy'),'--output_path',str(res),
             '--num_threads',str(threads),'--leiden_workers',str(plan['pool_workers'])],
            ['get_result','--contig_file',str(reference),'--emb_file',str(res/'embeddings.npy'),
             '--output_path',str(res),'--num_threads',str(plan['pool_workers'])]]
    else:
        if db is None:raise ValueError('CompleteBin needs its pinned database')
        shared['api']={'contig_file_path':str(reference),'sorted_bam_file_list':list(map(str,bams)),
            'temp_file_folder_path':str(output/'temporary'),'bin_output_folder_path':str(output/'bins'),
            'db_folder_path':str(db),'training_device':'cpu','cpu_workers':plan['pool_workers'],
            'gpu_dataloader_workers':0,'remove_temp_files':False,'base_epoch':35,'auto_disable_pretrain':True}
        shared['modified_epoch_maximum']=50
        shared['entrypoint']='CompleteBin.Binning_steps.binning_with_all_steps'
    return shared


def prepare_bam_directory(directory,bams):
    """Create COMEBin's native directory contract and verify resolved sample ordering.

    Native COMEBin sorts real paths, so numbered aliases alone cannot fix a wrong
    ordering. Refuse it before extraction and bind the original ordered BAM bytes.
    """
    directory=Path(directory);resolved=[Path(p).resolve() for p in bams]
    if resolved!=sorted(resolved) or len(set(resolved))!=2:raise ValueError('COMEBin resolved sample ordering differs from manifest')
    if len({p.name for p in resolved})!=2:raise ValueError('COMEBin emits real BAM basenames; samples need distinct basenames')
    directory.mkdir(parents=True,exist_ok=False)
    for i,path in enumerate(resolved):(directory/f'sample_{i}.bam').symlink_to(path)
    write_json(directory/'ordered-inputs.json',{'ordered_bams':[{'path':str(p),'file':binding(p)} for p in resolved]})


def validate_comebin_contigs(ids,lengths,sequences,threshold):
    """Require the native strict-greater-than length rule and exact FASTA order.

    COMEBin's manifest threshold 1000 excludes a 1000-bp contig. Validate emitted
    IDs/lengths against every eligible input, so missing or reordered native rows
    fail rather than silently changing the retained population.
    """
    ids,lengths=list(ids),list(lengths)
    if ids!=[name for name,seq in sequences.items() if len(seq)>threshold]:
        raise ValueError('COMEBin native eligibility/order differs from its declared threshold')
    if len(ids)!=len(lengths) or any(len(sequences[name])!=int(length) for name,length in zip(ids,lengths)):
        raise ValueError('COMEBin emitted contig axis/length differs')


def inspect_comebin_features(source,path,bams,reference):
    """Validate native emitted basename IDs, contig axes, intervals and zero masks.

    Resolve paths before checking their emitted basenames, preserving the complete
    ordered original-byte manifest. Does not generate features, train or score.
    """
    import numpy as np
    sys.path.insert(0,str(Path(source)/'COMEBin'))
    from feature_bundle import load_binary_feature_bundle
    bundle=load_binary_feature_bundle(path,n_views=6)
    expected=[p.name for p in map(lambda p:Path(p).resolve(),bams)]
    if list(bundle.bam_ids)!=expected:raise ValueError('COMEBin native sample axis differs from manifest')
    sequences=dict(fasta(reference))
    threshold=bundle.feature_manifest['contig_length_threshold']
    validate_comebin_contigs(bundle.contig_ids,bundle.contig_lengths,sequences,threshold)
    if not np.isfinite(bundle.coverage_mean).all() or not np.isfinite(bundle.coverage_var).all() or np.any(bundle.coverage_mean<0) or np.any(bundle.coverage_var<0):raise ValueError('COMEBin native features nonfinite/negative')
    return {'native_contig_ids':list(bundle.contig_ids),'native_sample_ids':list(bundle.bam_ids),
            'contig_length_threshold':threshold,'eligibility_comparison':'>',
            'ordered_bam_paths':list(map(str,bams)),'coverage_shape':list(bundle.coverage_mean.shape),
            'base_view_zero_rows_per_sample':[int((row==0).sum()) for row in bundle.coverage_mean[:,0,:]],
            'original_intervals':bundle.augmentation_intervals.tolist()}


def limit_hnsw(threads):
    """Bound SCGBinner's otherwise host-wide HNSW defaults without changing geometry."""
    import hnswlib
    original=hnswlib.Index
    class BoundedIndex(original):
        """Native index with an explicit allocation-bound thread default."""
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs);self.set_num_threads(threads)
    hnswlib.Index=BoundedIndex


def inventory(expected_prefix, modules, expected_freeze=None, dependency_prefix=None, expected_distributions=None, forbidden_prefix=None):
    """Probe complete installed distributions/origins and optional accepted full freeze.

    Invoke lexical Python -I -B. Full origins exclude inherited/user-site modules;
    freeze alone is insufficient. Explicit external inputs are bound before/after;
    restored numerical bytes are verified once by the chunk consumer. No install/upgrade runs in a reused prefix.
    """
    prefix=Path(sys.prefix).resolve()
    if prefix!=Path(expected_prefix).resolve():raise ValueError('Wrong lexical interpreter prefix')
    allowed=[prefix]+([Path(dependency_prefix).resolve()] if dependency_prefix else [])
    distributions=[]
    print('DLBINNER INVENTORY distribution scan begin',flush=True)
    for dist in importlib.metadata.distributions():
        origin=Path(dist.locate_file('')).resolve()
        if not any(origin.is_relative_to(p) for p in allowed):raise ValueError('Distribution outside isolated prefix/bound dependency prefix')
        print(f'DLBINNER INVENTORY metadata begin {getattr(dist,"_path",origin)}',flush=True)
        metadata=dist.metadata  # One shared-filesystem read, rather than reading twice.
        distributions.append({'name':metadata['Name'],'version':metadata['Version'],'origin':str(origin)})
        print(f'DLBINNER INVENTORY metadata ready {metadata["Name"]} {metadata["Version"]}',flush=True)
    origins={}
    for name in modules:
        print('DLBINNER INVENTORY import begin '+name,flush=True)
        module=__import__(name);origin=Path(module.__file__).resolve()
        if not any(origin.is_relative_to(p) for p in allowed):raise ValueError('Import outside isolated prefix/bound dependency prefix')
        origins[name]=str(origin)
        print('DLBINNER INVENTORY import ready '+name+' '+str(origin),flush=True)
    if expected_freeze:
        import subprocess
        from e009_startup import startup_argv
        print('DLBINNER INVENTORY pip freeze begin',flush=True)
        actual=subprocess.check_output(startup_argv(sys.executable,'pip',['freeze','--all'],mode='module'),text=True)
        if set(actual.splitlines())!=set(Path(expected_freeze).read_text().splitlines()):
            raise ValueError('Accepted complete prefix inventory changed')
        print('DLBINNER INVENTORY pip freeze ready',flush=True)
    if expected_distributions:
        import re
        normalize=lambda s:re.sub('[-_.]+','-',s).lower()
        actual={normalize(d['name']):d['version'] for d in distributions}
        expected={normalize(k):v for k,v in expected_distributions.items()}
        if len(actual)!=len(distributions) or actual!=expected:raise ValueError('Complete clean distribution inventory differs')
    execution_check=None
    if forbidden_prefix:
        # This is compatibility arithmetic, not training, inference on DNA or scores.
        import numpy as np
        a=np.arange(12,dtype=np.float64).reshape(3,4)
        if float((a@a.T).sum())!=1134:raise ValueError('Snapshot NumPy arithmetic failed')
        if 'torch' in modules:
            import torch
            torch.set_num_threads(1);torch.set_num_interop_threads(1)
            x=torch.arange(4,dtype=torch.float32,requires_grad=True)
            (x*x).sum().backward()
            if not torch.equal(x.grad,2*x.detach()):raise ValueError('Snapshot Torch backward failed')
        import sysconfig
        stdlib=Path(sysconfig.get_path('stdlib')).resolve()
        if not any(stdlib.is_relative_to(p) for p in allowed):raise ValueError('Snapshot uses unbound standard library')
        forbidden=str(Path(forbidden_prefix).resolve())+'/'
        mapped=[]
        if Path('/proc/self/maps').exists():
            mapped=[line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines() if '/' in line]
            if any(forbidden in path for path in mapped):raise ValueError('Snapshot loads original-prefix binary')
        execution_check={'numpy_matmul':True,'torch_backward':'torch' in modules,
                         'stdlib':str(stdlib),'mapped_files':sorted(set(mapped)),
                         'original_prefix_not_mapped':bool(mapped),
                         'native_mapping_check_available':bool(mapped)}
    return {'prefix':str(prefix),'python':sys.version,'distributions':distributions,'origins':origins,
            'python_executable_lexical':sys.executable,'user_site_isolated':True,
            'snapshot_execution_check':execution_check,
            'bytecode_policy':{'pycache_prefix':sys.pycache_prefix,'writes_disabled':sys.dont_write_bytecode}}


def invoke(tool, source, argv, threads):
    """Call the real selected tool entry point with explicit CPU/loader configuration."""
    source=Path(source)
    if tool in ('scgbinner','completebin','comebin','semibin'):
        import torch
        torch.set_num_threads(threads);torch.set_num_interop_threads(1)
        print('NATIVE_CPU_PLAN='+json.dumps(cpu_plan(tool,threads)),flush=True)
    if tool=='comebin':
        sys.path.insert(0,str(source/'COMEBin'))
        import train_CLmodel
        train_CLmodel.DATALOADER_WORKERS=0  # explicit operational override, no cache mutation
        sys.argv=[str(source/'COMEBin/main.py'),*argv]
        runpy.run_path(str(source/'COMEBin/main.py'),run_name='__main__')
    elif tool=='metacat':
        sys.path.insert(0,str(source));from MetaCAT import main
        sys.argv=['MetaCAT',*argv];main()
    elif tool=='semibin':
        sys.path.insert(0,str(source));from SemiBin.main import main2
        sys.argv=['SemiBin2',*argv];main2()
    elif tool=='scgbinner':
        sys.path.insert(0,str(source))
        limit_hnsw(threads)
        from SCGBinner import marker_search,get_final_result
        def capped_pool(processes=None,*args,**kwargs):
            """Cap native host-count pools at the reviewed N-1 process budget."""
            return multiprocessing.Pool(min(processes or threads-1,threads-1),*args,**kwargs)
        marker_search.Pool=capped_pool;get_final_result.Pool=capped_pool
        sys.argv=['SCGBinner',*argv]
        runpy.run_module('SCGBinner.main',run_name='__main__')
    elif tool=='completebin' and argv==['--help']:
        sys.path.insert(0,str(source));from CompleteBin.cli import main
        sys.argv=['CompleteBin','--help'];main()
    else:raise ValueError('CompleteBin fitting uses the explicit patched-source API, not argv')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory-prefix');parser.add_argument('--modules',nargs='*',default=[])
    parser.add_argument('--expected-freeze')
    parser.add_argument('--dependency-prefix')
    parser.add_argument('--forbidden-prefix')
    parser.add_argument('--expected-distributions',type=Path)
    parser.add_argument('--tool');parser.add_argument('--source',type=Path);parser.add_argument('--threads',type=int)
    parser.add_argument('native_args',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    if args.inventory_prefix:
        print('INVENTORY_JSON='+json.dumps(inventory(args.inventory_prefix,args.modules,args.expected_freeze,
              args.dependency_prefix,json.loads(args.expected_distributions.read_text()) if args.expected_distributions else None,args.forbidden_prefix)),flush=True)
    else:invoke(args.tool,args.source,args.native_args[1:] if args.native_args[:1]==['--'] else args.native_args,args.threads)
