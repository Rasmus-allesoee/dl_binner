#!/usr/bin/env python3
"""Summarize retained E022 engineering exits/bytes; never launch training or cloud."""
from pathlib import Path
import hashlib,json,time
R=Path('artifacts/e022-marker-learning');E=Path('experiments/E022-marker-informed-learning')
def b(p):return dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def get(p):return json.loads(p.read_text())
attempts=[];disk=[]
for p in sorted(R.glob('*.resources.json')):
 x=get(p);stem=p.name.removesuffix('.resources.json');files={q.name:b(q)for q in R.glob(stem+'.*')if q.is_file()}
 v=get(R/(stem+'.exit.json'))if(R/(stem+'.exit.json')).exists()else x.get('resources',{})
 attempts.append(dict(attempt=stem,status=x['status'],error=x.get('error'),measurement=v,original_clock_elapsed_seconds=x['elapsed_original_seconds'],retained_files=files))
 disk.extend(x['samples'])
assert get(R/'final-owned-product-suite-1.exit.json')['exit_code']==0
assert get(R/'final-owned-adapters-1.exit.json')['exit_code']==0
clock=get(R/'engineering-clock.json');elapsed=time.time()-clock['start_epoch'];assert elapsed<5400
final=get(R/'tiny-production-v1/work/units/E009-relational/train/checkpoint.json')
value=dict(status='PASS_LOCAL_ENGINEERING_NATIVE_AND_QUALITY_UNADMITTED',branch='marker-informed-cross-contig-learning',source_parent='9d02bdc',
 scope='One locally implemented candidate and label-free pair availability. No community fit/score, old rescore, DNA acquisition, external tool, VM start, GCP operation or retention change.',
 actual=dict(product_suite=dict(tests=50,status='PASS',final_exit=b(R/'final-owned-product-suite-1.exit.json')),
 operational_tests=6,installed_wheel_and_sdist_rebuild='Final clean build-v3, independent hooks, matching rebuilt logical members',
 full_owned_product_prefix=dict(receipt=b(R/'product-owned-v3.json'),regular_copied_bytes=get(R/'product-owned-v3.json')['regular_bytes']),
 complete_runtime=get(R/'runtime-v3.json')['status'],
 learning='Real 20-epoch active/zero-weight/anchor and sequence-only fits on own tiny DNA; stopped gradients, exact model/teacher/predictor state for zero control; all parent/view axes, exact same-runtime reload',
 native_operations='Real HMM file reader, sparse graph, reliability/pair selection, CPM, cached E013 refiner, streamed complete DNA export, actual installed console outside checkout, actual production Snakemake helper and collector argv from /private/tmp',
 marker_detection='Ordinary product suite performed real tiny native gene/HMM search; E022 reliability fixtures use explicitly hand-authored cached annotations, not detector-accuracy evidence',
 final_tiny_online_fused=final['history'][-1]['geometry']['online']['fused'],
 collection=get(R/'tiny-production-v1/return/collection.json'),
 source_freeze=b(E/'source-lock.json'),pair_manifest=b(R/'cached-E009-pairs-v1/cache.json')),
 mocks_and_unavailable=dict(GLM='NumericExtractor synthetic DNA-specific vectors in tiny fixtures; no DNABERT execution. Actual E009 pair construction consumed native E021 embeddings/graph, not omitted GLM arrays.',
 native_linux='Fresh Linux source/runtime/full raw bank/readers/systemd/provider/full-candidate affordability remain gates; not executed here',
 full_GLM_reread='Raw vectors.npy remains natively retained; no independent Mac reread or fallback',
 science='No biological pair correctness, recovery improvement, optimality, unseen-genome, product-default or joint E021 KEEP claim'),
 failures=[dict(attempt='product-relational-v1-1',reason='Fixture reseal tried exclusive write_json on existing fixture metadata; fixed only fixture and preserved failure/source'),
 dict(attempt='tiny-DAG-v1-1',reason='Wrong exporter keyword emit_dna; corrected to include_dna. Restore/train/embed/group/refine passed; resumed only export/proof and preserved original outputs/logs'),
 dict(attempt='product-suite-v2-1',reason='49 tests passed, version assertion expected dev8; updated to declared dev9'),
 dict(attempt='final-adapters-v3-1',reason='Version then passed; ordinary owned-dependency assertion correctly rejected borrowed research prefix. Kept assertion unchanged, made explicit fresh byte-verified local owned copy, final complete suite passes')],
 limits=dict(threads=4,sampled_RSS_bytes=8000000000,original_clock_seconds=5400,elapsed_at_seal_seconds=elapsed,extra_GiB=4,free_reserve_GiB=6),
 resources=dict(peak_sampled_RSS_bytes=max(a['measurement'].get('peak_sampled_rss_bytes',0)for a in attempts),
 peak_sampled_owned_extra_bytes=max(x['extra_bytes']for x in disk),minimum_sampled_free_bytes=min(x['free_bytes']for x in disk),
 disk_scope='Owned regular bytes below R, explicit borrowed dependency links excluded. Initial attempts before TMPDIR correction did not count system temporary fixture dirs; final suites/adapters redirect them under R. No claim of an all-Mac historical meter.'),
 native_ready=False,quality_result=None,new_GCP_compute_cost_USD=0,live_cloud_checks_this_task=False,
 preserved='All accepted old data/truth/results/source freezes and failures. E021 OPERATIONS owner edits retained; original Mac allclose remains failed unchanged.',
 attempts=attempts)
(E/'local-observed.json').write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
print('SEALED_LOCAL_EVIDENCE',len(attempts),elapsed,value['resources'])
