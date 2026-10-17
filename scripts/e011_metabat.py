#!/usr/bin/env python3
"""Own pinned MetaBAT2 setup, native tiny readers and executed binary provenance.

Install only predownloaded checksum-locked registry packages into a fresh prefix.
The smoke is generated software evidence with its explicit reduced bin-size
threshold, not community tuning. This module does not run the community reference.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import re
import subprocess
import sys
import tarfile
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding,write_json

REPO=Path(__file__).absolute().parents[1]


def install(payload,prefix,work):
    """Verify all independent native packages and install offline, without a solve/retry."""
    payload,prefix,work=map(Path,[payload,prefix,work]);work.mkdir(parents=True,exist_ok=False)
    if prefix.exists():raise FileExistsError('Fresh MetaBAT prefix required; no upgrade/resume')
    lock=json.loads((REPO/'experiments/E011-cached-grouping-reference/metabat-linux.json').read_text())
    for row in lock['packages']:
        if binding(payload/'linux-packages'/row['filename'])!={k:row[k]for k in ['bytes','sha256']}:
            raise ValueError('Pinned native package changed: '+row['name'])
    archive=payload/'micromamba-linux-2.3.3.tar.bz2'
    if binding(archive)!={k:lock['installer'][k]for k in ['bytes','sha256']}:raise ValueError('Installer bytes differ')
    binary=work/'micromamba'
    with tarfile.open(archive)as tar:
        member=tar.getmember('bin/micromamba')
        if not member.isfile():raise ValueError('Installer is not a regular executable')
        binary.write_bytes(tar.extractfile(member).read());binary.chmod(0o755)
    explicit=work/'explicit.txt'
    explicit.write_text('@EXPLICIT\n'+'\n'.join((payload/'linux-packages'/row['filename']).absolute().as_uri()+'#'+row['md5']for row in lock['packages'])+'\n')
    env=dict(os.environ,MAMBA_ROOT_PREFIX=str(work/'mamba-root'),MAMBA_REGISTER_ENVS='false')
    subprocess.run([str(binary),'create','-y','--offline','--no-rc','-p',str(prefix),'--file',str(explicit)],env=env,check=True)
    inventory={}
    for q in (prefix/'conda-meta').glob('*.json'):
        d=json.loads(q.read_text());inventory[d['name']]={'version':d['version'],'build':d['build']}
    expected={r['name']:{'version':r['version'],'build':r['build']}for r in lock['packages']}
    if inventory!=expected:raise ValueError('Complete independent native package closure differs')
    write_json(work/'installed.json',dict(inventory=inventory,installer=binding(binary),binary=binding(prefix/'bin/metabat2'),offline=True))


def probe(binary,output,previous=None):
    """Check actual native CLI and bind its binary/loaded library paths, not unused headers."""
    binary=Path(binary).absolute();help_run=subprocess.run([str(binary),'--help'],capture_output=True,text=True,check=True,timeout=15)
    text=help_run.stdout+help_run.stderr
    if '2:2.18'not in text or '--cvExt'not in text or '--minSmallContig'not in text:raise ValueError('Actual native MetaBAT CLI differs')
    command=['otool','-L',str(binary)]if platform.system()=='Darwin'else['ldd',str(binary)]
    libraries=subprocess.check_output(command,text=True,timeout=15)
    members={str(binary):binding(binary)}
    if platform.system()=='Linux':
        if 'not found'in libraries:raise ValueError('Native shared library missing')
        for name in re.findall(r'(/[^\s()]+)',libraries):
            q=Path(name)
            if q.is_file():members[str(q)]=binding(q)
    if previous is not None and json.loads(Path(previous).read_text())['execution_members']!=members:
        raise ValueError('Executed MetaBAT binary/library bytes changed')
    write_json(output,dict(version='2.18',system=platform.system(),binary=str(binary),help=text,
                           library_report=libraries,execution_members=members))


def smoke(binary,output):
    """Run native cvExt readers/writers and intended row-order refusal on tiny DNA."""
    from e011_cached import external_export
    output=Path(output);output.mkdir(parents=True,exist_ok=False);rng=random.Random(71)
    rows=[]
    for i in range(80):
        alphabet='AAACCGTT'if i<40 else'CCCGGGAT'
        rows.append(('opaque_'+str(i),''.join(rng.choice(alphabet)for _ in range(5000))))
    rows.append(('short_retained','ACGT'*100))
    fasta=output/'tiny.fa';depth=output/'tiny.depth.tsv'
    fasta.write_text(''.join('>'+q+'\n'+s+'\n'for q,s in rows))
    lines=['contig_id\t'+'\t'.join('sample_'+str(j)for j in range(10))]
    for i,(q,_)in enumerate(rows):
        values=[str((20+j*3)if i<40 else(80-j*3))for j in range(10)]
        lines.append(q+'\t'+'\t'.join(values))
    depth.write_text('\n'.join(lines)+'\n');native=output/'native';native.mkdir()
    argv=[str(Path(binary).absolute()),'-i',str(fasta),'-a',str(depth),'--cvExt','-o',str(native/'bin'),
          '-t','2','--seed','11','-s','20000','--unbinned','-v']
    env=dict(os.environ,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2')
    subprocess.run(argv,check=True,timeout=90,env=env)
    result=external_export(fasta,native,output/'export')
    if result['bins']<1 or result['contigs']!=81 or result['bp']!=400400:raise ValueError('Native positive/export contract missing')
    # Deliberately malformed input is a separate refusal contract, never a retry.
    bad=output/'wrong-order.tsv';lines[1],lines[2]=lines[2],lines[1];bad.write_text('\n'.join(lines)+'\n')
    broken=list(argv);broken[broken.index('-a')+1]=str(bad);broken[broken.index('-o')+1]=str(output/'refusal-bin')
    rejected=subprocess.run(broken,capture_output=True,text=True,timeout=30,env=env)
    (output/'refusal.log').write_text(rejected.stdout+rejected.stderr)
    if rejected.returncode==0 or 'order'not in (rejected.stdout+rejected.stderr).lower():
        raise ValueError('Native row-order refusal was not the intended error')
    write_json(output/'passed.json',dict(status='PASS',positive_command=argv,accounting=result,
        intended_order_refusal_exit=rejected.returncode,community_threshold_override=False,
        fixture_only_minimum_bin_bp=20000,native_readers_and_writers=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['install','probe','smoke'])
    for name in ['payload','prefix','work','binary','output','previous']:p.add_argument('--'+name,type=Path)
    a=p.parse_args()
    if a.action=='install':install(a.payload,a.prefix,a.work)
    elif a.action=='probe':probe(a.binary,a.output,a.previous)
    else:smoke(a.binary,a.output)
