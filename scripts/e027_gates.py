#!/usr/bin/env python3
"""Native common-version admission inside the original held-parent CPU clock.

Reuse complete accepted dependencies read-only; install only the locked new wheel
into a fresh package prefix. Actual Linux model/graph/marker/MetaBAT/tiny-DAG and
full-input readers must pass before any community fit. No acquisition fallback.
"""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
from e027_control import freeze
from e024_coverage import binding, write
from e021_control_json import publish
from e023_gates import workflow_probe
from e009_owner import supervisor


def publish_completion(path, value):
    """Atomically publish only all-zero gates with explicit package/dependency scope."""
    if (value.get('status') != 'PASS' or value.get('full_science_started') is not False
            or value.get('no_dependency_install_or_science_recopy') is not True
            or value.get('owned_package_install_explicit') is not True or not value.get('stages')
            or any(s['resources'].get('exit_code') != 0 for s in value['stages'])):
        raise ValueError('Incomplete/failed native gate cannot publish ready control')
    publish(value, path)


def unit_command(repo):
    """Run installed new modules with product fixtures, excluding checkout source."""
    code = ('import sys,unittest;from pathlib import Path;r=Path('+repr(str(repo))+');'
        'sys.path[:0]=[str(r/"tests/product"),str(r/"tests"),str(r/"scripts")];'
        'v=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames('
        '["test_unified","test_e027_operations"]));sys.exit(not v.wasSuccessful())')
    compile(code, 'native-E027-contracts', 'exec'); return code


def readers(plan, output):
    """Read exact complete arrays/banks/axes and both native measurement contracts."""
    from e027_control import verify_inputs
    from dl_binner.multiview.views import load
    from dl_binner.context.tokens import Bank
    from dl_binner.hybrid.bank import Bank as FrozenBank
    record = verify_inputs(plan)
    checked = set()
    for name, u in plan['units'].items():
        data, meta, views, vm = load(u['original_features'], u['views'])
        if u['tokens'] not in checked:
            Bank(u['tokens'], u['original_features'], u['views'], data, meta, views)
            checked.add(u['tokens'])
        if u['frozen']:
            FrozenBank(u['frozen'], u['original_features'], u['views'], data, meta, views)
    from e027_learning_reuse import verify
    from dl_binner.unified.training import configuration
    reuse = json.loads(Path(plan['learning_reuse_lock']).read_text())
    for producer, files in reuse['producer_scientific_module_identity'].items():
        if any(binding(ROOT/'src/dl_binner'/name) != wanted for name, wanted in files.items()):
            raise ValueError('Same-version accepted learning implementation differs: '+producer)
    record['identical_learning'] = {}
    for name, entries in reuse['models'].items():
        u = plan['units'][name]
        record['identical_learning'][name] = {role: verify(entry, u,
            configuration(u['frozen'] is not None), u['views'], u['tokens']) for role, entry in entries.items()}
    from e027_reference import validate_means
    ref = plan['reference']; record['oral_cvExt_means'] = validate_means(ref['matrix'], ref['matrix_receipt'], ref['fasta'])
    record['full_original_token_and_optional_native_GLM_readers'] = True
    write(output, record)


