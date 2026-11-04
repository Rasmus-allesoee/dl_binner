#!/usr/bin/env python3
"""Install only new owned E033 and pinned pysam bytes over a verified CPU base.

No dependency resolver, numerical upgrade or source-cache copy is performed.
The new HTSlib extension belongs to this prefix; old numerical distributions are
borrowed read-only with explicit provenance and native checks before fitting.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).absolute().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from e024_coverage import binding,write
from e019_runtime import create


def install(base,destination,wheel,pysam_wheel,lock,output):
    """Install the exact platform wheels and retain actual separate exit evidence."""
    lock=json.loads(Path(lock).read_text())
    if binding(wheel)!=lock['wheel'] or binding(pysam_wheel)!=lock['pysam_wheel']:
        raise ValueError('Candidate or new BAM dependency wheel differs')
    output=Path(output);create(base,destination,wheel,output.with_name('package-install.json'))
    site=Path(destination)/'lib'/('python'+str(sys.version_info.major)+'.'+str(sys.version_info.minor))/'site-packages'
    if any(site.glob('pysam*')):raise ValueError('New BAM dependency must not overwrite or borrow an existing base member')
    argv=[str(Path(destination)/'bin/python'),'-I','-B','-m','pip','--isolated','install','--no-deps','--no-index','--no-compile',str(pysam_wheel)]
    p=subprocess.run(argv,capture_output=True,text=True)
    output.with_suffix('.stdout').write_text(p.stdout);output.with_suffix('.stderr').write_text(p.stderr)
    write(output,dict(status='PASS' if not p.returncode else 'FAILED',argv=argv,exit_code=p.returncode,
        own_BAM_dependency=binding(pysam_wheel),no_numerical_reinstall_or_explicit_base_write=True))
    if p.returncode:raise RuntimeError('Owned pinned BAM dependency install failed')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['base','destination','wheel','pysam-wheel','lock','output']:p.add_argument('--'+n,required=True,type=Path)
    a=p.parse_args();install(a.base,a.destination,a.wheel,a.pysam_wheel,a.lock,a.output)
