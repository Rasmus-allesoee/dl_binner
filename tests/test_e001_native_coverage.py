"""Real COMEBin sequence/coverage contract on tiny BAMs using bedtools 2.31.1.

Requires the reviewed local COMEBin checkout and a real bedtools binary. Nothing
inside the path resolver, native readers, augmentation, coverage workers or
bedtools subprocess is mocked. This is macOS raw-feature evidence, not Linux
PyTorch or research-scale validation.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'scripts'))
from e001lib import native
from e001_vamb_cpu import sha


class NativeCoverageTests(unittest.TestCase):
    def test_actual_coverage_fresh_and_recovered_manifest_paths(self):
        import numpy as np
        import pysam
        source=REPO/'agent_context/tools_repo/COMEBin'
        binary=Path(os.environ.get('E001_TEST_BEDTOOLS',str(REPO/'scratch/e001-native-contract/bedtools2-2.31.1/bin/bedtools')))
        if not binary.exists() or not source.exists():self.skipTest('Native contract dependencies unavailable')
        self.assertEqual(subprocess.check_output([binary,'--version'],text=True).strip(),'bedtools v2.31.1')
        self.assertEqual(native.verify_source('COMEBin',source)['commit'],'1b476a41fac893294c70212a869573a732560ce5')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);old=root/'original';new=root/'recovery';new.mkdir()
            fasta=root/'canonical.fna';fasta.write_text('>a\n'+'ACGT'*625+'\n>b\n'+'TGCA'*875+'\n')
            inputs={}
            for c,count in (('C0',10),('CT',2)):
                folder=old/'bams'/c;folder.mkdir(parents=True);inputs[c]=[]
                for i in range(2):
                    bam=folder/f'{i:02d}-sample-{i*9}.bam';inputs[c].append(bam)
                    with pysam.AlignmentFile(str(bam),'wb',header={'HD':{'VN':'1.6','SO':'coordinate'},'SQ':[{'SN':'a','LN':2500},{'SN':'b','LN':3500}]}) as handle:
                        for j in range(count):
                            read=pysam.AlignedSegment();read.query_name=f'r{j}';read.query_sequence='A'*50;read.flag=0
                            read.reference_id=0;read.reference_start=100+j*60;read.mapping_quality=60;read.cigarstring='50M';handle.write(read)
                    pysam.index(str(bam))
            # Neither recovered condition has a local bams directory: exactly the returned failure.
            self.assertFalse((new/'bams').exists())
            with patch.dict(os.environ,{'PATH':str(binary.parent)+os.pathsep+os.environ['PATH']}):
                native.comebin_raw_features(source,fasta,inputs['C0'],old/'features',threads=1)
                # The full adapter normally publishes this after normalization; raw tests need only the reference contract.
                (old/'features/native-features.json').write_text(json.dumps({'fasta_sha256':sha(fasta)}))
                native.comebin_raw_features(source,fasta,inputs['C0'],new/'C0',fixed=old/'features',threads=1)
                (new/'C0/native-features.json').write_text(json.dumps({'fasta_sha256':sha(fasta)}))
                native.comebin_raw_features(source,fasta,inputs['CT'],new/'CT',fixed=new/'C0',threads=1)
            for name in ('coverage_mean.npy','coverage_var.npy'):
                np.testing.assert_array_equal(np.load(old/'features'/name),np.load(new/'C0'/name))
            c0=np.load(new/'C0/coverage_mean.npy');ct=np.load(new/'CT/coverage_mean.npy')
            self.assertEqual(c0.shape,(2,6,2));np.testing.assert_allclose(c0[:,0,0],.2);np.testing.assert_allclose(ct[:,0,0],.04)
            np.testing.assert_array_equal(c0[:,:,1],0)
            self.assertEqual(sha(new/'C0/augmentation_intervals.npy'),sha(new/'CT/augmentation_intervals.npy'))
            self.assertEqual((new/'CT/bam_ids.txt').read_text().splitlines(),['00-sample-0.bam','01-sample-9.bam'])
            # Fail before generating anything for missing, reordered or extra inputs.
            for paths in ([new/'bams/C0/missing.bam'],inputs['C0'][::-1],inputs['C0'][:1]):
                with self.assertRaises(ValueError):native.comebin_raw_features(source,fasta,paths,new/'bad',threads=1)
                self.assertFalse((new/'bad').exists())


if __name__=='__main__':unittest.main()
