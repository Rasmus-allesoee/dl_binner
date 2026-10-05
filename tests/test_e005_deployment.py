"""New deployment boundaries: immutable bytes, target locks, cleanup and full axes."""
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import time
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from e005_smoke import run, sha, write
from e005_owner import unpack_python, verify_bundle, isolated_env
from e005_bundle import wheel_lock


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_bundle_tamper_and_escape_fail_before_runtime(self):
        p = self.folder/'input.tsv'; p.write_text('contig_id\tS1\n')
        manifest = dict(files={'input.tsv': dict(sha256=sha(p), bytes=p.stat().st_size)})
        write(self.folder/'bundle-manifest.json', manifest)
        verify_bundle(self.folder)
        p.write_text('corrupted')
        with self.assertRaisesRegex(ValueError, 'byte mismatch'):
            verify_bundle(self.folder)
        manifest['files'] = {'../outside': dict(sha256='x', bytes=0)}
        (self.folder/'bundle-manifest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            verify_bundle(self.folder)

    def test_python_unpack_rejects_traversal_links_special_and_prior_prefix(self):
        for index, (name, kind, link) in enumerate([
                ('python/../../outside', tarfile.REGTYPE, ''),
                ('python/bin/x', tarfile.SYMTYPE, '/etc/passwd'),
                ('python/bin/x', tarfile.SYMTYPE, '../../outside'),
                ('python/device', tarfile.CHRTYPE, '')]):
            path = self.folder/f'bad-{index}.tar.gz'
            with tarfile.open(path, 'w:gz') as tar:
                member = tarfile.TarInfo(name); member.type = kind; member.linkname = link
                tar.addfile(member, io.BytesIO(b''))
            with self.assertRaises(ValueError):
                unpack_python(path, self.folder/f'out-{index}')
        # Actual upstream archive contracts are exercised by extracting new bytes,
        # never executing the Linux interpreter on Mac or relocating an old prefix.
        prefix = self.folder/'real-python'
        unpack_python(ROOT/'artifacts/e005-linux-pilot/payload/cpython-3.12.10+20250409-x86_64-unknown-linux-gnu-install_only.tar.gz', prefix)
        self.assertTrue((prefix/'bin/python3').is_file())
        self.assertTrue((prefix/'lib/python3.12/site-packages').is_dir())
        with self.assertRaises(FileExistsError):
            unpack_python(self.folder/'bad-0.tar.gz', prefix)

    def test_target_metadata_checks_missing_dependencies_and_python(self):
        def wheel(name, version, extra=''):
            path = self.folder/f'{name}-{version}-py3-none-any.whl'
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr(f'{name}-{version}.dist-info/METADATA', f'Name: {name}\nVersion: {version}\n'+extra)
                z.writestr(f'{name}-{version}.dist-info/WHEEL', 'Tag: py3-none-any\n')
        wheel('parent', '1', 'Requires-Dist: child==2; sys_platform == "linux"\n')
        with self.assertRaisesRegex(ValueError, 'Incomplete Linux'):
            wheel_lock(self.folder, self.folder/'lock')
        wheel('child', '2')
        self.assertEqual(len(wheel_lock(self.folder, self.folder/'lock')), 2)
        (self.folder/'child-2-py3-none-any.whl').unlink()
        wheel('child', '2', 'Requires-Python: <3.12\n')
        with self.assertRaisesRegex(ValueError, 'Unsupported target Python'):
            wheel_lock(self.folder, self.folder/'lock')

    def test_real_time_ceiling_and_failure_receipts_stop_children(self):
        started = time.monotonic()
        with self.assertRaisesRegex(RuntimeError, 'Stage failed'):
            run([sys.executable, '-c', 'import time; time.sleep(30)'], self.folder,
                'ceiling', .3, 8000000000, 2)
        self.assertLess(time.monotonic()-started, 5)
        receipt = json.loads((self.folder/'ceiling.json').read_text())
        self.assertIn('time ceiling', receipt['stop_reason'])
        self.assertEqual(receipt['allocated_vcpu_hours'], 2*receipt['wall_seconds']/3600)
        with self.assertRaises(RuntimeError):
            run([sys.executable, '-c', 'raise OSError("fatal worker fixture")'], self.folder,
                'fatal', 30, 8000000000, 4)
        receipt = json.loads((self.folder/'fatal.json').read_text())
        self.assertNotEqual(receipt['exit_code'], 0)
        self.assertIn('fatal worker fixture', (self.folder/'fatal.log').read_text())
        self.assertLess(receipt['wall_seconds'], 5)

    def test_failed_parent_leaves_no_live_observed_child(self):
        pidfile = self.folder/'child-pid'
        program = ('import subprocess,sys,time; from pathlib import Path; '
                   'p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); '
                   'Path(sys.argv[1]).write_text(str(p.pid)); time.sleep(.8); sys.exit(7)')
        with self.assertRaises(RuntimeError):
            run([sys.executable, '-c', program, str(pidfile)], self.folder,
                'orphan', 10, 8000000000, 4)
        pid = int(pidfile.read_text())
        result = subprocess.run(['ps', '-p', str(pid), '-o', 'stat='], capture_output=True, text=True)
        self.assertTrue(result.returncode != 0 or result.stdout.strip().startswith('Z'))

    def test_complete_short_inclusive_pilot_axis_hash_and_denominators(self):
        from dl_binner.io import read_fasta
        path = ROOT/'experiments/E005-linux-pilot/pilot-inputs.json'
        metadata = json.loads(path.read_text())
        table = ROOT/'experiments/E005-linux-pilot/pilot-contigs.tsv'
        self.assertEqual(sha(table), metadata['contig_manifest_sha256'])
        with table.open() as stream:
            records = list(csv.DictReader(stream, delimiter='\t'))
        fasta = ROOT/'artifacts/e005-linux-pilot/input/pilot/assembly.fna'
        self.assertEqual(sha(fasta), metadata['fasta_sha256'])
        rows = read_fasta(fasta)
        self.assertEqual([i for i, s in rows], [r['contig_id'] for r in records])
        self.assertEqual(sum(len(s) for i, s in rows), metadata['input_bp'])
        self.assertEqual(len(rows), metadata['input_contigs'])
        self.assertEqual(sum(len(s) < 500 for i, s in rows), 1097)
        self.assertTrue(all(len(s) == int(r['bp']) for (i, s), r in zip(rows, records)))
        self.assertEqual(sum(s['contigs'] for s in metadata['length_strata'].values()), len(rows))
        self.assertEqual(sum(s['bp'] for s in metadata['length_strata'].values()), metadata['input_bp'])
        self.assertEqual(sum(v['bp'] for v in metadata['genomes'].values()), metadata['input_bp'])

    def test_environment_paths_cleared_and_thread_budgets_reconciled(self):
        env = isolated_env(2)
        self.assertFalse({'PYTHONHOME', 'PYTHONPATH', 'PYTHONUSERBASE'} & env.keys())
        self.assertEqual(env['PYTHONNOUSERSITE'], '1')
        for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
            self.assertEqual(env[name], '2')

    def test_owner_command_bash_syntax(self):
        guide = (ROOT/'experiments/E005-linux-pilot/OPERATIONS.md').read_text()
        command = guide.split('```bash\n', 1)[1].split('```', 1)[0]
        subprocess.run(['bash', '-n'], input=command, text=True, check=True)
        self.assertIn('--allocated-vcpus 4 --allocated-ram-gb 12', command)
        self.assertIn('set -euo pipefail', command)
        self.assertIn('tee "$log"', command)


if __name__ == '__main__':
    unittest.main()
