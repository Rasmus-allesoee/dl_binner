"""Real tiny E024 read/alignment/summary/rebind/retrieval/export contracts.

No accepted community is mapped or scored. Native vectors/marker calls in the
fixture are explicitly synthetic; strobealign, SAM/BAM readers, samtools depth,
feature preparation, sparse grouping and complete exports are actual paths.
"""
import contextlib
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from e024_coverage import (SAMPLES, binding, write, verify_segments, fastq_pairs,
    sum_sam, map_summary, read_profile, axis, combine)
from e024_information import rebind, load_rebound, candidates, run, audit
from e024_control import cleanup_read, seal, verify_seal, acquire_one
from e024_collect import pack
from dl_binner.density import grouping as old
from dl_binner.io import digest, save_arrays

ROOT = Path(__file__).absolute().parents[1]
MAPPER = Path(os.environ.get('E024_MAPPER',str(ROOT/'artifacts/e005-linux-pilot/env-mapping-local/bin/strobealign')))
SAMTOOLS = Path(os.environ.get('E024_SAMTOOLS',str(ROOT/'artifacts/e005-linux-pilot/env-mapping-local/bin/samtools')))
CFG = json.loads((ROOT/'experiments/E023-adaptive-density-bins/config.json').read_text())


def fixture(root):
    """Build random DNA, actual caches/graph and synthetic unit-vector/marker inputs."""
    from dl_binner.multiview.views import prepare, config
    from dl_binner.multiview.arrays import load_arrays
    from dl_binner.candidate.grouping import group
    rng = random.Random(191)
    dna = [''.join(rng.choices('ACGT',k=n)) for n in [6000,6000,6000,6000,800,500,80]]
    dna[1] = dna[0]  # A real alignment competitor, not a label selected by the mapper.
    ids = ['opaque-z','opaque-a','opaque-t','opaque-b','short','marker-negative','excluded']
    fasta = root/'dna.fna'
    fasta.write_text(''.join('>'+q+'\n'+s+'\n' for q,s in zip(ids,dna)))
    prepare(fasta,None,root/'features',config())
    features = root/'features/features.npz'
    data, _ = load_arrays(features,'features')
    x = np.zeros((len(ids),64),np.float32)
    x[:6,:6] = np.eye(6,dtype=np.float32)
    embedding = root/'embeddings.npz'
    save_arrays(embedding,dict(ids=data['ids'],features=x,evidence=data['eligible']),
                dict(kind='embeddings',features_sha256=digest(features),metric='synthetic fixture unit vectors'))
    group(embedding,features,root/'original',config(),4)
    evidence = root/'markers.json'
    write(evidence,dict(panel_size=40,calls={'opaque-t':{'m':[1.]},'opaque-b':{'m':[.7]}},loci=[]))
    return dict(features=features,views=root/'features/views.npz',embeddings=embedding,
                graph=root/'original/graph.npz',marker_evidence=evidence,reference=fasta),dna


def reads(root, dna, sample=6):
    """Write real interleaved/paired reads with unique, ambiguous and unmapped pairs."""
    rc = str.maketrans('ACGT','TGCA')
    pairs = []
    for j, source in enumerate([dna[2],dna[0],dna[3]]):
        pairs.append((f'pair{j}',source[300:450],source[420:570].translate(rc)[::-1]))
    rng = random.Random(909+sample)
    pairs.append(('unmapped',''.join(rng.choices('ACGT',k=150)),''.join(rng.choices('ACGT',k=150))))
    left, right = [], []
    for ident,a,b in pairs:
        left.append(f'@{ident}/1\n{a}\n+\n'+('I'*150)+'\n')
        right.append(f'@{ident}/2\n{b}\n+\n'+('I'*150)+'\n')
    interleaved = root/'raw.fq.gz'
    with gzip.open(interleaved,'wt') as f:
        for a,b in zip(left,right):f.write(a+b)
    (root/'r1.fq').write_text(''.join(left))
    (root/'r2.fq').write_text(''.join(right))
    return interleaved,root/'r1.fq',root/'r2.fq'


