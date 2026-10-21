"""Actual E018 restore/refinement/export contracts on previously passed tiny DNA.

The cached source contains synthetic DNA/HMM/unit vectors generated in E017.
Only the new cache consumer, unchanged real marker-cache reader/refiner and full
FASTA exporter run here. No new graph, feature bank, marker search or fit occurs.
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).absolute().parents[2]/'scripts'))


def run(cached,output):
    """Exercise both actual depth-present and sequence-only tiny cached formats."""
    from e018_recruit import consume
    from e018_control import audit
    from e017_review import export_contract,legacy_membership_views
    from e010_review import refinement_membership
    from e013_review import verify_choices
    from dl_binner.multiview.downstream import refine
    from dl_binner.multiview.views import config,load
    from dl_binner.information.export import export,validate_partition
    from dl_binner.io import digest,write_json
    cached,output=Path(cached),Path(output);output.mkdir(parents=True,exist_ok=False);results={}
    before={str(p.relative_to(cached)):digest(p)for p in cached.rglob('*')if p.is_file()}
    for mode in ['depth','sequence']:
        original=cached/mode;root=output/mode;root.mkdir();features=original/'features/features.npz'
        result=consume(features,original/'group',root/'group')
        refine(features,original/'embeddings.npz',root/'group/partition.json',cached/'markers',
               cached/'assembly.fna',cached/'engineering-marker.hmm',root/'refine',config())
        data,meta=load(features);parts=[validate_partition(data,root/p,features)for p in
            ['group/partition.json','refine/old-partition.json','refine/partition.json']]
        views=legacy_membership_views(parts,[[]for _ in data['ids']]);refinement_membership(views[0],views[1])
        choices=verify_choices(*views,json.loads((root/'refine/decisions.json').read_text()),json.loads((root/'refine/alternatives.json').read_text()))
        for arm,part in zip(['pre','old','post'],['group/partition.json','refine/old-partition.json','refine/partition.json']):
            export(features,root/part,cached/'assembly.fna',root/('export-'+arm),include_dna=arm=='post')
            export_contract(json.loads((root/part).read_text()),data,root/('export-'+arm))
        audit(features,original/'group',root/'group',root/'audit.json')
        results[mode]=dict(result=result,choices=choices,export_contracts='PASS_ALL_THREE_FULL_AXES',
                           samples=meta['samples'],vectors='Retained synthetic unit vectors; no fit/inference contract claimed')
    if before!={str(p.relative_to(cached)):digest(p)for p in cached.rglob('*')if p.is_file()}:
        raise ValueError('Retained tiny cache mutated')
    record=dict(status='PASS',results=results,old_tiny_bytes_unchanged=True,marker_search=False,index_rebuilt=False)
    write_json(output/'fixture.json',record);return record


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cached',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(run(a.cached,a.output)),flush=True)
