#!/usr/bin/env python3
"""Entrypoint for the RIVAL6 poster.

Copies the pre-rendered poster.png into the grader output directory.
Only the *contents* of that directory are cleared -- the directory itself
is never deleted, in case the grader holds it open or mounts it read-only
from above. No drawing, no network, no writes outside the output dir.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "output"
    os.makedirs(out, exist_ok=True)
    for name in os.listdir(out):
        path = os.path.join(out, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    shutil.copyfile(os.path.join(HERE, "poster.png"),
                    os.path.join(out, "poster.png"))


if __name__ == "__main__":
    main()
