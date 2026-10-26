#!/usr/bin/env python3
"""Native E023 admission: reuse accepted runtime, actual readers and tiny DAG.

No installation, source recopy, training, community grouping or cloud API.
All gates share the parent's VM-start clock. The original installed package is
verified separately before the explicitly frozen research source overlay.
"""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from e009_owner import supervisor
from e014_collect import binding
from e021_control_json import publish
from e023_control import validate_plan,verify_reuse,verify_source,UNITS


def workflow_probe(python_version,workflow_version):
    """Return the same isolated version/origin probe for local and native prefixes."""
    code='''import importlib.metadata as metadata,json,platform,sys
from pathlib import Path
expected=EXPECTED
d=metadata.distribution('snakemake')
if (platform.python_version(),d.version)!=expected:raise ValueError('Frozen workflow Python/Snakemake version differs')
if not Path(d._path).resolve().is_relative_to(Path(sys.prefix).resolve()):raise ValueError('Foreign workflow distribution')
print(json.dumps(dict(status='PASS_WORKFLOW_VERSION_ORIGIN',python=platform.python_version(),snakemake=d.version,prefix=sys.prefix,distribution=str(Path(d._path).resolve()))))
'''.replace('EXPECTED',repr((python_version,workflow_version)))
    compile(code,'E023-workflow-probe','exec')
    return code


def readers(plan,output):
    """Read exact full feature/vector/sparse/marker and baseline axes without science."""
    from dl_binner.density.grouping import load_inputs,sparse_input
    from dl_binner.information.export import validate_partition
    validate_plan(plan);verify_reuse(plan['reuse_lock']);result={}
    expected_depth=json.loads((ROOT/'experiments/E010-coherent-prototype/candidate-lock.json').read_text())['ordered_depth_columns']
    for unit in UNITS:
        u=plan['units'][unit];data,x,valid,meta=load_inputs(u['features'],u['embeddings'])
        sparse_input(u['graph'],data['ids'].tolist(),valid,u['embeddings'])
        validate_partition(data,u['baseline_partition'],u['features'])
        evidence=json.loads(Path(u['marker_evidence']).read_text())
        if (not set(evidence['calls']) <= set(data['ids'].tolist()) or evidence['panel_size']!=len(evidence['families'])
                or (meta['samples']!=expected_depth if unit=='E009-E022' else bool(meta['samples']))):
            raise ValueError('Full marker/sample axes differ')
        # bp is bound by the accepted feature bytes; oral full count checked below.
        if len(data['ids'])!=(145702 if unit=='E009-E022' else 1286547):raise ValueError('Full contig axis differs')
        if unit=='E009-E022'and int(data['lengths'].sum())!=231678157:raise ValueError('E009 full DNA differs')
        if unit=='oral-E019'and int(data['lengths'].sum())!=1669981123:raise ValueError('Oral full DNA differs')
        result[unit]=dict(contigs=len(data['ids']),bp=int(data['lengths'].sum()),samples=meta['samples'],
                          eligible=int(valid.sum()),marker_loci=len(evidence['loci']))
        del data,x,valid,evidence
    publish(dict(status='PASS_FULL_READERS_NO_GROUPING',units=result),Path(output))


def run(path):
    """Capture all current Linux exits before held-parent scientific release."""
    cfg=json.loads(Path(path).read_text());root=Path(cfg['root']);repo=Path(cfg['repo'])
    g=root/'gates';g.mkdir(exist_ok=False);plan=json.loads(Path(cfg['science_plan']).read_text())
    publish(verify_source(),g/'source.json')
    lock=json.loads(Path(plan['reuse_lock']).read_text())
    s=supervisor();env=s.isolated_env(4);env.update(NUMBA_NUM_THREADS='4',NUMBA_CACHE_DIR=str(root/'native-cache'),TMPDIR=str(root/'tmp'))
    deadline=min(cfg['vm_start_epoch']+1800,cfg['vm_start_epoch']+7200-600);stages=[]
    def command(name,argv):
        r=s.supervise(argv,g/(name+'.log'),deadline-time.time(),26_000_000_000,env,sample_root=__import__('os').getpid())
        stages.append(dict(name=name,resources=r))
    command('workflow-version',[plan['workflow_python'],'-I','-B','-c',
        workflow_probe(lock['workflow_python_version'],lock['workflow_version'])])
    command('accepted-runtime',[plan['python'],'-I','-B',str(repo/'scripts/e023_runtime.py'),
        '--reference',lock['runtime_reference'],'--output',str(g/'runtime.json')])
    command('full-readers',[plan['python'],'-I','-B',str(repo/'scripts/e023_gates.py'),'--readers',cfg['science_plan'],'--output',str(g/'readers.json')])
    command('tiny-readers-selection-export',[plan['python'],'-I','-B',str(repo/'scripts/e023_checks.py')])
    command('tiny-DAG-collection',[plan['python'],'-I','-B',str(repo/'scripts/e023_tiny.py'),'--root',str(g/'tiny-DAG'),'--workflow-python',plan['workflow_python']])
    publish(dict(status='SUCCESS',config=binding(path),stages=stages,elapsed_since_VM_start_seconds=time.time()-cfg['vm_start_epoch'],
                 source_overlay='exact committed source; original installed package/runtime checked separately; no install'),g/'completion.json')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path);p.add_argument('--readers',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.config:run(a.config)
    elif a.readers and a.output:readers(json.loads(a.readers.read_text()),a.output)
    else:p.error('Select native config or readers/output')
