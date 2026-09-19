"""Exercise the complete resume driver on synthetic data in a disposable work root."""

import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from e001_inventory_resume import run


def sha(path, algorithm="sha256"):
    return hashlib.new(algorithm, path.read_bytes()).hexdigest()


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        repo = Path(__file__).resolve().parents[1]
        self.code = self.root / "code"
        shutil.copytree(repo / "scripts", self.code / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        experiment = self.code / "experiments/E001-coverage-thinning"
        experiment.mkdir(parents=True)
        shutil.copy(repo / "experiments/E001-coverage-thinning/config.json", experiment / "config.json")
        (self.code / "SOURCE_COMMIT").write_text("a" * 40 + "\n")
        (self.root / "envs").mkdir()
        (self.root / "envs/mapping").symlink_to(Path(sys.prefix), target_is_directory=True)
        gi = self.root / "inventory/per_bodysite/gastro_bam"
        gi.mkdir(parents=True)
        fasta = gi / "gsa.fa"
        fasta.write_text(">ref_from_1_to_2600_total_2600\n" + "A" * 2600 +
                         "\n>foreign_from_1_to_2501_total_2501\n" + "C" * 2501 +
                         "\n>_from__to_-42_total_0\n>_from__to_-42_total_0\n")
        mapping = gi / "gsa_pooled_mapping_fixed.tsv"
        mapping.write_text("#anonymous_contig_id\tgenome_id\ttax_id\tcontig_id\tnumber_reads\tstart_position\tend_position\n"
                           "PC0\tg1\t2\tref\t10\t1\t2600\nPC1\tg1\t2\tref\t10\t1\t2600\n")
        original = gi / "gsa_pooled_mapping.tsv"
        original.write_text(mapping.read_text())
        setup = self.root / "inventory/gastrooral/setup.tar.gz"
        setup.parent.mkdir()
        with tarfile.open(setup, "w:gz") as archive:
            member = tarfile.TarInfo("metadata.tsv")
            member.size = 4
            archive.addfile(member, io.BytesIO(b"test"))
        self.policy = experiment / "gi-input-policy.json"
        self.policy.write_text(json.dumps({
            "source_sha256": {"fasta": sha(fasta), "mapping": sha(mapping)},
            "original_mapping_md5": sha(original, "md5"), "setup_md5": sha(setup, "md5"),
            "setup_member_sha256": {"metadata.tsv": hashlib.sha256(b"test").hexdigest()},
            "expected_empty_records": 2, "expected_alias_groups": 1, "expected_mapping_keys": 1,
            "quarantine": [{"id": "foreign_from_1_to_2501_total_2501", "length": 2501,
                            "reason": "foreign_simulation_provenance"}]}))
        (self.root / "input-preflight-v2").mkdir()
        (self.root / "input-preflight-v2/old.txt").write_text("previous failed attempt\n")

    def tearDown(self):
        self.temp.cleanup()

    def execute(self, convert=True):
        # Empty PATH and poisoned user Python paths model the fresh-job boundary.
        return subprocess.run([sys.executable, "-I", str(self.code / "scripts/e001_inventory_resume.py"),
                               str(self.root), *(["--convert"] if convert else [])],
                              env={**os.environ, "PATH": "", "PYTHONPATH": "/nonexistent/injected",
                                   "PYTHONUSERBASE": "/nonexistent/injected"}, capture_output=True, text=True)

    def test_complete_resume_twice_preserves_attempts_without_system_utilities(self):
        for _ in range(2):
            result = self.execute()
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        archives = sorted(self.root.glob("inventory-resume-*-return.tar.gz"))
        self.assertEqual(len(archives), 2)
        for archive in archives:
            self.assertEqual(Path(str(archive) + ".sha256").read_text().split()[0], sha(archive))
            with tarfile.open(archive) as handle:
                names = handle.getnames()
                inventory = next(n for n in names if n.endswith("input/inventory.json"))
                report = json.load(handle.extractfile(inventory))
                self.assertEqual(report["quarantined_bp"], 2501)
                self.assertEqual(report["input_contigs"], 1)
                self.assertEqual(report["status"], "blocked")
                self.assertFalse(any(n.endswith("canonical.fna") for n in names))
        self.assertEqual((self.root / "input-preflight-v2/old.txt").read_text(), "previous failed attempt\n")

    def test_corrupt_metadata_stops_before_conversion_and_returns_error(self):
        policy = json.loads(self.policy.read_text())
        policy["setup_member_sha256"]["metadata.tsv"] = "0" * 64
        self.policy.write_text(json.dumps(policy))
        result = self.execute()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Setup member checksum mismatch", result.stderr)
        self.assertEqual(len(list(self.root.glob("inventory-resume-*-return.tar.gz"))), 1)
        self.assertFalse(list(self.root.glob("inventory-resume-*/input")))

    def test_audit_only_does_not_convert(self):
        result = self.execute(convert=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(list(self.root.glob("inventory-resume-*/input")))

    def test_missing_persistent_environment_is_packaged(self):
        (self.root / "envs/mapping").unlink()
        result = self.execute()
        self.assertEqual(result.returncode, 1)
        self.assertIn("Persistent mapping Python is missing", result.stderr)
        self.assertEqual(len(list(self.root.glob("inventory-resume-*-return.tar.gz"))), 1)
        self.assertFalse(list(self.root.glob("inventory-resume-*/input")))

    def test_packaging_failure_cannot_report_success(self):
        real_open = tarfile.open

        def fail_package(*args, **kwargs):
            if kwargs.get("mode") == "w:gz":
                raise OSError("synthetic packaging failure")
            return real_open(*args, **kwargs)

        with patch("e001_inventory_resume.tarfile.open", side_effect=fail_package), \
             patch("sys.stdout", new_callable=io.StringIO), patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(run(self.root, self.code, convert=True), 1)
        status = json.loads(next(self.root.glob("inventory-resume-*/status.json")).read_text())
        self.assertEqual(status["exit_code"], 1)
        self.assertTrue(status["packaging_failed"])
        self.assertFalse(list(self.root.glob("*-return.tar.gz.sha256")))