def run(config):
    """Capture each native exit and atomically expose completion only after all pass."""
    cfg = json.loads(Path(config).read_text()); p = json.loads(Path(cfg['plan']).read_text())
    root = Path(cfg['root']); out = root/'gates'; out.mkdir(exist_ok=False)
    write(out/'source.json', freeze())
    reuse = json.loads((ROOT/'experiments/E027-common-information-binner/reuse-lock.json').read_text())
    deadline = cfg['vm_start_epoch']+2700
    sup = supervisor(); env = sup.isolated_env(4)
    env.update(NUMBA_NUM_THREADS='4', NUMBA_CACHE_DIR=str(root/'native-cache'), TMPDIR=str(root/'tmp'),
        HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    stages = []
    def command(label, argv):
        remaining = deadline-time.time()
        if remaining < 30: raise TimeoutError('Native setup forecast exceeded original 45-minute allowance')
        value = sup.supervise(argv, out/(label+'.log'), remaining, 26_000_000_000, env, sample_root=__import__('os').getpid())
        stages.append(dict(stage=label, resources=value))
    base = reuse['native_dependency_base']
    wheel = Path(p['wheel']); candidate = json.loads((ROOT/'experiments/E027-common-information-binner/candidate-lock.json').read_text())
    if binding(wheel) != candidate['wheel']: raise ValueError('Native locked wheel transfer differs')
    command('workflow-origin', [p['workflow_python'], '-I', '-B', '-c', workflow_probe('3.12.10', '9.16.3')])
    # Full version/source/library probe of the passed complete base precedes reuse.
    accepted = json.loads((ROOT/'experiments/E023-adaptive-density-bins/reuse-lock.json').read_text())
    command('accepted-numerical', [accepted['numerical_python'], '-I', '-B', str(ROOT/'scripts/e023_runtime.py'),
        '--reference', accepted['runtime_reference'], '--output', str(out/'base-runtime.json')])
    command('package-install', [base+'/bin/python', '-I', '-B', str(ROOT/'scripts/e019_runtime.py'), 'create',
        '--base', base, '--destination', str(root/'env'), '--wheel', str(wheel), '--output', str(out/'package-install.json')])
    command('owned-complete-runtime', [p['python'], '-I', '-B', str(ROOT/'scripts/e027_runtime.py'),
        '--base', base, '--reference', reuse['native_runtime_reference'], '--candidate-lock',
        str(ROOT/'experiments/E027-common-information-binner/candidate-lock.json'), '--output', str(out/'runtime.json')])
    command('installed-model-graph-contracts', [p['python'], '-I', '-B', '-c', unit_command(ROOT)])
    met = reuse['metabat_install']
    code = ('import sys,json;from pathlib import Path;sys.path.insert(0,'+repr(str(ROOT/'scripts'))+');'
        'from e011_metabat import verify_install,probe;'
        'from e024_coverage import write;'
        'write(Path('+repr(str(out/'metabat-install.json'))+'),verify_install('+repr(met['metabat_prefix'])+','+
        repr(met['retained_install_receipt'])+','+repr(met['metabat_install_receipt'])+'));'
        'probe('+repr(p['reference']['binary'])+','+repr(str(out/'metabat-runtime.json'))+')')
    compile(code, 'actual-MetaBAT-native-gates', 'exec')
    command('metabat-native-readers-writers', [p['python'], '-I', '-B', '-c', code])
    command('serial-tiny-DAG', [p['python'], '-I', '-B', str(ROOT/'scripts/e027_tiny.py'),
        '--root', str(out/'tiny-DAG'), '--workflow-python', p['workflow_python'], '--metabat', p['reference']['binary']])
    command('synthetic-width-runtime', [p['python'], '-I', '-B', str(ROOT/'scripts/e027_probe.py'), '--output', str(out/'schedule.json')])
    command('synthetic-approximate-graph', [p['python'], '-I', '-B', str(ROOT/'scripts/e027_probe.py'),
        '--graph-probe', '--output', str(out/'synthetic-graph.json')])
    command('retained-data', [p['python'], '-I', '-B', str(ROOT/'scripts/e027_gates.py'),
        '--inputs', cfg['plan'], '--output', str(out/'data.json')])
    publish_completion(out/'completion.json', dict(status='PASS', config=binding(config), stages=stages,
        original_start_epoch=cfg['vm_start_epoch'], finished_epoch=time.time(), source=freeze(),
        full_science_started=False, no_dependency_install_or_science_recopy=True,
        owned_package_install_explicit=True))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--config', type=Path)
    p.add_argument('--inputs', type=Path); p.add_argument('--output', type=Path); a = p.parse_args()
    if a.config: run(a.config)
    elif a.inputs: readers(json.loads(a.inputs.read_text()), a.output)
    else: p.error('Select native gates or complete read-only input admission')
