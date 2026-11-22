#!/usr/bin/env python3
"""Entrypoint: copy poster.png into the grader output directory.

Only the *contents* of the output directory are cleared; the directory
itself is never removed (the grader runs as an unprivileged user on a
read-only bind mount, so deleting the directory fails with EACCES).
"""
import os
import shutil
import sys


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poster.png")
    os.makedirs(out_dir, exist_ok=True)
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    shutil.copyfile(src, os.path.join(out_dir, "poster.png"))
    print("copied poster.png to", out_dir)


if __name__ == "__main__":
    main()
