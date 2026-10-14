"""Protect evaluator admission against count-only IDs and guessed source/taxon joins."""
import importlib.util
import gzip
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('e009_data_review',Path(__file__).resolve().parents[1]/'scripts/e009_data_review.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


class DataReviewTests(unittest.TestCase):
    def test_unordered_exact_set_and_late_duplicate(self):
        ids=mod.ReadIDs(2)
        for value in ['S0R1/2','S0R0/1','S0R1/1','S0R0/2']:ids.add(value)
        self.assertEqual(ids.finish()['records'],4)
        with self.assertRaisesRegex(ValueError,'Duplicate'):ids.add('S0R1/2')
        with self.assertRaisesRegex(ValueError,'outside'):mod.ReadIDs(2).add('S0R2/1')
        with self.assertRaisesRegex(ValueError,'Noncanonical'):mod.ReadIDs(2).add('S0R00/1')
        with self.assertRaisesRegex(ValueError,'Incomplete'):mod.ReadIDs(2).finish()

    def test_source_format_requires_exact_unambiguous_member(self):
        records={'NC_1.1':{},'NC_1.1_part':{}}
        self.assertEqual(mod.source_id('NC_1.1-123/1',records),'NC_1.1')
        self.assertEqual(mod.source_id('NC_1.1_part_1_2_0:0:0_0:0:0_30/1',records),'NC_1.1_part')
        with self.assertRaisesRegex(ValueError,'Unknown/ambiguous'):mod.source_id('NC_1.2-123/1',records)
        both={'prefix':{},'prefix-x':{}}
        with self.assertRaisesRegex(ValueError,'Unknown/ambiguous'):mod.source_id('prefix-x_a_b_c_d_e',both)

    def test_provider_lineage_and_synthetic_strain_preserved(self):
        with tempfile.TemporaryDirectory()as tmp:
            path=Path(tmp)/'profile.txt';header='@SampleID:0\n@@TAXID\tRANK\tTAXPATH\tTAXPATHSN\tPERCENTAGE\t_CAMI_genomeID\t_CAMI_OTU\tHOST\n'
            row='817.9\tstrain\t131567|2|817|817.9\tcellular organisms|Bacteria|Bacteroides fragilis|strain\t0.0000\tASV1\t817\t\n'
            path.write_text(header+row)
            value=mod.profiles(path)['ASV1'];self.assertEqual(value['TAXID'],'817.9');self.assertEqual(value['lineage_class'],'bacterial')
            path.write_text(header+row.replace('Bacteria','Viruses'))
            with self.assertRaisesRegex(ValueError,'ID/name mismatch'):mod.profiles(path)

    def test_real_gzip_manifests_exact_join_and_source_drift(self):
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp)/'work';source=root/'parts/sources';reads=root/'parts/reads_0000'
            source.mkdir(parents=True);(reads/'reads').mkdir(parents=True);(reads/'evaluator-inputs').mkdir()
            def write(path,value):path.write_text(json.dumps(value))
            catalog=source/'catalog.json';axis=source/'reference.fna.axis.json'
            write(catalog,{'files':[{'name':'shared-file.fna','replicons':[{'replicon_id':'NC_1.1','length':4},{'replicon_id':'NC_2.1','length':4}]}]})
            write(axis,{'reference_axis':{'R1':{'original_replicon_id':'NC_1.1'},'R2':{'original_replicon_id':'NC_2.1'}}})
            fq=reads/'reads/anonymous.fq.gz'
            with gzip.open(fq,'wt')as f:
                for i in range(2):
                    for mate in [1,2]:f.write(f'@S0R{i}/{mate}\nACGT\n+\nIIII\n')
            origin=reads/'evaluator-inputs/reads_mapping.tsv.gz'
            with gzip.open(origin,'wt')as f:
                f.write('#anonymous_read_id\tgenome_id\ttax_id\tread_id\n')
                for i in [1,0]:
                    for mate in [2,1]:f.write(f'S0R{i}/{mate}\tASV{i+1}\t817\tNC_{i+1}.1-3/{mate}\n')
            write(source/'done.json',{'files':{str(p.relative_to(source)):mod.bind(p)for p in [catalog,axis]},'payload':{'catalog':str(catalog),'axis':str(axis)}})
            write(reads/'done.json',{'files':{str(p.relative_to(reads)):mod.bind(p)for p in [fq,origin]},'payload':{'first':str(fq),'second':None,'validation':{'pairs':2}}})
            profile=Path(tmp)/'profile.txt';profile.write_text('@SampleID:0\n@@TAXID\tRANK\tTAXPATH\tTAXPATHSN\tPERCENTAGE\t_CAMI_genomeID\t_CAMI_OTU\tHOST\n'+''.join(
                f'817.{i}\tstrain\t131567|2|817|817.{i}\tcellular organisms|Bacteria|Bacteroides fragilis|strain\t0.0000\tASV{i}\t817\t\n'for i in [1,2]))
            result=mod.review(root,profile,Path(tmp)/'review')
            self.assertTrue(result['sets_equal']);self.assertFalse(result['scientific_truth_admitted'])
            self.assertEqual(result['read_records_by_lineage'],{'bacterial':4})
            self.assertEqual(result['multiple_genome_source_files'],{'shared-file.fna':['ASV1','ASV2']})
            catalog.write_text(catalog.read_text()+' ')
            with self.assertRaisesRegex(ValueError,'Consumed sealed bytes changed'):
                mod.review(root,profile,Path(tmp)/'drift-review')


if __name__=='__main__':unittest.main()
