"""Portable tests for the supplemental no-download review driver."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from e001_environment_review import PROBE, clean_environment, run


class EnvironmentReviewTests(unittest.TestCase):
    def test_clean_environment_preserves_unrelated_settings(self):
        original = {"PYTHONPATH": "external", "PYTHONHOME": "other", "PYTHONUSERBASE": "user", "PATH": "keep"}
        cleaned = clean_environment(original)
        self.assertNotIn("PYTHONPATH", cleaned)
        self.assertNotIn("PYTHONHOME", cleaned)
        self.assertNotIn("PYTHONUSERBASE", cleaned)
        self.assertEqual(cleaned["PYTHONNOUSERSITE"], "1")
        self.assertEqual(cleaned["PATH"], "keep")
        self.assertEqual(original["PYTHONPATH"], "external")

    def test_failure_records_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            with self.assertRaises(RuntimeError):
                run([sys.executable, "-c", "raise SystemExit(7)"], out, "fail", dict(os.environ))
            self.assertEqual(json.loads((out / "fail.command.json").read_text())["returncode"], 7)

    def test_probe_detects_external_distribution(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / "external_fixture-1.0.dist-info"
            fake.mkdir()
            (fake / "METADATA").write_text("Metadata-Version: 2.1\nName: external-fixture\nVersion: 1.0\n")
            env = {**os.environ, "PYTHONPATH": directory, "PYTHONNOUSERSITE": "1"}
            observed = subprocess.run([sys.executable, "-c", PROBE, "mapping", "observed", sys.prefix],
                                      env=env, capture_output=True, text=True, check=True)
            report = json.loads(observed.stdout)
            self.assertTrue(any(d["name"] == "external-fixture" and not d["inside_prefix"] for d in report["distributions"]))
            cleaned = subprocess.run([sys.executable, "-c", PROBE, "mapping", "clean", sys.prefix],
                                     env=clean_environment(env), capture_output=True, text=True)
            self.assertEqual(cleaned.returncode, 0, cleaned.stderr)
