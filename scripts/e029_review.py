#!/usr/bin/env python3
"""Evaluate new E029 partitions with admitted, unchanged sequence-truth readers.

No fitting, inference, new neighbors, selection or threshold changes occur.
Sparse arrays supply a lazy, explicitly named joint-score 5-NN diagnostic view;
this never substitutes for or rewrites retained native learned geometry.
"""
import argparse
from collections import Counter
import csv
import gc
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
# Pin the actual installed wheel before legacy review helpers add checkout paths.
from e029_control import product_scope
if __name__=='__main__':product_scope()
from e024_coverage import binding,write
from e027_inspection import read,require


class JointNeighbors:
    """Expose a complete source-ID axis without allocating a million Python lists."""
    def __init__(self,ids,selected,neighbors):
        import numpy as np
        self.ids=ids;self.selected=selected;self.neighbors=neighbors
        self.inverse=np.full(len(ids),-1,np.int32);self.inverse[selected]=np.arange(len(selected))

    def __len__(self):return len(self.ids)

    def __getitem__(self,index):
        local=int(self.inverse[index])
        return [] if local<0 else [self.ids[int(self.selected[j])] for j in self.neighbors[local,:5]]


def sparse_contract(group,features,data,inventory,prefix):
    """Read real numeric caches and validate axes, graph and forest without rebuilding."""
    import numpy as np
    from dl_binner.calibrated.arrays import load
    ids=data['ids'].tolist();group=Path(group);record=read(group/'completed.json')
    require(record['input_sha256']['features']==binding(features)['sha256']
            and record['truth_accessed'] is False,'Frozen grouping feature binding differs')
    for name,wanted in record['files'].items():
        require(inventory[prefix+'/'+name]==wanted,'Group complete member table differs')
        if (group/name).exists():require(binding(group/name)==wanted,'Staged result changed: '+name)
    a,_=load(group/'retrieval/neighbors.npz','unified_graded_neighbors',ids)
    tree,_=load(group/'forest.npz','unified_density_forest',ids)
    selected=a['selected'];nn=a['neighbors'];dd=a['distances'];n=len(selected)
    expected=np.array(sorted(np.flatnonzero(data['eligible']),key=lambda i:ids[i]),np.int64)
    require(np.array_equal(selected,expected) and nn.shape==dd.shape==(n,30)
            and nn.dtype.kind in 'iu' and np.isfinite(dd).all() and np.all(dd>0)
            and np.all(np.diff(dd,axis=1)>=0),'Malformed actual full-axis sparse cache')
    for start in range(0,n,8192):
        block=nn[start:start+8192];ordered=np.sort(block,axis=1)
        require(np.all((block>=0)&(block<n)) and np.all(np.diff(ordered,axis=1)>0)
                and not np.any(block==np.arange(start,start+len(block))[:,None]),'Self/duplicate sparse endpoint')
    mass=tree['mass'];size=len(mass);children=tree['children'];level=tree['level'];count=tree['count']
    require(n<=size<=2*n-1 and children.shape==(size,2) and np.all(children[:n]==-1)
            and np.array_equal(mass[:n],data['lengths'][selected]) and np.all(count[:n]==1)
            and np.all(level[:n]==0) and np.isfinite(level).all(),'Forest full leaves differ')
    x,y=children[n:].T;at=np.arange(n,size)
    require(np.all((0<=x)&(x<y)&(y<at)) and np.array_equal(mass[n:],mass[x]+mass[y])
            and np.array_equal(count[n:],count[x]+count[y]) and np.all(level[n:]>=np.maximum(level[x],level[y])),
            'Forest parent mass/level/order differs')
    seen=np.bincount(children[n:].ravel(),minlength=size)
    require(np.all(seen<=1) and np.array_equal(tree['roots'],np.flatnonzero(seen==0))
            and np.array_equal(tree['core'],dd[:,9]) and tree['mst_edges'].shape==(size-n,2)
            and np.array_equal(np.sort(tree['mst_distances']),level[n:]),'Forest roots/core/MST counters differ')
    proof=dict(status='PASS_ACTUAL_SPARSE_READERS_FULL_AXES_FOREST',rows=len(ids),eligible=n,
        neighbors=30,forest_nodes=size,roots=len(tree['roots']),full_bp=int(data['lengths'].sum()),
        features=binding(features),local_graph_or_selection_rebuilt=False,
        native_complete_distance_and_choice_reproduction='Accepted serial native audit; source and every artifact separately verified',
        geometry='New joint-score eligible retrieval, not original fixed native learned graph')
    return a,proof


