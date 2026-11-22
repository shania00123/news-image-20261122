#!/usr/bin/env python3
"""Entrypoint for news-image-20261122 RIVAL9.

Renders the poster into a temporary directory (never into the repo, so
this works even when the repo is mounted read-only), then copies it into
the grader output directory. Only the output directory's CONTENTS are
cleared, never the directory itself.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    tmp = tempfile.mkdtemp(prefix="rival9-")
    try:
        poster = os.path.join(tmp, "poster.png")
        subprocess.run(
            [sys.executable, os.path.join(HERE, "render_rival9.py"), poster],
            check=True,
        )
        os.makedirs(out_dir, exist_ok=True)
        # Clear only the contents of the output directory, never the dir.
        for name in os.listdir(out_dir):
            path = os.path.join(out_dir, name)
            if os.path.isdir(path) and not os.path.islink(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        shutil.copyfile(poster, os.path.join(out_dir, "poster.png"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("wrote poster.png to", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
