"""Test placement categories and BAM parsing without scientific read inputs."""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from e001_mapper_diagnostics import compare, read_alignments, truth_comparison


class DiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.contigs = {"a": {"length": 1000, "origins": ["g1"]},
                        "b": {"length": 1000, "origins": ["g1", "g2"]},
                        "c": {"length": 1000, "origins": ["g3"]}}

    def record(self, contig="a", start=0, seq="A" * 10):
        return {"position": (contig, start, False), "mapq": 1, "cigar": "10M", "sequence": seq}

    def test_categories_partition_reads_without_claiming_truth(self):
        a = {(str(i), 1): self.record() for i in range(5)}
        b = {("0", 1): self.record(), ("1", 1): self.record(start=5),
             ("2", 1): self.record("b"), ("3", 1): self.record("c"), ("5", 1): self.record()}
        result = compare(a, b, self.contigs, 8)
        self.assertEqual(result["categories"], {"both_unmapped": 2, "same_position": 1,
                         "same_contig_other_position": 1, "different_contig_shared_origin": 1,
                         "different_contig_disjoint_origins": 1, "strobealign_only": 1, "bowtie2_only": 1})

    def test_sequence_mismatch_stops(self):
        with self.assertRaisesRegex(ValueError, "sequence differs"):
            compare({("r", 1): self.record()}, {("r", 1): self.record(seq="C" * 10)}, self.contigs, 2)

    def test_unknown_missing_read_count_stops(self):
        with self.assertRaisesRegex(ValueError, "More mapped"):
            compare({("r", 1): self.record()}, {}, self.contigs, 0)

    def test_bam_tags_and_duplicate_guard(self):
        import pysam
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mapped.bam"
            header = {"SQ": [{"SN": k, "LN": v["length"]} for k, v in self.contigs.items()]}
            def write(count):
                with pysam.AlignmentFile(path, "wb", header=header) as bam:
                    for _ in range(count):
                        r = pysam.AlignedSegment()
                        r.query_name, r.query_sequence, r.flag = "r", "A" * 10, 65
                        r.reference_id, r.reference_start, r.mapping_quality, r.cigarstring = 0, 0, 1, "10M"
                        r.set_tag("AS", 0); r.set_tag("XS", 0); r.set_tag("NM", 0)
                        bam.write(r)
            write(1)
            records, counts, hist = read_alignments(path, self.contigs)
            self.assertEqual(len(records), 1)
            self.assertEqual(hist["AS_minus_XS"]["0"], 1)
            self.assertEqual(counts["a"], 1)
            write(2)
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                read_alignments(path, self.contigs)

    def test_truth_join_and_ambiguous_destination(self):
        import gzip
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "truth.gz"
            def write(body):
                with gzip.open(path, "wt") as out:
                    out.write("#anonymous_read_id\tgenome_id\ttax_id\tread_id\n" + body)
            data = {"strobealign": ({("r", 1): self.record("b")}, {}, {}),
                    "bowtie2": ({("r", 1): self.record("c")}, {}, {})}
            write("r/1\tg2\t1\toriginal\n")
            result = truth_comparison(path, data, self.contigs)
            self.assertEqual(result["joint_on_mapped_union"]["strobe_1_bowtie_0"], 1)
            write("r/1\tg2\t1\toriginal\nr/1\tg2\t1\toriginal\n")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                truth_comparison(path, data, self.contigs)
            write("other/1\tg2\t1\toriginal\n")
            with self.assertRaisesRegex(ValueError, "Missing"):
                truth_comparison(path, data, self.contigs)


if __name__ == "__main__":
    unittest.main()
