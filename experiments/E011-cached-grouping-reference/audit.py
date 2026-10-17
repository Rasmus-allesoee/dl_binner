"""Audit frozen dev4 implementation choices against unchanged retained E010 bytes.

This is read-only inspection and independent arithmetic, not a refit, marker scan,
new partition, model repair or changed quality score. Historical prose is preserved;
the seed-rule discrepancy is reported explicitly rather than silently corrected.
"""
from pathlib import Path
import argparse
import json
import sys
import time
import numpy as np
sys.path.insert(0,str(Path(__file__).absolute().parents[2]/'scripts'))
from e009_common import binding, write_json
from e010_review import require, refinement_membership


def audit(root, output):
    """Check exact source/statistics, pairing, depth conditioning and actual seed logs."""
    from dl_binner.io import load_arrays
    from dl_binner.runner import source_records
    repo=Path(__file__).absolute().parents[2];root=Path(root);started=time.monotonic()
    lock=json.loads((repo/'experiments/E010-coherent-prototype/candidate-lock.json').read_text())
    require(source_records()==lock['package_files'],'Frozen installed source differs')
    for name,expected in lock['package_files'].items():
        require(binding(repo/'src/dl_binner'/name)==expected,'Tracked frozen source differs')
    f,fm=load_arrays(root/'features/features.npz','features')
    v,vm=load_arrays(root/'features/views.npz','candidate_views')
    cp=json.loads((root/'train/checkpoint.json').read_text());cfg=cp['config']
    stats={}
    for key,x in [('tnf',np.sqrt(f['tnf'])),('depth',np.log1p(f['depth']))]:
        x=x[f['eligible']].astype(np.float64)
        mean,std=x.mean(0),x.std(0)
        require(np.array_equal(mean,np.array(cp['transform'][key]['mean']))
                and np.array_equal(std,np.array(cp['transform'][key]['std'])), 'Fitted parent transform differs')
        stats[key]=dict(dimensions=x.shape[1],zero_variance_columns=int((std<=1e-8).sum()),
                        eligible_fit_rows=len(x),exact_saved_stats=True)
    require(np.array_equal(v['trainable'],f['eligible']&(v['valid_fourmers']>0).all(1)), 'Wrong training population')
    trainable=v['trainable'];coords=v['coordinates'][trainable]
    require(np.all(coords[:,0,1]<=coords[:,1,0]) and np.all(coords[:,2,1]<=coords[:,3,0]), 'Positive pairs overlap')
    duplicate=np.all(coords[:,:2]==coords[:,2:],axis=(1,2))
    lengths=f['lengths'];ids=f['ids'].tolist();positions={q:i for i,q in enumerate(ids)}
    pre=json.loads((root/'group/partition.json').read_text());post=json.loads((root/'refine/partition.json').read_text())
    marker=json.loads((root/'markers/evidence.json').read_text());seed_rows=[]
    for attempt in post['attempts']:
        if len(attempt['before'])<2:continue
        counts=attempt['before'];maximum=max(counts.values());k=sorted(counts.values(),reverse=True)[1]
        family=min(q for q,n in counts.items()if n==k)
        seeds=sorted((i for i,b in enumerate(pre['assignment'])if b==attempt['pre_bin'] and family in marker['clean'].get(ids[i],[])),
                     key=lambda i:(-int(lengths[i]),ids[i]))
        require(attempt['k']==k and attempt['seed_family']==family and attempt['seed_ids']==[ids[i]for i in seeds],
                'Actual logged refinement seed differs from frozen second-count policy')
        seed_rows.append(dict(pre_bin=attempt['pre_bin'],largest_count=maximum,second_count=k,
            seed_family=family,adopted=attempt['adopted'],differs_from_prose_largest=maximum!=k))
    result=dict(status='PASS with documented design discrepancy and scientific risks',source=binding(__file__),
        frozen_source_members=lock['package_files'],original_review=binding(repo/'experiments/E010-coherent-prototype/review.json'),
        transformations=stats,windows=dict(trainable_parents=int(trainable.sum()),eligible_parents=int(f['eligible'].sum()),
            real_windows=int((v['valid_fourmers']>0).sum()),training_bp=int(lengths[trainable].sum()),
            inference_only_eligible_parents=int((f['eligible']&~trainable).sum()),
            identical_two_pair_coordinates=int(duplicate.sum()),independent_pair_coordinates=int((~duplicate).sum()),
            explanation='For parents <=20000bp, each capped window fills its half; two seeded draws therefore coincide. Correct sampling, limited augmentation diversity.'),
        parent_depth=dict(samples=fm['samples'],zero_rows=int((f['depth']==0).all(1).sum()),
            semantics='Both positive windows share measured full-parent means; no measured window coverage/variance. Fitted log1p mean/std applied once; all-zero branch masked.'),
        marker_seed=dict(classification='Real prose/code design-contract discrepancy, not an out-of-range index or demonstrated performance cause',
            prose='most repeated clean family',executed='second-largest repeated-family count; lexicographic family at that count',
            possible_rationale='Largest split count supported by at least two independent repeated families; conservative against one anomalous family. This rationale was not explicit in the old prose.',
            actual_attempts=seed_rows,affected_attempts=sum(x['differs_from_prose_largest']for x in seed_rows),
            affected_adopted=sum(x['differs_from_prose_largest']and x['adopted']for x in seed_rows),
            control_policy='Preserve actual executed refinement; do not change it inside the CPM control'),
        refinement=refinement_membership(pre,post),
        inspection=dict(contrastive='Symmetric normalized dot products; positive index offset N; batch tail merged; every training parent seen each epoch; no labels/markers in training.',
            graph='Unit sphere -> Euclidean candidate search -> exact cosine rerank -> positive symmetric local weights; retained opaque-ID mapping and all-weight arithmetic passed prior independent review.',
            refinement='Length-weighted spherical centers, seed anchors, clean-family cannot-link, affinity/margin refusal, supported conflict-free adoption; no merge or rescue of prior noise.',
            evaluation='Same admitted independent sequence truth, all bin DNA purity, full references and duplicate-safe unions; original dev3 values reused. No denominator substitution or changed score here.'),
        unresolved=['No fatal arithmetic/axis/pairing/evaluation defect identified; this is not proof of optimality or exhaustive absence of bugs',
            'Long-only training, noisy/short TNF transfer, shared parent-depth shortcut and co-genomic negatives remain plausible representation risks',
            'Most-repeated prose differs from executed conservative seeds; effect of changing that policy is unmeasured',
            'Coarse RB communities and spherical affinity/unassignment can lose recovery even with improved local neighbors',
            'Exact native reload passed; original strict Mac portability failure remains unresolved and unchanged',
            'Low assembly availability, N quarantine and conservative purity restrict interpretation, not proof of bad simulation'],
        wall_seconds=time.monotonic()-started,no_new_training_partition_or_score=True)
    write_json(output,result)
    print(json.dumps({k:result[k]for k in ['status','windows','marker_seed','wall_seconds']}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();audit(a.root,a.output)
