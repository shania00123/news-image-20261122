#!/usr/bin/env python3
"""Entrypoint (copy-only): render the poster to a temp dir, then copy the
single poster.png into the output dir, removing only stale files inside
that dir. Never deletes the output dir itself."""
import os
import shutil
import subprocess
import sys
import tempfile


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "output"
    here = os.path.dirname(os.path.abspath(__file__))
    tmp = tempfile.mkdtemp(prefix="rival10-")
    try:
        subprocess.run(
            [sys.executable, os.path.join(here, "render_rival10.py"), tmp],
            check=True)
        os.makedirs(out, exist_ok=True)
        for name in os.listdir(out):
            p = os.path.join(out, name)
            if os.path.isfile(p):
                os.remove(p)
        shutil.copy(os.path.join(tmp, "poster.png"),
                    os.path.join(out, "poster.png"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
