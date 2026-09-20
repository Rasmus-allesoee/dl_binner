"""Portable grouping/isolation checks; native runtimes remain owner-executed."""

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import e001_remaining_cpu as group
import test_e001_vamb_cpu as fixtures


class RemainingTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.VambDriverTests()
        self.fixture.setUp()
        self.root, self.code = self.fixture.root, self.fixture.code
        config = self.code / "experiments/E001-coverage-thinning/config.json"
        config.write_text("{}")
        (config.parent / "frozen-inputs.json").write_text(json.dumps({"config_sha256": group.sha(config)}))
        self.calls = []

    def tearDown(self):
        self.fixture.tearDown()

    def test_isolated_entrypoint_imports_shared_helpers(self):
        script = Path(__file__).resolve().parents[1] / "scripts/e001_remaining_cpu.py"
        result = subprocess.run(
            [sys.executable, "-I", str(script), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("root", result.stdout)

    def invoke(self, args, env, stage, label, limit):
        tool = stage.name
        self.calls.append((tool, label))
        self.assertIn(tool, group.TOOLS)
        self.assertEqual(env["PATH"].split(os.pathsep)[0], str(self.root / "envs" / tool / "bin"))
        self.assertNotIn("PYTHONPATH", env)
        if label == "setup":
            self.assertEqual(args[-2], tool)
            (self.root / "envs" / tool).mkdir(parents=True)
            lock = self.root / "locks" / tool / "setup.exit-code.txt"
            lock.parent.mkdir(parents=True)
            lock.write_text("0\n")
            if tool == "comebin":
                auxiliary = self.root / "sources/COMEBin/auxiliary"
                auxiliary.mkdir(parents=True)
                for name in ("marker.hmm", "bacar_marker.hmm"):
                    (auxiliary / name).write_text("synthetic marker payload")
        if label == "cpu":
            work = stage / "cpu-work"
            work.mkdir()
            (work / "synthetic.fna").write_text("excluded bulk fixture")
            (stage / "cpu.json").write_text("{}")
        (stage / (label + ".stdout")).write_text("mock orchestration only")

    def run_group(self, fail=None, tools=group.TOOLS):
        real_sha = group.sha
        def sha(path):
            return "366cd9cd8be14df1ab8ed50352a82111082a36686b2d389fdb79a92c3fafb3e3" if Path(path).name == "micromamba" else real_sha(path)
        def invoke(*args):
            if (args[2].name, args[3]) == fail:
                raise RuntimeError("synthetic tool failure")
            self.invoke(*args)
        with patch.object(group.platform, "system", return_value="Linux"), \
             patch.object(group.platform, "machine", return_value="x86_64"), \
             patch.object(group, "sha", side_effect=sha), patch.object(group, "invoke", side_effect=invoke), \
             patch.dict(os.environ, {"PYTHONPATH": "/poison"}), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return group.run(self.root, self.code, tools)

    def test_two_isolated_tools_and_repeat_without_reinstall(self):
        for tool in ("mapping", "amber", "vamb"):
            prefix = self.root / "envs" / tool
            prefix.mkdir(parents=True)
            (prefix / "accepted").write_text("preserve validated runtime")
        self.assertEqual(self.run_group(), 0)
        self.assertEqual([t for t, l in self.calls if l == "setup"], list(group.TOOLS))
        self.calls.clear()
        self.assertEqual(self.run_group(), 0)
        self.assertFalse(any(l == "setup" for _, l in self.calls))
        for tool in ("mapping", "amber", "vamb"):
            self.assertEqual((self.root / "envs" / tool / "accepted").read_text(), "preserve validated runtime")
        archives = list(self.root.glob("native-remaining-*-return.tar.gz"))
        self.assertEqual(len(archives), 2)
        for path in archives:
            self.assertEqual(Path(str(path) + ".sha256").read_text().split()[0], group.sha(path))
            with tarfile.open(path) as archive:
                self.assertFalse(any(n.endswith("synthetic.fna") for n in archive.getnames()))
                self.assertEqual(sum(n.endswith("cpu.json") for n in archive.getnames()), 2)

    def test_one_setup_failure_does_not_block_other_tool(self):
        self.assertEqual(self.run_group(("metabat", "setup")), 1)
        self.assertIn(("comebin", "cpu"), self.calls)
        self.assertNotIn(("metabat", "smoke"), self.calls)

    def test_reviewed_recovery_can_target_one_tool(self):
        self.assertEqual(self.run_group(tools=("comebin",)), 0)
        self.assertTrue(all(tool == "comebin" for tool, _ in self.calls))
        status = json.loads(next(self.root.glob("native-remaining-*/status.json")).read_text())
        self.assertEqual(status["requested_tools"], ["comebin"])

    def test_smoke_failure_skips_only_its_cpu(self):
        self.assertEqual(self.run_group(("metabat", "smoke")), 1)
        self.assertNotIn(("metabat", "cpu"), self.calls)
        self.assertIn(("comebin", "cpu"), self.calls)

    def test_partial_environment_preserved_other_tool_runs(self):
        (self.root / "envs/metabat").mkdir(parents=True)
        (self.root / "envs/metabat/keep").write_text("previous failure")
        self.assertEqual(self.run_group(), 1)
        self.assertEqual((self.root / "envs/metabat/keep").read_text(), "previous failure")
        self.assertIn(("comebin", "cpu"), self.calls)

    def test_package_failure_returns_nonzero(self):
        with patch.object(group.tarfile, "open", side_effect=OSError("package failure")):
            self.assertEqual(self.run_group(), 1)
        self.assertFalse(list(self.root.glob("*.sha256")))

    def test_metabat_synthetic_generation_and_membership(self):
        source, out = self.root / "source", self.root / "synthetic"
        out.mkdir()
        def command(argv, logs, label):
            (out / "bins.MemberMatrix.txt").write_text("ContigName\tClusterId\n" + "".join(f"synthetic{i:06d}\t1\n" for i in range(4)))
        with patch("e001lib.native.verify_source", return_value={"tool": "metabat"}), \
             patch("e001lib.native.run_checked", side_effect=command):
            report = group.metabat_measure(source, out, {"retained_contigs": 4, "retained_bp": 16003, "samples": list(range(10))})
        self.assertEqual(report["synthetic_bp"], 16003)
        self.assertEqual(report["assigned_contigs"], 4)
        rows = (out / "depth.tsv").read_text().splitlines()
        self.assertEqual(len(rows), 5)
        self.assertEqual(len(rows[0].split("\t")), 23)


if __name__ == "__main__":
    unittest.main()
