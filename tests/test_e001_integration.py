"""Portable fixture and grouped integration-driver contracts, not native execution."""

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import e001_integration as integration


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.code = self.root / "code"
        (self.code / "scripts").mkdir(parents=True)
        (self.code / "scripts/e001_integration.py").write_text("fixture")
        (self.code / "SOURCE_COMMIT").write_text("a" * 40)
        self.input = self.root / "input"
        self.input.mkdir()
        with (self.input / "canonical.fna").open("w") as fasta, (self.input / "contigs.jsonl").open("w") as truth:
            for i in range(130):
                fasta.write(f">PC{i}\n" + "ACGT" * 2500 + "\n")
                truth.write(json.dumps({"id": f"PC{i}", "origins": [f"g{i%2}"]}) + "\n")
        self.frozen = {"owner_input_directory": str(self.input), "outputs":
                       {n: integration.sha(self.input / n) for n in ("canonical.fna", "contigs.jsonl")}}
        path = self.code / "experiments/E001-coverage-thinning/frozen-inputs.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(self.frozen))

    def tearDown(self):
        self.temp.cleanup()

    def test_fixture_is_bounded_deterministic_and_truth_separate(self):
        for suffix in ("a", "b"):
            integration.prepare(self.input, self.root / suffix, self.frozen)
        a = json.loads((self.root / "a/fixture.json").read_text())
        self.assertEqual(len(a["lengths"]), 128)
        self.assertEqual(sum(a["lengths"].values()), 1280000)
        self.assertEqual((self.root / "a/fixture.fna").read_bytes(), (self.root / "b/fixture.fna").read_bytes())
        self.assertTrue((self.root / "a/truth.tsv").is_file())

    def test_changed_input_stops_before_fixture(self):
        self.frozen["outputs"]["canonical.fna"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Changed frozen input"):
            integration.prepare(self.input, self.root / "a", self.frozen)
        self.assertFalse((self.root / "a").exists())

    def test_group_isolation_and_failure_dependency(self):
        calls = []
        def invoke(args, env, stage, label, limit):
            calls.append(label)
            self.assertEqual(args[1], "-I")
            self.assertNotIn("PYTHONPATH", env)
            if label == "vamb":
                raise RuntimeError("fixture failure")
            if label == "comebin":
                self.assertEqual(env["CHECKM_DATA_PATH"], str(self.root / "envs/comebin/checkm_data"))
        with patch.object(integration, "invoke", side_effect=invoke), patch.dict(os.environ, {"PYTHONPATH": "/poison"}), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(integration.run(self.root, self.code), 1)
        self.assertEqual(calls, ["fixture", "vamb", "comebin", "comebin-evaluate"])
        self.assertEqual(len(list(self.root.glob("*-return.tar.gz.sha256"))), 1)

    def test_repeat_preserves_previous_attempts(self):
        with patch.object(integration, "invoke"), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(integration.run(self.root, self.code), 0)
            self.assertEqual(integration.run(self.root, self.code), 0)
        self.assertEqual(len(list(self.root.glob("*-return.tar.gz.sha256"))), 2)

    def test_packaging_failure_is_nonzero(self):
        with patch.object(integration, "invoke"), patch.object(integration.tarfile, "open", side_effect=OSError("full")), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(integration.run(self.root, self.code), 1)
        self.assertFalse(list(self.root.glob("*.sha256")))

    def test_real_isolated_entrypoint(self):
        result = subprocess.run([sys.executable, "-I", str(Path(integration.__file__)), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
