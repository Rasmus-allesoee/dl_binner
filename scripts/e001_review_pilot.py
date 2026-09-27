"""Audit a compact seed-11 MetaBAT2/VAMB return without repeating native fits.

Recompute fixed-population R95 and verify AMBER tables against full native
partitions. Large embeddings/models are checked through hash-bound native
validation receipts; they are not included in the compact return.
"""
import argparse
from collections import Counter
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


def check_amber(directory, assignments, lengths, origins):
    """Independently validate AMBER's unfiltered single-origin bin/genome tables.

    This frozen truth has one origin per contig. Reject changed truth rather than
    silently approximating AMBER's multi-origin matching. Historical TSVs omitted
    the BINID index, so validate complete bin-row multisets and genome identities.
    """
    require(all(len(v)==1 for v in origins.values()), 'Multi-origin AMBER audit needs its native matcher')
    total=Counter(); overlap=Counter(); counts=Counter(); truth=Counter()
    for seq, owners in origins.items(): truth[owners[0]]+=lengths[seq]
    for seq, b in assignments.items():
        total[b]+=lengths[seq]; overlap[b,origins[seq][0]]+=lengths[seq]; counts[b]+=1
    expected=Counter()
    for b in total:
        best=max(bp for (bin_id,g),bp in overlap.items() if bin_id==b)
        # Confirm the returned winning origin below; ties are allowed only if maximal.
        expected[total[b],counts[b],best]+=1
    with (directory/'amber-per-bin.tsv').open() as f: bins=list(csv.DictReader(f,delimiter='\t'))
    observed=Counter((int(r['total_length']),int(r['total_seq_counts']),int(r['tp_length'])) for r in bins)
    require(observed==expected,'AMBER bin multiset mismatch')
    possible=Counter((total[b],counts[b],g,bp) for (b,g),bp in overlap.items()
                     if bp==max(v for (bb,gg),v in overlap.items() if bb==b))
    for r in bins:
        key=int(r['total_length']),int(r['total_seq_counts']),r['genome_id'],int(r['tp_length'])
        require(possible[key]>0,'AMBER dominant origin mismatch'); possible[key]-=1
        require(int(r['length_gs'])==truth[r['genome_id']],'AMBER truth denominator mismatch')
        require(math.isclose(float(r['precision_bp']),int(r['tp_length'])/int(r['total_length']),abs_tol=1e-12),'AMBER purity mismatch')
        require(math.isclose(float(r['recall_bp']),int(r['tp_length'])/truth[r['genome_id']],abs_tol=1e-12),'AMBER bin recall mismatch')
    with (directory/'amber-per-genome.tsv').open() as f: genomes=list(csv.DictReader(f,delimiter='\t'))
    require(len(genomes)==len(truth) and {r['genome_id'] for r in genomes}==set(truth),'AMBER genome axis mismatch')
    for r in genomes:
        g=r['genome_id']; best=max((v for (b,gg),v in overlap.items() if gg==g),default=0)
        require(int(float(r['genome_length']))==best and int(r['length_gs'])==truth[g],'AMBER genome recovery mismatch')
        require(math.isclose(float(r['recall_bp']),best/truth[g],abs_tol=1e-12),'AMBER genome recall mismatch')
    return dict(bins=len(bins),genomes=len(genomes),assigned_bp=sum(total.values()),
                weighted_purity=sum(int(r['tp_length']) for r in bins)/sum(total.values()),
                mean_genome_recall=sum(float(r['recall_bp']) for r in genomes)/len(genomes),
                bin_ids_in_return='BINID' in bins[0])


