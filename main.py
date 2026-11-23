#!/usr/bin/env python3
"""Copy-only entrypoint for news-image-20261122 RIVAL10 fix (v2).

Copies the checked-in poster.png to the grader output directory as
entry.png. Never renders, never writes into the repo directory, and
never clears the output directory — the repo is mounted read-only by
the grader and the output path is /output/entry.png (see the
competition rules). The previous version defaulted to a relative
"out" directory, so with MAKEFUN_OUTPUT_DIR unset the file never
reached /output and the gate scored it valid 0.
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
