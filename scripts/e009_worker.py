"""Monitored E009 native-contract worker; never runs community fits on import.

Native feature readers/writers execute on tiny byte-bound real DNA. Parser tests
remain explicitly distinct from full imports, feature extraction and training.
"""
import argparse
import ast
import logging
import csv
import gzip
import json
import os
import shutil
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).absolute().parent))

from e009_common import acquire, binding, fasta, write_json
from e009_contracts import complete_contract, parser_contract
from e009_data import run_native, source_catalog
from e009_native import command_plan,limit_hnsw,prepare_bam_directory,inspect_comebin_features


def comebin_native_augmentation(source, argv, threads):
    """Call the exact native augmentation API/default parser without training imports.

    The pinned main.generate_aug_data branch calls these same two functions.
    Its full Linux help/import already passed v10. Reuse that evidence explicitly;
    do not patch training AMP imports to run a feature-only preflight on Mac.
    Read native parser AST with real version/seed/HMM constants, preserve output
    resolution and RNG setup, then execute actual writers (no worker replacement).
    """
    source=Path(source);sys.path.insert(0,str(source/'COMEBin'))
    import torch
    torch.set_num_threads(threads);torch.set_num_interop_threads(1)
    from comebin_version import __version__
    from utils import DEFAULT_RANDOM_SEED,DEFAULT_HMM_EVALUE,configure_reproducibility
    from data_aug.generate_augfasta_and_saveindex import run_gen_augfasta
    from data_aug.gen_cov import run_gen_coverage
    path=source/'COMEBin/main.py'
    node=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='arguments')
    ns={'argparse':argparse,'ver':__version__,'DEFAULT_RANDOM_SEED':DEFAULT_RANDOM_SEED,'DEFAULT_HMM_EVALUE':DEFAULT_HMM_EVALUE}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),ns)
    previous=sys.argv
    try:
        sys.argv=[str(path),*map(str,argv)];args=ns['arguments']()
    finally:sys.argv=previous
    if args.subcmd!='generate_aug_data':raise ValueError('Native API preflight permits augmentation only')
    args.output_path=str(Path(args.out_augdata_path).expanduser().resolve())
    Path(args.output_path).mkdir(parents=True,exist_ok=True)
    logger=logging.getLogger('COMEBin\t'+__version__);logger.setLevel(logging.INFO)
    handler=logging.FileHandler(Path(args.output_path)/'comebin.log')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'));logger.addHandler(handler)
    try:
        if args.seed is not None:configure_reproducibility(args.seed)
        run_gen_augfasta(logger,args);run_gen_coverage(logger,args)
    finally:logger.removeHandler(handler);handler.close()
    return {'native_functions':['run_gen_augfasta','run_gen_coverage'],'parser':'actual pinned arguments AST with real constants',
            'seed':args.seed,'n_views':args.n_views,'pool_workers':args.num_threads,'model_training':False}


