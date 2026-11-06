#!/usr/bin/env python3
"""Inspect already downloaded small R220 taxonomy metadata, never protein DNA.

The full protein archive is represented only by its publisher MD5, HEAD size and
bounded range. Metadata admission is distinct from a verified bulk database.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time


def run(source,output):
    """Build the canonical full release tree and bound its real sparse dimensions."""
    from dl_binner.taxonomy.tree import from_gtdb,RANKS
    from dl_binner.context.tokens import binding
    from dl_binner.io import write_json
    source=Path(source);root=Path(output);root.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    payload=json.loads((source/'metadata-payloads.json').read_text())
    for n,b in payload.items():
        p=source/n
        if p.stat().st_size!=b['bytes']or hashlib.sha256(p.read_bytes()).hexdigest()!=b['sha256']:raise ValueError('Reference metadata bytes differ')
    tree,accessions=from_gtdb([source/'bac120_taxonomy_r220.tsv',source/'ar53_taxonomy_r220.tsv'])
    tree.save(root/'tree.json')
    value=dict(status='PASS_SMALL_REFERENCE_METADATA_ONLY',source_release=(source/'gtdb-VERSION.txt').read_text().strip(),
        accessions=len(accessions),nodes=len(tree.nodes),rank_counts={r:int((tree.rank==i).sum())for i,r in enumerate(RANKS)},
        max_siblings=max(map(len,tree.children)),two_embedding_and_bias_float32_bytes=len(tree.nodes)*33*4,
        tree=binding(root/'tree.json'),metadata=payload,transport=json.loads((source/'fetch.json').read_text()),
        protein_payload=dict(bytes=71733563809,publisher_md5='49fffb75d1d142ec669d964690c2ab6b',full_SHA256=None,
            full_archive_or_member_inventory_verified=False,bulk_not_acquired=True),
        license=dict(MMseqs2='MIT',GTDB='CC BY-SA 4.0',GTDB_source='https://gtdb.ecogenomic.org/licenses'),
        wall_seconds=time.monotonic()-start,community_annotations_created=False)
    write_json(root/'completed.json',value);print(json.dumps({k:v for k,v in value.items()if k not in ['transport','metadata']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.source,a.output)
