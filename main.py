#!/usr/bin/env python3
"""make.fun entrypoint for news-image-20261122.

Copies the checked-in poster.png to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output/entry.png). Nothing else: the poster is rendered at
build time by render.py, never here, so this program works on a
read-only source mount and always writes identical bytes.
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "poster.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
