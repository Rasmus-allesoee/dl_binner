#!/usr/bin/env python3
"""Run unchanged E031 learning once, then both frozen constructors on its outputs.

The existing worker owns all nine learning/E030 stages. Only the E023 consumer
and an explicit paired completion seal are added. Both receive the same native
vectors/graph and original measured-depth/marker inputs, with no truth interface.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import e031_control as original
from e024_control import fresh, seal, verify_seal
from e024_coverage import binding, write


def stage(path, name, unit, engineering=False):
    """Add an immutable E023 alternative without changing the fixed learning stages."""
    if name not in ['e023', 'paired']:
        return original.stage(path, name, unit, engineering=engineering)
    original.product_scope()
    plan = original.read_plan(path, engineering)
    if unit not in original.UNITS or plan['comparison'] != 'learning':
        raise ValueError('Only the three fixed learner modes may be paired')
    work = Path(plan['work']); root = work/unit; target = root/name
    expected = original.source_inputs(plan, unit)
    if (target/'done.json').is_file():
        record = verify_seal(target)
        if record.get('inputs') != expected:
            raise ValueError('Paired completed-stage source/input drift')
        return record
    verify_seal(work/'barrier')
    target = fresh(root, name)
    entry = plan['units'][unit]
    embeddings = root/'embed/embeddings.npz'; graph = root/'graph/result/graph.npz'
    before = {str(p): binding(p) for p in [embeddings, embeddings.with_suffix('.json'), graph, graph.with_suffix('.json')]}
    if name == 'e023':
        verify_seal(root/'graph')
        from dl_binner.bootstrap.bridge import run, query_view
        run(entry['features'], embeddings, graph, entry['marker_evidence'], entry['fasta'],
            ROOT/'experiments/E023-adaptive-density-bins/config.json',
            ROOT/'experiments/E023-adaptive-density-bins/source-lock.json', target/'science',
            engineering=engineering)
        result = target/'science/result'
        if engineering:
            queries = [dict(id=q, strata=[]) for q in json.loads((result/'selected-partition.json').read_text())['ids'][:4]]
        else:
            queries = json.loads((original.EXP/'query-axes.json').read_text())[unit]['student']['queries']
        query_view(result, entry['features'], graph, queries, target/'query-neighbors.json')
    else:
        verify_seal(root/'e023'); verify_seal(root/'audit'); verify_seal(root/'export')
        e023 = json.loads((root/'e023/science/bridge.json').read_text())
        e030 = json.loads((root/'construct/result/completed.json').read_text())
        if not (e023['status'] == 'PASS' and e023['truth_accessed'] is False
                and e023['audit']['status'] == 'PASS' and e030['status'] == 'SUCCESS'
                and e030['truth_accessed'] is False):
            raise ValueError('Both constructor/audit exits must pass')
        new_inputs = e023['inputs']
        for key, path in dict(features=Path(entry['features']), embeddings=embeddings,
                              graph=graph, evidence=Path(entry['marker_evidence'])).items():
            expected_bytes = binding(path)
            if (new_inputs[str(path.absolute())] != expected_bytes
                    or e030['input_sha256'][key] != expected_bytes['sha256']):
                raise ValueError('Constructors did not consume identical '+key)
        write(target/'proof.json', dict(status='PASS', same_new_vectors_and_graph=before,
            constructors=['source-bound E023', 'fixed E030'], one_fit_per_mode=True,
            native_reload_and_E030_audit=binding(root/'audit/proof.json'),
            E023_audit=binding(root/'e023/science/bridge.json'),
            no_teacher_refit=True, no_truth_selection=True))
    if {p: binding(p) for p in before} != before:
        raise ValueError('Constructor changed the shared native vector/graph bytes')
    return seal(target, dict(inputs=expected))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True); p.add_argument('--engineering', action='store_true')
    p.add_argument('--workflow', action='store_true'); p.add_argument('--dry-run', action='store_true')
    p.add_argument('--verify-inputs', action='store_true'); p.add_argument('--output', type=Path)
    p.add_argument('--stage', choices=original.LEARNING+['barrier', 'e023', 'paired'])
    p.add_argument('--unit', choices=original.UNITS)
    args = p.parse_args()
    if args.verify_inputs:
        original.product_scope()
        original.verify_inputs(original.read_plan(args.plan, args.engineering), args.output, args.engineering)
    elif args.workflow:
        original.workflow(args.plan, args.engineering, args.dry_run)
    elif args.stage:
        stage(args.plan, args.stage, args.unit, args.engineering)
    else:
        p.error('Choose one bounded paired workflow/stage')
