#!/usr/bin/env python3
"""Supervise one real pilot rule with frozen time/RSS/CPU limits and retained logs.

Receipts live in the attempt; native worker stdout is captured there. The outer
Snakemake benchmark is complementary and includes this supervision overhead.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e005_owner import isolated_env
from e005_smoke import run


def main():
    """Execute argv after --; reject empty commands and invalid resource declarations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    a = parser.parse_args(); cfg = json.loads(a.config.read_text())
    command = a.command[1:] if a.command and a.command[0] == '--' else a.command
    if not command or a.seconds <= 0 or not 1 <= cfg['threads'] <= 4 or '/' in a.name:
        parser.error('Invalid command/name/budget')
    run(command, cfg['rule_receipts'], a.name, a.seconds, cfg['rss_bytes'], cfg['threads'], isolated_env(cfg['threads']))


if __name__ == '__main__':
    main()
