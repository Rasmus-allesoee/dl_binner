"""Real BAM fixtures and an independent dense per-base coverage oracle.

Synthetic reads are encoded/decoded with pinned HTSlib; production counting uses
CIGAR interval sweeps, while this oracle uses independent SAM text/array logic.
No community input, aligner or scientific score is involved.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pysam

from dl_binner.multiscale import measurement as m
from dl_binner.multiscale.cache import Bank,seal,rebind,read_sample
from dl_binner.multiview.views import prepare,config,load


def fixture(root,rows=None,length=500):
    """Build actual parent/crop artifacts and a sorted BAM with a zero contig."""
    root=Path(root);root.mkdir(exist_ok=True)
    fasta=root/'assembly.fna';fasta.write_text('>opaque-A\n'+'ACGT'*(length//4)+'\n>opaque-Z\n'+'TGCA'*(length//4)+'\n')
    depth=root/'old.tsv';depth.write_text('contig_id\tZ9\nopaque-A\t1\nopaque-Z\t0\n')
    prepare(fasta,depth,root/'old',config());features=root/'old/features.npz';views=root/'old/views.npz'
    if rows is None:
        rows=[dict(name='perfect',flag=0,pos=100,mapq=60,cigar='150M',nm=0),
              dict(name='mapq0',flag=0,pos=100,mapq=0,cigar='150M',nm=0),
              dict(name='duplicate',flag=1024,pos=100,mapq=60,cigar='150M',nm=0),
              dict(name='qc',flag=512,pos=100,mapq=60,cigar='150M',nm=0),
              dict(name='secondary',flag=256,pos=100,mapq=60,cigar='150M',nm=0),
              dict(name='supplementary',flag=2048,pos=100,mapq=60,cigar='150M',nm=0),
              dict(name='low_id',flag=0,pos=100,mapq=60,cigar='150M',nm=6),
              dict(name='id98',flag=0,pos=100,mapq=60,cigar='150M',nm=3)]
    bam=root/'input.bam'
    with pysam.AlignmentFile(bam,'wb',header={'HD':{'VN':'1.6','SO':'coordinate'},'SQ':[{'SN':'opaque-A','LN':length},{'SN':'opaque-Z','LN':length}]}) as stream:
        for row in rows:
            r=pysam.AlignedSegment(stream.header);r.query_name=row['name'];r.flag=row.get('flag',0)
            r.reference_id=row.get('tid',0);r.reference_start=row.get('pos',0);r.mapping_quality=row.get('mapq',60);r.cigarstring=row.get('cigar','150M')
            n=sum(size for op,size in r.cigartuples if op in (0,1,4,7,8))
            r.query_sequence='A'*n
            if not row.get('missing_qualities'):r.query_qualities=pysam.qualitystring_to_array('I'*n)
            if row.get('nm') is not None:r.set_tag('NM',row['nm'])
            stream.write(r)
    return features,views,bam


def independent_counter(bam):
    """Decode SAM text and increment individual bases, separate from interval code."""
    import re
    with pysam.AlignmentFile(bam,'rb') as stream:
        result={name:np.zeros((length,2),np.int64) for name,length in zip(stream.references,stream.lengths)}
        for record in stream:
            fields=record.to_string().split('\t');flag=int(fields[1]);mq=int(fields[4])
            if flag&0xF04 or mq==255:continue
            cigar=[(int(n),op) for n,op in re.findall(r'(\d+)([MIDNSHP=X])',fields[5])]
            tags={x.split(':',2)[0]:x.split(':',2)[2] for x in fields[11:]}
            total=sum(n for n,op in cigar if op in 'M=X');gaps=sum(n for n,op in cigar if op in 'ID')
            substitutions=int(tags['NM'])-gaps
            if (total-substitutions)/(total+gaps)<.97:continue
            at=int(fields[3])-1
            for n,op in cigar:
                if op in 'M=X':
                    for i in range(at,at+n):
                        result[fields[2]][i,0]+=1;result[fields[2]][i,1]+=int(mq>=20)
                    at+=n
                elif op in 'DN':at+=n
    return result


class Measurement(unittest.TestCase):
    def test_run_sweep_exact_sparse_prefix_and_independent_dense_oracle(self):
        rng=np.random.default_rng(19)
        for length in (7,500,3200):
            coords=np.array([[0,length],[0,max(1,length//2)],[length//2,length],[-1,-1],[1,min(length,5)]],np.int64)
            sweep=m.Sweep(length,coords);depth=np.zeros(length,np.int64);high=depth.copy()
            starts=np.sort(rng.integers(0,length,size=100))
            for at in starts:
                end=int(rng.integers(at+1,length+1));good=bool(rng.integers(2));sweep.advance(int(at));sweep.add([(int(at),end)],good)
                depth[at:end]+=1
                if good:high[at:end]+=1
            actual=sweep.finish()
            for j,(a,b) in enumerate(coords):
                wanted=np.array([depth[a:b].sum(),(depth[a:b]**2).sum(),(depth[a:b]>0).sum(),high[a:b].sum()]) if a>=0 else np.zeros(4)
                np.testing.assert_array_equal(actual[j],wanted)

    def test_real_BAM_full_denominator_and_JGI_no_variance_regression_fixture(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);f,v,b=fixture(root)
            receipt=m.summarize(b,f,v,root/'bank/sample-00','Z9')
            a,_=read_sample(root/'bank/sample-00',f,v,'Z9')
            # Common rule additionally rejects the supplementary JGI default kept.
            # Three valid 150M records, full 500-bp denominator: mean .9, var 1.89.
            self.assertEqual(a[0,0].tolist(),[450.,1350.,150.,300.])
            self.assertEqual(a[1,0].tolist(),[0.,0.,0.,0.])
            seal(root/'bank',f,v,[root/'bank/sample-00']);bank=Bank(root/'bank',f,v)
            s,valid=bank.statistics(np.array([0,1]),np.array([0,0]))
            self.assertEqual(s[0,0,0],.9);self.assertAlmostEqual(s[0,0,2],1.89)
            self.assertTrue(valid.all());self.assertEqual(s[1,0,0],0.)
            rebind(root/'bank',f,v,root/'new.npz');new,meta=load(root/'new.npz')
            self.assertAlmostEqual(float(new['depth'][0,0]),.9,6);self.assertTrue(new['zero_depth'][1,0])
            self.assertEqual(receipt['counters']['excluded_flags'],4)
            self.assertEqual(receipt['counters']['excluded_identity'],1)
            # JGI's retained no-variance 0 is not adopted or relabelled correct.
            self.assertNotEqual(float(new['depth'][0,0]),0.)

    def test_exact_identity_indels_clips_mixed_EQ_X_BQ0_MAPQ255_and_flags(self):
        rows=[dict(name='clipped',pos=0,cigar='10S100M10S',nm=3),
              dict(name='indel',pos=110,cigar='50=1I49M1D',nm=3),
              dict(name='missingQ',pos=220,cigar='100M',nm=0,missing_qualities=True),
              dict(name='unknownMAPQ',pos=330,cigar='100M',nm=0,mapq=255)]
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);f,v,b=fixture(root,rows)
            r=m.summarize(b,f,v,root/'out','Z9');a=np.load(root/'out/moments.npy')
            self.assertEqual(a[0,0,0],299.);self.assertEqual(a[0,0,2],299.)
            self.assertEqual(r['counters']['included_missing_BQ'],1);self.assertEqual(r['counters']['excluded_MAPQ255'],1)

    def test_real_mates_double_count_reverse_endpoints_and_independent_SAM_oracle(self):
        rows=[dict(name='mate',flag=65,pos=0,cigar='100M',nm=0),
              dict(name='mate',flag=145,pos=50,cigar='100M',nm=0),
              dict(name='indel',pos=180,cigar='49M1I50M1D',nm=3),
              dict(name='edge',pos=400,cigar='100M',nm=0,mapq=0)]
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);f,v,b=fixture(root,rows)
            m.summarize(b,f,v,root/'bank/sample-00','Z9');seal(root/'bank',f,v,[root/'bank/sample-00'])
            bank=Bank(root/'bank',f,v);oracle=independent_counter(b)
            for row,ident in enumerate(bank.data['ids']):
                for j,(start,end) in enumerate(bank.coordinates[row]):
                    if start<0:continue
                    x=oracle[ident][start:end];s,valid=bank.statistics(np.array([row]),np.array([j]))
                    expected=[x[:,0].mean(),(x[:,0]>0).mean(),x[:,0].var(),x[:,1].sum()/x[:,0].sum() if x[:,0].sum() else 0,end-start]
                    np.testing.assert_allclose(s[0,0],expected,rtol=0,atol=1e-12)
            self.assertEqual(oracle['opaque-A'][50,0],2)

    def test_exact_DNA_windows_measured_separately_from_parent_and_missing(self):
        rows=[dict(name='left',pos=0,cigar='150M',nm=0),dict(name='right',pos=2900,cigar='150M',nm=0)]
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);f,v,b=fixture(root,rows,length=3200)
            m.summarize(b,f,v,root/'bank/sample-00','Z9');seal(root/'bank',f,v,[root/'bank/sample-00']);bank=Bank(root/'bank',f,v)
            data,_,views,_=load(f,v)
            for j in range(5):
                coords=bank.coordinates[0,j];s,valid=bank.statistics(np.array([0]),np.array([j]))
                dense=np.zeros(3200);dense[:150]=1;dense[2900:3050]=1
                np.testing.assert_allclose(s[0,0,:3],[dense[coords[0]:coords[1]].mean(),(dense[coords[0]:coords[1]]>0).mean(),dense[coords[0]:coords[1]].var()])
            (root/'missing').mkdir();seal(root/'missing',f,v,[None]);missing=Bank(root/'missing',f,v)
            s,valid=missing.statistics(np.array([1]),np.array([0]));self.assertFalse(valid.any());self.assertEqual(s.sum(),0.)
            s,valid=bank.statistics(np.array([1]),np.array([0]));self.assertTrue(valid.all());self.assertEqual(s.sum(),3200.)
            cells,w=bank.batch(np.array([0]),np.array([0]),bank.fit(),drop=np.array([True]))
            self.assertEqual(cells.sum(),0.);self.assertEqual(w.sum(),0.)
            with self.assertRaisesRegex(ValueError,'requires all'):rebind(root/'missing',f,v,root/'bad.npz')

    def test_seal_refuses_semantically_impossible_rehashed_crop_moments(self):
        from dl_binner.context.tokens import binding
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);f,v,b=fixture(root,length=3200)
            m.summarize(b,f,v,root/'bank/sample-00','Z9')
            path=root/'bank/sample-00/moments.npy';a=np.load(path,mmap_mode='r+')
            a[0,1]=[10000,100000,100,10000];a.flush();del a
            receipt=root/'bank/sample-00/sample.json';r=json.loads(receipt.read_text());r['moments']=binding(path)
            receipt.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'subset accounting'):seal(root/'bank',f,v,[root/'bank/sample-00'])
            self.assertFalse((root/'bank/bank.json').exists())

    def test_refuse_missing_NM_bad_NM_skips_overrun_order_dictionary_and_corruption(self):
        for rows,message in [([dict(name='noNM',cigar='100M')],'missing NM'),
                ([dict(name='badNM',cigar='99=1X',nm=0)],'substitution'),
                ([dict(name='N',cigar='90M10N10M',nm=0)],'Reference-skip'),
                ([dict(name='escape',pos=490,cigar='100M',nm=0)],'escapes'),
                ([dict(name='first',pos=50,cigar='100M',nm=0),dict(name='second',pos=20,cigar='100M',nm=0)],'Actual BAM coordinate')]:
            with self.subTest(message=message),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);f,v,b=fixture(root,rows)
                with self.assertRaisesRegex(ValueError,message):m.summarize(b,f,v,root/'out','Z9')
                self.assertFalse((root/'out/sample.json').exists())
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);f,v,b=fixture(root)
            with self.assertRaisesRegex(ValueError,'Ordered BAM dictionary'):m.summarize(b,f,v,root/'bad','Z9',expected_dictionary='0'*64)
            m.summarize(b,f,v,root/'good','Z9')
            with (root/'good/moments.npy').open('ab') as stream:stream.write(b'corrupt')
            with self.assertRaisesRegex(ValueError,'Corrupt'):read_sample(root/'good',f,v,'Z9')
        cfg=m.policy();cfg['min_base_quality']=20
        with self.assertRaisesRegex(ValueError,'Unfrozen'):m.policy(cfg)


if __name__=='__main__':unittest.main()
