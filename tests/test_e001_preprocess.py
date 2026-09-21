"""Portable extraction, owner-driver and actual Snakemake DAG tests."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import e001_preprocess as prep


class PreprocessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def archive(self, pairs=2):
        text = "".join(f"@r{i}/{mate}\n" + "A"*150 + "\n+\n" + "I"*150 + "\n"
                       for i in range(pairs) for mate in (1, 2))
        path = self.root / "sample.tar.gz"
        with tarfile.open(path, "w:gz") as tar:
            member = tarfile.TarInfo(prep.MEMBER)
            member.size = len(text)
            tar.addfile(member, io.BytesIO(text.encode()))
        return path

    def test_full_extraction_and_refusal_to_overwrite(self):
        archive = self.archive()
        output = self.root / "reads.fq"
        result = prep.extract(archive, output, expected_pairs=2)
        self.assertEqual(result["pairs"], 2)
        self.assertEqual(len(output.read_text().splitlines()), 16)
        with self.assertRaises(FileExistsError):
            prep.extract(archive, output, expected_pairs=2)

    def test_full_count_not_silent_prefix(self):
        with self.assertRaisesRegex(ValueError, "More pairs"):
            prep.extract(self.archive(), self.root / "reads.fq", expected_pairs=1)

    def test_allocation_guard(self):
        with self.assertRaisesRegex(ValueError, "three vCPUs"):
            prep.run(self.root, 2, 6)
        self.assertFalse(list(self.root.glob("sample0-*")))

    def test_complete_driver_order_and_repeat_preservation(self):
        code = self.root / "code"
        script = code / "scripts/e001_preprocess.py"
        script.parent.mkdir(parents=True)
        script.write_text("fixture")
        (code / "SOURCE_COMMIT").write_text("a"*40)
        frozen = code / "experiments/E001-coverage-thinning/frozen-inputs.json"
        frozen.parent.mkdir(parents=True)
        frozen.write_text(json.dumps({"owner_input_directory": str(self.root), "outputs": {"canonical.fna": "0"*64}}))
        archive = self.root / "mapper-feasibility-13l53afq/sample_0.tar.gz"
        archive.parent.mkdir()
        archive.touch()
        (self.root / "envs/workflow").mkdir(parents=True)
        calls = []
        with patch.object(prep, "__file__", str(script)), patch.object(prep.subprocess, "check_output", return_value="9.13.7\n"), \
             patch.object(prep.shutil, "disk_usage", return_value=SimpleNamespace(free=40*10**9)), \
             patch.object(prep, "invoke", side_effect=lambda args, env, stage, label, limit: calls.append(label)), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(prep.run(self.root, 4, 12), 0)
            self.assertEqual(prep.run(self.root, 4, 12), 0)
        self.assertEqual(calls, ["workflow-lock", "dag", "workflow"] * 2)
        self.assertEqual(len(list(self.root.glob("*-return.tar.gz"))), 2)

    def test_missing_prerequisite_returns_failure_archive(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(prep.run(self.root, 4, 12), 1)
        self.assertEqual(len(list(self.root.glob("*-return.tar.gz.sha256"))), 1)

    def test_actual_snakemake_dag_when_available(self):
        executable = REPO / "artifacts/e001-snakemake-test-env/bin/snakemake"
        if not executable.exists():
            self.skipTest("Optional isolated workflow-engine environment unavailable")
        archive, reference = self.root / "sample.tar.gz", self.root / "ref.fna"
        archive.touch(); reference.touch()
        runtime = self.root / "runtime.json"
        runtime.write_text(json.dumps({"archive": str(archive), "reference": str(reference), "vcpus": 4,
            "mapping_python": sys.executable, "helper": str(REPO / "scripts/e001_preprocess.py"), "runtime_config": str(runtime)}))
        result = subprocess.run([str(executable), "--snakefile", str(REPO / "workflows/e001-preprocess/Snakefile"),
            "--directory", str(self.root), "--configfile", str(runtime), "--cores", "4", "--dry-run"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for rule in ("extract_sample0", "map_full", "thin_and_report"):
            self.assertIn(rule, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
