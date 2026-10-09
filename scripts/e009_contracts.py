"""Tiny real-DNA contracts shared by local QA and the owner Linux preflight.

This is software validation, not E009 fitting/scoring or an accepted demonstration
replay. Input DNA is retained, byte-bound and <=32 contigs / 0.6 Mb. Native sources
are isolated E009 copies. No native community trainer is invoked here.
"""
import argparse
import ast
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).absolute().parent))

from e009_common import binding, fasta, write_json
from e009_data import assembly_axis, assemble, combine_depth, map_sample, mean_depth, run_native
from e009_native import command_plan, resolved_epochs
from e009_truth import construct, parse_paf, reconcile


def portable(inputs, mapping, minimap2, megahit, threads, output, assembly_threads=None):
    """Exercise real paired reads, serial map/sort/depth, assembly and competitive truth."""
    inputs,mapping,output=Path(inputs),Path(mapping),Path(output);output.mkdir(parents=True,exist_ok=False)
    reference=inputs/'assembly.fna';columns=['software_sample_0','software_sample_1'];paths=[]
    for i,column in enumerate(columns):
        first,second=(inputs/'reads_1.fq',inputs/'reads_2.fq') if i==0 else (inputs/'sample1_reads_1.fq',inputs/'sample1_reads_2.fq')
        bam=map_sample(mapping/'strobealign',mapping/'samtools',reference,first,second,i,column,threads,output/f'mapping_{i}')
        target=output/f'depth_{i}.tsv';mean_depth(mapping/'samtools',reference,bam,column,threads,target);paths.append(target)
    combine_depth(reference,columns,paths,output/'depth.tsv')
    import csv
    matrix=list(csv.reader((output/'depth.tsv').open(),delimiter='\t'))[1:]
    if not any(float(row[1])>float(row[2])>0 for row in matrix):
        raise ValueError('Distinct native sample values failed the ordered depth contract')
    assembly_threads=assembly_threads or threads
    if not 1<=assembly_threads<=threads:raise ValueError('Assembly CPU budget exceeds allocation')
    assembled=assemble(megahit,inputs/'reads_1.fq',inputs/'reads_2.fq',assembly_threads,1_000_000_000,output/'megahit',output/'megahit.log')
    paf=output/'truth.paf'
    run_native([minimap2,'-x','asm5','-P','-c','--eqx','-m','100','-s','100','-n','2','-t',threads-1,
                inputs/'truth-reference.fna',inputs/'truth-query.fna'],output/'align.log',stdout=paf)
    refs=json.loads((inputs/'truth-reference-axis.json').read_text())
    result=construct(inputs/'truth-query.fna',paf,refs,output/'truth')
    expected=json.loads((inputs/'truth-expectations.json').read_text())
    for qid,rule in expected.items():
        item=result[qid]
        if 'label' in rule and item['AMBER_label']!=rule['label']:raise ValueError(f'Native truth label mismatch: {qid}')
        for key in ['ambiguous_query_bp','repeat_locus_query_bp','unsupported_query_bp']:
            if key in rule and item[key]<rule[key]:raise ValueError(f'Native truth {key} mismatch: {qid}')
        if rule.get('unique_support_min') and sum(item['confirmed_query_bp'].values())<rule['unique_support_min']:
            raise ValueError(f'Native unique support mismatch: {qid}')
    receipt={'scope':'new E009 native software contracts only; no biological scoring',
             'inputs':binding(reference),'native_assembly':assembled,'mapping_samples':columns,
             'truth_queries':len(result),'native_competition_orientation_gaps_checked':True,
             'runtime':{'mapping_bin':str(mapping),'minimap2':binding(minimap2),'megahit':binding(megahit)},
             'threads':threads,'assembly_threads':assembly_threads}
    write_json(output/'passed.json',receipt);return receipt


def amber_contract(truth_path, source, output):
    """Exercise native AMBER on the tiny competitive-alignment fixture, never E009 scores.

    The software oracle checks the restricted population's exact length sum and a
    duplicate-safe source union. Fixture bin labels are not benchmark tuning.
    """
    from e009_evaluate import amber_view
    from e009_truth import recovery
    truth=json.loads(Path(truth_path).read_text());contigs=truth['contigs']
    assigned={qid:('fixture-bin' if item['AMBER_label']=='A' else None) for qid,item in contigs.items()}
    expected=sum(contigs[qid]['length'] for qid in ('unique','reverse','insert','delete','repeat'))
    value=amber_view(contigs,assigned,source,output)
    if not value['native_api_executed'] or value['scorable_contigs']!=5 or value['scorable_bp']!=expected:
        raise ValueError('Native AMBER restricted population/length contract changed')
    lengths={}
    for item in truth['reference_axis'].values():lengths[item['genome']]=lengths.get(item['genome'],0)+item['length']
    rows=recovery(contigs,assigned,truth['reference_axis'],lengths,['A','B'],min_bin=0)
    if rows[0]['recovered_bp']!=2000 or rows[1]['recovered_bp']!=0:
        raise ValueError('Duplicate/orientation/gap-aware reference union changed')
    write_json(Path(output)/'contract.json',{'software_only':True,'AMBER':value,'reference_union_contract':rows})


