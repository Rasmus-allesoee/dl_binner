#!/usr/bin/env python3
"""Exercise the actual three-arm Snakemake/MetaBAT/collection paths on tiny DNA.

No community DNA, truth or cloud calls. Synthetic HMM annotations and NumericExtractor
GLM values are explicit mocks; all view, sparse, training, reload, export and native
MetaBAT readers/writers are real. A separate real detector contract owns detection.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'tests/product')]


def run(root, workflow_python, metabat):
    """Run all independent ready rules serially; verify unchanged completed resume."""
    from relational_fixture import fixture, NumericExtractor
    from dl_binner.hybrid.bank import prepare, model_pin
    from dl_binner.io import write_json
    from e024_coverage import binding
    from e027_collect import pack, collect_controls, CONTROLS, verify
    root = Path(root).absolute(); root.mkdir(parents=True, exist_ok=False)
    # Real native positive bins and malformed-order refusal, then the new streaming
    # exporter. Main tiny DAG deliberately keeps community-default 200 kb bins.
    from e011_metabat import smoke
    from e027_reference import export as export_reference
    smoke(str(Path(metabat).absolute()), root/'native-positive')
    positive = export_reference(root/'native-positive/tiny.fa', root/'native-positive/native', root/'native-positive/new-streaming-export')
    if positive['bins'] < 1 or positive['contigs'] != 81: raise ValueError('New native positive export path failed')
    f = fixture(root/'inputs')
    prepare(f['fasta'], f['features'], f['views'], root/'frozen', NumericExtractor(), model_pin())
    physical = root/'physical.json'
    write_json(physical, dict(panel_size=4, calls={str(q): {'family-0': [1.]} for q in f['data']['ids'][:12]}))
    unit = dict(fasta=str(f['fasta']), original_features=str(f['features']), features=str(f['features']),
        views=str(f['views']), tokens=str(f['tokens']), frozen=None, marker_cache=str(f['markers']),
        hmm=str(f['hmm']), marker_evidence=str(physical), measured_receipt=None)
    # The production mean reader consumes the actual ordered FASTA axis.
    matrix = root/'mean.tsv'
    matrix.write_text('contig_id\t'+'\t'.join(f['metadata']['samples'])+'\n'+
        ''.join(str(q)+'\t'+'\t'.join(map(str, row))+'\n' for q, row in zip(f['data']['ids'], f['data']['depth'])))
    receipt = root/'mean.receipt.json'
    write_json(receipt, dict(status='PASS', matrix=binding(matrix), reference=binding(f['fasta']),
        rows=len(f['data']['ids']), samples=f['metadata']['samples'], missing_cells=0, all_cells_measured=True))
    p = json.loads((ROOT/'experiments/E027-common-information-binner/runtime-plan.json').read_text())
    p.update(work=str(root/'work'), python=sys.executable, workflow_python=str(Path(workflow_python).absolute()),
        worker=str(ROOT/'scripts/e027_control.py'), snakefile=str(ROOT/'experiments/E027-common-information-binner/Snakefile'),
        policy=str(ROOT/'experiments/E027-common-information-binner/policy.json'), engineering=True,
        units={'E009-noGLM': unit, 'E009-GLM': dict(unit, frozen=str(root/'frozen')), 'oral-noGLM': unit},
        reference=dict(fasta=str(f['fasta']), matrix=str(matrix), matrix_receipt=str(receipt), binary=str(Path(metabat).absolute())))
    write_json(root/'plan.json', p)
    argv = [sys.executable, '-I', '-B', str(ROOT/'scripts/e027_control.py'), '--plan', str(root/'plan.json'), '--engineering']
    env = dict(os.environ, NUMBA_NUM_THREADS='4', NUMBA_CACHE_DIR=str(root/'jit'))
    def call(label, action):
        with (root/(label+'.log')).open('x') as log:
            v = subprocess.run(argv+action, stdout=log, stderr=subprocess.STDOUT, env=env)
        write_json(root/(label+'.exit.json'), dict(exit_code=v.returncode, argv=argv+action))
        if v.returncode: raise RuntimeError('Actual tiny consumer failed: '+str(root/(label+'.log')))
    call('first', ['--workflow'])
    events = []; active = None
    for line in (root/'first.log').read_text().splitlines():
        if line.startswith('localrule ') and not line.startswith('localrule all:'):
            if active is not None: raise ValueError('Actual scheduler overlapped independent ready rules')
            active = line.split()[1].rstrip(':'); events.append(active)
        if 'Finished jobid:' in line: active = None
    from e027_control import STAGES, UNITS
    expected = ['oral_reference']+[u.replace('-', '_')+'_'+s.replace('-', '_') for u in UNITS for s in STAGES]
    if events != expected: raise ValueError('Actual priority/serial events differ: '+repr(events))
    before = {str(q): binding(q) for q in (root/'work').rglob('*') if q.is_file() and '.snakemake' not in q.parts}
    call('verified-completed-resume', ['--workflow'])
    if 'Nothing to be done' not in (root/'verified-completed-resume.log').read_text():
        raise ValueError('Completed scientific stages were not a verified no-op')
    if any(binding(q) != wanted for q, wanted in before.items()): raise ValueError('Completed stage changed on resume')
    # Actual restore-only consumer of these now-passed own tiny models. No fit,
    # inference, graph rebuild or metadata rewrite is allowed on this path.
    from e027_learning_reuse import restore, verify as verify_learning
    from dl_binner.unified.training import configuration
    import copy
    learned = root/'work/units/E009-GLM'; cfg = configuration(True); cfg.update(f['cfg'])
    reuse_proofs = {}
    teacher = None
    for role in ['teacher', 'student']:
        entry = dict(producer='own_completed_tiny_'+role, role=role,
            checkpoint=str(learned/role/'checkpoint.pt'), checkpoint_metadata=str(learned/role/'checkpoint.json'),
            reference=str(learned/role/'reference.npz'), reference_metadata=str(learned/role/'reference.json'),
            embeddings=str(learned/(role+'-embed/embeddings.npz')),
            embedding_metadata=str(learned/(role+'-embed/embeddings.json')),
            graph=str(learned/(role+'-graph/graph.npz')), graph_metadata=str(learned/(role+'-graph/graph.json')))
        entry['files'] = {v: binding(v) for k, v in entry.items() if k not in ['producer', 'role']}
        if role == 'student':
            entry.update(pairs=str(learned/'pairs/cache'), teacher_embedding=binding(teacher['embeddings']),
                         teacher_graph=binding(teacher['graph']))
            entry['files'].update({str(q): binding(q) for q in (learned/'pairs/cache').iterdir()})
        else: teacher = entry
        for kind in ['fit', 'embed', 'graph']+(['pairs'] if role == 'student' else []):
            reuse_proofs[role+'-'+kind] = restore(entry, p['units']['E009-GLM'], cfg,
                learned/'admit/views.npz', learned/'admit/tokens', root/'learning-reuse-contract'/(role+'-'+kind), kind)
        bad = copy.deepcopy(entry); bad['files'][entry['checkpoint_metadata']]['sha256'] = '0'*64
        try: verify_learning(bad, p['units']['E009-GLM'], cfg, learned/'admit/views.npz', learned/'admit/tokens')
        except ValueError: pass
        else: raise ValueError('Corrupt accepted learning was admitted')
    # Exact real controls/omission/alias writer, including linked token members.
    phase = root/'phase'; phase.mkdir(); evidence = root/'evidence'; evidence.mkdir()
    for name in CONTROLS+['config.json', 'science-plan.json', 'started.json', 'release.json',
                          'science-result.json', 'science-disk.jsonl', 'external-data.json']:
        path = phase/name; path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, dict(data_copied=False, fixture=True) if name == 'external-data.json' else dict(fixture=True))
    collect_controls(phase, evidence/'controls')
    write_json(evidence/'external-data.json', dict(data_copied=False, units=p['units'], fixture=True))
    collected = pack(root/'work', evidence, root/'return')
    verify(root/'return/e027-evidence.tar.gz', collected['archive'])
    write_json(root/'completed.json', dict(status='PASS', actual_three_mode_DAG=True,
        actual_serial_ready_rule_events=events, completed_resume_noop=True,
        actual_Metabat_cvExt=True, actual_collection=collected,
        actual_positive_native_bins_and_new_streaming_export=True,
        actual_restore_only_learning_contracts=reuse_proofs,
        mocked=['GLM numerical inference only', 'synthetic hand-authored HMM annotations'],
        real=['DNA/view/cache readers', 'teacher/student fits', 'own-teacher pair selection',
              'native exact reload', 'native sparse graph', 'graded density/marker selection', 'all-DNA accounting/export']))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['root', 'workflow-python', 'metabat']: p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args(); run(a.root, a.workflow_python, a.metabat)
