"""Refuse incomplete physical-template population evidence in E034 review."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parents[1]/'scripts'))
from e034_pilot_review import counter_contract


class TemplateAccountingTests(unittest.TestCase):
    def valid(self):
        """Include an earlier accepted read in a later-refused two-mate group."""
        return dict(templates=10,qualified_both_mates=6,
            template_identity_exclusion=3,template_flag_exclusion=1,
            calibration_eligible_templates=4,cross_contig_qualified_templates=1,
            accepted_reads=15,accepted_aligned_bases=2250)

    def test_closes_templates_without_mistaking_partial_read_counters_for_pairs(self):
        result=counter_contract(self.valid())
        self.assertEqual(result['exactly_two_record_fraction'],1)
        self.assertEqual(result['qualified_same_contig_other_orientation_or_over_insert'],1)
        self.assertEqual(result['terminal_rejection_fractions']['template_identity_exclusion'],.3)

    def test_missing_or_duplicated_terminal_outcome_is_refused(self):
        for qualified in [5,7]:
            value=self.valid();value['qualified_both_mates']=qualified
            with self.assertRaisesRegex(ValueError,'do not close'):counter_contract(value)

    def test_split_qname_groups_remain_join_failures(self):
        value=self.valid();value['templates']=11;value['template_record_count_not_two']=1
        self.assertAlmostEqual(counter_contract(value)['exactly_two_record_fraction'],10/11)

    def test_malformed_counter_is_refused(self):
        for count in [-1,True,1.0]:
            value=self.valid();value['accepted_reads']=count
            with self.assertRaisesRegex(ValueError,'Invalid template counter'):counter_contract(value)

    def test_empty_or_overlapping_qualification_population_is_refused(self):
        for patch in [dict(templates=0),dict(calibration_eligible_templates=6)]:
            value=self.valid();value.update(patch)
            with self.assertRaises(ValueError):counter_contract(value)


if __name__=='__main__':unittest.main()
