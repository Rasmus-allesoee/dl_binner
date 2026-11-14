#!/usr/bin/env python3
"""Restore admitted cache members only; verify the entire immutable generation.

No BAM reading, graph extraction, mapping, model inference or reference download.
Existing complete restores are verified, while incomplete staging is refused.
"""
import argparse,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e034_pilot import object_metadata,token
import e032_restore as reader


def needed(n,kind):
    """Keep exact companions for each downstream consumer, not broad science copies."""
    if kind=='pooled':return any(n.startswith('work/'+c+'/pooled/') for c in ['E009','oral'])
    if kind=='baseline':return n.startswith('work/oral-noGLM/')
    if kind=='bootstrap':return any(n.startswith('work/'+u+'/'+k)for u in ['E009-noGLM','E009-GLM','oral-noGLM'] for k in ['embed/','graph/result/'])
    if kind=='measurements':return n.startswith('work/E009/')
    raise ValueError('Unknown admitted cache kind')


def restore(kind,output):
    """Hash all source/member/alias bytes and stage only needed regular consumers."""
    output=Path(output);proof=output/'stream-admission.json'
    if proof.exists():
        value=json.loads(proof.read_text())
        for n,b in value['restored_members'].items():
            if binding(output/n)!=b:raise ValueError('Retained consumer drift; no silent recopy')
        return value
    if output.exists():raise ValueError('Partial restore retained; investigate before a fresh attempt')
    lock=json.loads((ROOT/'experiments/E036-optional-pooled-links/reuse-lock.json').read_text())['archives'][kind]
    meta,url=object_metadata(lock['uri'],lock['generation'])
    if int(meta['size'])!=lock['binding']['bytes']:raise ValueError('Archive size/generation differs')
    q=urllib.request.Request(url+'?alt=media&generation='+lock['generation'],headers={'Authorization':'Bearer '+token()})
    old=reader.needed,reader.LOGICAL;reader.needed=lambda n:needed(n,kind);reader.LOGICAL=8*1024**3
    try:
        with urllib.request.urlopen(q,timeout=180)as stream:
            value=reader.stream_restore(stream,dict(size=meta['size'],generation=lock['generation'],md5_hash=meta.get('md5Hash')),lock['binding'],output,lock['inventory'],25*1024**3)
    finally:reader.needed,reader.LOGICAL=old
    (output/'work/restore-admission.json').rename(proof)
    print('E036_RESTORED',kind,len(value['restored_members']),value['restored_bytes'],flush=True);return value

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--kind',choices=['pooled','baseline','bootstrap','measurements'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();restore(a.kind,a.output)
