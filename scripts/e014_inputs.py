#!/usr/bin/env python3
"""Verify complete accepted E009 axes and new lossless oral DNA, without fitting."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding,write_json
from e014_comparison import validate_plan
from dl_binner.multiview.views import load
from dl_binner.io import read_depth
from dl_binner.candidate.markers import load_cache


def main():
    """Read actual frozen matrices/cache and preserve a compact verified-axis receipt."""
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    plan=json.loads(a.plan.read_text());validate_plan(plan);u=plan['units']['E009-dev5'];repo=Path(__file__).absolute().parents[1]
    lock=json.loads((repo/'experiments/E010-coherent-prototype/candidate-lock.json').read_text())['inputs']
    for name,path in [('fasta',u['fasta']),('depth',u['depth']),('marker_hmm',plan['hmm']),('marker_manifest',plan['asset_manifest'])]:
        if binding(path)!=lock[name]:raise ValueError('Accepted E009 full input bytes differ: '+name)
    data,meta=load(u['features']);ids=data['ids'].tolist();samples,depth=read_depth(u['depth'],ids)
    if len(samples)!=10 or samples!=meta['samples']or not np.array_equal(depth,data['depth'])or meta['fasta_sha256']!=lock['fasta']['sha256']:
        raise ValueError('Full ordered ten-depth/contig axes differ')
    marker=load_cache(u['marker_cache'],u['fasta'],ids)
    oral=Path(plan['units']['oral-dev5']['fasta']);proof=json.loads(oral.with_suffix(oral.suffix+'.restored.json').read_text())
    if binding(oral)!=proof['restored']:raise ValueError('Lossless oral DNA differs')
    write_json(a.output,dict(status='PASS',E009=dict(contigs=len(ids),bp=int(data['lengths'].sum()),eligible=int(data['eligible'].sum()),
        ordered_samples=samples,depth_shape=list(depth.shape),all_zero_depth_rows=int((~data['depth_evidence']).sum()),features=binding(u['features']),
        marker_profiles=marker['profile_count'],canonical_families=marker['canonical_families']),
        oral=dict(DNA=proof['restored'],source_blind=True,sequence_only=True),truth_read=False))
    print('E014_COMPLETE_INPUT_AXES_VERIFIED',len(ids),len(samples),flush=True)


if __name__=='__main__':main()
