"""Separate E009 evaluator for complete frozen partitions; no feature/training access.

Native AMBER scores the explicitly restricted contig view. Conservative R95 uses
all-bin DNA and full supplied-reference denominators. Operational failures must
not be passed here as empty partitions. Truth/target taxonomy is frozen separately
before scoring; this module does not select/tune any tool or scientific settings.
"""
import argparse
import csv
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).absolute().parent))

from e009_common import binding, write_json
from e009_truth import recovery


def amber_view(contigs, assignments, source, output):
    """Use the pinned AMBER API on only attributable contigs, reporting its denominator."""
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    known={qid:item for qid,item in contigs.items() if item['AMBER_label'] is not None}
    with (output/'truth.tsv').open('x') as out:
        out.write('@Version:0.9.0\n@SampleID:E009\n@@SEQUENCEID\tBINID\t_LENGTH\n')
        for qid,item in known.items():out.write(f"{qid}\t{item['AMBER_label']}\t{item['length']}\n")
    predicted={qid:label for qid,label in assignments.items() if qid in known and label is not None}
    with (output/'predictions.tsv').open('x') as out:
        out.write('@Version:0.9.0\n@SampleID:E009\n@@SEQUENCEID\tBINID\n')
        for qid,label in predicted.items():out.write(f'{qid}\t{label}\n')
    result={'scorable_contigs':len(known),'scorable_bp':sum(x['length'] for x in known.values()),
            'unscored_contigs':len(contigs)-len(known),'predicted_contigs':len(predicted),
            'claim_limit':'restricted alignment-supported contig population; not whole-reference recovery'}
    if known and predicted:
        sys.path.insert(0,str(source))
        from cami_amber.binning_classes import GenomeQuery,Options
        from cami_amber.utils.load_data import read_metadata
        options=Options(filter_tail_percentage=0,skip_heatmap=True)
        gold=GenomeQuery('gold','E009',options,read_metadata((str(output/'truth.tsv'),'gold'))[0],is_gs=True)
        query=GenomeQuery('partition','E009',options,read_metadata((str(output/'predictions.tsv'),'partition'))[0])
        query.gold_standard=gold;query.compute_metrics()
        expected=sum(known[qid]['length'] for qid in predicted)
        if int(query.precision_df['total_length'].sum())!=expected:raise ValueError('Native AMBER assigned bp differ')
        query.precision_df.to_csv(output/'per-bin.tsv',sep='\t',index_label='BINID')
        query.recall_df.to_csv(output/'per-genome.tsv',sep='\t',index_label='BINID')
        result['native_api_executed']=True
    else:result.update(native_api_executed=False,reason='empty valid restricted truth/prediction population')
    write_json(output/'view.json',result);return result


def evaluate(truth_path, partition_path, targets_path, amber_source, output):
    """Evaluate one complete immutable partition with declared source taxonomy targets."""
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    truth=json.loads(Path(truth_path).read_text());targets=json.loads(Path(targets_path).read_text())
    with Path(partition_path).open() as stream:rows=list(csv.DictReader(stream,delimiter='\t'))
    if [row['contig_id'] for row in rows]!=truth['ordered_contig_ids']:raise ValueError('Partition/truth axis mismatch')
    assignments={}
    for row in rows:
        if row['status'] not in ('assigned','unassigned','excluded'):raise ValueError('Unknown assignment outcome')
        if bool(row['bin_id'])!=(row['status']=='assigned'):raise ValueError('Assignment state/bin mismatch')
        if int(row['length'])!=truth['contigs'][row['contig_id']]['length']:raise ValueError('Partition/truth length mismatch')
        if bool(row['exclusion_reason'])!=(row['status']=='excluded'):raise ValueError('Assignment exclusion reason mismatch')
        assignments[row['contig_id']]=row['bin_id'] or None
    metric=recovery(truth['contigs'],assignments,truth['reference_axis'],targets['genome_lengths'],targets['targets'])
    amber=amber_view(truth['contigs'],assignments,amber_source,output/'AMBER')
    value={'truth':binding(truth_path),'partition':binding(partition_path),'targets':binding(targets_path),
           'conservative_reference_recovery':metric,'AMBER':amber,'unassigned_excluded_retained':True,
           'claim_limit':'alignment-supported source-reference recovery; development assembly; not formal HQ MAG or unseen-genome generalization'}
    write_json(output/'evaluation.json',value);return value


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['truth','partition','targets','amber-source','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();evaluate(a.truth,a.partition,a.targets,a.amber_source,a.output)
