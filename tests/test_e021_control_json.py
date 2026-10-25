"""Actual filesystem/subprocess contracts for the E021 queue publication repair."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT=Path(__file__).absolute().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from e021_control_json import MAX_BYTES,publish,remote_program


class AtomicControlContracts(unittest.TestCase):
    def test_reader_cannot_observe_an_empty_or_partial_published_command(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'0002.json';entered=threading.Event();release=threading.Event();errors=[]
            original=os.fsync
            def slow_sync(fd):
                if not entered.is_set():entered.set();release.wait(5)
                original(fd)
            value=dict(argv=['native-worker','opaque \n quoted " DNA'],payload='x'*50000)
            def writer():
                try:publish(value,p)
                except BaseException as e:errors.append(e)
            with patch('e021_control_json.os.fsync',side_effect=slow_sync):
                t=threading.Thread(target=writer);t.start();self.assertTrue(entered.wait(3))
                self.assertFalse(p.exists());self.assertEqual(len(list(p.parent.glob('*.pending'))),1)
                release.set();t.join(5)
            self.assertFalse(t.is_alive());self.assertEqual(errors,[])
            self.assertEqual(json.loads(p.read_text()),value);self.assertEqual(list(p.parent.glob('*.pending')),[])

    def test_original_open_then_dump_pattern_exposes_empty_JSON(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'old.json'
            with p.open('x')as f:
                with self.assertRaises(json.JSONDecodeError):json.loads(p.read_text())
                json.dump(dict(event='old publication race'),f)

    def test_exact_isolated_remote_program_and_existing_target_refusal(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'command.json';code=remote_program(p);value=dict(name='fixed-stage',argv=['one','two\nthree'])
            q=subprocess.run([sys.executable,'-I','-B','-c',code],input=json.dumps(value),text=True,capture_output=True,cwd=d)
            self.assertEqual(q.returncode,0,q.stderr);self.assertEqual(json.loads(p.read_text()),value)
            q=subprocess.run([sys.executable,'-I','-B','-c',code],input='{}',text=True,capture_output=True,cwd=d)
            self.assertNotEqual(q.returncode,0);self.assertIn('FileExistsError',q.stderr)
            self.assertEqual(json.loads(p.read_text()),value)

    def test_invalid_or_oversized_JSON_never_publishes(self):
        with tempfile.TemporaryDirectory()as d:
            p=Path(d)/'command.json'
            for value in [dict(value=float('nan')),dict(value='x'*MAX_BYTES)]:
                with self.assertRaises(ValueError):publish(value,p)
                self.assertFalse(p.exists());self.assertEqual(list(p.parent.iterdir()),[])


if __name__=='__main__':unittest.main()
