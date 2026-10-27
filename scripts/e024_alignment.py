#!/usr/bin/env python3
"""Retain the exact E024 primary SAM stream as lossless BAM without disk spooling.

The grouping summary still consumes the original unfiltered SAM. This sidecar
changes retention only: it preserves sequence, qualities, unmapped records and
all emitted primary/supplementary records. It never sorts, filters or remaps.
Native transport is write-once private GCS; engineering uses exclusive local
fixture files. Full byte/SHA256 readback and native full BAM decode are required
before a caller can release newly acquired FASTQ. Future consumers sort/index
restored BAMs; these files are deliberately not advertised as sorted BAMs.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import threading


class BamRetention:
    """Tee SAM into one samtools encoder and verify its closed remote BAM bytes."""
    def __init__(self, samtools, destination, log_root, cap, gcloud=None):
        self.samtools=str(samtools);self.destination=str(destination);self.cap=int(cap)
        self.root=Path(log_root);self.gcloud=str(gcloud) if gcloud else None
        if not 0<self.cap<=130*1024**3:raise ValueError('Explicit bounded BAM cap required')
        if self.gcloud:
            if not self.destination.startswith('gs://dl-binner-archive-167650584170/e024/') or not self.destination.endswith('.bam'):
                raise ValueError('Private E024 BAM destination required')
        else:
            p=Path(self.destination);p.parent.mkdir(parents=True,exist_ok=True)
            self.local=p.open('xb')
        self.errors=[];self.size=0;self.digest=hashlib.sha256();self.logs=[];self.procs=[]
        log=(self.root/'bam-encode.log').open('xb');self.logs.append(log)
        self.encode=subprocess.Popen([self.samtools,'view','-@','0','-b','-'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=log)
        self.procs.append(self.encode)
        if self.gcloud:
            log=(self.root/'bam-upload.log').open('xb');self.logs.append(log)
            self.upload=subprocess.Popen([self.gcloud,'storage','cp','--if-generation-match=0','-',self.destination],stdin=subprocess.PIPE,stdout=log,stderr=log)
            self.procs.append(self.upload);sink=self.upload.stdin
        else:sink=self.local
        def pump():
            try:
                for b in iter(lambda:self.encode.stdout.read(1024**2),b''):
                    self.size+=len(b)
                    if self.size>self.cap:raise ValueError('BAM exceeds original per-sample/aggregate allowance')
                    self.digest.update(b);sink.write(b)
            except BaseException as exc:self.errors.append(repr(exc))
            finally:sink.close()
        self.thread=threading.Thread(target=pump,daemon=True);self.thread.start()

    def lines(self, stream):
        """Yield every original SAM line unchanged after submitting it to BAM."""
        for line in stream:
            if self.errors:raise RuntimeError('BAM producer/transport failed: '+repr(self.errors))
            self.encode.stdin.write(line.encode('ascii'))
            yield line

    def finish(self, expected_records):
        """Require all producers, exact readback and a complete native BAM decode."""
        self.encode.stdin.close();code=self.encode.wait(timeout=120);self.thread.join(120)
        if self.thread.is_alive() or code or self.errors:raise RuntimeError('BAM encoding failed: '+repr((code,self.errors)))
        if self.gcloud and self.upload.wait(timeout=120):raise RuntimeError('Write-once BAM upload failed')
        source=subprocess.Popen([self.gcloud,'storage','cat',self.destination],stdout=subprocess.PIPE,stderr=self.logs[-1]) if self.gcloud else None
        if source:self.procs.append(source)
        data=source.stdout if source else Path(self.destination).open('rb')
        log=(self.root/'bam-readback-decode.log').open('xb');self.logs.append(log)
        decoder=subprocess.Popen([self.samtools,'view','-@','0','-c','-'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=log)
        self.procs.append(decoder);h=hashlib.sha256();size=0
        try:
            for b in iter(lambda:data.read(1024**2),b''):
                size+=len(b)
                if size>self.size:raise ValueError('BAM readback exceeds emitted bytes')
                h.update(b);decoder.stdin.write(b)
            decoder.stdin.close();count=decoder.stdout.read();decode_exit=decoder.wait(timeout=120)
            remote_exit=source.wait(timeout=120) if source else 0
            if (size!=self.size or h.hexdigest()!=self.digest.hexdigest() or remote_exit or decode_exit
                    or int(count)!=expected_records):raise ValueError('BAM byte/readback/full-decode/record contract differs')
        finally:data.close()
        return dict(status='PASS',uri=self.destination,bytes=size,sha256=h.hexdigest(),
                    full_readback_verified=True,native_full_decode_records=int(count),
                    native_encoder_exit=code,native_decoder_exit=decode_exit,sorted=False,indexed=False,
                    semantics='All original emitted SAM records, sequence/quality retained; unfiltered primary -N0; sort/index on restore; cannot recover unreported alternatives',
                    backup=True)

    def close(self):
        """Stop only owned sidecar children on success or a failed primary consumer."""
        for p in reversed(self.procs):
            if p.poll() is None:
                p.terminate()
                try:p.wait(timeout=5)
                except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
        self.thread.join(5)
        for f in self.logs:f.close()
        if hasattr(self,'local') and not self.local.closed:self.local.close()
