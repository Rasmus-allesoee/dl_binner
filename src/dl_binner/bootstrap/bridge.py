"""Source-bound E023 graph/construction bridge on fixed admitted learning.

Reuse a closed successful result when every required member and consumed input
matches. Otherwise execute the original density module prospectively. There is
no fallback from a failed reuse check to rebuilding accepted science.
"""
import json
from pathlib import Path

from ..context.tokens import binding
from ..density import grouping as original
from ..information.export import export, validate_partition
from ..io import write_json
from ..multiview.views import load
from ..relational.evidence import require

MEMBERS = ['density-partition.json','selected-partition.json','density-choices.json',
           'selected-choices.json','hierarchy.npz','hierarchy.json','alternatives.json','completed.json']


def query_view(result, features, graph, queries, output):
    """Read exact cached local/global ID maps for a predeclared query population.

    This exposes new E023-composite versus unchanged native learned neighbors.
    It is not an exact-composite recall claim or a biological label calculation.
    Queries are source-blind IDs frozen before new community outcomes.
    """
    import numpy as np
    from ..multiview.arrays import load_arrays
    data,meta=load(features)
    sparse,sm=load_arrays(graph,'candidate_sparse_graph')
    tree,tm=load_arrays(Path(result)/'hierarchy.npz','density_hierarchy')
    ids=data['ids'].tolist(); selected=tree['selected'];inverse={ids[int(i)]:j for j,i in enumerate(selected)}
    require(np.array_equal(tree['ids'],data['ids']) and np.array_equal(sparse['ids'],data['ids']) and
            tm['features_sha256']==binding(features)['sha256'] and tm['original_graph_sha256']==binding(graph)['sha256'] and
            tm['embedding_sha256']==sm['embedding_sha256'] and
            selected.ndim==1 and selected.dtype.kind in 'iu' and len(set(selected.tolist()))==len(selected) and
            np.all((0<=selected)&(selected<len(ids))) and tree['neighbors'].dtype.kind in 'iu' and
            np.all((0<=tree['neighbors'])&(tree['neighbors']<len(selected))) and
            len({q['id'] for q in queries})==len(queries), 'Query-view full/unique ID axes differ')
    rows=[]
    for query in queries:
        require(query['id'] in inverse,'Frozen query absent from eligible cached axis')
        local=inverse[query['id']];global_row=int(selected[local]);near=tree['neighbors'][local]
        native=sparse['neighbors'][global_row];native=native[native>=0]
        rows.append(dict(id=query['id'],strata=query.get('strata',[]),length=int(data['lengths'][global_row]),
            measured_parent_depth=data['depth'][global_row].tolist(),depth_positive=bool(data['depth_evidence'][global_row]),
            E023_neighbors=[ids[int(selected[j])] for j in near],E023_distances=tree['distances'][local].tolist(),
            native_neighbors=[ids[int(j)] for j in native]))
    proof=dict(status='PASS',queries=rows,features=binding(features),graph=binding(graph),
        hierarchy=binding(Path(result)/'hierarchy.npz'),samples=meta['samples'],truth_accessed=False,
        geometry='E023 contextual-reranked candidates versus unchanged native learned graph; same query IDs',
        no_exact_composite_recall_or_biological_quality_claim=True)
    write_json(output,proof);return proof


def source_proof(lock, config):
    """Check actual installed E023 algorithm and policy bytes against its old lock."""
    value = json.loads(Path(lock).read_text())
    name = 'src/dl_binner/density/grouping.py'
    require(binding(original.__file__) == value['files'][name] and
            binding(config) == value['policy'], 'E023 source/policy identity differs')
    return dict(source=binding(original.__file__),policy=binding(config),
                frozen_E023_lock=binding(lock),new_scientific_defaults=False)


def consumed(features, embeddings, graph, evidence):
    """Name exact scientific inputs, including NPZ sidecars and physical-call evidence."""
    paths = [features,Path(features).with_suffix('.json'),embeddings,Path(embeddings).with_suffix('.json'),
             graph,Path(graph).with_suffix('.json'),evidence]
    return {str(Path(p).absolute()):binding(p) for p in paths}


