"""Prepare own synthetic DNA and native synthetic HMM, never public communities."""
import argparse,json,sys
from pathlib import Path


def generate(output):
    """Generate diverse oligomers plus native coding/short/N fixtures and both modes."""
    import numpy as np
    from dl_binner.hybrid.model import config
    from dl_binner.multiview.views import prepare,config as base
    from dl_binner.context.tokens import prepare as tokens
    sys.path.insert(0,str(Path(__file__).absolute().parents[2]/'tests/product'))
    from candidate_fixture import fixture
    r=Path(output);r.mkdir(parents=True,exist_ok=False)
    fasta,depth,rows=fixture(r);rng=np.random.default_rng(718)
    words=np.array([''.join('ACGT'[(i>>s)&3]for s in(6,4,2,0))for i in range(256)])
    for i in range(24):
        n=500+(i*43)%1400;prob=rng.dirichlet(np.full(256,.3));dna=''.join(rng.choice(words,(n+3)//4,p=prob))[:n];rows.append((f'own-opaque-{i:03d}',dna))
    fasta.write_text(''.join('>'+i+'\n'+s+'\n'for i,s in rows))
    depth.write_text('contig_id\tZ-last\tA-first\n'+''.join(i+'\t'+str(j%7)+'\t'+str(j%11)+'\n'for j,(i,_)in enumerate(reversed(rows))))
    cfg=config();cfg['epochs']=20;cfg['batch_size']=256;cfg.update(min_bin_bp=1,min_bin_contigs=1)
    b=base();b.update(min_bin_bp=1,min_bin_contigs=1)
    (r/'config.json').write_text(json.dumps(cfg,indent=2)+'\n');(r/'base-config.json').write_text(json.dumps(b,indent=2)+'\n')
    for mode in ['depth','sequence']:
        prepare(fasta,depth if mode=='depth'else None,r/mode,b)
        tokens(fasta,r/mode/'features.npz',r/mode/'views.npz',r/mode/'tokens')
    (r/'generated.json').write_text(json.dumps(dict(rows=len(rows),bp=sum(len(s)for _,s in rows),scope='Own synthetic engineering DNA and synthetic parent means, no quality score'),indent=2)+'\n')


def marker(output):
    """Build/call one real synthetic HMM in a separate non-Torch process."""
    from dl_binner.candidate.markers import cache
    sys.path.insert(0,str(Path(__file__).absolute().parents[2]/'tests/product'))
    from candidate_fixture import asset
    r=Path(output);hmm,manifest=asset(r,r/'assembly.fna');(r/'markers').mkdir();cache(r/'assembly.fna',hmm,manifest,r/'markers',4)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('operation',choices=['generate','marker']);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    (generate if a.operation=='generate'else marker)(a.output)
