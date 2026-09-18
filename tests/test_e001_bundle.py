"""Small transfer-package checks without native tools or network access."""

import hashlib
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from e001_bundle import PATHS, build


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        for entry in PATHS:
            path = self.repo / entry
            if not path.suffix:
                path = path / "fixture.txt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n")
        (self.repo / "private.txt").write_text("must not transfer")
        self.git("add", ".")
        self.git("commit", "-qm", "Fixture")

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args])

    def test_allowlist_commit_checksum_and_no_overwrite(self):
        archive, checksum = build(self.repo, self.root / "out")
        self.assertEqual(checksum.read_text().split()[0], hashlib.sha256(archive.read_bytes()).hexdigest())
        with tarfile.open(archive) as contents:
            names = contents.getnames()
            self.assertFalse(any("private.txt" in n or "/.git/" in n for n in names))
            self.assertEqual(contents.extractfile(archive.name[:-7] + "/SOURCE_COMMIT").read(), self.git("rev-parse", "HEAD"))
        with self.assertRaises(ValueError):
            build(self.repo, self.root / "out")

    def test_dirty_checkout_rejected(self):
        (self.repo / "private.txt").write_text("changed")
        with self.assertRaises(ValueError):
            build(self.repo, self.root / "out")

    def test_symlink_rejected(self):
        path = self.repo / "tests/link"
        path.symlink_to("../private.txt")
        self.git("add", ".")
        self.git("commit", "-qm", "Link")
        with self.assertRaises(ValueError):
            build(self.repo, self.root / "out")
