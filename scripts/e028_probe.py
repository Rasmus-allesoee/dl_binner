#!/usr/bin/env python3
"""One label-free width/runtime/space forecast; no community data or model work."""
import argparse,json,math,sys,time
from pathlib import Path
ROOT=Path(__file__).absolute().parents[1]
sys.path[:0]=[str(ROOT/'tests/product'),str(ROOT/'scripts')]
from e024_coverage import write


def probe(output):
    """Separate JIT warmup from measured full-width sparse retrieval and retained-byte projection."""
    from discovery_fixture import fixture
    from dl_binner.discovery.grouping import prepare
    from dl_binner.io import digest
    root=Path(output).parent/'probe-work';root.mkdir(exist_ok=False)
    f=fixture(root/'warm',256);start=time.monotonic();prepare(f['features'],f['embeddings'],f['graph'],root/'warm-cache',force_native=True)
    warm=time.monotonic()-start
    f=fixture(root/'width',4096);start=time.monotonic();prepare(f['features'],f['embeddings'],f['graph'],root/'width-cache',force_native=True)
    measured=time.monotonic()-start
    axes={'E009':89041,'oral':508763}
    retrieval={u:2*measured*(n/4096)*(math.log2(n)/12)*2 for u,n in axes.items()}
    # Four E009 and two Oral retrievals; 2x n-log-n headroom; independent fixed
    # selection/export/after-input/collection reserve. Forecast is not a timeout.
    retrieval['E009']*=2
    seconds=sum(retrieval.values())+5400
    raw=sum(p.stat().st_size for p in (root/'width-cache').iterdir() if p.is_file())
    result=dict(status='PASS' if seconds<=39600 else 'FORECAST_REQUIRES_ASSESSMENT',
        warmup_seconds=warm,measured_4096_seconds=measured,planning_retrieval_seconds=retrieval,
        planning_remaining_science_seconds=seconds,source_blind_synthetic=True,rows=4096,
        unused_model_or_community_data=False,byte_projection=dict(retrieval_bytes=raw*(4*89041+2*508763)/4096,
            conservative_complete_growth_bytes=3.8*1024**3,extra_cap_bytes=4*1024**3,
            compressed_cap_bytes=2*1024**3,scope='Retrieval measured on fixed dimensions; full partition/export/collection upper includes duplicated opaque IDs and deduplicated numeric caches. Active guard is authoritative.'),
        compile_excluded_from_n_scaling_but_inside_setup_clock=True)
    write(output,result);print(json.dumps(result),flush=True)
    if result['status']!='PASS':raise ValueError('Full complete schedule requires explicit recorded reassessment, no scientific weakening')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);probe(p.parse_args().output)
