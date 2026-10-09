"""Self-contained E009 adapter/failure regressions; no ignored assets or scientific fits.

Native real-DNA integration is a separately retained local receipt. These tests
exercise contracts and process cleanup, not tool quality or Linux feasibility.
"""
import contextlib
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
import zipfile

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e009_common import acquire,binding,extract,fasta,write_json
from e009_data import canonical_dna,combine_depth,competitive_reference,partition,source_catalog,validate_fastq_pair
from e009_native import cpu_plan,prepare_bam_directory
from e009_hmm import budget_args
from e009_owner import collect,supervisor,verify_bundle
from e009_truth import construct,parse_paf,reconcile,recovery,union


class E009Contracts(unittest.TestCase):
    """Check source, axes, truth and native failure behavior on new temporary inputs."""
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='e009-test-')
        self.addCleanup(self.temp.cleanup);self.p=Path(self.temp.name)

    def put(self,name,text):
        """Write one new fixture file and return its explicit path."""
        path=self.p/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text);return path

    def archive(self,name,members):
        """Create a tiny archive with explicit member types for extraction checks."""
        path=self.p/name
        with tarfile.open(path,'w:gz') as out:
            for ident,value,kind in members:
                item=tarfile.TarInfo(ident);item.type=kind;item.size=len(value)
                if kind==tarfile.SYMTYPE:item.linkname='../../outside';item.size=0
                out.addfile(item,io.BytesIO(value) if kind==tarfile.REGTYPE else None)
        return path

    def test_extraction_traversal_link_and_duplicate_refusal(self):
        for i,members in enumerate([
            [('../escape',b'x',tarfile.REGTYPE)],
            [('root/link',b'',tarfile.SYMTYPE)],
            [('root/a',b'x',tarfile.REGTYPE),('root/a',b'y',tarfile.REGTYPE)],
        ]):
            with self.subTest(i=i),self.assertRaises(ValueError):
                extract(self.archive(f'{i}.tar.gz',members),self.p/f'out{i}')
            self.assertFalse((self.p/f'out{i}').exists())

    def test_zip_and_size_bound_and_exact_reuse(self):
        archive=self.p/'safe.zip'
        with zipfile.ZipFile(archive,'w') as out:out.writestr('root/a.txt','abc')
        with self.assertRaisesRegex(ValueError,'declared space'):extract(archive,self.p/'large',max_bytes=2)
        result=extract(archive,self.p/'ok',strip_root=True)
        self.assertEqual(result['logical_bytes'],3);self.assertEqual((self.p/'ok/a.txt').read_text(),'abc')
        with self.assertRaisesRegex(ValueError,'fresh'):extract(archive,self.p/'ok')

    def test_acquisition_hash_explicit_resume_and_corruption(self):
        src=self.put('remote','abcdef');spec={'url':src.as_uri(),**binding(src)};dest=self.p/'received'
        result=acquire(spec,dest)
        self.assertTrue(result['publisher_checksum_verified']);self.assertFalse(result['admitted_scientific_input'])
        with self.assertRaisesRegex(ValueError,'explicit resume'):acquire(spec,dest)
        self.assertEqual(acquire(spec,dest,resume=True),result)
        dest.write_text('broken')
        with self.assertRaisesRegex(ValueError,'bytes/spec'):acquire(spec,dest,resume=True)

    def test_bad_download_retains_partial_and_provisional_is_not_admitted(self):
        src=self.put('remote','abcdef');spec={'url':src.as_uri(),'bytes':6,'sha256':'0'*64}
        with self.assertRaisesRegex(ValueError,'SHA256'):acquire(spec,self.p/'bad')
        self.assertTrue((self.p/'bad.partial').exists());self.assertFalse((self.p/'bad').exists())
        with self.assertRaisesRegex(ValueError,'partial download'):acquire(spec,self.p/'bad')
        value=acquire({'url':src.as_uri(),'bytes':6,'sha256':None},self.p/'provisional')
        self.assertFalse(value['publisher_checksum_verified']);self.assertFalse(value['admitted_scientific_input'])

    def test_fasta_and_mate_failure_contracts(self):
        a=self.put('a.fq','@r/1\nACGT\n+\nIIII\n');b=self.put('b.fq','@r/2\nTGCA\n+\nIIII\n')
        self.assertEqual(validate_fastq_pair(a,b)['pairs'],1)
        self.assertEqual(validate_fastq_pair(self.put('inter.fq',a.read_text()+b.read_text()))['bp'],8)
        b.write_text('@other/2\nTGCA\n+\nIIII\n')
        with self.assertRaisesRegex(ValueError,'mate'):validate_fastq_pair(a,b)
        b.write_text('@r/2\nTGCA\n+\nIII\n')
        with self.assertRaisesRegex(ValueError,'truncated'):validate_fastq_pair(a,b)
        with self.assertRaisesRegex(ValueError,'duplicate'):list(fasta(self.put('bad.fa','>same\nACG\n>same\nACT\n')))

    def test_source_catalog_and_reference_identity(self):
        source=self.p/'sources';source.mkdir();seq='ACGTRYSWKMBDHVN'
        self.put('sources/a.fna','>NC_000001.1\n'+seq+'\n');self.put('sources/b.fna','>NC_000001.1\n'+seq+'\n')
        catalog=source_catalog(source,{'accessions':['NC_000001.1'],'canonical_replicon_sha256s':[canonical_dna(seq)]},self.p/'catalog.json')
        self.assertTrue(all(x['development_exact_replicon_match'] for x in catalog['files'][0]['replicons']))
        axis=competitive_reference(catalog,{'a.fna','b.fna'},self.p/'reference.fa')
        self.assertEqual(len(axis),2);self.assertEqual(len({x['genome'] for x in axis.values()}),2)
        self.assertEqual(len({x['original_replicon_id'] for x in axis.values()}),1)
        self.put('sources/a.fna','>NC_000001.1\nACG\n')
        with self.assertRaisesRegex(ValueError,'bytes changed'):competitive_reference(catalog,{'a.fna'},self.p/'changed.fa')

    def test_depth_order_zeros_and_corruption(self):
        ref=self.put('ref.fa','>z\nACG\n>a\nACT\n');paths=[]
        for col,data in [('sample0',[0,2]),('sample1',[3,0])]:
            p=self.put(col+'.tsv',f'contig_id\t{col}\nz\t{data[0]}\na\t{data[1]}\n');paths.append(p)
            write_json(p.with_suffix('.receipt.json'),{'column':col,'reference':binding(ref),'output':binding(p)})
        combine_depth(ref,['sample0','sample1'],paths,self.p/'matrix.tsv')
        self.assertEqual((self.p/'matrix.tsv').read_text(),'contig_id\tsample0\tsample1\nz\t0\t3\na\t2\t0\n')
        with self.assertRaisesRegex(ValueError,'column'):combine_depth(ref,['sample1','sample0'],paths,self.p/'swapped.tsv')
        paths[0].write_text(paths[0].read_text().replace('z\t0','z\t1'))
        with self.assertRaisesRegex(ValueError,'bytes'):combine_depth(ref,['sample0','sample1'],paths,self.p/'changed.tsv')

    def test_native_partitions_are_complete_and_refuse_silent_repairs(self):
        ref=self.put('assembly.fa','>z\nACG\n>a\nACT\n>x\nATG\n')
        good=self.put('bin.fa','>z\nACG\n');res=partition(ref,[good],{'z','a'},self.p/'partition.tsv')
        self.assertEqual(res,{'assigned':1,'unassigned':1,'excluded':1})
        with (self.p/'partition.tsv').open() as stream:rows=list(csv.DictReader(stream,delimiter='\t'))
        self.assertEqual([r['contig_id'] for r in rows],['z','a','x'])
        for i,text in enumerate(['>z\nATG\n','>unknown\nACG\n','>x\nATG\n']):
            with self.subTest(i=i),self.assertRaises(ValueError):partition(ref,[self.put(f'bad{i}.fa',text)],{'z','a'},self.p/f'bad{i}.tsv')
        with self.assertRaisesRegex(ValueError,'Duplicate'):partition(ref,[good,self.put('duplicate.fa','>z\nACG\n')],{'z','a'},self.p/'dup.tsv')
        self.assertEqual(partition(ref,[],{'z','a'},self.p/'empty.tsv')['unassigned'],2)
        with self.assertRaisesRegex(ValueError,'unknown'):partition(ref,[],{'ghost'},self.p/'ghost.tsv')

    def paf(self,q,qlen,start,end,strand,r,rl,start_r,end_r,cigar,matches,columns):
        """Build a strict eqx PAF row with explicit endpoints, never inferred labels."""
        return '\t'.join(map(str,[q,qlen,start,end,strand,r,rl,start_r,end_r,matches,columns,0]))+'\tcg:Z:'+cigar+'\n'

    def test_reverse_indels_coordinate_consumption(self):
        rows=self.paf('reverse',300,0,300,'-','r',1000,100,400,'300=',300,300)
        rows+=self.paf('insert',301,0,301,'+','r',1000,100,400,'150=1I150=',300,301)
        rows+=self.paf('delete',300,0,300,'+','r',1000,100,401,'150=1D150=',300,301)
        blocks,_=parse_paf(self.put('truth.paf',rows),{'reverse':300,'insert':301,'delete':300},{'r':{'length':1000,'genome':'A'}})
        result=reconcile({'reverse':300,'insert':301,'delete':300},blocks)
        self.assertEqual(result['reverse']['source_intervals'],{'r':[[100,400]]})
        self.assertEqual(result['insert']['unsupported_query_bp'],1)
        self.assertEqual(result['delete']['source_intervals'],{'r':[[100,250],[251,401]]})

    def test_competing_genomes_repeats_and_duplicate_loci(self):
        def block(r,g,r0=0):return {'q0':0,'q1':300,'r0':r0,'r1':r0+300,'rid':r,'genome':g,'strand':'+'}
        a=block('r','A')
        result=reconcile({'cross':300,'repeat':300,'duplicate':300},
                         {'cross':[a,block('s','B')],'repeat':[a,block('r','A',400)],'duplicate':[a,a]})
        self.assertIsNone(result['cross']['AMBER_label']);self.assertEqual(result['cross']['ambiguous_query_bp'],300)
        self.assertEqual(result['repeat']['AMBER_label'],'A');self.assertEqual(result['repeat']['source_intervals'],{})
        self.assertEqual(result['repeat']['repeat_locus_query_bp'],300)
        self.assertEqual(result['duplicate']['source_intervals'],{'r':[[0,300]]})

    def test_truth_malformed_low_quality_rows_fail_and_axis_order_survives_json(self):
        ref={'r':{'length':1000,'genome':'A'}}
        for i,row in enumerate([
            self.paf('z',300,0,300,'+','r',1000,100,399,'300=',300,300),
            self.paf('z',300,0,300,'+','r',1000,100,400,'300=',1,300),
            self.paf('z',300,0,300,'?','r',1000,100,400,'300=',300,300),
        ]):
            with self.subTest(i=i),self.assertRaises(ValueError):parse_paf(self.put(f'bad{i}.paf',row),{'z':300},ref)
        query=self.put('query.fa','>z\n'+'A'*300+'\n>a\n'+'C'*300+'\n')
        paf=self.put('good.paf',self.paf('z',300,0,300,'+','r',1000,100,400,'300=',300,300))
        construct(query,paf,ref,self.p/'truth')
        self.assertEqual(json.loads((self.p/'truth/truth.json').read_text())['ordered_contig_ids'],['z','a'])

    def test_recovery_all_bin_dna_and_full_reference_denominators(self):
        item={'length':300,'confirmed_query_bp':{'A':300},'source_intervals':{'r':[[0,300]]}}
        unknown={'length':100,'confirmed_query_bp':{},'source_intervals':{}}
        contigs={'one':item,'dup':item,'noise':unknown};refs={'r':{'genome':'A','length':1000},'s':{'genome':'B','length':1000}}
        result=recovery(contigs,{'one':'bin','dup':'bin','noise':None},refs,{'A':1000,'B':1000},['A','B'],min_bin=0)
        self.assertEqual(result[0]['whole_reference_R95'],.3);self.assertEqual(result[1]['whole_reference_R95'],0)
        contaminated=recovery(contigs,dict.fromkeys(contigs,'bin'),refs,{'A':1000},['A'],min_bin=0)
        self.assertEqual(contaminated[0]['recovered_bp'],0)
        self.assertEqual(union([[0,300],[0,300],[200,400]]),[[0,400]])

    def test_resource_child_accounting(self):
        for tool in ('comebin','scgbinner','completebin','metacat','semibin'):
            plan=cpu_plan(tool,8);self.assertEqual(plan['loader_workers'],0);self.assertLess(plan['pool_workers'],8)
        self.assertEqual(cpu_plan('completebin',8)['pool_workers'],6)
        with self.assertRaises(ValueError):cpu_plan('comebin',3)
        self.assertEqual(budget_args(['--cpu','1','db','proteins']),(['--cpu','0','db','proteins'],1))
        self.assertEqual(budget_args(['--cpu','8','db','proteins'])[0][1],'7')
        self.assertEqual(budget_args(['-h']),(['-h'],None))
        with self.assertRaisesRegex(ValueError,'Explicit'):budget_args(['db','proteins'])

    def test_bundle_exact_bytes_and_no_extras(self):
        packet=self.p/'packet';packet.mkdir();p=self.put('packet/a','test')
        write_json(packet/'bundle-manifest.json',{'source_commit':'test-only','files':{'a':binding(p)}})
        self.assertEqual(verify_bundle(packet)['source_commit'],'test-only')
        p.write_text('altered')
        with self.assertRaisesRegex(ValueError,'bytes changed'):verify_bundle(packet)
        self.put('packet/extra','x')
        with self.assertRaisesRegex(ValueError,'file set'):verify_bundle(packet)

    def test_comebin_directory_follows_resolved_order_not_alias_names(self):
        first=self.put('first/sample0.bam','software-contract');second=self.put('last/sample1.bam','software-contract')
        prepare_bam_directory(self.p/'bams',[first,second])
        self.assertEqual((self.p/'bams/sample_0.bam').resolve(),first.resolve())
        with self.assertRaisesRegex(ValueError,'ordering'):prepare_bam_directory(self.p/'wrong',[second,first])
        duplicate=self.put('other/sample0.bam','different')
        with self.assertRaisesRegex(ValueError,'basenames'):prepare_bam_directory(self.p/'duplicate',[first,duplicate])

    def test_collector_binds_immutable_archive_log_and_inventory(self):
        attempt=self.p/'attempt';attempt.mkdir();transfer=self.p/'transfer';transfer.mkdir()
        self.put('attempt/terminal.log','exact snapshot\n');self.put('attempt/status.json','{}\n')
        with contextlib.redirect_stdout(io.StringIO()):receipt=collect(attempt,transfer)
        with tarfile.open(receipt['archive']) as archive:
            members=archive.getmembers();self.assertEqual(sum(m.size for m in members),receipt['retained_logical_bytes'])
            self.assertEqual(archive.extractfile('attempt/terminal.log').read(),b'exact snapshot\n')
            self.assertIn('attempt/retained-files.json',[m.name for m in members])
        self.assertEqual(binding(receipt['archive']),receipt['file'])

    def assert_stopped(self,pid):
        """Require absence of live child work; an unreaped zombie is not a running orphan."""
        probe=subprocess.run(['ps','-p',str(pid),'-o','stat='],text=True,capture_output=True)
        self.assertIn(probe.returncode,(0,1));state=probe.stdout.strip()
        self.assertTrue(not state or state.startswith('Z'),state)

    def test_fatal_trace_hang_stops_promptly_and_cleans_orphan(self):
        native=self.put('fatal.py',"import subprocess,sys,time\nfrom pathlib import Path\np=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'])\nPath(sys.argv[1]).write_text(str(p.pid))\nprint('Traceback (most recent call last):',flush=True)\nprint('ValueError: intended fatal fixture',flush=True)\ntime.sleep(60)\n")
        caller=self.put('caller.py',f"import sys\nsys.path.insert(0,{str(ROOT/'scripts')!r})\nfrom e009_data import run_native\nrun_native([sys.executable,'-B',{str(native)!r},{str(self.p/'pid')!r}],{str(self.p/'native.log')!r})\n")
        sup=supervisor();started=time.monotonic()
        with self.assertRaisesRegex(RuntimeError,'fatal Python traceback'):
            sup.supervise([sys.executable,'-B',caller],self.p/'fatal.log',15,8_000_000_000,sup.isolated_env(4))
        self.assertLess(time.monotonic()-started,12);self.assert_stopped(int((self.p/'pid').read_text()))
        inner=json.loads((self.p/'native.log.exit.json').read_text());self.assertIn('fatal Python traceback',inner['error'])
        self.assertNotEqual(inner['exit_code'],0)

    def test_timeout_and_rss_report_intended_limits(self):
        sup=supervisor()
        for name,code,seconds,ram,reason in [
            ('timeout','import time; time.sleep(60)',.5,8_000_000_000,'TimeoutError'),
            ('rss','import time; a=bytearray(80_000_000); time.sleep(60)',5,40_000_000,'MemoryError'),
        ]:
            with self.subTest(name=name),self.assertRaisesRegex(RuntimeError,reason):
                sup.supervise([sys.executable,'-B','-c',code],self.p/(name+'.log'),seconds,ram,sup.isolated_env(4))
            receipt=json.loads((self.p/(name+'.exit.json')).read_text())
            self.assertIn(reason,receipt['stop_reason']);self.assert_stopped(receipt['launched_pid'])


if __name__=='__main__':unittest.main()
