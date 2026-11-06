"""Strict full-axis MMseqs2 parent annotations and source-blind query emission.

The agreement and weighted-vote fractions below are evidence proxies. They are
not probabilities of correct taxonomy or independent common-genome evidence.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from ..io import id_digest, save_arrays
from ..context.tokens import binding
from .tree import Tree


def query_fasta(fasta, features, output):
    """Write only actual assembly DNA under new opaque IDs with a complete index.

    Check sequence ID/length/order against admitted features; no headers beyond
    the matching contig ID leave this boundary. Zero-bp records remain indexed
    but are not invented classifier queries. No origin/source metadata is read.
    """
    from ..multiview.views import load
    from ..io import DNA, write_json
    data, _ = load(features); out = Path(output); out.mkdir(parents=True, exist_ok=False)
    rows = []; expected = iter(zip(data['ids'], data['lengths']))
    def records():
        """Stream assembly records, including explicit original zero-bp records."""
        name = None; chunks = []; seen = set()
        with Path(fasta).open() as source:
            for line in source:
                line = line.strip()
                if not line: continue
                if line.startswith('>'):
                    if name is not None: yield name, ''.join(chunks).upper()
                    fields = line[1:].split()
                    if not fields or fields[0] in seen: raise ValueError('Missing/duplicate query FASTA ID')
                    name = fields[0]; seen.add(name); chunks = []
                else:
                    if name is None: raise ValueError('Query DNA before header')
                    chunks.append(line)
            if name is not None: yield name, ''.join(chunks).upper()
    with (out/'queries.fna').open('x') as stream:
        for i, (name, sequence) in enumerate(records()):
            if set(sequence)-DNA: raise ValueError('Invalid classifier query DNA')
            wanted = next(expected, None)
            if wanted is None or name != str(wanted[0]) or len(sequence) != int(wanted[1]):
                raise ValueError('Classifier FASTA differs from admitted opaque full axes')
            q = 'q%09d' % i
            rows.append(dict(query=q, id=name, length=len(sequence), sha256=hashlib.sha256(sequence.encode()).hexdigest(), queried=bool(sequence)))
            if sequence: stream.write('>'+q+'\n'+sequence+'\n')
        if next(expected, None) is not None: raise ValueError('Classifier FASTA axis is incomplete')
    record = dict(kind='taxonomy_query_index', version=1, ids_sha256=id_digest(data['ids'].tolist()),
                  features=binding(features), fasta=binding(fasta), query=binding(out/'queries.fna'), rows=rows)
    write_json(out/'index.json', record); return record


def parse(tsv, query_index, tree):
    """Read eight standard aggregated-taxonomy TSV columns without guessing.

    Columns: opaque query, taxid, rank, name, total ORFs, assigned ORFs, agreeing
    ORFs, weighted agreement. Missing/duplicate/foreign queries, impossible counts,
    nonfinite values, tree disagreement and unexpected extra fields are refused.
    A ninth lineage column is deliberately not requested by the pinned command.
    """
    index = json.loads(Path(query_index).read_text())
    if index.get('kind') != 'taxonomy_query_index' or index.get('version') != 1:
        raise ValueError('Unrecognized taxonomy query index')
    rows = index['rows']; ids = [r['id'] for r in rows]
    if len(set(ids)) != len(ids) or index['ids_sha256'] != id_digest(ids):
        raise ValueError('Malformed query full axis')
    expected = {r['query']: i for i, r in enumerate(rows) if r['queried']}
    if len(expected) != sum(bool(r['queried']) for r in rows): raise ValueError('Duplicate classifier query')
    seen = set(); n = len(rows); labels = np.zeros((n, 7), np.int32)
    counts = np.zeros((n, 3), np.int64); weighted = np.zeros(n, np.float32)
    confidence = np.zeros(n, np.float32); states = np.full(n, 'zero_length', dtype='<U24')
    with Path(tsv).open() as stream:
        for line in stream:
            f = line.rstrip('\n').split('\t')
            if len(f) != 8 or f[0] not in expected or f[0] in seen:
                raise ValueError('Malformed, missing-schema, duplicate or foreign taxonomy query')
            seen.add(f[0]); i = expected[f[0]]
            try: node, total, assigned, agree = map(int, [f[1], f[4], f[5], f[6]]); support = float(f[7])
            except ValueError as e: raise ValueError('Non-numeric taxonomy counters') from e
            if not 0 <= agree <= assigned <= total or not np.isfinite(support) or not 0 <= support <= 1:
                raise ValueError('Impossible taxonomy counters/support')
            path = tree.path(node)
            # MMseqs2 emits either 'unclassified' or 'no rank' for taxid zero.
            if node and (f[2] != tree.nodes[node]['rank'] or f[3] != tree.nodes[node]['name']):
                raise ValueError('Taxonomy rank/name differs from pinned tree')
            if not node and (assigned or agree or support):
                # Classified ORFs may disagree at root, but taxid=0 cannot claim
                # an agreeing nonzero lineage. Keep that case explicit/refused.
                if agree or support: raise ValueError('Unclassified row claims agreeing lineage')
            counts[i] = total, assigned, agree; weighted[i] = support
            if not node or not path.any(): states[i] = 'no_hit' if assigned == 0 else 'root_conflict'; continue
            labels[i] = path
            # Harmonic evidence cannot be manufactured from zero assignments.
            fraction = assigned/total if total else 0
            consensus = agree/assigned if assigned else 0
            proxy = min(float(np.float32(support)), consensus)*fraction
            if assigned < 2 or agree < 2: states[i] = 'insufficient_support'
            elif consensus < .5 or support < .5: states[i] = 'conflict'
            else:
                confidence[i] = proxy
                states[i] = 'classified' if path[-1] else 'partial'
    if seen != set(expected): raise ValueError('Missing classifier rows; no-hit is an explicit native record')
    return dict(ids=np.asarray(ids), paths=labels, counts=counts, support=weighted,
                confidence=confidence, states=states), index


def prepare(tsv, query_index, tree_path, features, provenance, output, completion):
    """Seal independent classifier evidence, binding raw bytes and query DNA.

    `provenance` must identify actual classifier/database/query bytes and whether
    this is a tiny synthetic reference. External acquisition has its own admission.
    """
    from ..io import write_json
    from ..multiview.views import load
    tree = Tree.load(tree_path); a, index = parse(tsv, query_index, tree)
    data, meta = load(features)
    if index['features'] != binding(features) or not np.array_equal(a['ids'], data['ids']):
        raise ValueError('Taxonomy feature/full-axis binding differs')
    p = json.loads(Path(provenance).read_text())
    required = {'classifier_version', 'binary', 'database', 'query_sha256', 'synthetic_reference', 'truth_accessed','zero_ORF_completion'}
    from .classifier import VERSION
    if set(p) != required or p['classifier_version'] != VERSION or p['query_sha256'] != index['query']['sha256'] or p['truth_accessed'] is not False:
        raise ValueError('Incomplete independent classifier provenance')
    if type(p['synthetic_reference']) is not bool or not p['binary'] or not p['database']:
        raise ValueError('Missing classifier/database byte identity')
    if binding(Path(query_index).parent/'queries.fna') != index['query']:
        raise ValueError('Actual classifier query DNA changed')
    proof=json.loads(Path(completion).read_text())
    if (p['zero_ORF_completion']!=binding(completion) or proof.get('kind')!='native_zero_ORF_completion'
            or proof['normalized']!=binding(tsv) or proof['query_index']!=binding(query_index)):
        raise ValueError('Missing exact native zero-ORF completion proof')
    no_orf=set(proof['zero_ORF_queries'])
    for i,row in enumerate(index['rows']):
        if row['query']in no_orf:
            if a['paths'][i].any() or a['counts'][i].any() or a['support'][i]!=0:raise ValueError('Zero-ORF row claims support')
            a['states'][i]='no_retained_ORF'
    out = Path(output); out.mkdir(parents=True, exist_ok=False)
    tree.save(out/'tree.json')
    receipt = dict(kind='parent_taxonomy_annotations', version=1, parent_context_not_crop_measurement=True,
                   confidence_semantics='min(weighted_support,agree/assigned) * assigned/total_ORFs; not calibrated accuracy',
                   features=binding(features), tree=binding(out/'tree.json'), raw=binding(tsv),
                   query_index=binding(query_index), native_zero_ORF_completion=proof, provenance=p, samples=meta['samples'], truth_accessed=False)
    save_arrays(out/'annotations.npz', a, receipt)
    write_json(out/'completed.json', dict(status='PASS', arrays=binding(out/'annotations.npz'), metadata=binding(out/'annotations.json'), tree=binding(out/'tree.json')))
    return receipt


def read(folder, features):
    """Reload sealed sparse annotations and refuse edited confidence/mask bytes."""
    from ..multiview.arrays import load_arrays
    from ..multiview.views import load
    root = Path(folder); seal = json.loads((root/'completed.json').read_text())
    if seal != dict(status='PASS', arrays=binding(root/'annotations.npz'), metadata=binding(root/'annotations.json'), tree=binding(root/'tree.json')):
        raise ValueError('Annotation cache byte seal differs')
    a, m = load_arrays(root/'annotations.npz', 'parent_taxonomy_annotations'); tree = Tree.load(root/'tree.json')
    d, meta = load(features); n = len(d['ids'])
    if (m['features'] != binding(features) or m['tree'] != binding(root/'tree.json') or m['samples'] != meta['samples']
            or not np.array_equal(a['ids'], d['ids']) or a['paths'].shape != (n, 7)
            or a['paths'].dtype != np.int32 or a['counts'].shape != (n, 3)
            or not np.isfinite(a['confidence']).all() or (a['confidence'] < 0).any() or (a['confidence'] > 1).any()):
        raise ValueError('Annotation full-axis/mask contract differs')
    if (a['counts'].dtype.kind not in 'iu' or (a['counts']<0).any()
            or (a['counts'][:,2]>a['counts'][:,1]).any() or (a['counts'][:,1]>a['counts'][:,0]).any()
            or a['support'].shape!=(n,) or not np.isfinite(a['support']).all()
            or (a['support']<0).any() or (a['support']>1).any() or a['states'].shape!=(n,)):
        raise ValueError('Malformed sealed annotation counters/states')
    if (a['paths'] < 0).any() or (a['paths'] >= len(tree.nodes)).any(): raise ValueError('Foreign annotation node')
    for rank in range(7):
        used = a['paths'][:, rank] != 0
        if (tree.rank[a['paths'][used, rank]] != rank).any(): raise ValueError('Annotation rank index differs')
    # A path must actually be a prefix of one lineage, not independently chosen ranks.
    leaf = np.max(a['paths'], axis=1)
    if not np.array_equal(tree._paths[leaf], a['paths']): raise ValueError('Conflicting annotation path')
    total,assigned,agree=a['counts'].T
    consensus=np.divide(agree,assigned,out=np.zeros(n),where=assigned>0)
    fraction=np.divide(assigned,total,out=np.zeros(n),where=total>0)
    known=(leaf>0)&(assigned>=2)&(agree>=2)&(consensus>=.5)&(a['support']>=.5)
    confidence=np.where(known,np.minimum(consensus,a['support'])*fraction,0).astype(np.float32)
    if not np.array_equal(confidence,a['confidence']):raise ValueError('Annotation confidence disagrees with raw counters')
    if not np.array_equal(known,np.isin(a['states'],['classified','partial'])):raise ValueError('Annotation evidence state differs')
    return a, m, tree
