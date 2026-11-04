#!/usr/bin/env python3
"""Seal complete ordered measurements and publish their explicit parent rebind."""
import argparse
from pathlib import Path


def close(root,features,views,output):
    """Require every expected closed sample before publishing a reusable bank."""
    from dl_binner.multiview.views import load
    from dl_binner.multiscale.cache import seal,rebind
    _,meta=load(features);root=Path(root)
    seal(root,features,views,[root/('sample-%02d'%i) for i in range(len(meta['samples']))])
    rebind(root,features,views,output)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['root','features','views','output']:p.add_argument('--'+n,required=True,type=Path)
    a=p.parse_args();close(a.root,a.features,a.views,a.output)
