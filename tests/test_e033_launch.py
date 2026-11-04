"""Check the actual E033 configuration producer and rendered native programs."""
import ast
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import e033_launch as launch
from e024_coverage import binding
from e033_arm import validate_config as arm_config
from e033_phase import validate_config


class Launch(unittest.TestCase):
    def fixture(self, folder):
        """Use tiny transport bytes with the real current schema and frozen paths."""
        root = Path(folder); wheel = root / 'dl_binner-0.1.0.dev9-py3-none-any.whl'
        pysam = root / 'pysam-0.23.3-cp310-cp310-manylinux_2_28_x86_64.whl'
        wheel.write_bytes(b'fixture owned product'); pysam.write_bytes(b'fixture platform dependency')
        source = root / 'source.bundle'; source.write_bytes(b'fixture source')
        now = time.time()
        ident = dict(source='a' * 40, repo='/srv/dl_binner/repo', phase='multiscale-test',
            root='/srv/dl_binner/experiments/e033/multiscale-test', user='research',
            service_name='e033-multiscale-test', archive_prefix='gs://dl-binner-archive-167650584170/e033/test/',
            vm_start_epoch=now)
        financial = dict(coverage_status='PASS_FOR_SPECIFIED_ORDINARY_FIRST_PARTY_PRODUCTS_ONLY', real_money_authorized=False,
            checked_epoch=now, credit_checked_epoch=now, estimated_complete_gross_USD=16, ceiling_USD=20,
            credit_valid_until_epoch=1799712000, storage_valid_until_epoch=1794351600,
            wheel_path=str(wheel), wheel_binding=binding(wheel), pysam_path=str(pysam),
            pysam_binding=binding(pysam), pysam_filename=pysam.name,
            source_transport=dict(kind='private_exact_Git_bundle', path=str(source), bundle=binding(source), base='b' * 40))
        return ident, financial

    def test_complete_actual_producer_matches_both_consumers_and_task_plan(self):
        with tempfile.TemporaryDirectory() as folder:
            ident, financial = self.fixture(folder)
            cfg = launch.config_value(ident, financial, 100, 200)
            self.assertTrue(validate_config(cfg)); arm_config(cfg)
            self.assertEqual(cfg['initial_filesystem_device'], 200)
            self.assertEqual(cfg['review_deadline_epoch'] - cfg['vm_start_epoch'], 36 * 3600)
            plan = json.loads((ROOT / 'experiments/E033-multiscale-bam/runtime-plan.json').read_text().replace('NEW_PHASE', ident['phase'] + '/task'))
            self.assertEqual(plan['python'], cfg['python'])
            self.assertEqual(plan['work'], cfg['task_filesystem'] + '/work')
            for value in plan['measurements'].values(): self.assertTrue(value['bank'].startswith(cfg['task_filesystem'] + '/'))
            for key in cfg:
                wrong = dict(cfg); del wrong[key]
                with self.assertRaisesRegex(ValueError, 'configuration'): validate_config(wrong)
            wrong = dict(cfg, invented_field=True)
            with self.assertRaisesRegex(ValueError, 'configuration'): validate_config(wrong)

    def test_compile_actual_mount_source_release_tail_and_inventory(self):
        with tempfile.TemporaryDirectory() as folder:
            ident, financial = self.fixture(folder)
            for disk in [None, dict(name='e033-task-123')]:
                code = launch.render_host(ident, financial, disk); compile(code, 'actual host', 'exec')
                tree = ast.parse(code)
                assignment = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == 'script' for x in n.targets))
                # Exercise the exact inner privileged script, not a separate facsimile.
                value = next(n.value for n in ast.walk(assignment.value) if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.startswith('import os,pathlib'))
                for a, b in [('@@TASK@@', repr(ident['root'] + '/task')), ('@@NAME@@', repr('e033-task-123')), ('@@USER@@', repr('research'))]: value = value.replace(a, b)
                compile(value, 'actual new-disk program', 'exec')
                self.assertIn('100*1024**3', value); self.assertIn('blkid', value)
                self.assertIn("name.startswith('e033-task-')", value)
                self.assertNotIn('dl-binner-work', value)
            for code in [launch.source_sync(ident, financial['source_transport']), launch.render_tail(ident),
                         launch.render_inventory(ident), launch.render_release(ident, {})]: compile(code, 'actual consumer', 'exec')
            self.assertIn('refs/heads/multiscale-bam-representation', launch.source_sync(ident, financial['source_transport']))
            tail = launch.render_tail(ident)
            self.assertIn('ro,nodev,nosuid,noload', tail)
            self.assertIn('actualwork!=allwork', tail)
            self.assertIn('storage_upload', tail)
            self.assertNotIn("'delete'", tail)
            bad = dict(financial, wheel_binding=dict(bytes=1, sha256='0' * 64))
            with self.assertRaisesRegex(ValueError, 'payload differs'): launch.render_host(ident, bad)


if __name__ == '__main__': unittest.main()
