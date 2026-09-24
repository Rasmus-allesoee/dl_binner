"""Diagnose tool imports before site initialization without altering the environment.

Run with the tool Python -I -S, expected prefix, then module names. Emit flushed
stage markers and repeated stacks; retain normal site initialization and verify
import origins. The caller enforces the unchanged startup timeout.
"""
import faulthandler
import sys

faulthandler.enable()
faulthandler.dump_traceback_later(10, repeat=True)
try:
    print('PROBE: before site', file=sys.stderr, flush=True)
    import site
    site.main()
    print('PROBE: site ready', file=sys.stderr, flush=True)
    import importlib
    from pathlib import Path
    prefix = Path(sys.argv[1]).resolve()
    assert Path(sys.prefix).resolve() == prefix and not site.ENABLE_USER_SITE
    for name in sys.argv[2:]:
        print('PROBE: importing '+name, file=sys.stderr, flush=True)
        module = importlib.import_module(name)
        assert Path(module.__file__).resolve().is_relative_to(prefix)
        print('PROBE: ready '+name+' '+module.__file__, file=sys.stderr, flush=True)
    print(sys.version, flush=True)
finally:
    faulthandler.cancel_dump_traceback_later()
