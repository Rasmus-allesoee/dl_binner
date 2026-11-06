#!/usr/bin/env python3
"""Re-use the passed E035 tiny science for the complete new sliced return reader.

No fit, view inference, graph construction or classification is repeated. Only
new compact staging, archive/readback, fresh restore and reader contracts run.
"""
import argparse
import json
import os
from pathlib import Path
import sys

import dl_binner as _owned_product

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write


def run(root):
    """Require all passed seals and exercise actual three-mode restore/reader paths."""
    from e035_control import UNITS,STAGES,product_scope
    from e024_control import verify_seal
    from e035_collect import compact_classification,pack,restore,verify
    from e035_review import contract
    product_scope();root=Path(root).absolute();p=json.loads((root/'plan.json').read_text())
    if json.loads((root/'completed.json').read_text())['status']!='PASS':raise ValueError('No completed tiny science to reuse')
    before={}
    for u in UNITS:
        for stage in STAGES:
            verify_seal(root/'work'/u/stage)
            for f in (root/'work'/u/stage).rglob('*'):
                if f.is_file():before[str(f)]=binding(f)
    classification=root/'classification';reuse_path=classification/'verified-reuse.json'
    native=None
    if reuse_path.is_file():
        # A verified tiny reuse has fresh normalization/annotation receipts, not
        # another native execution. Preserve both namespaces without fabricating
        # a second native completed.json or weakening the strict compact reader.
        reused=json.loads(reuse_path.read_text());native=Path(reused['source'])
        if (reused['status']!='PASS' or reused['native_classification_not_replayed']is not True
                or binding(native/'taxonomy.tsv')!=reused['raw']
                or any(binding(native/(n+'.exit.json'))!=b or json.loads((native/(n+'.exit.json')).read_text())['exit_code']!=0 for n,b in reused['original_exits'].items())):
            raise ValueError('Retained actual native classifier reuse changed')
    for c in ['E009','oral']:
        destination=root/'work/classifications'/c
        if native is None:compact_classification(classification,destination)
        else:
            destination.mkdir(parents=True,exist_ok=False)
            compact_classification(native,destination/'original-native')
            kept={}
            for source in classification.rglob('*'):
                if source.is_symlink():raise ValueError('Unexpected normalized classifier reuse alias')
                if source.is_file():
                    name=source.relative_to(classification);target=destination/name;target.parent.mkdir(parents=True,exist_ok=True)
                    os.link(source,target);kept[str(name)]=binding(source)
            write(destination/'compact-stage.json',dict(status='PASS_VERIFIED_NATIVE_REUSE_WITH_FRESH_NORMALIZATION',
                new_native_classification=False,normalization_members=kept,
                original_native_manifest=binding(destination/'original-native/compact-stage.json')))
    e=root/'evidence-v2';e.mkdir();write(e/'scope.json',dict(engineering=True,VM_started=False,truth_scored=False,
        actual='passed installed final wheel; real native classifier; actual 31-stage learning/construction; new full sliced archive/alias restore and review readers',
        mocked='synthetic reference taxa; generated DNA; NumericExtractor GLM bank and synthetic retained marker calls'))
    packed=pack(root/'work',e,root/'return-v2');verify(root/'return-v2');staged=restore(root/'return-v2',root/'restored-v2')
    write(root/'return-v2/admission.json',dict(provider_status='TERMINATED',archive_and_every_member_verified=True,cost_and_retention_admitted=True,
        workflow_completed=True,exact_source_schedule_axes_verified=True,fixture_only=True,live_provider_or_billing_observed=False))
    readers={u:contract(root/'return-v2',staged,u,'student',p['units'][u]['features'],'learning',engineering=True)[-1]for u in UNITS}
    if any(binding(n)!=b for n,b in before.items()):raise ValueError('Accepted tiny scientific bytes changed during collection repair')
    protected=json.loads((root/'protected-inputs.json').read_text())
    if any(binding(n)!=b for n,b in protected.items()):raise ValueError('Original E031 tiny inputs changed')
    write(root/'complete-return-reader.json',dict(status='PASS',slices=packed['slices'],members=len(packed['all_work_members']),
        full_classifier_and_per_ORF_companions_retained=True,all_three_actual_reader_contracts=readers,
        passed_science_not_replayed=True,original_E031_inputs_unchanged=True,live_cloud_or_community_score=False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);a=p.parse_args();run(a.root)
