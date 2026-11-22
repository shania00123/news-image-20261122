#!/usr/bin/env python3
"""Entrypoint: copy poster.png into the grader output directory.

Copy-only: it never draws, never uses the network, and never deletes the
output directory itself -- it clears only the directory's *contents*
(the grader runs as uid 65534 on a read-only mount, so removing the
directory itself would fail with EACCES).
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "poster.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    sys.exit(main())
