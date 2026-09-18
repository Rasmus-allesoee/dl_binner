"""Portable E001 contracts. Native-library parity is a separate Linux smoke gate."""

import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pysam

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from e001lib.acquire import archive_inventory, download_inventory
from e001lib.metrics import neighbor_purity, score
from e001lib.native import (mapping_commands, metabat_commands, run_checked, scale_comebin, scale_metabat_depth,
                            thinning_command, validate_comebin_pair, verify_source)
from e001lib.records import ContractError, EXPERIMENT, config, digest, partition, prepare_hmp, sequences, table, truth_table, validate_attempt, write_cami, write_json
from e001lib.smoke import bam_inventory, check_interleaved, check_thinned_fixture, make_fixture


class Files(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def file(self, name, text):
        path = self.root / name
        path.write_text(text)
        return path


class MetricTests(unittest.TestCase):
    def setUp(self):
        self.lengths = {"a1": 200000, "a2": 200000, "b1": 200000, "b2": 200000}
        self.pop = {"lengths": self.lengths, "unique_origins": {s: s[0] for s in self.lengths}, "genomes": ["a", "b"]}

    def test_perfect(self):
        self.assertEqual(score(self.pop, {s: s[0] for s in self.lengths})["r95"], 1)

    def test_merge(self):
        self.assertEqual(score(self.pop, {s: "x" for s in self.lengths})["r95"], 0)

    def test_split_penalty(self):
        result = score(self.pop, {s: s for s in self.lengths})
        self.assertEqual(result["r95"], .5)
        self.assertEqual(result["inclusive_recovered_counts"], {"0.5": 2, "0.9": 0})

    def test_missing_genome_stays_zero(self):
        self.assertEqual(score(self.pop, {"a1": "a", "a2": "a"})["r95"], .5)

    def test_unassigned_accounting(self):
        result = score(self.pop, {"a1": "a", "a2": "a", "b1": "b"})
        self.assertEqual(result["r95"], .75)
        self.assertEqual(result["assigned_bp"] + result["unassigned_bp"], 800000)

    def test_legal_empty_output(self):
        self.assertEqual(score(self.pop, {})["r95"], 0)
        self.assertEqual(score(self.pop, {})["unassigned_bp"], 800000)
        self.assertIsNone(score(self.pop, {})["per_genome"]["a"]["confirmed_purity"])

    def test_unknown_prediction(self):
        with self.assertRaises(ContractError):
            score(self.pop, {"wrong": "a"})

    def test_ambiguous_bases_remain_in_purity(self):
        self.pop["lengths"]["ambiguous"] = 100000
        result = score(self.pop, {"a1": "a", "a2": "a", "ambiguous": "a", "b1": "b", "b2": "b"})
        self.assertEqual(result["r95"], .5)
        self.assertEqual(result["ambiguous_or_unscored_assigned_bp"], 100000)

    def test_inclusive_purity_and_bin_size_boundary(self):
        pop = {"lengths": {"a": 190000, "a_missed": 10000, "unscored": 10000}, "unique_origins": {"a": "g", "a_missed": "g"}, "genomes": ["g"]}
        self.assertEqual(score(pop, {"a": "bin", "unscored": "bin"})["r95"], .95)
        pop["lengths"]["unscored"] += 1
        self.assertEqual(score(pop, {"a": "bin", "unscored": "bin"})["r95"], 0)

    def test_short_strata_do_not_recalculate_purity(self):
        pop = {"lengths": {"short": 5000, "long": 200000, "unknown": 50000}, "unique_origins": {"short": "g", "long": "g"}, "genomes": ["g"]}
        result = score(pop, {"short": "x", "long": "x", "unknown": "x"})
        self.assertEqual(result["per_genome"]["g"]["length_strata"][1]["recovery"], 0)

    def test_tied_bins_have_stable_choice(self):
        result = score(self.pop, {"a1": "z", "a2": "x", "b1": "b", "b2": "b"})
        self.assertEqual(result["per_genome"]["a"]["bin"], "x")


class ContractTests(Files):
    def test_duplicate_fasta(self):
        with self.assertRaises(ContractError):
            list(sequences(self.file("bad.fa", ">a\nACGT\n>a\nACGT\n")))

    def test_invalid_sequence(self):
        for text in (">a\n", ">a\nACGTX\n", "not a fasta\n>a\nACGT\n"):
            with self.subTest(text=text), self.assertRaises(ContractError):
                list(sequences(self.file("bad.fa", text)))

    def test_multiorigin_truth_is_preserved(self):
        p = self.root / "truth.tsv"
        write_cami(p, {"s": 4}, origins={"s": ["a", "b"]})
        self.assertEqual(truth_table(p, {"s": 4}), {"s": ["a", "b"]})

    def test_truth_missing_wrong_length_or_duplicate(self):
        for rows in ("s\ta\t3\n", "s\ta\t4\ns\ta\t4\n", "wrong\ta\t4\n", ""):
            with self.subTest(rows=rows), self.assertRaises(ContractError):
                truth_table(self.file("bad.tsv", "@@SEQUENCEID\tBINID\tLENGTH\n" + rows), {"s": 4})

    def test_unknown_duplicate_and_overlapping_predictions(self):
        for rows in ("x\tb\n", "s\tb\ns\tb\n", "s\ta\ns\tb\n"):
            with self.subTest(rows=rows), self.assertRaises(ContractError):
                partition(self.file("bad.tsv", "@@SEQUENCEID\tBINID\n" + rows), {"s": 4})

    def test_empty_partition_is_valid(self):
        self.assertEqual(partition(self.file("empty.tsv", "@@SEQUENCEID\tBINID\n"), {"s": 4}), {})

    def test_missing_header_is_not_empty_result(self):
        with self.assertRaises(ContractError):
            partition(self.file("empty.tsv", ""), {"s": 4})

    def test_multiple_cami_samples_rejected(self):
        with self.assertRaises(ContractError):
            partition(self.file("bad.tsv", "@SampleID:a\n@@SEQUENCEID\tBINID\ns\ta\n@SampleID:b\n@@SEQUENCEID\tBINID\ns\tb\n"), {"s": 4})

    def test_native_layouts(self):
        lengths = {"s": 4, "unassigned": 4}
        examples = {"vamb": "clustername\tcontigname\nb\ts\n", "comebin": "s\tb\n", "metabat": "ContigName\tClusterId\ns\t1\nunassigned\t0\n"}
        for layout, text in examples.items():
            self.assertEqual(set(partition(self.file(layout, text), lengths, layout)), {"s"})

    def test_metadata_output_cannot_overwrite(self):
        p = self.root / "out.json"
        write_json(p, {"a": 1})
        with self.assertRaises(FileExistsError):
            write_json(p, {"a": 2})

    def test_crashed_attempt_is_not_zero_recovery(self):
        attempt = self.file("attempt.json", '{"status": "failed"}')
        with self.assertRaises(ContractError):
            validate_attempt(attempt, self.root / "missing.tsv", self.root / "missing.json")

    def test_attempt_output_hashes_required(self):
        assignment = self.file("assignment.tsv", "@@SEQUENCEID\tBINID\n")
        pop = self.file("population.json", "{}")
        record = {"status": "completed", "source_commit": "a" * 40, "assignment_sha256": digest(assignment), "population_sha256": digest(pop), "config_sha256": digest(EXPERIMENT / "config.json")}
        attempt = self.file("attempt.json", json.dumps(record))
        self.assertEqual(validate_attempt(attempt, assignment, pop), record)
        assignment.write_text("modified")
        with self.assertRaises(ContractError):
            validate_attempt(attempt, assignment, pop)


class HMPTests(Files):
    def setup_hmp(self, duplicate=False):
        first, second = "A" * 2600, ("T" * 2600 if duplicate else "C" * 2600)
        fasta = self.file("gsa.fa", f">ref_a_from_3_to_2602_total_2600\n{first}\n>ref_b_from_1_to_2600_total_2600\n{second}\n")
        header = "#anonymous_contig_id\tgenome_id\ttax_id\tcontig_id\tnumber_reads\tstart_position\tend_position\n"
        mapping = self.file("mapping.tsv", header + "PC0\tg1\t2\tref_a\t10\t3\t2602\nPC1\tg2\t2157\tref_b\t10\t1\t2600\n")
        nodes = self.file("nodes.dmp", "1\t|\t1\t|\tno rank\t|\n2\t|\t1\t|\tsuperkingdom\t|\n2157\t|\t1\t|\tsuperkingdom\t|\n")
        return fasta, mapping, nodes

    def test_coordinate_join_anonymizes_and_preserves_sequence(self):
        fasta, mapping, nodes = self.setup_hmp()
        report = prepare_hmp(fasta, mapping, self.root / "out", nodes)
        actual = dict(sequences(self.root / "out/canonical.fna"))
        self.assertEqual(actual, {"PC0": "A" * 2600, "PC1": "C" * 2600})
        self.assertTrue(report["gates"]["domains_resolved"])
        self.assertEqual(report["status"], "blocked")  # Toy fixture is too small for science.

    def test_reverse_complement_cross_origin_excluded(self):
        fasta, mapping, nodes = self.setup_hmp(True)
        prepare_hmp(fasta, mapping, self.root / "out", nodes)
        p = json.loads((self.root / "out/population.json").read_text())
        self.assertEqual(p["unique_origins"], {})
        self.assertEqual(len(p["lengths"]), 2)

    def test_coordinate_aliases_preserve_one_sequence_and_all_ids(self):
        fasta, mapping, nodes = self.setup_hmp()
        mapping.write_text(mapping.read_text().replace("PC0\t", "PC10\t") + "PC2\tg1\t2\tref_a\t10\t3\t2602\n")
        report = prepare_hmp(fasta, mapping, self.root / "out", nodes)
        self.assertEqual(dict(sequences(self.root / "out/canonical.fna")), {"PC2": "A" * 2600, "PC1": "C" * 2600})
        self.assertEqual(report["retained_bp"], 5200)
        self.assertEqual(report["coordinate_aliases"][0]["source_ids"], ["PC2", "PC10"])
        lines = mapping.read_text().splitlines()
        mapping.write_text("\n".join([lines[0], *reversed(lines[1:])]) + "\n")
        again = prepare_hmp(fasta, mapping, self.root / "reordered", nodes)
        self.assertEqual(again["coordinate_aliases"], report["coordinate_aliases"])

    def test_conflicting_alias_metadata_and_exact_duplicates_rejected(self):
        for row in ("PC0\tg1\t2\tref_a\t10\t3\t2602\n",
                    "PC2\tg1\t2\tref_a\t11\t3\t2602\n",
                    "PC2\tg3\t2\tref_a\t10\t3\t2602\n",
                    "PC2\tg1\t2157\tref_a\t10\t3\t2602\n"):
            fasta, mapping, nodes = self.setup_hmp()
            mapping.write_text(mapping.read_text() + row)
            with self.assertRaises(ContractError):
                prepare_hmp(fasta, mapping, self.root / "out", nodes)

    def test_same_id_multiple_genomes_remains_ambiguous(self):
        fasta, mapping, nodes = self.setup_hmp()
        mapping.write_text(mapping.read_text() + "PC0\tg3\t2\tref_a\t10\t3\t2602\n")
        report = prepare_hmp(fasta, mapping, self.root / "out", nodes)
        self.assertEqual(report["coordinate_aliases"], [])
        population = json.loads((self.root / "out/population.json").read_text())
        self.assertNotIn("PC0", population["unique_origins"])

    def test_alias_below_cutoff_is_recorded_but_not_retained(self):
        fasta, mapping, nodes = self.setup_hmp()
        fasta.write_text(fasta.read_text().replace("to_2602_total_2600", "to_2468_total_2466").replace("A" * 2600, "A" * 2466))
        mapping.write_text(mapping.read_text().replace("\t2602", "\t2468") + "PC2\tg1\t2\tref_a\t10\t3\t2468\n")
        report = prepare_hmp(fasta, mapping, self.root / "out", nodes)
        self.assertFalse(report["coordinate_aliases"][0]["retained"])
        self.assertEqual(report["retained_bp"], 2600)

    def test_known_empty_orphans_are_recorded_and_skipped(self):
        fasta, mapping, nodes = self.setup_hmp()
        fasta.write_text(fasta.read_text() + ">*from__to*-42_total_0\n\n>*from__to*-42_total_0\n\n")
        report = prepare_hmp(fasta, mapping, self.root / "out", nodes)
        self.assertEqual(len(report["excluded_fasta_records"]), 2)
        self.assertEqual(report["excluded_fasta_records"][0]["reason"], "known_empty_orphan")
        self.assertEqual(len(list(sequences(self.root / "out/canonical.fna"))), 2)
        self.assertEqual(json.loads((self.root / "out/excluded-fasta.json").read_text()), report["excluded_fasta_records"])

    def test_converter_normalized_empty_orphan_is_recorded_and_skipped(self):
        fasta, mapping, nodes = self.setup_hmp()
        fasta.write_text(fasta.read_text() + ">_from__to_-42_total_0\n\n")
        report = prepare_hmp(fasta, mapping, self.root / "out", nodes)
        self.assertEqual(report["excluded_fasta_records"][0]["id"], "_from__to_-42_total_0")
        self.assertEqual(report["excluded_fasta_records"][0]["reason"], "known_empty_orphan")

    def test_known_orphan_with_sequence_is_rejected(self):
        fasta, mapping, nodes = self.setup_hmp()
        fasta.write_text(fasta.read_text() + ">*from__to*-42_total_0\nACGT\n")
        with self.assertRaises(ContractError):
            prepare_hmp(fasta, mapping, self.root / "out", nodes)

    def test_unresolved_domain_blocks_freeze(self):
        fasta, mapping, _ = self.setup_hmp()
        result = prepare_hmp(fasta, mapping, self.root / "out")
        self.assertFalse(result["gates"]["domains_resolved"])

    def test_original_broken_mapping_rejected(self):
        fasta, mapping, nodes = self.setup_hmp()
        mapping.write_text(mapping.read_text() + "PC1\tg1\t2\tref_a\t10\t3\t2602\n")
        with self.assertRaises(ContractError):
            prepare_hmp(fasta, mapping, self.root / "out", nodes)

    def test_length_mismatch_rejected(self):
        fasta, mapping, nodes = self.setup_hmp()
        fasta.write_text(fasta.read_text().replace("total_2600", "total_2599", 1))
        with self.assertRaises(ContractError):
            prepare_hmp(fasta, mapping, self.root / "out", nodes)

    def test_truth_coordinate_missing_from_fasta(self):
        fasta, mapping, nodes = self.setup_hmp()
        mapping.write_text(mapping.read_text() + "PC2\tg1\t2\tref_c\t10\t1\t4\n")
        with self.assertRaises(ContractError):
            prepare_hmp(fasta, mapping, self.root / "out", nodes)


class AcquisitionTests(Files):
    def archive(self, name, member_name, kind=tarfile.REGTYPE):
        path = self.root / name
        with tarfile.open(path, "w") as tar:
            entry = tarfile.TarInfo(member_name)
            entry.type = kind
            entry.size = 3 if kind == tarfile.REGTYPE else 0
            tar.addfile(entry, io.BytesIO(b"abc") if entry.size else None)
        return path

    def test_regular_archive_inventory(self):
        result = archive_inventory(self.archive("ok.tar", "data/file.tsv"))
        self.assertEqual(result["unpacked_bytes"], 3)

    def test_traversal_absolute_and_links_rejected(self):
        for name, kind in (("../escape", tarfile.REGTYPE), ("/absolute", tarfile.REGTYPE), ("link", tarfile.SYMTYPE), ("hard", tarfile.LNKTYPE)):
            with self.subTest(name=name), self.assertRaises(ContractError):
                archive_inventory(self.archive("bad.tar", name, kind))

    def test_archive_size_ceiling(self):
        with self.assertRaises(ContractError):
            archive_inventory(self.archive("big.tar", "file"), max_unpacked=2)

    def test_duplicate_archive_paths_rejected(self):
        path = self.root / "duplicates.tar"
        with tarfile.open(path, "w") as tar:
            tar.addfile(tarfile.TarInfo("same"), io.BytesIO())
            tar.addfile(tarfile.TarInfo("./same"), io.BytesIO())
        with self.assertRaises(ContractError):
            archive_inventory(path)

    def test_acquire_default_does_not_download(self):
        with patch("e001lib.acquire.urlopen", side_effect=AssertionError("Network forbidden")):
            result = download_inventory(self.root / "not_created")
        self.assertEqual(result["status"], "plan_only")
        self.assertFalse((self.root / "not_created").exists())
        self.assertFalse(any("sample_" in r["path"] for r in result["files"]))

    def mocked_download(self, expected_md5=None, max_bytes=100000):
        payload = self.archive("source.tar", "metadata.tsv").read_bytes()
        spec = {"base_url": "https://example.invalid/", "inventory_files": [{"path": "gastrooral/setup.tar.gz", "md5": expected_md5 or hashlib.md5(payload).hexdigest(), "max_bytes": max_bytes}]}
        self.file("acquisition.json", json.dumps(spec))
        response = io.BytesIO(payload)
        response.status = 200
        with patch("e001lib.acquire.EXPERIMENT", self.root), patch("e001lib.acquire.urlopen", return_value=response), patch("e001lib.acquire.shutil.disk_usage", return_value=SimpleNamespace(free=20_000_000_000)):
            return download_inventory(self.root / "download", execute=True)

    def test_download_checks_identity_before_success(self):
        result = self.mocked_download()
        self.assertTrue(result["files"][0]["publisher_checksum_verified"])
        self.assertTrue((self.root / "download/setup-members.json").exists())
        self.assertEqual(result["reads"], "not downloaded")

    def test_wrong_download_checksum_keeps_partial_and_no_success_marker(self):
        with self.assertRaises(ContractError):
            self.mocked_download(expected_md5="0" * 32)
        self.assertTrue((self.root / "download/gastrooral/setup.tar.gz.part").exists())
        self.assertFalse((self.root / "download/acquisition-report.json").exists())

    def test_download_size_limit(self):
        with self.assertRaises(ContractError):
            self.mocked_download(max_bytes=2)
        self.assertFalse((self.root / "download/acquisition-report.json").exists())


class AdapterTests(Files):
    def test_mapping_alignment_not_abundance_or_paf(self):
        commands = mapping_commands("ref.fna", "reads.fq", "GI0", "out.bam")
        self.assertIn("--interleaved", commands[0])
        self.assertNotIn("--aemb", commands[0])
        self.assertNotIn("-x", commands[0])
        self.assertIn("2308", commands[1])
        self.assertNotIn("--interleaved", mapping_commands("f", "r1", "s", "b", read2="r2")[0])

    def test_thinning_seeds_are_independent_and_explicit(self):
        seeds = set()
        for r in range(3):
            for s in range(10):
                cmd = thinning_command("C0.bam", self.root / "CT.bam", r, s)
                seeds.add(cmd[cmd.index("--subsample-seed") + 1])
        self.assertEqual(len(seeds), 30)
        self.assertIn("1000", seeds)
        self.assertIn("3009", seeds)

    def test_thinning_output_collision(self):
        path = self.file("out.bam", "existing")
        with self.assertRaises(ContractError):
            thinning_command("C0.bam", path, 0, 0)

    def test_native_metabat_settings(self):
        commands = metabat_commands("ref", ["bam"], self.root)
        self.assertIn("--saveCls", commands[1])
        self.assertNotIn("--cvExt", commands[1])
        with self.assertRaises(ContractError):
            metabat_commands("ref", ["bam"], self.root, seed=0)

    def test_metabat_scale_is_not_thinning(self):
        path = self.file("depth.tsv", "contigName\tcontigLen\ttotalAvgDepth\ts.bam\ts.bam-var\na\t2500\t10\t10\t4\nb\t2500\t0\t0\t0\n")
        scale_metabat_depth(path, self.root / "scaled.tsv", {"a": 2500, "b": 2500})
        with (self.root / "scaled.tsv").open() as handle:
            rows = list(csv.reader(handle, delimiter="\t"))
        np.testing.assert_allclose([float(v) for v in rows[1][2:]], [1, 1, .04])
        np.testing.assert_allclose([float(v) for v in rows[2][2:]], [0, 0, 0])

    def test_all_comebin_views_scaled(self):
        bundle = self.root / "bundle"
        bundle.mkdir()
        for name in ("feature_manifest.json", "contig_ids.txt", "contig_lengths.npy", "augmentation_intervals.npy", "kmer_counts.npy", "coverage_manifest.json", "bam_ids.txt"):
            (bundle / name).write_text("fixture")
        a = np.arange(2 * 6 * 3, dtype=float).reshape(2, 6, 3)
        np.save(bundle / "coverage_mean.npy", a)
        np.save(bundle / "coverage_var.npy", a * 4)
        scale_comebin(bundle, self.root / "CS")
        np.testing.assert_allclose(np.load(self.root / "CS/coverage_mean.npy"), a * .1)
        np.testing.assert_allclose(np.load(self.root / "CS/coverage_var.npy"), a * .04)
        self.assertEqual(digest(bundle / "augmentation_intervals.npy"), digest(self.root / "CS/augmentation_intervals.npy"))

    def test_reject_negative_comebin_variance(self):
        bundle = self.root / "bundle"
        bundle.mkdir()
        for name in ("feature_manifest.json", "contig_ids.txt", "contig_lengths.npy", "augmentation_intervals.npy", "kmer_counts.npy", "coverage_manifest.json", "bam_ids.txt"):
            (bundle / name).write_text("fixture")
        np.save(bundle / "coverage_mean.npy", np.ones((2, 6, 3)))
        np.save(bundle / "coverage_var.npy", -np.ones((2, 6, 3)))
        with self.assertRaises(ContractError):
            scale_comebin(bundle, self.root / "CS")

    def test_paired_comebin_stale_view_rejected(self):
        full, thin = self.root / "C0", self.root / "CT"
        for directory in (full, thin):
            directory.mkdir()
            for name in ("contig_ids.txt", "contig_lengths.npy", "augmentation_intervals.npy", "kmer_counts.npy", "bam_ids.txt"):
                (directory / name).write_text("identical")
            for name in ("coverage_mean.npy", "coverage_var.npy"):
                np.save(directory / name, np.ones((2, 6, 3)) * (10 if directory == full else 1))
            write_json(directory / "native-features.json", {"fasta_sha256": "reference", "bam_sha256": {"sample_0.bam": str(directory)},
                       "coverage_sha256": {n: digest(directory / n) for n in ("coverage_mean.npy", "coverage_var.npy")}})
        self.assertEqual(validate_comebin_pair(full, thin)["changed_entries_per_view"]["coverage_mean.npy"], [6] * 6)
        stale = np.load(thin / "coverage_mean.npy")
        stale[:, 2, :] = 10
        np.save(thin / "coverage_mean.npy", stale)
        with self.assertRaises(ContractError):
            validate_comebin_pair(full, thin)

    def test_config_and_dataset_samples_agree(self):
        root = Path(__file__).resolve().parents[1]
        spec = json.loads((root / "experiments/E001-coverage-thinning/acquisition.json").read_text())
        self.assertEqual(config()["samples"], [r["sample"] for r in spec["read_archives_not_authorized_by_inventory"]])
        self.assertEqual(config()["resources"]["gpu_count"], 0)

    def test_failed_native_command_is_recorded(self):
        with self.assertRaises(ContractError):
            run_checked([sys.executable, "-c", "raise SystemExit(7)"], self.root / "logs", "fail")
        self.assertEqual(json.loads((self.root / "logs/fail.json").read_text())["status"], "failed")

    def test_native_source_must_have_own_git_root(self):
        with self.assertRaises(ContractError):
            verify_source("vamb", Path(__file__).resolve().parent)


class ProbeTests(unittest.TestCase):
    def test_neighbors_exclude_self_and_are_not_chosen_by_truth(self):
        pop = {"lengths": {s: 2500 for s in "abcd"}, "unique_origins": {"a": "A", "b": "B", "c": "A", "d": "B"}, "probe_pool": list("abcd"), "probe_queries": ["a"]}
        x = [[1, 0], [1, 0], [0, 1], [-1, 0]]
        result = neighbor_purity(list("abcd"), x, pop, k=1)
        self.assertEqual(result["a"]["neighbors"], ["b"])
        self.assertEqual(result["a"]["purity"], 0)

    def test_zero_and_filtered_rows_reported(self):
        pop = {"lengths": {s: 2500 for s in "abc"}, "unique_origins": {s: "A" for s in "abc"}, "probe_pool": list("abc"), "probe_queries": list("abc")}
        result = neighbor_purity(["a", "b"], [[0, 0], [1, 0]], pop, k=1)
        self.assertEqual([result[s]["status"] for s in "abc"], ["zero_row", "insufficient_neighbors", "filtered"])

    def test_probe_ties_are_stable_across_input_order(self):
        pop = {"lengths": {s: 2500 for s in "abcd"}, "unique_origins": {s: s for s in "abcd"}, "probe_pool": list("abcd"), "probe_queries": ["a"]}
        a = neighbor_purity(list("abcd"), [[1, 0]] * 4, pop, k=2)
        b = neighbor_purity(list("dcba"), [[1, 0]] * 4, pop, k=2)
        self.assertEqual(a, b)
        self.assertEqual(a["a"]["neighbors"], ["b", "c"])


class BamFixtureTests(Files):
    def test_fixture_and_parser(self):
        make_fixture(self.root / "fixture")
        report = check_interleaved(self.root / "fixture/sample_00.fq")
        self.assertGreater(report["pairs_checked"], 0)
        self.assertEqual(list(report["read_length_counts"]), [150])
        report = bam_inventory(self.root / "fixture/C0/sample_00.bam", self.root / "fixture/fixture.fna")
        self.assertGreater(report["records"], 0)

    def test_mate_split_rejected(self):
        make_fixture(self.root / "fixture")
        original = self.root / "fixture/C0/sample_00.bam"
        broken = self.root / "broken.bam"
        with pysam.AlignmentFile(original, "rb") as source, pysam.AlignmentFile(broken, "wb", header=source.header) as target:
            target.write(next(source))
        with self.assertRaises(ContractError):
            check_thinned_fixture(original, broken)

    def test_odd_interleaved_fastq_rejected(self):
        path = self.file("odd.fq", "@read/1\nACGT\n+\nIIII\n")
        with self.assertRaises(ContractError):
            check_interleaved(path)


class CLITests(Files):
    def command(self, *args):
        script = Path(__file__).resolve().parents[1] / "scripts/e001.py"
        return subprocess.run([sys.executable, str(script), *map(str, args)], cwd=self.root, capture_output=True, text=True)

    def test_cli_acquisition_is_dry_run(self):
        result = self.command("acquire", "--root", self.root / "data")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "plan_only")
        self.assertFalse((self.root / "data").exists())

    def test_cli_fixture_is_immutable(self):
        result = self.command("fixture", "--out", self.root / "fixture")
        self.assertEqual(result.returncode, 0, result.stderr)
        before = digest(self.root / "fixture/fixture.fna")
        result = self.command("fixture", "--out", self.root / "fixture")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(digest(self.root / "fixture/fixture.fna"), before)


if __name__ == "__main__":
    unittest.main()
