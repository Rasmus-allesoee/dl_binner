"""Installed local/native stages for explicit BAM measurement and new learning.

No truth, acquisition, mapper, detector or cloud interface. A scientific launcher
must supply external source/runtime/resource/release gates before community use.
"""
import argparse
from pathlib import Path


def main():
    """Run one exclusive stage; never silently regenerate another prerequisite."""
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',required=True,choices=['measure','rebind','teacher','pairs','student','embed'])
    for n in ['features','views','output','new-features','bam','measurements','tokens','frozen','original','teacher','pairs','checkpoint','embeddings','graph','markers','hmm']:
        p.add_argument('--'+n,type=Path,required=n in ['features','views','output'])
    p.add_argument('--sample');p.add_argument('--threads',type=int,default=4)
    p.add_argument('--engineering-epochs',type=int)
    a=p.parse_args()
    def needed(*fields):
        for f in fields:
            if getattr(a,f) is None:p.error(a.stage+' requires --'+f.replace('_','-'))
    if a.stage=='measure':
        needed('bam','sample');from .measurement import summarize
        summarize(a.bam,a.features,a.views,a.output,a.sample)
    elif a.stage=='rebind':
        needed('measurements');from .cache import rebind
        rebind(a.measurements,a.features,a.views,a.output)
    elif a.stage=='pairs':
        needed('new_features','measurements','embeddings','graph','markers','hmm');from .pairs import prepare
        prepare(a.new_features,a.features,a.views,a.measurements,a.embeddings,a.graph,a.markers,a.hmm,a.output)
    else:
        needed('new_features','measurements','tokens','original');from . import model
        args=(a.features,a.new_features,a.views,a.tokens,a.frozen,a.measurements,a.original)
        if a.stage=='embed':
            needed('checkpoint');model.embed(*args,a.checkpoint,a.output,pairs=a.pairs,threads=a.threads)
        else:
            if a.stage=='student':needed('teacher','pairs')
            model.train(*args,a.output,teacher=a.teacher,pairs=a.pairs,threads=a.threads,engineering_epochs=a.engineering_epochs)


if __name__=='__main__':main()
