#!/usr/bin/env python3
"""Run the unchanged E021 worker with an extraction-only CUDA allocation ceiling.

The lower 13 GiB allocator budget leaves one GiB for CUDA context/workspace below
its separately monitored 14 GiB whole-device limit. No precision, views, model,
seed, loss, geometry or downstream policy changes; graph processes never import
Torch through this wrapper.
"""
import argparse,json,runpy,sys
from pathlib import Path


def main():
    """Configure only actual GPU extraction, then dispatch the frozen stage argv."""
    p=argparse.ArgumentParser(add_help=False);p.add_argument('--plan');p.add_argument('--stage');args,_=p.parse_known_args()
    if args.stage=='extract':
        plan=json.loads(Path(args.plan).read_text())
        if plan['extract_device']!='cuda':raise ValueError('Explicit CUDA extraction required')
        import torch
        if not torch.cuda.is_available()or torch.cuda.device_count()!=1:raise ValueError('One admitted CUDA GPU required')
        total=torch.cuda.get_device_properties(0).total_memory
        if total<14*1024**3:raise ValueError('Insufficient GPU physical memory')
        torch.cuda.set_per_process_memory_fraction(13*1024**3/total,0)
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        print('E021_GPU_ALLOCATOR_CAP_BYTES',13*1024**3,flush=True)
    runpy.run_path(str(Path(__file__).absolute().with_name('e021_control.py')),run_name='__main__')

if __name__=='__main__':main()
