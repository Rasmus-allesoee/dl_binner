"""Small validated taxonomic trees; no community truth or dense one-hot matrices.

Node zero is an unclassified sentinel and node one is the classifier's root.
Ranked paths preserve absent ranks as zero rather than inventing a species.
"""
import json
from pathlib import Path

import numpy as np

RANKS = ('superkingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species')


class Tree:
    """Validate an independently supplied rooted hierarchy and expose sparse paths."""

    def __init__(self, nodes):
        if not isinstance(nodes, list) or len(nodes) < 2:
            raise ValueError('Taxonomy needs an explicit sentinel and root')
        self.nodes = nodes
        self.children = [[] for _ in nodes]
        for i, row in enumerate(nodes):
            if (set(row) != {'id', 'parent', 'rank', 'name'} or type(row['id']) is not int
                    or row['id'] != i or type(row['parent']) is not int
                    or not isinstance(row['name'], str) or not row['name']
                    or row['rank'] not in RANKS + ('no rank',)):
                raise ValueError('Malformed taxonomy node/schema')
            parent = row['parent']
            if i < 2:
                if parent != i or row['rank'] != 'no rank':
                    raise ValueError('Invalid taxonomy sentinel/root')
            elif not 1 <= parent < i:
                raise ValueError('Taxonomy must be acyclic, rooted and parent-first')
            else:
                self.children[parent].append(i)
        self._paths = np.zeros((len(nodes), len(RANKS)), np.int32)
        for i in range(2, len(nodes)):
            row = nodes[i]; parent = row['parent']
            self._paths[i] = self._paths[parent]
            if row['rank'] in RANKS:
                at = RANKS.index(row['rank'])
                if self._paths[i, at:].any():
                    raise ValueError('Repeated or reversed taxonomy rank')
                self._paths[i, at] = i
        self.rank = np.array([RANKS.index(r['rank']) if r['rank'] in RANKS else -1 for r in nodes])

    def path(self, node):
        """Return a copy of the partial ranked path, refusing foreign numeric labels."""
        if type(node) is not int or not 0 <= node < len(self.nodes):
            raise ValueError('Unknown classifier taxid')
        return self._paths[node].copy()

    def save(self, path):
        """Write a fresh canonical tree; never replace a classifier database's tree."""
        from ..io import write_json
        write_json(path, dict(kind='classifier_taxonomy_tree', version=1, nodes=self.nodes))

    @classmethod
    def load(cls, path):
        """Read only the declared classifier-tree schema, not arbitrary metadata."""
        value = json.loads(Path(path).read_text())
        if set(value) != {'kind', 'version', 'nodes'} or value['kind'] != 'classifier_taxonomy_tree' or type(value['version']) is not int or value['version'] != 1:
            raise ValueError('Unknown classifier taxonomy tree schema')
        return cls(value['nodes'])


def from_gtdb(paths):
    """Build a deterministic prefix tree and accession map from GTDB TSV metadata.

    GTDB names are hierarchy-specific. Empty ranks truncate the annotation;
    nonempty ranks after a gap are refused. Accessions are reference metadata,
    never query features. This does not acquire reference protein sequences.
    """
    accessions = {}; prefixes = set(); letters = 'dpcofgs'
    for path in paths:
        with Path(path).open() as stream:
            for line in stream:
                fields = line.rstrip('\n').split('\t')
                if len(fields) != 2 or not fields[0] or fields[0] in accessions:
                    raise ValueError('Malformed/duplicate GTDB accession')
                names = fields[1].split(';')
                if len(names) != 7 or any(not x.startswith(k+'__') for k, x in zip(letters, names)):
                    raise ValueError('Unexpected GTDB rank layout')
                used = []; gap = False
                for name in names:
                    if len(name) == 3: gap = True; continue
                    if gap: raise ValueError('Nonempty GTDB rank after a gap')
                    used.append(name); prefixes.add(tuple(used))
                accessions[fields[0]] = tuple(used)
    nodes = [dict(id=0, parent=0, rank='no rank', name='unclassified'),
             dict(id=1, parent=1, rank='no rank', name='root')]
    lookup = {(): 1}
    for prefix in sorted(prefixes, key=lambda p: (len(p), p)):
        i = len(nodes); lookup[prefix] = i
        nodes.append(dict(id=i, parent=lookup[prefix[:-1]], rank=RANKS[len(prefix)-1], name=prefix[-1][3:]))
    return Tree(nodes), {a: lookup[p] for a, p in accessions.items()}
