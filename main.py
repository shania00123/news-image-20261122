#!/usr/bin/env python3
"""Entrypoint: copy poster.png into the grader output directory.

Only the *contents* of the output directory are cleared; the directory
itself is never removed (the grader may hold it open or mount it).
The poster is pre-rendered by render_rival5.py, so this entrypoint does
no drawing, no network and no writes outside the output directory.
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
