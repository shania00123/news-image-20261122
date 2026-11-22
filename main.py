#!/usr/bin/env python3
"""Entrypoint: copy poster.png to $MAKEFUN_OUTPUT_DIR as entry.png.

Copy-only: clears ONLY the CONTENTS of the output directory, never the
directory itself (deleting the directory breaks the grader: EACCES).
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    os.makedirs(out, exist_ok=True)
    for name in os.listdir(out):
        path = os.path.join(out, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    shutil.copyfile(os.path.join(HERE, "poster.png"),
                    os.path.join(out, "entry.png"))
    print("wrote entry.png to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
