"""Complete only native-proven zero-ORF queries; never conceal missing results."""
import json
from pathlib import Path

from ..context.tokens import binding
from ..io import write_json


def complete(raw, index, lookup, orf_index, output):
    """Join exact MMseqs2 query keys and the reducer's retained-ORF query index.

    MMseqs2 18's aggregatetaxweights iterates orfs_h_swapped, so a zero-ORF parent
    has no result row. Require every indexed positive-ORF parent to have a raw
    row and forbid results for absent keys. Only the complement can receive an
    explicit zero-count no-ORF row. Bind all original files in a fresh receipt.
    """
    rows=json.loads(Path(index).read_text())['rows'];expected={r['query'] for r in rows if r['queried']}
    mapping={}; names=set()
    with Path(lookup).open()as stream:
        for line in stream:
            f=line.rstrip('\n').split('\t')
            if len(f)!=3 or not f[0].isdigit() or f[0]in mapping or f[1]in names or f[1]not in expected:
                raise ValueError('Malformed/foreign native query lookup')
            mapping[f[0]]=f[1];names.add(f[1])
    if names!=expected:raise ValueError('Native query lookup is incomplete')
    present=set()
    with Path(orf_index).open()as stream:
        for line in stream:
            f=line.rstrip('\n').split('\t')
            if (len(f)!=3 or f[0]not in mapping or f[0]in present
                    or any(not x.isdigit()for x in f[1:]) or int(f[2])<=1):
                raise ValueError('Malformed native ORF reducer index')
            present.add(f[0])
    emitted={}
    with Path(raw).open()as stream:
        for line in stream:
            f=line.rstrip('\n').split('\t')
            if len(f)!=8 or f[0]not in expected or f[0]in emitted:raise ValueError('Malformed native aggregated rows')
            emitted[f[0]]=line.rstrip('\n')
    positive={mapping[k]for k in present}
    if set(emitted)!=positive:raise ValueError('Missing/extra classifier result for a native retained-ORF query')
    zero=sorted(expected-positive);output=Path(output)
    with output.open('x')as stream:
        for row in rows:
            q=row['query']
            if not row['queried']:continue
            stream.write(emitted[q]+'\n'if q in emitted else q+'\t0\tno rank\tunclassified\t0\t0\t0\t0\n')
    proof=dict(kind='native_zero_ORF_completion',version=1,raw=binding(raw),query_index=binding(index),
        query_lookup=binding(lookup),orf_reducer_index=binding(orf_index),normalized=binding(output),
        raw_queries=len(emitted),expected_queries=len(expected),zero_ORF_queries=zero,
        basis='MMseqs2 18 aggregatetaxweights iterates orfs_h_swapped; absence is admitted only from that exact native index')
    write_json(output.with_suffix('.completion.json'),proof);return proof
