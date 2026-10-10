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
from e009_native import cpu_plan,prepare_bam_directory,validate_comebin_contigs
from e009_hmm import budget_args
from e009_startup import startup_argv,supervise_startup,wait_snapshot,StartupProgress,progress_signature,source_cache_argv
from e009_owner import collect,supervisor,verify_bundle,verify_readonly_after,run_stage,python_wrapper,readonly_inputs,bind_readonly_files
from e009_common import tree_binding
from e009_truth import construct,parse_paf,reconcile,recovery,union
from e009_snapshot import create as create_snapshot, restore as restore_snapshot, verify as verify_snapshot
from e009_materialize import materialize,plan as runtime_plan,restore_accepted,digest_json
from e009_startup import supervise_work


class E009Contracts(unittest.TestCase):
    """Check source, axes, truth and native failure behavior on new temporary inputs."""
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='e009-test-')
        self.addCleanup(self.temp.cleanup);self.p=Path(self.temp.name)

    def put(self,name,text):
        """Write one new fixture file and return its explicit path."""
        path=self.p/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text);return path

    def accepted_fixture(self):
        """Create actual sealed bytes and the reviewed-acceptance anchor for restore tests."""
        self.put('original/lib/module.py','retained source\n')
        m=materialize(self.p/'original',self.p/'first',self.p/'state',self.p/'first.json')
        return {'snapshot':{'state':str(self.p/'state'),'receipt_file':binding(self.p/'state/snapshot.json'),
            'source_prefix':m['source_prefix'],'shards':m['shards'],'files':len(m['files']),
            'logical_bytes':m['logical_bytes']}}

    def test_accepted_restore_never_accesses_original_and_keeps_state_immutable(self):
        anchor=self.accepted_fixture();before=tree_binding(self.p/'state')
        (self.p/'original').rename(self.p/'original-unavailable')
        restore_accepted(anchor,self.p/'restored',self.p/'restored.json')
        obs=json.loads((self.p/'restored.json').read_text())
        self.assertEqual(obs['source_copied_entries'],0);self.assertEqual(obs['restored_entries'],1)
        self.assertFalse(obs['original_source_accessed']);self.assertEqual(tree_binding(self.p/'state'),before)
        self.assertEqual((self.p/'restored/lib/module.py').read_bytes(),(self.p/'first/lib/module.py').read_bytes())

    def test_accepted_restore_refuses_receipt_seal_missing_chunk_and_corruption(self):
        for case in ('receipt','seal','missing','corrupt'):
            with self.subTest(case=case):
                import shutil
                for name in ('original','first','state'):
                    if (self.p/name).exists():shutil.rmtree(self.p/name)
                if (self.p/'first.json').exists():(self.p/'first.json').unlink()
                a=self.accepted_fixture();shard=a['snapshot']['shards'][0]
                if case=='receipt':(self.p/'state/snapshot.json').write_text('{}')
                elif case=='seal':(self.p/'state'/shard['receipt']).write_text('{}')
                elif case=='missing':(self.p/'state'/shard['archive']['name']).unlink()
                else:
                    with (self.p/'state'/shard['archive']['name']).open('r+b') as f:f.seek(-1,2);f.write(b'X')
                with self.assertRaises((ValueError,KeyError,FileNotFoundError)):
                    restore_accepted(a,self.p/('restore-'+case),self.p/(case+'.json'))

    def test_python_wrapper_keeps_lexical_venv_cache_policy_and_forwarded_args(self):
        import venv
        venv.EnvBuilder(with_pip=False).create(self.p/'venv')
        python=self.p/'venv/bin/python';script=self.put('probe.py',
            "import json,sys;print(json.dumps({'prefix':sys.prefix,'lexical':sys.executable,'cache':sys.pycache_prefix,'no_writes':sys.dont_write_bytecode,'args':sys.argv[1:]}))\n")
        wrapper=self.p/'wrapper';python_wrapper(wrapper,python,script,['fixed'],{'E009_SOURCE_CACHE_ROOT':str(self.p/'cache')})
        r=json.loads(subprocess.check_output([wrapper,'forwarded with space'],text=True))
        self.assertEqual(r['prefix'],str(self.p/'venv'));self.assertEqual(r['lexical'],str(python))
        self.assertEqual(r['cache'],str(self.p/'cache'));self.assertTrue(r['no_writes'])
        self.assertEqual(r['args'],['fixed','forwarded with space'])

    def test_native_activity_ignores_short_stage_cap_and_stops_sleeper_or_fatal(self):
        sup=supervisor();env=sup.isolated_env(1);policy={'native_activity':True,'startup_idle_seconds':.5}
        busy=self.put('busy.py','import time\nend=time.monotonic()+1.3\nwhile time.monotonic()<end: x=sum(range(1000))\n')
        run_stage(sup,[sys.executable,'-I','-B',busy],self.p/'busy.log',.1,4,4_000_000_000,env,policy)
        for name,code,cause in [('sleep','import time;time.sleep(30)','no observed'),
                                ('fatal',"import time;print('Traceback (most recent call last):',flush=True);time.sleep(30)",'Fatal native worker')]:
            with self.subTest(name=name):
                script=self.put(name+'.py',code);log=self.p/(name+'.log')
                with self.assertRaises(RuntimeError):run_stage(sup,[sys.executable,'-I','-B',script],log,.1,5,4_000_000_000,env,policy)
                receipt=json.loads(log.with_suffix('.exit.json').read_text())
                self.assertIn(cause,receipt['stop_reason']);self.assert_stopped(receipt['launched_pid'])

    def test_native_child_uses_parent_clock_without_short_inner_cap(self):
        from unittest.mock import patch
        from e009_data import run_native
        with patch.dict(os.environ,{'E009_PARENT_DEADLINE':str(time.monotonic()+3)}):
            run_native([sys.executable,'-I','-B','-c','import time;time.sleep(.2)'],self.p/'inner.log',timeout=.01)
        with patch.dict(os.environ,{'E009_PARENT_DEADLINE':str(time.monotonic()-1)}):
            with self.assertRaisesRegex(TimeoutError,'Owner overall'):
                run_native([sys.executable,'-c','pass'],self.p/'expired.log',timeout=60)

    def test_native_download_work_reports_advance_without_heartbeat_credit(self):
        sup=supervisor();env=sup.isolated_env(1);policy={'native_activity':True,'startup_idle_seconds':1.1}
        for moving in (True,False):
            script=self.put('reports-'+str(moving)+'.py',
                "import json,time\nfor n in range(35):\n print('DLBINNER WORK_PROGRESS_JSON='+json.dumps({'work_key':'software-download','completed_bytes':n if "+str(moving)+" else 0}),flush=True)\n time.sleep(.1)\n")
            log=self.p/('reports-'+str(moving)+'.log')
            if moving:run_stage(sup,[sys.executable,'-I','-B',script],log,.1,6,4_000_000_000,env,policy)
            else:
                with self.assertRaisesRegex(RuntimeError,'no observed'):
                    run_stage(sup,[sys.executable,'-I','-B',script],log,.1,6,4_000_000_000,env,policy)
                self.assert_stopped(json.loads(log.with_suffix('.exit.json').read_text())['launched_pid'])

    def test_actual_http_acquisition_reports_completed_bytes_and_verifies_payload(self):
        import functools,hashlib,http.server,threading
        payload=self.put('http/payload.bin','bounded software payload\n'*4096)
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*args):pass
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(payload.parent)))
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            destination=self.p/'downloaded.bin';text=io.StringIO()
            with contextlib.redirect_stdout(text):
                receipt=acquire({'url':f'http://127.0.0.1:{server.server_port}/payload.bin',
                    'bytes':payload.stat().st_size,'sha256':hashlib.sha256(payload.read_bytes()).hexdigest()},destination)
            rows=[json.loads(line.split('=',1)[1]) for line in text.getvalue().splitlines() if line.startswith('DLBINNER WORK_PROGRESS_JSON=')]
            self.assertEqual(rows[0]['completed_bytes'],0);self.assertEqual(rows[-1]['completed_bytes'],payload.stat().st_size)
            self.assertTrue(all(row['work_key']==str(destination) for row in rows))
            self.assertTrue(receipt['publisher_checksum_verified']);self.assertEqual(destination.read_bytes(),payload.read_bytes())
        finally:server.shutdown();server.server_close();worker.join(timeout=2)

    def test_runtime_selection_preserves_data_metadata_testing_and_internal_link_targets(self):
        for n in ['bin/python3.13','lib/python3.13/os.py','lib/libblas.so',
                  'lib/python3.13/site-packages/torch/testing/_comparison.py',
                  'lib/python3.13/site-packages/example/data/model.bin',
                  'lib/python3.13/site-packages/example-1.dist-info/RECORD',
                  'lib/python3.13/site-packages/example-1.dist-info/licenses/LICENSE']:
            self.put('prefix/'+n,'retained')
        for n in ['bin/gcc','include/python.h','lib/gcc/header.h','lib/libblas.a',
                  'lib/python3.13/test/test_os.py','lib/python3.13/site-packages/pandas/tests/test_a.py',
                  'lib/python3.13/site-packages/torch/include/header.h']:
            self.put('prefix/'+n,'excluded')
        target=self.put('prefix/share/licences/extra','required link target')
        (self.p/'prefix/lib/licence-link').symlink_to(target)
        result=runtime_plan(self.p/'prefix')
        self.assertEqual(result['selected_entries'],9)
        self.assertEqual(len(result['omitted']),7)
        self.assertIn('share/licences/extra',result['files'])
        self.assertIn('lib/python3.13/site-packages/torch/testing/_comparison.py',result['files'])

    def test_chunk_materialization_full_reuse_and_corrupted_archive(self):
        for i in range(300):self.put(f'prefix/lib/module-{i:04}.py',f'value={i}\n')
        before=tree_binding(self.p/'prefix');state=self.p/'state'
        first=materialize(self.p/'prefix',self.p/'first',state,self.p/'selection.json')
        receipt_before=(state/'snapshot.json').read_bytes()
        self.assertEqual(first['source_copied_entries'],300);self.assertEqual(len(first['shards']),3)
        second=materialize(self.p/'prefix',self.p/'second',state,self.p/'selection2.json')
        self.assertEqual(second['source_copied_entries'],0);self.assertEqual(second['restored_entries'],300)
        self.assertEqual((state/'snapshot.json').read_bytes(),receipt_before)
        self.assertEqual(tree_binding(self.p/'prefix'),before)
        archive=state/first['shards'][0]['archive']['name']
        with archive.open('r+b') as f:f.seek(-1,2);f.write(b'X')
        with self.assertRaisesRegex(ValueError,'Chunk archive bytes changed'):
            materialize(self.p/'prefix',self.p/'corrupt',state,self.p/'selection3.json')

    def test_real_interrupted_chunk_worker_resumes_sealed_outputs_and_source_drift_refuses(self):
        for i in range(512):self.put(f'prefix/lib/module-{i:04}.py',f'value={i}\n')
        state=self.p/'state';command=[str(sys.executable),'-I','-B',str(ROOT/'scripts/e009_materialize.py'),
            '--source',str(self.p/'prefix'),'--destination',str(self.p/'partial'),
            '--state',str(state),'--summary',str(self.p/'selection.json')]
        child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
        captured=[]
        try:
            for line in child.stdout:
                captured.append(line)
                if '"sealed_chunks": 1' in line:
                    child.terminate();break
            child.wait(timeout=5)
        finally:
            if child.poll() is None:child.kill();child.wait()
            child.stdout.close()
        self.assertNotEqual(child.returncode,0);self.assertTrue(list(state.glob('chunk-*.json')))
        resumed=materialize(self.p/'prefix',self.p/'resumed',state,self.p/'selection2.json')
        self.assertGreaterEqual(resumed['restored_entries'],128)
        self.assertEqual(resumed['restored_entries']+resumed['source_copied_entries'],512)
        self.assertLessEqual(resumed['source_copied_entries'],384)
        (self.p/'prefix/lib/module-0000.py').write_text('changed input')
        with self.assertRaisesRegex(ValueError,'Source/selection plan changed'):
            materialize(self.p/'prefix',self.p/'drift',state,self.p/'selection3.json')

    def test_progressing_work_has_only_overall_clock_and_identical_heartbeats_stall(self):
        sup=supervisor()
        for name,script,success in [
            ('moving',"import time,json\nfor i in range(12):\n print('DLBINNER SNAPSHOT_PROGRESS_JSON='+json.dumps({'work_units':i+1}),flush=True);time.sleep(.25)\n",True),
            ('stalled',"import time,json\nfor i in range(100):\n print('DLBINNER SNAPSHOT_PROGRESS_JSON='+json.dumps({'work_units':0}),flush=True);time.sleep(.1)\n",False),
        ]:
            worker=self.put(name+'.py',script);log=self.p/(name+'.log')
            if success:
                record=supervise_work(sup,[sys.executable,'-I','-B',worker],log,8,1_000_000_000,sup.isolated_env(1),idle_seconds=1.25)
                self.assertGreater(record['wall_seconds'],3);self.assertEqual(record['exit_code'],0)
            else:
                with self.assertRaisesRegex(RuntimeError,'no completed byte/entry progress'):
                    supervise_work(sup,[sys.executable,'-I','-B',worker],log,8,1_000_000_000,sup.isolated_env(1),idle_seconds=1.25)
                record=json.loads(log.with_suffix('.exit.json').read_text());self.assert_stopped(record['launched_pid'])

    @unittest.skipIf(os.geteuid()==0,'Permission failure needs an ordinary user')
    def test_actual_chunk_reader_error_stops_and_preserves_previously_sealed_work(self):
        for i in range(512):self.put(f'prefix/lib/module-{i:04}.py',f'value={i}\n')
        (self.p/'prefix/lib/module-0300.py').chmod(0)
        state=self.p/'state';log=self.p/'chunk-reader-error.log';sup=supervisor()
        with self.assertRaisesRegex(RuntimeError,'PermissionError'):
            sup.supervise([sys.executable,'-I','-B',ROOT/'scripts/e009_materialize.py',
                '--source',self.p/'prefix','--destination',self.p/'partial','--state',state,
                '--summary',self.p/'selection.json'],log,8,1_000_000_000,sup.isolated_env(1))
        record=json.loads(log.with_suffix('.exit.json').read_text())
        self.assertEqual(record['exit_code'],1);self.assertIsNone(record['stop_reason'])
        self.assertIn('module-0300.py',log.read_text());self.assert_stopped(record['launched_pid'])
        self.assertEqual(len(list(state.glob('chunk-*.json'))),2)
        self.assertFalse((state/'snapshot.json').exists())

    def test_concurrent_chunk_writer_refuses_without_changing_seals(self):
        import fcntl
        self.put('prefix/lib/module.py','value=1');state=self.p/'state';state.mkdir()
        log=self.p/'concurrent.log';sup=supervisor()
        with (state/'writer.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with self.assertRaisesRegex(RuntimeError,'BlockingIOError'):
                sup.supervise([sys.executable,'-I','-B',ROOT/'scripts/e009_materialize.py',
                    '--source',self.p/'prefix','--destination',self.p/'local','--state',state,
                    '--summary',self.p/'selection.json'],log,5,1_000_000_000,sup.isolated_env(1))
        self.assertFalse((state/'plan.json').exists());self.assertFalse((self.p/'local').exists())

    def test_snapshot_real_bytes_internal_links_reuse_and_corruption(self):
        source=self.p/'prefix';self.put('prefix/lib/module.py','value=42\n')
        executable=self.put('prefix/bin/python3','executable-bytes');executable.chmod(0o755)
        (source/'bin/python').symlink_to(executable.absolute())
        self.put('prefix/lib/__pycache__/module.pyc','ignored')
        before=tree_binding(source)
        archive=self.p/'snapshot.tar';receipt=self.p/'snapshot.json'
        manifest=create_snapshot(source,self.p/'local',archive,receipt)
        self.assertEqual(tree_binding(source),before)
        self.assertEqual(len(manifest['files']),3)
        self.assertEqual((self.p/'local/bin/python').readlink(),Path('python3'))
        restore_snapshot(receipt,self.p/'reused')
        verify_snapshot(self.p/'reused',manifest)
        (self.p/'reused/lib/module.py').write_text('changed')
        with self.assertRaisesRegex(ValueError,'bytes changed'):verify_snapshot(self.p/'reused',manifest)
        with archive.open('r+b') as f:f.write(b'broken')
        with self.assertRaisesRegex(ValueError,'archive bytes changed'):restore_snapshot(receipt,self.p/'bad')

    def test_snapshot_rejects_external_links_venvs_special_files_and_existing_dest(self):
        source=self.p/'prefix';self.put('prefix/data','bytes')
        external=self.put('outside','outside');(source/'external').symlink_to(external)
        with self.assertRaisesRegex(ValueError,'External'):create_snapshot(source,self.p/'local',self.p/'a.tar',self.p/'a.json')
        (source/'external').unlink();self.put('prefix/pyvenv.cfg','home = /outside')
        with self.assertRaisesRegex(ValueError,'venv'):create_snapshot(source,self.p/'local',self.p/'a.tar',self.p/'a.json')
        (source/'pyvenv.cfg').unlink();os.mkfifo(source/'blocked')
        with self.assertRaisesRegex(ValueError,'Nonregular'):create_snapshot(source,self.p/'local',self.p/'a.tar',self.p/'a.json')
        (source/'blocked').unlink();(self.p/'local').mkdir()
        with self.assertRaisesRegex(ValueError,'fresh'):create_snapshot(source,self.p/'local',self.p/'a.tar',self.p/'a.json')

    @unittest.skipIf(os.geteuid()==0,'Root can read mode-zero files; permission failure needs an ordinary user')
    def test_snapshot_actual_copy_reader_failure_exits_and_retains_cause(self):
        source=self.p/'prefix';bad=self.put('prefix/unreadable.py','original bytes');bad.chmod(0)
        for i in range(20):self.put(f'prefix/other-{i}.py','unchanged')
        log=self.p/'reader-failure.log';sup=supervisor()
        with self.assertRaisesRegex(RuntimeError,'PermissionError'):
            sup.supervise([sys.executable,'-I','-B',ROOT/'scripts/e009_snapshot.py',
                '--source',source,'--destination',self.p/'copy','--archive',self.p/'a.tar',
                '--receipt',self.p/'receipt.json'],log,5,1_000_000_000,sup.isolated_env(1))
        record=json.loads(log.with_suffix('.exit.json').read_text())
        self.assertEqual(record['exit_code'],1);self.assertIsNone(record['stop_reason'])
        self.assertIn('unreadable.py',log.read_text());self.assert_stopped(record['launched_pid'])
        self.assertFalse((self.p/'receipt.json').exists());self.assertFalse((self.p/'a.tar').exists())

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

    def test_comebin_exact_threshold_missing_order_and_length_contracts(self):
        sequences={'below':'A'*999,'boundary':'C'*1000,'z':'G'*1001,'a':'T'*2499}
        validate_comebin_contigs(['z','a'],[1001,2499],sequences,1000)
        for ids,lengths,reason in [
            (['boundary','z','a'],[1000,1001,2499],'eligibility'),
            (['z'],[1001],'eligibility'),
            (['a','z'],[2499,1001],'order'),
            (['z','a'],[1001,2498],'length'),
            (['z','a'],[1001],'length'),
        ]:
            with self.subTest(ids=ids,lengths=lengths),self.assertRaisesRegex(ValueError,reason):
                validate_comebin_contigs(ids,lengths,sequences,1000)

    def test_collector_binds_immutable_archive_log_and_inventory(self):
        attempt=self.p/'attempt';attempt.mkdir();transfer=self.p/'transfer';transfer.mkdir()
        self.put('attempt/terminal.log','exact snapshot\n');self.put('attempt/status.json','{}\n')
        with contextlib.redirect_stdout(io.StringIO()):receipt=collect(attempt,transfer)
        with tarfile.open(receipt['archive']) as archive:
            members=archive.getmembers();self.assertEqual(sum(m.size for m in members),receipt['retained_logical_bytes'])
            self.assertEqual(archive.extractfile('attempt/terminal.log').read(),b'exact snapshot\n')
            self.assertIn('attempt/retained-files.json',[m.name for m in members])
        self.assertEqual(binding(receipt['archive']),receipt['file'])

    def test_final_readonly_bytes_are_checked_and_changed_bytes_fail(self):
        root=self.p/'dependency';root.mkdir();self.put('dependency/native','unchanged')
        files={'dependency':root/'native'}
        before=bind_readonly_files(files)
        for name,changed in [('intact',False),('changed',True)]:
            attempt=self.p/name;attempt.mkdir()
            if changed:self.put('dependency/native','changed')
            now=time.monotonic()
            if changed:
                with self.assertRaisesRegex(ValueError,'Read-only dependency bytes changed'):
                    verify_readonly_after(files,before,attempt,now+10,now+20)
                self.assertIsNone(json.loads((attempt/'readonly-after-failure.json').read_text())['unchanged'])
            else:verify_readonly_after(files,before,attempt,now+10,now+20)
            self.assertEqual(json.loads((attempt/'readonly-after.json').read_text())['unchanged'],not changed)

    def test_readonly_selection_never_enumerates_unrelated_trees(self):
        from unittest.mock import patch
        baseline={'comebin_dependencies':{'prefix':str(self.p/'old')},
            'mapping':{'prefix':str(self.p/'mapping'),'versions':{'samtools':'1','strobealign':'1'}},
            'amber':{'source':str(self.p/'amber')},'amber_source_files':{},'checkm_payloads':{}}
        src=self.put('amber/evaluate.py','real evaluator input')
        marker=self.put('old/checkm_data/hmms/checkm.hmm','real marker input')
        baseline['amber_source_files']['evaluate.py']=binding(src)['sha256']
        baseline['checkm_payloads']['hmms/checkm.hmm']=binding(marker)['sha256']
        self.put('old/bin/checkm','console source');self.put('mapping/bin/samtools','native binary')
        self.put('mapping/bin/strobealign','native mapper')
        self.put('old/tests/unrelated','not an input');self.put('mapping/lib/unrelated','not an input')
        files,expected=readonly_inputs(baseline)
        with patch.object(Path,'rglob',side_effect=AssertionError('whole-tree traversal forbidden')):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                before=bind_readonly_files(files,expected)
                self.put('old/tests/unrelated','unrelated file change')
                self.assertEqual(bind_readonly_files(files),before)
        self.assertEqual(len(before),5)
        self.assertIn('READONLY_FILE begin',output.getvalue())
        self.assertIn('completed_bytes',output.getvalue())
        marker.write_text('corrupted marker')
        with self.assertRaisesRegex(ValueError,'Accepted read-only input changed: checkm_data'):
            bind_readonly_files(files,expected)

    def test_readonly_file_target_changes_and_missing_files_fail(self):
        a=self.put('a','same bytes');b=self.put('b','same bytes');link=self.p/'link';link.symlink_to(a)
        files={'native':link};before=bind_readonly_files(files)
        link.unlink();link.symlink_to(b)
        attempt=self.p/'after';attempt.mkdir();now=time.monotonic()
        with self.assertRaisesRegex(ValueError,'Read-only dependency bytes changed'):
            verify_readonly_after(files,before,attempt,now+10,now+20)
        link.unlink()
        with self.assertRaises(FileNotFoundError):bind_readonly_files(files)

    def test_binding_progress_reports_actual_byte_counts(self):
        data=self.p/'stream';data.write_bytes(b'x'*(2*1024*1024+17));counts=[]
        original=binding(data);self.assertEqual(binding(data,progress=counts.append),original)
        self.assertEqual(counts[0],0);self.assertEqual(counts[-1],original['bytes'])

    def test_expired_parent_alarm_cannot_leave_readonly_cleanup_unbounded(self):
        # Inject a stalled filesystem check, outside the actual hashing contract.
        # The production guard must re-arm an expired parent timer and retain
        # the intended timeout before returning; an outer failure is not a pass.
        code=self.put('cleanup.py',f"""import json,signal,sys,time
from pathlib import Path
sys.path.insert(0,{str(ROOT/'scripts')!r})
import e009_owner as owner
def alarm(signum,frame):raise TimeoutError('intended cleanup clock')
signal.signal(signal.SIGALRM,alarm)
signal.setitimer(signal.ITIMER_REAL,.02)
try:time.sleep(1)
except TimeoutError:pass
assert signal.getitimer(signal.ITIMER_REAL)[0]==0
def blocked(path):time.sleep(60)
owner.bind_readonly_files=blocked
attempt=Path({str(self.p/'cleanup')!r});attempt.mkdir()
now=time.monotonic()
try:owner.verify_readonly_after({{'blocked':attempt}},{{}},attempt,now-1,now+.15)
except TimeoutError:
    result=json.loads((attempt/'readonly-after-failure.json').read_text())
    assert result['unchanged'] is None and 'intended cleanup clock' in result['error']
    assert time.monotonic()-now<2
    print('PASS intended re-armed cleanup timeout',flush=True)
else:raise AssertionError('stalled check was accepted')
""")
        sup=supervisor();receipt=sup.supervise([sys.executable,'-B',code],self.p/'cleanup.log',5,8_000_000_000,sup.isolated_env(4))
        self.assertEqual(receipt['exit_code'],0)
        self.assertIn('PASS intended re-armed cleanup timeout',(self.p/'cleanup.log').read_text())

    def startup_prefix(self):
        """Create a fresh no-pip venv to test actual site and lexical-prefix behavior."""
        prefix=self.p/'prefix'
        subprocess.run([sys.executable,'-I','-B','-m','venv','--without-pip',prefix],check=True)
        site=next((prefix/'lib').glob('python*/site-packages'))
        return prefix,prefix/'bin/python',site

    def test_startup_real_site_inventory_and_module_stdout_contract(self):
        prefix,python,site=self.startup_prefix()
        (site/'fixture-1.0.dist-info').mkdir()
        (site/'fixture-1.0.dist-info/METADATA').write_text('Metadata-Version: 2.1\nName: fixture\nVersion: 1.0\n')
        expected=self.put('expected.json','{"fixture":"1.0"}')
        log=self.p/'healthy.log';sup=supervisor()
        argv=startup_argv(python,ROOT/'scripts/e009_native.py',['--inventory-prefix',prefix,'--expected-distributions',expected],trace_seconds=.1)
        self.assertEqual(argv[0],str(python))
        original=sup.process_sample
        receipt=supervise_startup(sup,argv,log,10,8_000_000_000,sup.isolated_env(4))
        self.assertEqual(receipt['exit_code'],0);self.assertIs(sup.process_sample,original)
        text=log.read_text();self.assertLess(text.index('before site'),text.index('site ready'))
        self.assertIn('metadata ready fixture 1.0',text)
        result=json.loads(next(line.split('=',1)[1] for line in text.splitlines() if line.startswith('INVENTORY_JSON=')))
        self.assertEqual(Path(result['prefix']),prefix.resolve());self.assertEqual(result['python_executable_lexical'],str(python))
        self.assertEqual(result['distributions'][0]['version'],'1.0')
        (site/'fixture_cli.py').write_text("print('fixture==1.0')\n")
        module_env=dict(sup.isolated_env(4),E009_STARTUP_STACK_DIR=str(self.p/'healthy.startup-stacks'))
        module=subprocess.run(startup_argv(python,'fixture_cli',mode='module',trace_seconds=.1),env=module_env,capture_output=True,text=True,check=True)
        self.assertEqual(module.stdout,'fixture==1.0\n');self.assertIn('site ready',module.stderr)
        standalone=subprocess.run(startup_argv(python,'fixture_cli',mode='module'),env=sup.isolated_env(4),capture_output=True,text=True,check=True)
        self.assertEqual(standalone.stdout,'fixture==1.0\n');self.assertIn('finished pid=',standalone.stderr)

    def test_actual_blocked_bytecode_read_is_avoided_without_prefix_writes(self):
        """Reproduce get_data/read on a cache FIFO; actual source import must succeed."""
        import importlib.util
        import py_compile
        prefix,python,site=self.startup_prefix()
        module=site/'blocked_cache.py';module.write_text('VALUE=731\n')
        before=binding(module);cache=Path(importlib.util.cache_from_source(str(module)))
        py_compile.compile(str(module),cfile=str(cache),doraise=True)
        cache.unlink();os.mkfifo(cache)
        fd=os.open(cache,os.O_RDWR|os.O_NONBLOCK);self.addCleanup(os.close,fd)
        target=self.put('cache-target.py',"import blocked_cache\nprint('VALUE='+str(blocked_cache.VALUE),flush=True)\n")
        sup=supervisor();old=self.p/'cache-blocked.log';env=sup.isolated_env(1)
        with self.assertRaisesRegex(RuntimeError,'Configured wall-time limit'):
            supervise_startup(sup,startup_argv(python,target,trace_seconds=.1),old,.8,4_000_000_000,env)
        stacks=''.join(p.read_text() for p in old.with_suffix('.startup-stacks').glob('*.log'))
        self.assertIn('get_data',stacks)
        self.assert_stopped(json.loads(old.with_suffix('.exit.json').read_text())['launched_pid'])
        env=dict(env,E009_SOURCE_CACHE_ROOT=str(self.p/'empty-cache-namespace'))
        fixed=self.p/'cache-source.log'
        receipt=supervise_startup(sup,startup_argv(python,target,trace_seconds=.1,env=env),fixed,5,4_000_000_000,env)
        self.assertEqual(receipt['exit_code'],0);self.assertIn('VALUE=731',fixed.read_text())
        audit=json.loads(next(l.split('=',1)[1] for l in fixed.read_text().splitlines() if l.startswith('CACHE_POLICY_JSON=')))
        self.assertEqual(audit['persistent_bytecode_attempts'],0);self.assertGreater(audit['source_opens'],0)
        self.assertTrue(audit['writes_disabled']);self.assertEqual(binding(module),before)
        self.assertFalse((self.p/'empty-cache-namespace').exists());self.assertTrue(cache.is_fifo())

    def test_source_cache_flags_are_explicit_idempotent_and_only_for_python(self):
        env={'E009_SOURCE_CACHE_ROOT':str(self.p/'empty-cache')}
        argv=['/lexical/venv/bin/python','-I','-B','-m','pip','freeze','--all']
        adjusted=source_cache_argv(argv,env)
        self.assertEqual(adjusted[0],argv[0]);self.assertEqual(adjusted[3:5],['-X','pycache_prefix='+env['E009_SOURCE_CACHE_ROOT']])
        self.assertEqual(source_cache_argv(adjusted,env),adjusted)
        self.assertEqual(source_cache_argv(['/tool','--version'],env),['/tool','--version'])
        with self.assertRaisesRegex(ValueError,'Absolute'):source_cache_argv(argv,{'E009_SOURCE_CACHE_ROOT':'relative'})

    def test_startup_site_hang_keeps_stack_timeout_and_cleanup(self):
        prefix,python,site=self.startup_prefix()
        (site/'stall_fixture.py').write_text('import time\ntime.sleep(60)\n')
        (site/'stall.pth').write_text('import stall_fixture\n')
        sup=supervisor();log=self.p/'site-stall.log';original=sup.process_sample
        with self.assertRaisesRegex(RuntimeError,'TimeoutError'):
            supervise_startup(sup,startup_argv(python,ROOT/'scripts/e009_native.py',['--inventory-prefix',prefix],trace_seconds=.1),log,.8,8_000_000_000,sup.isolated_env(4))
        self.assertIs(sup.process_sample,original)
        text=log.read_text();self.assertIn('before site',text);self.assertNotIn('site ready',text)
        stacks=''.join(p.read_text() for p in log.with_suffix('.startup-stacks').glob('*.log'))
        self.assertIn('stall_fixture.py',stacks);self.assertIn('addpackage',stacks)
        receipt=json.loads(log.with_suffix('.exit.json').read_text());self.assertIn('TimeoutError',receipt['stop_reason']);self.assert_stopped(receipt['launched_pid'])
        self.assertTrue(log.with_suffix('.process-wait.jsonl').is_file())

    def test_slow_actual_inventory_keeps_all_import_checks(self):
        prefix,python,site=self.startup_prefix()
        modules=[]
        for i in range(8):
            name='slow_import_'+str(i);modules.append(name)
            (site/(name+'.py')).write_text('import time\ntime.sleep(.2)\n')
        expected=self.put('slow-expected.json','{}')
        args=['--inventory-prefix',prefix,'--expected-distributions',expected,'--modules',*modules]
        log=self.p/'slow-inventory.log';sup=supervisor()
        receipt=run_stage(sup,[python,'-I','-B',ROOT/'scripts/e009_native.py',*args],log,.8,10,8_000_000_000,sup.isolated_env(4),{'startup_probe_seconds':8,'startup_idle_seconds':.8})
        self.assertEqual(receipt['seconds_ceiling'],8)
        self.assertEqual(receipt['exit_code'],0);self.assertGreater(receipt['wall_seconds'],.8)
        text=log.read_text();inventory=json.loads(next(line.split('=',1)[1] for line in text.splitlines() if line.startswith('INVENTORY_JSON=')))
        self.assertEqual(set(inventory['origins']),set(modules))
        for name in modules:self.assertIn('import ready '+name,text)

    def test_startup_progress_ignores_duplicate_dumps_and_kernel_counters(self):
        tracker=StartupProgress(2,0)
        first=progress_signature('phase',('Current thread same\nread file A',))
        self.assertTrue(tracker.observe(first,0))
        repeat=progress_signature('phase',('Current thread same\nread file ACurrent thread same\nread file A',))
        self.assertFalse(tracker.observe(repeat,1))
        with self.assertRaisesRegex(TimeoutError,'no observed'):tracker.observe(repeat,2)
        changed=progress_signature('phase',('Current thread same\nread file B',))
        self.assertTrue(tracker.observe(changed,3))
        row={'pid':123,'observation_status':'observed owned process','fd_targets':{'4':'file A'},'wchan':'read_wait','io':'10'}
        original=progress_signature('',processes=[row])
        row.update(wchan='running',io='20')
        self.assertEqual(original,progress_signature('',processes=[row]))
        row['fd_targets']['4']='file B'
        self.assertNotEqual(original,progress_signature('',processes=[row]))

    def test_startup_slow_progress_and_idle_fatal_cleanup(self):
        sup=supervisor()
        for name,code,ok,cause in [
            ('moving',"import time\nfor i in range(8):\n print('phase',i,flush=True)\n time.sleep(.2)\n",True,None),
            ('idle',"import time\ntime.sleep(60)\n",False,'no observed'),
            ('absolute',"import time\nfor i in range(200):\n print('phase',i,flush=True)\n time.sleep(.1)\n",False,'Configured wall-time limit'),
            ('fatal',"import time,subprocess,sys\nfrom pathlib import Path\np=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])\nPath(__file__).with_suffix('.pid').write_text(str(p.pid))\nprint('Traceback (most recent call last):',flush=True)\nprint('ValueError: intended startup failure',flush=True)\ntime.sleep(60)\n",False,'Fatal Python traceback')]:
            log=self.p/(name+'.log');native=self.put(name+'.py',code)
            with self.subTest(name=name):
                def run():return supervise_startup(sup,startup_argv(sys.executable,native,trace_seconds=.1),log,2 if name=='absolute' else 5,8_000_000_000,sup.isolated_env(4),idle_seconds=.7)
                if ok:
                    self.assertEqual(run()['exit_code'],0)
                    self.assertGreater(json.loads(log.with_suffix('.exit.json').read_text())['wall_seconds'],.7)
                else:
                    with self.assertRaisesRegex(RuntimeError,cause):run()
                    receipt=json.loads(log.with_suffix('.exit.json').read_text())
                    self.assertIn(cause,receipt['stop_reason']);self.assertNotIn('Cleanup failed',receipt['stop_reason'])
                    self.assertLess(receipt['wall_seconds'],8);self.assert_stopped(receipt['launched_pid'])
                    if name=='fatal':self.assert_stopped(int(native.with_suffix('.pid').read_text()))

    def test_wait_snapshot_checks_pid_identity_and_bounds_without_environs(self):
        proc=self.p/'proc';folder=proc/'123';folder.mkdir(parents=True)
        fields=['S']+['0']*21;fields[19]='42'
        (folder/'stat').write_text('123 (owned fixture) '+' '.join(fields))
        (folder/'status').write_text('State:\tS (sleeping)\nThreads:\t1\n')
        (folder/'wchan').write_text('futex_wait_queue')
        (folder/'cmdline').write_bytes(b'python\0probe\0')
        (folder/'environ').write_text('SECRET=must not be read')
        result=wait_snapshot(123,'42',proc)
        self.assertEqual(result['observation_status'],'observed owned process');self.assertEqual(result['wchan'],'futex_wait_queue')
        self.assertEqual(result['cmdline'],'python probe ');self.assertNotIn('environ',result)
        self.assertIn('unavailable',result['stack'])
        self.assertEqual(wait_snapshot(123,'wrong',proc)['observation_status'],'exited or PID reused')

    def test_transfer_terminal_is_live_while_archive_snapshot_is_immutable(self):
        attempt=self.p/'attempt';attempt.mkdir();transfer=self.p/'transfer';transfer.mkdir()
        terminal=self.put('transfer/attempt-terminal.log','before collection\n')
        self.put('attempt/status.json','{}\n')
        with contextlib.redirect_stdout(io.StringIO()):result=collect(attempt,transfer,terminal)
        terminal.write_text('before collection\nafter collection\n')
        with tarfile.open(result['archive']) as tar:
            self.assertEqual(tar.extractfile('attempt/terminal.log').read(),b'before collection\n')
            self.assertEqual(sum(m.size for m in tar.getmembers()),result['retained_logical_bytes'])

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
