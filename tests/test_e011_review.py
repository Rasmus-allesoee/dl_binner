"""Independent return-byte and all-DNA grouping/evaluator contracts for E011."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e011_review import verify_return, grouping_diagnostics, verify_native_members, verify_refinement_inputs
from e009_common import binding


class ReturnReviewTests(unittest.TestCase):
    def test_loaded_files_stay_exact_while_ldd_addresses_vary(self):
        before = dict(version='2.18',system='Linux',binary='/prefix/bin/metabat2',help='same CLI',
                      execution_members={'/prefix/libz.so.1':{'resolved_path':'/prefix/libz.so.1.3','content':'same SHA256'}},
                      member_scope='loaded ELF files and aliases',library_report='libz at (0x1234)')
        after = dict(before, library_report='libz at (0x9876)')
        verify_native_members(before, after)
        with self.assertRaisesRegex(ValueError,'loaded members changed'):
            verify_native_members(before,dict(after,execution_members={'/prefix/libz.so.1':{'content':'changed SHA256'}}))
        with self.assertRaisesRegex(ValueError,'schema changed'):
            verify_native_members(before,dict(after,unexpected='drift'))

    def test_actual_refinement_schema_uses_bindings_without_copied_config(self):
        pre = dict(parent_features_sha256='features',neighbors=[['other']])
        post = dict(pre_partition_sha256='pre',marker_cache_sha256='cache',
                    parent_features_sha256='features',neighbors=[['other']])
        verify_refinement_inputs(pre,post,'pre','features','cache')
        for key,value in [('pre_partition_sha256','changed'),('marker_cache_sha256','changed'),
                          ('parent_features_sha256','changed'),('neighbors',[[]])]:
            with self.subTest(key=key), self.assertRaisesRegex(ValueError,'refinement inputs differ'):
                verify_refinement_inputs(pre,dict(post,**{key:value}),'pre','features','cache')

    def test_retained_seed_audit_separates_whole_contig_overlap_and_protein_bytes(self):
        import importlib.util
        source=Path(__file__).parents[1]/'experiments/E011-cached-grouping-reference/review_diagnostics.py'
        spec=importlib.util.spec_from_file_location('e011_extra',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory()as d:
            p=Path(d);genes=[dict(gene='g1',partial_begin=False,partial_end=False),dict(gene='g2',partial_begin=False,partial_end=False)]
            (p/'genes.jsonl').write_text(''.join(json.dumps(g)+'\n'for g in genes))
            (p/'proteins.faa').write_text('>g1\nAAA\nCCC\n>g2\nTTTTTT\n')
            truth={'contigs':{'a':dict(AMBER_label='G',confirmed_query_bp={'G':100},source_intervals={'r':[[0,100]]}),
                              'b':dict(AMBER_label='G',confirmed_query_bp={'G':100},source_intervals={'r':[[200,300]]})}}
            marker={'calls':[dict(contig='a',gene='g1',family='F'),dict(contig='b',gene='g2',family='F')]}
            changed=[dict(genome='G',pre=dict(recovered_bp=200,confirmed_purity=1),post=dict(recovered_bp=100),
                          pre_bin_refinement_proposal=[dict(pre_bin=1,seed_ids=['a','b'],seed_family='F')])]
            result=module.seed_audit(changed,truth,marker,p)['lost_passing_bins'][0]
            self.assertEqual(result['whole_contig_reference_overlap_bp'],0)
            self.assertFalse(result['same_marker_protein_bytes'])
            self.assertEqual(result['genes']['g1']['protein_sha256'],hashlib.sha256(b'AAACCC').hexdigest())
            truth['contigs']['b']['source_intervals']['r']=[[50,150]]
            self.assertEqual(module.seed_audit(changed,truth,marker,p)['lost_passing_bins'][0]['whole_contig_reference_overlap_bp'],50)

    def test_every_member_and_unsafe_paths_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); files={'science':b'bound partition','unused-log':b'also verified'}
            def create(tag, changed=False, unsafe=False):
                archive=root/(tag+'.tar.gz'); inventory={'files':{k:dict(bytes=len(v),sha256=hashlib.sha256(v).hexdigest())for k,v in files.items()}}
                raw=json.dumps(inventory).encode(); payload=dict(files,**{'collection-inventory.json':raw})
                if changed:payload['unused-log']=b'corrupt log bytes'
                if unsafe:payload['../escape']=b'bad'
                with tarfile.open(archive,'w:gz') as tar:
                    for name,data in payload.items():
                        member=tarfile.TarInfo(name);member.size=len(data);tar.addfile(member,io.BytesIO(data))
                checksum=root/(tag+'.sha256');checksum.write_text(binding(archive)['sha256']+'  '+archive.name+'\n')
                completion={'control_archive':dict(**binding(archive),collection=dict(archive=binding(archive),inventory=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()),members=len(payload),logical_member_bytes=sum(map(len,payload.values()))))}
                return archive,checksum,completion,root/(tag+'-return')
            self.assertEqual(verify_return(*create('valid'))['regular_members'],3)
            with self.assertRaisesRegex(ValueError,'member differs: unused-log'):verify_return(*create('changed',changed=True))
            with self.assertRaisesRegex(ValueError,'Unsafe'):verify_return(*create('unsafe',unsafe=True))

    def test_unknown_dna_stays_in_full_bin_purity_and_all_statuses(self):
        def item(bp,label,start=0):
            return dict(length=bp,AMBER_label=label,confirmed_query_bp={label:bp}if label else{},
                source_intervals={'r1':[[start,start+bp]]}if label else{},ambiguous_query_bp=0,
                nn_quarantined_query_bp=50000 if label is None else 0,unsupported_query_bp=150000 if label is None else 0)
        truth=dict(ordered_contig_ids=['a','b','unknown'],contigs=dict(a=item(600000,'g1'),b=item(400000,'g1',600000),unknown=item(200000,None)),reference_axis={'r1':dict(genome='g1',length=1000000)})
        rows=[dict(contig_id=q,length=i['length'],bin_id='bin'if q!='b'else'',status='assigned'if q!='b'else'unassigned')for q,i in truth['contigs'].items()]
        pop={'genomes':{'g1':{'lineage_class':'primary_bacterial'}}};targets={'genome_lengths':{'g1':1000000},'targets':['g1']}
        mixed=grouping_diagnostics(truth,rows,pop,targets,['a'])
        self.assertEqual(mixed['recovery_summary']['bp_weighted_R95'],0)
        self.assertEqual(mixed['bins'][0]['all_DNA_confirmed_purity'],.75)
        self.assertAlmostEqual(mixed['restricted_B3']['precision'],.6)
        self.assertAlmostEqual(mixed['restricted_B3']['recall'],.36)
        self.assertEqual(sum(s['all_bp']for s in mixed['statuses'].values()),1200000)
        self.assertEqual(mixed['origin_by_status']['assigned']['nn_quarantined_query_bp'],50000)
        self.assertEqual(mixed['clean_marker_by_status']['no_clean_marker']['assigned_bp'],200000)
        rows[-1].update(bin_id='',status='unassigned')
        pure=grouping_diagnostics(truth,rows,pop,targets,['a'])
        self.assertEqual(pure['recovery_summary']['bp_weighted_R95'],.6)
        self.assertEqual(pure['recovery'][0]['reference_bp'],1000000)


if __name__=='__main__':unittest.main()
