"""Driver failure guards only; these mocks do not establish Linux compatibility."""

import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest


class PreflightDriverTests(unittest.TestCase):
    def test_inventory_refuses_existing_data_before_work(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code = root / "e001-code-9c2b0ec6feb3"
            code.mkdir()
            (code / "SOURCE_COMMIT").write_text("9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea\n")
            (root / "inventory").mkdir()
            mocks = root / "mock-bin"
            mocks.mkdir()
            uname = mocks / "uname"
            uname.write_text('#!/bin/sh\nif [ "$1" = -s ]; then echo Linux; else echo x86_64; fi\n')
            uname.chmod(0o755)
            driver = Path(__file__).resolve().parents[1] / "scripts/e001_gi_inventory.sh"
            result = subprocess.run(["bash", str(driver), str(root)], capture_output=True, text=True,
                                    env={**os.environ, "PATH": str(mocks) + os.pathsep + os.environ["PATH"]})
            self.assertEqual(result.returncode, 2)
            self.assertIn("existing", result.stderr)
            self.assertFalse((root / "inventory-stage").exists())
            retry = subprocess.run(["bash", str(driver), str(root), "--retry-missing-time"], capture_output=True, text=True,
                                   env={**os.environ, "PATH": str(mocks) + os.pathsep + os.environ["PATH"]})
            self.assertEqual(retry.returncode, 2)
            self.assertFalse((root / "failed-inventory-missing-time").exists())

    def test_inventory_recovery_preserves_inspected_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code = root / "e001-code-9c2b0ec6feb3"
            code.mkdir()
            (code / "SOURCE_COMMIT").write_text("9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea\n")
            old = root / "inventory-stage"
            old.mkdir()
            (old / "exit-code.txt").write_text("127\n")
            (old / "prerequisites.exit-code.txt").write_text("127\n")
            (old / "prerequisites.stderr").write_text("/usr/bin/time: No such file or directory\n")
            (root / "gi-inventory-return.tar.gz").write_bytes(b"preserve fixture")
            (root / "gi-inventory-return.tar.gz.sha256").write_text("fixture checksum\n")
            mocks = root / "mock-bin"
            mocks.mkdir()
            for name, body in {"uname": 'if [ "$1" = -s ]; then echo Linux; else echo x86_64; fi',
                               "sha256sum": "echo mock-checksum"}.items():
                path = mocks / name
                path.write_text("#!/bin/sh\n" + body + "\n")
                path.chmod(0o755)
            driver = Path(__file__).resolve().parents[1] / "scripts/e001_gi_inventory.sh"
            result = subprocess.run(["bash", str(driver), str(root), "--retry-missing-time"], capture_output=True, text=True,
                                    env={**os.environ, "PATH": str(mocks) + os.pathsep + os.environ["PATH"]})
            # The intentionally incomplete source fixture stops before any installation.
            self.assertNotEqual(result.returncode, 0)
            saved = root / "failed-inventory-missing-time"
            self.assertEqual((saved / "gi-inventory-return.tar.gz").read_bytes(), b"preserve fixture")
            self.assertEqual((saved / "inventory-stage/exit-code.txt").read_text(), "127\n")
            self.assertFalse((root / "inventory").exists())

    def test_conversion_recovery_preserves_known_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stage = root / "conversion-alias-stage"
            stage.mkdir()
            (stage / "exit-code.txt").write_text("1\n")
            (stage / "stderr.txt").write_text("E001 check failed: Invalid DNA: orphan\n")
            (root / "conversion-alias-return.tar.gz").write_bytes(b"return")
            (root / "conversion-alias-return.tar.gz.sha256").write_text("fixture\n")
            mocks = root / "mock-bin"
            mocks.mkdir()
            sha = mocks / "sha256sum"
            sha.write_text("#!/bin/sh\nexit 0\n")
            sha.chmod(0o755)
            code = root / "code"
            (code / "scripts").mkdir(parents=True)
            (code / "SOURCE_COMMIT").write_text("x\n")
            driver = Path(__file__).resolve().parents[1] / "scripts/e001_retry_conversion.sh"
            result = subprocess.run(["bash", str(driver), str(root), "--retry-known-failure"], capture_output=True, text=True,
                                    env={**os.environ, "PATH": str(mocks) + os.pathsep + os.environ["PATH"]})
            self.assertNotEqual(result.returncode, 0)
            saved = root / "failed-conversion-malformed-fasta"
            self.assertEqual((saved / "conversion-alias-return.tar.gz").read_bytes(), b"return")
            self.assertTrue((saved / "conversion-alias-stage").exists())
            self.assertTrue((root / "conversion-alias-stage").exists())

    def test_download_failure_is_packaged_and_stops_before_install(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code = root / "e001-code-9c2b0ec6feb3"
            (code / "scripts").mkdir(parents=True)
            (code / "SOURCE_COMMIT").write_text("9c2b0ec6feb3b7884bbf7d519c63176d4fb10aea\n")
            for name in ("e001_linux_setup.sh", "e001_linux_smoke.sh"):
                (code / "scripts" / name).write_text("exit 99\n")
            mocks = root / "mock-bin"
            mocks.mkdir()
            for name, body in {
                "uname": 'if [ "$1" = -s ]; then echo Linux; else echo x86_64; fi',
                "curl": "echo 'simulated download failure' >&2; exit 22",
                "sha256sum": "echo mock-checksum",
            }.items():
                path = mocks / name
                path.write_text("#!/bin/sh\n" + body + "\n")
                path.chmod(0o755)
            driver = Path(__file__).resolve().parents[1] / "scripts/e001_ucloud_preflight.sh"
            result = subprocess.run(["bash", str(driver), str(root)], capture_output=True, text=True,
                                    env={**os.environ, "PATH": str(mocks) + os.pathsep + os.environ["PATH"]})
            self.assertEqual(result.returncode, 22, result.stdout + result.stderr)
            self.assertEqual((root / "bootstrap/exit-code.txt").read_text(), "22\n")
            self.assertFalse((root / "envs").exists())
            self.assertFalse((root / "bootstrap/apt-update.log").exists())
            with tarfile.open(root / "preflight-return.tar.gz") as archive:
                self.assertIn("bootstrap/download-micromamba.log", archive.getnames())
            retry = subprocess.run(["bash", str(driver), str(root)], capture_output=True, text=True,
                                   env={**os.environ, "PATH": str(mocks) + os.pathsep + os.environ["PATH"]})
            self.assertEqual(retry.returncode, 2)
            self.assertIn("existing", retry.stderr)
