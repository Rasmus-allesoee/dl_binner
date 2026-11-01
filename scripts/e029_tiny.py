#!/usr/bin/env python3
"""Exercise the actual cached three-mode DAG, six-cache barrier, no-op and collector."""
import argparse,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/product')]
from e024_coverage import binding,write


def run(root,workflow_python):
    """Use actual tiny DNA/sparse caches; fits, marker detection and GLM inference are absent."""
    from discovery_fixture import fixture
    from e029_control import UNITS,COMPONENTS
    from e029_collect import CONTROLS,pack,collect_controls,verify
    root=Path(root).absolute();root.mkdir(parents=True,exist_ok=False);f=fixture(root/'input',64)
    source=root/'accepted-fixture'
    for u,r in COMPONENTS:
        for label,path in [(r+'-embed/embeddings.npz',f['embeddings']),(r+'-embed/embeddings.json',f['embeddings'].with_suffix('.json')),(r+'-graph/graph.npz',f['graph']),(r+'-graph/graph.json',f['graph'].with_suffix('.json'))]:
            dst=source/'units'/u/label;dst.parent.mkdir(parents=True,exist_ok=True);os.link(path,dst)
    p=json.loads((ROOT/'experiments/E029-certifiable-joint-retrieval/runtime-plan.json').read_text())
    p.update(work=str(root/'work'),source_work=str(source),python=sys.executable,workflow_python=str(Path(workflow_python).absolute()),worker=str(ROOT/'scripts/e029_control.py'),snakefile=str(ROOT/'experiments/E029-certifiable-joint-retrieval/Snakefile'),engineering=True,
        units={u:dict(features=str(f['features']),fasta=str(f['fasta']),marker_evidence=str(f['evidence']),frozen=None) for u in UNITS})
    p['retained_cache_work']=str(root/'retained')
    from dl_binner.discovery.grouping import prepare
    for u,r in COMPONENTS[:4]:
        prepare(f['features'],f['embeddings'],f['graph'],Path(p['retained_cache_work'])/'retrieval'/u/r/'cache')
    write(root/'plan.json',p)
    argv=[sys.executable,'-I','-B',str(ROOT/'scripts/e029_control.py'),'--plan',str(root/'plan.json'),'--engineering','--workflow']
    def call(name):
        with (root/(name+'.log')).open('x') as log:v=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT)
        write(root/(name+'.exit.json'),dict(argv=argv,exit_code=v.returncode))
        if v.returncode:raise RuntimeError('Actual cached tiny DAG failed: '+str(root/(name+'.log')))
    call('first');events=[];active=None
    for line in (root/'first.log').read_text().splitlines():
        if line.startswith('localrule ') and not line.startswith('localrule all:'):
            if active is not None:raise ValueError('Independent ready rules overlapped')
            active=line.split()[1].rstrip(':');events.append(active)
        if 'Finished jobid:' in line:active=None
    if len(events)!=19 or events[6]!='barrier' or not all(x.endswith('_retrieve') for x in events[:6]):raise ValueError('Actual six-cache barrier/schedule differs: '+repr(events))
    before={str(p):binding(p) for p in (root/'work').rglob('*') if p.is_file() and '.snakemake' not in p.parts}
    call('verified-resume')
    if 'Nothing to be done' not in (root/'verified-resume.log').read_text() or any(binding(p)!=b for p,b in before.items()):raise ValueError('Resume replayed/changed completed science')
    phase=root/'phase';phase.mkdir();evidence=root/'evidence';evidence.mkdir()
    for name in CONTROLS+['config.json','science-plan.json','started.json','release.json','science-result.json','science-disk.jsonl','external-data.json']:
        d=phase/name;d.parent.mkdir(parents=True,exist_ok=True);write(d,dict(data_copied=False,fixture=True) if name=='external-data.json' else dict(fixture=True))
    collect_controls(phase,evidence/'controls');write(evidence/'external-data.json',dict(data_copied=False))
    result=pack(root/'work',evidence,root/'return');verify(root/'return/e029-evidence.tar.gz',result['archive'])
    write(root/'completed.json',dict(status='PASS',real_ready_rule_events=events,no_overlap=True,all_six_retrievals_before_bins=True,completed_resume_noop=True,actual_archive=result,
        synthetic=['numeric original embeddings/native-neighbor cache','hand-authored marker evidence'],real=['FASTA/feature/sparse readers','bin selection/refinement','all-DNA export','Snakemake barrier and scheduling','member/alias collector'],scientific_fits=0,external_binners=0))


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--root',type=Path,required=True);a.add_argument('--workflow-python',type=Path,required=True);v=a.parse_args();run(v.root,v.workflow_python)
