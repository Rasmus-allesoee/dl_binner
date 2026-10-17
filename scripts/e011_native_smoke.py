#!/usr/bin/env python3
"""Exercise the changed restore/control adapter on accepted tiny cached evidence.

Reuse actual pre-existing engineering features/marker evidence/vectors, without
training, HMM search or index construction. Only this explicitly tiny invocation
uses the tiny archived configuration/input hashes; the community CLI stays locked.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding,write_json
from e011_cached import restore,control


def run(payload,output):
    """Verify portable fixture members then use production readers/refinement/export."""
    payload,output=map(Path,[payload,output]);output.mkdir(parents=True,exist_ok=False)
    assets=json.loads((Path(__file__).parents[1]/'experiments/E011-cached-grouping-reference/assets.json').read_text())
    for name in ['tiny-native-cache.tar.gz','tiny-assembly.fna','tiny-depth.tsv']:
        if binding(payload/name)!=assets['fixture_files'][name]:raise ValueError('Tiny accepted fixture bytes differ')
    restored=output/'restored';restore(payload/'tiny-native-cache.tar.gz',restored,assets['fixture_files']['tiny-native-cache.tar.gz'])
    cfg=json.loads((restored/'candidate/candidate.json').read_text())
    protocol=dict(config=cfg,inputs=dict(fasta=binding(payload/'tiny-assembly.fna'),depth=binding(payload/'tiny-depth.tsv')))
    control(restored,payload/'tiny-assembly.fna',payload/'tiny-depth.tsv',output/'control',protocol)
    write_json(output/'passed.json',dict(status='PASS',production_adapter=True,
        fixture_only=True,no_training_detection_or_index=True,completed=binding(output/'control/completed.json')))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--payload',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.payload,a.output)