def parser_contract(tool, source, plan):
    """Run the upstream parser AST for every prepared argv, without heavy imports.

    This checks actual native option names/defaults, not successful Linux imports
    or training. It catches wrapper mistakes before transfer. Native Linux also
    imports the full modules and exercises their real readers/writers separately.
    """
    import argparse as arg
    import os as os_module
    import re
    source=Path(source)
    if tool in ('comebin','scgbinner'):
        p=source/('COMEBin' if tool=='comebin' else 'SCGBinner')/'main.py'
        node=next(n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='arguments')
        ns={'argparse':arg,'ver':'contract','DEFAULT_RANDOM_SEED':1,'DEFAULT_HMM_EVALUE':1e-5}
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(p),'exec'),ns)
        original=sys.argv
        try:
            for argv in plan['stages']:
                sys.argv=['native-contract',*argv];ns['arguments']()
        finally:sys.argv=original
    elif tool=='semibin':
        p=source/'SemiBin/main.py';tree=ast.parse(p.read_text())
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='semibin_arg_parser')
        ns={'argparse':arg,'os':os_module,'__version__':'contract'}
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(p),'exec'),ns)
        for argv in plan['stages']:ns['semibin_arg_parser']().parse_args(argv)
    elif tool=='metacat':
        p=source/'MetaCAT/__init__.py';tree=ast.parse(p.read_text())
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
        ns={'MetaCATParser':arg.ArgumentParser,'ArgumentParser':arg.ArgumentParser,
            'RawTextHelpFormatter':arg.RawTextHelpFormatter,'os':os_module,'Path':Path}
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(p),'exec'),ns)
        original=sys.argv
        try:
            for argv in plan['stages']:
                sys.argv=['MetaCAT',*argv];ns['__init__']()
        finally:sys.argv=original
    else:
        epochs=[resolved_epochs(source,n50,n) for n50,n in [(1000,100),(2000,100),(1000,200000),(2000,200000)]]
        if epochs!=[50,50,35,39]:raise ValueError(f'Modified CompleteBin scheduler drift: {epochs}')
        node=next(n for n in ast.parse((source/'CompleteBin/Binning_steps.py').read_text()).body
                  if isinstance(n,ast.FunctionDef) and n.name=='binning_with_all_steps')
        if set(plan['api'])-{arg.arg for arg in node.args.args}:raise ValueError('CompleteBin prepared API argument drift')
    return {'tool':tool,'parser_only':True,'native_imports_or_full_schedule_validated':False}


def complete_contract(source, db, reference, bam, threads, output):
    """Run CompleteBin's real FASTA/BAM coverage writer, checkpoint load and small forward.

    Loads the actual database state dictionary using upstream model construction;
    does not train, infer a community, select clusters or evaluate bin quality.
    """
    source,db,output=Path(source),Path(db),Path(output);output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(source))
    import torch
    import numpy as np
    torch.set_num_threads(threads);torch.set_num_interop_threads(1)
    from CompleteBin.IO import readFasta, readPickle
    from CompleteBin.Seqs.seq_utils import base_pair_coverage_calculate
    from CompleteBin.Model.model import CompleteBinModel
    from CompleteBin.Utils.pretrain_decision import apply_epoch_safety_valve,compute_O,decide_pretrained
    if apply_epoch_safety_valve(50,2,50)[0]!=50 or apply_epoch_safety_valve(200,2,50)[0]!=150:
        raise ValueError('Native epoch safety-valve behavior changed')
    if decide_pretrained(.1,compute_O(50,100))[0] is not True or decide_pretrained(.1,compute_O(200,100))[0] is not False:
        raise ValueError('Native capped-epoch pretraining-decision contract changed')
    data=readFasta(str(reference));path=output/'coverage.pkl'
    base_pair_coverage_calculate(data,str(bam),str(path),min_contig_length=0,num_worker=threads-2,write_pickle=True)
    arrays=readPickle(str(path))
    if set(arrays)!=set(data) or any(len(arrays[k])!=len(data[k]) for k in data):
        raise ValueError('Native CompleteBin coverage axes changed')
    # Mirrors ssmt_v2.py's production hidden width, class count and split tokens.
    model=CompleteBinModel(136,136,100,2,[1,11],.15,'cpu',2,1,
                           hidden_dim=768,layers=4,num_classes=15434,use_pretrained=True)
    weights=db/'CheckPoint/pretrain_weight_large_hidden_dim_768_layers_4.pth'
    model.load_weight_for_model(str(weights));model.eval()
    with torch.no_grad():
        result=model(torch.ones(4,12,136),torch.ones(4,12,2),torch.ones(4,12,2),torch.ones(4,2,136),2)
    tensors=[result] if torch.is_tensor(result) else [t for t in result if torch.is_tensor(t)]
    if not tensors or not all(torch.isfinite(t).all() for t in tensors):raise ValueError('Native checkpoint forward nonfinite')
    write_json(output/'passed.json',{'coverage_rows':len(arrays),'weights':binding(weights),'model_state_loaded':True,
               'forward_shapes':[list(t.shape) for t in tensors],'training':'not run','loader_workers':0,'torch_threads':torch.get_num_threads()})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--threads',type=int,required=True)
    p.add_argument('--mapping-bin',type=Path);p.add_argument('--minimap2',type=Path);p.add_argument('--megahit',type=Path)
    p.add_argument('--assembly-threads',type=int,help='Explicit local contract override only; Linux preflight uses its full eight-CPU allocation')
    p.add_argument('--completebin-source',type=Path);p.add_argument('--completebin-db',type=Path);p.add_argument('--bam',type=Path)
    p.add_argument('--amber-source',type=Path);p.add_argument('--truth',type=Path)
    a=p.parse_args()
    if a.amber_source:amber_contract(a.truth,a.amber_source,a.output)
    elif a.completebin_source:complete_contract(a.completebin_source,a.completebin_db,a.inputs/'assembly.fna',a.bam,a.threads,a.output)
    else:portable(a.inputs,a.mapping_bin,a.minimap2,a.megahit,a.threads,a.output,a.assembly_threads)
