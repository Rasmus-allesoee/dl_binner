"""Data-stage boundary, archive and resume checks using tiny owned files only."""
import gzip
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e009_gcp_stage import unpack_reads, split_interleaved, seal, origin_summary
from e009_gcp_run import verify_completed, ClockAndDisk
from e009_native import cpu_plan, prepare_bam_directory, command_plan


class GCPDataContracts(unittest.TestCase):
    """Protect source bytes, declared axes, disk stops and journaled completed work."""
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    def archive(self, members):
        """Make a new tiny tar with explicit byte/type members."""
        path=self.root/'reads.tar.gz'
        with tarfile.open(path,'w:gz') as tar:
            for name,data,kind in members:
                m=tarfile.TarInfo(name);m.type=kind;m.size=len(data);m.linkname='../outside'
                tar.addfile(m,io.BytesIO(data))
        folder=self.root/'stage';folder.mkdir();return path,folder
    def test_interleaved_and_plain_mates_retain_complete_fastq(self):
        pair='@x/1\nACGT\n+\nIIII\n@x/2\nACGT\n+\nIIII\n'
        archive,folder=self.archive([('s/anonymous_reads.fq.gz',gzip.compress(pair.encode()),tarfile.REGTYPE)])
        result=unpack_reads(archive,folder,0,10000)
        self.assertEqual(result['validation']['pairs'],1)
        left,right=split_interleaved(result['first'],folder)
        self.assertEqual(gzip.open(left,'rt').read()+gzip.open(right,'rt').read(),pair)
        self.assertTrue(archive.exists())
    def test_archive_links_traversal_and_duplicates_fail(self):
        for name,kind in [('../bad',tarfile.REGTYPE),('s/link',tarfile.SYMTYPE)]:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
                old=self.root;self.root=Path(tmp)
                try:
                    archive,folder=self.archive([(name,b'bad',kind)])
                    with self.assertRaises(ValueError):unpack_reads(archive,folder,0,10000)
                finally:self.root=old
    def test_completed_resume_rejects_missing_changed_extra_and_unsealed(self):
        folder=self.root/'parts/source';folder.mkdir(parents=True);p=folder/'data';p.write_text('original')
        seal(folder,{'value':str(p)});verify_completed(self.root)
        p.write_text('changed')
        with self.assertRaisesRegex(ValueError,'bytes changed'):verify_completed(self.root)
        p.write_text('original');(folder/'extra').write_text('extra')
        with self.assertRaisesRegex(ValueError,'file set changed'):verify_completed(self.root)
        (folder/'extra').unlink();p.unlink()
        with self.assertRaisesRegex(ValueError,'file set changed'):verify_completed(self.root)
        (self.root/'parts/incomplete').mkdir()
        with self.assertRaisesRegex(ValueError,'Unsealed'):verify_completed(self.root)
    def test_origin_population_refuses_changed_counts_or_taxonomy(self):
        text='#anonymous_read_id\tgenome_id\ttax_id\tread_id\nS0R0/1\tA\t1\tx/1\nS0R0/2\tA\t1\tx/2\n'
        p=self.root/'origins.gz';p.write_bytes(gzip.compress(text.encode()))
        self.assertEqual(origin_summary(p,1,self.root/'ok.json')['rows'],2)
        with self.assertRaisesRegex(ValueError,'counts differ'):origin_summary(p,2,self.root/'bad.json')
        p.write_bytes(gzip.compress(text.replace('S0R0/2\tA\t1','S0R0/2\tA\t2').encode()))
        with self.assertRaisesRegex(ValueError,'taxon'):origin_summary(p,1,self.root/'bad.json')
    def test_parent_clock_covers_work_before_child(self):
        import time
        with self.assertRaisesRegex(RuntimeError,'overall'):
            with ClockAndDisk(self.root,.05,0):time.sleep(1)
    def test_actual_disk_reserve_stops_parent_before_child(self):
        import time
        with self.assertRaisesRegex(RuntimeError,'disk reserve violated'):
            with ClockAndDisk(self.root,5,10**30):time.sleep(4)
    def test_ten_bam_completebin_budget_and_resolved_directory(self):
        ids=[0,2,3,4,6,9,10,11,14,17];bams=[]
        for i in ids:
            p=self.root/f'map_{i:04d}'/f'sample_{i:04d}.bam';p.parent.mkdir();p.write_bytes(bytes([i]));bams.append(p)
        prepare_bam_directory(self.root/'bams',bams)
        links=sorted((self.root/'bams').glob('*.bam'))
        self.assertEqual([p.resolve() for p in links],[p.resolve() for p in bams])
        ref=self.root/'assembly.fa';ref.write_text('>c\nACGT\n')
        plan=command_plan('completebin',self.root,ref,bams,self.root/'out',8,self.root/'db')
        budget=plan['resource_plan'];self.assertEqual(budget['coverage_outer_processes'],2)
        self.assertLessEqual(2*(budget['pool_workers']+1)+2,8)
        self.assertEqual(plan['api']['gpu_dataloader_workers'],0)
        self.assertEqual(plan['api']['sorted_bam_file_list'],list(map(str,bams)))


if __name__=='__main__':unittest.main()
