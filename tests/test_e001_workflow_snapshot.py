"""Test snapshot integrity, safe extraction, failure preservation and executable modes."""

import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from e001_workflow_snapshot import stage_snapshot


class SnapshotTests(unittest.TestCase):
    def archive(self, root, bad=None):
        archive = root / "input.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            member = tarfile.TarInfo("workflow/bin/python")
            member.mode = 0o755
            content = b"fixture interpreter"
            member.size = len(content)
            tar.addfile(member, io.BytesIO(content))
            if bad:
                tar.addfile(bad)
        return archive

    def stage(self, archive, root, name):
        return stage_snapshot(archive, root / (name + ".json"), root,
                              hashlib.sha256(archive.read_bytes()).hexdigest(), archive.stat().st_size)

    def test_repeated_staging_is_unique_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive = self.archive(root)
            one, two = self.stage(archive, root, "one"), self.stage(archive, root, "two")
            self.assertNotEqual(one, two)
            self.assertEqual((one / "bin/python").read_bytes(), b"fixture interpreter")
            self.assertEqual((one / "bin/python").stat().st_mode & 0o777, 0o755)
            self.assertEqual(json.loads((root / "one.json").read_text())["status"], "extracted")
            self.assertTrue(archive.exists())

    def test_bad_hash_stops_before_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive = self.archive(root)
            with self.assertRaisesRegex(ValueError, "SHA256"):
                stage_snapshot(archive, root / "record.json", root, "0" * 64, archive.stat().st_size)
            self.assertFalse(list(root.glob("e001-workflow-*")))

    def test_reject_escape_links_and_duplicates(self):
        for name, kind in (("workflow/../../escape", tarfile.REGTYPE),
                           ("workflow/link", tarfile.SYMTYPE),
                           ("workflow/bin/python", tarfile.REGTYPE)):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                member = tarfile.TarInfo(name)
                member.type, member.linkname = kind, "/etc/passwd"
                archive = self.archive(root, member)
                with self.assertRaisesRegex(ValueError, "Unsafe/duplicate"):
                    self.stage(archive, root, "failed")
                self.assertEqual(json.loads((root / "failed.json").read_text())["status"], "extracting")
                self.assertFalse((root / "escape").exists())


if __name__ == "__main__":
    unittest.main()
