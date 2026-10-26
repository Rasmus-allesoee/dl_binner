#!/usr/bin/env python3
"""Run actual local E023 tiny readers/selection/export contracts from any cwd.

The numerical environment is borrowed read-only. Only this source checkout and
its tiny tests are overlaid; no neural/training/marker-detection imports occur.
"""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'tests'), str(ROOT/'scripts')]

if __name__ == '__main__':
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name)
                               for name in ['test_e023_density','test_e023_operational'])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
