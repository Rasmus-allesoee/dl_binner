"""Small deployment invariants; real native owner harness is recorded separately."""
import importlib.util
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

ROOT=Path(__file__).absolute().parents[1]
spec=importlib.util.spec_from_file_location('e006_owner',ROOT/'scripts/e006_owner.py')
owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)


class DeploymentContracts(unittest.TestCase):
    def test_packet_detects_byte_set_and_link_changes(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);file=root/'file';file.write_bytes(b'one')
            owner.write(root/'bundle-manifest.json',dict(files={'file':owner.record(file)}))
            self.assertEqual(owner.verify_bundle(root)['files']['file'],owner.record(file))
            file.write_bytes(b'two')
            with self.assertRaisesRegex(ValueError,'bytes changed'):owner.verify_bundle(root)
            file.write_bytes(b'one');(root/'extra').write_text('x')
            with self.assertRaisesRegex(ValueError,'file set'):owner.verify_bundle(root)
            (root/'extra').unlink();file.unlink();file.symlink_to(root/'bundle-manifest.json')
            with self.assertRaisesRegex(ValueError,'Linked'):owner.verify_bundle(root)

    def test_dependencies_never_link_old_package_or_path_injection(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);source=root/'source';dest=root/'dest';source.mkdir();dest.mkdir()
            for name in ('numpy','dl_binner','dl_binner-0.1.0.dev0.dist-info','__pycache__'):
                (source/name).mkdir();(source/name/'data').write_text(name)
            (source/'inject.pth').write_text('outside');(source/'.DS_Store').write_text('volatile')
            before=owner.tree_binding(source)
            self.assertEqual(set(owner.link_dependencies(source,dest)),{'numpy'})
            self.assertEqual((dest/'numpy/data').read_text(),'numpy')
            self.assertEqual(owner.tree_binding(source),before)
            (source/'numpy/data').write_text('changed')
            self.assertNotEqual(owner.tree_binding(source),before)
            with self.assertRaises(ValueError):owner.link_dependencies(source,dest)

    def test_failed_return_preserves_status_manifest_and_checksum(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);attempt=root/'attempt';transfer=root/'transfer';attempt.mkdir();transfer.mkdir()
            owner.write(attempt/'status.json',dict(status='failed',error='intended prerequisite'))
            owner.write(attempt/'bundle-manifest.json',dict(source_commit='bound'))
            (attempt/'terminal.log').write_text('intended prerequisite\n')
            result=owner.collect(attempt,transfer)
            archive=Path(result['archive'])
            self.assertEqual(Path(result['checksum']).read_text().split()[0],owner.record(archive)['sha256'])
            with tarfile.open(archive) as tar:
                self.assertEqual(json.load(tar.extractfile('attempt/status.json'))['error'],'intended prerequisite')
                self.assertIn('attempt/bundle-manifest.json',tar.getnames())
            self.assertTrue((attempt/'terminal.log').exists())

    def test_frozen_budget_and_accepted_wheel(self):
        spec=json.loads((ROOT/'experiments/E006-cli-usability/linux-smoke.json').read_text())
        self.assertEqual((spec['execution_seconds_ceiling'],spec['evidence_collection_seconds_ceiling']),(1800,120))
        self.assertEqual((spec['allocated_vcpus'],spec['allocated_ram_gb'],spec['loader_workers']),(4,12,0))
        self.assertEqual(spec['working_rss_bytes_ceiling'],8000000000)
        wheel=ROOT/'artifacts/e006-cli-usability/setup/dist-v7/dl_binner-0.1.0.dev1-py3-none-any.whl'
        self.assertEqual(owner.record(wheel),spec['wheel_record'])


if __name__=='__main__':unittest.main()
