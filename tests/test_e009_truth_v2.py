"""Fresh truth contracts on explicit tiny DNA/PAF, without running any aligner or fit."""
import hashlib
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e009_common import binding
from e009_truth_v2 import paf_row, parse_paf, reconcile_one, reference_axes, split_circular

POLICY = {'aligned_query_bp_min': 200, 'identity_min': .99}


def row(cigar='300=', *, nn=0, matches=300, block=300, qs=0, qe=300, rs=100, re_=400, strand='+', nm=0):
    """Build explicit native-tag rows; each test states counts/endpoints independently."""
    return '\t'.join(map(str,['q',300,qs,qe,strand,'r',1000,rs,re_,matches,block,0]))+f'\tcg:Z:{cigar}\tnn:i:{nn}\tNM:i:{nm}\n'


class TruthContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.alias = {'length':1000,'genome':'A','canonical_id':'r','offset':0}

    def parse(self,text):
        p=self.root/'input.paf';p.write_text(text)
        return parse_paf(p,{'q':300},{'r':self.alias},POLICY)

    def test_native_ambiguous_deletion_insertion_mismatch_and_NN_equal(self):
        # Tiny DNA contracts: N in D/I, N:A in X, and N:N in =. The writer
        # excludes N from blen/mlen but its eqx converter can emit '=' for N:N.
        for text in [row('150=1D150=',nn=1,block=300,re_=401,nm=1),
                     row('149=1I150=',nn=1,matches=299,block=299,re_=399,nm=1),
                     row('149=1X150=',nn=1,matches=299,block=299,nm=1),
                     row('300=',nn=1,matches=299,block=299,nm=1)]:
            blocks,vetoes,counts=self.parse(text)
            self.assertFalse(blocks);self.assertEqual(vetoes['q'],[[0,300]])
            self.assertEqual(counts['quarantined_rows'],1)
        clean,vetoes,_=self.parse(row('149=1X150=',matches=299,nm=1))
        self.assertEqual(sum(v['q1']-v['q0']for v in clean['q']),300);self.assertFalse(vetoes)

    def test_actual_native_failure_row_and_strict_bad_row_refusal_before_filter(self):
        record=json.loads((Path(__file__).parents[1]/'experiments/E009-competitive-benchmark/truth-failure-example.json').read_text())
        raw=record['paf']+'\n'
        result=paf_row(raw,{'k141_73461':2792},{'G000644R000085':{'length':58312}})
        self.assertEqual(result[8],1)
        for bad in [raw.replace('nn:i:1','nn:i:0'), raw.replace('nn:i:1','nn:f:1'),
                    raw.replace('NM:i:156','NM:i:155'),raw.replace('933=','932='),
                    raw.replace('1859=','1859M'),raw+'\tcg:Z:1=',
                    raw.replace('nn:i:1','nn:i:-1'),raw.replace('\t2792\t2947\t','\t2791\t2947\t')]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                paf_row(bad,{'k141_73461':2792},{'G000644R000085':{'length':58312}})

    def test_veto_is_global_and_does_not_erase_competition_into_false_support(self):
        clean,_,_=self.parse(row())
        item=reconcile_one(300,clean['q'],[[20,40]])
        self.assertEqual(item['nn_quarantined_query_bp'],20)
        self.assertEqual(item['confirmed_query_bp'],{'A':280})
        self.assertIsNone(item['AMBER_label'])
        self.assertEqual(item['source_intervals'],{'r':[[100,120],[140,400]]})

    def test_forward_reverse_wrap_alias_duplicates_and_true_repeats(self):
        alias=dict(self.alias,length=100,offset=80)
        for strand,expected in [('+',[(0,20,80,100),(20,40,0,20)]),
                                ('-',[(20,40,80,100),(0,20,0,20)])]:
            values=split_circular(0,40,0,'alias',strand,alias)
            self.assertEqual([(v['q0'],v['q1'],v['r0'],v['r1'])for v in values],expected)
            duplicate=split_circular(0,40,0,'alias',strand,alias)
            result=reconcile_one(40,values+duplicate,[])
            self.assertEqual(result['source_intervals'],{'r':[[0,20],[80,100]]})
            self.assertEqual(result['repeat_locus_query_bp'],0)
            other=split_circular(0,40,1,'alias',strand,alias)
            repeated=reconcile_one(40,values+other,[])
            self.assertEqual(repeated['repeat_locus_query_bp'],40)
            self.assertEqual(repeated['source_intervals'],{})

    def test_full_population_denominators_HOST_and_zero_origin_competitors(self):
        dna='ACGTTGCATG'; names=['0circle','1circle']
        path=self.root/'plasmid.permuted.fna';path.write_text('>0circle\n'+dna+'\n>1circle\n'+dna[3:]+dna[:3]+'\n')
        catalog={'files':[{'name':path.name,'file':binding(path),'replicons':[
            {'replicon_id':k,'length':10,'DNA_sha256':hashlib.sha256(s.encode()).hexdigest()}
            for k,s in zip(names,[dna,dna[3:]+dna[:3]])]},
            {'name':'host.fna','replicons':[{'replicon_id':'host1','length':200000},{'replicon_id':'host_unobserved','length':1000}]},
            {'name':'virus.fna','replicons':[{'replicon_id':'virus','length':800}]}]}
        axis={'reference_axis':{r:{'genome':n,'original_replicon_id':i,'length':l}for r,n,i,l in
              [('p0',path.name,names[0],10),('p1',path.name,names[1],10),('h0','host.fna','host1',200000),
               ('h1','host.fna','host_unobserved',1000),('v0','virus.fna','virus',800)]}}
        pg={'pASV':{'source_files':[path.name],'HOST':'ASV','lineage_class':'other','positive_read_records':2,
                    'literal_provided_bp':20,'one_copy_provided_bp':10},
            'ASV':{'source_files':['host.fna'],'HOST':'','lineage_class':'bacterial','positive_read_records':10,
                   'literal_provided_bp':201000,'one_copy_provided_bp':201000}}
        audit={'all_origin_source_taxonomy_joins_resolved':True,'sets_equal':True,
               'multiple_genome_source_records':{},'multiple_genome_source_files':{},
               'source_file_to_observed_genomes':{path.name:['pASV'],'host.fna':['ASV']},
               'positive_genomes':{g:dict(v,read_records=v['positive_read_records'])for g,v in pg.items()}}
        pop={'genomes':pg,'selected_source_files_without_positive_origins':['virus.fna']}
        aliases,refs,genomes,circular=reference_axes(axis,catalog,audit,pop,self.root)
        self.assertEqual(aliases['p1']['genome'],'pASV');self.assertEqual(aliases['p1']['offset'],3)
        self.assertEqual(len(refs),4);self.assertEqual(genomes['ASV']['one_copy_provided_bp'],201000)
        self.assertEqual(genomes['pASV']['HOST'],'ASV');self.assertIn('zero_origin::virus.fna',genomes)
        path.write_text(path.read_text().replace('ACGTT','ACGTA'))
        with self.assertRaisesRegex(ValueError,'bytes drift'):reference_axes(axis,catalog,audit,pop,self.root)

    def test_sweep_matches_independent_per_base_oracle_and_permutation(self):
        random.seed(221)
        for case in range(80):
            values=[];size=35
            for _ in range(12):
                a=random.randrange(size);b=random.randint(a+1,size);r=random.randrange(80)
                values.append({'q0':a,'q1':b,'r0':r,'r1':r+b-a,'strand':random.choice('+-'),
                               'rid':random.choice(['a','b']),'genome':random.choice(['A','B'])})
            vetoes=[[3,8],[7,11]];result=reconcile_one(size,values,vetoes)
            confirmed=Counter();ambiguous=repeat=quarantine=0;loci=defaultdict(set)
            for q in range(size):
                if any(a<=q<b for a,b in vetoes):quarantine+=1;continue
                active=[v for v in values if v['q0']<=q<v['q1']];gs={v['genome']for v in active}
                if len(gs)>1:ambiguous+=1;continue
                if not gs:continue
                confirmed[next(iter(gs))]+=1
                positions={(v['rid'],v['r0']+q-v['q0']if v['strand']=='+'else v['r0']+v['q1']-1-q,v['strand'])for v in active}
                if len(positions)>1:repeat+=1
                else:
                    rid,pos,_=next(iter(positions));loci[rid].add(pos)
            self.assertEqual(result['confirmed_query_bp'],dict(confirmed))
            self.assertEqual([result[k]for k in ['ambiguous_query_bp','repeat_locus_query_bp','nn_quarantined_query_bp']],
                             [ambiguous,repeat,quarantine])
            self.assertEqual({r:{p for a,b in spans for p in range(a,b)}for r,spans in result['source_intervals'].items()},dict(loci))
            random.shuffle(values);self.assertEqual(reconcile_one(size,values+values,vetoes),result)


from collections import Counter, defaultdict
if __name__=='__main__':unittest.main()
