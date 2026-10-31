"""Real tiny FASTA/features and synthetic retained unit-vector/marker caches."""
from pathlib import Path
import numpy as np
from dl_binner.multiview.views import prepare, config, load
from dl_binner.io import save_arrays, digest, write_json


def fixture(root, n=256):
    """Build disconnected old-neighbor components without fitting or detecting markers."""
    root=Path(root);root.mkdir(exist_ok=True);rng=np.random.default_rng(11)
    rows=[]
    for i in range(n):
        length=3200 if i%2 else 800
        dna=''.join(rng.choice(list('ACGT'),length,p=rng.dirichlet([1.,1.,1.,1.])))
        rows.append((f'opaque-{i:04d}',dna))
    rows += [('short-kept-in-accounting','ACGT'*10),('ambiguous-kept','N'*600)]
    fasta=root/'source.fna';fasta.write_text(''.join('>'+q+'\n'+s+'\n' for q,s in rows))
    depth=rng.uniform(1,30,(len(rows),10));depth[np.arange(len(rows))%3==0]=0
    table=root/'depth.tsv';table.write_text('contig_id\t'+'\t'.join('sample-'+str(i) for i in range(10))+'\n'+''.join(q+'\t'+'\t'.join(map(str,d))+'\n' for (q,s),d in zip(rows,depth)))
    prepare(fasta,table,root/'data',config());features=root/'data/features.npz';data,meta=load(features)
    vectors=np.eye(64,dtype=np.float32)[np.minimum(np.arange(len(rows))//32,63)]+rng.normal(0,.001,(len(rows),64)).astype(np.float32)
    vectors/=np.linalg.norm(vectors,axis=1)[:,None];vectors[~data['eligible']]=0
    emb=root/'embeddings.npz';save_arrays(emb,dict(ids=data['ids'],features=vectors,evidence=data['eligible']),dict(kind='embeddings',features_sha256=digest(features),metric='unit sphere'))
    nn=np.full((len(rows),min(30,n-1)),-1,np.int64);edges=set()
    for i in range(n):
        component=np.arange(i//32*32,min(n,(i//32+1)*32));component=component[component!=i]
        nn[i]=component[:nn.shape[1]]
        edges.update(tuple(sorted((i,int(j)))) for j in nn[i])
    graph=root/'graph.npz';ordered=sorted(edges)
    save_arrays(graph,dict(ids=data['ids'],neighbors=nn,edges=np.asarray(ordered,np.int64).reshape(-1,2),weights=np.ones(len(ordered))),dict(kind='candidate_sparse_graph',embedding_sha256=digest(emb),audit={'mean_tie_aware_recall':1.}))
    evidence=root/'markers.json';write_json(evidence,dict(panel_size=4,calls={str(data['ids'][i]):{'family-0':[.95]} for i in range(0,n,17)}))
    return dict(root=root,fasta=fasta,features=features,embeddings=emb,graph=graph,evidence=evidence,data=data)
