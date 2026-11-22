#!/usr/bin/env python3
"""Copy poster.png to the grader output directory as entry.png.

Copy-only: never writes into the repo (read-only at grade time) and never
deletes the output directory itself (that fails EACCES, because deleting
a directory needs write permission on its parent). It only clears the
directory's contents, then copies one file. Deterministic: the same
bytes on every run.
"""
import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    for name in os.listdir(out):
        path = os.path.join(out, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    shutil.copyfile(os.path.join(here, "poster.png"),
                    os.path.join(out, "entry.png"))


if __name__ == "__main__":
    main()
