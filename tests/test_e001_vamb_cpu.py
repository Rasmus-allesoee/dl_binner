"""Portable driver orchestration tests; native VAMB execution is owner-run."""

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import e001_vamb_cpu as driver


class VambDriverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.code = self.root / "code"
        (self.code / "scripts").mkdir(parents=True)
        (self.code / "scripts/e001_vamb_cpu.py").write_text("fixture")
        (self.code / "SOURCE_COMMIT").write_text("a" * 40)
        record = self.code / "experiments/E001-coverage-thinning/frozen-inputs.json"
        record.parent.mkdir(parents=True)
        record.write_text("{}")
        (self.root / "fixture").mkdir()
        (self.root / "fixture/fixture.fna").write_text(">fixture\nACGT\n")
        ct = self.root / "environment-review/mapping-smoke/CT"
        ct.mkdir(parents=True)
        for name in ("a.bam", "b.bam"):
            (ct / name).write_bytes(b"fixture")
        (self.root / "bin").mkdir()
        (self.root / "bin/micromamba").write_bytes(b"fixture")
        self.calls = []

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self, args, env, stage, label, limit):
        self.calls.append(label)
        self.assertNotIn("PYTHONPATH", env)
        self.assertNotIn("PYTHONHOME", env)
        self.assertEqual(env["PYTHONNOUSERSITE"], "1")
        if label == "setup":
            (self.root / "envs/vamb").mkdir(parents=True)
            lock = self.root / "locks/vamb/setup.exit-code.txt"
            lock.parent.mkdir(parents=True)
            lock.write_text("0\n")
        (stage / (label + ".stdout")).write_text("synthetic orchestration pass\n")

    def run_driver(self, invoke=None):
        real_sha = driver.sha
        def sha(path):
            return "366cd9cd8be14df1ab8ed50352a82111082a36686b2d389fdb79a92c3fafb3e3" if Path(path).name == "micromamba" else real_sha(path)
        with patch.object(driver.platform, "system", return_value="Linux"), \
             patch.object(driver.platform, "machine", return_value="x86_64"), \
             patch.object(driver, "sha", side_effect=sha), \
             patch.object(driver, "invoke", side_effect=invoke or self.invoke), \
             patch.dict(os.environ, {"PYTHONPATH": "/poison", "PYTHONHOME": "/poison"}), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return driver.run(self.root, self.code)

    def test_install_then_reuse_preserves_results(self):
        self.assertEqual(self.run_driver(), 0)
        self.assertEqual(self.calls, ["setup", "environment", "pip-check", "smoke", "cpu"])
        self.calls.clear()
        self.assertEqual(self.run_driver(), 0)
        self.assertEqual(self.calls, ["environment", "pip-check", "smoke", "cpu"])
        archives = list(self.root.glob("native-vamb-*-return.tar.gz"))
        self.assertEqual(len(archives), 2)
        for archive in archives:
            self.assertEqual(Path(str(archive) + ".sha256").read_text().split()[0], driver.sha(archive))
            with tarfile.open(archive) as handle:
                self.assertTrue(any(n.endswith("status.json") for n in handle.getnames()))

    def test_setup_failure_stops_and_packages(self):
        def fail(*args):
            raise RuntimeError("synthetic setup failure")
        self.assertEqual(self.run_driver(fail), 1)
        self.assertEqual(len(list(self.root.glob("*-return.tar.gz"))), 1)
        self.assertTrue(next(self.root.glob("native-vamb-*/failure.txt")).is_file())

    def test_partial_environment_is_not_reinstalled(self):
        (self.root / "envs/vamb").mkdir(parents=True)
        self.assertEqual(self.run_driver(), 1)
        self.assertEqual(self.calls, [])

    def test_missing_fixture_blocks_before_install(self):
        (self.root / "fixture/fixture.fna").unlink()
        self.assertEqual(self.run_driver(), 1)
        self.assertEqual(self.calls, [])

    def test_packaging_failure_is_not_success(self):
        with patch.object(driver.tarfile, "open", side_effect=OSError("packaging failed")):
            self.assertEqual(self.run_driver(), 1)
        self.assertFalse(list(self.root.glob("*.sha256")))
        status = json.loads(next(self.root.glob("native-vamb-*/status.json")).read_text())
        self.assertEqual(status["exit_code"], 1)

    def test_command_timeout_retains_record(self):
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(subprocess.TimeoutExpired):
            driver.invoke([sys.executable, "-c", "import time; time.sleep(10)"], dict(os.environ), self.root, "timeout", 0.1)
        self.assertTrue((self.root / "timeout.command.json").is_file())

    def test_native_schedule_projection(self):
        self.assertEqual(sum(n for _, n in driver.SCHEDULE), 300)
        self.assertEqual([b for b, _ in driver.SCHEDULE], [256, 512, 1024, 2048, 4096])
        rows = [{"schedule_epochs": n, "measured_epoch_seconds": [2, 3]} for _, n in driver.SCHEDULE]
        self.assertEqual(driver.projected_core_hours(rows, 4), 1)


if __name__ == "__main__":
    unittest.main()