def audit_directory(root, population_dir):
    """Validate execution, retained members, schedules, partitions and evaluation."""
    frozen=read(EXP/'frozen-inputs.json')
    require(sha(EXP/'config.json')==frozen['config_sha256'],'Scientific configuration changed')
    source_pins={r['name']:r['commit'] for r in read(EXP.parents[1]/'docs/evidence/2026-09-17-tool-snapshots.json')['tools']}
    for name in ('population.json','truth.tsv'):
        require(sha(population_dir/name)==frozen['outputs'][name],'Changed frozen '+name)
    population=read(population_dir/'population.json'); lengths=population['lengths']
    origins=truth_table(population_dir/'truth.tsv',lengths)
    status=read(root/'status.json'); cfg=read(root/'runtime.json'); paired=read(root/'paired-summary.json')
    require(status['exit_code']==0 and not list(root.rglob('failure.json')),'Incomplete pilot')
    require(cfg['vcpus']==4 and cfg['ram_gb']==12 and cfg['threads']==4,'Unexpected allocation')
    require(cfg['source_commit']=='ac7159f8d1c7c4e94db62f301c7714d101be9214','Unreviewed execution source')
    require(math.isclose(status['allocated_core_hours'],status['elapsed_seconds']*4/3600),'Wrong charged cost')
    verified=read(root/'verified.json')
    require(verified['feature_record_sha256']==sha(EXP/'features-observed.json'),'Feature provenance mismatch')
    require(verified['frozen_record_sha256']==sha(EXP/'frozen-inputs.json'),'Frozen provenance mismatch')
    ipc=read(root/'vamb-ipc-smoke.json'); require(ipc['status']=='passed' and ipc['rows']==32,'IPC smoke failed')
    results={}; member_hashes={}
    for tool in ('metabat','vamb'):
        results[tool]={}
        for condition in ('C0','CT'):
            d=root/tool/condition; retained=read(d/'retained.json')
            for name,receipt in retained.items():
                path=d/name
                if path.is_file():
                    require(path.stat().st_size==receipt['bytes'] and sha(path)==receipt['sha256'],'Retained member mismatch: '+str(path))
                    member_hashes[str(path.relative_to(root))]=receipt['sha256']
            for command in d.glob('*.command.json'):
                r=read(command); require(r['returncode']==0 and 'failure' not in r,'Failed native stage')
            evaluation=read(d/'evaluation.json'); fit=read(d/'fit.json')
            require(fit['source']['commit']==source_pins[tool],'Native source identity mismatch')
            require(fit['feature_record_sha256']==verified['feature_record_sha256'],'Fit feature identity mismatch')
            require(evaluation==read(d/'complete.json')==paired['results'][tool][condition],'Receipt mismatch')
            require(fit['seed']==11 and fit['condition']==condition and evaluation['seed']==11,'Seed/condition mismatch')
            native=d/'native'/('bins.MemberMatrix.txt' if tool=='metabat' else 'vae_clusters_unsplit.tsv')
            assignments=partition(native,lengths,tool)
            require(assignments==partition(d/'predictions.tsv',lengths),'Export differs from full native partition')
            require(len(assignments)==fit['assigned_contigs'],'Assigned count mismatch')
            require(sha(d/'predictions.tsv')==fit['assignment_sha256']==evaluation['assignment_sha256'],'Assignment checksum mismatch')
            recomputed=score(population,assignments)
            require(recomputed==read(d/'r95.json'),'Recomputed R95 differs')
            require(recomputed['r95']==evaluation['r95'] and recomputed['assigned_bp']==evaluation['assigned_bp'],'Evaluation receipt differs')
            command=read(d/'native-command.json')
            embedding=None; native_support=None
            if tool=='vamb':
                log=(d/'native/log.txt').read_text()
                epochs=list(map(int,re.findall(r'Epoch:\s*(\d+)',log)))
                require(epochs==list(range(1,301)),'Incomplete or repeated VAMB epochs')
                for token in ('Starting batch size: 256','Batchsteps: 25, 75, 150, 225','N latent: 32','N samples: 10','CUDA: False'):
                    require(token in log,'Changed native schedule: '+token)
                require(command[command.index('-p')+1]=='3' and command[command.index('-e')+1]=='300','Changed VAMB arguments')
                ids=read(d/'native/embedding-ids.json')
                require(len(ids)==len(set(ids))==len(lengths) and set(ids)==set(lengths),'Embedding axis mismatch')
                embedding={n:retained['native/'+n] for n in ('latent.npz','model.pt','embedding-ids.json')}
                require(all(r['bytes']>0 for r in embedding.values()),'Empty retained embedding/model')
                embedding.update(rows=len(ids),dimensions=32,scope='Native finite/row validation and retained hash receipts; binary arrays/models remain on UCloud')
            else:
                with native.open() as f: rows=list(csv.reader(f,delimiter='\t'))[1:]
                emitted={r[0] for r in rows}
                require(len(emitted)==len(rows) and emitted<=set(lengths),'Invalid MetaBAT matrix axis')
                native_support=dict(matrix_rows=len(rows),explicit_zero_rows=sum(r[1]=='0' for r in rows),
                    filtered_or_omitted_contigs=len(lengths)-len(emitted),
                    filtered_or_omitted_bp=sum(lengths[n] for n in set(lengths)-emitted),
                    scope='Every missing or cluster-zero contig remains unassigned in the frozen denominator')
                require(command[command.index('-t')+1]=='4','Wrong MetaBAT thread flag')
                require('Executing with 4 threads' in (d/'fit.stdout').read_text(),'Wrong effective MetaBAT threads')
            with (root/'benchmarks'/f'{tool}-{condition}.tsv').open() as f: benchmark=next(csv.DictReader(f,delimiter='\t'))
            require(benchmark['threads']=='4','Wrong rule threads')
            results[tool][condition]=dict(r95=recomputed['r95'],r95_base_weighted=recomputed['r95_base_weighted'],
                assigned_contigs=len(assignments),unassigned_contigs=len(lengths)-len(assignments),
                assigned_bp=recomputed['assigned_bp'],unassigned_bp=recomputed['unassigned_bp'],
                inclusive_recovered_counts=recomputed['inclusive_recovered_counts'],
                assignment_sha256=sha(d/'predictions.tsv'),amber=check_amber(d,assignments,lengths,origins),
                embedding=embedding,native_support=native_support,source=fit['source'],rule_wall_seconds=float(benchmark['s']),
                rule_cpu_seconds=float(benchmark['cpu_time']),average_rule_cpus=float(benchmark['cpu_time'])/float(benchmark['s']),
                fit=read(d/'fit.command.json'))
    require(read(root/'vamb/C0/native/embedding-ids.json')==read(root/'vamb/CT/native/embedding-ids.json'),'Paired embedding axes differ')
    delta={t:results[t]['CT']['r95']-results[t]['C0']['r95'] for t in results}
    require(delta==paired['delta_r95'],'Paired delta mismatch')
    return dict(status='accepted',directory=cfg['stage'],source_commit=cfg['source_commit'],
                resources=status,results=results,delta_ct_minus_c0=delta,
                scope='Seed-11 development pair only; COMEBin and seeds 23/47 remain pending',
                verified_return_members=member_hashes)


