#!/usr/bin/env python3
"""Entrypoint for news-image-20261122 (RIVAL3).

Copies the pre-rendered poster.png into the grader output directory as
entry.png. No network, deterministic, exit 0.

Only the *contents* of the output directory are cleared, never the
directory itself (deleting the directory breaks the grader mount).
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    # Clear only the contents of the output directory, never the dir itself.
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    src = os.path.join(HERE, "poster.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