def review(base,staged,unit,role,output):
    """Evaluate one teacher/student pair of parent/post exports; reuse old summaries only."""
    import numpy as np
    from threadpoolctl import threadpool_limits
    from dl_binner.multiview.views import load
    from dl_binner.information.export import validate_partition
    from dl_binner.density.bin_quality import summarize
    from e022_review import admission_contract
    from e014_review import manifest_bindings,diagnostics,grouping_diagnostics,population_cells,oral_labels,oral_population
    from e017_review import export_contract
    from e023_review import oral_secondary_rows
    from e025_review import coverage_populations
    from e012_marker_audit import verify_truth
    from e014_oral_truth import evaluate
    threadpool_limits(4);base=Path(base);stage=Path(staged);output=Path(output)
    require(unit in ['E009-noGLM','E009-GLM','oral-noGLM']and role in ['teacher','student'],'Unfrozen review arm')
    admitted=admission_contract(base/'admission.json');inv=read(base/'inventory.json')['all_work_members']
    paths=dict(E009=ROOT/'artifacts/e011-cached-grouping-reference/restore-local/candidate/features/features.npz',
        oral=ROOT/'artifacts/e024-inspection/20261028T193107Z/verified/work/rebound/features.npz')
    dataset='E009'if unit.startswith('E009')else'oral';features=paths[dataset]
    data,meta=load(features);ids=data['ids'].tolist();axis=admitted['axes'][unit]
    require(len(ids)==axis['rows'] and int(data['lengths'].sum())==axis['bp']
            and int(data['eligible'].sum())==axis['eligible'] and meta['samples']==axis['samples']
            and data['depth'].shape==(len(ids),10) and np.isfinite(data['depth']).all(),
            'Independent feature/source/ordered ten-depth axes differ')
    prefix='groups/'+unit+'/'+role+'/result';group=stage/'work'/prefix
    cache,numeric=sparse_contract(group,features,data,inv,prefix)
    marker=ROOT/('artifacts/e022-inspection/20261026/verified/work/units/E009-relational/refine/quality-evidence.json'
        if dataset=='E009'else'artifacts/e019-window-context/review-20261023/verified/work/units/oral-context/refine/quality-evidence.json')
    require(binding(marker)['sha256']==read(group/'completed.json')['input_sha256']['evidence'],'Cached marker evidence differs')
    clean_path=ROOT/('artifacts/e011-cached-grouping-reference/restore-local/candidate/markers/evidence.json'
        if dataset=='E009'else'artifacts/e014-multiview-reconstruction/inspection-20261019/oral-marker-review.json')
    clean=set(read(clean_path)['clean'])
    clean_binding=(read(ROOT/'experiments/E022-marker-informed-learning/reuse-lock.json')['files']
        if dataset=='E009'else None)
    if clean_binding:
        candidates=[v for k,v in clean_binding.items()if k.endswith('/candidate/markers/evidence.json')]
        require(len(candidates)==1 and binding(clean_path)==candidates[0],'Clean-marker strata source differs')
    else:
        require(binding(clean_path)==read(ROOT/'experiments/E014-multiview-reconstruction/comparison-review.json')['evidence'][str(clean_path.relative_to(ROOT))],
                'Retained Oral clean-marker review differs')
    result=dict(status='SUCCESS',unit=unit,role=role,numeric_contract=numeric,arms={},
        features=binding(features),marker_evidence=binding(marker),marker_clean=binding(clean_path),
        geometry_scope='New joint-score retrieval population; older learned geometry reused as summaries, not recalculated',
        original_Mac_portability_tolerance_unchanged=True,primary_rule_unchanged=True)
    output.mkdir(parents=True,exist_ok=False)
    if dataset=='E009':
        lock=read(ROOT/'experiments/E013-marker-quality/review-lock.json');source=verify_truth(lock)
        truth=read(source/'truth.json');targets=read(source/'targets.json');pop=read(ROOT/lock['population_path'])
        require(ids==truth['ordered_contig_ids']and len(targets['targets'])==156
                and sum(targets['genome_lengths'][g]for g in targets['targets'])==554661890,'E009 truth/denominator differs')
    else:
        truth_root=ROOT/'artifacts/e014-multiview-reconstruction/oral-truth-origin-v1'
        lab,quarantine,shared,genomes,truth=oral_labels(truth_root,ids,data['lengths'])
        require(len(truth['targets'])==799 and sum(truth['targets'].values())==2083072211
                and meta['fasta_sha256']==truth['model_input']['sha256'],'Oral full-reference/source truth differs')
    neighbors=JointNeighbors(ids,cache['selected'],cache['neighbors'])
    for arm in ['parent','post']:
        path=group/(arm+'-partition.json');part=validate_partition(data,path,features)
        require(binding(path)==inv[prefix+'/'+path.name],'Partition original bytes differ')
        export_prefix=unit+'/export/'+role+'-'+arm;folder=stage/'work'/export_prefix
        manifest_bindings(read(folder/'manifest.json'),export_prefix,inv)
        rows,account=export_contract(part,data,folder);part['neighbors']=neighbors
        assignments={q:b if b>=0 else None for q,b in zip(ids,part['assignment'])}
        if dataset=='E009':
            primary=diagnostics(truth,rows,part,pop,targets)
            primary['geometry']['scope']=result['geometry_scope']
            grouped=grouping_diagnostics(truth,rows,pop,targets,clean)
            require(primary['recovery']==grouped['recovery'],'Independent primary recovery readers disagree')
            secondary={'conservative_sequence':summarize(({**truth['contigs'][q],'id':q}for q in ids),
                assignments,truth['reference_axis'],targets['genome_lengths'],targets['targets'])}
            value=dict(diagnostics=primary,grouping=grouped,populations=population_cells(rows,truth,pop,clean),secondary=secondary)
        else:
            evaluated=evaluate(truth_root,path,output/('truth-'+arm));refs=truth['references'];lengths=Counter()
            for ref in refs.values():lengths[ref['genome']]+=ref['length']
            secondary={mode:summarize(oral_secondary_rows(truth_root/'rows.jsonl.gz',refs,masked),assignments,refs,lengths,truth['targets'])
                       for mode,masked in [('provided_origin',False),('known_shared_sensitivity',True)]}
            value=dict(evaluation=evaluated,grouping=oral_population(part,data,lab,quarantine,shared,genomes,truth['targets'],clean),
                measured_depth_population=coverage_populations(data,part,lab,genomes,truth['targets'],clean),secondary=secondary)
        value['export_contract']=account;value['partition']=binding(path);result['arms'][arm]=value
        for mode,table in secondary.items():
            with (output/('bin-quality-'+arm+'-'+mode+'.tsv')).open('x')as stream:
                writer=csv.DictWriter(stream,fieldnames=list(table['bins'][0])if table['bins']else['bin_id'],delimiter='\t',lineterminator='\n')
                writer.writeheader();writer.writerows(table['bins'])
        # Keep compact results, not full temporary query-row dictionaries.
        del part,rows,assignments;gc.collect()
        write(output/('review-through-'+arm+'.json'),result)
        summary=value['diagnostics']['recovery_summary']if dataset=='E009'else value['evaluation']['origin']['recovery_summary']
        print(unit,role,arm,json.dumps(summary),flush=True)
    write(output/'review.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['base','staged','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--unit',required=True);p.add_argument('--role',choices=['teacher','student'],required=True)
    a=p.parse_args();review(a.base,a.staged,a.unit,a.role,a.output)
