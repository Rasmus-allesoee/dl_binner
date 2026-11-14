"""Real tiny baseline/export producer and explicit empty physical graph fixture.

Synthetic DNA, native vectors and marker calls are engineering inputs only.
Construction, selection, full exports and audits execute actual installed code.
"""
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests/product')]


def empty_physical(root,f):
    """Write a real empty graph with intact all-DNA axes and the frozen policy."""
    import numpy as np
    from dl_binner.genomegraph.links import DEFAULT,utility
    from dl_binner.io import save_arrays,write_json,id_digest
    from e024_coverage import binding
    root=Path(root);root.mkdir();d=f['data'];e=np.empty((0,2),np.int64)
    m=dict(kind='physical_template_graph',version=1,sample='pooled',samples=f['metadata']['samples'],policy=DEFAULT,
           ids_sha256=id_digest(d['ids'].tolist()),rows=len(d['ids']),bp=int(d['lengths'].sum()),truth_accessed=False,utility=utility(e,d['ids'],d['lengths'],d['eligible']))
    save_arrays(root/'graph.npz',dict(ids=d['ids'],lengths=d['lengths'],eligible=d['eligible'],edges=e,support=np.empty(0,np.int64),orientations=np.empty(0,np.uint8),weights=np.empty(0)),m)
    write_json(root/'completed.json',dict(status='PASS',graph=binding(root/'graph.npz'),receipt=binding(root/'graph.json')));return root


def baseline(root,f,quality,original):
    """Produce a real tiny fixed-vector comparator in an isolated graph process."""
    root=Path(root);root.mkdir();paths={k:str(f[k]) for k in ['features','embeddings','graph','fasta']};paths.update(quality=str(quality),original=str(original),root=str(root))
    (root/'paths.json').write_text(json.dumps(paths))
    with (root/'producer.log').open('x')as log:
        p=subprocess.run([sys.executable,'-I','-B',str(Path(__file__).absolute()),str(root/'paths.json')],stdout=log,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError('Real baseline fixture failed: '+str(root/'producer.log'))


def produce(path):
    """Run unchanged retrieval, E030/E023 candidates, E032 selection and DNA audit."""
    from e024_coverage import write
    from e033_control import constructor_cache
    from dl_binner.discovery import exact
    from dl_binner.construction.grouping import run as construct
    from dl_binner.bootstrap.bridge import run as bridge
    from dl_binner.selection.grouping import run,audit
    p=json.loads(Path(path).read_text());r=Path(p['root'])/'work/oral-noGLM';r.mkdir(parents=True)
    original=Path(p['original'])/'work/oral-noGLM'
    for source,dest in [(original/'embed',r/'student-embed'),(original/'graph',r/'student-graph')]:
        for f in source.rglob('*'):
            if f.is_file():
                q=dest/f.relative_to(source);q.parent.mkdir(parents=True,exist_ok=True);os.link(f,q)
    exact.prepare(p['features'],p['embeddings'],p['graph'],r/'retrieve/result')
    exact.run(p['features'],p['embeddings'],p['graph'],p['quality'],r/'retrieve/result',r/'forest/result')
    construct(p['features'],p['embeddings'],p['graph'],p['quality'],r/'forest/result',r/'construct/result')
    bridge(p['features'],p['embeddings'],p['graph'],p['quality'],p['fasta'],ROOT/'experiments/E023-adaptive-density-bins/config.json',ROOT/'experiments/E023-adaptive-density-bins/source-lock.json',r/'e023/science',engineering=True)
    from e024_control import seal
    for stage in ['forest','construct','e023']:seal(r/stage,dict(engineering=True,actual_producer=True))
    cached=constructor_cache(r,r/'cache');run(p['features'],p['embeddings'],p['graph'],p['quality'],cached,p['fasta'],r/'select/result')
    (r/'audit').mkdir()
    write(r/'audit/proof.json',audit(p['features'],p['embeddings'],p['graph'],p['quality'],cached,r/'select/result'))

if __name__=='__main__':produce(sys.argv[1])
