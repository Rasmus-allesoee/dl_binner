#!/usr/bin/env python3
"""Keep E009's tested boot/process detector; best-effort archive its final snapshot.

No progress monitoring, retry or scientific work. Snapshot upload uses only the
existing VM service identity/bucket, and can never prevent clean shutdown. The
provider STOP remains independent. The unchanged base detector is explicitly
copied and byte-bound beside this wrapper before arming the fresh timer.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import urllib.parse
import urllib.request


def upload_snapshot(path,uri):
    """Send one bounded private JSON object with an ephemeral metadata token, once."""
    parsed=urllib.parse.urlsplit(uri)
    if parsed.scheme!='gs' or not parsed.netloc:raise ValueError('Private gs locator required')
    data=Path(path).read_bytes()
    if len(data)>256*1024:raise ValueError('Exit snapshot exceeds compact bound')
    token_url='http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token'
    with urllib.request.urlopen(urllib.request.Request(token_url,headers={'Metadata-Flavor':'Google'}),timeout=5)as response:
        token=json.load(response)['access_token']
    query=urllib.parse.urlencode(dict(uploadType='media',name=parsed.path.lstrip('/'),ifGenerationMatch=0))
    url='https://storage.googleapis.com/upload/storage/v1/b/'+parsed.netloc+'/o?'+query
    request=urllib.request.Request(url,data=data,method='POST',headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=5)as response:response.read(65536)


def finish(path,uri,stop,upload=upload_snapshot):
    """Attempt compact evidence upload but always request shutdown, including failure."""
    try:upload(path,uri)
    except Exception as exc:print('EXIT_SNAPSHOT_UPLOAD_UNAVAILABLE '+str(exc),flush=True)
    finally:stop()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['base','config','state','evidence']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();spec=importlib.util.spec_from_file_location('e011_pinned_base_watchdog',a.base)
    base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
    cfg=json.loads(a.config.read_text())
    base.tick(cfg,a.state,a.evidence,shutdown=lambda:finish(a.evidence/'exit-snapshot.json',cfg['exit_snapshot_uri'],base.clean_shutdown))