def review(archive, checksum, terminal, population_dir):
    """Verify the return digest, safely unpack regular members and audit evidence."""
    require(checksum.read_text().split()==[sha(archive),archive.name],'Archive checksum mismatch')
    with tempfile.TemporaryDirectory() as tmp, tarfile.open(archive) as tar:
        members=tar.getmembers(); names=[m.name for m in members]
        require(len(names)==len(set(names)),'Duplicate archive paths')
        require(all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names),'Unsafe archive path')
        require(all(m.isfile() or m.isdir() for m in members),'Unexpected archive link')
        tar.extractall(tmp,filter='data')
        roots=list(Path(tmp).iterdir()); require(len(roots)==1,'Multiple attempt roots')
        result=audit_directory(roots[0],population_dir)
    log=terminal.read_text()
    require('PASS: workflow' in log and archive.name in log,'Terminal does not confirm this completed attempt')
    result.update(archive=archive.name,archive_sha256=sha(archive),terminal=terminal.name,terminal_sha256=sha(terminal))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('archive','checksum','terminal','population_dir','output'): p.add_argument(n,type=Path)
    a=p.parse_args(); result=review(a.archive,a.checksum,a.terminal,a.population_dir)
    write(a.output,result); print(json.dumps(dict(status=result['status'],delta=result['delta_ct_minus_c0'],cost=result['resources']['allocated_core_hours'])))
