#!/usr/bin/env python3
"""Read and check original E014 graph artifacts in place, without a new index/fit.

This bounded evidence reader reuses the independently tested E010 sparse and
unit-neighbor contracts. It permits a smaller science return while leaving all
original graph bytes on disk and keeping exact graph hashes in the evidence.
No truth labels, model inference, selection or scientific output is written.
"""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e014_collect import binding


def review(unit,output):
    """Validate full graph axes/edges/weights and 128 fixed label-blind cosine queries."""
    import numpy as np
    from threadpoolctl import threadpool_limits
    from dl_binner.io import load_arrays
    from e010_review import unit_neighbors,sparse_graph_contract,require
    started=time.monotonic();unit,output=Path(unit),Path(output)
    threadpool_limits(4)
    pre=json.loads((unit/'group/partition.json').read_text());ids=pre['ids']
    graph,gm=load_arrays(unit/'group/graph.npz','candidate_sparse_graph')
    embedded,em=load_arrays(unit/'embeddings.npz','embeddings')
    require(graph['ids'].tolist()==ids==embedded['ids'].tolist(),'Complete graph/embedding axes differ')
    require(pre['graph_sha256']==binding(unit/'group/graph.npz')['sha256']
            and pre['embedding_sha256']==binding(unit/'embeddings.npz')['sha256']
            and gm['embedding_sha256']==pre['embedding_sha256'],'Original graph/embedding bindings differ')
    sparse=sparse_graph_contract(graph['edges'],graph['weights'],ids,pre['valid'])
    gamma=float(np.median(graph['weights']))/pre['config']['neighbors']
    require(pre['objective']['gamma']==gamma and pre['objective']['node_sizes']==1
            and pre['objective']['seed']==11,'Frozen label-free CPM rule differs')
    geometry=unit_neighbors(embedded['features'],ids,pre['valid'],pre['neighbors'],graph['neighbors'],pre['config']['neighbors'])
    value=dict(status='PASS',unit=unit.name,graph=binding(unit/'group/graph.npz'),embedding=binding(unit/'embeddings.npz'),
               partition=binding(unit/'group/partition.json'),graph_metadata=gm,embedding_metadata=em,
               sparse=sparse,geometry=geometry,objective=pre['objective'],seconds=time.monotonic()-started,
               fit_inference_index_or_selection_ran=False)
    with output.open('x')as f:json.dump(value,f,indent=2);f.write('\n')
    print('RETAINED_GRAPH_VERIFIED',unit.name,len(ids),sparse['edges'],flush=True)
    return value


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--research-scripts',type=Path,default=Path(__file__).absolute().parent,
                   help='Read-only frozen review-helper directory when this collector is transferred separately')
    a=p.parse_args();sys.path.insert(1,str(a.research_scripts));review(a.unit,a.output)