def tool_contract(args):
    """Exercise real production adapters/readers without shortened community fitting."""
    out=args.output;out.mkdir(parents=True,exist_ok=False)
    (out/'native').mkdir()
    reference=args.inputs/'assembly.fna'
    plan=command_plan(args.tool,args.source,reference,args.bams,out/'native',args.threads,args.db)
    if args.tool=='comebin':prepare_bam_directory(plan['bam_directory'],args.bams)
    write_json(out/'parser-contract.json',parser_contract(args.tool,args.source,plan))
    own=[sys.executable,'-I','-B',str(Path(__file__).with_name('e009_native.py')),'--tool',args.tool,
         '--source',str(args.source),'--threads',str(args.threads),'--']
    reused=getattr(args,'reused_help',None)
    if reused:
        if args.tool!='comebin':raise ValueError('Only accepted COMEBin help can be reused')
        shutil.copyfile(reused,out/'native-full-import-help-reused.log')
        write_json(out/'native-help-reused.json',{'source':str(reused),'file':binding(reused),
                   'scope':'accepted v10 full Linux CLI/import; not rescheduled'})
    else:run_native(own+['--help'],out/'native-full-import-help.log',timeout=60)
    if args.tool=='completebin':
        # CompleteBin has an API path; its real checkpoint/coverage path is the contract.
        complete_contract(args.source,args.db,reference,args.bams[0],args.threads,out/'complete')
    elif args.tool=='semibin':
        run_native(own+['generate_sequence_features_single','-i',reference,'-b',*args.bams,'-o',out/'features','-p',args.threads],out/'features.log',timeout=180)
        files=list((out/'features').glob('data*.csv'))
        if len(files)<2:raise ValueError('SemiBin native whole/split features missing')
        import pandas as pd
        matrices={p.name:pd.read_csv(p,index_col=0) for p in files}
        if any(m.empty or m.index.has_duplicates for m in matrices.values()):raise ValueError('SemiBin native feature axis invalid')
        write_json(out/'features.json',{'files':{p.name:binding(p) for p in files},'axes':{n:list(map(str,m.index)) for n,m in matrices.items()}})
    elif args.tool=='metacat':
        run_native(own+plan['stages'][0],out/'coverage.log',timeout=180)
        run_native(own+plan['stages'][1]+['--temp',str(out)],out/'seed.log',timeout=180)
        with gzip.open(out/'native/coverage','rt') as stream:rows=list(csv.reader(stream,delimiter='\t'))
        if rows[0]!=['Sequence ID','Mean','Variance','Mean','Variance'] or [r[0] for r in rows[1:]]!=[name for name,seq in fasta(reference)]:
            raise ValueError('MetaCAT native coverage axes/header changed')
        if not any(float(r[1])>float(r[3])>0 for r in rows[1:]):raise ValueError('MetaCAT ordered native sample means changed')
        write_json(out/'features.json',{'coverage':binding(out/'native/coverage'),'seed':binding(out/'native/seed'),
                   'contig_ids':[r[0] for r in rows[1:]],'sample_axis':'two input BAMs in declared order; native duplicate Mean/Variance headers',
                   'cluster':'not run; native full import/argv verified only'})
    elif args.tool=='scgbinner':
        run_native(own+plan['stages'][0],out/'augmentation.log',timeout=300)
        # Execute the upstream initializer that actually calls stable_cumsum,
        # without a community clustering fit or truth-based K selection.
        sys.path.insert(0,str(args.source));from SCGBinner.cluster import partial_seed_init
        import numpy as np
        probe=np.arange(24,dtype=np.float64).reshape(8,3)
        centers=partial_seed_init(probe,3,11,[0])
        if centers.shape!=(3,3) or not np.isfinite(centers).all():
            raise ValueError('SCGBinner native seeded initializer contract failed')
        # Exercise the dtype patch in the actual reader on native emitted data.
        sys.path.insert(0,str(args.source));from SCGBinner.utils import get_kmer_coverage_aug0
        values=get_kmer_coverage_aug0(str(out/'native/data_augmentation')+'/')
        import numpy as np
        if not all(np.isfinite(v).all() for v in values[:3]):raise ValueError('SCGBinner native features nonfinite')
        limit_hnsw(args.threads)
        import hnswlib
        index=hnswlib.Index(space='l2',dim=values[0].shape[1]);index.init_index(max_elements=len(values[0]))
        index.add_items(values[0]);index.knn_query(values[0],k=1)
        if index.num_threads!=args.threads:raise ValueError('SCGBinner HNSW CPU limit did not take effect')
        write_json(out/'features.json',{'shapes':[list(v.shape) for v in values],'ids':list(map(str,values[-1])),
                   'model_training':'not run; max200 native schedule retained'})
    else:
        run_native([shutil.which('checkm') or 'checkm','--help'],out/'checkm-readonly-help.log',timeout=60)
        if reused:
            write_json(out/'augmentation-api.json',comebin_native_augmentation(args.source,plan['stages'][0],args.threads))
        else:run_native(own+plan['stages'][0],out/'augmentation.log',timeout=300)
        root=out/'native/augmentation';files=list(root.rglob('*.tsv'))+list(root.rglob('*.npy'))+list(root.rglob('*.csv'))
        if not files:raise ValueError('COMEBin native augmentation artifacts missing')
        axes=inspect_comebin_features(args.source,root,args.bams,reference)
        write_json(out/'features.json',{'files':{str(p.relative_to(root)):binding(p) for p in files},
                   'native_axes':axes,
                   'model_training_and_120_candidate_grid':'not run; E001 accepted grid evidence reused; full E009 native grid admission pending'})
    write_json(out/'passed.json',{'tool':args.tool,'inputs':binding(reference),'ordered_bams':[binding(p) for p in args.bams],
               'native_readers_writers':True,'full_community_fit':False,'config':plan})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='operation',required=True)
    a=subs.add_parser('acquire');a.add_argument('--spec-json',required=True);a.add_argument('--destination',type=Path,required=True)
    many=subs.add_parser('acquire-utilities',aliases=['acquire-conda']);many.add_argument('--lock',type=Path,required=True);many.add_argument('--destination',type=Path,required=True);many.add_argument('--explicit',type=Path,required=True)
    c=subs.add_parser('source-catalog');c.add_argument('--source',type=Path,required=True);c.add_argument('--development',type=Path,required=True);c.add_argument('--output',type=Path,required=True)
    t=subs.add_parser('tool-contract')
    for name in ['source','inputs','output','db']:t.add_argument('--'+name,type=Path,required=True)
    t.add_argument('--tool',choices=['semibin','metacat','scgbinner','comebin','completebin'],required=True)
    t.add_argument('--reused-help',type=Path,help='Exact previously accepted COMEBin Linux help; supplied only by verified retry adapter')
    t.add_argument('--bams',nargs=2,type=Path,required=True);t.add_argument('--threads',type=int,required=True)
    args=p.parse_args()
    if args.operation=='acquire':
        print(json.dumps(acquire(json.loads(args.spec_json),args.destination,resume=True)),flush=True)
    elif args.operation in ('acquire-utilities','acquire-conda'):
        packages=json.loads(args.lock.read_text())['packages'];args.destination.mkdir(parents=True,exist_ok=True)
        with args.explicit.open('x') as out:
            out.write('@EXPLICIT\n')
            for spec in packages:
                target=args.destination/spec['fn']
                print('DLBINNER pinned Conda acquisition: '+spec['fn'],flush=True)
                acquire({'url':spec['url'],'bytes':spec['size'],'sha256':spec['sha256']},target,resume=True)
                out.write(target.absolute().as_uri()+'#'+spec['md5']+'\n')
    elif args.operation=='source-catalog':
        source_catalog(args.source,json.loads(args.development.read_text()),args.output)
    else:tool_contract(args)