def matrix_fixture(root, source):
    """Write tiny measured summaries in the exact production writer schema."""
    ids,lengths = axis(source)
    paths = []
    for j,sample in enumerate(SAMPLES):
        d = root/str(sample)
        d.mkdir()
        path = d/'depth.tsv'
        with path.open('x') as f:
            f.write('contig_id\taligned_read_bases\tlength\tmean\n')
            for i,(q,n) in enumerate(zip(ids,lengths)):
                total = 0 if i == 5 else (i+1)*(j+1)*100
                f.write(f'{q}\t{total}\t{n}\t{total/n:.17g}\n')
        write(d/'done.json',dict(status='PASS',sample=sample,reference=binding(source),depth=binding(path)))
        paths.append(path)
    combine(source,paths,SAMPLES,root/'matrix.tsv')
    return root/'matrix.tsv'


class Coverage(unittest.TestCase):
    def test_segment_MD5_SHA_and_all_failure_modes(self):
        payload = b'first'+b'second'
        parts = [dict(bytes=len(s),md5=hashlib.md5(s).hexdigest()) for s in [b'first',b'second']]
        sink = io.BytesIO()
        r = verify_segments(io.BytesIO(payload),parts,sink)
        self.assertEqual(sink.getvalue(),payload)
        self.assertEqual(r['sha256'],hashlib.sha256(payload).hexdigest())
        for value in [payload[:-1],payload+b'x',b'FIRSTsecond']:
            with self.assertRaises(ValueError):verify_segments(io.BytesIO(value),parts,io.BytesIO())

    def test_actual_paired_interleaved_gzip_and_malformed_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rng = random.Random(1)
            dna = [''.join(rng.choices('ACGT',k=1000)) for _ in range(4)]
            interleaved,left,right = reads(root,dna)
            self.assertEqual(list(fastq_pairs(interleaved)),list(fastq_pairs(left,right)))
            self.assertEqual(read_profile(interleaved),150)
            bad = root/'bad.fq'
            bad.write_text('@x/2\nACGT\n+\nIIII\n@x/1\nACGT\n+\nIIII\n')
            with self.assertRaisesRegex(ValueError,'Mismatched/swapped'):list(fastq_pairs(bad))
            bad.write_text('@x/1\nACGT\n+\nIII\n')
            with self.assertRaisesRegex(ValueError,'Malformed'):list(fastq_pairs(bad))
            bad.write_text('@x/1\nACGT \n+\nIIII \n@x/2\nACGT\n+\nIIII\n')
            with self.assertRaisesRegex(ValueError,'Malformed'):list(fastq_pairs(bad))
            broken = root/'broken.fq.gz'
            broken.write_bytes(interleaved.read_bytes()[:-5])
            with self.assertRaises((EOFError,gzip.BadGzipFile)):list(fastq_pairs(broken))

    def test_CIGAR_full_denominator_filters_zero_and_exact_native_depth(self):
        header = '@HD\tVN:1.6\tSO:unsorted\n@SQ\tSN:q\tLN:100\n@SQ\tSN:zero\tLN:10\n'
        def row(q,flag,pos,mq,cigar,seq):
            return f'{q}\t{flag}\tq\t{pos}\t{mq}\t{cigar}\t*\t0\t0\t{seq}\t'+('I'*len(seq))+'\n'
        sam = header+row('a',0,1,60,'2S4=1X2D3M1I','A'*11)+row('b',0,5,60,'10M','A'*10)
        sam += row('low',0,1,0,'10M','A'*10)+row('secondary',256,1,60,'10M','A'*10)
        sam += row('supp',2048,1,60,'10M','A'*10)+row('duplicate',1024,1,60,'10M','A'*10)
        sums,counts,hist = sum_sam(io.StringIO(sam),['q','zero'],[100,10])
        self.assertEqual(list(sums),[18,0])
        self.assertEqual(counts['accepted_alignments'],2)
        self.assertEqual(hist[0],1)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'in.sam').write_text(sam)
            subprocess.run([str(SAMTOOLS),'sort','-@','0','-o',str(root/'in.bam'),str(root/'in.sam')],check=True,capture_output=True)
            r = subprocess.check_output([str(SAMTOOLS),'depth','-aa','-q','0','-Q','20','-G',str(0xF04),str(root/'in.bam')],text=True)
            self.assertEqual(sum(int(line.split('\t')[2]) for line in r.splitlines()),18)
        unknown = header+row('unknown',0,1,255,'10M','A'*10)
        self.assertEqual(sum_sam(io.StringIO(unknown),['q','zero'],[100,10])[1]['excluded_MAPQ'],1)
        for malformed in [sam.replace('4=1X','4Z1X'),sam.replace('LN:100','LN:101'),sam.replace('2S4=','99S4=')]:
            with self.assertRaises(ValueError):sum_sam(io.StringIO(malformed),['q','zero'],[100,10])

    def test_real_mapper_index_interleaved_multimapper_and_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            u,dna = fixture(root)
            raw,left,right = reads(root,dna)
            # Mapping must retain SQ/zero rows even for below-seed and all-N DNA.
            reference=root/'mapping-reference.fna'
            reference.write_text(u['reference'].read_text()+'>tiny\nACGT\n>unknown-DNA\nNNNNNNNN\n')
            subprocess.run([str(MAPPER),'--create-index','-t','2','-r','150',str(reference)],check=True,capture_output=True)
            a = map_summary(MAPPER,reference,raw,root/'mapped',sample=6)
            b = map_summary(MAPPER,reference,left,root/'paired',second=right,sample=6)
            self.assertEqual((root/'mapped/depth.tsv').read_bytes(),(root/'paired/depth.tsv').read_bytes())
            self.assertEqual(a['feeder']['reads'],8)
            self.assertGreater(a['counters']['accepted_alignments'],0)
            self.assertGreater(a['counters']['excluded_MAPQ'],0)
            self.assertGreater(a['zero_rows'],0)
            self.assertEqual(a['reference'],binding(reference))
            self.assertEqual(a['rows'],9)
            self.assertTrue((root/'mapped/depth.tsv').read_text().endswith('tiny\t0\t4\t0\nunknown-DNA\t0\t8\t0\n'))
            self.assertEqual(b['mapper_exit'],0)

    def test_actual_primary_BAM_roundtrip_preserves_frozen_means_and_can_sort(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);u,dna=fixture(root);raw,_,_=reads(root,dna)
            native=map_summary(MAPPER,u['reference'],raw,root/'base',use_index=False,sample=6)
            bam=root/'retained.bam'
            retained=map_summary(MAPPER,u['reference'],raw,root/'backed',use_index=False,sample=6,
                bam_retention=dict(samtools=SAMTOOLS,destination=bam,cap=1024**2))
            self.assertEqual((root/'base/depth.tsv').read_bytes(),(root/'backed/depth.tsv').read_bytes())
            self.assertEqual(native['counters'],retained['counters'])
            self.assertTrue(retained['retained_alignment']['full_readback_verified'])
            sam=subprocess.check_output([str(SAMTOOLS),'view','-h',str(bam)],text=True)
            totals,counts,_=sum_sam(sam.splitlines(True),*axis(u['reference']),paired=True)
            self.assertEqual(counts,retained['counters'])
            ordered=root/'sorted.bam'
            subprocess.run([str(SAMTOOLS),'sort','-@','0','-m','1M','-o',str(ordered),str(bam)],check=True,capture_output=True)
            subprocess.run([str(SAMTOOLS),'index',str(ordered)],check=True,capture_output=True)
            self.assertTrue(ordered.with_suffix('.bam.bai').is_file())
            with self.assertRaises(Exception):
                map_summary(MAPPER,u['reference'],raw,root/'capped',use_index=False,
                    bam_retention=dict(samtools=SAMTOOLS,destination=root/'cap.bam',cap=1))
            self.assertFalse((root/'capped/done.json').exists())

    def test_actual_BAM_external_transport_write_once_and_corrupt_readback_refused(self):
        from e024_alignment import BamRetention
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);u,dna=fixture(root);raw,_,_=reads(root,dna)
            remote=root/'object.bam';cli=root/'cloud-transport'
            script='#!'+sys.executable+'\nimport sys\nfrom pathlib import Path\np=Path('+repr(str(remote))+')\na=sys.argv[1:]\nif a[:2]==["storage","cp"]:\n assert a[2]=="--if-generation-match=0" and a[3]=="-"\n with p.open("xb") as f:\n  while b:=sys.stdin.buffer.read(65536):f.write(b)\nelif a[:2]==["storage","cat"]:sys.stdout.buffer.write(p.read_bytes())\nelse:raise SystemExit(8)\n'
            cli.write_text(script);cli.chmod(0o700)
            options=dict(samtools=SAMTOOLS,destination='gs://dl-binner-archive-167650584170/e024/tiny-only/6.bam',cap=1024**2,gcloud=str(cli))
            value=map_summary(MAPPER,u['reference'],raw,root/'remote',use_index=False,sample=6,bam_retention=options)
            self.assertEqual(value['retained_alignment']['sha256'],binding(remote)['sha256'])
            with self.assertRaises(Exception):
                map_summary(MAPPER,u['reference'],raw,root/'overwrite',use_index=False,sample=6,bam_retention=options)
            remote.unlink();cli.write_text(script.replace('p.read_bytes())','p.read_bytes()[:-5])'))
            with self.assertRaisesRegex(ValueError,'readback'):
                map_summary(MAPPER,u['reference'],raw,root/'corrupt',use_index=False,sample=6,bam_retention=options)
            self.assertFalse((root/'corrupt/done.json').exists())

    def test_actual_public_segment_transport_without_aggregate_GET(self):
        import functools,http.server,threading
        from e024_coverage import acquire
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);public=root/'public';public.mkdir();payload=b'precise generated segmented bytes'*123
            pieces=[payload[:1000],payload[1000:]];seen=[]
            for j,b in enumerate(pieces):(public/str(j)).write_bytes(b)
            class Handler(http.server.SimpleHTTPRequestHandler):
                def log_message(self,*a):pass
                def do_GET(self):
                    seen.append(self.path)
                    if self.path=='/aggregate':self.send_error(401);return
                    if self.path=='/corrupt':self.send_error(401);return
                    return super().do_GET()
                def end_headers(self):
                    if self.path in ['/0','/1']:
                        self.send_header('ETag',hashlib.md5(pieces[int(self.path[1:])]).hexdigest())
                    super().end_headers()
            server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(public)))
            worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
            try:
                base='http://127.0.0.1:'+str(server.server_port)
                parts=[dict(url=base+'/'+str(j),bytes=len(b),md5=hashlib.md5(b).hexdigest()) for j,b in enumerate(pieces)]
                record=dict(sample=6,url=base+'/aggregate',bytes=len(payload),segments=parts,
                    DLO_aggregate_md5=hashlib.md5(''.join(p['md5'] for p in parts).encode()).hexdigest())
                value=acquire(record,root/'exact')
                self.assertEqual((root/'exact').read_bytes(),payload)
                self.assertEqual(value['sha256'],hashlib.sha256(payload).hexdigest())
                self.assertEqual(seen,['/0','/1'])
                record['segments'][1]['url']=base+'/corrupt'
                with self.assertRaises(Exception):acquire(record,root/'partial')
                self.assertEqual((root/'partial').read_bytes(),pieces[0])
                self.assertFalse((root/'partial.acquired.json').exists())
            finally:server.shutdown();server.server_close();worker.join(5)

    def test_stream_failure_never_seals_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            u,dna = fixture(root)
            raw,_,_ = reads(root,dna)
            bad = root/'bad.fq.gz'
            bad.write_bytes(raw.read_bytes()[:-5])
            with self.assertRaisesRegex(RuntimeError,'FASTQ/count contract'):
                map_summary(MAPPER,u['reference'],bad,root/'failed',use_index=False)
            self.assertFalse((root/'failed/done.json').exists())
            self.assertTrue((root/'failed/failed.json').exists())

    def test_ordered_combine_missing_and_changed_summary_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ref = root/'ref.fna'
            ref.write_text('>opaque\nACGT\n>zero\nAAAA\n')
            matrix = matrix_fixture(root,ref)
            self.assertEqual(matrix.read_text().splitlines()[0].split('\t')[1:],[f'oral_sample_{s}' for s in SAMPLES])
            with self.assertRaisesRegex(ValueError,'ordered ten'):combine(ref,[],SAMPLES[::-1],root/'bad.tsv')
            (root/'6/depth.tsv').write_text('bad')
            with self.assertRaisesRegex(ValueError,'provenance'):combine(ref,[root/str(s)/'depth.tsv' for s in SAMPLES],SAMPLES,root/'bad.tsv')

    def test_cleanup_only_verified_new_raw_and_strict_completed_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root/'raw.fq.gz'; raw.write_bytes(b'generated')
            write(root/'acquired.json',dict(**binding(raw),manifest={'synthetic':True}))
            mapped = root/'mapped';mapped.mkdir()
            (mapped/'depth.tsv').write_text('verified fixture')
            write(mapped/'done.json',dict(status='PASS',mapper_exit=0,reads=binding(raw),depth=binding(mapped/'depth.tsv'),retained_alignment=dict(full_readback_verified=True)))
            with self.assertRaises(ValueError):cleanup_read(root/'other.gz',root/'acquired.json',mapped/'done.json')
            cleanup_read(raw,root/'acquired.json',mapped/'done.json')
            self.assertFalse(raw.exists())
            # Seal a new enclosing stage, not the writer's immutable done.json.
            seal(root)
            verify_seal(root)
            (mapped/'depth.tsv').write_text('corrupt')
            with self.assertRaisesRegex(ValueError,'Changed/missing'):verify_seal(root)

    def test_passed_download_is_verified_without_recopy_and_missing_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);d=root/'downloads/6';d.mkdir(parents=True)
            raw=d/'raw.fq.gz';raw.write_bytes(b'fixture')
            record=dict(sample=6,bytes=7,url='https://not-called.invalid/',segments=[dict(bytes=7,md5=hashlib.md5(b'fixture').hexdigest())])
            write(d/'raw.fq.gz.acquired.json',dict(**binding(raw),manifest=record,publisher_segment_MD5_passed=1))
            self.assertTrue(acquire_one(root,record)['reused_without_download'])
            raw.unlink()
            with self.assertRaises(ValueError):acquire_one(root,record)


