# main.py — news-image-20261122 v3 entrypoint.
# Copies the rendered poster to the grader output directory.
# Never writes into the repository (the repo is read-only at grade time).
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "poster.png")
OUTDIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "output")
OUT = os.path.join(OUTDIR, "entry.png")

os.makedirs(OUTDIR, exist_ok=True)
shutil.copyfile(SRC, OUT)
print("wrote", OUT)
