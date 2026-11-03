#!/usr/bin/env python3
"""Complete observed-zero E009 strata using only admitted new partitions.

The primary frozen reviewers already retain all length/origin/marker/excluded/
unassigned DNA. This adds their existing coverage-population function for E009
and verifies the three exact cached query axes. It performs no inference,
search, bin selection, changed threshold or old-baseline scoring.
"""
import argparse
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))


def run(base,output):
    """Bind full E009 DNA, ten actual depth columns and every new assignment."""
    import numpy as np
    from threadpoolctl import threadpool_limits
    from e024_coverage import binding,write
    from e025_review import coverage_populations
    from dl_binner.multiview.views import load
    from dl_binner.information.export import validate_partition
    threadpool_limits(4);base=Path(base).absolute();output=Path(output)
    admitted=json.loads((base/'native-review-admission.json').read_text())
    if admitted['provider_status']!='TERMINATED'or not admitted['archive_and_every_member_verified']:
        raise ValueError('Independent scientific/diagnostic return admission required')
    features=ROOT/'artifacts/e011-cached-grouping-reference/restore-local/candidate/features/features.npz'
    expected=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/reuse-lock.json').read_text())
    wanted=expected['learning_files']['/srv/dl_binner/experiments/e011/phase-20261017T005141Z-ab80312/restore/candidate/features/features.npz']
    if binding(features)!=wanted:raise ValueError('Exact accepted E009 feature bytes differ')
    data,meta=load(features)
    lock=json.loads((ROOT/'experiments/E013-marker-quality/review-lock.json').read_text())
    truth=json.loads((ROOT/lock['truth_root']/'truth.json').read_text())
    targets=json.loads((ROOT/lock['truth_root']/'targets.json').read_text())['targets']
    clean=set(json.loads((ROOT/'artifacts/e011-cached-grouping-reference/restore-local/candidate/markers/evidence.json').read_text())['clean'])
    if data['ids'].tolist()!=truth['ordered_contig_ids']or len(targets)!=156 or len(meta['samples'])!=10:
        raise ValueError('Complete DNA/target/ten-depth axes differ')
    labels={q:c['AMBER_label']for q,c in truth['contigs'].items()}
    genomes=sorted({g for g in labels.values()if g is not None});index={g:i for i,g in enumerate(genomes)}
    lab=np.asarray([index.get(labels[q],-1)for q in data['ids']],np.int64)
    inv=json.loads((base/'inventory.json').read_text())['all_work_members'];populations={}
    for unit in ['E009-noGLM','E009-GLM']:
        values={}
        for family,arms in [('E023',['density','selected']),('E030',['root-only','pre','post'])]:
            for arm in arms:
                relative=(unit+'/e023/science/result/'if family=='E023'else unit+'/construct/result/')+arm+'-partition.json'
                p=base/'verified/work'/relative
                if binding(p)!=inv[relative]:raise ValueError('New partition inventory binding differs')
                validate_partition(data,p,features);part=json.loads(p.read_text())
                values[family+'/'+arm]=coverage_populations(data,part,lab,genomes,targets,clean)
        populations[unit]=values
    queries=json.loads((ROOT/'experiments/E031-bootstrap-preserving-learning/query-axes.json').read_text())
    query_bindings={}
    for unit in ['E009-noGLM','E009-GLM','oral-noGLM']:
        relative=unit+'/e023/query-neighbors.json';p=base/'verified/work'/relative;value=json.loads(p.read_text())
        if (binding(p)!=inv[relative]or [dict(id=q['id'],strata=q['strata'])for q in value['queries']]!=queries[unit]['student']['queries']):
            raise ValueError('Original source-blind query axis differs')
        query_bindings[unit]=dict(binding=binding(p),queries=len(value['queries']))
    with (base/'summary/learning-targets.tsv').open()as f:rows=list(csv.DictReader(f,delimiter='\t'))
    represented={}
    for unit in ['E009-noGLM','E009-GLM','oral-noGLM']:
        at=[r for r in rows if r['unit']==unit]
        represented[unit]=dict(confirmed_reference_union_bp=sum(int(r['assembly_confirmed_bp'])for r in at),
            full_provided_reference_bp=sum(int(r['reference_bp'])for r in at),
            scope='Diagnostic represented source-coordinate unions; unchanged primary full-reference denominator')
    result=dict(status='PASS',E009_full_population_measured_depth=populations,
        all_three_source_blind_query_axes=query_bindings,represented_reference_unions=represented,
        primary_or_secondary_scores_recomputed=False,model_or_search_run=False,
        original_Mac_portability_tolerance_unchanged=True)
    write(output,result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=run(a.base,a.output);print('PASS full new-output observed-zero strata and exact cached query axes')
