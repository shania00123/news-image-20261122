#!/usr/bin/env python3
"""Graded entrypoint for news-image-20261122 v2.

Copy-only: copies the checked-in poster.png to the grader output
directory as entry.png. It never renders, never writes into the repo
directory, and never modifies poster.png — the repo is mounted read-only
by the grader, so any in-place write would fail (see news-21 v3).
"""

import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "poster.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