def retain_refusal(error,output,inputs):
    """Retain a legacy recall refusal without changing/repeating its calculations.

    The original E023 writer raises before persisting its completed candidates.
    Its pinned traceback exposes the actual computed recall and fully populated
    arrays. Capture only that known complete gate, never uninitialized arrays
    from an earlier failure. This observer cannot turn a failed gate into PASS.
    """
    import numpy as np
    frames={};trace=error.__traceback__
    while trace is not None:
        frames[trace.tb_frame.f_code.co_name]=trace.tb_frame.f_locals
        trace=trace.tb_next
    audit=frames.get('audit',{});candidates=frames.get('candidates',{})
    gate='Core/query sampled neighbor recall below frozen gate'
    if str(error)!=gate or not {'mean','k','selected','ids','recalls','self'}<=set(audit):return
    out=Path(output)
    record=dict(status='FAILED_RECALL_GATE_UNCHANGED',error=str(error),inputs=inputs,
        measured_recall=float(audit['mean']),threshold=float(audit['self'].cfg['min_neighbor_recall']),k=int(audit['k']),
        query_ids=[audit['ids'][i] for i in audit['selected']],query_recalls=list(audit['recalls']),
        no_retry_or_gate_change=True,candidate_scope='E023 proposal geometry, not exact composite recall')
    if {'selected','nn','dd'}<=set(candidates):
        selected,near,dist=(candidates[k] for k in ['selected','nn','dd'])
        if (near.shape==dist.shape and near.ndim==2 and near.shape[0]==len(selected) and
                np.isfinite(dist).all() and (dist>0).all() and
                np.all((near>=0)&(near<len(selected)))):
            path=out/'failed-neighbors.npz'
            with path.open('xb') as stream:np.savez_compressed(stream,selected=selected,neighbors=near,distances=dist)
            record['completed_candidate_arrays']=binding(path)
            record['global_ID_axis']='Bound original features; selected maps local neighbor rows to full parent indices'
    write_json(out/'failed-recall.json',record)


def restore(features, embeddings, graph, evidence, accepted, expected, output, cfg):
    """Admit existing E023 members in place and retain a fresh cached audit proof.

    The accepted-directory member set is explicit; stage seals/logs outside it
    are not silently claimed as backed up. Required scientific members must be
    ordinary files. No recopy or filesystem-link fallback is used; the original
    independently archived result remains the scientific data owner.
    """
    root = Path(accepted)
    require(set(expected) == set(MEMBERS), 'Incomplete accepted E023 member lock')
    for name,wanted in expected.items():
        require(binding(root/name) == wanted, 'Missing/corrupt accepted E023 member; no rebuild: '+name)
    record = json.loads((root/'completed.json').read_text())
    require(record['status'] == 'SUCCESS' and record['config'] == cfg and
            record['features_sha256'] == binding(features)['sha256'] and
            record['embeddings_sha256'] == binding(embeddings)['sha256'] and
            record['original_graph_sha256'] == binding(graph)['sha256'] and
            record['marker_evidence_sha256'] == binding(evidence)['sha256'],
            'Accepted E023 science belongs to different inputs/defaults')
    out = Path(output); out.mkdir(parents=True,exist_ok=False)
    proof = original.audit_cache(features,embeddings,graph,evidence,root,cfg)
    require(all(binding(root/name)==wanted for name,wanted in expected.items()), 'Accepted E023 members changed during audit')
    write_json(out/'verified-reuse.json',dict(status='PASS',accepted=str(root),members=expected,
        audit=proof,science_replayed=False,source_vectors_modified=False,accepted_members_copied=False))
    return proof


def run(features, embeddings, graph, evidence, fasta, config, source_lock, output,
        accepted=None, members=None, engineering=False):
    """Run or strictly reuse one original E023 actor; export full-DNA alternatives."""
    cfg = original.policy(config); proof = source_proof(source_lock,config)
    data,meta = load(features)
    if engineering:
        require(len(data['ids']) <= 128 and int(data['lengths'].sum()) <= 1_000_000,
                'Engineering bridge fixture exceeds tiny scope')
    out = Path(output); out.mkdir(parents=True,exist_ok=False)
    before = consumed(features,embeddings,graph,evidence)
    if accepted is not None:
        result_root=Path(accepted)
        audit = restore(features,embeddings,graph,evidence,accepted,members,out/'reuse',cfg)
    else:
        result_root=out/'result'
        require(members is None, 'Orphaned accepted-member lock')
        try:original.run(features,embeddings,graph,evidence,out/'result',cfg,4)
        except ValueError as error:
            retain_refusal(error,out,before)
            raise
        audit = original.audit_cache(features,embeddings,graph,evidence,out/'result',cfg)
    accounts = {}
    for arm in ('density','selected'):
        accounts[arm] = export(features,result_root/(arm+'-partition.json'),fasta,out/'export'/arm,include_dna=False)
        validate_partition(data,result_root/(arm+'-partition.json'),features)
    require(consumed(features,embeddings,graph,evidence) == before, 'Bridge immutable inputs changed')
    write_json(out/'bridge.json',dict(status='PASS',source=proof,inputs=before,audit=audit,
        accepted_science_reused=accepted is not None,accounts=accounts,samples=meta['samples'],
        result_root=str(result_root.absolute()),accepted_members_copied=False,
        DNA_reuse=dict(fasta=binding(fasta),full_DNA_preserved=True,duplicate_FASTAs=False),
        native_learned_geometry_fixed=True,truth_accessed=False,
        composite_neighbor_recall_established=False))
    return audit
