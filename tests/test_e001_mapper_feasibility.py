"""Portable prefix/driver safeguards; these tests do not execute Linux mappers."""

import contextlib
import gzip
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import e001_mapper_feasibility as mapper


PUBLISHER_MEMBER = "2017.12.04_18.45.54_sample_0/reads/anonymous_reads.fq"


class MapperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def fixture(self, bad=False, member=PUBLISHER_MEMBER):
        text = ""
        for i in range(3):
            for mate in (1, 2):
                name = f"r{i + int(bad and mate == 2)}/{mate}"
                text += f"@{name}\n" + "A" * 150 + "\n+\n" + "I" * 150 + "\n"
        path = self.root / "sample.tar.gz"
        data = gzip.compress(text.encode()) if member.endswith(".gz") else text.encode()
        with tarfile.open(path, "w:gz") as tar:
            entry = tarfile.TarInfo(member)
            entry.size = len(data)
            tar.addfile(entry, io.BytesIO(data))
        return path

    def test_prefix_stops_at_complete_pairs(self):
        result = mapper.extract_prefix(self.fixture(), self.root / "reads", pairs=2)
        self.assertEqual(result["pairs"], 2)
        self.assertEqual(result["member"], PUBLISHER_MEMBER)
        self.assertEqual(len((self.root / "reads/R1.fq").read_text().splitlines()), 8)

    def test_gzipped_fastq_member_remains_supported(self):
        with patch.object(mapper, "MEMBER", PUBLISHER_MEMBER + ".gz"):
            result = mapper.extract_prefix(self.fixture(member=PUBLISHER_MEMBER + ".gz"), self.root / "reads", pairs=2)
        self.assertEqual(result["pairs"], 2)

    def test_mismatched_pairs_stop(self):
        with self.assertRaisesRegex(ValueError, "Mismatched"):
            mapper.extract_prefix(self.fixture(bad=True), self.root / "reads", pairs=2)

    def test_missing_member_stops(self):
        with self.assertRaisesRegex(ValueError, "absent"):
            mapper.extract_prefix(self.fixture(member="other"), self.root / "reads")

    def test_short_prefix_stops(self):
        with self.assertRaisesRegex(ValueError, "Insufficient"):
            mapper.extract_prefix(self.fixture(), self.root / "reads", pairs=4)

    def test_download_requires_opt_in(self):
        args = SimpleNamespace(root=self.root, vcpus=2, ram_gb=6, archive=None, allow_sample_archive=False)
        with self.assertRaisesRegex(ValueError, "explicitly authorize"):
            mapper.run(args)
        self.assertFalse(list(self.root.glob("mapper-feasibility-*")))

    def test_group_success_uses_actual_threads(self):
        code = self.root / "code"
        (code / "scripts").mkdir(parents=True)
        script = code / "scripts/e001_mapper_feasibility.py"
        script.write_text("fixture")
        (code / "SOURCE_COMMIT").write_text("a" * 40)
        binary = self.root / "envs/bowtie2/bin/bowtie2"
        binary.parent.mkdir(parents=True)
        binary.write_text("fixture")
        archive = self.fixture()
        args = SimpleNamespace(root=self.root, vcpus=2, ram_gb=6, archive=archive, allow_sample_archive=False)
        calls = []
        def invoke(argv, env, stage, label, limit):
            calls.append(label)
            self.assertNotIn("PYTHONPATH", env)
            if label == "mapping":
                self.assertEqual(argv[-1], 2)
        with patch.object(mapper, "__file__", str(script)), patch.object(mapper, "ARCHIVE_BYTES", archive.stat().st_size), \
             patch.object(mapper, "invoke", side_effect=invoke), patch.object(mapper.shutil, "disk_usage", return_value=SimpleNamespace(free=30*10**9)), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(mapper.run(args), 0)
        self.assertEqual(calls, ["bowtie-lock", "prefix", "mapping"])

    def test_changed_remote_archive_stops_before_payload(self):
        response = unittest.mock.MagicMock()
        response.__enter__.return_value = response
        response.status = 200
        response.headers = {"ETag": "changed", "Content-Length": str(mapper.ARCHIVE_BYTES)}
        with patch.object(mapper.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(ValueError, "changed"):
                mapper.acquire(self.root / "archive.tar.gz")
        response.read.assert_not_called()

    def test_failure_preserves_unique_attempt_and_actual_allocation(self):
        args = SimpleNamespace(root=self.root, vcpus=2, ram_gb=6, archive=self.root / "absent", allow_sample_archive=False)
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(mapper.run(args), 1)
            self.assertEqual(mapper.run(args), 1)
        archives = list(self.root.glob("*-return.tar.gz"))
        self.assertEqual(len(archives), 2)
        with tarfile.open(archives[0]) as tar:
            status = json.load(tar.extractfile(next(m for m in tar if m.name.endswith("status.json"))))
        self.assertEqual(status["vcpus"], 2)
        self.assertAlmostEqual(status["allocated_core_hours"], 2 * status["elapsed_seconds"] / 3600)


if __name__ == "__main__":
    unittest.main()
