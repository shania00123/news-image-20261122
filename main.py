#!/usr/bin/env python3
"""Copy-only entrypoint: copies the pre-rendered poster.png to $MAKEFUN_OUTPUT_DIR/entry.png.

Clears only the contents of the output directory; never deletes the
output directory itself.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "poster.png")


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out:
        print("MAKEFUN_OUTPUT_DIR not set", file=sys.stderr)
        return 1
    os.makedirs(out, exist_ok=True)
    for name in os.listdir(out):
        p = os.path.join(out, name)
        if os.path.isdir(p) and not os.path.islink(p):
            shutil.rmtree(p)
        else:
            os.remove(p)
    shutil.copyfile(SRC, os.path.join(out, "entry.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