class Information(unittest.TestCase):
    def test_rebind_actual_cache_graph_choices_export_reload_and_collection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            work = root/'work';work.mkdir()
            u,_ = fixture(work)
            summary = root/'summary';summary.mkdir()
            matrix = matrix_fixture(summary,u['reference'])
            before = {k:binding(v) for k,v in u.items()}
            r = rebind(u['features'],u['views'],u['embeddings'],matrix,u['reference'],work/'rebound')
            self.assertTrue(r['native_vector_bytes_unchanged'])
            data,v,valid,_,_ = load_rebound(work/'rebound/rebind.json')
            self.assertEqual(int((data['depth'] == 0).all(1).sum()),1)
            run(work/'rebound/rebind.json',u['graph'],u['marker_evidence'],work/'group',CFG)
            proof=audit(work/'rebound/rebind.json',u['graph'],u['marker_evidence'],work/'group',CFG)
            self.assertEqual(proof['status'],'PASS')
            (work/'audited').mkdir();write(work/'audited/done.json',dict(proof=proof))
            from dl_binner.information.export import export
            for arm in ['density','selected']:
                value = export(work/'rebound/features.npz',work/'group'/(arm+'-partition.json'),u['reference'],work/arm,include_dna=True)
                self.assertEqual(value['bp'],int(data['lengths'].sum()))
            self.assertEqual(before,{k:binding(v) for k,v in u.items()})
            evidence=root/'evidence';evidence.mkdir();(evidence/'note.json').write_text('{"synthetic":true}')
            result=pack(work,evidence,root/'return')
            self.assertTrue(result['every_member_verified'])
            self.assertGreater(len(result['omitted_retained_on_disk']),0)
            from e024_review import contracts
            write(root/'review-admission.json',dict(provider_status='TERMINATED',archive_and_every_member_verified=True,
                cost_and_retention_admitted=True,workflow_completed=True,scope='synthetic local contract only'))
            _,restored,meta,_=contracts(work,root/'return/inventory.json',root/'review-admission.json')
            self.assertEqual(len(restored['ids']),7)
            self.assertEqual(len(meta['samples']),10)
            (work/'rebound/features.npz').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'Corrupt/missing'):load_rebound(work/'rebound/rebind.json')

    def test_exact_no_depth_path_and_observed_depth_candidate_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            u,_ = fixture(root)
            data,v,valid,_ = old.load_inputs(u['features'],u['embeddings'])
            graph,_ = old.sparse_input(u['graph'],data['ids'].tolist(),valid,u['embeddings'])
            a = old.candidates(data,v,valid,graph,CFG,4)
            b = candidates(data,v,valid,graph,CFG,4)
            self.assertTrue(all(np.array_equal(x,y) for x,y in zip(a[:3],b[:3])))
            self.assertEqual(a[3],b[3])
            with_depth = dict(data,depth=np.array([[10.,1.],[1.,10.],[10.,1.],[1.,10.],[0.,0.],[1.,10.],[0.,0.]],np.float32),
                              depth_evidence=np.array([1,1,1,1,0,1,0],bool))
            c = candidates(with_depth,v,valid,graph,CFG,4)
            self.assertEqual(c[3]['final_composite_recall'],1.)
            self.assertFalse(np.array_equal(b[2],c[2]))

    def test_actual_NNDescent_path_at_forced_tiny_engineering_crossover(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);u,_=fixture(root)
            data,v,valid,_=old.load_inputs(u['features'],u['embeddings'])
            graph,_=old.sparse_input(u['graph'],data['ids'].tolist(),valid,u['embeddings'])
            data=dict(data,depth=np.array([[1,10],[10,1],[2,9],[9,2],[3,8],[8,3],[0,0]],np.float32),
                      depth_evidence=np.array([1,1,1,1,1,1,0],bool))
            # Only the engineering crossover is forced; the native policy and
            # community plan still have exact_threshold=2048, no grid or tuning.
            cfg=dict(CFG,exact_threshold=4)
            result=candidates(data,v,valid,graph,cfg,4)
            self.assertIn('NNDescent',result[3]['depth_retrieval']['mode'])
            self.assertEqual(result[3]['final_composite_recall'],1.)

    def test_collection_compressed_limit_and_symlink_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);work=root/'work';work.mkdir();evidence=root/'evidence';evidence.mkdir()
            (work/'x.tsv').write_bytes(bytes(range(256))*100)
            with self.assertRaises(Exception):pack(work,evidence,root/'small',ceiling=100)
            (work/'link.tsv').symlink_to(work/'x.tsv')
            with self.assertRaisesRegex(ValueError,'links'):pack(work,evidence,root/'link-return')


if __name__ == '__main__':
    unittest.main()
