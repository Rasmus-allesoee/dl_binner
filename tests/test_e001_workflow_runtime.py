"""Exercise real workflow startup and deliberately blocked site initialization.

Fixtures use temporary virtual environments; no research data or native mapper
is involved. The existing pinned local engine also tests the production wrapper.
"""

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

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import e001_multisample as multi


class WorkflowRuntimeTests(unittest.TestCase):
    def test_failure_collects_both_probes_without_proceeding(self):
        with tempfile.TemporaryDirectory() as folder:
            calls = []
            def fail(argv, env, stage, label, limit):
                calls.append(label)
                raise RuntimeError("fixture startup failure")
            with patch.object(multi, "invoke", side_effect=fail), self.assertRaisesRegex(ValueError, "both diagnostics"):
                multi.workflow_preflight(Path("/env/bin/snakemake"), {}, Path(folder))
            self.assertEqual(calls, ["workflow-lock", "snakemake-startup"])

    def test_site_hang_emits_child_stack_before_timeout(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            prefix = root / "env"
            subprocess.run([sys.executable, "-m", "venv", "--without-pip", prefix], check=True, timeout=30)
            site = next((prefix / "lib").glob("python*/site-packages"))
            (site / "blocked.pth").write_text("import time; time.sleep(60)\n")
            argv = multi.workflow_command(prefix / "bin/snakemake", "pip", ["freeze"], 0.2)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(subprocess.TimeoutExpired):
                multi.invoke(argv, dict(os.environ), root, "blocked-site", 1.5)
            stderr = (root / "blocked-site.stderr").read_text()
            self.assertIn("initializing site", stderr)
            self.assertIn("addpackage", stderr)
            self.assertNotIn("site ready", stderr)
            record = json.loads((root / "blocked-site.command.json").read_text())
            self.assertTrue(record["timed_out"])
            self.assertIn("pid", record)
            self.assertIn("process_at_timeout", record)

    def test_real_pinned_startup_with_driver_environment(self):
        executable = Path(os.environ.get("E001_TEST_SNAKEMAKE", str(REPO / "artifacts/e001-snakemake-test-env/bin/snakemake")))
        if not executable.is_file():
            self.skipTest("Pinned local workflow runtime unavailable")
        with tempfile.TemporaryDirectory(prefix="e001 # ") as folder:
            root = Path(folder)
            env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONUSERBASE")}
            env.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1", TMPDIR=str(root))
            with contextlib.redirect_stdout(io.StringIO()):
                multi.workflow_preflight(executable, env, root)
            self.assertIn("site ready", (root / "workflow-lock.stderr").read_text())
            snakefile = root / "Snakefile"
            snakefile.write_text('rule all:\n    output: "done.txt"\n    shell: "echo ok > {output}"\n')
            args = ["--snakefile", str(snakefile), "--directory", str(root), "--cores", "1", "--executor", "local"]
            for label, suffix in (("dag", ["--dry-run"]), ("workflow", [])):
                multi.invoke(multi.workflow_command(executable, "snakemake", args + suffix), env, root, label, 60)
            self.assertEqual((root / "done.txt").read_text().strip(), "ok")


if __name__ == "__main__":
    unittest.main()
