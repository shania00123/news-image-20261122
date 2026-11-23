"""Copy-only entrypoint: copy the pre-built poster.png into the output dir.

No image generation happens here. The poster is built offline and committed to
the repo; at grade time this script only copies it, using the standard
library so it runs on a bare stock Python image with no third-party
packages, no fonts and no network.
"""

import os
import shutil
import sys


def clean_output_dir(path):
    os.makedirs(path, exist_ok=True)
    for name in os.listdir(path):
        target = os.path.join(path, name)
        if os.path.islink(target) or os.path.isfile(target):
            os.remove(target)
        elif os.path.isdir(target):
            shutil.rmtree(target)


def main():
    repo_dir = os.environ.get("MAKEFUN_BOT_DIR", ".")
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "output")
    clean_output_dir(output_dir)
    src = os.path.join(repo_dir, "poster.png")
    dst = os.path.join(output_dir, "poster.png")
    shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
