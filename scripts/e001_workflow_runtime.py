"""Launch the existing workflow Python with diagnostics before site initialization.

Invoke with its Python using -I -S, then this file, a diagnostic interval (0
disables it), a module name and that module's arguments. Normal site processing
is deliberately retained: no packages or startup hooks are silently bypassed.
Progress and delayed Python stacks go to stderr; module stdout stays unchanged.
This neither installs software nor changes the persistent environment.
"""

import faulthandler
import sys


def main():
    """Initialize site explicitly, then run pip or Snakemake with original argv."""
    interval = float(sys.argv[1])
    module = sys.argv[2]
    if module not in ("pip", "snakemake"):
        raise ValueError("Only pip and snakemake entry points are supported")
    faulthandler.enable()
    if interval:
        faulthandler.dump_traceback_later(interval, repeat=True)
    try:
        print("RUNTIME: interpreter entered; initializing site", file=sys.stderr, flush=True)
        import site
        site.main()
        print("RUNTIME: site ready; prefix=" + sys.prefix, file=sys.stderr, flush=True)
        import runpy
        sys.argv = [module] + sys.argv[3:]
        print("RUNTIME: entering " + module, file=sys.stderr, flush=True)
        runpy.run_module(module, run_name="__main__", alter_sys=True)
    finally:
        if interval:
            faulthandler.cancel_dump_traceback_later()


if __name__ == "__main__":
    main()
