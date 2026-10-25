"""Prepare only generated tiny inputs and a restore packet for the actual DAG."""
import sys,json,tarfile,hashlib,argparse
from pathlib import Path
repo=Path(__file__).absolute().parents[1];sys.path.insert(0,str(repo/'tests/product'))
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--workflow-python',type=Path,required=True);a=p.parse_args()
from relational_fixture import fixture,NumericExtractor
from dl_binner.hybrid.bank import prepare as bank,model_pin
from dl_binner.relational.pairs import prepare
from dl_binner.relational.model import config
from dl_binner.io import write_json
r=a.root.absolute();r.mkdir(exist_ok=False)
f=fixture(r/'inputs')
bank(f['fasta'],f['features'],f['views'],r/'input-bank',NumericExtractor(),model_pin())
prepare(f['features'],f['embeddings'],f['graph'],f['markers'],f['hmm'],r/'original-pairs')
def bound(p):return dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
archive=r/'pairs.tar.gz'
with tarfile.open(archive,'x:gz')as t:
 for p in sorted((r/'original-pairs').iterdir()):t.add(p,arcname=p.name,recursive=False)
files={str(p):bound(p)for directory in [f['root']/'data',f['tokens'],f['markers'],r/'input-bank',f['root']/'group']for p in directory.iterdir()if p.is_file()}
for p in [f['fasta'],f['hmm'],f['embeddings'],f['embeddings'].with_suffix('.json')]:files[str(p)]=bound(p)
lock=dict(kind='E022 exact used-input and pair-cache lock',files=files,pair_archive=bound(archive),pair_members={p.name:bound(p)for p in (r/'original-pairs').iterdir()})
write_json(r/'input-lock.json',lock);cfg=config();cfg.update(min_bin_bp=1,min_bin_contigs=1);write_json(r/'config.json',cfg);write_json(r/'base-config.json',f['cfg'])
u=dict(fasta=str(f['fasta']),features=str(f['features']),views=str(f['views']),tokens=str(f['tokens']),frozen=str(r/'input-bank'),marker_cache=str(f['markers']),hmm=str(f['hmm']),anchor_embeddings=str(f['embeddings']),anchor_graph=str(f['graph']))
plan=dict(kind='E022 cached marker-informed learning',work=str(r/'work'),unit=u,threads=4,python=sys.executable,worker=str(repo/'scripts/e022_control.py'),workflow_python=str(a.workflow_python.absolute()),snakefile=str(repo/'experiments/E022-marker-informed-learning/Snakefile'),config=str(r/'config.json'),base_config=str(r/'base-config.json'),input_lock=str(r/'input-lock.json'),pair_archive=str(archive))
write_json(r/'plan.json',plan)
print('PREPARED_EXACT_TINY_DAG',r)

import subprocess
subprocess.run([sys.executable,'-I','-B',str(repo/'scripts/e022_control.py'),'--plan',str(r/'plan.json'),'--workflow','--engineering'],check=True)
sys.path.insert(0,str(repo/'scripts'))
from e022_collect import pack
e=r/'evidence';e.mkdir();write_json(e/'fixture.json',dict(actual='native HMM/sparse/cache/train/reload/refine/export/DAG',mocked='GLM NumericExtractor and hand-authored marker annotations'))
pack(r/'work',e,r/'return')
