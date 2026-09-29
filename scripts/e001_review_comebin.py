"""Audit the completed seed-11 COMEBin resume from compact retained evidence.

No native work is run. Binary arrays absent from the return remain receipt-only;
this audit deliberately does not claim independent candidate/embedding inspection.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import re
import tarfile
import tempfile

from e001_features import EXP, read, sha, write
from e001lib.records import require, partition, truth_table
from e001lib.metrics import score
from e001_review_pilot import check_amber


def candidate_names():
    """Return the pinned native 5 x 8 x 3 Leiden grid, max_edges=100."""
    return {f'Leiden_bandwidth_{b}_res_maxedges100respara_{r}_partgraph_ratio_{p}.labels.npy'
            for b in (.05, .1, .15, .2, .3) for r in (1,5,10,30,50,70,90,110) for p in (50,100,80)}


def native_schedule(log):
    """Check contiguous native epochs and the first legal three-epoch stop."""
    rows=re.findall(r'NN training: epoch=(\d+)/200, batches=(\d+), loss=[^,]+, top1=([\d.]+), elapsed=([\d.]+)s',log)
    require(rows and [int(r[0]) for r in rows]==list(range(1,len(rows)+1)), 'Noncontiguous epochs')
    require(all(int(r[1])==22 for r in rows), 'Changed full-batch count')
    streak=0; stop=None
    for epoch,_,top,_ in rows:
        streak=streak+1 if int(epoch)>=11 and float(top)>99 else 0
        if streak>=3:
            stop=int(epoch); break
    require(len(rows)==(stop or 200), 'Native early-stop mismatch')
    require('published complete binary embedding bundle; contigs=22594' in log and 'Finish training.' in log,
            'Missing final embedding publication')
    return dict(epochs=len(rows),maximum=200,native_early_stop=stop is not None,
                mean_epoch_seconds=sum(float(r[3]) for r in rows)/len(rows))


def marker_selection(path, expected):
    """Validate all native marker scores and deterministic lexicographic tie-breaking."""
    with path.open() as f: rows=list(csv.DictReader(f,delimiter='\t'))
    require(len(rows)==120 and {r['Binning_method'] for r in rows}==candidate_names(), 'Incomplete marker grid')
    for r in rows:
        require(all(int(r[k])>=0 for k in r if k!='Binning_method'), 'Negative marker count')
        require(sum(int(r[k]) for k in ('num_5010','num_7010','num_9010','num_505','num_705','num_905'))==int(r['sum']), 'Marker sum mismatch')
        require(sum(int(r[k]) for k in ('num_505','num_705','num_905'))==int(r['sum_cont5']), 'Marker purity sum mismatch')
    rows.sort(key=lambda r:r['Binning_method'])
    winner=max(rows,key=lambda r:(int(r['sum']),int(r['sum_cont5'])))
    require(winner['Binning_method']==expected,'Marker winner mismatch')
    return dict(candidate_rows=120,winner=expected,score=int(winner['sum']),pure_score=int(winner['sum_cont5']),
                scope='Score-table arithmetic and native selection rule independently checked; recomputing markers from all labels needs omitted binary candidates')


def audit(root, population_dir):
    """Validate live completed conditions, excluding explicitly preserved failures."""
    frozen=read(EXP/'frozen-inputs.json')
    require(sha(EXP/'config.json')==frozen['config_sha256'],'Changed scientific configuration')
    for n in ('population.json','truth.tsv'):
        require(sha(population_dir/n)==frozen['outputs'][n], 'Changed frozen '+n)
    pop=read(population_dir/'population.json'); lengths=pop['lengths']; origins=truth_table(population_dir/'truth.tsv',lengths)
    cfg=read(root/'runtime.json'); status=read(root/'status.json'); paired=read(root/'paired-summary.json')
    require(status['exit_code']==0 and status['reused_condition']=='COMEBin/C0', 'Incomplete resume')
    require(not (root/'failure.json').exists(),'Active failure receipt')
    require((cfg['vcpus'],cfg['ram_gb'],cfg['threads'],cfg['comebin_threads'],cfg['comebin_loader_workers'],cfg['leiden_workers'])==(8,24,8,7,1,8),'Changed CPU contract')
    require(cfg['source_commit']=='9ceeb087441d06ff69b6a639233781ddad674d58','Unreviewed resume source')
    require(math.isclose(status['allocated_core_hours'],status['elapsed_seconds']*8/3600),'Cost mismatch')
    verified=read(root/'verified.json')
    require(verified['feature_record_sha256']==sha(EXP/'features-observed.json') and verified['frozen_record_sha256']==sha(EXP/'frozen-inputs.json'),'Provenance mismatch')
    history=root/'recovery/comebin-ct-resume-20260928T182949Z-fe7ig32w'
    from e001_pilot import validate_resume_dag
    validate_resume_dag((history/'dag.stdout').read_text())
    require(read(history/'workflow-unlock.command.json')['returncode']==0,'Unlock failed')
    results={}; hashes={}; axes=[]
    for condition in ('C0','CT'):
        d=root/'comebin'/condition; fit=read(d/'fit.json'); retained=read(d/'retained.json'); ev=read(d/'evaluation.json')
        require(not (d/'failure.json').exists(),'Active condition failure')
        for name, receipt in retained.items():
            require(not Path(name).is_absolute() and '..' not in Path(name).parts,'Unsafe retained member')
            p=d/name
            if p.is_file():
                require(p.stat().st_size==receipt['bytes'] and sha(p)==receipt['sha256'],'Retained member mismatch: '+name)
                hashes[str(p.relative_to(root))]=receipt['sha256']
        for p in d.glob('*.command.json'):
            r=read(p); require(r['returncode']==0 and 'failure' not in r,'Failed native command')
        require(fit['source']['commit']=='1b476a41fac893294c70212a869573a732560ce5','Native source changed')
        require(fit['feature_record_sha256']==verified['feature_record_sha256'],'Feature identity changed')
        require(fit['seed']==ev['seed']==11 and fit['condition']==ev['condition']==condition,'Seed/condition mismatch')
        require(ev==read(d/'complete.json')==paired['results']['comebin'][condition],'Completion mismatch')
        cmd=read(d/'native-command.json')
        for flag,value in (('--epochs','200'),('--batch_size','1024'),('--n_views','6'),('--num_threads','7'),('--seed','11'),('--device','cpu')):
            require(cmd[cmd.index(flag)+1]==value,'Changed native schedule '+flag)
        require(all(x in cmd for x in ('--earlystop','--addvars','--vars_sqrt')),'Changed scientific options')
        require('PyTorch intra-op threads=7, DataLoader workers=1' in (d/'native/comebin.log').read_text(),'Wrong effective thread report')
        require('Automatically selected temperature=0.07 from complete-assembly N50=2870581.' in (d/'native/comebin.log').read_text(),'Changed native temperature')
        schedule=native_schedule((d/'native/comebin.log').read_text())
        ids=(d/'native/embedding_ids.txt').read_text().splitlines(); axes.append(ids)
        require(len(ids)==len(set(ids))==len(lengths) and set(ids)==set(lengths),'Embedding axis mismatch')
        manifest=read(d/'native/embedding_manifest.json')
        require(manifest['complete'] and manifest['embeddings']['shape']==[len(ids),128] and manifest['coverage_embeddings']['shape']==[len(ids),128],'Embedding manifest mismatch')
        require(fit['candidate_count']==120 and fit['rows']==len(ids) and set(fit['candidate_sha256'])==candidate_names(),'Candidate grid mismatch')
        for n,h in fit['candidate_sha256'].items():
            require(retained['native/cluster_res/'+n]['sha256']==h,'Candidate receipt mismatch')
        selection=marker_selection(d/'native/cluster_res/estimate_res.txt',fit['winning_candidate'])
        assignments=partition(d/'predictions.tsv',lengths)
        require(set(assignments)==set(lengths),'Incomplete selected partition')
        require(sha(d/'predictions.tsv')==fit['assignment_sha256']==ev['assignment_sha256'],'Assignment identity mismatch')
        recomputed=score(pop,assignments)
        require(recomputed==read(d/'r95.json') and recomputed['r95']==ev['r95'],'R95 mismatch')
        with (root/'benchmarks'/f'comebin-{condition}.tsv').open() as f: bench=next(csv.DictReader(f,delimiter='\t'))
        require(bench['threads']=='8','Wrong scheduler threads')
        results[condition]=dict(r95=recomputed['r95'],r95_base_weighted=recomputed['r95_base_weighted'],
            assigned_contigs=len(assignments),assigned_bp=recomputed['assigned_bp'],inclusive_recovered_counts=recomputed['inclusive_recovered_counts'],
            schedule=schedule,selection=selection,amber=check_amber(d,assignments,lengths,origins),
            retained_artifacts=len(retained),retained_bytes=sum(v['bytes'] for v in retained.values()),
            rule_seconds=float(bench['s']),rule_core_hours=float(bench['s'])*8/3600,
            sampled_cpu_seconds=float(bench['cpu_time']),average_rule_cpus=float(bench['cpu_time'])/float(bench['s']),
            fit_seconds=read(d/'fit.command.json')['elapsed_seconds'],cluster_seconds=read(d/'cluster.command.json')['elapsed_seconds'],
            peak_process_tree_pss_mb=max(read(d/n)['peak_tree_memory_mb'] for n in ('fit.command.json','cluster.command.json')),
            embedding=dict(rows=len(ids),dimensions=128,ids_sha256=sha(d/'native/embedding_ids.txt'),
                           scope='Native reader validation and hash receipts accepted; binary content absent locally'),
            source_commit=ev['source_commit'],retained_receipt_sha256=sha(d/'retained.json'))
    require(read(root/'comebin/C0/checkm-payloads.json')==read(root/'comebin/CT/checkm-payloads.json'),'Paired marker payloads differ')
    require((root/'comebin/C0/inventory.stdout').read_bytes()==(root/'comebin/CT/inventory.stdout').read_bytes(),'Paired package inventory differs')
    require(axes[0]==axes[1],'Paired embedding axes differ')
    require(results['C0']['retained_receipt_sha256']==status['c0_validation']['retained_receipt_sha256'],'Reused C0 receipt differs')
    delta=results['CT']['r95']-results['C0']['r95']
    require(delta==paired['delta_r95']['comebin'],'Paired delta differs')
    return dict(status='accepted native execution and primary evaluation; binary diagnostic audit pending',reviewed='2026-09-29',
                directory=cfg['stage'],results=results,delta_ct_minus_c0=delta,resume_resources=status,
                successful_condition_core_hours=sum(r['rule_core_hours'] for r in results.values()),
                retained_condition_bytes=sum(r['retained_bytes'] for r in results.values()),
                scope='Single seed, fixed GI development derivative; all 120 candidates per condition validated by native execution and receipts, not yet independently read locally; historical failures remain preserved',
                verified_return_members=hashes)


def review(archive,checksum,terminal,population_dir):
    """Verify the archive, safely unpack it and bind the audit to its terminal log."""
    require(checksum.read_text().split()==[sha(archive),archive.name],'Archive checksum mismatch')
    with tempfile.TemporaryDirectory() as tmp,tarfile.open(archive) as tar:
        members=tar.getmembers()
        require(len({m.name for m in members})==len(members),'Duplicate archive members')
        require(all((m.isfile() or m.isdir()) and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in members),'Unsafe archive member')
        tar.extractall(tmp,filter='data'); roots=list(Path(tmp).iterdir()); require(len(roots)==1,'Multiple roots')
        result=audit(roots[0],population_dir)
    require('PASS: workflow' in terminal.read_text() and archive.name in terminal.read_text(),'Terminal mismatch')
    result.update(archive=archive.name,archive_sha256=sha(archive),terminal=terminal.name,terminal_sha256=sha(terminal))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for n in ('archive','checksum','terminal','population_dir','output'): parser.add_argument(n,type=Path)
    a=parser.parse_args(); result=review(a.archive,a.checksum,a.terminal,a.population_dir); write(a.output,result)
    print(json.dumps({k:result[k] for k in ('status','delta_ct_minus_c0','successful_condition_core_hours')}))
